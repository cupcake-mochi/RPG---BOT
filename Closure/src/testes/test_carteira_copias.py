"""Cópias com rede simulada: perda de resposta, reinício, isolamento e backup."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import parse_qs

from cryptography.fernet import Fernet
import httpx

from carteira_viva.backup import gravar_backup, restaurar_backup
from carteira_viva.banco import Cadastro, DIA
from carteira_viva.copias_banco import ReferenciaCopia
from carteira_viva.copias_google import DestinoCopia, MIME, marcadores, observar, procurar, enviar
from carteira_viva.consultas import Consultas
from carteira_viva.fluxos import DadosAsync
from carteira_viva.permissoes import Membro
from carteira_viva.provedores import DRIVE_FILE, Provedores, ErroProvedor
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from testes.test_carteira_banco import Fixtures, schema_historico
from testes.test_carteira_modelos import referencia
from testes.test_carteira_provedores import configuracao

DESTINO = 'arquivo_descartavel_sintetico_copia_001'


class BancoCopias(Fixtures, unittest.TestCase):
    def preparar(self, pedido='pedido-ficticio'):
        self.cid = self.conectar()
        return self.c.preparar_copia_modelo(self.m, conexao=self.cid, modelo='ciclo', pedido=pedido)

    def identificar(self, ref):
        d = self.c.contexto_copia(self.m, ref)
        self.c.fixar_versao_copia(self.m, ref, '7')
        self.assertTrue(self.c.armar_envio_copia(self.m, ref))
        self.c.registrar_candidata_copia(self.m, ref, DestinoCopia(DESTINO, '1', ref.operacao, d['origem']))
        return self.c.registrar_destino_copia(self.m, ref, DestinoCopia(DESTINO, '1', ref.operacao, d['origem']))

    def test_uma_intencao_retorna_mesmo_registro_e_impede_segunda_pendente(self):
        ref = self.preparar()
        outro = self.c.preparar_copia_modelo(self.m, conexao=self.cid, modelo='ciclo', pedido='pedido-ficticio')
        self.assertEqual(ref, outro)
        with self.assertRaises(Conflito):
            self.c.preparar_copia_modelo(self.m, conexao=self.cid, modelo='era', pedido='outro')
        with self.assertRaises(Conflito):
            self.c.preparar_copia_modelo(self.m, conexao=self.cid, modelo='era', pedido='pedido-ficticio')

    def test_envio_atomico_persiste_apos_reinicio_e_nao_arma_duas_vezes(self):
        ref = self.preparar()
        with self.assertRaises(Conflito): self.c.armar_envio_copia(self.m, ref)
        self.c.fixar_versao_copia(self.m, ref, '7')
        self.assertTrue(self.c.armar_envio_copia(self.m, ref))
        self.reabrir()
        self.assertFalse(self.c.armar_envio_copia(self.m, ref))
        self.assertEqual(self.c.contexto_copia(self.m, ref)['estado'], 'enviada')

    def test_dois_workers_nao_armam_o_mesmo_envio(self):
        ref = self.preparar();self.c.fixar_versao_copia(self.m,ref,'7')
        with Cadastro(self.path,(self.chave,),agora=self.agora) as outro:
            self.assertTrue(outro.armar_envio_copia(self.m,ref))
            self.assertFalse(self.c.armar_envio_copia(self.m,ref))

    def test_dono_conexao_e_servidor_nao_sao_herdados_por_admin(self):
        ref = self.preparar()
        for m in (self.outro, self.admin, replace(self.m, servidor='outra-mesa'), replace(self.m, presente=False)):
            with self.subTest(m=m), self.assertRaises(AcessoNegado): self.c.contexto_copia(m, ref)
        with self.assertRaises(AcessoNegado):
            self.c.preparar_copia_modelo(self.admin, conexao=self.cid, modelo='ciclo', pedido='x')

    def test_modelo_trocado_e_reconexao_nao_adotam_pedido_anterior(self):
        ref = self.preparar()
        self.c.configurar_modelo(self.admin, escolha='era', revisao=0)
        with self.assertRaises(Conflito): self.c.contexto_copia(self.m, ref)
        self.c.configurar_modelo(self.admin, escolha='oficiais', revisao=1)
        with self.assertRaises(Conflito): self.c.contexto_copia(self.m, ref)
        # Novo grant não autoriza continuar o diário antigo, mesmo na mesma conta.
        self.conectar()
        with self.assertRaises(Conflito): self.c.contexto_copia(self.m, ref)

    def test_destino_nao_recebe_ids_arbitrarios_nem_e_personagem_criado(self):
        ref = self.preparar()
        with self.assertRaises(ErroCarteira): self.c.registrar_destino_copia(self.m, ref, {'id':DESTINO})
        r = self.identificar(ref)
        self.assertEqual(r, dict(copia_identificada=True, inicializacao_concluida=False, criacao_disponivel=False))
        self.assertFalse(self.c.listar(self.m))
        self.assertNotIn(DESTINO, str(r))
        from carteira_viva.modelos import CriacaoBloqueada
        with self.assertRaises(CriacaoBloqueada): self.c.criar_por_modelo(self.m, modelo='ciclo')

    def test_backup_pre_envio_so_permite_reconciliar_sem_modificar_base_viva(self):
        ref = self.preparar()
        bak = self.path.parent/'copia.cvb'; destino = self.path.parent/'restaurado.sqlite3'
        gravar_backup(self.c, bak)
        self.assertEqual(self.c.contexto_copia(self.m, ref)['estado'], 'preparada')
        restaurar_backup(bak, destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as c:
            self.assertEqual(c.contexto_copia(self.m, ref)['estado'], 'enviada')
            self.assertFalse(c.armar_envio_copia(self.m, ref))

    def test_rotacao_cifra_preserva_diario_sem_repetir_post(self):
        ref = self.preparar(); self.identificar(ref)
        nova = Fernet.generate_key(); self.c.rotacionar_chave(nova)
        self.assertEqual(self.c.contexto_copia(self.m, ref)['destino'], DESTINO)
        self.reabrir((nova,))
        self.assertFalse(self.c.armar_envio_copia(self.m, ref))
        self.assertNotIn(DESTINO.encode(), self.path.read_bytes())

    def test_exclusao_global_nao_restaura_diario_pelo_backup_antigo(self):
        self.preparar(); bak = self.path.parent/'anterior.cvb'; destino = self.path.parent/'restaurado.sqlite3'
        gravar_backup(self.c, bak); self.c.apagar_usuario(self.m.usuario)
        restaurar_backup(bak, destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as c:
            self.assertEqual(c.db.execute('SELECT count(*) FROM copias_rest').fetchone()[0], 0)

    def test_pendente_nao_expira_nem_perde_conexao_sem_personagem(self):
        ref = self.preparar(); self.clock[0] += 40*DIA; self.c.limpar()
        self.assertEqual(self.c.contexto_copia(self.m, ref)['estado'], 'preparada')
        self.assertIsNone(self.c.db.execute('SELECT sem_uso_desde FROM conexoes').fetchone()[0])

    def test_identificada_tem_retencao_e_nao_pina_conexao_para_sempre(self):
        ref = self.preparar(); self.identificar(ref); self.clock[0] += 31*DIA; self.c.limpar()
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM copias_rest').fetchone()[0], 0)
        self.clock[0] += DIA + 1; self.c.limpar()
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM conexoes').fetchone()[0], 0)

    def test_migra_banco_7_e_ledger_1_sem_perder_dados(self):
        p = self.criar()
        schema_historico(self.c.db,7)
        self.c.db.execute('DROP TABLE remocoes.copias'); self.c.db.execute('PRAGMA remocoes.user_version=1')
        self.reabrir()
        self.assertEqual(self.c.listar(self.m)[0]['id'], p['id'])
        self.assertEqual(self.c.db.execute('PRAGMA user_version').fetchone()[0], 9)
        self.assertEqual(self.c.db.execute('PRAGMA remocoes.user_version').fetchone()[0], 2)
        self.c.verificar_integridade()


class CopiasServico(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = TemporaryDirectory(); self.clock = [180000.]; self.agora = lambda:self.clock[0]
        self.cfg = configuracao(Path(self.tmp.name)/'banco.sqlite3')
        self.dados = DadosAsync(self.cfg, agora=self.agora); await self.dados.iniciar()
        self.req=[]; self.copiados=[]; self.marcador=None; self.hook=None; self.falha_post=False
        self.versao='7'; self.alteracao_meta={}; self.extra_lista=False; self.incompleta=False; self.renovacoes=0
        self.post_id=DESTINO;self.post_status=200;self.meta_indisponivel=False
        self.prov=Provedores(self.cfg, agora=self.agora, transporte=httpx.MockTransport(self.http))
        self.s=Consultas(self.dados,self.prov,agora=self.agora)
        self.m=Membro('111','222')
        self.cid=await self.b('conectar',self.m,conta='conta-ficticia',cliente=self.cfg.google_id,refresh_token='refresh-ficticio')
        self.fonte=referencia()['arquivo']
        await self.b('configurar_modelo',replace(self.m,administrador=True),escolha='servidor',revisao=0,previa=referencia())

    async def asyncTearDown(self):
        await self.s.fechar();await self.dados.fechar();self.tmp.cleanup()

    async def b(self, metodo, *args, **kw):
        return await self.dados.chamar('cadastro.'+metodo,*args,**kw)

    async def copiar(self,pedido='intencao-ficticia',usuario='222',conexao=None):
        return await self.s.copiar_modelo('111',usuario,conexao=conexao or self.cid,modelo='servidor',pedido=pedido)

    def meta(self):
        return dict(id=DESTINO,mimeType=MIME,isAppAuthorized=True,trashed=False,version='1',ownedByMe=True,
                    shared=False,appProperties=self.marcador,permissions=[dict(type='user',role='owner')])

    async def http(self,req):
        self.req.append(req)
        if self.hook: await self.hook(req)
        if req.url.host=='discord.com':
            if '/members/' in req.url.path:return httpx.Response(200,json={'user':{'id':req.url.path.rsplit('/',1)[1]},'roles':[]})
            if req.url.path.endswith('/roles'):return httpx.Response(200,json=[{'id':'111','permissions':'0'}])
            return httpx.Response(200,json={'owner_id':'999'})
        if req.url.host=='oauth2.googleapis.com':
            self.renovacoes+=1
            return httpx.Response(200,json=dict(access_token='access-ficticio',refresh_token='refresh-rotacionado-ficticio',
                expires_in=3600,expires_at=self.agora()+3600,token_type='Bearer',scope=DRIVE_FILE))
        if req.url.path.endswith('/copy'):
            self.assertEqual(req.method,'POST'); self.assertEqual(req.url.path.split('/')[-2],self.fonte)
            obj=json.loads(req.content);self.assertEqual(obj['parents'],['root']);self.assertEqual(set(obj),{'name','parents','appProperties'})
            self.marcador=obj['appProperties'];self.copiados.append(DESTINO)
            if self.falha_post:raise httpx.ReadTimeout('resposta fictícia perdida')
            return httpx.Response(self.post_status,json={'id':self.post_id})
        self.assertEqual(req.method,'GET')
        if req.url.path.endswith('/'+self.fonte):
            return httpx.Response(200,json=dict(id=self.fonte,mimeType=MIME,isAppAuthorized=True,trashed=False,version=self.versao))
        if req.url.path.endswith('/'+DESTINO):return httpx.Response(503 if self.meta_indisponivel else 200,json={**self.meta(),**self.alteracao_meta})
        if req.url.path.endswith('/files'):
            q=parse_qs(req.url.query.decode());self.assertNotIn('trashed=false',q['q'][0])
            return httpx.Response(200,json=dict(files=[{'id':x} for x in self.copiados]+([{'id':'outra_copia_ficticia_123456'}] if self.extra_lista else []),incompleteSearch=self.incompleta))
        self.fail('Rota externa inesperada: '+req.url.host+req.url.path)

    def posts(self): return [r for r in self.req if r.url.path.endswith('/copy')]

    async def ref(self):
        return await self.b('preparar_copia_modelo',self.m,conexao=self.cid,modelo='servidor',pedido='intencao-ficticia')

    async def test_fluxo_identifica_copia_privada_sem_cadastrar_limpar_ou_liberar(self):
        r=await self.copiar();self.assertEqual(len(self.posts()),1);self.assertFalse(r['criacao_disponivel'])
        self.assertFalse(await self.b('listar',self.m));self.assertEqual(self.renovacoes,1)
        self.assertFalse(any(x.url.host=='sheets.googleapis.com' for x in self.req))
        self.assertNotIn(DESTINO,str(r));self.assertNotIn('access-ficticio',str(r))
        cred=await self.b('_credencial_copia',self.m,await self.ref())
        self.assertEqual(cred.refresh_token,'refresh-rotacionado-ficticio')

    async def test_resposta_perdida_reconcilia_apos_reinicio_sem_segundo_post(self):
        self.falha_post=True
        with self.assertRaises(ErroProvedor) as e:await self.copiar()
        self.assertEqual(e.exception.codigo,'copia_incerta')
        await self.s.fechar();await self.dados.fechar()
        self.dados=DadosAsync(self.cfg,agora=self.agora);await self.dados.iniciar()
        self.s=Consultas(self.dados,self.prov,agora=self.agora)
        self.assertTrue((await self.copiar())['copia_identificada']);self.assertEqual(len(self.posts()),1)

    async def test_ausencia_na_busca_nao_prova_que_pode_repetir_post(self):
        self.falha_post=True
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.copiados=[]
        for _ in range(2):
            with self.assertRaises(ErroProvedor) as e:await self.copiar()
            self.assertEqual(e.exception.codigo,'copia_incerta')
        self.assertEqual(len(self.posts()),1)

    async def test_429_do_post_nao_libera_reenvio_automatico(self):
        self.post_status=429
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.copiados=[]
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.assertEqual(len(self.posts()),1)

    async def test_id_da_origem_no_retorno_nao_e_adotado_como_destino(self):
        self.post_id=self.fonte
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.assertEqual(len(self.posts()),1)
        self.assertFalse(any(r.url.path.endswith('/'+DESTINO) for r in self.req))

    async def test_falha_ao_observar_destino_reconcilia_sem_segundo_post(self):
        self.meta_indisponivel=True
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.meta_indisponivel=False
        self.assertTrue((await self.copiar())['copia_identificada'])
        self.assertEqual(len(self.posts()),1)

    async def test_backup_sem_versao_de_origem_nao_identifica_copia_tardia(self):
        ref=await self.ref()
        # Transformação conservadora do backup: preparada vira enviada, mas o
        # backup pode ter sido feito antes de observar/fixar a versão da origem.
        def restaurado():
            c=self.dados.store.c;d=c.contexto_copia(self.m,ref)
            self.assertIsNone(d['versao_origem']);c._guardar_copia(ref,{**d,'estado':'enviada'})
        await asyncio.wrap_future(self.dados.executor.submit(restaurado))
        self.copiados=[DESTINO];self.marcador=marcadores(ref.operacao,self.fonte)
        with self.assertRaises(Conflito):await self.copiar()
        d=await self.b('contexto_copia',self.m,ref)
        self.assertEqual(d['estado'],'enviada');self.assertIsNone(d['versao_origem']);self.assertIsNone(d['destino'])
        self.assertFalse(self.posts())
        self.assertFalse(any(r.url.host in ('www.googleapis.com','sheets.googleapis.com') for r in self.req))

    async def test_candidata_muda_durante_conferencia_da_origem_nao_e_identificada(self):
        vista=False
        async def hook(req):
            nonlocal vista
            if req.url.path.endswith('/'+DESTINO):vista=True
            if vista and req.url.path.endswith('/'+self.fonte):self.alteracao_meta={'version':'2'}
        self.hook=hook
        with self.assertRaises(Conflito):await self.copiar()
        d=await self.b('contexto_copia',self.m,await self.ref())
        self.assertEqual(d['estado'],'enviada');self.assertIsNone(d['destino'])
        self.assertEqual(d['candidata'],dict(arquivo=DESTINO,versao='1'))
        self.assertEqual(d['observacoes_versao'][-1]['esperada'],'1')
        self.assertEqual(d['observacoes_versao'][-1]['observada'],'2')
        with self.assertRaises(Conflito):await self.copiar()
        self.assertEqual(len(self.posts()),1)

    async def test_candidata_fica_persistida_quando_fonte_muda_sem_adotar_versao_nova(self):
        async def hook(req):
            if req.url.path.endswith('/'+DESTINO):self.versao='8'
        self.hook=hook
        with self.assertRaises(Conflito):await self.copiar()
        d=await self.b('contexto_copia',self.m,await self.ref())
        self.assertEqual(d['estado'],'enviada');self.assertIsNone(d['versao_destino'])
        self.assertEqual(d['versao_origem'],'7');self.assertEqual(d['candidata']['versao'],'1')
        self.assertEqual(d['observacoes_versao'][-1]['etapa'],'origem_apos_candidata')
        self.assertEqual(d['observacoes_versao'][-1]['observada'],'8')
        self.req.clear()
        with self.assertRaises(Conflito):await self.copiar()
        self.assertFalse(any(r.url.path.endswith('/'+DESTINO) or r.url.path.endswith('/files') for r in self.req))
        self.assertFalse(self.posts())

    async def test_autorizacao_revogada_durante_cota_impede_envio(self):
        caso=self
        class Cota:
            async def esperar(self,conta):
                await caso.b('desconectar',caso.m,caso.cid)
        self.s.cotas=Cota()
        with self.assertRaises(AcessoNegado):await self.copiar()
        self.assertFalse(self.posts())

    async def test_modelo_trocado_durante_cota_impede_envio(self):
        caso=self
        class Cota:
            async def esperar(self,conta):
                await caso.b('configurar_modelo',replace(caso.m,administrador=True),escolha='ciclo',revisao=1)
        self.s.cotas=Cota()
        with self.assertRaises(Conflito):await self.copiar()
        self.assertFalse(self.posts())

    async def test_pedidos_concorrentes_coalescem_uma_copia(self):
        entrou=asyncio.Event();liberar=asyncio.Event()
        async def hook(req):
            if req.url.path.endswith('/copy'):entrou.set();await liberar.wait()
        self.hook=hook
        ts=[asyncio.create_task(self.copiar()) for _ in range(4)]
        await entrou.wait();await asyncio.sleep(.02);liberar.set()
        rs=await asyncio.gather(*ts);self.assertTrue(all(x==rs[0] for x in rs));self.assertEqual(len(self.posts()),1)

    async def test_cancelamento_no_post_nao_reenvia_ao_retomar(self):
        entrou=asyncio.Event()
        async def hook(req):
            if req.url.path.endswith('/copy'):entrou.set();await asyncio.Event().wait()
        self.hook=hook;t=asyncio.create_task(self.copiar());await entrou.wait();t.cancel()
        with self.assertRaises(asyncio.CancelledError):await t
        self.hook=None
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.assertEqual(len(self.posts()),1)

    async def test_conexao_alheia_recusa_antes_de_google_inclusive_admin(self):
        with self.assertRaises(AcessoNegado):await self.copiar(usuario='999')
        self.assertFalse(any(x.url.host!='discord.com' for x in self.req))

    async def test_modelo_alterado_antes_da_rede_recusa_sem_post(self):
        self.versao='8'
        with self.assertRaises(Conflito):await self.copiar()
        self.assertFalse(self.posts())

    async def test_modelo_alterado_durante_copia_nao_e_identificado_ou_repetido(self):
        async def hook(req):
            if req.url.path.endswith('/copy'):self.versao='8'
        self.hook=hook
        for _ in range(2):
            with self.assertRaises(Conflito):await self.copiar()
        self.assertEqual(len(self.posts()),1)

    async def test_multiplos_candidatos_na_busca_nao_escolhem_primeiro(self):
        self.falha_post=True
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.extra_lista=True
        with self.assertRaises(ErroProvedor) as e:await self.copiar()
        self.assertEqual(e.exception.codigo,'copia_ambigua');self.assertEqual(len(self.posts()),1)

    async def test_busca_incompleta_nao_adota_candidato(self):
        self.falha_post=True
        with self.assertRaises(ErroProvedor):await self.copiar()
        self.incompleta=True
        with self.assertRaises(ErroProvedor) as e:await self.copiar()
        self.assertEqual(e.exception.codigo,'copia_ambigua')

    async def test_copia_compartilhada_trashed_ou_marcador_errado_recusa(self):
        # Cada observação é GET. Nenhuma falha pode voltar ao POST.
        await self.copiar()
        for patch in ({'shared':True},{'trashed':True},{'ownedByMe':False},{'driveId':'drive-ficticio'},
                      {'appProperties':{}},{'permissions':[]},{'permissions':[{'type':'anyone','role':'reader'}]}):
            self.alteracao_meta=patch
            with self.subTest(patch=patch),self.assertRaises(ErroProvedor):await self.copiar()
        self.assertEqual(len(self.posts()),1)

    async def test_reconexao_durante_oauth_nao_adota_grant_antigo(self):
        async def hook(req):
            if req.url.host=='oauth2.googleapis.com':
                await self.b('conectar',self.m,conta='conta-ficticia',cliente=self.cfg.google_id,refresh_token='novo-grant-ficticio')
        self.hook=hook
        with self.assertRaises(Conflito):await self.copiar()
        self.assertFalse(self.posts())
