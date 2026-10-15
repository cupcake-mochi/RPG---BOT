"""Reflexão diária: tira das mensagens do dia os fatos que valem lembrar de cada pessoa, e apaga o texto.

Desenho: dados/personagem/kaltsit/vida.md, seção 7, com duas mudanças do Mizuki em 13/10/2026: o fato pode ser
qualquer coisa sobre a pessoa, não só do jogo, e a pessoa também pode escrever os dela por comando.

O que fica de fora não é escolha de estilo. A política de desenvolvedor do Discord (regra 16) proíbe guardar
saúde, dinheiro e outros dados sensíveis, e traçar a relação de uma pessoa com as outras. Por isso a peneira
roda duas vezes: no pedido ao modelo e de novo aqui no código, antes de gravar.

O pedido leva mensagem de várias pessoas, então só vai por provedor pago (modelo.py, `so_pagos`).
"""
from __future__ import annotations

import json
import logging
import re
import unicodedata
from dataclasses import replace

from .modelo import Falhou, Modelos
from .registro import FATOS_MAX, MensagemDoDia, Registro

log = logging.getLogger(__name__)

FATO_MAX = 120  # caracteres
MENSAGENS_POR_LOTE = 400

# Assunto que não entra na ficha, por regra do Discord ou por ser dado sensível na LGPD. Radicais, sem acento.
PROIBIDO = re.compile(
    # começo de palavra
    r"\b(?:doenc|doente|diagnos|remedio|medicament|depress|ansiedade|terapi|psicolog|psiquiatr|hospital|cirurgi|"
    r"autis|sindrome|transtorno|cancer|diabet|gravid|deficien|suicid|"
    r"salario|divida|devendo|emprestimo|cartao de credito|conta bancaria|"
    r"religi|igreja|evangelic|catolic|umbanda|candomble|"
    r"politic|partido|vot(?:a|ou|ei) (?:em|no|na)|esquerdista|de esquerda|de direita|direitista|"
    r"lesbic|bissexual|transgenero|transexual|heterossexual|homossexual|sexual|namor|casad[oa]|solteir|"
    r"e (?:negr[oa]|pard[oa]|branc[oa]|indigena)\b|etnia|"
    r"endereco|mora (?:em|no|na)|telefone|whatsapp|e-?mail|"
    r"\d{1,2} anos|menor de idade)"
    # palavra inteira
    r"|\b(?:tdah|pix|cpf|rg|gay|bi|trans|hetero|ateu|ateia|idade)\b", re.IGNORECASE)

INSTRUCAO = """Você recebe mensagens que pessoas de um servidor de Discord de RPG de mesa mandaram hoje para a guia do servidor.
Sua tarefa: tirar fatos duradouros sobre QUEM ESCREVEU, que valha a pena a guia lembrar daqui a semanas.

Entra: o que a pessoa disse de si mesma. Personagem que joga, mesa, mestre, gostos, hobbies, jogos, o que estuda ou faz em linhas gerais, jeito que prefere ser respondida, dúvida que ela repete.
Não entra, nunca: saúde física ou mental, dinheiro, religião, política, orientação sexual, relacionamento, cor ou etnia, idade, endereço, contato, documento. Nada sobre outra pessoa. Nada que ela não tenha dito com as próprias palavras. Humor do momento, pergunta de regra avulsa, cumprimento e piada não são fato.

Cada fato é uma frase curta em português, sem o nome da pessoa, começando pelo verbo ("joga com um Bastião chamado Ren", "prefere resposta curta"). No máximo 3 fatos por pessoa. Não repita fato que ela já tem. Se não houver nada que valha, devolva a lista vazia: é o caso mais comum.

Responda só com JSON, sem texto em volta: [{"autor": <número do autor>, "mensagem": <número da mensagem de onde saiu>, "fato": "<frase>"}]"""


def _plano(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def fato_permitido(texto: str) -> bool:
    """A peneira do código: tamanho e assunto. Vale pro fato que vem do modelo e pro que a pessoa escreve por comando."""
    limpo = " ".join(texto.split())
    return 3 <= len(limpo) <= FATO_MAX and not PROIBIDO.search(_plano(limpo))


def _ordem(mensagens: list[MensagemDoDia]) -> tuple[dict[int, int], dict[int, int]]:
    """Número de ordem de cada autor e de cada mensagem no lote. É o que vai no pedido: o ID do Discord não sai daqui."""
    autores = {autor: n for n, autor in enumerate(dict.fromkeys(m.autor_id for m in mensagens), 1)}
    return autores, {m.message_id: n for n, m in enumerate(mensagens, 1)}


def montar_pedido(mensagens: list[MensagemDoDia], fatos_atuais: dict[int, tuple[str, ...]]) -> list[dict]:
    autores, numeros = _ordem(mensagens)
    linhas = ["MENSAGENS DE HOJE"]
    linhas += [f"mensagem {numeros[m.message_id]} | autor {autores[m.autor_id]} | {' '.join(m.texto.split())[:500]}" for m in mensagens]
    linhas.append("\nFATOS QUE CADA AUTOR JÁ TEM")
    linhas += [f"autor {n}: {'; '.join(fatos_atuais.get(autor, ())) or 'nenhum'}" for autor, n in autores.items()]
    # a primeira mensagem vira a instrução de sistema (modelo.montar_corpo); o lote vai na segunda
    return [{"role": "user", "content": INSTRUCAO}, {"role": "user", "content": "\n".join(linhas)}]


def conferir(saida: str, mensagens: list[MensagemDoDia], fatos_atuais: dict[int, tuple[str, ...]]) -> dict[int, list[str]]:
    """Lê o JSON do modelo e deixa passar só o fato que cita uma mensagem da própria pessoa, passa na peneira e é novo."""
    achado = re.search(r"\[.*\]", saida, re.DOTALL)
    try:
        itens = json.loads(achado.group(0)) if achado else []
    except json.JSONDecodeError:
        log.warning("reflexão: o modelo não devolveu JSON")
        return {}
    autores, numeros = _ordem(mensagens)
    autor_de = {n: autor for autor, n in autores.items()}
    dono = {numeros[m.message_id]: m.autor_id for m in mensagens}
    novos: dict[int, list[str]] = {}
    for item in itens if isinstance(itens, list) else []:
        try:
            autor, mensagem, fato = autor_de.get(int(item["autor"])), int(item["mensagem"]), " ".join(str(item["fato"]).split())
        except (KeyError, TypeError, ValueError):
            continue
        ja_tem = {_plano(f) for f in fatos_atuais.get(autor, ())} | {_plano(f) for f in novos.get(autor, [])}
        if autor is None or dono.get(mensagem) != autor or not fato_permitido(fato) or _plano(fato) in ja_tem or len(novos.get(autor, [])) >= 3:
            continue
        novos.setdefault(autor, []).append(fato)
    return novos


async def refletir(registro: Registro, modelos: Modelos) -> dict[int, list[str]]:
    """Roda a reflexão sobre as mensagens guardadas. O texto delas é apagado no fim, tenha dado certo ou não:
    se o modelo falhar, o dia se perde, mas mensagem de gente não fica parada no banco."""
    mensagens = registro.mensagens_do_dia()[:MENSAGENS_POR_LOTE]
    if not mensagens:
        return {}
    autores = sorted({m.autor_id for m in mensagens})
    fatos_atuais = {autor: registro.ficha(autor).fatos for autor in autores}
    novos: dict[int, list[str]] = {}
    with registro.proteger_dados(autores) as leitura:
        try:
            resposta = await modelos.responder(montar_pedido(mensagens, fatos_atuais), gatilho="reflexao", so_pagos=True)
            novos = {autor: fatos for autor, fatos in conferir(resposta.texto, mensagens, fatos_atuais).items()
                     if autor not in leitura.apagados}
            for autor, fatos in novos.items():
                ficha = registro.ficha(autor)
                registro.gravar_ficha(autor, replace(ficha, fatos=(ficha.fatos + tuple(fatos))[-FATOS_MAX:]))
        except Falhou as erro:
            log.warning("reflexão: o modelo falhou (%s); as mensagens do dia foram apagadas sem virar fato", str(erro)[:200])
        finally:
            registro.apagar_mensagens_do_dia([m.message_id for m in mensagens])
    log.info("reflexão: %d mensagens de %d pessoas, %d fatos novos", len(mensagens), len(autores), sum(map(len, novos.values())))
    return novos
