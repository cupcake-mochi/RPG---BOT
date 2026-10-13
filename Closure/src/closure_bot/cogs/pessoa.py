"""O que as personagens guardam de cada pessoa, os comandos pra ela ver, corrigir e apagar, e a reflexão diária.

O desenho chama isto de "ficha de pessoa" (dados/personagem/kaltsit/vida.md, seções 4, 7 e 8). Os comandos não usam
a palavra "ficha" porque num servidor de RPG ela quer dizer a ficha do personagem, que é o módulo ficha.py.
Cada pessoa só vê e só apaga o que é dela; as respostas são sempre só pra ela.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from datetime import time

import discord
from discord import app_commands
from discord.ext import commands, tasks

from ..plantao import FUSO
from ..reflexao import FATO_MAX, fato_permitido, refletir
from ..registro import FATOS_MAX
from ..vida import DIAS_POR_NIVEL, intimidade

log = logging.getLogger(__name__)

PRONOMES_MAX = 30
HORA_DA_REFLEXAO = time(4, 30, tzinfo=FUSO)


class Pessoa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.reflexao_diaria.start()

    async def cog_unload(self) -> None:
        self.reflexao_diaria.cancel()

    @tasks.loop(time=HORA_DA_REFLEXAO)
    async def reflexao_diaria(self) -> None:
        try:
            await refletir(self.bot.registro, self.bot.modelos)
        except Exception:  # um erro aqui não pode derrubar o laço: amanhã tem outra
            log.exception("reflexão diária falhou")

    @app_commands.command(name="meus_dados", description="Mostra o que a Kal'tsit e a Closure guardam sobre você.")
    async def meus_dados(self, interacao: discord.Interaction) -> None:
        eu = interacao.user.id
        ficha = self.bot.registro.ficha(eu)
        linhas = [f"Pronomes: {ficha.pronomes or 'não informados (elas usam forma neutra)'}."]
        linhas.append("Fatos:" if ficha.fatos else "Fatos: nenhum.")
        linhas += [f"{n}. {fato}" for n, fato in enumerate(ficha.fatos, 1)]
        for persona in self.bot.personas.values():
            dias = self.bot.registro.dias_de_conversa(autor_id=eu, persona=persona.chave)
            linhas.append(f"{persona.nome}: você falou com ela em {dias} dia(s) diferente(s) "
                          f"(intimidade {intimidade(dias)} de {len(DIAS_POR_NIVEL)}).")
        linhas.append("Quando você chama uma delas, o texto da mensagem fica guardado até as 4h30, vira no máximo alguns "
                      "fatos como os de cima e é apagado. /meu_fato acrescenta um, /esquecer_fato tira um, "
                      "/apagar_meus_dados apaga tudo.")
        await interacao.response.send_message("\n".join(linhas), ephemeral=True)

    @app_commands.command(name="meus_pronomes", description="Diz às personagens como tratar você. Sem texto, volta pra forma neutra.")
    @app_commands.describe(pronomes='Por exemplo "ele/dele", "ela/dela", "elu/delu".')
    async def meus_pronomes(self, interacao: discord.Interaction, pronomes: str | None = None) -> None:
        limpo = " ".join((pronomes or "").split())[:PRONOMES_MAX] or None
        self.bot.registro.gravar_ficha(interacao.user.id, replace(self.bot.registro.ficha(interacao.user.id), pronomes=limpo))
        await interacao.response.send_message(f"Anotado: {limpo}." if limpo else "Voltei pra forma neutra.", ephemeral=True)

    @app_commands.command(name="meu_fato", description="Conta uma coisa sobre você pra elas lembrarem (personagem, mesa, gosto).")
    @app_commands.describe(fato='Uma frase curta, por exemplo "jogo com um Bastião chamado Ren na mesa do Tiago".')
    async def meu_fato(self, interacao: discord.Interaction, fato: str) -> None:
        limpo = " ".join(fato.split())
        ficha = self.bot.registro.ficha(interacao.user.id)
        if not fato_permitido(limpo):
            aviso = (f"Não guardei. O fato tem que ter até {FATO_MAX} letras, e elas não guardam saúde, dinheiro, religião, "
                     "política, relacionamento, idade, endereço nem contato.")
        elif limpo in ficha.fatos:
            aviso = "Esse elas já sabem."
        else:
            self.bot.registro.gravar_ficha(interacao.user.id, replace(ficha, fatos=ficha.fatos + (limpo,)))
            saiu = f" Como o limite é {FATOS_MAX}, o mais antigo saiu." if len(ficha.fatos) >= FATOS_MAX else ""
            aviso = f"Anotado: {limpo}.{saiu}"
        await interacao.response.send_message(aviso, ephemeral=True)

    @app_commands.command(name="esquecer_fato", description="Tira um fato da sua lista. O número é o que aparece em /meus_dados.")
    async def esquecer_fato(self, interacao: discord.Interaction, numero: int) -> None:
        ficha = self.bot.registro.ficha(interacao.user.id)
        if not 1 <= numero <= len(ficha.fatos):
            await interacao.response.send_message("Não achei esse número. Veja a lista em /meus_dados.", ephemeral=True)
            return
        self.bot.registro.gravar_ficha(interacao.user.id, replace(ficha, fatos=ficha.fatos[:numero - 1] + ficha.fatos[numero:]))
        await interacao.response.send_message(f"Esquecido: {ficha.fatos[numero - 1]}.", ephemeral=True)

    @app_commands.command(name="apagar_meus_dados", description="Apaga tudo o que as personagens guardam sobre você. Não tem volta.")
    async def apagar_meus_dados(self, interacao: discord.Interaction) -> None:
        self.bot.registro.apagar_pessoa(interacao.user.id)
        await interacao.response.send_message("Apagado: pronomes, fatos, mensagens de hoje e o histórico de quando você chamou cada uma.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pessoa(bot))
