"""Regras: /livro manda o link do livro de regras em PDF. A consulta por comando (/regra) entra na fase 2 do
docs/PLANEJAMENTO.md; hoje a busca no livro vive dentro do chat.

O PDF passa de 50 MB, acima do que o Discord deixa um bot anexar, então vai o link (LIVRO_URL no .env).
"""
from __future__ import annotations

from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from ..plantao import CLOSURE, FUSO, de_plantao
from ..idiomas import atual

COR = 0xCC0102
# Uma frase por guia, no jeito de cada uma; quem aparece é quem está de plantão.
FALA = {CLOSURE: "Tá aqui o livro de regras inteiro, em PDF.",
        "kaltsit": "O livro de regras inteiro está aqui, em PDF."}


class Regras(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def painel_do_livro(self) -> tuple[discord.Embed, discord.ui.View]:
        url = self.bot.config.livro_url
        persona = self.bot.personas[de_plantao(datetime.now(FUSO))]
        ingles = atual() == "en"
        descricao = ("Choose **standard theme** or **dark theme** below. The official editions have the same text; only the appearance changes. "
                     "Large PDFs may take a while to open on mobile." if ingles else
                     "Escolha **tema normal** ou **tema escuro** nos botões abaixo. As duas edições oficiais têm o mesmo texto; muda a aparência. "
                     "Os PDFs são grandes e podem demorar para abrir no celular.")
        embed = discord.Embed(title="Ciclo Maldito rulebook" if ingles else "Livro de regras do Ciclo Maldito",url=url,color=COR,description=descricao)
        embed.set_author(name=persona.nome,icon_url=persona.avatar_url or None)
        manifesto = getattr(self.bot,"manifesto",None) or {}
        if manifesto.get("edicao_livro"):
            edicao=manifesto['edicao_livro']
            versao=manifesto.get('versao_sistema','?')
            embed.set_footer(text=(f"General lookup reference: {edicao} ({versao}). The PDFs may be newer; check your table's edition." if ingles else
                                   f"Base geral de consulta: {edicao} ({versao}). Os PDFs podem ser mais recentes; confira a edição da mesa."))
        botao = discord.ui.View()
        botao.add_item(discord.ui.Button(label="Standard theme" if ingles else "Tema normal",url=url))
        botao.add_item(discord.ui.Button(label="Dark theme" if ingles else "Tema escuro",url=self.bot.config.livro_noturno_url))
        return embed, botao

    @app_commands.command(name="livro", description="Link do livro de regras do Ciclo Maldito, em PDF.")
    async def livro(self, interacao: discord.Interaction) -> None:
        embed, botao = self.painel_do_livro()
        await interacao.response.send_message(embed=embed, view=botao)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Regras(bot))
