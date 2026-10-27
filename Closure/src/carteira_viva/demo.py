"""Demonstração visual local, sem chamadas ao Discord/Google ou credenciais reais."""
from tempfile import TemporaryDirectory
from pathlib import Path
from urllib.parse import urlencode

from aiohttp import web
from cryptography.fernet import Fernet

from .config_web import ConfigWeb
from .permissoes import Membro
from .provedores import Provedores
from .web import DADOS, GALERIA, criar_app
from .segredos import AcessoNegado


class ProvedoresDemo(Provedores):
    def autorizar(self, provedor, estado, verificador):
        return self.cfg.origem + "/demo/autorizar?" + urlencode({"provedor": provedor, "state": estado})

    async def trocar_codigo(self, provedor, **kwargs):
        return {"access_token": "acesso_visitante" if "conta_comum" in kwargs.get("retorno", "") else "acesso_totalmente_ficticio", "refresh_token": "refresh_totalmente_ficticio", "expires_in": 3600}

    async def usuario_discord(self, token):
        return "999" if token == "acesso_visitante" else "222"

    async def membro(self, servidor, usuario):
        if servidor!='111' or usuario not in ('222','999'):raise AcessoNegado('Conta fictícia indisponível.')
        return Membro(servidor,usuario,nome='Ayla · jogador fictício' if usuario=='222' else 'Visitante · conta fictícia')

    async def conta_google(self, acesso):
        return "conta_google_ficticia"

    async def renovar(self, refresh):
        return self.token_google({"access_token": "acesso_totalmente_ficticio", "expires_in": 3600})

    async def validar_arquivo(self, acesso, arquivo):
        return {"arquivo": arquivo, "nome_arquivo": "Ficha de demonstração — somente dados fictícios",
                "nome": "Personagem de teste", "contrato": "analise-12", "prova_parcial": True}

    async def ler_analise(self,acesso,arquivo):
        from closure_bot.ficha_leitor import Campo
        nome=('Ayla','Ren','Noa')[int(arquivo.rsplit('_',1)[1])] if arquivo.startswith('arquivo_demo_somente_ficticio_') else 'Personagem de teste'
        valores={'formato.versao':12,'nome':nome,'nivel':1,'origem':'Latente','caminho':'Bastião',
                 'vida_max':23,'energia_max':8,'integridade_max':26,'defesa':13,'protecao':1}
        return {k:Campo(v,'','entrada') for k,v in valores.items()},'demo'


def preparar(porta):
    temp = TemporaryDirectory(prefix="carteira-demo-")
    origem = f"http://127.0.0.1:{porta}"
    cfg = ConfigWeb(origem, Path(temp.name) / "demo.sqlite3", (Fernet.generate_key(),),
                    "servico_ficticio_sem_qualquer_acesso_real_123", "111", "discord_ficticio", "bot_ficticio",
                    "google_ficticio", "segredo_ficticio", "333", "picker_ficticio", frozenset({"111"}), True)
    from dataclasses import replace
    dados=Path(__file__).resolve().parents[2]/'dados'
    campanha=Path(temp.name)/'campanhas.json';campanha.write_text('{}')
    cfg=replace(cfg,dados_livro=dados,campanhas=campanha)
    app = criar_app(cfg, provedores=ProvedoresDemo(cfg), demonstracao=True)

    async def inicio(request):
        return web.Response(text="<html lang='pt-BR'><meta charset='utf-8'><title>Demonstração da Carteira</title>"
                                 "<h1>Carteira viva · demonstração local</h1>"
                                 "<p>Este ensaio usa contas e planilhas fictícias. Não entra no Google ou Discord.</p>"
                                 "<p><a href='/demo/iniciar'>Testar cadastro de personagem</a></p><p><a href='/carteira/111'>Abrir Carteira de demonstração</a></p></html>", content_type="text/html")

    async def iniciar(request):
        ticket = await app[DADOS].chamar("criar", Membro("111", "222"), "cadastro", None)
        return web.HTTPFound(origem + "/conectar?" + urlencode({"ticket": ticket}))

    async def autorizar(request):
        provedor = request.query.get("provedor")
        if provedor not in ("discord", "google"):
            raise web.HTTPBadRequest()
        if provedor=='discord' and await app[DADOS].chamar('sessoes.tem_estado',request.query.get('state','')):
            if request.query.get('conta') not in ('222','999'):
                from html import escape
                links=''.join("<p><a href='"+escape('/demo/autorizar?'+urlencode({'provedor':'discord','state':request.query.get('state',''),'conta':u}),quote=True)+"'>"+nome+"</a></p>" for u,nome in (('222','Entrar como responsável fictício'),('999','Entrar como membro comum fictício')))
                return web.Response(text="<!doctype html><html lang='pt-BR'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><link rel='stylesheet' href='/static/carteira.css'><main class='pagina'><h1>Demonstração · escolha uma conta fictícia</h1><p>Não há login real nem acesso a arquivos Google.</p>"+links+"</main></html>",content_type='text/html')
            return web.HTTPFound(origem+'/oauth/discord/retorno?'+urlencode({'state':request.query.get('state',''),'code':'conta_comum' if request.query['conta']=='999' else 'conta_responsavel'}))
        return web.HTTPFound(origem + f"/oauth/{provedor}/retorno?" +
                             urlencode({"state": request.query.get("state", ""), "code": "codigo_ficticio"}))

    async def semear(app):
        m=Membro('111','222');cid=await app[DADOS].chamar('cadastro.conectar',m,conta='demo',cliente=cfg.google_id,refresh_token='ficticio')
        for i,nome in enumerate(('Ayla','Ren','Noa')):
            p=await app[DADOS].chamar('cadastro.cadastrar',m,conexao=cid,arquivo='arquivo_demo_somente_ficticio_'+str(i),nome=nome,contrato='analise-12',responsabilidade=True,pedido='demo-'+str(i))
            await app[DADOS].chamar('cadastro.personalizar',m,p['id'],perfil={'nome':nome,'titulo':'Exploradora de fronteiras','frase':'Uma história ainda por escrever.','origem':'Latente','caminho':'Bastião','cor':0x397B77},campos_publicos={'nome','titulo','frase','origem','caminho','cor'})
    app.on_startup.append(semear)

    async def encerrar(app):
        temp.cleanup()

    app.router.add_get("/", inicio)
    app.router.add_get("/demo/iniciar", iniciar)
    app.router.add_get("/demo/autorizar", autorizar)
    app.on_cleanup.append(encerrar)
    return app
