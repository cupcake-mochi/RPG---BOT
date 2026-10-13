"""Servidor do site de teste do bot (Kal'tsit e Closure) pros amigos do Mizuki.
Serve a página montada por montar.py e repassa as mensagens pro Gemini com a chave guardada aqui,
nunca no navegador. Só a biblioteca padrão do Python.

Variáveis de ambiente:
  GEMINI_API_KEY         obrigatória
  SENHA                  código que os amigos digitam na página (obrigatória)
  SENHA_ADMIN            libera GET /api/conversas?admin=... pra baixar as conversas salvas
  GEMINI_MODELO          modelo do botão "Padrão" (padrão: gemini-3.8-flash)
  GEMINI_MODELO_RAPIDO   modelo do botão "Rápido" (padrão: gemini-3.1-flash-lite)
  LIMITE_HORA            mensagens por pessoa (IP) por hora (padrão: 40)
  LIMITE_DIA             mensagens no total por dia, horário de Brasília (padrão: 300)
  PASTA_CONVERSAS        onde as conversas ficam salvas (padrão: ./conversas)
  PORT                   porta (padrão: 8000)
"""
import json, os, re, threading, time, urllib.error, urllib.request
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(AQUI, "publico")
CHAVE = os.environ.get("GEMINI_API_KEY", "")
SENHA = os.environ.get("SENHA", "")
SENHA_ADMIN = os.environ.get("SENHA_ADMIN", "")
MODELO = os.environ.get("GEMINI_MODELO", "gemini-3.8-flash")
MODELOS = {"default": MODELO, "complex": MODELO, "quick": os.environ.get("GEMINI_MODELO_RAPIDO", "gemini-3.1-flash-lite")}
LIMITE_HORA = int(os.environ.get("LIMITE_HORA", "40"))
LIMITE_DIA = int(os.environ.get("LIMITE_DIA", "300"))
CONVERSAS = os.environ.get("PASTA_CONVERSAS", os.path.join(AQUI, "conversas"))
MAX_CARACTERES, MAX_MENSAGENS = 200_000, 60

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


def gemini(entrada, tier):
    corpo = {
        "system_instruction": {"parts": [{"text": entrada[0]["content"]}]},
        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in entrada[1:]],
        "generationConfig": {"temperature": 0.8, "maxOutputTokens": 2048},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELOS.get(tier, MODELO)}:generateContent"
    req = urllib.request.Request(url, json.dumps(corpo).encode(), {"Content-Type": "application/json", "x-goog-api-key": CHAVE})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    cand = (d.get("candidates") or [{}])[0]
    partes = cand.get("content", {}).get("parts", [])
    texto = "".join(p.get("text", "") for p in partes if not p.get("thought")).strip()
    if not texto:
        return None, cand.get("finishReason") or d.get("promptFeedback", {}).get("blockReason") or "vazio"
    return {"text": texto, "truncated": cand.get("finishReason") == "MAX_TOKENS"}, None


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
        tier = corpo.get("tier")
        try:
            try:
                resp, motivo = gemini(entrada, tier)
            except urllib.error.HTTPError as e:
                # cota do modelo principal acabou: responde com o do botão Rápido, que tem cota própria
                if e.code != 429 or MODELOS.get(tier, MODELO) == MODELOS["quick"]:
                    raise
                print("cota de", MODELOS.get(tier, MODELO), "acabou, usando", MODELOS["quick"], flush=True)
                resp, motivo = gemini(entrada, "quick")
        except urllib.error.HTTPError as e:
            detalhe = e.read().decode(errors="replace")[:300]
            print("gemini HTTP", e.code, detalhe.replace("\n", " "), flush=True)
            return self.responder(503 if e.code == 429 else 502, {"erro": "cota_gemini" if e.code == 429 else "gemini"})
        except (urllib.error.URLError, TimeoutError) as e:
            print("gemini rede", e, flush=True)
            return self.responder(502, {"erro": "gemini"})
        if resp is None:
            return self.responder(502, {"erro": "bloqueado" if motivo in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "OTHER") else "gemini", "detalhe": motivo})
        self.responder(200, resp)

    def conversa(self, corpo):
        cid = str(corpo.get("id") or "")
        if not re.fullmatch(r"[a-z0-9]{4,40}", cid) or not isinstance(corpo.get("dados"), dict):
            return self.responder(400, {"erro": "pedido_invalido"})
        os.makedirs(CONVERSAS, exist_ok=True)
        dados = dict(corpo["dados"], id=cid)
        with open(os.path.join(CONVERSAS, cid + ".json"), "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)
        self.responder(200, {"ok": True})


if __name__ == "__main__":
    if not CHAVE or not SENHA:
        raise SystemExit("Faltou GEMINI_API_KEY ou SENHA nas variáveis de ambiente.")
    porta = int(os.environ.get("PORT", "8000"))
    print(f"no ar na porta {porta} · modelos {MODELOS['quick']} / {MODELOS['default']} · {LIMITE_HORA}/h por pessoa, {LIMITE_DIA}/dia", flush=True)
    ThreadingHTTPServer(("0.0.0.0", porta), Site).serve_forever()
