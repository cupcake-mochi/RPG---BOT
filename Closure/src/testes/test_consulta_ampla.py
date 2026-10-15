"""Fontes de recomendações, nomes exatos e contestação; não chama o modelo."""
import json
from pathlib import Path
import re
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas/prompt_do_site"))
import site_prompt

PRONTO = bool(site_prompt.motores()) and (site_prompt.CACHE / "nucleo.js").exists()


@unittest.skipUnless(PRONTO, "precisa do núcleo local e de um motor")
class ConsultaAmpla(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.livro = {b["ancora"]: b for b in map(json.loads, (RAIZ / "dados/sistema/livro.jsonl").read_text().splitlines())}

    def montar(self, msg, anteriores=(), pers="kal", **extra):
        turnos = [{"de": "user", "nome": "Alex", "texto": t} for t in anteriores]
        p = site_prompt.montar(pers, msg, nome="Alex", hora=(14, 0), turnos=turnos, **extra)
        texto = p["input"][-1]["content"]
        return texto, re.findall(r"\[Livro, âncora ([^\]]+)\]", texto)

    def origem(self, msg, anteriores=()):
        texto, fontes = self.montar(msg, anteriores)
        self.assertEqual(fontes[:2], ["origens--legado-criar", "origens--origem-escolhas"])
        for a in fontes[:2]:
            self.assertIn(self.livro[a]["texto"], texto)
        self.assertIn("criar com o mestre uma marcante e menores", texto)
        return texto

    def test_criacao_de_origem_inclui_permissao_e_escolha_padrao(self):
        for msg in ("oq eu posso criar na origem?", "posso criar uma marcante própria?",
                    "posso personalizar as duas menores da Origem?"):
            with self.subTest(msg=msg):
                self.origem(msg)

    def test_duvida_do_usuario_nao_substitui_a_fonte(self):
        for msg in ("Mas a capacidade marcante da pra criar? Acreditava q era só a menor e os legados",
                    "Tem certeza? Achei que só podia criar menores e Legados."):
            self.origem(msg, ["oq eu posso criar na origem?"])

    def test_pergunta_da_imagem_conserva_assunto(self):
        texto = self.origem("Ent pq disse q da pra criar?",
                            ["oq eu posso criar na origem?", "Mas a capacidade marcante da pra criar?"])
        self.assertIn("só mude uma conclusão quando a regra justificar", texto)

    def test_confirmacoes_repetidas_nao_perdem_regra_depois_de_dois_turnos(self):
        self.origem("qual a fonte?", ["oq eu posso criar na origem?", "tem certeza?", "onde está escrito?"])

    def test_assunto_novo_explicito_nao_herda_permissao_da_origem(self):
        _, fontes = self.montar("Tem certeza? Como funciona Energia Reversa?", ["oq eu posso criar na origem?"])
        self.assertIn("aptidoes--apt-reversa", fontes)
        self.assertNotIn("origens--legado-criar", fontes)

    def test_cafe_e_conversa_casual_nao_puxam_panorama(self):
        for msg, ant in (("me explica café", ["oq eu posso criar na origem?"]),
                         ("tem certeza?", ["você gosta de café?"]),
                         ("me recomende um café", ["me recomende uma trilha para lutar com armas"])):
            texto, fontes = self.montar(msg, ant)
            self.assertEqual(fontes, [])
            self.assertNotIn("[Panorama de Caminhos", texto)

    def test_recomendacao_real_mostra_malabarista_condutor_e_permissao_da_parceria(self):
        for pers in ("kal", "clo"):
            texto, fontes = self.montar("me recomende uma trilha para um indivíduo que luta com várias armas diferentes.", pers=pers)
            for a in ("incursor--inc-malabarista", "emanador--ema-condutor"):
                self.assertIn(a, fontes)
                self.assertIn(self.livro[a]["texto"], texto)
            self.assertIn("[Referência do livro: evocador--ev-parceria]", texto)
            self.assertIn("#### Treino de Combate\n\n**Nível 2.**\n\nEscolha uma **categoria de armas** e receba treino com suas armas.", texto)
            self.assertIn("todas as categorias de armas Simples, Marciais e de Fogo", texto)
            self.assertIn("Os requisitos de Força continuam valendo", texto)
            self.assertEqual(texto.count("#### Arma Condutora"), 1)

    def test_panorama_contem_os_seis_caminhos_e_as_dezoito_trilhas(self):
        texto, _ = self.montar("quais caminhos e trilhas existem no livro?")
        cat = json.loads((RAIZ / "dados/sistema/catalogos.json").read_text())
        self.assertEqual(len(cat["CAMINHOS"]), 6)
        for caminho in cat["CAMINHOS"]:
            for nome in [caminho["nome"], *caminho["trilhas"]]:
                self.assertIn("### " + nome, texto)
        self.assertIn("Batedor é uma Trilha com três rotas", texto)

    def test_panorama_traz_recortes_literais_e_tem_limite(self):
        texto, _ = self.montar("me recomende uma trilha para lutar com armas diferentes")
        pano = texto.split("[Panorama de Caminhos", 1)[1].split("[Livro, âncora", 1)[0]
        self.assertLessEqual(len(pano), 12300)
        fontes = re.findall(r"\[Referência do livro: ([^\]]+)\]\n([\s\S]*?)(?=\n\n\[Referência|$)", pano)
        self.assertTrue(fontes)
        for a, recorte in fontes:
            for parte in recorte.strip().split("\n\n"):
                self.assertIn(parte.strip(), self.livro[a]["texto"], a)

    def test_pergunta_de_um_caminho_nao_precisa_panorama_de_todos(self):
        texto, fontes = self.montar("quais trilhas da Vanguarda você recomenda?")
        refs = re.findall(r"\[Referência do livro: ([^\]]+)\]", texto)
        self.assertTrue(refs)
        self.assertTrue(all(a.startswith("vanguarda--") for a in refs))
        self.assertTrue({"vanguarda--van-estocada", "vanguarda--van-executor"} <= set(fontes))
        self.assertTrue(any(a in fontes for a in ("vanguarda--van-yumi", "vanguarda--van-besta", "vanguarda--van-fogo")))

    def test_preco_pontual_nao_expande_panorama(self):
        texto, fontes = self.montar("quanto custa uma katana?", ["me recomende uma trilha para lutar com armas"])
        self.assertIn("equip--eqa-laminas", fontes)
        self.assertNotIn("[Panorama de Caminhos", texto)

    def test_nome_de_trilha_prevalece_sobre_caminho_associado_errado(self):
        texto, fontes = self.montar("o que faz a Trilha Condutor Armado da Vanguarda?")
        self.assertIn("emanador--ema-condutor", fontes)
        self.assertIn(self.livro["emanador--ema-condutor"]["texto"], texto)

    def test_nomes_exatos_nao_se_confundem_com_radicais_ou_subsecoes(self):
        for nome, a in (("Arrastar e transportar", "geral--arrasto"), ("Socorro", "dano--socorro"),
                        ("Artes do Vínculo", "emanador--ema-artes"), ("Propriedades", "equip--eq-propriedades"),
                        ("Catálogo de criação", "catalogo--cat-catalogo"), ("Rotas de criação", "rotas--rotas")):
            texto, fontes = self.montar("No livro, como funciona " + nome + "?")
            self.assertIn(a, fontes, nome)
            self.assertIn(self.livro[a]["texto"], texto, nome)
            self.assertTrue(all(f.split("--")[0] == a.split("--")[0] for f in fontes), (nome, fontes))

    def test_comparacao_de_nome_contido_preserva_ambas_quando_pedidas(self):
        texto, fontes = self.montar("qual a diferença entre Artes do Vínculo e Vínculo?")
        for a in ("emanador--ema-artes", "evocador--ev-vinculo"):
            self.assertIn(a, fontes)
            self.assertIn(self.livro[a]["texto"], texto)

    @unittest.skipUnless(len(site_prompt.motores()) == 2, "precisa dos dois motores")
    def test_recomendacao_contestacao_e_nomes_exatos_iguais_nos_motores(self):
        for msg, ant in (("me recomende uma trilha para lutar com armas diferentes", []),
                         ("Ent pq disse q da pra criar?", ["oq eu posso criar na origem?", "tem certeza?"]),
                         ("No livro, como funciona Socorro?", [])):
            self.assertEqual(self.montar(msg, ant, motor="quickjs"), self.montar(msg, ant, motor="node"))
