"""Navegador autenticado sobre HTTP/SQLite/cifra reais e provedores fictícios."""
import asyncio
import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit
from aiohttp import CookieJar
from aiohttp.test_utils import TestClient,TestServer
from carteira_viva.web import criar_app,DADOS,GALERIA
from carteira_viva.motor import Motor
from carteira_viva.sessoes import nome_cookie
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_galeria import ProvedorGaleria
from testes.test_carteira_web import F1,F2

class NavegadorTeste(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=tempfile.TemporaryDirectory();p=Path(cls.base.name)/'campanhas.json';p.write_text('{}')
        cls.motor_base=Motor(Path(__file__).parents[2]/'dados',p)
    @classmethod
    def tearDownClass(cls):cls.base.cleanup()
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();p=Path(self.tmp.name);self.cfg=configuracao(p/'db.sqlite3',servidores=frozenset({'111','333'}));self.clock=[180000.]
        self.prov=ProvedorGaleria(self.cfg,lambda:self.clock[0]);self.prov.pessoas['222']=replace(self.prov.pessoas['222'],nome='Jogador QA')
        self.camp=p/'campanhas.json';self.camp.write_text('{}');motor=copy.copy(self.motor_base);motor.campanhas=self.camp
        self.app=criar_app(self.cfg,provedores=self.prov,motor=motor,agora=lambda:self.clock[0]);self.client=TestClient(TestServer(self.app),cookie_jar=CookieJar(unsafe=True));await self.client.start_server()
        self.m=self.prov.pessoas['222'];cid=await self.b('conectar',self.m,conta='ficticia',cliente=self.cfg.google_id,refresh_token='ficticio')
        self.personagem=await self.b('cadastrar',self.m,conexao=cid,arquivo=F1,nome='Nome privado QA',contrato='analise-12',responsabilidade=True,pedido='primeiro');self.pid=self.personagem['id']
    async def asyncTearDown(self):await self.client.close();self.tmp.cleanup()
    async def b(self,m,*a,**kw):return await self.app[DADOS].chamar('cadastro.'+m,*a,**kw)
    async def get(self,path):return await self.client.get('/api/carteira/111/'+path)
    async def post(self,path,data=None,*,csrf=None,origin=None):
        return await self.client.post('/api/carteira/111/'+path,json=data or {},headers={'Origin':origin or self.cfg.origem,'X-CSRF-Token':self.state['csrf'] if csrf is None else csrf})
    async def login(self,uid='222'):
        self.prov.usuario=uid
        r=await self.client.get('/carteira/111/'+self.pid);self.assertEqual(r.status,200)
        self.state=await (await self.get('sessao')).json();self.antigo=self.client.session.cookie_jar.filter_cookies(self.client.make_url('/'))[nome_cookie(False)].value
        r=await self.post('entrar',{'personagem':self.pid});self.assertEqual(r.status,200,await r.text());state=parse_qs(urlsplit((await r.json())['url']).query)['state'][0]
        r=await self.client.get('/oauth/discord/retorno',params={'state':state,'code':'codigo_ficticio'},allow_redirects=False);self.assertEqual(r.status,302,await r.text());self.assertEqual(r.headers['Location'],'/carteira/111/'+self.pid)
        self.state=await (await self.get('sessao')).json()
        self.assertEqual(self.state['usuario'],uid)
        return state
    async def aguardar_leitura(self,task):
        evento=asyncio.create_task(self.prov.entrou.wait())
        try:
            done,_=await asyncio.wait((task,evento),return_when=asyncio.FIRST_COMPLETED)
            if task in done and not self.prov.entrou.is_set():
                r=task.result();self.fail('Consulta encerrada antes de ler: '+str(r.status)+' '+await r.text())
        finally:
            evento.cancel();await asyncio.gather(evento,return_exceptions=True)
    async def logout(self):
        return await self.client.post('/api/carteira/sair',json={},headers={'Origin':self.cfg.origem,'X-CSRF-Token':self.state['csrf']})
    async def test_html_sem_dados_e_api_exige_login(self):
        for path in ('/carteira/111','/carteira/111/'+self.pid):
            r=await self.client.get(path);t=await r.text();self.assertNotIn(F1,t);self.assertNotIn('Nome privado QA',t);self.assertEqual(r.headers['Cache-Control'],'private, no-store')
        self.assertEqual((await self.get('galeria')).status,401)
        self.assertEqual((await self.get('personagens/'+self.pid)).status,401)
    async def test_cookie_e_csp_sem_relaxar_origem(self):
        r=await self.client.get('/carteira/111');cookie=r.cookies[nome_cookie(False)]
        self.assertTrue(cookie['httponly']);self.assertEqual(cookie['samesite'],'Lax');self.assertEqual(cookie['path'],'/')
        self.assertIn("frame-src 'none'",r.headers['Content-Security-Policy']);self.assertNotIn('unsafe-inline',r.headers['Content-Security-Policy'])
        self.assertEqual(r.headers['Referrer-Policy'],'no-referrer');self.assertNotIn('Access-Control-Allow-Origin',r.headers)
    async def test_login_rotaciona_cookie_e_logout_invalida_replay(self):
        await self.login();self.assertNotEqual(self.client.session.cookie_jar.filter_cookies(self.client.make_url('/'))[nome_cookie(False)].value,self.antigo)
        cookie=self.client.session.cookie_jar.filter_cookies(self.client.make_url('/'))[nome_cookie(False)].value
        self.assertEqual((await self.logout()).status,200)
        r=await self.client.get('/api/carteira/111/galeria',headers={'Cookie':nome_cookie(False)+'='+cookie});self.assertEqual(r.status,401)
    async def test_idioma_da_pagina_sobrevive_ao_login_sem_mudar_servidor(self):
        await self.client.get('/carteira/111');self.state=await (await self.get('sessao')).json()
        r=await self.post('entrar',{'idioma':'xx'});self.assertEqual(r.status,400)
        r=await self.post('entrar',{'idioma':'en'});state=parse_qs(urlsplit((await r.json())['url']).query)['state'][0]
        r=await self.client.get('/oauth/discord/retorno',params={'state':state,'code':'ficticio'},allow_redirects=False)
        self.assertEqual(r.headers['Location'],'/carteira/111?idioma=en')
        self.assertEqual((await (await self.get('sessao')).json())['idioma'],'pt-BR')
    async def test_csrf_e_origem_errados_nao_executam_acao(self):
        await self.login()
        for kw in ({'csrf':'errado'},{'origin':'https://terceiro.invalid'}):self.assertEqual((await self.post('personagens/'+self.pid+'/analisar',**kw)).status,403)
        self.assertEqual(self.prov.leituras,0)
    async def test_ator_nunca_vem_de_json_ou_query(self):
        await self.login('999')
        self.assertEqual((await self.post('personagens/'+self.pid+'/analisar',{'usuario':'222'})).status,400)
        self.assertEqual((await self.get('galeria?usuario=222')).status,400)
        self.assertEqual((await self.post('personagens/'+self.pid+'/analisar')).status,403)
    async def test_galeria_alheia_so_basico_e_sem_google(self):
        await self.login('999');r=await self.get('galeria?dono=222');d=await r.json();self.assertEqual(r.status,200)
        self.assertEqual(d['cartoes'][0]['responsavel_nome'],'Jogador QA');self.assertNotIn(F1,str(d));self.assertNotIn('leitura',d['cartoes'][0]);self.assertFalse(d['cartoes'][0]['capacidades']['ver_detalhes']);self.assertEqual(self.prov.leituras,0)
        self.assertEqual((await self.post('personagens/'+self.pid+'/detalhes')).status,403)
        self.assertEqual((await self.post('personagens/'+self.pid+'/atualizar')).status,403)
    async def test_alterar_servidor_e_id_nao_da_acesso(self):
        await self.login()
        for path in ('/api/carteira/333/personagens/'+self.pid,'/api/carteira/111/personagens/'+'a'*32):self.assertEqual((await self.client.get(path)).status,403)
        self.assertEqual((await self.client.get('/carteira/999')).status,404)
        self.assertEqual((await self.client.get('/carteira/111/nao-e-id')).status,404)
    async def test_detalhes_e_analise_sao_projecoes_privadas_sem_snapshot(self):
        await self.login();r=await self.post('personagens/'+self.pid+'/detalhes');d=await r.json();self.assertEqual(r.status,200,await r.text());self.assertIn(F1,d['arquivo']);self.assertNotIn('ficha',d);self.assertNotIn('leitura',d)
        r=await self.post('personagens/'+self.pid+'/analisar',{'idioma':'en'});self.assertEqual(r.status,200,await r.text());a=await r.json();self.assertGreater(a['total'],0)
        self.assertNotIn('access_token',str(a));self.assertNotIn('csrf',a);self.assertNotIn('resultado',a)
        self.assertNotIn('controls for 10 min',a['rodape'])
    async def test_navegar_na_analise_revalida_cargo_sem_google(self):
        await self.b('configurar',self.prov.pessoas['555'],revisores={'888'});await self.login('777')
        self.assertEqual((await self.post('personagens/'+self.pid+'/analisar')).status,200);n=self.prov.leituras
        self.assertEqual((await self.post('personagens/'+self.pid+'/analise')).status,200);self.assertEqual(self.prov.leituras,n)
        self.prov.pessoas['777']=replace(self.prov.pessoas['777'],cargos=frozenset())
        r=await self.post('personagens/'+self.pid+'/analise');self.assertEqual(r.status,403);self.assertNotIn(F1,await r.text())
    async def test_campanha_ou_fonte_mudou_nao_abre_analise_antiga(self):
        await self.login();await self.post('personagens/'+self.pid+'/analisar');self.camp.write_text(json.dumps({'111':{'nome':'outra'}}))
        self.assertEqual((await self.post('personagens/'+self.pid+'/analise')).status,409)
        self.camp.write_text('{}');cid=(await self.b('_fonte','111',self.pid))['conexao']
        await self.b('trocar_arquivo',self.m,self.pid,arquivo=F2,conexao=cid,contrato='analise-12',revisao=1,pedido='troca')
        self.assertEqual((await self.post('personagens/'+self.pid+'/analise')).status,409)
    async def test_sair_do_servidor_encerra_sessao(self):
        await self.login();self.prov.ausentes.add('222');self.assertEqual((await self.get('galeria')).status,401)
        self.prov.ausentes.clear();self.assertEqual((await self.get('galeria')).status,401)
    async def test_resposta_atrasada_apos_logout_nao_entrega_dados(self):
        await self.login();self.prov.bloqueio=asyncio.Event()
        task=asyncio.create_task(self.post('personagens/'+self.pid+'/detalhes'))
        await self.aguardar_leitura(task);self.assertEqual((await self.logout()).status,200);self.prov.bloqueio.set()
        r=await task;self.assertEqual(r.status,401);self.assertNotIn(F1,await r.text())
    async def test_expiracao_durante_leitura_nao_entrega_dados(self):
        await self.login();self.prov.bloqueio=asyncio.Event();task=asyncio.create_task(self.post('personagens/'+self.pid+'/detalhes'))
        await self.aguardar_leitura(task);self.clock[0]+=1801;self.prov.bloqueio.set();self.assertEqual((await task).status,401)
    async def test_callback_logout_nao_recria_sessao(self):
        await self.client.get('/carteira/111');self.state=await (await self.get('sessao')).json()
        r=await self.post('entrar');state=parse_qs(urlsplit((await r.json())['url']).query)['state'][0]
        self.prov.espera=asyncio.Event();entrou=asyncio.Event();original=self.prov.trocar_codigo
        async def trocar(*a,**kw):entrou.set();return await original(*a,**kw)
        self.prov.trocar_codigo=trocar
        task=asyncio.create_task(self.client.get('/oauth/discord/retorno',params={'state':state,'code':'ficticio'},allow_redirects=False))
        await entrou.wait()
        await self.logout();self.prov.espera.set();r=await task;self.assertEqual(r.status,302)
        self.assertNotIn(nome_cookie(False),r.cookies);self.assertEqual((await self.get('galeria')).status,401)
    async def test_privado_revalida_apos_montar_pagina(self):
        await self.b('configurar',self.prov.pessoas['555'],revisores={'888'});await self.login('777')
        from carteira_viva.web_carteira import apresentar
        def montar(*a):
            result=apresentar(*a);self.prov.pessoas['777']=replace(self.prov.pessoas['777'],cargos=frozenset());return result
        with patch('carteira_viva.web_carteira.apresentar',side_effect=montar):r=await self.post('personagens/'+self.pid+'/analisar')
        self.assertEqual(r.status,403);self.assertNotIn(F1,await r.text())
    async def test_numero_de_pagina_e_metodo_fechados(self):
        await self.login()
        self.assertEqual((await self.post('personagens/'+self.pid+'/analisar',{'pagina':-1})).status,400)
        self.assertEqual((await self.post('personagens/'+self.pid+'/apagar_usuario')).status,404)
        self.assertEqual((await self.post('personagens/'+self.pid+'/detalhes',{'idioma':'xx'})).status,400)
    async def test_json_tem_limite_e_nao_aceita_arquivo_para_escrever(self):
        await self.login()
        self.assertEqual((await self.post('personagens/'+self.pid+'/detalhes',{'arquivo':'x'*18000})).status,413)
        self.assertEqual((await self.post('personagens/'+self.pid+'/detalhes',{'arquivo':F2})).status,400)
    async def test_assets_nao_contem_dados_privados_nem_html_dinamico(self):
        for f in ('carteira.js','carteira.css'):
            r=await self.client.get('/static/'+f);self.assertEqual(r.status,200);self.assertNotIn(self.cfg.servico_token,await r.text())
        js=await (await self.client.get('/static/carteira.js')).text()
        self.assertNotIn('innerHTML',js);self.assertNotIn('localStorage',js);self.assertNotIn('sessionStorage',js)

    async def test_cookie_do_navegador_nao_e_segredo_de_servico(self):
        await self.login()
        r=await self.client.post('/interno/galeria',json={'servidor':'111','usuario':'222'})
        self.assertEqual(r.status,403)
    async def test_estado_de_outro_browser_nao_faz_logout_da_vitima(self):
        from aiohttp import ClientSession
        await self.login()
        async with ClientSession(cookie_jar=CookieJar(unsafe=True)) as outro:
            await outro.get(self.client.make_url('/carteira/111'))
            estado=await (await outro.get(self.client.make_url('/api/carteira/111/sessao'))).json()
            r=await outro.post(self.client.make_url('/api/carteira/111/entrar'),json={},headers={'Origin':self.cfg.origem,'X-CSRF-Token':estado['csrf']})
            state=parse_qs(urlsplit((await r.json())['url']).query)['state'][0]
            r=await self.client.get('/oauth/discord/retorno',params={'state':state,'code':'ficticio'},allow_redirects=False)
            self.assertEqual(r.status,302)
            self.assertEqual((await self.get('galeria')).status,200)
