"""Contrato público local, exportado pelo produtor. Não aceita JSON do cliente."""
import hashlib
import json
from pathlib import Path
from .segredos import ErroCarteira

CONTRATO_SHA256 = '0c9dcc89e6b1cb3401a54fb1311d9f72c60774cbec84d741474a7a6066bd8098'
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
