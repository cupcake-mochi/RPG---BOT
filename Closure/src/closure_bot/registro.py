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
  fichas         o que as personagens sabem de cada pessoa: pronomes, se ela informou, e até 15 fatos curtos.
                 A pessoa vê com /meus_dados e apaga com /apagar_meus_dados.
  mensagens_do_dia  o texto das mensagens em que alguém chamou uma personagem, só até a reflexão das 4h30
                 (closure_bot/reflexao.py), que tira os fatos e apaga o texto.
  conversas_recentes  últimos turnos cifrados por canal/personagem; expiram após 30 minutos sem conversa ou às 4h30.
  participantes_conversa  IDs locais para apagar o fio completo quando um participante apaga seus dados.

Com a CHAVE_DO_BANCO no .env, o texto que fala de gente vai cifrado pro disco: falas, mensagens do dia, pronomes e
fatos. IDs, horas e contagens ficam em claro, porque as consultas dependem deles.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS conversas_recentes (
    canal_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    expira TEXT NOT NULL,
    texto TEXT NOT NULL,
    PRIMARY KEY (canal_id, persona)
);
CREATE TABLE IF NOT EXISTS participantes_conversa (
    canal_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    autor_id INTEGER NOT NULL,
    PRIMARY KEY (canal_id, persona, autor_id)
);
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
CREATE TABLE IF NOT EXISTS mensagens_do_dia (
    message_id INTEGER PRIMARY KEY,
    quando TEXT NOT NULL,
    autor_id INTEGER NOT NULL,
    persona TEXT NOT NULL,
    texto TEXT NOT NULL
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


@dataclass(frozen=True)
class MensagemDoDia:
    message_id: int
    autor_id: int
    persona: str
    texto: str


FATOS_MAX = 15  # por pessoa; passando disso sai o mais velho
FALAS_GUARDADAS = 30  # por personagem e por canal
FALAS_VALEM_HORAS = 12  # fala mais velha que um turno não conta mais como repetição


class Cofre:
    """Cifra e abre texto com a chave do .env (Fernet, da biblioteca cryptography). Sem chave, o texto passa em claro."""

    MARCA = "gAAAA"  # todo texto cifrado pelo Fernet começa assim

    def __init__(self, chave: str | None = None):
        self._fernet = None
        if chave:
            from cryptography.fernet import Fernet  # só é preciso com chave definida

            self._fernet = Fernet(chave.encode())

    @property
    def ligado(self) -> bool:
        return self._fernet is not None

    @staticmethod
    def nova_chave() -> str:
        from cryptography.fernet import Fernet

        return Fernet.generate_key().decode()

    def fechar(self, texto: str | None) -> str | None:
        if texto is None or not self._fernet:
            return texto
        return self._fernet.encrypt(texto.encode()).decode()

    def abrir(self, guardado: str | None) -> str | None:
        """Devolve None quando o texto está cifrado e não abre (sem chave, ou chave trocada): melhor esquecer do que
        mandar letra embaralhada pro modelo. Texto antigo, gravado em claro, volta como está."""
        if guardado is None or not guardado.startswith(self.MARCA):
            return guardado
        if not self._fernet:
            return None
        from cryptography.fernet import InvalidToken

        try:
            return self._fernet.decrypt(guardado.encode()).decode()
        except InvalidToken:
            return None


def _agora() -> str:
    return _iso(datetime.now(timezone.utc))


def _iso(quando: datetime) -> str:
    return quando.astimezone(timezone.utc).isoformat(timespec="seconds")


@dataclass(eq=False)
class LeituraDados:
    """Só vive durante uma operação assíncrona; exclusão invalida a cópia em uso."""
    autores: frozenset[int]
    apagados: set[int] = field(default_factory=set)


class Registro:
    def __init__(self, caminho: Path | str, chave: str | None = None):
        self.cofre = Cofre(chave)
        self._leituras: list[LeituraDados] = []
        if str(caminho) != ":memory:":
            Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(caminho), check_same_thread=False)
        self._db.executescript(ESQUEMA)
        # Migração aditiva: o banco da hospedagem mantém todo o histórico.
        colunas = {r[1] for r in self._db.execute("PRAGMA table_info(chamadas_api)")}
        for nome, tipo in {"tokens_resposta": "INTEGER", "tokens_raciocinio": "INTEGER",
                           "tokens_cache": "INTEGER", "cortada": "INTEGER", "fim": "TEXT",
                           "raciocinio": "TEXT", "custo_estimado_usd": "REAL",
                           "reserva_sem_uso_usd": "REAL NOT NULL DEFAULT 0"}.items():
            if nome not in colunas:
                self._db.execute(f"ALTER TABLE chamadas_api ADD COLUMN {nome} {tipo}")
        self._db.commit()

    def fechar(self) -> None:
        self._db.close()

    def registrar_chamada(self, *, modelo: str, persona: str | None = None, gatilho: str | None = None,
                          tokens_entrada: int | None = None, tokens_saida: int | None = None,
                          latencia_ms: int | None = None, ok: bool = True, erro: str | None = None,
                          tokens_resposta: int | None = None, tokens_raciocinio: int | None = None,
                          tokens_cache: int | None = None, cortada: bool | None = None, fim: str | None = None,
                          raciocinio: str | None = None, custo_estimado_usd: float | None = None,
                          reserva_sem_uso_usd: float = 0.0) -> None:
        self._db.execute(
            "INSERT INTO chamadas_api (quando, modelo, persona, gatilho, tokens_entrada, tokens_saida, latencia_ms, ok, erro,"
            " tokens_resposta, tokens_raciocinio, tokens_cache, cortada, fim, raciocinio, custo_estimado_usd, reserva_sem_uso_usd)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (_agora(), modelo, persona, gatilho, tokens_entrada, tokens_saida, latencia_ms, int(ok), erro,
             tokens_resposta, tokens_raciocinio, tokens_cache, cortada, fim, raciocinio, custo_estimado_usd, reserva_sem_uso_usd),
        )
        self._db.commit()

    def tokens_do_mes(self, quando: datetime) -> list[tuple[str, int, int]]:
        """(modelo, tokens de entrada, tokens de saída) somados das chamadas que deram certo no mês de `quando` (UTC)."""
        linhas = self._db.execute(
            "SELECT modelo, COALESCE(SUM(tokens_entrada), 0), COALESCE(SUM(tokens_saida), 0) FROM chamadas_api"
            " WHERE ok = 1 AND substr(quando, 1, 7) = ? GROUP BY modelo ORDER BY modelo", (quando.strftime("%Y-%m"),))
        return [tuple(linha) for linha in linhas]

    def consumo_do_mes(self, quando: datetime) -> list[tuple]:
        """Consumo para o limite: inclui reserva cautelar de uso desconhecido, sem somar duas vezes.

        A reserva não é cobrança confirmada; custo antigo é recalculado pela data da chamada.
        """
        # (modelo, quando, entrada, saída, cache, custo estimado, reserva): quem soma escolhe o preço e fica com o maior
        # entre custo e reserva, pra não contar duas vezes.
        return self._db.execute(
            "SELECT modelo, quando, COALESCE(tokens_entrada, 0), COALESCE(tokens_saida, 0),"
            " COALESCE(tokens_cache, 0), custo_estimado_usd, COALESCE(reserva_sem_uso_usd, 0) FROM chamadas_api"
            " WHERE substr(quando, 1, 7) = ?", (quando.strftime("%Y-%m"),)).fetchall()

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
                         (_iso(quando) if quando else _agora(), canal_id, persona, self.cofre.fechar(texto)))
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
        abertas = (self.cofre.abrir(linha[0]) for linha in reversed(linhas))
        return [texto for texto in abertas if texto is not None]

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
        if not linha:
            return Ficha()
        return Ficha(self.cofre.abrir(linha[0]), tuple(json.loads(self.cofre.abrir(linha[1]) or "[]")))

    def gravar_ficha(self, autor_id: int, ficha: Ficha) -> None:
        """Os fatos ficam do mais velho pro mais novo; passando de FATOS_MAX, os mais velhos saem."""
        self._db.execute("INSERT OR REPLACE INTO fichas (autor_id, pronomes, fatos) VALUES (?, ?, ?)",
                         (autor_id, self.cofre.fechar(ficha.pronomes),
                          self.cofre.fechar(json.dumps(list(ficha.fatos)[-FATOS_MAX:], ensure_ascii=False))))
        self._db.commit()

    def guardar_mensagem_do_dia(self, *, message_id: int, autor_id: int, persona: str, texto: str,
                                quando: datetime | None = None) -> None:
        self._db.execute("INSERT OR REPLACE INTO mensagens_do_dia (message_id, quando, autor_id, persona, texto) VALUES (?, ?, ?, ?, ?)",
                         (message_id, _iso(quando) if quando else _agora(), autor_id, persona, self.cofre.fechar(texto)))
        self._db.commit()

    def mensagens_do_dia(self) -> list[MensagemDoDia]:
        linhas = self._db.execute("SELECT message_id, autor_id, persona, texto FROM mensagens_do_dia ORDER BY message_id")
        abertas = [MensagemDoDia(m, autor, persona, self.cofre.abrir(texto)) for m, autor, persona, texto in linhas]
        return [m for m in abertas if m.texto is not None]

    def mensagem_do_dia_mais_antiga(self) -> datetime | None:
        linha = self._db.execute("SELECT MIN(quando) FROM mensagens_do_dia").fetchone()
        return datetime.fromisoformat(linha[0]) if linha and linha[0] else None

    def apagar_mensagens_do_dia(self, ids: list[int] | None = None) -> None:
        """Sem `ids`, apaga todas. Com eles, só as que entraram na reflexão (as que chegaram durante ela ficam pra próxima)."""
        if ids is None:
            self._db.execute("DELETE FROM mensagens_do_dia")
        else:
            self._db.executemany("DELETE FROM mensagens_do_dia WHERE message_id = ?", [(i,) for i in ids])
        self._db.commit()

    @contextmanager
    def proteger_dados(self, autores):
        leitura = LeituraDados(frozenset(autores))
        self._leituras.append(leitura)
        try:
            yield leitura
        finally:
            self._leituras.remove(leitura)

    def autores_conversa(self, canal_id: int, persona: str) -> set[int]:
        return {r[0] for r in self._db.execute(
            "SELECT autor_id FROM participantes_conversa WHERE canal_id = ? AND persona = ?",
            (canal_id, persona))}

    def apagar_pessoa(self, autor_id: int) -> None:
        """Apaga tudo o que o bot guarda de uma pessoa: ficha, paciência, mensagens do dia e o histórico de quando ela chamou."""
        # A resposta e falas dos demais podem citar a pessoa: apague o fio todo.
        fios = list(self._db.execute("SELECT canal_id, persona FROM participantes_conversa WHERE autor_id = ?", (autor_id,)))
        for canal, persona in fios:
            self._db.execute("DELETE FROM conversas_recentes WHERE canal_id = ? AND persona = ?", (canal, persona))
            self._db.execute("DELETE FROM participantes_conversa WHERE canal_id = ? AND persona = ?", (canal, persona))
            self._db.execute("DELETE FROM falas WHERE canal_id = ? AND persona = ?", (canal, persona))
        for tabela in ("fichas", "paciencia", "gatilhos", "mensagens_do_dia"):
            self._db.execute(f"DELETE FROM {tabela} WHERE autor_id = ?", (autor_id,))
        self._db.commit()
        # Uma chamada já enviada pode terminar depois da exclusão. A resposta
        # continua contabilizada, mas não pode recriar dados que foram apagados.
        for leitura in self._leituras:
            if autor_id in leitura.autores:
                leitura.apagados.add(autor_id)

    def limpar_conversas(self, agora: datetime) -> None:
        self._db.execute("DELETE FROM conversas_recentes WHERE expira <= ?", (_iso(agora),))
        self._db.execute("DELETE FROM participantes_conversa WHERE NOT EXISTS (SELECT 1 FROM conversas_recentes c "
                         "WHERE c.canal_id = participantes_conversa.canal_id AND c.persona = participantes_conversa.persona)")
        self._db.commit()

    def ler_conversa(self, canal_id: int, persona: str, agora: datetime) -> list[dict]:
        self.limpar_conversas(agora)
        linha = self._db.execute("SELECT texto FROM conversas_recentes WHERE canal_id = ? AND persona = ?",
                                (canal_id, persona)).fetchone()
        aberto = self.cofre.abrir(linha[0]) if linha else None
        return json.loads(aberto) if aberto else []

    def guardar_conversa(self, canal_id: int, persona: str, turnos: list[dict], expira: datetime) -> None:
        with self._db:
            self._db.execute("INSERT OR REPLACE INTO conversas_recentes VALUES (?, ?, ?, ?)",
                             (canal_id, persona, _iso(expira), self.cofre.fechar(json.dumps(turnos, ensure_ascii=False))))
            # Conserve participantes até o fio expirar: uma resposta posterior
            # ainda pode citar quem já saiu dos últimos 12 turnos.
            self._db.executemany("INSERT OR IGNORE INTO participantes_conversa VALUES (?, ?, ?)",
                                 [(canal_id, persona, t['autor_id']) for t in turnos if t.get('autor_id') is not None])

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
