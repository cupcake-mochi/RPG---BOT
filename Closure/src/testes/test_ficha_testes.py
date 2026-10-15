"""Bônus e concessões de TR/perícias/Ofícios, sem depender dos avisos da ficha."""
import unittest
from pathlib import Path

from closure_bot.ficha_corretor import Referencias, Resultado
from closure_bot.ficha_leitor import Campo
from closure_bot.ficha_testes import conferir_testes, ATRIBUTOS, TRS
from testes.test_ficha_magia import campos

RAIZ = Path(__file__).resolve().parents[2]


def pessoal(ref, nivel=2):
    f = campos(formato__versao=4, nivel=nivel, marco__corpo=0, caminho="Bastião", origem="Descendente",
               origem__marcante="", origem__menor_1="", origem__menor_2="", trocou_por_arma="Não trocou")
    atrs = dict(zip(ATRIBUTOS, (3, 2, 2, 1, 1)))
    for a, v in atrs.items():
        f.update(campos(**{f"atributo.{a}.base": v, f"atributo.{a}.corpo": 0}))
    m = ref.magia.maestria[nivel]
    for tipo, catalogo, treinados in (("pericia", ref.testes.pericias, 9), ("oficio", ref.testes.oficios, 2)):
        for i, (slug, (n, a)) in enumerate(catalogo.items()):
            t = int(i < treinados)
            f.update(campos(**{f"{tipo}.{slug}.{k}": v for k, v in {
                "treino": t, "especialista": 0, "atributo": ATRIBUTOS[a], "ajuste": 0,
                "bonus": atrs[a] + m * t}.items()}))
    for i, (slug, (n, a)) in enumerate(TRS.items()):
        a = a or "forca";t = int(i < 2)
        f.update(campos(**{f"tr.{slug}.{k}": v for k, v in {
            "treino": t, "atributo": ATRIBUTOS[a], "ajuste": 0, "bonus": atrs[a] + m * t}.items()}))
    return f


class TestesDaFicha(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def analisar(self, f):
        r = Resultado("aprovada")
        ignorados = conferir_testes(f, self.ref, r)
        return r, ignorados

    def trocar(self, f, **trocas):
        f.update(campos(**trocas));return f

    def test_kaori_tr_e_pericias_basicos(self):
        r, avisos = self.analisar(pessoal(self.ref))
        self.assertEqual((r.problemas, r.pendencias), ([], []))
        self.assertIn("TR Físico: bônus +4", r.conferidos)
        self.assertIn("TR Vigor: bônus +3", r.conferidos)
        self.assertIn("TR Intelecto: bônus +1", r.conferidos)
        self.assertIn("aviso.testes_disponiveis", avisos)

    def test_bonus_adulterado_sem_aviso_reprova(self):
        f = self.trocar(pessoal(self.ref), tr__fisico__bonus=999, pericia__atletismo__bonus=999,
                        oficio__conducao__bonus=999)
        r, _ = self.analisar(f)
        self.assertTrue({"tr.fisico.bonus", "pericia.atletismo.bonus", "oficio.conducao.bonus"} <= {p.campo for p in r.problemas})

    def test_buff_numerico_soma_e_e_nota_para_mestre(self):
        f = self.trocar(pessoal(self.ref), tr__fisico__ajuste=-2, tr__fisico__bonus=2,
                        pericia__atletismo__ajuste=0.5, pericia__atletismo__bonus=4.5)
        r, _ = self.analisar(f)
        self.assertEqual(r.problemas, [])
        self.assertTrue({"tr.fisico.ajuste", "pericia.atletismo.ajuste"} <= {p.campo for p in r.notas})

    def test_ajuste_ausente_nao_virou_zero(self):
        f = pessoal(self.ref);del f["pericia.atletismo.ajuste"]
        r, _ = self.analisar(f)
        self.assertFalse(any(s.startswith("Atletismo:") for s in r.conferidos))
        self.assertTrue(any("faltam entradas" in s for s in r.nao_conferido))

    def test_ajuste_invalido_nao_e_ignorado(self):
        for v in ("muito", float("nan"), float("inf"), True):
            f = self.trocar(pessoal(self.ref), tr__vigor__ajuste=v)
            r, _ = self.analisar(f)
            self.assertIn("tr.vigor.ajuste", [p.campo for p in r.problemas])

    def test_fisico_usa_escolha_fixa_nao_maior_atributo(self):
        f = self.trocar(pessoal(self.ref), tr__fisico__atributo="Destreza", tr__fisico__bonus=3)
        r, _ = self.analisar(f);self.assertEqual(r.problemas, [])
        self.trocar(f, tr__fisico__bonus=4)
        self.assertIn("tr.fisico.bonus", [p.campo for p in self.analisar(f)[0].problemas])

    def test_tr_e_pericia_nao_aceitam_atributo_trocado(self):
        f = self.trocar(pessoal(self.ref), tr__fisico__atributo="Essência", tr__vigor__atributo="Força",
                        pericia__atletismo__atributo="Destreza")
        r, _ = self.analisar(f)
        self.assertTrue({"tr.fisico.atributo", "tr.vigor.atributo", "pericia.atletismo.atributo"} <= {p.campo for p in r.problemas})

    def test_oficio_admite_outro_atributo_com_tarefa_revisada(self):
        f = self.trocar(pessoal(self.ref), oficio__arrombamento__atributo="Inteligência", oficio__arrombamento__bonus=2)
        r, _ = self.analisar(f)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any(p.campo == "oficio.arrombamento.atributo" for p in r.notas))
        self.assertTrue(any("não autoriza tentativa" in s for s in r.nao_conferido))

    def test_especializacao_requer_treino_e_nivel10(self):
        f = self.trocar(pessoal(self.ref), pericia__provocar__especialista=1)
        r, _ = self.analisar(f)
        self.assertTrue(any("exige treino" in p.esperado for p in r.problemas))
        self.assertTrue(any("nível 10" in p.esperado for p in r.problemas))

    def test_especializacao_soma_metade_da_maestria_para_baixo(self):
        for nivel, bonus in ((10, 6), (18, 7), (26, 9)):
            f = self.trocar(pessoal(self.ref, nivel), marco__corpo=1,
                            pericia__atletismo__especialista=1, pericia__atletismo__bonus=bonus)
            r, _ = self.analisar(f)
            self.assertFalse(any(p.campo == "pericia.atletismo.bonus" for p in r.problemas))

    def test_tr_a_menos_pendente_a_mais_erro(self):
        f = self.trocar(pessoal(self.ref), tr__vigor__treino=0, tr__vigor__bonus=2)
        r, _ = self.analisar(f)
        self.assertTrue(any(p.campo == "tr" for p in r.pendencias))
        self.assertFalse(r.problemas)
        self.trocar(f, tr__vigor__treino=1, tr__vigor__bonus=3, tr__intelecto__treino=1, tr__intelecto__bonus=2)
        self.assertTrue(any(p.campo == "tr" for p in self.analisar(f)[0].problemas))

    def test_marcacao_invalida_nao_remove_aviso_antigo(self):
        f = self.trocar(pessoal(self.ref), tr__fisico__treino=2)
        r, avisos = self.analisar(f)
        self.assertTrue(r.problemas)
        self.assertNotIn("aviso.testes_disponiveis", avisos)

    def test_escolha_de_treino_ausente_amarelo_excesso_vermelho(self):
        f = self.trocar(pessoal(self.ref), pericia__atletismo__treino=0, pericia__atletismo__bonus=3)
        r, _ = self.analisar(f);self.assertFalse(r.problemas)
        self.assertTrue(any(p.campo == "treinos" for p in r.pendencias))
        f = self.trocar(pessoal(self.ref), pericia__provocar__treino=1, pericia__provocar__bonus=2)
        self.assertTrue(any(p.campo == "treinos" for p in self.analisar(f)[0].problemas))

    def test_origem_nao_concede_duas_pericias_por_aprendizado(self):
        f = self.trocar(pessoal(self.ref), origem="Restrição Celestial · Sem Energia", origem__menor_1="Aprendizado Complementar",
                        pericia__provocar__treino=1, pericia__provocar__bonus=2)
        self.assertFalse(self.analisar(f)[0].problemas)
        self.trocar(f, pericia__atuacao__treino=1, pericia__atuacao__bonus=2)
        self.assertTrue(any(p.campo == "treinos" for p in self.analisar(f)[0].problemas))

    def test_duas_vidas_nao_soma_os_dois_destinos_do_treino(self):
        f = self.trocar(pessoal(self.ref), origem="Encarnado", origem__marcante="Duas Vidas",
                        pericia__provocar__treino=1, pericia__provocar__bonus=2)
        self.assertFalse(self.analisar(f)[0].problemas)
        self.trocar(f, oficio__forja__treino=1, oficio__forja__bonus=4)
        self.assertTrue(any(p.campo == "treinos" for p in self.analisar(f)[0].problemas))

    def test_especialidade_antiga_gratuita_sem_marco_corpo(self):
        f = self.trocar(pessoal(self.ref, 10), origem="Encarnado", origem__marcante="Duas Vidas",
                        origem__menor_1="Especialidade Antiga", pericia__provocar__treino=1, pericia__provocar__bonus=3,
                        pericia__atletismo__especialista=1, pericia__atletismo__bonus=6)
        self.assertFalse(self.analisar(f)[0].problemas)
        self.assertTrue(any("origem de cada escolha" in s for s in self.analisar(f)[0].nao_conferido))

    def test_troca_oficios_por_pericia_e_armas_por_duas_pericias(self):
        f = self.trocar(pessoal(self.ref), oficio__conducao__treino=0, oficio__conducao__bonus=2,
                        oficio__arrombamento__treino=0, oficio__arrombamento__bonus=2,
                        pericia__provocar__treino=1, pericia__provocar__bonus=2)
        self.assertFalse(self.analisar(f)[0].problemas)
        f = self.trocar(pessoal(self.ref), caminho="Evocador", trocou_por_arma="1 arma (-2 pericias)")
        for slug in list(self.ref.testes.pericias)[7:9]:
            a = self.ref.testes.pericias[slug][1]
            f["pericia." + slug + ".treino"] = Campo(0, "", "entrada")
            f["pericia." + slug + ".bonus"] = f["atributo." + a + ".base"]
        self.assertFalse(self.analisar(f)[0].problemas)

    def test_formato_antigo_preserva_cobertura_parcial(self):
        f = self.trocar(pessoal(self.ref), formato__versao=2)
        r, avisos = self.analisar(f)
        self.assertEqual((r.problemas, avisos), ([], set()))
        self.assertTrue(any("ANALISE 4" in s for s in r.nao_conferido))

    def test_atributos_nao_confiam_no_aviso_ou_no_total_exportado(self):
        f = self.trocar(pessoal(self.ref), atributo__forca__base=4, atributo__destreza__base=1,
                        aviso__pontos_disponiveis="")  # nove pontos, mas 4 sem marco
        r, _ = self.analisar(f)
        self.assertIn("atributos.base", [p.campo for p in r.problemas])
        f = self.trocar(pessoal(self.ref), atributo__essencia__base=0)
        self.assertIn("atributos.base", [p.campo for p in self.analisar(f)[0].pendencias])

    def test_ponto_de_corpo_exige_marco_e_total_maximo_seis(self):
        f = self.trocar(pessoal(self.ref), atributo__forca__corpo=1)
        self.assertIn("atributos.corpo", [p.campo for p in self.analisar(f)[0].problemas])
        f = self.trocar(pessoal(self.ref, 30), marco__corpo=4,
                        atributo__forca__base=6, atributo__forca__corpo=1)
        self.assertIn("atributo.forca.corpo", [p.campo for p in self.analisar(f)[0].problemas])

    def entidade(self):
        f = pessoal(self.ref, 18)
        atrs = dict(zip(ATRIBUTOS, (1, 2, 3, 2, 1)))
        f.update(campos(invocacao__1__nome="Domada de nível 5", invocacao__1__nivel=5,
                        invocacao__1__atributo_fisico="Força", invocacao__1__tr_treinado="Vigor"))
        for a, v in atrs.items():
            f.update(campos(**{f"invocacao.1.atributo.{a}.base": v, f"invocacao.1.atributo.{a}.buff": 0}))
        for slug, (nome, a) in TRS.items():
            f.update(campos(**{f"invocacao.1.buff.tr.{slug}": 0,
                f"invocacao.1.tr.{slug}.bonus": atrs[a or 'forca'] + (3 if nome == 'Vigor' else 0)}))
        for i in range(1, 8):
            slug = list(self.ref.testes.pericias)[i - 1]
            n, a = self.ref.testes.pericias[slug]
            f.update(campos(**{f"invocacao.1.pericia.{i}": n if i <= 5 else "",
                f"invocacao.1.pericia.{i}.bonus": atrs[a] + 3 if i <= 5 else "",
                f"invocacao.1.buff.pericia.{i}": 999}))
        return f

    def test_domada_usa_maestria_dono_sem_somar_buff_pericia_legado(self):
        r, _ = self.analisar(self.entidade())
        self.assertFalse(r.problemas)
        self.assertTrue(any("TR Vigor: bônus +6" in s for s in r.conferidos))
        self.assertTrue(any("Atletismo: bônus +4" in s for s in r.conferidos))

    def test_pericia_duplicada_e_excesso_da_entidade(self):
        f = self.entidade()
        self.trocar(f, invocacao__1__pericia__6="Atletismo", invocacao__1__pericia__6__bonus=4)
        self.assertTrue(any("distintas" in p.esperado for p in self.analisar(f)[0].problemas))

    def test_tr_faltando_e_pericias_a_menos_da_entidade_sao_pendencias(self):
        f = self.trocar(self.entidade(), invocacao__1__tr_treinado="", invocacao__1__pericia__5="")
        r, _ = self.analisar(f)
        self.assertTrue({"invocacao.1.tr_treinado", "invocacao.1.pericias"} <= {p.campo for p in r.pendencias})

    def test_bonus_entidade_adulterado_e_ajuste_ausente(self):
        f = self.trocar(self.entidade(), invocacao__1__tr__fisico__bonus=999, invocacao__1__pericia__1__bonus=999)
        r, _ = self.analisar(f)
        self.assertTrue({"invocacao.1.tr.fisico.bonus", "invocacao.1.pericia.1.bonus"} <= {p.campo for p in r.problemas})
        del f["invocacao.1.buff.tr.fisico"]
        r, _ = self.analisar(f)
        self.assertFalse(any("TR Físico: bônus" in s and "Invocação" in s for s in r.conferidos))

    def test_buff_de_inteligencia_nao_prova_treino_permanente(self):
        f = self.trocar(self.entidade(), invocacao__1__atributo__inteligencia__buff=2)
        r, _ = self.analisar(f)
        self.assertTrue(any("duração/origem" in s for s in r.nao_conferido))


if __name__ == "__main__":
    unittest.main()
