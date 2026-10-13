"""Servidor do site de teste do bot (Kal'tsit e Closure) pros amigos do Mizuki.
Serve a página montada por montar.py e repassa as mensagens pro Gemini com a chave guardada aqui,
nunca no navegador. Só a biblioteca padrão do Python.

Variáveis de ambiente:
  GEMINI_API_KEY         obrigatória
  MISTRAL_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY   opcionais: liberam esses provedores nas filas abaixo
  SENHA                  código que os amigos digitam na página (obrigatória)
  SENHA_ADMIN            libera GET /api/conversas?admin=... pra baixar as conversas salvas
  FILA_RAPIDO, FILA_PADRAO  modelos de cada botão, em ordem, separados por vírgula, no formato provedor:modelo.
                         Se um esgota a cota, está fora do ar ou demora, o próximo responde. Itens de um
                         provedor sem chave são pulados. Cada modelo do Gemini grátis tem cota própria.
  LIMITE_HORA            mensagens por pessoa (IP) por hora (padrão: 40)
  LIMITE_DIA             mensagens no total por dia, horário de Brasília (padrão: 300)
  PASTA_CONVERSAS        onde as conversas ficam salvas (padrão: ./conversas)
  GITHUB_TOKEN           token com permissão de escrever no repositório GITHUB_REPO (padrão: cupcake-mochi/closure-conversas):
                         as conversas vão também, em texto, pra pasta conversas/ dele, porque o disco do Render
                         grátis apaga quando reinicia. O repositório tem que ser PRIVADO; se for público, não envia.
  PORT                   porta (padrão: 8000)
"""
import base64, json, os, re, threading, time, urllib.error, urllib.request
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(AQUI, "publico")
CHAVE = os.environ.get("GEMINI_API_KEY", "")
SENHA = os.environ.get("SENHA", "")
SENHA_ADMIN = os.environ.get("SENHA_ADMIN", "")
RAPIDO = "gemini:gemini-3.1-flash-lite,gemini:gemini-3.5-flash-lite,gemini:gemini-2.5-flash-lite,mistral:mistral-medium-latest"
PADRAO = "gemini:gemini-3.8-flash,gemini:gemini-3.5-flash,gemini:gemini-3-flash-preview,mistral:mistral-medium-latest," + RAPIDO
CHAVES = {"gemini": CHAVE, "mistral": os.environ.get("MISTRAL_API_KEY", ""), "groq": os.environ.get("GROQ_API_KEY", ""),
          "openrouter": os.environ.get("OPENROUTER_API_KEY", "")}
URL_OPENAI = {"mistral": "https://api.mistral.ai/v1/chat/completions", "groq": "https://api.groq.com/openai/v1/chat/completions",
              "openrouter": "https://openrouter.ai/api/v1/chat/completions"}


def fila(texto):
    itens = []
    for item in texto.split(","):
        prov, _, modelo = item.strip().partition(":")
        if modelo and CHAVES.get(prov) and (prov, modelo) not in itens:
            itens.append((prov, modelo))
    return itens


FILAS = {"quick": fila(os.environ.get("FILA_RAPIDO", RAPIDO)), "default": fila(os.environ.get("FILA_PADRAO", PADRAO))}
FILAS["complex"] = FILAS["default"]
ESPERA = 60  # segundos por tentativa; os Flash grátis às vezes ficam 2 minutos sem responder
esgotado = {}  # (provedor, modelo) -> instante até quando pular, depois de um 429
LIMITE_HORA = int(os.environ.get("LIMITE_HORA", "40"))
LIMITE_DIA = int(os.environ.get("LIMITE_DIA", "300"))
CONVERSAS = os.environ.get("PASTA_CONVERSAS", os.path.join(AQUI, "conversas"))
MAX_CARACTERES, MAX_MENSAGENS = 200_000, 60
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GH_REPO = os.environ.get("GITHUB_REPO", "cupcake-mochi/closure-conversas")
GH_API = os.environ.get("GITHUB_API", "https://api.github.com")
GH_INTERVALO = int(os.environ.get("GITHUB_INTERVALO", "90"))  # segundos entre envios; cada conversa muda a cada mensagem e não precisa de um commit por mensagem

INDEX = open(os.path.join(PUB, "index.html"), "rb").read()
PROMPTS = list(json.load(open(os.path.join(PUB, "prompts.json"), encoding="utf-8"))["prompts"].values())

trava = threading.Lock()
por_ip = defaultdict(deque)
dia = {"data": "", "n": 0}


def hoje_br():
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() - 3 * 3600))


def contar(ip):
    """Devolve None se pode mandar, ou o código do limite estourado."""
    agora = time.time()
    with trava:
        if dia["data"] != hoje_br():
            dia.update(data=hoje_br(), n=0)
        if dia["n"] >= LIMITE_DIA:
            return "limite_dia"
        q = por_ip[ip]
        while q and agora - q[0] > 3600:
            q.popleft()
        if len(q) >= LIMITE_HORA:
            return "limite_pessoa"
        q.append(agora)
        dia["n"] += 1
    return None


def valido(entrada):
    # só aceita a conversa que a própria página monta: primeira mensagem com um dos prompts de sistema do bot
    if not isinstance(entrada, list) or not 2 <= len(entrada) <= MAX_MENSAGENS:
        return False
    if any(not isinstance(m, dict) or m.get("role") not in ("user", "assistant") or not isinstance(m.get("content"), str) for m in entrada):
        return False
    if entrada[0]["role"] != "user" or entrada[-1]["role"] != "user":
        return False
    if sum(len(m["content"]) for m in entrada) > MAX_CARACTERES:
        return False
    return any(entrada[0]["content"].endswith(p) for p in PROMPTS)


class Falhou(Exception):
    def __init__(self, codigo, motivo):
        super().__init__(f"{codigo} {motivo}")
        self.codigo, self.motivo = codigo, motivo


def pedir(req):
    try:
        with urllib.request.urlopen(req, timeout=ESPERA) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise Falhou(e.code, e.read().decode(errors="replace")[:3000].replace("\n", " "))
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise Falhou("rede", str(e))


def gemini(modelo, entrada):
    corpo = {
        "system_instruction": {"parts": [{"text": entrada[0]["content"]}]},
        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in entrada[1:]],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 2048},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    d = pedir(urllib.request.Request(url, json.dumps(corpo).encode(), {"Content-Type": "application/json", "x-goog-api-key": CHAVE}))
    cand = (d.get("candidates") or [{}])[0]
    texto = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought")).strip()
    if not texto:
        motivo = cand.get("finishReason") or d.get("promptFeedback", {}).get("blockReason") or "vazio"
        raise Falhou("bloqueado" if motivo in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "OTHER") else "vazio", motivo)
    return texto, cand.get("finishReason") == "MAX_TOKENS"


def openai(prov, modelo, entrada):
    # Mistral, Groq e OpenRouter falam o formato de chat da OpenAI; a primeira mensagem vira o system
    msgs = [{"role": "system", "content": entrada[0]["content"]}] + [{"role": m["role"], "content": m["content"]} for m in entrada[1:]]
    corpo = {"model": modelo, "messages": msgs, "temperature": 0.8, "max_tokens": 2048}
    d = pedir(urllib.request.Request(URL_OPENAI[prov], json.dumps(corpo).encode(),
                                     {"Content-Type": "application/json", "Authorization": f"Bearer {CHAVES[prov]}"}))
    esc = (d.get("choices") or [{}])[0]
    texto = (esc.get("message", {}).get("content") or "").strip()
    if not texto:
        raise Falhou("bloqueado" if esc.get("finish_reason") == "content_filter" else "vazio", esc.get("finish_reason"))
    return texto, esc.get("finish_reason") == "length"


def responder_com_fila(entrada, tier):
    """Tenta cada modelo da fila do botão; devolve (resposta, None) ou (None, código de erro pra página)."""
    ultimo = "gemini"
    for prov, modelo in FILAS.get(tier) or FILAS["quick"]:
        if esgotado.get((prov, modelo), 0) > time.time():
            ultimo = "cota_gemini"
            continue
        try:
            texto, cortado = gemini(modelo, entrada) if prov == "gemini" else openai(prov, modelo, entrada)
            return {"text": texto, "truncated": cortado, "modelo": f"{prov}:{modelo}"}, None
        except Falhou as f:
            print("falhou", prov, modelo, f.codigo, str(f.motivo)[:200], flush=True)
            if f.codigo == "bloqueado":
                return None, "bloqueado"
            if f.codigo == 429:
                # cota diária volta à meia-noite do Pacífico; por minuto, logo. Pula esse modelo por um tempo.
                esgotado[(prov, modelo)] = time.time() + (3600 if "PerDay" in str(f.motivo) else 60)
                ultimo = "cota_gemini"
            else:
                ultimo = "gemini"
    return None, ultimo


# ---------- cópia das conversas no GitHub ----------
pendentes = set()
NOME = {"kal": "Kal'tsit", "clo": "Closure"}


def em_texto(c):
    linhas = [f"# Conversa {c['id']}", "",
              f"- Atualizada: {c.get('atualizada', '?')}",
              f"- Modelo: {'Rápido' if c.get('modelo') == 'quick' else 'Padrão'}",
              f"- Cards: {json.dumps(c.get('cards', {}), ensure_ascii=False)}", ""]
    estranhas = 0
    for t in c.get("turnos", []):
        quem = t.get("nome") or "alguém" if t.get("de") == "user" else NOME.get(t.get("pers"), "bot")
        modelo = f" _({t['modelo'].split(':', 1)[1]})_" if t.get("modelo") else ""
        linhas.append(f"**{quem}:**{modelo} {t.get('texto', '')}")
        if t.get("estranha"):
            estranhas += 1
            linhas.append(f"> ⚠️ ESTRANHA{': ' + t['nota'] if t.get('nota') else ''}")
        linhas.append("")
    linhas.insert(5, f"- Falas marcadas como estranhas: {estranhas}")
    return "\n".join(linhas)


def github(metodo, caminho, corpo=None):
    req = urllib.request.Request(f"{GH_API}/repos/{GH_REPO}/{caminho}", json.dumps(corpo).encode() if corpo else None,
                                 {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github+json", "User-Agent": "closure-teste"}, method=metodo)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def conferir_repo():
    # o que os amigos escrevem não pode cair num repositório público
    if not github("GET", "").get("private"):
        raise RuntimeError(f"{GH_REPO} é público; crie um repositório privado pras conversas")


def enviar_conversa(cid):
    c = json.load(open(os.path.join(CONVERSAS, cid + ".json"), encoding="utf-8"))
    caminho = f"contents/conversas/{cid}.md"
    corpo = {"message": f"Conversa {cid}",
             "content": base64.b64encode(em_texto(c).encode()).decode()}
    try:
        corpo["sha"] = github("GET", caminho)["sha"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    github("PUT", caminho, corpo)


def laco_github():
    try:
        conferir_repo()
    except Exception as e:
        print("GitHub indisponível, as conversas ficam só no servidor:", e, flush=True)
        return
    while True:
        time.sleep(GH_INTERVALO)
        with trava:
            fila = list(pendentes)
            pendentes.clear()
        for cid in fila:
            try:
                enviar_conversa(cid)
            except Exception as e:
                print("falhou ao mandar", cid, "pro GitHub:", e, flush=True)
                with trava:
                    pendentes.add(cid)


class Site(BaseHTTPRequestHandler):
    server_version = "closure-teste"

    def ip(self):
        return (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()

    def responder(self, codigo, dados, tipo="application/json; charset=utf-8"):
        corpo = dados if isinstance(dados, bytes) else json.dumps(dados, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, fmt, *args):
        # sem texto de mensagem nem senha no log, só a linha da requisição
        print(f"{self.log_date_time_string()} {self.command} {self.path.split('?')[0]} {args[1] if len(args) > 1 else ''}", flush=True)

    def do_GET(self):
        caminho = self.path.split("?")[0]
        if caminho in ("/", "/index.html"):
            return self.responder(200, INDEX, "text/html; charset=utf-8")
        if caminho == "/saude":
            return self.responder(200, {"ok": True})
        if caminho == "/api/conversas":
            q = dict(p.split("=", 1) for p in self.path.partition("?")[2].split("&") if "=" in p)
            if not SENHA_ADMIN or q.get("admin") != SENHA_ADMIN:
                return self.responder(401, {"erro": "senha"})
            todas = []
            if os.path.isdir(CONVERSAS):
                for n in sorted(os.listdir(CONVERSAS)):
                    todas.append(json.load(open(os.path.join(CONVERSAS, n), encoding="utf-8")))
            return self.responder(200, todas)
        self.responder(404, {"erro": "nao_achei"})

    def do_POST(self):
        try:
            tam = int(self.headers.get("Content-Length") or 0)
            if tam > 1_000_000:
                return self.responder(413, {"erro": "grande_demais"})
            corpo = json.loads(self.rfile.read(tam) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self.responder(400, {"erro": "pedido_invalido"})
        if corpo.get("senha") != SENHA:
            return self.responder(401, {"erro": "senha"})
        caminho = self.path.split("?")[0]
        if caminho == "/api/chat":
            return self.chat(corpo)
        if caminho == "/api/conversa":
            return self.conversa(corpo)
        self.responder(404, {"erro": "nao_achei"})

    def chat(self, corpo):
        entrada = corpo.get("input")
        if not valido(entrada):
            return self.responder(400, {"erro": "pedido_invalido"})
        limite = contar(self.ip())
        if limite:
            return self.responder(429, {"erro": limite})
        resp, erro = responder_com_fila(entrada, corpo.get("tier"))
        if erro:
            return self.responder(503 if erro == "cota_gemini" else 502, {"erro": erro})
        print("respondeu", resp["modelo"], flush=True)
        self.responder(200, resp)

    def conversa(self, corpo):
        cid = str(corpo.get("id") or "")
        if not re.fullmatch(r"[a-z0-9]{4,40}", cid) or not isinstance(corpo.get("dados"), dict):
            return self.responder(400, {"erro": "pedido_invalido"})
        os.makedirs(CONVERSAS, exist_ok=True)
        dados = dict(corpo["dados"], id=cid)
        with open(os.path.join(CONVERSAS, cid + ".json"), "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)
        if GH_TOKEN:
            with trava:
                pendentes.add(cid)
        self.responder(200, {"ok": True})


if __name__ == "__main__":
    if not CHAVE or not SENHA:
        raise SystemExit("Faltou GEMINI_API_KEY ou SENHA nas variáveis de ambiente.")
    if GH_TOKEN:
        threading.Thread(target=laco_github, daemon=True).start()
    porta = int(os.environ.get("PORT", "8000"))
    print(f"no ar na porta {porta} · {LIMITE_HORA}/h por pessoa, {LIMITE_DIA}/dia", flush=True)
    for nome in ("quick", "default"):
        print(" ", "Rápido:" if nome == "quick" else "Padrão:", ", ".join(f"{p}:{m}" for p, m in FILAS[nome]), flush=True)
    ThreadingHTTPServer(("0.0.0.0", porta), Site).serve_forever()
