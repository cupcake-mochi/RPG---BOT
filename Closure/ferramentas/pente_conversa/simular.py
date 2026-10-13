"""Conversa autogerada: um usuário simulado (Gemini, com a ficha) conversa com a personagem (Gemini, prompt da versão).
    python3 simular.py --pers clo --sistema sistema_closure_v20.txt --lembrete lembrete_closure_v20.txt --ficha testador --semente 1 --saida pasta/
Os arquivos de sistema e lembrete são procurados na pasta de avaliação. --aviso-antigo monta o turno como a página fazia antes.
Saída: <saida>/<pers>_<ficha>_s<semente>.json com os turnos e o que entrou no contexto."""
import argparse, json, os, random, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contexto as C
AV = os.path.join(C.R, "dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos")
KEY = dict(l.strip().split("=", 1) for l in open(os.path.join(C.R, ".env")) if "=" in l)["GEMINI_API_KEY"]

def gemini(modelo, sistema, contents, temp):
    body = {"system_instruction": {"parts": [{"text": sistema}]}, "contents": contents,
            "generationConfig": {"temperature": temp, "maxOutputTokens": 2048}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    for tent in range(40):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": KEY})
            with urllib.request.urlopen(req, timeout=120) as r: d = json.load(r)
            parts = d["candidates"][0].get("content", {}).get("parts", [])
            txt = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            if txt: return txt
        except urllib.error.HTTPError as e:
            msg = e.read()[:2000].decode(errors="replace")
            if e.code not in (429, 500, 503): raise RuntimeError(f"{e.code} {msg}")
            if e.code == 429 and ("PerDay" in msg or "free_tier" in msg): raise RuntimeError("cota: " + msg)
        except (urllib.error.URLError, TimeoutError, KeyError): pass
        time.sleep(min(120, 4 * 2 ** tent))
    raise RuntimeError("sem resposta depois de 40 tentativas")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pers", required=True); ap.add_argument("--sistema", required=True); ap.add_argument("--lembrete", required=True)
    ap.add_argument("--ficha", required=True); ap.add_argument("--semente", type=int, default=1); ap.add_argument("--turnos", type=int, default=24)
    ap.add_argument("--modelo", default=os.environ.get("MODELO", "gemini-3.5-flash")); ap.add_argument("--modelo-usuario", default=os.environ.get("MODELO_USUARIO", "gemini-3.5-flash"))
    ap.add_argument("--aviso-antigo", action="store_true"); ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    F = {f["id"]: f for f in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fichas.json"), encoding="utf-8"))}[a.ficha]
    random.seed(a.semente * 7919 + hash(a.ficha) % 1000)
    sistema = open(os.path.join(AV, a.sistema), encoding="utf-8").read()
    lembrete = open(os.path.join(AV, a.lembrete), encoding="utf-8").read().strip()
    # hora: dentro do turno da personagem, ou fora dele na ficha "fora"
    dentro = ["22:40", "23:55", "01:20", "03:10"] if a.pers == "clo" else ["10:30", "14:15", "16:40", "19:05"]
    fora = ["14:15", "16:40"] if a.pers == "clo" else ["23:55", "02:10"]
    h0 = random.choice(fora if F.get("fora") else dentro)
    nome, pron = F["nome"], F.get("pron", "")
    out_f = os.path.join(a.saida, f"{a.pers}_{a.ficha}_s{a.semente}.json")
    hist, reg = [], {"pers": a.pers, "ficha": a.ficha, "semente": a.semente, "sistema": a.sistema, "lembrete": a.lembrete,
                     "modelo": a.modelo, "aviso_antigo": a.aviso_antigo, "hora_inicio": h0, "assuntos": F.get("assuntos", []), "turnos": []}
    sim_sis = (F["ficha"] + f"\n\nVocê está num canal de Discord falando com a {C.NOME[a.pers]}, guia do servidor do RPG Ciclo Maldito. "
               "Escreva só a sua próxima mensagem, como gente escreve no Discord em português do Brasil: curta, informal, sem aspas em volta, "
               "sem narrar ação, às vezes sem pontuação. Reaja ao que ela acabou de dizer. Se uma frase dela soar montada, repetida ou robótica, "
               "comente ou pergunte sobre isso. Não seja educado demais e não termine a conversa.")
    for n in range(1, a.turnos + 1):
        hh, mm = map(int, h0.split(":")); mm += 2 * (n - 1); hora = f"{(hh + mm // 60) % 24:02d}:{mm % 60:02d}"
        fixa = F.get("roteiro", {}).get(str(n))
        if fixa: msg = fixa
        else:
            conv = [{"role": "user" if t["de"] == "bot" else "model", "parts": [{"text": t["texto"]}]} for t in hist[-16:]]
            if not conv: conv = [{"role": "user", "parts": [{"text": f"[Comece a conversa com a {C.NOME[a.pers]}.]"}]}]
            elif conv[0]["role"] == "model": conv.insert(0, {"role": "user", "parts": [{"text": "[início]"}]})
            msg = gemini(a.modelo_usuario, sim_sis, conv, 1.0).split("\n")[0].strip().strip('"')
        ctx, estado, avis, ativ = C.turno(a.pers, hora, nome, msg, hist, pron, a.aviso_antigo)
        contents = []
        for t in hist[-24:]:
            contents.append({"role": "user", "parts": [{"text": f"{nome}: {t['texto']}"}]} if t["de"] == "user" else {"role": "model", "parts": [{"text": t["texto"]}]})
        ultimo = f"[Contexto ativado]\n{ctx}\n\n{estado}\n\n[Mensagem]\n{nome}: {msg}\n\n{lembrete}{avis}"
        contents.append({"role": "user", "parts": [{"text": ultimo}]})
        resp = gemini(a.modelo, sistema, contents, 1.0)
        hist += [{"de": "user", "texto": msg}, {"de": "bot", "texto": resp}]
        reg["turnos"].append({"n": n, "hora": hora, "usuario": msg, "fixa": bool(fixa), "resposta": resp, "ativadas": ativ, "aviso": avis.strip()})
        json.dump(reg, open(out_f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{n:>2} {nome}: {msg[:70]}\n   {C.NOME[a.pers]}: {resp[:110]}", flush=True)

if __name__ == "__main__": main()
