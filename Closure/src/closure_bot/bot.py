"""O bot: junta configuração, registro, personagens e os módulos (admin, chat, regras, ficha)."""
from __future__ import annotations

import logging

import discord
from discord.ext import commands

from .carteiro import Carteiro
from .clima import ServicoClima
from .config import Config
from .dados import carregar_personas, ler_manifesto
from .modelo import FILA_PADRAO, RACIOCINIO_PADRAO, TETO_PADRAO_USD, Modelos, ler_fila
from .registro import Registro

log = logging.getLogger(__name__)

MODULOS = ("admin", "chat", "clima", "regras", "ficha")


class ClosureBot(commands.Bot):
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.message_content = True  # sem isso o bot não lê o nome chamado na mensagem
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, help_command=None)
        self.config = config
        self.registro = Registro(config.banco)
        self.manifesto = ler_manifesto(config.dados)
        self.personas = carregar_personas(config.dados, config.avatares)
        self.carteiro = Carteiro(self.registro)
        self.clima = ServicoClima()
        self.modelos = Modelos(ler_fila(config.fila_modelos or FILA_PADRAO), config.chaves, self.registro,
                               teto_usd=config.teto_mensal_usd or TETO_PADRAO_USD, raciocinio=config.raciocinio or RACIOCINIO_PADRAO)

    async def setup_hook(self) -> None:
        for modulo in MODULOS:
            await self.load_extension(f"closure_bot.cogs.{modulo}")
        if self.config.guild_id:
            servidor = discord.Object(id=self.config.guild_id)
            self.tree.copy_global_to(guild=servidor)
            await self.tree.sync(guild=servidor)
        else:
            await self.tree.sync()

    async def on_ready(self) -> None:
        log.info("no ar como %s, em %d servidor(es)", self.user, len(self.guilds))

    async def close(self) -> None:
        await super().close()
        self.registro.fechar()
