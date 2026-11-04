"""Perguntas de mesa e seguimentos. Só contexto local, sem modelo ou rede."""
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
class ConsultaNatural(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.livro = {b["ancora"]: b["texto"] for b in map(
            json.loads, (RAIZ / "dados/sistema/livro.jsonl").read_text().splitlines())}

    def montar(self, msg, anteriores=(), persona="kal", nova_terra=False, motor=None):
        p = site_prompt.montar(persona, msg, nome="Alex", hora=(14, 0),
                              turnos=[{"de": "user", "nome": "Alex", "texto": t} for t in anteriores],
                              estado={"nova_terra": nova_terra}, motor=motor)
        texto = p["input"][-1]["content"]
        fontes = re.findall(r"\[Livro, âncora ([^\]]+)\]", texto)
        self.assertLessEqual(len(fontes), 3)
        self.assertEqual(len(fontes), len(set(fontes)))
        return texto, fontes

    def conferir(self, msg, esperadas, **kwargs):
        texto, fontes = self.montar(msg, **kwargs)
        for a in esperadas:
            self.assertIn(a, fontes, msg)
            self.assertIn(self.livro[a], texto, msg)
        return fontes

    def test_casos_relatados_nas_duas_personagens_e_lores(self):
        for persona in ("kal", "clo"):
            for nova_terra in (False, True):
                for msg, fontes in (
                    ("Como funciona empunhadura dupla?", ["equip--eq-propriedades", "equip--eqa-armas"]),
                    ("Como funciona os Atributos?", ["geral--atributos"]),
                    ("quando eu invoco uma invocação elas já agem no meu turno que invoquei elas? Ou só depois?",
                     ["campo--inv-entrada", "campo--inv-ciclo"]),
                    ("Invocações autônomas, ao serem invocadas elas precisam de uma intenção básica pra agir, "
                     "vindo de uma segunda ação bônus, ou já ao chegarem no chão podem receber a intenção básica para ações simples",
                     ["campo--inv-entrada", "campo--inv-intencao"]),
                ):
                    with self.subTest(msg=msg, persona=persona, nova_terra=nova_terra):
                        obtidas = self.conferir(msg, fontes, persona=persona, nova_terra=nova_terra)
                        self.assertEqual(obtidas[0], fontes[0])

    def test_armas_em_duas_maos_nao_sao_arma_de_duas_maos(self):
        for msg in ("Como lutar com duas armas?", "Posso usar uma arma em cada mão?",
                    "Qual a vantagem de usar dois punhais?", "Como funciona dual wield no sistema?"):
            with self.subTest(msg=msg):
                fontes = self.conferir(msg, ["equip--eq-propriedades", "equip--eqa-armas"])
                self.assertFalse(any(a.startswith("evocador--") for a in fontes))
        self.conferir("Como usar uma arma de duas mãos?", ["equip--eq-propriedades"])

    def test_turnos_e_entrada_com_variacoes(self):
        for msg in ("Quando as invocações podem agir? Assim que invocadas?",
                    "Uma invocação age no turno em que é invocada?",
                    "Meu shikigami já pode atacar quando aparece?",
                    "Se eu invocar, ela ataca na mesma rodada?",
                    "Minha entidade acabou de entrar, ela pode agir?"):
            with self.subTest(msg=msg):
                self.conferir(msg, ["campo--inv-entrada", "campo--inv-ciclo"])
        self.conferir("Invocações têm iniciativa própria?", ["campo--inv-ciclo"])
        self.conferir("Como dar uma ordem pro shikigami?", ["campo--inv-intencao"])
        self.conferir("Como funciona a primeira intenção da invocação?",
                      ["campo--inv-intencao", "campo--inv-entrada"])
        self.conferir("Se eu trocar a invocação, ela já pode atacar?",
                      ["campo--inv-troca", "campo--inv-ciclo"])

    def test_atributos_e_definicoes_de_outros_capitulos(self):
        for msg, fonte in (
            ("Como funcionam os atributos?", "geral--atributos"),
            ("Como é que funcionam os atributos?", "geral--atributos"),
            ("Como q funciona os atributos?", "geral--atributos"),
            ("Me explica a maestria?", "geral--atributos"),
            ("Como funciona a iniciativa?", "geral--turnos"),
            ("O que é concentração?", "geral--concentracao"),
            ("Como funciona carga?", "geral--carga"),
            ("Como funciona o descanso curto?", "dano--descansos"),
            ("Como eu faço pra agarrar alguém?", "geral--manobras"),
            ("Se eu ficar com zero de vida, o que acontece?", "dano--zero"),
            ("Como recupero minha Integridade?", "dano--integridade"),
            ("Como funcionam os testes de resistência?", "geral--resistencia"),
            ("Como é que calcula um crítico?", "geral--critico"),
        ):
            with self.subTest(msg=msg):
                self.conferir(msg, [fonte])

    def test_seguimento_de_beneficio_mantem_armas_e_tabela_de_punhais(self):
        anteriores = ["Como funciona empunhadura dupla?",
                      "me refiro a usar duas armas para lutar, como por exemplo dois punhais"]
        self.conferir(anteriores[-1], ["equip--eq-propriedades", "equip--eqa-laminas"],
                      anteriores=anteriores[:1])
        for msg in ("então não existe nenhum benefício?", "e qual a vantagem?", "e tem alguma desvantagem?"):
            with self.subTest(msg=msg):
                self.conferir(msg, ["equip--eq-propriedades", "equip--eqa-laminas"], anteriores=anteriores)

    def test_seguimentos_em_outros_capitulos_e_confirmacoes(self):
        for ant, fonte in (("Como funciona Concentração?", "geral--concentracao"),
                           ("Como funciona o descanso curto?", "dano--descansos"),
                           ("Como funciona Energia Reversa?", "aptidoes--apt-reversa")):
            for msg in ("e quais os limites?", "e tem alguma desvantagem?", "qual a duração?"):
                with self.subTest(ant=ant, msg=msg):
                    self.conferir(msg, [fonte], anteriores=[ant])
        self.conferir("tem certeza?", ["equip--eq-propriedades"], anteriores=[
            "Como funciona empunhadura dupla?", "então não existe nenhum benefício?"])

    def test_mudanca_de_assunto_e_conversa_casual(self):
        for anteriores in ([], ["Como funciona empunhadura dupla?"], ["Quando minha invocação pode agir?"]):
            for msg in ("Como funciona autenticação dupla no celular?", "e qual a vantagem de tomar café?",
                        "Como funciona uma dupla musical?", "Quais os atributos de um arquivo no Linux?"):
                with self.subTest(msg=msg, anteriores=anteriores):
                    _, fontes = self.montar(msg, anteriores=anteriores)
                    self.assertEqual(fontes, [])
        for ant in ("Como funciona empunhadura dupla?", "Quando minha invocação pode agir?"):
            fontes = self.conferir("E como funciona Energia Reversa?", ["aptidoes--apt-reversa"], anteriores=[ant])
            self.assertNotIn("equip--eq-propriedades", fontes)
            self.assertNotIn("campo--inv-entrada", fontes)
            for msg, esperada in (("E como funcionam os atributos?", "geral--atributos"),
                                  ("E os atributos?", "geral--atributos"),
                                  ("Me explica melhor a maestria?", "geral--atributos"),
                                  ("E como funciona a iniciativa?", "geral--turnos")):
                with self.subTest(msg=msg, ant=ant):
                    fontes = self.conferir(msg, [esperada], anteriores=[ant])
                    self.assertEqual(fontes[0], esperada)
                    self.assertNotIn("equip--eq-propriedades", fontes)
                    self.assertNotIn("campo--inv-entrada", fontes)
        _, fontes = self.montar("e qual a vantagem?", anteriores=["Como funciona Concentração?", "gosto de café"])
        self.assertEqual(fontes, [])

    def test_duvida_especifica_nao_vira_regra_geral(self):
        for msg, esperada, proibida in (
            ("Como escolho o atributo da técnica?", "fundamento--tecnica", "campo--inv-entrada"),
            ("Quanto cura a especial da minha invocação de classe 5?", "construcao--entidades-especiais", "campo--inv-entrada"),
            ("Qual a vida e defesa de uma invocação nível 6 com Constituição 2?", "construcao--entidades-vida-defesa", "campo--inv-entrada"),
            ("Qual o preço em PE para retornar uma entidade caída?", "campo--inv-retorno", "campo--inv-entrada"),
            ("Quanto custa um punhal?", "equip--eqa-laminas", "campo--inv-entrada"),
        ):
            with self.subTest(msg=msg):
                fontes = self.conferir(msg, [esperada])
                self.assertNotIn(proibida, fontes)

    def test_atributo_do_golpe_com_arma_nomeada(self):
        for msg in ("Posso usar Destreza pra bater com uma faca?",
                    "Meu ataque com uma katana usa Força ou Destreza?",
                    "Uso Destreza no dano dos punhais?",
                    "Posso atacar com Destreza usando um machado?"):
            with self.subTest(msg=msg):
                # Ter a fonte não autoriza Fineza em todas as armas. A tabela
                # e a regra da propriedade precisam acompanhar a fórmula.
                fontes = self.conferir(msg, ["geral--ataques", "equip--eq-propriedades"])
                self.assertTrue(any(a.startswith("equip--eqa-") for a in fontes))
        fontes = self.conferir("Minha invocação usa Força ou Destreza no ataque com uma faca?",
                              ["construcao--entidades-atributos", "equip--eq-propriedades", "equip--eqa-laminas"])
        self.assertNotIn("geral--ataques", fontes)

    @unittest.skipUnless(len(site_prompt.motores()) == 2, "precisa dos dois motores")
    def test_paridade_dos_motores(self):
        for msg, anteriores in (
            ("Como funciona empunhadura dupla?", []),
            ("Como funciona os Atributos?", []),
            ("Quando minha invocação pode agir?", []),
            ("então não existe nenhum benefício?", ["Como lutar com dois punhais?"]),
        ):
            with self.subTest(msg=msg):
                self.assertEqual(self.montar(msg, anteriores, motor="quickjs"),
                                 self.montar(msg, anteriores, motor="node"))


if __name__ == "__main__":
    unittest.main()
