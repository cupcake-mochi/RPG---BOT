"""Troca a busca do livro de uma página montada (ou do modelo.html) pela busca v2.
    python3 aplicar.py ENTRADA.html SAIDA.html"""
import sys, os
h = open(sys.argv[1], encoding="utf-8").read()
novo = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "busca_v2.js"), encoding="utf-8").read()
a, b = h.index("// ---------- livro:"), h.index("// ---------- estado da conversa")
h = h[:a] + novo + "\n" + h[b:]
velho = "const livro = blocosLivro(msg, a.termos);"
assert h.count(velho) == 1
h = h.replace(velho, 'const livro = blocosLivro(msg, a.termos, turnos.filter(t => t.de === "user").slice(-1).map(t => t.texto).join(" "));')
open(sys.argv[2], "w", encoding="utf-8").write(h)
print("ok")
