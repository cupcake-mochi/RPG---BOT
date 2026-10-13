import json, os, sys, time, urllib.request, urllib.error
# uso: python3 gemini_bateria.py <pasta> <bateria.json> <saida.json> <modelo> [lorebook]
# a chave vem de GEMINI_API_KEY ou do .env na raiz do Closure. Com "lorebook", o contexto de lore
# sai do lorebook.json acionado pela mensagem (o trecho do livro da bateria é mantido).
# Pra outra personagem: SISTEMA=<arquivo do prompt na pasta> e CARD=<caminho do card.json> no ambiente
# (padrão: sistema_v7.txt e o card da Kal'tsit).
pasta, bat, saida, modelo = sys.argv[1:5]
usar_lb = len(sys.argv) > 5 and sys.argv[5] == "lorebook"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re
from ativar_lorebook import ativar
key = os.environ.get("GEMINI_API_KEY") or dict(l.strip().split("=",1) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")) if "=" in l)["GEMINI_API_KEY"]
sistema = open(os.path.join(pasta, os.environ.get("SISTEMA", "sistema_v7.txt"))).read()
card = json.load(open(os.environ.get("CARD") or os.path.join(pasta, "../../card.json")))["data"]
lembrete = card["post_history_instructions"]
B = json.load(open(os.path.join(pasta, bat)))
out_path = os.path.join(pasta, saida)
R = json.load(open(out_path)) if os.path.exists(out_path) else []
feitos = {r["id"] for r in R}

def contexto(m):
    if not usar_lb:
        return m["contexto"]
    livro = [b for b in re.split(r"\n\n(?=\[)", m["contexto"]) if b.startswith("[Livro")]
    nomes, lore = ativar(m["mensagem"])
    m["ativadas"] = nomes
    return "\n\n".join([lore] + livro)

def chamar(m):
    body = {
        "system_instruction": {"parts": [{"text": sistema + "\n\nContexto ativado:\n" + contexto(m)}]},
        "contents": [{"role": "user", "parts": [{"text": f'{m["de"]}: {m["mensagem"]}\n\n{lembrete}'}]}],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 2048},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"] if not p.get("thought")).strip()

for m in B:
    if m["id"] in feitos:
        continue
    for tent in range(4):
        try:
            t = chamar(m); break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            print("HTTP", e.code, m["id"], msg[:200].replace("\n", " "), flush=True)
            if e.code == 429 and "PerDay" in msg:
                json.dump(R, open(out_path, "w"), ensure_ascii=False, indent=1); sys.exit("cota diária")
            time.sleep(20 * (tent + 1))
    else:
        continue
    R.append({"id": m["id"], "resposta": t, "ativadas": m.get("ativadas")})
    json.dump(R, open(out_path, "w"), ensure_ascii=False, indent=1)
    print(m["id"], len(t.split()), "palavras", flush=True)
    time.sleep(4)
print("feito", len(R))
