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

import asyncio
import base64
import logging
import math
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Awaitable, Callable

log = logging.getLogger(__name__)

URLS = {
    "vertex": "https://aiplatform.googleapis.com/v1/publishers/google/models/{modelo}:generateContent",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
}
FILA_PADRAO = "gemini:gemini-3.8-flash,vertex:gemini-3.8-flash,gemini:gemini-3.1-flash-lite,vertex:gemini-3.1-flash-lite"
ARGON = "gemini-4-argon"
FLASH = "gemini-3.8-flash"
FILA_REFLEXAO = [("vertex", FLASH), ("vertex", "gemini-3.1-flash-lite")]
PAGOS = ("vertex",)
TETO_PADRAO_USD = 9.0  # o crédito do mês é de US$ 10
# Quanto o modelo pensa antes de falar. "low" por escolha do Mizuki em 13/10/2026, depois da comparação:
# 42% mais barato e menos da metade do tempo, sem perda visível. "modelo" devolve o padrão do próprio modelo.
RACIOCINIO_PADRAO = "low"

# US$ por milhão de tokens (entrada, saída; raciocínio conta como saída), lidos em 13/10/2026 em
# https://ai.google.dev/gemini-api/docs/pricing. É estimativa: quem manda é a fatura do Google Cloud.
PRECOS = {FLASH: (0.75, 3.75), "gemini-3.1-flash-lite": (0.25, 1.50), ARGON: (2.0, 10.0)}
PRECOS_2027 = {"gemini-3.8-flash": (1.50, 7.50)}  # o 3.8 Flash dobra em 01/01/2027
PRECO_DESCONHECIDO = (4.0, 20.0)  # aproximação, sem garantia para modelos fora da tabela
TEMPERATURA = 0.8
MAX_SAIDA = 2048
ARGON_MAX_SAIDA = 4096  # primeira amostra low: até 286 tokens; continua configurável
ARGON_ESPERA = 60  # evita abandonar raciocínio ainda faturável e pagar outra resposta no fallback
ESPERA = 25  # segundos por tentativa; resposta normal chega em 2 a 8
# O gratuito espera menos: quando ele engasga, quem chamou a personagem não fica meio minuto olhando pro "digitando".
ESPERA_POR_PROVEDOR = {"gemini": 12, "vertex": 60}
# Prazo da mensagem inteira, somando as tentativas: quem chamou não fica mais que isso olhando pro "digitando".
# Sem ele, a fila padrão podia esperar 144 s (204 s com o Argon na frente). A reflexão das 4h30 não tem quem
# espere e fica fora do prazo. Tentativa que teria menos que TENTATIVA_MINIMA não é enviada.
PRAZO_TOTAL = 75
TENTATIVA_MINIMA = 5
# Depois de falhar, o provedor fica de molho e a fila pula direto pro seguinte, pra ninguém esperar à toa:
# cota estourada (429) demora a voltar; sobrecarga e queda de rede passam logo.
# 400 fica de fora: é erro do pedido, não do provedor, e um pedido malformado (a reflexão já mandou um) não
# pode tirar o modelo de todos os outros por meia hora.
MOLHO = {401: 1800, 403: 1800, 404: 1800, 429: 600, 500: 120, 502: 120,
         503: 120, 504: 120, "rede": 120, "vazio": 120}
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
    tokens_resposta: int | None = None
    tokens_raciocinio: int | None = None
    tokens_cache: int | None = None
    fim: str | None = None
    custo_estimado_usd: float | None = None


def custo_usd(modelo: str, tokens_entrada: int, tokens_saida: int, ano: int | None = None,
              *, mes: int | None = None, tokens_cache: int = 0, sem_promocao: bool = False) -> float:
    """Estimativa global. Promoções são créditos sobre gasto líquido, sujeitos à fatura.

    Não pressupõe cache: só desconta tokens que a API informou como reutilizados.
    `sem_promocao` permite comparar com o preço cheio, antes dos créditos promocionais.
    """
    agora = datetime.now(timezone.utc)
    ano, mes = ano if ano is not None else agora.year, mes if mes is not None else agora.month
    tabela = {**PRECOS, **PRECOS_2027} if ano >= 2027 else PRECOS
    entrada, saida = tabela.get(modelo, PRECO_DESCONHECIDO)
    if modelo == ARGON and (sem_promocao or (ano, mes) >= (2026, 12)):
        entrada, saida = 4.0, 20.0
    if modelo == FLASH and sem_promocao:
        entrada, saida = 1.5, 7.5
    cache = min(max(tokens_cache, 0), tokens_entrada)
    desconto = 0.05 if modelo == ARGON else 0.10 if modelo in PRECOS else 1.0
    return ((tokens_entrada - cache + cache * desconto) * entrada + tokens_saida * saida) / 1_000_000


def fila_do_chat(modelo: str = "", fila: str = "") -> list[tuple[str, str]]:
    if modelo == ARGON:
        return [("vertex", ARGON)] + [(p, m) for p, m in ler_fila(fila or FILA_PADRAO) if m != ARGON]
    if modelo == "misto":
        return [(p, m) for p, m in ler_fila(fila or FILA_PADRAO) if m != ARGON]
    if modelo == FLASH:
        return ler_fila(FILA_PADRAO)
    if modelo:
        raise ValueError("modelo de chat não reconhecido")
    return ler_fila(fila or FILA_PADRAO)


def ler_fila(texto: str) -> list[tuple[str, str]]:
    fila = []
    for item in texto.split(","):
        provedor, _, modelo = item.strip().partition(":")
        if provedor in URLS and modelo:
            fila.append((provedor, modelo))
    return fila


def reserva_midia(entrada: list[dict]) -> int:
    """Reserva visual conservadora, independente dos bytes do texto/base64.

    Só aceita a saída normalizada do preparador, no último turno do usuário.
    Não autoriza enviar mídia ao modelo apenas por uma estimativa declarada.
    """
    imagens = audios = extras = 0
    for i, m in enumerate(entrada):
        partes = m.get('midias', [])
        if not partes:
            continue
        if i != len(entrada) - 1 or i == 0 or m['role'] != 'user' or len(partes) > 6:
            raise ValueError('mídia só é permitida no último turno do usuário')
        for parte in partes:
            if set(parte) == {'text'} and isinstance(parte['text'], str) and len(parte['text']) <= 180:
                extras += len(parte['text'].encode())
                continue
            if set(parte) != {'inlineData'} or set(parte['inlineData']) != {'mimeType', 'data'}:
                raise ValueError('parte de mídia inválida')
            blob = parte['inlineData']
            if not isinstance(blob['data'], str) or len(blob['data']) > 1_400_000:
                raise ValueError('mídia grande')
            dados = base64.b64decode(blob['data'], validate=True)
            if blob['mimeType'] == 'image/jpeg' and dados.startswith(b'\xff\xd8'):
                imagens += 1
            elif blob['mimeType'] == 'audio/wav' and dados[:4] == b'RIFF' and dados[8:12] == b'WAVE':
                audios += 1
            else:
                raise ValueError('tipo de mídia inválido')
    if imagens > 3 or audios > 1 or (imagens and audios):
        raise ValueError('limite de mídia por mensagem excedido')
    return imagens * 4096 + audios * 2048 + extras


def montar_corpo(entrada: list[dict], raciocinio: str | None = None, *, modelo: str = FLASH,
                 argon_max_saida: int = ARGON_MAX_SAIDA) -> dict:
    """`raciocinio` ("low", "medium", "high") limita o quanto o modelo pensa antes de falar; None ou "modelo" deixa o padrão dele."""
    geracao = {"temperature": TEMPERATURA, "maxOutputTokens": MAX_SAIDA}
    if modelo == ARGON:
        # Argon ignora amostragem e rejeita penalidades; esforço fica explícito.
        geracao = {"maxOutputTokens": argon_max_saida}
        raciocinio = "low"
    if raciocinio and raciocinio != "modelo":
        geracao["thinkingConfig"] = {"thinkingLevel": raciocinio}
    tem_midia = reserva_midia(entrada)
    if tem_midia and modelo != FLASH:
        raise ValueError('mídia exige o Flash validado para esta integração')
    return {
        "system_instruction": {"parts": [{"text": entrada[0]["content"]}]},
        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}] + m.get('midias', [])}
                     for m in entrada[1:]],
        "generationConfig": geracao,
    }


def ler_uso(dados: dict) -> dict:
    uso = dados.get("usageMetadata", {})
    candidato = (dados.get("candidates") or [{}])[0]
    tem_saida = "candidatesTokenCount" in uso or "thoughtsTokenCount" in uso
    return {"entrada": uso.get("promptTokenCount"),
            "saida": ((uso.get("candidatesTokenCount") or 0) + (uso.get("thoughtsTokenCount") or 0)) if tem_saida else None,
            "tokens_resposta": uso.get("candidatesTokenCount"),
            "tokens_raciocinio": uso.get("thoughtsTokenCount", 0) if uso else None,
            "tokens_cache": uso.get("cachedContentTokenCount", 0) if uso else None,
            "fim": candidato.get("finishReason") or dados.get("promptFeedback", {}).get("blockReason"),
            "cortada": candidato.get("finishReason") == "MAX_TOKENS"}


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
                 raciocinio: str | None = RACIOCINIO_PADRAO, argon_max_saida: int = ARGON_MAX_SAIDA,
                 vertex_projeto: str = "", argon_teto_usd: float | None = None,
                 argon_perfil: str = "original", dados: Path | None = None,
                 teto_preco: str = "promocional", gasto_externo_usd: float = 0.0):
        self.fila = [(p, m) for p, m in fila if chaves.get(p)]  # provedor sem chave sai da fila
        self.teto_usd = teto_usd
        if not math.isfinite(teto_usd) or teto_usd < 0:
            raise ValueError("teto de gasto deve ser finito e não negativo")
        if argon_teto_usd is not None and (not math.isfinite(argon_teto_usd) or argon_teto_usd < 0):
            raise ValueError("teto do Argon deve ser finito e não negativo")
        self.argon_teto_usd = argon_teto_usd
        if argon_perfil not in ("original", "compacto-v1", "compacto-v2"):
            raise ValueError("perfil Argon não reconhecido")
        self.argon_perfil, self.dados = argon_perfil, dados
        if teto_preco not in ("cheio", "promocional"):
            raise ValueError("teto_preco deve ser cheio ou promocional")
        if not math.isfinite(gasto_externo_usd) or gasto_externo_usd < 0:
            raise ValueError("gasto externo deve ser finito e não negativo")
        # "cheio" soma pelo preço sem promoção: a fatura pode abater o crédito do mês antes da promoção.
        self.teto_preco, self.gasto_externo_usd = teto_preco, gasto_externo_usd
        self.raciocinio = raciocinio
        self.argon_max_saida = argon_max_saida
        if vertex_projeto and not re.fullmatch(r"[a-zA-Z0-9-]+", vertex_projeto):
            raise ValueError("VERTEX_PROJETO inválido")
        self.vertex_projeto = vertex_projeto
        if not 256 <= argon_max_saida <= 32768:
            raise ValueError("limite de saída do Argon fora de 256..32768")
        self._reservado = 0.0
        self._reservado_argon = 0.0
        # Sem SQLite (testes/uso embutido), ainda contabiliza a sessão até o mês virar.
        self._consumo_local: list[tuple] = []
        self._chaves = chaves
        self._de_molho: dict[tuple[str, str], float] = {}  # (provedor, modelo) -> quando volta, no relógio de time.monotonic
        self._registro = registro
        self._enviar = enviar or _enviar_http

    def gasto_do_mes(self, apenas_modelo: str | None = None, *, preco: str | None = None, externo: bool = True) -> float:
        """Estimativa em US$ do que os provedores pagos já consumiram neste mês, pelo registro, mais as reservas por
        consumo incerto. `preco` "cheio" recalcula pelos tokens sem promoção (padrão: o do teto). O gasto externo
        (GASTO_EXTERNO_USD) entra só na conta global, com `externo`."""
        agora = datetime.now(timezone.utc)
        cheio = (preco or self.teto_preco) == "cheio"
        linhas = (self._registro.consumo_do_mes(agora) if self._registro else
                  [r for r in self._consumo_local if r[1][:7] == agora.strftime("%Y-%m")])
        total = 0.0
        for modelo, data, entrada, saida, cache, custo, reserva in linhas:
            provedor, _, nome = modelo.partition(":")
            if provedor not in PAGOS or (apenas_modelo is not None and nome != apenas_modelo):
                continue
            if cheio or custo is None:
                custo = custo_usd(nome, entrada, saida, int(data[:4]), mes=int(data[5:7]), tokens_cache=cache,
                                  sem_promocao=cheio)
            total += max(custo, reserva or 0.0)
        if externo and apenas_modelo is None:
            total += self.gasto_externo_usd
        return total

    async def responder(self, entrada: list[dict], *, persona: str | None = None, gatilho: str | None = None,
                        so_pagos: bool = False, usar_argon: bool = False) -> Resposta:
        """`so_pagos` deixa de fora o provedor gratuito, que pelos termos do Google pode usar o que recebe pra
        treinar modelo e passar por revisão humana. É pra pedido com mensagem de várias pessoas, como a reflexão diária."""
        base = FILA_REFLEXAO if gatilho == "reflexao" else self.fila
        adicionais_midia = reserva_midia(entrada)
        if adicionais_midia:
            # Piloto com uma única tentativa: não replica anexos no gratuito ou
            # em modelo sem validação. O fluxo textual mantém a fila anterior.
            base, so_pagos = [("vertex", FLASH)], True
        if usar_argon and gatilho != "reflexao" and not adicionais_midia:
            base = [("vertex", ARGON)] + [(p, m) for p, m in base if m != ARGON]
        fila = [(p, m) for p, m in base if self._chaves.get(p) and (not so_pagos or p in PAGOS)]
        if not fila:
            raise Falhou("sem_chave", "nenhum provedor pago da fila tem chave no .env" if so_pagos else "nenhum provedor da fila tem chave no .env")
        ultimo_erro = None
        disponiveis = [par for par in fila if self._de_molho.get(par, 0) <= time.monotonic()]
        if not disponiveis:
            raise Falhou("aguardar", "modelos temporariamente indisponíveis; intervalo de recuperação em andamento")
        prazo = None if gatilho == "reflexao" else time.monotonic() + PRAZO_TOTAL
        for provedor, modelo in disponiveis:
            restante = prazo - time.monotonic() if prazo is not None else None
            if restante is not None and restante < TENTATIVA_MINIMA:
                ultimo_erro = ultimo_erro or Falhou("prazo", f"sem resposta em {PRAZO_TOTAL} s somando a fila")
                break
            pedido = entrada
            if modelo == ARGON and self.argon_perfil != "original":
                try:
                    if self.argon_perfil == "compacto-v2":
                        from .perfil_compacto_v2 import aplicar
                    else:
                        from .perfil_argon import aplicar
                    pedido = aplicar(entrada, persona, self.dados)
                except (ValueError, OSError, KeyError):
                    # Card novo/formato desconhecido exige revisão: nunca envia um perfil desatualizado.
                    ultimo_erro = Falhou("perfil", "perfil compacto incompatível; seguindo para o fallback")
                    log.warning("Argon compacto incompatível com o prompt; tentativa não enviada")
                    continue
            raciocinio = "low" if modelo == ARGON or gatilho == "reflexao" else self.raciocinio
            corpo = montar_corpo(pedido, raciocinio, modelo=modelo, argon_max_saida=self.argon_max_saida)
            # Reserva conservadora para chamadas concorrentes: bytes UTF-8 de texto + saída máxima.
            # Estimativa local, não uma garantia da fatura (timeouts podem ser cobrados sem usageMetadata).
            reserva = custo_usd(modelo, sum(len(m["content"].encode()) for m in pedido) + 256 + adicionais_midia,
                                corpo["generationConfig"]["maxOutputTokens"],
                                sem_promocao=self.teto_preco == "cheio") if provedor in PAGOS else 0.0
            if provedor in PAGOS and self.gasto_do_mes() + self._reservado + reserva > self.teto_usd:
                ultimo_erro = ultimo_erro or Falhou("teto", f"gasto do mês chegou ao teto de US$ {self.teto_usd:.2f}")
                continue
            if (modelo == ARGON and self.argon_teto_usd is not None and
                    self.gasto_do_mes(ARGON) + self._reservado_argon + reserva > self.argon_teto_usd):
                ultimo_erro = ultimo_erro or Falhou("teto", "parcela mensal do Argon atingida")
                continue
            inicio = time.monotonic()
            self._reservado += reserva
            if modelo == ARGON:
                self._reservado_argon += reserva
            uso = {}
            try:
                espera = ARGON_ESPERA if modelo == ARGON else ESPERA_POR_PROVEDOR.get(provedor, ESPERA)
                if restante is not None:
                    espera = min(espera, restante)
                url = URLS[provedor].format(modelo=modelo)
                if provedor == "vertex" and modelo in (ARGON, FLASH) and self.vertex_projeto:
                    url = f"https://aiplatform.googleapis.com/v1/projects/{self.vertex_projeto}/locations/global/publishers/google/models/{modelo}:generateContent"
                try:
                    dados = await asyncio.wait_for(self._enviar(url, corpo, self._chaves[provedor]), espera)
                except asyncio.TimeoutError:
                    raise Falhou("rede", f"sem resposta em {espera:.0f} s")
                uso = ler_uso(dados)
                if adicionais_midia:
                    # Só contagens retornadas pela API; nenhum conteúdo do anexo.
                    modalidades = {str(x.get('modality')): x.get('tokenCount')
                        for x in dados.get('usageMetadata', {}).get('promptTokensDetails', [])
                        if x.get('modality') in ('IMAGE', 'AUDIO', 'TEXT')}
                    log.info('mídia: tokens de entrada por modalidade=%s', modalidades)
                texto, cortada, entrada_tk, saida_tk = ler_resposta(dados)
            except Falhou as erro:
                ultimo_erro = erro
                if erro.codigo in MOLHO:
                    self._de_molho[(provedor, modelo)] = time.monotonic() + MOLHO[erro.codigo]
                self._registrar(provedor, modelo, persona, gatilho, inicio, ok=False, erro=str(erro)[:300],
                                # HTTP 4xx/5xx confirmado não é faturado. Timeout e 200 sem uso completo são incertos.
                                raciocinio=raciocinio, reserva_sem_uso_usd=reserva if erro.codigo in ("rede", "vazio", "bloqueado") else 0,
                                **uso)
                log.warning("modelo: %s:%s falhou (%s)", provedor, modelo, str(erro)[:200])
                continue
            except asyncio.CancelledError:
                self._registrar(provedor, modelo, persona, gatilho, inicio, ok=False,
                                erro="cancelada; consumo não informado", raciocinio=raciocinio, reserva_sem_uso_usd=reserva, **uso)
                raise
            finally:
                self._reservado -= reserva
                if modelo == ARGON:
                    self._reservado_argon -= reserva
            latencia = round((time.monotonic() - inicio) * 1000)
            custo = self._registrar(provedor, modelo, persona, gatilho, inicio, ok=True, raciocinio=raciocinio,
                                    reserva_sem_uso_usd=reserva, **uso)
            return Resposta(texto, provedor, modelo, entrada_tk, saida_tk, latencia, cortada,
                            uso["tokens_resposta"], uso["tokens_raciocinio"], uso["tokens_cache"], uso["fim"], custo)
        ultimo_erro = ultimo_erro or Falhou("prazo", "nenhuma tentativa coube no prazo")
        if ultimo_erro.codigo == "teto":
            log.warning("modelo: teto do mês atingido (US$ %.2f); provedores pagos fora da fila", self.teto_usd)
        raise ultimo_erro

    def _registrar(self, provedor, modelo, persona, gatilho, inicio, *, ok, entrada=None, saida=None, erro=None,
                   raciocinio=None, reserva_sem_uso_usd=0.0, **uso) -> float | None:
        custo = custo_usd(modelo, entrada or 0, saida or 0, tokens_cache=uso.get("tokens_cache") or 0) if entrada is not None or saida is not None else None
        # Uma resposta sem uso completo não prova custo zero. Reserva persistente, separada do gasto medido.
        incerto = reserva_sem_uso_usd if entrada is None or saida is None else 0.0
        if provedor not in PAGOS:
            custo = 0.0
        latencia = round((time.monotonic() - inicio) * 1000)
        if self._registro:
            self._registro.registrar_chamada(modelo=f"{provedor}:{modelo}", persona=persona, gatilho=gatilho,
                                             tokens_entrada=entrada, tokens_saida=saida,
                                             latencia_ms=latencia, ok=ok, erro=erro, raciocinio=raciocinio,
                                             custo_estimado_usd=custo, reserva_sem_uso_usd=incerto, **uso)
        else:
            self._consumo_local.append((f"{provedor}:{modelo}", datetime.now(timezone.utc).isoformat(),
                                        entrada or 0, saida or 0, uso.get("tokens_cache") or 0,
                                        custo, incerto))
        log.info("modelo=%s:%s ok=%s entrada=%s resposta=%s raciocinio=%s cache=%s fim=%s ms=%s custo_usd=%s",
                 provedor, modelo, ok, entrada, uso.get("tokens_resposta"), uso.get("tokens_raciocinio"),
                 uso.get("tokens_cache"), uso.get("fim"), latencia, custo)
        if incerto:
            log.warning("modelo=%s:%s consumo incompleto; reserva cautelar_usd=%.6f (não é cobrança confirmada)",
                        provedor, modelo, incerto)
        return custo


async def _enviar_http(url: str, corpo: dict, chave: str) -> dict:
    import asyncio

    import aiohttp  # já vem com o discord.py

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=max(ESPERA, ARGON_ESPERA, *ESPERA_POR_PROVEDOR.values()))) as sessao:
            # a chave vai no cabeçalho, não na URL, pra não aparecer em registro de acesso
            async with sessao.post(url, json=corpo, headers={"x-goog-api-key": chave}) as resposta:
                if resposta.status != 200:
                    if any(p.get('inlineData') for c in corpo.get('contents', []) for p in c.get('parts', [])):
                        # Erros do provedor podem ecoar o pedido: nunca grave
                        # base64 ou conteúdo de um anexo nos logs/banco.
                        raise Falhou(resposta.status, 'pedido com mídia recusado pelo provedor')
                    motivo = (await resposta.text()).replace(chave, "[chave omitida]")
                    motivo = re.sub(r"projects/[^/`\s]+", "projects/[omitido]", motivo)
                    raise Falhou(resposta.status, motivo[:3000].replace("\n", " "))
                return await resposta.json()
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as erro:
        raise Falhou("rede", str(erro))
