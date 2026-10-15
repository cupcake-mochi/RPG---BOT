"""Configuração do bot: lê o .env da raiz do Closure (o ambiente vence o arquivo) e resolve os caminhos.

Variáveis (modelo em .env.exemplo, na raiz do repositório):
  DISCORD_TOKEN    token do app no Discord. Sem ele o bot não sobe.
  GUILD_ID         servidor principal. Os comandos valem em todo servidor; aqui o bot só apaga comando antigo que
                   tenha ficado registrado só nesse servidor, pra não aparecer em dobro.
  DONO_ID          ID de quem pode usar os comandos de administração (o do Mizuki está em dados/personagem/servidor.md).
  CANAIS           IDs dos canais em que basta escrever o nome delas, separados por vírgula. Vazio = todos.
                   Fora desses, elas só respondem a quem marca o bot ou responde a uma mensagem dele.
  POLITICA_URL     link público da política de privacidade (o texto é o docs/PRIVACIDADE.md). Aparece no fim do /meus_dados.
  LIVRO_URL        link do livro de regras em PDF, que o /livro e o GC:livro mandam. Padrão: o do site do sistema.
  TERMOS_URL       link público dos termos de uso (o texto é o docs/TERMOS.md). Aparece no /ajuda, junto do da política.
  CLIMA_CANAIS     IDs de canais que já nascem com o painel diário de clima, um por servidor. O comando
                   /clima_canal faz o mesmo de dentro do Discord; isto é pra não depender dele na primeira subida.
  AVATAR_KALTSIT   URL da imagem que aparece nas mensagens da Kal'tsit.
  AVATAR_CLOSURE   URL da imagem que aparece nas mensagens da Closure.
  VERTEX_API_KEY   chave de API do Google Cloud pra Vertex AI (projeto do bot). É onde o crédito mensal abate.
  GEMINI_API_KEY   chave gratuita do AI Studio. Reserva e testes.
  FILA_MODELOS     "provedor:modelo,..." em ordem de tentativa. Padrão em modelo.FILA_PADRAO (gratuito primeiro).
  MODELO_CHAT      vazio preserva FILA_MODELOS; gemini-4-argon ativa Vertex Argon com Flash de reserva;
                   gemini-3.8-flash escolhe a fila padrão; misto limita Argon a ARGON_CANAIS.
  ARGON_CANAIS     IDs dos canais selecionados no modo misto; vazio não ativa nenhum.
  ARGON_TETO_USD   parcela máxima do teto global para Argon, padrão US$ 1; zero desativa.
  ARGON_PERFIL     original (padrão), compacto-v1 ou compacto-v2 experimental; Flash preserva o prompt completo.
  ARGON_MAX_SAIDA  limite conjunto de raciocínio e resposta do Argon (padrão 4096, entre 256 e 32768).
  VERTEX_PROJETO   ID/número do projeto para chamar Argon e Flash 3.8 explicitamente em locations/global.
  RACIOCINIO       quanto o modelo pensa antes de falar: low, medium, high, ou "modelo" pro padrão do próprio
                   modelo. Vazio = low (modelo.RACIOCINIO_PADRAO).
  TETO_MENSAL_USD  quanto os provedores pagos podem gastar por mês, em dólar, antes de saírem da fila. Padrão: 9.
  TETO_PRECO       como o teto soma o gasto: "cheio" (padrão) pelo preço de tabela sem promoção, ou "promocional".
                   Cheio é o lado seguro enquanto a fatura não mostrar como o crédito do mês abate a promoção.
  GASTO_EXTERNO_USD gasto do mês que o bot não vê (baterias e testes rodados em outro banco), lido na fatura e
                   atualizado à mão. Entra no teto global; não entra no do Argon. Vazio = 0.
  BANCO            caminho do SQLite de registro. Padrão: src/var/bot.sqlite3.
  CHAVE_DO_BANCO   chave que cifra no disco o texto que fala de gente. Cria com: python3 -m closure_bot --gerar-chave.
                   Perder a chave é perder as fichas e as falas guardadas.
"""
from __future__ import annotations

import os
import math
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # a pasta Closure/
DADOS = RAIZ / "dados"


def ler_env(arquivo: Path) -> dict[str, str]:
    """Lê linhas CHAVE=valor; ignora vazias e comentários, tira aspas em volta do valor."""
    if not arquivo.exists():
        return {}
    pares = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        pares[chave.strip()] = valor.strip().strip("\"'")
    return pares


def _inteiro(valor: str | None) -> int | None:
    return int(valor) if valor and valor.strip().isdigit() else None


def _decimal(valor: str | None) -> float | None:
    if not valor or not valor.strip():
        return None
    numero = float(valor.replace(",", "."))
    if not math.isfinite(numero) or numero < 0:
        raise ValueError("teto de gasto deve ser finito e não negativo")
    return numero


LIVRO_PADRAO = "https://ciclo-maldito.vercel.app/livro/Ciclo-Maldito-Livro-de-Regras.pdf"


@dataclass(frozen=True)
class Config:
    token: str
    guild_id: int | None
    dono_id: int | None
    canais: frozenset[int]
    avatares: dict[str, str | None]
    chaves: dict[str, str]
    fila_modelos: str
    teto_mensal_usd: float | None
    raciocinio: str | None
    banco: Path
    dados: Path = DADOS
    chave_do_banco: str | None = None
    clima_canais: tuple[int, ...] = ()
    politica_url: str | None = None
    termos_url: str | None = None
    modelo_chat: str = ""
    argon_max_saida: int = 4096
    vertex_projeto: str = ""
    argon_canais: frozenset[int] = frozenset()
    argon_teto_usd: float = 1.0
    argon_perfil: str = "original"
    teto_preco: str = "cheio"
    livro_url: str = LIVRO_PADRAO
    gasto_externo_usd: float = 0.0
    midia_ativa: bool = False
    midia_canais: frozenset[int] = frozenset()

    def escuta(self, canal_id: int) -> bool:
        return not self.canais or canal_id in self.canais

    def usa_argon(self, canal_id: int) -> bool:
        """Seleção explícita por canal; nenhum texto do usuário ativa o modelo pago."""
        return self.modelo_chat == "misto" and canal_id in self.argon_canais


def carregar(arquivo: Path | None = None, ambiente: dict[str, str] | None = None) -> Config:
    valores = ler_env(arquivo or RAIZ / ".env")
    valores.update(os.environ if ambiente is None else ambiente)
    canais = frozenset(int(c) for c in valores.get("CANAIS", "").replace(" ", "").split(",") if c.isdigit())
    modelo_chat = valores.get("MODELO_CHAT", "").strip()
    if modelo_chat not in ("", "gemini-3.8-flash", "gemini-4-argon", "misto"):
        raise ValueError("MODELO_CHAT deve ser gemini-3.8-flash, gemini-4-argon ou misto")
    canais_argon = valores.get("ARGON_CANAIS", "").replace(" ", "")
    midia = valores.get("MIDIA_ATIVA", "0").strip().lower()
    if midia not in ('0', '1', 'false', 'true'):
        raise ValueError('MIDIA_ATIVA deve ser 0 ou 1')
    canais_midia = valores.get('MIDIA_CANAIS', '').replace(' ', '')
    if canais_midia and any(not c.isdigit() or int(c) <= 0 for c in canais_midia.split(',')):
        raise ValueError('MIDIA_CANAIS deve conter IDs positivos separados por vírgula')
    if canais_argon and any(not c.isdigit() or int(c) <= 0 for c in canais_argon.split(",")):
        raise ValueError("ARGON_CANAIS deve conter IDs positivos separados por vírgula")
    teto_argon = _decimal(valores.get("ARGON_TETO_USD"))
    perfil = valores.get("ARGON_PERFIL", "").strip() or "original"
    if perfil not in ("original", "compacto-v1", "compacto-v2"):
        raise ValueError("ARGON_PERFIL deve ser original, compacto-v1 ou compacto-v2")
    teto_preco = valores.get("TETO_PRECO", "").strip().lower() or "cheio"
    if teto_preco not in ("cheio", "promocional"):
        raise ValueError("TETO_PRECO deve ser cheio ou promocional")
    limite = int(valores.get("ARGON_MAX_SAIDA") or 4096)
    if not 256 <= limite <= 32768:
        raise ValueError("ARGON_MAX_SAIDA deve ficar entre 256 e 32768")
    return Config(
        token=valores.get("DISCORD_TOKEN", ""),
        guild_id=_inteiro(valores.get("GUILD_ID")),
        dono_id=_inteiro(valores.get("DONO_ID")),
        canais=canais,
        avatares={
            "kaltsit": valores.get("AVATAR_KALTSIT") or None,
            "closure": valores.get("AVATAR_CLOSURE") or None,
        },
        chaves={"vertex": valores.get("VERTEX_API_KEY", ""), "gemini": valores.get("GEMINI_API_KEY", "")},
        fila_modelos=valores.get("FILA_MODELOS", ""),
        teto_mensal_usd=_decimal(valores.get("TETO_MENSAL_USD")),
        raciocinio=valores.get("RACIOCINIO", "").strip().lower() or None,
        banco=Path(valores.get("BANCO") or RAIZ / "src" / "var" / "bot.sqlite3"),
        chave_do_banco=valores.get("CHAVE_DO_BANCO") or None,
        politica_url=valores.get("POLITICA_URL") or None,
        termos_url=valores.get("TERMOS_URL") or None,
        clima_canais=tuple(int(c) for c in valores.get("CLIMA_CANAIS", "").replace(" ", "").split(",") if c.isdigit()),
        modelo_chat=modelo_chat,
        argon_max_saida=limite,
        vertex_projeto=valores.get("VERTEX_PROJETO", "").strip(),
        argon_canais=frozenset(int(c) for c in canais_argon.split(",") if c),
        argon_teto_usd=teto_argon if teto_argon is not None else 1.0,
        argon_perfil=perfil,
        teto_preco=teto_preco,
        livro_url=valores.get("LIVRO_URL", "").strip() or LIVRO_PADRAO,
        gasto_externo_usd=_decimal(valores.get("GASTO_EXTERNO_USD")) or 0.0,
        midia_ativa=midia in ('1', 'true'),
        midia_canais=frozenset(int(c) for c in canais_midia.split(',') if c),
    )
