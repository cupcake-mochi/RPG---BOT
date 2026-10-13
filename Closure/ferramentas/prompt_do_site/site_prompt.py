"""Monta o prompt com as mesmas peças do site de teste: prompts dos cards, lorebook, livro e a busca.

A página do site (ramo site-teste do RPG---BOT, site/publico/index.html) traz tudo embutido e é o que os
amigos testam. Em vez de copiar texto de card ou reescrever a busca, isto roda a lógica da própria página
no Node e devolve a conversa pronta pra mandar ao modelo. Quando um card ou a busca mudam lá, basta baixar
a página de novo.

    python3 site_prompt.py --atualizar      baixa a página e mostra as versões
    python3 site_prompt.py clo "closure, o que é Integridade?"

Precisa do Node instalado. A página baixada fica em src/var/site/, fora do git.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CACHE = AQUI.parents[1] / "src" / "var" / "site"
PAGINA = "https://raw.githubusercontent.com/cupcake-mochi/RPG---BOT/site-teste/site/publico/index.html"
FIM_DO_NUCLEO = "// ---------- tela ----------"


def atualizar() -> Path:
    """Baixa a página e separa o núcleo (dados e lógica, sem a parte que desenha a tela)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(PAGINA, timeout=60) as resposta:
        html = resposta.read().decode("utf-8")
    inicio = html.index("const D =")
    fim = html.index(FIM_DO_NUCLEO, inicio)  # se a página mudar de forma, isto falha alto em vez de montar errado
    (CACHE / "nucleo.js").write_text(html[inicio:fim], encoding="utf-8")
    return CACHE / "nucleo.js"


def nucleo() -> Path:
    caminho = CACHE / "nucleo.js"
    return caminho if caminho.exists() else atualizar()


def montar(pers: str, msg: str, *, nome: str = "", pronomes: str = "", turnos: list[dict] | None = None,
           hora: tuple[int, int] | None = None, falas_anteriores: list[str] | None = None,
           estado: dict | None = None) -> dict:
    """Devolve {"input": [...], "ativadas": [...], "versoes": {...}}. `pers` é "kal" ou "clo".

    `falas_anteriores` são as últimas respostas da personagem no canal, de outras conversas: com elas o aviso de
    repetição da página passa a valer de uma conversa pra outra.
    `estado` é o de closure_bot.vida (Estado.para_a_ponte()): o bloco de estado entra no lugar do da página, que é
    fixo, e as linhas dele vão pro lembrete do fim."""
    pedido = {"pers": pers, "msg": msg, "nome": nome, "pronomes": pronomes, "turnos": turnos or [],
              "falas_anteriores": falas_anteriores or []}
    if estado:
        pedido["estado"] = estado
    if hora:
        pedido["hora"] = {"h": hora[0], "m": hora[1]}
    saida = subprocess.run(["node", str(AQUI / "ponte.js"), str(nucleo())], input=json.dumps(pedido),
                           capture_output=True, text=True, timeout=60)
    if saida.returncode != 0:
        raise RuntimeError("ponte.js falhou: " + saida.stderr[-800:])
    return json.loads(saida.stdout)


if __name__ == "__main__":
    if "--atualizar" in sys.argv:
        atualizar()
        print("versões:", montar("clo", "oi")["versoes"])
    else:
        r = montar(sys.argv[1], sys.argv[2], nome="teste")
        print("versões:", r["versoes"], "| ativadas:", r["ativadas"])
        print(r["input"][-1]["content"])
