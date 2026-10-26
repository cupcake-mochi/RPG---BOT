"""Demonstração visual local, sem chamadas ao Discord/Google ou credenciais reais."""
from tempfile import TemporaryDirectory
from pathlib import Path
from urllib.parse import urlencode

from aiohttp import web
from cryptography.fernet import Fernet

from .config_web import ConfigWeb
from .permissoes import Membro
from .provedores import Provedores
from .web import DADOS, criar_app


class ProvedoresDemo(Provedores):
    def autorizar(self, provedor, estado, verificador):
        return self.cfg.origem + "/demo/autorizar?" + urlencode({"provedor": provedor, "state": estado})

    async def trocar_codigo(self, provedor, **kwargs):
        return {"access_token": "acesso_totalmente_ficticio", "refresh_token": "refresh_totalmente_ficticio", "expires_in": 3600}

    async def usuario_discord(self, token):
        return "222"

    async def membro(self, servidor, usuario):
        return Membro(servidor, usuario)

    async def conta_google(self, acesso):
        return "conta_google_ficticia"

    async def renovar(self, refresh):
        return self.token_google({"access_token": "acesso_totalmente_ficticio", "expires_in": 3600})

    async def validar_arquivo(self, acesso, arquivo):
        return {"arquivo": arquivo, "nome_arquivo": "Ficha de demonstração — somente dados fictícios",
                "nome": "Personagem de teste", "contrato": "analise-12", "prova_parcial": True}


def preparar(porta):
    temp = TemporaryDirectory(prefix="carteira-demo-")
    origem = f"http://127.0.0.1:{porta}"
    cfg = ConfigWeb(origem, Path(temp.name) / "demo.sqlite3", (Fernet.generate_key(),),
                    "servico_ficticio_sem_qualquer_acesso_real_123", "111", "discord_ficticio", "bot_ficticio",
                    "google_ficticio", "segredo_ficticio", "333", "picker_ficticio", frozenset({"111"}), True)
    app = criar_app(cfg, provedores=ProvedoresDemo(cfg), demonstracao=True)

    async def inicio(request):
        return web.Response(text="<html lang='pt-BR'><meta charset='utf-8'><title>Demonstração da Carteira</title>"
                                 "<h1>Carteira viva · demonstração local</h1>"
                                 "<p>Este ensaio usa contas e planilhas fictícias. Não entra no Google ou Discord.</p>"
                                 "<p><a href='/demo/iniciar'>Testar cadastro de personagem</a></p></html>", content_type="text/html")

    async def iniciar(request):
        ticket = await app[DADOS].chamar("criar", Membro("111", "222"), "cadastro", None)
        return web.HTTPFound(origem + "/conectar?" + urlencode({"ticket": ticket}))

    async def autorizar(request):
        provedor = request.query.get("provedor")
        if provedor not in ("discord", "google"):
            raise web.HTTPBadRequest()
        return web.HTTPFound(origem + f"/oauth/{provedor}/retorno?" +
                             urlencode({"state": request.query.get("state", ""), "code": "codigo_ficticio"}))

    async def encerrar(app):
        temp.cleanup()

    app.router.add_get("/", inicio)
    app.router.add_get("/demo/iniciar", iniciar)
    app.router.add_get("/demo/autorizar", autorizar)
    app.on_cleanup.append(encerrar)
    return app
