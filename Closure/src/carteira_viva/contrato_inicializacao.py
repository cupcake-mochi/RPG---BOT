"""Contrato público local, exportado pelo produtor. Não aceita JSON do cliente."""
import hashlib
import json
from pathlib import Path
from .segredos import ErroCarteira

CONTRATO_SHA256 = 'e41de3e441156e97bd4f44b1deefdac0d0c43b756aa06081d4a189229c6fba86'
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
