"""Teto pelo preço cheio, gasto de fora do bot, 400 sem molho e prazo total da mensagem (revisão de 14/10/2026)."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from closure_bot import modelo as M
from closure_bot.config import carregar
from closure_bot.modelo import ARGON, FLASH, Falhou, Modelos
from closure_bot.registro import Registro

ENTRADA = [{"role": "user", "content": "sistema"}, {"role": "user", "content": "oi"}]
BOA = {"candidates": [{"content": {"parts": [{"text": "ok"}]}, "finishReason": "STOP"}],
       "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 2}}


class Gasto(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.r = Registro(":memory:")

    def tearDown(self):
        self.r.fechar()

    def test_preco_cheio_dobra_o_flash_e_o_promocional_fica_como_antes(self):
        self.r.registrar_chamada(modelo=f"vertex:{FLASH}", tokens_entrada=1_000_000, tokens_saida=0,
                                 custo_estimado_usd=0.75)
        cheio = Modelos([], {}, self.r, teto_preco="cheio")
        promo = Modelos([], {}, self.r)
        self.assertAlmostEqual(cheio.gasto_do_mes(), 1.5)
        self.assertAlmostEqual(promo.gasto_do_mes(), 0.75)
        self.assertAlmostEqual(cheio.gasto_do_mes(preco="promocional"), 0.75)

    def test_reserva_por_consumo_incerto_continua_contando_no_preco_cheio(self):
        self.r.registrar_chamada(modelo=f"vertex:{ARGON}", ok=False, erro="rede", reserva_sem_uso_usd=0.08)
        self.assertAlmostEqual(Modelos([], {}, self.r, teto_preco="cheio").gasto_do_mes(), 0.08)

    def test_gasto_de_fora_entra_no_teto_global_e_nao_no_do_argon(self):
        m = Modelos([], {}, self.r, teto_preco="cheio", gasto_externo_usd=4.0)
        self.assertAlmostEqual(m.gasto_do_mes(), 4.0)
        self.assertAlmostEqual(m.gasto_do_mes(ARGON), 0.0)
        self.assertAlmostEqual(m.gasto_do_mes(externo=False), 0.0)

    async def test_gasto_de_fora_tira_o_pago_da_fila(self):
        chamadas = []

        async def enviar(url, corpo, chave):
            chamadas.append(url)
            return BOA
        m = Modelos([("vertex", FLASH), ("gemini", FLASH)], {"vertex": "v", "gemini": "g"}, self.r, enviar=enviar,
                    teto_usd=9, teto_preco="cheio", gasto_externo_usd=9)
        r = await m.responder(ENTRADA)
        self.assertEqual(r.provedor, "gemini")
        self.assertEqual(len(chamadas), 1)

    def test_valores_invalidos(self):
        with self.assertRaises(ValueError):
            Modelos([], {}, teto_preco="barato")
        with self.assertRaises(ValueError):
            Modelos([], {}, gasto_externo_usd=-1)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                carregar(Path(t) / "nao_existe", {"TETO_PRECO": "barato"})
            c = carregar(Path(t) / "nao_existe", {"GASTO_EXTERNO_USD": "3,5"})
            self.assertEqual((c.teto_preco, c.gasto_externo_usd), ("cheio", 3.5))
            self.assertEqual(carregar(Path(t) / "nao_existe", {}).gasto_externo_usd, 0.0)


class Fila(unittest.IsolatedAsyncioTestCase):
    async def test_400_e_erro_do_pedido_e_nao_tira_o_modelo_dos_outros(self):
        chamadas = []

        async def enviar(url, corpo, chave):
            chamadas.append(url)
            if len(chamadas) == 1:
                raise Falhou(400, "contents required")
            return BOA
        m = Modelos([("vertex", FLASH)], {"vertex": "v"}, enviar=enviar)
        with self.assertRaises(Falhou):
            await m.responder(ENTRADA)
        self.assertEqual((await m.responder(ENTRADA)).modelo, FLASH)
        self.assertEqual(m._de_molho, {})

    async def test_prazo_total_corta_a_fila_e_a_reflexao_nao_tem_prazo(self):
        chamadas = []

        async def enviar(url, corpo, chave):
            chamadas.append(url)
            if "generativelanguage" in url:  # o gratuito engasga
                await asyncio.sleep(10)
            return BOA
        fila = [("gemini", FLASH), ("vertex", FLASH)]
        with patch.object(M, "PRAZO_TOTAL", 0.3), patch.object(M, "TENTATIVA_MINIMA", 0.2), \
                patch.dict(M.ESPERA_POR_PROVEDOR, {"gemini": 0.2, "vertex": 0.2}):
            m = Modelos(fila, {"gemini": "g", "vertex": "v"}, enviar=enviar)
            with self.assertRaises(Falhou) as erro:
                await m.responder(ENTRADA, gatilho="nome")
            self.assertEqual(len(chamadas), 1)  # sobrou menos que a tentativa mínima: o pago nem é chamado
            self.assertEqual(erro.exception.codigo, "rede")

    async def test_reflexao_espera_o_pago_lento_que_o_chat_largaria(self):
        async def lento(url, corpo, chave):
            await asyncio.sleep(0.4)
            return BOA
        with patch.object(M, "PRAZO_TOTAL", 0.3), patch.object(M, "TENTATIVA_MINIMA", 0.1), \
                patch.dict(M.ESPERA_POR_PROVEDOR, {"vertex": 1.0}):
            m = Modelos([("vertex", FLASH)], {"vertex": "v"}, enviar=lento)
            with self.assertRaises(Falhou):
                await m.responder(ENTRADA, gatilho="nome")
            m._de_molho.clear()
            self.assertEqual((await m.responder(ENTRADA, gatilho="reflexao", so_pagos=True)).modelo, FLASH)


if __name__ == "__main__":
    unittest.main()
