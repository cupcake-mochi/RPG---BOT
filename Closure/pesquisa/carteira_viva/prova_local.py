"""Prova LOCAL da fronteira entre OAuth verificado e cadastro.

Não é servidor OAuth nem prova de acesso real ao Google/Discord. Usa identidades
e respostas fictícias nos testes. Banco temporário próprio, fora da produção.
Não executa rede, não altera planilhas e não integra os comandos do bot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Callable

from cryptography.fernet import Fernet

from .contrato import Acao, Membro, permitido

DRIVE_FILE = "https://www.googleapis.com/auth/drive.file"
MIME_PLANILHA = "application/vnd.google-apps.spreadsheet"


class Recusa(ValueError):
    pass


class Revogada(Recusa):
    pass


@dataclass(frozen=True)
class AutorizacaoGoogle:
    """Saída de adaptador confiável, após validar código, estado e provedor."""
    conta: str
    refresh_token: str = field(repr=False)
    escopos: frozenset[str] = frozenset({DRIVE_FILE})


@dataclass(frozen=True)
class ArquivoGoogle:
    """Metadados confirmados com a API, não apenas o retorno JavaScript do Picker."""
    arquivo: str
    conta: str
    autorizado_app: bool = True
    mime: str = MIME_PLANILHA
    lixeira: bool = False
    contrato_compativel: bool = True


def resumo(valor: str) -> str:
    return hashlib.sha256(valor.encode()).hexdigest()


class Prova:
    """Modelo síncrono de um único serviço; não usar como persistência de produção.

    Renovação e leitura reais são substituídas por funções nos testes. A cifra
    associa conta, usuário e servidor; cópia de um envelope para outra chave falha.
    Tentativas OAuth em andamento expiram ao reiniciar; vínculos persistem.
    """

    def __init__(self, banco: Path, chave: bytes, agora: Callable[[], float] = time.time):
        self.cifra = Fernet(chave)
        self.agora = agora
        self.db = sqlite3.connect(banco, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS vinculos (
                servidor TEXT, personagem TEXT, dono TEXT, arquivo TEXT,
                conta TEXT, revisao INTEGER, segredo BLOB, ativo INTEGER,
                PRIMARY KEY (servidor, personagem), UNIQUE (servidor, arquivo));
            CREATE TABLE IF NOT EXISTS fluxos (
                estado TEXT PRIMARY KEY, servidor TEXT, usuario TEXT, personagem TEXT,
                revisao INTEGER, sessao TEXT, expira REAL, fase TEXT, conta TEXT,
                segredo BLOB, arquivo TEXT);
            DELETE FROM fluxos;
        """)

    def fechar(self):
        self.db.close()

    def iniciar(self, membro: Membro, personagem: str | None = None) -> str:
        atual = self.vinculo(membro.servidor, personagem) if personagem else None
        if personagem and not atual:
            raise Recusa("Personagem não encontrado neste servidor.")
        acao = Acao.TROCAR_ARQUIVO if atual else Acao.CADASTRAR
        if not permitido(acao, membro, membro.servidor, atual["dono"] if atual else None):
            raise Recusa("Você não pode iniciar esta operação.")
        estado = secrets.token_urlsafe(32)
        self.db.execute("INSERT INTO fluxos VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (resumo(estado), membro.servidor, membro.usuario,
                         personagem or secrets.token_urlsafe(16), atual["revisao"] if atual else 0,
                         None, self.agora() + 600, "discord", None, None, None))
        return estado

    def _fluxo(self, estado: str, membro: Membro, fase: str, sessao: str | None = None):
        f = self.db.execute("SELECT * FROM fluxos WHERE estado=?", (resumo(estado),)).fetchone()
        if (not f or f["expira"] <= self.agora() or f["fase"] != fase or
                not membro.presente or membro.usuario != f["usuario"] or
                membro.servidor != f["servidor"] or
                (sessao is not None and f["sessao"] != resumo(sessao))):
            raise Recusa("Operação expirada, já usada ou de outra sessão.")
        return f

    def identificar_discord(self, estado: str, membro: Membro, sessao: str):
        if not sessao:
            raise Recusa("Sessão do navegador ausente.")
        self._fluxo(estado, membro, "discord")
        self.db.execute("UPDATE fluxos SET fase='google', sessao=? WHERE estado=?",
                        (resumo(sessao), resumo(estado)))

    def receber_google(self, estado: str, membro: Membro, sessao: str, auth: AutorizacaoGoogle):
        f = self._fluxo(estado, membro, "google", sessao)
        if auth.escopos != frozenset({DRIVE_FILE}) or not auth.conta or not auth.refresh_token:
            raise Recusa("Escopo ou autorização durável não confirmado.")
        # Trocar arquivo não serve para trocar a identidade Google silenciosamente.
        atual = self.vinculo(f["servidor"], f["personagem"])
        if atual and atual["conta"] != auth.conta:
            raise Recusa("Use a conta vinculada; trocar conta exige reconexão separada.")
        payload = json.dumps({"servidor": membro.servidor, "usuario": membro.usuario,
                              "conta": auth.conta, "refresh": auth.refresh_token}).encode()
        self.db.execute("UPDATE fluxos SET fase='picker', conta=?, segredo=? WHERE estado=?",
                        (auth.conta, self.cifra.encrypt(payload), resumo(estado)))

    def selecionar(self, estado: str, membro: Membro, sessao: str, arquivo: ArquivoGoogle):
        f = self._fluxo(estado, membro, "picker", sessao)
        if (not arquivo.arquivo or arquivo.conta != f["conta"] or
                not arquivo.autorizado_app or arquivo.mime != MIME_PLANILHA or
                arquivo.lixeira or not arquivo.contrato_compativel):
            raise Recusa("Selecione uma ficha compatível e autorizada para o aplicativo.")
        self.db.execute("UPDATE fluxos SET fase='confirmar', arquivo=? WHERE estado=?",
                        (arquivo.arquivo, resumo(estado)))
        return {"personagem": f["personagem"], "arquivo_novo": arquivo.arquivo,
                "substituicao": f["revisao"] > 0}

    def confirmar(self, estado: str, membro: Membro, sessao: str) -> dict:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            f = self._fluxo(estado, membro, "confirmar", sessao)
            atual = self.vinculo(f["servidor"], f["personagem"])
            if f["revisao"] and (not atual or atual["revisao"] != f["revisao"] or
                                  atual["dono"] != membro.usuario):
                raise Recusa("A ficha mudou durante a operação. Comece novamente.")
            if not f["revisao"] and atual:
                raise Recusa("O personagem já foi cadastrado.")
            self.db.execute("""INSERT INTO vinculos VALUES (?,?,?,?,?,?,?,1)
                ON CONFLICT(servidor,personagem) DO UPDATE SET
                arquivo=excluded.arquivo, conta=excluded.conta,
                revisao=excluded.revisao, segredo=excluded.segredo, ativo=1""",
                            (f["servidor"], f["personagem"], f["usuario"], f["arquivo"],
                             f["conta"], f["revisao"] + 1, f["segredo"]))
            self.db.execute("DELETE FROM fluxos WHERE estado=?", (resumo(estado),))
            self.db.execute("COMMIT")
        except Exception as exc:
            self.db.execute("ROLLBACK")
            if isinstance(exc, sqlite3.IntegrityError):
                raise Recusa("Esse arquivo já tem um cadastro neste servidor.") from None
            raise
        return self.vinculo(f["servidor"], f["personagem"])

    def cancelar(self, estado: str, membro: Membro, sessao: str):
        # Exige identidade e sessão; não aceita cancelamento por conhecer só a URL.
        f = self.db.execute("SELECT fase FROM fluxos WHERE estado=?", (resumo(estado),)).fetchone()
        if not f:
            raise Recusa("Operação não encontrada.")
        self._fluxo(estado, membro, f["fase"], sessao)
        self.db.execute("DELETE FROM fluxos WHERE estado=?", (resumo(estado),))

    def vinculo(self, servidor: str, personagem: str | None) -> dict | None:
        # DTO interno para o serviço. A API pública deverá usar somente cartao_publico.
        row = self.db.execute("""SELECT servidor,personagem,dono,arquivo,conta,revisao,ativo
            FROM vinculos WHERE servidor=? AND personagem=?""", (servidor, personagem)).fetchone()
        return dict(row) if row else None

    def ler(self, membro: Membro, personagem: str, renovar, ler_faixa):
        """Prova limitada ao dono; revisão por equipe será integrada na etapa 4.

        Os callbacks são adaptadores confiáveis. Nenhuma URL fornecida pelo
        usuário é buscada aqui; a faixa é fixa e pequena na prova.
        """
        v = self.vinculo(membro.servidor, personagem)
        if not v or membro.usuario != v["dono"] or not membro.presente or not v["ativo"]:
            raise Recusa("Leitura indisponível para este usuário.")
        envelope = self.db.execute("SELECT segredo FROM vinculos WHERE servidor=? AND personagem=?",
                                   (membro.servidor, personagem)).fetchone()[0]
        secret = json.loads(self.cifra.decrypt(envelope))
        if (secret["servidor"], secret["usuario"], secret["conta"]) != (
                membro.servidor, membro.usuario, v["conta"]):
            raise Recusa("Conexão pertence a outro contexto.")
        try:
            token = renovar(secret["refresh"])
            dados = ler_faixa(token, v["arquivo"], "ANALISE!A1:B3")
        except Revogada:
            self.db.execute("""UPDATE vinculos SET ativo=0
                WHERE conta=? AND dono=?""", (v["conta"], membro.usuario))
            raise Recusa("Reconecte a conta Google para continuar.") from None
        atual = self.vinculo(membro.servidor, personagem)
        if not atual or atual["revisao"] != v["revisao"] or not atual["ativo"]:
            raise Recusa("A fonte mudou durante a leitura; resultado descartado.")
        return {"dados": dados, "revisao": v["revisao"], "lido_em": self.agora()}
