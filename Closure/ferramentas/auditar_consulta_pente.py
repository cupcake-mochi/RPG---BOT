"""Pente fino da consulta do livro: cada tópico de cada página vira perguntas naturais. Sem modelo, sem rede.

Diferente de auditar_consulta_livro.py, que pergunta "No livro, como funciona {título}?" (as palavras "livro" e
"como funciona" já abrem a busca sozinhas), aqui as perguntas são do jeito que se pergunta no Discord:
"o que {nome} faz?", "quais os benefícios de {nome}?", "me explica {nome}".

Tópicos de cada página: título, subtítulos, cabeçalhos (#), abertura em negrito (**Nome.**), linha de tabela em
negrito (| **Nome** |) e termos que o índice/glossário ligam a uma página ([Nome](#ancora)). Um tópico acerta
quando alguma página que define aquele nome chega entre as fontes. Também mede a conversa comum: mensagens sem
assunto de regra que não deveriam receber trecho do livro.

    python3 ferramentas/auditar_consulta_pente.py --saida src/var/pente.md
    python3 ferramentas/auditar_consulta_pente.py --saida src/var/pente.md --comparar nucleo-antigo.js

Precisa do Node (ferramentas/prompt_do_site/lote.js): são ~13 mil pedidos e o QuickJS levaria horas.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas/prompt_do_site"))
import site_prompt

MODELOS = ["o que {t} faz?", "quais os benefícios de {t}?", "me explica {t}"]
PERS = ("kal", "clo")
FORA = re.compile(r"(?i)^(n[ií]vel|classe|categoria|exemplo|grau|tabela|progress)|continua|exemplo|índice|indice|^\d")
CONVERSA = [
    "oi kal, tudo bem?", "qual a duração do filme que você viu ontem?", "o que você acha da área de TI?",
    "quais os benefícios de acordar cedo?", "você tem destreza pra tocar piano?", "qual o tamanho da sua sala?",
    "o que você faz no seu tempo livre?", "quanto tempo dura uma viagem pro Japão?", "qual é a sua comida favorita?",
    "você prefere café ou chá?", "como foi seu dia?", "qual o melhor anime da temporada?",
    "tem alguma dica pra estudar pra prova?", "o que é física quântica?", "me explica como funciona a bolsa de valores",
    "você acha que vai chover hoje?", "qual a distância daqui até São Paulo?", "o que significa resiliência?",
    "você gosta de música clássica?", "qual a melhor forma de aprender inglês?",
    "qual o peso ideal pra uma mochila de viagem?", "qual a velocidade da luz?", "me fala sobre a sua família",
    "o que você acha do meu desenho?", "qual o melhor jeito de dormir cedo?", "você conhece algum livro bom de fantasia?",
    "qual o preço de um notebook bom hoje?", "qual a sua cor favorita?", "quais os benefícios de meditar?",
    "o que a energia solar faz de bom?", "você sabe a diferença entre baixo e contrabaixo?",
    "qual é o maior planeta do sistema solar?", "o que você acha de gatos?", "como eu faço um bolo de cenoura?",
    "qual a sua reação quando alguém te elogia?", "você já teve medo de altura?",
    "qual o limite de velocidade numa rodovia?", "quais os efeitos colaterais do café?",
    "o que é um sinal de trânsito amarelo?", "você prefere praia ou montanha?", "quanto custa uma pizza grande?",
    "qual o seu nível de paciência hoje?", "o que é marketing digital?", "qual a melhor estratégia no xadrez?",
    "como você se protege do frio?", "qual a sua especialização na faculdade?", "como ganhar mais foco nos estudos?",
    "o que é um vínculo afetivo?", "qual o melhor treino pra iniciante na academia?",
]

livro = [json.loads(l) for l in (RAIZ / "dados/sistema/livro.jsonl").read_text(encoding="utf-8").splitlines()]
POS = {b["ancora"]: i for i, b in enumerate(livro)}
norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip()


def limpa(t):
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_`#]", "", t).strip().rstrip(".:;,")
    return re.sub(r"\s*\(.*?\)\s*", " ", t).strip()


def topicos():
    """[(nome, tipo, âncora)] e o mapa nome -> páginas que definem esse nome."""
    achados = []
    for b in livro:
        a, texto = b["ancora"], b["texto"]
        achados += [(b["titulo"], "título", a)] + [(t, "subtítulo", a) for t in b.get("titulos") or []]
        achados += [(m, "cabeçalho", a) for m in re.findall(r"^#{1,6} ([^\n]+)$", texto, re.M)]
        achados += [(m, "negrito", a) for m in re.findall(r"^\*\*([^*\n]{3,50})\.\*\*", texto, re.M)]
        achados += [(m, "tabela", a) for m in re.findall(r"^\| \*\*([^*|]{3,50})\*\* \|", texto, re.M)]
        achados += [(m[0], "glossário", m[1]) for m in re.findall(r"\[([^\]]{3,50})\]\(#([\w-]+)\)", texto) if m[1] in POS]
    defs, saida, vistos = defaultdict(set), [], set()
    for nome, tipo, a in achados:
        nome = limpa(nome)
        if not 3 <= len(nome) <= 50 or FORA.search(nome) or len(nome.split()) > 7:
            continue
        defs[norm(nome)].add(a)
        if (norm(nome), a) not in vistos:
            vistos.add((norm(nome), a))
            saida.append((nome, tipo, a))
    return saida, defs


def rodar(perguntas, nucleo):
    with tempfile.TemporaryDirectory() as tmp:
        entrada, saida = Path(tmp) / "q.json", Path(tmp) / "r.json"
        entrada.write_text(json.dumps(perguntas, ensure_ascii=False), encoding="utf-8")
        subprocess.run(["node", str(RAIZ / "ferramentas/prompt_do_site/lote.js"), str(nucleo), str(entrada), str(saida)],
                       check=True, timeout=1800)
        return {r["id"]: r["fontes"] for r in json.loads(saida.read_text(encoding="utf-8"))}


def medir(nucleo):
    tops, defs = topicos()
    qs = [{"id": f"{k}|{m}|{p}", "pers": p, "msg": m.format(t=nome if nome[:2].isupper() else nome[0].lower() + nome[1:])}
          for k, (nome, _, _) in enumerate(tops) for m in MODELOS for p in PERS]
    qs += [{"id": f"conversa|{i}", "pers": "kal", "msg": m} for i, m in enumerate(CONVERSA)]
    res = rodar(qs, nucleo)
    msg = {q["id"]: q["msg"] for q in qs}
    linhas = []
    for k, (nome, tipo, a) in enumerate(tops):
        alvo, item = defs[norm(nome)], {"nome": nome, "tipo": tipo, "ancora": a}
        for p in PERS:
            casos = [(msg[f"{k}|{m}|{p}"], res[f"{k}|{m}|{p}"]) for m in MODELOS]
            item[p] = {"certas": sum(bool(alvo & set(f)) for _, f in casos), "vazias": sum(not f for _, f in casos),
                       "exemplo": next(((q, f) for q, f in casos if not alvo & set(f)), None)}
        linhas.append(item)
    conversa = {m: res[f"conversa|{i}"] for i, m in enumerate(CONVERSA)}
    return linhas, conversa


def resumo(linhas, conversa, p="kal"):
    return {"ok": sum(x[p]["certas"] == 3 for x in linhas), "parcial": sum(0 < x[p]["certas"] < 3 for x in linhas),
            "falha": sum(x[p]["certas"] == 0 for x in linhas), "sem_trecho": sum(x[p]["vazias"] for x in linhas),
            "conversa_com_livro": sum(bool(f) for f in conversa.values())}


def relatorio(linhas, conversa, antes=None):
    r = resumo(linhas, conversa)
    L = ["# Pente fino da consulta do livro", "",
         f"{len(linhas)} tópicos × {len(MODELOS)} jeitos de perguntar × Kal'tsit e Closure, mais {len(conversa)} mensagens de conversa comum.",
         "Tópico **ok** = a página certa chega nas 3 formas; **parcial** = em 1 ou 2; **falha** = em nenhuma.", "",
         "| | ok | parcial | falha | perguntas sem trecho | conversa com livro |", "|---|---|---|---|---|---|"]
    if antes:
        a = resumo(*antes)
        L.append(f"| antes | {a['ok']} | {a['parcial']} | {a['falha']} | {a['sem_trecho']} | {a['conversa_com_livro']} de {len(conversa)} |")
    L.append(f"| agora | {r['ok']} | {r['parcial']} | {r['falha']} | {r['sem_trecho']} | {r['conversa_com_livro']} de {len(conversa)} |")
    dif = sum(x["kal"]["certas"] != x["clo"]["certas"] for x in linhas)
    L += ["", f"Tópicos com resultado diferente entre Kal'tsit e Closure: {dif}.", "",
          "## Por capítulo", "", "| Cap. | Capítulo | Tópicos | ok | parcial | falha | sem trecho |", "|---|---|---|---|---|---|---|"]
    grupos = defaultdict(list)
    for x in linhas:
        b = livro[POS[x["ancora"]]]
        grupos[(b["capitulo"], b["capitulo_titulo"])].append(x["kal"])
    for (n, nome), ks in sorted(grupos.items()):
        L.append(f"| {n} | {nome} | {len(ks)} | {sum(k['certas'] == 3 for k in ks)} | {sum(0 < k['certas'] < 3 for k in ks)} | "
                 f"{sum(k['certas'] == 0 for k in ks)} | {sum(k['vazias'] for k in ks)} |")
    L += ["", "## Conversa comum que recebe trecho do livro", ""]
    L += [f"- “{m}” → {', '.join(f)}" for m, f in conversa.items() if f] or ["- nenhuma"]
    L += ["", "## Tópicos que não chegam nas 3 formas, por página", "",
          "Muitos são subtítulos genéricos (“limites”, “resolução”) que ninguém pergunta soltos; leia como lista para conferir, não como meta.", ""]
    por_pag = defaultdict(list)
    for x in linhas:
        if x["kal"]["certas"] < 3:
            por_pag[x["ancora"]].append(x)
    for a in sorted(por_pag, key=POS.get):
        b = livro[POS[a]]
        L.append(f"### Cap. {b['capitulo']} · {b['titulo']} (`{a}`)")
        for x in por_pag[a]:
            q, f = x["kal"]["exemplo"]
            L.append(f"- {x['nome']} ({x['tipo']}): {x['kal']['certas']}/3. Ex.: “{q}” → {', '.join(f) if f else 'nenhum trecho'}")
        L.append("")
    return "\n".join(L) + "\n", r


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", type=Path, required=True, help="relatório em Markdown")
    p.add_argument("--comparar", type=Path, help="núcleo anterior, para a linha 'antes'")
    args = p.parse_args()
    antes = medir(args.comparar) if args.comparar else None
    # atualizar(), não nucleo(): o cache em src/var/site guarda o núcleo da última montagem, e a medida tem que
    # sair do modelo.html como está agora.
    texto, r = relatorio(*medir(site_prompt.atualizar()), antes=antes)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(texto, encoding="utf-8")
    print(f"ok {r['ok']}, parcial {r['parcial']}, falha {r['falha']}, sem trecho {r['sem_trecho']}, "
          f"conversa com livro {r['conversa_com_livro']} de {len(CONVERSA)} -> {args.saida}")


if __name__ == "__main__":
    main()
