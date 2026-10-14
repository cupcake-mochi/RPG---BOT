"""Gera a proposta revisável usada na bateria do Argon compacto."""
import copy
import hashlib
import json
from closure_bot.perfil_argon import RAIZ, VERSOES, COMUM, PERSONAS, LEMBRETE, aplicar

def preparar_proposta(casos):
    pasta = RAIZ / "pesquisa/propostas/argon-compacto-v1"
    pasta.mkdir(parents=True, exist_ok=True)
    for persona in PERSONAS:
        (pasta / f"{persona}.txt").write_text(PERSONAS[persona] + "\n\n" + COMUM + "\n\n" + LEMBRETE + "\n")
    saida = copy.deepcopy(casos)
    for caso in saida:
        caso["input_argon"] = aplicar(caso["input"], caso["persona"])
        caso["perfil_argon"] = "compacto-v1-proposta"
        caso["sha256"] = hashlib.sha256(json.dumps([caso["input"], caso["input_argon"]], ensure_ascii=False).encode()).hexdigest()
    return saida
