"""Quem responde a uma mensagem: a regra de plantão das duas personagens.

Dono da regra: dados/personagem/servidor.md (turnos) e os vida.md das duas. Resumo do que está lá:
  - Kal'tsit das 9h às 21h, Closure das 21h às 9h, horário de Brasília. Troca sem anúncio.
  - Elas só aparecem quando chamadas: nome na mensagem, menção ao bot ou resposta a uma mensagem do bot.
  - Sem nome na mensagem, responde quem está de plantão.
  - Chamada pelo nome fora do turno, a própria responde (curto: o lembrete ganha a linha de fora do plantão).
  - As duas nunca respondem à mesma mensagem.

Este módulo não conhece o Discord: recebe texto e hora, devolve a decisão.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")

KALTSIT = "kaltsit"
CLOSURE = "closure"

# [início, fim) em horas de Brasília; fora disso o plantão é da Closure
INICIO_KALTSIT, FIM_KALTSIT = 9, 21

# Como cada uma é chamada no chat, já sem acento e em minúsculo
APELIDOS = {
    KALTSIT: ("kal'tsit", "kaltsit", "kal"),
    CLOSURE: ("closure",),
}

MOTIVO_NOME = "nome"
MOTIVO_MENCAO = "mencao"
MOTIVO_RESPOSTA = "resposta"
MOTIVO_SEGUIMENTO = "seguimento"  # quem ela acabou de responder continua falando, sem chamar (cogs/chat.py)


@dataclass(frozen=True)
class Decisao:
    persona: str
    motivo: str
    fora_do_plantao: bool


def de_plantao(agora: datetime) -> str:
    """Quem está de plantão no instante dado (com fuso; sem fuso é lido como Brasília)."""
    local = agora.astimezone(FUSO) if agora.tzinfo else agora.replace(tzinfo=FUSO)
    return KALTSIT if INICIO_KALTSIT <= local.hour < FIM_KALTSIT else CLOSURE


def _normalizar(texto: str) -> str:
    texto = texto.lower()
    for aspa in "’‘`´":
        texto = texto.replace(aspa, "'")
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def _primeira_posicao(texto_norm: str, persona: str) -> int | None:
    posicoes = []
    for apelido in APELIDOS[persona]:
        achou = re.search(r"(?<![\w'])" + re.escape(apelido) + r"(?![\w'])", texto_norm)
        if achou:
            posicoes.append(achou.start())
    return min(posicoes) if posicoes else None


def nomes_chamados(texto: str) -> list[str]:
    """Personagens citadas pelo nome, na ordem em que aparecem."""
    norm = _normalizar(texto)
    achadas = [(pos, p) for p in (KALTSIT, CLOSURE) if (pos := _primeira_posicao(norm, p)) is not None]
    return [p for _, p in sorted(achadas)]


def _vocativo(texto: str) -> str | None:
    """A personagem cujo nome abre a mensagem ("closure, ..."), ignorando menção e pontuação do começo."""
    norm = re.sub(r"^(\s|<@!?\d+>|[^\w'])+", "", _normalizar(texto))
    for persona, apelidos in APELIDOS.items():
        for apelido in apelidos:
            if re.match(re.escape(apelido) + r"(?![\w'])", norm):
                return persona
    return None


def decidir(texto: str, agora: datetime, *, mencionou_bot: bool = False, respondeu_ao_bot: bool = False,
            respondeu_a: str | None = None) -> Decisao | None:
    """Devolve quem responde, ou None se ninguém foi chamado. `respondeu_a` é a personagem dona da mensagem respondida,
    quando se sabe; nome escrito na mensagem vale mais que isso."""
    plantao = de_plantao(agora)
    citadas = nomes_chamados(texto)

    if len(citadas) == 1:
        persona = citadas[0]
    elif len(citadas) == 2:
        # As duas citadas: fala-se com uma sobre a outra. Vale quem abre a mensagem; sem isso, quem está de plantão.
        persona = _vocativo(texto) or plantao
    elif respondeu_a in APELIDOS:
        persona = respondeu_a  # respondeu a uma fala dela: é ela quem continua, mesmo fora do plantão
    elif mencionou_bot or respondeu_ao_bot:
        persona = plantao
    else:
        return None

    motivo = MOTIVO_NOME if citadas else (MOTIVO_MENCAO if mencionou_bot else MOTIVO_RESPOSTA)
    return Decisao(persona=persona, motivo=motivo, fora_do_plantao=persona != plantao)
