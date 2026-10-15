"""Proposta local: integridade dos dados e isolamento dos experimentos anteriores."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

from closure_bot.config import carregar
from closure_bot.modelo import Modelos
from closure_bot import perfil_compacto_v2 as v2

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ferramentas"))
import perfil_compacto_v3 as v3
import preparar_compacto_v3 as plano
import comparar_argon


class Proposta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bases, cls.casos = plano.preparar()

    def test_preserva_contexto_e_nao_muda_entrada_ou_v2(self):
        for base in self.bases:
            with self.subTest(caso=base["id"]):
                entrada = copy.deepcopy(base["input"])
                antes = v2.aplicar(entrada, base["persona"])
                novo = v3.aplicar(entrada, base["persona"])
                self.assertEqual(entrada, base["input"])
                self.assertEqual(v2.aplicar(entrada, base["persona"]), antes)
                self.assertEqual(novo[1:-1], entrada[1:-1])
                prefixo, sufixo = antes[-1]["content"].rsplit("\n\n" + v2.LEMBRETE, 1)
                self.assertEqual(novo[-1]["content"], prefixo + "\n\n" + v3.LEMBRETE + sufixo)

    def test_ineditos_repeticoes_e_variantes_com_contexto_igual(self):
        mensagens_anteriores = {c["mensagem"] for c in comparar_argon.preparar()}
        self.assertEqual(len(self.bases), 16)
        self.assertEqual(len(self.casos), 40)
        self.assertEqual(len({c["id"] for c in self.casos}), 40)
        self.assertFalse(mensagens_anteriores & {b["mensagem"] for b in self.bases})
        for base in self.bases:
            grupo = [c for c in self.casos if c["caso_base"] == base["id"]]
            self.assertEqual(len(grupo), 4 if base["categoria"] in ("identidade", "cuidado") else 2)
            por_perfil = {}
            for caso in grupo:
                self.assertEqual(caso["alvos"], ["gemini-4-argon"])
                self.assertEqual(caso["sha256"], plano.hash_entrada(caso["input"]))
                self.assertEqual(caso["input"][1:-1], base["input"][1:-1])
                anterior = por_perfil.setdefault(caso["perfil"], caso["input"])
                self.assertEqual(anterior, caso["input"])

    def test_v2_aprovada_reproduz_hashes_das_bases_congeladas(self):
        raiz = Path(__file__).resolve().parents[2]
        import perfil_compacto_v2 as ferramenta_v2
        congelados = json.loads((raiz / "pesquisa/validacao/2026-10-14-compacto-v2/casos.json").read_text())
        # A busca atual pode evoluir. A aprovação antiga cobre os pedidos salvos,
        # não uma nova consulta ao livro. Valide o perfil sobre aquelas mesmas bases.
        bases = []
        for caso in congelados:
            self.assertEqual(ferramenta_v2.hash_entrada(caso["input"]), caso["sha256"])
            if caso["variante"] == "flash-original":
                base = copy.deepcopy(caso)
                base["id"] = base["caso_base"]
                bases.append(base)
        atuais = ferramenta_v2.preparar(bases)
        self.assertEqual([(c["id"], c["sha256"]) for c in atuais],
                         [(c["id"], c["sha256"]) for c in congelados])

    def test_nao_libera_perfil_sem_validacao_no_bot(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                carregar(Path(t) / "ausente", {"ARGON_PERFIL": "compacto-v3"})
        with self.assertRaises(ValueError):
            Modelos([], {}, argon_perfil="compacto-v3")

    def test_card_incompativel_exige_revisao(self):
        raiz = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as t:
            destino = Path(t) / "personagem/closure/card.json"
            destino.parent.mkdir(parents=True)
            card = json.loads((raiz / "dados/personagem/closure/card.json").read_text())
            card["data"]["character_version"] = "outra"
            destino.write_text(json.dumps(card))
            with self.assertRaises(ValueError):
                v3.aplicar(self.bases[0]["input"], "closure", Path(t))

    def test_textos_exportados_correspondem_a_proposta(self):
        with tempfile.TemporaryDirectory() as t:
            pasta = v3.exportar(Path(t))
            for persona in v3.PERSONAS:
                self.assertEqual((pasta / f"{persona}.txt").read_text(),
                                 v3.PERSONAS[persona] + "\n\n" + v3.COMUM + "\n\n" + v3.LEMBRETE + "\n")
