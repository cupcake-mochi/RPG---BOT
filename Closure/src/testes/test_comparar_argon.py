"""A bateria paga não repete tentativa interrompida nem troca modelo silenciosamente."""
import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from closure_bot.modelo import Resposta

ARQUIVO = Path(__file__).resolve().parents[2] / "ferramentas/comparar_argon.py"
spec = importlib.util.spec_from_file_location("comparar_argon", ARQUIVO)
bateria = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bateria)

class Retomada(unittest.IsolatedAsyncioTestCase):
    async def test_interrupcao_conta_como_tentativa_e_nao_repete(self):
        chamadas = []
        interromper = True
        class Falso:
            def __init__(self, *args, **kwargs):
                self.fila = []
            async def responder(self, entrada, **kwargs):
                alvo = self.fila[0][1]
                chamadas.append((alvo, entrada))
                if interromper:
                    raise asyncio.CancelledError()
                return Resposta("Oi", "vertex", alvo, 10, 2, 10, False, 2, 0, 0, "STOP", .00002)
        casos = [{"id": "a", "persona": "closure", "sha256": "mesmo", "input": [{"role": "user", "content": "sistema"}, {"role": "user", "content": "oi"}]}]
        with tempfile.TemporaryDirectory() as t:
            args = SimpleNamespace(pasta=Path(t), limite_chamadas=2, teto_usd=.5, continuar_apos_interrupcao=False)
            config = SimpleNamespace(chaves={"vertex": "fake"}, banco=":memory:", chave_do_banco=None, teto_mensal_usd=9, vertex_projeto="", argon_max_saida=4096)
            with patch.object(bateria, "carregar", return_value=config), patch.object(bateria, "Modelos", Falso):
                with self.assertRaises(asyncio.CancelledError):
                    await bateria.executar(args, casos)
                self.assertEqual(json.loads((Path(t)/"respostas.json").read_text())[0]["estado"], "interrompida")
                self.assertEqual(await bateria.executar(args, casos), 1)
                args.continuar_apos_interrupcao = True
                interromper = False
                self.assertEqual(await bateria.executar(args, casos), 0)
                self.assertEqual(await bateria.executar(args, casos), 0)
            self.assertEqual([c[0] for c in chamadas], [bateria.ARGON, bateria.FLASH])
            self.assertEqual(chamadas[0][1], chamadas[1][1])
            dados=json.loads((Path(t)/"respostas.json").read_text())
            self.assertEqual(len(dados), 2)
            self.assertGreater(dados[0]["reserva_sem_uso_usd"], 0)
