"""Conversa: decide se alguém chamou uma personagem, monta o pedido, chama o modelo e envia a resposta."""
from __future__ import annotations

import logging
from datetime import datetime

import discord
from discord.ext import commands

from ..clima import contexto_clima
from ..modelo import Falhou
from ..plantao import FUSO, Decisao, decidir
from ..prompt import montar as montar_prompt

log = logging.getLogger(__name__)

LIMITE_DO_DISCORD = 1900  # o Discord corta em 2000 caracteres
NOME_DO_DONO = "Mizuki"  # a página do site reconhece o dono por este nome; aqui quem garante é o ID


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _respondeu_ao_bot(self, mensagem: discord.Message) -> bool:
        ref = mensagem.reference
        if not ref or not ref.message_id:
            return False
        if self.bot.registro.persona_da_mensagem(ref.message_id):
            return True
        original = ref.resolved
        return isinstance(original, discord.Message) and original.author.id == self.bot.user.id

    def _nome(self, autor) -> str:
        """O nome que vai no pedido. Só o dono, pelo ID, vai como Mizuki; outra pessoa com esse nome não ganha o tratamento dele."""
        if self.bot.config.dono_id and autor.id == self.bot.config.dono_id:
            return NOME_DO_DONO
        nome = str(autor.display_name).strip()[:40]
        return "outro Mizuki" if nome.lower() == NOME_DO_DONO.lower() else nome

    @commands.Cog.listener()
    async def on_message(self, mensagem: discord.Message) -> None:
        # Mensagem de bot ou de webhook (inclusive as nossas) nunca é gatilho; conversa privada fica pra depois.
        if mensagem.author.bot or mensagem.webhook_id or mensagem.guild is None:
            return
        canal_id = getattr(mensagem.channel, "parent_id", None) or mensagem.channel.id
        if not self.bot.config.escuta(canal_id):
            return

        agora = datetime.now(FUSO)
        self.bot.vida.ouvir(mensagem.channel.id, agora)  # só a hora, pra saber se o canal está quieto ou cheio
        decisao = decidir(
            mensagem.content,
            agora,
            mencionou_bot=self.bot.user in mensagem.mentions,
            respondeu_ao_bot=self._respondeu_ao_bot(mensagem),
        )
        if decisao is None:
            return

        self.bot.registro.registrar_gatilho(canal_id=mensagem.channel.id, autor_id=mensagem.author.id,
                                            persona=decisao.persona, motivo=decisao.motivo,
                                            fora_do_plantao=decisao.fora_do_plantao)
        # o texto de quem chamou fica guardado só até a reflexão das 4h30, que tira os fatos e apaga (reflexao.py)
        self.bot.registro.guardar_mensagem_do_dia(message_id=mensagem.id, autor_id=mensagem.author.id,
                                                  persona=decisao.persona, texto=mensagem.content)
        atrito = self.bot.vida.chamada(autor_id=mensagem.author.id, persona=decisao.persona, texto=mensagem.content, agora=agora)
        log.info("gatilho: %s responde (%s%s%s)", decisao.persona, decisao.motivo,
                 ", fora do plantão" if decisao.fora_do_plantao else "", f", atrito: {atrito}" if atrito else "")
        try:
            async with mensagem.channel.typing():
                await self._responder(mensagem, decisao, agora)
        except Falhou as erro:
            # sem resposta do modelo ela fica calada: frase pronta de erro não é fala dela
            log.warning("sem resposta pra mensagem %s: %s", mensagem.id, str(erro)[:200])
        except Exception:
            log.exception("falha ao responder a mensagem %s", mensagem.id)

    async def _responder(self, mensagem: discord.Message, decisao: Decisao, agora: datetime) -> None:
        bot, persona, canal, texto = self.bot, decisao.persona, mensagem.channel, mensagem.content
        nome = self._nome(mensagem.author)
        turnos = bot.conversas.turnos(canal.id, persona, agora)
        estado = bot.vida.estado(persona=persona, canal_id=canal.id, autor_id=mensagem.author.id, nome=nome, agora=agora, texto=texto)
        para_a_ponte = estado.para_a_ponte()
        clima = await contexto_clima(bot.clima, texto)
        if clima:  # a linha de clima entra antes do bloco de estado, só quando a mensagem puxa o assunto
            para_a_ponte["bloco"] = f"{clima}\n\n{para_a_ponte['bloco']}"
        # falas de outras conversas no canal; as desta já vão em `turnos`, e contá-las duas vezes viraria aviso falso de repetição
        desta = {t.texto for t in turnos if t.nome is None}
        anteriores = [f for f in bot.registro.ultimas_falas(canal_id=canal.id, persona=persona, agora=agora) if f not in desta]
        entrada = await montar_prompt(persona, texto, nome=nome, pronomes=estado.pronomes, turnos=turnos,
                                      falas_anteriores=anteriores, estado=para_a_ponte)
        resposta = await bot.modelos.responder(entrada, persona=persona, gatilho=decisao.motivo)
        fala = resposta.texto.strip()[:LIMITE_DO_DISCORD]
        if not fala:
            return
        await bot.carteiro.enviar(canal, bot.personas[persona], fala)
        bot.conversas.anotar(canal.id, persona, agora, texto, nome=nome)
        bot.conversas.anotar(canal.id, persona, agora, fala)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
