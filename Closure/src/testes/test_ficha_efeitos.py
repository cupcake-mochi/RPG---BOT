"""Contas e medidas do R51; resultados adulterados e entradas incompletas."""
import unittest

from closure_bot.ficha_corretor import Referencias, Resultado, conferir_feiticos
from closure_bot.ficha_leitor import Campo
from closure_bot.ficha_magia import conferir_montagem
from testes.test_ficha_magia import RAIZ, campos, carta


class Efeitos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")
        cls.magia = cls.ref.magia

    def ficha(self, classe=5, forma="Cura", pecas="", res="", dano="Cura 10d8 = 45", **extras):
        f = campos(nivel=17)
        f.update(carta("feitico.1", classe, forma, pecas, res, f"{3 * classe} PE", dano))
        f.update({"feitico.1." + k: Campo(v, "", "resultado") for k, v in extras.items()})
        return f

    def analisar(self, f, *, livres=frozenset(), entidade=False):
        r = Resultado("aprovada")
        conferir_montagem(f, self.magia, "feitico.1", 30, r.problemas, r.conferidos, r.nao_conferido,
                          entidade=entidade, basica=f["feitico.1.classe"].valor == 0,
                          familias=(set(livres), set(self.magia.familias)), pendencias=r.pendencias)
        return r

    def test_cura_comum_classe_cinco_teto_e_media(self):
        for d in ("Cura 10d8 = 45", "10d8"):
            r = self.analisar(self.ficha(dano=d))
            self.assertEqual(r.problemas, [])
            self.assertIn("Feitiço 1: cura 10d8", r.conferidos)
        for d in ("Cura 15d8", "Cura 10d8 = 46", "Cura 10d8 + 5d8"):
            self.assertIn("feitico.1.dano", [p.campo for p in self.analisar(self.ficha(dano=d)).problemas])

    def test_cura_da_entidade_tem_orcamento_proprio(self):
        r = self.analisar(self.ficha(dano="Cura 6d8"), entidade=True)
        self.assertEqual(r.problemas, [])
        r = self.analisar(self.ficha(dano="Cura 10d8"), entidade=True)
        self.assertIn("feitico.1.dano", [p.campo for p in r.problemas])

    def test_apoio_converte_saldo_sem_multiplicar_por_junto(self):
        f = self.ficha(forma="Apoio", pecas="Junto", dano="36 de vida temp.")
        r = self.analisar(f)
        self.assertEqual(r.problemas, [])  # 15 - 3 = 12; 12 × 3 = 36, repartidos
        self.assertIn("Feitiço 1: vida temporária 36", r.conferidos)
        self.assertTrue(any("distribuição" in s for s in r.nao_conferido))
        f["feitico.1.dano"] = Campo("72 de vida temp.", "", "resultado")
        self.assertIn("feitico.1.dano", [p.campo for p in self.analisar(f).problemas])

    def test_onda_nao_inventa_modo_a_partir_do_resultado(self):
        for d in ("Cura 7d8 = 31", "21 de vida temp."):
            r = self.analisar(self.ficha(forma="Onda", dano=d))
            self.assertEqual(r.problemas, [])
            self.assertFalse(any(": cura" in s or ": vida temporária" in s for s in r.conferidos))
            self.assertTrue(any("escolha estruturada" in s for s in r.nao_conferido))
        for d in ("Cura 8d8", "42 de vida temp.", "Cura 7d8 = 35"):
            self.assertIn("feitico.1.dano", [p.campo for p in self.analisar(self.ficha(forma="Onda", dano=d)).problemas])

    def test_onda_entidade_classe_um_saldo_zero(self):
        r = self.analisar(self.ficha(1, "Onda", "Impulso", "Gesto", "Sem cura"), entidade=True)
        self.assertEqual(r.problemas, [])
        r = self.analisar(self.ficha(1, "Onda", "Impulso", "Gesto", "Cura 1d8"), entidade=True)
        self.assertIn("feitico.1.dano", [p.campo for p in r.problemas])

    def test_apoio_zero_e_efeito_nao_concedem_saldo(self):
        for c, forma in ((0, "Apoio"), (0, "Efeito"), (5, "Efeito")):
            r = self.analisar(self.ficha(c, forma, dano="Sem dano"))
            self.assertEqual(r.problemas, [])
            for d in ("5d8", "9 de vida temp."):
                self.assertIn("feitico.1.dano", [p.campo for p in self.analisar(self.ficha(c, forma, dano=d)).problemas])

    def test_restricao_paga_peca_nao_forma(self):
        r = self.analisar(self.ficha(pecas="Junto", res="Sangra", dano="Cura 10d8"))
        self.assertEqual(r.problemas, [])

    def test_remate_e_adicionais_contam_no_teto(self):
        f = self.ficha(2, "Projétil", "Remate · Salto", "Sangra", "4d8 · +2d8")
        r = self.analisar(f)
        self.assertEqual(r.problemas, [])
        self.assertIn("Feitiço 1: dano-base 4d8", r.conferidos)
        f["feitico.1.dano"] = Campo("5d8 · +2d8", "", "resultado")
        self.assertIn("feitico.1.dano", [p.campo for p in self.analisar(f).problemas])

    def test_alma_reduz_dados_sem_validar_permissao(self):
        r = self.analisar(self.ficha(3, "Projétil", "Toca a Alma", dano="3d8"))
        self.assertEqual(r.problemas, [])  # (9 - 2) // 2 = 3
        self.assertTrue(any("permissão" in s for s in r.nao_conferido))
        r = self.analisar(self.ficha(3, "Projétil", "Toca a Alma", dano="99d8"))
        self.assertIn("feitico.1.dano", [p.campo for p in r.problemas])

    def test_controle_saldo_zero_duracao_e_cd_so_controle(self):
        r = self.analisar(self.ficha(3, "Explosão", "Condição: Atordoado · Terreno", dano="Sem dano"))
        self.assertEqual(r.problemas, [])
        self.assertIn("Feitiço 1: Controle com uma rodada adicional e +2 na CD apenas do Controle", r.conferidos)

    def test_descartar_dano_nao_compra_bonus_controle(self):
        r = self.analisar(self.ficha(3, "Projétil", "Condição: Lento", dano="Sem dano"))
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("saldo calculado 7" in s for s in r.nao_conferido))
        self.assertFalse(any("rodada adicional" in s for s in r.conferidos))

    def test_tipo_de_resolucao_com_e_sem_controle(self):
        for forma, pecas, esperado, dano in (("Projétil", "Condição: Lento", "Acerto + TR", "7d8"),
                ("Explosão", "", "TR, metade", "7d8"), ("Cura", "", "Automático", "Cura 6d8"),
                ("Projétil", "Certeiro", "TR para metade", "6d8")):
            r = self.analisar(self.ficha(3, forma, pecas, dano=dano, resolve=esperado))
            self.assertNotIn("feitico.1.resolve", [p.campo for p in r.problemas])
            r = self.analisar(self.ficha(3, forma, pecas, dano=dano, resolve="Automático 999"))
            self.assertIn("feitico.1.resolve", [p.campo for p in r.problemas])

    def test_nao_confirma_numero_exportado_da_resolucao_entidade(self):
        f = self.ficha(2, "Toque", "Precisão", dano="4d8", resolve="Ataque +999")
        r = self.analisar(f, entidade=True)
        self.assertFalse(any(": resolução" in s for s in r.conferidos))
        self.assertTrue(any("numéricos não certificados" in s for s in r.nao_conferido))

    def test_resolucao_alternativa_permitida_nao_e_reprovada_ou_certificada(self):
        for forma, escolha in (("Projétil", "TR, metade"), ("Explosão", "Acerto")):
            r = self.analisar(self.ficha(3, forma, dano="7d8", resolve=escolha))
            self.assertNotIn("feitico.1.resolve", [p.campo for p in r.problemas])
            self.assertFalse(any(": resolução" in s for s in r.conferidos))
            self.assertTrue(any("resolução alternativa" in s for s in r.nao_conferido))

    def test_maxima_respeita_familia_da_forma_e_inescapavel(self):
        from closure_bot.ficha_magia import conferir_maxima
        for forma, pecas, campo in (("Explosão", "", "forma"), ("Projétil", "Inescapável", "pecas")):
            f = campos(nivel=17, maxima__nome="Máxima", maxima__forma=forma,
                       maxima__pecas=pecas, maxima__pe=25, maxima__dano="24d8 = 108")
            r = Resultado("aprovada")
            conferir_maxima(f, self.magia, r, ({"Mira", "Alcance"}, set(self.magia.familias) - {"Área"}))
            self.assertIn("maxima." + campo, [p.campo for p in r.problemas])

    def test_area_e_amparo_fechadas_bloqueiam_formas_pessoais(self):
        for forma in ("Explosão", "Apoio", "Cura", "Onda"):
            f = self.ficha(forma=forma)
            for fam in self.magia.familias:
                f["tecnica.familia." + fam.lower().replace("á", "a")] = Campo(
                    "Livre" if fam in ("Mira", "Alcance") else "Fechada" if fam in ("Área", "Amparo", "Marca") else "Neutra", "", "entrada")
            r = Resultado("aprovada"); conferir_feiticos(f, self.ref, r)
            self.assertIn("feitico.1.forma", [p.campo for p in r.problemas])

    def test_pecas_exigem_forma_compativel(self):
        for forma, p in (("Onda", "Junto"), ("Cura", "Mais Um"), ("Explosão", "Rajada"),
                         ("Projétil", "Rajada · Certeiro"), ("Projétil", "Terreno")):
            self.assertIn("feitico.1.pecas", [p.campo for p in self.analisar(self.ficha(forma=forma, pecas=p)).problemas])
        r = self.analisar(self.ficha(forma="Efeito", pecas="Mais Um", dano="Sem dano"))
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("alvo individual" in s for s in r.nao_conferido))

    def test_duas_compras_de_junto_e_limite(self):
        r = self.analisar(self.ficha(forma="Apoio", pecas="Junto · Junto", dano="27 de vida temp."))
        self.assertEqual(r.problemas, [])
        r = self.analisar(self.ficha(forma="Apoio", pecas="Junto · Junto · Junto", dano="18 de vida temp."))
        self.assertIn("feitico.1.pecas", [p.campo for p in r.problemas])

    def test_requisito_invalido_nao_certifica_dano(self):
        for p in ("Corrói", "Toca a Alma"):
            r = self.analisar(self.ficha(1, "Projétil", p, dano="2d8"))
            self.assertIn("feitico.1.pecas", [p.campo for p in r.problemas])
            self.assertFalse(any("dano-base" in s for s in r.conferidos))

    def test_formula_antiga_de_alma_gera_pendencia_precisa(self):
        r = self.analisar(self.ficha(3, "Projétil", "Toca a Alma", dano="7d8 = 31"))
        self.assertEqual(r.problemas, [])
        self.assertEqual(r.pendencias[0].esperado, "3d8 de Alma")
        self.assertFalse(any("dano-base" in s for s in r.conferidos))
        for d in ("7d8 = 999", "8d8", "7d8 × 100"):
            self.assertIn("feitico.1.dano", [p.campo for p in self.analisar(self.ficha(3, "Projétil", "Toca a Alma", dano=d)).problemas])

    def test_alcance_e_area_independentes_e_escadas(self):
        casos = [("Explosão", 2, ["Longe", "Maior"], False, "Raio 4,5 m, a 36 m"),
                 ("Explosão", 6, [], True, "Raio 3 m, a 36 m"),
                 ("Explosão", 7, [], True, "Raio 4,5 m, a 36 m"),
                 ("Cone", 0, ["Maior"], False, "Cone de 4,5 m"),
                 ("Linha", 5, ["Muito Longe", "Maior"], False, "Linha de 60 m por 3 m"),
                 ("Linha", 6, ["Muito Maior"], False, "Linha de 60 m por 4,5 m"),
                 ("Projétil", 7, ["Muito Longe", "Longe"], False, "Visão a olho nu, um alvo"),
                 ("Apoio", 0, [], False, "Um aliado a 4,5 m"),
                 ("Onda", 6, [], True, "Raio 3 m, em você"),
                 ("Onda", 6, [], False, "Raio 4,5 m, em você")]
        for forma, classe, pecas, entidade, esperado in casos:
            with self.subTest(forma=forma, classe=classe, entidade=entidade):
                self.assertEqual(self.magia.medidas.alcance(forma, classe, pecas, entidade=entidade), esperado)

    def test_linha_formula_antiga_pendente_outros_valores_reprovam(self):
        for alcance, problema, pendencia in (("Linha de 60 m por 1,5 m", False, True),
                    ("Linha de 60 m por 3 m", False, False), ("Linha de 999 m por 1,5 m", True, False)):
            r = self.analisar(self.ficha(5, "Linha", "Muito Longe · Maior", dano="1d8", alcance=alcance))
            self.assertEqual(any(p.campo.endswith(".alcance") for p in r.problemas), problema)
            self.assertEqual(any(p.campo.endswith(".alcance") for p in r.pendencias), pendencia)
            self.assertEqual(any(": alcance" in s for s in r.conferidos), not problema and not pendencia)

    def test_campos_ausentes_nao_sao_zeros_certificados(self):
        r = self.analisar(self.ficha())
        self.assertTrue(any("alcance não exportado" in s for s in r.nao_conferido))
        self.assertTrue(any("resolução não exportada" in s for s in r.nao_conferido))


if __name__ == "__main__":
    unittest.main()
