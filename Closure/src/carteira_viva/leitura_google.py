"""Adapta a grade autenticada ao leitor tipado existente, sem interpretar regras."""
from closure_bot.ficha_leitor import FichaIlegivel, de_linhas


def da_grade(obj, arquivo):
    if not isinstance(obj, dict) or obj.get("spreadsheetId") != arquivo:
        raise FichaIlegivel("o Google não retornou a ficha solicitada")
    abas = obj.get("sheets", [])
    if len(abas) != 1 or abas[0].get("properties", {}).get("title") != "ANALISE":
        raise FichaIlegivel("a planilha não tem a aba ANALISE")
    dados = abas[0].get("data", [])
    if len(dados) != 1 or dados[0].get("startRow", 0) != 0 or dados[0].get("startColumn", 0) != 0:
        raise FichaIlegivel("a grade ANALISE está incompleta")
    linhas = dados[0].get("rowData", [])
    if isinstance(linhas, list):
        # Formatação em linhas vazias não é uma exportação com mais registros.
        linhas = list(linhas)
        while linhas and not any(c.get("effectiveValue")
                                 for c in linhas[-1].get("values", [])):
            linhas.pop()
    # A linha sentinela impede aceitar uma exportação cortada no limite.
    if not isinstance(linhas, list) or len(linhas) > 20001:
        raise FichaIlegivel("a aba ANALISE excede o limite de linhas")
    valores = []
    for n, linha in enumerate(linhas, 1):
        celulas = linha.get("values", [])
        if not isinstance(celulas, list) or len(celulas) > 4:
            raise FichaIlegivel("a grade ANALISE está fora do formato")
        saida = []
        for col, celula in enumerate(celulas):
            efetivo = celula.get("effectiveValue", {})
            if "errorValue" in efetivo:
                # Não registrar a fórmula, o texto do Google nem o conteúdo da célula.
                raise FichaIlegivel(f"erro de fórmula em ANALISE!{'ABCD'[col]}{n}")
            tipos = set(efetivo) & {"stringValue", "numberValue", "boolValue"}
            if len(tipos) > 1 or (efetivo and not tipos):
                raise FichaIlegivel("valor de célula fora do formato")
            # Sheets pode omitir effectiveValue quando o resultado é vazio.
            # Não é o cache XLSX: a API entrega resultados vivos e errorValue.
            # O leitor/motor conservam vazio e não certificam contas sem entrada.
            valor = efetivo[next(iter(tipos))] if tipos else ""
            if type(valor) not in (str, int, float, bool):
                raise FichaIlegivel("valor de célula fora do formato")
            saida.append(valor)
        valores.append(saida)
    if not valores or valores[0] != ["chave", "valor", "célula", "parte"]:
        raise FichaIlegivel("o cabeçalho da ANALISE está fora do formato")
    ficha = de_linhas(valores)
    if "formato.versao" not in ficha:
        raise FichaIlegivel("a aba ANALISE está fora do formato (falta formato.versao)")
    return ficha
