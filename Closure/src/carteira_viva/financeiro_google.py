"""Único POST das células financeiras; sem retry, notas globais ou PropertiesService."""
import json
import re

import httpx

from .financeiro_banco import EnvioFinanceiro
from .modelos import OFICIAIS
from .provedores import ErroProvedor, ARQUIVO
from .segredos import ErroCarteira


async def enviar(provedor, acesso, envio):
    if type(envio) is not EnvioFinanceiro:
        raise ErroCarteira('Envio financeiro não autorizado pelo diário.')
    oficiais = {re.search(r'/d/([A-Za-z0-9_-]+)', x['url']).group(1) for x in OFICIAIS}
    if not ARQUIVO.fullmatch(envio.arquivo) or envio.arquivo in oficiais:
        raise ErroCarteira('Destino de escrita proibido.')
    corpo = envio.consumir()
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False,
                                     transport=provedor.transporte) as client:
            async with client.stream('POST', 'https://sheets.googleapis.com/v4/spreadsheets/' +
                envio.arquivo + ':batchUpdate?fields=spreadsheetId', content=corpo,
                headers={'Authorization': 'Bearer '+acesso, 'Content-Type': 'application/json'}) as resp:
                if resp.status_code != 200:
                    raise ErroProvedor('escrita_incerta')
                raw = bytearray()
                async for chunk in resp.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > 32768:
                        raise ErroProvedor('escrita_incerta')
        obj = json.loads(raw)
        if not isinstance(obj, dict) or obj.get('spreadsheetId') != envio.arquivo:
            raise ErroProvedor('escrita_incerta')
    except (httpx.HTTPError, ValueError):
        raise ErroProvedor('escrita_incerta') from None
