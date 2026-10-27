"""Carteira web: sessão identificada, projeções mínimas e ações fechadas."""
import asyncio
from contextlib import suppress
from pathlib import Path
import re
import secrets
from urllib.parse import urlencode

from aiohttp import web
from .segredos import AcessoNegado, ErroCarteira
from .sessoes import SessaoEncerrada, nome_cookie

STATIC=Path(__file__).with_name('static')
PID=re.compile(r'[a-f0-9]{32}\Z')


def contexto(request):
    from .web import CFG
    gid=request.match_info['servidor']
    pid=request.match_info.get('personagem')
    if gid not in request.app[CFG].servidores or (pid is not None and not PID.fullmatch(pid)):
        raise web.HTTPNotFound(text='{"erro":"acesso"}',content_type='application/json')
    return gid,pid


def sid(request):
    from .web import CFG
    return request.cookies.get(nome_cookie(request.app[CFG].segura),'')


async def banco(request,metodo,*a,**kw):
    from .web import DADOS
    return await request.app[DADOS].chamar('sessoes.'+metodo,*a,**kw)


def cookie(out,request,valor):
    from .web import CFG
    out.set_cookie(nome_cookie(request.app[CFG].segura),valor,path='/',max_age=28800,
                   secure=request.app[CFG].segura,httponly=True,samesite='Lax')


async def identidade(request,*,mutacao=False):
    from .web import PROVEDORES,csrf
    gid,_=contexto(request)
    uid=await banco(request,'identidade',sid(request),csrf(request) if mutacao else None)
    try:m=await request.app[PROVEDORES].membro(gid,uid)
    except AcessoNegado:
        await banco(request,'invalidar',sid(request));raise SessaoEncerrada('A participação mudou.') from None
    return m


async def finalizar(request,m,data):
    from .web import PROVEDORES,resposta_json
    # A saída só é emitida se logout/expiração/saída não ocorreram na espera.
    try:await request.app[PROVEDORES].membro(m.servidor,m.usuario)
    except AcessoNegado:
        await banco(request,'invalidar',sid(request));raise SessaoEncerrada('A participação mudou.') from None
    s=await banco(request,'conferir',sid(request),m.usuario,tocar=True)
    out=resposta_json(data);out.headers['X-Carteira-Expira-Em']=str(s['expira_em'])
    return out


async def pagina(request):
    if 'servidor' not in request.match_info:
        return web.Response(text=(STATIC/'carteira.html').read_text(),content_type='text/html')
    contexto(request)
    novo=secrets.token_urlsafe(32)
    trocar=await banco(request,'abrir',sid(request),novo)
    out=web.Response(text=(STATIC/'carteira.html').read_text(),content_type='text/html')
    if trocar:cookie(out,request,novo)
    return out


async def estado(request):
    from .web import DADOS,DEMO,resposta_json
    contexto(request);s=await banco(request,'estado',sid(request))
    s['demonstracao']=request.app[DEMO];s['idioma']='pt-BR'
    if not s['autenticado']:return resposta_json(s)
    m=await identidade(request)
    s['nome']=m.nome
    s['idioma']=await request.app[DADOS].chamar('cadastro.idioma_carteira',m)
    return await finalizar(request,m,s)


async def entrar(request):
    from .web import PROVEDORES,corpo,csrf,resposta_json
    gid,_=contexto(request);d=await corpo(request)
    if set(d)-{'personagem','idioma'} or d.get('idioma','pt-BR') not in ('pt-BR','en'):raise ErroCarteira('Campos inesperados.')
    pid=d.get('personagem')
    if pid is not None and (not isinstance(pid,str) or not PID.fullmatch(pid)):raise ErroCarteira('Personagem inválido.')
    o=await banco(request,'login',sid(request),csrf(request),gid,pid,idioma=d.get('idioma'))
    return resposta_json({'url':request.app[PROVEDORES].autorizar('discord',o['estado'],o['verificador'])})


async def retorno(request,state):
    from .web import PROVEDORES,CFG
    destino='/carteira';consumido=False
    try:
        o=await banco(request,'consumir',sid(request),state);consumido=True
        destino='/carteira/'+o['servidor']+('/'+o['personagem'] if o['personagem'] else '')
        if o.get('idioma'):destino+='?'+urlencode({'idioma':o['idioma']})
        if 'error' in request.query or not request.query.get('code'):raise AcessoNegado('Login cancelado.')
        retorno=request.app[CFG].origem+request.path+'?'+urlencode(list(request.query.items()))
        token=await request.app[PROVEDORES].trocar_codigo('discord',estado=state,verificador=o['verificador'],retorno=retorno)
        user=await request.app[PROVEDORES].usuario_discord(token['access_token'])
        await request.app[PROVEDORES].membro(o['servidor'],user)
        novo=secrets.token_urlsafe(32)
        await banco(request,'finalizar',sid(request),state,novo,user)
        out=web.HTTPFound(destino);cookie(out,request,novo);return out
    except ErroCarteira:
        # Um state de outra pessoa não pode causar logout da sessão atual.
        if consumido:await banco(request,'invalidar',sid(request))
        return web.HTTPFound(destino+('&' if '?' in destino else '?')+'erro=conexao')


async def sair(request):
    from .web import CFG,corpo,csrf,resposta_json
    d=await corpo(request)
    if d:raise ErroCarteira('Campos inesperados.')
    await banco(request,'sair',sid(request),csrf(request))
    out=resposta_json({'ok':True});out.del_cookie(nome_cookie(request.app[CFG].segura),path='/')
    return out


async def galeria(request):
    from .web import GALERIA
    if set(request.query)-{'dono','depois'}:raise ErroCarteira('Campos inesperados.')
    m=await identidade(request)
    d=await request.app[GALERIA].listar(m.servidor,m.usuario,**dict(request.query))
    return await finalizar(request,m,d)


async def cartao(request):
    from .web import GALERIA
    m=await identidade(request);_,pid=contexto(request)
    return await finalizar(request,m,await request.app[GALERIA].cartao_salvo(m.servidor,m.usuario,pid))


def apresentar(bundle,idioma,pagina,analisar):
    # O mesmo apresentador usado no Discord; não reimplementa as contas.
    from .discord_ui import paginas_privadas
    ps=paginas_privadas(bundle,idioma,analisar)
    if type(pagina) is not int or not 0<=pagina<len(ps):raise ErroCarteira('Página inválida.')
    p=ps[pagina]
    return {'pagina':pagina,'total':len(ps),'titulo':p.title,'descricao':p.description or '',
            'campos':[{'nome':f.name,'valor':f.value} for f in p.fields],
            'rodape':(p.footer.text or '').replace(' · controles por 10 min','').replace(' · controls for 10 min',''),'cor':p.colour.value if p.colour else 0,
            'arquivo':'https://docs.google.com/spreadsheets/d/'+bundle['arquivo']+'/edit',
            'lido_em':bundle['leitura']['lido_em']}


async def acao(request):
    from .web import GALERIA,corpo
    from closure_bot.ficha_leitor import FichaIlegivel
    m=await identidade(request,mutacao=True);_,pid=contexto(request);d=await corpo(request)
    if set(d)-{'pagina','idioma'} or d.get('idioma','pt-BR') not in ('pt-BR','en'):
        raise ErroCarteira('Campos inesperados.')
    g=request.app[GALERIA];a=request.match_info['acao']
    try:
        if a=='atualizar':
            if d:raise ErroCarteira('Campos inesperados.')
            c=await g.cartao_salvo(m.servidor,m.usuario,pid)
            if not c['capacidades']['ver_detalhes']:raise AcessoNegado('Somente cartão básico.')
            return await finalizar(request,m,await g.cartao(m.servidor,m.usuario,pid))
        if a not in ('detalhes','analisar','analise'):raise web.HTTPNotFound()
        if a!='analise' and d.get('pagina',0)!=0:raise ErroCarteira('Comece pela primeira página.')
        b=await g.analise_salva(m.servidor,m.usuario,pid) if a=='analise' else await g.detalhes(m.servidor,m.usuario,pid,analisar=a=='analisar')
        await banco(request,'conferir',sid(request),m.usuario)
        data=await asyncio.to_thread(apresentar,b,d.get('idioma','pt-BR'),d.get('pagina',0),a!='detalhes')
        # Conversão pode levar tempo; revalidar a análise antes de devolver.
        if a!='detalhes':
            atual=await g.analise_salva(m.servidor,m.usuario,pid)
            if atual['analise']!=b['analise']:raise ErroCarteira('A análise mudou. Abra novamente.')
        else:
            membro=await g.membro(m.servidor,m.usuario);await g._dono(membro,pid)
            atual=await g.banco('detalhes',membro,pid)
            if not atual['leitura'] or atual['leitura']['id']!=b['leitura']['id']:raise ErroCarteira('A leitura mudou.')
        return await finalizar(request,m,data)
    except FichaIlegivel:
        from .web import resposta_json
        return resposta_json({'erro':'leitura'},422)


async def imagem(request):
    from .web import GALERIA
    m=await identidade(request);_,pid=contexto(request)
    b=await request.app[GALERIA].imagem(m.servidor,m.usuario,pid)
    await banco(request,'conferir',sid(request),m.usuario)
    return web.Response(body=b,content_type='image/webp')


def registrar(app):
    app.router.add_get('/carteira',pagina)
    app.router.add_get('/carteira/{servidor}',pagina)
    app.router.add_get('/carteira/{servidor}/{personagem}',pagina)
    app.router.add_get('/api/carteira/{servidor}/sessao',estado)
    app.router.add_post('/api/carteira/{servidor}/entrar',entrar)
    app.router.add_post('/api/carteira/sair',sair)
    app.router.add_get('/api/carteira/{servidor}/galeria',galeria)
    app.router.add_get('/api/carteira/{servidor}/personagens/{personagem}',cartao)
    app.router.add_get('/api/carteira/{servidor}/personagens/{personagem}/imagem',imagem)
    app.router.add_post('/api/carteira/{servidor}/personagens/{personagem}/{acao}',acao)
