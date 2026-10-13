"""O que as personagens guardam de cada pessoa, e os comandos pra ela ver, corrigir e apagar.

O desenho chama isto de "ficha de pessoa" (dados/personagem/kaltsit/vida.md, seções 4 e 8). Os comandos não usam
a palavra "ficha" porque num servidor de RPG ela quer dizer a ficha do personagem, que é o módulo ficha.py.
Cada pessoa só vê e só apaga o que é dela; as respostas são sempre só pra ela.
"""
from __future__ import annotations

from dataclasses import replace

import discord
from discord import app_commands
from discord.ext import commands

from ..vida import DIAS_POR_NIVEL, intimidade

PRONOMES_MAX = 30


class Pessoa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="meus_dados", description="Mostra o que a Kal'tsit e a Closure guardam sobre você.")
    async def meus_dados(self, interacao: discord.Interaction) -> None:
        eu = interacao.user.id
        ficha = self.bot.registro.ficha(eu)
        linhas = [f"Pronomes: {ficha.pronomes or 'não informados (elas usam forma neutra)'}."]
        linhas.append("Fatos sobre o jogo: " + ("; ".join(ficha.fatos) if ficha.fatos else "nenhum") + ".")
        for persona in self.bot.personas.values():
            dias = self.bot.registro.dias_de_conversa(autor_id=eu, persona=persona.chave)
            linhas.append(f"{persona.nome}: você falou com ela em {dias} dia(s) diferente(s) "
                          f"(intimidade {intimidade(dias)} de {len(DIAS_POR_NIVEL)}).")
        linhas.append("O texto das suas mensagens não fica guardado. Pra apagar tudo isto: /apagar_meus_dados.")
        await interacao.response.send_message("\n".join(linhas), ephemeral=True)

    @app_commands.command(name="meus_pronomes", description="Diz às personagens como tratar você. Sem texto, volta pra forma neutra.")
    @app_commands.describe(pronomes='Por exemplo "ele/dele", "ela/dela", "elu/delu".')
    async def meus_pronomes(self, interacao: discord.Interaction, pronomes: str | None = None) -> None:
        limpo = " ".join((pronomes or "").split())[:PRONOMES_MAX] or None
        self.bot.registro.gravar_ficha(interacao.user.id, replace(self.bot.registro.ficha(interacao.user.id), pronomes=limpo))
        await interacao.response.send_message(f"Anotado: {limpo}." if limpo else "Voltei pra forma neutra.", ephemeral=True)

    @app_commands.command(name="apagar_meus_dados", description="Apaga tudo o que as personagens guardam sobre você. Não tem volta.")
    async def apagar_meus_dados(self, interacao: discord.Interaction) -> None:
        self.bot.registro.apagar_pessoa(interacao.user.id)
        await interacao.response.send_message("Apagado: pronomes, fatos e o histórico de quando você chamou cada uma.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pessoa(bot))
