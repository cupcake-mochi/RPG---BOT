"""Criar ficha vazia: Drive fictício em memória, sem rede nem conta externa."""
import asyncio
from dataclasses import replace
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import unittest
from urllib.parse import parse_qs, urlsplit

import httpx

from carteira_viva import criacao
from carteira_viva.backup import gravar_backup, restaurar_backup
from carteira_viva.banco import Cadastro, DIA
from carteira_viva.config_web import ConfigWeb
from carteira_viva.copias_google import DestinoCopia, MIME
from carteira_viva.modelos import CriacaoBloqueada
from carteira_viva.permissoes import Membro
from carteira_viva.ponte_discord import ConectarFicha
from carteira_viva.provedores import ErroProvedor, Provedores
from carteira_viva.segredos import AcessoNegado, Conflito
from carteira_viva.web import CONSULTAS, CRIACOES, DADOS
from closure_bot.recursos_publicos import FICHA_CICLO_MALDITO
from testes.test_carteira_banco import Fixtures
from testes.test_carteira_modelos import referencia
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_web import F1, ProvedorFicticio, WebFixture

MODELO = FICHA_CICLO_MALDITO.split("/d/")[1].split("/")[0]
COPIA = "copia_ficticia_para_teste_0001"


class Drive(httpx.AsyncBaseTransport):
    """Só o que a criação usa: metadados, cópia, busca por marcador."""
    def __init__(self):
        self.req, self.copias, self.autorizado, self.hook = [], {}, True, None
        self.perde_resposta = self.nao_copia = self.busca_vazia = False
        self.extra, self.status_meta = {}, 200

    def posts(self):
        return [r for r in self.req if r.method == "POST"]

    async def handle_async_request(self, r):
        self.req.append(r)
        if self.hook:
            await self.hook(r)
        assert r.url.host == "www.googleapis.com", r.url
        partes = r.url.path.split("/")
        if r.method == "POST":
            corpo = json.loads(await r.aread())
            novo = COPIA if not self.copias else f"{COPIA}_{len(self.copias)}"
            if not self.nao_copia:
                self.copias[novo] = corpo
            if self.perde_resposta or self.nao_copia:
                return httpx.Response(503, json={})
            return httpx.Response(200, json={"id": novo})
        if len(partes) < 5:  # busca
            q = r.url.params["q"]
            achados = [] if self.busca_vazia else [k for k, v in self.copias.items()
                                                   if all(x in q for x in v["appProperties"].values())]
            return httpx.Response(200, json={"files": [{"id": x} for x in achados]})
        arquivo = partes[4]
        meta = dict(id=arquivo, mimeType=MIME, trashed=False, version="7", modifiedTime="2026-11-24T12:00:00.000Z")
        if arquivo in self.copias:
            if self.status_meta != 200:
                return httpx.Response(self.status_meta, json={})
            meta |= dict(isAppAuthorized=True, ownedByMe=True, shared=False, version="1",
                         appProperties=self.copias[arquivo]["appProperties"],
                         permissions=[dict(type="user", role="owner")]) | self.extra
            return httpx.Response(200, json=meta)
        if arquivo == MODELO and self.autorizado:
            return httpx.Response(200, json=meta | dict(isAppAuthorized=True))
        return httpx.Response(404, json={})


class ProvedorCriacao(ProvedorFicticio):
    def __init__(self, cfg, agora):
        super().__init__(cfg, agora)
        self.drive = self.transporte = Drive()
        self.falhas = 0

    async def validar_arquivo(self, acesso, arquivo):
        if arquivo == MODELO or arquivo in self.drive.copias:
            await self.observar_arquivo(acesso, arquivo)
            if arquivo != MODELO and self.falhas:
                self.falhas -= 1
                raise ErroProvedor("temporario")
            return {"arquivo": arquivo, "nome_arquivo": "Ficha - Ciclo Maldito (CM)", "nome": "Coloque o nome do personagem aqui",
                    "contrato": "analise-13", "prova_parcial": True}
        return await super().validar_arquivo(acesso, arquivo)


class BancoCriacao(Fixtures, unittest.TestCase):
    def preparar(self, pedido="um", nome="Ayla", **kw):
        self.cid = self.conectar(**kw)
        return self.c.preparar_criacao(self.m, conexao=self.cid, nome=nome, pedido=pedido)

    def enviar(self, ref):
        self.c.fixar_versao_copia(self.m, ref, "7")
        self.assertTrue(self.c.armar_envio_copia(self.m, ref))

    def identificar(self, ref, arquivo=COPIA):
        self.c.identificar_criacao(self.m, ref, DestinoCopia(arquivo, "1", ref.operacao, MODELO))

    def total(self):
        return self.c.db.execute("SELECT count(*) FROM copias_rest").fetchone()[0]

    def test_ciclo_inteiro_cadastra_e_apaga_o_registro(self):
        ref = self.preparar()
        self.enviar(ref); self.identificar(ref)
        r = self.c.concluir_criacao(self.m, ref, "analise-13")
        self.assertEqual((r["arquivo"], r["perfil"]["nome"], r["responsavel"]), (COPIA, "Ayla", self.m.usuario))
        self.assertEqual(self.total(), 0)
        with self.assertRaises(Conflito):
            self.c.concluir_criacao(self.m, ref, "analise-13")
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM personagens").fetchone()[0], 1)

    def test_nada_aberto_no_banco(self):
        ref = self.preparar(nome="Nome só do jogador")
        self.enviar(ref); self.identificar(ref)
        self.c.db.execute("PRAGMA wal_checkpoint")
        bruto = self.path.read_bytes()
        for segredo in (b"Nome s", COPIA.encode(), MODELO.encode(), b"refresh-ficticio-secreto"):
            self.assertNotIn(segredo, bruto)

    def test_pedido_que_nunca_saiu_e_trocado(self):
        a = self.preparar("um")
        b = self.preparar("dois")  # novo login: autorização nova
        self.assertNotEqual(a.operacao, b.operacao)
        self.assertEqual(self.total(), 1)

    def test_novo_login_retoma_copia_enviada_sem_criar_outra(self):
        a = self.preparar("um", "Primeiro nome")
        self.enviar(a)
        with self.assertRaises(Conflito):  # autorização mudou: a tarefa antiga para
            self.conectar(); self.c.contexto_criacao(self.m, a)
        b = self.preparar("dois", "Nome novo")
        self.assertEqual(a.operacao, b.operacao)
        self.identificar(b)
        c = self.preparar("tres", "Nome final")
        self.assertEqual(c.operacao, a.operacao)
        self.assertEqual(self.c.concluir_criacao(self.m, c, "analise-13")["perfil"]["nome"], "Nome final")

    def test_outra_conta_google_espera_e_depois_comeca_do_zero(self):
        self.enviar(self.preparar("um"))
        with self.assertRaises(ErroProvedor) as e:
            self.preparar("dois", conta="outra-conta")
        self.assertEqual(e.exception.codigo, "copia_incerta")
        self.clock[0] += criacao.ESPERA_COPIA
        self.preparar("dois", conta="outra-conta")
        self.assertEqual(self.total(), 1)

    def test_identificada_por_outra_conta_nao_bloqueia(self):
        a = self.preparar("um")
        self.enviar(a); self.identificar(a)
        b = self.preparar("dois", conta="outra-conta")
        self.assertNotEqual(a.operacao, b.operacao)

    def test_reinicio_so_depois_da_espera(self):
        a = self.preparar()
        self.assertFalse(self.c.reiniciar_criacao(self.m, a))  # ainda nem saiu
        self.enviar(a)
        self.assertFalse(self.c.reiniciar_criacao(self.m, a))
        self.clock[0] += criacao.ESPERA_COPIA
        self.assertTrue(self.c.reiniciar_criacao(self.m, a))
        self.assertEqual(self.c.contexto_criacao(self.m, a)["estado"], "preparada")

    def test_isolamento_entre_jogadores_e_servidores(self):
        a = self.preparar()
        for outro in (self.outro, replace(self.m, servidor="mesa-b")):
            with self.assertRaises(AcessoNegado):
                self.c.contexto_criacao(outro, a)
        with self.assertRaises(AcessoNegado):
            self.c.preparar_criacao(self.outro, conexao=self.cid, nome="x", pedido="y")

    def test_desconectar_impede_continuar(self):
        a = self.preparar()
        self.c.desconectar(self.m, self.cid)
        with self.assertRaises(AcessoNegado):
            self.c.contexto_criacao(self.m, a)

    def test_modelo_do_servidor_bloqueia(self):
        for escolha in ("era", "servidor"):
            rev = self.c.modelos(self.m)["revisao"]
            self.c.configurar_modelo(self.admin, escolha=escolha, revisao=rev,
                                     previa=referencia() if escolha == "servidor" else None)
            with self.subTest(escolha), self.assertRaises(CriacaoBloqueada):
                self.c.modelo_criacao(self.m)
        self.c.configurar_modelo(self.admin, escolha="ciclo", revisao=self.c.modelos(self.m)["revisao"])
        self.assertEqual(self.c.modelo_criacao(self.m), MODELO)

    def test_troca_de_modelo_no_meio_para_a_copia(self):
        a = self.preparar()
        self.enviar(a)
        self.c.configurar_modelo(self.admin, escolha="era", revisao=0)
        with self.assertRaises((Conflito, CriacaoBloqueada)):
            self.c.contexto_criacao(self.m, a)

    def test_destino_de_outra_operacao_ou_ja_cadastrado_recusado(self):
        a = self.preparar()
        self.enviar(a)
        with self.assertRaises(Conflito):
            self.c.identificar_criacao(self.m, a, DestinoCopia(COPIA, "1", "a" * 64, MODELO))
        self.c.cadastrar(self.m, conexao=self.cid, arquivo=COPIA, nome="x", contrato="analise-13",
                         responsabilidade=True, pedido="p")
        with self.assertRaises(Conflito):
            self.identificar(a)

    def test_pedido_abandonado_expira_e_solta_a_conexao(self):
        self.enviar(self.preparar())
        self.clock[0] += DIA - 1
        self.assertEqual(self.c.limpar()["criacoes"], 0)
        self.clock[0] += 1
        self.assertEqual(self.c.limpar()["criacoes"], 1)
        self.clock[0] += DIA
        self.c.limpar()
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM conexoes").fetchone()[0], 0)

    def test_limpeza_nao_mexe_na_copia_do_protocolo_antigo(self):
        cid = self.conectar()
        ref = self.c.preparar_copia_modelo(self.m, conexao=cid, modelo="ciclo", pedido="antigo")
        with self.assertRaises(Conflito):  # e a criação não passa por cima dela
            self.c.preparar_criacao(self.m, conexao=cid, nome="x", pedido="y")
        with self.assertRaises(Conflito):
            self.c.contexto_criacao(self.m, ref)
        self.clock[0] += 2 * DIA
        self.assertEqual(self.c.limpar()["criacoes"], 0)

    def test_apagar_meus_dados_remove_o_pedido(self):
        self.enviar(self.preparar())
        self.c.apagar_usuario(self.m.usuario)
        self.assertEqual(self.total(), 0)

    def test_rotacao_e_backup_preservam_o_pedido(self):
        from cryptography.fernet import Fernet
        a = self.preparar()
        self.enviar(a)
        nova = Fernet.generate_key()
        self.c.rotacionar_chave(nova)
        self.assertEqual(self.c.contexto_criacao(self.m, a)["estado"], "enviada")
        bak, dest = self.pasta / "x.cvb", self.pasta / "r.sqlite3"
        gravar_backup(self.c, bak)
        restaurar_backup(bak, dest, (nova,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(dest, (nova,), remocoes=self.c.remocoes, agora=self.agora) as c:
            self.assertEqual(c.contexto_criacao(self.m, a)["nome"], "Ayla")

    def test_nome_do_arquivo_sem_controle(self):
        self.assertEqual(criacao.nome_do_arquivo("  Ayla\n‮ da Silva "), "Ficha - Ayla da Silva")
        self.assertEqual(len(criacao.nome_do_arquivo("x" * 300)), 108)


class ServicoCriacao(Fixtures, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from carteira_viva.consultas import Consultas
        from carteira_viva.fluxos import DadosAsync
        self.cfg = configuracao(self.pasta / "s.sqlite3")
        self.dados = DadosAsync(self.cfg, agora=self.agora)
        await self.dados.iniciar()
        self.prov = ProvedorCriacao(self.cfg, self.agora)
        self.drive = self.prov.drive
        self.s = Consultas(self.dados, self.prov, agora=self.agora)
        self.m = Membro("111", "222")

    async def asyncTearDown(self):
        await self.s.fechar()
        await self.prov.fechar()
        await self.dados.fechar()

    async def b(self, metodo, *a, **kw):
        return await self.dados.chamar("cadastro." + metodo, *a, **kw)

    async def ref(self, pedido="um", nome="Ayla"):
        cid = await self.b("conectar", self.m, conta="conta_ficticia", cliente=self.cfg.google_id, refresh_token="r" + pedido)
        return await self.b("preparar_criacao", self.m, conexao=cid, nome=nome, pedido=pedido)

    async def criar(self, ref=None, esperas=(0, 0)):
        return await criacao.criar_ficha(self.s, "111", "222", ref or await self.ref(), esperas=esperas)

    async def test_uma_copia_com_nome_marcador_e_sem_compartilhar(self):
        r = await self.criar()
        self.assertEqual(r["arquivo"], COPIA)
        post, = self.drive.posts()
        corpo = json.loads(post.content)
        self.assertEqual(corpo["name"], "Ficha - Ayla")
        self.assertEqual(corpo["parents"], ["root"])
        self.assertEqual(set(corpo["appProperties"]), {"cv_operacao", "cv_origem", "cv_protocolo"})
        # Resumo sha256 pode ter "222" por acaso; o que não pode é o ID em claro.
        self.assertEqual(corpo["appProperties"]["cv_protocolo"], "1")
        for campo in ("cv_operacao", "cv_origem"):
            self.assertRegex(corpo["appProperties"][campo], r"\A[0-9a-f]{64}\Z")
        # Nenhuma escrita além da cópia.
        self.assertEqual({r.method for r in self.drive.req}, {"GET", "POST"})

    async def test_resposta_perdida_acha_a_copia_e_nao_repete(self):
        self.drive.perde_resposta = True
        self.assertEqual((await self.criar())["arquivo"], COPIA)
        self.assertEqual(len(self.drive.posts()), 1)

    async def test_copia_que_nao_aconteceu_so_repete_depois_da_espera(self):
        self.drive.nao_copia = True
        with self.assertRaises(ErroProvedor):
            await self.criar()
        with self.assertRaises(ErroProvedor) as e:
            await self.criar(await self.ref("dois"))
        self.assertEqual(e.exception.codigo, "copia_incerta")
        self.assertEqual(len(self.drive.posts()), 1)
        self.clock[0] += criacao.ESPERA_COPIA
        self.drive.nao_copia = False
        self.assertEqual((await self.criar(await self.ref("tres")))["arquivo"], COPIA)
        self.assertEqual(len(self.drive.posts()), 2)

    async def test_queda_entre_copia_e_cadastro_e_retomada(self):
        self.prov.falhas = 3
        with self.assertRaises(ErroProvedor):
            await self.criar()
        r = await self.criar(await self.ref("dois", "Outro nome"))
        self.assertEqual(r["perfil"]["nome"], "Outro nome")
        self.assertEqual(len(self.drive.posts()), 1)

    async def test_leitura_lenta_da_copia_nova_e_repetida(self):
        self.prov.falhas = 2
        self.assertEqual((await self.criar())["arquivo"], COPIA)

    async def test_queda_durante_o_post_e_retomada(self):
        pronto = asyncio.Event()
        async def hook(r):
            if r.method == "POST":
                pronto.set()
                await asyncio.sleep(60)
        self.drive.hook = hook
        tarefa = asyncio.create_task(self.criar())
        await asyncio.wait_for(pronto.wait(), 5)
        tarefa.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await tarefa
        self.drive.hook = None
        self.drive.copias[COPIA] = {"appProperties": criacao_props(self.drive.posts()[0])}
        self.assertEqual((await self.criar(await self.ref("dois")))["arquivo"], COPIA)
        self.assertEqual(len(self.drive.posts()), 1)

    async def test_pedidos_juntos_viram_uma_copia(self):
        ref = await self.ref()
        a, b = await asyncio.gather(self.criar(ref), self.criar(ref))
        self.assertEqual(a["id"], b["id"])
        self.assertEqual(len(self.drive.posts()), 1)

    async def test_copia_na_lixeira_ou_compartilhada_libera_outro_pedido(self):
        for extra in (dict(trashed=True), dict(shared=True)):
            with self.subTest(extra):
                self.drive.extra = extra
                antes = len(self.drive.posts())
                with self.assertRaises(ErroProvedor) as e:
                    await self.criar(await self.ref("p" + str(extra)))
                self.assertEqual(e.exception.codigo, "copia_invalida")
                self.drive.extra = {}
                self.drive.copias.clear()
                self.assertEqual(len(self.drive.posts()), antes + 1)
        self.assertEqual((await self.criar(await self.ref("fim")))["arquivo"], COPIA)

    async def test_modelo_nao_autorizado_nao_copia(self):
        self.drive.autorizado = False
        with self.assertRaises(ErroProvedor):
            await self.criar()
        self.assertFalse(self.drive.posts())

    async def test_desconexao_antes_do_envio_impede_a_copia(self):
        original = self.s._banco
        async def banco(metodo, *a, **kw):
            r = await original(metodo, *a, **kw)
            if metodo == "armar_envio_copia":
                await original("desconectar", self.m, a[1].conexao)
            return r
        self.s._banco = banco
        with self.assertRaises(AcessoNegado):
            await self.criar()
        self.assertFalse(self.drive.posts())

    async def test_saida_do_servidor_antes_do_cadastro_nao_cadastra(self):
        async def hook(r):
            if r.method == "POST":
                self.prov.presente = False
        self.drive.hook = hook
        with self.assertRaises(AcessoNegado):
            await self.criar()
        def n():
            return self.dados.store.c.db.execute("SELECT count(*) FROM personagens").fetchone()[0]
        self.assertEqual(await asyncio.wrap_future(self.dados.executor.submit(n)), 0)

    async def test_saida_durante_a_leitura_da_copia_nao_cadastra(self):
        original = self.prov.validar_arquivo
        async def validar(acesso, arquivo):
            r = await original(acesso, arquivo)
            self.prov.presente = False
            return r
        self.prov.validar_arquivo = validar
        with self.assertRaises(AcessoNegado):
            await self.criar()


def criacao_props(request):
    return json.loads(request.content)["appProperties"]


class WebCriacao(WebFixture, unittest.IsolatedAsyncioTestCase):
    provedor_tipo = ProvedorCriacao

    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def abrir_cliente(self):
        self.cfg = replace(self.cfg, criar=frozenset({"222"}))
        self.prov.cfg = self.cfg
        await super().abrir_cliente()

    async def ate_revisar(self):
        await self.comecar("criar")
        await self.oauth("discord")
        self.assertEqual((self.s["fase"], self.s.get("conexoes")), ("google", None))
        await self.oauth("google")
        self.assertEqual(self.s["fase"], "revisar", self.s)

    async def terminar(self):
        await asyncio.gather(*self.app[CRIACOES])
        await self.atualizar()

    async def interno(self, acao, usuario="222"):
        return await self.client.post("/interno/conexoes", json={"servidor": "111", "usuario": usuario, "acao": acao, "personagem": None},
                                      headers={"Authorization": "Bearer " + self.cfg.servico_token})

    async def test_fluxo_inteiro(self):
        await self.ate_revisar()
        self.assertEqual(self.s["previa"]["arquivo"], MODELO)
        r = await self.confirmar()
        self.assertEqual(r.status, 200, await r.text())
        self.assertNotIn("resultado", await r.json())
        await self.terminar()
        self.assertEqual(self.s["fase"], "concluido", self.s)
        self.assertEqual(self.s["resultado"]["arquivo"], COPIA)
        self.assertEqual(self.s["resultado"]["perfil"]["nome"], "Nome confirmado")
        self.assertEqual(len(self.prov.drive.posts()), 1)
        self.assertEqual(await self.scalar("SELECT count(*) FROM copias_rest"), 0)
        self.assertEqual(await self.scalar("SELECT arquivo FROM fontes"), COPIA)

    async def test_url_do_google_abre_o_seletor_so_no_modelo(self):
        await self.comecar("criar")
        await self.oauth("discord")
        url = (await (await self.post("/api/login/google")).json())["url"]
        q = parse_qs(urlsplit(url).query)
        self.assertEqual((q["trigger_onepick"], q["file_ids"]), (["true"], [MODELO]))
        self.assertIn("consent", q["prompt"][0])
        self.assertEqual(q["scope"], ["https://www.googleapis.com/auth/drive.file"])

    async def test_cadastro_comum_continua_sem_o_seletor(self):
        await self.comecar()
        await self.oauth("discord")
        url = (await (await self.post("/api/login/google")).json())["url"]
        self.assertNotIn("trigger_onepick", url)

    async def test_desistir_no_google_volta_pra_etapa_e_tenta_de_novo(self):
        await self.comecar("criar")
        await self.oauth("discord")
        r = await self.callback("google", await self.estado_oauth("google"), error="access_denied")
        self.assertEqual(r.status, 302)
        await self.atualizar()
        self.assertEqual((self.s["fase"], self.s["aviso"]), ("google", "cancelado"))
        self.assertEqual(await self.scalar("SELECT count(*) FROM conexoes"), 0)
        await self.oauth("google")
        self.assertEqual((self.s["fase"], self.s["aviso"]), ("revisar", None))

    async def test_sem_escolher_o_modelo_volta_com_aviso(self):
        self.prov.drive.autorizado = False
        await self.comecar("criar")
        await self.oauth("discord")
        await self.oauth("google")
        self.assertEqual((self.s["fase"], self.s["aviso"]), ("google", "modelo"))
        self.prov.drive.autorizado = True
        await self.oauth("google")
        self.assertEqual(self.s["fase"], "revisar")

    async def test_pagina_nao_recebe_token_nem_escolhe_outro_arquivo(self):
        await self.ate_revisar()
        r = await self.client.get("/api/picker", params={"ticket": self.ticket})
        self.assertEqual(r.status, 409)
        self.assertEqual((await self.post("/api/selecionar", {"arquivo": F1})).status, 409)
        await self.atualizar()
        self.assertEqual(self.s["fase"], "revisar")

    async def test_conexao_antiga_nao_pula_o_seletor(self):
        cid = await self.seed()
        await self.comecar("criar")
        await self.oauth("discord")
        self.assertEqual((await self.post("/api/usar", {"conexao": cid})).status, 409)

    async def test_exige_nome_e_responsabilidade(self):
        await self.ate_revisar()
        for dados in ({"nome": "  ", "responsabilidade": True}, {"nome": "Ayla", "responsabilidade": False}):
            self.assertEqual((await self.post("/api/confirmar", dados)).status, 400)
        await self.atualizar()
        self.assertEqual(self.s["fase"], "revisar")
        self.assertFalse(self.prov.drive.posts())

    async def test_confirmar_duas_vezes_nao_copia_duas(self):
        await self.ate_revisar()
        a, b = await asyncio.gather(self.confirmar(), self.confirmar())
        self.assertEqual(sorted((a.status, b.status)), [200, 409])
        await self.terminar()
        self.assertEqual(len(self.prov.drive.posts()), 1)
        r = await self.confirmar()
        self.assertEqual((await r.json())["resultado"]["arquivo"], COPIA)

    async def test_nao_cancela_com_a_copia_em_andamento(self):
        solta = asyncio.Event()
        async def hook(r):
            if r.method == "POST":
                await solta.wait()
        self.prov.drive.hook = hook
        await self.ate_revisar()
        await self.confirmar()
        await self.atualizar()
        self.assertEqual(self.s["fase"], "copiando")
        self.assertNotIn("google", self.s)
        self.assertEqual((await self.post("/api/cancelar")).status, 409)
        solta.set()
        await self.terminar()
        self.assertEqual(self.s["fase"], "concluido")

    async def test_falha_da_copia_aparece_com_codigo_publico(self):
        self.prov.drive.extra = {"shared": True}
        await self.ate_revisar()
        await self.confirmar()
        with self.assertLogs("carteira_viva.criacao", "WARNING") as log:
            await self.terminar()
        self.assertEqual((self.s["fase"], self.s["erro"]), ("falhou", "copia_invalida"))
        self.assertNotIn(COPIA, "".join(log.output))
        self.assertEqual(await self.scalar("SELECT count(*) FROM personagens"), 0)

    async def test_reinicio_no_meio_retoma_no_pedido_seguinte(self):
        pronto = asyncio.Event()
        async def hook(r):
            if r.method == "POST":
                pronto.set()
                await asyncio.sleep(60)
        self.prov.drive.hook = hook
        await self.ate_revisar()
        await self.confirmar()
        await asyncio.wait_for(pronto.wait(), 5)
        await self.client.close()
        self.prov.drive.hook = None
        self.prov.drive.copias[COPIA] = {"appProperties": criacao_props(self.prov.drive.posts()[0])}
        await self.abrir_cliente()
        await self.ate_revisar()
        await self.confirmar()
        await self.terminar()
        self.assertEqual(self.s["fase"], "concluido", self.s)
        self.assertEqual(len(self.prov.drive.posts()), 1)

    async def test_solicitacao_vencida_durante_a_copia_ainda_cadastra(self):
        solta = asyncio.Event()
        async def hook(r):
            if r.method == "POST":
                await solta.wait()
        self.prov.drive.hook = hook
        await self.ate_revisar()
        await self.confirmar()
        self.clock[0] += 601
        solta.set()
        await asyncio.gather(*self.app[CRIACOES])
        self.assertEqual(await self.scalar("SELECT count(*) FROM personagens"), 1)

    async def test_desligado_ou_fora_da_lista_nao_cria(self):
        r = await self.interno("criar", "333")
        self.assertEqual((r.status, (await r.json())["erro"]), (400, "modelo_bloqueado"))
        self.assertFalse((await (await self.interno("cadastro", "333")).json())["criar"])
        self.assertTrue((await (await self.interno("cadastro")).json())["criar"])

    async def test_liberacao_retirada_depois_de_abrir_barra_a_confirmacao(self):
        await self.ate_revisar()
        object.__setattr__(self.cfg, "criar", frozenset())
        r = await self.confirmar()
        self.assertEqual((r.status, (await r.json())["erro"]), (400, "modelo_bloqueado"))
        self.assertFalse(self.prov.drive.posts())

    async def test_servidor_com_a_era_nao_oferece(self):
        admin = replace(self.membro, administrador=True)
        await self.app[DADOS].chamar("cadastro.configurar_modelo", admin, escolha="era", revisao=0)
        self.assertEqual((await self.interno("criar")).status, 400)
        self.assertFalse((await (await self.interno("cadastro")).json())["criar"])

    async def test_cadastro_vira_criacao_depois_do_discord(self):
        await self.comecar()
        self.assertEqual((await self.post("/api/criar")).status, 409)  # antes do Discord
        await self.oauth("discord")
        self.assertTrue(self.s["pode_criar"])
        self.assertEqual((await self.post("/api/criar", csrf="x" * 40)).status, 403)
        self.assertEqual((await self.post("/api/criar")).status, 200)
        await self.atualizar()
        self.assertEqual(self.s["acao"], "criar")
        await self.oauth("google")
        await self.confirmar()
        await self.terminar()
        self.assertEqual(self.s["resultado"]["arquivo"], COPIA)

    async def test_troca_e_modelo_nao_viram_criacao(self):
        _, p = await self.seed(F1)
        await self.comecar("troca", p["id"])
        await self.oauth("discord")
        self.assertNotIn("pode_criar", self.s)
        self.assertEqual((await self.post("/api/criar")).status, 409)


class ConfigCriacao(unittest.TestCase):
    def test_lista_de_quem_pode(self):
        cfg = configuracao("x")
        self.assertFalse(cfg.pode_criar("222"))
        self.assertTrue(replace(cfg, criar=frozenset({"222"})).pode_criar("222"))
        self.assertTrue(replace(cfg, criar=frozenset({"todos"})).pode_criar("999"))

    def test_ambiente_opcional(self):
        from cryptography.fernet import Fernet
        base = {"PUBLIC_ORIGIN": "https://x.example", "DATABASE_PATH": "x", "ENCRYPTION_KEYS": Fernet.generate_key().decode(),
                "SERVICE_TOKEN": "s" * 40, "DISCORD_CLIENT_ID": "1", "DISCORD_CLIENT_SECRET": "1", "DISCORD_BOT_TOKEN": "1",
                "GOOGLE_CLIENT_ID": "1", "GOOGLE_CLIENT_SECRET": "1", "GOOGLE_PROJECT_NUMBER": "1", "PICKER_API_KEY": "1", "GUILDS": "1"}
        amb = {"CARTEIRA_" + k: v for k, v in base.items()}
        with patch.dict("os.environ", amb, clear=True):
            self.assertEqual(ConfigWeb.do_ambiente().criar, frozenset())
        with patch.dict("os.environ", amb | {"CARTEIRA_CRIAR": " 222, 333 ,"}, clear=True):
            self.assertEqual(ConfigWeb.do_ambiente().criar, frozenset({"222", "333"}))

    def test_modelo_so_no_login_google(self):
        p = Provedores(configuracao("x"))
        for provedor, modelo in (("discord", MODELO), ("google", "x&y=1")):
            with self.assertRaises(ErroProvedor):
                p.autorizar(provedor, "e" * 43, "v" * 64, modelo=modelo)


class PonteCriacao(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.cog = ConectarFicha(None, "https://carteira.example", "ficticio_" * 5)
        self.i = SimpleNamespace(guild_id=111, user=SimpleNamespace(id=222), locale="pt-BR",
                                 response=SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock()),
                                 followup=SimpleNamespace(send=AsyncMock()))

    async def executar(self, acao, dados, status=200):
        resposta = AsyncMock()
        resposta.status = status
        resposta.json.return_value = dados
        request = AsyncMock()
        request.__aenter__.return_value = resposta
        sessao = AsyncMock()
        sessao.__aenter__.return_value = SimpleNamespace(post=lambda *a, **kw: request)
        with patch("carteira_viva.ponte_discord.aiohttp.ClientSession", return_value=sessao):
            await self.cog.iniciar(self.i, acao)
        self.assertTrue(self.i.response.defer.call_args.kwargs["ephemeral"])
        call = self.i.followup.send.call_args
        self.assertTrue(call.kwargs["ephemeral"])
        return call

    URL = "https://carteira.example/conectar?ticket=ficticio"

    async def test_criar_manda_link_privado(self):
        call = await self.executar("criar", {"url": self.URL})
        botao, = call.kwargs["view"].children
        self.assertEqual((botao.label, botao.url), ("Criar minha ficha", self.URL))

    async def test_cadastro_so_oferece_criar_quando_liberado(self):
        call = await self.executar("cadastro", {"url": self.URL, "criar": True})
        self.assertEqual([b.label for b in call.kwargs["view"].children], ["Conectar minha ficha", "Criar minha ficha"])
        call = await self.executar("cadastro", {"url": self.URL, "criar": False})
        self.assertEqual([b.label for b in call.kwargs["view"].children], ["Conectar minha ficha"])

    async def test_botao_abre_a_criacao_de_quem_clicou(self):
        call = await self.executar("cadastro", {"url": self.URL, "criar": True})
        with patch.object(self.cog, "iniciar", AsyncMock()) as iniciar:
            await call.kwargs["view"].children[1].callback(self.i)
        iniciar.assert_awaited_once_with(self.i, "criar")

    async def test_nao_liberado_explica_o_caminho_manual(self):
        call = await self.executar("criar", {"erro": "modelo_bloqueado"}, 400)
        self.assertIn("GC:guia criar", call.args[0])
        self.assertNotIn("view", call.kwargs)
        self.i.locale = "en-US"
        self.assertIn("not enabled", (await self.executar("criar", {"erro": "modelo_bloqueado"}, 400)).args[0])

    async def test_outro_erro_e_generico(self):
        call = await self.executar("criar", {"erro": "limite"}, 429)
        self.assertIn("Não consegui abrir", call.args[0])


if __name__ == "__main__":
    unittest.main()
