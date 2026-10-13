"""A conversa em andamento com cada personagem em cada canal, só na memória do programa.

Entra aqui só o que faz parte da conversa com ela: a mensagem de quem a chamou e a resposta dela. O resto do
canal não entra. Meia hora sem ninguém falar com ela e a conversa acaba; reiniciar o bot também zera.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta

DURA = timedelta(minutes=30)
TURNOS_MAX = 12


@dataclass(frozen=True)
class Turno:
    quando: datetime
    texto: str
    nome: str | None = None  # de quem falou com ela; None quando a fala é dela


class Conversas:
    def __init__(self):
        self._turnos: dict[tuple[int, str], deque[Turno]] = {}

    def turnos(self, canal_id: int, persona: str, agora: datetime) -> list[Turno]:
        fila = self._turnos.get((canal_id, persona))
        if fila and agora - fila[-1].quando > DURA:
            fila.clear()
        return list(fila or ())

    def anotar(self, canal_id: int, persona: str, agora: datetime, texto: str, nome: str | None = None) -> None:
        self.turnos(canal_id, persona, agora)  # fecha a conversa velha antes de começar outra
        self._turnos.setdefault((canal_id, persona), deque(maxlen=TURNOS_MAX)).append(Turno(agora, texto, nome))
