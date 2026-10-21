"""Monta o pedido ao modelo: prompt do card, lorebook, trecho do livro, estado e conversa.

Isso sai da página do site de teste, pela ponte em ferramentas/prompt_do_site: o JavaScript da página roda
dentro do Python (quickjs-ng), então o bot não precisa do Node. É o único ponto do bot que depende da ponte.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from .conversa import Turno
from .midia import AVISO
from .plantao import CLOSURE, KALTSIT
from .atalhos import orientacao

PONTE = Path(__file__).resolve().parents[2] / "ferramentas" / "prompt_do_site"
SIGLA = {KALTSIT: "kal", CLOSURE: "clo"}


def _ponte():
    if str(PONTE) not in sys.path:
        sys.path.insert(0, str(PONTE))
    import site_prompt

    return site_prompt


async def versoes() -> dict:
    """As versões dos cards, do lorebook e da busca que estão na página do site: é com elas que o bot responde."""
    return (await asyncio.to_thread(_ponte().montar, "clo", "oi"))["versoes"]


async def montar(persona: str, mensagem: str, *, nome: str, pronomes: str | None, turnos: list[Turno],
                 falas_anteriores: list[str], estado: dict) -> list[dict]:
    site_prompt = _ponte()
    sigla = SIGLA[persona]
    conversa = [{"de": "user", "nome": t.nome, "texto": t.texto} if t.nome is not None else {"de": "bot", "pers": sigla, "texto": t.texto}
                for t in turnos]
    # fora do laço principal: a primeira chamada carrega a página (meio segundo) e as seguintes levam uns 40 ms
    montado = await asyncio.to_thread(site_prompt.montar, sigla, mensagem, nome=nome, pronomes=pronomes or "", turnos=conversa,
                                      falas_anteriores=falas_anteriores, estado=estado)
    entrada = montado["input"]
    # Metadados antigos acompanham o turno, mas ficam fora da busca do livro.
    for pedido, turno in zip(entrada[1:-1], turnos[-24:]):
        if turno.midia:
            pedido["content"] += "\n\n" + turno.midia
    entrada[0]["content"] += "\n\n" + AVISO
    entrada[0]["content"] += "\n\n" + orientacao(estado.get("atalhos_servidor"))
    if not turnos:
        entrada[0]["content"] += ("\n[Sem histórico recente disponível neste pedido. Se perguntarem onde a conversa parou, "
                                  "diga que não tem esse trecho disponível e peça uma lembrança; "
                                  "isso não prova que nunca houve conversa ou assunto anterior.]")
    return entrada
