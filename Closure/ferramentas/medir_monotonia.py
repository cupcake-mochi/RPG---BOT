"""Mede a monotonia: manda a mesma mensagem várias vezes, cada vez numa conversa nova, e conta as respostas diferentes.

Roda duas vezes, pra comparar:
  sem memória   cada conversa começa do zero, como era antes;
  com memória   as últimas falas da personagem entram no pedido, e o aviso de repetição da página do site
                passa a valer de uma conversa pra outra (é o que o bot faz, pelo registro de falas).

    python3 ferramentas/medir_monotonia.py              6 repetições de cada mensagem, nos dois modos
    python3 ferramentas/medir_monotonia.py --vezes 4 --modo com

Cada repetição é uma chamada ao modelo (paga, se a fila for da Vertex). Grava em pesquisa/validacao/.
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "ferramentas" / "prompt_do_site"))

import site_prompt  # noqa: E402
from closure_bot.config import carregar  # noqa: E402
from closure_bot.modelo import FILA_PADRAO, TETO_PADRAO_USD, Falhou, Modelos, ler_fila  # noqa: E402
from closure_bot.registro import Registro  # noqa: E402

NOMES = {"kal": "Kal'tsit", "clo": "Closure"}
CHAVES = {"kal": "kaltsit", "clo": "closure"}
CASOS = [("clo", (22, 10), "oi closure"), ("kal", (14, 20), "kal, tudo bem?"), ("clo", (22, 10), "closure, me conta uma piada")]
CANAL = 1  # canal de mentira, só pra separar as falas no registro em memória


def abertura(texto: str) -> str:
    """As três primeiras palavras, sem pontuação nem maiúscula, pra contar abertura repetida."""
    return " ".join(re.findall(r"\w+", texto.lower())[:3])


async def rodar(args) -> int:
    config = carregar()
    modelos = Modelos(ler_fila(args.fila or config.fila_modelos or FILA_PADRAO), config.chaves, Registro(config.banco),
                      teto_usd=config.teto_mensal_usd or TETO_PADRAO_USD)
    if not modelos.fila:
        print("Nenhum provedor da fila tem chave no .env da pasta Closure.")
        return 1
    modos = ["sem", "com"] if args.modo == "ambos" else [args.modo]
    linhas, resumo = [], []
    for pers, hora, msg in CASOS:
        linhas.append(f"## {NOMES[pers]}: \"{msg}\"\n")
        for modo in modos:
            falas = Registro(":memory:")  # as falas do teste não entram no registro do bot
            respostas = []
            for _ in range(args.vezes):
                anteriores = falas.ultimas_falas(canal_id=CANAL, persona=CHAVES[pers]) if modo == "com" else None
                entrada = site_prompt.montar(pers, msg, nome="rafa", hora=hora, falas_anteriores=anteriores)["input"]
                try:
                    texto = (await modelos.responder(entrada, persona=pers, gatilho="monotonia")).texto
                except Falhou as erro:
                    texto = f"[falhou: {erro.codigo}]"
                respostas.append(texto)
                falas.guardar_fala(canal_id=CANAL, persona=CHAVES[pers], texto=texto)
            diferentes, aberturas = len(set(respostas)), len({abertura(r) for r in respostas})
            resumo.append((NOMES[pers], msg, modo, diferentes, aberturas))
            linhas.append(f"**{modo} memória:** {diferentes} respostas diferentes e {aberturas} aberturas diferentes em {args.vezes}\n")
            linhas += [f"{i}. {r}" for i, r in enumerate(respostas, 1)] + [""]
            print(f"\n== {NOMES[pers]}: {msg}  [{modo} memória]  {diferentes} diferentes, {aberturas} aberturas em {args.vezes}")
            for r in respostas:
                print("  -", r)

    saida = RAIZ / "pesquisa" / "validacao" / f"{datetime.now():%Y-%m-%d-%Hh%M}-monotonia.md"
    tabela = ["| Personagem | Mensagem | Memória | Respostas diferentes | Aberturas diferentes |", "|---|---|---|---|---|"]
    tabela += [f"| {p} | {m} | {modo} | {d} de {args.vezes} | {a} de {args.vezes} |" for p, m, modo, d, a in resumo]
    fila = ", ".join(f"{p}:{m}" for p, m in modelos.fila)
    cabecalho = [f"# Monotonia: a mesma mensagem {args.vezes} vezes ({datetime.now():%d/%m/%Y %H:%M})\n",
                 f"Fila: `{fila}`. Raciocínio: {modelos.raciocinio}. Cada repetição é uma conversa nova. "
                 "Gerado por `ferramentas/medir_monotonia.py`.\n", *tabela, ""]
    saida.write_text("\n".join(cabecalho + linhas), encoding="utf-8")
    print(f"\nGasto estimado no mês: US$ {modelos.gasto_do_mes():.4f}. Gravado em {saida.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--vezes", type=int, default=6)
    ap.add_argument("--modo", choices=["sem", "com", "ambos"], default="ambos")
    ap.add_argument("--fila", default="vertex:gemini-3.8-flash,vertex:gemini-3.1-flash-lite")
    sys.exit(asyncio.run(rodar(ap.parse_args())))
