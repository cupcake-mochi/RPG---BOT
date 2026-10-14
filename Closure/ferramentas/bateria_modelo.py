"""Roda uma bateria de mensagens pelo mesmo modelo e pela mesma camada que o bot usa, pra o nota_c3.py conferir.

    python3 ferramentas/bateria_modelo.py bateria_c3lb12.json sistema_closure_v32.txt lembrete_closure_v32.txt r_c3lb12v32_gemini_a.json

Os quatro arquivos ficam em dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos/. O pedido tem a forma do
gemini_bateria.py (sistema + contexto da bateria; mensagem + lembrete), mas vai pela Vertex, com o raciocínio
reduzido do bot, e várias de uma vez. Se a saída já existe, continua de onde parou. Cada mensagem é uma chamada paga.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
PASTA = RAIZ / "dados" / "personagem" / "kaltsit" / "avaliacao" / "2026-10-12-ciclos"

from closure_bot.config import carregar  # noqa: E402
from closure_bot.modelo import Falhou, Modelos, ler_fila  # noqa: E402
from closure_bot.registro import Registro  # noqa: E402


async def rodar(args) -> int:
    config = carregar()
    modelos = Modelos(ler_fila(args.fila), config.chaves, Registro(config.banco))
    sistema = (PASTA / args.sistema).read_text(encoding="utf-8").strip()
    lembrete = (PASTA / args.lembrete).read_text(encoding="utf-8").strip()
    bateria = json.loads((PASTA / args.bateria).read_text(encoding="utf-8"))
    saida = PASTA / args.saida
    feitas = {r["id"]: r for r in json.loads(saida.read_text(encoding="utf-8"))} if saida.exists() else {}
    vagas = asyncio.Semaphore(args.juntas)

    def salvar() -> None:
        # Grava cada sucesso antes de pedir outro: uma interrupção não deve
        # obrigar a pagar novamente pelas respostas que já chegaram.
        temporario = saida.with_name(saida.name + ".tmp")
        temporario.write_text(json.dumps([feitas[m["id"]] for m in bateria if m["id"] in feitas],
                                        ensure_ascii=False, indent=1), encoding="utf-8")
        temporario.replace(saida)

    async def uma(m: dict) -> None:
        entrada = [{"role": "user", "content": sistema + "\n\nContexto ativado:\n" + m["contexto"]},
                   {"role": "user", "content": f'{m["de"]}: {m["mensagem"]}\n\n{lembrete}'}]
        async with vagas:
            for _ in range(3):
                try:
                    feitas[m["id"]] = {"id": m["id"], "resposta": (await modelos.responder(entrada, gatilho="bateria")).texto.strip()}
                    salvar()
                    return
                except Falhou as erro:
                    ultimo = erro
                    await asyncio.sleep(5)
            print(f"  {m['id']}: sem resposta ({str(ultimo)[:80]})", flush=True)

    await asyncio.gather(*(uma(m) for m in bateria if m["id"] not in feitas))
    salvar()
    print(f"{args.saida}: {len(feitas)} de {len(bateria)} respostas. Gasto estimado no mês: US$ {modelos.gasto_do_mes():.2f}")
    return 0 if len(feitas) == len(bateria) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("bateria"); ap.add_argument("sistema"); ap.add_argument("lembrete"); ap.add_argument("saida")
    ap.add_argument("--fila", default="vertex:gemini-3.8-flash")
    ap.add_argument("--juntas", type=int, default=6, help="quantas chamadas ao mesmo tempo")
    sys.exit(asyncio.run(rodar(ap.parse_args())))
