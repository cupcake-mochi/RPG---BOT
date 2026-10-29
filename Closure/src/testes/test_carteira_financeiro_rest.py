"""Inicialização parcial: HTTP simulado, dados fictícios e SQL real; nenhum Google."""
import asyncio
import copy
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.fernet import Fernet
import httpx

from carteira_viva.backup import gravar_backup, restaurar_backup
from carteira_viva.banco import Cadastro
from carteira_viva.consultas import Consultas
from carteira_viva.copias_google import DestinoCopia, marcadores
from carteira_viva.financeiro_plano import medir
from carteira_viva.financeiro_google import enviar
from carteira_viva.financeiro_banco import EnvioFinanceiro
from carteira_viva.fluxos import DadosAsync
from carteira_viva.grade_inicializacao import LeitorGradeRest
from carteira_viva.permissoes import Membro
from carteira_viva.provedores import Provedores, ErroProvedor, DRIVE_FILE, MIME
from carteira_viva.segredos import Conflito, AcessoNegado, ErroCarteira
from testes.test_carteira_banco import schema_historico
from testes.test_carteira_conferencia_inicializacao import Dados
from testes.test_carteira_grade_inicializacao import ARQUIVO
from testes.test_carteira_modelos import referencia
from testes.test_carteira_provedores import configuracao


class CotasTeste:
    def __init__(self): self.n = 0; self.hook = None
    async def esperar(self, conta):
        self.n += 1
        if self.hook: await self.hook()


class FinanceiroRestTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=TemporaryDirectory(); self.cfg=configuracao(Path(self.tmp.name)/'dados.sqlite3')
        self.clock=[180000.];self.agora=lambda:self.clock[0]
        self.dados=DadosAsync(self.cfg,agora=self.agora);await self.dados.iniciar()
        self.data=Dados('financeiro');self.data.versao='7'
        for a in ('EXTRATO','SALÁRIOS','DADOS_SALARIOS'):self.data.grades[a]['gridProperties']['rowCount']=20
        self.data.literal('EXTRATO',2,1,'histórico privado fictício')
        self.data.mapa['EXTRATO',2,1]['note']='nota privada fictícia'
        self.data.mapa['EXTRATO',2,1]['userEnteredFormat']={'numberFormat':{'type':'TEXT','pattern':'@'}}
        self.data.literal('DADOS_SALARIOS',2,12,'estado antigo fictício')
        self.data.literal('DADOS_SALARIOS',2,13,'preservar M2')
        self.data.literal('FICHA',11,34,10)
        self.data.literal('CARTEIRA',3,46,True)
        self.http_hook=None;self.req=[];self.posts=[];self.perder=False;self.aplicar=True;self.post_status=200
        self.source_version='7';self.meta_patch={};self.token_erro=False
        self.prov=Provedores(self.cfg,agora=self.agora,transporte=httpx.MockTransport(self.http))
        self.s=Consultas(self.dados,self.prov,agora=self.agora);self.cotas=CotasTeste();self.s.cotas=self.cotas
        self.m=Membro('111','222');self.fonte=referencia()['arquivo']
        self.cid=await self.b('conectar',self.m,conta='conta-ficticia',cliente=self.cfg.google_id,refresh_token='refresh-ficticio')
        await self.b('configurar_modelo',replace(self.m,administrador=True),escolha='servidor',revisao=0,previa=referencia())
        self.ref=await self.b('preparar_copia_modelo',self.m,conexao=self.cid,modelo='servidor',pedido='copia-ficticia')
        await self.b('fixar_versao_copia',self.m,self.ref,'7');await self.b('armar_envio_copia',self.m,self.ref)
        await self.b('registrar_candidata_copia',self.m,self.ref,DestinoCopia(ARQUIVO,'7',self.ref.operacao,self.fonte))
        await self.b('registrar_destino_copia',self.m,self.ref,DestinoCopia(ARQUIVO,'7',self.ref.operacao,self.fonte))

    async def asyncTearDown(self):
        await self.s.fechar();await self.dados.fechar();self.tmp.cleanup()

    async def b(self,metodo,*args,**kw):return await self.dados.chamar('cadastro.'+metodo,*args,**kw)
    async def inicializar(self,usuario='222'):
        return await self.s.inicializar_financeiro_celulas('111',usuario,self.ref)

    async def executar_no_worker(self,fn):
        return await asyncio.wrap_future(self.dados.executor.submit(lambda:fn(self.dados.store.c)))

    async def plano(self):
        _,ctx=await self.b('contexto_financeiro',self.m,self.ref)
        async def contexto():return ctx
        async def cota():pass
        return await medir(LeitorGradeRest(self.prov,contexto,cota),'acesso-ficticio',ARQUIVO)

    def aplicar_pedidos(self,obj):
        # Emulador independente: aplica somente o field mask de cada request.
        self.assertEqual(set(obj),{'requests'});self.assertEqual(len(obj['requests']),21)
        por_id={v['sheetId']:k for k,v in self.data.grades.items()}
        for request in obj['requests']:
            self.assertEqual(set(request),{'repeatCell'});x=request['repeatCell']
            self.assertEqual(set(x),{'range','cell','fields'})
            self.assertIn(x['fields'],('userEnteredValue','note'))
            self.assertNotIn('formulaValue',str(x['cell']))
        for request in obj['requests']:
            x=request['repeatCell'];g=x['range'];aba=por_id[g['sheetId']]
            for r in range(g['startRowIndex']+1,g['endRowIndex']+1):
                for col in range(g['startColumnIndex']+1,g['endColumnIndex']+1):
                    d=self.data.mapa.setdefault((aba,r,col),{})
                    if x['fields']=='note':d.pop('note',None)
                    elif 'userEnteredValue' in x['cell']:
                        d['userEnteredValue']=copy.deepcopy(x['cell']['userEnteredValue'])
                        d['effectiveValue']=copy.deepcopy(d['userEnteredValue'])
                    else:d.pop('userEnteredValue',None);d.pop('effectiveValue',None)
        self.data.versao=str(int(self.data.versao)+1)

    async def http(self,req):
        self.req.append(req)
        if self.http_hook:await self.http_hook(req)
        if req.url.host=='discord.com':
            if '/members/' in req.url.path:return httpx.Response(200,json={'user':{'id':req.url.path.rsplit('/',1)[1]},'roles':[]})
            if req.url.path.endswith('/roles'):return httpx.Response(200,json=[{'id':'111','permissions':'0'}])
            return httpx.Response(200,json={'owner_id':'999'})
        if req.url.host=='oauth2.googleapis.com':
            if self.token_erro:return httpx.Response(400,json={'error':'invalid_grant'})
            return httpx.Response(200,json=dict(access_token='access-ficticio',refresh_token='refresh-ficticio-rotacionado',
                expires_in=3600,expires_at=self.agora()+3600,token_type='Bearer',scope=DRIVE_FILE))
        if req.url.host=='www.googleapis.com':
            arquivo=req.url.path.rsplit('/',1)[1]
            if arquivo==self.fonte:return httpx.Response(200,json=dict(id=arquivo,mimeType=MIME,isAppAuthorized=True,trashed=False,version=self.source_version))
            self.assertEqual(arquivo,ARQUIVO)
            return httpx.Response(200,json={**dict(id=ARQUIVO,mimeType=MIME,isAppAuthorized=True,trashed=False,
                version=self.data.versao,ownedByMe=True,shared=False,appProperties=marcadores(self.ref.operacao,self.fonte),
                permissions=[dict(type='user',role='owner')]),**self.meta_patch})
        if req.method=='POST':
            self.assertEqual(req.url.host,'sheets.googleapis.com')
            self.assertEqual(req.url.path,'/v4/spreadsheets/'+ARQUIVO+':batchUpdate')
            self.posts.append(json.loads(req.content))
            if self.aplicar:self.aplicar_pedidos(self.posts[-1])
            if self.perder:raise httpx.ReadTimeout('resposta fictícia perdida')
            return httpx.Response(self.post_status,json={'spreadsheetId':ARQUIVO})
        return self.data.http(req)

    async def test_limpa_so_entradas_e_notas_mantem_formulas_configuracao_e_formato(self):
        antes=copy.deepcopy(self.data.mapa)
        r=await self.inicializar();self.assertEqual(r['estado'],'celulas_conferidas')
        self.assertEqual(len(self.posts),1);self.assertFalse(r['financeiro_concluido'])
        self.assertTrue(r['propriedades_apps_script_pendentes']);self.assertFalse(r['criacao_disponivel'])
        self.assertFalse(await self.b('listar',self.m))
        self.assertNotIn('userEnteredValue',self.data.mapa['EXTRATO',2,1]);self.assertNotIn('note',self.data.mapa['EXTRATO',2,1])
        self.assertEqual(self.data.mapa['EXTRATO',2,1]['userEnteredFormat'],antes['EXTRATO',2,1]['userEnteredFormat'])
        for k in [('DADOS_SALARIOS',2,13),('FICHA',11,34),('FICHA',11,40),('DADOS_SALARIOS',11,16)]:
            self.assertEqual(self.data.mapa[k],antes[k],k)
        for x in ('histórico privado','nota privada','access-ficticio',ARQUIVO):self.assertNotIn(x,str(r))

    async def test_resposta_perdida_retomada_so_le_sem_segundo_post(self):
        self.perder=True
        with self.assertRaises(ErroProvedor):await self.inicializar()
        r=await self.inicializar();self.assertTrue(r['financeiro_celulas_conferidas']);self.assertEqual(len(self.posts),1)

    async def test_resposta_perdida_sem_aplicacao_fica_pendente_nao_reenvia(self):
        self.perder=True;self.aplicar=False
        with self.assertRaises(ErroProvedor):await self.inicializar()
        r=await self.inicializar();self.assertEqual(r['estado'],'aguardando_leitura');self.assertEqual(len(self.posts),1)

    async def test_reinicio_preserva_envio_e_reconcilia_sem_novo_post(self):
        self.perder=True
        with self.assertRaises(ErroProvedor):await self.inicializar()
        await self.s.fechar();await self.dados.fechar()
        self.dados=DadosAsync(self.cfg,agora=self.agora);await self.dados.iniciar()
        self.s=Consultas(self.dados,self.prov,agora=self.agora);self.s.cotas=self.cotas
        self.assertTrue((await self.inicializar())['financeiro_celulas_conferidas']);self.assertEqual(len(self.posts),1)

    async def test_formula_em_entrada_impede_toda_escrita(self):
        self.data.formula('EXTRATO',2,1,'=123',123)
        with self.assertRaises(ErroCarteira):await self.inicializar()
        self.assertFalse(self.posts)

    async def test_guarda_adulterada_apos_mais_de_16_residuos_nao_some_no_limite(self):
        for r in range(15,30):self.data.literal('FICHA PESSOAL',r,49,'resíduo fictício')
        self.data.formula('FICHA',11,40,'=0',0)
        with self.assertRaises(ErroCarteira):await self.inicializar()
        self.assertFalse(self.posts)

    async def test_copia_alterada_desde_criacao_nao_pode_ser_inicializada(self):
        self.data.versao='8'
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertFalse(self.posts)
        self.assertFalse(any(r.url.host=='sheets.googleapis.com' for r in self.req))
        d=await self.b('contexto_copia',self.m,self.ref)
        self.assertEqual(d['versao_destino'],'7')
        self.assertEqual(d['observacoes_versao'][-1]['observada'],'8')

    async def test_versao_muda_na_pagina_fica_no_diario_sem_dados_privados(self):
        mudou=False
        async def hook(req):
            nonlocal mudou
            if req.url.host=='sheets.googleapis.com' and 'ranges' in req.url.params and not mudou:
                mudou=True;self.data.versao='8'
        self.http_hook=hook
        with self.assertRaises(ErroProvedor) as erro:await self.inicializar()
        self.assertEqual(erro.exception.codigo,'alterada')
        d=await self.b('contexto_copia',self.m,self.ref)
        e=d['observacoes_versao'][-1];self.assertEqual(e['etapa'],'copia_leitura')
        self.assertEqual((e['esperada'],e['observada']),('7','8'))
        self.assertFalse(self.posts);self.assertIsNone(await self.b('estado_financeiro',self.m,self.ref))
        for s in ('histórico privado','nota privada',ARQUIVO,self.fonte):self.assertNotIn(s,str(e))

    async def test_mudanca_de_fonte_e_registrada_antes_de_ler_celulas(self):
        self.source_version='8'
        with self.assertRaises(Conflito):await self.inicializar()
        e=(await self.b('contexto_copia',self.m,self.ref))['observacoes_versao'][-1]
        self.assertEqual((e['etapa'],e['esperada'],e['observada']),('origem_financeiro','7','8'))
        self.assertFalse(any(r.url.host=='sheets.googleapis.com' for r in self.req))

    async def test_ficha_cadastrada_em_qualquer_servidor_impede_mutacao(self):
        m=replace(self.m,servidor='outra-mesa')
        await self.b('cadastrar',m,conexao=self.cid,arquivo=ARQUIVO,nome='Fictício',contrato='analise-12',responsabilidade=True,pedido='x')
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertFalse(self.posts)

    async def test_outro_usuario_e_json_de_referencia_nao_acessam_google(self):
        with self.assertRaises(AcessoNegado):await self.inicializar(usuario='999')
        with self.assertRaises(AcessoNegado):await self.s.inicializar_financeiro_celulas('111','222',{'arquivo':ARQUIVO})
        self.assertFalse(self.req)

    async def test_destino_compartilhado_e_modelo_alterado_recusam(self):
        self.meta_patch={'shared':True}
        with self.assertRaises(ErroProvedor):await self.inicializar()
        self.meta_patch={};self.source_version='8'
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertFalse(self.posts)

    async def test_guarda_de_versao_reobservada_depois_da_cota_de_escrita(self):
        plano=await self.plano();await self.b('preparar_financeiro',self.m,self.ref,plano)
        n=0
        async def cota():
            nonlocal n
            n+=1
            if n==4:self.data.versao='8' # Cota do envio, após as observações iniciais.
        self.cotas.hook=cota
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertFalse(self.posts)

    async def test_mudanca_interna_durante_leitura_de_pagina_recusa(self):
        async def hook(req):
            if req.url.host=='sheets.googleapis.com' and 'ranges' in req.url.params:
                await self.b('desconectar',self.m,self.cid)
        self.http_hook=hook
        with self.assertRaises(ErroCarteira):await self.inicializar()
        self.assertFalse(self.posts)

    async def test_alteracao_externa_depois_do_envio_recusa_sem_repetir(self):
        self.perder=True
        with self.assertRaises(ErroProvedor):await self.inicializar()
        self.data.literal('DADOS_SALARIOS',2,13,'alteração alheia')
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertEqual(len(self.posts),1)

    async def test_resultado_conferido_nao_pode_limpar_uso_posterior(self):
        await self.inicializar();self.data.literal('EXTRATO',2,1,'novo gasto fictício')
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertEqual(len(self.posts),1)

    async def test_perda_de_cache_literal_aguarda_recalculo_sem_post_novo(self):
        self.perder=True
        with self.assertRaises(ErroProvedor):await self.inicializar()
        self.data.mapa['CARTEIRA',3,46].pop('effectiveValue')
        r=await self.inicializar();self.assertEqual(r['estado'],'aguardando_recalculo');self.assertEqual(len(self.posts),1)

    async def test_429_de_escrita_nao_e_repetido(self):
        self.post_status=429;self.aplicar=False
        with self.assertRaises(ErroProvedor):await self.inicializar()
        self.assertEqual((await self.inicializar())['estado'],'aguardando_leitura');self.assertEqual(len(self.posts),1)

    async def test_tabelas_limpas_nao_precisam_de_post(self):
        self.data=Dados('financeiro');self.data.versao='7'
        for a in ('EXTRATO','SALÁRIOS','DADOS_SALARIOS'):self.data.grades[a]['gridProperties']['rowCount']=20
        self.assertTrue((await self.inicializar())['financeiro_celulas_conferidas']);self.assertFalse(self.posts)

    async def test_backup_pre_envio_marca_enviada_e_nao_libera_replay(self):
        plano=await self.plano();await self.b('preparar_financeiro',self.m,self.ref,plano)
        bak=Path(self.tmp.name)/'dados.cvb';dest=Path(self.tmp.name)/'restaurado.sqlite3'
        await self.executar_no_worker(lambda c:gravar_backup(c,bak))
        restaurar_backup(bak,dest,self.cfg.chaves,remocoes=self.cfg.banco.with_suffix('.remocoes.sqlite3'),agora=self.agora)
        with Cadastro(dest,self.cfg.chaves,remocoes=self.cfg.banco.with_suffix('.remocoes.sqlite3'),agora=self.agora) as c:
            self.assertEqual(c.estado_financeiro(self.m,self.ref)['estado'],'enviada')
            self.assertIsNone(c.armar_financeiro(self.m,self.ref,'7'))
        self.assertEqual((await self.b('estado_financeiro',self.m,self.ref))['estado'],'preparada')

    async def test_diario_nao_contem_historico_e_rotacao_conserva_contexto(self):
        plano=await self.plano();await self.b('preparar_financeiro',self.m,self.ref,plano)
        d=await self.b('estado_financeiro',self.m,self.ref)
        for s in ('histórico privado','nota privada','preservar M2'):self.assertNotIn(s,str(d))
        nova=Fernet.generate_key();await self.b('rotacionar_chave',nova)
        self.assertEqual(await self.b('estado_financeiro',self.m,self.ref),d)

    async def test_exclusao_global_cascateia_financeiro_e_restore_nao_ressuscita(self):
        plano=await self.plano();await self.b('preparar_financeiro',self.m,self.ref,plano)
        bak=Path(self.tmp.name)/'dados.cvb';dest=Path(self.tmp.name)/'restaurado.sqlite3'
        await self.executar_no_worker(lambda c:gravar_backup(c,bak))
        await self.b('apagar_usuario',self.m.usuario)
        restaurar_backup(bak,dest,self.cfg.chaves,remocoes=self.cfg.banco.with_suffix('.remocoes.sqlite3'),agora=self.agora)
        with Cadastro(dest,self.cfg.chaves,remocoes=self.cfg.banco.with_suffix('.remocoes.sqlite3'),agora=self.agora) as c:
            self.assertEqual(c.db.execute('SELECT count(*) FROM financeiro_rest').fetchone()[0],0)
            self.assertEqual(c.db.execute('SELECT count(*) FROM copias_rest').fetchone()[0],0)

    async def test_prazo_original_nao_renova_para_permitir_outra_escrita(self):
        self.perder=True
        with self.assertRaises(ErroProvedor):await self.inicializar()
        self.clock[0]+=1801
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertEqual(len(self.posts),1)

    async def test_migracao8_preserva_prova_da_copia(self):
        await self.executar_no_worker(lambda c:schema_historico(c.db,8))
        await self.s.fechar();await self.dados.fechar()
        self.dados=DadosAsync(self.cfg,agora=self.agora);await self.dados.iniciar()
        self.s=Consultas(self.dados,self.prov,agora=self.agora);self.s.cotas=self.cotas
        self.assertEqual((await self.b('contexto_financeiro',self.m,self.ref))[0]['destino'],ARQUIVO)
        self.assertIsNone(await self.b('estado_financeiro',self.m,self.ref))

    async def test_mudanca_apos_leitura_final_nao_recebe_selo_conferida(self):
        self.perder=True
        with self.assertRaises(ErroProvedor):await self.inicializar()
        async def hook(req):
            if req.url.host=='www.googleapis.com' and req.url.path.endswith('/'+self.fonte):
                # Segunda leitura da origem: a medição final já terminou.
                hook.n+=1
                if hook.n==2:
                    self.data.literal('EXTRATO',2,1,'gasto durante fechamento')
                    self.data.versao='9'
        hook.n=0;self.http_hook=hook
        with self.assertRaises(Conflito):await self.inicializar()
        self.assertEqual((await self.b('estado_financeiro',self.m,self.ref))['estado'],'enviada')
        self.assertEqual(len(self.posts),1)

    async def test_recibo_original_da_copia_nao_adota_versao_editada(self):
        with self.assertRaises(Conflito):
            await self.b('registrar_destino_copia',self.m,self.ref,
                DestinoCopia(ARQUIVO,'8',self.ref.operacao,self.fonte))
        self.assertEqual((await self.b('contexto_copia',self.m,self.ref))['versao_destino'],'7')

    async def test_cancelamento_durante_post_retomada_nao_repete(self):
        entrou=asyncio.Event();bloqueio=asyncio.Event()
        async def hook(req):
            if req.url.host=='sheets.googleapis.com' and req.method=='POST':
                entrou.set();await bloqueio.wait()
        self.http_hook=hook
        tarefa=asyncio.create_task(self.inicializar())
        await asyncio.wait_for(entrou.wait(),10)
        tarefa.cancel()
        with self.assertRaises(asyncio.CancelledError):await tarefa
        await self.s.fechar()
        self.s=Consultas(self.dados,self.prov,agora=self.agora);self.s.cotas=self.cotas
        self.http_hook=None
        self.assertEqual((await self.inicializar())['estado'],'aguardando_leitura')
        self.assertFalse(self.posts)

    async def test_pedidos_concorrentes_compartilham_um_post(self):
        a,b=await asyncio.gather(self.inicializar(),self.inicializar())
        self.assertTrue(a['financeiro_celulas_conferidas']);self.assertEqual(a,b)
        self.assertEqual(len(self.posts),1)

    async def test_dois_bancos_armam_uma_vez_e_capacidade_nao_se_reutiliza(self):
        plano=await self.plano();await self.b('preparar_financeiro',self.m,self.ref,plano)
        with Cadastro(self.cfg.banco,self.cfg.chaves,agora=self.agora) as c:
            envio=c.armar_financeiro(self.m,self.ref,'7')
        self.assertIsNone(await self.b('armar_financeiro',self.m,self.ref,'7'))
        await enviar(self.prov,'acesso-ficticio',envio)
        with self.assertRaises(Conflito):await enviar(self.prov,'acesso-ficticio',envio)
        self.assertEqual(len(self.posts),1)

    async def test_transporte_recusa_json_e_destino_oficial(self):
        with self.assertRaises(ErroCarteira):await enviar(self.prov,'acesso-ficticio',{})
        from carteira_viva.modelos import OFICIAIS
        import re
        arquivo=re.search(r'/d/([A-Za-z0-9_-]+)',OFICIAIS[0]['url']).group(1)
        with self.assertRaises(ErroCarteira):await enviar(self.prov,'acesso-ficticio',EnvioFinanceiro(arquivo,b'{}'))
        self.assertFalse(self.req)
