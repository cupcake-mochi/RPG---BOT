"""O preenchimento planejado pelo bot contra o que o script da ficha faz."""
import hashlib
import json
from pathlib import Path
import unittest

from carteira_viva import criacao_plano as cp
from carteira_viva.criacao_plano import MAPA, PESSOAL, PROGRESSAO, SEM_CAMINHO, SEM_TRILHA

ESPERADO = json.loads((Path(__file__).parent / "dados_criacao_esperado.json").read_text(encoding="utf-8"))
CAMINHOS = [("Bastião", "Atletismo", "Provocar", "Não", "Todas"), ("Vanguarda", "Acrobacia", "Percepção", "Não", "Todas"),
            ("Guia", "Persuasão", "Medicina", "Sim", "Categorias selecionadas"),
            ("Emanador", "Ocultismo", "Investigação", "Sim", "Categorias selecionadas"),
            ("Evocador", "Religião", "Lidar com Animais", "Sim", "Categorias selecionadas"),
            ("Incursor", "Acrobacia", "Intuição", "Não", "Todas")]


def curto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


class Ficha:
    """Grade em memória: nasce como a oficial limpa e aplica os planos."""
    def __init__(self):
        self.v, self.notas, self.ricos, self.alturas = {}, {}, {}, {}
        for c in MAPA["identidade"] + MAPA["escolhas"]:
            self.poe(c["aba"], c["rotulo"], c["texto_rotulo"])
            self.poe(c["aba"], c["celula"], c["fabrica"])
        for a in MAPA["atributos"]:
            self.poe("FICHA", a["rotulo"], a["nome"])
            self.poe("FICHA", a["celula"], 0)
        for k in ("pericias", "oficios", "testes"):
            for m in MAPA[k]:
                self.poe("FICHA", m["rotulo"], m["nome"])
                self.poe("FICHA", m["caixa"], False)
        for c in MAPA["treino"]["caixas"]:
            self.poe(PESSOAL, c["caixa"], False)
        self.poe("FICHA", MAPA["troca_arma"]["celula"], "Não trocou")
        self.poe("FICHA", MAPA["tr_fisico"], "FORÇA")
        self.poe("FICHA", MAPA["leituras"]["nivel"], 2)
        for n, (nome, p1, p2, troca, treino) in enumerate(CAMINHOS, 2):
            for coluna, x in zip("MRSUV", (nome, p1, p2, troca, treino)):
                self.poe(PROGRESSAO, f"{coluna}{n}", x)
        trilhas = list(dict.fromkeys((c["trilha"], c["caminho"]) for c in ESPERADO["casos"]
                                     if c["trilha"] != SEM_TRILHA and c["antes"] == SEM_CAMINHO))
        for n, (trilha, caminho) in enumerate(trilhas, 2):
            self.poe(PROGRESSAO, f"AA{n}", trilha)
            self.poe(PROGRESSAO, f"AB{n}", caminho)
        for n, x in enumerate((2, 9, 3, 6, 9, 2, 10), 2):
            self.poe("DADOS_CONFIG", f"S{n}", x)
        for coluna, xs in dict(CS=("Latente", "Descendente"), CP=("Zenin", "Kamo"), CQ=("✎ Criada com o mestre", "Menor A", "Menor B")).items():
            for n, x in enumerate(xs, 2):
                self.poe("DADOS_CUSTOM", f"{coluna}{n}", x)

    def poe(self, aba, celula, valor):
        self.v[aba, *cp.posicao(celula)] = valor

    def de(self, aba, celula):
        return self.v.get((aba, *cp.posicao(celula)), "")

    def ler(self):
        saida = []
        for faixa in cp.FAIXAS:
            aba, a1 = faixa.rsplit("!", 1)
            (l1, c1), (l2, c2) = map(cp.posicao, a1.split(":"))
            linhas = []
            for y in range(l1, l2 + 1):
                linha = [self.v.get((aba.strip("'"), y, x), "") for x in range(c1, c2 + 1)]
                while linha and linha[-1] == "":     # a API corta o fim vazio
                    linha.pop()
                linhas.append(linha)
            while linhas and not linhas[-1]:
                linhas.pop()
            saida.append({"range": faixa, "values": linhas})
        return cp.Leitura({"valueRanges": saida})

    def aplicar(self, plano):
        for e in plano.escritas:
            self.poe(e.aba, e.celula, e.valor)
            self.ricos[e.aba, e.celula] = [list(x) for x in e.negritos]
            if e.nota is not None:
                self.notas[e.aba, e.celula] = e.nota
        self.alturas |= plano.alturas
        return plano


class CaminhoComoNoScript(unittest.TestCase):
    def test_todos_os_caminhos_e_trilhas(self):
        self.assertEqual(len(ESPERADO["casos"]), 44)
        for caso in ESPERADO["casos"]:
            with self.subTest(**{k: caso[k] for k in ("antes", "trilhaAntes", "caminho", "trilha")}):
                f = Ficha()
                if caso["antes"] != SEM_CAMINHO:
                    f.aplicar(cp.caminho(f.ler(), caso["antes"], caso["trilhaAntes"]))
                    texto = MAPA["cartas"][0]["texto"]
                    f.poe("FICHA", texto, f.de("FICHA", texto) + "\n\nAnotação da mesa")
                    f.aplicar(cp.caminho(f.ler(), caso["caminho"], None, {"caminho"}))
                else:
                    f.aplicar(cp.caminho(f.ler(), caso["caminho"], caso["trilha"]))
                self.assertEqual(f.de("FICHA", "D11"), caso["caminho"])
                self.assertEqual(f.de("FICHA", "N11"), caso["fica"])
                marcadas = {p["nome"] for p in MAPA["pericias"] if f.de("FICHA", p["caixa"])}
                self.assertEqual(marcadas, set(caso["marcar"]))
                for p in MAPA["pericias"]:
                    if p["nome"] in caso["marcar"]:
                        self.assertEqual(f.notas["FICHA", p["caixa"]], "Treinado pelo Caminho " + caso["caminho"])
                    elif p["nome"] in caso["desmarcar"]:
                        self.assertEqual(f.notas["FICHA", p["caixa"]], "")
                self.assertEqual(sorted(c["caixa"] for c in MAPA["treino"]["caixas"] if f.de(PESSOAL, c["caixa"])), caso["treino"])
                for n, (carta, quer) in enumerate(zip(MAPA["cartas"], caso["cartas"])):
                    self.assertEqual(f.de("FICHA", carta["nome"]), quer["nome"])
                    self.assertEqual(curto(f.de("FICHA", carta["texto"])), quer["texto"])
                    nota = f.notas.get(("FICHA", carta["texto"]), "")
                    self.assertEqual(nota and curto(nota), quer["nota"])
                    self.assertEqual(f.de(PROGRESSAO, f"CB{n + 2}"), quer["automatico"])
                    self.assertEqual(curto(f.de(PROGRESSAO, f"CC{n + 2}")), quer["livro"])
                    if quer["texto"] == quer["livro"] != curto(""):
                        self.assertEqual(f.ricos["FICHA", carta["texto"]], quer["negritos"])
                    if ("FICHA", carta["linha"]) in f.alturas and not quer["nota"]:
                        self.assertEqual({f.alturas["FICHA", carta["linha"] + k] for k in range(4)}, {quer["altura"]})

    def test_repetir_nao_muda_nada(self):
        f = Ficha()
        f.aplicar(cp.caminho(f.ler(), "Guia", "Socorrista"))
        de_novo = cp.caminho(f.ler(), "Guia", "Socorrista")
        self.assertEqual(([e for e in de_novo.escritas], de_novo.alturas), ([], {}))

    def test_recusas(self):
        f = Ficha()
        for args in (("Inventado",), ("Guia", "Estocada"), (SEM_CAMINHO,)):
            with self.assertRaises(cp.Recusa):
                cp.caminho(f.ler(), *args)
        f.aplicar(cp.caminho(f.ler(), "Guia", "Socorrista"))
        with self.assertRaises(cp.JaPreenchido) as e:
            cp.caminho(f.ler(), "Bastião")
        self.assertEqual(e.exception.campos, ("caminho",))

    def test_categoria_de_arma_so_se_vazia(self):
        f = Ficha()
        p = f.aplicar(cp.caminho(f.ler(), "Emanador", "Condutor Armado"))
        self.assertIn("Arma Condutora", f.de("FICHA", MAPA["categoria_trilha"]))
        self.assertTrue(p.avisos)
        f.poe("FICHA", MAPA["categoria_trilha"], "Espadas")
        f.aplicar(cp.caminho(f.ler(), "Evocador", "Parceria", {"caminho", "trilha"}))
        self.assertEqual(f.de("FICHA", MAPA["categoria_trilha"]), "Espadas")


class Passos(unittest.TestCase):
    def test_rotulo_fora_do_lugar(self):
        f = Ficha()
        self.assertEqual(cp.conferir(f.ler()), [])
        f.poe("FICHA", "D10", "OUTRA COISA")
        f.poe("FICHA", MAPA["pericias"][0]["caixa"], "sim")
        self.assertEqual(cp.conferir(f.ler()), ["FICHA!D10", "FICHA!" + MAPA["pericias"][0]["caixa"]])

    def test_identidade(self):
        f = Ficha()
        p = f.aplicar(cp.identidade(f.ler(), {"nome": " Kaito ", "historia": "=IMPORTXML(1)\r\nfim"}))
        self.assertEqual((f.de("CARTEIRA", "O9"), f.de(PESSOAL, "Q27")), ("Kaito", "=IMPORTXML(1)\nfim"))
        self.assertTrue(p.alturas)
        with self.assertRaises(cp.JaPreenchido):
            cp.identidade(f.ler(), {"nome": "Outro"})
        f.aplicar(cp.identidade(f.ler(), {"nome": ""}, {"nome"}))
        self.assertEqual(f.de("CARTEIRA", "O9"), "Coloque o nome do personagem aqui")
        for ruim in ({"nome": "x" * 101}, {"nome": "a\x00"}, {"nome": 3}, {"xp": "9"}):
            with self.assertRaises(cp.Recusa):
                cp.identidade(f.ler(), ruim)

    def test_alturas_como_no_script(self):
        amostras = [x[0] for x in ESPERADO["linhas"]]
        for a in ESPERADO["alturas"]:
            grupo = MAPA["esticam"][a["grupo"]]
            textos = [amostras[(i + a["amostra"]) % len(amostras)] for i in range(len(grupo))]
            h = cp.alturas_que_esticam(grupo, textos)
            self.assertEqual({str(k): v for k, v in h.items()}, a["alturas"])
        for texto, linhas in ESPERADO["linhas"]:
            self.assertEqual([cp.linhas_do_texto(texto, 60 + 7 * k) for k in range(len(linhas))], linhas)

    def test_atributos(self):
        f, nomes = Ficha(), [a["nome"] for a in MAPA["atributos"]]
        f.aplicar(cp.atributos(f.ler(), dict(zip(nomes, (3, 2, 2, 1, 1)))))
        self.assertEqual([f.de("FICHA", a["celula"]) for a in MAPA["atributos"]], [3, 2, 2, 1, 1])
        for ruim in ((4, 2, 1, 1, 1), (3, 3, 3, 1, 0), (-1, 3, 3, 1, 1), (True, 2, 2, 1, 1), (3, 2, 2, 1)):
            with self.assertRaises(cp.Recusa):
                cp.atributos(Ficha().ler(), dict(zip(nomes, ruim)))
        f2 = Ficha()
        self.assertIn("Sobram 2", cp.atributos(f2.ler(), dict(zip(nomes, (3, 2, 2, 0, 0)))).avisos[0])
        f2.poe("DADOS_CONFIG", "S4", "três")
        with self.assertRaises(cp.Recusa):
            cp.atributos(f2.ler(), dict(zip(nomes, (3, 2, 2, 1, 1))))
        f4 = Ficha()
        f4.poe("FICHA", MAPA["leituras"]["nivel"], 3)
        with self.assertRaisesRegex(cp.Recusa, "nível inicial"):
            cp.atributos(f4.ler(), dict(zip(nomes, (3, 2, 2, 1, 1))))
        with self.assertRaisesRegex(cp.Recusa, "nível inicial"):
            cp.treinos(f4.ler(), pericias=[], oficios=[], testes=[])
        # A campanha manda: o limite vem da cópia, não do código.
        f3 = Ficha()
        f3.poe("DADOS_CONFIG", "S3", 12)
        f3.poe("DADOS_CONFIG", "S4", 4)
        self.assertTrue(cp.atributos(f3.ler(), dict(zip(nomes, (4, 4, 4, 0, 0)))).escritas)

    def test_origem_e_capacidades(self):
        f = Ficha()
        f.aplicar(cp.origem(f.ler(), "Descendente"))
        self.assertEqual(f.de("FICHA", "X11"), "Descendente")
        f.aplicar(cp.capacidades(f.ler(), {"marcante": "Zenin", "menor1": "Menor A"}))
        with self.assertRaises(cp.Recusa):
            cp.capacidades(f.ler(), {"menor2": "Menor A"})
        with self.assertRaises(cp.Recusa):
            cp.capacidades(f.ler(), {"marcante": "Gojo"})
        self.assertTrue(cp.capacidades(f.ler(), {"menor2": "✎ Criada com o mestre"}).avisos)
        # Texto escrito por cima da fórmula: só o script da ficha devolve a conta.
        with self.assertRaisesRegex(cp.Recusa, "à mão"):
            cp.capacidades(f.ler(), {"marcante": "Kamo"}, {"marcante"}, {"marcante"})
        self.assertTrue(cp.capacidades(f.ler(), {"marcante": "Kamo"}, {"marcante"}, {"menor2"}).escritas)
        # A Origem de fábrica da ficha é Latente: trocar dela não é conflito; trocar de novo é.
        with self.assertRaises(cp.JaPreenchido):
            cp.origem(f.ler(), "Latente")
        self.assertTrue(cp.origem(f.ler(), "Latente", {"origem"}).avisos)
        self.assertTrue(cp.altura_capacidades(f.ler()).alturas)

    def test_treinos(self):
        f = Ficha()
        with self.assertRaises(cp.Recusa):
            cp.treinos(f.ler(), pericias=[], oficios=[], testes=[])
        f.aplicar(cp.caminho(f.ler(), "Guia", "Socorrista"))
        livres = [p["nome"] for p in MAPA["pericias"] if p["nome"] not in ("Persuasão", "Medicina")]
        dois = [o["nome"] for o in MAPA["oficios"]][:2]
        ok = cp.treinos(f.ler(), pericias=livres[:7], oficios=dois, testes=["Físico", "Vigor"], tr_fisico="DESTREZA")
        self.assertNotIn("faltam", " ".join(ok.avisos))
        f.aplicar(ok)
        self.assertEqual(sum(f.de("FICHA", p["caixa"]) for p in MAPA["pericias"]), 9)
        self.assertEqual(f.de("FICHA", MAPA["tr_fisico"]), "DESTREZA")
        for ruim in (dict(pericias=livres[:8], oficios=dois, testes=[]), dict(pericias=livres[:9], oficios=[], testes=[]),
                     dict(pericias=livres[:7], oficios=[], testes=["Físico", "Vigor", "Espírito"]),
                     dict(pericias=livres[:6], oficios=dois, testes=[], troca=1), dict(pericias=["Voar"], oficios=[], testes=[]),
                     dict(pericias=[livres[0]] * 2, oficios=[], testes=[])):
            with self.assertRaises(cp.Recusa):
                cp.treinos(f.ler(), **ruim)
        # Desmarcar o que o jogador tinha marcado pede confirmação, e só do que muda.
        sem = dict(pericias=livres[:8], oficios=[], testes=["Físico"])      # 10 sem ofício
        with self.assertRaises(cp.JaPreenchido) as e:
            cp.treinos(f.ler(), **sem)
        self.assertEqual(e.exception.campos, ("oficios", "testes"))
        f.aplicar(cp.treinos(f.ler(), **sem, confirmados={"oficios", "testes"}))
        com = dict(pericias=livres[:5], oficios=dois, testes=[], troca=1)
        f.aplicar(cp.treinos(f.ler(), **com, confirmados={"pericias", "testes"}))
        with self.assertRaises(cp.JaPreenchido) as e:
            cp.treinos(f.ler(), **com | dict(tr_fisico="FORÇA", troca=0))
        self.assertEqual(e.exception.campos, ("tr_fisico", "troca"))
        self.assertEqual(f.de("FICHA", MAPA["troca_arma"]["celula"]), "1 arma (-2 pericias)")
        f.aplicar(cp.caminho(f.ler(), "Bastião", None, {"caminho"}))
        self.assertEqual(f.de("FICHA", MAPA["troca_arma"]["celula"]), "Não trocou")
        with self.assertRaises(cp.Recusa):
            cp.treinos(f.ler(), pericias=[], oficios=[], testes=[], troca=1)


class Pedido(unittest.TestCase):
    def test_corpo(self):
        f = Ficha()
        plano = cp.caminho(f.ler(), "Vanguarda", "Estocada")
        corpo = cp.pedido(plano, {"FICHA": 1, PESSOAL: 2, PROGRESSAO: 3, "CARTEIRA": 4})
        self.assertEqual(set(corpo), {"requests"})
        self.assertLess(len(json.dumps(corpo)), 400_000)
        tipos = {next(iter(r)) for r in corpo["requests"]}
        self.assertEqual(tipos, {"updateCells", "updateDimensionProperties"})
        for r in corpo["requests"]:
            if "updateCells" in r:
                g = r["updateCells"]["range"]
                self.assertEqual((g["endRowIndex"] - g["startRowIndex"], g["endColumnIndex"] - g["startColumnIndex"]), (1, 1))
                celula = r["updateCells"]["rows"][0]["values"][0]
                self.assertNotIn("formulaValue", celula.get("userEnteredValue", {}))
                for t in celula.get("textFormatRuns", []):
                    self.assertLess(t["startIndex"], len(celula["userEnteredValue"]["stringValue"].encode("utf-16-le")) // 2)
        with self.assertRaises(KeyError):
            cp.pedido(plano, {"FICHA": 1})

    def test_nota_viva_nao_toca_no_valor(self):
        f = Ficha()
        lido = f.ler()
        for y, (texto, caixa) in enumerate((("Falta Força", "AF86"), ("", "D86"), ("x", "")), 5):
            lido.v["DADOS", y, 116], lido.v["DADOS", y, 117] = texto, caixa
        plano = cp.notas_vivas(lido)
        self.assertEqual([(e.celula, e.nota) for e in plano.escritas], [("AF86", "Falta Força"), ("D86", "")])
        for r in cp.pedido(plano, {PESSOAL: 2})["requests"]:
            self.assertEqual(r["updateCells"]["fields"], "note")
            self.assertNotIn("userEnteredValue", r["updateCells"]["rows"][0]["values"][0])


if __name__ == "__main__":
    unittest.main()
