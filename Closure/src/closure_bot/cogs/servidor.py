"""Idioma e mundo são preferências independentes, com delegação administrativa explícita."""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from ..servidor import administrador, autorizado


class Servidor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def permitir(self, i, *, somente_admin=False):
        if not i.guild_id:
            await i.response.send_message("Use em um servidor. / Use this in a server.", ephemeral=True)
            return False
        opcoes = self.bot.registro.opcoes_servidor(i.guild_id)
        pode = administrador(i.user, i.permissions) if somente_admin else autorizado(i.user, opcoes, i.permissions)
        if not pode:
            texto = ("You need Manage Server or an authorized administrative role." if opcoes.idioma == "en" else
                     "Você precisa de Gerenciar servidor ou de um cargo administrativo autorizado.")
            if somente_admin:
                texto = ("Only members with Manage Server can change the authorized roles." if opcoes.idioma == "en" else
                         "Só quem tem Gerenciar servidor pode mudar os cargos autorizados.")
            await i.response.send_message(texto, ephemeral=True)
        return pode

    async def mudar_idioma(self, i, idioma):
        if not await self.permitir(i):
            return
        atual = self.bot.registro.opcoes_servidor(i.guild_id)
        if idioma is not None:
            atual = self.bot.registro.configurar_publico(i.guild_id, idioma=idioma)
        texto = ("Server language: **English**. Use `/language` to change it. Lore is a separate setting: `/lnt`." if atual.idioma == "en" else
                 "Idioma do servidor: **Português do Brasil**. Use `/idioma` para mudar. O mundo é uma configuração separada: `/lnt`.")
        await i.response.send_message(texto, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="idioma", description="Consultar ou escolher o idioma do servidor: português ou inglês.")
    @app_commands.guild_only()
    @app_commands.choices(idioma=[app_commands.Choice(name="Português do Brasil", value="pt-BR"), app_commands.Choice(name="English", value="en")])
    async def idioma(self, interacao: discord.Interaction, idioma: str | None = None):
        await self.mudar_idioma(interacao, idioma)

    @app_commands.command(name="language", description="View or set the server language: English or Brazilian Portuguese.")
    @app_commands.guild_only()
    @app_commands.choices(language=[app_commands.Choice(name="English", value="en"), app_commands.Choice(name="Português do Brasil", value="pt-BR")])
    async def language(self, interaction: discord.Interaction, language: str | None = None):
        await self.mudar_idioma(interaction, language)

    @app_commands.command(name="lnt", description="Consultar, ativar ou desativar a lore Nova Terra neste servidor.")
    @app_commands.guild_only()
    async def lnt(self, interacao: discord.Interaction, ativar: bool | None = None):
        if not await self.permitir(interacao):
            return
        atual = self.bot.registro.opcoes_servidor(interacao.guild_id)
        if ativar is not None:
            atual = self.bot.registro.configurar_publico(interacao.guild_id, nova_terra=ativar)
        if atual.idioma == "en":
            texto = ("**Nova Terra lore is on.** The guides use Mizuki's campaign sources. This does not approve characters or custom rules." if atual.nova_terra else
                     "**Nova Terra lore is off.** The guides use the original Arknights setting and keep tabletop/Jujutsu rules separate. Campaign memories are not loaded.")
            texto += "\nUse `/lnt` with the enable option to change this. Changing worlds starts a new conversation context; saved facts stay in their original world."
        else:
            texto = ("**Lore Nova Terra ativada.** As guias consultam as fontes da campanha do Mizuki. Isso não aprova fichas nem regras próprias." if atual.nova_terra else
                     "**Lore Nova Terra desativada.** As guias usam o cenário original de Arknights e separam dele as regras de mesa/Jujutsu. As memórias da campanha não entram.")
            texto += "\nUse `/lnt ativar:Sim/Não` para mudar. A troca começa um contexto novo de conversa; fatos salvos permanecem no mundo em que foram registrados."
        await interacao.response.send_message(texto, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="cargo_admin", description="Autorizar ou retirar um cargo para configurar idioma e lore.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def cargo_admin(self, interacao: discord.Interaction, cargo: discord.Role | None = None, remover: bool = False):
        if not await self.permitir(interacao, somente_admin=True):
            return
        atual = self.bot.registro.opcoes_servidor(interacao.guild_id)
        cargos = set(atual.cargos)
        if cargo:
            if getattr(getattr(cargo,"guild",None),"id",None) != interacao.guild_id or cargo.id == interacao.guild_id or cargo.managed:
                await interacao.response.send_message("Escolha um cargo próprio, sem ser @everyone ou de integração. / Choose a custom role, not @everyone or a managed role.", ephemeral=True)
                return
            cargos.discard(cargo.id) if remover else cargos.add(cargo.id)
            try:
                atual = self.bot.registro.configurar_publico(interacao.guild_id, cargos=cargos)
            except ValueError:
                await interacao.response.send_message("Limite: 20 cargos. / Limit: 20 roles.", ephemeral=True)
                return
        lista = ", ".join(f"<@&{r}>" for r in atual.cargos)
        texto = ("Roles authorized to change language and lore: " + (lista or "none; Manage Server still applies.") if atual.idioma == "en" else
                 "Cargos autorizados a mudar idioma e lore: " + (lista or "nenhum; Gerenciar servidor continua valendo."))
        await interacao.response.send_message(texto, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())


async def setup(bot):
    await bot.add_cog(Servidor(bot))
