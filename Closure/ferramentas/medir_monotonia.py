"""Mede a monotonia: manda a mesma mensagem várias vezes, cada vez numa conversa nova, e conta as respostas diferentes.

Roda duas vezes, pra comparar:
  sem memória   cada conversa começa do zero, como era antes;
  com memória   as últimas falas da personagem entram no pedido, e o aviso de repetição da página do site
                passa a valer de uma conversa pra outra (é o que o bot faz, pelo registro de falas).

    python3 ferramentas/medir_monotonia.py              6 repetições de cada mensagem, nos dois modos
    python3 ferramentas/medir_monotonia.py --vezes 4 --modo com
    python3 ferramentas/medir_monotonia.py --vezes 3 --modo vida

O modo "vida" responde outra pergunta: a mesma mensagem, com memória, em situações diferentes do estado
(closure_bot/vida.py): pessoa nova, pessoa conhecida com ficha, canal cheio com carga alta, paciência baixa.

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
from closure_bot.plantao import FUSO  # noqa: E402
from closure_bot.registro import Registro  # noqa: E402
from closure_bot.vida import Estado  # noqa: E402

NOMES = {"kal": "Kal'tsit", "clo": "Closure"}
CHAVES = {"kal": "kaltsit", "clo": "closure"}
CASOS = [("clo", (22, 10), "oi closure"), ("kal", (14, 20), "kal, tudo bem?"), ("clo", (22, 10), "closure, me conta uma piada")]
CANAL = 1  # canal de mentira, só pra separar as falas no registro em memória

# Situações do modo "vida". A ficha é inventada pra medição: no bot os fatos vêm do que a pessoa disse no servidor.
FICHA = ("joga com um Bastião chamado Ren na mesa do Tiago", "perguntou da Integridade na semana passada")
SITUACOES = [
    ("pessoa nova, canal quieto", dict(movimento="quieto", carga=0, dias=0, intimidade=0, paciencia=3, fatos=())),
    ("conhecida (intimidade 2), com ficha", dict(movimento="normal", carga=0, dias=17, intimidade=2, paciencia=3, fatos=FICHA)),
    ("íntima (3), canal cheio, carga alta", dict(movimento="cheio", carga=2, dias=45, intimidade=3, paciencia=3, fatos=FICHA)),
    ("paciência baixa (1), intimidade 1", dict(movimento="normal", carga=0, dias=6, intimidade=1, paciencia=1, fatos=())),
]


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
    if args.modo == "vida":
        modos = [nome for nome, _ in SITUACOES]
    linhas, resumo = [], []
    for pers, hora, msg in CASOS[:2] if args.modo == "vida" else CASOS:
        linhas.append(f"## {NOMES[pers]}: \"{msg}\"\n")
        for modo in modos:
            falas = Registro(":memory:")  # as falas do teste não entram no registro do bot
            respostas = []
            estado = None
            if args.modo == "vida":
                estado = Estado(persona=CHAVES[pers], agora=datetime(2026, 10, 13, *hora, tzinfo=FUSO), nome="rafa", pronomes=None,
                                **dict(SITUACOES)[modo]).para_a_ponte()
            for _ in range(args.vezes):
                anteriores = falas.ultimas_falas(canal_id=CANAL, persona=CHAVES[pers]) if modo != "sem" else None
                entrada = site_prompt.montar(pers, msg, nome="rafa", hora=hora, falas_anteriores=anteriores, estado=estado)["input"]
                try:
                    texto = (await modelos.responder(entrada, persona=pers, gatilho="monotonia")).texto
                except Falhou as erro:
                    texto = f"[falhou: {erro.codigo}]"
                respostas.append(texto)
                falas.guardar_fala(canal_id=CANAL, persona=CHAVES[pers], texto=texto)
            diferentes, aberturas = len(set(respostas)), len({abertura(r) for r in respostas})
            resumo.append((NOMES[pers], msg, modo, diferentes, aberturas))
            rotulo = modo if args.modo == "vida" else f"{modo} memória"
            linhas.append(f"**{rotulo}:** {diferentes} respostas diferentes e {aberturas} aberturas diferentes em {args.vezes}\n")
            linhas += [f"{i}. {r}" for i, r in enumerate(respostas, 1)] + [""]
            print(f"\n== {NOMES[pers]}: {msg}  [{rotulo}]  {diferentes} diferentes, {aberturas} aberturas em {args.vezes}")
            for r in respostas:
                print("  -", r)

    saida = RAIZ / "pesquisa" / "validacao" / f"{datetime.now():%Y-%m-%d-%Hh%M}-{'vida' if args.modo == 'vida' else 'monotonia'}.md"
    tabela = [f"| Personagem | Mensagem | {'Situação' if args.modo == 'vida' else 'Memória'} | Respostas diferentes | Aberturas diferentes |", "|---|---|---|---|---|"]
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
    ap.add_argument("--modo", choices=["sem", "com", "ambos", "vida"], default="ambos")
    ap.add_argument("--fila", default="vertex:gemini-3.8-flash,vertex:gemini-3.1-flash-lite")
    sys.exit(asyncio.run(rodar(ap.parse_args())))
