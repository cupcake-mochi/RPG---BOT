"""Guardas da bateria paga: só respostas falsas, sem rede/chaves."""
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

ARQUIVO = Path(__file__).resolve().parents[2] / "ferramentas/bateria_mista.py"
spec = importlib.util.spec_from_file_location("bateria_mista_testada", ARQUIVO)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BateriaMista(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pasta = Path(self.tmp.name)
        self.privado = self.pasta / "privado"
        self.p = {"casos": b.casos()[:2], "chamadas_maximas": 2, "teto_estimado_cheio_usd": 1.20}

    async def rodar(self, modelo, montador=None, margem=.1):
        with patch.object(b, "montar", montador or (lambda c, rs: {"input": [{"content":"s"}, {"content":"m"}], "ativadas":[]})), patch.object(b, "reserva", return_value=margem):
            return await b.executar(self.p, modelo, pasta=self.pasta, privado=self.privado)

    def falso(self, falhar=False, cortar=False):
        from closure_bot.modelo import Resposta
        owner = self
        class Modelo:
            chamadas = 0
            async def responder(self, entrada, **kw):
                self.chamadas += 1
                # A intenção precisa estar durável antes de qualquer POST.
                rs = json.loads((owner.pasta / "respostas.json").read_text())
                owner.assertEqual(rs[-1]["estado"], "iniciada")
                if falhar:
                    raise b.Falhou("rede", "timeout simulado")
                return Resposta("resposta real anterior simulada", "vertex", b.FLASH, 10, 10, 3, cortar,
                                6, 4, 0, "MAX_TOKENS" if cortar else "STOP", .000045)
        return Modelo()

    async def test_salva_antes_de_enviar_e_retomada_nao_repete(self):
        m = self.falso()
        self.assertEqual(await self.rodar(m), 0)
        self.assertEqual(await self.rodar(m), 0)
        self.assertEqual(m.chamadas, 2)

    async def test_teto_considera_reserva_antes_da_chamada(self):
        self.p["teto_estimado_cheio_usd"] = .05
        m = self.falso()
        self.assertEqual(await self.rodar(m), 1)
        self.assertEqual(m.chamadas, 0)

    async def test_timeout_para_e_nao_repete_ao_retomar(self):
        m = self.falso(falhar=True)
        self.assertEqual(await self.rodar(m), 1)
        with self.assertRaisesRegex(ValueError, "tentativa falha"):
            await self.rodar(m)
        self.assertEqual(m.chamadas, 1)
        rs = json.loads((self.pasta / "respostas.json").read_text())
        self.assertEqual(rs[0]["reserva_usd"], .1)

    async def test_corte_para_sem_proxima_chamada(self):
        m = self.falso(cortar=True)
        self.assertEqual(await self.rodar(m), 1)
        self.assertEqual(m.chamadas, 1)

    async def test_mudanca_no_plano_recusa_retomada(self):
        m = self.falso()
        await self.rodar(m)
        self.p["teto_estimado_cheio_usd"] = 2
        with self.assertRaisesRegex(ValueError, "Plano mudou"):
            await self.rodar(m)
        self.assertEqual(m.chamadas, 2)

    def test_distribuicao_48_sem_ids_repetidos(self):
        from collections import Counter
        cs = b.casos()
        self.assertEqual(len(cs), len({c["id"] for c in cs}))
        self.assertEqual(Counter(c["categoria"] for c in cs), {"sistema":16, "conversa":12, "ambigua":12, "dialogo":8})

    def test_dialogo_usa_a_resposta_anterior_e_assuntos_avulsos_nao(self):
        cs = b.casos()
        primeiro = next(c for c in cs if c["id"] == "clo_origem1")
        segundo = next(c for c in cs if c["id"] == "clo_origem2")
        outras = [{**primeiro, "estado":"ok", "texto":"resposta recebida da API"},
                  {**primeiro, "pers":"kal", "estado":"ok", "texto":"de outra personagem"}]
        with patch.object(b.site_prompt, "montar", return_value={}) as montar:
            b.montar(segundo, outras)
            self.assertEqual(montar.call_args.kwargs["turnos"][1]["texto"], "resposta recebida da API")
            self.assertEqual(len(montar.call_args.kwargs["turnos"]), 2)
            b.montar(cs[0], outras)
            self.assertEqual(montar.call_args.kwargs["turnos"], [])

    async def test_retomada_so_envia_ineditas_e_preserva_timeout(self):
        sys.path.insert(0, str(ARQUIVO.parent))
        import retomar_bateria_mista as ret
        p = {"casos": b.casos()[:35], "teto_estimado_cheio_usd": 1.2}
        rs = [{**c, "estado":"falhou" if c["id"] == "clo_musica" else "ok", "reserva_usd":.01}
              for c in p["casos"][:33]]
        anteriores = json.dumps(rs, sort_keys=True)
        m = self.falso()
        with patch.object(ret, "b", b), patch.object(b, "PASTA", self.pasta), patch.object(b, "PRIVADO", self.privado), patch.object(b, "reserva", return_value=.1), patch.object(b, "montar", return_value={"input":[{"content":"s"},{"content":"m"}],"ativadas":[]}):
            self.assertEqual(await ret.continuar(p, rs, m), 0)
        self.assertEqual(m.chamadas, 2)
        self.assertEqual(json.dumps(rs[:33], sort_keys=True), anteriores)
        self.assertEqual([r["id"] for r in rs[33:]], ["kal_musica", "clo_defesa"])

    async def test_retomada_para_na_segunda_falha_sem_repetir(self):
        sys.path.insert(0, str(ARQUIVO.parent))
        import retomar_bateria_mista as ret
        p = {"casos": b.casos()[:35], "teto_estimado_cheio_usd": 1.2}
        rs = [{**c, "estado":"falhou" if c["id"] == "clo_musica" else "ok", "reserva_usd":.01}
              for c in p["casos"][:33]]
        m = self.falso(falhar=True)
        with patch.object(ret, "b", b), patch.object(b, "PASTA", self.pasta), patch.object(b, "PRIVADO", self.privado), patch.object(b, "reserva", return_value=.1), patch.object(b, "montar", return_value={"input":[{"content":"s"},{"content":"m"}],"ativadas":[]}):
            self.assertEqual(await ret.continuar(p, rs, m), 1)
        self.assertEqual(m.chamadas, 1)
        self.assertEqual(len(rs), 34)
