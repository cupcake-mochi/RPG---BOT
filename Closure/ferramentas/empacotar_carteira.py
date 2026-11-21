"""Monta o pacote do site da Carteira viva: um .zip pro app TYPE=site da Discloud, separado do bot.

    python3 ferramentas/empacotar_carteira.py --subdominio NOME
    python3 ferramentas/empacotar_carteira.py --subdominio NOME --campanhas CAMINHO/ficha-campanhas.json
    python3 ferramentas/empacotar_carteira.py --subdominio NOME --env CAMINHO/.env-carteira
    python3 ferramentas/empacotar_carteira.py --gerar-env CAMINHO/.env-carteira

--gerar-env   cria o .env do site com a chave de cifra e o segredo de serviço já sorteados (nada aparece na tela) e
              os outros campos em branco pra preencher. Não sobrescreve arquivo que já existe.

--subdominio  o nome registrado na Discloud, sem ".discloud.app" (vai no ID= do discloud.config).
--ram         memória do app em MB. Padrão 512, o mínimo que a Discloud pede pra site. A decisão é do Mizuki.
--campanhas   cópia do src/var/ficha-campanhas.json do bot (sai no backup do app das Guias). Sem ela, a análise
              de ficha fica desligada no site; cartão, galeria e cadastro funcionam.
--env         .env só do site, com as variáveis CARTEIRA_* (lista no docs/carteira-viva/PUBLICAR-SITE.md). Linha de
              outro nome é recusada, pra o .env do bot não ir parar no site por engano.

O que entra: discloud.config, iniciar_carteira.py, requirements.txt (o de carteira/), o código de src/carteira_viva e
de src/closure_bot (o motor da análise usa o corretor de ficha das Guias) e os dados do livro em dados/sistema.
O banco nunca entra: ele fica em var/ no disco do app e continua lá entre um envio e outro.
O .zip sai em src/var/, que está fora do git.
"""
from __future__ import annotations

import argparse
import re
import secrets
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "src" / "var" / "carteira-site.zip"
SUFIXOS = (".py", ".js", ".css", ".html", ".json", ".jsonl", ".tsv", ".webp", ".png", ".jpg", ".txt", ".md")
DADOS_LIVRO = ("catalogos.json", "livro.jsonl", "legado-r52.jsonl", "MANIFESTO.json")
# O que o ConfigWeb exige. CARTEIRA_DATABASE_PATH, CARTEIRA_BOOK_DATA e CARTEIRA_CAMPAIGNS_PATH o iniciar_carteira.py completa.
OBRIGATORIAS = {
    "CARTEIRA_PUBLIC_ORIGIN": "https://NOME.discloud.app, sem barra no fim",
    "CARTEIRA_ENCRYPTION_KEYS": "chave Fernet do banco. Guarde uma cópia longe dos backups: sem ela o banco não abre",
    "CARTEIRA_SERVICE_TOKEN": "o mesmo valor vai no .env do bot, em CARTEIRA_SERVICE_TOKEN",
    "CARTEIRA_DISCORD_CLIENT_ID": "Discord Developer Portal > Guias do Ciclo > OAuth2 > Client ID",
    "CARTEIRA_DISCORD_CLIENT_SECRET": "mesma tela, Client Secret",
    "CARTEIRA_DISCORD_BOT_TOKEN": "o token do bot das Guias (o DISCORD_TOKEN do .env do bot)",
    "CARTEIRA_GOOGLE_CLIENT_ID": "Google Cloud > guias-ciclo-fichas > Credenciais > cliente OAuth web de produção",
    "CARTEIRA_GOOGLE_CLIENT_SECRET": "mesmo cliente, chave secreta",
    "CARTEIRA_GOOGLE_PROJECT_NUMBER": "número do projeto guias-ciclo-fichas (1015676492327)",
    "CARTEIRA_PICKER_API_KEY": "chave de API do Picker, restrita ao endereço do site",
    "CARTEIRA_GUILDS": "IDs dos servidores liberados, separados por vírgula",
}


def config(subdominio: str, ram: int) -> str:
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", subdominio or ""):
        raise SystemExit("Subdomínio inválido: use letras minúsculas, números e hífen, sem .discloud.app.")
    if ram < 512:
        raise SystemExit("A Discloud pede pelo menos 512 MB pra site.")
    return (f"NAME=Carteira viva\nTYPE=site\nID={subdominio}\nMAIN=iniciar_carteira.py\nRAM={ram}\n"
            "AUTORESTART=true\nVERSION=latest\n")


def gerar_env(arquivo: Path) -> Path:
    if arquivo.exists():
        raise SystemExit(f"{arquivo} já existe; não sobrescrevo.")
    from cryptography.fernet import Fernet
    sorteados = {"CARTEIRA_ENCRYPTION_KEYS": Fernet.generate_key().decode(), "CARTEIRA_SERVICE_TOKEN": secrets.token_urlsafe(48)}
    linhas = ["# .env do site da Carteira viva. Fora do git e longe do HD externo. Não mande este arquivo pra ninguém.", ""]
    for chave, ajuda in OBRIGATORIAS.items():
        linhas += [f"# {ajuda}", f"{chave}={sorteados.get(chave, '')}", ""]
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linhas))
    return arquivo


def conferir_env(arquivo: Path) -> None:
    valores = {}
    for n, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        chave = linha.split("=", 1)[0].strip()
        if "=" not in linha or not chave.startswith("CARTEIRA_"):
            raise SystemExit(f"{arquivo.name}, linha {n}: o .env do site só leva variáveis CARTEIRA_*.")
        if chave == "CARTEIRA_DEV":
            raise SystemExit(f"{arquivo.name}, linha {n}: CARTEIRA_DEV é só pro piloto em casa.")
        valores[chave] = linha.split("=", 1)[1].strip().strip("\"'")
    vazias = [c for c in OBRIGATORIAS if not valores.get(c)]
    if vazias:
        raise SystemExit(f"{arquivo.name}: falta preencher " + ", ".join(vazias))
    if not valores["CARTEIRA_PUBLIC_ORIGIN"].startswith("https://"):
        raise SystemExit(f"{arquivo.name}: CARTEIRA_PUBLIC_ORIGIN precisa começar com https://")


def arquivos(campanhas: Path | None = None, env: Path | None = None) -> list[tuple[Path, str]]:
    """(arquivo no disco, caminho dentro do .zip). O discloud.config é escrito à parte."""
    lista = [(RAIZ / "iniciar_carteira.py", "iniciar_carteira.py"), (RAIZ / "carteira" / "requirements.txt", "requirements.txt")]
    for pasta in (RAIZ / "src" / "carteira_viva", RAIZ / "src" / "closure_bot"):
        lista += [(a, a.relative_to(RAIZ).as_posix()) for a in sorted(pasta.rglob("*"))
                  if a.is_file() and "__pycache__" not in a.parts and a.suffix in SUFIXOS]
    lista += [(RAIZ / "dados" / "sistema" / nome, f"dados/sistema/{nome}") for nome in DADOS_LIVRO]
    if campanhas is not None:
        lista.append((campanhas, "var/ficha-campanhas.json"))
    if env is not None:
        lista.append((env, ".env"))
    return lista


def empacotar(subdominio: str, *, ram: int = 512, campanhas: Path | None = None, env: Path | None = None,
              saida: Path = SAIDA) -> Path:
    texto_config = config(subdominio, ram)
    if env is not None:
        conferir_env(env)
    lista = arquivos(campanhas, env)
    faltando = [str(a) for a, _ in lista if not a.is_file()]
    if faltando:
        raise SystemExit("faltam arquivos pro pacote: " + ", ".join(faltando))
    saida.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(saida, "w", zipfile.ZIP_DEFLATED) as pacote:
        pacote.writestr("discloud.config", texto_config)
        for arquivo, nome in lista:
            pacote.write(arquivo, nome)
    return saida


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Pacote do site da Carteira viva (Discloud, TYPE=site)")
    p.add_argument("--subdominio")
    p.add_argument("--gerar-env", type=Path)
    p.add_argument("--ram", type=int, default=512)
    p.add_argument("--campanhas", type=Path)
    p.add_argument("--env", type=Path)
    a = p.parse_args(argv)
    if a.gerar_env:
        print(f"{gerar_env(a.gerar_env)} criado. Chave e segredo já sorteados; preencha o resto (não aparece nada na tela).")
        return 0
    if not a.subdominio:
        p.error("falta --subdominio")
    caminho = empacotar(a.subdominio, ram=a.ram, campanhas=a.campanhas, env=a.env)
    with zipfile.ZipFile(caminho) as z:
        total = len(z.namelist())
    avisos = ["COM o .env: não compartilhe este arquivo" if a.env else "sem o .env",
              "com o cadastro das campanhas" if a.campanhas else "SEM o cadastro das campanhas: análise desligada"]
    print(f"{caminho} ({caminho.stat().st_size // 1024} KB, {total} arquivos; {'; '.join(avisos)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
