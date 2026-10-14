"""Triagem experimental: comparação justa, integridade do contexto e controle de gasto."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from closure_bot.config import carregar
from closure_bot.modelo import ARGON, FLASH, Falhou, Modelos, Resposta, montar_corpo
from closure_bot import perfil_argon as v1

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ferramentas"))
import comparar_argon as bateria
import perfil_compacto_v2 as v2


class Perfil(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = bateria.preparar()
        cls.casos = v2.preparar(cls.base)

    def test_mesmo_compacto_nos_dois_modelos_e_original_preservado(self):
        self.assertEqual(len(self.casos), 36)
        self.assertEqual(len({c["id"] for c in self.casos}), 36)
        for caso in self.base:
            variantes = {c["variante"]: c for c in self.casos if c["caso_base"] == caso["id"]}
            if not variantes:
                continue
            self.assertEqual(variantes["flash-original"]["input"], caso["input"])
            a, f = variantes["argon-compacto-v2"], variantes["flash-compacto-v2"]
            self.assertEqual(a["input"], f["input"])
            self.assertEqual(a["sha256"], f["sha256"])
            self.assertEqual(a["alvos"], [ARGON])
            self.assertEqual(f["alvos"], [FLASH])

    def test_contexto_dinamico_inteiro_e_v1_nao_muda(self):
        for c in self.base:
            entrada = copy.deepcopy(c["input"])
            anterior = v1.aplicar(entrada, c["persona"])
            novo = v2.aplicar(entrada, c["persona"])
            self.assertEqual(entrada, c["input"])
            self.assertEqual(v1.aplicar(entrada, c["persona"]), anterior)
            self.assertEqual(novo[1:-1], entrada[1:-1])
            a, b = anterior[-1]["content"].rsplit("\n\n" + v1.LEMBRETE, 1)
            self.assertEqual(novo[-1]["content"], a + "\n\n" + v2.LEMBRETE + b)

    def test_v2_exige_configuracao_explicita_e_base_conhecida(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(carregar(Path(t) / "ausente", {}).argon_perfil, "original")
            c = carregar(Path(t) / "ausente", {"ARGON_PERFIL": "compacto-v2"})
            self.assertEqual(c.argon_perfil, "compacto-v2")
            self.assertEqual(c.modelo_chat, "")
        with self.assertRaises(ValueError):
            v2.substituir("outra base", [("texto anterior", "novo")])


class Execucao(unittest.IsolatedAsyncioTestCase):
    async def test_runtime_v2_repete_prompt_aprovado_e_preserva_fallback_original(self):
        base = bateria.preparar()
        casos = v2.preparar(base)
        for original in base:
            alvo = next((c for c in casos if c["caso_base"] == original["id"]
                         and c["variante"] == "argon-compacto-v2"), None)
            if alvo is None:
                continue
            with self.subTest(caso=original["id"]):
                chamadas = []
                async def enviar(url, corpo, chave):
                    chamadas.append(copy.deepcopy(corpo))
                    if ARGON in url:
                        raise Falhou(503, "sobrecarga simulada")
                    return {"candidates": [{"content": {"parts": [{"text": "Oi."}]},
                                            "finishReason": "STOP"}],
                            "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 10}}
                entrada = copy.deepcopy(original["input"])
                m = Modelos([("vertex", ARGON), ("vertex", FLASH)], {"vertex": "fake"},
                            enviar=enviar, argon_perfil="compacto-v2")
                resposta = await m.responder(entrada, persona=original["persona"])
                self.assertEqual(resposta.modelo, FLASH)
                self.assertEqual(chamadas, [montar_corpo(alvo["input"], "low", modelo=ARGON),
                                           montar_corpo(original["input"], "low", modelo=FLASH)])
                self.assertEqual(entrada, original["input"])

    def config(self):
        return SimpleNamespace(chaves={"vertex": "fake"}, banco=":memory:", chave_do_banco=None,
                               teto_mensal_usd=9, vertex_projeto="", argon_max_saida=4096)

    async def test_variantes_flash_nao_colidem_e_retomada_nao_repete(self):
        chamadas = []
        class Falso:
            def __init__(self, *args, **kwargs):
                self.fila = []
            async def responder(self, entrada, **kwargs):
                alvo = self.fila[0][1]
                chamadas.append((alvo, copy.deepcopy(entrada)))
                return Resposta("Oi", "vertex", alvo, 10, 2, 10, False, 2, 0, 0, "STOP", .00002)
        casos = []
        for variante, alvo in (("flash-original", FLASH), ("flash-v2", FLASH), ("argon-v2", ARGON)):
            entrada = [{"role": "user", "content": variante}, {"role": "user", "content": "oi"}]
            casos.append({"id": variante, "persona": "closure", "sha256": v2.hash_entrada(entrada),
                          "input": entrada, "alvos": [alvo], "perfil": variante})
        with tempfile.TemporaryDirectory() as t:
            args = SimpleNamespace(pasta=Path(t), limite_chamadas=3, teto_usd=.4, continuar_apos_interrupcao=False)
            with patch.object(bateria, "carregar", return_value=self.config()), patch.object(bateria, "Modelos", Falso):
                self.assertEqual(await bateria.executar(args, casos), 0)
                self.assertEqual(await bateria.executar(args, casos), 0)
            self.assertEqual([alvo for alvo, _ in chamadas], [FLASH, FLASH, ARGON])
            r = json.loads((args.pasta / "respostas.json").read_text())
            self.assertEqual([c["perfil"] for c in r], [c["perfil"] for c in casos])

    async def test_consumo_incompleto_interrompe_com_reserva(self):
        class Falso:
            def __init__(self, *args, **kwargs):
                self.fila = []
            async def responder(self, *args, **kwargs):
                return Resposta("Oi", "vertex", FLASH, None, None, 10, False)
        entrada = [{"role": "user", "content": "sistema"}, {"role": "user", "content": "oi"}]
        caso = {"id": "a", "persona": "closure", "sha256": "hash", "input": entrada, "alvos": [FLASH]}
        with tempfile.TemporaryDirectory() as t:
            args = SimpleNamespace(pasta=Path(t), limite_chamadas=1, teto_usd=.4, continuar_apos_interrupcao=False)
            with patch.object(bateria, "carregar", return_value=self.config()), patch.object(bateria, "Modelos", Falso):
                self.assertEqual(await bateria.executar(args, [caso]), 1)
            r = json.loads((args.pasta / "respostas.json").read_text())[0]
            self.assertEqual(r["estado"], "invalida")
            self.assertGreater(r["reserva_sem_uso_usd"], 0)

    async def test_retomada_usa_reserva_maior_que_custo_parcial(self):
        class Falso:
            def __init__(self, *args, **kwargs):
                self.fila = []
            async def responder(self, *args, **kwargs):
                raise AssertionError("Reserva anterior já impede a próxima tentativa")
        entrada = [{"role": "user", "content": "sistema"}, {"role": "user", "content": "oi"}]
        casos = [{"id": i, "persona": "closure", "sha256": "hash", "input": entrada, "alvos": [FLASH]} for i in ("a", "b")]
        with tempfile.TemporaryDirectory() as t:
            args = SimpleNamespace(pasta=Path(t), limite_chamadas=2, teto_usd=.4, continuar_apos_interrupcao=True)
            bateria.gravar(args.pasta / "respostas.json", [{"id": "a", "alvo": FLASH, "sha256": "hash",
                           "estado": "invalida", "custo_estimado_usd": .00001, "reserva_sem_uso_usd": .399}])
            with patch.object(bateria, "carregar", return_value=self.config()), patch.object(bateria, "Modelos", Falso):
                self.assertEqual(await bateria.executar(args, casos), 1)
