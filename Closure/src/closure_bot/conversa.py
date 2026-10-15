"""Últimos 12 turnos por canal/personagem, por 30 minutos sem conversa.

Com Registro, sobrevive ao reinício e usa a mesma cifra do banco. O texto
expira no máximo às próximas 4h30. Sem Registro, serve a simulações locais.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, time
from .plantao import FUSO

DURA = timedelta(minutes=30)
TURNOS_MAX = 12


@dataclass(frozen=True)
class Turno:
    quando: datetime
    texto: str
    nome: str | None = None
    autor_id: int | None = None  # apenas local, nunca vai ao modelo
    midia: str = ''


def prazo(turnos: list[Turno]) -> datetime:
    inicio = turnos[0].quando.astimezone(FUSO)
    corte = datetime.combine(inicio.date(), time(4, 30), tzinfo=FUSO)
    if corte <= inicio:
        corte += timedelta(days=1)
    return min(turnos[-1].quando + DURA, corte)


class Conversas:
    def __init__(self, registro=None):
        self.registro = registro
        self._turnos: dict[tuple[int, str], deque[Turno]] = {}

    def limpar(self, agora: datetime) -> None:
        if self.registro is not None:
            self.registro.limpar_conversas(agora)
        for chave, fila in list(self._turnos.items()):
            if fila and prazo(list(fila)) <= agora:
                del self._turnos[chave]

    def turnos(self, canal_id: int, persona: str, agora: datetime) -> list[Turno]:
        if self.registro is not None:
            return [Turno(**{**t, 'quando': datetime.fromisoformat(t['quando'])})
                    for t in self.registro.ler_conversa(canal_id, persona, agora)]
        self.limpar(agora)
        return list(self._turnos.get((canal_id, persona), ()))

    def anotar(self, canal_id: int, persona: str, agora: datetime, texto: str, nome: str | None = None,
               *, autor_id: int | None = None, midia: str = '') -> None:
        fila = deque(self.turnos(canal_id, persona, agora), maxlen=TURNOS_MAX)
        fila.append(Turno(agora, texto, nome, autor_id, midia))
        if self.registro is not None:
            self.registro.guardar_conversa(canal_id, persona,
                [{**asdict(t), 'quando': t.quando.isoformat()} for t in fila], prazo(list(fila)))
        else:
            self._turnos[canal_id, persona] = fila
