"""Desambiguação de contexto e continuidade; nenhum modelo ou rede."""
import re
import sys
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas/prompt_do_site"))
import site_prompt

PRONTO = bool(site_prompt.motores()) and (site_prompt.CACHE / "nucleo.js").exists()

CASUAIS = (
    "Meu sistema operacional travou de novo. Você também perde a paciência com computador?",
    "Hoje fiquei sem energia para fazer qualquer coisa. Como você descansa?",
    "Essa trilha sonora ficou na minha cabeça. Você ouve música enquanto trabalha?",
    "Saí em defesa de um amigo numa discussão. Você acha que fiz besteira?",
    "Meu irmão dominou o videogame e não larga o controle. Você dividiria a vez?",
    "A integridade do arquivo deu erro e perdi o download. Que saco, né?",
    "Pode me tratar no feminino. Estou contente por ter passado na prova.",
    # Paráfrases que não participaram da bateria paga.
    "Meu Linux parou no meio da atualização do sistema. Como você lida com isso?",
    "Estou esgotado depois da semana. O que você faz para descansar?",
    "Recomende uma trilha sonora para ouvir enquanto trabalho.",
    "Fui em defesa da minha irmã. Será que fiz certo?",
    "Como dividir o controle do console sem discutir?",
    "Como verifico a integridade dos dados depois do download?",
    "Meus pronomes são ela/dela. Pode me tratar no feminino?",
    'A música diz "faça um teste de resistência". Que letra estranha, né?',
)


@unittest.skipUnless(PRONTO, "precisa do núcleo local e de um motor")
class ConsultaCotidiana(unittest.TestCase):
    def test_precos_em_relato_longo_priorizam_tabela_do_item(self):
        for item, fonte, valor in (
            ("katana", "equip--eqa-laminas", "48.000"),
            ("espada longa", "equip--eqa-laminas", None),
        ):
            for pers in ("clo", "kal"):
                msg = ("A gente tava falando mais sobre musica e talz, antes eu tava ouvindo sky fall "
                       f"mas por sinal, tinha te pedido o valor da {item} no livro, quanto tá?")
                p, fontes = self.montar(msg, pers=pers)
                self.assertEqual(fontes[0], fonte)
                if valor:
                    self.assertIn(valor, p['ctx'])

    def test_precos_de_tabelas_curtas_e_nomes_curtos(self):
        for item, fonte in (("Bō", "equip--eqa-impacto"), ("Pé de cabra", "equip--eqi-itens"),
                            ("Telefone", "equip--eqi-itens"), ("Traje 2", "equip--eqc-precos"),
                            ("Escudo Médio", "equip--eqc-precos")):
            for prefixo in ("", "Meu computador travou. "):
                with self.subTest(item=item, prefixo=prefixo):
                    _, fontes = self.montar(prefixo + f"Quanto custa {item} no livro?")
                    self.assertEqual(fontes[0], fonte)

    def test_preco_de_conversa_nao_e_preco_de_equipamento(self):
        for msg in ("Quanto custa uma playlist de música clássica?", "Meu celular quebrou, quanto custa o conserto?"):
            _, fontes = self.montar(msg)
            self.assertEqual(fontes, [])

    def montar(self, msg, anteriores=(), pers="kal", **extra):
        turnos = [{"de": "user", "nome": "Alex", "texto": t} for t in anteriores]
        p = site_prompt.montar(pers, msg, nome="Alex", hora=(14, 0), turnos=turnos, **extra)
        p["ctx"] = p["input"][-1]["content"].split("[Contexto ativado]\n", 1)[1].split("\n\n[Mensagem]", 1)[0]
        fontes = re.findall(r"\[Livro, âncora ([^\]]+)\]", p["ctx"])
        return p, fontes

    def test_conversa_nao_puxa_livro_ou_panorama_nas_duas_guias(self):
        for msg in CASUAIS:
            for pers in ("clo", "kal"):
                with self.subTest(msg=msg, pers=pers):
                    p, fontes = self.montar(msg, pers=pers)
                    self.assertEqual(fontes, [])
                    self.assertNotIn("[Panorama de Caminhos", p["ctx"])
                    self.assertFalse(any(n.startswith("Termo:") for n in p["ativadas"]))
                    self.assertIn("Alex: " + msg, p["input"][-1]["content"])

    def test_perguntas_reais_com_mesmas_palavras_conservam_fontes(self):
        for msg, esperada in (
            ("No sistema, como funciona um teste de resistência?", "geral--resistencia"),
            ("Como funciona Energia Reversa?", "aptidoes--apt-reversa"),
            ("Como funciona a Trilha Malabarista?", "incursor--inc-malabarista"),
            ("No livro, como funciona a Forma Controle?", "fundamento--controle"),
            ("No livro, como funciona Defesa e cobertura?", "geral--defesa"),
            ("No livro, como funcionam os Estágios de Integridade?", "dano--integridade"),
            ("No livro, como funciona Tratar e Retomar?", "guia--guia-tratamento"),
        ):
            with self.subTest(msg=msg):
                _, fontes = self.montar(msg)
                self.assertIn(esperada, fontes)

    def test_conversa_e_regra_na_mesma_mensagem(self):
        for msg in (
            "Essa trilha sonora é ótima. Como funciona Energia Reversa?",
            "Essa trilha sonora é ótima, mas como funciona Energia Reversa?",
            "Meu sistema operacional travou; quais os requisitos de Energia Reversa?",
            "Estou sem energia para sair e quero saber o custo de Energia Reversa.",
            "O videogame cansou, como funciona Energia Reversa no RPG?",
        ):
            with self.subTest(msg=msg):
                p, fontes = self.montar(msg)
                self.assertIn("aptidoes--apt-reversa", fontes)
                self.assertIn("Alex: " + msg, p["input"][-1]["content"])

    def test_misto_de_musica_e_recomendacao_de_trilha(self):
        p, fontes = self.montar("Gostei da trilha sonora, mas recomende uma Trilha para lutar com várias armas diferentes no RPG.")
        self.assertIn("[Panorama de Caminhos", p["ctx"])
        self.assertIn("[Referência do livro: incursor--inc-malabarista]", p["ctx"])
        self.assertIn("emanador--ema-condutor", fontes)

    def test_nomes_de_trilha_em_mensagens_mistas_sem_rotulo(self):
        for nome, fonte in (("Malabarista", "incursor--inc-malabarista"), ("Parceria", "evocador--ev-parceria")):
            with self.subTest(nome=nome):
                _, fontes = self.montar("Meu computador travou. Como funciona " + nome + "?")
                self.assertIn(fonte, fontes)

    def test_descanso_mecanico_e_forma_controle_em_contexto_misto(self):
        for msg, fonte in (
            ("Estou esgotado. Quanto PE recupero no descanso curto?", "dano--descansos"),
            ("Meu irmão não larga o videogame. Como funciona a Forma Controle?", "fundamento--controle"),
            ("A integridade do arquivo falhou. No livro, o que acontece ao perder Integridade?", "dano--integridade"),
        ):
            with self.subTest(msg=msg):
                _, fontes = self.montar(msg)
                self.assertIn(fonte, fontes)

    def test_preco_de_item_nomeado_nao_exige_rotulo_livro_depois_de_papo(self):
        for msg in ("Meu computador travou. Quanto custa uma katana?",
                    "O download falhou, mas quanto custa uma katana no livro?",
                    "Estou cansado, quanto custa uma katana?"):
            with self.subTest(msg=msg):
                _, fontes = self.montar(msg)
                self.assertIn("equip--eqa-laminas", fontes)

    def test_troca_casual_encerra_regra_e_nao_a_ressuscita(self):
        origem = "O que posso criar na Origem?"
        for msg in CASUAIS[:7]:
            with self.subTest(msg=msg):
                self.assertEqual(self.montar(msg, [origem])[1], [])
                p, fontes = self.montar("Tem certeza?", [origem, msg])
                self.assertEqual(fontes, [])
                self.assertNotIn("[Panorama de Caminhos", p["ctx"])

    def test_consulta_real_depois_de_conversa_recupera_livro(self):
        _, fontes = self.montar("Como funciona Energia Reversa?", ["Essa trilha sonora ficou na cabeça."])
        self.assertIn("aptidoes--apt-reversa", fontes)

    def test_contestacao_de_regra_mista_conserva_fonte(self):
        ant = ["Meu computador travou, mas o que posso criar na Origem?", "Tem certeza?"]
        for msg in ("Qual é a fonte disso no livro?", "Pode explicar melhor?"):
            with self.subTest(msg=msg):
                _, fontes = self.montar(msg, ant)
                self.assertIn("origens--legado-criar", fontes)

    @unittest.skipUnless(len(site_prompt.motores()) == 2, "precisa dos dois motores")
    def test_filtro_igual_em_quickjs_e_node(self):
        for msg in (CASUAIS[0], CASUAIS[2], CASUAIS[7], CASUAIS[-1],
                    "Essa trilha sonora é ótima, mas como funciona Energia Reversa?"):
            with self.subTest(msg=msg):
                q = self.montar(msg, motor="quickjs")
                n = self.montar(msg, motor="node")
                self.assertEqual(q, n)


if __name__ == "__main__":
    unittest.main()
