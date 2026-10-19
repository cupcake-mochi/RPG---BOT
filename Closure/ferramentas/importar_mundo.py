"""Importa somente os textos permitidos do consolidado fornecido pelo Mizuki.

Não extrai o ZIP. Arquivos fora da lista positiva sequer são abertos.
Uso: python3 ferramentas/importar_mundo.py CAMINHO.zip
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "dados" / "mundo" / "era-revolucao.json"
PASTAS = {"01-Regioes-Extras": "regiao", "02-Canais-Publicos": "publico", "03-Guia-de-Mestragem": "mestragem"}
PREFIXO = "Era_da_Revolucao_Consolidado"


def normalizar(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.casefold().replace("æ", "ae")) if unicodedata.category(c) != "Mn")


def limpar(texto: str) -> str:
    texto = re.sub(r"(?m)^> ?", "", texto)
    texto = re.sub(r"(?m)^M:``` ```\s*$", "", texto)
    texto = re.sub(r"(?m)^N:## \* ", "## ", texto)
    # Links de capas e menções não são fonte adicional nem precisam ir ao modelo.
    texto = re.sub(r"\[([^\]]+)\]\(https?://[^\s)]+\)", r"\1", texto)
    texto = re.sub(r"<#\d+>", "[canal indicado no servidor]", texto)
    texto = re.sub(r"<@&\d+>", "[cargo indicado no servidor]", texto)
    texto = re.sub(r"<@!?\d+>", "[pessoa indicada no servidor]", texto)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def dividir(texto: str, titulo: str) -> list[dict]:
    """Preserva seções, parágrafos e listas; nenhum recorte começa no meio de frase."""
    partes, cabecalho, corpo, escopo = [], titulo, [], titulo

    def fechar():
        if not corpo:
            return
        atual = ""
        for paragrafo in "\n".join(corpo).strip().split("\n\n"):
            # Listas grandes são divididas por item, sem perder nenhum item.
            unidades = re.split(r"\n(?=\* )", paragrafo) if len(paragrafo) > 2200 else [paragrafo]
            for unidade in unidades:
                if atual and len(atual) + len(unidade) > 2800:
                    partes.append({"titulo": cabecalho, "texto": atual})
                    atual = ""
                if len(unidade) > 5000:
                    raise ValueError("parágrafo grande demais: " + cabecalho)
                atual += ("\n\n" if atual else "") + unidade
        if atual:
            partes.append({"titulo": cabecalho, "texto": atual})
        corpo.clear()

    for linha in texto.splitlines():
        m = re.match(r"^(#{1,3})\s+(.+)$", linha)
        if m:
            fechar()
            nome = re.sub(r"^[^\wÀ-ÿ]+", "", m[2]).strip()
            if len(m[1]) == 1:
                escopo = nome
            cabecalho = nome if nome == escopo else escopo + " / " + nome
        else:
            corpo.append(linha)
    fechar()
    return partes


def importar(caminho: Path) -> dict:
    documentos, vistos = [], set()
    with zipfile.ZipFile(caminho) as pacote:
        for item in sorted(pacote.infolist(), key=lambda i: i.filename):
            p = PurePosixPath(item.filename)
            # Seleção exata: não aceita subpastas extras, raiz, notas ou registros privados.
            if (len(p.parts) != 4 or p.parts[0] != PREFIXO or p.parts[1] not in PASTAS
                    or p.name != "Texto-para-Discord.txt" or ".." in p.parts or "\\" in item.filename):
                continue
            if item.filename in vistos:
                raise ValueError("fonte duplicada: " + item.filename)
            vistos.add(item.filename)
            if (item.external_attr >> 16) & 0o170000 == 0o120000 or item.file_size > 100_000:
                raise ValueError("fonte inválida: " + item.filename)
            bruto = pacote.read(item)
            texto = limpar(bruto.decode("utf-8-sig"))
            if not texto:
                raise ValueError("fonte vazia: " + item.filename)
            titulo = re.sub(r"^\d+-", "", p.parts[2]).replace("-", " ")
            apelidos = [titulo]
            if PASTAS[p.parts[1]] == "regiao" and not p.parts[2].startswith("00-"):
                # Nomes próprios publicados em negrito, inclusive cidades sem ficha própria.
                for nome in re.findall(r"\*\*([^*\n]+)\*\*", texto):
                    if (4 <= len(nome) <= 45 and nome[0].isupper() and ":" not in nome
                            and normalizar(nome) not in {"norte", "sul", "desconhecida", "lago", "montanhas", "rios", "locomotiva", "cidade de ouro", "basilica", "era da revolucao"}
                            and not normalizar(nome).startswith(("rei das maldicoes", "nao possui", "assentamento sem nome", "santa reconhecida"))):
                        apelidos.append(nome)
            documentos.append({"fonte": "/".join(p.parts[1:]), "titulo": titulo,
                               "tipo": PASTAS[p.parts[1]], "sha256": hashlib.sha256(bruto).hexdigest(),
                               "apelidos": sorted(set(normalizar(n) for n in apelidos)),
                               "secoes": dividir(texto, titulo)})
    if not documentos or set(d["tipo"] for d in documentos) != set(PASTAS.values()):
        raise ValueError("consolidado sem as três categorias públicas esperadas")
    return {"versao": "era-2026-10-18-v1", "arquivo_sha256": hashlib.sha256(caminho.read_bytes()).hexdigest(),
            "pastas_permitidas": list(PASTAS), "documentos": documentos}


if __name__ == "__main__":
    dados = importar(Path(sys.argv[1]))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(dados['documentos'])} documentos; {sum(len(d['secoes']) for d in dados['documentos'])} seções; {SAIDA}")
