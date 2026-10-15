"""GIFs do seletor: somente a mídia da prévia do Discord vinculada ao link."""
from __future__ import annotations

import asyncio
import re
from urllib.parse import urlsplit

from .midia import URL
from .midia_preparar import MAX_BYTES

PROVEDORES = {'klipy.com': 'klipy', 'tenor.com': 'tenor', 'giphy.com': 'giphy'}
CDNS = {'static.klipy.com': 'klipy', 'static1.klipy.com': 'klipy', 'static2.klipy.com': 'klipy',
        'media.tenor.com': 'tenor', 'media.giphy.com': 'giphy', 'i.giphy.com': 'giphy',
        **{f'media{i}.giphy.com': 'giphy' for i in range(5)}}
PROXIES = {'images-ext-1.discordapp.net', 'images-ext-2.discordapp.net', 'media.discordapp.net'}


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
    padrao = r'/(?:[a-z]{2}(?:-[A-Z]{2})?/)?view/[\w-]+' if provedor == 'tenor' else r'/gifs/[\w-]+'
    if provedor and re.fullmatch(padrao, caminho, re.ASCII):
        return provedor, caminho
    return None


def links(mensagem):
    texto = getattr(mensagem, 'content', '')
    if not isinstance(texto, str):
        return []
    return list(dict.fromkeys(u.rstrip('.,!?)]') for u in URL.findall(texto)
                             if pagina(u.rstrip('.,!?)]'))))


def tipo_midia(url, provedor):
    p = _url(url)
    if not p:
        return None
    if p.hostname in PROXIES:
        partes = p.path.split('/', 4)
        if len(partes) != 5 or partes[1] != 'external' or not re.fullmatch(r'[\w-]+', partes[2], re.ASCII) or partes[3] != 'https':
            return None
        p = _url('https://' + partes[4])
        if not p:
            return None
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
        # Vídeo representa a animação; miniatura PNG/JPEG não serve de GIF.
        for campo in ('video', 'image', 'thumbnail'):
            parte = getattr(embed, campo, None)
            for chave in ('proxy_url', 'url'):
                url = getattr(parte, chave, None)
                tipo = tipo_midia(url, ident[0])
                if tipo:
                    return url, tipo
    return None


async def resolver(mensagem, link):
    escolhido = escolher(mensagem, link)
    if escolhido:
        return escolhido
    # A prévia pode chegar após MESSAGE_CREATE. Uma única releitura, sem
    # responder novamente a MESSAGE_UPDATE e sem buscar páginas arbitrárias.
    buscar = getattr(getattr(mensagem, 'channel', None), 'fetch_message', None)
    if not callable(buscar):
        raise ValueError('prévia indisponível')
    import discord
    try:
        await asyncio.sleep(0.6)
        atual = await asyncio.wait_for(buscar(mensagem.id), timeout=2)
    except (discord.HTTPException, OSError, TimeoutError):
        raise ValueError('prévia indisponível') from None
    if link not in links(atual):
        raise ValueError('mensagem alterada')
    escolhido = escolher(atual, link)
    if not escolhido:
        raise ValueError('prévia sem animação compatível')
    return escolhido


async def baixar(url, provedor):
    import aiohttp
    if not tipo_midia(url, provedor):
        raise ValueError('origem não permitida')
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as sessao:
            async with sessao.get(url, allow_redirects=False) as resposta:
                if resposta.status != 200 or (resposta.content_length or 0) > MAX_BYTES:
                    raise ValueError('GIF indisponível ou grande')
                dados = bytearray()
                async for parte in resposta.content.iter_chunked(65536):
                    dados.extend(parte)
                    if len(dados) > MAX_BYTES:
                        raise ValueError('GIF grande')
                return bytes(dados)
    except aiohttp.ClientError:
        raise ValueError('GIF indisponível') from None
