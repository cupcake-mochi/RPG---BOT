"""Configuração do bot: lê o .env da raiz do Closure (o ambiente vence o arquivo) e resolve os caminhos.

Variáveis (modelo em .env.exemplo, na raiz do repositório):
  DISCORD_TOKEN    token do app no Discord. Sem ele o bot não sobe.
  GUILD_ID         ID de um servidor de teste: nele os comandos de barra aparecem na hora. O bot funciona em
                   vários servidores; nos outros os comandos levam até 1 h pra aparecer depois de mudarem.
  DONO_ID          ID de quem pode usar os comandos de administração (o do Mizuki está em dados/personagem/servidor.md).
  CANAIS           IDs dos canais em que o bot escuta, separados por vírgula. Vazio = todos.
  AVATAR_KALTSIT   URL da imagem que aparece nas mensagens da Kal'tsit.
  AVATAR_CLOSURE   URL da imagem que aparece nas mensagens da Closure.
  BANCO            caminho do SQLite de registro. Padrão: src/var/bot.sqlite3.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]  # a pasta Closure/
DADOS = RAIZ / "dados"


def ler_env(arquivo: Path) -> dict[str, str]:
    """Lê linhas CHAVE=valor; ignora vazias e comentários, tira aspas em volta do valor."""
    if not arquivo.exists():
        return {}
    pares = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        pares[chave.strip()] = valor.strip().strip("\"'")
    return pares


def _inteiro(valor: str | None) -> int | None:
    return int(valor) if valor and valor.strip().isdigit() else None


@dataclass(frozen=True)
class Config:
    token: str
    guild_id: int | None
    dono_id: int | None
    canais: frozenset[int]
    avatares: dict[str, str | None]
    banco: Path
    dados: Path = DADOS

    def escuta(self, canal_id: int) -> bool:
        return not self.canais or canal_id in self.canais


def carregar(arquivo: Path | None = None, ambiente: dict[str, str] | None = None) -> Config:
    valores = ler_env(arquivo or RAIZ / ".env")
    valores.update(os.environ if ambiente is None else ambiente)
    canais = frozenset(int(c) for c in valores.get("CANAIS", "").replace(" ", "").split(",") if c.isdigit())
    return Config(
        token=valores.get("DISCORD_TOKEN", ""),
        guild_id=_inteiro(valores.get("GUILD_ID")),
        dono_id=_inteiro(valores.get("DONO_ID")),
        canais=canais,
        avatares={
            "kaltsit": valores.get("AVATAR_KALTSIT") or None,
            "closure": valores.get("AVATAR_CLOSURE") or None,
        },
        banco=Path(valores.get("BANCO") or RAIZ / "src" / "var" / "bot.sqlite3"),
    )
