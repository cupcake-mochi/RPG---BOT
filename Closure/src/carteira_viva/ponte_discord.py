"""Extensão opcional: carrega apenas depois de configurar o serviço.

Não é carregada por closure_bot.bot nem empacotada com o bot atual. Usa só
aiohttp/discord.py; as bibliotecas OAuth ficam no serviço separado.
"""
import os
from urllib.parse import urlsplit

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from .cliente_discord import ClienteCarteira, FalhaCarteira, origem_valida
from .discord_ui import GaleriaView, ConsultaView, PreviaView, AbrirEditor, txt, erro, seguro


class ConectarFicha(commands.Cog):
    grupo = app_commands.Group(name="personagem", description="Conecte a ficha do seu personagem")

    grupo_en = app_commands.Group(name="character", description="Connect and manage your characters")

    def __init__(self, bot, origem, token, *, desenvolvimento=False):
        self.bot, self.origem, self.token = bot, origem.rstrip("/"), token
        origem_valida(self.origem, desenvolvimento)
        self.api = ClienteCarteira(origem, token, desenvolvimento=desenvolvimento)

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
                        raise ValueError("Serviço indisponível")
                    data = await resp.json()
            url = data["url"]
            u = urlsplit(url)
            if (u.scheme, u.netloc) != (urlsplit(self.origem).scheme, urlsplit(self.origem).netloc) or u.path != "/conectar":
                raise ValueError("Destino de conexão inválido")
            view = discord.ui.View(timeout=600)
            view.add_item(discord.ui.Button(label=texto("Conectar minha ficha", "Connect my sheet"), url=url))
            await interacao.followup.send(texto("Abra a conexão com a mesma conta Discord. O link vale por dez minutos e só você pode confirmar sua ficha.",
                                               "Open the connection with the same Discord account. The link lasts ten minutes and only you can confirm your sheet."),
                                          ephemeral=True, view=view)
        except (aiohttp.ClientError, TimeoutError, ValueError, KeyError):
            await interacao.followup.send(texto("Não consegui abrir a conexão agora. Confira o personagem ou tente novamente em instantes.",
                                               "Could not open the connection. Check the character or try again shortly."), ephemeral=True)

    async def completar(self,i,atual):
        if not i.guild_id:return []
        try:
            d=await self.api.pedir(i.guild_id,i.user.id,'listar')
            return [app_commands.Choice(name=seguro(c['perfil'].get('nome','Personagem'),90),value=c['id']) for c in d['cartoes'] if atual.casefold() in c['perfil'].get('nome','').casefold()][:20]
        except FalhaCarteira:return []

    @grupo.command(name="cadastrar", description="Conecte uma ficha que você já usa")
    async def cadastrar(self, interacao: discord.Interaction):
        await self.iniciar(interacao, "cadastro")

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
            if view.card:
                view.card=await self.api.pedir(i.guild_id,i.user.id,'cartao',personagem=view.card['id'])
                view.dados['cartoes']=[view.card if c['id']==view.card['id'] else c for c in view.dados['cartoes']]
                view.montar()
            kw=await view.conteudo();files=kw.pop('attachments')
            view.mensagem=await i.followup.send(**kw,files=files,view=view,wait=True,allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:await i.followup.send(erro(exc,lang),ephemeral=True)

    async def ver_cartao(self,i,personagem):
        if not await self.contexto(i,privado=False):return
        try:
            c=await self.api.pedir(i.guild_id,i.user.id,'cartao',personagem=personagem)
            view=GaleriaView(self,i.guild_id,i.user.id,c['responsavel'],{'cartoes':[c],'proximo':None},single=True)
            kw=await view.conteudo();files=kw.pop('attachments')
            view.mensagem=await i.followup.send(**kw,files=files,view=view,wait=True,allowed_mentions=discord.AllowedMentions.none())
        except FalhaCarteira as exc:await i.followup.send(erro(exc,self.idioma(i)),ephemeral=True)

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

    @grupo.command(name='cargo_revisor',description='Administra o acesso privado da equipe; só dono ou administrador')
    async def cargo_revisor(self,i:discord.Interaction,cargo:discord.Role,permitir:bool):await self.alterar_revisor(i,cargo,permitir)

    @grupo_en.command(name='register',description='Connect a character sheet you already use')
    async def register(self,i:discord.Interaction):await self.iniciar(i,'cadastro')

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
    await bot.add_cog(ConectarFicha(bot,os.environ['CARTEIRA_API_URL'],os.environ['CARTEIRA_SERVICE_TOKEN'],desenvolvimento=os.getenv('CARTEIRA_DEV')=='1'))
