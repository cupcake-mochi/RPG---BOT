"""Migrações transacionais exclusivas do banco da Carteira viva."""
from .segredos import ErroCarteira

APPLICATION_ID = 0x43564956
VERSAO = 2

MIGRACOES = {
    1: (
        "CREATE TABLE meta (chave TEXT PRIMARY KEY, valor BLOB NOT NULL)",
        """CREATE TABLE servidores (
            id TEXT PRIMARY KEY, revisao INTEGER NOT NULL DEFAULT 0,
            campos_publicos TEXT NOT NULL, idioma TEXT NOT NULL DEFAULT 'pt-BR'
            CHECK(idioma IN ('pt-BR','en')))""",
        """CREATE TABLE cargos (
            servidor TEXT NOT NULL REFERENCES servidores(id) ON DELETE CASCADE,
            cargo TEXT NOT NULL, capacidade TEXT NOT NULL CHECK(capacidade IN ('revisao','edicao')),
            PRIMARY KEY(servidor,cargo,capacidade))""",
        """CREATE TABLE conexoes (
            id TEXT PRIMARY KEY, usuario TEXT NOT NULL, conta_hash TEXT NOT NULL,
            cliente_hash TEXT NOT NULL, segredo BLOB, criado REAL NOT NULL,
            atualizado REAL NOT NULL, sem_uso_desde REAL, autorizacao TEXT NOT NULL,
            estado TEXT NOT NULL CHECK(estado IN ('ativa','revogada','desconectada')),
            UNIQUE(usuario,conta_hash,cliente_hash))""",
        """CREATE TABLE personagens (
            servidor TEXT NOT NULL REFERENCES servidores(id), id TEXT NOT NULL,
            dono TEXT NOT NULL, perfil BLOB NOT NULL, campos_publicos TEXT NOT NULL,
            criado REAL NOT NULL, atualizado REAL NOT NULL, ausente_em REAL,
            PRIMARY KEY(servidor,id))""",
        """CREATE TABLE fontes (
            servidor TEXT NOT NULL, personagem TEXT NOT NULL,
            conexao TEXT NOT NULL REFERENCES conexoes(id), arquivo TEXT NOT NULL,
            contrato TEXT NOT NULL, revisao INTEGER NOT NULL CHECK(revisao>0),
            geracao INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(servidor,personagem), UNIQUE(servidor,arquivo),
            FOREIGN KEY(servidor,personagem) REFERENCES personagens(servidor,id) ON DELETE CASCADE)""",
        """CREATE TABLE leituras (
            servidor TEXT NOT NULL, personagem TEXT NOT NULL, id TEXT NOT NULL,
            revisao INTEGER NOT NULL, schema TEXT NOT NULL, criado REAL NOT NULL,
            expira REAL NOT NULL, conteudo BLOB NOT NULL,
            PRIMARY KEY(servidor,personagem),
            FOREIGN KEY(servidor,personagem) REFERENCES personagens(servidor,id) ON DELETE CASCADE)""",
        """CREATE TABLE analises (
            servidor TEXT NOT NULL, personagem TEXT NOT NULL, leitura_id TEXT NOT NULL,
            revisao INTEGER NOT NULL, campanha_revisao TEXT NOT NULL,
            criado REAL NOT NULL, expira REAL NOT NULL, conteudo BLOB NOT NULL,
            PRIMARY KEY(servidor,personagem),
            FOREIGN KEY(servidor,personagem) REFERENCES personagens(servidor,id) ON DELETE CASCADE)""",
        "CREATE INDEX personagens_dono ON personagens(servidor,dono,ausente_em,id)",
        "CREATE INDEX fontes_conexao ON fontes(conexao)",
    ),
    2: (
        """CREATE TABLE pedidos (
            servidor TEXT NOT NULL, usuario TEXT NOT NULL, chave TEXT NOT NULL,
            tipo TEXT NOT NULL, assinatura TEXT NOT NULL, personagem TEXT NOT NULL,
            criado REAL NOT NULL, PRIMARY KEY(servidor,usuario,chave))""",
        """CREATE TABLE auditoria (
            id INTEGER PRIMARY KEY, servidor TEXT NOT NULL, ator TEXT NOT NULL,
            personagem TEXT, acao TEXT NOT NULL, criado REAL NOT NULL)""",
        "CREATE INDEX auditoria_retencao ON auditoria(criado)",
    ),
}


def conferir_banco(db):
    app = db.execute("PRAGMA application_id").fetchone()[0]
    versao = db.execute("PRAGMA user_version").fetchone()[0]
    tabelas = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    if app != APPLICATION_ID and (app or versao or tabelas):
        raise ErroCarteira("Este arquivo não é um banco da Carteira viva.")
    if versao > VERSAO:
        raise ErroCarteira("Banco criado por uma versão mais nova da Carteira.")
    return versao


def migrar(db):
    """Chamado dentro da transação de abertura; sem executescript/commit implícito."""
    versao = conferir_banco(db)
    for numero in range(versao + 1, VERSAO + 1):
        for sql in MIGRACOES[numero]:
            db.execute(sql)
        db.execute(f"PRAGMA user_version={numero}")
    db.execute(f"PRAGMA application_id={APPLICATION_ID}")
