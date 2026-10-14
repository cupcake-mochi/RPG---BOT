"""Monta cada turno igual à página de teste (ferramentas/pagina_teste/modelo.html): lorebook acionado pelas
duas últimas falas do usuário + a mensagem, bloco do livro (âncora dos termos + o que mais casa, só com cara de
regra), linha de estado, linha do Mizuki, aniversário e o aviso de fora do plantão uma vez só."""
import json, math, os, re, unicodedata
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
LORE = [e for e in json.load(open(f"{R}/dados/personagem/kaltsit/lorebook.json", encoding="utf-8"))["entries"].values() if not e["disable"]]
LIVRO = [json.loads(l) for l in open(f"{R}/dados/sistema/livro.jsonl", encoding="utf-8")]
NOME = {"kal": "Kal'tsit", "clo": "Closure"}
ANIV = {"clo": "[Aniversário: o seu é 10 de dezembro.]",
        "kal": "[Aniversário: você não diz a data do seu e não explica o motivo. Não fale de quem escolheu o dia nem de confirmar ou negar. "
               "Reaja curto, como a qualquer pergunta pessoal (\"Por que a pergunta?\", \"Isso não é importante.\", \"Talvez. Esse dia pode chegar.\"); "
               "a parabéns, só agradeça a intenção.]"}

def strip(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
def norm(s): s = s.lower(); return s + "\n" + strip(s)
def borda(k): return re.compile(r"(?<!\w)" + re.escape(k) + r"(?!\w)")
KRE = [[borda(k) for k in e["key"]] for e in LORE]

def ativar(texto):
    t, hit = norm(texto), []
    for e, ks in zip(LORE, KRE):
        if e["constant"]: continue
        n = max([len(k) for k, r in zip(e["key"], ks) if r.search(t)] or [0])
        if n: hit.append((n, e))
    hit.sort(key=lambda x: -x[0])
    sempre = [e for e in LORE if e["constant"]]
    mundo = [e for _, e in hit if e["group"] == "mundo"][:5]
    termos = [e for _, e in hit if e["group"] == "sistema"][:3]
    E = sempre + mundo + termos
    return [e["comment"] for e in E], "\n\n".join(e["content"] for e in E), termos

PARADA = set(("a o e de da do das dos que pra para por com sem um uma uns umas no na nos nas em é eu vc voce você tu se me te meu minha seu sua isso isto esse essa aqui ai aí la lá ja já mais menos muito pouco quando como qual quais quanto quantos onde porque pq tá ta to tô ou mas nao não sim ele ela eles elas ser ter tem tenho foi vai vou pode posso faz fazer "
              "closure kal kaltsit kal'tsit mizuki livro regra regras").split())
def tok(s):
    t = re.sub(r"(?<![a-z])(?:nv|nvl|niv|lv|lvl)\.?\s?(\d+)", r"nivel \1", strip(s.lower()))
    return [w[:-1] if len(w) > 4 and w.endswith("s") else w for w in re.findall(r"[a-z0-9]{3,}", t)]
REGRA = re.compile(r"(?<![a-z0-9])(d4|d6|d8|d10|d12|d20|rol\w*|dado\w*|teste\w*|dano|ataq\w*|defe\w*|bloque\w*|apar\w*|esquiv\w*|critic\w*|bonus|penalidade|turno\w*|rodada\w*|acao|acoes|reacao|movimento|passos?|alcance|descans\w*|vida|integridade|condic\w*|pericia\w*|atributo\w*|ficha\w*|nivel|niveis|nv\d*|nvl\d*|lv\d*|habilidade\w*|caminho\w*|trilha\w*|origem|origens|legado\w*|classe\w*|feitic\w*|grau|tecnica\w*|expansao|dominio|receptaculo|encarnado|maldic\w*|arma\w*|cobertura|regra\w*|livro|mestre|como funciona|o que e|o que acontece|da pra|pode usar|quanto\w*)(?![a-z0-9])")
DF, BT = {}, []
for b in LIVRO:
    c = {}
    for w in tok(b["titulo"] + " " + b["titulo"] + " " + " ".join(b.get("titulos") or []) + " " + b["texto"]): c[w] = c.get(w, 0) + 1
    for w in c: DF[w] = DF.get(w, 0) + 1
    BT.append(c)

CAMINHOS = ["bastiao", "vanguarda", "guia", "emanador", "evocador", "incursor"]
FAM = [b["ancora"].split("--")[0] for b in LIVRO]
FAMILIA_DE = {c: c for c in CAMINHOS}
for b, f in zip(LIVRO, FAM):
    t = tok(b["titulo"])
    if f in CAMINHOS and len(t) == 1 and t[0] not in FAMILIA_DE: FAMILIA_DE[t[0]] = f

def blocos_livro(texto, termos):
    out = []
    for e in termos:
        m = re.search(r"âncora ([\w-]+)", e["content"])
        if m:
            b = next((x for x in LIVRO if x["ancora"] == m.group(1)), None)
            if b and b not in out: out.append(b)
    q = list(dict.fromkeys(w for w in tok(texto) if w not in PARADA and w in DF))
    familia = {FAMILIA_DE[w] for w in q if w in FAMILIA_DE}
    if q and (termos or familia or REGRA.search(strip(texto.lower()))):
        nota = []
        for c, b, f in zip(BT, LIVRO, FAM):
            s = sum(math.log(1 + len(LIVRO) / DF[w]) * (1 + math.log(c[w])) for w in q if w in c)
            if familia and f not in familia: continue
            if familia and "progressao" in b["ancora"] and ({"nivel", "habilidade"} & set(q)): s += 5
            if s >= 6: nota.append((s, b))
        nota.sort(key=lambda x: -x[0])
        for _, b in nota[:1 if termos else 2]:
            if b not in out: out.append(b)
    return out[:2]

def de_turno(h): return "kal" if 9 <= h < 21 else "clo"

def turno(pers, hora, nome, msg, hist, pron="", aviso_antigo=False):
    """hist: lista de {"de": "user"|"bot", "texto"}. Devolve (texto do último turno, nomes ativados)."""
    recentes = " ".join([t["texto"] for t in hist if t["de"] == "user"][-2:])
    nomes, lore, termos = ativar(recentes + " " + msg)
    livro = blocos_livro(msg, termos)
    ctx = lore + "".join(f"\n\n[Livro, âncora {b['ancora']}]\n{b['texto']}" for b in livro)
    if nome.lower() == "mizuki": ctx += "\n\n[Servidor: quem fala é o Mizuki, ID 459030926928904230, que criou o mundo do Ciclo Maldito e o sistema.]"
    elif re.search("mizuki", msg, re.I): ctx += "\n\n[Servidor: o Mizuki criou o mundo do Ciclo Maldito e o sistema. Quem fala agora não é ele.]"
    if re.search("anivers[aá]rio", msg, re.I): ctx += "\n\n" + ANIV[pers]
    h = int(hora.split(":")[0]); dono = de_turno(h)
    if aviso_antigo:  # como a página era até a v0.20 (grupo de controle)
        plant = "plantão" if dono == pers else f"fora do plantão (a {NOME[dono]} está de plantão)"
        fora = "" if dono == pers else f"\n[Fora do plantão: responda o essencial. Que agora o plantão é da {NOME[dono]}, diga no máximo uma vez nesta conversa.]"
    else:
        plant = "plantão" if dono == pers else "fora do plantão"
        outra = NOME[dono]
        ja = any(t["de"] == "bot" and (re.search("plant[aã]o", t["texto"], re.I) or outra in t["texto"]) for t in hist)
        mundo = any(n.startswith("Mundo:") and n != "Mundo: premissa" for n in nomes)
        cabe = bool(termos) or mundo or bool(REGRA.search(strip(msg.lower()))) or bool(re.search(r"plant[aã]o|turno|hor[aá]rio|que horas|" + ("closure" if pers == "kal" else "kal"), msg, re.I))
        fora = "" if dono == pers else (f"\n[Fora do plantão: responda o essencial. Se fizer sentido para esta pergunta, diga que agora quem atende é a {outra}.]" if (cabe and not ja) else "\n[Fora do plantão: responda o essencial, sobre o que foi perguntado.]")
    estado = f"[Estado agora: {plant}; {hora} em Brasília; canal normal; carga 0.\nQuem fala: {nome} ({'pronomes: ' + pron if pron else 'pronomes não informados'}).]"
    return ctx, estado, fora, nomes + ["Livro: " + b["titulo"] for b in livro]
