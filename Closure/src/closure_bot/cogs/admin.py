"""Comandos de administração: /ping, /status e /teste_webhook."""
from __future__ import annotations

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from ..dados import resumo_manifesto
from ..plantao import FUSO, de_plantao


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Confere se o bot está no ar e qual versão das regras ele leu.")
    async def ping(self, interacao: discord.Interaction) -> None:
        await interacao.response.send_message(
            f"No ar ({round(self.bot.latency * 1000)} ms). Regras: {resumo_manifesto(self.bot.manifesto)}.",
            ephemeral=True,
        )

    @app_commands.command(name="status", description="Quem está de plantão, versões dos cards e contagens do registro.")
    async def status(self, interacao: discord.Interaction) -> None:
        agora = datetime.now(FUSO)
        plantao = self.bot.personas[de_plantao(agora)]
        cards = ", ".join(f"{p.nome} v{p.versao}" for p in self.bot.personas.values())
        contagens = self.bot.registro.contagens()
        await interacao.response.send_message(
            f"Agora ({agora:%H:%M}, Brasília) o plantão é de {plantao.nome}.\n"
            f"Cards: {cards}.\n"
            f"Registro: {contagens['gatilhos']} gatilhos, {contagens['chamadas_api']} chamadas de API, "
            f"{contagens['mensagens_bot']} mensagens enviadas.\n"
            f"Gasto estimado no mês com modelo pago: US$ {self.bot.modelos.gasto_do_mes():.2f} "
            f"de US$ {self.bot.modelos.teto_usd:.2f}.",
            ephemeral=True,
        )

    @app_commands.command(name="teste_webhook", description="Manda uma mensagem de teste com o nome e o avatar de quem está de plantão.")
    async def teste_webhook(self, interacao: discord.Interaction) -> None:
        if interacao.user.id != self.bot.config.dono_id:
            await interacao.response.send_message("Esse comando é só do dono do bot.", ephemeral=True)
            return
        persona = self.bot.personas[de_plantao(datetime.now(FUSO))]
        await interacao.response.defer(ephemeral=True)
        await self.bot.carteiro.enviar(interacao.channel, persona, "[teste de webhook]")
        await interacao.followup.send(f"Enviado como {persona.nome}.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
