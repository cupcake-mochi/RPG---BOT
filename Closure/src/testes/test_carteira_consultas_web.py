"""Rotas internas: a ponte autentica, o servidor confere membro e capacidade."""
import asyncio
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from aiohttp.test_utils import TestClient, TestServer
from carteira_viva.motor import Motor
from carteira_viva.permissoes import Membro
from carteira_viva.web import criar_app, DADOS, LIMITE
from testes.test_carteira_consultas import GoogleFicticio
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_web import F1


class ConsultasHTTPTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory(); p=Path(self.tmp.name)
        self.cfg=configuracao(p/"db.sqlite3")
        self.prov=GoogleFicticio(self.cfg,lambda:180000.)
        self.campanhas=p/"campanhas.json"; self.campanhas.write_text("{}")
        motor=Motor(Path(__file__).resolve().parents[2]/"dados",self.campanhas)
        self.app=criar_app(self.cfg,provedores=self.prov,motor=motor)
        self.client=TestClient(TestServer(self.app,handler_cancellation=True)); await self.client.start_server()
        m=Membro("111","222")
        cid=await self.app[DADOS].chamar("cadastro.conectar",m,conta="ficticia",cliente=self.cfg.google_id,refresh_token="ficticio")
        p=await self.app[DADOS].chamar("cadastro.cadastrar",m,conexao=cid,arquivo=F1,nome="QA",contrato="analise-12",responsabilidade=True,pedido="ficticio")
        self.url="/interno/personagens/"+p["id"]+"/"
        self.headers={"Authorization":"Bearer "+self.cfg.servico_token}
        self.ctx={"servidor":"111","usuario":"222"}
    async def asyncTearDown(self):
        await self.client.close(); self.tmp.cleanup()

    async def post(self,acao,**kw):
        return await self.client.post(self.url+acao,json=kw.get("data",self.ctx),headers=kw.get("headers",self.headers))

    async def test_sem_bearer_e_nao_dono_nao_leem(self):
        self.assertEqual((await self.post("atualizar",headers={})).status,403)
        self.assertEqual((await self.post("atualizar",data=self.ctx|{"usuario":"999"})).status,403)
        self.assertEqual(self.prov.leituras,0)

    async def test_cliente_nao_injeta_campanha_ou_metodo(self):
        self.assertEqual((await self.post("analisar",data=self.ctx|{"campanha":{"aprovados":"tudo"}})).status,400)
        self.assertEqual((await self.post("apagar_usuario")).status,404)
        self.assertEqual(self.prov.leituras,0)

    async def test_resposta_privada_e_atualizacao_so_metadados(self):
        r=await self.post("atualizar"); d=await r.json()
        self.assertEqual(r.status,200); self.assertEqual(r.headers["Cache-Control"],"private, no-store")
        self.assertIn("leitura_id",d); self.assertNotIn("ficha",d); self.assertNotIn("refresh",str(d))
        r=await self.post("analisar"); d=await r.json()
        self.assertEqual(r.status,200); self.assertEqual(d["campanha"]["servidor"],"111")
        self.assertEqual((await self.post("analise")).status,200)
        self.campanhas.write_text('{"111":{"nome":"mudou"}}')
        self.assertEqual((await self.post("analise")).status,409)

    async def test_saude_nao_espera_vagas_de_leitura(self):
        sem=self.app[LIMITE]
        for _ in range(8): await sem.acquire()
        try:
            r=await asyncio.wait_for(self.client.get("/saude"),1)
            self.assertEqual(r.status,200)
            self.assertEqual((await self.post("atualizar")).status,429)
        finally:
            for _ in range(8): sem.release()
