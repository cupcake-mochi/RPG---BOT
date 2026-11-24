"""Extensão opcional: carrega apenas depois de configurar o serviço.

As Guias carregam esta extensão só quando CARTEIRA_API_URL e
CARTEIRA_SERVICE_TOKEN estão configurados. Usa só aiohttp/discord.py; as
bibliotecas OAuth ficam no serviço separado.
"""
import asyncio
import os
import secrets
import time
from collections import OrderedDict
from urllib.parse import urlsplit

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from .cliente_discord import ClienteCarteira, FalhaCarteira, origem_valida
from .discord_ui import GaleriaView, ConsultaView, PreviaView, AbrirEditor, txt, erro, seguro

NOMES_VALIDADE = 600  # segundos que os nomes do autocompletar valem
NOMES_PRAZO = 2.5  # o Discord espera 3 s pela resposta do autocompletar


class Confirmar(discord.ui.View):
    """Botão só de quem pediu; expira em dois minutos sem apagar nada."""
    def __init__(self,usuario,lang,rotulo,acao):
        super().__init__(timeout=120)
        self.usuario,self.lang,self.acao=usuario,lang,acao
        sim=discord.ui.Button(label=rotulo,style=discord.ButtonStyle.danger)
        nao=discord.ui.Button(label=txt('cancelar_botao',lang),style=discord.ButtonStyle.secondary)
        sim.callback,nao.callback=self.confirmar,self.cancelar
        self.add_item(sim);self.add_item(nao)

    async def interaction_check(self,i):
        return i.user.id==self.usuario

    async def confirmar(self,i):
        self.stop()
        await i.response.edit_message(view=None)
        try:await i.followup.send(await self.acao(),ephemeral=True)
        except FalhaCarteira as exc:await i.followup.send(erro(exc,self.lang),ephemeral=True)

    async def cancelar(self,i):
        self.stop()
        await i.response.edit_message(content=txt('cancelado',self.lang),view=None)


class ConectarFicha(commands.Cog):
    grupo = app_commands.Group(name="personagem", description="Conecte a ficha do seu personagem")

    grupo_en = app_commands.Group(name="character", description="Connect and manage your characters")

    def __init__(self, bot, origem, token, *, desenvolvimento=False):
        self.bot, self.origem, self.token = bot, origem.rstrip("/"), token
        origem_valida(self.origem, desenvolvimento)
        self.api = ClienteCarteira(origem, token, desenvolvimento=desenvolvimento)
        self.nomes = OrderedDict()
        self.buscas = {}

    async def iniciar(self, interacao, acao, personagem=None):
        en = self.idioma(interacao) == "en"
        def texto(pt, ingles):
            return ingles if en else pt
        if not interacao.guild_id:
            await interacao.response.send_message(texto("Use este comando no servidor do personagem.", "Use this command in the character’s server."), ephemeral=True)
            return
        await interacao.response.defer(ephemeral=True, thinking=True)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as client:
                async with client.post(self.origem + "/interno/conexoes", allow_redirects=False,
                                       headers={"Authorization": "Bearer " + self.token},
                                       json={"servidor": str(interacao.guild_id), "usuario": str(interacao.user.id),
                                             "acao": acao, "personagem": personagem}) as resp:
                    if resp.status != 200:
                        if acao == "criar" and resp.status == 400 and (await resp.json()).get("erro") == "modelo_bloqueado":
                            await interacao.followup.send(texto("A criação pelo bot ainda não está liberada aqui. Faça sua cópia pelo `GC:guia criar` e cadastre com `/personagem cadastrar`.",
                                                                "Creation by the bot is not enabled here yet. Make your copy with `GC:guia criar` and register it with `/character register`."), ephemeral=True)
                            return
                        raise ValueError("Serviço indisponível")
                    data = await resp.json()
            url = data["url"]
            u = urlsplit(url)
            if (u.scheme, u.netloc) != (urlsplit(self.origem).scheme, urlsplit(self.origem).netloc) or u.path != "/conectar":
                raise ValueError("Destino de conexão inválido")
            view = discord.ui.View(timeout=600)
            view.add_item(discord.ui.Button(label=texto("Escolher modelo", "Choose template") if acao == "modelo" else texto("Criar minha ficha", "Create my sheet") if acao == "criar" else texto("Conectar minha ficha", "Connect my sheet"), url=url))
            if acao == "modelo":
                await interacao.followup.send(texto("Abra com a mesma conta Discord de administrador. Salvar o modelo não libera a criação automática. O link vale dez minutos.",
                                                    "Open with the same administrator Discord account. Saving the template does not enable automatic creation. The link lasts ten minutes."), ephemeral=True, view=view)
                return
            if acao == "criar":
                await interacao.followup.send(texto("O bot copia a ficha oficial **Ciclo Maldito**, vazia, pra sua conta Google e já cadastra o personagem. Abra com a mesma conta Discord; o link vale dez minutos.\nJá tem ficha? Use `/personagem cadastrar`.",
                                                    "The bot copies the empty official **Ciclo Maldito** sheet to your Google account and registers the character. Open with the same Discord account; the link lasts ten minutes.\nAlready have a sheet? Use `/character register`."), ephemeral=True, view=view)
                return
            if acao == "cadastro" and data.get("criar") is True:
                criar = discord.ui.Button(label=texto("Criar minha ficha", "Create my sheet"), style=discord.ButtonStyle.secondary)
                async def criar_ficha(i): await self.iniciar(i, "criar")
                criar.callback = criar_ficha
                view.add_item(criar)
            await interacao.followup.send(texto("Abra a conexão com a mesma conta Discord. O link vale por dez minutos e só você pode confirmar sua ficha.",
                                               "Open the connection with the same Discord account. The link lasts ten minutes and only you can confirm your sheet."),
                                          ephemeral=True, view=view)
        except (aiohttp.ClientError, TimeoutError, ValueError, KeyError):
            await interacao.followup.send(texto("Não consegui abrir a conexão agora. Confira o personagem ou tente novamente em instantes.",
                                               "Could not open the connection. Check the character or try again shortly."), ephemeral=True)

    async def completar(self,i,atual):
        if not i.guild_id:return []
        # Autocomplete não pode ser adiado no Discord (3 s). Usa só nomes dos
        # personagens do próprio jogador; abrir dados revalida no site.
        chave=(str(i.guild_id),str(i.user.id))
        item=self.nomes.get(chave)
        def opcoes(item):
            return [app_commands.Choice(name=seguro(nome,90),value=pid) for pid,nome in item[1] if atual.casefold() in nome.casefold()][:20]
        idade=time.monotonic()-item[0] if item else None
        # Sem nomes, nomes velhos ou nada batendo depois de 30 s (personagem
        # cadastrado agora): busca a lista no site, sem passar do prazo.
        if item is None or idade>NOMES_VALIDADE or (idade>30 and not opcoes(item)):
            item=await self.buscar_nomes(i.guild_id,i.user.id) or item
        if not item or time.monotonic()-item[0]>NOMES_VALIDADE:return []
        return opcoes(item)

    async def buscar_nomes(self,servidor,usuario):
        chave=(str(servidor),str(usuario))
        tarefa=self.buscas.get(chave)
        if tarefa is None or tarefa.done():
            async def carregar():
                try:self.lembrar_nomes(servidor,usuario,usuario,await self.api.pedir(servidor,usuario,'listar'))
                except (FalhaCarteira,KeyError,TypeError,AttributeError):pass
            tarefa=asyncio.ensure_future(carregar())
            self.buscas[chave]=tarefa
            tarefa.add_done_callback(lambda t:self.buscas.pop(chave,None) if self.buscas.get(chave) is t else None)
        try:await asyncio.wait_for(asyncio.shield(tarefa),NOMES_PRAZO)
        except asyncio.TimeoutError:return None  # a busca segue; a próxima tecla já acha os nomes
        return self.nomes.get(chave)

    def lembrar_nomes(self,servidor,usuario,dono,dados):
        if str(usuario)!=str(dono):return
        chave=(str(servidor),str(usuario))
        self.nomes[chave]=(time.monotonic(),[(c['id'],c['perfil'].get('nome','Personagem')) for c in dados['cartoes'][:20]])
        self.nomes.move_to_end(chave)
        while len(self.nomes)>128:self.nomes.popitem(last=False)

    @grupo.command(name="cadastrar", description="Conecte uma ficha que você já usa")
    async def cadastrar(self, interacao: discord.Interaction):
        await self.iniciar(interacao, "cadastro")

    @grupo.command(name="criar", description="Crie uma ficha vazia do Ciclo Maldito na sua conta Google")
    async def criar(self, interacao: discord.Interaction):
        await self.iniciar(interacao, "criar")

    @grupo.command(name="trocar_arquivo", description="Troque o arquivo sem perder o cadastro do personagem")
    @app_commands.autocomplete(personagem=completar)
    async def trocar(self, interacao: discord.Interaction, personagem: str):
        await self.iniciar(interacao, "troca", personagem)

    @grupo.command(name="reconectar", description="Restabeleça a conexão Google do personagem")
    @app_commands.autocomplete(personagem=completar)
    async def reconectar(self, interacao: discord.Interaction, personagem: str):
        await self.iniciar(interacao, "reconectar", personagem)


    def idioma_guild(self, servidor):
        if self.bot is not None and hasattr(self.bot, 'registro'):
            from closure_bot.idiomas import idioma_servidor
            return idioma_servidor(self.bot, int(servidor))
        return getattr(self, '_idioma_teste', 'pt-BR')

    def idioma(self, i):
        if self.bot is not None and hasattr(self.bot, 'registro'):
            return self.idioma_guild(i.guild_id)
        return 'en' if str(getattr(i,'locale','')).startswith('en') else 'pt-BR'

    async def contexto(self,i,*,privado=True):
        if not i.guild_id:
            await i.response.send_message(txt('sem_arquivo',self.idioma(i)),ephemeral=True)
            return False
        await i.response.defer(ephemeral=privado,thinking=True)
        return True

    async def abrir_galeria(self,i,jogador=None):
        if not await self.contexto(i,privado=False):return
        lang=self.idioma(i)
        try:
            dono=str(jogador.id if jogador else i.user.id)
            d=await self.api.pedir(i.guild_id,i.user.id,'listar',dono=dono)
            view=GaleriaView(self,i.guild_id,i.user.id,dono,d)
            self.lembrar_nomes(i.guild_id,i.user.id,dono,view.dados)
            # Mostra já o cartão salvo (a lista traz a última leitura) e só então
            # relê a ficha: a releitura no Google leva uns 10 s (medido 22/11/2026).
            kw=await view.conteudo();files=kw.pop('attachments')
            view.mensagem=await i.followup.send(**kw,files=files,view=view,wait=True,allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:
            await i.followup.send(erro(exc,lang),ephemeral=True);return
        await self.atualizar_primeiro(view)

    async def atualizar_primeiro(self,view):
        """Releitura do primeiro cartão depois de exibido; nunca passa por cima do jogador."""
        card=view.card
        if not card or not card.get('capacidades',{}).get('ver_detalhes'):return
        pid,pagina=card['id'],view.pagina
        try:novo=await self.api.pedir(view.servidor,view.usuario,'cartao',personagem=pid)
        except FalhaCarteira:return  # o cartão salvo já está na tela
        # Se o jogador trocou de cartão ou de página enquanto lia, a ação dele vale.
        if view.is_finished() or view.mensagem is None or view.pagina!=pagina or not view.card or view.card['id']!=pid:return
        view.card=novo
        view.dados['cartoes']=[novo if c['id']==pid else c for c in view.dados['cartoes']]
        view.montar()
        try:
            kw=await view.conteudo();files=kw.pop('attachments')
            view.mensagem=await view.mensagem.edit(**kw,attachments=files,view=view,allowed_mentions=discord.AllowedMentions.none())
        except (discord.HTTPException,FalhaCarteira):pass  # mensagem apagada ou sem permissão: fica a versão salva

    async def ver_cartao(self,i,personagem):
        if not await self.contexto(i,privado=False):return
        try:
            # Salvo primeiro, releitura depois (ver abrir_galeria).
            c=await self.api.pedir(i.guild_id,i.user.id,'cartao_salvo',personagem=personagem)
            view=GaleriaView(self,i.guild_id,i.user.id,c['responsavel'],{'cartoes':[c],'proximo':None},single=True)
            kw=await view.conteudo();files=kw.pop('attachments')
            view.mensagem=await i.followup.send(**kw,files=files,view=view,wait=True,allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:
            await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True);return
        await self.atualizar_primeiro(view)

    async def consulta_privada(self,i,personagem,acao):
        try:
            d=await self.api.pedir(i.guild_id,i.user.id,acao,personagem=personagem)
            view=ConsultaView(self,i.guild_id,i.user.id,personagem,analise=acao=='analisar')
            emb=await view.montar(d)
            view.mensagem=await i.followup.send(embed=emb,view=view,ephemeral=True,wait=True,allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True)

    async def editar_privado(self,i,personagem):
        try:
            d=await self.api.pedir(i.guild_id,i.user.id,'editar',personagem=personagem)
            view=AbrirEditor(self,i.guild_id,i.user.id,personagem,d)
            view.mensagem=await i.followup.send(txt('continuar_edicao',self.idioma(i))+' '+txt('limparfoto',self.idioma(i)),view=view,ephemeral=True,wait=True)
        except FalhaCarteira as exc:await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True)

    async def mostrar_previa(self,i,personagem,d):
        view=PreviaView(self,i.guild_id,i.user.id,personagem,d)
        e,files=await view.conteudo()
        view.mensagem=await i.followup.send(embed=e,files=files,view=view,ephemeral=True,wait=True,allowed_mentions=discord.AllowedMentions.none())

    async def enviar_imagem(self,i,personagem,arquivo):
        if not await self.contexto(i):return
        try:
            if not 0<arquivo.size<=1024*1024:raise FalhaCarteira('tamanho')
            b=await arquivo.read()
            d=await self.api.pedir(i.guild_id,i.user.id,'enviar_imagem',personagem=personagem,imagem=b)
            await self.mostrar_previa(i,personagem,d)
        except (discord.HTTPException,FalhaCarteira) as exc:await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True)

    async def pedir_exclusao(self,i,personagem):
        if not await self.contexto(i):return
        lang=self.idioma(i)
        try:
            c=await self.api.pedir(i.guild_id,i.user.id,'cartao_salvo',personagem=personagem)
            if str(c.get('responsavel'))!=str(i.user.id):raise FalhaCarteira('acesso')
            pedido=secrets.token_hex(16)
            async def acao():
                await self.api.pedir(i.guild_id,i.user.id,'excluir',personagem=personagem,pedido=pedido)
                self.nomes.pop((str(i.guild_id),str(i.user.id)),None)
                return txt('excluido',lang)
            nome=seguro(c.get('perfil',{}).get('nome') or 'Personagem',90)
            await i.followup.send(txt('excluir_pergunta',lang).format(nome=nome),ephemeral=True,
                                  view=Confirmar(i.user.id,lang,txt('excluir_botao',lang),acao),allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:await i.followup.send(erro(exc,lang),ephemeral=True)

    async def pedir_apagar_dados(self,i):
        if not await self.contexto(i):return
        lang=self.idioma(i)
        async def acao():
            await self.api.pedir(i.guild_id,i.user.id,'apagar_meus_dados')
            self.nomes.pop((str(i.guild_id),str(i.user.id)),None)
            return txt('apagado',lang)
        await i.followup.send(txt('apagar_pergunta',lang),ephemeral=True,view=Confirmar(i.user.id,lang,txt('apagar_botao',lang),acao))

    @grupo.command(name='excluir',description='Tire um personagem seu da Carteira; a planilha não muda')
    @app_commands.autocomplete(personagem=completar)
    async def excluir(self,i:discord.Interaction,personagem:str):await self.pedir_exclusao(i,personagem)

    @grupo.command(name='apagar_meus_dados',description='Apague todos os seus dados da Carteira, em todos os servidores')
    async def apagar_meus_dados(self,i:discord.Interaction):await self.pedir_apagar_dados(i)

    @grupo_en.command(name='delete',description='Remove one of your characters from the Wallet; the sheet is unchanged')
    @app_commands.autocomplete(character=completar)
    async def delete(self,i:discord.Interaction,character:str):await self.pedir_exclusao(i,character)

    @grupo_en.command(name='delete_my_data',description='Delete all your Wallet data in every server')
    async def delete_my_data(self,i:discord.Interaction):await self.pedir_apagar_dados(i)

    @app_commands.command(name='personagens',description='Veja seus personagens ou a galeria de outro jogador')
    async def personagens(self,i:discord.Interaction,jogador:discord.Member|None=None):
        await self.abrir_galeria(i,jogador)

    @app_commands.command(name='characters',description='Browse your characters or another player’s gallery')
    async def characters(self,i:discord.Interaction,player:discord.Member|None=None):
        await self.abrir_galeria(i,player)

    @grupo.command(name='ver',description='Abra o cartão básico de um personagem')
    @app_commands.autocomplete(personagem=completar)
    async def ver(self,i:discord.Interaction,personagem:str):await self.ver_cartao(i,personagem)

    @grupo.command(name='analisar',description='Confira a ficha em privado; cadastro não concede aprovação')
    @app_commands.autocomplete(personagem=completar)
    async def analisar(self,i:discord.Interaction,personagem:str):
        if await self.contexto(i):await self.consulta_privada(i,personagem,'analisar')

    @grupo.command(name='editar_cartao',description='Prepare e confirme a apresentação; não altera a planilha')
    @app_commands.autocomplete(personagem=completar)
    async def editar_cartao(self,i:discord.Interaction,personagem:str):
        if await self.contexto(i):await self.editar_privado(i,personagem)

    @grupo.command(name='imagem',description='Use PNG, JPEG ou WebP até 1 MiB; confirme a prévia para salvar')
    @app_commands.autocomplete(personagem=completar)
    async def imagem(self,i:discord.Interaction,personagem:str,arquivo:discord.Attachment):await self.enviar_imagem(i,personagem,arquivo)

    async def alterar_revisor(self,i,cargo,permitir):
        if not await self.contexto(i):return
        try:
            await self.api.pedir(i.guild_id,i.user.id,'cargo_revisor',cargo=str(cargo.id),permitir=permitir)
            await i.followup.send(txt('cargo',self.idioma(i)),ephemeral=True)
        except FalhaCarteira as exc:await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True)

    async def mostrar_modelos(self,i,escolha=None):
        if escolha == 'servidor':
            await self.iniciar(i,'modelo')
            return
        if not await self.contexto(i):return
        en=self.idioma(i)=='en'
        try:
            d=await self.api.pedir(i.guild_id,i.user.id,'modelos')
            if escolha is not None:
                d=await self.api.pedir(i.guild_id,i.user.id,'configurar_modelo',escolha=escolha,revisao=d['revisao'])
            nomes={'oficiais':('Dois modelos oficiais','Both official templates'),'era':('Era da Revolução','Era da Revolução'),
                   'ciclo':('Ciclo Maldito','Ciclo Maldito'),'servidor':('Modelo do servidor','Server template')}
            titulo=nomes[d['escolha']][1 if en else 0]
            texto=(f'Template: **{titulo}**. Creation by the bot only uses the official Ciclo Maldito, with `/character create`, when enabled. Existing characters keep their sheets. Register an existing sheet with `/character register`.' if en else
                   f'Modelo: **{titulo}**. A criação pelo bot só usa a oficial Ciclo Maldito, com `/personagem criar`, quando liberada. Personagens cadastrados continuam com suas fichas. Para uma ficha existente, use `/personagem cadastrar`.')
            await i.followup.send(texto,ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True)

    @grupo.command(name='modelos',description='Veja o modelo escolhido e a disponibilidade de criação')
    async def modelos(self,i:discord.Interaction):await self.mostrar_modelos(i)

    @grupo.command(name='modelo_configurar',description='Administrador: escolha o modelo sem alterar personagens cadastrados')
    @app_commands.choices(escolha=[app_commands.Choice(name='Padrão: dois oficiais',value='oficiais'),
        app_commands.Choice(name='Era da Revolução',value='era'),app_commands.Choice(name='Ciclo Maldito',value='ciclo'),
        app_commands.Choice(name='Personalizado pelo Google Picker',value='servidor')])
    async def modelo_configurar(self,i:discord.Interaction,escolha:str):await self.mostrar_modelos(i,escolha)

    @grupo_en.command(name='templates',description='View the selected template and creation availability')
    async def templates(self,i:discord.Interaction):await self.mostrar_modelos(i)

    @grupo_en.command(name='set_template',description='Administrator: select a template without changing registered characters')
    @app_commands.choices(choice=[app_commands.Choice(name='Default: both official templates',value='oficiais'),
        app_commands.Choice(name='Era da Revolução',value='era'),app_commands.Choice(name='Ciclo Maldito',value='ciclo'),
        app_commands.Choice(name='Custom via Google Picker',value='servidor')])
    async def set_template(self,i:discord.Interaction,choice:str):await self.mostrar_modelos(i,choice)

    @grupo.command(name='cargo_revisor',description='Administra o acesso privado da equipe; só dono ou administrador')
    async def cargo_revisor(self,i:discord.Interaction,cargo:discord.Role,permitir:bool):await self.alterar_revisor(i,cargo,permitir)

    @grupo_en.command(name='register',description='Connect a character sheet you already use')
    async def register(self,i:discord.Interaction):await self.iniciar(i,'cadastro')

    @grupo_en.command(name='create',description='Create an empty Ciclo Maldito sheet in your Google account')
    async def create(self,i:discord.Interaction):await self.iniciar(i,'criar')

    @grupo_en.command(name='replace_sheet',description='Replace a sheet without losing the character’s registration')
    @app_commands.autocomplete(character=completar)
    async def replace_sheet(self,i:discord.Interaction,character:str):await self.iniciar(i,'troca',character)

    @grupo_en.command(name='reconnect',description='Reconnect the character’s Google account')
    @app_commands.autocomplete(character=completar)
    async def reconnect(self,i:discord.Interaction,character:str):await self.iniciar(i,'reconectar',character)

    @grupo_en.command(name='view',description='Open a character’s basic card')
    @app_commands.autocomplete(character=completar)
    async def view(self,i:discord.Interaction,character:str):await self.ver_cartao(i,character)

    @grupo_en.command(name='analyse',description='Analyse privately; registration does not approve a sheet')
    @app_commands.autocomplete(character=completar)
    async def analyse(self,i:discord.Interaction,character:str):
        if await self.contexto(i):await self.consulta_privada(i,character,'analisar')

    @grupo_en.command(name='edit_card',description='Preview and confirm the card’s presentation; does not edit the sheet')
    @app_commands.autocomplete(character=completar)
    async def edit_card(self,i:discord.Interaction,character:str):
        if await self.contexto(i):await self.editar_privado(i,character)

    @grupo_en.command(name='image',description='Use a PNG, JPEG or WebP up to 1 MiB; confirm the preview to save')
    @app_commands.autocomplete(character=completar)
    async def image(self,i:discord.Interaction,character:str,file:discord.Attachment):await self.enviar_imagem(i,character,file)

    @grupo_en.command(name='reviewer_role',description='Manage private staff access; server owner or administrator only')
    async def reviewer_role(self,i:discord.Interaction,role:discord.Role,allow:bool):await self.alterar_revisor(i,role,allow)


async def setup(bot):
    # As Guias passam a configuração lida do .env delas; fora delas, vale o ambiente.
    cfg=getattr(bot,'config',None)
    origem=getattr(cfg,'carteira_url','') or os.environ['CARTEIRA_API_URL']
    token=getattr(cfg,'carteira_token','') or os.environ['CARTEIRA_SERVICE_TOKEN']
    await bot.add_cog(ConectarFicha(bot,origem,token,desenvolvimento=os.getenv('CARTEIRA_DEV')=='1'))
