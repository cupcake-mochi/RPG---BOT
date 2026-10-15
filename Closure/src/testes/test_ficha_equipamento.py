"""Equipamento do R51: requisitos, penalidades e resultados hostis, sem rede."""
import json
import unittest
from pathlib import Path

from closure_bot.ficha_corretor import Referencias, Resultado, conferir_contas, conferir_invocacoes
from closure_bot.ficha_equipamento import conferir_uso
from closure_bot.ficha_leitor import Campo, de_linhas
from closure_bot.ficha_entidade import conferir_numeros
from testes.test_ficha_magia import campos

RAIZ = Path(__file__).resolve().parents[2]


def copia(n=3, **trocas):
    f = de_linhas(json.loads((RAIZ / f"src/testes/dados/ficha_v2_montagem_{n}.json").read_text()))
    f.update(campos(**trocas))
    return f


class Equipamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def pessoal(self, forca=0, principal="Soco", secundaria="—", vestindo="Traje 1", grau="Grau 4", **extras):
        return campos(atributo__forca__base=forca, atributo__forca__corpo=0,
                      em_uso__principal=principal, em_uso__secundaria=secundaria,
                      em_uso__vestindo=vestindo, grau=grau, **extras)

    def uso(self, f, **kw):
        r = Resultado("aprovada")
        conferir_uso(f, self.ref.equipamento, r, **kw)
        return r

    def numeros(self, f, nivel=16):
        r = Resultado("aprovada")
        conferir_numeros(f, self.ref.magia, "invocacao.1", nivel, r,
                        (self.ref.uniformes, self.ref.escudos, self.ref.duas_maos), self.ref.equipamento)
        return r

    def test_catalogo_e_alias_saem_do_livro(self):
        p = self.ref.equipamento.pecas
        self.assertEqual(p["Katana"], p["Katana (espada curva)"])
        self.assertEqual((p["Espadão"].forca, p["Espadão"].maos), (3, 2))
        self.assertEqual(str(p["Traje 1"].volume), "0.3")
        self.assertTrue(p["Pistola"].fogo)

    def test_forca_insuficiente_nao_reprova_ou_apaga_protecao(self):
        r = self.uso(self.pessoal(vestindo="Revestimento 2", grau="Grau 3"))
        self.assertEqual(r.problemas, [])
        self.assertEqual(len(r.pendencias), 1)
        self.assertIn("Força 4", r.pendencias[0].esperado)

    def test_requisito_arma_independe_do_aviso_da_ficha(self):
        r = self.uso(self.pessoal(principal="Espadão", aviso__forca_p="Cumprido"))
        self.assertEqual(r.problemas, [])
        self.assertEqual(r.pendencias[0].campo, "em_uso.principal")

    def test_escudo_inativo_ainda_pesa_sem_impor_forca_de_uso(self):
        r = self.uso(self.pessoal(forca=3, principal="Espadão", secundaria="Torre"))
        self.assertEqual(r.pendencias, [])

    def test_patente_revestimento_sem_aviso_calculado(self):
        for nome, grau, erro in (("Revestimento 2", "Grau 4", True), ("Revestimento 2", "Grau 3", False),
                                  ("Revestimento 3", "Grau 3", True), ("Revestimento 3", "Grau 2", False)):
            with self.subTest(nome=nome, grau=grau):
                r = self.uso(self.pessoal(forca=6, vestindo=nome, grau=grau))
                self.assertEqual(bool(r.problemas), erro)

    def test_fogo_tem_excecao_de_autorizacao_nao_reprovacao_automatica(self):
        r = self.uso(self.pessoal(principal="Pistola"))
        self.assertEqual(r.problemas, [])
        self.assertIn("autorização prévia", r.notas[0].esperado)
        self.assertEqual(self.uso(self.pessoal(principal="Pistola", grau="Grau 2")).notas, [])

    def test_carga_pessoal_nunca_e_certificada_pelo_resultado(self):
        r = self.uso(self.pessoal(carga="0 de 999"))
        self.assertTrue(any("quantidade dos equipáveis" in s for s in r.nao_conferido))
        self.assertFalse(any("Carga" in s for s in r.conferidos))

    def test_equipamento_custom_e_entrada_ausente_nao_viram_zero(self):
        f = self.pessoal(vestindo="Meu uniforme")
        self.assertTrue(any("não reconhecido" in s for s in self.uso(f).nao_conferido))
        del f["em_uso.principal"]
        self.assertTrue(any("faltam entradas" in s for s in self.uso(f).nao_conferido))

    def test_forca_nao_finita_ou_booleana_nao_confirma_requisitos(self):
        for v in (float("nan"), float("inf"), True, "", "muita"):
            f = self.pessoal(forca=v)
            self.assertTrue(any("Força de entrada" in s for s in self.uso(f).nao_conferido))

    def test_defesa_pessoal_nao_ignora_escudo_proprio(self):
        f = copia(4, em_uso__secundaria="Escudo próprio")
        certos = []
        _, pulou = conferir_contas(f, self.ref, certos=certos)
        self.assertFalse(any(s.startswith("Defesa ") for s in certos))
        self.assertTrue(any("ocupação das mãos" in s for s in pulou))

    def test_entidade_com_arma_de_uma_mao_tem_defesa_conferida(self):
        f = copia(invocacao__1__equipamento__1="Maça", invocacao__1__acerto=5)
        r = self.numeros(f)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any(": defesa 14" in s for s in r.conferidos))
        self.assertTrue(any("acerto armado 5" in s for s in r.conferidos))
        self.assertTrue(any("desvantagem" in p.esperado for p in r.pendencias))

    def test_entidade_arma_nao_usa_atributo_magico_por_engano(self):
        f = copia(invocacao__1__atributo_acerto="Destreza", invocacao__1__cd=14,
                  invocacao__1__equipamento__1="Maça", invocacao__1__acerto=6)
        r = self.numeros(f)
        self.assertEqual(r.problemas, [])  # fórmula antiga conhecida: pendência, sem certificar
        self.assertTrue(any(p.campo.endswith(".acerto") for p in r.pendencias))
        f["invocacao.1.acerto"] = Campo(999, "", "resultado")
        self.assertTrue(any(p.campo.endswith(".acerto") for p in self.numeros(f).problemas))

    def test_fineza_e_disparo_respeitam_atributos_da_arma(self):
        for arma, acerto in (("Katana", 5), ("Katana", 6), ("Pistola", 6), ("Kunai", 6)):
            r = self.numeros(copia(invocacao__1__equipamento__1=arma, invocacao__1__acerto=acerto))
            self.assertFalse(any(p.campo.endswith(".acerto") for p in r.problemas + r.pendencias))

    def test_arma_desconhecida_nao_certifica_defesa_ou_ataque(self):
        r = self.numeros(copia(invocacao__1__equipamento__1="Arma própria"))
        self.assertFalse(any(": defesa " in s or "acerto armado" in s for s in r.conferidos))

    def test_carga_entidade_e_subtotal_incluindo_escudo_inativo(self):
        f = copia(invocacao__1__equipamento__1="Metralhadora Pesada", invocacao__1__equipamento__2="Torre",
                  invocacao__1__equipamento__3="Revestimento 3")
        r = self.uso(f, base="invocacao.1", atributos={"forca": 0})
        self.assertTrue(any("10 Volume; limite básico 5" in s for s in r.conferidos))
        self.assertTrue(any(p.regra == "carga" and "metade" in p.esperado for p in r.pendencias))
        r = self.uso(f, base="invocacao.1", atributos={"forca": -1})
        self.assertTrue(any(p.regra == "carga" and "reduzir" in p.esperado for p in r.pendencias))
        self.assertTrue(any("carga adicional/total" in s for s in r.nao_conferido))

    def test_atributo_entidade_invalido_tem_erro_proprio(self):
        r = self.numeros(copia(invocacao__1__atributo__forca__base=99))
        self.assertIn("invocacao.1.atributo.forca.base", [p.campo for p in r.problemas])


if __name__ == "__main__":
    unittest.main()
