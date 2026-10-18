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

log = logging.getLogger(__name__)

PREFIXO = re.compile(r"\s*gc\s*:\s*(\w*)\s*(.*)", re.IGNORECASE | re.DOTALL)
SO_NA_BARRA = {"meus_dados", "meus_pronomes", "meu_fato", "esquecer_fato", "apagar_meus_dados",
               "clima_canal", "clima_canal_desligar", "teste_webhook"}
OUTROS_NOMES = {"help": "ajuda", "comandos": "ajuda", "tempo": "clima", "sistema": "livro", "pdf": "livro",
                "analisar": "ficha", "analise": "ficha"}


def separar(texto: str) -> tuple[str, str] | None:
    """("clima", "Quioto") pra "GC: clima Quioto"; None se a mensagem não começa com GC:."""
    achou = PREFIXO.fullmatch(texto)
    if not achou:
        return None
    nome = achou.group(1).lower()
    return OUTROS_NOMES.get(nome, nome), " ".join(achou.group(2).split())[:300]  # cabe o link da planilha


class Atalho(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, mensagem: discord.Message) -> None:
        if mensagem.author.bot or mensagem.webhook_id or mensagem.guild is None:
            return
        pedido = separar(mensagem.content)
        if pedido is None:
            return
        nome, resto = pedido
        try:
            await self._atender(mensagem, nome, resto)
        except discord.HTTPException as erro:  # sem permissão de escrever no canal, por exemplo
            log.warning("GC:%s sem resposta no canal %s (%s)", nome, mensagem.channel.id, erro)

    async def _atender(self, mensagem: discord.Message, nome: str, resto: str) -> None:
        async def responder(texto: str | None = None, **extras) -> None:
            return await mensagem.channel.send(texto, reference=mensagem, mention_author=False,
                                        allowed_mentions=discord.AllowedMentions.none(), **extras)

        admin = self.bot.get_cog("Admin")
        if nome in ("", "ajuda"):
            dono = mensagem.author.id == self.bot.config.dono_id
            permissoes = getattr(mensagem.author, "guild_permissions", None)
            await responder(embed=admin.painel_de_ajuda(cuida_do_servidor=dono or bool(permissoes and permissoes.manage_guild), dono=dono))
        elif nome == "livro":
            embed, botao = self.bot.get_cog("Regras").painel_do_livro()
            await responder(embed=embed, view=botao)
        elif nome == "ficha":
            ficha = self.bot.get_cog("Ficha")
            if ficha is None:
                await responder("A correção de ficha está fora do ar agora.")
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
            await responder(f"Esse é só pela barra, porque a resposta aparece só pra você: {self.bot.mencoes.get(nome, '/' + nome)}")
        else:
            await responder("Não conheço esse. `GC:ajuda` mostra a lista.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Atalho(bot))
