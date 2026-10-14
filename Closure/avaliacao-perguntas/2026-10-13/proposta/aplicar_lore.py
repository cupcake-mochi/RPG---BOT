"""Só pra teste: aplica lorebook_proposta.json no D.lore de uma página montada.
    python3 aplicar_lore.py ENTRADA.html SAIDA.html"""
import sys, os, json
h = open(sys.argv[1], encoding="utf-8").read()
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lorebook_proposta.json"), encoding="utf-8"))
js = "\n// lorebook proposto (teste)\n" + f"(() => {{ const P = {json.dumps(P, ensure_ascii=False)};\n" + """
  for (const e of D.lore) { const m = P.mudar[e.comment]; if (m) { e.key = e.key.concat(m.key_adicionar); if (m.content) e.content = m.content; } }
  for (const n of P.novas) D.lore.push({ key: n.key, content: n.content, constant: false, group: n.group, comment: n.comment });
})();
"""
marca = "// ---------- utilidades ----------"
assert h.count(marca) == 1
open(sys.argv[2], "w", encoding="utf-8").write(h.replace(marca, js + marca))
print("ok")
