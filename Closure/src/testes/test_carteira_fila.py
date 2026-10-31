import asyncio
import unittest
from carteira_viva.fila import Fila, Ocupado

class FilaTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self): self.fila=Fila(paralelos=1, prazo=1, espera=2)
    async def asyncTearDown(self): await self.fila.fechar()

    async def test_coalescencia(self):
        chamadas=[]; liberar=asyncio.Event()
        async def job(): chamadas.append(1); await liberar.wait(); return 42
        ts=[asyncio.create_task(self.fila.executar(("igual",),("mesa","u"),job)) for _ in range(20)]
        await asyncio.sleep(.02); liberar.set()
        self.assertEqual(await asyncio.gather(*ts),[42]*20); self.assertEqual(len(chamadas),1)

    async def test_cancelar_um_preserva_demais(self):
        liberar=asyncio.Event()
        async def job(): await liberar.wait(); return 42
        a=asyncio.create_task(self.fila.executar((1,),(1,),job)); b=asyncio.create_task(self.fila.executar((1,),(1,),job))
        await asyncio.sleep(.01); a.cancel()
        with self.assertRaises(asyncio.CancelledError): await a
        liberar.set(); self.assertEqual(await b,42)

    async def test_ultimo_cliente_cancela_job(self):
        terminou=asyncio.Event()
        async def job():
            try: await asyncio.Event().wait()
            finally: terminou.set()
        a=asyncio.create_task(self.fila.executar((1,),(1,),job)); await asyncio.sleep(.01); a.cancel()
        with self.assertRaises(asyncio.CancelledError): await a
        await asyncio.wait_for(terminou.wait(),1)

    async def test_justica(self):
        liberar=asyncio.Event(); ordem=[]
        async def primeiro(): await liberar.wait()
        async def job(x): ordem.append(x)
        a=asyncio.create_task(self.fila.executar((0,),("a",),primeiro)); await asyncio.sleep(.01)
        ts=[asyncio.create_task(self.fila.executar((i,), (g,),lambda i=i: job(i))) for i,g in [(1,"a"),(2,"a"),(3,"b"),(4,"c")]]
        await asyncio.sleep(.01); liberar.set(); await asyncio.gather(a,*ts)
        self.assertEqual(ordem,[1,3,4,2])

    async def test_limite_e_cancelar_espera(self):
        self.fila.por_grupo=1
        async def job(): await asyncio.Event().wait()
        a=asyncio.create_task(self.fila.executar((1,),(1,),job)); await asyncio.sleep(.01)
        with self.assertRaises(Ocupado): await self.fila.executar((2,),(1,),job)
        b=asyncio.create_task(self.fila.executar((2,),(2,),job)); await asyncio.sleep(.01); b.cancel()
        with self.assertRaises(asyncio.CancelledError): await b
        self.assertNotIn((2,),self.fila.pedidos)
        a.cancel(); await asyncio.gather(a,return_exceptions=True)

    async def test_timeout_libera(self):
        self.fila.prazo=.02
        async def job(): await asyncio.Event().wait()
        with self.assertRaises(Ocupado): await self.fila.executar((1,),(1,),job)
        async def pronto(): return 2
        self.assertEqual(await self.fila.executar((2,),(2,),pronto),2)

    async def test_erro_e_fechar(self):
        async def falhar(): raise ValueError("ficticio")
        with self.assertRaises(ValueError): await self.fila.executar((1,),(1,),falhar)
        await self.fila.fechar()
        with self.assertRaises(Ocupado): await self.fila.executar((1,),(1,),falhar)

    async def test_limite_total(self):
        self.fila.limite=1
        async def job(): await asyncio.Event().wait()
        a=asyncio.create_task(self.fila.executar((1,),(1,),job)); await asyncio.sleep(.01)
        with self.assertRaises(Ocupado): await self.fila.executar((2,),(2,),job)
        a.cancel(); await asyncio.gather(a,return_exceptions=True)

    async def test_dois_trabalhadores_nao_sao_ocupados_pelo_mesmo_ator(self):
        self.fila.paralelos=2; liberar=asyncio.Event(); iniciou=[]
        async def job(i): iniciou.append(i); await liberar.wait()
        ts=[asyncio.create_task(self.fila.executar((i,),(g,),lambda i=i:job(i))) for i,g in [(1,"a"),(2,"a"),(3,"b")]]
        await asyncio.sleep(.02); self.assertEqual(iniciou,[1,3]); liberar.set(); await asyncio.gather(*ts)


class CotasTeste(unittest.IsolatedAsyncioTestCase):
    async def test_limites_por_conta_e_projeto(self):
        from carteira_viva.cotas import Cotas
        c=Cotas(conta=1,projeto=2,janela=.03)
        await c.esperar("a"); await c.esperar("b")
        t=asyncio.get_running_loop().time(); await c.esperar("c")
        self.assertGreaterEqual(asyncio.get_running_loop().time()-t,.02)
        t=asyncio.get_running_loop().time(); await c.esperar("c")
        self.assertGreaterEqual(asyncio.get_running_loop().time()-t,.02)

class PrazosFilaTeste(unittest.IsolatedAsyncioTestCase):
    async def test_prazo_maior_somente_para_pedido_especifico(self):
        f=Fila(prazo=.01,espera=.2)
        async def lento(): await asyncio.sleep(.04); return 7
        try:
            self.assertEqual(await f.executar(('especial',),('a',),lento,prazo=.1,espera=.3),7)
            with self.assertRaises(Ocupado): await f.executar(('comum',),('b',),lento)
            self.assertEqual(f.prazo,.01); self.assertEqual(f.espera,.2)
        finally: await f.fechar()

    async def test_prazos_invalidos_recusados_antes_da_fila(self):
        f=Fila()
        async def job(): raise AssertionError('não executar')
        try:
            for v in (True,0,-1,float('inf'),float('nan'),1801,2**4096,'60'):
                for k in ('prazo','espera'):
                    with self.subTest(v=v,k=k),self.assertRaises(Ocupado):
                        await f.executar(('invalido',),('a',),job,**{k:v})
            self.assertFalse(f.pedidos)
        finally: await f.fechar()

    async def test_coalescencia_nao_estende_prazo_existente(self):
        f=Fila(); entrou=asyncio.Event(); liberar=asyncio.Event()
        async def job(): entrou.set(); await liberar.wait(); return 1
        a=asyncio.create_task(f.executar(('igual',),('a',),job,prazo=1))
        try:
            await entrou.wait()
            with self.assertRaises(Ocupado): await f.executar(('igual',),('a',),job,prazo=2)
            liberar.set(); self.assertEqual(await a,1)
        finally: await f.fechar()
