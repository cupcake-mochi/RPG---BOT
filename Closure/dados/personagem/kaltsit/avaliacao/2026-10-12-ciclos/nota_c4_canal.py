"""Confere as respostas da bateria_c4_canal.json pelo gabarito (deve, nao).

    python3 nota_c4_canal.py r_c4canal_haiku_a.json [r_c4canal_sonnet_a.json ...]
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
B = {b["id"]: b for b in json.load(open(os.path.join(AQUI, "bateria_c4_canal.json"), encoding="utf-8"))}
for arq in sys.argv[1:]:
    R = {r["id"]: r["resposta"] for r in json.load(open(os.path.join(AQUI, arq), encoding="utf-8"))}
    ok = 0
    print(f"== {arq}")
    for i, b in B.items():
        t = R.get(i, "")
        falta = [p for p in b["deve"] if not re.search(p, t, re.I)]
        sobra = [p for p in b["nao"] if re.search(p, t, re.I)]
        passou = not falta and not sobra and t
        ok += bool(passou)
        print(f"{'ok ' if passou else 'FALHA'} {i} {len(t.split())}p {'!' if '!' in t else ' '} | {t[:150]}")
        if not passou:
            print(f"      falta {falta} sobra {sobra} | {b['nota']}")
    print(f"   {ok} de {len(B)}")
