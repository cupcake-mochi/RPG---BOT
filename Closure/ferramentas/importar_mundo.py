"""Importa somente os textos permitidos do consolidado fornecido pelo Mizuki.

Não extrai o ZIP. Arquivos fora da lista positiva sequer são abertos.
Uso: python3 ferramentas/importar_mundo.py CAMINHO.zip
"""
from __future__ import annotations

import hashlib
import copy
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
VERSAO = "era-2026-10-18-v2"


def normalizar(texto: str) -> str:
    texto = texto.translate(str.maketrans("’‘ʼ＇", "''''"))
    return "".join(c for c in unicodedata.normalize("NFD", texto.casefold().replace("æ", "ae")) if unicodedata.category(c) != "Mn")


def nomes_publicados(texto: str) -> tuple[set[str], dict[str, set[str]]]:
    """Nomes em negrito e títulos nome — cargo; rótulos editoriais não são nomes."""
    nomes, curtos = set(), {}
    rotulo = re.compile(r"^(?:localizacao|acesso|capital|capitais|cidades?|vilas?|regiao|regioes|territorios?|distritos?|grandes|estado associado|antiga capital|centro religioso|principal centro|governoratos|condados|prefeituras|assentamentos|divisao|divisoes|fortificacoes|localidade|localidades|local religioso|igrejas|marco historico|formacao|montanhas|rios|lago|consulta|registros individuais|conhecimento do personagem|aprofundamento|nivel|niveis|os nove|as tres|outras cidades|expansao urbana)\b")
    for m in re.finditer(r"\*\*([^*\n]+)\*\*", texto):
        bruto = m[1].strip()
        nome = bruto.rstrip(":").strip()
        composto = re.split(r"\s+[—–]\s+", nome, maxsplit=1)
        pessoa_com_cargo = len(composto) == 2 and bool(re.search(r"\b(?:capo|conselheir[oa]|diretor[a]?|governador[a]?|presidente|lider|comandante|chefe|rei|rainha|imperador|imperatriz|representante)\b", normalizar(composto[1])))
        if len(composto) == 2:
            nome = composto[0]
        n = normalizar(nome)
        if (not 4 <= len(nome) <= 60 or not nome[0].isupper() or ":" in nome
                or n in {"norte", "sul", "desconhecida", "lago", "montanhas", "rios", "locomotiva", "cidade de ouro", "basilica", "era da revolucao", "primavera"}
                or n.startswith(("rei das maldicoes", "nao possui", "assentamento sem nome", "santa reconhecida"))):
            continue
        if bruto.endswith(":") and rotulo.match(n):
            continue
        nomes.add(n)
        if "'" in n:
            nomes.add(n.replace("'", ""))
        # Abrevia apenas pessoas identificadas pelo cargo ou parentesco publicado.
        # Não transforma Northern Court em Northern, Max D.C. em Max ou uma
        # localidade com descrição (Porto Lungmen — Distrito comercial) em Porto.
        parentesco = re.match(r",\s+(?:sua|seu)\s+(?:namorad[oa]|mae|pai|irma[oa]?|tutor[a]?)\b", normalizar(texto[m.end():]))
        partes = nome.split()
        if (pessoa_com_cargo or parentesco) and len(partes) >= 2:
            primeiro = normalizar(partes[0])
            if len(primeiro) >= 4 and primeiro not in {"signora", "senhor", "senhora", "mount", "lake", "saint", "north", "northern", "south", "southern", "grand"}:
                curtos.setdefault(primeiro, set()).add(n)
    return nomes, curtos


def reindexar(dados: dict) -> dict:
    """Recria apenas o índice do corpus autorizado já salvo; não acessa o ZIP."""
    saida = copy.deepcopy(dados)
    abreviacoes, indices = {}, {}
    for i, doc in enumerate(saida["documentos"]):
        if doc["fonte"].split("/")[0] not in PASTAS:
            raise ValueError("documento fora da lista permitida")
        if doc["tipo"] == "regiao" and not doc["fonte"].split("/")[1].startswith("00-"):
            nomes, curtos = nomes_publicados("\n\n".join(s["texto"] for s in doc["secoes"]))
            indices[i] = (nomes, curtos)
            # Considera também homônimos sem cargo/parentesco, não só os nomes
            # que ganharam uma forma curta. Apóstrofos não criam outra pessoa.
            for nome in nomes:
                if " " in nome:
                    abreviacoes.setdefault(nome.split()[0], set()).add(nome.replace("'", ""))
    for i, doc in enumerate(saida["documentos"]):
        nomes, curtos = indices.get(i, (set(), {}))
        doc["apelidos"] = sorted(nomes | {normalizar(doc["titulo"])} | {c for c in curtos if len(abreviacoes[c]) == 1})
    saida["versao"] = VERSAO
    return saida


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
            documentos.append({"fonte": "/".join(p.parts[1:]), "titulo": titulo,
                               "tipo": PASTAS[p.parts[1]], "sha256": hashlib.sha256(bruto).hexdigest(),
                               "secoes": dividir(texto, titulo)})
    if not documentos or set(d["tipo"] for d in documentos) != set(PASTAS.values()):
        raise ValueError("consolidado sem as três categorias públicas esperadas")
    return reindexar({"arquivo_sha256": hashlib.sha256(caminho.read_bytes()).hexdigest(),
                     "pastas_permitidas": list(PASTAS), "documentos": documentos})


if __name__ == "__main__":
    dados = reindexar(json.loads(SAIDA.read_text(encoding="utf-8"))) if sys.argv[1] == "--reindexar" else importar(Path(sys.argv[1]))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(dados['documentos'])} documentos; {sum(len(d['secoes']) for d in dados['documentos'])} seções; {SAIDA}")
