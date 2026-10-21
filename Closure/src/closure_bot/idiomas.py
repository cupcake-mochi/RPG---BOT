"""Traduções locais, antes de interpolar dados de usuários; sem serviços externos."""
from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path

_atual = ContextVar("idioma_guias", default="pt-BR")


def atual():
    return _atual.get()


def definir(idioma):
    return _atual.set("en" if idioma == "en" else "pt-BR")


@contextmanager
def usar(idioma):
    token = definir(idioma)
    try:
        yield
    finally:
        _atual.reset(token)


@lru_cache(maxsize=1)
def catalogo():
    return json.loads((Path(__file__).parent / "recursos" / "ingles.json").read_text(encoding="utf-8"))


def tr(texto: str, idioma: str | None = None) -> str:
    """Somente modelos estáticos entram aqui; nomes, prosa e números são interpolados depois."""
    if (idioma or atual()) != "en":
        return texto
    return catalogo().get(texto, texto)


def idioma_servidor(bot, guild_id):
    return bot.registro.opcoes_servidor(guild_id).idioma if guild_id else "pt-BR"


def preparar(bot, guild_id):
    definir(idioma_servidor(bot, guild_id))


# A linguagem do menu nativo é uma preferência do CLIENTE Discord. O idioma das
# respostas é do servidor. Os dois mecanismos são independentes por desenho.
def arvore_e_tradutor():
    import discord
    from discord import app_commands

    class Arvore(app_commands.CommandTree):
        async def interaction_check(self, interaction):
            preparar(self.client, interaction.guild_id)
            return True

    class Tradutor(app_commands.Translator):
        async def translate(self, string, locale, context):
            if locale not in (discord.Locale.american_english, discord.Locale.british_english):
                return None
            chave = str(string)
            if context.location.name.endswith("name"):
                return catalogo().get("discord:" + chave)
            return catalogo().get(chave)

    return Arvore, Tradutor
