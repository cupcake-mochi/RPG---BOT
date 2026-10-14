"""Exporta proposta v2 e prepara sua comparação; não ativa o perfil no bot."""
import copy
import difflib
import hashlib
import json
from closure_bot import perfil_argon as v1
from closure_bot.perfil_compacto_v2 import RAIZ, TROCAS, COMUM, PERSONAS, LEMBRETE, substituir, aplicar

def exportar():
    pasta = RAIZ / "pesquisa/propostas/compacto-v2"
    pasta.mkdir(parents=True, exist_ok=True)
    diffs = []
    for persona in PERSONAS:
        antes = v1.PERSONAS[persona] + "\n\n" + v1.COMUM + "\n\n" + v1.LEMBRETE + "\n"
        depois = PERSONAS[persona] + "\n\n" + COMUM + "\n\n" + LEMBRETE + "\n"
        (pasta / f"{persona}.txt").write_text(depois)
        diffs += list(difflib.unified_diff(antes.splitlines(True), depois.splitlines(True),
                                          fromfile=f"{persona}-v1", tofile=f"{persona}-v2"))
    (pasta / "alteracoes.diff").write_text("".join(diffs))
    return pasta


def hash_entrada(entrada):
    return hashlib.sha256(json.dumps(entrada, ensure_ascii=False).encode()).hexdigest()


def preparar(casos):
    """12 cenários × 3 variantes = 36 tentativas; ordem gira para reduzir efeito temporal."""
    categorias = {"mundo", "genero", "espelhamento", "cuidado", "identidade", "eco_inteiro"}
    saida = []
    for i, caso in enumerate(c for c in casos if c["categoria"] in categorias):
        compacto = aplicar(caso["input"], caso["persona"])
        variantes = [("flash-original", "gemini-3.8-flash", "original", caso["input"]),
                     ("flash-compacto-v2", "gemini-3.8-flash", "compacto-v2", compacto),
                     ("argon-compacto-v2", "gemini-4-argon", "compacto-v2", compacto)]
        variantes = variantes[i % 3:] + variantes[:i % 3]
        for variante, modelo, perfil, entrada in variantes:
            novo = copy.deepcopy(caso)
            novo.update(id=f"{caso['id']}__{variante}", caso_base=caso["id"], variante=variante,
                        alvos=[modelo], perfil=perfil, input=copy.deepcopy(entrada), sha256=hash_entrada(entrada))
            saida.append(novo)
    return saida
