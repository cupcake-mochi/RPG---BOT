"""A chamada à IA numa camada só: trocar de provedor ou de modelo é mudar a fila, não o código.

Fila = lista de "provedor:modelo", em ordem. Se um falha (cota, erro, resposta vazia), o próximo responde.
Cada tentativa vira uma linha em chamadas_api, com tokens e latência: é daí que sai o gasto real.

Provedores:
  gemini  Gemini pelo AI Studio, com a chave gratuita. Não custa nada, mas a cota do dia é pequena (o 3.8 Flash
          tem 20 pedidos por dia, divididos com o site de teste) e o Google pode usar as conversas do nível
          gratuito pra melhorar os produtos dele.
  vertex  Gemini pela Vertex AI (hoje "Gemini Enterprise Agent Platform"), com chave de API do Google Cloud.
          É onde o crédito mensal do Google AI Pro abate, e as conversas não são usadas pelo Google.
          https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start?usertype=apikey

A fila padrão tenta o gratuito primeiro e só gasta quando a cota do dia acaba (Mizuki, 13/10/2026).

A Vertex é pós-paga e NÃO para quando o crédito acaba: passa a cobrar no cartão, e o alerta de orçamento do
Google só avisa. Por isso o teto é daqui: antes de usar um provedor pago, o bot soma o que já gastou no mês
(tokens do registro vezes o preço de tabela) e, passando do teto, tira os pagos da fila até o mês virar.

O formato do pedido é o mesmo do site de teste (site/servidor.py): a primeira mensagem da entrada é o prompt
de sistema, o resto é a conversa.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable

log = logging.getLogger(__name__)

URLS = {
    "vertex": "https://aiplatform.googleapis.com/v1/publishers/google/models/{modelo}:generateContent",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
}
FILA_PADRAO = "gemini:gemini-3.8-flash,vertex:gemini-3.8-flash,gemini:gemini-3.1-flash-lite,vertex:gemini-3.1-flash-lite"
PAGOS = ("vertex",)
TETO_PADRAO_USD = 9.0  # o crédito do mês é de US$ 10

# US$ por milhão de tokens (entrada, saída; raciocínio conta como saída), lidos em 13/10/2026 em
# https://ai.google.dev/gemini-api/docs/pricing. É estimativa: quem manda é a fatura do Google Cloud.
PRECOS = {"gemini-3.8-flash": (0.75, 3.75), "gemini-3.1-flash-lite": (0.25, 1.50)}
PRECOS_2027 = {"gemini-3.8-flash": (1.50, 7.50)}  # o 3.8 Flash dobra em 01/01/2027
PRECO_DESCONHECIDO = (1.50, 7.50)  # modelo fora da tabela conta pelo mais caro, pra errar pra cima
TEMPERATURA = 0.8
MAX_SAIDA = 2048
ESPERA = 60  # segundos por tentativa
BLOQUEIOS = ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "OTHER")


class Falhou(Exception):
    def __init__(self, codigo, motivo: str = ""):
        super().__init__(f"{codigo} {motivo}".strip())
        self.codigo, self.motivo = codigo, motivo


@dataclass(frozen=True)
class Resposta:
    texto: str
    provedor: str
    modelo: str
    tokens_entrada: int | None
    tokens_saida: int | None
    latencia_ms: int
    cortada: bool  # parou no limite de tokens de saída


def custo_usd(modelo: str, tokens_entrada: int, tokens_saida: int, ano: int = 2026) -> float:
    tabela = {**PRECOS, **PRECOS_2027} if ano >= 2027 else PRECOS
    entrada, saida = tabela.get(modelo, PRECO_DESCONHECIDO)
    return (tokens_entrada * entrada + tokens_saida * saida) / 1_000_000


def ler_fila(texto: str) -> list[tuple[str, str]]:
    fila = []
    for item in texto.split(","):
        provedor, _, modelo = item.strip().partition(":")
        if provedor in URLS and modelo:
            fila.append((provedor, modelo))
    return fila


def montar_corpo(entrada: list[dict], raciocinio: str | None = None) -> dict:
    """`raciocinio` ("low", "medium", "high") limita o quanto o modelo pensa antes de falar; None deixa o padrão dele."""
    geracao = {"temperature": TEMPERATURA, "maxOutputTokens": MAX_SAIDA}
    if raciocinio:
        geracao["thinkingConfig"] = {"thinkingLevel": raciocinio}
    return {
        "system_instruction": {"parts": [{"text": entrada[0]["content"]}]},
        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
                     for m in entrada[1:]],
        "generationConfig": geracao,
    }


def ler_resposta(dados: dict) -> tuple[str, bool, int | None, int | None]:
    """Devolve (texto, cortada, tokens de entrada, tokens de saída). Levanta Falhou se veio vazio ou bloqueado."""
    candidato = (dados.get("candidates") or [{}])[0]
    partes = candidato.get("content", {}).get("parts", [])
    texto = "".join(p.get("text", "") for p in partes if not p.get("thought")).strip()
    if not texto:
        motivo = candidato.get("finishReason") or dados.get("promptFeedback", {}).get("blockReason") or "vazio"
        raise Falhou("bloqueado" if motivo in BLOQUEIOS else "vazio", motivo)
    uso = dados.get("usageMetadata", {})
    # os tokens de raciocínio são cobrados como saída
    saida = (uso.get("candidatesTokenCount") or 0) + (uso.get("thoughtsTokenCount") or 0)
    return texto, candidato.get("finishReason") == "MAX_TOKENS", uso.get("promptTokenCount"), saida or None


class Modelos:
    """`enviar(url, corpo, chave)` faz o POST e devolve o JSON, ou levanta Falhou; no teste é uma função falsa."""

    def __init__(self, fila: list[tuple[str, str]], chaves: dict[str, str], registro=None,
                 enviar: Callable[[str, dict, str], Awaitable[dict]] | None = None, teto_usd: float = TETO_PADRAO_USD,
                 raciocinio: str | None = None):
        self.fila = [(p, m) for p, m in fila if chaves.get(p)]  # provedor sem chave sai da fila
        self.teto_usd = teto_usd
        self.raciocinio = raciocinio
        self._chaves = chaves
        self._registro = registro
        self._enviar = enviar or _enviar_http

    def gasto_do_mes(self) -> float:
        """Estimativa em US$ do que os provedores pagos já consumiram neste mês, pelo registro."""
        if not self._registro:
            return 0.0
        agora = datetime.now(timezone.utc)
        return sum(custo_usd(modelo.partition(":")[2], entrada, saida, agora.year)
                   for modelo, entrada, saida in self._registro.tokens_do_mes(agora)
                   if modelo.partition(":")[0] in PAGOS)

    async def responder(self, entrada: list[dict], *, persona: str | None = None, gatilho: str | None = None) -> Resposta:
        if not self.fila:
            raise Falhou("sem_chave", "nenhum provedor da fila tem chave no .env")
        corpo, ultimo_erro = montar_corpo(entrada, self.raciocinio), None
        pagos_liberados = self.gasto_do_mes() < self.teto_usd
        for provedor, modelo in self.fila:
            if provedor in PAGOS and not pagos_liberados:
                ultimo_erro = ultimo_erro or Falhou("teto", f"gasto do mês chegou ao teto de US$ {self.teto_usd:.2f}")
                continue
            inicio = time.monotonic()
            try:
                dados = await self._enviar(URLS[provedor].format(modelo=modelo), corpo, self._chaves[provedor])
                texto, cortada, entrada_tk, saida_tk = ler_resposta(dados)
            except Falhou as erro:
                ultimo_erro = erro
                self._registrar(provedor, modelo, persona, gatilho, inicio, ok=False, erro=str(erro)[:300])
                log.warning("modelo: %s:%s falhou (%s)", provedor, modelo, str(erro)[:200])
                continue
            latencia = round((time.monotonic() - inicio) * 1000)
            self._registrar(provedor, modelo, persona, gatilho, inicio, ok=True, entrada=entrada_tk, saida=saida_tk)
            return Resposta(texto, provedor, modelo, entrada_tk, saida_tk, latencia, cortada)
        if ultimo_erro.codigo == "teto":
            log.warning("modelo: teto do mês atingido (US$ %.2f); provedores pagos fora da fila", self.teto_usd)
        raise ultimo_erro

    def _registrar(self, provedor, modelo, persona, gatilho, inicio, *, ok, entrada=None, saida=None, erro=None) -> None:
        if self._registro:
            self._registro.registrar_chamada(modelo=f"{provedor}:{modelo}", persona=persona, gatilho=gatilho,
                                             tokens_entrada=entrada, tokens_saida=saida,
                                             latencia_ms=round((time.monotonic() - inicio) * 1000), ok=ok, erro=erro)


async def _enviar_http(url: str, corpo: dict, chave: str) -> dict:
    import asyncio

    import aiohttp  # já vem com o discord.py

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=ESPERA)) as sessao:
            # a chave vai no cabeçalho, não na URL, pra não aparecer em registro de acesso
            async with sessao.post(url, json=corpo, headers={"x-goog-api-key": chave}) as resposta:
                if resposta.status != 200:
                    raise Falhou(resposta.status, (await resposta.text())[:3000].replace("\n", " "))
                return await resposta.json()
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as erro:
        raise Falhou("rede", str(erro))
