"""Cria deliberadamente a fórmula sem cache de A02; não calcula uma ficha."""
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def invalidar(arquivo: Path):
    # O XLSX normal foi produzido pelo artifact-tool. Esta corrupção pontual
    # é necessária para exercitar a recusa de arquivo incompleto pelo leitor.
    from openpyxl import load_workbook
    wb = load_workbook(arquivo, read_only=True)
    try:
        aba = wb["ANALISE"]
        caminho = aba._worksheet_path
        linha = next(i for i, valores in enumerate(aba.values, 1)
                     if valores[0] == "vida_max")
    finally:
        wb.close()
    with ZipFile(arquivo) as z:
        entradas = [(info, z.read(info.filename)) for info in z.infolist()]
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    alterados = []
    for info, dados in entradas:
        if info.filename == caminho:
            raiz = ET.fromstring(dados)
            celula = raiz.find(f".//{ns}c[@r='B{linha}']")
            if celula is None:
                raise ValueError("vida_max sem célula de valor")
            celula.attrib.pop("t", None)
            for filho in list(celula):
                celula.remove(filho)
            ET.SubElement(celula, ns + "f").text = "1+1"
            dados = ET.tostring(raiz, encoding="utf-8", xml_declaration=True)
        alterados.append((info, dados))
    with ZipFile(arquivo, "w") as z:
        for info, dados in alterados:
            z.writestr(info, dados)
    print(f"{arquivo.name}: ANALISE!B{linha} contém fórmula sem resultado em cache")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", type=Path)
    invalidar(parser.parse_args().arquivo)
