"""Conversa autogerada conduzida por um agente (quando não há cota de API): o agente faz o usuário pela ficha e a
personagem pelo prompt, e este script monta cada turno igual à página e guarda tudo no formato do simular.py.
    python3 conversa_cli.py iniciar <arquivo.json> --pers clo --sistema X --lembrete Y --ficha F [--semente 1] [--aviso-antigo] [--pagina P.html]
    (com --pagina, cada turno é montado pelo JS da própria página, via pagina_turno.js; sem ela, pelo contexto.py)
    python3 conversa_cli.py usuario <arquivo.json>   < mensagem   (imprime o que a personagem recebe neste turno)
    python3 conversa_cli.py bot <arquivo.json>       < resposta   (grava e diz o próximo turno e a fala fixa, se houver)"""
import argparse, json, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contexto as C
FICHAS = {f["id"]: f for f in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fichas.json"), encoding="utf-8"))}

def hora(d, n):
    hh, mm = map(int, d["hora_inicio"].split(":")); mm += 2 * (n - 1)
    return f"{(hh + mm // 60) % 24:02d}:{mm % 60:02d}"

def proximo(d):
    n = len(d["turnos"]) + 1; F = FICHAS[d["ficha"]]
    fixa = F.get("roteiro", {}).get(str(n))
    return n, fixa

cmd, arq = sys.argv[1], sys.argv[2]
if cmd == "iniciar":
    ap = argparse.ArgumentParser(); ap.add_argument("--pers"); ap.add_argument("--sistema"); ap.add_argument("--lembrete"); ap.add_argument("--ficha")
    ap.add_argument("--semente", type=int, default=1); ap.add_argument("--aviso-antigo", action="store_true"); ap.add_argument("--pagina")
    a = ap.parse_args(sys.argv[3:]); F = FICHAS[a.ficha]
    random.seed(a.semente * 7919 + sum(map(ord, a.ficha)))
    dentro = ["22:40", "23:55", "01:20", "03:10"] if a.pers == "clo" else ["10:30", "14:15", "16:40", "19:05"]
    fora = ["14:15", "16:40"] if a.pers == "clo" else ["23:55", "02:10"]
    d = {"pers": a.pers, "ficha": a.ficha, "semente": a.semente, "sistema": a.sistema, "lembrete": a.lembrete, "modelo": "agente",
         "aviso_antigo": a.aviso_antigo, "pagina": os.path.abspath(a.pagina) if a.pagina else None, "hora_inicio": random.choice(fora if F.get("fora") else dentro), "assuntos": F.get("assuntos", []), "turnos": [], "pendente": None}
    json.dump(d, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n, fixa = proximo(d)
    print(f"Conversa criada. Você vai conversar com a {C.NOME[a.pers]} como {F['nome']}.\nFICHA DO USUÁRIO: {F['ficha']}\n"
          f"PROMPT DA PERSONAGEM: {os.path.join(C.R, 'dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos', a.sistema)}\n"
          f"Turno 1{': fala fixa -> ' + fixa if fixa else ''}")
    sys.exit()
d = json.load(open(arq, encoding="utf-8"))
txt = sys.stdin.read().strip()
if not txt: sys.exit("texto vazio")
if cmd == "usuario":
    n, fixa = proximo(d)
    if fixa and txt != fixa: print(f"(aviso: o turno {n} tinha fala fixa; usei a fala fixa)"); txt = fixa
    hist = [x for t in d["turnos"] for x in ({"de": "user", "texto": t["usuario"]}, {"de": "bot", "texto": t["resposta"]})]
    F = FICHAS[d["ficha"]]
    if d.get("pagina"):
        ent = {"pers": d["pers"], "hora": hora(d, n), "nome": F["nome"], "pron": F.get("pron", ""), "msg": txt, "hist": hist}
        r = json.loads(subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pagina_turno.js"), d["pagina"]],
                                      input=json.dumps(ent, ensure_ascii=False), capture_output=True, text=True, check=True).stdout)
        recebe, ativ = r["ultimo"], r["ativadas"]
        avis = recebe[recebe.index("[Fora do plantão"):] if "[Fora do plantão" in recebe else ""
    else:
        ctx, estado, avis, ativ = C.turno(d["pers"], hora(d, n), F["nome"], txt, hist, F.get("pron", ""), d["aviso_antigo"])
        lem = open(os.path.join(C.R, "dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos", d["lembrete"]), encoding="utf-8").read().strip()
        recebe = f"[Contexto ativado]\n{ctx}\n\n{estado}\n\n[Mensagem]\n{F['nome']}: {txt}\n\n{lem}{avis}"
    d["pendente"] = {"n": n, "hora": hora(d, n), "usuario": txt, "fixa": bool(fixa), "ativadas": ativ, "aviso": avis.strip()}
    json.dump(d, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"=== O QUE A {C.NOME[d['pers']].upper()} RECEBE NO TURNO {n} (depois do prompt e do histórico) ===\n{recebe}")
elif cmd == "bot":
    if not d.get("pendente"): sys.exit("mande a fala do usuário antes")
    t = d.pop("pendente"); t["resposta"] = txt; d["turnos"].append(t); d["pendente"] = None
    json.dump(d, open(arq, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n, fixa = proximo(d)
    print(f"Gravado turno {t['n']}. Próximo: turno {n}{': fala fixa -> ' + fixa if fixa else ''}")
