"""OAuth e leituras mínimas em provedores oficiais; sem escrita em planilhas."""
from dataclasses import dataclass, field
import json
import math
import logging
import re
import secrets
import time
from urllib.parse import quote

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.base_client.errors import OAuthError
from authlib.oauth2.rfc6749.errors import OAuth2Error
import httpx

from .config_web import ConfigWeb
from .permissoes import Membro
from .segredos import AcessoNegado, ErroCarteira

DRIVE_FILE = "https://www.googleapis.com/auth/drive.file"
MIME = "application/vnd.google-apps.spreadsheet"
DISCORD = "https://discord.com/api/v10"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
AUTORIZAR = {"discord": "https://discord.com/oauth2/authorize",
             "google": "https://accounts.google.com/o/oauth2/v2/auth"}
ARQUIVO = re.compile(r"[A-Za-z0-9_-]{20,200}\Z")
SNOWFLAKE = re.compile(r"[0-9]{1,22}\Z")


class ErroProvedor(ErroCarteira):
    def __init__(self, codigo="provedor"):
        self.codigo = codigo
        super().__init__("Não foi possível confirmar o acesso. Reabra a conexão ou tente novamente.")


@dataclass(frozen=True)
class TokenGoogle:
    acesso: str = field(repr=False)
    refresh: str | None = field(repr=False)
    expira: float


class Provedores:
    def __init__(self, cfg: ConfigWeb, *, transporte=None, agora=time.time):
        self.cfg, self.transporte, self.agora = cfg, transporte, agora

    def _cliente(self, provedor, estado=None):
        google = provedor == "google"
        return AsyncOAuth2Client(
            self.cfg.google_id if google else self.cfg.discord_id,
            self.cfg.google_secret if google else self.cfg.discord_secret,
            token_endpoint_auth_method="client_secret_post", state=estado,
            scope=DRIVE_FILE if google else "identify", code_challenge_method="S256",
            redirect_uri=self.cfg.origem + f"/oauth/{provedor}/retorno",
            timeout=15, follow_redirects=False, trust_env=False, transport=self.transporte)

    def autorizar(self, provedor: str, estado: str, verificador: str) -> str:
        if provedor not in AUTORIZAR:
            raise ErroProvedor()
        # create_authorization_url não realiza rede. Fecha-se o cliente no callback
        # real; aqui usamos o núcleo OAuth sem abrir um pool HTTP.
        from authlib.oauth2.client import OAuth2Client
        google = provedor == "google"
        client = OAuth2Client(None, client_id=self.cfg.google_id if google else self.cfg.discord_id,
                              scope=DRIVE_FILE if google else "identify",
                              redirect_uri=self.cfg.origem + f"/oauth/{provedor}/retorno",
                              code_challenge_method="S256")
        extras = {"access_type": "offline", "prompt": "consent select_account",
                  "include_granted_scopes": "false"} if google else {}
        url, _ = client.create_authorization_url(AUTORIZAR[provedor], state=estado,
                                                  code_verifier=verificador, **extras)
        return url

    async def trocar_codigo(self, provedor, *, estado, verificador, retorno):
        endpoint = GOOGLE_TOKEN if provedor == "google" else DISCORD + "/oauth2/token"
        try:
            async with self._cliente(provedor, estado) as client:
                token = await client.fetch_token(endpoint, authorization_response=retorno,
                                                  code_verifier=verificador)
        except (OAuthError, OAuth2Error) as exc:
            erro = exc.error if exc.error in {"invalid_client", "invalid_grant", "invalid_request", "invalid_scope", "access_denied", "unauthorized_client", "unsupported_grant_type"} else type(exc).__name__
            logging.getLogger(__name__).warning("Retorno OAuth %s recusado (%s)", provedor, erro)
            raise ErroProvedor("oauth") from None
        except (httpx.HTTPError, ValueError) as exc:
            logging.getLogger(__name__).warning("Retorno OAuth %s indisponível (%s)", provedor, type(exc).__name__)
            raise ErroProvedor("oauth") from None
        esperado = {DRIVE_FILE} if provedor == "google" else {"identify"}
        # O Discord inclui applications.commands já concedido pela instalação.
        # O login só pede/usa identify; nenhum outro escopo extra é aceito.
        permitido = esperado | ({"applications.commands"} if provedor == "discord" else set())
        scope = token.get("scope")
        if scope is not None and (not isinstance(scope, str) or not esperado <= set(scope.split()) <= permitido):
            valores = set(scope.split()) if isinstance(scope, str) else set()
            nomes = valores & {"identify", "applications.commands", "bot", "email", "guilds", "connections", DRIVE_FILE}
            logging.getLogger(__name__).warning("Escopo OAuth %s recusado (tipo=%s, conhecidos=%s, outros=%d)",
                                                provedor, type(scope).__name__, ",".join(sorted(nomes)), len(valores - nomes))
            raise ErroProvedor("escopo")
        if not isinstance(token.get("access_token"), str) or not token["access_token"]:
            raise ErroProvedor("oauth")
        return token

    def token_google(self, token: dict) -> TokenGoogle:
        expira = token.get("expires_at")
        if expira is None and type(token.get("expires_in")) in (int, float):
            expira = self.agora() + token["expires_in"]
        if (type(expira) not in (int, float) or not math.isfinite(expira) or
                expira <= self.agora() + 30 or not isinstance(token.get("access_token"), str)):
            raise ErroProvedor("expirado")
        refresh = token.get("refresh_token")
        if refresh is not None and (not isinstance(refresh, str) or not refresh):
            raise ErroProvedor("oauth")
        return TokenGoogle(token["access_token"], refresh, expira)

    async def _json(self, url: str, token: str, *, bot=False):
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False,
                                         transport=self.transporte) as client:
                async with client.stream("GET", url, headers={"Authorization": ("Bot " if bot else "Bearer ") + token}) as resp:
                    if resp.status_code != 200:
                        raise ErroProvedor("acesso" if resp.status_code in (401, 403, 404) else "temporario")
                    corpo = bytearray()
                    async for bloco in resp.aiter_bytes():
                        corpo.extend(bloco)
                        if len(corpo) > 512 * 1024:
                            raise ErroProvedor("tamanho")
            return json.loads(corpo)
        except (httpx.HTTPError, ValueError) as exc:
            if isinstance(exc, ErroProvedor):
                raise
            raise ErroProvedor("temporario") from None

    async def usuario_discord(self, token: str) -> str:
        user = await self._json(DISCORD + "/users/@me", token)
        uid = user.get("id")
        if not isinstance(uid, str) or not SNOWFLAKE.fullmatch(uid):
            raise ErroProvedor("identidade")
        return uid

    async def membro(self, servidor: str, usuario: str) -> Membro:
        if (servidor not in self.cfg.servidores or not SNOWFLAKE.fullmatch(servidor) or
                not SNOWFLAKE.fullmatch(usuario)):
            raise AcessoNegado("Servidor ou usuário não permitido neste piloto.")
        token = self.cfg.discord_bot_token
        m = await self._json(f"{DISCORD}/guilds/{servidor}/members/{usuario}", token, bot=True)
        if m.get("user", {}).get("id") != usuario or m.get("pending") is True:
            raise AcessoNegado("Confirme sua participação no servidor.")
        guild = await self._json(f"{DISCORD}/guilds/{servidor}", token, bot=True)
        roles = await self._json(f"{DISCORD}/guilds/{servidor}/roles", token, bot=True)
        try:
            cargos = frozenset(m["roles"])
            permissoes = 0
            for role in roles:
                if role["id"] in cargos or role["id"] == servidor:
                    permissoes |= int(role["permissions"])
        except (TypeError, KeyError, ValueError):
            raise ErroProvedor("identidade") from None
        return Membro(servidor, usuario, dono_servidor=guild.get("owner_id") == usuario,
                       administrador=bool(permissoes & 8), gerenciar_servidor=bool(permissoes & 32), cargos=cargos)

    async def conta_google(self, acesso: str) -> str:
        obj = await self._json("https://www.googleapis.com/drive/v3/about?fields=user(permissionId)", acesso)
        conta = obj.get("user", {}).get("permissionId")
        if not isinstance(conta, str) or not conta or len(conta) > 300:
            raise ErroProvedor("identidade")
        return conta

    async def renovar(self, refresh: str) -> TokenGoogle:
        try:
            async with self._cliente("google") as client:
                token = await client.refresh_token(GOOGLE_TOKEN, refresh_token=refresh)
        except (OAuthError, OAuth2Error) as exc:
            raise ErroProvedor("revogada" if exc.error == "invalid_grant" else "oauth") from None
        except (httpx.HTTPError, ValueError):
            raise ErroProvedor("temporario") from None
        scope = token.get("scope")
        if scope is not None and (not isinstance(scope, str) or set(scope.split()) != {DRIVE_FILE}):
            raise ErroProvedor("escopo")
        return self.token_google(token)

    async def validar_arquivo(self, acesso: str, arquivo: str) -> dict:
        if not isinstance(arquivo, str) or not ARQUIVO.fullmatch(arquivo):
            raise ErroProvedor("arquivo")
        meta = await self._json("https://www.googleapis.com/drive/v3/files/" + arquivo +
                                "?fields=id,name,mimeType,isAppAuthorized,trashed", acesso)
        if (meta.get("id") != arquivo or meta.get("mimeType") != MIME or
                meta.get("isAppAuthorized") is not True or meta.get("trashed") is True):
            raise ErroProvedor("arquivo")
        prova = await self._json("https://sheets.googleapis.com/v4/spreadsheets/" + arquivo +
                                 "/values/" + quote("ANALISE!A1:D32", safe="") +
                                 "?valueRenderOption=UNFORMATTED_VALUE", acesso)
        linhas = prova.get("values")
        if not isinstance(linhas, list) or len(linhas) > 32:
            raise ErroProvedor("formato")
        valores = {}
        for linha in linhas:
            if not isinstance(linha, list) or not linha or not isinstance(linha[0], str):
                raise ErroProvedor("formato")
            chave = linha[0].strip()
            if not chave or chave == "chave":
                continue
            if chave in valores:
                raise ErroProvedor("formato")
            valores[chave] = linha[1] if len(linha) > 1 else ""
        versao = valores.get("formato.versao")
        if type(versao) is str and versao in ("1", "2", "4", "11", "12"):
            versao = int(versao)
        if type(versao) is not int or versao not in {1, 2, 4, 11, 12}:
            raise ErroProvedor("formato")
        nome = valores.get("nome")
        nome = nome.strip() if isinstance(nome, str) else ""
        if not nome or len(nome) > 100:
            nome = "Novo personagem"
        return {"arquivo": arquivo, "nome_arquivo": str(meta.get("name", "Planilha"))[:200],
                "nome": nome, "contrato": f"analise-{versao}", "prova_parcial": True}
