"""GIFs do seletor e links diretos para GIFs hospedados no Discord."""
from __future__ import annotations

import asyncio
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit

from .midia import URL
from .midia_preparar import MAX_BYTES

PROVEDORES = {'klipy.com': 'klipy', 'tenor.com': 'tenor', 'giphy.com': 'giphy'}
CDNS = {'static.klipy.com': 'klipy', 'static1.klipy.com': 'klipy', 'static2.klipy.com': 'klipy',
        'media.tenor.com': 'tenor', 'media1.tenor.com': 'tenor', 'media.giphy.com': 'giphy', 'i.giphy.com': 'giphy',
        **{f'media{i}.giphy.com': 'giphy' for i in range(5)}}
PROXIES = {'images-ext-1.discordapp.net', 'images-ext-2.discordapp.net', 'media.discordapp.net'}


class Indisponivel(ValueError):
    def __init__(self, status):
        self.status = status
        super().__init__('mídia indisponível')


def _url(url):
    if not isinstance(url, str) or len(url) > 2048 or re.search(r'[\s\\\x00-\x1f]', url):
        return None
    try:
        p = urlsplit(url)
        if p.scheme == 'https' and p.hostname and not p.username and not p.password and p.port in (None, 443):
            return p
    except ValueError:
        pass
    return None


def pagina(url):
    """Identidade do link; não navega nem reconstrói URLs de entrega."""
    p = _url(url)
    if not p:
        return None
    host = p.hostname.removeprefix('www.')
    provedor = PROVEDORES.get(host)
    caminho = p.path.rstrip('/')
    if provedor == 'tenor':
        match = re.fullmatch(r'/(?:[a-z]{2}(?:-[A-Z]{2})?/)?view/(?:[\w-]+-)?([0-9]{1,20})', caminho, re.ASCII)
        return (provedor, match[1]) if match else None
    if provedor and re.fullmatch(r'/gifs/[\w-]+', caminho, re.ASCII):
        return provedor, caminho
    return None


def gif_discord(url):
    """Reconhece só arquivo GIF de anexo; preserva a assinatura da URL."""
    p = _url(url)
    return bool(p and p.hostname in {'cdn.discordapp.com', 'media.discordapp.net'}
                and re.fullmatch(r'/attachments/[0-9]+/[0-9]+/[^/]+\.gif', p.path, re.I))


def links(mensagem):
    texto = getattr(mensagem, 'content', '')
    if not isinstance(texto, str):
        return []
    urls = (u.rstrip('.,!?)]') for u in URL.findall(texto))
    return list(dict.fromkeys(u for u in urls if pagina(u) or gif_discord(u)))


def tipo_midia(url, provedor):
    p = _url(url)
    if not p:
        return None
    if p.hostname in PROXIES and p.path.startswith('/external/'):
        partes = p.path.split('/', 4)
        if len(partes) != 5 or partes[1] != 'external' or not re.fullmatch(r'[\w-]+', partes[2], re.ASCII) or partes[3] != 'https':
            return None
        p = _url('https://' + partes[4])
        if not p:
            return None
    if provedor == 'discord':
        return 'imagem' if gif_discord(p.geturl()) else None
    if CDNS.get(p.hostname) != provedor or not re.fullmatch(r'/[A-Za-z0-9_./-]+', p.path):
        return None
    if any(s in ('.', '..') for s in p.path.split('/')):
        return None
    return 'imagem' if p.path.endswith('.gif') else 'gif_video' if p.path.endswith('.mp4') else None


def escolher(mensagem, link):
    ident = pagina(link)
    if not ident:
        return None
    for embed in list(getattr(mensagem, 'embeds', ()) or ())[:10]:
        if pagina(getattr(embed, 'url', '')) != ident:
            continue
        # GIF animado evita a conversão MP4; PNG/JPEG de prévia não serve.
        for campo in ('image', 'thumbnail', 'video'):
            parte = getattr(embed, campo, None)
            for chave in ('proxy_url', 'url'):
                url = getattr(parte, chave, None)
                tipo = tipo_midia(url, ident[0])
                if tipo:
                    return url, tipo
    return None


def _anexo(url):
    p = _url(url)
    if not p:
        return None
    if p.hostname in PROXIES and p.path.startswith('/external/'):
        partes = p.path.split('/', 4)
        if len(partes) != 5 or partes[3] != 'https' or not re.fullmatch(r'[\w-]+', partes[2], re.ASCII):
            return None
        p = _url('https://' + partes[4])
    return p.path if p and gif_discord(p.geturl()) else None


def escolher_discord(mensagem, link):
    alvo = _anexo(link)
    if not alvo:
        return None
    for embed in list(getattr(mensagem, 'embeds', ()) or ())[:10]:
        for campo in ('image', 'thumbnail'):
            parte = getattr(embed, campo, None)
            # Ignora título/ordens externas; o caminho do arquivo deve ser idêntico.
            for chave in ('url', 'proxy_url'):
                url = getattr(parte, chave, None)
                if url != link and _anexo(url) == alvo and tipo_midia(url, 'discord'):
                    return url, 'imagem'
    return None


async def _reler(mensagem):
    buscar = getattr(getattr(mensagem, 'channel', None), 'fetch_message', None)
    if not callable(buscar):
        raise ValueError('prévia indisponível')
    import discord
    try:
        await asyncio.sleep(0.6)
        return await asyncio.wait_for(buscar(mensagem.id), timeout=2)
    except (discord.HTTPException, OSError, TimeoutError):
        raise ValueError('prévia indisponível') from None


async def resolver_discord(mensagem, link):
    escolhido = escolher_discord(mensagem, link)
    if escolhido:
        return escolhido
    atual = await _reler(mensagem)
    if link not in links(atual):
        raise ValueError('mensagem alterada')
    escolhido = escolher_discord(atual, link)
    if not escolhido:
        raise ValueError('prévia sem endereço válido para o mesmo GIF')
    return escolhido


class _Metas(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag != 'meta' or len(self.urls) >= 16:
            return
        attrs = dict(attrs)
        if attrs.get('property') in ('og:image', 'og:video', 'og:video:secure_url'):
            url = attrs.get('content')
            tipo = tipo_midia(url, 'tenor')
            if tipo:
                self.urls.append((url, tipo))


def metadados_tenor(html):
    parser = _Metas(); parser.feed(html)
    if not parser.urls:
        raise ValueError('página sem GIF compatível')
    return next((p for p in parser.urls if p[1] == 'imagem'), parser.urls[0])


async def pagina_tenor(link):
    """Reserva para prévia ausente; somente metadados da página Tenor pedida."""
    import aiohttp
    ident = pagina(link)
    if not ident or ident[0] != 'tenor':
        raise ValueError('página não permitida')
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as sessao:
            async with sessao.get(link, allow_redirects=False) as resposta:
                if resposta.status != 200 or (resposta.content_length or 0) > 262144:
                    raise ValueError('página indisponível')
                dados = bytearray()
                async for parte in resposta.content.iter_chunked(8192):
                    dados.extend(parte)
                    if len(dados) > 262144:
                        raise ValueError('página grande')
    except aiohttp.ClientError:
        raise ValueError('página indisponível') from None
    return metadados_tenor(dados.decode('utf-8', errors='replace'))


async def resolver(mensagem, link):
    escolhido = escolher(mensagem, link)
    if escolhido:
        return escolhido
    # A prévia pode chegar após MESSAGE_CREATE. Uma única releitura, sem
    # responder novamente a MESSAGE_UPDATE e sem buscar páginas arbitrárias.
    try:
        atual = await _reler(mensagem)
    except ValueError:
        atual = mensagem
    if link not in links(atual):
        raise ValueError('mensagem alterada')
    escolhido = escolher(atual, link)
    if escolhido:
        return escolhido
    if pagina(link) and pagina(link)[0] == 'tenor':
        return await pagina_tenor(link)
    raise ValueError('prévia sem animação compatível')


async def baixar(url, provedor):
    import aiohttp
    if not tipo_midia(url, provedor):
        raise ValueError('origem não permitida')
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as sessao:
            async with sessao.get(url, allow_redirects=False) as resposta:
                if resposta.status != 200:
                    raise Indisponivel(resposta.status)
                if (resposta.content_length or 0) > MAX_BYTES:
                    raise ValueError('GIF grande')
                dados = bytearray()
                async for parte in resposta.content.iter_chunked(65536):
                    dados.extend(parte)
                    if len(dados) > MAX_BYTES:
                        raise ValueError('GIF grande')
                return bytes(dados)
    except aiohttp.ClientError:
        raise ValueError('GIF indisponível') from None
