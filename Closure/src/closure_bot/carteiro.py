"""Envio das falas: um bot só, com o nome e o avatar de quem fala em cada mensagem.

O caminho é o webhook do canal, que aceita `username` e `avatar_url` por mensagem. Trocar o nome da conta do
bot não serve (o Discord limita a poucas trocas por hora). Toda mensagem enviada tem o ID guardado no
registro, pra o bot reconhecer depois quando alguém responde a ela.
"""
from __future__ import annotations

import logging

import discord

from .dados import Persona
from .registro import Registro

log = logging.getLogger(__name__)

NOME_WEBHOOK = "Guias do Ciclo"


class Carteiro:
    def __init__(self, registro: Registro):
        self._registro = registro
        self._webhooks: dict[int, discord.Webhook] = {}

    async def _webhook(self, canal: discord.TextChannel) -> discord.Webhook:
        if canal.id not in self._webhooks:
            existentes = await canal.webhooks()
            meu = next((w for w in existentes if w.name == NOME_WEBHOOK and w.token), None)
            self._webhooks[canal.id] = meu or await canal.create_webhook(name=NOME_WEBHOOK)
        return self._webhooks[canal.id]

    async def enviar(self, canal: discord.abc.Messageable, persona: Persona, texto: str, *, lembrar: bool = True) -> discord.Message:
        """Manda `texto` como a personagem. Em tópico, usa o webhook do canal pai.

        Com `lembrar`, o texto entra nas últimas falas dela no canal (pra não repetir depois); mensagem de teste não entra."""
        topico = canal if isinstance(canal, discord.Thread) else None
        base = canal.parent if topico else canal
        try:
            webhook = await self._webhook(base)
            extras = {"thread": topico} if topico else {}
            mensagem = await webhook.send(texto, username=persona.nome, avatar_url=persona.avatar_url,
                                          allowed_mentions=discord.AllowedMentions.none(), wait=True, **extras)
        except (discord.Forbidden, AttributeError):
            # Sem permissão de gerenciar webhooks (ou canal que não tem webhook): sai pela conta do bot, com o nome na frente.
            log.warning("sem webhook no canal %s; enviando pela conta do bot", getattr(canal, "id", "?"))
            self._webhooks.pop(getattr(base, "id", 0), None)
            mensagem = await canal.send(f"**{persona.nome}:** {texto}", allowed_mentions=discord.AllowedMentions.none())
        self._registro.registrar_mensagem(message_id=mensagem.id, canal_id=canal.id, persona=persona.chave)
        if lembrar:
            self._registro.guardar_fala(canal_id=canal.id, persona=persona.chave, texto=texto)
        return mensagem
