"""Conversa: decide se alguém chamou uma personagem e quem responde.

Fase 1: só decide e registra o gatilho. A resposta em si (busca nas regras, prompt do card, chamada ao
modelo) entra nas fases 2 e 4, no ponto marcado abaixo.
"""
from __future__ import annotations

import logging
from datetime import datetime

import discord
from discord.ext import commands

from ..plantao import FUSO, decidir

log = logging.getLogger(__name__)


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _respondeu_ao_bot(self, mensagem: discord.Message) -> bool:
        ref = mensagem.reference
        if not ref or not ref.message_id:
            return False
        if self.bot.registro.persona_da_mensagem(ref.message_id):
            return True
        original = ref.resolved
        return isinstance(original, discord.Message) and original.author.id == self.bot.user.id

    @commands.Cog.listener()
    async def on_message(self, mensagem: discord.Message) -> None:
        # Mensagem de bot ou de webhook (inclusive as nossas) nunca é gatilho; conversa privada fica pra depois.
        if mensagem.author.bot or mensagem.webhook_id or mensagem.guild is None:
            return
        canal_id = getattr(mensagem.channel, "parent_id", None) or mensagem.channel.id
        if not self.bot.config.escuta(canal_id):
            return

        decisao = decidir(
            mensagem.content,
            datetime.now(FUSO),
            mencionou_bot=self.bot.user in mensagem.mentions,
            respondeu_ao_bot=self._respondeu_ao_bot(mensagem),
        )
        if decisao is None:
            return

        self.bot.registro.registrar_gatilho(canal_id=mensagem.channel.id, autor_id=mensagem.author.id,
                                            persona=decisao.persona, motivo=decisao.motivo,
                                            fora_do_plantao=decisao.fora_do_plantao)
        log.info("gatilho: %s responderia (%s%s)", decisao.persona, decisao.motivo,
                 ", fora do plantão" if decisao.fora_do_plantao else "")
        # Fases 2 e 4: montar o contexto, chamar o modelo e enviar com
        # self.bot.carteiro.enviar(mensagem.channel, self.bot.personas[decisao.persona], resposta).
        # No bloco 4 do contexto entra a linha de clima.contexto_clima(self.bot.clima, mensagem.content),
        # quando ela não for None (a mensagem puxou o assunto e deu pra ler).
        # Pra ela não repetir abertura e frase de uma conversa pra outra, o pedido leva
        # self.bot.registro.ultimas_falas(canal_id=mensagem.channel.id, persona=decisao.persona).


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
