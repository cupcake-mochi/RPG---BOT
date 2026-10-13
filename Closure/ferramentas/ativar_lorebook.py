"""Simula o acionamento do lorebook.json por palavra-chave, como o bot vai fazer.
ativar(texto) devolve o bloco de contexto: as entradas sempre ligadas e as acionadas."""
import json, os, re, unicodedata
LB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dados/personagem/kaltsit/lorebook.json")
MAX_MUNDO, MAX_TERMOS = 5, 3

def _norm(s):
    s = s.lower()
    return s + "\n" + "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def ativar(texto, lb=None):
    E = list(json.load(open(lb or LB, encoding="utf-8"))["entries"].values())
    t = _norm(texto)
    sempre = [e for e in E if e["constant"]]
    hit = []
    for e in E:
        if e["constant"] or e["disable"]:
            continue
        # a chave mais longa que bateu decide a prioridade: "arquivo restrito" passa na frente de "escola"
        n = max([len(k) for k in e["key"] if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", t)] or [0])
        if n:
            hit.append((n, e))
    mundo = [e for n, e in sorted(hit, key=lambda x: -x[0]) if e["group"] == "mundo"][:MAX_MUNDO]
    termos = [e for n, e in sorted(hit, key=lambda x: -x[0]) if e["group"] == "sistema"][:MAX_TERMOS]
    return [e["comment"] for e in sempre + mundo + termos], "\n\n".join(e["content"] for e in sempre + mundo + termos)

if __name__ == "__main__":
    import sys
    print(ativar(" ".join(sys.argv[1:]))[0])
