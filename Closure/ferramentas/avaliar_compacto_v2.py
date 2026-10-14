"""Prepara triagem de 36 chamadas; sem --executar não chama a API.

Flash original, Flash compacto v2 e Argon compacto v2 nos mesmos 12 cenários.
Execução exige aprovação nova dos textos, quantidade e custo. Não ativa o perfil no bot.
"""
import argparse
import asyncio
import json
import math
from pathlib import Path

from comparar_argon import executar, preparar as preparar_base, gravar
from perfil_compacto_v2 import RAIZ, exportar, preparar

PASTA = RAIZ / "pesquisa/validacao/2026-10-14-compacto-v2"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--executar", action="store_true")
    ap.add_argument("--continuar-apos-interrupcao", action="store_true")
    ap.add_argument("--pasta", type=Path, default=PASTA)
    ap.add_argument("--teto-usd", type=float, default=.40)
    ap.add_argument("--suspender-original", action="store_true", help="após revisão de falhas, não inicia novas chamadas Flash original")
    args = ap.parse_args()
    if not math.isfinite(args.teto_usd) or not 0 < args.teto_usd <= .40:
        ap.error("o teto desta triagem deve ficar entre zero (exclusivo) e US$ 0,40")
    args.limite_chamadas = 36
    args.somente_argon = False
    args.pular_variantes = ("flash-original",) if args.suspender_original else ()
    exportar()
    casos = preparar(preparar_base())
    if len(casos) != 36 or len({c["id"] for c in casos}) != 36:
        raise ValueError("Seleção mudou; revisar o plano antes de executar")
    destino = args.pasta / "casos.json"
    if destino.exists():
        antigos = json.loads(destino.read_text())
        chaves = lambda xs: [(c["id"], c["sha256"], c["alvos"]) for c in xs]
        if chaves(antigos) != chaves(casos):
            raise ValueError("Plano mudou; não misturar baterias")
    else:
        gravar(destino, casos)
    print("12 cenários × 3 variantes = 36 chamadas; mesmos prompts compactos nos dois modelos.")
    if args.suspender_original:
        print("Novas tentativas Flash original suspensas; tentativas anteriores continuam contando no limite.")
    if not args.executar:
        print("Preparação local concluída; nenhuma chamada de API feita.")
        return 0
    return asyncio.run(executar(args, casos))


if __name__ == "__main__":
    raise SystemExit(main())
