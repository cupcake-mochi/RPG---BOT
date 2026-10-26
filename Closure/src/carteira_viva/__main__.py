"""Servidor separado das Guias: python -m carteira_viva."""
import argparse
import logging
from urllib.parse import urlsplit

from aiohttp import web

from .config_web import ConfigWeb
from .web import criar_app


def main():
    parser = argparse.ArgumentParser(description="Serviço de conexão de fichas das Guias do Ciclo")
    parser.add_argument("--porta", type=int, default=8080)
    parser.add_argument("--demo", action="store_true", help="somente loopback e dados fictícios")
    args = parser.parse_args()
    for nome in ("authlib", "httpx", "httpcore"):
        logging.getLogger(nome).setLevel(logging.WARNING)
    if args.demo:
        from .demo import preparar
        app = preparar(args.porta)
        host = "127.0.0.1"
    else:
        cfg = ConfigWeb.do_ambiente()
        app = criar_app(cfg)
        host = urlsplit(cfg.origem).hostname if cfg.desenvolvimento else "0.0.0.0"
    web.run_app(app, host=host, port=args.porta, access_log=None)


if __name__ == "__main__":
    main()
