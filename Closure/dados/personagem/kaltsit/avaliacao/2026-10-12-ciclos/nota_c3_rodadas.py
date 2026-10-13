"""Três rodadas da bateria_c3: separa padrão (falha em 2 ou 3 rodadas) de ruído (falha em 1).
    python3 nota_c3_rodadas.py c3v14 [closure|kaltsit] [haiku]
Lê r_<v>r1.._r3_[<pers>_]<modelo>_a/_b.json e confere cada resposta com o conferir() do nota_c3.py."""
import collections, json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
v = sys.argv[1]; pers = sys.argv[2] if len(sys.argv) > 2 else "closure"; mod = sys.argv[3] if len(sys.argv) > 3 else "haiku"
sys.argv = ["nota_c3.py", v, pers, mod]
import nota_c3 as N  # noqa: E402

def rodada(k):
    R = {}
    for p in "ab":
        f = os.path.join(D, f"r_{v}r{k}{'' if pers == 'closure' else '_' + pers}_{mod}_{p}.json")
        if os.path.exists(f): R.update({r["id"]: r["resposta"] for r in json.load(open(f, encoding="utf-8"))})
    return R

rods = [rodada(k) for k in (1, 2, 3)]
print(f"{pers} {v} {mod}: respostas por rodada {[len(r) for r in rods]}")
limpos = [sum(1 for i, t in r.items() if not N.conferir(i, t)) for r in rods]
print("sem nenhuma falha por rodada:", limpos, "| '!' por rodada:", [sum('!' in t for t in r.values()) for r in rods])
por_id = collections.defaultdict(list)
for k, r in enumerate(rods, 1):
    for i, t in r.items():
        for tipo, d in N.conferir(i, t): por_id[(i, tipo, d.split(':')[0][:30])].append(k)
padrao = {x: ks for x, ks in por_id.items() if len(set(ks)) >= 2}
ruido = {x: ks for x, ks in por_id.items() if len(set(ks)) == 1}
print(f"\nPADRÃO (falha em 2 ou 3 rodadas): {len(padrao)}")
for (i, tipo, d), ks in sorted(padrao.items()):
    print(f"  {i} {N.B[i]['cat']} {tipo:<9} {d:<30} rodadas {sorted(set(ks))} | {N.B[i]['mensagem'][:45]}")
    for k in sorted(set(ks)): print(f"      r{k}: {rods[k-1][i][:160]}")
print(f"\nRUÍDO (falha em 1 rodada): {len(ruido)} | por tipo {dict(collections.Counter(t for (_, t, _) in ruido))}")
for (i, tipo, d), ks in sorted(ruido.items()):
    print(f"  {i} {N.B[i]['cat']} {tipo:<9} {d:<30} r{ks[0]} | {rods[ks[0]-1][i][:120]}")
