"""Transporte restrito de cópia Drive. Nenhuma escrita Sheets ou compartilhamento."""
from dataclasses import dataclass
import json
import re
from urllib.parse import urlencode

import httpx

from .copias_banco import hash_texto

DRIVE = 'https://www.googleapis.com/drive/v3/files'
MIME = 'application/vnd.google-apps.spreadsheet'
ID = re.compile(r'[A-Za-z0-9_-]{20,200}\Z')
CAMPOS = 'id,mimeType,isAppAuthorized,trashed,version,modifiedTime,ownedByMe,shared,driveId,appProperties,permissions(type,role,deleted)'


@dataclass(frozen=True, repr=False)
class DestinoCopia:
    arquivo: str
    versao: str
    operacao: str
    origem: str
    # None = não observado; nunca serve de prova de equivalência.
    modificado: str | None = None

    def __post_init__(self):
        from .segredos import ErroCarteira
        from .provedores import MODIFICADO
        if self.modificado is not None and (type(self.modificado) is not str or
                                            not MODIFICADO.fullmatch(self.modificado)):
            raise ErroCarteira('Observação de cópia inválida.')
        if (any(not isinstance(s, str) or not ID.fullmatch(s) for s in (self.arquivo, self.origem)) or
                self.arquivo == self.origem or not isinstance(self.versao, str) or
                not re.fullmatch(r'[0-9]{1,30}', self.versao) or not isinstance(self.operacao, str) or
                not re.fullmatch(r'[a-f0-9]{64}', self.operacao)):
            raise ErroCarteira('Observação de cópia inválida.')


# Copiar a ficha completa passou de 15 s no Google real (30/10). Mais espera reduz
# a cópia incerta; sem resposta continua sendo recuperada pelo marcador, nunca repetida.
TIMEOUT_COPIA = 120
PRAZO_JOB_COPIA = 300


def marcadores(operacao, origem):
    from .provedores import ErroProvedor
    if (not isinstance(operacao, str) or not re.fullmatch(r'[a-f0-9]{64}', operacao) or
            not isinstance(origem, str) or not ID.fullmatch(origem)):
        raise ErroProvedor('arquivo')
    return dict(cv_operacao=operacao, cv_origem=hash_texto(origem), cv_protocolo='1')


async def enviar(provedor, acesso, operacao, origem):
    """Chamador precisa persistir enviada antes de entrar. Nunca retry do POST."""
    from .provedores import ErroProvedor
    props = marcadores(operacao, origem)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15, read=TIMEOUT_COPIA), follow_redirects=False,
                                     trust_env=False, transport=provedor.transporte) as client:
            async with client.stream('POST', DRIVE + '/' + origem + '/copy?fields=id',
                headers={'Authorization': 'Bearer ' + acesso}, json=dict(
                    name='Ficha — cópia em preparação', parents=['root'], appProperties=props)) as resp:
                if resp.status_code != 200:
                    raise ErroProvedor('copia_incerta')
                raw = bytearray()
                async for chunk in resp.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > 32768:
                        raise ErroProvedor('copia_incerta')
        obj = json.loads(raw)
        arquivo = obj.get('id') if isinstance(obj, dict) else None
        if not isinstance(arquivo, str) or not ID.fullmatch(arquivo) or arquivo == origem:
            raise ErroProvedor('copia_incerta')
        return arquivo
    except (httpx.HTTPError, ValueError, UnicodeError):
        # O Google pode ter criado o arquivo apesar da falha local. Não repetir.
        raise ErroProvedor('copia_incerta') from None


async def procurar(provedor, acesso, operacao, origem):
    from .provedores import ErroProvedor
    props = marcadores(operacao, origem)
    q = ' and '.join("appProperties has { key='%s' and value='%s' }" % (k, v)
                     for k, v in props.items())
    # Inclui lixeira: não criar outra cópia se o usuário tiver descartado esta.
    url = DRIVE + '?' + urlencode(dict(q=q, spaces='drive', corpora='user', pageSize=2,
        fields='files(id),nextPageToken,incompleteSearch'))
    obj = await provedor._json(url, acesso, limite=32768)
    if (not isinstance(obj, dict) or (obj.get('incompleteSearch') is not None and obj['incompleteSearch'] is not False) or
            obj.get('nextPageToken') or not isinstance(obj.get('files'), list)):
        raise ErroProvedor('copia_ambigua')
    arquivos = obj['files']
    if not arquivos:
        # Zero resultados não prova que um POST perdido não foi executado.
        raise ErroProvedor('copia_incerta')
    if len(arquivos) != 1 or not isinstance(arquivos[0], dict):
        raise ErroProvedor('copia_ambigua')
    arquivo = arquivos[0].get('id')
    if not isinstance(arquivo, str) or not ID.fullmatch(arquivo) or arquivo == origem:
        raise ErroProvedor('copia_ambigua')
    return arquivo


def _privada(meta, arquivo):
    from .provedores import ErroProvedor
    if (not isinstance(meta, dict) or meta.get('id') != arquivo or meta.get('mimeType') != MIME or
            meta.get('isAppAuthorized') is not True or meta.get('trashed') is not False or
            meta.get('ownedByMe') is not True or meta.get('shared') is not False or meta.get('driveId') is not None or
            not isinstance(meta.get('version'), str) or not re.fullmatch(r'[0-9]{1,30}', meta['version'])):
        raise ErroProvedor('copia_invalida')
    perms = meta.get('permissions')
    if (not isinstance(perms, list) or len(perms) != 1 or not isinstance(perms[0], dict) or
            perms[0].get('type') != 'user' or perms[0].get('role') != 'owner' or
            (perms[0].get('deleted') is not None and perms[0]['deleted'] is not False)):
        raise ErroProvedor('copia_invalida')
    return meta['version']


async def observar_fonte_diagnostico(provedor, acesso, arquivo):
    """Somente GET; origem privada derivada da operação, sem exigir marcador de cópia."""
    from .provedores import ErroProvedor
    if not isinstance(arquivo, str) or not ID.fullmatch(arquivo):
        raise ErroProvedor('arquivo')
    campos = CAMPOS.replace(',appProperties', '')
    meta = await provedor._json(DRIVE + '/' + arquivo + '?' + urlencode(dict(fields=campos)), acesso)
    return _privada(meta, arquivo)


async def observar(provedor, acesso, operacao, origem, arquivo):
    from .provedores import ErroProvedor
    props = marcadores(operacao, origem)
    if not isinstance(arquivo, str) or not ID.fullmatch(arquivo) or arquivo == origem:
        raise ErroProvedor('arquivo')
    meta = await provedor._json(DRIVE + '/' + arquivo + '?' + urlencode(dict(fields=CAMPOS)), acesso)
    _privada(meta, arquivo)
    if (not isinstance(meta.get('appProperties'), dict) or
            any(meta['appProperties'].get(k) != v for k, v in props.items())):
        raise ErroProvedor('copia_invalida')
    mod = meta.get('modifiedTime')
    from .provedores import MODIFICADO
    return DestinoCopia(arquivo, meta['version'], operacao, origem,
                        mod if isinstance(mod, str) and MODIFICADO.fullmatch(mod) else None)
