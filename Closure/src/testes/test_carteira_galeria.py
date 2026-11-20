"""Rotas da galeria com SQLite/cifra/HTTP reais e identidades simuladas."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from aiohttp.test_utils import TestClient,TestServer
from carteira_viva.permissoes import Membro
from carteira_viva.provedores import MembroAusente,ErroProvedor
from carteira_viva.web import criar_app,DADOS,GALERIA
from carteira_viva.motor import Motor
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_consultas import GoogleFicticio
from testes.test_carteira_web import F1,F2
from testes.test_carteira_imagens import png


class ProvedorGaleria(GoogleFicticio):
    def __init__(self,cfg,agora):
        super().__init__(cfg,agora);self.pessoas={'222':Membro('111','222'),'999':Membro('111','999'),'777':Membro('111','777',cargos=frozenset({'888'})),'555':Membro('111','555',administrador=True)};self.ausentes=set();self.erro_membro=None
    async def membro(self,s,u):
        if self.erro_membro:raise self.erro_membro
        if s not in self.cfg.servidores or u not in self.pessoas or u in self.ausentes:raise MembroAusente('ficticio')
        return replace(self.pessoas[u],servidor=s)


class GaleriaHTTPTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.pasta=Path(self.tmp.name);self.cfg=configuracao(self.pasta/'db.sqlite3',servidores=frozenset({'111','333'}))
        self.clock=[180000.];self.prov=ProvedorGaleria(self.cfg,lambda:self.clock[0]);camp=self.pasta/'campanhas.json';camp.write_text('{}')
        self.app=criar_app(self.cfg,provedores=self.prov,motor=Motor(Path(__file__).parents[2]/'dados',camp),agora=lambda:self.clock[0])
        self.client=TestClient(TestServer(self.app));await self.client.start_server();self.m=self.prov.pessoas['222']
        self.cid=await self.b('conectar',self.m,conta='ficticia',cliente=self.cfg.google_id,refresh_token='ficticio')
        self.p=await self.b('cadastrar',self.m,conexao=self.cid,arquivo=F1,nome='Exemplo',contrato='analise-12',responsabilidade=True,pedido='primeiro');self.pid=self.p['id']
    async def asyncTearDown(self):await self.client.close();self.tmp.cleanup()
    async def b(self,metodo,*args,**kw):return await self.app[DADOS].chamar('cadastro.'+metodo,*args,**kw)
    async def post(self,acao='',*,usuario='222',servidor='111',pid=None,auth=True,**kw):
        url='/interno/galeria'+('/'+(pid or self.pid)+'/'+acao if acao and acao!='cargo_revisor' else '/acao/cargo_revisor' if acao else '')
        return await self.client.post(url,json={'servidor':servidor,'usuario':usuario,**kw},headers={'Authorization':'Bearer '+self.cfg.servico_token} if auth else {})
    async def test_lista_alheia_basica_sem_google(self):
        r=await self.post(usuario='999',dono='222');d=await r.json();self.assertEqual(r.status,200);self.assertEqual(d['cartoes'][0]['id'],self.pid)
        self.assertNotIn('arquivo',d['cartoes'][0]);self.assertNotIn(F1,str(d));self.assertNotIn('ficha',d['cartoes'][0]);self.assertEqual(self.prov.leituras,0)
        self.assertFalse(d['cartoes'][0]['capacidades']['ver_detalhes'])
    async def test_sem_autenticacao_e_cross_guild(self):
        self.assertEqual((await self.post(auth=False)).status,403)
        self.assertEqual((await self.post('cartao',servidor='333')).status,403)
    async def test_abrir_cartao_proprio_atualiza_alheio_nao(self):
        r=await self.post('cartao');self.assertEqual(r.status,200);self.assertEqual(self.prov.leituras,1)
        self.assertFalse((await r.json())['precisa_atualizar'])
        self.assertEqual((await self.post('cartao',usuario='999')).status,200);self.assertEqual(self.prov.leituras,1)
    async def test_projecao_publica_apos_snapshot_privado(self):
        await self.post('detalhes')
        r=await self.post('cartao',usuario='999');d=await r.json()
        self.assertNotIn('leitura',d);self.assertNotIn('arquivo',d);self.assertNotIn('analise',d)
        self.assertEqual((await self.post('detalhes',usuario='999')).status,403)
    async def test_revisor_perde_cargo_botao_antigo_recusa(self):
        await self.post('cargo_revisor',usuario='555',cargo='888',permitir=True)
        self.assertEqual((await self.post('analisar',usuario='777')).status,200)
        self.prov.pessoas['777']=replace(self.prov.pessoas['777'],cargos=frozenset())
        self.assertEqual((await self.post('analise_salva',usuario='777')).status,403)
        self.assertEqual((await self.post('preparar',usuario='555',alteracoes={'titulo':'não'},campos_publicos=['nome'])).status,403)
    async def test_gerenciar_servidor_e_cargo_lore_nao_ganham_revisao(self):
        self.prov.pessoas['999']=replace(self.prov.pessoas['999'],gerenciar_servidor=True,cargos=frozenset({'lore'}))
        self.assertEqual((await self.post('detalhes',usuario='999')).status,403)
        self.assertEqual((await self.post('cargo_revisor',usuario='999',cargo='888',permitir=True)).status,403)
    async def test_membro_ausente_oculta_e_retorno_reabre(self):
        self.prov.ausentes.add('222')
        r=await self.post(usuario='999',dono='222');self.assertEqual((await r.json())['cartoes'],[])
        self.prov.ausentes.clear()
        r=await self.post(dono='222');self.assertEqual(len((await r.json())['cartoes']),1)
    async def test_falha_transitoria_nao_registra_saida(self):
        self.prov.erro_membro=ErroProvedor('temporario')
        self.assertNotEqual((await self.post(usuario='999',dono='222')).status,200)
        self.prov.erro_membro=None
        self.assertEqual(len((await (await self.post(dono='222')).json())['cartoes']),1)
    async def test_paginar_multiplos_nao_le_fichas(self):
        for n in range(22):await self.b('cadastrar',self.m,conexao=self.cid,arquivo='ficticio-'+str(n),nome='Personagem '+str(n),contrato='analise-12',responsabilidade=True,pedido='c'+str(n))
        a=await (await self.post()).json();b=await (await self.post(depois=a['proximo'])).json()
        self.assertEqual(len(a['cartoes']),20);self.assertEqual(len(b['cartoes']),3);self.assertFalse({c['id'] for c in a['cartoes']}&{c['id'] for c in b['cartoes']});self.assertEqual(self.prov.leituras,0)
    async def test_previa_confirmacao_e_cancelamento(self):
        a=await (await self.post('preparar',alteracoes={'titulo':'Novo'},campos_publicos=['nome','titulo'])).json()
        self.assertNotIn('titulo',(await (await self.post('cartao_salvo')).json())['perfil'])
        self.assertEqual((await self.post('confirmar',usuario='999',previa=a['previa'])).status,403)
        self.assertEqual((await self.post('confirmar',previa=a['previa'])).status,200)
        self.assertEqual((await self.post('confirmar',previa=a['previa'])).status,409)
    async def test_imagem_validada_preview_e_blob_autenticado(self):
        r=await self.client.post('/interno/galeria/'+self.pid+'/enviar_imagem',data=png(),headers={'Authorization':'Bearer '+self.cfg.servico_token,'X-Carteira-Servidor':'111','X-Carteira-Usuario':'222','Content-Type':'application/octet-stream'})
        self.assertEqual(r.status,200);a=await r.json()
        r=await self.post('imagem',previa=a['previa']);self.assertEqual(r.content_type,'image/webp');self.assertTrue(await r.read())
        self.assertEqual((await self.post('imagem',usuario='999',previa=a['previa'])).status,403)
        await self.post('confirmar',previa=a['previa'])
        self.assertEqual((await self.post('imagem',usuario='999')).status,200)
    async def test_entrada_extra_e_imagem_arbitraria_recusadas(self):
        self.assertEqual((await self.post('preparar',alteracoes={'arquivo':'http://interno'},campos_publicos=['nome'])).status,400)
        self.assertEqual((await self.post('detalhes',arquivo=F2)).status,400)
        self.assertEqual((await self.post('apagar_usuario')).status,404)
    async def test_limite_json_continua_16k(self):
        r=await self.post('preparar',alteracoes={'titulo':'x'*18000},campos_publicos=['nome']);self.assertEqual(r.status,413)
    async def test_destinatario_e_cursor_invalidos_recusados(self):
        for dados in ({'dono':[]},{'dono':'http://interno'},{'depois':[]},{'depois':'../segredo'}):
            with self.subTest(dados=dados):self.assertEqual((await self.post(**dados)).status,400)
