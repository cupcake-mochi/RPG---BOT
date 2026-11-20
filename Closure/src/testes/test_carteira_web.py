"""HTTP local e provedores fictícios. Nenhuma conta externa é acessada."""
import asyncio
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlencode, urlsplit

from aiohttp import CookieJar
from aiohttp.test_utils import TestClient, TestServer

from carteira_viva.banco import Cadastro
from carteira_viva.permissoes import Membro
from carteira_viva.provedores import ErroProvedor, Provedores
from carteira_viva.web import CFG, DADOS, criar_app
from testes.test_carteira_provedores import configuracao

F1 = "arquivo_ficticio_para_teste_001"
F2 = "arquivo_ficticio_para_teste_002"


class ProvedorFicticio(Provedores):
    def __init__(self, cfg, agora):
        super().__init__(cfg, agora=agora)
        self.usuario = "222"
        self.conta = "conta_ficticia"
        self.presente = True
        self.renovacoes = 0
        self.logins_google = 0
        self.falha_renovacao = False
        self.falha_validacao = False
        self.espera = None
        self.validacoes = 0

    async def trocar_codigo(self, provedor, **kwargs):
        if provedor == "google": self.logins_google += 1
        if self.espera:
            await self.espera.wait()
        return {"access_token": "acesso_ficticio_nao_real", "refresh_token": "refresh_ficticio_nao_real", "expires_in": 3600}

    async def usuario_discord(self, token):
        return self.usuario

    async def membro(self, servidor, usuario):
        from carteira_viva.segredos import AcessoNegado
        if not self.presente or servidor not in self.cfg.servidores:
            raise AcessoNegado("Membro indisponível")
        return Membro(servidor, usuario)

    async def conta_google(self, acesso):
        return self.conta

    async def renovar(self, refresh):
        self.renovacoes += 1
        if self.falha_renovacao: raise ErroProvedor("revogada")
        return self.token_google({"access_token": "acesso_ficticio_renovado", "expires_in": 3600})

    async def validar_arquivo(self, acesso, arquivo):
        self.validacoes += 1
        if arquivo not in (F1, F2) or self.falha_validacao:
            raise ErroProvedor("arquivo")
        return {"arquivo": arquivo, "nome_arquivo": "Planilha fictícia", "nome": "Personagem fictício",
                "contrato": "analise-12", "prova_parcial": True}


class WebFixture:
    provedor_tipo = ProvedorFicticio

    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "web.sqlite3"
        self.clock = [180000.0]
        self.agora = lambda: self.clock[0]
        self.cfg = configuracao(self.path)
        self.prov = self.provedor_tipo(self.cfg, self.agora)
        await self.abrir_cliente()
        self.membro = Membro("111", "222")

    async def abrir_cliente(self):
        self.app = criar_app(self.cfg, provedores=self.prov, agora=self.agora)
        self.client = TestClient(TestServer(self.app), cookie_jar=CookieJar(unsafe=True))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        self.tmp.cleanup()

    async def scalar(self, sql, args=()):
        def read():
            return self.app[DADOS].store.c.db.execute(sql, args).fetchone()[0]
        return await asyncio.wrap_future(self.app[DADOS].executor.submit(read))

    async def seed(self, arquivo=None):
        cid = await self.app[DADOS].chamar("cadastro.conectar", self.membro, conta="conta_ficticia",
                                          cliente=self.cfg.google_id, refresh_token="refresh_anterior_ficticio")
        if arquivo:
            p = await self.app[DADOS].chamar("cadastro.cadastrar", self.membro, conexao=cid, arquivo=arquivo,
                                            nome="Anterior", contrato="analise-12", responsabilidade=True, pedido="seed-" + arquivo)
            return cid, p
        return cid

    async def comecar(self, acao="cadastro", personagem=None):
        resp = await self.client.post("/interno/conexoes", json={"servidor": "111", "usuario": "222", "acao": acao, "personagem": personagem},
                                      headers={"Authorization": "Bearer " + self.cfg.servico_token})
        self.assertEqual(resp.status, 200, await resp.text())
        self.ticket = parse_qs(urlsplit((await resp.json())["url"]).query)["ticket"][0]
        resp = await self.client.get("/conectar", params={"ticket": self.ticket})
        self.assertEqual(resp.status, 200)
        await self.atualizar()
        return resp

    async def atualizar(self):
        resp = await self.client.get("/api/fluxo", params={"ticket": self.ticket})
        self.assertEqual(resp.status, 200, await resp.text())
        self.s = await resp.json()
        return self.s

    async def post(self, path, data=None, *, csrf=None, origin=None):
        return await self.client.post(path, json={"ticket": self.ticket, **(data or {})},
                                      headers={"Origin": origin or self.cfg.origem,
                                               "X-CSRF-Token": self.s["csrf"] if csrf is None else csrf})

    async def estado_oauth(self, provider):
        r = await self.post("/api/login/" + provider)
        self.assertEqual(r.status, 200, await r.text())
        return parse_qs(urlsplit((await r.json())["url"]).query)["state"][0]

    async def callback(self, provider, state, *, error=None):
        params = {"state": state, "error": error} if error else {"state": state, "code": "codigo_ficticio"}
        return await self.client.get(f"/oauth/{provider}/retorno", params=params, allow_redirects=False)

    async def oauth(self, provider):
        state = await self.estado_oauth(provider)
        resp = await self.callback(provider, state)
        self.assertEqual(resp.status, 302, await resp.text())
        await self.atualizar()
        return resp, state

    async def ate_picker(self):
        await self.comecar()
        await self.oauth("discord")
        await self.oauth("google")
        self.assertEqual(self.s["fase"], "picker")

    async def selecionar(self, arquivo=F1):
        r = await self.post("/api/selecionar", {"arquivo": arquivo})
        self.assertEqual(r.status, 200, await r.text())
        await self.atualizar()

    async def confirmar(self):
        return await self.post("/api/confirmar", {"nome": "Nome confirmado", "responsabilidade": True})

class WebTeste(WebFixture, unittest.IsolatedAsyncioTestCase):
    async def test_backup_exclui_fluxo_oauth_pendente_sem_apagar_o_ativo(self):
        from carteira_viva.backup import gravar_backup, _extrair
        import sqlite3
        await self.ate_picker()
        destino = Path(self.tmp.name) / "teste.cvb"
        raw = Path(self.tmp.name) / "conferir.sqlite3"
        def verificar():
            c = self.app[DADOS].store.c
            gravar_backup(c, destino)
            _extrair(destino, raw, c.cifra, self.agora(), "cadastro")
            with sqlite3.connect(raw) as db:
                return db.execute("SELECT count(*) FROM web_fluxos").fetchone()[0]
        count = await asyncio.wrap_future(self.app[DADOS].executor.submit(verificar))
        self.assertEqual(count, 0)
        self.assertEqual(await self.scalar("SELECT count(*) FROM web_fluxos"), 1)
        await self.selecionar()
        self.assertEqual((await self.confirmar()).status, 200)

    async def test_cadastro_inteiro_sem_persistir_token_antes_da_confirmacao(self):
        await self.ate_picker()
        self.assertEqual(await self.scalar("SELECT count(*) FROM conexoes"), 0)
        await self.selecionar()
        resp = await self.confirmar()
        self.assertEqual(resp.status, 200, await resp.text())
        p = (await resp.json())["resultado"]
        self.assertEqual(p["responsavel"], "222")
        self.assertEqual(p["perfil"]["nome"], "Nome confirmado")
        self.assertEqual(await self.scalar("SELECT count(*) FROM personagens"), 1)
        self.assertNotIn(b"refresh_ficticio_nao_real", self.path.read_bytes())
        await self.atualizar()
        self.assertEqual(self.s["fase"], "concluido")
        self.assertNotIn("google", self.s)

    async def test_api_interna_exige_segredo_e_servidor_permitido(self):
        r = await self.client.post("/interno/conexoes", json={"usuario": "222", "servidor": "111"})
        self.assertEqual(r.status, 403)
        r = await self.client.post("/interno/conexoes", json={"usuario": "222", "servidor": "999"},
                                    headers={"Authorization": "Bearer " + self.cfg.servico_token})
        self.assertEqual(r.status, 403)

    async def test_cookie_http_only_e_rotacao_no_login_discord(self):
        resp = await self.comecar()
        ck = next(iter(resp.cookies.values()))
        self.assertTrue(ck["httponly"])
        self.assertEqual(ck["samesite"], "Lax")
        anterior = ck.value
        resp, _ = await self.oauth("discord")
        self.assertNotEqual(next(iter(resp.cookies.values())).value, anterior)

    async def test_ticket_sem_cookie_nao_da_acesso(self):
        await self.comecar()
        self.client.session.cookie_jar.clear()
        r = await self.client.get("/api/fluxo", params={"ticket": self.ticket})
        self.assertEqual(r.status, 403)

    async def test_cookie_antigo_falha_apos_identificar(self):
        resp = await self.comecar()
        old = next(iter(resp.cookies.values()))
        await self.oauth("discord")
        self.client.session.cookie_jar.clear()  # Impede que o cliente substitua o cookie antigo pelo novo.
        r = await self.client.get("/api/fluxo", params={"ticket": self.ticket}, headers={"Cookie": f"{old.key}={old.value}"})
        self.assertEqual(r.status, 403)

    async def test_origem_e_csrf_errados_nao_avancam_etapa(self):
        await self.comecar()
        r = await self.post("/api/login/discord", origin="https://alheio.invalid")
        self.assertEqual(r.status, 403)
        self.assertEqual(r.headers["Cache-Control"], "private, no-store")
        r = await self.post("/api/login/discord", csrf="invalido" * 5)
        self.assertEqual(r.status, 403)
        await self.atualizar()
        self.assertEqual(self.s["fase"], "identificar")

    async def test_conta_discord_errada_nao_libera_google(self):
        await self.comecar()
        self.prov.usuario = "999"
        await self.oauth("discord")
        self.assertEqual(self.s["fase"], "falhou")
        r = await self.post("/api/login/google")
        self.assertNotEqual(r.status, 200)

    async def test_callback_repetido_nao_reabre_fluxo(self):
        await self.comecar()
        _, state = await self.oauth("discord")
        r = await self.callback("discord", state)
        self.assertEqual(r.status, 302)
        self.assertTrue(r.headers["Location"].endswith("/erro"))
        await self.atualizar()
        self.assertEqual(self.s["fase"], "google")

    async def test_erro_google_limpa_tentativa_sem_refletir_codigo_no_destino(self):
        await self.comecar()
        await self.oauth("discord")
        s = await self.estado_oauth("google")
        r = await self.callback("google", s, error="access_denied")
        self.assertNotIn("code=", r.headers["Location"])
        self.assertNotIn("state=", r.headers["Location"])
        await self.atualizar()
        self.assertEqual(self.s["fase"], "falhou")

    async def test_cookie_de_outra_tentativa_nao_confirma_callback(self):
        await self.comecar()
        s = await self.estado_oauth("discord")
        self.client.session.cookie_jar.clear()
        r = await self.callback("discord", s)
        self.assertTrue(r.headers["Location"].endswith("/erro"))

    async def test_cancelamento_apos_google_nao_persiste_conexao(self):
        await self.ate_picker()
        r = await self.post("/api/cancelar")
        self.assertEqual(r.status, 200)
        await self.atualizar()
        self.assertEqual(self.s["fase"], "cancelado")
        self.assertEqual(await self.scalar("SELECT count(*) FROM conexoes"), 0)
        r = await self.client.get("/api/picker", params={"ticket": self.ticket})
        self.assertNotEqual(r.status, 200)

    async def test_cancelamento_durante_callback_nao_ressuscita(self):
        await self.comecar()
        await self.oauth("discord")
        s = await self.estado_oauth("google")
        self.prov.espera = asyncio.Event()
        task = asyncio.create_task(self.callback("google", s))
        for _ in range(100):
            if await self.scalar("SELECT count(*) FROM web_fluxos WHERE fase='processando_google'"): break
            await asyncio.sleep(.01)
        await self.post("/api/cancelar")
        self.prov.espera.set()
        await task
        await self.atualizar()
        self.assertEqual(self.s["fase"], "cancelado")
        self.assertEqual(await self.scalar("SELECT count(*) FROM conexoes"), 0)

    async def test_picker_so_expoe_access_token_na_sessao_certa(self):
        await self.ate_picker()
        r = await self.client.get("/api/picker", params={"ticket": self.ticket})
        self.assertEqual(r.status, 200)
        data = await r.json()
        self.assertEqual(data["access_token"], "acesso_ficticio_nao_real")
        self.assertNotIn("refresh", data)
        self.assertNotIn(self.cfg.google_secret, str(data))
        self.assertEqual(r.headers["Referrer-Policy"], "strict-origin")
        self.assertIn("style-src 'self'", r.headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-inline", r.headers["Content-Security-Policy"])

    async def test_expiracao_nao_entrega_token(self):
        await self.ate_picker()
        self.clock[0] += 600
        r = await self.client.get("/api/picker", params={"ticket": self.ticket})
        self.assertEqual(r.status, 410)
        self.assertNotIn("acesso_ficticio", await r.text())

    async def test_membro_que_saiu_nao_continua_sessao(self):
        await self.ate_picker()
        self.prov.presente = False
        r = await self.client.get("/api/picker", params={"ticket": self.ticket})
        self.assertEqual(r.status, 403)

    async def test_nao_confirma_sem_responsabilidade(self):
        await self.ate_picker()
        await self.selecionar()
        r = await self.post("/api/confirmar", {"responsabilidade": False})
        self.assertEqual(r.status, 400)
        self.assertEqual(await self.scalar("SELECT count(*) FROM personagens"), 0)

    async def test_confirmacao_repetida_nao_duplica_personagem(self):
        await self.ate_picker()
        await self.selecionar()
        a, b = await self.confirmar(), await self.confirmar()
        self.assertEqual((await a.json())["resultado"]["id"], (await b.json())["resultado"]["id"])
        self.assertEqual(await self.scalar("SELECT count(*) FROM personagens"), 1)

    async def test_falha_de_validacao_preserva_registro_anterior(self):
        cid, p = await self.seed(F1)
        await self.comecar("troca", p["id"])
        await self.oauth("discord"); await self.oauth("google")
        self.prov.falha_validacao = True
        r = await self.post("/api/selecionar", {"arquivo": F2})
        self.assertNotEqual(r.status, 200)
        self.assertEqual((await self.app[DADOS].chamar("cadastro.detalhes", self.membro, p["id"]))["arquivo"], F1)

    async def test_troca_mantem_id_e_nao_aceita_outra_conta(self):
        cid, p = await self.seed(F1)
        await self.comecar("troca", p["id"])
        await self.oauth("discord"); await self.oauth("google")
        await self.selecionar(F2)
        r = await self.confirmar()
        self.assertEqual((await r.json())["resultado"]["id"], p["id"])
        self.assertEqual((await self.app[DADOS].chamar("cadastro.detalhes", self.membro, p["id"]))["arquivo"], F2)
        await self.comecar("troca", p["id"])
        await self.oauth("discord")
        self.prov.conta = "conta_de_outro_google"
        await self.oauth("google")
        self.assertEqual(self.s["fase"], "falhou")

    async def test_reconectar_revalida_arquivo_existente(self):
        cid, p = await self.seed(F1)
        autorizacao = await self.scalar("SELECT autorizacao FROM conexoes WHERE id=?", (cid,))
        await self.app[DADOS].chamar("cadastro.marcar_revogada", cid, autorizacao=autorizacao)
        await self.comecar("reconectar", p["id"])
        await self.oauth("discord"); await self.oauth("google")
        self.assertEqual(self.s["fase"], "revisar")
        r = await self.confirmar()
        self.assertEqual(r.status, 200, await r.text())
        self.assertEqual((await self.app[DADOS].chamar("cadastro.detalhes", self.membro, p["id"]))["arquivo"], F1)

    async def test_usa_conexao_existente_sem_novo_consentimento(self):
        cid = await self.seed()
        await self.comecar(); await self.oauth("discord")
        self.assertIn(cid, self.s["conexoes"])
        r = await self.post("/api/usar", {"conexao": cid})
        self.assertEqual(r.status, 200)
        await self.atualizar()
        await self.selecionar(); r = await self.confirmar()
        self.assertEqual(r.status, 200)
        self.assertEqual(self.prov.logins_google, 0)
        self.assertEqual(self.prov.renovacoes, 1)

    async def test_revogacao_em_renovacao_remove_sessao_sem_reativar(self):
        cid = await self.seed()
        await self.comecar(); await self.oauth("discord")
        self.prov.falha_renovacao = True
        r = await self.post("/api/usar", {"conexao": cid})
        self.assertNotEqual(r.status, 200)
        self.assertEqual(await self.scalar("SELECT estado FROM conexoes WHERE id=?", (cid,)), "revogada")

    async def test_conexao_de_outro_usuario_nao_pode_ser_reutilizada(self):
        cid = await self.app[DADOS].chamar("cadastro.conectar", Membro("111", "999"), conta="alheia",
                                          cliente=self.cfg.google_id, refresh_token="refresh_alheio_ficticio")
        await self.comecar(); await self.oauth("discord")
        r = await self.post("/api/usar", {"conexao": cid})
        self.assertEqual(r.status, 403)

    async def test_arquivo_duplicado_reverte_ativacao_de_nova_credencial(self):
        cid, p = await self.seed(F1)
        anterior = await self.scalar("SELECT autorizacao FROM conexoes WHERE id=?", (cid,))
        await self.ate_picker(); await self.selecionar(F1)
        r = await self.confirmar()
        self.assertEqual(r.status, 409)
        self.assertEqual(await self.scalar("SELECT autorizacao FROM conexoes WHERE id=?", (cid,)), anterior)
        self.assertEqual(await self.scalar("SELECT count(*) FROM personagens"), 1)

    async def test_callback_antigo_nao_desfaz_desconexao(self):
        cid = await self.seed()
        await self.comecar(); await self.oauth("discord")
        state = await self.estado_oauth("google")
        await self.app[DADOS].chamar("cadastro.desconectar", self.membro, cid)
        await self.callback("google", state)
        self.assertEqual(await self.scalar("SELECT estado FROM conexoes WHERE id=?", (cid,)), "desconectada")

    async def test_limite_de_tentativas(self):
        for _ in range(3): await self.comecar()
        r = await self.client.post("/interno/conexoes", json={"servidor": "111", "usuario": "222"},
                                    headers={"Authorization": "Bearer " + self.cfg.servico_token})
        self.assertEqual(r.status, 429)
        self.assertEqual((await r.json())["erro"], "limite")

    async def test_reinicio_invalida_fluxo_mas_conserva_vinculo_confirmado(self):
        await self.ate_picker(); await self.selecionar(); r = await self.confirmar()
        p = (await r.json())["resultado"]
        old_ticket = self.ticket
        await self.client.close(); await self.abrir_cliente()
        r = await self.client.get("/api/fluxo", params={"ticket": old_ticket})
        self.assertEqual(r.status, 410)
        self.assertEqual(len(await self.app[DADOS].chamar("cadastro.listar", self.membro)), 1)
        await self.comecar(); await self.oauth("discord")
        self.assertEqual(len(self.s["conexoes"]), 1)

    async def test_demo_nao_existe_no_servico_real_e_estaticos_nao_fazem_travessia(self):
        r = await self.client.get("/demo/iniciar", allow_redirects=False)
        self.assertEqual(r.status, 404)
        r = await self.client.get("/static/config_web.py")
        self.assertEqual(r.status, 404)
        r = await self.client.get("/static/conectar.js")
        self.assertEqual(r.status, 200)
        self.assertNotIn(self.cfg.google_secret, await r.text())


if __name__ == "__main__":
    unittest.main()
