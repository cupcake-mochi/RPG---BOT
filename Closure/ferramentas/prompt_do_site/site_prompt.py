"""Monta o prompt com as mesmas peças do site de teste: prompts dos cards, lorebook, livro e a busca.

A página do site (ramo site-teste do RPG---BOT, site/publico/index.html) traz tudo embutido e é o que os
amigos testam. Em vez de copiar texto de card ou reescrever a busca, isto roda a lógica da própria página
e devolve a conversa pronta pra mandar ao modelo. Quando um card ou a busca mudam lá, basta baixar a página
de novo.

São dois motores pra rodar o JavaScript da página, com o mesmo resultado (os testes comparam):
  quickjs   embutido no Python (pip install quickjs-ng). É o do bot: a hospedagem só precisa do Python.
  node      o Node instalado na máquina, por ponte.js. Fica de reserva e pra conferência.
Sem escolher, vale o quickjs se estiver instalado, senão o node.

O pacote tem que ser o quickjs-ng. O "quickjs" antigo, de mesmo nome de módulo, erra expressão regular com letra
acentuada entre colchetes e a flag i (/anivers[aá]rio/i não casa com "aniversário"); aqui ele é recusado.

    python3 site_prompt.py --conferir       compara os dois motores numa bateria de pedidos (precisa dos dois)

    python3 site_prompt.py --atualizar      baixa a página e mostra as versões
    python3 site_prompt.py clo "closure, o que é Integridade?"

A página baixada fica em src/var/site/, fora do git.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import threading
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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


_funcao = None  # (mtime do núcleo, quickjs.Function)
_trava = threading.Lock()


def motores() -> list[str]:
    """Os motores que esta máquina tem, o preferido primeiro."""
    achados = []
    try:
        import quickjs

        # o quickjs antigo erra esta expressão; com ele o pedido sairia diferente do da página, sem aviso
        if quickjs.Context().eval('/[aá]/i.test("á")'):
            achados.append("quickjs")
    except ImportError:
        pass
    if shutil.which("node"):
        achados.append("node")
    return achados


# Pedidos pra comparar os dois motores: regra, mundo, conversa, seguimento, repetição, estado, plantão e aniversário.
CONFERENCIA = [
    ("clo", "oi closure", {}),
    ("clo", "closure, o que é Integridade?", {}),
    ("kal", "kal, qual a diferença entre Aguentar e Insistir?", {}),
    ("clo", "tenho 10 de PE máximo e tô com 1, quanto recupero no descanso curto?", {}),
    ("kal", "kal, quem é o Ozpin?", {"nome": "mel"}),
    ("kal", "vc gosta de café?", {"pronomes": "ela/dela"}),
    ("clo", "closure, a Escola trata infectados?", {"nome": "Mizuki"}),
    ("clo", "e o custo?", {"turnos": [{"de": "user", "nome": "sora", "texto": "qual o custo de PE da Técnica Máxima?"},
                                      {"de": "bot", "pers": "clo", "texto": "Depende do nível, olha no livro."}]}),
    ("kal", "kal, tudo bem?", {"falas_anteriores": ["Tudo em ordem por aqui.", "Boa tarde. Tudo em ordem por aqui.", "O custo é esse mesmo."]}),
    ("clo", "closure, o que é Refino?", {"hora": (14, 0), "estado": {"bloco": "[Estado agora: x.]", "lembretes": ["A.", "B.", "C."]}}),
    ("kal", "kal, quando é seu aniversário?", {"hora": (23, 0)}),
    ("clo", "closure me conta uma piada", {"hora": (3, 40)}),
    ("kal", "kal, que horário é o seu plantão?", {"hora": (23, 0)}),
    ("clo", "closure, de quem é o PLANTÃO agora?", {"hora": (14, 0)}),
]


def conferir_motores() -> list[str]:
    """As mensagens da bateria em que o quickjs e o node montaram pedidos diferentes. Lista vazia é o esperado."""
    diferentes = []
    for pers, msg, extra in CONFERENCIA:
        extra = {"hora": (22, 10), "nome": "rafa", **extra}
        if montar(pers, msg, motor="quickjs", **extra) != montar(pers, msg, motor="node", **extra):
            diferentes.append(msg)
    return diferentes


def _pelo_quickjs(pedido: str) -> str:
    """O contexto fica carregado entre as chamadas; se a página for baixada de novo, carrega outro."""
    global _funcao
    import quickjs

    caminho = nucleo()
    with _trava:
        if _funcao is None or _funcao[0] != caminho.stat().st_mtime:
            codigo = "".join((AQUI / "antes.js").read_text(encoding="utf-8") + caminho.read_text(encoding="utf-8") + "\n"
                             + (AQUI / "depois.js").read_text(encoding="utf-8"))
            funcao = quickjs.Function("__montarJSON", codigo)  # roda numa linha de execução só dela; pode ser chamada de qualquer uma
            funcao.set_time_limit(20)
            _funcao = (caminho.stat().st_mtime, funcao)
        return _funcao[1](pedido)


def _pelo_node(pedido: str) -> str:
    saida = subprocess.run(["node", str(AQUI / "ponte.js"), str(nucleo())], input=pedido, capture_output=True, text=True, timeout=60)
    if saida.returncode != 0:
        raise RuntimeError("ponte.js falhou: " + saida.stderr[-800:])
    return saida.stdout


def montar(pers: str, msg: str, *, nome: str = "", pronomes: str = "", turnos: list[dict] | None = None,
           hora: tuple[int, int] | None = None, falas_anteriores: list[str] | None = None,
           estado: dict | None = None, motor: str | None = None) -> dict:
    """Devolve {"input": [...], "ativadas": [...], "versoes": {...}}. `pers` é "kal" ou "clo".

    `falas_anteriores` são as últimas respostas da personagem no canal, de outras conversas: com elas o aviso de
    repetição da página passa a valer de uma conversa pra outra.
    `estado` é o de closure_bot.vida (Estado.para_a_ponte()): o bloco de estado entra no lugar do da página, que é
    fixo, e as linhas dele vão pro lembrete do fim.
    `hora` fixa a hora de Brasília do pedido, pra teste; sem ela vale a de agora."""
    pedido = {"pers": pers, "msg": msg, "nome": nome, "pronomes": pronomes, "turnos": turnos or [],
              "falas_anteriores": falas_anteriores or []}
    if estado:
        pedido["estado"] = estado
    if hora:
        pedido["agora"] = int(datetime(2026, 10, 13, hora[0], hora[1], tzinfo=ZoneInfo("America/Sao_Paulo")).timestamp() * 1000)
    motor = motor or next(iter(motores()), None)
    if motor == "quickjs":
        return json.loads(_pelo_quickjs(json.dumps(pedido)))
    if motor == "node":
        return json.loads(_pelo_node(json.dumps(pedido)))
    raise RuntimeError("nenhum motor pra rodar a página do site: instale o quickjs-ng (pip install quickjs-ng) ou o Node")


if __name__ == "__main__":
    if "--atualizar" in sys.argv:
        atualizar()
        print("motores:", motores(), "| versões:", montar("clo", "oi")["versoes"])
    if "--conferir" in sys.argv or ("--atualizar" in sys.argv and len(motores()) == 2):
        diferentes = conferir_motores()
        print(f"motores iguais em {len(CONFERENCIA) - len(diferentes)} de {len(CONFERENCIA)} pedidos" + (": DIFERENTES em " + "; ".join(diferentes) if diferentes else ""))
        sys.exit(1 if diferentes else 0)
    if len(sys.argv) > 2 and not sys.argv[1].startswith("--"):
        r = montar(sys.argv[1], sys.argv[2], nome="teste")
        print("versões:", r["versoes"], "| ativadas:", r["ativadas"])
        print(r["input"][-1]["content"])
