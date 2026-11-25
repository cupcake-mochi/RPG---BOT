"""Preenchimento da ficha: planilha fictícia em memória, sem rede nem conta externa."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from aiohttp import CookieJar
from aiohttp.test_utils import TestClient, TestServer
import httpx

from carteira_viva import criacao_plano as cp, preencher
from carteira_viva.config_web import ConfigWeb
from carteira_viva.criacao_plano import MAPA, PESSOAL
from carteira_viva.demo_ficha import FIM_ANALISE, Planilha
from carteira_viva.permissoes import Acao, Membro, permitido
from carteira_viva.provedores import MIME, ErroProvedor
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from carteira_viva.web import DADOS, PREENCHER, criar_app
from testes.test_carteira_galeria import ProvedorGaleria
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_web import F1

ATRIBUTOS = dict(zip([a["nome"] for a in MAPA["atributos"]], (3, 2, 2, 1, 1)))


class Google(httpx.AsyncBaseTransport):
    def __init__(self):
        self.planilha, self.req, self.posts = Planilha(), [], []
        self.autorizado, self.lixeira, self.status, self.perde, self.antes = True, False, 200, False, None
        self.bloqueio, self.entrou = None, asyncio.Event()

    async def handle_async_request(self, r):
        self.req.append(r)
        if r.url.host == "www.googleapis.com":
            return httpx.Response(200, json=dict(id=F1, mimeType=MIME, isAppAuthorized=self.autorizado, trashed=self.lixeira,
                                                 version="7", modifiedTime="2026-11-24T12:00:00.000Z"))
        assert r.url.host == "sheets.googleapis.com", r.url
        corpo = await r.aread()
        if r.method != "POST":
            return self.planilha.responder(r)
        self.posts.append(json.loads(corpo))
        self.entrou.set()
        if self.bloqueio:
            await self.bloqueio.wait()
        if self.status != 200:
            return httpx.Response(self.status, json={})
        resposta = self.planilha.responder(r, corpo)
        if self.perde:
            raise httpx.ReadTimeout("fictício", request=r)
        return resposta


class ProvedorPreencher(ProvedorGaleria):
    def __init__(self, cfg, agora):
        super().__init__(cfg, agora)
        self.google = self.transporte = Google()


class Base(unittest.IsolatedAsyncioTestCase):
    preencher = frozenset({"222"})

    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cfg = replace(configuracao(Path(self.tmp.name) / "db.sqlite3", servidores=frozenset({"111", "333"})), preencher=self.preencher)
        self.clock = [180000.0]
        self.prov = ProvedorPreencher(self.cfg, lambda: self.clock[0])
        self.g, self.f = self.prov.google, self.prov.google.planilha
        self.app = criar_app(self.cfg, provedores=self.prov, agora=lambda: self.clock[0])
        self.client = TestClient(TestServer(self.app), cookie_jar=CookieJar(unsafe=True))
        await self.client.start_server()
        self.m = self.prov.pessoas["222"]
        self.cid = await self.b("conectar", self.m, conta="ficticia", cliente=self.cfg.google_id, refresh_token="ficticio")
        self.pid = (await self.b("cadastrar", self.m, conexao=self.cid, arquivo=F1, nome="Nome privado", contrato="analise-13",
                                 responsabilidade=True, pedido="primeiro"))["id"]
        self.s = self.app[PREENCHER]
        relogio = patch.object(preencher, "RELER", 0)
        relogio.start()
        self.addCleanup(relogio.stop)

    async def asyncTearDown(self):
        await self.client.close()
        self.tmp.cleanup()

    async def b(self, metodo, *a, **kw):
        return await self.app[DADOS].chamar("cadastro." + metodo, *a, **kw)

    async def sql(self, texto, *args):
        def ler():
            return [tuple(r) for r in self.app[DADOS].store.c.db.execute(texto, args)]
        return await asyncio.wrap_future(self.app[DADOS].executor.submit(ler))

    async def estado(self, usuario="222"):
        return await self.s.estado("111", usuario, self.pid)

    async def salvar(self, passo, dados, *, base=None, confirmados=(), usuario="222", servidor="111", pid=None):
        base = base or preencher.base_do_passo(passo, (await self.lida()).lido)
        return await self.s.salvar(servidor, usuario, pid or self.pid, passo, dados=dados, base=base, confirmados=list(confirmados))

    async def lida(self):
        def url(faixas, forma):
            return httpx.Request("GET", "https://sheets.googleapis.com/v4/spreadsheets/x/values:batchGet",
                                 params=[("ranges", f) for f in faixas] + [("valueRenderOption", forma)])
        cauda = f"ANALISE!A{FIM_ANALISE - 40}:B{FIM_ANALISE}"
        return preencher.Ficha([], self.f.responder(url(preencher.FAIXAS + (cauda,), "UNFORMATTED_VALUE")).json(),
                               self.f.responder(url([f"'{PESSOAL}'!{c}" for c in preencher.TEXTOS.values()], "FORMULA")).json())


class Servico(Base):
    async def test_estado_le_sem_escrever(self):
        e = await self.estado()
        self.assertEqual(self.g.posts, [])
        self.assertEqual(set(e["bases"]), set(preencher.PASSOS))
        self.assertTrue(e["criacao"])
        self.assertEqual(e["identidade"][0], {"chave": "nome", "rotulo": "PORTADOR", "curto": True, "valor": ""})
        self.assertEqual((e["exportacao"], e["a_mao"], e["escolhas"]["origem"]), ("em_dia", [], "Latente"))
        json.dumps(e)

    async def test_passo_a_passo_ate_o_fim(self):
        r = await self.salvar("identidade", {"nome": "Kaito", "historia": "=IMPORTXML(1)"})
        self.assertTrue(r["gravou"])
        self.assertEqual((self.f.de("CARTEIRA", "O9"), self.f.de(PESSOAL, "Q27")), ("Kaito", "=IMPORTXML(1)"))
        await self.salvar("atributos", ATRIBUTOS)
        self.assertEqual(self.f.de("FICHA", "D21"), 3)
        self.assertEqual(self.f.notas[PESSOAL, *cp.posicao("AF86")], "Tudo cabe na sua Força.")
        await self.salvar("origem", {"origem": "Descendente"})
        await self.salvar("capacidades", {"marcante": "Marcante A", "menor1": "Menor A", "menor2": "Menor B"})
        self.assertIn((PESSOAL, 45), self.f.alturas)
        r = await self.salvar("caminho", {"caminho": "Guia", "trilha": "Socorrista"})
        self.assertEqual((self.f.de("FICHA", "D11"), self.f.de("FICHA", "N11")), ("Guia", "Socorrista"))
        self.assertEqual(r["treinos"]["fixas"], ["Persuasão", "Medicina"])
        livres = [p["nome"] for p in MAPA["pericias"] if p["nome"] not in r["treinos"]["fixas"]]
        r = await self.salvar("treinos", dict(pericias=livres[:7], oficios=[o["nome"] for o in MAPA["oficios"]][:2],
                                             testes=["Físico", "Vigor"], tr_fisico="DESTREZA", troca=0))
        self.assertEqual(sum(x["marcada"] for x in r["treinos"]["pericias"]), 9)
        self.assertEqual(r["escolhas"]["trilha"], "Socorrista")

    async def test_marca_a_exportacao_como_velha_uma_vez(self):
        await self.salvar("identidade", {"nome": "Kaito"})
        self.assertEqual(self.f.de("ANALISE", f"B{FIM_ANALISE - 1}"), "desatualizada")
        self.assertEqual(self.f.de("CARTEIRA", "AH4"), preencher.DESATUALIZADA)
        n = len(self.g.posts[-1]["requests"])
        await self.salvar("identidade", {"nome": "Outro"}, confirmados={"nome"})
        self.assertEqual(len(self.g.posts[-1]["requests"]), n - 2)

    async def test_exportacao_no_meio_nao_escreve(self):
        self.f.poe("ANALISE", f"B{FIM_ANALISE - 1}", "exportando")
        with self.assertRaisesRegex(cp.Recusa, "exportação"):
            await self.salvar("identidade", {"nome": "Kaito"})
        self.assertEqual(self.g.posts, [])

    async def test_ficha_que_nao_e_a_oficial_atual_nao_escreve(self):
        casos = [("ANALISE", "B2", "12"), ("ANALISE", "B3", "R54"), ("ANALISE", "B4", "Outro sistema"), ("FICHA", "AH10", "XP"),
                 ("DADOS", "DM4", "outra"), ("ANALISE", f"A{FIM_ANALISE - 1}", "outra"), ("FICHA", MAPA["pericias"][0]["rotulo"], "Voar")]
        for aba, celula, valor in casos:
            with self.subTest(celula=celula):
                certo = self.f.de(aba, celula)
                self.f.poe(aba, celula, valor)
                with self.assertLogs("carteira_viva.preencher", "WARNING"), self.assertRaises(ErroProvedor) as e:
                    await self.salvar("identidade", {"nome": "Kaito"}, base="0" * 32)
                self.assertEqual(e.exception.codigo, "formato")
                self.f.poe(aba, celula, certo)
        self.f.ids.pop("DADOS")
        with self.assertRaises(ErroProvedor) as e:
            await self.estado()
        self.assertEqual((e.exception.codigo, self.g.posts), ("formato", []))

    async def test_oficial_recusada_antes_de_ler(self):
        with patch.object(preencher, "IDS_OFICIAIS", frozenset({F1})):
            for f in (self.estado(), self.salvar("identidade", {"nome": "Kaito"}, base="0" * 32)):
                with self.assertRaises(ErroProvedor) as e:
                    await f
                self.assertEqual(e.exception.codigo, "oficial")
            with self.assertRaises(ErroProvedor):
                await self.s._enviar("x", F1, {"requests": []})
        self.assertEqual(self.g.req, [])
        self.assertEqual(len(preencher.IDS_OFICIAIS), 2)

    async def test_arquivo_fora_do_alcance(self):
        for campo, valor in (("autorizado", False), ("lixeira", True)):
            setattr(self.g, campo, valor)
            with self.assertRaises(ErroProvedor) as e:
                await self.estado()
            self.assertEqual(e.exception.codigo, "arquivo")
            setattr(self.g, campo, not valor)

    async def test_so_o_dono(self):
        for usuario in ("999", "777", "555"):      # membro, revisor e administrador
            with self.assertRaises(AcessoNegado):
                await self.estado(usuario)
            with self.assertRaises(AcessoNegado):
                await self.salvar("identidade", {"nome": "X"}, usuario=usuario)
        with self.assertRaises(AcessoNegado):
            await self.salvar("identidade", {"nome": "X"}, servidor="333")
        self.assertEqual(self.g.req, [])
        self.assertTrue(permitido(Acao.PREENCHER, Membro("1", "2"), "1", "2"))
        self.assertFalse(permitido(Acao.PREENCHER, Membro("1", "2", dono_servidor=True, administrador=True), "1", "3"))

    async def test_conexao_revogada(self):
        autorizacao = (await self.sql("SELECT autorizacao FROM conexoes"))[0][0]
        await self.b("marcar_revogada", self.cid, autorizacao=autorizacao)
        with self.assertRaises(ErroCarteira):
            await self.estado()

    async def test_quem_saiu_no_meio_nao_escreve(self):
        original = self.s._ler

        async def ler_e_sair(*a):
            ficha = await original(*a)
            self.prov.ausentes.add("222")
            return ficha
        with patch.object(self.s, "_ler", ler_e_sair), self.assertRaises(AcessoNegado):
            await self.salvar("identidade", {"nome": "Kaito"})
        self.assertEqual(self.g.posts, [])

    async def test_preenchido_pede_confirmacao_por_campo(self):
        await self.salvar("identidade", {"nome": "Kaito", "olhos": "verdes"})
        n = len(self.g.posts)
        with self.assertRaises(cp.JaPreenchido) as e:
            await self.salvar("identidade", {"nome": "Ren", "olhos": "azuis", "cabelo": "preto"}, confirmados={"nome"})
        self.assertEqual((e.exception.campos, len(self.g.posts)), (("olhos",), n))
        await self.salvar("identidade", {"nome": "Ren", "cabelo": "preto"}, confirmados={"nome"})
        self.assertEqual((self.f.de("CARTEIRA", "O9"), self.f.de(PESSOAL, "Q15")), ("Ren", "verdes"))

    async def test_mudou_na_planilha_desde_a_tela(self):
        base = (await self.estado())["bases"]["identidade"]
        self.f.poe("CARTEIRA", "O9", "Escrito na planilha")
        with self.assertRaises(preencher.Mudou) as e:
            await self.salvar("identidade", {"olhos": "verdes"}, base=base)
        self.assertEqual(e.exception.estado["identidade"][0]["valor"], "Escrito na planilha")
        self.assertEqual(self.g.posts, [])
        # Mudança em outro passo não atrapalha.
        base = (await self.estado())["bases"]["origem"]
        self.f.poe("CARTEIRA", "O9", "De novo")
        await self.salvar("origem", {"origem": "Descendente"}, base=base)

    async def test_repetir_pedido_que_ja_entrou_nao_e_conflito(self):
        base = (await self.estado())["bases"]["caminho"]
        await self.salvar("caminho", {"caminho": "Guia"}, base=base)
        n = len(self.g.posts)
        self.assertFalse((await self.salvar("caminho", {"caminho": "Guia"}, base=base))["gravou"])
        self.assertEqual(len(self.g.posts), n)

    async def test_resposta_perdida_se_resolve_relendo(self):
        self.g.perde = True
        r = await self.salvar("identidade", {"nome": "Kaito"})
        self.assertTrue(r["gravou"])
        self.assertEqual(len(self.g.posts), 1)

    async def test_google_recusou_ou_nao_gravou(self):
        for status, codigo in ((400, "escrita_recusada"), (403, "escrita_recusada"), (429, "escrita_incerta"), (503, "escrita_incerta")):
            self.g.status = status
            with self.assertLogs("carteira_viva.preencher", "WARNING"), self.assertRaises(ErroProvedor) as e:
                await self.salvar("identidade", {"nome": "Kaito"})
            self.assertEqual(e.exception.codigo, codigo)
        self.assertEqual(len(self.g.posts), 4)      # nunca repete sozinho
        self.assertEqual(self.f.de("ANALISE", f"B{FIM_ANALISE - 1}"), "em_dia")

    async def test_segunda_escrita_falhou_vira_aviso(self):
        original, envios = self.s._enviar, []

        async def enviar(*a):
            envios.append(a)
            return await original(*a) if len(envios) == 1 else "escrita_incerta"
        with patch.object(self.s, "_enviar", enviar):
            r = await self.salvar("atributos", ATRIBUTOS)
        self.assertIn("notas", " ".join(r["avisos"]))
        self.assertEqual(self.f.de("FICHA", "D21"), 3)

    async def test_clique_duplo_escreve_uma_vez(self):
        self.g.bloqueio = asyncio.Event()
        base = (await self.estado())["bases"]["identidade"]
        a = asyncio.create_task(self.salvar("identidade", {"nome": "Kaito"}, base=base))
        b = asyncio.create_task(self.salvar("identidade", {"nome": "Kaito"}, base=base))
        await self.g.entrou.wait()
        self.g.bloqueio.set()
        self.assertEqual(await a, await b)
        self.assertEqual(len(self.g.posts), 1)

    async def test_fechar_a_aba_no_meio_nao_corta_a_escrita(self):
        self.g.bloqueio = asyncio.Event()
        t = asyncio.create_task(self.salvar("atributos", ATRIBUTOS))
        await self.g.entrou.wait()
        t.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await t
        self.g.bloqueio.set()
        await self.s.fechar()
        self.assertEqual(self.f.notas[PESSOAL, *cp.posicao("AF86")], "Tudo cabe na sua Força.")
        self.assertEqual(self.s.tarefas, set())

    async def test_mesmo_arquivo_em_dois_servidores_nao_escreve_junto(self):
        m = replace(self.m, servidor="333")
        pid = (await self.b("cadastrar", m, conexao=self.cid, arquivo=F1, nome="Outro", contrato="analise-13",
                            responsabilidade=True, pedido="segundo"))["id"]
        base = (await self.estado())["bases"]["identidade"]
        self.g.bloqueio = asyncio.Event()
        a = asyncio.create_task(self.salvar("identidade", {"nome": "Kaito"}, base=base))
        await self.g.entrou.wait()
        b = asyncio.create_task(self.salvar("identidade", {"nome": "Ren"}, base=base, servidor="333", pid=pid))
        await asyncio.sleep(0.05)
        self.assertEqual(len(self.g.posts), 1)
        self.g.bloqueio.set()
        await a
        with self.assertRaises(preencher.Mudou):
            await b
        self.assertEqual(self.f.de("CARTEIRA", "O9"), "Kaito")

    async def test_leitura_guardada_deixa_de_valer_e_o_registro_nao_tem_conteudo(self):
        ref = await self.b("reservar_leitura", self.m, self.pid)
        await self.b("gravar_leitura", self.m, ref, campos={"ficha": {}}, schema="carteira-analise-1")
        ref = await self.b("reservar_leitura", self.m, self.pid)      # leitura em andamento
        await self.salvar("identidade", {"nome": "Segredo do jogador"})
        self.assertEqual(await self.sql("SELECT count(*) FROM leituras"), [(0,)])
        with self.assertRaises(Conflito):
            await self.b("gravar_leitura", self.m, ref, campos={"ficha": {}}, schema="carteira-analise-1")
        registro = await self.sql("SELECT ator,acao FROM auditoria WHERE acao LIKE 'preencher%'")
        self.assertEqual(registro, [("222", "preencher_identidade")])
        bruto = b"".join(p.read_bytes() for p in Path(self.tmp.name).glob("db.sqlite3*"))
        self.assertNotIn("Segredo do jogador".encode(), bruto)

    async def test_troca_de_arquivo_no_meio_nao_escreve(self):
        original = self.s._ler

        async def ler_e_trocar(*a):
            ficha = await original(*a)
            await self.b("trocar_arquivo", self.m, self.pid, arquivo="outro_arquivo_ficticio_0001", conexao=self.cid,
                         contrato="analise-13", revisao=1, pedido="troca")
            return ficha
        with patch.object(self.s, "_ler", ler_e_trocar), self.assertRaises(Conflito):
            await self.salvar("identidade", {"nome": "Kaito"})
        self.assertEqual(self.g.posts, [])

    async def test_dados_tortos_nao_chegam_no_google(self):
        base = (await self.estado())["bases"]
        lidas = len(self.g.req)
        for args in (("voar", {}, base["origem"]), ("origem", {"origem": "Latente"}, "x"), ("origem", {"origem": "Latente"}, None)):
            with self.assertRaises(ErroCarteira):
                await self.s.salvar("111", "222", self.pid, args[0], dados=args[1], base=args[2])
        self.assertEqual(len(self.g.req), lidas)
        treino = dict(pericias=[], oficios=[], testes=[], tr_fisico=None, troca=0)
        for passo, dados in (("identidade", []), ("identidade", {"xp": "9"}), ("identidade", {"nome": 3}), ("atributos", {"Força": "3"}),
                             ("atributos", {**ATRIBUTOS, "Força": True}), ("origem", {}), ("origem", {"origem": ["Latente"]}),
                             ("capacidades", {"marcante": 1}), ("caminho", {"trilha": "Muro"}), ("caminho", {"caminho": {}}),
                             ("treinos", {}), ("treinos", treino | {"pericias": "Voar"}), ("treinos", treino | {"pericias": [1]}),
                             ("treinos", treino | {"troca": "1"}), ("treinos", treino | {"tr_fisico": ["FORÇA"]})):
            with self.subTest(passo=passo, dados=dados), self.assertRaises((ErroCarteira, cp.Recusa)):
                await self.salvar(passo, dados, base=base[passo])
        self.assertEqual(self.g.posts, [])

    async def test_texto_a_mao_na_capacidade(self):
        self.f.formulas.pop((PESSOAL, *cp.posicao("D45")))
        self.f.poe(PESSOAL, "D45", "Escrito pelo jogador")
        self.assertEqual((await self.estado())["a_mao"], ["marcante"])
        with self.assertRaisesRegex(cp.Recusa, "à mão"):
            await self.salvar("capacidades", {"marcante": "Marcante A"})
        await self.salvar("capacidades", {"marcante": "✎ Criada com o mestre", "menor1": "Menor A"})

    async def test_configuracao_quebrada_ainda_mostra_a_ficha(self):
        self.f.poe("DADOS_CONFIG", "S4", "três")
        e = await self.estado()
        self.assertEqual((e["limites"], e["criacao"]), (None, False))


class Rotas(Base):
    async def entrar(self, usuario="222", preencher=True):
        self.prov.usuario = usuario
        url = f"/carteira/111/{self.pid}/preencher"
        r = await self.client.get(url)
        self.assertEqual(r.status, 200)
        self.assertNotIn("Nome privado", await r.text())
        self.assertNotIn("unsafe-inline", r.headers["Content-Security-Policy"])
        self.assertIn("frame-src 'none'", r.headers["Content-Security-Policy"])
        self.csrf = (await (await self.client.get("/api/carteira/111/sessao")).json())["csrf"]
        r = await self.post("/api/carteira/111/entrar", {"personagem": self.pid, "idioma": "en"} | ({"preencher": True} if preencher else {}))
        state = parse_qs(urlsplit((await r.json())["url"]).query)["state"][0]
        r = await self.client.get("/oauth/discord/retorno", params={"state": state, "code": "x"}, allow_redirects=False)
        self.assertEqual(r.headers["Location"], (url if preencher else f"/carteira/111/{self.pid}") + "?idioma=en")
        sessao = await (await self.client.get("/api/carteira/111/sessao")).json()
        self.csrf = sessao["csrf"]
        return sessao

    async def post(self, caminho, dados, csrf=None):
        return await self.client.post(caminho, json=dados, headers={"Origin": self.cfg.origem, "X-CSRF-Token": self.csrf if csrf is None else csrf})

    async def passo(self, passo, dados=None, **kw):
        return await self.post(f"/api/carteira/111/personagens/{self.pid}/preencher/{passo}", {} if dados is None else dados, **kw)

    async def test_ler_salvar_e_erros(self):
        self.assertTrue((await self.entrar())["preencher"])
        r = await self.passo("ler")
        self.assertEqual(r.status, 200, await r.text())
        self.assertIn("X-Carteira-Expira-Em", r.headers)
        base = (await r.json())["bases"]
        r = await self.passo("identidade", dict(dados={"nome": "Kaito"}, base=base["identidade"], confirmados=[]))
        self.assertEqual((r.status, (await r.json())["gravou"]), (200, True))
        r = await self.passo("identidade", dict(dados={"nome": "Ren"}, base=base["identidade"], confirmados=[]))
        self.assertEqual(r.status, 409)
        d = await r.json()
        self.assertEqual((d["erro"], d["estado"]["identidade"][0]["valor"]), ("mudou", "Kaito"))
        r = await self.passo("identidade", dict(dados={"nome": "Ren"}, base=d["estado"]["bases"]["identidade"], confirmados=[]))
        self.assertEqual((r.status, await r.json()), (409, {"erro": "preenchido", "campos": ["nome"]}))
        r = await self.passo("atributos", dict(dados=ATRIBUTOS | {"Força": 9}, base=base["atributos"], confirmados=[]))
        self.assertEqual(r.status, 422)
        self.assertTrue((await r.json())["motivos"])
        for corpo in ({}, dict(dados={}, base="0" * 32), dict(dados={}, base="0" * 32, confirmados="nome"),
                      dict(dados={}, base="0" * 32, confirmados=[], arquivo=F1), dict(dados={}, base="0" * 32, confirmados=[1])):
            self.assertEqual((await self.passo("identidade", corpo)).status, 400)
        self.assertEqual((await self.passo("ler", {"pagina": 1})).status, 400)
        self.assertEqual((await self.passo("voar", dict(dados={}, base="0" * 32, confirmados=[]))).status, 400)
        self.assertEqual((await self.passo("identidade", dict(dados={"historia": "x" * 200000}, base="0" * 32, confirmados=[]))).status, 413)
        r = await self.client.get("/static/preencher.js")
        self.assertEqual((r.status, r.content_type), (200, "application/javascript"))
        self.assertIn("frame-src 'none'", r.headers["Content-Security-Policy"])

    async def test_texto_longo_cabe_no_limite_do_passo(self):
        await self.entrar()
        base = (await (await self.passo("ler")).json())["bases"]["identidade"]
        longos = ["aparencia", "cicatrizes", "traco", "historia", "personalidade", "lacos"]
        r = await self.passo("identidade", dict(dados={k: "é" * 4000 for k in longos}, base=base, confirmados=[]))
        self.assertEqual(r.status, 200, await r.text())

    async def test_sem_sessao_csrf_ou_origem(self):
        await self.client.get(f"/carteira/111/{self.pid}/preencher")
        self.csrf = (await (await self.client.get("/api/carteira/111/sessao")).json())["csrf"]
        self.assertEqual((await self.passo("ler")).status, 401)
        await self.entrar()
        self.assertEqual((await self.passo("ler", csrf="errado")).status, 403)
        r = await self.client.post(f"/api/carteira/111/personagens/{self.pid}/preencher/ler", json={},
                                   headers={"Origin": "https://outra.example", "X-CSRF-Token": self.csrf})
        self.assertEqual(r.status, 403)
        self.assertEqual(self.g.req, [])

    async def test_outro_membro_nao_entra(self):
        self.assertFalse((await self.entrar("999"))["preencher"])
        self.assertEqual((await self.passo("ler")).status, 403)
        self.assertEqual(self.g.req, [])

    async def test_login_comum_continua_indo_pro_cartao(self):
        await self.entrar(preencher=False)
        r = await (await self.client.get(f"/api/carteira/111/personagens/{self.pid}")).json()
        self.assertTrue(r["capacidades"]["preencher"])
        self.csrf = "x"
        r = await self.client.post("/api/carteira/111/entrar", json={"personagem": self.pid, "preencher": "sim"},
                                   headers={"Origin": self.cfg.origem, "X-CSRF-Token": "x"})
        self.assertEqual(r.status, 400)

    async def test_pagina_de_outro_servidor_ou_id_torto(self):
        self.assertEqual((await self.client.get(f"/carteira/999/{self.pid}/preencher")).status, 404)
        self.assertEqual((await self.client.get("/carteira/111/abc/preencher")).status, 404)


class Desligado(Base):
    preencher = frozenset()

    async def test_sem_liberacao_ninguem_le_nem_escreve(self):
        entrar, self.post, self.passo = Rotas.entrar, lambda *a, **k: Rotas.post(self, *a, **k), lambda *a, **k: Rotas.passo(self, *a, **k)
        self.assertFalse((await entrar(self))["preencher"])
        self.assertEqual((await self.passo("ler")).status, 403)
        self.assertEqual((await self.passo("identidade", dict(dados={"nome": "X"}, base="0" * 32, confirmados=[]))).status, 403)
        self.assertEqual(self.g.req, [])


class Liberacao(unittest.TestCase):
    def test_vazio_ninguem_lista_e_todos(self):
        cfg = configuracao(Path("x"))
        self.assertFalse(cfg.pode_preencher("222"))
        self.assertTrue(replace(cfg, preencher=frozenset({"222"})).pode_preencher("222"))
        self.assertFalse(replace(cfg, preencher=frozenset({"222"})).pode_preencher("22"))
        self.assertTrue(replace(cfg, preencher=frozenset({"todos"})).pode_preencher("9"))

    def test_le_do_ambiente(self):
        from cryptography.fernet import Fernet
        base = {"PUBLIC_ORIGIN": "https://x.example", "DATABASE_PATH": "x", "ENCRYPTION_KEYS": Fernet.generate_key().decode(),
                "SERVICE_TOKEN": "s" * 32, "GUILDS": "111"} | {k: "x" for k in (
                    "DISCORD_CLIENT_ID", "DISCORD_CLIENT_SECRET", "DISCORD_BOT_TOKEN", "GOOGLE_CLIENT_ID",
                    "GOOGLE_CLIENT_SECRET", "GOOGLE_PROJECT_NUMBER", "PICKER_API_KEY")}
        for valor, esperado in (("", set()), (" 1, 2 ,", {"1", "2"}), ("todos", {"todos"})):
            with patch.dict("os.environ", {"CARTEIRA_" + k: v for k, v in (base | {"PREENCHER": valor}).items()}, clear=True):
                self.assertEqual(ConfigWeb.do_ambiente().preencher, esperado)


if __name__ == "__main__":
    unittest.main()
