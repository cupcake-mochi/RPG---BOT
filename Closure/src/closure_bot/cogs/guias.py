"""Orientação estática, sem consultar fichas, modelos ou configurações privadas."""
from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from .. import guias
from ..ficha_paginacao import PaginasFicha


class GuiaNavegavel(PaginasFicha):
    def __init__(self, tema: str):
        self.tema = tema
        super().__init__(guias.paginas(tema), aviso_encerrado="Abra /guia ou GC:guia novamente para continuar")

    @discord.ui.select(placeholder="Ir para uma página", row=1)
    async def seletor(self, interacao: discord.Interaction, seletor: discord.ui.Select):
        try:
            indice = int(seletor.values[0])
        except (ValueError, IndexError):
            indice = self.indice
        await self.mostrar(interacao, indice)

    @discord.ui.button(label="Primeira", emoji="⏮️", row=2)
    async def primeira(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, 0)

    @discord.ui.button(label="Anterior", emoji="◀️", row=2)
    async def anterior(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, deslocamento=-1)

    @discord.ui.button(label="Próxima", emoji="▶️", row=2)
    async def proxima(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, deslocamento=1)

    @discord.ui.button(label="Última", emoji="⏭️", row=2)
    async def ultima(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, len(self.paginas) - 1)

    def _atualizar(self):
        super()._atualizar()
        self.assuntos.options = [discord.SelectOption(label=titulo, value=tema, default=tema == self.tema)
                                 for tema, (titulo, _) in guias.ASSUNTOS.items()]

    @discord.ui.select(placeholder="Escolha um assunto", row=0)
    async def assuntos(self, interacao: discord.Interaction, seletor: discord.ui.Select):
        async with self._troca:
            if self.is_finished():
                await interacao.response.send_message(f"Os controles encerraram. {self.aviso_encerrado}.", ephemeral=True)
                return
            tema = seletor.values[0] if seletor.values else self.tema
            if tema not in guias.ASSUNTOS:
                tema = self.tema
            self.tema = tema
            self.paginas = guias.paginas(tema)
            self.indice = 0
            self._atualizar()
            await interacao.response.edit_message(embed=self.paginas[0], view=self,
                                                  allowed_mentions=discord.AllowedMentions.none())
            self._ultima_interacao = interacao


class Guias(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def enviar(self, enviar, tema: str | None = None):
        tema = guias.assunto(tema)
        if tema is None:
            await enviar("Não achei esse assunto. Use `GC:guia` ou `/guia` para escolher no menu.")
            return
        view = GuiaNavegavel(tema)
        view.mensagem = await enviar(embed=view.paginas[0], view=view)

    async def pela_barra(self, interacao: discord.Interaction, tema: str | None = None):
        async def enviar(texto=None, **extras):
            await interacao.response.send_message(texto, **extras, ephemeral=True,
                                                  allowed_mentions=discord.AllowedMentions.none())
            return await interacao.original_response()
        await self.enviar(enviar, tema)

    @app_commands.command(name="guia", description="Como criar sua ficha, conhecer a planilha e usar o bot.")
    @app_commands.describe(assunto="Escolha o assunto ou deixe em branco para começar.")
    @app_commands.choices(assunto=[app_commands.Choice(name=titulo, value=tema)
                                  for tema, (titulo, _) in guias.ASSUNTOS.items()])
    async def guia(self, interacao: discord.Interaction, assunto: str | None = None):
        await self.pela_barra(interacao, assunto)


async def setup(bot: commands.Bot):
    await bot.add_cog(Guias(bot))
