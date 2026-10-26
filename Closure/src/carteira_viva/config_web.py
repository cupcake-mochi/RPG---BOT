"""Configuração exclusiva do serviço web. Não carrega o .env das Guias."""
from dataclasses import dataclass, field
import os
from pathlib import Path
from urllib.parse import urlsplit

from .segredos import Cifra, ErroCarteira


@dataclass(frozen=True)
class ConfigWeb:
    origem: str
    banco: Path
    chaves: tuple[bytes, ...] = field(repr=False)
    servico_token: str = field(repr=False)
    discord_id: str
    discord_secret: str = field(repr=False)
    discord_bot_token: str = field(repr=False)
    google_id: str
    google_secret: str = field(repr=False)
    projeto_google: str
    picker_key: str = field(repr=False)
    servidores: frozenset[str]
    desenvolvimento: bool = False
    dados_livro: Path | None = None
    campanhas: Path | None = None

    def __post_init__(self):
        u = urlsplit(self.origem)
        loopback = u.hostname in ("127.0.0.1", "localhost", "::1")
        if (u.username or u.password or u.path or u.query or u.fragment or not u.netloc or
                (u.scheme != "https" and not (self.desenvolvimento and loopback and u.scheme == "http"))):
            raise ErroCarteira("Use uma origem HTTPS; HTTP só é permitido no loopback de desenvolvimento.")
        if len(self.servico_token) < 32 or not self.servidores:
            raise ErroCarteira("Configure segredo de serviço e servidores de teste permitidos.")
        for valor in (self.discord_id, self.discord_secret, self.discord_bot_token,
                      self.google_id, self.google_secret, self.projeto_google, self.picker_key):
            if not isinstance(valor, str) or not valor.strip():
                raise ErroCarteira("Falta configuração de login/Picker.")
        Cifra(self.chaves)
        if (self.dados_livro is None) != (self.campanhas is None):
            raise ErroCarteira("Configure juntos o livro e o cadastro confiável de campanhas.")

    @property
    def segura(self):
        return urlsplit(self.origem).scheme == "https"

    @classmethod
    def do_ambiente(cls):
        def env(nome):
            valor = os.getenv("CARTEIRA_" + nome, "").strip()
            if not valor:
                raise ErroCarteira("Falta CARTEIRA_" + nome + ".")
            return valor
        return cls(origem=env("PUBLIC_ORIGIN"), banco=Path(env("DATABASE_PATH")),
                   chaves=tuple(x.strip().encode() for x in env("ENCRYPTION_KEYS").split(",")),
                   servico_token=env("SERVICE_TOKEN"), discord_id=env("DISCORD_CLIENT_ID"),
                   discord_secret=env("DISCORD_CLIENT_SECRET"), discord_bot_token=env("DISCORD_BOT_TOKEN"),
                   google_id=env("GOOGLE_CLIENT_ID"), google_secret=env("GOOGLE_CLIENT_SECRET"),
                   projeto_google=env("GOOGLE_PROJECT_NUMBER"), picker_key=env("PICKER_API_KEY"),
                   servidores=frozenset(x.strip() for x in env("GUILDS").split(",") if x.strip()),
                   desenvolvimento=os.getenv("CARTEIRA_DEV") == "1",
                   dados_livro=Path(os.environ["CARTEIRA_BOOK_DATA"]) if os.getenv("CARTEIRA_BOOK_DATA") else None,
                   campanhas=Path(os.environ["CARTEIRA_CAMPAIGNS_PATH"]) if os.getenv("CARTEIRA_CAMPAIGNS_PATH") else None)
