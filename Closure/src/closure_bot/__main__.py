"""Sobe o bot:  python -m closure_bot   (rodando de dentro de src/)

Com --conferir, só lê a configuração e os dados e mostra o que achou, sem conectar ao Discord.
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime

from .config import carregar
from .dados import carregar_personas, ler_manifesto, resumo_manifesto
from .modelo import FILA_PADRAO, TETO_PADRAO_USD, Modelos, ler_fila
from .plantao import FUSO, de_plantao
from .registro import Registro


def conferir() -> int:
    config = carregar()
    personas = carregar_personas(config.dados, config.avatares)
    registro = Registro(config.banco)
    agora = datetime.now(FUSO)
    print("Regras:  ", resumo_manifesto(ler_manifesto(config.dados)))
    print("Cards:   ", ", ".join(f"{p.nome} v{p.versao}" for p in personas.values()))
    print("Plantão: ", f"{personas[de_plantao(agora)].nome} ({agora:%H:%M}, Brasília)")
    print("Registro:", config.banco, registro.contagens())
    modelos = Modelos(ler_fila(config.fila_modelos or FILA_PADRAO), config.chaves, registro,
                      teto_usd=config.teto_mensal_usd or TETO_PADRAO_USD)
    print("Modelos: ", ", ".join(f"{p}:{m}" for p, m in modelos.fila) or "nenhum (faltam GEMINI_API_KEY e VERTEX_API_KEY no .env)")
    print("Gasto:   ", f"US$ {modelos.gasto_do_mes():.4f} estimados neste mês nos provedores pagos; teto de US$ {modelos.teto_usd:.2f}")
    print("Token:   ", "definido" if config.token else "FALTA (DISCORD_TOKEN no .env)")
    print("Servidor de teste:", config.guild_id or "não definido (comandos demoram até 1 h pra aparecer)")
    print("Dono:    ", config.dono_id or "não definido (/teste_webhook fica bloqueado)")
    print("Avatares:", ", ".join(f"{k}: {'ok' if v else 'falta'}" for k, v in config.avatares.items()))
    print("Painéis: ", f"{len(registro.paineis())} servidor(es) com painel diário de clima (liga com /clima_canal)")
    registro.fechar()
    return 0


def main() -> int:
    if "--conferir" in sys.argv[1:]:
        return conferir()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = carregar()
    if not config.token:
        print("Falta o DISCORD_TOKEN no .env da pasta Closure (modelo em .env.exemplo, na raiz do repositório).", file=sys.stderr)
        return 1
    from .bot import ClosureBot  # só aqui, pra --conferir funcionar sem o discord.py instalado

    ClosureBot(config).run(config.token, log_handler=None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
