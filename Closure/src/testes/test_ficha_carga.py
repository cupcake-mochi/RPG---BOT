"""Carga recalculada do catálogo/entradas; limites, lacunas e fórmula legada."""
import unittest
from pathlib import Path

from closure_bot.ficha_corretor import Referencias, Resultado
from closure_bot.ficha_carga import conferir_carga
from testes.test_ficha_magia import campos

RAIZ = Path(__file__).resolve().parents[2]


class Carga(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def ficha(self, **trocas):
        f = campos(formato__versao=4, nivel=2, atributo__forca__base=0, atributo__forca__corpo=0,
            origem="Descendente", origem__menor_1="", origem__menor_2="", carga__ajuste_limite=0,
            carga__total=0.3, carga__limite=5, em_uso__vestindo="Traje 1", em_uso__principal="Soco", em_uso__secundaria="—")
        for tipo, teto in (("equipavel", 8), ("item", 12)):
            for i in range(1, teto + 1):
                f.update(campos(**{f"{tipo}.{i}.{k}": "" for k in ("nome", "quantidade", "volume")}))
        f.update(campos(**trocas));return f

    def analisar(self, f):
        r = Resultado("aprovada");conferir_carga(f, self.ref, r);return r

    def test_traje_vestido_entra_na_carga(self):
        r = self.analisar(self.ficha())
        self.assertEqual((r.problemas, r.pendencias), ([], []))
        self.assertTrue(any("0.3 de 5 Volume pelo catálogo" in s for s in r.conferidos))

    def test_quantidade_da_arma_multiplica_volume_sem_arredondar(self):
        r = self.analisar(self.ficha(equipavel__1__nome="Kunai", equipavel__1__quantidade=3,
            equipavel__1__volume=0.6, carga__total=0.9))
        self.assertEqual((r.problemas, r.pendencias), ([], []))
        self.assertTrue(any("0.9 de 5" in s for s in r.conferidos))

    def test_quantidade_vazia_e_um_zero_continua_zero(self):
        for q, v, total in (("", 0.2, 0.5), (0, 0, 0.3)):
            r = self.analisar(self.ficha(equipavel__1__nome="Kunai", equipavel__1__quantidade=q,
                equipavel__1__volume=v, carga__total=total))
            self.assertEqual(r.problemas, [])

    def test_escudo_guardado_arma_em_duas_maos_conta_ambos(self):
        r = self.analisar(self.ficha(equipavel__1__nome="Espadão", equipavel__1__volume=2,
            equipavel__2__nome="Torre", equipavel__2__volume=2, carga__total=4.3,
            em_uso__principal="Espadão", em_uso__secundaria="Torre"))
        self.assertEqual((r.problemas, r.pendencias), ([], []))

    def test_alias_da_arma_nao_cria_falta_falsa_no_inventario(self):
        r = self.analisar(self.ficha(equipavel__1__nome="Katana (espada curva)", equipavel__1__volume=1,
            carga__total=1.3, em_uso__principal="Katana"))
        self.assertEqual(r.pendencias, [])

    def test_nome_de_item_tabelado_vence_peso_generico(self):
        r = self.analisar(self.ficha(item__1__nome="Corda", item__1__volume=0.5, carga__total=0.8))
        self.assertEqual((r.problemas, r.pendencias), ([], []))

    def test_apenas_peso_e_total_exatos_da_formula_antiga_sao_pendencia(self):
        r = self.analisar(self.ficha(item__1__nome="Corda", item__1__volume=0.1, carga__total=0.4))
        self.assertFalse(r.problemas)
        self.assertEqual({p.campo for p in r.pendencias}, {"item.1.volume", "carga.total"})
        r = self.analisar(self.ficha(item__1__nome="Corda", item__1__volume=999, carga__total=999.3))
        self.assertTrue({"item.1.volume", "carga.total"} <= {p.campo for p in r.problemas})

    def test_volume_livre_e_total_declarado_sem_multiplicar_duas_vezes(self):
        r = self.analisar(self.ficha(equipavel__7__nome="Peças próprias", equipavel__7__quantidade=3,
            equipavel__7__volume=2, item__1__nome="Lembrança", item__1__volume=0.1, carga__total=2.4))
        self.assertFalse(r.problemas)
        self.assertEqual(len(r.notas), 2)
        self.assertTrue(any("pelas entradas declaradas" in s for s in r.conferidos))

    def test_dado_ausente_e_item_sem_nome_nao_fecham_total(self):
        f = self.ficha();del f["equipavel.8.quantidade"]
        r = self.analisar(f);self.assertFalse(r.conferidos)
        self.assertTrue(any("faltam posições" in s for s in r.nao_conferido))
        r = self.analisar(self.ficha(item__1__volume=2))
        self.assertFalse(r.conferidos)
        self.assertTrue(any(p.campo == "item.1.nome" for p in r.pendencias))

    def test_negativo_nao_finito_e_texto_na_quantidade_nao_viram_zero(self):
        for q in (-1, float("nan"), float("inf"), "muitas", True):
            r = self.analisar(self.ficha(equipavel__1__nome="Kunai", equipavel__1__quantidade=q))
            self.assertTrue(r.problemas)
            self.assertFalse(r.conferidos)

    def test_equipamento_em_uso_precisa_constar_do_inventario(self):
        r = self.analisar(self.ficha(em_uso__principal="Besta"))
        self.assertTrue(any(p.campo == "em_uso.principal" for p in r.pendencias))

    def test_carga_no_limite_dobro_e_acima(self):
        for v, esperado in ((5, None), (10, "metade"), (10.1, "voltar a se deslocar")):
            r = self.analisar(self.ficha(em_uso__vestindo="", item__1__nome="Carga declarada", item__1__volume=v, carga__total=v))
            self.assertFalse(r.problemas)
            if esperado:
                self.assertTrue(any(esperado in p.esperado for p in r.pendencias))
            else:
                self.assertEqual(r.pendencias, [])

    def test_buff_do_limite_separado_do_peso(self):
        r = self.analisar(self.ficha(carga__ajuste_limite=-1, carga__limite=4))
        self.assertFalse(r.problemas)
        self.assertTrue(any(p.campo == "carga.ajuste_limite" for p in r.notas))

    def test_porte_incomum_nao_e_forca_nem_dobro_do_antigo(self):
        r = self.analisar(self.ficha(origem="Restrição Celestial · Sem Energia", origem__menor_1="Porte Incomum", carga__limite=6))
        self.assertEqual((r.problemas, r.pendencias), ([], []))
        r = self.analisar(self.ficha(origem="Restrição Celestial · Sem Energia", origem__menor_1="Porte Incomum",
            carga__ajuste_limite=1, carga__limite=6))
        self.assertFalse(r.problemas)
        self.assertTrue(any(p.campo == "carga.limite" for p in r.pendencias))

    def test_ferramenta_integrada_nao_e_cobrada_sem_identificar_conjunto(self):
        r = self.analisar(self.ficha(origem="Corpo Amaldiçoado", origem__menor_1="Ferramentas Integradas",
            item__1__nome="Ferramentas de ofício", item__1__volume=0))
        self.assertFalse(r.problemas)
        self.assertFalse(r.conferidos)
        self.assertTrue(any("qual conjunto" in s for s in r.nao_conferido))

    def entidade(self, **trocas):
        f = self.ficha(invocacao__1__nome="Entidade", invocacao__1__atributo__forca__base=0,
            invocacao__1__atributo__forca__buff=0, invocacao__1__equipamento__1="Espadão",
            invocacao__1__equipamento__2="Torre", invocacao__1__equipamento__3="Traje 1",
            invocacao__1__carga__total=4.3, invocacao__1__carga__limite=5)
        for i in range(1, 7):
            f.update(campos(**{f"invocacao.1.carga.item.{i}.nome": "", f"invocacao.1.carga.item.{i}.volume": ""}))
        f.update(campos(**trocas));return f

    def test_entidade_soma_tres_pecas_sem_apagar_escudo_inativo(self):
        r = self.analisar(self.entidade())
        self.assertFalse(r.problemas)
        self.assertTrue(any("Invocação 1: 4.3 de 5" in s for s in r.conferidos))

    def test_guardado_entidade_e_declarado_nao_autoriza_armazenamento(self):
        r = self.analisar(self.entidade(invocacao__1__carga__item__1__nome="Objeto", invocacao__1__carga__item__1__volume=1,
            invocacao__1__carga__total=5.3))
        self.assertFalse(r.problemas)
        self.assertTrue(any(p.campo == "invocacao.1.carga.total" for p in r.pendencias))
        self.assertTrue(any("campo preenchido não prova" in s for s in r.nao_conferido))

    def test_guardado_ausente_ou_equipamento_proprio_nao_certifica_total_entidade(self):
        f = self.entidade();del f["invocacao.1.carga.item.6.volume"]
        self.assertFalse(any("Invocação 1:" in s for s in self.analisar(f).conferidos))
        r = self.analisar(self.entidade(invocacao__1__equipamento__1="Arma própria"))
        self.assertFalse(any("Invocação 1:" in s for s in r.conferidos))

    def test_formato_antigo_continua_parcial(self):
        r = self.analisar(self.ficha(formato__versao=2, carga__total=999))
        self.assertEqual((r.problemas, r.conferidos), ([], []))

    def test_total_substitui_alerta_do_subtotal_so_com_entradas_completas(self):
        from closure_bot.ficha_equipamento import conferir_uso
        f = self.entidade(invocacao__1__equipamento__3="Traje 3", invocacao__1__carga__total=6)
        for incompleta in (False, True):
            g = f.copy()
            if incompleta:
                del g["invocacao.1.carga.item.6.volume"]
            r = Resultado("aprovada")
            conferir_uso(g, self.ref.equipamento, r, base="invocacao.1", atributos={"forca": 0})
            conferir_carga(g, self.ref, r)
            self.assertEqual([p.campo for p in r.pendencias if p.regra == "carga"],
                             ["invocacao.1.equipamento" if incompleta else "invocacao.1.carga.total"])


if __name__ == "__main__":
    unittest.main()
