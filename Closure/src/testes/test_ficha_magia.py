"""Exemplos numéricos do R51 e alterações hostis, sem modelo ou Google."""
import json
import tempfile
import unittest
from pathlib import Path

from closure_bot.ficha_corretor import (Referencias, Resultado, conferir_feiticos,
                                      conferir_invocacoes)
from closure_bot.ficha_leitor import Campo

RAIZ = Path(__file__).resolve().parents[2]


def campos(**entradas):
    return {k.replace("__", "."): Campo(v, "", "entrada") for k, v in entradas.items()}


def carta(base, classe, forma="Projétil", pecas="", res="", pe="3 PE", dano="2d8"):
    return {base + "." + k: Campo(v, "", "entrada" if k in ("nome", "classe", "forma", "pecas", "restricoes") else "resultado")
            for k, v in dict(nome="Aplicação", classe=classe, forma=forma, pecas=pecas, restricoes=res, pe=pe, dano=dano).items()}


class Montagens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def conferir(self, carta_, nivel=10, inv=None):
        f = campos(nivel=nivel)
        f.update(carta_)
        r = Resultado("aprovada")
        if inv:
            f.update(inv)
            conferir_invocacoes(f, self.ref, r)
        else:
            conferir_feiticos(f, self.ref, r)
        return r

    def test_fio_de_arrasto_do_livro(self):
        r = self.conferir(carta("feitico.1", 1, pecas="Empurrão"), nivel=2)
        self.assertEqual(r.problemas, [])
        self.assertIn("Feitiço 1: dano-base 2d8", r.conferidos)
        self.assertTrue(any("Selo" in n for n in r.nao_conferido))

    def test_livro_sem_referencia_falha_com_aviso_tratavel_pelo_bot(self):
        with tempfile.TemporaryDirectory() as d:
            pasta = Path(d) / "sistema"
            pasta.mkdir()
            (pasta / "catalogos.json").write_bytes((RAIZ / "dados/sistema/catalogos.json").read_bytes())
            linhas = (RAIZ / "dados/sistema/livro.jsonl").read_text().splitlines()
            (pasta / "livro.jsonl").write_text("\n".join(l for l in linhas if json.loads(l)["ancora"] != "fundamento--pontos"))
            with self.assertRaisesRegex(ValueError, "referência de magia ausente"):
                Referencias.do_livro(Path(d))

    def test_pe_e_dano_adulterados_sem_aviso_da_ficha(self):
        r = self.conferir(carta("feitico.1", 1, pecas="Empurrão", pe="2 PE", dano="999d8"), nivel=2)
        self.assertEqual({p.campo for p in r.problemas}, {"feitico.1.pe", "feitico.1.dano"})

    def test_liberacao_corte_de_ruptura(self):
        r = self.conferir(carta("liberacao.1", 3, forma="Linha", pe="14 PE", dano="10d8 = 45"))
        self.assertEqual(r.problemas, [])
        self.assertIn("Liberação 1: dano-base 10d8", r.conferidos)

    def test_liberacao_preco_acao_e_nivel(self):
        r = self.conferir(carta("liberacao.1", 3, pecas="Rápido", pe="9 PE", dano="9d8"), nivel=9)
        self.assertTrue({"liberacao.1.pe", "liberacao.1.classe", "liberacao.1.pecas"} <= {p.campo for p in r.problemas})

    def test_liberacoes_respeitam_quantidade_recebida(self):
        c = carta("liberacao.1", 3, pe="14 PE", dano="12d8")
        c.update(carta("liberacao.2", 3, pe="14 PE", dano="12d8"))
        r = self.conferir(c, nivel=10)
        self.assertTrue(any(p.campo == "liberacao.2.nome" for p in r.problemas))

    def test_toca_alma_nao_fura_requisito_classe(self):
        r = self.conferir(carta("feitico.1", 1, pecas="Toca a Alma"))
        self.assertTrue(any(p.campo == "feitico.1.pecas" for p in r.problemas))
        self.assertFalse(any("dano-base" in c for c in r.conferidos))

    def test_atrasar_nao_paga_a_forma_da_liberacao(self):
        r = self.conferir(carta("liberacao.1", 3, forma="Linha", res="Atrasar", pe="14 PE", dano="10d8"))
        self.assertEqual(r.problemas, [])

    def test_restricao_nao_reembolsa_forma(self):
        r = self.conferir(carta("feitico.1", 3, forma="Linha", pecas="Precisão", res="Sangra", pe="9 PE", dano="7d8"))
        self.assertEqual(r.problemas, [])
        self.assertIn("Feitiço 1: dano-base 7d8", r.conferidos)

    def test_salto_capado_pelo_total_do_livro(self):
        r = self.conferir(carta("feitico.1", 2, pecas="Salto", res="Gesto", pe="6 PE", dano="5d8 = 22 · +2d8"))
        self.assertEqual(r.problemas, [])
        ruim = self.conferir(carta("feitico.1", 2, pecas="Salto", res="Gesto", pe="6 PE", dano="5d8 · +9d8"))
        self.assertIn("feitico.1.dano", [p.campo for p in ruim.problemas])

    def test_familia_ausente_nao_certifica_numero_plausivel(self):
        r = self.conferir(carta("feitico.1", 3, pecas="Precisão", pe="9 PE", dano="8d8"))
        self.assertEqual(r.problemas, [])
        self.assertFalse(any("dano-base" in c for c in r.conferidos))
        ruim = self.conferir(carta("feitico.1", 3, pecas="Precisão", pe="9 PE", dano="999d8"))
        self.assertTrue(any(p.campo.endswith(".dano") for p in ruim.problemas))

    def test_formula_ou_media_escrita_errada(self):
        for dano in ("2d8 = 999", "2d8 × 100", "2d8 + 1000", "2d8 + 2d6"):
            with self.subTest(dano=dano):
                r = self.conferir(carta("feitico.1", 1, pecas="Empurrão", dano=dano), nivel=2)
                self.assertIn("feitico.1.dano", [p.campo for p in r.problemas])

    def test_limites_e_embutida_sem_confiar_no_aviso(self):
        r = self.conferir(carta("feitico.1", 1, forma="Toque", pecas="Precisão · Empurrão · Fura", res="Corpo a Corpo · Sangra"))
        self.assertTrue({"feitico.1.pecas", "feitico.1.restricoes"} <= {p.campo for p in r.problemas})

    def test_peca_propria_e_controle_nao_certificam_dano(self):
        for p in ("Efeito Próprio (Leve)", "Condição: Lento"):
            r = self.conferir(carta("feitico.1", 1, pecas=p, dano="Sem dano"))
            self.assertFalse(any("dano-base" in c for c in r.conferidos))
            self.assertTrue(r.nao_conferido)

    def test_frequencia_e_uso_incompativel(self):
        r = self.conferir(carta("feitico.1", 2, forma="Aura", pecas="Longe", res="Uma Vez · Dívida", pe="6 PE"))
        self.assertTrue({"feitico.1.restricoes", "feitico.1.pecas"} <= {p.campo for p in r.problemas})

    def test_cartas_vazias_com_valores_iniciais_nao_contam(self):
        r = self.conferir(campos(feitico__1__nome="", feitico__1__classe=1, feitico__1__forma="Projétil"))
        self.assertEqual((r.problemas, r.conferidos, r.nao_conferido), ([], [], []))

    def test_erro_de_formula_nao_vira_peca_ou_dano_certificado(self):
        r = self.conferir(campos(feitico__1__nome="", feitico__1__classe=1, feitico__1__forma="Projétil",
                                feitico__1__pecas="#NAME?", feitico__1__restricoes="#NAME?"))
        self.assertEqual(r.problemas, [])
        r = self.conferir(carta("feitico.1", 1, pecas="#NAME?", dano="3d8"))
        self.assertFalse(any("dano-base" in c for c in r.conferidos))
        self.assertTrue(any("fórmulas" in n for n in r.nao_conferido))

    def test_classe_invalida_nao_derruba_comando(self):
        for c in (-1, 8, 1.5, True, "um"):
            r = self.conferir(carta("feitico.1", c))
            self.assertEqual(r.problemas[0].campo, "feitico.1.classe")

    def invocacao(self, nivel=5, aquisicao="Espaço conhecido", fixo=0):
        tipo = "Maldição domada" if aquisicao == "Maldição domada" else "Shikigami de criação" if aquisicao == "Criação" else "Shikigami de técnica"
        return campos(invocacao__1__nome="Cão", invocacao__1__tipo=tipo, invocacao__1__aquisicao=aquisicao,
                      invocacao__1__nivel_fixo=fixo, invocacao__1__nivel=nivel, invocacao__1__classe=2 if nivel == 5 else 3,
                      invocacao__1__entrada=2 if nivel == 5 else 3, invocacao__1__retorno=4 if nivel == 5 else 6,
                      invocacao__1__pontos="1 · 2 · 2 · 1 · 3")

    def test_mordida_precisa_da_entidade(self):
        r = self.conferir(carta("invocacao.1.esp.1", 2, forma="Toque", pecas="Precisão", pe="6 PE", dano="4d8"),
                          nivel=5, inv=self.invocacao())
        self.assertEqual(r.problemas, [])
        self.assertIn("Invocação 1 · especial 1: dano-base 4d8", r.conferidos)
        self.assertTrue(any("vida, Defesa" in n for n in r.nao_conferido))

    def test_especial_tem_orcamento_proprio(self):
        r = self.conferir(carta("invocacao.1.esp.1", 2, pe="6 PE", dano="6d8"), nivel=5, inv=self.invocacao())
        self.assertIn("invocacao.1.esp.1.dano", [p.campo for p in r.problemas])
        self.assertEqual(next(p.esperado for p in r.problemas if p.campo.endswith(".dano")), "4d8")

    def test_basica_sem_pe_d6_e_leve(self):
        r = self.conferir(carta("invocacao.1.bas.1", 0, forma="Toque", pecas="Precisão", pe="Sem PE", dano="1d6 Cortante"),
                          nivel=5, inv=self.invocacao())
        self.assertEqual(r.problemas, [])
        self.assertIn("Invocação 1 · básica 1: dano-base 1d6", r.conferidos)

    def test_domada_nao_sobe_com_invocador(self):
        inv = self.invocacao(aquisicao="Maldição domada", fixo=5)
        r = self.conferir({}, nivel=20, inv=inv)
        self.assertEqual(r.problemas, [])
        inv["invocacao.1.nivel"] = Campo(20, "", "resultado")
        r = self.conferir({}, nivel=20, inv=inv)
        self.assertIn("invocacao.1.nivel", [p.campo for p in r.problemas])

    def test_criada_para_no_fim_da_classe(self):
        inv = self.invocacao(nivel=8, aquisicao="Criação", fixo=6)
        for campo, v in (("classe", 2), ("entrada", 2), ("retorno", 4)):
            inv["invocacao.1." + campo] = Campo(v, "", "resultado")
        r = self.conferir({}, nivel=11, inv=inv)
        self.assertEqual(r.problemas, [])

    def test_atributos_adulterados_nao_dependem_do_aviso(self):
        inv = self.invocacao()
        inv["invocacao.1.pontos"] = Campo("6 · 6 · 6 · 6 · 6", "", "entrada")
        r = self.conferir({}, nivel=5, inv=inv)
        self.assertIn("invocacao.1.pontos", [p.campo for p in r.problemas])



if __name__ == "__main__":
    unittest.main()
