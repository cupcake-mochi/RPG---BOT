import copy
from dataclasses import asdict
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock,patch,PropertyMock
import discord
from carteira_viva.cliente_discord import ClienteCarteira,FalhaCarteira
from carteira_viva.ponte_discord import ConectarFicha
from carteira_viva.discord_ui import GaleriaView,ConsultaView,PreviaView,cartao_embed,paginas_privadas,txt

PID='a'*32;P2='b'*32


def card(pid=PID):
    return {'id':pid,'responsavel':'222','perfil':{'nome':'Personagem QA','titulo':'Título','frase':'Uma frase','cor':0x397B77,'origem':'Latente'},'lido_em':180000.,'precisa_atualizar':False,'capacidades':{'ver_detalhes':True,'analisar':True,'personalizar':True,'trocar_arquivo':True}}


def interacao(uid=222,gid=111):
    return SimpleNamespace(guild_id=gid,user=SimpleNamespace(id=uid),locale='pt-BR',response=SimpleNamespace(defer=AsyncMock(),send_message=AsyncMock(),send_modal=AsyncMock()),followup=SimpleNamespace(send=AsyncMock()),edit_original_response=AsyncMock())


class DiscordUITeste(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.bot=SimpleNamespace(registro=SimpleNamespace(opcoes_servidor=lambda g:SimpleNamespace(idioma='pt-BR')))
        self.cog=ConectarFicha(self.bot,'https://carteira.example','ficticio_'*5);self.api=SimpleNamespace(pedir=AsyncMock());self.cog.api=self.api;self.i=interacao()
    def dados(self):return {'cartoes':[card(),card(P2)],'proximo':None}
    def botao(self,v,n):return next(x for x in v.children if isinstance(x,discord.ui.Button) and x.label==n)
    async def test_publico_usa_fonte_apresentacao_sem_link_google(self):
        c=card();c['perfil']|={'nome':'@everyone **Teste** <@999>','frase':'[clique](https://example.invalid)'}
        e=cartao_embed(c,'pt-BR');s=json.dumps(e.to_dict())
        self.assertNotIn('@everyone',s);self.assertNotIn('<@999>',s);self.assertIsNone(e.url);self.assertNotIn('docs.google',s)
    async def test_titulo_do_cartao_abre_carteira_sem_link_google(self):
        v=GaleriaView(self.cog,111,222,222,self.dados())
        kw=await v.conteudo();e=kw['embeds'][0]
        self.assertEqual(e.url,'https://carteira.example/carteira/111/'+v.card['id'])
        self.assertNotIn('docs.google',json.dumps(e.to_dict()))
    async def test_mensagens_e_labels_en_sem_mudar_conteudo_do_jogador(self):
        e=cartao_embed(card(),'en');self.assertIn('Player',[f.name for f in e.fields]);self.assertEqual(e.title,'Personagem QA')
        self.assertIn('No current',txt('nenhuma','en'))
    async def test_controles_de_outro_usuario_e_dm_recusados(self):
        v=GaleriaView(self.cog,111,222,222,self.dados())
        self.assertFalse(await v.interaction_check(interacao(uid=999)));self.assertFalse(await v.interaction_check(interacao(gid=None)))
        self.api.pedir.assert_not_called()
    async def test_galeria_vazia_legivel(self):
        v=GaleriaView(self.cog,111,222,222,{'cartoes':[],'proximo':None});kw=await v.conteudo()
        self.assertIn('Nenhum personagem',kw['content']);self.assertFalse(kw['embeds'])
        self.assertTrue(all(x.disabled for x in v.children))
    def mensagem(self):
        m=SimpleNamespace();m.edit=AsyncMock(return_value=m);return m
    async def test_primeiro_nome_no_menu_acompanha_leitura_nova(self):
        antigo=card();antigo['perfil']['nome']='Nome anterior'
        novo=card();novo['perfil']['nome']='Nome atual'
        rotulos=[]
        async def enviar(**kw):
            rotulos.append(kw['view'].children[0].options[0].label);return self.mensagem()
        self.i.followup.send.side_effect=enviar
        self.api.pedir.side_effect=[{'cartoes':[antigo],'proximo':None},novo]
        await self.cog.abrir_galeria(self.i)
        self.assertEqual(rotulos,['Nome anterior'])  # aparece logo, com a última leitura salva
        view=self.i.followup.send.call_args.kwargs['view']
        view.mensagem.edit.assert_awaited_once()
        self.assertEqual(view.children[0].options[0].label,'Nome atual')
        self.assertEqual(self.api.pedir.await_args_list[1].args[2:],('cartao',))
    async def test_releitura_nao_passa_por_cima_de_quem_trocou_de_cartao(self):
        self.i.followup.send.return_value=self.mensagem()
        async def pedir(s,u,acao,**kw):
            if acao=='listar':return self.dados()
            view=self.i.followup.send.call_args.kwargs['view'];view.card=view.dados['cartoes'][1]  # clicou no outro
            return card()
        self.api.pedir.side_effect=pedir
        await self.cog.abrir_galeria(self.i)
        view=self.i.followup.send.call_args.kwargs['view']
        view.mensagem.edit.assert_not_awaited();self.assertEqual(view.card['id'],P2)
    async def test_releitura_que_falha_deixa_o_cartao_salvo_sem_erro(self):
        self.i.followup.send.return_value=self.mensagem()
        self.api.pedir.side_effect=[self.dados(),FalhaCarteira('leitura')]
        await self.cog.abrir_galeria(self.i)
        self.i.followup.send.assert_awaited_once()  # nenhuma mensagem de erro extra
        self.i.followup.send.call_args.kwargs['view'].mensagem.edit.assert_not_awaited()
    async def test_ver_mostra_salvo_e_depois_a_releitura(self):
        novo=card();novo['perfil']['nome']='Nome atual'
        self.i.followup.send.return_value=self.mensagem()
        self.api.pedir.side_effect=[card(),novo]
        await self.cog.ver_cartao(self.i,PID)
        self.assertEqual([c.args[2] for c in self.api.pedir.await_args_list],['cartao_salvo','cartao'])
        view=self.i.followup.send.call_args.kwargs['view']
        view.mensagem.edit.assert_awaited_once();self.assertEqual(view.card['perfil']['nome'],'Nome atual')
    async def test_galeria_alheia_nao_rele_ficha(self):
        alheio=card();alheio['capacidades']={'ver_detalhes':False}
        self.i.followup.send.return_value=self.mensagem()
        self.api.pedir.side_effect=[{'cartoes':[alheio],'proximo':None}]
        await self.cog.abrir_galeria(self.i)
        self.assertEqual(self.api.pedir.await_count,1)
    async def test_autocomplete_so_nomes_proprios_e_sem_rede_com_nomes_frescos(self):
        self.cog.lembrar_nomes(111,222,999,self.dados())  # galeria de outro jogador não entra
        self.assertNotIn((str(111),str(222)),self.cog.nomes)
        self.cog.lembrar_nomes(111,222,222,self.dados())
        self.assertEqual(len(await self.cog.completar(self.i,'QA')),2)
        self.api.pedir.assert_not_called()
    async def test_autocomplete_sem_personagens_busca_a_propria_lista(self):
        self.api.pedir.return_value=self.dados()
        opcoes=await self.cog.completar(self.i,'')
        self.assertEqual([o.value for o in opcoes],[PID,P2])
        self.api.pedir.assert_awaited_once_with(111,222,'listar')
        await self.cog.completar(self.i,'QA')
        self.api.pedir.assert_awaited_once()  # a segunda tecla usa o que já veio
    async def test_autocomplete_lento_responde_vazio_e_a_proxima_tecla_acha(self):
        import asyncio
        from carteira_viva import ponte_discord
        liberar=asyncio.Event()
        async def lento(*a,**k):
            await liberar.wait();return self.dados()
        self.api.pedir.side_effect=lento
        with patch.object(ponte_discord,'NOMES_PRAZO',0.01):
            self.assertEqual(await self.cog.completar(self.i,''),[])
            liberar.set();await asyncio.sleep(0)
            await asyncio.sleep(0)
            self.assertEqual(len(await self.cog.completar(self.i,'')),2)
        self.assertEqual(self.api.pedir.await_count,1)
    async def test_autocomplete_falha_do_site_nao_quebra(self):
        self.api.pedir.side_effect=FalhaCarteira('temporario')
        self.assertEqual(await self.cog.completar(self.i,''),[])
        self.assertEqual(await self.cog.completar(interacao(gid=None),''),[])
    async def test_autocomplete_expira_e_cache_tem_teto(self):
        import time
        self.cog.lembrar_nomes(111,222,222,self.dados())
        self.api.pedir.side_effect=FalhaCarteira('temporario')
        with patch('carteira_viva.ponte_discord.time.monotonic',return_value=time.monotonic()+601):
            self.assertEqual(await self.cog.completar(self.i,''),[])
        for n in range(200):self.cog.lembrar_nomes(111,n,n,self.dados())
        self.assertEqual(len(self.cog.nomes),128)
    async def test_autocomplete_rebusca_quando_nada_bate_depois_de_30s(self):
        import time
        self.cog.lembrar_nomes(111,222,222,self.dados())
        novo=card('c'*32);novo['perfil']['nome']='Recém cadastrado'
        self.api.pedir.return_value={'cartoes':[card(),card(P2),novo],'proximo':None}
        with patch('carteira_viva.ponte_discord.time.monotonic',return_value=time.monotonic()+31):
            self.assertEqual([o.value for o in await self.cog.completar(self.i,'Recém')],['c'*32])
    async def test_privado_nunca_edita_resposta_publica(self):
        self.api.pedir.return_value={'cartao':card(),'arquivo':'arquivo_ficticio_para_teste_001','revisao':1,'leitura':{'campos':{'ficha':{}},'lido_em':180000.},'analise':None}
        await self.cog.consulta_privada(self.i,PID,'detalhes')
        self.assertTrue(self.i.followup.send.call_args.kwargs['ephemeral']);self.i.edit_original_response.assert_not_called()
    async def test_permissao_removida_limpa_pagina_privada(self):
        v=ConsultaView(self.cog,111,222,PID,analise=False)
        d={'cartao':card(),'arquivo':'arquivo_ficticio_para_teste_001','leitura':{'campos':{'ficha':{}}}}
        await v.montar(d);self.api.pedir.side_effect=FalhaCarteira('acesso')
        await self.botao(v,'Próxima').callback(self.i)
        call=self.i.edit_original_response.call_args
        self.assertEqual(call.kwargs['embeds'],[]);self.assertIsNone(call.kwargs['view'])
        self.assertNotIn('arquivo_ficticio',call.kwargs['content'])
    async def test_paginar_reconsulta_lista_sem_usar_analise(self):
        d=self.dados();d['proximo']=P2;v=GaleriaView(self.cog,111,222,222,d)
        self.api.pedir.return_value={'cartoes':[card(P2)],'proximo':None}
        await self.botao(v,'Próxima').callback(self.i)
        self.assertEqual(v.pagina,1);self.assertEqual(v.card['id'],P2)
        self.assertTrue(all(c.args[2]=='listar' for c in self.api.pedir.call_args_list))
    async def test_selecionar_atualiza_uma_ficha_e_revalida_projecao(self):
        v=GaleriaView(self.cog,111,222,222,self.dados())
        self.api.pedir.side_effect=[card(P2),self.dados()]
        with patch.object(discord.ui.Select,'values',new_callable=PropertyMock,return_value=[P2]):await v.children[0].callback(self.i)
        self.assertEqual(self.api.pedir.call_args_list[0].args[2],'cartao');self.assertEqual(v.card['id'],P2)
    async def test_peer_so_ve_cartao_sem_botoes_privados(self):
        c=card();c['capacidades']={k:False for k in c['capacidades']}
        v=GaleriaView(self.cog,111,999,222,{'cartoes':[c],'proximo':None})
        labels=[getattr(x,'label','') for x in v.children]
        self.assertNotIn('Analisar · privado',labels);self.assertNotIn('Editar cartão',labels)
    async def test_previa_salvar_confere_no_servico_e_nao_publica_arquivo(self):
        v=PreviaView(self.cog,111,222,PID,{'previa':'p'*32,'cartao':card()})
        self.api.pedir.return_value=card()
        await self.botao(v,'Salvar cartão').callback(self.i)
        self.assertEqual(self.api.pedir.call_args.args[2],'confirmar');self.assertEqual(self.i.edit_original_response.call_args.kwargs['embeds'],[])
    async def test_timeout_desabilita_controles(self):
        v=GaleriaView(self.cog,111,222,222,self.dados());v.mensagem=SimpleNamespace(edit=AsyncMock())
        await v.on_timeout();self.assertTrue(all(x.disabled for x in v.children));v.mensagem.edit.assert_awaited_once()
    async def test_upload_grande_nao_e_baixado(self):
        a=SimpleNamespace(size=1024*1024+1,read=AsyncMock())
        await self.cog.enviar_imagem(self.i,PID,a);a.read.assert_not_called();self.api.pedir.assert_not_called()
        self.assertTrue(self.i.response.defer.call_args.kwargs['ephemeral'])
    async def test_comandos_pt_en_e_limites_discord(self):
        roots={c.name:c for c in self.cog.__cog_app_commands__}
        self.assertEqual(set(roots),{'personagem','character','personagens','characters'})
        for grupo in ('personagem','character'):
            self.assertEqual(len(roots[grupo].commands),12)
            novos={'modelos','modelo_configurar','excluir','apagar_meus_dados'} if grupo=='personagem' else {'templates','set_template','delete','delete_my_data'}
            self.assertTrue(novos <= {c.name for c in roots[grupo].commands})
            for c in roots[grupo].commands:self.assertLessEqual(len(c.name),32);self.assertLessEqual(len(c.description),100)
    async def test_analise_pt_en_reaproveita_json_e_limites_de_pagina(self):
        from testes.test_carteira_consultas import completa_r53
        from testes.test_b47_integracao import REF
        from testes.test_r53 import gravar
        from closure_bot.ficha_corretor import conferir
        f=completa_r53();gravar(f,'feitico.1',1,nome='Nome com _ e @everyone')
        b={'cartao':card(),'arquivo':'arquivo_ficticio_para_teste_001','leitura':{'campos':{'ficha':{k:asdict(c) for k,c in f.items()}},'lido_em':180000.},'analise':{'resultado':asdict(conferir(f,REF)),'origem':{'lido_em':180000.,'revisao':1},'campanha':{'nome':'Campanha QA'}}}
        for lang in ('pt-BR','en'):
            ps=paginas_privadas(b,lang,True)
            self.assertTrue(ps)
            for p in ps:
                self.assertLessEqual(len(p),6000);self.assertLessEqual(len(p.fields),25);self.assertNotIn('@everyone',json.dumps(p.to_dict()))
                for campo in p.fields:self.assertLessEqual(len(campo.value),1024)


class ClienteTeste(unittest.IsolatedAsyncioTestCase):
    async def resposta(self,body,status=200,content_type='application/json'):
        async def chunks(n):yield body
        resp=SimpleNamespace(status=status,content_type=content_type,content=SimpleNamespace(iter_chunked=chunks))
        cm=AsyncMock();cm.__aenter__.return_value=resp
        client=SimpleNamespace(post=lambda *a,**kw:cm);sessao=AsyncMock();sessao.__aenter__.return_value=client
        return patch('carteira_viva.cliente_discord.aiohttp.ClientSession',return_value=sessao)
    async def test_nao_segue_redirect_e_nao_expoe_erro_arbitrario(self):
        c=ClienteCarteira('https://carteira.example','ficticio_'*5)
        for status,body in ((302,b'link segredo'),(400,b'{"erro":"segredo_privado"}')):
            with await self.resposta(body,status),self.assertRaises(FalhaCarteira) as erro:await c.pedir('111','222','listar')
            self.assertNotIn('segredo',erro.exception.codigo)
    async def test_recusa_id_e_metodo_arbitrarios_sem_rede(self):
        c=ClienteCarteira('https://carteira.example','ficticio_'*5)
        for acao,pid in (('apagar_usuario',None),('detalhes','../../interno'),('listar',PID)):
            with self.assertRaises(FalhaCarteira):await c.pedir('111','222',acao,personagem=pid)
    async def test_le_resposta_valida_e_whitelist_de_erro(self):
        c=ClienteCarteira('https://carteira.example','ficticio_'*5)
        with await self.resposta(b'{"cartoes":[],"proximo":null}'):
            self.assertEqual((await c.pedir('111','222','listar'))['cartoes'],[])
        with await self.resposta(b'{"erro":"imagem"}',400),self.assertRaises(FalhaCarteira) as erro:await c.pedir('111','222','listar')
        self.assertEqual(erro.exception.codigo,'imagem')
    async def test_http_apenas_piloto_loopback(self):
        with self.assertRaises(ValueError):ClienteCarteira('http://127.0.0.1:8876','ficticio_'*5)
        ClienteCarteira('http://127.0.0.1:8876','ficticio_'*5,desenvolvimento=True)
        with self.assertRaises(ValueError):ClienteCarteira('http://site.example','ficticio_'*5,desenvolvimento=True)
