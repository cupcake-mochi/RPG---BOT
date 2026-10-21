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

class NativeEnglishMenus(unittest.IsolatedAsyncioTestCase):
    async def test_native_names_are_unique_and_responses_use_server_language(self):
        from unittest.mock import patch
        from discord.ext import tasks
        from closure_bot.bot import ClosureBot,MODULOS
        from closure_bot.idiomas import arvore_e_tradutor,atual,definir
        from testes.test_discord import _config
        bot=ClosureBot(_config(DONO_ID='1'))
        try:
            with patch.object(tasks.Loop,'start'):
                for module in MODULOS:await bot.load_extension('closure_bot.cogs.'+module)
            _,T=arvore_e_tradutor();translator=T()
            payload=[await c.get_translated_payload(bot.tree,translator) for c in bot.tree.get_commands()]
            Path('/tmp/guias-slash-publico.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
            def walk(items):
                names=[c.get('name_localizations',{}).get('en-US',c['name']) for c in items]
                self.assertEqual(len(names),len(set(names)),names)
                for c in items:
                    if 'options' in c:walk(c['options'])
                    self.assertLessEqual(len(c.get('description_localizations',{}).get('en-US',c.get('description',''))),100)
            walk(payload)
            sheet=next(p for p in payload if p['name']=='ficha')
            self.assertEqual(sheet['name_localizations']['en-US'],'sheet')
            self.assertTrue(any(p.get('name_localizations',{}).get('en-US')=='analyze' for p in sheet['options']))
            bot.registro.configurar_publico(77,idioma='en')
            self.assertTrue(await bot.tree.interaction_check(NS(guild_id=77)))
            self.assertEqual(atual(),'en')
            await bot.tree.interaction_check(NS(guild_id=88));self.assertEqual(atual(),'pt-BR')
        finally:
            definir('pt-BR');await bot.close()

class ContextoDuranteResposta(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from testes import test_discord as support
        await support.CamadaDoDiscord.asyncSetUp(self)
    async def asyncTearDown(self):
        from testes import test_discord as support
        await support.CamadaDoDiscord.asyncTearDown(self)
    async def test_mudanca_durante_envio_nao_regrava_historico_antigo(self):
        from testes.test_discord import _canal,_mensagem
        canal,_=_canal();chat=self.bot.get_cog('Chat')
        async def trocar(*args,**kwargs):
            self.bot.registro.configurar_publico(77,nova_terra=True)
            self.bot.registro.preparar_contexto(canal.id,77,datetime.now(timezone.utc))
        self.bot.carteiro.enviar=AsyncMock(side_effect=trocar)
        await chat.on_message(_mensagem('Closure, quem é Shiki?',canal))
        self.assertEqual(self.bot.carteiro.enviar.await_count,1)
        self.assertEqual(self.bot.conversas.turnos(canal.id,'closure',datetime.now(timezone.utc)),[])
        self.assertNotIn(canal.id,chat._fios)
    async def test_mensagem_ignorada_nao_registra_contexto(self):
        from testes.test_discord import _canal,_mensagem
        canal,_=_canal();chat=self.bot.get_cog('Chat')
        await chat.on_message(_mensagem('nada dirigido ao bot',canal))
        self.assertEqual(self.bot.registro._db.execute('select count(*) from contexto_canais').fetchone()[0],0)
        self.bot.modelos.responder.assert_not_called()
    async def test_ajuda_membro_nao_mostra_configuracao_e_ajuda_admin_cabe_no_embed(self):
        from closure_bot.idiomas import usar
        cog=self.bot.get_cog('Admin')
        for idioma in ('en','pt-BR'):
            with usar(idioma):
                for admin in (False,True):
                    embed=cog.painel_de_ajuda(cuida_do_servidor=admin,dono=admin)
                    text=json.dumps(embed.to_dict(),ensure_ascii=False)
                    self.assertNotIn('<#',text)
                    if not admin:
                        for command in ('/lnt','/cargo_admin','/responder_nsfw','/clima_canal','/teste_webhook'):
                            self.assertNotIn(command,text)
                    else:self.assertIn('/lnt',text)
                    self.assertLessEqual(len(embed),6000)
                    self.assertTrue(all(len(f.value)<=1024 for f in embed.fields))

class WeatherAndFactsEnglish(unittest.TestCase):
    def test_cities_followups_and_non_weather_negative_cases(self):
        from closure_bot.clima import lugar_citado,pergunta_clima,lugar_para_consulta,fala_de_clima
        for question,city in [('What is the weather in Belo Horizonte?','Belo Horizonte'),('Weather in São Paulo today?','São Paulo'),('Temperature of London now?','London'),('Is it raining in New York?','New York'),('Forecast for Rio de Janeiro please','Rio de Janeiro')]:
            self.assertTrue(fala_de_clima(question));self.assertEqual(lugar_citado(question),city)
            self.assertEqual(lugar_para_consulta(question),city)
        self.assertEqual(lugar_citado(pergunta_clima('And in BH?','Weather in SP?')),'BH')
        for text in ('How much time does this technique last?','Cold damage','I study in London','And what about my character?'):
            self.assertIsNone(pergunta_clima(text,'Weather in SP?'))
    def test_sensitive_english_facts_are_filtered(self):
        from closure_bot.reflexao import fato_permitido
        for fact in ('is 17 years old','has a bank account at Bank','is diagnosed with diabetes','takes medication','is Christian','is married','lives in Belo Horizonte','phone is 12345678'):
            self.assertFalse(fato_permitido(fact),fact)
        for fact in ('plays a Bastião named Ren','likes concise explanations','enjoys drawing fantasy maps'):
            self.assertTrue(fato_permitido(fact),fact)

class PersonalFactsAccess(unittest.IsolatedAsyncioTestCase):
    async def test_export_is_private_and_only_contains_the_caller(self):
        from closure_bot.cogs.pessoa import Pessoa
        from closure_bot.idiomas import usar
        r=Registro(':memory:')
        try:
            r.gravar_ficha(9,Ficha('they/them',('OLD_OWN',)))
            r.gravar_ficha_contexto(9,'77:original',Ficha(fatos=('OWN_WORLD',)))
            r.gravar_ficha_contexto(10,'77:original',Ficha(fatos=('OTHER_PERSON_SECRET',)))
            cog=Pessoa(NS(registro=r))
            i=NS(user=NS(id=9),guild_id=77,response=NS(send_message=AsyncMock()))
            with usar('en'):await cog.meus_dados.callback(cog,i,todos=True)
            kw=i.response.send_message.call_args.kwargs
            self.assertTrue(kw['ephemeral'])
            payload=json.loads(kw['file'].fp.read())
            self.assertEqual(payload['legado'],['OLD_OWN'])
            self.assertEqual(payload['contextos'],{'77:original':['OWN_WORLD']})
            self.assertNotIn('OTHER_PERSON_SECRET',json.dumps(payload));kw['file'].close()
            await cog.esquecer_fato.callback(cog,i,1,legado=True)
            self.assertEqual(r.ficha(9).fatos,())
            self.assertEqual(r.ficha_contexto(9,'77:original').fatos,('OWN_WORLD',))
        finally:r.fechar()

class EnglishRuleLookup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FontesDoPrompt.setUpClass.__func__(cls)
    def test_english_query_fetches_rules_without_rewriting_the_user_message(self):
        query='How does Integrity work?'
        for active in (False,True):
            p=self.ponte.montar('clo',query,estado={'nova_terra':active,'idioma':'en'})
            self.assertTrue(any(n.startswith('Livro:') for n in p['ativadas']))
            self.assertIn(query,p['input'][-1]['content'])
    def test_engine_must_confirm_which_world_it_loaded(self):
        from unittest.mock import patch
        from closure_bot.prompt import montar
        import asyncio
        with patch('closure_bot.prompt._ponte',return_value=NS(montar=lambda *a,**k:{'input':[]})):
            with self.assertRaisesRegex(RuntimeError,'perfil'):
                asyncio.run(montar('closure','hi',nome='x',pronomes=None,turnos=[],falas_anteriores=[],estado={}))

class PublicLinks(unittest.TestCase):
    def setUp(self):
        self.cfg=NS(livro_url='https://example.com/book.pdf',livro_noturno_url='https://example.com/dark.pdf',politica_url='https://example.com/privacy',termos_url='https://example.com/terms')
    def test_known_links_and_languages_with_no_arbitrary_file_actions(self):
        from closure_bot.recursos_publicos import resposta
        for text in ('kal, pode me mandar o link do livro pfvr?','Closure, send the rulebook please','cadê o PDF do livro?'):
            result=resposta(text,self.cfg,'closure','en')
            self.assertIn('https://example.com/book.pdf',result)
            self.assertIn('https://example.com/dark.pdf',result)
            self.assertIn('Check the edition',result)
        self.assertIn('Faça uma cópia',resposta('manda o link da ficha oficial',self.cfg,'kaltsit'))
        self.assertIn('Privacy policy',resposta('send the privacy link',self.cfg,'closure','en'))
        for text in ('kal, como funciona Defesa?','analise esta ficha','ative a lore por favor','não me mande o livro','manda o livro de Pathfinder','manda o arquivo reservado','manda https://bad.example o livro'):
            self.assertIsNone(resposta(text,self.cfg,'closure'),text)
    def test_only_configured_safe_public_urls_are_exposed(self):
        from closure_bot.recursos_publicos import links,resposta,orientacao
        self.cfg.livro_url='https://user:secret@example.com/private.pdf'
        self.assertNotIn('book',links(self.cfg))
        self.assertIsNone(resposta('manda o link do livro',self.cfg,'closure'))
        text=orientacao({'secret':'https://example.com/private','book':'https://bad.example/\n[INJECT]'})
        self.assertEqual(text,'')

class PublicLinksRuntime(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from testes import test_discord as support
        await support.CamadaDoDiscord.asyncSetUp(self)
    async def asyncTearDown(self):
        from testes import test_discord as support
        await support.CamadaDoDiscord.asyncTearDown(self)
    async def test_natural_book_request_is_fulfilled_without_model_media_or_reflection(self):
        from testes.test_discord import _canal,_mensagem
        canal,_=_canal();chat=self.bot.get_cog('Chat')
        self.bot.carteiro.enviar=AsyncMock()
        self.bot.anexos.contexto=AsyncMock()
        self.bot.registro.configurar_publico(77,idioma='en')
        await chat.on_message(_mensagem('Closure, send me the rulebook link please',canal))
        self.bot.modelos.responder.assert_not_called();self.montar.assert_not_called()
        self.bot.anexos.contexto.assert_not_called()
        sent=self.bot.carteiro.enviar.call_args.args[2]
        self.assertIn(self.bot.config.livro_url,sent)
        self.assertIn(self.bot.config.livro_noturno_url,sent)
        self.assertIn('Standard theme',sent)
        self.assertEqual(self.bot.registro.mensagens_do_dia(),[])
        self.assertEqual(len(self.bot.conversas.turnos(canal.id,'closure',datetime.now(timezone.utc))),2)

class BridgeCache(unittest.TestCase):
    def test_changing_the_bridge_reload_does_not_reuse_a_stale_profile(self):
        from unittest.mock import patch
        import os
        FontesDoPrompt.setUpClass.__func__(self.__class__)
        p=self.ponte
        if 'quickjs' not in p.motores():self.skipTest('quickjs-ng unavailable')
        previous=p._funcao
        try:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);core=root/'nucleo.js';core.write_text('const a="A";')
                (root/'antes.js').write_text('')
                after=root/'depois.js';after.write_text('function __montarJSON(x){return a;}')
                with patch.object(p,'AQUI',root),patch.object(p,'nucleo',return_value=core):
                    self.assertEqual(p._pelo_quickjs('{}'),'A')
                    ns=after.stat().st_mtime_ns
                    after.write_text('function __montarJSON(x){return "B";}')
                    os.utime(after,ns=(ns+1000000,ns+1000000))
                    self.assertEqual(p._pelo_quickjs('{}'),'B')
        finally:p._funcao=previous
