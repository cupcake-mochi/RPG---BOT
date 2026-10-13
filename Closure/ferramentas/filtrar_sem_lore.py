"""Gera o banco "respostas sem lore": falas EN em que a personagem responde a outra pessoa e a fala dela
não tem nome próprio nem termo de Arknights. Reescrito em 12/10/2026 a partir da descrição do filtro v2
no dados/corpus_kaltsit/LEIA-ME.md (o script original não foi salvo).

    python3 ferramentas/filtrar_sem_lore.py --corpus dados/corpus_closure/historia_en_US.jsonl \
        --nome Closure --card dados/personagem/closure/card.json --falantes dados/falantes_historia_en_US.csv \
        --loja dados/corpus_closure/loja_en_US.json --saida dados/corpus_closure/respostas_sem_lore_en.jsonl

Diferenças pro banco da Kal'tsit (881): fala só de pontuação ("......") fica de fora; resposta cujo gatilho tem
nome continua no banco, marcada em antes_tem_nome (lá, gatilho com maiúscula no meio da frase saía); as falas
da Loja entram com fonte "loja" e sem gatilho. Rodado no corpus da Kal'tsit sem essas diferenças, recupera
846 das 881.

O filtro é automático: revisar cada fala antes de usar."""
import argparse, json, re

# palavras que começam frase ou aparecem em maiúscula sem serem nome próprio
COMUNS = set("""i i'm i'll i've i'd ok okay mr mrs ms dr sir ma'am madam miss god gods""".split())
# tags de falante que são palavra comum do inglês: não viram nome a barrar
PALAVRAS = set("""the voice female male young old man woman girl boy child person people mysterious injured calm angry tired
everyone both all other others radio broadcast intercom communicator staff worker soldier guard driver citizen resident
villager merchant customer student teacher mother father sister brother leader captain member speaker announcer reporter
technician engineer researcher messenger mercenary elder unknown black white red blue green tall short little big team
squad scout and with from that this what who how why when where yes not you your they them his her she him our out one two
three four five six first second third new long lost last next same just very well good bad right left back down over
under after before here there now then still even also only more most some any each every many much few own
doctor officer medic nurse patient kid kids lady ladies gentleman boss chief master mister madam sir king queen prince
princess lord knight priest hunter fighter warrior sniper caster defender vanguard specialist supporter operator
operators machine robot drone system program computer terminal door phone screen noise sound shadow figure crowd
group passerby stranger traveler visitor guest waiter cook chef clerk shopkeeper owner manager director assistant
secretary agent police thug bandit thief pirate sailor farmer miner smith tailor singer dancer actor artist writer
hey wait look come let get got take make say tell see know think want need help stop run hold keep give find
day night time year home house room city town street world life death love hope fear war peace fire water wind
ice snow rain sun moon star sky sea land stone iron steel gold silver light dark""".split())

def termos_do_card(card):
    d = json.load(open(card, encoding="utf-8"))["data"]
    return list(d["extensions"]["closure_lab"]["termos_proibidos"])

def frases(t):
    t = re.sub(r"\b(Dr|Mr|Mrs|Ms|Prof|St)\.\s+", r"\1 ", t)
    return [f for f in re.split(r"(?<=[.!?…])\s+|\s+—\s*|\s*\.\.\.\s*", t) if f]

def tem_maiuscula_interna(t):
    """nome próprio pelo critério da v1: palavra em maiúscula que não abre a frase."""
    for f in frases(t):
        ws = re.findall(r"[A-Za-z0-9'’\-]+", f)
        for w in ws[1:]:
            if w[0].isupper() and w.lower() not in COMUNS and not w.isupper():
                return w
            if w.isupper() and len(w) > 1 and w.lower() not in COMUNS and re.search(r"\d", w):
                return w
    return None

def casa(lista, t):
    # nome próprio casa com a maiúscula; só termo todo em minúscula casa sem olhar caixa
    for x in lista:
        if re.search(r"(?<!\w)" + re.escape(x) + r"(?!\w)", t, re.I if x.islower() else 0):
            return x
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True); ap.add_argument("--nome", action="append", required=True)
    ap.add_argument("--card", required=True); ap.add_argument("--saida")
    ap.add_argument("--extra", action="append", default=[], help="termo a mais pra barrar")
    ap.add_argument("--falantes", help="csv de tags de falante do jogo: vira lista de nomes a barrar")
    ap.add_argument("--loja", help="json das falas da Loja, pra entrar no mesmo banco")
    a = ap.parse_args()
    C = [json.loads(l) for l in open(a.corpus, encoding="utf-8") if l.strip()]
    R = [c for c in C if c.get("antes") and c["antes"]["quem"] not in a.nome]
    # nomes de quem fala com ela, e cada pedaço em maiúscula das tags compostas
    tags = {c["antes"]["quem"] for c in R}
    nomes = set()
    for t in tags:
        if t.strip("?"): nomes.add(t)
        for p in re.findall(r"[A-Z][A-Za-z0-9'’\-]{2,}", t):
            if p.lower() not in COMUNS: nomes.add(p)
    genericos = {"The","Voice","Female","Male","Young","Old","Man","Woman","Girl","Boy","Child","Person","People",
                 "Mysterious","Injured","Calm","Angry","Tired","Everyone","Both","All","Other","Others","Radio","Broadcast",
                 "Intercom","Communicator","Staff","Worker","Soldier","Guard","Driver","Citizen","Resident","Villager",
                 "Merchant","Customer","Student","Teacher","Mother","Father","Sister","Brother","Leader","Captain","Member",
                 "Speaker","Announcer","Reporter","Technician","Engineer","Researcher","Messenger","Mercenary","Elder",
                 "Unknown","Black","White","Red","Blue","Green","Tall","Short","Little","Big","Team","Squad","Scout"}
    if a.falantes:
        import csv
        for linha in csv.DictReader(open(a.falantes, encoding="utf-8")):
            for p in re.findall(r"[A-Z][A-Za-z0-9'’\-]{2,}", linha["nome_na_tag"]):
                if p.lower() not in COMUNS: nomes.add(p)
    nomes = {n for n in nomes if n not in genericos and n.lower() not in PALAVRAS}
    barrar = sorted(nomes | set(termos_do_card(a.card)) | set(a.nome) | set(a.extra) | {"{@", "Dr."}, key=len, reverse=True)
    out, motivos = [], {}
    for c in R:
        f = c["fala"]
        if not re.search(r"[A-Za-z]{2}", f):
            motivos["(sem palavra)"] = motivos.get("(sem palavra)", 0) + 1; continue
        m = casa(barrar, f) or tem_maiuscula_interna(f)
        if m:
            motivos[m] = motivos.get(m, 0) + 1; continue
        antes = c["antes"]["fala"]
        out.append({"fonte": "historia", "antes": antes, "quem": c["antes"]["quem"], "fala": f, "arquivo": c["arquivo"],
                    "linha": c["linha"], "antes_tem_nome": bool(casa(barrar, antes) or tem_maiuscula_interna(antes))})
    n_hist = len(out)
    if a.loja:
        L = json.load(open(a.loja, encoding="utf-8"))
        for i, f in enumerate([x["fala"] for x in L["balcao"]] + L["vitrine"]):
            m = casa(barrar, f) or tem_maiuscula_interna(f)
            if m:
                motivos[m] = motivos.get(m, 0) + 1; continue
            out.append({"fonte": "loja", "antes": None, "quem": None, "fala": f, "arquivo": "excel/shop_client_table.json",
                        "linha": i, "antes_tem_nome": False})
        print(f"loja: {len(L['balcao']) + len(L['vitrine'])} falas, passam {len(out) - n_hist}")
    print(f"falas {len(C)} | respostas a outra pessoa {len(R)} | tags de quem fala com ela {len(tags)} | "
          f"passam {n_hist} | com nome só no gatilho {sum(o['antes_tem_nome'] for o in out)}")
    print("mais barrados:", sorted(motivos.items(), key=lambda x: -x[1])[:25])
    if a.saida:
        with open(a.saida, "w", encoding="utf-8") as fh:
            for o in out: fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    return out

if __name__ == "__main__":
    main()
