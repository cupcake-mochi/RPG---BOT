"""Extrai as falas de história de uma personagem dos dados do jogo.

Lê os roteiros (`gamedata/story/**/*.txt`) de um clone do ArknightsGameData
(zh_CN) ou do ArknightsGameData_YoStar (en_US, ja_JP, ko_KR) e grava um JSONL
por idioma, no mesmo formato de `dados/corpus_closure/`:

    {"lang", "arquivo", "linha", "antes": {"quem", "fala"} | null, "fala"}

`antes` é a última fala com [name=...] antes desta, no mesmo arquivo.

Uso:
    python ferramentas/extrair_corpus.py --raiz <clone> --lang en_US \
        --nome "Kal'tsit" --saida dados/corpus_kaltsit/historia_en_US.jsonl

`--nome` pode repetir, para juntar variantes da tag.
"""

import argparse
import json
import re
from pathlib import Path

FALA = re.compile(r'^\[name="([^"]*)"[^\]]*\](.*)$')


def extrair(raiz, lang, nomes):
    base = Path(raiz) / lang / "gamedata" / "story"
    saida = []
    for caminho in sorted(base.rglob("*.txt")):
        anterior = None
        rel = caminho.relative_to(base).as_posix()
        linhas = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
        for n, linha in enumerate(linhas, 1):
            m = FALA.match(linha.strip())
            if not m:
                continue
            quem, fala = m.group(1), m.group(2).strip()
            if quem in nomes:
                saida.append({"lang": lang, "arquivo": rel, "linha": n,
                              "antes": anterior, "fala": fala})
            anterior = {"quem": quem, "fala": fala}
    return saida


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raiz", required=True)
    p.add_argument("--lang", required=True)
    p.add_argument("--nome", action="append", required=True)
    p.add_argument("--saida", required=True)
    a = p.parse_args()
    falas = extrair(a.raiz, a.lang, set(a.nome))
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    with open(a.saida, "w", encoding="utf-8") as f:
        for x in falas:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"{a.lang}: {len(falas)} falas em "
          f"{len({x['arquivo'] for x in falas})} arquivos -> {a.saida}")


if __name__ == "__main__":
    main()
