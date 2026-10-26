"""OAuth usa a biblioteca real e transporte HTTP simulado, sem acessar contas."""
import asyncio
import base64
import hashlib
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlencode, urlsplit

from cryptography.fernet import Fernet
import httpx

from carteira_viva.config_web import ConfigWeb
from carteira_viva.provedores import DRIVE_FILE, ErroProvedor, Provedores
from carteira_viva.segredos import AcessoNegado, ErroCarteira


def configuracao(path, **kw):
    data = dict(origem="http://127.0.0.1:8876", banco=path, chaves=(Fernet.generate_key(),),
                servico_token="segredo_de_servico_somente_ficticio_12345", discord_id="111",
                discord_secret="discord_secret_ficticio", discord_bot_token="bot_ficticio",
                google_id="google_ficticio", google_secret="google_secret_ficticio",
                projeto_google="333", picker_key="picker_ficticio", servidores=frozenset({"111"}), desenvolvimento=True)
    return ConfigWeb(**{**data, **kw})


class ConfigTeste(unittest.TestCase):
    def test_http_so_loopback_em_desenvolvimento(self):
        for origin, dev in (("http://publico.example", True), ("http://127.0.0.1:8876", False),
                            ("https://user:senha@exemplo.invalid", False), ("https://exemplo.invalid/caminho", False)):
            with self.subTest(origin=origin), self.assertRaises(ErroCarteira):
                configuracao(Path("nao-criar.sqlite3"), origem=origin, desenvolvimento=dev)

    def test_config_repr_nao_mostra_segredos(self):
        cfg = configuracao(Path("nao-criar.sqlite3"))
        for secret in (cfg.servico_token, cfg.discord_secret, cfg.google_secret, cfg.discord_bot_token, cfg.picker_key):
            self.assertNotIn(secret, repr(cfg))


class ProvedoresTeste(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.cfg = configuracao(Path("nao-criar.sqlite3"))
        self.req = []
        self.resposta_token = {"access_token": "access_ficticio", "refresh_token": "refresh_ficticio",
                               "token_type": "Bearer", "scope": DRIVE_FILE, "expires_in": 3600}
        self.metadados = {"id": "arquivo_ficticio_para_teste_001", "name": "Ficha fictícia",
                          "mimeType": "application/vnd.google-apps.spreadsheet", "isAppAuthorized": True}
        self.valores = {"values": [["chave", "valor", "célula", "parte"], ["formato.versao", 12], ["nome", "Personagem fictício"]]}
        self.membro = {"user": {"id": "222"}, "roles": ["444"]}
        self.roles = [{"id": "111", "permissions": "0"}, {"id": "444", "permissions": "8"}]
        self.http_status = 200
        self.prov = Provedores(self.cfg, transporte=httpx.MockTransport(self.handler))

    def handler(self, request):
        self.req.append(request)
        if request.url.path.endswith("/token"):
            return httpx.Response(self.http_status, json=self.resposta_token)
        if request.url.path.endswith("/users/@me"):
            return httpx.Response(200, json={"id": "222"})
        if "/members/" in request.url.path:
            return httpx.Response(200, json=self.membro)
        if request.url.path.endswith("/roles"):
            return httpx.Response(200, json=self.roles)
        if request.url.path.endswith("/guilds/111"):
            return httpx.Response(200, json={"owner_id": "999"})
        if request.url.path.endswith("/about"):
            return httpx.Response(200, json={"user": {"permissionId": "conta_ficticia"}})
        if "/values/" in request.url.path:
            return httpx.Response(200, json=self.valores)
        return httpx.Response(self.http_status, json=self.metadados)

    def test_url_oauth_pkce_sem_segredo(self):
        state, verifier = "s" * 43, "v" * 64
        for provider in ("google", "discord"):
            url = self.prov.autorizar(provider, state, verifier)
            query = parse_qs(urlsplit(url).query)
            challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
            self.assertEqual(query["code_challenge"], [challenge])
            self.assertEqual(query["code_challenge_method"], ["S256"])
            self.assertEqual(query["state"], [state])
            self.assertEqual(query["client_id"], [self.cfg.google_id if provider == "google" else self.cfg.discord_id])
            self.assertNotIn(self.cfg.google_secret, url)
            self.assertNotIn(self.cfg.discord_secret, url)
            self.assertNotIn(verifier, url)

    async def test_codigo_estado_e_verificador_biblioteca_real(self):
        state = "s" * 43
        callback = self.cfg.origem + "/oauth/google/retorno?" + urlencode({"state": state, "code": "codigo+com/reservados"})
        token = await self.prov.trocar_codigo("google", estado=state, verificador="v" * 64, retorno=callback)
        self.assertEqual(token["access_token"], "access_ficticio")
        body = parse_qs(self.req[0].content.decode())
        self.assertEqual(body["code"], ["codigo+com/reservados"])
        self.assertEqual(body["code_verifier"], ["v" * 64])
        self.assertEqual(body["client_secret"], [self.cfg.google_secret])
        self.assertEqual(str(self.req[0].url), "https://oauth2.googleapis.com/token")

    async def test_estado_errado_nao_chama_endpoint_de_token(self):
        with self.assertRaises(ErroProvedor):
            await self.prov.trocar_codigo("google", estado="a" * 43, verificador="v" * 64,
                                         retorno=self.cfg.origem + "/oauth/google/retorno?state=" + "b" * 43 + "&code=falso")
        self.assertFalse(self.req)

    async def test_escopo_ampliado_recusado(self):
        self.resposta_token["scope"] += " email"
        with self.assertRaises(ErroProvedor):
            await self.prov.trocar_codigo("google", estado="s" * 43, verificador="v" * 64,
                                         retorno=self.cfg.origem + "/oauth/google/retorno?state=" + "s" * 43 + "&code=falso")

    async def test_renovacao_invalida_tem_erro_especifico_sem_vazar_descricao(self):
        self.http_status = 400
        self.resposta_token = {"error": "invalid_grant", "error_description": "NAO_VAZAR_REFRESH_FICTICIO"}
        with self.assertRaises(ErroProvedor) as ctx: await self.prov.renovar("refresh_ficticio")
        self.assertEqual(ctx.exception.codigo, "revogada")
        self.assertNotIn("NAO_VAZAR", str(ctx.exception))

    async def test_renovacao_recusa_escopo_malformado_ou_ampliado(self):
        for scope in (123, [DRIVE_FILE], DRIVE_FILE + " email"):
            self.resposta_token["scope"] = scope
            with self.subTest(scope=scope), self.assertRaises(ErroProvedor):
                await self.prov.renovar("refresh_ficticio")

    async def test_renovacao_valida_e_identidade_google(self):
        token = await self.prov.renovar("refresh_ficticio")
        self.assertGreater(token.expira, self.prov.agora())
        self.assertEqual(await self.prov.conta_google(token.acesso), "conta_ficticia")

    async def test_administrador_e_gerenciar_servidor_sao_diferentes(self):
        m = await self.prov.membro("111", "222")
        self.assertTrue(m.administrador)
        self.roles[1]["permissions"] = "32"
        m = await self.prov.membro("111", "222")
        self.assertFalse(m.administrador)
        self.assertTrue(m.gerenciar_servidor)

    async def test_user_e_membro_pendente_ou_servidor_alheio(self):
        self.assertEqual(await self.prov.usuario_discord("token_ficticio"), "222")
        self.membro["pending"] = True
        with self.assertRaises(AcessoNegado): await self.prov.membro("111", "222")
        with self.assertRaises(AcessoNegado): await self.prov.membro("999", "222")

    async def test_selecao_valida_so_le_primeiras_linhas(self):
        p = await self.prov.validar_arquivo("token_ficticio", self.metadados["id"])
        self.assertEqual(p["nome"], "Personagem fictício")
        self.assertEqual(p["contrato"], "analise-12")
        self.assertTrue(p["prova_parcial"])
        self.assertTrue(all(r.method == "GET" for r in self.req))
        self.assertIn("ANALISE", self.req[-1].url.path)
        self.assertIn("A1:D32", self.req[-1].url.path)

    async def test_id_nao_permite_url_ou_travessia(self):
        for value in ("https://interno/arquivo", "../segredo", "x" * 201, None):
            with self.subTest(value=value), self.assertRaises(ErroProvedor):
                await self.prov.validar_arquivo("token_ficticio", value)
        self.assertFalse(self.req)

    async def test_metadados_nao_autorizados_lixeira_e_tipo_errado(self):
        for campo, valor in (("isAppAuthorized", False), ("trashed", True), ("mimeType", "application/pdf")):
            original = self.metadados.copy()
            self.metadados[campo] = valor
            with self.subTest(campo=campo), self.assertRaises(ErroProvedor):
                await self.prov.validar_arquivo("token_ficticio", self.metadados["id"])
            self.metadados = original

    async def test_formato_ausente_duplicado_booleano_e_futuro(self):
        for linhas in ([['nome', 'A']], [['formato.versao', 12], ['formato.versao', 12]],
                        [['formato.versao', True]], [['formato.versao', 99]]):
            self.valores = {"values": linhas}
            with self.subTest(linhas=linhas), self.assertRaises(ErroProvedor):
                await self.prov.validar_arquivo("token_ficticio", self.metadados["id"])

    async def test_resposta_grande_e_redirect_nao_seguido(self):
        async def resposta(request):
            return httpx.Response(200, content=b"x" * 600000)
        p = Provedores(self.cfg, transporte=httpx.MockTransport(resposta))
        with self.assertRaises(ErroProvedor): await p.conta_google("token_ficticio")
        p = Provedores(self.cfg, transporte=httpx.MockTransport(lambda r: httpx.Response(302, headers={"Location": "https://outra.invalid/"})))
        with self.assertRaises(ErroProvedor): await p.conta_google("token_ficticio")
