"""/clima [lugar], /clima_canal e o painel diário de Tóquio. São recursos do bot, sem nome de personagem.

O painel diário vem do bot antigo: sai uma vez por dia, na primeira leitura depois das 6h de Brasília, e a
mesma mensagem é editada quando a condição ou a temperatura mudam. O bot roda em vários servidores, então
cada servidor escolhe o seu canal com /clima_canal (no próprio canal ou passando o canal); o canal, o dia, o
ID da mensagem e o último estado ficam no registro, pra um reinício não postar de novo.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands, tasks

from ..clima import TOQUIO, Clima, acao_painel, lugar_para_consulta
from ..plantao import FUSO
from ..idiomas import preparar
from ..registro import PainelClima

log = logging.getLogger(__name__)

COR = 0xCC0102  # a do painel do bot antigo
ARTE = Path(__file__).resolve().parents[1] / "recursos" / "painel_clima.webp"
ARTE_DE = "hatutaro"  # quem desenhou a imagem do painel; o crédito vai no rodapé, embaixo dela
DESENHO = "p2"        # muda quando o desenho do painel muda, pra o painel do dia ser refeito sem esperar o tempo virar


def arte() -> discord.File | None:
    """A imagem do painel, pra ir anexada na mensagem. Sem o arquivo, o painel sai sem imagem."""
    return discord.File(ARTE, filename=ARTE.name) if ARTE.exists() else None


def painel(clima: Clima, atualizado: str | None = None) -> discord.Embed:
    embed = discord.Embed(title=tr('{0} Clima em {1}').format(clima.emoji, clima.lugar), description=f"**{tr(clima.condicao).capitalize()}**", color=COR)
    embed.set_thumbnail(url=clima.icone)
    embed.add_field(name=tr('🌡️ Temperatura'), value=f"{clima.temperatura} °C")
    embed.add_field(name=tr('🧠 Sensação'), value=f"{clima.sensacao} °C")
    embed.add_field(name=tr('💧 Umidade'), value=f"{clima.umidade}%")
    embed.add_field(name=tr('🍃 Vento'), value=f"{clima.vento_kmh} km/h")
    embed.add_field(name=tr('📊 Mín. e máx.'), value=tr("{0} °C a {1} °C").format(clima.minima,clima.maxima))
    embed.add_field(name=tr('☔ Chuva hoje'), value=tr('sem previsão') if clima.chuva_hoje is None else tr('{0}% de chance').format(clima.chuva_hoje))
    embed.add_field(name=tr('🌅 Nascer do sol'), value=clima.nascer)
    embed.add_field(name=tr('🌇 Pôr do sol'), value=clima.por_do_sol)
    rodape = []
    if ARTE.exists():
        embed.set_image(url=f"attachment://{ARTE.name}")
        rodape.append(tr('Arte: {0}').format(ARTE_DE))
    rodape += [tr('Dados: Open-Meteo'), tr('Leitura das {0} de {1}').format(clima.hora_local, tr('Tóquio') if clima.lugar == TOQUIO.nome else tr('lá'))]
    if atualizado:
        rodape.append(tr('Atualizado às {0} de Brasília').format(atualizado))
    embed.set_footer(text=" • ".join(rodape))
    return embed


def _com_arte() -> dict:
    """O que acompanha o painel num envio: o anexo da imagem, quando existe."""
    anexo = arte()
    return {"file": anexo} if anexo else {}


class ComandoClima(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.painel_diario.start()

    async def cog_unload(self) -> None:
        self.painel_diario.cancel()

    async def consultar(self, lugar: str | None) -> tuple[discord.Embed | None, str | None]:
        """O painel do lugar (Tóquio sem lugar), ou o aviso de por que não saiu."""
        onde = TOQUIO
        if lugar:
            lugar = lugar_para_consulta(lugar)
        if lugar:
            try:
                onde = await self.bot.clima.procurar(lugar)
            except Exception as erro:
                log.warning("clima: falha ao procurar %r (%s)", lugar, erro)
                return None, tr('Não consegui procurar esse lugar agora. Tente de novo daqui a pouco.')
            if onde is None:
                return None, tr('Não achei esse lugar. Tente o nome completo da cidade e acrescente o estado ou país. Exemplo: `GC:clima Belo Horizonte, Brasil`.')
        leitura = await self.bot.clima.agora(onde)
        if leitura is None:
            return None, tr('Não consegui ler o clima agora. Tente de novo daqui a pouco.')
        return painel(leitura), None

    @app_commands.command(name="clima", description="Mostra como está o tempo agora em Tóquio ou em outro lugar.")
    @app_commands.describe(lugar="Cidade ou lugar. Em branco, Tóquio.")
    async def clima(self, interacao: discord.Interaction, lugar: str | None = None) -> None:
        await interacao.response.defer()
        embed, aviso = await self.consultar(lugar)
        if embed is None:
            await interacao.followup.send(aviso)
        else:
            await interacao.followup.send(embed=embed, **_com_arte())

    @app_commands.command(name="clima_canal", description="Escolhe o canal do painel diário de clima deste servidor.")
    @app_commands.describe(canal="Canal do painel. Em branco, o canal em que o comando foi usado.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def clima_canal(self, interacao: discord.Interaction, canal: discord.TextChannel | None = None) -> None:
        destino = canal or interacao.channel
        if not isinstance(destino, discord.TextChannel):
            await interacao.response.send_message(tr('Use num canal de texto, ou escolha um no campo `canal`.'), ephemeral=True)
            return
        permissoes = destino.permissions_for(interacao.guild.me)
        if not (permissoes.send_messages and permissoes.embed_links):
            await interacao.response.send_message(
                tr('Não tenho permissão de enviar mensagens e inserir links em {0}.').format(destino.mention), ephemeral=True)
            return
        self.bot.registro.definir_painel(guild_id=interacao.guild_id, canal_id=destino.id)
        await interacao.response.defer(ephemeral=True)
        feito = await self.atualizar_painel(self.bot.registro.painel(interacao.guild_id), datetime.now(FUSO))
        quando = tr('O de hoje já está lá.') if feito else tr('O próximo sai depois das 6h de Brasília.')
        await interacao.followup.send(tr('Painel diário de clima ligado em {0}. {1}').format(destino.mention, quando), ephemeral=True)

    @app_commands.command(name="clima_canal_desligar", description="Desliga o painel diário de clima deste servidor.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def clima_canal_desligar(self, interacao: discord.Interaction) -> None:
        tinha = self.bot.registro.remover_painel(interacao.guild_id)
        await interacao.response.send_message(
            tr('Painel diário de clima desligado.') if tinha else tr('Este servidor não tinha painel diário de clima.'),
            ephemeral=True)

    async def atualizar_painel(self, config: PainelClima, agora: datetime) -> str | None:
        """Um passo do painel diário de um servidor. Devolve o que fez ("postar", "editar") ou None."""
        leitura = await self.bot.clima.agora()
        if leitura is None:
            return None
        estado = f"{leitura.estado}|{DESENHO}"
        acao = acao_painel(agora, config.dia, config.estado, estado)
        if acao is None:
            return None
        canal = self.bot.get_channel(config.canal_id)
        if canal is None:
            log.warning("clima: canal do painel (%s) não encontrado", config.canal_id)
            return None
        try:
            if acao == "postar":
                mensagem = await canal.send(embed=painel(leitura), **_com_arte())
                dia, mensagem_id = agora.date().isoformat(), mensagem.id
            else:
                mensagem = await canal.fetch_message(config.mensagem_id or 0)
                anexo = arte()  # vai de novo a cada edição: é o que mantém a imagem presa ao painel
                await mensagem.edit(embed=painel(leitura, atualizado=f"{agora:%H:%M}"), attachments=[anexo] if anexo else [])
                dia, mensagem_id = config.dia, config.mensagem_id
        except discord.HTTPException as erro:  # apagaram a mensagem ou faltou permissão: tenta de novo na próxima volta
            log.warning("clima: painel do servidor %s falhou (%s)", config.guild_id, erro)
            return None
        self.bot.registro.marcar_painel(config.guild_id, dia=dia, mensagem_id=mensagem_id, estado=estado)
        return acao

    @tasks.loop(minutes=15)
    async def painel_diario(self) -> None:
        agora = datetime.now(FUSO)
        for config in self.bot.registro.paineis():
            preparar(self.bot,config.guild_id)
            try:
                await self.atualizar_painel(config, agora)
            except Exception:  # um servidor com erro não pode parar os outros nem as próximas voltas
                log.exception("clima: erro no painel do servidor %s", config.guild_id)

    @painel_diario.before_loop
    async def _esperar_conexao(self) -> None:
        await self.bot.wait_until_ready()
        self.semear_paineis()

    def semear_paineis(self) -> None:
        """Canais de painel que vêm do .env (CLIMA_CANAIS). Valem pro servidor que ainda não tem painel; quem já
        escolheu o canal por /clima_canal fica com a escolha dele."""
        for canal_id in self.bot.config.clima_canais:
            canal = self.bot.get_channel(canal_id)
            servidor = getattr(canal, "guild", None)
            if servidor is None:
                log.warning("clima: canal %s do CLIMA_CANAIS não encontrado (o bot está nesse servidor e vê o canal?)", canal_id)
            elif self.bot.registro.painel(servidor.id) is None:
                self.bot.registro.definir_painel(guild_id=servidor.id, canal_id=canal_id)
                log.info("clima: painel diário do servidor %s ligado no canal %s pelo .env", servidor.id, canal_id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ComandoClima(bot))
