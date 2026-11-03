"""Leitura do pulso de ativação: um GET em spreadsheets.get, nunca escrita.

O produtor grava `r53_pulso_<rotina>` nos metadados de desenvolvedor da
planilha, com visibilidade DOCUMENT (r53/inicializacao/ativacao.gs, PR31 da
ficha). `spreadsheets.get` aceita `drive.file`. O bot não cria, altera nem
apaga esses metadados: ver testes/test_carteira_pulso_sem_escrita.py.
"""
import json
from urllib.parse import urlencode

from .atestado_ativacao import TIPOS, Pulso
from .provedores import ARQUIVO, ErroProvedor
from .segredos import ErroCarteira

PREFIXO = 'r53_pulso_'
CAMPOS = 'spreadsheetId,developerMetadata(metadataKey,metadataValue,visibility,location(locationType))'
MAX_ITENS = 5
MAX_VALOR = 4096


async def ler(provedor, acesso, arquivo):
    """Devolve (pulsos, problema); problema é 'pulso_ilegivel', 'pulso_duplicado' ou None."""
    if not isinstance(arquivo, str) or not ARQUIVO.fullmatch(arquivo):
        raise ErroProvedor('arquivo')
    obj = await provedor._json('https://sheets.googleapis.com/v4/spreadsheets/' + arquivo + '?' +
                               urlencode({'fields': CAMPOS}), acesso, limite=256 * 1024)
    if not isinstance(obj, dict) or obj.get('spreadsheetId') != arquivo:
        raise ErroProvedor('arquivo')
    metas = obj.get('developerMetadata', [])
    if not isinstance(metas, list):
        return (), 'pulso_ilegivel'
    vistos, pulsos = set(), []
    for m in metas:
        chave = m.get('metadataKey') if isinstance(m, dict) else None
        if not isinstance(chave, str) or not chave.startswith(PREFIXO):
            continue  # metadados alheios ao pulso ficam fora da leitura
        rotina = chave[len(PREFIXO):]
        if chave in vistos:
            return (), 'pulso_duplicado'
        vistos.add(chave)
        local = m.get('location')
        valor = m.get('metadataValue')
        if (rotina not in TIPOS or m.get('visibility') != 'DOCUMENT' or not isinstance(local, dict) or
                local.get('locationType') != 'SPREADSHEET' or not isinstance(valor, str) or len(valor) > MAX_VALOR):
            return (), 'pulso_ilegivel'
        try:
            d = json.loads(valor)
            if (not isinstance(d, dict) or set(d) != {'versao', 'itens'} or d['versao'] != 1 or
                    not isinstance(d['itens'], list) or not 1 <= len(d['itens']) <= MAX_ITENS):
                return (), 'pulso_ilegivel'
            itens = [Pulso.de_dados(i) for i in d['itens']]
        except (ValueError, TypeError, RecursionError, ErroCarteira):
            return (), 'pulso_ilegivel'
        if any(p.rotina != rotina for p in itens):
            return (), 'pulso_ilegivel'
        pulsos.extend(itens)
    return tuple(pulsos), None
