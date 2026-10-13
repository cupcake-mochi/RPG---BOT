"""Conta marcas de voz de uma personagem no corpus de história (etapa 1).

Lê o JSONL gerado por `extrair_corpus.py` e imprime uma tabela em Markdown com:
tamanho de fala, pontuação ("!", "?", "~", reticências, travessão), risada e
interjeições, gíria, vocativos, palavras que voltam, campos de assunto e com quem
ela mais fala. Com `--raiz` e `--comparar`, mede as mesmas coisas pro elenco
direto dos roteiros, pra ter régua (ex.: "22% de '!' é muito ou pouco?").

Com `--zh`, mede as marcas do chinês (～, ！, 嘿嘿, 啦...) no corpus CN e, se
passar `--operadora`, nas falas de operadora do JSON.

Uso:
    python ferramentas/contar_voz.py --corpus dados/corpus_closure/historia_en_US.jsonl \
        --nome Closure --raiz <clone YoStar> --comparar "Kal'tsit" --comparar Amiya
    python ferramentas/contar_voz.py --corpus dados/corpus_closure/historia_zh_CN.jsonl \
        --nome 可露希尔 --zh --operadora dados/corpus_closure/operadora_zh_CN.json
    # amostra pra leitura humana (respostas a outra pessoa, espalhadas pelos arquivos):
    python ferramentas/contar_voz.py --corpus ... --nome Closure --amostra 100 --saida-amostra /tmp/a.txt

Só biblioteca padrão. Os padrões ficam no topo do arquivo pra serem conferidos.
"""

import argparse
import json
import random
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

# --- padrões EN ---------------------------------------------------------------
RISO = {
    "heh / heh heh": r"\bheh(?:[\s,.~-]+heh)*\b",
    "hehe / hehehe": r"\bhe(?:he)+h?\b",
    "eheh / ehehe": r"\beh(?:eh)+e?\b|\behe(?:he)+\b",
    "haha / ahaha": r"\ba?ha(?:ha)+h?\b",
    "hee hee / teehee": r"\b(?:tee)?hee(?:[\s-]*hee)*\b",
    "pfft / pff": r"\bpff+t?\b",
}
INTERJ = ["eh", "ehh", "uh", "uhh", "um", "umm", "hm", "hmm", "huh", "oh", "ah", "aah", "whoa",
          "wow", "ugh", "hmph", "ahem", "yep", "nope", "yay", "phew", "tch", "tsk", "ow", "waah",
          "wah", "argh", "aw", "aww", "geez", "jeez", "yikes", "ooh", "heh"]
GIRIA = ["gonna", "wanna", "gotta", "kinda", "sorta", "y'know", "ya", "'em", "dunno", "lemme",
         "don'tcha", "nah", "yeah", "yep", "nope", "okay", "ok", "alright", "dammit", "crap",
         "hell", "damn", "guys", "stuff", "thingy", "super", "totally", "seriously", "like"]
CAMPOS = {
    "dinheiro / loja": r"\b(LMD|money|pay|paid|paying|fee|fees|charg\w*|price\w*|discount\w*|buy\w*|"
                       r"sell\w*|sale|sales|purchas\w*|cost\w*|bill|bills|profit\w*|salary|budget|"
                       r"funds?|expensive|cheap|store|shop|refund\w*|deal)\b",
    "máquina / técnica": r"\b(drones?|machines?|equipment|terminals?|systems?|data|signals?|comms|"
                         r"program\w*|codes?|servers?|network\w*|hack\w*|repair\w*|fix\w*|"
                         r"engineer\w*|devices?|circuit\w*|firmware|power|battery|batteries|"
                         r"install\w*|upgrade\w*|robots?|tech\w*|calculat\w*|analy\w*)\b",
    "cansaço / trabalho / comida": r"\b(sleep\w*|tired|exhaust\w*|overtime|work\w*|break|rest|"
                                   r"snacks?|eat\w*|food|hungry|starv\w*|coffee|meal|nap|"
                                   r"headache|busy|lazy|vacation|holiday)\b",
    "auto-título (genius, Chief Engineer...)": r"genius|ever-reliable|Destroyer of the Kazdel|creator of Rhodes Island|"
                       r"Closure difference|Chief Engineer|head of Engineering|super chief",
    "provoca pela idade (old hag, as old as)": r"\bold (hag|lady|people|man|woman|geezer)\b|as old as|\bgrumpy\b",
    "pega no flagra / desculpa rápida": r"my bad|do over|it was a power outage|I didn't (do|break)|wasn't me|"
                       r"what do you mean I|just blurted|knee-jerked|no offense|simply an example",
    "vergonha (stop / don't say it)": r"\bstop[,!]|don't say it|don't you dare|don't record|shut up|blush",
    "autoelogio": r"\b(genius|ever-reliable|reliable|amazing|brilliant|the best|leave it to me|"
                  r"count on me|of course I can|impressive|clever|smart)\b",
}
ACRONIMOS = {"LMD", "PRTS", "OK", "ID", "AI", "OS", "CPU", "HR", "IT", "DJ", "TV", "II", "III", "IV",
             "THRM", "EX", "RHO", "I", "A", "W", "AU", "BSW", "PR", "SOS", "VIP"}
NAO_VOCATIVO = {"Well", "Yeah", "Wait", "Alright", "Hey", "No", "So", "Also", "Right", "Anyway",
                "Seriously", "Great", "Okay", "Look", "Come", "Fine", "Yes", "Then", "Now", "Still",
                "But", "Sure", "Listen", "Actually", "Honestly", "Besides", "Man", "And", "Oh well",
                "Thanks", "Sorry", "Good", "Huh", "Wow", "Fair", "Like", "See", "Ok", "OK", "Hold on",
                "Nah", "Nope", "Yep", "Please", "Hmm", "Why", "What", "Really", "Damn", "Dammit"}
VAZIAS = set("""a an the and or but if so to of in on at for with from by as is are was were be been
being am i you he she it we they me him her us them my your his its our their this that these those
what which who whom whose there here then than too very just not no yes do does did done have has had
can could will would shall should may might must don't i'm it's that's you're we're they're i'll
you'll i've can't won't didn't isn't aren't wasn't let's there's what's all any some one more much
about up out into over again also only even still now how why when where well oh ah uh eh hm hmm
huh um right okay ok yeah get got go going gonna like know think see said say really come back
""".split())


def palavras(texto):
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", texto)


def limpa(texto):
    return re.sub(r"<[^>]+>", "", texto)


def pct(n, total):
    return f"{100 * n / total:.1f}%" if total else "—"


def medir_en(falas, nome=None):
    """falas: lista de dicts no formato do corpus. Retorna dict de métricas."""
    textos = [limpa(x["fala"]) for x in falas]
    total = len(textos)
    tam = [len(palavras(t)) for t in textos]
    m = {"falas": total}
    if not total:
        return m
    tam_ord = sorted(tam)
    m["mediana"] = statistics.median(tam)
    m["media"] = round(statistics.mean(tam), 1)
    m["p90"] = tam_ord[int(0.9 * (total - 1))]
    m["curtas<=3"] = sum(1 for n in tam if n <= 3)
    m["só reticência"] = sum(1 for t in textos if re.fullmatch(r"[.…\s]+", t))
    m["!"] = sum(1 for t in textos if "!" in t)
    m["!!+"] = sum(1 for t in textos if re.search(r"!{2,}", t))
    m["?! / !?"] = sum(1 for t in textos if re.search(r"\?!|!\?", t))
    m["?"] = sum(1 for t in textos if "?" in t)
    m["~"] = sum(1 for t in textos if re.search(r"[~～]", t))
    m["reticências"] = sum(1 for t in textos if re.search(r"\.\.\.|…", t))
    m["travessão"] = sum(1 for t in textos if re.search(r"—|--", t))
    m["fala entre parênteses (pensamento)"] = sum(1 for t in textos if re.fullmatch(r"\s*\(.*\)\s*", t))
    m["gagueira (W-Why)"] = sum(1 for t in textos if re.search(r"\b([A-Za-z])-\1", t, re.I))
    m["letra esticada (sooo)"] = sum(1 for t in textos if re.search(r"([a-z])\1\1", t))
    m["palavra em CAIXA ALTA"] = sum(
        1 for t in textos
        if any(len(w) >= 2 and w.isupper() and w.strip("'-") not in ACRONIMOS
               for w in palavras(t)))
    for rotulo, p in RISO.items():
        r = re.compile(p, re.I)
        n = sum(1 for t in textos if r.search(t))
        m["riso: " + rotulo] = n
    m["riso (qualquer)"] = sum(1 for t in textos if any(re.search(p, t, re.I) for p in RISO.values()))
    m["'Heh heh~' exato"] = sum(1 for t in textos if re.search(r"heh heh~", t, re.I))
    inter = Counter()
    for t in textos:
        primeira = re.match(r"\W*([A-Za-z]+)", t)
        if primeira and primeira.group(1).lower() in INTERJ:
            inter[primeira.group(1).lower()] += 1
    m["abre com interjeição"] = sum(inter.values())
    m["_interj"] = inter
    gir = Counter()
    falas_giria = 0
    for t in textos:
        ws = [w.lower() for w in palavras(t)]
        achou = [g for g in GIRIA if g in ws]
        for g in achou:
            gir[g] += 1
        falas_giria += bool(achou)
    m["com gíria/informal"] = falas_giria
    m["_giria"] = gir
    m["contração"] = sum(1 for t in textos if re.search(r"\b\w+'(t|s|m|re|ll|ve|d)\b", t, re.I))
    m["forma sem contração (I do not, it is)"] = sum(
        1 for t in textos if re.search(r"\b(I do not|I will not|I am not|it is not|do not|cannot|I have not|we are not)\b", t))
    longas = sum(1 for t in textos for w in palavras(t) if len(w) >= 10)
    m["palavras 10+ letras (% das palavras)"] = round(100 * longas / max(1, sum(tam)), 1)
    for rotulo, p in CAMPOS.items():
        r = re.compile(p, re.I)
        m["campo: " + rotulo] = sum(1 for t in textos if r.search(t))
    m["Doctor/Doc"] = sum(1 for t in textos if re.search(r"\bDoc(tor)?\b", t))
    voc = Counter()
    # vocativo só conta se a palavra é nome de alguém que fala no corpus (ou Doctor/Doc)
    falantes = {x["antes"]["quem"] for x in falas if x.get("antes")} | {"Doctor", "Doc"}
    for t in textos:
        for mm in re.finditer(r"^([A-Z][\w'\-]+(?: [A-Z][\w'\-]+)?),\s", t):
            if mm.group(1) in falantes and mm.group(1) not in NAO_VOCATIVO:
                voc[mm.group(1)] += 1
        for mm in re.finditer(r",\s([A-Z][\w'\-]+(?: [A-Z][\w'\-]+)?)[.!?~…]+\s*$", t):
            if mm.group(1) in falantes and mm.group(1) not in NAO_VOCATIVO:
                voc[mm.group(1)] += 1
    m["_vocativo"] = voc
    m["vocativo (início ou fim)"] = sum(voc.values())
    pal = Counter(w.lower() for t in textos for w in palavras(t) if w.lower() not in VAZIAS and len(w) > 2)
    m["_palavras"] = pal
    grupos = Counter()
    excl = Counter()
    for x, t in zip(falas, textos):
        g = "história principal" if x["arquivo"].startswith("obt/main") else (
            "registros de operador" if x["arquivo"].startswith("obt/memory") else "eventos e outros")
        grupos[g] += 1
        excl[g] += "!" in t
    m["_excl_por_grupo"] = {g: (excl[g], grupos[g]) for g in grupos}
    if nome:
        resp = [x for x in falas if x["antes"] and x["antes"]["quem"] != nome]
        m["respostas a outra pessoa"] = len(resp)
        m["_quem_antes"] = Counter(x["antes"]["quem"] for x in resp)
        m["continua fala dela"] = sum(1 for x in falas if x["antes"] and x["antes"]["quem"] == nome)
    return m


ZH = {
    "～ / ~": r"[~～]",
    "！": r"[!！]",
    "？": r"[?？]",
    "……": r"……|\.\.\.",
    "——": r"——",
    "嘿嘿 / 嘿": r"嘿",
    "哈哈": r"哈哈",
    "呜 (choro/manha)": r"呜",
    "啦": r"啦",
    "嘛": r"嘛",
    "呢": r"呢",
    "哼": r"哼",
    "诶 / 欸 / 哎": r"[诶欸哎]",
    "哇": r"哇",
    "唔": r"唔",
    "咳 (ahem)": r"咳",
    "钱/龙门币/付费/收费": r"钱|龙门币|付费|收费|价|买|卖|折扣|采购",
}


def medir_zh(textos):
    total = len(textos)
    m = {"falas": total}
    if not total:
        return m
    tam = [len(re.sub(r"[\W_]", "", t)) for t in textos]
    m["caracteres, mediana"] = statistics.median(tam)
    for rot, p in ZH.items():
        r = re.compile(p)
        m[rot] = sum(1 for t in textos if r.search(t))
    return m


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def tabela_en(medidas, nomes):
    chaves = [k for k in medidas[nomes[0]] if not k.startswith("_")]
    linhas = ["| Medida | " + " | ".join(nomes) + " |", "| --- |" + " --- |" * len(nomes)]
    for k in chaves:
        cel = []
        for n in nomes:
            m = medidas[n]
            v = m.get(k, "—")
            if isinstance(v, int) and k not in ("falas", "p90", "mediana") and m.get("falas"):
                cel.append(f"{v} ({pct(v, m['falas'])})")
            else:
                cel.append(str(v))
        linhas.append(f"| {k} | " + " | ".join(cel) + " |")
    return "\n".join(linhas)


def amostra(falas, nome, n, seed):
    resp = [x for x in falas if x["antes"] and x["antes"]["quem"] != nome]
    por_arq = {}
    for x in resp:
        por_arq.setdefault(x["arquivo"], []).append(x)
    rnd = random.Random(seed)
    escolha = []
    arquivos = sorted(por_arq)
    while len(escolha) < min(n, len(resp)):
        for a in arquivos:
            if por_arq[a] and len(escolha) < n:
                escolha.append(por_arq[a].pop(rnd.randrange(len(por_arq[a]))))
    return escolha


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", required=True)
    p.add_argument("--nome", required=True, help="tag da personagem no corpus")
    p.add_argument("--zh", action="store_true")
    p.add_argument("--operadora", help="JSON de falas de operadora (zh)")
    p.add_argument("--raiz", help="clone do ArknightsGameData(_YoStar) pra comparar com o elenco")
    p.add_argument("--lang", default="en_US")
    p.add_argument("--comparar", action="append", default=[])
    p.add_argument("--amostra", type=int, default=0)
    p.add_argument("--saida-amostra")
    p.add_argument("--seed", type=int, default=12)
    a = p.parse_args()

    falas = carregar(a.corpus)
    if a.zh:
        print(f"## Marcas do chinês: {a.corpus}\n")
        res = {"história (todas)": medir_zh([x["fala"] for x in falas])}
        if a.operadora:
            op = json.load(open(a.operadora, encoding="utf-8"))
            res["operadora"] = medir_zh([x["fala"] for x in op["falas_de_operadora"]])
        nomes = list(res)
        print("| Marca | " + " | ".join(nomes) + " |\n| --- |" + " --- |" * len(nomes))
        for k in res[nomes[0]]:
            cel = []
            for n in nomes:
                v = res[n][k]
                cel.append(f"{v} ({pct(v, res[n]['falas'])})" if k not in ("falas", "caracteres, mediana") else str(v))
            print(f"| {k} | " + " | ".join(cel) + " |")
        return

    medidas = {a.nome: medir_en(falas, a.nome)}
    if a.raiz and a.comparar:
        sys.path.insert(0, str(Path(__file__).parent))
        from extrair_corpus import extrair
        for nome in a.comparar:
            medidas[nome] = medir_en(extrair(a.raiz, a.lang, {nome}), nome)
    nomes = list(medidas)
    print(f"## Contagem: {a.corpus}\n")
    print(tabela_en(medidas, nomes))
    m = medidas[a.nome]
    for chave, titulo, k in [("_interj", "Interjeição que abre a fala", 15),
                             ("_giria", "Gíria / informal (falas com a palavra)", 20),
                             ("_vocativo", "Vocativo (nome no começo ou no fim da fala)", 20),
                             ("_palavras", "Palavras que mais voltam (fora as vazias)", 40),
                             ("_quem_antes", "Quem falou antes, quando não é ela", 25)]:
        if chave in m:
            itens = ", ".join(f"{w} ({c})" for w, c in m[chave].most_common(k))
            print(f"\n**{titulo}:** {itens}")
    if "_excl_por_grupo" in m:
        itens = ", ".join(f"{g}: {e}/{n} ({pct(e, n)})" for g, (e, n) in m["_excl_por_grupo"].items())
        print(f"\n**Falas com '!' por tipo de cena:** {itens}")
    if a.amostra:
        esc = amostra(falas, a.nome, a.amostra, a.seed)
        destino = open(a.saida_amostra, "w", encoding="utf-8") if a.saida_amostra else sys.stdout
        for x in esc:
            destino.write(f"[{x['arquivo']}:{x['linha']}] {x['antes']['quem']}: {x['antes']['fala']}\n"
                          f"    >> {x['fala']}\n")


if __name__ == "__main__":
    main()
