"""Troca o bloco da busca do livro de uma página montada pela busca v4 (busca_v4.js ao lado deste script).
    python3 aplicar3.py ENTRADA.html SAIDA.html"""
import sys, os
h = open(sys.argv[1], encoding="utf-8").read()
novo = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "busca_v4.js"), encoding="utf-8").read()
a, b = h.index("// ---------- livro:"), h.index("// ---------- estado da conversa")
open(sys.argv[2], "w", encoding="utf-8").write(h[:a] + novo.rstrip() + "\n\n" + h[b:])
print("ok")
