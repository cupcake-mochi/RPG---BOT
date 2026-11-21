"""Arquivo de início do site da Carteira viva (o MAIN do discloud.config do app TYPE=site).

O pacote sai de ferramentas/empacotar_carteira.py. Este arquivo:
- lê o .env que está ao lado dele (só as linhas CARTEIRA_*; o ambiente vence o arquivo);
- completa os caminhos que têm lugar fixo no pacote (banco em var/, livro em dados/, campanhas em var/);
- sobe o serviço na porta 8080 e em 0.0.0.0, que é o que a Discloud exige pra site.

Em casa, o jeito é o do docs/carteira-viva/SERVICO.md (python -m carteira_viva).
"""
import os
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent


def ler_env(arquivo: Path) -> dict[str, str]:
    """Linhas CHAVE=valor do .env do site. Só aceita CARTEIRA_*: o .env do bot não serve aqui."""
    if not arquivo.is_file():
        return {}
    pares = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        if chave.startswith("CARTEIRA_"):
            pares[chave] = valor.strip().strip("\"'")
    return pares


def preparar_ambiente(pasta: Path = PASTA, ambiente=None) -> dict:
    """Monta o ambiente do serviço. Devolve o próprio dicionário (os.environ por padrão)."""
    amb = os.environ if ambiente is None else ambiente
    for chave, valor in ler_env(pasta / ".env").items():
        amb.setdefault(chave, valor)
    if amb.get("CARTEIRA_DEV") == "1":
        raise SystemExit("CARTEIRA_DEV=1 é só pro piloto em casa. Tire essa linha do .env do site.")
    (pasta / "var").mkdir(exist_ok=True)
    amb.setdefault("CARTEIRA_DATABASE_PATH", str(pasta / "var" / "carteira.sqlite3"))
    campanhas = pasta / "var" / "ficha-campanhas.json"
    # O motor da análise precisa do livro e do cadastro das campanhas juntos; sem o cadastro, a análise fica desligada.
    if (pasta / "dados" / "sistema").is_dir() and campanhas.is_file():
        amb.setdefault("CARTEIRA_BOOK_DATA", str(pasta / "dados"))
        amb.setdefault("CARTEIRA_CAMPAIGNS_PATH", str(campanhas))
    return amb


def main():
    preparar_ambiente()
    sys.path.insert(0, str(PASTA / "src"))
    from carteira_viva.__main__ import main as servico
    sys.argv = [sys.argv[0], "--porta", "8080"]
    servico()


if __name__ == "__main__":
    main()
