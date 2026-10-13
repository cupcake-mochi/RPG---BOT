"""Monta o pedido ao modelo: prompt do card, lorebook, trecho do livro, estado e conversa.

Hoje isso sai da página do site de teste, pela ponte em ferramentas/prompt_do_site, que roda no Node. É o único
ponto do bot que depende dela: se a busca ganhar versão em Python, troca-se só este arquivo.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from .conversa import Turno
from .plantao import CLOSURE, KALTSIT

PONTE = Path(__file__).resolve().parents[2] / "ferramentas" / "prompt_do_site"
SIGLA = {KALTSIT: "kal", CLOSURE: "clo"}


async def montar(persona: str, mensagem: str, *, nome: str, pronomes: str | None, turnos: list[Turno],
                 falas_anteriores: list[str], estado: dict) -> list[dict]:
    if str(PONTE) not in sys.path:
        sys.path.insert(0, str(PONTE))
    import site_prompt

    sigla = SIGLA[persona]
    conversa = [{"de": "user", "nome": t.nome, "texto": t.texto} if t.nome is not None else {"de": "bot", "pers": sigla, "texto": t.texto}
                for t in turnos]
    # a ponte chama o Node e espera; fora do laço principal, pra não travar o bot enquanto isso
    montado = await asyncio.to_thread(site_prompt.montar, sigla, mensagem, nome=nome, pronomes=pronomes or "", turnos=conversa,
                                      falas_anteriores=falas_anteriores, estado=estado)
    return montado["input"]
