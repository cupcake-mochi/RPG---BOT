"""Fila/OAuth/HTTP/banco reais, transporte externo simulado; nenhuma conta real."""
import asyncio
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import parse_qs
import httpx

from carteira_viva.consultas import Consultas
from carteira_viva.fila import Fila
from carteira_viva.fluxos import DadosAsync
from carteira_viva.permissoes import Membro
from carteira_viva.provedores import DRIVE_FILE, Provedores, ErroProvedor
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_conferencia_inicializacao import Dados
from testes.test_carteira_grade_inicializacao import ARQUIVO


class CotasContadas:
    def __init__(self): self.contas = []; self.hook = None
    async def esperar(self, conta):
        self.contas.append(conta)
        if self.hook: await self.hook()


class ConferenciasServicoTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = TemporaryDirectory(); self.clock = [180000.]
        self.agora = lambda: self.clock[0]
        self.cfg = configuracao(Path(self.tmp.name)/'banco.sqlite3')
        self.dados = DadosAsync(self.cfg, agora=self.agora); await self.dados.iniciar()
        self.data = Dados('financeiro'); self.data.mapa.update(Dados().mapa)
        for n in ('EXTRATO','SALÁRIOS','DADOS_SALARIOS'): self.data.grades[n]['gridProperties']['rowCount'] = 100
        self.tokens = []; self.discord = []; self.hook = None; self.token_hook = None
        self.presentes = True; self.roles = {}; self.token_erro = None; self.duracao = 3600
        self.prov = Provedores(self.cfg, agora=self.agora, transporte=httpx.MockTransport(self.http))
        self.s = Consultas(self.dados, self.prov, agora=self.agora)
        self.s.cotas = CotasContadas()
        self.m = Membro('111','222')
        self.cid = await self.b('conectar', self.m, conta='conta-ficticia', cliente=self.cfg.google_id, refresh_token='refresh-inicial-ficticio')
        p = await self.b('cadastrar', self.m, conexao=self.cid, arquivo=ARQUIVO, nome='Personagem fictício', contrato='analise-12', responsabilidade=True, pedido='cadastro-ficticio')
        self.pid = p['id']

    async def asyncTearDown(self):
        await self.s.fechar(); await self.dados.fechar(); self.tmp.cleanup()

    async def b(self, metodo, *args, **kw): return await self.dados.chamar('cadastro.'+metodo, *args, **kw)

    async def http(self, req):
        if self.hook: await self.hook(req)
        if req.url.host == 'oauth2.googleapis.com':
            self.tokens.append(parse_qs(req.content.decode()))
            if self.token_hook: await self.token_hook()
            if self.token_erro: return httpx.Response(400, json={'error':self.token_erro})
            return httpx.Response(200, json={'access_token':'access-ficticio', 'refresh_token':f'refresh-ficticio-{len(self.tokens)}', 'expires_in':self.duracao, 'expires_at':self.agora()+self.duracao, 'token_type':'Bearer', 'scope':DRIVE_FILE})
        if req.url.host == 'discord.com':
            self.discord.append(req)
            if '/members/' in req.url.path:
                if not self.presentes: return httpx.Response(404, json={})
                u = req.url.path.rsplit('/',1)[1]
                return httpx.Response(200, json={'user':{'id':u},'roles':self.roles.get(u,[])})
            if req.url.path.endswith('/roles'):
                return httpx.Response(200, json=[{'id':'111','permissions':'0'},{'id':'revisor','permissions':'0'},{'id':'adm','permissions':'8'}])
            return httpx.Response(200, json={'owner_id':'777'})
        return self.data.http(req)

    async def conferir(self, *, usuario='222', retomar=False):
        return await self.s.conferir_inicializacao('111', usuario, self.pid, retomar=retomar)

    async def bilhete(self): return await self.b('retomar_conferencia_rest', self.m, self.pid)

    async def test_fluxo_http_completo_renova_cifra_refresh_e_nao_libera(self):
        r = await self.conferir()
        self.assertEqual(r['dominios_conferidos'], 2)
        self.assertEqual([x['erros'] for x in r['resultados']], [0,0])
        self.assertFalse(r['criacao_disponivel']); self.assertTrue(r['leitura_historica'])
        self.assertEqual(len(self.tokens),1); self.assertEqual(self.tokens[0]['grant_type'],['refresh_token'])
        ref,_,_,_ = await self.b('contexto_operacao_rest', self.m, await self.bilhete())
        cred = await self.b('_credencial', self.m, ref)
        self.assertEqual(cred.refresh_token,'refresh-ficticio-1')
        self.assertEqual(len(self.data.requests),len(self.s.cotas.contas))
        self.assertEqual(len(set(self.s.cotas.contas)),1)
        for req in self.data.requests: self.assertEqual(req.method,'GET')
        for segredo in (ARQUIVO,'access-ficticio','refresh-ficticio','conta-ficticia'): self.assertNotIn(segredo,str(r))

    async def test_pedidos_repetidos_coalescem_sem_invalidar_referencia(self):
        entrou=asyncio.Event(); liberar=asyncio.Event()
        async def bloquear(): entrou.set(); await liberar.wait()
        self.token_hook=bloquear
        ts=[asyncio.create_task(self.conferir()) for _ in range(4)]
        await entrou.wait(); await asyncio.sleep(.02); liberar.set()
        rs=await asyncio.gather(*ts)
        self.assertEqual(len(self.tokens),1); self.assertTrue(all(r==rs[0] for r in rs))
        rs[0]['resultados'].clear(); self.assertEqual(len(rs[1]['resultados']),2)

    async def test_nao_dono_e_booleano_invalido_nao_consultam_google(self):
        with self.assertRaises(AcessoNegado): await self.conferir(usuario='999')
        with self.assertRaises(ErroCarteira): await self.conferir(retomar='sim')
        self.assertFalse(self.tokens); self.assertFalse(self.data.requests)

    async def test_troca_enquanto_na_fila_nao_renova_nem_le(self):
        self.s.fila = Fila(paralelos=1)
        entrou=asyncio.Event(); liberar=asyncio.Event()
        async def segurar(): entrou.set(); await liberar.wait()
        a=asyncio.create_task(self.s.fila.executar(('outro',),('outra','pessoa'),segurar))
        await entrou.wait(); t=asyncio.create_task(self.conferir()); await asyncio.sleep(.02)
        await self.b('trocar_arquivo',self.m,self.pid,conexao=self.cid,arquivo='arquivo_descartavel_sintetico_002',contrato='analise-12',revisao=1,pedido='trocar')
        liberar.set(); await a
        with self.assertRaises(Conflito): await t
        self.assertFalse(self.tokens); self.assertFalse(self.data.requests)

    async def test_invalid_grant_remove_segredo_e_bloqueia_fonte(self):
        self.token_erro='invalid_grant'
        with self.assertRaises(ErroProvedor): await self.conferir()
        with self.assertRaises(ErroCarteira): await self.b('reservar_leitura',self.m,self.pid)
        self.assertFalse(self.data.requests)

    async def test_erro_oauth_temporario_nao_revoga_conexao(self):
        self.token_erro='temporarily_unavailable'
        with self.assertRaises(ErroProvedor): await self.conferir()
        self.assertIsNotNone(await self.b('reservar_leitura',self.m,self.pid))
        self.assertFalse(self.data.requests)

    async def test_reautorizacao_durante_oauth_nao_grava_refresh_antigo(self):
        async def reconectar():
            await self.b('conectar',self.m,conta='conta-ficticia',cliente=self.cfg.google_id,refresh_token='refresh-novo-ficticio')
        self.token_hook=reconectar
        with self.assertRaises(Conflito): await self.conferir()
        ref=await self.b('reservar_leitura',self.m,self.pid)
        self.assertEqual((await self.b('_credencial',self.m,ref)).refresh_token,'refresh-novo-ficticio')
        self.assertFalse(self.data.requests)

    async def test_invalid_grant_antigo_nao_revoga_reautorizacao_nova(self):
        async def reconectar():
            await self.b('conectar',self.m,conta='conta-ficticia',cliente=self.cfg.google_id,refresh_token='refresh-novo-ficticio')
        self.token_hook=reconectar; self.token_erro='invalid_grant'
        with self.assertRaises(ErroProvedor): await self.conferir()
        ref=await self.b('reservar_leitura',self.m,self.pid)
        self.assertEqual((await self.b('_credencial',self.m,ref)).refresh_token,'refresh-novo-ficticio')

    async def test_cargo_removido_durante_cota_nao_emite_primeiro_get(self):
        await self.b('configurar',replace(self.m,administrador=True),revisores=('revisor',))
        self.roles['999']=['revisor']
        async def remover(): self.roles['999']=[]
        self.s.cotas.hook=remover
        with self.assertRaises(AcessoNegado): await self.conferir(usuario='999')
        self.assertEqual(len(self.tokens),1); self.assertFalse(self.data.requests)

    async def test_revogacao_durante_cota_nao_emite_get(self):
        async def revogar(): await self.b('desconectar',self.m,self.cid)
        self.s.cotas.hook=revogar
        with self.assertRaises(ErroCarteira): await self.conferir()
        self.assertFalse(self.data.requests)

    async def test_token_expira_durante_cota_interrompe_sem_get(self):
        self.duracao=60
        async def expirar(): self.clock[0]+=50
        self.s.cotas.hook=expirar
        with self.assertRaises(ErroProvedor): await self.conferir()
        self.assertFalse(self.data.requests)

    async def interromper_progressao(self):
        entrou=asyncio.Event(); liberar=asyncio.Event()
        async def bloquear(req):
            if req.url.params.get('ranges')=="'CONFIGURAÇÃO'!C46:H46": entrou.set(); await liberar.wait()
        self.hook=bloquear
        t=asyncio.create_task(self.conferir()); await asyncio.wait_for(entrou.wait(),20)
        t.cancel()
        with self.assertRaises(asyncio.CancelledError): await t
        # O último cliente cancelado aguarda o trabalho encerrando antes da retomada.
        await self.s.fechar(); self.s=Consultas(self.dados,self.prov,agora=self.agora); self.s.cotas=CotasContadas()
        self.hook=None
        return await self.bilhete()

    async def test_cancelamento_preserva_financeiro_e_retomada_renova_sem_reler(self):
        b=await self.interromper_progressao(); self.assertEqual(b.revisao,1)
        self.data.requests.clear(); r=await self.conferir(retomar=True)
        self.assertEqual(r['dominios_conferidos'],2); self.assertEqual(len(self.tokens),2)
        # Progressão em 2 lotes (antes 29).
        self.assertEqual(len(self.data.requests),11); self.assertEqual(len(self.s.cotas.contas),11)

    async def test_versao_mudou_entre_reinicio_e_retomada_nao_le_celulas(self):
        b=await self.interromper_progressao(); self.data.versao='999'; self.data.requests.clear()
        with self.assertRaises(Conflito): await self.conferir(retomar=True)
        self.assertEqual(len(self.data.requests),1); self.assertEqual(await self.bilhete(),b)

    async def test_nova_sem_retomar_nao_invalida_trabalho_existente(self):
        b=await self.interromper_progressao(); self.data.requests.clear(); self.tokens.clear()
        with self.assertRaises(Conflito): await self.conferir()
        self.assertEqual(await self.bilhete(),b); self.assertFalse(self.tokens); self.assertFalse(self.data.requests)

    async def test_retomada_expirada_enquanto_aguarda_fila_nao_consulta_google(self):
        await self.interromper_progressao()
        self.s.fila=Fila(paralelos=1); entrou=asyncio.Event(); liberar=asyncio.Event()
        async def segurar(): entrou.set(); await liberar.wait()
        a=asyncio.create_task(self.s.fila.executar(('outro',),('outra','pessoa'),segurar)); await entrou.wait()
        t=asyncio.create_task(self.conferir(retomar=True)); await asyncio.sleep(.02)
        self.clock[0]+=1800; self.data.requests.clear(); self.tokens.clear(); liberar.set(); await a
        with self.assertRaises(Conflito): await t
        self.assertFalse(self.data.requests); self.assertFalse(self.tokens)

    async def test_retomada_concluida_observa_drive_mas_nao_rele_dominios(self):
        await self.conferir(); self.data.requests.clear()
        r=await self.conferir(retomar=True)
        self.assertEqual(r['dominios_conferidos'],2); self.assertEqual(len(self.data.requests),1)
        self.data.versao='999'
        with self.assertRaises(Conflito): await self.conferir(retomar=True)

    async def test_trava_compartilhada_preserva_cadeia_de_refresh_entre_personagens(self):
        p=await self.b('cadastrar',self.m,conexao=self.cid,arquivo='arquivo_descartavel_sintetico_002',nome='Outro fictício',contrato='analise-12',responsabilidade=True,pedido='segundo')
        a=await self.b('reservar_leitura',self.m,self.pid); b=await self.b('reservar_leitura',self.m,p['id'])
        entrou=asyncio.Event(); liberar=asyncio.Event()
        async def esperar(): entrou.set(); await liberar.wait()
        self.token_hook=esperar
        t1=asyncio.create_task(self.s._renovar_google(self.m,a)); await entrou.wait()
        t2=asyncio.create_task(self.s._renovar_google(self.m,b)); await asyncio.sleep(.02)
        self.assertEqual(len(self.tokens),1); liberar.set(); await asyncio.gather(t1,t2)
        self.assertEqual(self.tokens[1]['refresh_token'],['refresh-ficticio-1'])
        self.assertEqual((await self.b('_credencial',self.m,a)).refresh_token,'refresh-ficticio-2')

    async def test_cliente_google_diferente_recusa_antes_do_oauth(self):
        self.prov.cfg=replace(self.cfg,google_id='cliente-diferente-ficticio')
        with self.assertRaises(ErroCarteira): await self.conferir()
        self.assertFalse(self.tokens); self.assertFalse(self.data.requests)

    async def test_ficha_5000_linhas_respeita_cota_em_todos_os_126_gets(self):
        for n in ('EXTRATO','SALÁRIOS','DADOS_SALARIOS'): self.data.grades[n]['gridProperties']['rowCount']=5000
        r=await self.conferir()
        self.assertEqual([x['paginas_lidas'] for x in r['resultados']],[50,8])
        # Lotes: 50+8 faixas em 37+2 lotes, 3 GETs cada (antes 183).
        self.assertEqual(len(self.data.requests),126); self.assertEqual(len(self.s.cotas.contas),126)
        self.assertFalse(r['conferencia_conjunta_concluida'])

    async def test_saida_durante_get_nao_finaliza_dominio(self):
        def sair(): self.presentes=False
        self.data.depois=sair
        with self.assertRaises(ErroCarteira): await self.conferir()
        self.presentes=True
        self.assertEqual((await self.bilhete()).revisao,0)

    async def test_cancelar_um_cliente_mantem_outro_com_mesma_operacao(self):
        entrou=asyncio.Event(); liberar=asyncio.Event()
        async def esperar(): entrou.set(); await liberar.wait()
        self.token_hook=esperar
        a=asyncio.create_task(self.conferir()); await entrou.wait()
        b=asyncio.create_task(self.conferir()); await asyncio.sleep(.02)
        a.cancel()
        with self.assertRaises(asyncio.CancelledError): await a
        liberar.set(); self.assertEqual((await b)['dominios_conferidos'],2)
        self.assertEqual(len(self.tokens),1)

    async def test_perda_de_cargo_no_oauth_nega_leitura_mas_preserva_refresh_do_dono(self):
        await self.b('configurar',replace(self.m,administrador=True),revisores=('revisor',))
        self.roles['999']=['revisor']
        async def remover(): self.roles['999']=[]
        self.token_hook=remover
        with self.assertRaises(AcessoNegado): await self.conferir(usuario='999')
        ref=await self.b('reservar_leitura',self.m,self.pid)
        self.assertEqual((await self.b('_credencial',self.m,ref)).refresh_token,'refresh-ficticio-1')
        self.assertFalse(self.data.requests)

    async def test_troca_de_fonte_no_oauth_nega_leitura_mas_preserva_refresh_da_conexao(self):
        async def trocar():
            await self.b('trocar_arquivo',self.m,self.pid,conexao=self.cid,arquivo='arquivo_descartavel_sintetico_002',contrato='analise-12',revisao=1,pedido='trocar-oauth')
        self.token_hook=trocar
        with self.assertRaises(Conflito): await self.conferir()
        ref=await self.b('reservar_leitura',self.m,self.pid)
        self.assertEqual((await self.b('_credencial',self.m,ref)).refresh_token,'refresh-ficticio-1')
        self.assertFalse(self.data.requests)

    async def test_refresh_concorrente_nao_e_sobrescrito_por_resposta_atrasada(self):
        ref=await self.b('reservar_leitura',self.m,self.pid); cred=await self.b('_credencial',self.m,ref)
        await self.b('_guardar_renovacao_google',self.cid,autorizacao=cred.autorizacao,refresh_anterior=cred.refresh_token,refresh_novo='refresh-mais-novo-ficticio')
        with self.assertRaises(Conflito):
            await self.b('_guardar_renovacao_google',self.cid,autorizacao=cred.autorizacao,refresh_anterior=cred.refresh_token,refresh_novo='refresh-atrasado-ficticio')
        self.assertEqual((await self.b('_credencial',self.m,ref)).refresh_token,'refresh-mais-novo-ficticio')

    async def test_grant_novo_ou_desconectado_nao_aceita_refresh_anterior(self):
        ref=await self.b('reservar_leitura',self.m,self.pid); cred=await self.b('_credencial',self.m,ref)
        await self.b('conectar',self.m,conta='conta-ficticia',cliente=self.cfg.google_id,refresh_token='refresh-novo-grant-ficticio')
        with self.assertRaises(Conflito):
            await self.b('_guardar_renovacao_google',self.cid,autorizacao=cred.autorizacao,refresh_anterior=cred.refresh_token,refresh_novo='atrasado-ficticio')
        ref=await self.b('reservar_leitura',self.m,self.pid); cred=await self.b('_credencial',self.m,ref)
        await self.b('desconectar',self.m,self.cid)
        with self.assertRaises(Conflito):
            await self.b('_guardar_renovacao_google',self.cid,autorizacao=cred.autorizacao,refresh_anterior=cred.refresh_token,refresh_novo='atrasado-ficticio')

    async def test_cancelar_durante_oauth_conclui_manutencao_sem_ler_google(self):
        entrou=asyncio.Event(); liberar=asyncio.Event()
        async def esperar(): entrou.set(); await liberar.wait()
        self.token_hook=esperar
        t=asyncio.create_task(self.conferir()); await entrou.wait(); t.cancel()
        with self.assertRaises(asyncio.CancelledError): await t
        liberar.set(); await self.s.fechar()
        ref=await self.b('reservar_leitura',self.m,self.pid)
        self.assertEqual((await self.b('_credencial',self.m,ref)).refresh_token,'refresh-ficticio-1')
        self.assertFalse(self.data.requests)
