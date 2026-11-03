"""Contrato público local, exportado pelo produtor. Não aceita JSON do cliente."""
import hashlib
import json
from pathlib import Path
from .segredos import ErroCarteira

CONTRATO_SHA256 = '948f9a3d3f83ada52bfbdba13840cd5ee67034bac34101dbca988ea29c3d4f60'
CAMINHO = Path(__file__).resolve().parents[2] / 'dados/ficha/inicializacao-rest-v1.json'


def carregar():
    raw = CAMINHO.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CONTRATO_SHA256:
        raise ErroCarteira('Contrato de inicialização mudou. Revise a integração antes de continuar.')
    c = json.loads(raw)
    if c['protocolo'] != 'carteira-contrato-rest-1' or any(c[k] is not False for k in
            ('criacaoDisponivel', 'conferenciaConjuntaConcluida', 'consistenciaTemporalVerificada', 'imagensAtuaisConferidas')):
        raise ErroCarteira('Contrato de inicialização incompatível.')
    return c
