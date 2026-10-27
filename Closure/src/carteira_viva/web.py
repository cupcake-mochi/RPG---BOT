"""Conexão e API interna da galeria. Sem escrita de ficha ou conversa por IA."""
import asyncio
from contextlib import suppress
import hmac
import json
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
CONSULTAS = web.AppKey("consultas", object)
GALERIA = web.AppKey("galeria", object)
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
        if request.path == "/saude":
            resposta = await handler(request)
        else:
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
            status = (401 if codigo == "sessao" else 429 if codigo == "limite" else 403 if isinstance(exc, AcessoNegado) else
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
    if request.path.startswith(('/carteira','/api/carteira','/static/carteira.')):
        resposta.headers.update({'Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin','Vary':'Cookie',
            'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"})
    if cfg.segura:
        resposta.headers["Strict-Transport-Security"] = "max-age=31536000"
    if isinstance(resposta, web.HTTPException):
        raise resposta
    return resposta


async def corpo(request):
    if request.content_type != "application/json":
        raise ErroCarteira("Envie um formulário JSON.")
    data = json.loads(await limitado(request,16*1024))
    if not isinstance(data, dict):
        raise ErroCarteira("Solicitação inválida.")
    return data


async def limitado(request,tamanho):
    corpo=bytearray()
    async for b in request.content.iter_chunked(65536):
        corpo.extend(b)
        if len(corpo)>tamanho:
            raise web.HTTPRequestEntityTooLarge(max_size=tamanho,actual_size=len(corpo))
    return bytes(corpo)


def servico(request):
    if not hmac.compare_digest(request.headers.get('Authorization',''),'Bearer '+request.app[CFG].servico_token):
        raise AcessoNegado('Acesso de serviço inválido.')


async def api_galeria(request):
    servico(request)
    acao=request.match_info.get('acao','listar');pid=request.match_info.get('personagem')
    g=request.app[GALERIA]
    if acao=='enviar_imagem':
        if request.content_type!='application/octet-stream': raise ErroCarteira('Envie uma imagem.')
        s,u=request.headers.get('X-Carteira-Servidor',''),request.headers.get('X-Carteira-Usuario','')
        return resposta_json(await g.enviar_imagem(s,u,pid,await limitado(request,1024*1024)))
    d=await corpo(request)
    s,u=d.pop('servidor',None),d.pop('usuario',None)
    if not all(isinstance(x,str) and x.isdigit() and len(x)<=22 for x in (s,u)):
        raise ErroCarteira('Contexto de servidor inválido.')
    # Operações e argumentos fechados; nunca publicar DadosAsync.chamar.
    globais={'listar':(g.listar,{'dono','depois'}),'cargo_revisor':(g.cargo_revisor,{'cargo','permitir'})}
    locais={'cartao':(g.cartao,set()),'cartao_salvo':(g.cartao_salvo,set()),'detalhes':(g.detalhes,set()),
             'analisar':(g.detalhes,set()),'analise_salva':(g.analise_salva,set()),
             'editar':(g.editar,set()),'preparar':(g.preparar,{'alteracoes','campos_publicos','remover_imagem','base_esperada'}),
             'confirmar':(g.confirmar,{'previa'}),'cancelar':(g.cancelar,{'previa'}),'imagem':(g.imagem,{'previa'})}
    tabela=locais if pid is not None else globais
    if acao not in tabela: raise web.HTTPNotFound()
    fn,permitidos=tabela[acao]
    if set(d)-permitidos: raise ErroCarteira('Argumento não permitido.')
    args=(s,u,pid) if pid is not None else (s,u)
    from closure_bot.ficha_leitor import FichaIlegivel
    try:
        if acao=='analisar': d['analisar']=True
        result=await fn(*args,**d)
    except FichaIlegivel:
        return resposta_json({'erro':'leitura'},422)
    if acao=='imagem': return web.Response(body=result,content_type='image/webp')
    from .segredos import json_bytes
    if len(json_bytes(result))>8*1024*1024: raise ErroCarteira('A resposta privada ultrapassou o limite.')
    return resposta_json(result)


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


async def consultar(request):
    # Só a ponte autenticada do bot fornece o ator da interação. Nunca uma
    # identidade enviada diretamente pelo navegador e nunca despacho arbitrário.
    token = request.headers.get("Authorization", "")
    if not hmac.compare_digest(token, "Bearer " + request.app[CFG].servico_token):
        raise AcessoNegado("Acesso de serviço inválido.")
    data = await corpo(request)
    if set(data) != {"servidor", "usuario"}:
        raise ErroCarteira("Informe apenas o contexto da interação.")
    acoes = {"atualizar": "atualizar", "analisar": "analisar", "analise": "analise_salva"}
    metodo = acoes.get(request.match_info["acao"])
    if metodo is None:
        raise web.HTTPNotFound()
    from closure_bot.ficha_leitor import FichaIlegivel
    try:
        resultado = await getattr(request.app[CONSULTAS], metodo)(
            data["servidor"], data["usuario"], request.match_info["personagem"])
    except FichaIlegivel:
        # O diagnóstico detalhado pode conter dados escolhidos pelo jogador.
        return resposta_json({"erro": "leitura", "mensagem": "A ficha está incompleta ou recalculando. Confira a aba ANALISE e tente novamente."}, 422)
    except TimeoutError:
        return resposta_json({"erro": "temporario"}, 504)
    return resposta_json(resultado)


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
    if provider=='discord' and await request.app[DADOS].chamar('sessoes.tem_estado',state):
        from .web_carteira import retorno as retorno_carteira
        return await retorno_carteira(request,state)
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
    if nome not in ("conectar.js", "conectar.css", "carteira.js", "carteira.css"):
        raise web.HTTPNotFound()
    return web.Response(body=(STATIC / nome).read_bytes(), content_type="application/javascript" if nome.endswith(".js") else "text/css")


async def saude(request):
    return resposta_json({"servico": "carteira-viva", "estado": "online"})


async def erro(request):
    return web.Response(text="<html lang='pt-BR'><meta charset='utf-8'><title>Conexão encerrada</title>"
                             "<p>Esta conexão não pôde ser confirmada. Abra uma nova solicitação pelo Discord.</p></html>",
                        content_type="text/html")


def criar_app(cfg, *, provedores=None, agora=time.time, demonstracao=False, motor=None):
    if demonstracao and (cfg.segura or not cfg.desenvolvimento):
        raise ErroCarteira("A demonstração só pode rodar no loopback de desenvolvimento.")
    app = web.Application(middlewares=[guardas], client_max_size=2 * 1024 * 1024)
    app[CFG], app[PROVEDORES], app[LIMITE], app[DEMO] = cfg, provedores or Provedores(cfg, agora=agora), asyncio.Semaphore(8), demonstracao
    dados = DadosAsync(cfg, agora=agora)
    app[DADOS] = dados

    async def ciclo(app):
        try:
            await dados.iniciar()
        except BaseException:
            await dados.fechar()
            raise
        from .consultas import Consultas
        analisador = motor
        try:
            if analisador is None and cfg.dados_livro is not None:
                from .motor import Motor
                analisador = await asyncio.to_thread(Motor, cfg.dados_livro, cfg.campanhas)
            app[CONSULTAS] = Consultas(dados, app[PROVEDORES], analisador, agora=agora)
            from .galeria import Galeria
            from .imagens import Imagens
            from .segredos import Cifra
            imagens=Imagens(cfg.banco.parent/'imagens',Cifra(cfg.chaves),agora=agora)
            app[GALERIA]=Galeria(dados,app[PROVEDORES],app[CONSULTAS],imagens)
        except BaseException:
            await dados.fechar()
            raise
        async def manutencao():
            while True:
                await asyncio.sleep(60)
                await dados.chamar("limpar")
                await app[GALERIA].limpar()
        task = asyncio.create_task(manutencao())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            await app[CONSULTAS].fechar()
            await dados.fechar()
    app.cleanup_ctx.append(ciclo)
    app.router.add_post("/interno/conexoes", iniciar)
    app.router.add_post("/interno/personagens/{personagem}/{acao}", consultar)
    app.router.add_post('/interno/galeria',api_galeria)
    app.router.add_post('/interno/galeria/acao/{acao}',api_galeria)
    app.router.add_post('/interno/galeria/{personagem}/{acao}',api_galeria)
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
    from .web_carteira import registrar
    registrar(app)
    return app
