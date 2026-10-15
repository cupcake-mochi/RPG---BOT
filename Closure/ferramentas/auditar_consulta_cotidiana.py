"""Remonta a bateria já encerrada para comparar contexto, sem modelo ou rede.

As respostas antigas só recompõem o histórico dos diálogos. Esta auditoria não
repete tentativas, altera a evidência paga nem mede qualidade/custo de respostas.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas"))
from bateria_mista import montar, site_prompt


def medidas(p):
    textos = [m["content"] for m in p["input"]]
    return {"caracteres_entrada": sum(map(len, textos)),
            "bytes_entrada_utf8": sum(len(t.encode()) for t in textos),
            "caracteres_ultima_mensagem": len(textos[-1]),
            "fontes": re.findall(r"\[Livro, âncora ([^\]]+)\]", textos[-1]),
            "ativadas": p["ativadas"]}


def remonta(casos, respostas, nucleo=None):
    cache = site_prompt.CACHE
    resultado = []
    try:
        with tempfile.TemporaryDirectory() as tmp:
            if nucleo:
                pasta = Path(tmp)
                (pasta / "nucleo.js").write_bytes(nucleo.read_bytes())
                site_prompt.CACHE = pasta
            site_prompt._funcao = None
            anteriores = []
            por_id = {r["id"]: r for r in respostas}
            for c in casos:
                p = montar(c, anteriores)
                resultado.append(p)
                anteriores.append(por_id[c["id"]])
    finally:
        site_prompt.CACHE = cache
        site_prompt._funcao = None
    return resultado


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--comparar", type=Path, required=True)
    p.add_argument("--bateria", type=Path, default=RAIZ / "pesquisa/validacao/2026-10-15-bateria-mista-v10")
    p.add_argument("--capturas", type=Path, default=RAIZ / "pesquisa/privado/bateria-mista-v10")
    p.add_argument("--saida", type=Path, required=True)
    args = p.parse_args()
    plano = json.loads((args.bateria / "plano.json").read_text())
    respostas = json.loads((args.bateria / "respostas.json").read_text())
    casos = plano["casos"]
    assert hashlib.sha256(args.comparar.read_bytes()).hexdigest() == plano["nucleo_sha256"], "núcleo anterior não corresponde à bateria"
    antes = remonta(casos, respostas, args.comparar)
    # Confirma igualdade exata com cada pedido salvo antes de comparar versões.
    for c, a in zip(casos, antes):
        salvo = json.loads((args.capturas / (c["id"] + ".json")).read_text())
        assert a == salvo, "reconstrução divergiu: " + c["id"]
    depois = remonta(casos, respostas)
    grupos = defaultdict(list)
    registros = []
    for c, a, d in zip(casos, antes, depois):
        m = {"id": c["id"], "categoria": c["categoria"], "antes": medidas(a), "depois": medidas(d)}
        m["pedido_igual"] = a == d
        registros.append(m)
        grupos[c["categoria"]].append(m)
    resumo = {}
    for grupo, rs in grupos.items():
        resumo[grupo] = {"casos": len(rs), "pedidos_iguais": sum(r["pedido_igual"] for r in rs)}
        for versao in ("antes", "depois"):
            resumo[grupo][versao] = {
                "caracteres_entrada": sum(r[versao]["caracteres_entrada"] for r in rs),
                "bytes_entrada_utf8": sum(r[versao]["bytes_entrada_utf8"] for r in rs),
                "casos_com_fontes": sum(bool(r[versao]["fontes"]) for r in rs)}
    resultado = {"escopo": "reconstrução exata dos 48 pedidos antigos; contexto novo sem API, sem tokens ou custo novos",
                 "nucleo_antes_sha256": plano["nucleo_sha256"],
                 "nucleo_depois_sha256": hashlib.sha256(site_prompt.nucleo().read_bytes()).hexdigest(),
                 "pedidos_anteriores_iguais_as_capturas": len(antes), "resumo": resumo, "casos": registros}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
