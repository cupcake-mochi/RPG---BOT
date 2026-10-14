"""Monta a página de teste (Plantão de teste) a partir do modelo.html com os cards e o lorebook atuais.
    python3 ferramentas/pagina_teste/montar_pagina.py SAIDA.html
Usa os textos de sistema e lembrete da pasta de avaliação; troque VERSOES quando um card mudar."""
import json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..")
AV = os.path.join(R, "dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos")
VERSOES = {"closure": "v0.33", "kaltsit": "v0.26", "lorebook": "v1.9"}
ler = lambda p: open(p, encoding="utf-8").read().strip()
ANIV_KAL = ("[Aniversário: você não diz a data do seu e não explica o motivo. Não fale de quem escolheu o dia nem de confirmar ou negar. "
            "Reaja curto, como a qualquer pergunta pessoal (\"Por que a pergunta?\", \"Isso não é importante.\", \"Talvez. Esse dia pode chegar.\"); "
            "a parabéns, só agradeça a intenção.]")
D = {
    "pers": {
        "kal": {"sistema": ler(f"{AV}/sistema_kal_v26.txt"), "lembrete": ler(f"{AV}/lembrete_kaltsit_v26.txt"), "aniversario": ANIV_KAL},
        "clo": {"sistema": ler(f"{AV}/sistema_closure_v33.txt"), "lembrete": ler(f"{AV}/lembrete_closure_v33.txt"),
                "aniversario": "[Aniversário: o seu é 10 de dezembro.]"},
    },
    "lore": [{k: e[k] for k in ("key", "content", "constant", "group", "comment")}
             for e in json.load(open(f"{R}/dados/personagem/kaltsit/lorebook.json", encoding="utf-8"))["entries"].values() if not e["disable"]],
    "livro": [{k: b.get(k) for k in ("ancora", "titulo", "titulos", "texto")} for b in map(json.loads, open(f"{R}/dados/sistema/livro.jsonl", encoding="utf-8"))],
    "versoes": VERSOES,
}
html = ler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo.html"))
assert html.count("/*__DATADOS__*/null") == 1
dados = json.dumps(D, ensure_ascii=False).replace("</", "<\\/")
open(sys.argv[1], "w", encoding="utf-8").write(html.replace("/*__DATADOS__*/null", dados))
print(f"ok: {len(D['lore'])} entradas, {len(D['livro'])} blocos, {os.path.getsize(sys.argv[1])//1024} KB")
