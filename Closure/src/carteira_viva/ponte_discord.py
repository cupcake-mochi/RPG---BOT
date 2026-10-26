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


class ConectarFicha(commands.Cog):
    grupo = app_commands.Group(name="personagem", description="Conecte a ficha do seu personagem")

    def __init__(self, bot, origem, token):
        self.bot, self.origem, self.token = bot, origem.rstrip("/"), token
        u = urlsplit(self.origem)
        if not u.hostname or u.scheme != "https" or u.path not in ("", "/") or u.query or u.fragment or u.username or u.password or len(token) < 32:
            raise ValueError("Configure a origem HTTPS e o segredo de serviço da Carteira.")

    async def iniciar(self, interacao, acao, personagem=None):
        en = str(getattr(interacao, "locale", "")).startswith("en")
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

    @grupo.command(name="cadastrar", description="Conecte uma ficha que você já usa")
    async def cadastrar(self, interacao: discord.Interaction):
        await self.iniciar(interacao, "cadastro")

    @grupo.command(name="trocar_arquivo", description="Troque o arquivo sem perder o cadastro do personagem")
    async def trocar(self, interacao: discord.Interaction, personagem: str):
        await self.iniciar(interacao, "troca", personagem)

    @grupo.command(name="reconectar", description="Restabeleça a conexão Google do personagem")
    async def reconectar(self, interacao: discord.Interaction, personagem: str):
        await self.iniciar(interacao, "reconectar", personagem)


async def setup(bot):
    await bot.add_cog(ConectarFicha(bot, os.environ["CARTEIRA_API_URL"], os.environ["CARTEIRA_SERVICE_TOKEN"]))
