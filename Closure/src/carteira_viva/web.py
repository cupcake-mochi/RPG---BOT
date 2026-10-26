"""Serviço de conexão. Sem galeria pública, escrita de ficha ou conversa por IA."""
import asyncio
from contextlib import suppress
import hmac
import logging
from pathlib import Path
import secrets
import time
from urllib.parse import urlencode

from aiohttp import web

from .banco import digest
from .config_web import ConfigWeb
from .fluxos import DadosAsync, ErroFluxo, nome_cookie
from .provedores import ErroProvedor, Provedores
from .segredos import AcessoNegado, Conflito, ErroCarteira

CFG = web.AppKey("cfg", ConfigWeb)
DADOS = web.AppKey("dados", DadosAsync)
PROVEDORES = web.AppKey("provedores", Provedores)
LIMITE = web.AppKey("limite", asyncio.Semaphore)
DEMO = web.AppKey("demo", bool)
STATIC = Path(__file__).with_name("static")
RequestKey = getattr(web, "RequestKey", web.AppKey)
TICKET = RequestKey("ticket", str)
COOKIE = RequestKey("cookie", str)
TRANSICAO = RequestKey("transicao_valida", bool)


def cookie(request, fid):
    return request.cookies.get(nome_cookie(fid, request.app[CFG].segura), "")


def resposta_json(data, status=200):
    return web.json_response(data, status=status)


@web.middleware
async def guardas(request, handler):
    cfg = request.app[CFG]
    try:
        if request.method in ("POST", "PUT", "DELETE", "PATCH") and not request.path.startswith("/interno/"):
            if request.headers.get("Origin") != cfg.origem:
                raise web.HTTPForbidden(text='{"erro":"origem"}', content_type="application/json")
        if request.path != "/saude" and request.app[LIMITE].locked():
            raise web.HTTPTooManyRequests(text='{"erro":"ocupado"}', content_type="application/json")
        async with request.app[LIMITE]:
            resposta = await handler(request)
    except (ErroCarteira, ValueError, TypeError, KeyError) as exc:
        codigo = getattr(exc, "codigo", None) or ("acesso" if isinstance(exc, AcessoNegado) else
                                                   "conflito" if isinstance(exc, Conflito) else "solicitacao")
        if request.get(TRANSICAO):
            with suppress(ErroCarteira):
                await request.app[DADOS].chamar("encerrar", request[TICKET], request[COOKIE], None, falhou=True)
        if request.path.startswith("/oauth/"):
            seguro = codigo if codigo in {"oauth", "acesso", "identidade", "escopo", "expirada", "etapa", "cancelado", "provedor", "temporario"} else type(exc).__name__
            logging.getLogger(__name__).warning("Conexão recusada no retorno OAuth (%s)", seguro)
            destino = "/conectar?" + urlencode({"ticket": request[TICKET]}) if request.get(TRANSICAO) else "/erro"
            resposta = web.HTTPFound(cfg.origem + destino)
        else:
            status = (429 if codigo == "limite" else 403 if isinstance(exc, AcessoNegado) else
                      409 if isinstance(exc, Conflito) or codigo == "etapa" else
                      410 if codigo == "expirada" else 400)
            resposta = resposta_json({"erro": codigo}, status)
    except web.HTTPException as exc:
        resposta = exc
    except Exception as exc:
        # Não registrar str(exc), URL de callback, corpo ou tokens dos provedores.
        logging.getLogger(__name__).error("Falha interna da Carteira (%s)", type(exc).__name__)
        resposta = resposta_json({"erro": "interno"}, 500)
    resposta.headers.update({"Cache-Control": "private, no-store", "Referrer-Policy": "strict-origin",
                             "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
                             "Content-Security-Policy": "default-src 'self'; script-src 'self' https://apis.google.com https://www.gstatic.com; "
                             "frame-src https://docs.google.com https://drive.google.com https://accounts.google.com; "
                             "connect-src 'self' https://*.googleapis.com; img-src 'self' data: https://*.googleusercontent.com; "
                             "style-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"})
    if cfg.segura:
        resposta.headers["Strict-Transport-Security"] = "max-age=31536000"
    if isinstance(resposta, web.HTTPException):
        raise resposta
    return resposta


async def corpo(request):
    if request.content_type != "application/json":
        raise ErroCarteira("Envie um formulário JSON.")
    data = await request.json()
    if not isinstance(data, dict):
        raise ErroCarteira("Solicitação inválida.")
    return data


async def sessao(request, *, data=None, membro=False):
    ticket = data.get("ticket") if data is not None else request.query.get("ticket")
    ctx = await request.app[DADOS].chamar("contexto", ticket)
    sid = cookie(request, ctx["id"])
    # estado também verifica cookie, inclusive para endpoints somente de leitura.
    estado = await request.app[DADOS].chamar("estado", ticket, sid)
    request.update({TICKET: ticket, COOKIE: sid})
    if membro and estado["fase"] not in ("identificar", "oauth_discord", "processando_discord"):
        atual = await request.app[PROVEDORES].membro(ctx["servidor"], ctx["usuario"])
        return ticket, sid, atual
    return ticket, sid, estado


def csrf(request):
    valor = request.headers.get("X-CSRF-Token")
    if not isinstance(valor, str) or not 30 <= len(valor) <= 100:
        raise AcessoNegado("Confirmação da sessão ausente.")
    return valor


async def iniciar(request):
    token = request.headers.get("Authorization", "")
    if not hmac.compare_digest(token, "Bearer " + request.app[CFG].servico_token):
        raise AcessoNegado("Acesso de serviço inválido.")
    data = await corpo(request)
    m = await request.app[PROVEDORES].membro(data.get("servidor", ""), data.get("usuario", ""))
    ticket = await request.app[DADOS].chamar("criar", m, data.get("acao", "cadastro"), data.get("personagem"))
    return resposta_json({"url": request.app[CFG].origem + "/conectar?" + urlencode({"ticket": ticket}), "expira_em": 600})


async def pagina(request):
    ticket = request.query.get("ticket")
    ctx = await request.app[DADOS].chamar("contexto", ticket)
    nome = nome_cookie(ctx["id"], request.app[CFG].segura)
    sid = request.cookies.get(nome) or secrets.token_urlsafe(32)
    await request.app[DADOS].chamar("abrir", ticket, sid)
    out = web.Response(text=(STATIC / "conectar.html").read_text(), content_type="text/html")
    out.set_cookie(nome, sid, max_age=600, path="/", secure=request.app[CFG].segura, httponly=True, samesite="Lax")
    return out


async def status(request):
    ticket, sid, estado = await sessao(request)
    if estado["fase"] not in ("identificar", "oauth_discord", "processando_discord"):
        ctx = await request.app[DADOS].chamar("contexto", ticket)
        await request.app[PROVEDORES].membro(ctx["servidor"], ctx["usuario"])
    estado["demonstracao"] = request.app[DEMO]
    return resposta_json(estado)


async def login(request):
    data = await corpo(request)
    ticket, sid, _ = await sessao(request, data=data, membro=True)
    provider = request.match_info["provedor"]
    oauth = await request.app[DADOS].chamar("login", ticket, sid, csrf(request), provider)
    return resposta_json({"url": request.app[PROVEDORES].autorizar(provider, oauth["estado"], oauth["verificador"])})


async def selecionar_automatico(request, ticket, sid, arquivo):
    estado = await request.app[DADOS].chamar("estado", ticket, sid)
    g = await request.app[DADOS].chamar("preparar_selecao", ticket, sid, estado["csrf"])
    previa = await request.app[PROVEDORES].validar_arquivo(g["acesso"], arquivo)
    await request.app[DADOS].chamar("arquivo_ok", ticket, sid, previa)


async def retorno(request):
    provider = request.match_info["provedor"]
    if provider not in ("discord", "google"):
        raise ErroFluxo()
    if len(request.query.getall("state", [])) != 1 or len(request.query.getall("code", [])) > 1:
        raise ErroFluxo()
    state = request.query["state"]
    if not 30 <= len(state) <= 100:
        raise ErroFluxo()
    fid = await request.app[DADOS].chamar("por_estado", state, provider)
    sid = cookie(request, fid)
    oauth = await request.app[DADOS].chamar("consumir_retorno", state, provider, sid)
    ticket = oauth["ticket"]
    request.update({TICKET: ticket, COOKIE: sid, TRANSICAO: True})
    if "error" in request.query or not request.query.get("code"):
        raise ErroProvedor("cancelado")
    callback = request.app[CFG].origem + request.path + "?" + urlencode(list(request.query.items()))
    token = await request.app[PROVEDORES].trocar_codigo(provider, estado=state,
                                                     verificador=oauth["verificador"], retorno=callback)
    out = web.HTTPFound(request.app[CFG].origem + "/conectar?" + urlencode({"ticket": ticket}))
    if provider == "discord":
        user = await request.app[PROVEDORES].usuario_discord(token["access_token"])
        if user != oauth["usuario"]:
            raise AcessoNegado("Entre com a conta que iniciou a conexão.")
        m = await request.app[PROVEDORES].membro(oauth["servidor"], user)
        novo = secrets.token_urlsafe(32)
        await request.app[DADOS].chamar("identificar", ticket, sid, novo, m)
        out.set_cookie(nome_cookie(fid, request.app[CFG].segura), novo, max_age=600, path="/",
                       secure=request.app[CFG].segura, httponly=True, samesite="Lax")
    else:
        await request.app[PROVEDORES].membro(oauth["servidor"], oauth["usuario"])
        g = request.app[PROVEDORES].token_google(token)
        conta = await request.app[PROVEDORES].conta_google(g.acesso)
        arquivo = await request.app[DADOS].chamar("google_ok", ticket, sid, conta=conta, token=g)
        if arquivo:
            await selecionar_automatico(request, ticket, sid, arquivo)
    return out


async def usar_conexao(request):
    data = await corpo(request)
    ticket, sid, _ = await sessao(request, data=data, membro=True)
    uso = await request.app[DADOS].chamar("preparar_uso", ticket, sid, csrf(request), data.get("conexao"))
    request[TRANSICAO] = True
    try:
        g = await request.app[PROVEDORES].renovar(uso["credencial"].refresh_token)
    except ErroProvedor as exc:
        if exc.codigo == "revogada":
            await request.app[DADOS].chamar("cadastro.marcar_revogada", uso["id"], autorizacao=uso["credencial"].autorizacao)
        raise
    conta = await request.app[PROVEDORES].conta_google(g.acesso)
    arquivo = await request.app[DADOS].chamar("google_ok", ticket, sid, conta=conta, token=g, reutilizada=True)
    if arquivo:
        await selecionar_automatico(request, ticket, sid, arquivo)
    return resposta_json({"ok": True})


async def picker(request):
    ticket, sid, _ = await sessao(request, membro=True)
    g = await request.app[DADOS].chamar("google", ticket, sid)
    return resposta_json({"access_token": g["acesso"], "app_id": request.app[CFG].projeto_google,
                          "developer_key": request.app[CFG].picker_key})


async def selecionar(request):
    data = await corpo(request)
    ticket, sid, _ = await sessao(request, data=data, membro=True)
    g = await request.app[DADOS].chamar("preparar_selecao", ticket, sid, csrf(request))
    request[TRANSICAO] = True
    previa = await request.app[PROVEDORES].validar_arquivo(g["acesso"], data.get("arquivo"))
    await request.app[DADOS].chamar("arquivo_ok", ticket, sid, previa)
    return resposta_json({"ok": True})


async def confirmar(request):
    data = await corpo(request)
    ticket, sid, membro = await sessao(request, data=data, membro=True)
    etapa = await request.app[DADOS].chamar("preparar_confirmacao", ticket, sid, csrf(request),
                                           data.get("nome"), data.get("responsabilidade"))
    if "resultado" in etapa:
        return resposta_json({"resultado": etapa["resultado"]})
    request[TRANSICAO] = True
    previa = await request.app[PROVEDORES].validar_arquivo(etapa["google"]["acesso"], etapa["previa"]["arquivo"])
    # Refaz a consulta ao Discord depois da espera pelo Google.
    membro = await request.app[PROVEDORES].membro(membro.servidor, membro.usuario)
    resultado = await request.app[DADOS].chamar("finalizar", ticket, sid, membro, previa)
    return resposta_json({"resultado": resultado})


async def cancelar(request):
    data = await corpo(request)
    ticket, sid, _ = await sessao(request, data=data)
    await request.app[DADOS].chamar("encerrar", ticket, sid, csrf(request))
    return resposta_json({"ok": True})


async def estatico(request):
    nome = request.match_info["nome"]
    if nome not in ("conectar.js", "conectar.css"):
        raise web.HTTPNotFound()
    return web.Response(body=(STATIC / nome).read_bytes(), content_type="application/javascript" if nome.endswith(".js") else "text/css")


async def saude(request):
    return resposta_json({"servico": "carteira-viva", "estado": "online"})


async def erro(request):
    return web.Response(text="<html lang='pt-BR'><meta charset='utf-8'><title>Conexão encerrada</title>"
                             "<p>Esta conexão não pôde ser confirmada. Abra uma nova solicitação pelo Discord.</p></html>",
                        content_type="text/html")


def criar_app(cfg, *, provedores=None, agora=time.time, demonstracao=False):
    if demonstracao and (cfg.segura or not cfg.desenvolvimento):
        raise ErroCarteira("A demonstração só pode rodar no loopback de desenvolvimento.")
    app = web.Application(middlewares=[guardas], client_max_size=16 * 1024)
    app[CFG], app[PROVEDORES], app[LIMITE], app[DEMO] = cfg, provedores or Provedores(cfg, agora=agora), asyncio.Semaphore(8), demonstracao
    dados = DadosAsync(cfg, agora=agora)
    app[DADOS] = dados

    async def ciclo(app):
        try:
            await dados.iniciar()
        except BaseException:
            await dados.fechar()
            raise
        async def manutencao():
            while True:
                await asyncio.sleep(60)
                await dados.chamar("limpar")
        task = asyncio.create_task(manutencao())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            await dados.fechar()
    app.cleanup_ctx.append(ciclo)
    app.router.add_post("/interno/conexoes", iniciar)
    app.router.add_get("/conectar", pagina)
    app.router.add_get("/api/fluxo", status)
    app.router.add_post("/api/login/{provedor}", login)
    app.router.add_get("/oauth/{provedor}/retorno", retorno)
    app.router.add_post("/api/usar", usar_conexao)
    app.router.add_get("/api/picker", picker)
    app.router.add_post("/api/selecionar", selecionar)
    app.router.add_post("/api/confirmar", confirmar)
    app.router.add_post("/api/cancelar", cancelar)
    app.router.add_get("/static/{nome}", estatico)
    app.router.add_get("/saude", saude)
    app.router.add_get("/erro", erro)
    return app
