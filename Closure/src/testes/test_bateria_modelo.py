"""Interromper e retomar uma bateria não repete chamadas já respondidas."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ARQUIVO = Path(__file__).resolve().parents[2] / "ferramentas/bateria_modelo.py"
spec = importlib.util.spec_from_file_location("bateria_modelo", ARQUIVO)
bateria = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bateria)


class RetomarBateria(unittest.IsolatedAsyncioTestCase):
    async def test_resposta_salva_antes_de_interrupcao_e_nao_repetida(self):
        chamadas = []
        interromper = True

        class ModeloFalso:
            def __init__(self, *args):
                pass

            async def responder(self, entrada, **kwargs):
                numero = 1 if "mensagem 1" in entrada[-1]["content"] else 2
                chamadas.append(numero)
                if interromper and numero == 2:
                    raise RuntimeError("interrupção simulada")
                return SimpleNamespace(texto=f"resposta {numero}")

            def gasto_do_mes(self):
                return 0.0

        with tempfile.TemporaryDirectory() as nome:
            pasta = Path(nome)
            casos = [{"id": n, "de": "Pessoa", "mensagem": f"mensagem {n}",
                      "contexto": "contexto"} for n in (1, 2)]
            (pasta / "casos.json").write_text(json.dumps(casos))
            (pasta / "sistema.txt").write_text("sistema")
            (pasta / "lembrete.txt").write_text("lembrete")
            args = SimpleNamespace(bateria="casos.json", sistema="sistema.txt",
                                   lembrete="lembrete.txt", saida="respostas.json",
                                   juntas=1, fila="vertex:teste")
            config = SimpleNamespace(chaves={}, banco="não-usado")
            with patch.object(bateria, "PASTA", pasta), \
                    patch.object(bateria, "carregar", return_value=config), \
                    patch.object(bateria, "Registro", return_value=None), \
                    patch.object(bateria, "Modelos", ModeloFalso):
                with self.assertRaisesRegex(RuntimeError, "interrupção simulada"):
                    await bateria.rodar(args)
                self.assertEqual(json.loads((pasta / "respostas.json").read_text()),
                                 [{"id": 1, "resposta": "resposta 1"}])
                interromper = False
                self.assertEqual(await bateria.rodar(args), 0)
            self.assertEqual(chamadas, [1, 2, 2])
            self.assertEqual([r["id"] for r in json.loads((pasta / "respostas.json").read_text())], [1, 2])
            self.assertFalse((pasta / "respostas.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
