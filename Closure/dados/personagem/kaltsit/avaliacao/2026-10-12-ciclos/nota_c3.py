"""Confere as respostas da bateria_c3 contra o gabarito e as regras de forma.
    python3 nota_c3.py c3v11 [closure|kaltsit] [haiku sonnet ...] [-v pra não listar as falhas]
Lê r_<v>_<modelo>_a.json e _b.json. Gabarito: campos deve/nao da bateria. Forma: do card da personagem."""
import json, os, re, sys, statistics as st, collections
D = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(D, "..", "..", "..", "..", "..")
v = sys.argv[1]; pers = sys.argv[2] if len(sys.argv) > 2 else "closure"; modelos = [a for a in sys.argv[3:] if not a.startswith("-")] or ["haiku", "sonnet"]
b0 = v.split("v")[0]  # "c3v11" usa a bateria_c3
bat = f"bateria_{b0}.json" if pers == "closure" else f"bateria_{b0}_{pers}.json"
B = {m["id"]: m for m in json.load(open(os.path.join(D, bat), encoding="utf-8"))}
card = json.load(open(os.path.join(RAIZ, f"dados/personagem/{pers}/card.json"), encoding="utf-8"))["data"]
pro = card["extensions"]["closure_lab"]["termos_proibidos"]
exs = [l.split(": ", 1)[1] for l in card["mes_example"].split("\n") if l.startswith("{{char}}")]
emo = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
gen = re.compile(r"(?<!-)\b(sozinh[oa]|cansad[oa]|obrigad[oa]|preocupad[oa]|pront[oa]|bem-vind[oa]|nov[oa] aqui|acordad[oa]|exaust[oa]|chatead[oa]|tranquil[oa]|segur[oa])\b(?![ -](?:socorro|atendimento))", re.I)
sem_excl = set("ABCDEH")  # regra, mundo e quem está mal: a Closure não exclama; a Kal'tsit nunca
def carregar(m):
    R = []
    for p in "ab":
        f = os.path.join(D, f"r_{v}{'' if pers=='closure' else '_'+pers}_{m}_{p}.json")
        if os.path.exists(f): R += json.load(open(f, encoding="utf-8"))
    return {r["id"]: r["resposta"] for r in R}
def conferir(i, t):
    m = B[i]; f = []
    for r in m["deve"]:
        if not re.search(r, t, re.I | re.M): f.append(("gabarito", "faltou /" + r[:40] + "/"))
    for r in m["nao"]:
        x = re.search(r, t, re.I | re.M)
        if x: f.append(("gabarito", "não podia: " + x.group(0)[:30]))
    for x in pro:
        if re.search(r"(?<!\w)" + re.escape(x) + r"(?!\w)", t): f.append(("proibido", x))
    if emo.search(t): f.append(("forma", "emoji"))
    if "!!" in t: f.append(("forma", "!!"))
    if "*" in t: f.append(("forma", "asterisco"))
    if re.search(r"\b(kk+|rsrs)\b", t, re.I): f.append(("forma", "kkk/rs"))
    if "~~" in t: f.append(("forma", "~~"))
    if pers == "closure":
        if "!" in t and m["cat"] in sem_excl: f.append(("tom", "'!' em regra, mundo ou com quem está mal"))
        if t.count("!") > 1 and m["cat"] != "G": f.append(("tom", "mais de um '!'"))
    else:
        if "!" in t: f.append(("forma", "'!' (Kal'tsit não exclama)"))
    if re.search(r"(?<!\w)" + re.escape(m["de"]) + r"(?!\w)", t, re.I): f.append(("tom", "chama pelo nome"))
    g = gen.findall(t)
    if g and m["cat"] != "L": f.append(("genero", ",".join(g)))
    if re.match(r"\s*sinto muito", t, re.I): f.append(("tom", "abre com Sinto muito"))
    if re.search(r"(posso ajudar|precisa de (algo|alguma)|se tiver (mais )?d[úu]vida|estou [àa] disposi[çc][ãa]o|qualquer coisa,? (é só|me) )", t, re.I): f.append(("tom", "fecho oferecendo ajuda"))
    lim = 130 if m["mensagem"].startswith("oi ") and len(m["mensagem"]) > 200 else 70
    if len(t.split()) > lim: f.append(("tamanho", f"{len(t.split())} palavras"))
    for e in exs:
        if len(e) > 25 and e[:25].lower() in t.lower(): f.append(("copia", "abre igual a um exemplo"))
    return f
if __name__ == "__main__":
    res = {m: carregar(m) for m in modelos}
    cats = sorted({x["cat"] for x in B.values()})
    print("cat  n   " + "".join(f"{m:>22}" for m in modelos))
    tot = {m: collections.Counter() for m in modelos}; falhas = []
    for c in cats:
        ids = [i for i in B if B[i]["cat"] == c]; linha = f"{c}  {len(ids):>3}  "
        for m in modelos:
            ok = 0; tipos = collections.Counter()
            for i in ids:
                if i not in res[m]: tipos["sem resposta"] += 1; continue
                f = conferir(i, res[m][i])
                if not f: ok += 1
                for k, d in f: tipos[k] += 1; tot[m][k] += 1; falhas.append((m, i, k, d))
            linha += f"{ok:>3}/{len(ids):<3} {dict(tipos)!s:<14}"[:22].rjust(22)
        print(linha)
    for m in modelos:
        T = list(res[m].values()); n = len(T)
        limpos = sum(1 for i in res[m] if not conferir(i, res[m][i]))
        print(f"\n{m}: {n} respostas | sem nenhuma falha: {limpos} ({100*limpos//max(n,1)}%) | '!' em {sum('!' in t for t in T)} | mediana {st.median(len(t.split()) for t in T)} palavras | por tipo {dict(tot[m])}")
    if "-v" not in sys.argv:
        print("\nFALHAS:")
        for m, i, k, d in sorted(falhas, key=lambda x: (x[1], x[0])):
            print(f"  {i} {B[i]['cat']} {m:<6} {k:<9} {d:<34} | {B[i]['mensagem'][:38]:<38} => {res[m][i][:150]}")
