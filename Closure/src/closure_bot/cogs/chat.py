"""Conversa: decide se alguém chamou uma personagem, monta o pedido, chama o modelo e envia a resposta."""
from __future__ import annotations

import logging
import re
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from ..clima import contexto_clima
from ..conversa import Turno
from ..modelo import Falhou
from ..plantao import FUSO, MOTIVO_SEGUIMENTO, Decisao, de_plantao, decidir
from ..prompt import montar as montar_prompt
from .atalho import separar as separar_atalho

log = logging.getLogger(__name__)

LIMITE_DO_DISCORD = 1900  # o Discord corta em 2000 caracteres
LIMITE_DA_MENSAGEM = 1500  # o que passa disso numa mensagem de gente não vai pro modelo
CHAMADAS_POR_MINUTO = 8    # por pessoa; acima disso ela fica sem resposta até o minuto passar (cada resposta custa)
SEGUIMENTO = timedelta(minutes=3)  # quanto tempo depois da resposta dela a pessoa pode continuar sem chamar
# mensagem que só reage ("kkk", "ok", "valeu", emoji) fecha a conversa em vez de pedir resposta
SO_REACAO = re.compile(r"^(?:k{2,}|(?:ha|he|hi|rs){2,}|rs|ok+|okay|blz|beleza|vlw|valeu|obg|obrigad[oa]|brigad[oa]|tmj|show|top|entendi|ah|aah+|hm+|nossa|sim|uhum|isso|:\w+:|<a?:\w+:\d+>|[^\w\s]|\s)+$", re.I)
NOME_DO_DONO = "Mizuki"  # a página do site reconhece o dono por este nome; aqui quem garante é o ID


def em_partes(texto: str, limite: int = LIMITE_DO_DISCORD) -> list[str]:
    """Corta uma resposta longa (a explicação de uma habilidade, por exemplo) em mensagens que o Discord aceita.

    Corta no fim de parágrafo; sem parágrafo que caiba, no fim de linha, de frase ou de palavra, nessa ordem."""
    partes = []
    texto = texto.strip()
    while len(texto) > limite:
        trecho = texto[:limite]
        corte = next((i + len(sep) for sep in ("\n\n", "\n", ". ", "? ", "! ", " ") if (i := trecho.rfind(sep)) > limite // 3), limite)
        partes.append(texto[:corte].strip())
        texto = texto[corte:].strip()
    if texto:
        partes.append(texto)
    return partes


@dataclass
class Fio:
    """A última pessoa que ela respondeu num canal: enquanto ninguém mais fala ali, essa pessoa continua sem chamar."""
    persona: str
    autor_id: int
    quando: datetime


class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._recentes: dict[int, deque[datetime]] = {}  # hora das últimas chamadas de cada pessoa
        self._fios: dict[int, Fio] = {}  # por canal (ou tópico); só na memória, reiniciar o bot zera

    def _respondida(self, mensagem: discord.Message) -> tuple[bool, str | None, str | None]:
        """(respondeu a uma mensagem do bot?, de qual personagem era, o texto dela). A personagem vem do registro
        das mensagens enviadas; o texto só vem quando o Discord entrega a mensagem respondida junto."""
        ref = mensagem.reference
        if not ref or not ref.message_id:
            return False, None, None
        persona = self.bot.registro.persona_da_mensagem(ref.message_id)
        original = ref.resolved if isinstance(ref.resolved, discord.Message) else None
        do_bot = bool(persona) or (original is not None and original.author.id == self.bot.user.id)
        return do_bot, persona, (original.content or None) if original is not None and do_bot else None

    def _nome(self, autor) -> str:
        """O nome que vai no pedido. Só o dono, pelo ID, vai como Mizuki; outra pessoa com esse nome não ganha o tratamento dele."""
        if self.bot.config.dono_id and autor.id == self.bot.config.dono_id:
            return NOME_DO_DONO
        nome = " ".join(re.sub(r"[\[\]\r\n]", " ", str(autor.display_name)).split())[:40]
        return "outro Mizuki" if nome.lower() == NOME_DO_DONO.lower() else nome

    def _texto(self, mensagem: discord.Message) -> str:
        """O texto como vai pro modelo e pro registro: sem a menção ao bot e sem ID de ninguém (menção vira @nome)."""
        texto = mensagem.content
        nomes = {m.id: str(getattr(m, "display_name", "alguém")) for m in mensagem.mentions}

        def trocar(achou: re.Match) -> str:
            quem = int(achou.group(1))
            return "" if quem == self.bot.user.id else "@" + nomes.get(quem, "alguém")
        texto = re.sub(r"<@!?(\d+)>", trocar, texto)
        texto = re.sub(r"<@&\d+>", "@cargo", texto)
        texto = re.sub(r"<#\d+>", "#canal", texto)
        texto = re.sub(r"<a?(:\w+:)\d+>", r"\1", texto)  # emoji do servidor: fica só o nome
        return " ".join(texto.split())[:LIMITE_DA_MENSAGEM]

    def _passou_do_limite(self, autor_id: int, agora: datetime) -> bool:
        fila = self._recentes.setdefault(autor_id, deque())
        while fila and agora - fila[0] > timedelta(minutes=1):
            fila.popleft()
        if len(fila) >= CHAMADAS_POR_MINUTO:
            return True
        fila.append(agora)
        return False

    def _seguimento(self, mensagem: discord.Message, agora: datetime) -> Decisao | None:
        """A pessoa que ela acabou de responder segue a conversa sem chamar: mesma pessoa, mesmo canal, pouco tempo
        depois, ninguém falou no meio, e a mensagem não é pra outra pessoa nem só uma reação."""
        fio = self._fios.get(mensagem.channel.id)
        if not fio or fio.autor_id != mensagem.author.id or agora - fio.quando > SEGUIMENTO:
            return None
        if mensagem.reference or any(not m.bot for m in mensagem.mentions):
            return None  # respondeu ou marcou outra pessoa: a conversa é com ela
        if not mensagem.content.strip() or SO_REACAO.match(mensagem.content.strip()):
            self._fios.pop(mensagem.channel.id, None)
            return None
        return Decisao(persona=fio.persona, motivo=MOTIVO_SEGUIMENTO, fora_do_plantao=fio.persona != de_plantao(agora))

    @commands.Cog.listener()
    async def on_message(self, mensagem: discord.Message) -> None:
        # Mensagem de bot ou de webhook (inclusive as nossas) nunca é gatilho; conversa privada fica pra depois.
        if mensagem.author.bot or mensagem.webhook_id or mensagem.guild is None:
            return
        fio = self._fios.get(mensagem.channel.id)
        if fio and fio.autor_id != mensagem.author.id:
            del self._fios[mensagem.channel.id]  # outra pessoa falou no canal: quem conversava com ela volta a chamar
        if mensagem.mention_everyone or mensagem.role_mentions:
            return  # aviso pra todo mundo ou pra um cargo não é conversa com as guias, mesmo citando o nome delas
        if separar_atalho(mensagem.content) is not None:
            return  # "GC:clima" é comando (cogs/atalho.py), não conversa com as guias

        mencionou = self.bot.user in mensagem.mentions
        respondeu, persona_respondida, fala_respondida = self._respondida(mensagem)
        canal_id = getattr(mensagem.channel, "parent_id", None) or mensagem.channel.id
        agora = datetime.now(FUSO)
        seguimento = self._seguimento(mensagem, agora)
        if not self.bot.config.escuta(canal_id) and not (mencionou or respondeu or seguimento):
            # Fora dos canais delas (CANAIS), o nome solto não chama ninguém: "closure" aparece em conversa dos outros.
            # Marcar o bot, responder a uma mensagem dele ou seguir a conversa com ela é falar com ela, em qualquer canal.
            return

        self.bot.vida.ouvir(mensagem.channel.id, agora)  # só a hora, pra saber se o canal está quieto ou cheio
        decisao = decidir(
            mensagem.content,
            agora,
            mencionou_bot=mencionou,
            respondeu_ao_bot=respondeu,
            respondeu_a=persona_respondida,
        ) or seguimento
        if decisao is None:
            return
        if self._passou_do_limite(mensagem.author.id, agora):
            log.info("pessoa %s passou de %d chamadas em um minuto; sem resposta", mensagem.author.id, CHAMADAS_POR_MINUTO)
            return
        texto = self._texto(mensagem)

        self.bot.registro.registrar_gatilho(canal_id=mensagem.channel.id, autor_id=mensagem.author.id,
                                            persona=decisao.persona, motivo=decisao.motivo,
                                            fora_do_plantao=decisao.fora_do_plantao)
        # o texto de quem chamou fica guardado só até a reflexão das 4h30, que tira os fatos e apaga (reflexao.py)
        self.bot.registro.guardar_mensagem_do_dia(message_id=mensagem.id, autor_id=mensagem.author.id,
                                                  persona=decisao.persona, texto=texto)
        atrito = self.bot.vida.chamada(autor_id=mensagem.author.id, persona=decisao.persona, texto=texto, agora=agora)
        log.info("gatilho: %s responde (%s%s%s)", decisao.persona, decisao.motivo,
                 ", fora do plantão" if decisao.fora_do_plantao else "", f", atrito: {atrito}" if atrito else "")
        try:
            async with mensagem.channel.typing():
                await self._responder(mensagem, decisao, agora, texto,
                                      fala_respondida if persona_respondida == decisao.persona else None)
        except Falhou as erro:
            # sem resposta do modelo ela fica calada: frase pronta de erro não é fala dela
            log.warning("sem resposta pra mensagem %s: %s", mensagem.id, str(erro)[:200])
        except Exception:
            log.exception("falha ao responder a mensagem %s", mensagem.id)

    async def _responder(self, mensagem: discord.Message, decisao: Decisao, agora: datetime, texto: str,
                         fala_respondida: str | None = None) -> None:
        bot, persona, canal = self.bot, decisao.persona, mensagem.channel
        nome = self._nome(mensagem.author)
        turnos = bot.conversas.turnos(canal.id, persona, agora)
        if fala_respondida and all(t.texto != fala_respondida for t in turnos):
            # respondeu a uma fala antiga dela, de fora da conversa em andamento: a fala entra na frente, só neste pedido
            turnos = [Turno(agora, fala_respondida[:LIMITE_DO_DISCORD])] + turnos
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
        rota = {}
        if bot.config.usa_argon(canal.id):
            rota["usar_argon"] = True
        resposta = await bot.modelos.responder(entrada, persona=persona, gatilho=decisao.motivo, **rota)
        fala = resposta.texto.strip()
        partes = em_partes(fala)
        if not partes:
            return
        for parte in partes:
            # resposta em várias mensagens entra inteira na memória de falas, uma vez só
            await bot.carteiro.enviar(canal, bot.personas[persona], parte, lembrar=len(partes) == 1)
        # a hora conta do fim da resposta: a pessoa ainda pode estar lendo enquanto ela escrevia
        self._fios[canal.id] = Fio(persona, mensagem.author.id, datetime.now(FUSO))
        if len(partes) > 1:
            bot.registro.guardar_fala(canal_id=canal.id, persona=persona, texto=fala)
        bot.conversas.anotar(canal.id, persona, agora, texto, nome=nome)
        bot.conversas.anotar(canal.id, persona, agora, fala)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
