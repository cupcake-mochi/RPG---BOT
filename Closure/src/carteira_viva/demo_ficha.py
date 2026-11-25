"""Planilha fictícia em memória, com as células que o preenchimento usa. Só demonstração e testes."""
import json

import httpx

from . import criacao_plano as cp
from .criacao_plano import MAPA, PESSOAL, PROGRESSAO
from .preencher import ABAS, TEXTOS

CAMINHOS = [("Bastião", "Atletismo", "Provocar", "Não", "Todas", ("Muro", "Punho", "Combatente Amaldiçoado")),
            ("Vanguarda", "Acrobacia", "Percepção", "Não", "Todas", ("Estocada", "Executor")),
            ("Guia", "Persuasão", "Medicina", "Sim", "Categorias selecionadas", ("Arquiteto", "Analista", "Socorrista")),
            ("Emanador", "Ocultismo", "Investigação", "Sim", "Categorias selecionadas", ("Condutor Armado", "Ressonante", "Catalisador")),
            ("Evocador", "Religião", "Lidar com Animais", "Sim", "Categorias selecionadas", ("Parceria",)),
            ("Incursor", "Acrobacia", "Intuição", "Não", "Todas", ("Assassino", "Pugilista", "Malabarista"))]
FIM_ANALISE = 60


class Planilha:
    def __init__(self):
        self.v, self.notas, self.alturas, self.formulas = {}, {}, {}, {}
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
        self.poe("FICHA", MAPA["troca_arma"]["celula"], cp.TROCAS[0])
        self.poe("FICHA", MAPA["tr_fisico"], "FORÇA")
        self.poe("FICHA", "AH10", "NÍVEL")
        for k, texto in dict(nivel=2, pontos="9 de 9", pericias="9 de 9", oficios="2 de 2", testes="2 de 2").items():
            self.poe("FICHA", MAPA["leituras"][k], texto)
        trilha = 2
        for n, (nome, p1, p2, troca, treino, trilhas) in enumerate(CAMINHOS, 2):
            for coluna, x in zip("MRSUV", (nome, p1, p2, troca, treino)):
                self.poe(PROGRESSAO, f"{coluna}{n}", x)
            for t in trilhas:
                self.poe(PROGRESSAO, f"AA{trilha}", t)
                self.poe(PROGRESSAO, f"AB{trilha}", nome)
                trilha += 1
        for n, x in enumerate((2, 9, 3, 6, 9, 2, 10), 2):
            self.poe("DADOS_CONFIG", f"S{n}", x)
        for coluna, xs in dict(CS=("Latente", "Descendente"), CP=("✎ Criada com o mestre", "Marcante A", "Marcante B"),
                               CQ=("✎ Criada com o mestre", "Menor A", "Menor B")).items():
            for n, x in enumerate(xs, 2):
                self.poe("DADOS_CUSTOM", f"{coluna}{n}", x)
        for n, (k, x) in enumerate((("formato.versao", "13"), ("ficha.versao", "R53"), ("ficha.sistema", "Ciclo Maldito")), 2):
            self.poe("ANALISE", f"A{n}", k)
            self.poe("ANALISE", f"B{n}", x)
        self.poe("ANALISE", f"A{FIM_ANALISE - 1}", "analise.estado")
        self.poe("ANALISE", f"B{FIM_ANALISE - 1}", "em_dia")
        self.poe("CARTEIRA", "AH4", "Bot: em dia · 24/11 13:25")
        self.poe("CARTEIRA", "AT4", False)
        self.poe("DADOS", "DL4", "texto da nota")
        self.poe("DADOS", "DM4", "caixa da nota")
        for n, (texto, caixa) in enumerate((("Tudo cabe na sua Força.", "AF86"), ("", "D86")), 5):
            self.poe("DADOS", f"DL{n}", texto)
            self.poe("DADOS", f"DM{n}", caixa)
        for c in TEXTOS.values():
            self.formulas[PESSOAL, *cp.posicao(c)] = "=SE(1;2)"
        self.ids = {aba: n for n, aba in enumerate(ABAS, 1)}

    def poe(self, aba, celula, valor):
        self.v[aba, *cp.posicao(celula)] = valor

    def de(self, aba, celula):
        return self.v.get((aba, *cp.posicao(celula)), "")

    def _faixa(self, faixa, formulas):
        aba, _, a1 = faixa.rpartition("!")
        aba, (de, _, ate) = aba.strip("'"), a1.partition(":")
        (l1, c1), (l2, c2) = cp.posicao(de), cp.posicao(ate or de)
        linhas = []
        for y in range(l1, l2 + 1):
            linha = [(self.formulas if formulas else {}).get((aba, y, x), self.v.get((aba, y, x), "")) for x in range(c1, c2 + 1)]
            while linha and linha[-1] == "":     # a API corta o fim vazio
                linha.pop()
            linhas.append(linha)
        while linhas and not linhas[-1]:
            linhas.pop()
        return {"range": faixa} | ({"values": linhas} if linhas else {})

    def aplicar(self, corpo):
        nomes = {n: aba for aba, n in self.ids.items()}
        for r in corpo["requests"]:
            if "updateDimensionProperties" in r:
                g = r["updateDimensionProperties"]
                self.alturas[nomes[g["range"]["sheetId"]], g["range"]["startIndex"] + 1] = g["properties"]["pixelSize"]
                continue
            r = r["updateCells"]
            lugar = (nomes[r["range"]["sheetId"]], r["range"]["startRowIndex"] + 1, r["range"]["startColumnIndex"] + 1)
            celula, campos = r["rows"][0]["values"][0], r["fields"].split(",")
            if "userEnteredValue" in campos:
                self.v[lugar] = next(iter(celula.get("userEnteredValue", {"": ""}).values()))
            if "note" in campos:
                self.notas[lugar] = celula.get("note", "")

    def responder(self, request, corpo=b""):
        """O mínimo da API do Sheets que o preenchimento chama."""
        arquivo = request.url.path.split("/")[3].partition(":")[0]
        if request.method == "POST":
            self.aplicar(json.loads(corpo))
            return httpx.Response(200, json={"spreadsheetId": arquivo})
        if request.url.path.endswith("/values:batchGet"):
            formulas = request.url.params["valueRenderOption"] == "FORMULA"
            return httpx.Response(200, json={"spreadsheetId": arquivo, "valueRanges":
                                             [self._faixa(f, formulas) for f in request.url.params.get_list("ranges")]})
        return httpx.Response(200, json={"spreadsheetId": arquivo, "sheets": [{"properties": {
            "sheetId": n, "title": aba, "gridProperties": {"rowCount": FIM_ANALISE if aba == "ANALISE" else 300}}}
            for aba, n in self.ids.items()]})
