"""Regressões de contexto: entradas completas e fontes conjuntas para contas do R53.

Monta pedidos localmente, sem chamar um modelo. Não certifica a resposta gerada no Discord.
"""
import json
import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas" / "prompt_do_site"))
import site_prompt  # noqa: E402

PRONTO = bool(site_prompt.motores()) and (site_prompt.CACHE / "nucleo.js").exists()


@unittest.skipUnless(PRONTO, "sem motor ou página montada")
class ConsultaDoLivro(unittest.TestCase):
    def test_reacao_fora_do_turno_traz_esclarecimento_r60_nas_duas_lores(self):
        for persona in ('kal', 'clo'):
            for nova_terra in (False, True):
                with self.subTest(persona=persona, nova_terra=nova_terra):
                    p = site_prompt.montar(persona, 'No livro, como funciona Conjurar?',
                                          nome='Alex', hora=(14, 20),
                                          estado={'nova_terra': nova_terra})
                    texto = p['input'][-1]['content']
                    self.assertIn(self.livro['fundamento--conjurar']['texto'], texto)
                    self.assertIn('Uma conjuração de Reação fora do seu turno fica fora desse limite.', texto)
                    self.assertIn('apenas um feitiço de Classe 1 ou maior', texto)
                    self.assertIn('o gatilho registrado', texto)

    def test_especialidade_antiga_traz_texto_editorial_r57_completo(self):
        texto, _ = self.fontes('No livro, como funciona Especialidade Antiga?',
                              ['origens--encarnado-beneficios'])
        self.assertIn('sem precisar escolher **Corpo** naquele **[Marco](#progressao--prog-marcos)**', texto)
        self.assertIn('um nível de progressão que concede ganhos comuns e uma escolha adicional', texto)

    def test_mais_um_nome_com_palavras_de_parada_tem_fonte_propria(self):
        texto, _ = self.fontes('No livro, como funciona Mais Um?', ['catalogo--melhoria-mais-um'])
        self.assertIn('Não copie os totais nem converta uma função em outra', texto)
        _, fontes = self.montar('Você conta mais um caso engraçado?')
        self.assertNotIn('catalogo--melhoria-mais-um', fontes)

    @classmethod
    def setUpClass(cls):
        cls.livro = {b["ancora"]: b for b in map(json.loads, (RAIZ / "dados/sistema/livro.jsonl").read_text().splitlines())}

    def montar(self, msg, anterior=None, **extra):
        turnos = [{"de": "user", "nome": "Alex", "texto": anterior}] if anterior else []
        p = site_prompt.montar("kal", msg, nome="Alex", hora=(14, 20), turnos=turnos, **extra)
        texto = p["input"][-1]["content"]
        return texto, re.findall(r"\[Livro, âncora ([^\]]+)\]", texto)

    def fontes(self, msg, esperadas, anterior=None, **extra):
        texto, ancoras = self.montar(msg, anterior, **extra)
        self.assertEqual(ancoras[:len(esperadas)], esperadas, msg)
        self.assertLessEqual(len(ancoras), 3)
        self.assertEqual(len(ancoras), len(set(ancoras)))
        for a in esperadas:
            self.assertIn(self.livro[a]["texto"], texto, a)
        return texto, ancoras

    def test_requisitos_reversa_incluem_origem_da_excecao(self):
        texto, _ = self.fontes("quais os requisitos para se ter energia reversa?",
                              ["aptidoes--apt-reversa", "rotas--rota-sem-tecnica"])
        self.assertIn("Refino 7 e nível 14", texto)
        self.assertIn("no nível 2", texto)
        self.assertIn("sem cumprir os requisitos comuns de nível e refino", texto)

    def test_pergunta_real_cura_classe_cinco_tem_orcamento_e_limite(self):
        texto, ancoras = self.fontes("Qual é o máximo que um feitiço de classe 5 pode fornecer de cura?",
                                    ["fundamento--pontos", "fundamento--funcoes"])
        self.assertIn("| 5 | 17 | 15 | 3 | 5 | 8 |", texto)
        self.assertIn("2 × Classe em d8", texto)
        self.assertIn("| 5 | 10 | 7 |", texto)
        self.assertIn("Cada ponto pode ser usado uma vez nessa distribuição", texto)
        self.assertNotIn("rotas--rota-cura", ancoras)
        self.assertFalse(any(a.startswith("aptidoes--") for a in ancoras))

    def test_variacoes_de_cura_e_apoio_em_todas_as_classes(self):
        for classe in range(1, 8):
            for forma in ("cura", "vida temporária"):
                with self.subTest(classe=classe, forma=forma):
                    self.fontes(f"quanto de {forma} um feitiço de classe {classe} fornece?",
                                ["fundamento--pontos", "fundamento--funcoes"])

    def test_conta_de_dano_tem_orcamento_e_tetos(self):
        self.fontes("quanto dano faz um feitiço de classe 5?",
                    ["fundamento--pontos", "fundamento--danolimites"])

    def test_pecas_nomeadas_tem_definicao_e_preco_da_classe(self):
        for nome, ancora in (("Longe", "catalogo--melhoria-longe"), ("Fura", "catalogo--melhoria-fura")):
            with self.subTest(nome=nome):
                _, ancoras = self.fontes(f"quanto custa a Melhoria {nome} na classe 5?", [ancora, "fundamento--pontos"])
                self.assertFalse(any(a.startswith("construcao--") for a in ancoras))

    def test_formas_nomeadas_tambem_trazem_sua_regra(self):
        for forma in ("Cura", "Apoio"):
            with self.subTest(forma=forma):
                self.fontes(f"como funciona a Forma {forma}?", ["fundamento--pontos", "fundamento--funcoes"])

    def test_habilidade_especial_usa_orcamento_da_entidade(self):
        texto, ancoras = self.fontes("quanto cura a especial da minha invocação de classe 5?",
                                    ["construcao--entidades-especiais", "construcao--entidades-saldo"])
        self.assertNotIn("fundamento--pontos", ancoras)
        self.assertFalse(any(a.startswith("aptidoes--") for a in ancoras))
        self.assertIn("| 5 | 6 | 3 |", texto)

    def test_tecnica_maxima_tem_tabela_propria_e_excecao(self):
        texto, _ = self.fontes("qual a cura máxima da Técnica Máxima?",
                              ["fundamento--maxima"])
        self.assertIn("A quantidade de dados permanece igual ao valor indicado na tabela", texto)

    def test_classe_zero_tem_proibicao_de_cura(self):
        texto, _ = self.fontes("pode usar Forma Cura num feitiço de classe 0?",
                              ["fundamento--classezero", "fundamento--funcoes"])
        self.assertIn("Cura e aplicação coletiva de benefícios não estão disponíveis", texto)

    def test_explicacoes_de_aptidoes_tem_complemento(self):
        for msg, esperadas in [
            ("como funciona energia reversa?", ["aptidoes--apt-reversa", "aptidoes--apt-energia-positiva"]),
            ("como funciona domínio simples?", ["aptidoes--apt-simples", "aptidoes--apt-simples-duracao"]),
            ("o que faz Cobrir-se de Energia?", ["aptidoes--apt-cobrir"]),
            ("me explique Canalizar em Golpe", ["aptidoes--apt-canalizar"]),
        ]:
            with self.subTest(msg=msg):
                self.fontes(msg, esperadas)

    def test_custo_pontual_nao_forca_complemento_da_explicacao(self):
        _, ancoras = self.fontes("quanto custa usar energia reversa?", ["aptidoes--apt-reversa"])
        self.assertNotIn("aptidoes--apt-energia-positiva", ancoras)

    def test_descanso_curto_nao_e_confundido_com_forma_cura(self):
        _, ancoras = self.montar("quanto PE um feitiço me deixa recuperar no descanso curto?")
        self.assertIn("dano--descansos", ancoras)
        self.assertNotIn("fundamento--funcoes", ancoras)

    def test_valores_e_definicoes_de_outros_capitulos(self):
        casos = [
            ("quanto custa uma katana?", ["equip--eqa-laminas"]),
            ("qual a proteção e o preço de um revestimento 3?", ["equip--eqp-escudo", "equip--eqc-precos"]),
            ("quanto custa um traje de proteção 2?", ["equip--eqc-precos"]),
            ("tenho 10 PE máximos e 1 atual, quanto recupero no descanso curto?", ["dano--descansos"]),
            ("quanto consigo saltar com Força 3?", ["geral--saltos"]),
            ("qual a carga que posso carregar com Força 3?", ["geral--carga"]),
            ("quanto dano eu tomo numa queda de 6 metros?", ["geral--quedas"]),
            ("como recupero Integridade no descanso longo?", ["dano--descansos", "dano--integridade"]),
            ("quanto XP custa passar do nível 9 para o 10?", ["progressao--prog-xp"]),
            ("qual a vida e defesa de uma invocação nível 6 com Constituição 2?", ["construcao--entidades-vida-defesa"]),
            ("quanto PE custa manifestar minha invocação?", ["campo--inv-entrada"]),
            ("qual o preço em PE para retornar uma entidade caída?", ["campo--inv-retorno"]),
            ("como calculo o teste de Ritual?", ["ritual--rit-teste"]),
            ("como funciona crítico com dados adicionais de arma?", ["geral--critico"]),
            ("qual a duração do Domínio Simples?", ["aptidoes--apt-simples-duracao"]),
            ("o que faz Fluxo?", ["catalogo--cat-passivas-2-recursos"]),
            ("como funciona Passo Rápido?", ["incursor--inc-fluidez"]),
            ("o que faz Pétala?", ["aptidoes--apt-petala"]),
            ("como funciona Concentração?", ["geral--concentracao"]),
        ]
        for msg, esperadas in casos:
            with self.subTest(msg=msg):
                texto, ancoras = self.montar(msg)
                for a in esperadas:
                    self.assertIn(a, ancoras)
                    self.assertIn(self.livro[a]["texto"], texto)

    def test_cruza_campos_de_tabela_por_nivel_sem_decorar_os_valores(self):
        for nivel in (1, 14, 16, 30):
            with self.subTest(nivel=nivel):
                _, ancoras = self.montar(f"qual o refino e a maestria no nível {nivel}?")
                tabela = "progressao--prog-tabela-" + ("inicial" if nivel <= 15 else "avancada")
                self.assertIn(tabela, ancoras)

    def test_lista_de_aptidoes_traz_catalogo(self):
        self.fontes("quais são as aptidões?", ["aptidoes--apt-catalogo", "aptidoes--apt-refino"])

    def test_explicar_melhor_herda_assunto_e_fontes(self):
        for msg in ("me explica melhor", "pode aprofundar?", "quanto custa?"):
            with self.subTest(msg=msg):
                self.fontes(msg, ["fundamento--pontos", "fundamento--funcoes"],
                            anterior="quanto cura um feitiço de classe 5?")
        self.fontes("me explica melhor", ["aptidoes--apt-reversa", "aptidoes--apt-energia-positiva"],
                    anterior="como funciona energia reversa?")

    def test_mudanca_de_assunto_nao_herda_regra(self):
        for msg, anterior in (("me explica café", "quanto cura um feitiço de classe 5?"),
                              ("me explica melhor", "você gosta de café?")):
            texto, ancoras = self.montar(msg, anterior)
            self.assertEqual(ancoras, [])
            self.assertNotIn("[Consulta do livro:", texto)

    def test_regra_com_carga_alta_preserva_explicacao_e_duvida_pontual(self):
        texto, _ = self.montar("como funciona energia reversa?", estado={
            "bloco": "[Estado agora: plantão; carga 2.]",
            "lembretes": ["Carga alta: uma frase."]})
        self.assertGreater(texto.index("[Consulta do livro:"), texto.index("[Carga alta:"))
        self.assertIn("Os avisos de brevidade não devem cortar regras necessárias", texto)
        self.assertIn("Numa dúvida pontual, responda só ao aspecto pedido", texto)

    @unittest.skipUnless(len(site_prompt.motores()) == 2, "precisa dos dois motores")
    def test_novas_fontes_e_seguimento_sao_iguais_nos_dois_motores(self):
        for msg, ant in (("quanto cura um feitiço de classe 5?", None),
                         ("qual a cura máxima da Técnica Máxima?", None),
                         ("como funciona energia reversa?", None),
                         ("me explica melhor", "quanto cura um feitiço de classe 5?")):
            with self.subTest(msg=msg):
                self.assertEqual(self.montar(msg, ant, motor="quickjs"), self.montar(msg, ant, motor="node"))


if __name__ == "__main__":
    unittest.main()
