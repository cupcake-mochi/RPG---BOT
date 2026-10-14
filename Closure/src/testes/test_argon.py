"""Contrato Argon/Flash, isolamento da reflexão, consumo e migração sem chamadas reais."""
import asyncio
import copy
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from closure_bot.config import carregar
from closure_bot.modelo import ARGON, FLASH, Falhou, Modelos, custo_usd, fila_do_chat, montar_corpo
from closure_bot.registro import Registro

ENTRADA = [{"role": "user", "content": "sistema"}, {"role": "user", "content": "oi"}]
BOA = {"candidates": [{"content": {"parts": [{"text": "Oi."}]}, "finishReason": "STOP"}],
       "usageMetadata": {"promptTokenCount": 8000, "candidatesTokenCount": 40,
                         "thoughtsTokenCount": 110, "cachedContentTokenCount": 6144}}

class Configuracao(unittest.TestCase):
    def test_selecao_sem_mudar_fila_legada(self):
        self.assertEqual(fila_do_chat("", "vertex:antigo"), [("vertex", "antigo")])
        fila = fila_do_chat(ARGON)
        self.assertEqual(fila[0], ("vertex", ARGON))
        self.assertIn(("vertex", FLASH), fila[1:])
        with tempfile.TemporaryDirectory() as t:
            c = carregar(Path(t) / "ausente", ambiente={"MODELO_CHAT": ARGON, "ARGON_MAX_SAIDA": "4096"})
            self.assertEqual((c.modelo_chat, c.argon_max_saida), (ARGON, 4096))
            for env in ({"MODELO_CHAT": "typo"}, {"ARGON_MAX_SAIDA": "0"}):
                with self.assertRaises(ValueError):
                    carregar(Path(t) / "ausente", ambiente=env)

    def test_parametros_e_historico(self):
        for nivel in (None, "modelo", "high", "low"):
            corpo = montar_corpo(ENTRADA, nivel, modelo=ARGON)
            self.assertEqual(corpo["generationConfig"], {"maxOutputTokens": 4096, "thinkingConfig": {"thinkingLevel": "low"}})
        self.assertEqual(montar_corpo(ENTRADA, "low")["generationConfig"]["temperature"], .8)
        self.assertEqual(montar_corpo(ENTRADA, "low", modelo=ARGON)["contents"], montar_corpo(ENTRADA)["contents"])

    def test_precos_por_data_cache_sem_dupla_contagem(self):
        self.assertAlmostEqual(custo_usd(ARGON, 1000000, 1000000, 2026, mes=11), 12)
        self.assertAlmostEqual(custo_usd(ARGON, 1000000, 1000000, 2026, mes=12), 24)
        self.assertAlmostEqual(custo_usd(ARGON, 1000000, 0, 2026, mes=10, tokens_cache=1000000), .10)
        self.assertAlmostEqual(custo_usd(ARGON, 1000000, 0, 2026, mes=10, sem_promocao=True), 4)
        self.assertAlmostEqual(custo_usd(FLASH, 1000000, 0, 2026, mes=12), .75)
        self.assertAlmostEqual(custo_usd(FLASH, 1000000, 0, 2027, mes=1), 1.5)

    def test_migracao_reabre_banco_antigo_sem_perder_linhas(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "banco.sqlite3"
            db = sqlite3.connect(p)
            db.execute("CREATE TABLE chamadas_api(id INTEGER PRIMARY KEY, quando TEXT, modelo TEXT, persona TEXT, gatilho TEXT, tokens_entrada INTEGER, tokens_saida INTEGER, latencia_ms INTEGER, ok INTEGER, erro TEXT)")
            db.execute("INSERT INTO chamadas_api(quando,modelo,tokens_entrada,tokens_saida,ok) VALUES('2026-10-14','vertex:gemini-3.8-flash',1000,40,1)")
            db.commit(); db.close()
            for _ in range(2):
                r = Registro(p)
                self.assertEqual(r.contagens()["chamadas_api"], 1)
                self.assertEqual(len(r.consumo_do_mes(datetime(2026, 10, 14, tzinfo=timezone.utc))), 1)
                r.fechar()

class Chamadas(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.r = Registro(":memory:")
        self.pedidos = []

    def tearDown(self):
        self.r.fechar()

    async def test_fallback_reconstroi_corpo_e_conta_falha_com_uso(self):
        async def enviar(url, corpo, chave):
            self.pedidos.append((url, corpo))
            dados = copy.deepcopy(BOA)
            if ARGON in url:
                dados["candidates"][0] = {"finishReason": "MAX_TOKENS"}
            return dados
        m = Modelos([("vertex", ARGON), ("vertex", FLASH)], {"vertex": "fake"}, self.r, enviar=enviar)
        r = await m.responder(ENTRADA)
        self.assertEqual(r.modelo, FLASH)
        self.assertNotIn("temperature", self.pedidos[0][1]["generationConfig"])
        self.assertEqual(self.pedidos[1][1]["generationConfig"]["maxOutputTokens"], 2048)
        linhas = self.r._db.execute("SELECT ok,tokens_saida,tokens_resposta,tokens_raciocinio,tokens_cache,cortada,custo_estimado_usd FROM chamadas_api").fetchall()
        self.assertEqual(linhas[0][:6], (0, 150, 40, 110, 6144, 1))
        self.assertAlmostEqual(m.gasto_do_mes(), sum(l[-1] for l in linhas))
        self.assertEqual((r.tokens_resposta, r.tokens_raciocinio, r.tokens_cache), (40, 110, 6144))
        self.assertEqual(m._reservado, 0)

    async def test_reflexao_nunca_usa_argon_nem_gratuito(self):
        async def enviar(url, corpo, chave):
            self.pedidos.append((url, corpo))
            return BOA
        m = Modelos(fila_do_chat(ARGON), {"vertex": "v", "gemini": "g"}, self.r, enviar=enviar, raciocinio="high")
        r = await m.responder(ENTRADA, gatilho="reflexao", so_pagos=True)
        self.assertEqual((r.provedor, r.modelo), ("vertex", FLASH))
        self.assertEqual(self.pedidos[0][1]["generationConfig"]["thinkingConfig"], {"thinkingLevel": "low"})

    async def test_argon_e_flash_fallback_global_no_mesmo_projeto(self):
        async def enviar(url, corpo, chave):
            self.pedidos.append(url)
            if ARGON in url:
                raise Falhou(404, "indisponível")
            return BOA
        m = Modelos([("vertex", ARGON), ("vertex", FLASH)], {"vertex": "v"}, self.r,
                    enviar=enviar, vertex_projeto="projeto-teste")
        await m.responder(ENTRADA)
        self.assertIn("/projects/projeto-teste/locations/global/", self.pedidos[0])
        self.assertIn("/projects/projeto-teste/locations/global/", self.pedidos[1])

    async def test_concorrencia_reserva_e_teto_compartilhado(self):
        entrou, terminar = asyncio.Event(), asyncio.Event()
        async def enviar(url, corpo, chave):
            entrou.set()
            await terminar.wait()
            return BOA
        m = Modelos([("vertex", ARGON)], {"vertex": "v"}, self.r, enviar=enviar, teto_usd=.06)
        primeira = asyncio.create_task(m.responder(ENTRADA))
        await entrou.wait()
        with self.assertRaises(Falhou) as erro:
            await m.responder(ENTRADA)
        self.assertEqual(erro.exception.codigo, "teto")
        terminar.set()
        await primeira
        self.assertEqual(m._reservado, 0)

    async def test_cancelamento_devolve_reserva(self):
        async def enviar(*args):
            raise asyncio.CancelledError()
        m = Modelos([("vertex", ARGON)], {"vertex": "v"}, self.r, enviar=enviar)
        with self.assertRaises(asyncio.CancelledError):
            await m.responder(ENTRADA)
        self.assertEqual(m._reservado, 0)

    async def test_teto_zero_nao_envia(self):
        async def enviar(*args):
            self.fail("não pode enviar")
        m = Modelos([("vertex", ARGON)], {"vertex": "v"}, self.r, enviar=enviar, teto_usd=0)
        with self.assertRaises(Falhou):
            await m.responder(ENTRADA)
