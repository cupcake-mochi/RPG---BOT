"""Fila em memória limitada, justa por servidor/usuário, com coalescência."""
import asyncio
from collections import OrderedDict, deque
from dataclasses import dataclass

from .segredos import ErroCarteira


class Ocupado(ErroCarteira):
    codigo = "limite"


@dataclass
class Pedido:
    chave: tuple
    grupo: tuple
    executar: object
    resultado: asyncio.Future
    clientes: int = 0
    tarefa: asyncio.Task | None = None


class Fila:
    def __init__(self, *, paralelos=2, limite=32, por_grupo=4, prazo=60, espera=90):
        self.paralelos, self.limite, self.por_grupo = paralelos, limite, por_grupo
        self.prazo, self.espera = prazo, espera
        self.pedidos = {}
        self.grupos = OrderedDict()
        self.ativos = set()
        self.fechada = False

    async def executar(self, chave, grupo, funcao):
        if self.fechada:
            raise Ocupado("A leitura está encerrando. Tente novamente depois.")
        p = self.pedidos.get(chave)
        if p and p.resultado.cancelled() and p.tarefa:
            # O último cliente desistiu, mas o job ainda está limpando a fonte.
            # Esperar essa limpeza impede que ela invalide o pedido substituto.
            await asyncio.shield(p.tarefa)
            p = self.pedidos.get(chave)
        if p is None:
            if (len(self.pedidos) >= self.limite or
                    sum(p.grupo == grupo for p in self.pedidos.values()) >= self.por_grupo):
                raise Ocupado("Há consultas demais em espera. Tente novamente em instantes.")
            futuro = asyncio.get_running_loop().create_future()
            futuro.add_done_callback(lambda f: f.exception() if not f.cancelled() else None)
            p = Pedido(chave, grupo, funcao, futuro)
            self.pedidos[chave] = p
            self.grupos.setdefault(grupo, deque()).append(p)
        if p.clientes >= 64:
            raise Ocupado("Esta consulta já tem muitas solicitações em andamento.")
        p.clientes += 1
        self._iniciar()
        try:
            return await asyncio.wait_for(asyncio.shield(p.resultado), self.espera)
        except TimeoutError:
            raise Ocupado("A consulta demorou demais. Tente novamente em instantes.") from None
        finally:
            p.clientes -= 1
            if not p.clientes and not p.resultado.done():
                p.resultado.cancel()
                if p.tarefa:
                    p.tarefa.cancel()
                else:
                    self.grupos[p.grupo].remove(p)
                    if not self.grupos[p.grupo]:
                        del self.grupos[p.grupo]
                    self.pedidos.pop(chave, None)

    def _iniciar(self):
        while len(self.ativos) < self.paralelos and self.grupos:
            # Um ator não ocupa os dois trabalhadores. Grupos giram a cada saída.
            ocupados = {self.pedidos[k].grupo for k in self.ativos}
            disponivel = next((g for g in self.grupos if g not in ocupados), None)
            if disponivel is None:
                break
            fila = self.grupos.pop(disponivel)
            p = fila.popleft()
            if fila:
                self.grupos[disponivel] = fila
            self.ativos.add(p.chave)
            p.tarefa = asyncio.create_task(self._rodar(p))

    async def _rodar(self, p):
        try:
            async with asyncio.timeout(self.prazo):
                valor = await p.executar()
            if not p.resultado.done():
                p.resultado.set_result(valor)
        except asyncio.CancelledError:
            p.resultado.cancel()
        except Exception as exc:
            if not p.resultado.done():
                p.resultado.set_exception(exc)
        finally:
            self.ativos.discard(p.chave)
            self.pedidos.pop(p.chave, None)
            self._iniciar()

    async def fechar(self):
        self.fechada = True
        tarefas = []
        for p in list(self.pedidos.values()):
            p.resultado.cancel()
            if p.tarefa:
                p.tarefa.cancel()
                tarefas.append(p.tarefa)
        self.grupos.clear()
        await asyncio.gather(*tarefas, return_exceptions=True)
        self.pedidos.clear()
