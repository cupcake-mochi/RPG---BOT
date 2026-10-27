"""Sondagem de leitura; resultado vazio nunca atesta inicialização limpa.

Os livros financeiros são lidos até o limite físico, após conferir a grade.
Notas de missão também carregam identidade salarial. Nada aqui limpa dados.
"""
import re

from .segredos import ErroCarteira

VERSAO_SONDAGEM = 2
MAX_LINHAS_HISTORICO = 5000
SINAIS = frozenset({"extrato_presente", "estado_salarial_presente", "emissao_presente", "salarios_presentes",
                    "missoes_registradas", "trocas_salariais_presentes", "marcas_salariais_presentes",
                    "missoes_preenchidas", "caixa_financeira_preenchida", "correcao_missao_pendente"})
FIXAS = ("'ANALISE'!A1:B5", "'FICHA'!AH11:AN11", "'DADOS'!CZ47:CZ47",
         "'CONFIGURAÇÃO'!E46:G46", "'DADOS_SALARIOS'!L2:N2", "'FICHA PESSOAL'!O86:O86",
         "'FICHA PESSOAL'!BI11:BI11", "'FICHA PESSOAL'!BO11:BO11",
         "'FICHA PESSOAL'!AW15:AX87", "'FICHA PESSOAL'!BC15:BD87",
         "'FICHA PESSOAL'!BI15:BJ87", "'FICHA PESSOAL'!BO15:BP87")
MINIMOS = {"ANALISE": (5, 2), "FICHA": (11, 40), "DADOS": (47, 104), "CONFIGURAÇÃO": (46, 7),
           "DADOS_SALARIOS": (2, 14), "FICHA PESSOAL": (87, 68), "EXTRATO": (2, 3), "SALÁRIOS": (2, 12)}


def faixas_sondagem(meta):
    """Ranges explícitos dentro da grade; nunca truncar um livro para parecer vazio."""
    grades = {}
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        nome = props.get("title")
        if nome in grades:
            raise ErroCarteira("Sondagem de modelo ambígua.")
        grades[nome] = props.get("gridProperties", {})
    for nome, minimo in MINIMOS.items():
        g = grades.get(nome, {})
        dimensoes = (g.get("rowCount"), g.get("columnCount"))
        if any(type(v) is not int or v < m for v, m in zip(dimensoes, minimo)):
            raise ErroCarteira("Falta uma grade compatível com o modelo R53.")
    ranges = list(FIXAS)
    for nome, ultima_coluna in (("EXTRATO", "C"), ("SALÁRIOS", "L"), ("DADOS_SALARIOS", "J")):
        linhas = grades[nome]["rowCount"]
        if linhas > MAX_LINHAS_HISTORICO:
            raise ErroCarteira("O histórico do modelo excede o limite da conferência. Não foi certificado como vazio.")
        ranges.append(f"'{nome}'!A2:{ultima_coluna}{linhas}")
    return tuple(ranges)


def sondar(obj):
    cells = {}
    for sheet in obj.get("sheets", []):
        title = sheet.get("properties", {}).get("title")
        if title in cells:
            raise ErroCarteira("Sondagem de modelo ambígua.")
        cells[title] = {}
        for block in sheet.get("data", []):
            for ri, row in enumerate(block.get("rowData", []), block.get("startRow", 0)):
                for ci, value in enumerate(row.get("values", []), block.get("startColumn", 0)):
                    if "errorValue" in value.get("effectiveValue", {}):
                        raise ErroCarteira("O modelo está incompleto ou recalculando.")
                    cells[title][ri, ci] = value
    required = MINIMOS.keys()
    if not required <= cells.keys():
        raise ErroCarteira("Faltam abas do contrato de modelo R53.")

    def cell(title, row, col):
        return cells[title].get((row - 1, col - 1), {})

    def value(c):
        v = c.get("effectiveValue", {})
        return v.get("stringValue", v.get("numberValue", v.get("boolValue")))

    header = {value(cell("ANALISE", r, 1)): value(cell("ANALISE", r, 2)) for r in range(2, 6)}
    if (header.get("formato.versao") not in (12, "12") or header.get("ficha.versao") != "R53" or
            header.get("ficha.livro") != "Ciclo Maldito R53"):
        raise ErroCarteira("Use um modelo ANALISE 12 / R53.")
    for title, row, col in (("FICHA", 11, 40), ("DADOS", 47, 104), ("CONFIGURAÇÃO", 46, 7)):
        if not cell(title, row, col).get("userEnteredValue", {}).get("formulaValue"):
            raise ErroCarteira("Falta uma fórmula de referência no modelo.")

    def filled(c):
        # Literal ou fórmula retornando conteúdo; não reter seus valores.
        return value(c) not in (None, "") or any(v not in (None, "") for v in c.get("userEnteredValue", {}).values())

    signs = []
    if any(filled(c) for c in cells["EXTRATO"].values()): signs.append("extrato_presente")
    if filled(cell("DADOS_SALARIOS", 2, 12)): signs.append("estado_salarial_presente")
    if filled(cell("DADOS_SALARIOS", 2, 14)): signs.append("emissao_presente")
    if any(filled(c) for c in cells["SALÁRIOS"].values()): signs.append("salarios_presentes")
    salarial = cells["DADOS_SALARIOS"]
    if any(filled(c) for (r, col), c in salarial.items() if r >= 1 and 0 <= col < 7):
        signs.append("missoes_registradas")
    if any(filled(c) for (r, col), c in salarial.items() if r >= 1 and 7 <= col < 10):
        signs.append("trocas_salariais_presentes")
    pessoal = cells["FICHA PESSOAL"]
    missoes = [c for (r, col), c in pessoal.items() if 14 <= r < 87 and col in (48, 49, 54, 55, 60, 61, 66, 67)]
    if any(filled(c) for c in missoes): signs.append("missoes_preenchidas")
    if any(re.search(r"\[Sal[aá]rio:", c.get("note", ""), re.IGNORECASE) for c in missoes):
        signs.append("marcas_salariais_presentes")
    if filled(cell("FICHA PESSOAL", 86, 15)): signs.append("caixa_financeira_preenchida")
    if any(filled(cell("FICHA PESSOAL", 11, col)) for col in (61, 67)):
        signs.append("correcao_missao_pendente")
    return sorted(signs)
