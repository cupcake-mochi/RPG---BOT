"""Observações atuais, sem TTL, e prova de acesso pelo banco da conferência."""
import copy
from dataclasses import replace
from pathlib import Path
import unittest
import httpx

from carteira_viva.provedores import Provedores, ErroProvedor
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from testes.test_carteira_provedores import configuracao
from testes import test_carteira_conferencias_servico as cenarios


class ObservacaoMembroTeste(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.req=[]; self.status=200
        self.membro={'user':{'id':'222'},'roles':['444']}
        self.p=Provedores(configuracao(Path('nao_criar_observacao.sqlite3')), transporte=httpx.MockTransport(self.http))
    def http(self,r):
        self.req.append(r)
        if '/members/' in r.url.path: return httpx.Response(self.status,json=self.membro)
        if r.url.path.endswith('/roles'): return httpx.Response(200,json=[{'id':'444','permissions':'8'}])
        return httpx.Response(200,json={'owner_id':'222'})
    async def sim(self,m): return True
    async def nao(self,m): return False

    async def test_prova_basica_so_confirma_membro_e_nao_inventa_privilegios(self):
        m=await self.p.membro_para_leitura('111','222',self.sim)
        self.assertEqual(m.cargos,frozenset({'444'})); self.assertTrue(m.presente)
        self.assertFalse(m.administrador or m.dono_servidor or m.gerenciar_servidor)
        self.assertEqual(len(self.req),1); self.assertIn('/members/',self.req[0].url.path)

    async def test_sem_prova_basica_mesmas_tres_consultas_e_permissoes(self):
        m=await self.p.membro_para_leitura('111','222',self.nao)
        self.assertTrue(m.administrador); self.assertTrue(m.dono_servidor)
        self.assertEqual(len(self.req),3)
        self.assertEqual(sum('/members/' in r.url.path for r in self.req),1)

    async def test_segunda_observacao_reconsulta_membro_e_cargos(self):
        a=await self.p.membro_para_leitura('111','222',self.sim)
        self.membro['roles']=[]
        b=await self.p.membro_para_leitura('111','222',self.sim)
        self.assertEqual(a.cargos,frozenset({'444'})); self.assertEqual(b.cargos,frozenset())
        self.assertEqual(len(self.req),2)

    async def test_resposta_invalida_nao_chama_prova_nem_busca_privilegios(self):
        original=copy.deepcopy(self.membro); chamadas=[]
        async def provar(m): chamadas.append(m); return True
        casos=[None,{}, {'user':{'id':'999'},'roles':[]},
               {'user':{'id':'222'},'roles':'444'}, {'user':{'id':'222'},'roles':[None]},
               {**original,'pending':True}]
        for v in casos:
            with self.subTest(v=v):
                self.membro=v; antes=len(self.req)
                with self.assertRaises(ErroCarteira): await self.p.membro_para_leitura('111','222',provar)
                self.assertEqual(len(self.req)-antes,1)
        self.assertFalse(chamadas)

    async def test_callback_invalido_ou_resposta_truthy_nao_concede_acesso(self):
        for cb in (None,True,{}):
            with self.assertRaises(ErroProvedor): await self.p.membro_para_leitura('111','222',cb)
        self.assertFalse(self.req)
        for x in (1,'sim',{},None):
            async def retornar(m): return x
            with self.assertRaises(ErroProvedor): await self.p.membro_para_leitura('111','222',retornar)
        self.assertEqual(len(self.req),4)

    async def test_limite_ou_saida_nao_reutiliza_observacao_anterior(self):
        await self.p.membro_para_leitura('111','222',self.sim)
        for status in (429,503,404,403):
            self.status=status
            with self.subTest(status=status),self.assertRaises(ErroCarteira):
                await self.p.membro_para_leitura('111','222',self.sim)
        self.assertEqual(len(self.req),5)

    async def test_conflito_do_banco_nao_vira_fallback_de_permissao(self):
        async def mudar(m): raise Conflito('Fonte mudou')
        with self.assertRaises(Conflito): await self.p.membro_para_leitura('111','222',mudar)
        self.assertEqual(len(self.req),1)

    async def test_membro_completo_comum_continua_sem_atalho(self):
        await self.p.membro('111','222'); await self.p.membro('111','222')
        self.assertEqual(len(self.req),6)


class ObservacaoServicoTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Reusa dados/HTTP/worker reais sem importar TestCase para o discovery.
        self.c=cenarios.ConferenciasServicoTeste('test_fluxo_http_completo_renova_cifra_refresh_e_nao_libera')
        await self.c.asyncSetUp()
    async def asyncTearDown(self): await self.c.asyncTearDown()
    def papeis(self): return sum(r.url.path.endswith('/roles') for r in self.c.discord)

    async def test_dono_5000_linhas_reduz_requisicoes_preservando_183_gets_google(self):
        for n in ('EXTRATO','SALÁRIOS','DADOS_SALARIOS'): self.c.data.grades[n]['gridProperties']['rowCount']=5000
        r=await self.c.conferir()
        self.assertEqual([x['erros'] for x in r['resultados']],[0,0])
        self.assertEqual(len(self.c.data.requests),183); self.assertEqual(len(self.c.s.cotas.contas),183)
        self.assertLessEqual(len(self.c.discord),4*183)  # Base anterior: 1.686.
        self.assertLessEqual(self.papeis(),10)
        self.assertFalse(r['criacao_disponivel'])

    async def test_revisor_explicito_tambem_pode_provar_sem_privilégio_admin(self):
        await self.c.b('configurar',replace(self.c.m,administrador=True),revisores=('revisor',))
        self.c.roles['999']=['revisor']
        r=await self.c.conferir(usuario='999')
        self.assertEqual(r['dominios_conferidos'],2); self.assertLessEqual(self.papeis(),10)
        self.assertLessEqual(len(self.c.discord),4*len(self.c.data.requests))

    async def test_administrador_sem_cargo_configurado_continua_por_prova_completa(self):
        self.c.roles['999']=['adm']
        r=await self.c.conferir(usuario='999')
        self.assertEqual(r['dominios_conferidos'],2)
        self.assertGreater(self.papeis(),100)
        self.assertEqual(len(self.c.discord),3*self.papeis())

    async def test_permissao_admin_removida_durante_cota_nao_le(self):
        self.c.roles['999']=['adm']; original=self.c.http; bits=['8']
        async def http(req):
            resposta=await original(req)
            if req.url.path.endswith('/roles'):
                papeis=resposta.json(); papeis[-1]['permissions']=bits[0]
                return httpx.Response(200,json=papeis)
            return resposta
        self.c.prov.transporte=httpx.MockTransport(http)
        async def remover(): bits[0]='32'  # Gerenciar servidor não é Administrator.
        self.c.s.cotas.hook=remover
        with self.assertRaises(AcessoNegado): await self.c.conferir(usuario='999')
        self.assertFalse(self.c.data.requests)

    async def test_dono_do_servidor_trocado_durante_cota_nao_le(self):
        original=self.c.http; dono=['777']
        async def http(req):
            resposta=await original(req)
            if req.url.path.endswith('/guilds/111'): return httpx.Response(200,json={'owner_id':dono[0]})
            return resposta
        self.c.prov.transporte=httpx.MockTransport(http)
        async def trocar(): dono[0]='888'
        self.c.s.cotas.hook=trocar
        with self.assertRaises(AcessoNegado): await self.c.conferir(usuario='777')
        self.assertFalse(self.c.data.requests)

    async def test_cargo_desautorizado_no_banco_continua_sendo_negado(self):
        await self.c.b('configurar',replace(self.c.m,administrador=True),revisores=('revisor',))
        self.c.roles['999']=['revisor']
        async def remover(): await self.c.b('configurar',replace(self.c.m,administrador=True),revisores=())
        self.c.s.cotas.hook=remover
        with self.assertRaises(ErroCarteira): await self.c.conferir(usuario='999')
        self.assertFalse(self.c.data.requests)

    async def test_troca_de_fonte_na_cota_nao_tenta_contornar_com_admin(self):
        marcas=[]
        async def trocar():
            marcas.append(self.papeis())
            await self.c.b('trocar_arquivo',self.c.m,self.c.pid,conexao=self.c.cid,arquivo='arquivo_descartavel_sintetico_002',contrato='analise-12',revisao=1,pedido='troca-cota')
        self.c.s.cotas.hook=trocar
        with self.assertRaises(Conflito): await self.c.conferir()
        self.assertFalse(self.c.data.requests); self.assertEqual(self.papeis(),marcas[0])

    async def test_erro_discord_depois_do_get_recusa_sem_revogar_google(self):
        original=self.c.http
        async def http(req):
            if '/members/' in req.url.path and self.c.data.requests:
                self.c.discord.append(req); return httpx.Response(429,json={})
            return await original(req)
        self.c.prov.transporte=httpx.MockTransport(http)
        with self.assertRaises(ErroCarteira): await self.c.conferir()
        self.assertEqual(len(self.c.data.requests),1)
        self.assertIsNotNone(await self.c.b('reservar_leitura',self.c.m,self.c.pid))

    async def test_entrega_revalida_cargo_mesmo_depois_de_dominios_salvos(self):
        await self.c.b('configurar',replace(self.c.m,administrador=True),revisores=('revisor',))
        self.c.roles['999']=['revisor']; executar=self.c.s.fila.executar
        async def interceptar(*a,**kw):
            r=await executar(*a,**kw); self.c.roles['999']=[]; return r
        self.c.s.fila.executar=interceptar
        with self.assertRaises(AcessoNegado): await self.c.conferir(usuario='999')

    async def test_perder_cargo_revisor_mantendo_admin_continua_com_prova_completa(self):
        await self.c.b('configurar',replace(self.c.m,administrador=True),revisores=('revisor',))
        self.c.roles['999']=['revisor','adm']
        async def remover(): self.c.roles['999']=['adm']
        self.c.s.cotas.hook=remover
        r=await self.c.conferir(usuario='999')
        self.assertEqual(r['dominios_conferidos'],2); self.assertGreater(self.papeis(),100)
        self.assertFalse(r['criacao_disponivel'])
