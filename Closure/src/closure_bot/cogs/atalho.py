"""Comandos escritos no chat com "GC:" na frente, pra quem não quer usar a barra (pedido do Mizuki, 13/10/2026).

Só entram aqui os comandos de resposta pública: ajuda, livro, ficha, clima, ping e status. `GC:ficha` leva o link
da planilha depois do comando ou o .xlsx anexo na mesma mensagem. Os que mostram ou mexem em dado da
pessoa, e os de quem cuida do servidor, continuam só na barra, porque lá a resposta aparece só pra quem pediu;
aqui o bot aponta o comando certo. Funciona em qualquer canal que o bot leia, como os comandos de barra.
"""
from __future__ import annotations

import logging
import re

import discord
from discord.ext import commands

from .clima import _com_arte
from ..ficha_paginacao import enviar_relatorio
from ..idiomas import preparar, tr
from ..atalhos import OUTROS_NOMES, SO_NA_BARRA, destinos, limpo, resolver
from discord import app_commands

log = logging.getLogger(__name__)

PREFIXO = re.compile(r"\s*gc\s*:\s*(\w*)\s*(.*)", re.IGNORECASE | re.DOTALL)


def separar(texto: str, personalizados: dict[str, str] | None = None) -> tuple[str, str] | None:
    """("clima", "Quioto") pra "GC: clima Quioto"; None se a mensagem não começa com GC:."""
    achou = PREFIXO.fullmatch(texto)
    if not achou:
        return None
    nome = achou.group(1).lower()
    return resolver(nome, " ".join(achou.group(2).split())[:300], personalizados)  # cabe o link da planilha


class Atalho(commands.Cog):
    grupo = app_commands.Group(name="atalho", description="Configurar abreviações deste servidor.",
                               guild_only=True, default_permissions=discord.Permissions(manage_guild=True))

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, mensagem: discord.Message) -> None:
        if mensagem.author.bot or mensagem.webhook_id or mensagem.guild is None:
            return
        pedido = separar(mensagem.content)
        if pedido is None:
            return
        pedido = separar(mensagem.content, self.bot.registro.atalhos_servidor(mensagem.guild.id))
        preparar(self.bot, mensagem.guild.id)
        nome, resto = pedido
        try:
            await self._atender(mensagem, nome, resto)
        except discord.HTTPException as erro:  # sem permissão de escrever no canal, por exemplo
            log.warning("GC:%s sem resposta no canal %s (%s)", nome, mensagem.channel.id, erro)

    async def _atender(self, mensagem: discord.Message, nome: str, resto: str) -> None:
        async def responder(texto: str | None = None, **extras) -> None:
            return await mensagem.channel.send(texto, reference=mensagem, mention_author=False,
                                        allowed_mentions=discord.AllowedMentions.none(), **extras)

        if nome == "ficha" and limpo(resto) in ("guide", "help", "gm"):
            resto = "mestre" if limpo(resto) == "gm" else "guia"
        if nome == "ajuda" and limpo(resto) in ("abbreviations", "shortcuts"):
            resto = "abreviacoes"
        admin = self.bot.get_cog("Admin")
        if nome == "ajuda" and limpo(resto) in ("abreviacoes", "atalhos"):
            await admin.enviar_ajuda(responder, usuario=mensagem.author, servidor=mensagem.guild.id, abreviacoes=True)
        elif nome == "guia" or (nome == "ajuda" and resto) or (nome == "ficha" and limpo(resto) in ("guia", "ajuda", "mestre")):
            tema = ("mestre" if limpo(resto) == "mestre" else "ficha") if nome == "ficha" else resto
            await self.bot.get_cog("Guias").enviar(responder, tema)
        elif nome in ("", "ajuda"):
            await admin.enviar_ajuda(responder, usuario=mensagem.author, servidor=mensagem.guild.id)
        elif nome == "livro":
            embed, botao = self.bot.get_cog("Regras").painel_do_livro()
            await responder(embed=embed, view=botao)
        elif nome == "ficha":
            ficha = self.bot.get_cog("Ficha")
            if ficha is None:
                await responder(tr('A correção de ficha está fora do ar agora.'))
                return
            anexo = next((a for a in mensagem.attachments if a.filename.lower().endswith(".xlsx")), None)
            link = resto.split()[0] if resto else None
            async with mensagem.channel.typing():
                resposta = await ficha.analisar_fonte(link=None if anexo else link, arquivo=anexo, servidor=mensagem.guild.id)
            await enviar_relatorio(resposta, responder)
        elif nome == "clima":
            embed, aviso = await self.bot.get_cog("ComandoClima").consultar(resto or None)
            if embed is None:
                await responder(aviso)
            else:
                await responder(embed=embed, **_com_arte())
        elif nome == "ping":
            await responder(admin.texto_ping())
        elif nome == "status":
            await responder(await admin.texto_status())
        elif nome in SO_NA_BARRA:
            await responder(tr('Esse é só pela barra, porque a resposta aparece só pra você: {0}').format(self.bot.mencoes.get(nome, '/' + nome)))
        else:
            await responder(tr('Não conheço esse comando. `GC:ajuda` mostra a lista; `GC:guia` explica como usar.'))

    async def _administrador(self, interacao):
        return await self.bot.get_cog("Admin")._administrador(interacao)

    @grupo.command(name="definir", description="Cria ou atualiza um atalho público neste servidor.")
    @app_commands.describe(nome="Só o nome curto, sem GC:. Exemplo: revisar", destino="Comando ou guia que o atalho abre.")
    @app_commands.choices(destino=[app_commands.Choice(name=rotulo, value=alvo) for alvo, rotulo in destinos().items()])
    async def definir(self, interacao: discord.Interaction, nome: str, destino: str):
        if not await self._administrador(interacao):
            return
        try:
            nome = self.bot.registro.definir_atalho(interacao.guild_id, nome, destino)
        except ValueError as erro:
            await interacao.response.send_message(str(erro), ephemeral=True)
            return
        await interacao.response.send_message(tr('Atalho deste servidor: `GC:{0}` faz o mesmo que `GC:{1}`. Ele já aparece na página Abreviações de /ajuda.').format(nome, destino), ephemeral=True,
                                              allowed_mentions=discord.AllowedMentions.none())

    @grupo.command(name="remover", description="Remove um atalho próprio deste servidor.")
    @app_commands.describe(nome="Nome do atalho que você quer retirar, sem GC:.")
    async def remover(self, interacao: discord.Interaction, nome: str):
        if not await self._administrador(interacao):
            return
        try:
            apagado = self.bot.registro.remover_atalho(interacao.guild_id, nome)
        except ValueError as erro:
            await interacao.response.send_message(str(erro), ephemeral=True)
            return
        await interacao.response.send_message(tr('Atalho removido deste servidor.') if apagado else tr('Não há um atalho próprio com esse nome neste servidor.'), ephemeral=True)

    @grupo.command(name="listar", description="Mostra os atalhos próprios deste servidor.")
    async def listar(self, interacao: discord.Interaction):
        if not await self._administrador(interacao):
            return
        extras = self.bot.registro.atalhos_servidor(interacao.guild_id)
        texto = "\n".join(f"`GC:{n}` → `GC:{d}`" for n, d in extras.items()) or tr('Este servidor ainda não tem atalhos próprios.')
        await interacao.response.send_message(texto + tr('\nPara ver também os padrões, abra a página Abreviações de /ajuda.'),
                                              ephemeral=True, allowed_mentions=discord.AllowedMentions.none())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Atalho(bot))
