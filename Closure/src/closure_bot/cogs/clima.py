"""/clima [lugar], /clima_canal e o painel diário de Tóquio. São recursos do bot, sem nome de personagem.

O painel diário vem do bot antigo: sai uma vez por dia, na primeira leitura depois das 6h de Brasília, e a
mesma mensagem é editada quando a condição ou a temperatura mudam. O bot roda em vários servidores, então
cada servidor escolhe o seu canal com /clima_canal (no próprio canal ou passando o canal); o canal, o dia, o
ID da mensagem e o último estado ficam no registro, pra um reinício não postar de novo.
"""
from __future__ import annotations

import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from ..clima import TOQUIO, Clima, acao_painel
from ..plantao import FUSO
from ..registro import PainelClima

log = logging.getLogger(__name__)

COR = 0xCC0102  # a do painel do bot antigo


def painel(clima: Clima, atualizado: str | None = None) -> discord.Embed:
    embed = discord.Embed(title=f"{clima.lugar} agora", description=clima.condicao.capitalize(), color=COR)
    embed.add_field(name="Temperatura", value=f"{clima.temperatura} °C")
    embed.add_field(name="Sensação", value=f"{clima.sensacao} °C")
    embed.add_field(name="Umidade", value=f"{clima.umidade}%")
    embed.add_field(name="Vento", value=f"{clima.vento_kmh} km/h")
    embed.add_field(name="Hoje", value=f"{clima.minima} °C a {clima.maxima} °C")
    embed.add_field(name="Sol", value=f"{clima.nascer} às {clima.por_do_sol}")
    rodape = f"Leitura das {clima.hora_local} de lá. Dados: Open-Meteo"
    if atualizado:
        rodape += f". Atualizado às {atualizado} de Brasília"
    embed.set_footer(text=rodape)
    return embed


class ComandoClima(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.painel_diario.start()

    async def cog_unload(self) -> None:
        self.painel_diario.cancel()

    @app_commands.command(name="clima", description="Mostra como está o tempo agora em Tóquio ou em outro lugar.")
    @app_commands.describe(lugar="Cidade ou lugar. Em branco, Tóquio.")
    async def clima(self, interacao: discord.Interaction, lugar: str | None = None) -> None:
        await interacao.response.defer()
        onde = TOQUIO
        if lugar:
            try:
                onde = await self.bot.clima.procurar(lugar)
            except Exception as erro:
                log.warning("clima: falha ao procurar %r (%s)", lugar, erro)
                await interacao.followup.send("Não consegui procurar esse lugar agora. Tente de novo daqui a pouco.")
                return
            if onde is None:
                await interacao.followup.send("Não achei esse lugar. Tente o nome da cidade.")
                return
        leitura = await self.bot.clima.agora(onde)
        if leitura is None:
            await interacao.followup.send("Não consegui ler o clima agora. Tente de novo daqui a pouco.")
            return
        await interacao.followup.send(embed=painel(leitura))

    @app_commands.command(name="clima_canal", description="Escolhe o canal do painel diário de clima deste servidor.")
    @app_commands.describe(canal="Canal do painel. Em branco, o canal em que o comando foi usado.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def clima_canal(self, interacao: discord.Interaction, canal: discord.TextChannel | None = None) -> None:
        destino = canal or interacao.channel
        if not isinstance(destino, discord.TextChannel):
            await interacao.response.send_message("Use num canal de texto, ou escolha um no campo `canal`.", ephemeral=True)
            return
        permissoes = destino.permissions_for(interacao.guild.me)
        if not (permissoes.send_messages and permissoes.embed_links):
            await interacao.response.send_message(
                f"Não tenho permissão de enviar mensagens e inserir links em {destino.mention}.", ephemeral=True)
            return
        self.bot.registro.definir_painel(guild_id=interacao.guild_id, canal_id=destino.id)
        await interacao.response.defer(ephemeral=True)
        feito = await self.atualizar_painel(self.bot.registro.painel(interacao.guild_id), datetime.now(FUSO))
        quando = "O de hoje já está lá." if feito else "O próximo sai depois das 6h de Brasília."
        await interacao.followup.send(f"Painel diário de clima ligado em {destino.mention}. {quando}", ephemeral=True)

    @app_commands.command(name="clima_canal_desligar", description="Desliga o painel diário de clima deste servidor.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def clima_canal_desligar(self, interacao: discord.Interaction) -> None:
        tinha = self.bot.registro.remover_painel(interacao.guild_id)
        await interacao.response.send_message(
            "Painel diário de clima desligado." if tinha else "Este servidor não tinha painel diário de clima.",
            ephemeral=True)

    async def atualizar_painel(self, config: PainelClima, agora: datetime) -> str | None:
        """Um passo do painel diário de um servidor. Devolve o que fez ("postar", "editar") ou None."""
        leitura = await self.bot.clima.agora()
        if leitura is None:
            return None
        acao = acao_painel(agora, config.dia, config.estado, leitura.estado)
        if acao is None:
            return None
        canal = self.bot.get_channel(config.canal_id)
        if canal is None:
            log.warning("clima: canal do painel (%s) não encontrado", config.canal_id)
            return None
        try:
            if acao == "postar":
                mensagem = await canal.send(embed=painel(leitura))
                dia, mensagem_id = agora.date().isoformat(), mensagem.id
            else:
                mensagem = await canal.fetch_message(config.mensagem_id or 0)
                await mensagem.edit(embed=painel(leitura, atualizado=f"{agora:%H:%M}"))
                dia, mensagem_id = config.dia, config.mensagem_id
        except discord.HTTPException as erro:  # apagaram a mensagem ou faltou permissão: tenta de novo na próxima volta
            log.warning("clima: painel do servidor %s falhou (%s)", config.guild_id, erro)
            return None
        self.bot.registro.marcar_painel(config.guild_id, dia=dia, mensagem_id=mensagem_id, estado=leitura.estado)
        return acao

    @tasks.loop(minutes=15)
    async def painel_diario(self) -> None:
        agora = datetime.now(FUSO)
        for config in self.bot.registro.paineis():
            try:
                await self.atualizar_painel(config, agora)
            except Exception:  # um servidor com erro não pode parar os outros nem as próximas voltas
                log.exception("clima: erro no painel do servidor %s", config.guild_id)

    @painel_diario.before_loop
    async def _esperar_conexao(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ComandoClima(bot))
