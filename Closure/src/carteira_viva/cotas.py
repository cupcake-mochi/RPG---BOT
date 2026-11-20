"""Limites locais conservadores de leituras Sheets; sem sondar/exaurir cota real."""
import asyncio
from collections import deque
import time


class Cotas:
    def __init__(self, *, conta=45, projeto=240, janela=60, agora=time.monotonic):
        self.por_conta, self.projeto, self.janela, self.agora = conta, projeto, janela, agora
        self.contas = {}
        self.total = deque()
        self.lock = asyncio.Lock()

    async def esperar(self, conta):
        while True:
            async with self.lock:
                agora = self.agora()
                while self.total and self.total[0] <= agora-self.janela:
                    self.total.popleft()
                for chave, fila in list(self.contas.items()):
                    while fila and fila[0] <= agora-self.janela:
                        fila.popleft()
                    if not fila:
                        del self.contas[chave]
                fila = self.contas.setdefault(conta, deque())
                espera = max(fila[0]+self.janela-agora if len(fila)>=self.por_conta else 0,
                             self.total[0]+self.janela-agora if len(self.total)>=self.projeto else 0)
                if espera <= 0:
                    fila.append(agora); self.total.append(agora)
                    return
            await asyncio.sleep(espera)
