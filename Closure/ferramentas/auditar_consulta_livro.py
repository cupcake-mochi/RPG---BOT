"""Confere fontes para títulos únicos do livro, sem chamar modelos ou rede.

Compara seleção de fontes, não a qualidade das respostas. Títulos repetidos,
continuações e exemplos ficam fora desta régua automática; exigem contexto.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import tempfile
import unicodedata

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas/prompt_do_site"))
import site_prompt


def casos():
    livro = list(map(json.loads, (RAIZ / "dados/sistema/livro.jsonl").read_text().splitlines()))
    def normal(s):
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()
    contagens = Counter(normal(b["titulo"]) for b in livro)
    return [{"pergunta": f'No livro, como funciona {b["titulo"]}?', "esperada": b["ancora"]}
            for b in livro if contagens[normal(b["titulo"])] == 1
            and not re.search(r"continua|exemplo|indice", normal(b["titulo"]))]


def conferir(titulos, nucleo=None):
    cache = site_prompt.CACHE
    resultados = []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            if nucleo:
                pasta = Path(tmp)
                (pasta / "nucleo.js").write_bytes(Path(nucleo).read_bytes())
                site_prompt.CACHE = pasta
            site_prompt._funcao = None
            for caso in titulos:
                p = site_prompt.montar("kal", caso["pergunta"], nome="Alex", hora=(14, 0))
                texto = p["input"][-1]["content"]
                fontes = re.findall(r"\[Livro, âncora ([^\]]+)\]", texto)
                resultados.append({**caso, "fontes": fontes, "achou": caso["esperada"] in fontes,
                                   "caracteres_ultima_mensagem": len(texto)})
    finally:
        site_prompt.CACHE = cache
        site_prompt._funcao = None
    return resultados


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--comparar", type=Path, help="núcleo anterior salvo para comparação")
    p.add_argument("--saida", type=Path, required=True)
    args = p.parse_args()
    titulos = casos()
    resultado = {"escopo": "fontes de títulos únicos; sem modelo, não mede respostas", "total": len(titulos)}
    for nome, nucleo in (("antes", args.comparar), ("depois", None)):
        if nome == "antes" and nucleo is None:
            continue
        resultado[nome] = conferir(titulos, nucleo)
        n = sum(r["achou"] for r in resultado[nome])
        print(f"{nome}: {n}/{len(titulos)} fontes esperadas", flush=True)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    faltantes = [r for r in resultado["depois"] if not r["achou"]]
    for r in faltantes:
        print(r["pergunta"], "->", r["fontes"])
    return int(bool(faltantes))


if __name__ == "__main__":
    raise SystemExit(main())
