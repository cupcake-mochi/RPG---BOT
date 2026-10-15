"""Valores calculados no Google em três cópias preenchidas; perturbações independentes."""
import json
import unittest
from pathlib import Path

from closure_bot.ficha_corretor import Referencias, Resultado, conferir, conferir_feiticos, conferir_invocacoes
from closure_bot.ficha_leitor import Campo, de_linhas

RAIZ = Path(__file__).resolve().parents[2]


class AnaliseV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def ficha(self, caso, **trocas):
        f = de_linhas(json.loads((RAIZ / f"src/testes/dados/ficha_v2_montagem_{caso}.json").read_text()))
        for k, v in trocas.items():
            k = k.replace("__", ".")
            c = f.get(k, Campo("", "", "entrada"))
            f[k] = Campo(v, c.celula, c.parte)
        return f

    def conferir(self, f):
        r = Resultado("aprovada")
        conferir_feiticos(f, self.ref, r)
        conferir_invocacoes(f, self.ref, r)
        return r

    def test_tres_montagens_calculadas_no_google(self):
        for i in (1, 2, 3, 4):
            with self.subTest(caso=i):
                self.assertEqual(self.conferir(self.ficha(i)).problemas, [])

    def test_kaori_anterior_com_magia_passou_pela_conferencia_inteira(self):
        r = conferir(self.ficha(4), self.ref)
        self.assertEqual((r.veredito, r.problemas, r.pendencias), ("aprovada", [], []))
        for campo, v in (("zero__1__dano", "999d8"), ("feitico__1__pe", "999 PE")):
            r = conferir(self.ficha(4, **{campo: v}), self.ref)
            self.assertEqual(r.veredito, "reprovada")

    def test_contrato_novo_preserva_antigo_e_origens_dos_campos_reais(self):
        def contrato(nome):
            linhas = (RAIZ / "dados/ficha" / nome).read_text().splitlines()
            return {k: (p, c) for k, p, c in (l.split("\t") for l in linhas if l and not l.startswith(("#", "chave\t")))}
        antigo, novo = contrato("analise-chaves-v1.tsv"), contrato("analise-chaves.tsv")
        self.assertEqual(len(novo), 4896)
        self.assertTrue(antigo.items() <= novo.items())
        for i in (1, 2, 3):
            for k, c in self.ficha(i).items():
                self.assertEqual(novo[k], (c.parte, c.celula), k)

    def test_zero_vazio_com_dados_visiveis_nao_vira_habilidade(self):
        r = self.conferir(self.ficha(1))
        self.assertIn("Classe 0 1: dano-base 4d8", r.conferidos)
        self.assertFalse(any("Classe 0 2:" in c for c in r.conferidos))
        self.assertFalse(any("Famílias" in c for c in self.conferir(self.ficha(2)).nao_conferido if "Classe 0" in c))

    def test_zero_hostil_nao_confia_no_resultado(self):
        r = self.conferir(self.ficha(1, zero__1__dano="5d8 = 22"))
        self.assertIn("zero.1.dano", [p.campo for p in r.problemas])

    def test_maxima_orcamento_e_dados_sao_independentes(self):
        for campo, v in (("maxima.pe", 24), ("maxima.dano", "8d8 = 36")):
            with self.subTest(campo=campo):
                f = self.ficha(1); f[campo] = Campo(v, "", "resultado")
                self.assertIn(campo, [p.campo for p in self.conferir(f).problemas])

    def test_texto_preenchido_sem_nome_nao_e_ignorado(self):
        for f, campo in ((self.ficha(1, maxima__nome="", maxima__texto="Efeito registrado"), "maxima.nome"),
                         (self.ficha(4, feitico__1__nome=""), "feitico.1.nome")):
            self.assertIn(campo, [p.campo for p in self.conferir(f).problemas])

    def test_familia_fechada_reprova_peca_sem_erro_na_planilha(self):
        f = self.ficha(1, tecnica__familia__alcance="Fechada", tecnica__familia__castigo="Livre")
        self.assertIn("feitico.1.pecas", [p.campo for p in self.conferir(f).problemas])

    def test_domada_usa_maestria_do_dono_e_constituicao_com_buff(self):
        r = self.conferir(self.ficha(2))
        for texto in ("Invocação 1: vida.max 34", "Invocação 1: acerto 5", "Invocação 1: cd 13"):
            self.assertIn(texto, r.conferidos)
        self.assertEqual({p.campo for p in r.notas}, {"invocacao.1.atributo.constituicao.buff", "invocacao.1.buff.vida"})

    def test_criada_para_no_fim_da_classe_e_talisma_nao_abate_retorno(self):
        r = self.conferir(self.ficha(3))
        for texto in ("Invocação 1: nivel 16", "Invocação 1: entrada 2", "Invocação 1: retorno 8"):
            self.assertIn(texto, r.conferidos)
        r = self.conferir(self.ficha(3, invocacao__1__retorno=6))
        self.assertIn("invocacao.1.retorno", [p.campo for p in r.problemas])

    def test_principal_tem_segunda_livre_com_desconto_exato(self):
        r = self.conferir(self.ficha(3))
        self.assertIn("Invocação 1 · especial 1: dano-base 3d8", r.conferidos)
        r = self.conferir(self.ficha(3, invocacao__1__esp__1__dano="2d8 Força · +1d8"))
        self.assertIn("invocacao.1.esp.1.dano", [p.campo for p in r.problemas])

    def test_segunda_livre_sem_trilha_e_familia_repetida_reprovam(self):
        for trocas in ({"trilha": "Parceria"}, {"invocacao__1__familia__2": "Área"}):
            r = self.conferir(self.ficha(3, **trocas))
            self.assertIn("invocacao.1.familias", [p.campo for p in r.problemas])

    def test_vida_defesa_ataque_e_cd_adulterados_sem_aviso(self):
        for campo in ("vida.max", "defesa", "acerto", "cd", "deslocamento"):
            f = self.ficha(2); k = "invocacao.1." + campo
            f[k] = Campo(999, "", "resultado")
            with self.subTest(campo=campo):
                self.assertIn(k, [p.campo for p in self.conferir(f).problemas])

    def test_entradas_individuais_nao_burlam_orcamento_antigo(self):
        f = self.ficha(2)
        for a in ("forca", "destreza", "constituicao", "inteligencia", "essencia"):
            f[f"invocacao.1.atributo.{a}.base"] = Campo(3, "", "entrada")
        self.assertIn("invocacao.1.pontos", [p.campo for p in self.conferir(f).problemas])

    def test_equipamento_proprio_nao_certifica_defesa(self):
        r = self.conferir(self.ficha(2, invocacao__1__equipamento__3="Armadura própria"))
        self.assertFalse(any(c.startswith("Invocação 1: defesa") for c in r.conferidos))
        self.assertTrue(any("Defesa depende de equipamento" in c for c in r.nao_conferido))

    def test_campo_ausente_nao_virou_ajuste_zero(self):
        f = self.ficha(2); del f["invocacao.1.atributo.constituicao.buff"]
        r = self.conferir(f)
        self.assertFalse(any(c.startswith("Invocação 1: vida.max") for c in r.conferidos))
        self.assertTrue(any("ANALISE 2" in c for c in r.nao_conferido))

    def test_buff_invalido_nao_e_ignorado(self):
        r = self.conferir(self.ficha(2, invocacao__1__buff__vida="muito"))
        self.assertIn("invocacao.1.buff.vida", [p.campo for p in r.problemas])
        self.assertFalse(any(c.startswith("Invocação 1: vida.max") for c in r.conferidos))

    def test_talento_respeita_ce_do_marco_e_nivel_da_entidade(self):
        for caso, trocas, campo in ((2, {"invocacao__1__talento__2": "Leitura"}, "invocacao.1.talento.2"),
                                    (3, {"invocacao__1__talento__1": "Eco"}, "invocacao.1.talento.1")):
            self.assertIn(campo, [p.campo for p in self.conferir(self.ficha(caso, **trocas)).problemas])
