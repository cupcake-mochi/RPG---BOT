"""Registro em SQLite: chamadas de API, gatilhos e mensagens que o bot mandou.

  chamadas_api   uma linha por chamada ao modelo (modelo, tokens, latência, gatilho). É daqui que sai o
                 volume real pra conferir o gasto com o crédito mensal.
  gatilhos       uma linha por vez que alguém chamou uma personagem. Não guarda o texto da mensagem.
  paineis_clima  por servidor: o canal do painel diário de clima, o dia do último painel, o ID da mensagem
                 e o último estado mostrado. Fica aqui pra um reinício não postar de novo.
  falas          o texto das últimas respostas de cada personagem em cada canal (só o que ela disse, nunca o que
                 as pessoas escreveram). Serve pra ela não repetir a mesma abertura ou frase de uma conversa pra outra.
  mensagens_bot  ID de cada mensagem enviada por webhook e de quem era a fala. Mensagem de webhook não é da
                 conta do bot, então "responderam a uma mensagem dela" só se reconhece por esta tabela.
  paciencia      a paciência de cada personagem com cada pessoa (0 a 3) e o resumo embaralhado da última pergunta
                 dela, pra reconhecer pergunta repetida sem guardar o texto.
  fichas         o que as personagens sabem de cada pessoa: pronomes, se ela informou, e fatos curtos sobre o jogo.
                 A pessoa vê com /meus_dados e apaga com /apagar_meus_dados.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
CREATE TABLE IF NOT EXISTS falas (
    id INTEGER PRIMARY KEY,
    quando TEXT NOT NULL,
    canal_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    texto TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mensagens_bot (
    message_id INTEGER PRIMARY KEY,
    canal_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    quando TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS paciencia (
    autor_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    valor INTEGER NOT NULL,
    desde TEXT NOT NULL,
    pergunta TEXT,
    pergunta_quando TEXT,
    PRIMARY KEY (autor_id, persona)
);
CREATE TABLE IF NOT EXISTS fichas (
    autor_id INTEGER PRIMARY KEY,
    pronomes TEXT,
    fatos TEXT NOT NULL DEFAULT '[]'
);
"""


@dataclass(frozen=True)
class PainelClima:
    guild_id: int
    canal_id: int
    dia: str | None
    mensagem_id: int | None
    estado: str | None


@dataclass(frozen=True)
class Paciencia:
    valor: int  # na hora `desde`; quem lê soma o que o tempo devolveu (closure_bot/vida.py)
    desde: datetime
    pergunta: str | None
    pergunta_quando: datetime | None


@dataclass(frozen=True)
class Ficha:
    pronomes: str | None = None
    fatos: tuple[str, ...] = ()


FALAS_GUARDADAS = 30  # por personagem e por canal
FALAS_VALEM_HORAS = 12  # fala mais velha que um turno não conta mais como repetição


def _agora() -> str:
    return _iso(datetime.now(timezone.utc))


def _iso(quando: datetime) -> str:
    return quando.astimezone(timezone.utc).isoformat(timespec="seconds")


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

    def registrar_gatilho(self, *, canal_id: int, autor_id: int, persona: str, motivo: str, fora_do_plantao: bool,
                          quando: datetime | None = None) -> None:
        self._db.execute(
            "INSERT INTO gatilhos (quando, canal_id, autor_id, persona, motivo, fora_do_plantao) VALUES (?, ?, ?, ?, ?, ?)",
            (_iso(quando) if quando else _agora(), canal_id, autor_id, persona, motivo, int(fora_do_plantao)),
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

    def guardar_fala(self, *, canal_id: int, persona: str, texto: str, quando: datetime | None = None) -> None:
        """Guarda o que a personagem disse e mantém só as FALAS_GUARDADAS mais novas dela nesse canal."""
        self._db.execute("INSERT INTO falas (quando, canal_id, persona, texto) VALUES (?, ?, ?, ?)",
                         (_iso(quando) if quando else _agora(), canal_id, persona, texto))
        self._db.execute(
            "DELETE FROM falas WHERE canal_id = ? AND persona = ? AND id NOT IN"
            " (SELECT id FROM falas WHERE canal_id = ? AND persona = ? ORDER BY id DESC LIMIT ?)",
            (canal_id, persona, canal_id, persona, FALAS_GUARDADAS))
        self._db.commit()

    def ultimas_falas(self, *, canal_id: int, persona: str, limite: int = 6, horas: float = FALAS_VALEM_HORAS,
                      agora: datetime | None = None) -> list[str]:
        """As últimas respostas da personagem nesse canal, da mais antiga pra mais nova.

        São dois limites, pra ela não ter que inventar pra sempre: só as `limite` mais novas, e só as das
        últimas `horas`. Passou disso, a frase volta a ser dela."""
        desde = _iso((agora or datetime.now(timezone.utc)) - timedelta(hours=horas))
        linhas = self._db.execute(
            "SELECT texto FROM falas WHERE canal_id = ? AND persona = ? AND quando >= ? ORDER BY id DESC LIMIT ?",
            (canal_id, persona, desde, limite)).fetchall()
        return [linha[0] for linha in reversed(linhas)]

    def respostas_desde(self, *, persona: str, desde: datetime) -> int:
        """Quantas mensagens a personagem mandou de `desde` pra cá, em todos os canais."""
        return self._db.execute("SELECT COUNT(*) FROM mensagens_bot WHERE persona = ? AND quando >= ?",
                                (persona, _iso(desde))).fetchone()[0]

    def dias_de_conversa(self, *, autor_id: int, persona: str) -> int:
        """Em quantos dias diferentes (de Brasília, UTC-3) a pessoa chamou essa personagem."""
        return self._db.execute(
            "SELECT COUNT(DISTINCT date(quando, '-3 hours')) FROM gatilhos WHERE autor_id = ? AND persona = ?",
            (autor_id, persona)).fetchone()[0]

    def paciencia(self, *, autor_id: int, persona: str) -> Paciencia | None:
        linha = self._db.execute("SELECT valor, desde, pergunta, pergunta_quando FROM paciencia WHERE autor_id = ? AND persona = ?",
                                 (autor_id, persona)).fetchone()
        if not linha:
            return None
        return Paciencia(linha[0], datetime.fromisoformat(linha[1]), linha[2], datetime.fromisoformat(linha[3]) if linha[3] else None)

    def gravar_paciencia(self, *, autor_id: int, persona: str, valor: int, desde: datetime,
                         pergunta: str | None, pergunta_quando: datetime | None) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO paciencia (autor_id, persona, valor, desde, pergunta, pergunta_quando) VALUES (?, ?, ?, ?, ?, ?)",
            (autor_id, persona, valor, _iso(desde), pergunta, _iso(pergunta_quando) if pergunta_quando else None))
        self._db.commit()

    def ficha(self, autor_id: int) -> Ficha:
        linha = self._db.execute("SELECT pronomes, fatos FROM fichas WHERE autor_id = ?", (autor_id,)).fetchone()
        return Ficha(linha[0], tuple(json.loads(linha[1]))) if linha else Ficha()

    def gravar_ficha(self, autor_id: int, ficha: Ficha) -> None:
        self._db.execute("INSERT OR REPLACE INTO fichas (autor_id, pronomes, fatos) VALUES (?, ?, ?)",
                         (autor_id, ficha.pronomes, json.dumps(list(ficha.fatos), ensure_ascii=False)))
        self._db.commit()

    def apagar_pessoa(self, autor_id: int) -> None:
        """Apaga tudo o que o bot guarda de uma pessoa: ficha, paciência e o histórico de quando ela chamou."""
        for tabela in ("fichas", "paciencia", "gatilhos"):
            self._db.execute(f"DELETE FROM {tabela} WHERE autor_id = ?", (autor_id,))
        self._db.commit()

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
