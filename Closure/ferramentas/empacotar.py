"""Monta o pacote de hospedagem: um .zip só com o que o bot precisa pra rodar, pronto pra subir na Discloud.

    python3 ferramentas/empacotar.py              sem o .env (as variáveis vão pelo painel da hospedagem)
    python3 ferramentas/empacotar.py --com-env    com o .env dentro, que é como a Discloud costuma receber

O que entra: discloud.config, iniciar.py, closure_lab.py (o nome do arquivo principal do app antigo na Discloud), requirements.txt (o de src/), o código em src/closure_bot, a ponte do
site com a página já baixada, o manifesto das regras e os dois card.json. O banco, os testes e o resto de dados/
ficam de fora. O .zip sai em src/var/, que está fora do git: com --com-env ele carrega segredo.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "prompt_do_site"))
SAIDA = RAIZ / "src" / "var" / "closure-lab.zip"


def arquivos(com_env: bool) -> list[tuple[Path, str]]:
    """(arquivo no disco, caminho dentro do .zip)."""
    lista = [(RAIZ / "discloud.config", "discloud.config"), (RAIZ / "iniciar.py", "iniciar.py"), (RAIZ / "closure_lab.py", "closure_lab.py"),
             (RAIZ / "src" / "requirements.txt", "requirements.txt")]
    pastas = [RAIZ / "src" / "closure_bot", RAIZ / "ferramentas" / "prompt_do_site"]
    for pasta in pastas:
        lista += [(a, str(a.relative_to(RAIZ))) for a in sorted(pasta.rglob("*"))
                  if a.is_file() and "__pycache__" not in a.parts and a.suffix in (".py", ".js", ".webp", ".png", ".jpg", ".tsv", ".json")]
    lista.append((RAIZ / "src" / "var" / "site" / "nucleo.js", "src/var/site/nucleo.js"))
    lista.append((RAIZ / "dados" / "sistema" / "MANIFESTO.json", "dados/sistema/MANIFESTO.json"))
    # a correção de ficha (cogs/ficha.py) lê o catálogo e o livro: Caminhos, Origens, uniformes, escudos e marcos
    for nome in ("catalogos.json", "livro.jsonl"):
        lista.append((RAIZ / "dados" / "sistema" / nome, f"dados/sistema/{nome}"))
    lista += [(c, str(c.relative_to(RAIZ))) for c in sorted((RAIZ / "dados" / "personagem").glob("*/card.json"))]
    if com_env:
        lista.append((RAIZ / ".env", ".env"))
    return lista


def empacotar(com_env: bool = False, saida: Path = SAIDA) -> Path:
    import site_prompt

    site_prompt.nucleo()  # baixa a página se ainda não tiver
    lista = arquivos(com_env)
    faltando = [str(a) for a, _ in lista if not a.exists()]
    if faltando:
        raise SystemExit("faltam arquivos pro pacote: " + ", ".join(faltando))
    saida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as pacote:
        for arquivo, nome in lista:
            pacote.write(arquivo, nome)
    return saida


if __name__ == "__main__":
    com_env = "--com-env" in sys.argv
    caminho = empacotar(com_env)
    print(f"{caminho} ({caminho.stat().st_size // 1024} KB, {len(arquivos(com_env))} arquivos, "
          f"{'COM o .env: não compartilhe este arquivo' if com_env else 'sem o .env'})")
