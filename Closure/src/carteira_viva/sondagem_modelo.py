"""Sondagem limitada de leitura; resultado vazio nunca atesta ficha limpa."""
from .segredos import ErroCarteira

RANGES = ("'ANALISE'!A1:B5", "'FICHA'!AH11:AN11", "'DADOS'!CZ47:CZ47",
          "'CONFIGURAÇÃO'!E46:G46", "'EXTRATO'!A2:C6", "'DADOS_SALARIOS'!L2:N2",
          "'SALÁRIOS'!A2:L3")


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
    required = {"ANALISE", "FICHA", "DADOS", "CONFIGURAÇÃO", "EXTRATO", "DADOS_SALARIOS", "SALÁRIOS"}
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
        return value(c) not in (None, "") or bool(c.get("userEnteredValue", {}).get("stringValue"))

    signs = []
    if any(filled(c) for c in cells["EXTRATO"].values()): signs.append("extrato_presente")
    if filled(cell("DADOS_SALARIOS", 2, 12)): signs.append("estado_salarial_presente")
    if filled(cell("DADOS_SALARIOS", 2, 14)): signs.append("emissao_presente")
    if any(filled(c) for c in cells["SALÁRIOS"].values()): signs.append("salarios_presentes")
    return sorted(signs)
