"""Ganhos da Trilha e trunfos: conta independente e limites de aquisição."""
import unittest

from closure_bot.ficha_corretor import Referencias, Resultado, conferir_contas
from closure_bot.ficha_entidade_repertorio import conferir_repertorio_entidade
from closure_bot.ficha_efeitos import conferir_resolucao
from closure_bot.ficha_leitor import Campo
from testes.test_ficha_equipamento import RAIZ, copia
from testes.test_ficha_magia import campos, carta


class EntidadeRepertorio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def ficha(self, **trocas):
        f = copia(caminho="Evocador", trilha="Invocação Principal", nivel=18,
                  invocacao__1__tipo="Maldição domada", marco__refino=1)
        for i in range(1, 4):
            f.update(campos(**{f"invocacao.1.talento_extra.{i}": "", f"invocacao.1.ext.{i}.nome": ""}))
        for i in range(1, 9):
            f.update(campos(**{f"invocacao.1.esp.{i}.nome": ""}))
        f.update(campos(**trocas))
        return f

    def analisar(self, f, nivel=17, cartas=None, familias=None):
        r = Resultado("aprovada")
        conferir_repertorio_entidade(f, self.ref, "invocacao.1", nivel, cartas or [],
                                    familias or ({"Alcance", "Mira"}, set(self.ref.magia.familias)), r)
        return r

    def test_tabelas_da_domada_nao_sao_as_pessoais(self):
        regras = self.ref.entidades
        self.assertEqual(regras.extras, (8, 16, 24))
        self.assertEqual([regras.maximas[n] for n in (17, 21, 26)], [(19, 8, 25), (22, 12, 30), (26, 16, 35)])

    def test_formulas_vazias_nao_ativam_trunfos(self):
        r = self.analisar(self.ficha(invocacao__1__liberacao__1__pe="999 PE", invocacao__1__tm__pe="999 PE",
                                   invocacao__1__exp__acerto="999d8"))
        self.assertEqual(r.problemas, [])

    def test_extra_exige_trilha_e_caminho(self):
        for extras in ({"trilha": "Parceria"}, {"caminho": "Bastião"}, {"nivel": 1}):
            f = self.ficha(invocacao__1__talento_extra__1="Leitura", **extras)
            self.assertTrue(self.analisar(f).problemas)

    def test_extra_usa_nivel_da_entidade_nao_do_dono(self):
        f = self.ficha(invocacao__1__talento_extra__1="Leitura")
        self.assertTrue(self.analisar(f, nivel=5).problemas)
        self.assertEqual(self.analisar(f, nivel=8).problemas, [])

    def test_escolha_de_24_nao_cabe_no_nivel_16(self):
        f = self.ficha(invocacao__1__talento_extra__3="Instinto")
        self.assertTrue(self.analisar(f, nivel=16).problemas)

    def test_talento_e_carta_nao_ocupam_mesmo_extra(self):
        f = self.ficha(invocacao__1__talento_extra__1="Leitura")
        f.update(carta("invocacao.1.ext.1", 0, pe="Sem PE", dano="2d6"))
        self.assertTrue(any("não duas concessões" in p.esperado for p in self.analisar(f).problemas))

    def test_extra_mantem_ce1_nos_marcos_16_e_24(self):
        for i in (2, 3):
            f = self.ficha(**{f"invocacao.1.talento_extra.{i}": "Eco"})
            self.assertTrue(any("CE1" in p.esperado for p in self.analisar(f, nivel=30).problemas))

    def test_ce_propria_explicita_tambem_respeita_o_ganho(self):
        f = self.ficha(invocacao__1__talento_extra__2="Talento Próprio (CE 3)",
                       invocacao__1__talento__1="Talento Próprio (CE 2)")
        r = self.analisar(f)
        self.assertTrue({"invocacao.1.talento_extra.2", "invocacao.1.talento.1"} <= {p.campo for p in r.problemas})

    def test_nao_aceita_quarta_escolha_extra_inventada(self):
        f = self.ficha(invocacao__1__talento_extra__4="Leitura")
        self.assertTrue(any("três escolhas" in p.esperado for p in self.analisar(f, nivel=30).problemas))

    def test_trunfo_sem_nome_da_entidade_nao_e_ignorado_no_fluxo_completo(self):
        from closure_bot.ficha_corretor import conferir_invocacoes
        f = self.ficha(invocacao__1__nome="", invocacao__1__tm__nome="Máxima")
        for k in list(f):
            if k.startswith("invocacao.1.bas."):
                del f[k]
        r = Resultado("aprovada")
        conferir_invocacoes(f, self.ref, r)
        self.assertTrue(any(p.campo == "invocacao.1.nome" for p in r.problemas))

    def test_talento_pessoal_nao_entra_no_catalogo_da_entidade(self):
        f = self.ficha(invocacao__1__talento__4="Reserva Profunda")
        self.assertTrue(any(p.campo.endswith("talento.4") for p in self.analisar(f).problemas))

    def test_proprio_extra_continua_sem_aprovacao_automatica(self):
        r = self.analisar(self.ficha(invocacao__1__talento_extra__1="Meu Talento"))
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("aprovação do mestre" in s for s in r.nao_conferido))

    def test_posicao_ausente_nao_certifica_conjunto(self):
        f = self.ficha(); del f["invocacao.1.talento_extra.3"]
        r = self.analisar(f)
        self.assertTrue(any("faltam posições" in s for s in r.nao_conferido))
        self.assertFalse(any("escolhas extras separadas" in s for s in r.conferidos))

    def liberacao(self, **trocas):
        return self.ficha(invocacao__1__liberacao__1__nome="Trunfo", invocacao__1__liberacao__1__como="Efeito escrito",
            invocacao__1__liberacao__1__classe=3, invocacao__1__liberacao__1__pe="14 PE",
            invocacao__1__liberacao__1__pontos="6 pontos + 3d8", invocacao__1__liberacao__1__acao="Sua Ação Completa + a básica dela",
            **trocas)

    def test_liberacao_domada_tem_conta_propria(self):
        r = self.analisar(self.liberacao(), nivel=10)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("técnica própria" in s for s in r.nao_conferido))

    def test_outros_tipos_nao_tem_trunfos(self):
        for tipo in ("Shikigami", "Corpo amaldiçoado de criação", "Shikigami de criação"):
            f = self.liberacao(invocacao__1__tipo=tipo)
            self.assertIn("invocacao.1.tipo", [p.campo for p in self.analisar(f).problemas])

    def test_liberacao_respeita_quantidade_fixa(self):
        f = self.liberacao(invocacao__1__liberacao__2__nome="Segundo")
        self.assertTrue(any(p.campo.endswith(".liberacao") for p in self.analisar(f, nivel=10).problemas))

    def test_liberacao_adulterada_em_pe_pontos_e_acao(self):
        f = self.liberacao()
        for k in ("pe", "pontos", "acao"):
            f["invocacao.1.liberacao.1." + k] = Campo("999", "", "resultado")
        self.assertTrue({"invocacao.1.liberacao.1." + k for k in ("pe", "pontos", "acao")} <=
                        {p.campo for p in self.analisar(f).problemas})

    def test_maxima_usa_faixa_da_domada(self):
        for nivel, dados, pontos, pe in ((17, 19, 8, 25), (21, 22, 12, 30), (26, 26, 16, 35)):
            f = self.ficha(nivel=30, invocacao__1__tm__nome="Máxima", invocacao__1__tm__pe=f"{pe} PE",
                invocacao__1__tm__dados=f"{dados}d8 fixos · {pontos} pontos", invocacao__1__tm__acao="Sua Ação Completa + a básica dela")
            self.assertEqual(self.analisar(f, nivel=nivel).problemas, [])
            f["invocacao.1.tm.dados"] = Campo("32d8 fixos · 16 pontos", "", "resultado")
            self.assertTrue(any(p.campo.endswith("tm.dados") for p in self.analisar(f, nivel=nivel).problemas))

    def test_maxima_antes_17_ou_resultado_ausente_nao_certifica(self):
        f = self.ficha(invocacao__1__tm__nome="Máxima")
        self.assertTrue(any(p.campo.endswith("tm.nome") for p in self.analisar(f, nivel=16).problemas))
        del f["invocacao.1.tm.dados"]
        r = self.analisar(f)
        self.assertTrue(any("não exportado" in s for s in r.nao_conferido))

    def dominio(self, **trocas):
        f = self.ficha(invocacao__1__exp__nome="Domínio", invocacao__1__exp__degrau="Completa",
                       invocacao__1__exp__pe="24 PE", invocacao__1__exp__acerto="Acerto 5d8")
        f.update(campos(**trocas)); return f

    def test_dominio_exemplo_do_livro_sem_desconto(self):
        r = self.analisar(self.dominio(), nivel=14, familias=({"Alcance"}, set(self.ref.magia.familias)))
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("Domínio ocupam 3 de 4" in s for s in r.conferidos))

    def test_dominio_aplica_livre_da_entidade(self):
        r = self.analisar(self.dominio(invocacao__1__exp__acerto="Acerto 7d8"), nivel=14)
        self.assertEqual(r.problemas, [])

    def test_acerto_informativo_nao_e_forcado_a_dano(self):
        r = self.analisar(self.dominio(invocacao__1__exp__acerto="Transmite as regras do local"), nivel=14)
        self.assertFalse(any(p.campo.endswith(".acerto") for p in r.problemas))
        self.assertTrue(any("não convertido em dano" in s for s in r.nao_conferido))
        self.assertFalse(any("exp.acerto" in s for s in r.conferidos))

    def test_dominio_divide_vagas_com_especiais(self):
        r = self.analisar(self.dominio(), nivel=14, cartas=["invocacao.1.esp.1", "invocacao.1.esp.2"])
        self.assertTrue(any("especiais + 3" in p.esperado for p in r.problemas))

    def test_dominio_nao_usa_nivel_do_dono_como_nivel_da_domada(self):
        r = self.analisar(self.dominio(nivel=30), nivel=10)
        self.assertTrue(any("nível 14" in p.esperado for p in r.problemas))

    def test_dominio_exige_refino_do_dono(self):
        r = self.analisar(self.dominio(nivel=14, marco__refino=0), nivel=14)
        self.assertTrue(any("Refino 5" in p.esperado for p in r.problemas))

    def test_dominio_sem_barreiras_custa_sete_e_nao_aprova_pericia(self):
        f = self.dominio(nivel=30, marco__refino=7, invocacao__1__exp__degrau="Sem Barreiras",
                        invocacao__1__exp__pe="49 PE", invocacao__1__exp__acerto="Acerto 12d8")
        r = self.analisar(f, nivel=30)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("perícias fica para a próxima etapa" in s for s in r.nao_conferido))


class ResolucaoETalento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def resolucao(self, texto, escolha="Ataque", pecas=(), **trocas):
        f = copia(invocacao__1__esp__1__resolve=texto, invocacao__1__esp__1__resolucao_escolha=escolha, **trocas)
        r = Resultado("aprovada")
        conferir_resolucao(f, self.ref.magia, "invocacao.1.esp.1", "Projétil", pecas,
                          r.problemas, r.conferidos, r.nao_conferido, entidade=True, pendencias=r.pendencias)
        return r

    def test_bonus_usa_atributos_nao_resultados_da_entidade(self):
        r = self.resolucao("Ataque +5", invocacao__1__acerto=999, invocacao__1__cd=999)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("bônus da resolução" in s for s in r.conferidos))
        self.assertTrue(self.resolucao("Ataque +999").problemas)

    def test_precisao_soma_dois_ao_ataque_ou_cd(self):
        for texto, escolha in (("Ataque +7", "Ataque"), ("TR Espírito · CD 15", "TR Espírito")):
            r = self.resolucao(texto, escolha, ("Precisão",))
            self.assertEqual((r.problemas, r.pendencias), ([], []))

    def test_buff_fracionario_e_negativo_nao_e_perdido_na_resolucao(self):
        r = self.resolucao("Ataque +5,5", invocacao__1__buff__acerto=0.5)
        self.assertEqual(r.problemas, [])
        self.assertTrue(r.conferidos)
        r = self.resolucao("TR Espírito · CD -1", "TR Espírito", invocacao__1__buff__cd=-14)
        self.assertEqual(r.problemas, [])

    def test_cd_sem_precisao_da_formula_antiga_vira_pendencia(self):
        r = self.resolucao("TR Espírito · CD 13", "TR Espírito", ("Precisão",))
        self.assertEqual(r.problemas, [])
        self.assertTrue(r.pendencias)

    def test_controle_rejeita_bonus_impossivel_sem_certificar_saldo(self):
        self.assertTrue(self.resolucao("Ataque +5 · TR CD 999", pecas=("Condição: Lento",)).problemas)
        r = self.resolucao("Ataque +5 · TR CD 13", pecas=("Condição: Lento",))
        self.assertEqual(r.problemas, [])
        self.assertTrue(any("saldo zero" in s for s in r.nao_conferido))
        self.assertFalse(any("bônus da resolução" in s for s in r.conferidos))

    def test_ajuste_ausente_nao_virou_zero(self):
        f = copia(invocacao__1__esp__1__resolve="Ataque +999")
        del f["invocacao.1.buff.acerto"]
        r = Resultado("aprovada")
        conferir_resolucao(f, self.ref.magia, "invocacao.1.esp.1", "Projétil", (), r.problemas, r.conferidos, r.nao_conferido, entidade=True)
        self.assertFalse(r.conferidos)
        self.assertTrue(any("numéricos não certificados" in s for s in r.nao_conferido))

    def test_reserva_profunda_tem_acrescimo_por_classe_nao_por_quantidade(self):
        f = copia(4, nivel=17, energia_max=83, passiva__1="Reserva Profunda", passiva__2="Reserva Profunda")
        # Bastião 4 PE/nível = 68; Classe 5 dá +15 uma só vez.
        certos = []; pendencias = []
        problemas, _ = conferir_contas(f, self.ref, certos=certos, pendencias=pendencias)
        self.assertFalse(any(p.campo == "energia_max" for p in problemas + pendencias))
        self.assertIn("PE 83", certos)

    def test_reserva_buff_legado_nao_e_somada_duas_vezes(self):
        f = copia(4, nivel=17, energia_max=83, buff__energia=15, passiva__1="Reserva Profunda")
        certos = []; pendencias = []
        problemas, pulou = conferir_contas(f, self.ref, certos=certos, pendencias=pendencias)
        self.assertFalse(any(p.campo == "energia_max" for p in problemas))
        self.assertTrue(any(p.regra == "talento" for p in pendencias))
        self.assertNotIn("PE 83", certos)
        self.assertTrue(any("origem do ajuste" in s for s in pulou))


if __name__ == "__main__":
    unittest.main()
