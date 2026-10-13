"""Registro em SQLite: chamadas de API, gatilhos e mensagens que o bot mandou.

  chamadas_api   uma linha por chamada ao modelo (modelo, tokens, latência, gatilho). É daqui que sai o
                 volume real pra conferir o gasto com o crédito mensal.
  gatilhos       uma linha por vez que alguém chamou uma personagem. Não guarda o texto da mensagem.
  paineis_clima  por servidor: o canal do painel diário de clima, o dia do último painel, o ID da mensagem
                 e o último estado mostrado. Fica aqui pra um reinício não postar de novo.
  mensagens_bot  ID de cada mensagem enviada por webhook e de quem era a fala. Mensagem de webhook não é da
                 conta do bot, então "responderam a uma mensagem dela" só se reconhece por esta tabela.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS chamadas_api (
    id INTEGER PRIMARY KEY,
    quando TEXT NOT NULL,
    modelo TEXT NOT NULL,
    persona TEXT,
    gatilho TEXT,
    tokens_entrada INTEGER,
    tokens_saida INTEGER,
    latencia_ms INTEGER,
    ok INTEGER NOT NULL,
    erro TEXT
);
CREATE TABLE IF NOT EXISTS gatilhos (
    id INTEGER PRIMARY KEY,
    quando TEXT NOT NULL,
    canal_id INTEGER NOT NULL,
    autor_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    motivo TEXT NOT NULL,
    fora_do_plantao INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS paineis_clima (
    guild_id INTEGER PRIMARY KEY,
    canal_id INTEGER NOT NULL,
    dia TEXT,
    mensagem_id INTEGER,
    estado TEXT
);
CREATE TABLE IF NOT EXISTS mensagens_bot (
    message_id INTEGER PRIMARY KEY,
    canal_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    quando TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class PainelClima:
    guild_id: int
    canal_id: int
    dia: str | None
    mensagem_id: int | None
    estado: str | None


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Registro:
    def __init__(self, caminho: Path | str):
        if str(caminho) != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(caminho), check_same_thread=False)
        self._db.executescript(ESQUEMA)
        self._db.commit()

    def fechar(self) -> None:
        self._db.close()

    def registrar_chamada(self, *, modelo: str, persona: str | None = None, gatilho: str | None = None,
                          tokens_entrada: int | None = None, tokens_saida: int | None = None,
                          latencia_ms: int | None = None, ok: bool = True, erro: str | None = None) -> None:
        self._db.execute(
            "INSERT INTO chamadas_api (quando, modelo, persona, gatilho, tokens_entrada, tokens_saida, latencia_ms, ok, erro)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (_agora(), modelo, persona, gatilho, tokens_entrada, tokens_saida, latencia_ms, int(ok), erro),
        )
        self._db.commit()

    def tokens_do_mes(self, quando: datetime) -> list[tuple[str, int, int]]:
        """(modelo, tokens de entrada, tokens de saída) somados das chamadas que deram certo no mês de `quando` (UTC)."""
        linhas = self._db.execute(
            "SELECT modelo, COALESCE(SUM(tokens_entrada), 0), COALESCE(SUM(tokens_saida), 0) FROM chamadas_api"
            " WHERE ok = 1 AND substr(quando, 1, 7) = ? GROUP BY modelo ORDER BY modelo", (quando.strftime("%Y-%m"),))
        return [tuple(linha) for linha in linhas]

    def registrar_gatilho(self, *, canal_id: int, autor_id: int, persona: str, motivo: str, fora_do_plantao: bool) -> None:
        self._db.execute(
            "INSERT INTO gatilhos (quando, canal_id, autor_id, persona, motivo, fora_do_plantao) VALUES (?, ?, ?, ?, ?, ?)",
            (_agora(), canal_id, autor_id, persona, motivo, int(fora_do_plantao)),
        )
        self._db.commit()

    def registrar_mensagem(self, *, message_id: int, canal_id: int, persona: str) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO mensagens_bot (message_id, canal_id, persona, quando) VALUES (?, ?, ?, ?)",
            (message_id, canal_id, persona, _agora()),
        )
        self._db.commit()

    def persona_da_mensagem(self, message_id: int) -> str | None:
        linha = self._db.execute("SELECT persona FROM mensagens_bot WHERE message_id = ?", (message_id,)).fetchone()
        return linha[0] if linha else None

    def definir_painel(self, *, guild_id: int, canal_id: int) -> None:
        """Liga o painel diário do servidor nesse canal (ou troca de canal); o próximo passo posta um painel novo."""
        self._db.execute(
            "INSERT OR REPLACE INTO paineis_clima (guild_id, canal_id, dia, mensagem_id, estado) VALUES (?, ?, NULL, NULL, NULL)",
            (guild_id, canal_id),
        )
        self._db.commit()

    def remover_painel(self, guild_id: int) -> bool:
        apagadas = self._db.execute("DELETE FROM paineis_clima WHERE guild_id = ?", (guild_id,)).rowcount
        self._db.commit()
        return apagadas > 0

    def marcar_painel(self, guild_id: int, *, dia: str, mensagem_id: int, estado: str) -> None:
        self._db.execute("UPDATE paineis_clima SET dia = ?, mensagem_id = ?, estado = ? WHERE guild_id = ?",
                         (dia, mensagem_id, estado, guild_id))
        self._db.commit()

    def paineis(self) -> list[PainelClima]:
        linhas = self._db.execute("SELECT guild_id, canal_id, dia, mensagem_id, estado FROM paineis_clima ORDER BY guild_id")
        return [PainelClima(*linha) for linha in linhas]

    def painel(self, guild_id: int) -> PainelClima | None:
        return next((p for p in self.paineis() if p.guild_id == guild_id), None)

    def contagens(self) -> dict[str, int]:
        return {t: self._db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("chamadas_api", "gatilhos", "mensagens_bot", "paineis_clima")}
