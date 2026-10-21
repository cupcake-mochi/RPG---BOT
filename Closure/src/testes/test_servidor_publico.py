"""Isolamento entre mesas/mundos e mudança administrativa, sem chamar modelos reais."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock

from closure_bot.registro import Registro, Ficha
from closure_bot.servidor import NOVA_TERRA_PADRAO, autorizado
from closure_bot.cogs.servidor import Servidor
from closure_bot.reflexao import refletir

AGORA = datetime(2026,10,21,16,tzinfo=timezone.utc)

class Preferencias(unittest.TestCase):
    def setUp(self): self.r = Registro(':memory:')
    def tearDown(self): self.r.fechar()

    def test_tres_servidores_padrao_e_publico_fechado(self):
        for g in NOVA_TERRA_PADRAO:
            self.assertTrue(self.r.opcoes_servidor(g).nova_terra)
            self.assertFalse(self.r.configurar_publico(g,nova_terra=False).nova_terra)
            self.assertFalse(self.r.opcoes_servidor(g).nova_terra)
        for g in (1,77,999999999999999999):
            self.assertEqual(self.r.opcoes_servidor(g).idioma,'pt-BR')
            self.assertFalse(self.r.opcoes_servidor(g).nova_terra)
            self.assertTrue(self.r.configurar_publico(g,nova_terra=True).nova_terra)
            self.assertFalse(self.r.opcoes_servidor(g+1).nova_terra)

    def test_idioma_independente_e_revisao_so_quando_muda(self):
        a=self.r.configurar_publico(77,idioma='en');self.assertFalse(a.nova_terra)
        self.assertEqual(a.revisao,1)
        self.assertEqual(self.r.configurar_publico(77,idioma='en').revisao,1)
        self.assertEqual(self.r.configurar_publico(77,cargos=(88,)).revisao,1)
        b=self.r.configurar_publico(77,nova_terra=True);self.assertEqual(b.idioma,'en')
        self.assertEqual(b.revisao,2)
        for idioma in ('en-US','fr','EN','',True):
            with self.assertRaises(ValueError):self.r.configurar_publico(77,idioma=idioma)
        with self.assertRaises(ValueError):self.r.configurar_publico(77,nova_terra=1)
        with self.assertRaises(ValueError):self.r.configurar_publico(77,cargos=(0,))

    def test_memoria_por_servidor_e_mundo_sem_migracao_adivinhada(self):
        self.r.gravar_ficha(9,Ficha('ele/dele',('CANARIO_LEGADO',)))
        self.r.gravar_ficha_contexto(9,'77:nova-terra',Ficha(None,('CANARIO_NOVA',)))
        self.r.gravar_ficha_contexto(9,'88:original',Ficha(None,('CANARIO_OUTRO',)))
        for ctx in ('77:original','88:nova-terra'):
            self.assertEqual(self.r.ficha_contexto(9,ctx),Ficha('ele/dele'))
        self.assertEqual(self.r.ficha_contexto(9,'77:nova-terra').fatos,('CANARIO_NOVA',))
        self.assertEqual(self.r.ficha(9).fatos,('CANARIO_LEGADO',))
        self.r.apagar_pessoa(9)
        self.assertEqual(self.r.ficha_contexto(9,'77:nova-terra'),Ficha())
        self.assertEqual(self.r.ficha(9),Ficha())

    def test_barreira_historico_no_primeiro_uso_e_na_troca(self):
        self.r.guardar_fala(canal_id=44,persona='closure',texto='LEGADO',quando=AGORA)
        self.assertEqual(self.r.preparar_contexto(44,77,AGORA),(True,AGORA))
        self.assertEqual(self.r.ultimas_falas(canal_id=44,persona='closure',agora=AGORA),[])
        self.r.guardar_fala(canal_id=44,persona='closure',texto='ORIGINAL',quando=AGORA)
        self.assertEqual(self.r.preparar_contexto(44,77,AGORA+timedelta(seconds=1)),(False,AGORA))
        self.r.configurar_publico(77,nova_terra=True)
        self.assertTrue(self.r.preparar_contexto(44,77,AGORA+timedelta(seconds=2))[0])
        self.assertEqual(self.r.ultimas_falas(canal_id=44,persona='closure',agora=AGORA),[])

    def test_persistencia_aditiva(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'db';r=Registro(p)
            r.definir_responder_nsfw(77,True)
            r.configurar_publico(77,idioma='en',nova_terra=True,cargos=(8,9))
            r.gravar_ficha_contexto(1,'77:nova-terra',Ficha(fatos=('fato salvo',)));r.fechar()
            r=Registro(p)
            self.assertTrue(r.preferencias_servidor(77).responder_nsfw)
            self.assertEqual(r.opcoes_servidor(77).cargos,(8,9))
            self.assertEqual(r.opcoes_servidor(77).idioma,'en')
            self.assertEqual(r.ficha_contexto(1,'77:nova-terra').fatos,('fato salvo',));r.fechar()

class Comandos(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.r=Registro(':memory:');self.c=Servidor(NS(registro=self.r))
    def tearDown(self):self.r.fechar()
    def i(self,admin=False,roles=(),guild=77):
        return NS(guild_id=guild,permissions=NS(administrator=admin,manage_guild=False),
                  user=NS(roles=[NS(id=r) for r in roles]), response=NS(send_message=AsyncMock()))
    async def test_membro_nao_muda_preferencia_e_cargo_pode_mas_nao_delega(self):
        i=self.i();await self.c.mudar_idioma(i,'en');self.assertEqual(self.r.opcoes_servidor(77).idioma,'pt-BR')
        self.r.configurar_publico(77,cargos=(88,));i=self.i(roles=(88,))
        await self.c.mudar_idioma(i,'en');self.assertEqual(self.r.opcoes_servidor(77).idioma,'en')
        self.assertFalse(await self.c.permitir(self.i(roles=(88,)),somente_admin=True))
        self.assertFalse(autorizado(self.i(roles=(88,)).user,self.r.opcoes_servidor(78)))
    async def test_admin_pode_e_retorno_no_novo_idioma(self):
        i=self.i(True);await self.c.mudar_idioma(i,'en')
        self.assertIn('Server language: **English**',i.response.send_message.call_args.args[0])
        i=self.i(True);await self.c.mudar_idioma(i,'pt-BR')
        self.assertIn('Português do Brasil',i.response.send_message.call_args.args[0])
    async def test_dm_nao_grava(self):
        i=self.i(True,guild=None);await self.c.mudar_idioma(i,'en')
        self.assertIn('servidor',i.response.send_message.call_args.args[0])
    async def test_reflexao_um_pedido_com_o_mesmo_autor_em_tres_contextos(self):
        for m,ctx in enumerate(('77:original','77:nova-terra','88:original'),1):
            self.r.guardar_mensagem_do_dia(message_id=m,autor_id=9,persona='closure',texto=f'gosto do hobby {m}',contexto=ctx)
        saida=json.dumps([{'autor':n,'mensagem':n,'fato':f'gosta do hobby {n}'} for n in (1,2,3)])
        modelos=NS(responder=AsyncMock(return_value=NS(texto=saida)))
        await refletir(self.r,modelos)
        self.assertEqual(modelos.responder.await_count,1)
        for m,ctx in enumerate(('77:original','77:nova-terra','88:original'),1):
            self.assertEqual(self.r.ficha_contexto(9,ctx).fatos,(f'gosta do hobby {m}',))
        self.assertEqual(self.r.ficha(9).fatos,())
        self.assertEqual(self.r.mensagens_do_dia(),[])
        self.assertEqual(self.r._db.execute('select count(*) from origem_mensagens').fetchone()[0],0)

class FontesDoPrompt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sys
        cls.raiz=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(cls.raiz/'ferramentas/prompt_do_site'))
        import site_prompt
        cls.ponte=site_prompt
    def test_original_nao_recebe_fontes_da_campanha_e_alternancia_nao_contamina(self):
        for persona in ('kal','clo'):
            for ativa in (False,True,False):
                p=self.ponte.montar(persona,'O que sabemos de Shiki em Siracusa?',nome='mizuki',estado={'nova_terra':ativa})
                fontes=p['input'][0]['content']+'\n'+p['input'][-1]['content'].split('[Mensagem]')[0]
                if ativa:
                    self.assertIn('Capo dei capi',fontes)
                    self.assertTrue(any(n.startswith('Era:') for n in p['ativadas']))
                else:
                    self.assertNotIn('Capo dei capi',fontes)
                    self.assertNotIn('Siracusano II',fontes)
                    self.assertNotIn('ID 459030926928904230',fontes)
                    self.assertNotIn('não tem facção, casa',fontes)
                    self.assertIn('Rhodes Island',fontes)
                    self.assertIn('Siracusa',fontes)
                    self.assertFalse(any(n.startswith(('Era:','Mundo:')) for n in p['ativadas']))
    def test_sem_opcao_explicita_e_original_e_conta_do_livro_permanece(self):
        p=self.ponte.montar('kal','Como funciona Integridade?')
        self.assertIn('Original: Arknights',p['ativadas'])
        self.assertTrue(any(n.startswith('Livro:') for n in p['ativadas']))
        self.assertNotIn('Mundo: premissa',p['ativadas'])
    def test_paridade_node_quickjs_nos_dois_mundos(self):
        if not {'node','quickjs'} <= set(self.ponte.motores()):self.skipTest('precisa dos dois motores')
        for persona in ('kal','clo'):
            for ativo in (False,True):
                kw=dict(estado={'nova_terra':ativo,'idioma':'en'},hora=(22,0))
                self.assertEqual(self.ponte.montar(persona,'Quem lidera Siracusa?',motor='node',**kw),self.ponte.montar(persona,'Quem lidera Siracusa?',motor='quickjs',**kw))

class GuiasEmIngles(unittest.IsolatedAsyncioTestCase):
    async def test_todas_as_paginas_e_controles_sem_traduzir_identificadores(self):
        from closure_bot import guias
        from closure_bot.idiomas import usar
        from closure_bot.cogs.guias import GuiaNavegavel
        paginas=guias._ingles()['pages']
        esperadas={f'{t}.{i}' for t,(_,p) in guias.ASSUNTOS.items() for i in range(1,len(p)+1)}
        self.assertEqual(set(paginas),esperadas)
        for tema,(_,p) in guias.ASSUNTOS.items():
            with usar('en'):
                view=GuiaNavegavel(tema)
                self.assertEqual(view.idioma,'en')
                self.assertEqual(view.primeira.label,'First')
                self.assertEqual(view.assuntos.placeholder,'Choose a topic')
                self.assertEqual(len(view.paginas),len(p))
                for pagina in view.paginas:
                    self.assertTrue(pagina.footer.text.startswith('Page '))
                    self.assertLessEqual(len(pagina.description),4096)
                    self.assertLessEqual(len(pagina),6000)
        self.assertIn('Emitida',guias.paginas('criar','en')[-1].description)
        self.assertIn('CARTEIRA',guias.paginas('criar','en')[-1].description)
        self.assertIn('¥150,000',guias.paginas('criar','en')[10].description)
        self.assertIn('9 points',guias.paginas('criar','en')[2].description)
    async def test_contextos_de_idioma_concorrentes_nao_vazam(self):
        import asyncio
        from closure_bot.idiomas import usar,tr,atual
        async def resposta(idioma):
            with usar(idioma):
                await asyncio.sleep(0)
                return tr('Primeira')
        self.assertEqual(await asyncio.gather(resposta('en'),resposta('pt-BR')),['First','Primeira'])
        self.assertEqual(atual(),'pt-BR')


class AjudaSemCanalDaHospedagem(unittest.IsolatedAsyncioTestCase):
    async def test_configuracao_global_nao_vaza_na_ajuda(self):
        from closure_bot.cogs.admin import Admin
        from closure_bot.plantao import KALTSIT,CLOSURE
        bot=NS(config=NS(canais={1361766042514489477},politica_url="",termos_url=""),
               personas={KALTSIT:NS(nome="Kal'tsit"),CLOSURE:NS(nome="Closure")},
               tree=NS(get_commands=lambda:[]),user=None)
        embed=Admin(bot).painel_de_ajuda(cuida_do_servidor=False,dono=False)
        texto=json.dumps(embed.to_dict(),ensure_ascii=False)
        self.assertNotIn('<#',texto)
        self.assertNotIn('1361766042514489477',texto)
        self.assertIn('Nos canais onde o bot atende',texto)
        self.assertIn('mencione o bot diretamente',texto)
