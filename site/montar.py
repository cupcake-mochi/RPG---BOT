"""Monta o site de teste a partir da página "Plantão de teste" (ferramentas/pagina_teste) do Closure.
    python3 site/montar.py [CAMINHO_DA_PASTA_CLOSURE]   (padrão: a pasta Closure do lado de site/)
Gera site/publico/index.html (a página com os cards e o lorebook atuais, mais o adaptador que troca o
Claude do claude.ai pelo servidor) e site/publico/prompts.json (os prompts de sistema que o servidor
aceita). Rode de novo sempre que um card mudar e suba os dois arquivos."""
import json, os, re, subprocess, sys, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
closure = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "../Closure"))
pag = os.path.join(closure, "ferramentas/pagina_teste/montar_pagina.py")
with tempfile.TemporaryDirectory() as t:
    saida = os.path.join(t, "p.html")
    subprocess.run([sys.executable, pag, saida], check=True)
    html = open(saida, encoding="utf-8").read()

# os prompts de sistema vão pro servidor, que só aceita conversa com um deles (a chave não vira Gemini grátis pra qualquer uso)
m = re.search(r"const D = (\{.*?\});\n", html, re.S)
D = json.loads(m.group(1).replace("<\\/", "</"))
prompts = {k: v["sistema"] for k, v in D["pers"].items()}

adaptador = open(os.path.join(AQUI, "adaptador.js"), encoding="utf-8").read()
assert html.count("<script>\nconst D") == 1
# no site cada amigo digita o próprio nome
assert html.count('id="nome" value="mizuki"') == 1
html = html.replace('id="nome" value="mizuki"', 'id="nome" value="" placeholder="seu nome"', 1)
assert html.count("const ERRO = {") == 1
html = html.replace("const ERRO = {", "const ERRO = { ...(window.__ERROS_SITE || {}),", 1)
html = html.replace("<script>\nconst D", "<script>\n" + adaptador + "\n</script>\n<script>\nconst D", 1)
html = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n' + html + "\n</body></html>\n")

os.makedirs(os.path.join(AQUI, "publico"), exist_ok=True)
open(os.path.join(AQUI, "publico/index.html"), "w", encoding="utf-8").write(html)
json.dump({"versoes": D["versoes"], "prompts": prompts}, open(os.path.join(AQUI, "publico/prompts.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("ok:", D["versoes"], f"{os.path.getsize(os.path.join(AQUI, 'publico/index.html')) // 1024} KB")
