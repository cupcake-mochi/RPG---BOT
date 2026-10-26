"""Cifra obrigatória, envelopes ligados ao contexto e suporte a chaves antigas."""
import json

from cryptography.fernet import Fernet, InvalidToken, MultiFernet


class ErroCarteira(ValueError):
    pass


class AcessoNegado(ErroCarteira):
    pass


class Conflito(ErroCarteira):
    pass


def json_bytes(valor) -> bytes:
    try:
        return json.dumps(valor, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError):
        raise ErroCarteira("Conteúdo não pode ser armazenado neste formato.") from None


class Cifra:
    def __init__(self, chaves: tuple[bytes, ...]):
        if not chaves:
            raise ErroCarteira("Configure uma chave de cifra própria da Carteira.")
        try:
            self.fernet = MultiFernet([Fernet(chave) for chave in chaves])
        except (ValueError, TypeError):
            raise ErroCarteira("Chave de cifra inválida.") from None

    def cifrar(self, contexto: list[str], valor) -> bytes:
        return self.fernet.encrypt(json_bytes({"contexto": contexto, "valor": valor}))

    def abrir(self, contexto: list[str], envelope: bytes):
        try:
            obj = json.loads(self.fernet.decrypt(envelope))
            if obj["contexto"] != contexto:
                raise ErroCarteira("Envelope pertence a outro contexto.")
            return obj["valor"]
        except (InvalidToken, ValueError, TypeError, KeyError) as exc:
            if isinstance(exc, ErroCarteira):
                raise
            raise ErroCarteira("Não foi possível abrir os dados cifrados.") from None
