"""Navegação pública de uma análise já calculada; sem nova leitura ou chamada de modelo."""
from __future__ import annotations

import asyncio
import logging

import discord

log = logging.getLogger(__name__)
TEMPO_CONTROLES = 600


class PaginasFicha(discord.ui.View):
    def __init__(self, paginas: list[discord.Embed]):
        super().__init__(timeout=TEMPO_CONTROLES)
        if not paginas:
            raise ValueError("a análise precisa de uma página")
        self.paginas = paginas
        self.indice = 0
        self.mensagem = None
        self._ultima_interacao = None
        self._troca = asyncio.Lock()
        self._atualizar()

    def _atualizar(self):
        ultima = len(self.paginas) - 1
        self.primeira.disabled = self.anterior.disabled = self.indice == 0
        self.proxima.disabled = self.ultima.disabled = self.indice == ultima
        # O Discord aceita até 25 opções. As setas alcançam as páginas fora da janela.
        inicio = max(0, min(self.indice - 12, len(self.paginas) - 25))
        self.seletor.options = [discord.SelectOption(
            label=f"{i + 1}. {self.paginas[i].footer.text.split(' · ')[1]}"[:100],
            value=str(i), default=i == self.indice,
        ) for i in range(inicio, min(inicio + 25, len(self.paginas)))]
        self.seletor.placeholder = f"Página {self.indice + 1} de {len(self.paginas)} — ir para…"
        self.seletor.disabled = len(self.paginas) == 1

    async def mostrar(self, interacao: discord.Interaction, indice: int | None = None, *, deslocamento=0):
        async with self._troca:
            if self.is_finished():
                await interacao.response.send_message("Os controles encerraram. Rode a análise novamente para abrir.", ephemeral=True)
                return
            if indice is None:
                indice = self.indice + deslocamento
            self.indice = max(0, min(indice, len(self.paginas) - 1))
            self._atualizar()
            await interacao.response.edit_message(embed=self.paginas[self.indice], view=self,
                                                  allowed_mentions=discord.AllowedMentions.none())
            self._ultima_interacao = interacao

    @discord.ui.select(placeholder="Ir para uma página", row=0)
    async def seletor(self, interacao: discord.Interaction, seletor: discord.ui.Select):
        try:
            indice = int(seletor.values[0])
        except (ValueError, IndexError):
            indice = self.indice
        await self.mostrar(interacao, indice)

    @discord.ui.button(label="Primeira", emoji="⏮️", row=1)
    async def primeira(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, 0)

    @discord.ui.button(label="Anterior", emoji="◀️", row=1)
    async def anterior(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, deslocamento=-1)

    @discord.ui.button(label="Próxima", emoji="▶️", row=1)
    async def proxima(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, deslocamento=1)

    @discord.ui.button(label="Última", emoji="⏭️", row=1)
    async def ultima(self, interacao: discord.Interaction, botao: discord.ui.Button):
        await self.mostrar(interacao, len(self.paginas) - 1)

    async def on_timeout(self):
        async with self._troca:
            self.stop()
            # A mensagem continua útil depois da navegação: volta ao resumo.
            self.indice = 0
            self._atualizar()
            for item in self.children:
                item.disabled = True
            if self.mensagem is not None:
                resumo = self.paginas[0].copy()
                resumo.set_footer(text=resumo.footer.text + " · Controles encerrados; rode a análise novamente para abrir")
                try:
                    # A navegação pode durar mais que o token do comando inicial.
                    # O último clique tem token novo e o timeout é menor que sua validade.
                    editar = self._ultima_interacao.edit_original_response if self._ultima_interacao else self.mensagem.edit
                    await editar(embed=resumo, view=self, allowed_mentions=discord.AllowedMentions.none())
                except discord.HTTPException:
                    log.info("não foi possível encerrar os controles do painel de ficha")


async def enviar_relatorio(resposta: list[discord.Embed] | str, enviar):
    """Serve ao GC:ficha e à barra, preservando a mesma apresentação e mensagem pública."""
    if isinstance(resposta, str):
        await enviar(resposta)
        return
    view = PaginasFicha(resposta) if len(resposta) > 1 else None
    mensagem = await enviar(embed=resposta[0], **({"view": view} if view is not None else {}))
    if view is not None:
        view.mensagem = mensagem
