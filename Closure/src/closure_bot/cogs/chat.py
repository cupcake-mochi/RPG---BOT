"""Conversa: decide se alguém chamou uma personagem, monta o pedido, chama o modelo e envia a resposta."""
from __future__ import annotations

import logging
import re
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from ..clima import contexto_clima, pergunta_clima
from ..conversa import Turno
from ..modelo import Falhou
from ..plantao import FUSO, MOTIVO_SEGUIMENTO, Decisao, de_plantao, decidir
from ..prompt import montar as montar_prompt
from ..conteudo_adulto import aplicar as aplicar_preferencia_adulta
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

    def _cargo_dela(self, cargo) -> bool:
        """O cargo que o Discord cria pro bot ao entrar no servidor (o "Guias do Ciclo"): marcar ele é marcar o bot."""
        proprio = getattr(getattr(cargo, "guild", None), "self_role", None)
        dono_do_cargo = getattr(getattr(cargo, "tags", None), "bot_id", None)
        return (proprio is not None and getattr(proprio, "id", None) == cargo.id) or dono_do_cargo == self.bot.user.id

    def _texto(self, mensagem: discord.Message) -> str:
        """O texto como vai pro modelo e pro registro: sem a menção ao bot e sem ID de ninguém (menção vira @nome)."""
        texto = mensagem.content
        nomes = {m.id: str(getattr(m, "display_name", "alguém")) for m in mensagem.mentions}

        def trocar(achou: re.Match) -> str:
            quem = int(achou.group(1))
            return "" if quem == self.bot.user.id else "@" + nomes.get(quem, "alguém")
        texto = re.sub(r"<@!?(\d+)>", trocar, texto)
        cargos_dela = {c.id for c in mensagem.role_mentions if self._cargo_dela(c)}
        texto = re.sub(r"<@&(\d+)>", lambda achou: "" if int(achou.group(1)) in cargos_dela else "@cargo", texto)
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
        tem_anexo = bool(list(getattr(mensagem, "attachments", ()) or ()))
        if (not mensagem.content.strip() and not tem_anexo) or SO_REACAO.match(mensagem.content.strip()):
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
        cargo_dela = any(self._cargo_dela(c) for c in mensagem.role_mentions)
        if mensagem.mention_everyone or any(not self._cargo_dela(c) for c in mensagem.role_mentions):
            # aviso pra todo mundo ou pra outro cargo não é conversa com as guias, mesmo citando o nome delas ou o
            # cargo delas junto. Só o cargo do próprio bot vale como marcar o bot.
            return
        if separar_atalho(mensagem.content) is not None:
            return  # "GC:clima" é comando (cogs/atalho.py), não conversa com as guias

        mencionou = self.bot.user in mensagem.mentions or cargo_dela
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
            await self._responder(mensagem, decisao, agora, texto,
                                  fala_respondida if persona_respondida == decisao.persona else None)
        except Falhou as erro:
            # sem resposta do modelo ela fica calada: frase pronta de erro não é fala dela
            log.warning("sem resposta pra mensagem %s: %s", mensagem.id, str(erro)[:200])
        except Exception:
            log.exception("falha ao responder a mensagem %s", mensagem.id)

    async def _responder(self, mensagem: discord.Message, decisao: Decisao, agora: datetime, texto: str,
                         fala_respondida: str | None = None) -> None:
        autores = self.bot.registro.autores_conversa(mensagem.channel.id, decisao.persona)
        autores.add(mensagem.author.id)
        with self.bot.registro.proteger_dados(autores) as leitura:
            async with mensagem.channel.typing():
                if not leitura.apagados:
                    await self._responder_com_leitura(mensagem, decisao, agora, texto, fala_respondida, leitura)

    async def _responder_com_leitura(self, mensagem, decisao, agora, texto, fala_respondida, leitura):
        bot, persona, canal = self.bot, decisao.persona, mensagem.channel
        nome = self._nome(mensagem.author)
        # Outra conversa pode ter terminado enquanto o indicador de digitação
        # era enviado. Inclua os autores exatamente antes de ler seus dados.
        leitura.autores |= bot.registro.autores_conversa(canal.id, persona)
        turnos = bot.conversas.turnos(canal.id, persona, agora)
        if fala_respondida and all(t.texto != fala_respondida for t in turnos):
            # respondeu a uma fala antiga dela, de fora da conversa em andamento: a fala entra na frente, só neste pedido
            turnos = [Turno(agora, fala_respondida[:LIMITE_DO_DISCORD])] + turnos
        estado = bot.vida.estado(persona=persona, canal_id=canal.id, autor_id=mensagem.author.id, nome=nome, agora=agora, texto=texto)
        para_a_ponte = estado.para_a_ponte()
        para_a_ponte["atalhos_servidor"] = bot.registro.atalhos_servidor(mensagem.guild.id)
        # Reconstituir só a sequência meteorológica ainda presente no histórico.
        # Uma fala de outro assunto encerra a sequência; não puxa clima antigo.
        anterior = None
        for turno in turnos:
            if turno.nome is not None:
                anterior = pergunta_clima(turno.texto, anterior)
        clima = await contexto_clima(bot.clima, texto, anterior)
        if leitura.apagados:
            return
        if clima:  # a linha de clima entra antes do bloco de estado, só quando a mensagem puxa o assunto
            para_a_ponte["bloco"] = f"{clima}\n\n{para_a_ponte['bloco']}"
        # falas de outras conversas no canal; as desta já vão em `turnos`, e contá-las duas vezes viraria aviso falso de repetição
        desta = {t.texto for t in turnos if t.nome is None}
        leitura.autores |= bot.registro.autores_conversa(canal.id, persona)
        anteriores = [f for f in bot.registro.ultimas_falas(canal_id=canal.id, persona=persona, agora=agora) if f not in desta]
        inicio_prompt = time.monotonic()
        entrada = await montar_prompt(persona, texto, nome=nome, pronomes=estado.pronomes, turnos=turnos,
                                      falas_anteriores=anteriores, estado=para_a_ponte)
        if leitura.apagados:
            return
        inicio_preparo = time.monotonic()
        preparo = await bot.anexos.contexto(mensagem)
        if leitura.apagados:
            return
        midia = await bot.midias.contexto(mensagem, texto, incluir_anexos=not (preparo.partes or preparo.silencio),
                                        links_analisados=preparo.links_analisados)
        if leitura.apagados:
            return
        if midia:
            entrada[-1]["content"] += "\n\n" + midia
        preparo.aplicar(entrada)
        aplicar_preferencia_adulta(entrada, mensagem, bot.registro)
        rota = {}
        if bot.config.usa_argon(canal.id):
            rota["usar_argon"] = True
        fala = preparo.resposta_local(texto)
        inicio_modelo = time.monotonic()
        if fala is None:
            resposta = await bot.modelos.responder(entrada, persona=persona, gatilho=decisao.motivo, **rota)
            if leitura.apagados:
                return
            fala = resposta.texto.strip()
        if preparo.partes or preparo.silencio:
            fim = time.monotonic()
            log.info('mídia: prompt_ms=%d preparo_ms=%d modelo_ms=%d total_ms=%d',
                     (inicio_preparo - inicio_prompt) * 1000, (inicio_modelo - inicio_preparo) * 1000,
                     (fim - inicio_modelo) * 1000, (fim - inicio_prompt) * 1000)
        partes = em_partes(fala)
        if not partes:
            return
        for parte in partes:
            # Grave só depois de confirmar que ninguém apagou os dados durante
            # o envio. Uma mensagem já em trânsito não pode ser desfeita aqui.
            await bot.carteiro.enviar(canal, bot.personas[persona], parte, lembrar=False)
            if leitura.apagados:
                return
        # a hora conta do fim da resposta: a pessoa ainda pode estar lendo enquanto ela escrevia
        self._fios[canal.id] = Fio(persona, mensagem.author.id, datetime.now(FUSO))
        bot.registro.guardar_fala(canal_id=canal.id, persona=persona, texto=fala)
        bot.conversas.anotar(canal.id, persona, agora, texto, nome=nome,
                             autor_id=mensagem.author.id, midia='\n'.join(filter(None, [midia, preparo.historico])))
        bot.conversas.anotar(canal.id, persona, agora, fala, autor_id=mensagem.author.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Chat(bot))
