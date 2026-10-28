"""Contrato público local, exportado pelo produtor. Não aceita JSON do cliente."""
import hashlib
import json
from pathlib import Path
from .segredos import ErroCarteira

CONTRATO_SHA256 = '1001e7c3605c754b5bf04c33cfd65542c90ef4b897deffda40167a2bafb30439'
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
