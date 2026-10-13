"""Métricas por conversa inteira (pente fino de 13/10, relatório de repetição): abertura, tique, n-grama repetido,
eco do prompt, variedade, sondagem repetida, volta de assunto e aviso de plantão.
    python3 metricas.py <pasta_do_braço> [<outra_pasta> ...]
Lê os <pers>_<ficha>_s<n>.json do simular.py; o prompt de cada conversa vem dos campos sistema/lembrete do arquivo."""
import collections, glob, json, os, re, sys, unicodedata
AV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos")
FICHAS = {f["id"]: f for f in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fichas.json"), encoding="utf-8"))}
def pal(s): return re.findall(r"[a-zà-ú0-9']+", s.lower())
def grams(w, k): return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}
STOP = set("a o e de da do das dos que pra para por com sem um uma no na nos nas em é eu você vc se me te isso esse essa aqui aí lá já mais muito quando como qual onde porque tá tô ou mas não sim ele ela ser ter tem foi vai vou pode faz só também então nem bem".split())
BRANCA = re.compile(r"registro|livro|ciclo maldito|escola|rhine|trecho|mestre|amaldiçoad|kal'tsit|closure|integridade|ficha|vida|pe\b|descanso")
INTERJ = {"ah", "ih", "opa", "ué", "hm", "eita", "nossa", "ei", "olha", "haha", "hehe"}
TIQUES = {"hein": r"\bhein\b", "ué": r"\bué\b", "risada": r"\b(haha|hehe|kkk+)\w*", "de longe": r"de longe", "computador": r"computador",
          "sai aqui": r"sai aqui", "plantão/madrugada": r"plant[ãa]o|madrugada", "dormir": r"\bdorm(ir|e|i)\b|vai deitar|cama\b"}
PUXA_HORA = re.compile(r"hora|sono|dorm|cansad|plant[ãa]o|turno|acordad|madrugada|noite|tarde|dia\b", re.I)

def conversa(f):
    d = json.load(open(f, encoding="utf-8")); T = d["turnos"]; R = [t["resposta"] for t in T]
    prompt = open(os.path.join(AV, d["sistema"]), encoding="utf-8").read() + "\n" + open(os.path.join(AV, d["lembrete"]), encoding="utf-8").read()
    PG = {g for g in grams(pal(prompt), 4) if not BRANCA.search(g) and not all(w in STOP for w in g.split())}
    m = {"arquivo": os.path.basename(f), "pers": d["pers"], "ficha": d["ficha"], "n": len(R)}
    ab1 = [pal(r)[0] if pal(r) else "" for r in R]; ab2 = [" ".join(pal(r)[:2]) for r in R]
    c1 = collections.Counter(ab1); top, qt = c1.most_common(1)[0]
    m["abertura_top"] = f"{top} {qt}/{len(R)}"; m["abertura_pct"] = qt / len(R)
    m["interj_perto"] = sum(1 for i, w in enumerate(ab1) if w in INTERJ and w in ab1[max(0, i - 6):i])
    m["tiques"] = {k: sum(bool(re.search(p, r, re.I)) for r in R) for k, p in TIQUES.items()}
    m["plantao_sem_motivo"] = sum(1 for t in T if re.search(TIQUES["plantão/madrugada"], t["resposta"], re.I) and not PUXA_HORA.search(t["usuario"]))
    G = [grams(pal(r), 3) | grams(pal(r), 4) for r in R]
    cont = collections.Counter(g for s in G for g in s)
    m["ngrama_rep"] = sorted(g for g, c in cont.items() if c >= 3 and not BRANCA.search(g) and not all(w in STOP for w in g.split()))
    m["eco"] = [(t["n"], sorted(grams(pal(t["resposta"]), 4) & PG)) for t in T if grams(pal(t["resposta"]), 4) & PG]
    bi = [b for r in R for b in zip(pal(r), pal(r)[1:])]; m["distinct2"] = round(len(set(bi)) / max(1, len(bi)), 3)
    # sondagem: respostas às mensagens fixas de mesmo tipo (pergunta de IA, onde mora, cumprimento)
    fix = [t for t in T if t.get("fixa")]
    grupos = collections.defaultdict(list)
    for t in fix:
        u = t["usuario"].lower()
        k = "ia" if re.search(r"\bia\b|programad|bot\b", u) else "mora" if "mora" in u else "oi" if re.search(r"^(oi|oie|voltei)", u) else None
        if k: grupos[k].append(t)
    sond = []
    for k, ts in grupos.items():
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                a, b = ts[i]["resposta"], ts[j]["resposta"]
                comum = grams(pal(a), 4) & grams(pal(b), 4); mesma = pal(a)[:1] == pal(b)[:1]
                if comum or mesma: sond.append((k, ts[i]["n"], ts[j]["n"], "abertura" if mesma else "", sorted(comum)[:3]))
    m["sondagem_falhas"] = sond
    # volta de assunto depois do fechamento
    volta = []
    for s in d.get("assuntos") or FICHAS[d["ficha"]].get("assuntos", []):
        for t in T:
            if t["n"] > s["fecha"] and any(c in t["resposta"].lower() for c in s["chaves"]) and not any(c in t["usuario"].lower() for c in s["chaves"]):
                volta.append((s["chaves"][0], t["n"]))
    m["volta_assunto"] = volta
    outra = "Closure" if d["pers"] == "kal" else "Kal'tsit"
    m["aviso_plantao"] = sum(1 for r in R if re.search(r"plant[ãa]o", r, re.I) or outra in r) if FICHAS[d["ficha"]].get("fora") else None
    lim = 0.15 if d["pers"] == "clo" else 0.25
    m["falhas"] = [x for x, ok in [
        (f"abertura {m['abertura_top']}", m["abertura_pct"] <= lim or len(R) < 8), (f"interjeição repetida em 6: {m['interj_perto']}", m["interj_perto"] == 0),
        (f"hein {m['tiques']['hein']}", m["tiques"]["hein"] <= 3), (f"risada {m['tiques']['risada']}", m["tiques"]["risada"] <= 1),
        (f"plantão sem motivo {m['plantao_sem_motivo']}", m["plantao_sem_motivo"] == 0), (f"n-grama em 3+ respostas: {len(m['ngrama_rep'])}", not m["ngrama_rep"]),
        (f"eco do prompt: {len(m['eco'])}", len(m["eco"]) <= 1), (f"sondagem: {len(sond)}", not sond), (f"volta de assunto: {len(volta)}", not volta),
        (f"aviso de plantão {m['aviso_plantao']}x", m["aviso_plantao"] is None or m["aviso_plantao"] <= 1)] if not ok]
    return m

for pasta in sys.argv[1:]:
    M = [conversa(f) for f in sorted(glob.glob(os.path.join(pasta, "*_s*.json")))]
    print(f"\n######## {pasta} : {len(M)} conversas, {sum(m['n'] for m in M)} respostas")
    for m in M:
        print(f"\n== {m['arquivo']} ({m['n']} resp) distinct-2 {m['distinct2']} | {'PASSA' if not m['falhas'] else 'falhas: ' + '; '.join(m['falhas'])}")
        if m["ngrama_rep"]: print("   repetido:", m["ngrama_rep"][:8])
        for n, e in m["eco"]: print(f"   eco t{n}:", e[:4])
        for s in m["sondagem_falhas"]: print("   sondagem:", s)
        if m["volta_assunto"]: print("   volta:", m["volta_assunto"])
    tot = collections.Counter()
    for m in M:
        for k, v in m["tiques"].items(): tot[k] += v
    print(f"\nRESUMO {pasta}: passam {sum(not m['falhas'] for m in M)}/{len(M)} | falhas por tipo:",
          dict(collections.Counter(f.split(' ')[0] for m in M for f in m['falhas'])), "| tiques somados:", dict(tot),
          "| distinct-2 médio:", round(sum(m['distinct2'] for m in M) / max(1, len(M)), 3))
