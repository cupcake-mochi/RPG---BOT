"""O que as personagens guardam de cada pessoa, os comandos pra ela ver, corrigir e apagar, e a reflexão diária.

O desenho chama isto de "ficha de pessoa" (dados/personagem/kaltsit/vida.md, seções 4, 7 e 8). Os comandos não usam
a palavra "ficha" porque num servidor de RPG ela quer dizer a ficha do personagem, que é o módulo ficha.py.
Cada pessoa só vê e só apaga o que é dela; as respostas são sempre só pra ela.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from datetime import datetime, time, timedelta

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


def _pontuar(texto: str) -> str:
    return texto if texto.endswith((".", "!", "?", "…")) else texto + "."


class Pessoa(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _contexto(self, interacao):
        gid = getattr(interacao, "guild_id", None)
        return self.bot.registro.opcoes_servidor(gid).contexto(gid) if gid else ""

    def _ficha(self, interacao):
        contexto = self._contexto(interacao)
        return self.bot.registro.ficha_contexto(interacao.user.id, contexto) if contexto else self.bot.registro.ficha(interacao.user.id)

    def _gravar(self, interacao, ficha):
        contexto = self._contexto(interacao)
        if contexto:
            self.bot.registro.gravar_ficha_contexto(interacao.user.id, contexto, ficha)
        else:
            self.bot.registro.gravar_ficha(interacao.user.id, ficha)

    async def cog_load(self) -> None:
        self.reflexao_diaria.start()
        self.limpeza_conversas.start()

    async def cog_unload(self) -> None:
        self.reflexao_diaria.cancel()
        self.limpeza_conversas.cancel()

    @tasks.loop(minutes=1)
    async def limpeza_conversas(self) -> None:
        self.bot.conversas.limpar(datetime.now(FUSO))

    @tasks.loop(time=HORA_DA_REFLEXAO)
    async def reflexao_diaria(self) -> None:
        try:
            await refletir(self.bot.registro, self.bot.modelos)
        except Exception:  # um erro aqui não pode derrubar o laço: amanhã tem outra
            log.exception("reflexão diária falhou")

    @reflexao_diaria.before_loop
    async def _ao_subir(self) -> None:
        await self.bot.wait_until_ready()
        await self.por_em_dia(datetime.now(FUSO))

    async def por_em_dia(self, agora: datetime) -> bool:
        """Se ficou mensagem de antes da última reflexão marcada (o bot estava fora do ar às 4h30), reflete agora.
        O texto de quem chamou não pode ficar guardado além disso."""
        devida = datetime.combine(agora.date(), HORA_DA_REFLEXAO)
        if agora < devida:
            devida -= timedelta(days=1)
        mais_antiga = self.bot.registro.mensagem_do_dia_mais_antiga()
        if mais_antiga is None or mais_antiga >= devida:
            return False
        log.info("reflexão atrasada: tem mensagem guardada de antes das 4h30")
        await self.reflexao_diaria()
        return True

    @app_commands.command(name="meus_dados", description="Mostra o que a Kal'tsit e a Closure guardam sobre você.")
    async def meus_dados(self, interacao: discord.Interaction, legado: bool = False) -> None:
        eu = interacao.user.id
        ficha = self.bot.registro.ficha(eu) if legado else self._ficha(interacao)
        escopo = tr('Memória antiga, sem servidor identificado; não entra nas novas conversas.') if legado else tr('Fatos deste servidor e do mundo atualmente escolhido. Pronomes são pessoais.')
        linhas = [escopo, tr('Pronomes: {0}.').format(ficha.pronomes or 'não informados (elas usam forma neutra)')]
        linhas.append(tr('Fatos:') if ficha.fatos else tr('Fatos: nenhum.'))
        linhas += [f"{n}. {fato}" for n, fato in enumerate(ficha.fatos, 1)]
        for persona in self.bot.personas.values():
            dias = self.bot.registro.dias_de_conversa(autor_id=eu, persona=persona.chave)
            periodo = tr('1 dia') if dias == 1 else tr('{0} dias').format(dias)
            linhas.append(tr('{0}: você falou com ela em {1} (intimidade {2} de {3}).').format(persona.nome, periodo, intimidade(dias), len(DIAS_POR_NIVEL)))
        linhas.append(tr('A conversa recente guarda até 12 falas, por até 30 minutos sem conversa ou até as 4h30, mesmo após reiniciar. Quando você chama uma delas, o texto da mensagem fica guardado até as 4h30, pode dar origem a alguns fatos como os de cima e depois é apagado. /meu_fato acrescenta um, /esquecer_fato tira um, /apagar_meus_dados apaga tudo.'))
        if self.bot.config.politica_url:
            linhas.append(tr('Política de privacidade: {0}').format(self.bot.config.politica_url))
        from .chat import em_partes
        partes=em_partes("\n".join(linhas))
        await interacao.response.send_message(partes[0],ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
        for parte in partes[1:]:
            await interacao.followup.send(parte,ephemeral=True,allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="meus_pronomes", description="Diz às personagens como tratar você. Sem texto, volta pra forma neutra.")
    @app_commands.describe(pronomes='Por exemplo "ele/dele", "ela/dela", "elu/delu".')
    async def meus_pronomes(self, interacao: discord.Interaction, pronomes: str | None = None) -> None:
        limpo = " ".join((pronomes or "").split())[:PRONOMES_MAX] or None
        self.bot.registro.gravar_ficha(interacao.user.id, replace(self.bot.registro.ficha(interacao.user.id), pronomes=limpo))
        await interacao.response.send_message(_pontuar(tr('Anotado: {0}').format(limpo)) if limpo else tr('Voltei pra forma neutra.'), ephemeral=True)

    @app_commands.command(name="meu_fato", description="Conta uma coisa sobre você pra elas lembrarem (personagem, mesa, gosto).")
    @app_commands.describe(fato='Uma frase curta, por exemplo "jogo com um Bastião chamado Ren na mesa do Tiago".')
    async def meu_fato(self, interacao: discord.Interaction, fato: str) -> None:
        limpo = " ".join(fato.split())
        ficha = self._ficha(interacao)
        if not fato_permitido(limpo):
            aviso = (tr('Não guardei. O fato precisa ter até {0} caracteres, e elas não guardam saúde, dinheiro, religião, política, relacionamento, idade, endereço nem contato.').format(FATO_MAX))
        elif limpo in ficha.fatos:
            aviso = tr('Esse elas já sabem.')
        else:
            self._gravar(interacao, replace(ficha, fatos=ficha.fatos + (limpo,)))
            saiu = tr(' Como o limite é {0}, o mais antigo saiu.').format(FATOS_MAX) if len(ficha.fatos) >= FATOS_MAX else ""
            aviso = _pontuar(tr('Anotado: {0}').format(limpo)) + saiu
        await interacao.response.send_message(aviso, ephemeral=True)

    @app_commands.command(name="esquecer_fato", description="Tira um fato da sua lista. O número é o que aparece em /meus_dados.")
    async def esquecer_fato(self, interacao: discord.Interaction, numero: int) -> None:
        ficha = self._ficha(interacao)
        if not 1 <= numero <= len(ficha.fatos):
            await interacao.response.send_message(tr('Não achei esse número. Veja a lista em /meus_dados.'), ephemeral=True)
            return
        self._gravar(interacao, replace(ficha, fatos=ficha.fatos[:numero - 1] + ficha.fatos[numero:]))
        await interacao.response.send_message(_pontuar(tr('Esquecido: {0}').format(ficha.fatos[numero - 1])), ephemeral=True)

    @app_commands.command(name="apagar_meus_dados", description="Apaga tudo o que as personagens guardam sobre você. Não tem volta.")
    async def apagar_meus_dados(self, interacao: discord.Interaction) -> None:
        self.bot.registro.apagar_pessoa(interacao.user.id)
        await interacao.response.send_message(tr('Apagado: pronomes, fatos, mensagens de hoje e o histórico de quando você chamou cada uma.'), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Pessoa(bot))
