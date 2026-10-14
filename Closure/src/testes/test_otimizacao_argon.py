"""Proteções de gasto e experimento de prompt, sem chamar serviços externos."""
import asyncio
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from closure_bot.config import carregar
from closure_bot.modelo import ARGON, FLASH, Falhou, Modelos, fila_do_chat
from closure_bot.registro import Registro

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ferramentas"))
import comparar_argon
import perfil_argon

ENTRADA = [{"role": "user", "content": "sistema"}, {"role": "user", "content": "oi"}]
BOA = {"candidates": [{"content": {"parts": [{"text": "Oi."}]}, "finishReason": "STOP"}],
       "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 10}}


class Configuracao(unittest.TestCase):
    def test_misto_exige_canal_explicitamente_escolhido(self):
        with tempfile.TemporaryDirectory() as t:
            arquivo = Path(t) / "ausente"
            c = carregar(arquivo, {"MODELO_CHAT": "misto", "ARGON_CANAIS": "10,20"})
            self.assertTrue(c.usa_argon(10))
            self.assertFalse(c.usa_argon(30))
            self.assertFalse(carregar(arquivo, {"ARGON_CANAIS": "10"}).usa_argon(10))
            self.assertFalse(carregar(arquivo, {"MODELO_CHAT": "misto"}).usa_argon(10))
            self.assertEqual(c.argon_teto_usd, 1.0)
            self.assertEqual(carregar(arquivo, {"ARGON_TETO_USD": "0"}).argon_teto_usd, 0)
            for chave in ("ARGON_TETO_USD", "TETO_MENSAL_USD"):
                for valor in ("nan", "inf", "-1", "errado"):
                    with self.assertRaises(ValueError):
                        carregar(arquivo, {chave: valor})
            with self.assertRaises(ValueError):
                carregar(arquivo, {"ARGON_CANAIS": "10,errado"})

    def test_fila_respeita_fallback_personalizado(self):
        fila = f"vertex:{ARGON},vertex:{FLASH}"
        self.assertEqual(fila_do_chat("misto", fila), [("vertex", FLASH)])
        self.assertEqual(fila_do_chat(ARGON, fila), [("vertex", ARGON), ("vertex", FLASH)])


class Orcamento(unittest.IsolatedAsyncioTestCase):
    async def test_flash_e_argon_usam_rota_global_explicita_quando_ha_projeto(self):
        urls = []
        async def enviar(url, corpo, chave):
            urls.append(url)
            self.assertEqual(chave, "segredo-falso")
            return BOA
        for modelo in (FLASH, ARGON):
            m = Modelos([("vertex", modelo)], {"vertex": "segredo-falso"}, enviar=enviar,
                        vertex_projeto="projeto-teste")
            await m.responder(ENTRADA)
        self.assertEqual(len(urls), 2)
        for url, modelo in zip(urls, (FLASH, ARGON)):
            self.assertIn(f"/projects/projeto-teste/locations/global/publishers/google/models/{modelo}:", url)
            self.assertNotIn("segredo-falso", url)

    async def test_http_confirmado_nao_reserva_custo_e_200_bloqueado_sem_uso_reserva(self):
        r = Registro(":memory:")
        try:
            for codigo in (400, 403, 429, 500, 503):
                async def enviar(*args):
                    raise Falhou(codigo, "status HTTP confirmado")
                m = Modelos([("vertex", ARGON)], {"vertex": "v"}, r, enviar=enviar)
                with self.assertRaises(Falhou):
                    await m.responder(ENTRADA)
                self.assertEqual(m.gasto_do_mes(), 0)
            async def bloqueada(*args):
                return {"promptFeedback": {"blockReason": "SAFETY"}}
            m = Modelos([("vertex", ARGON)], {"vertex": "v"}, r, enviar=bloqueada)
            with self.assertRaises(Falhou):
                await m.responder(ENTRADA)
            self.assertGreater(m.gasto_do_mes(), 0)
        finally:
            r.fechar()

    async def test_teto_argon_nao_bloqueia_flash_nem_muda_reflexao(self):
        chamadas = []
        async def enviar(url, corpo, chave):
            chamadas.append(url)
            return BOA
        m = Modelos([("vertex", FLASH)], {"vertex": "v"}, enviar=enviar, argon_teto_usd=0)
        self.assertEqual((await m.responder(ENTRADA, usar_argon=True)).modelo, FLASH)
        m.argon_teto_usd = 1
        self.assertEqual((await m.responder(ENTRADA, usar_argon=True)).modelo, ARGON)
        self.assertEqual((await m.responder(ENTRADA, usar_argon=True, gatilho="reflexao")).modelo, FLASH)
        self.assertEqual((await m.responder(ENTRADA)).modelo, FLASH)
        self.assertGreater(m.gasto_do_mes(ARGON), 0)
        self.assertGreater(m.gasto_do_mes(), m.gasto_do_mes(ARGON))

    async def test_cooldown_nao_repete_404_e_recupera_depois(self):
        chamadas = []
        async def enviar(url, corpo, chave):
            chamadas.append(url)
            raise Falhou(404, "modelo indisponível")
        m = Modelos([("vertex", ARGON)], {"vertex": "v"}, enviar=enviar)
        for _ in range(2):
            with self.assertRaises(Falhou):
                await m.responder(ENTRADA)
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(m.gasto_do_mes(), 0)
        m._de_molho[("vertex", ARGON)] = 0
        with self.assertRaises(Falhou):
            await m.responder(ENTRADA)
        self.assertEqual(len(chamadas), 2)

    async def test_cancelamento_preserva_reserva_apos_reabrir_banco(self):
        async def enviar(*args):
            raise asyncio.CancelledError()
        with tempfile.TemporaryDirectory() as t:
            arquivo = Path(t) / "banco.sqlite3"
            r = Registro(arquivo)
            m = Modelos([("vertex", ARGON)], {"vertex": "v"}, r, enviar=enviar)
            with self.assertRaises(asyncio.CancelledError):
                await m.responder(ENTRADA)
            self.assertEqual(m._reservado, 0)
            gasto = m.gasto_do_mes()
            self.assertGreater(gasto, 0)
            row = r._db.execute("SELECT custo_estimado_usd, reserva_sem_uso_usd FROM chamadas_api").fetchone()
            self.assertIsNone(row[0])
            self.assertEqual(row[1], gasto)
            r.fechar()
            r = Registro(arquivo)
            try:
                novo = Modelos([("vertex", ARGON)], {"vertex": "v"}, r, enviar=enviar, teto_usd=gasto)
                self.assertEqual(novo.gasto_do_mes(), gasto)
                with self.assertRaises(Falhou) as erro:
                    await novo.responder(ENTRADA)
                self.assertEqual(erro.exception.codigo, "teto")
            finally:
                r.fechar()

    async def test_subteto_argon_reserva_concorrente(self):
        entrou, terminar = asyncio.Event(), asyncio.Event()
        async def enviar(url, *args):
            if ARGON in url:
                entrou.set()
                await terminar.wait()
            return BOA
        m = Modelos([("vertex", FLASH)], {"vertex": "v"}, enviar=enviar, argon_teto_usd=.06)
        tarefa = asyncio.create_task(m.responder(ENTRADA, usar_argon=True))
        await entrou.wait()
        self.assertEqual((await m.responder(ENTRADA, usar_argon=True)).modelo, FLASH)
        terminar.set()
        self.assertEqual((await tarefa).modelo, ARGON)
        self.assertAlmostEqual(m._reservado_argon, 0)

    async def test_resposta_sem_uso_e_falha_com_uso_sao_diferentes(self):
        r = Registro(":memory:")
        try:
            async def enviar(*args):
                return {"candidates": BOA["candidates"]}
            m = Modelos([("vertex", ARGON)], {"vertex": "v"}, r, enviar=enviar)
            self.assertIsNone((await m.responder(ENTRADA)).custo_estimado_usd)
            self.assertGreater(m.gasto_do_mes(), 0)
            async def vazio(*args):
                return {"candidates": [], "usageMetadata": BOA["usageMetadata"]}
            m._enviar = vazio
            with self.assertRaises(Falhou):
                await m.responder(ENTRADA)
            row = r._db.execute("SELECT custo_estimado_usd, reserva_sem_uso_usd FROM chamadas_api ORDER BY rowid DESC LIMIT 1").fetchone()
            self.assertGreater(row[0], 0)
            self.assertEqual(row[1], 0)
        finally:
            r.fechar()

    async def test_compacto_no_argon_e_original_no_fallback(self):
        caso = comparar_argon.preparar()[0]
        entrada = caso["input"]
        chamadas = []
        async def enviar(url, corpo, chave):
            chamadas.append(corpo)
            if ARGON in url:
                raise Falhou(503, "sobrecarga")
            return BOA
        m = Modelos([("vertex", ARGON), ("vertex", FLASH)], {"vertex": "v"},
                    enviar=enviar, argon_perfil="compacto-v1")
        r = await m.responder(entrada, persona="closure")
        self.assertEqual(r.modelo, FLASH)
        esperado = perfil_argon.aplicar(entrada, "closure")
        self.assertEqual(chamadas[0]["system_instruction"]["parts"][0]["text"], esperado[0]["content"])
        self.assertEqual(chamadas[1]["system_instruction"]["parts"][0]["text"], entrada[0]["content"])
        self.assertEqual(chamadas[1]["contents"][-1]["parts"][0]["text"], entrada[-1]["content"])

    async def test_card_incompativel_vai_ao_flash_sem_chamar_argon(self):
        chamadas = []
        async def enviar(url, *args):
            chamadas.append(url)
            return BOA
        m = Modelos([("vertex", ARGON), ("vertex", FLASH)], {"vertex": "v"},
                    enviar=enviar, argon_perfil="compacto-v1")
        self.assertEqual((await m.responder(ENTRADA, persona="closure")).modelo, FLASH)
        self.assertEqual(len(chamadas), 1)
        self.assertIn(FLASH, chamadas[0])


class Perfil(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = comparar_argon.preparar()

    def test_so_sistema_e_lembrete_mudam_sem_perder_estado_livro_historico(self):
        original = copy.deepcopy(self.casos)
        compactos = perfil_argon.preparar_proposta(self.casos)
        self.assertEqual(self.casos, original)
        for c in compactos:
            a, b = c["input"], c["input_argon"]
            self.assertEqual(a[1:-1], b[1:-1])
            card = json.loads((perfil_argon.RAIZ / f"dados/personagem/{c['persona']}/card.json").read_text())["data"]
            antes, depois = a[-1]["content"].rsplit("\n\n" + card["post_history_instructions"], 1)
            self.assertEqual(b[-1]["content"], antes + "\n\n" + perfil_argon.LEMBRETE + depois)
            self.assertLess(len(b[0]["content"]), len(a[0]["content"]))
            self.assertEqual(c["input"], next(o["input"] for o in original if o["id"] == c["id"]))

    def test_sistema_desconhecido_bloqueia_compactacao(self):
        entrada = copy.deepcopy(self.casos[0]["input"])
        entrada[0]["content"] += " mudança"
        with self.assertRaises(ValueError):
            perfil_argon.aplicar(entrada, "closure")
