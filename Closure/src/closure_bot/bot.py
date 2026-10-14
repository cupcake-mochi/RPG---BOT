"""O bot: junta configuração, registro, personagens e os módulos (admin, chat, clima, pessoa, regras, ficha)."""
from __future__ import annotations

import logging

import discord
from discord.ext import commands

from .carteiro import Carteiro
from .clima import ServicoClima
from .config import Config
from .conversa import Conversas
from .dados import carregar_personas, ler_manifesto
from .modelo import RACIOCINIO_PADRAO, TETO_PADRAO_USD, Modelos, fila_do_chat
from .registro import Registro
from .vida import Vida

log = logging.getLogger(__name__)

MODULOS = ("admin", "atalho", "chat", "clima", "pessoa", "regras", "ficha")


class ClosureBot(commands.Bot):
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.message_content = True  # sem isso o bot não lê o nome chamado na mensagem
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, help_command=None)
        self.config = config
        self.registro = Registro(config.banco, config.chave_do_banco)
        if not self.registro.cofre.ligado:
            log.warning("banco sem cifra: falta a CHAVE_DO_BANCO no .env (python3 -m closure_bot --gerar-chave)")
        self.manifesto = ler_manifesto(config.dados)
        self.personas = carregar_personas(config.dados, config.avatares)
        self.carteiro = Carteiro(self.registro)
        self.clima = ServicoClima()
        self.vida = Vida(self.registro)
        self.conversas = Conversas()
        self.tree.on_error = self._erro_de_comando
        self.mencoes: dict[str, str] = {}  # nome do comando -> menção clicável (</nome:id>), preenchida ao registrar
        self.modelos = Modelos(fila_do_chat(config.modelo_chat, config.fila_modelos), config.chaves, self.registro,
                               teto_usd=config.teto_mensal_usd if config.teto_mensal_usd is not None else TETO_PADRAO_USD,
                               raciocinio=config.raciocinio or RACIOCINIO_PADRAO,
                               argon_max_saida=config.argon_max_saida, vertex_projeto=config.vertex_projeto,
                               argon_teto_usd=config.argon_teto_usd, argon_perfil=config.argon_perfil, dados=config.dados)

    async def _erro_de_comando(self, interacao: discord.Interaction, erro: Exception) -> None:
        """Sem isto, um comando que quebra deixa a pessoa olhando pra "o aplicativo não respondeu"."""
        log.error("comando /%s falhou", getattr(interacao.command, "name", "?"), exc_info=erro)
        aviso = "Deu um erro aqui do meu lado. Tenta de novo daqui a pouco."
        try:
            if interacao.response.is_done():
                await interacao.followup.send(aviso, ephemeral=True)
            else:
                await interacao.response.send_message(aviso, ephemeral=True)
        except discord.HTTPException:
            pass

    async def setup_hook(self) -> None:
        for modulo in MODULOS:
            await self.load_extension(f"closure_bot.cogs.{modulo}")
        # O registro geral troca, em todo servidor, a lista de comandos que o bot antigo deixou no mesmo aplicativo.
        self.mencoes = {comando.name: comando.mention for comando in await self.tree.sync()}
        if self.config.guild_id:
            # Comando registrado só num servidor não sai com o registro geral e apareceria em dobro: limpa os desse.
            await self.tree.sync(guild=discord.Object(id=self.config.guild_id))

    async def on_message(self, mensagem: discord.Message) -> None:
        """Vazio de propósito. O padrão do discord.py lê toda mensagem que menciona o bot como comando de prefixo
        ("@bot o rato roeu" virava o comando "o", com erro no log). Quem trata mensagem são os módulos, cada um no seu on_message."""

    async def on_ready(self) -> None:
        log.info("no ar como %s, em %d servidor(es)", self.user, len(self.guilds))

    async def close(self) -> None:
        await super().close()
        self.registro.fechar()
