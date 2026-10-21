"""Leitura do que o bot não é dono: o manifesto das regras e os cards das personagens.

Nada aqui escreve em dados/. O manifesto é gerado por ferramentas/sincronizar.py e os cards pelos geradores.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .plantao import CLOSURE, KALTSIT


@dataclass(frozen=True)
class Persona:
    chave: str
    nome: str
    versao: str
    avatar_url: str | None


def ler_manifesto(dados: Path) -> dict:
    return json.loads((dados / "sistema" / "MANIFESTO.json").read_text(encoding="utf-8"))


def resumo_manifesto(manifesto: dict, idioma="pt-BR") -> str:
    edicao = manifesto['edicao_livro']
    if idioma == "en":
        return (f"{manifesto['sistema']} {manifesto['versao_sistema']}, rulebook version: {edicao}, "
                f"{manifesto['blocos']} reference excerpts")
    return (f"{manifesto['sistema']} {manifesto['versao_sistema']}, versão do livro: {edicao}, "
            f"{manifesto['blocos']} trechos de referência")


def carregar_personas(dados: Path, avatares: dict[str, str | None]) -> dict[str, Persona]:
    personas = {}
    for chave in (KALTSIT, CLOSURE):
        card = json.loads((dados / "personagem" / chave / "card.json").read_text(encoding="utf-8"))["data"]
        personas[chave] = Persona(chave=chave, nome=card["name"], versao=card.get("character_version", "?"),
                                  avatar_url=avatares.get(chave))
    return personas
