"""Armazenamento da Carteira viva, sem integração com Google ou Discord.

As identidades e escolhas de arquivo são entradas de adaptadores autenticados
do servidor. Este módulo não deve ser exposto diretamente como uma API HTTP.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time
from typing import Callable

from . import esquema
from .cartoes_banco import Cartoes
from .modelos import Modelos
from .permissoes import Acao, Membro, Permissoes, PUBLICOS, cartao_publico, permitido
from .segredos import AcessoNegado, Cifra, Conflito, ErroCarteira, json_bytes

DIA = 86400
MAX_JSON = 8 * 1024 * 1024
CAMPOS_PADRAO = PUBLICOS - {"idade", "cla", "origem", "caminho"}
LEDGER_ID = 0x43564C47


def digest(valor: str) -> str:
    return hashlib.sha256(valor.encode()).hexdigest()


def texto(valor, nome: str, limite: int = 200) -> str:
    if not isinstance(valor, str) or not valor.strip() or len(valor) > limite:
        raise ErroCarteira(f"{nome} inválido.")
    return valor.strip()


def arquivo_privado(path: Path) -> bool:
    """Não sobrescreve arquivos; cria somente arquivos próprios com 0600."""
    if path.is_symlink():
        raise ErroCarteira("Não use links simbólicos para os dados da Carteira.")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        if not path.is_file():
            raise ErroCarteira("Caminho de dados inválido.") from None
        return False
    else:
        os.close(fd)
        return True


@dataclass(frozen=True)
class ReferenciaLeitura:
    servidor: str
    personagem: str
    ator: str
    revisao: int
    geracao: int
    arquivo: str
    conexao: str


@dataclass(frozen=True)
class CredencialGoogle:
    conta: str = field(repr=False)
    cliente: str = field(repr=False)
    refresh_token: str = field(repr=False)
    autorizacao: str = field(repr=False)


class Cadastro(Cartoes, Modelos):
    def __init__(self, caminho: Path, chaves: tuple[bytes, ...], *,
                 remocoes: Path | None = None, agora: Callable[[], float] = time.time):
        self.cifra = Cifra(chaves)  # Não criar banco se a chave estiver ausente/inválida.
        self.caminho = Path(caminho).absolute()
        self.remocoes = Path(remocoes).absolute() if remocoes else self.caminho.with_suffix(".remocoes.sqlite3")
        if self.caminho == self.remocoes:
            raise ErroCarteira("Use arquivos distintos para cadastro e registro de remoções.")
        self.agora = agora
        novo = not self.caminho.exists()
        if not novo and not self.remocoes.exists():
            raise ErroCarteira("Falta o registro de remoções. Recupere-o antes de abrir o cadastro.")
        if novo and self.remocoes.exists():
            raise ErroCarteira("Já há um registro de remoções neste destino.")
        # A criação exclusiva é a autoridade, não a sondagem anterior: outro
        # inicializador pode ter criado o arquivo entre exists() e open().
        novo = arquivo_privado(self.caminho)
        if not novo and not self.remocoes.exists():
            raise ErroCarteira("Cadastro em inicialização ou sem registro de remoções. Tente novamente após conferir os arquivos.")
        novo_ledger = arquivo_privado(self.remocoes)
        self.db = sqlite3.connect(self.caminho, isolation_level=None, timeout=5)
        self.db.row_factory = sqlite3.Row
        try:
            self.db.execute("PRAGMA foreign_keys=ON")
            self.db.execute("PRAGMA trusted_schema=OFF")
            esquema.conferir_banco(self.db)
            if not novo:
                uid = self.db.execute("SELECT valor FROM meta WHERE chave='banco_id'").fetchone()[0]
                verificador = self.db.execute("SELECT valor FROM meta WHERE chave='verificador'").fetchone()[0]
                if self.cifra.abrir(["verificador", uid], verificador) != "carteira-viva":
                    raise ErroCarteira("Verificador de cifra inválido.")
            # DELETE permite atomicidade entre banco principal e ledger anexado.
            # Não mudar para WAL sem rever a recuperação entre os dois arquivos.
            self.db.execute("PRAGMA journal_mode=DELETE")
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("PRAGMA secure_delete=ON")
            self.db.execute("ATTACH DATABASE ? AS remocoes", (str(self.remocoes),))
            ledger_app = self.db.execute("PRAGMA remocoes.application_id").fetchone()[0]
            if not novo_ledger and ledger_app != LEDGER_ID:
                raise ErroCarteira("Registro de remoções incompatível.")
            self.db.execute("PRAGMA remocoes.journal_mode=DELETE")
            self.db.execute("PRAGMA remocoes.synchronous=FULL")
            with self._transacao():
                esquema.migrar(self.db)
                if novo:
                    uid = secrets.token_hex(16)
                    self.db.execute("INSERT INTO meta VALUES ('banco_id',?)", (uid,))
                    self.db.execute("INSERT INTO meta VALUES ('verificador',?)",
                                    (self.cifra.cifrar(["verificador", uid], "carteira-viva"),))
                self.banco_id = uid
                if novo_ledger:
                    self.db.execute("CREATE TABLE remocoes.meta (banco_id TEXT PRIMARY KEY)")
                    self.db.execute("INSERT INTO remocoes.meta VALUES (?)", (uid,))
                    self.db.execute("""CREATE TABLE remocoes.exclusoes (
                        servidor TEXT NOT NULL, personagem TEXT NOT NULL, criado REAL NOT NULL,
                        PRIMARY KEY(servidor,personagem))""")
                    self.db.execute("""CREATE TABLE remocoes.autorizacoes (
                        conexao TEXT NOT NULL, autorizacao TEXT NOT NULL, criado REAL NOT NULL,
                        PRIMARY KEY(conexao,autorizacao))""")
                    self.db.execute(f"PRAGMA remocoes.application_id={LEDGER_ID}")
                    self.db.execute("PRAGMA remocoes.user_version=1")
                if self.db.execute("PRAGMA remocoes.user_version").fetchone()[0] != 1:
                    raise ErroCarteira("Versão do registro de remoções incompatível.")
                ledger_uid = self.db.execute("SELECT banco_id FROM remocoes.meta").fetchone()[0]
                if ledger_uid != uid:
                    raise ErroCarteira("Registro de remoções pertence a outro cadastro.")
                self._reaplicar_remocoes()
                # Retornos OAuth de antes de um reinício/restore não reativam
                # concessões antigas. Os vínculos confirmados são preservados.
                self.db.execute("DELETE FROM web_fluxos")
                self.db.execute("DELETE FROM web_sessoes")
                self.db.execute("DELETE FROM previas_cartao")
        except Exception:
            self.db.close()
            if novo:
                self.caminho.unlink(missing_ok=True)
            if novo_ledger:
                self.remocoes.unlink(missing_ok=True)
            raise

    def fechar(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.fechar()

    @contextmanager
    def _transacao(self):
        savepoint = "cv_" + secrets.token_hex(8) if self.db.in_transaction else None
        self.db.execute(f"SAVEPOINT {savepoint}" if savepoint else "BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute(f"RELEASE {savepoint}" if savepoint else "COMMIT")
        except BaseException:
            if savepoint:
                self.db.execute(f"ROLLBACK TO {savepoint}")
                self.db.execute(f"RELEASE {savepoint}")
            else:
                self.db.execute("ROLLBACK")
            raise

    def _membro(self, membro: Membro):
        if not membro.presente:
            raise AcessoNegado("Entre no servidor para usar este recurso.")
        texto(membro.servidor, "Servidor")
        texto(membro.usuario, "Usuário")

    def _servidor(self, servidor: str):
        self.db.execute("INSERT OR IGNORE INTO servidores(id,campos_publicos) VALUES (?,?)",
                        (servidor, json.dumps(sorted(PUBLICOS))))

    def _permissoes(self, servidor: str) -> Permissoes:
        rows = self.db.execute("SELECT cargo,capacidade FROM cargos WHERE servidor=?", (servidor,)).fetchall()
        return Permissoes(frozenset(r["cargo"] for r in rows if r["capacidade"] == "revisao"),
                          frozenset(r["cargo"] for r in rows if r["capacidade"] == "edicao"))

    def _autorizar(self, membro: Membro, acao: Acao, dono: str | None = None):
        self._membro(membro)
        if not permitido(acao, membro, membro.servidor, dono, self._permissoes(membro.servidor)):
            raise AcessoNegado("Você não tem acesso a esta ação.")

    def _personagem(self, membro: Membro, personagem: str, acao=Acao.VER_CARTAO):
        self._membro(membro)
        row = self.db.execute("SELECT * FROM personagens WHERE servidor=? AND id=? AND ausente_em IS NULL",
                              (membro.servidor, personagem)).fetchone()
        if not row:
            raise AcessoNegado("Personagem indisponível neste servidor.")
        self._autorizar(membro, acao, row["dono"])
        return row

    def _fonte(self, servidor: str, personagem: str):
        return self.db.execute("""SELECT f.*,c.estado,c.usuario FROM fontes f
            JOIN conexoes c ON c.id=f.conexao WHERE f.servidor=? AND f.personagem=?""",
                               (servidor, personagem)).fetchone()

    def _auditar(self, servidor: str, ator: str, personagem: str | None, acao: str):
        self.db.execute("INSERT INTO auditoria(servidor,ator,personagem,acao,criado) VALUES (?,?,?,?,?)",
                        (servidor, ator, personagem, acao, self.agora()))

    def _pedido(self, membro: Membro, chave: str, tipo: str, dados) -> tuple[str, str, str | None]:
        chave_hash = digest(texto(chave, "Identificador do pedido"))
        assinatura = hashlib.sha256(json_bytes(dados)).hexdigest()
        row = self.db.execute("SELECT * FROM pedidos WHERE servidor=? AND usuario=? AND chave=?",
                              (membro.servidor, membro.usuario, chave_hash)).fetchone()
        if row and (row["tipo"] != tipo or row["assinatura"] != assinatura):
            raise Conflito("Este pedido já foi usado com outros dados.")
        return chave_hash, assinatura, row["personagem"] if row else None

    def _salvar_pedido(self, membro, chave, tipo, assinatura, personagem):
        self.db.execute("INSERT INTO pedidos VALUES (?,?,?,?,?,?,?)",
                        (membro.servidor, membro.usuario, chave, tipo, assinatura, personagem, self.agora()))

    def configurar(self, membro: Membro, *, revisores=(), editores=(), campos_publicos=PUBLICOS,
                   idioma="pt-BR"):
        self._autorizar(membro, Acao.CONFIGURAR)
        campos = frozenset(campos_publicos)
        if not campos <= PUBLICOS or "nome" not in campos or idioma not in ("pt-BR", "en"):
            raise ErroCarteira("Configuração de apresentação inválida.")
        revisores, editores = tuple(revisores), tuple(editores)
        if len(revisores) > 20 or len(editores) > 20:
            raise ErroCarteira("Use no máximo 20 cargos por capacidade.")
        for cargo in revisores + editores:
            texto(cargo, "Cargo")
        with self._transacao():
            self._servidor(membro.servidor)
            self.db.execute("UPDATE servidores SET revisao=revisao+1,campos_publicos=?,idioma=? WHERE id=?",
                            (json.dumps(sorted(campos)), idioma, membro.servidor))
            self.db.execute("DELETE FROM cargos WHERE servidor=?", (membro.servidor,))
            self.db.executemany("INSERT OR IGNORE INTO cargos VALUES (?,?,?)",
                                [(membro.servidor, cargo, cap) for cap, cargos in
                                 (("revisao", revisores), ("edicao", editores)) for cargo in cargos])
            self._auditar(membro.servidor, membro.usuario, None, "configurar")

    def conectar(self, membro: Membro, *, conta: str, cliente: str, refresh_token: str | None) -> str:
        """Somente após o adaptador OAuth verificar identidade, cliente e escopo.

        Não é concessão de acesso Google. Token ausente só conserva uma conexão
        ativa já confirmada para a MESMA identidade; revogada exige reconexão.
        """
        self._membro(membro)
        conta, cliente = texto(conta, "Conta Google", 300), texto(cliente, "Cliente OAuth", 300)
        if refresh_token is not None:
            texto(refresh_token, "Autorização Google", 8192)
        with self._transacao():
            row = self.db.execute("SELECT * FROM conexoes WHERE usuario=? AND conta_hash=? AND cliente_hash=?",
                                  (membro.usuario, digest(conta), digest(cliente))).fetchone()
            if not refresh_token:
                if row and row["estado"] == "ativa" and row["segredo"]:
                    return row["id"]
                raise ErroCarteira("Reconecte a conta para obter autorização durável.")
            cid = row["id"] if row else secrets.token_hex(16)
            autorizacao = secrets.token_hex(16)
            envelope = self.cifra.cifrar(["conexao", cid, membro.usuario, autorizacao],
                                        {"conta": conta, "cliente": cliente, "refresh": refresh_token})
            self.db.execute("""INSERT INTO conexoes VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET segredo=excluded.segredo,
                estado='ativa',atualizado=excluded.atualizado,autorizacao=excluded.autorizacao,
                sem_uso_desde=CASE WHEN EXISTS(SELECT 1 FROM fontes WHERE conexao=excluded.id)
                THEN NULL ELSE excluded.atualizado END""",
                            (cid, membro.usuario, digest(conta), digest(cliente), envelope,
                             self.agora(), self.agora(), self.agora(), autorizacao, "ativa"))
            self.db.execute("UPDATE fontes SET geracao=geracao+1 WHERE conexao=?", (cid,))
            return cid

    def _conexao_do_dono(self, membro: Membro, conexao: str):
        row = self.db.execute("SELECT * FROM conexoes WHERE id=? AND usuario=? AND estado='ativa'",
                              (conexao, membro.usuario)).fetchone()
        if not row:
            raise AcessoNegado("Conexão Google indisponível para este usuário.")
        return row

    def _perfil(self, servidor: str, personagem: str, perfil: dict) -> bytes:
        if not isinstance(perfil, dict) or set(perfil) - PUBLICOS:
            raise ErroCarteira("O perfil contém campos não permitidos.")
        nome = texto(perfil.get("nome"), "Nome do personagem", 100)
        for campo, valor in perfil.items():
            if campo == "cor":
                if type(valor) is not int or not 0 <= valor <= 0xFFFFFF:
                    raise ErroCarteira("Cor inválida.")
            elif campo == "idade":
                if type(valor) is not int or not 0 <= valor <= 100000:
                    raise ErroCarteira("Idade inválida.")
            elif not isinstance(valor, str) or len(valor) > (500 if campo == "frase" else 200):
                raise ErroCarteira("Campo de apresentação inválido.")
        return self.cifra.cifrar(["perfil", servidor, personagem], {**perfil, "nome": nome})

    def cadastrar(self, membro: Membro, *, conexao: str, arquivo: str, nome: str,
                  contrato: str, responsabilidade: bool, pedido: str) -> dict:
        """Arquivo/contrato devem estar validados pelo adaptador Google da etapa 3."""
        self._autorizar(membro, Acao.CADASTRAR)
        if responsabilidade is not True:
            raise ErroCarteira("Confirme que pode cadastrar esta ficha.")
        arquivo, contrato = texto(arquivo, "Arquivo", 300), texto(contrato, "Formato", 100)
        nome = texto(nome, "Nome do personagem", 100)
        try:
            with self._transacao():
                chave, assinatura, anterior = self._pedido(membro, pedido, "cadastrar",
                                                           [conexao, arquivo, nome, contrato])
                if anterior:
                    return self.cartao(membro, anterior)
                self._conexao_do_dono(membro, conexao)
                self._servidor(membro.servidor)
                pid = secrets.token_hex(16)
                perfil = self._perfil(membro.servidor, pid, {"nome": nome})
                self.db.execute("INSERT INTO personagens VALUES (?,?,?,?,?,?,?,NULL)",
                                (membro.servidor, pid, membro.usuario, perfil,
                                 json.dumps(sorted(CAMPOS_PADRAO)), self.agora(), self.agora()))
                self.db.execute("INSERT INTO fontes VALUES (?,?,?,?,?,?,0)",
                                (membro.servidor, pid, conexao, arquivo, contrato, 1))
                self.db.execute("UPDATE conexoes SET sem_uso_desde=NULL WHERE id=?", (conexao,))
                self._salvar_pedido(membro, chave, "cadastrar", assinatura, pid)
                self._auditar(membro.servidor, membro.usuario, pid, "cadastrar")
                return self.cartao(membro, pid)
        except sqlite3.IntegrityError:
            raise Conflito("Esse arquivo já tem um cadastro neste servidor.") from None

    def cartao(self, membro: Membro, personagem: str) -> dict:
        row = self._personagem(membro, personagem)
        perfil = self.cifra.abrir(["perfil", membro.servidor, personagem], row["perfil"])
        config = self.db.execute("SELECT campos_publicos FROM servidores WHERE id=?", (membro.servidor,)).fetchone()
        autorizados = frozenset(json.loads(row["campos_publicos"])) & frozenset(json.loads(config[0]))
        return {"id": row["id"], "responsavel": row["dono"],
                "perfil": cartao_publico(perfil | self._resumo_cartao(membro.servidor, personagem)[0], autorizados), "atualizado_em": row["atualizado"]}

    def listar(self, membro: Membro, *, dono: str | None = None, depois: str = "", limite: int = 20) -> list[dict]:
        self._autorizar(membro, Acao.VER_CARTAO)
        if type(limite) is not int or not 1 <= limite <= 50:
            raise ErroCarteira("Tamanho da página inválido.")
        dono = dono or membro.usuario
        ids = self.db.execute("""SELECT id FROM personagens WHERE servidor=? AND dono=?
            AND ausente_em IS NULL AND id>? ORDER BY id LIMIT ?""",
                              (membro.servidor, dono, depois, limite)).fetchall()
        return [self.cartao(membro, row[0]) for row in ids]

    def personalizar(self, membro: Membro, personagem: str, *, perfil: dict, campos_publicos):
        self._personagem(membro, personagem, Acao.PERSONALIZAR)
        campos = frozenset(campos_publicos)
        if not campos <= PUBLICOS or "nome" not in campos:
            raise ErroCarteira("Campos públicos inválidos.")
        envelope = self._perfil(membro.servidor, personagem, perfil)
        with self._transacao():
            self._personagem(membro, personagem, Acao.PERSONALIZAR)
            self.db.execute("UPDATE personagens SET perfil=?,campos_publicos=?,atualizado=? WHERE servidor=? AND id=?",
                            (envelope, json.dumps(sorted(campos)), self.agora(), membro.servidor, personagem))
            self._auditar(membro.servidor, membro.usuario, personagem, "personalizar")

    def trocar_arquivo(self, membro: Membro, personagem: str, *, arquivo: str, conexao: str,
                       contrato: str, revisao: int, pedido: str):
        if type(revisao) is not int or revisao < 1:
            raise ErroCarteira("Revisão da fonte inválida.")
        arquivo, contrato = texto(arquivo, "Arquivo", 300), texto(contrato, "Formato", 100)
        try:
            with self._transacao():
                self._personagem(membro, personagem, Acao.TROCAR_ARQUIVO)
                chave, assinatura, anterior = self._pedido(membro, pedido, "trocar",
                                                           [personagem, arquivo, conexao, contrato, revisao])
                if anterior:
                    return
                fonte = self._fonte(membro.servidor, personagem)
                if fonte["revisao"] != revisao:
                    raise Conflito("O arquivo mudou. Abra uma nova confirmação.")
                if fonte["conexao"] != conexao:
                    raise ErroCarteira("Trocar conta exige reconexão separada.")
                self._conexao_do_dono(membro, conexao)
                self.db.execute("""UPDATE fontes SET arquivo=?,contrato=?,revisao=revisao+1,
                    geracao=geracao+1 WHERE servidor=? AND personagem=?""",
                                (arquivo, contrato, membro.servidor, personagem))
                self.db.execute("DELETE FROM leituras WHERE servidor=? AND personagem=?", (membro.servidor, personagem))
                self.db.execute("DELETE FROM resumos_cartao WHERE servidor=? AND personagem=?", (membro.servidor, personagem))
                self._salvar_pedido(membro, chave, "trocar", assinatura, personagem)
                self._auditar(membro.servidor, membro.usuario, personagem, "trocar_arquivo")
        except sqlite3.IntegrityError:
            raise Conflito("Esse arquivo já tem um cadastro neste servidor.") from None

    def reservar_leitura(self, membro: Membro, personagem: str) -> ReferenciaLeitura:
        with self._transacao():
            self._personagem(membro, personagem, Acao.VER_DETALHES)
            f = self._fonte(membro.servidor, personagem)
            if f["estado"] != "ativa":
                raise ErroCarteira("Reconecte a conta Google para atualizar a ficha.")
            self.db.execute("UPDATE fontes SET geracao=geracao+1 WHERE servidor=? AND personagem=?",
                            (membro.servidor, personagem))
            return ReferenciaLeitura(membro.servidor, personagem, membro.usuario,
                                    f["revisao"], f["geracao"] + 1, f["arquivo"], f["conexao"])

    def contexto_leitura(self, membro: Membro, personagem: str) -> tuple:
        """Chave interna de coalescência. Nunca enviar autorização ao navegador."""
        self._personagem(membro, personagem, Acao.VER_DETALHES)
        f = self._fonte(membro.servidor, personagem)
        if f["estado"] != "ativa":
            raise ErroCarteira("Reconecte a conta Google para atualizar a ficha.")
        a = self.db.execute("SELECT autorizacao FROM conexoes WHERE id=?", (f["conexao"],)).fetchone()[0]
        return (membro.servidor, personagem, f["revisao"], f["arquivo"], f["conexao"], a)

    def renovar_credencial(self, membro: Membro, ref: ReferenciaLeitura, *, autorizacao: str, refresh: str):
        with self._transacao():
            cred = self._credencial(membro, ref)
            if cred.autorizacao != autorizacao:
                raise Conflito("A autorização mudou durante a leitura.")
            texto(refresh, "Renovação", 8192)
            envelope = self.cifra.cifrar(["conexao", ref.conexao, self._fonte(ref.servidor, ref.personagem)["usuario"], autorizacao],
                                       {"conta": cred.conta, "cliente": cred.cliente, "refresh": refresh})
            self.db.execute("UPDATE conexoes SET segredo=? WHERE id=?", (envelope, ref.conexao))

    def invalidar_leitura(self, membro: Membro, ref: ReferenciaLeitura):
        """Falha na atualização não deixa um resultado anterior parecer atual."""
        with self._transacao():
            self._referencia(membro, ref)
            self.db.execute("DELETE FROM leituras WHERE servidor=? AND personagem=?", (ref.servidor, ref.personagem))
            self.db.execute("DELETE FROM analises WHERE servidor=? AND personagem=?", (ref.servidor, ref.personagem))

    def _referencia(self, membro: Membro, ref: ReferenciaLeitura):
        if (membro.servidor, membro.usuario) != (ref.servidor, ref.ator):
            raise AcessoNegado("Leitura pertence a outro contexto.")
        self._personagem(membro, ref.personagem, Acao.VER_DETALHES)
        f = self._fonte(ref.servidor, ref.personagem)
        if (f["revisao"], f["geracao"], f["arquivo"], f["conexao"], f["estado"]) != (
                ref.revisao, ref.geracao, ref.arquivo, ref.conexao, "ativa"):
            raise Conflito("A fonte mudou durante a leitura. Descarte o resultado.")

    def _credencial(self, membro: Membro, ref: ReferenciaLeitura) -> CredencialGoogle:
        """Só para o adaptador Google do serviço; nunca serializar na API/Discord."""
        self._referencia(membro, ref)
        row = self.db.execute("SELECT * FROM conexoes WHERE id=?", (ref.conexao,)).fetchone()
        obj = self.cifra.abrir(["conexao", row["id"], row["usuario"], row["autorizacao"]], row["segredo"])
        if digest(obj["conta"]) != row["conta_hash"] or digest(obj["cliente"]) != row["cliente_hash"]:
            raise ErroCarteira("Identidade da conexão inconsistente.")
        return CredencialGoogle(obj["conta"], obj["cliente"], obj["refresh"], row["autorizacao"])

    def gravar_leitura(self, membro: Membro, ref: ReferenciaLeitura, *, campos: dict, schema: str) -> str:
        if not isinstance(campos, dict) or len(json_bytes(campos)) > MAX_JSON:
            raise ErroCarteira("Leitura excede o limite de armazenamento.")
        texto(schema, "Versão da leitura", 100)
        lid = secrets.token_hex(16)
        envelope = self.cifra.cifrar(["leitura", ref.servidor, ref.personagem, lid], campos)
        with self._transacao():
            self._referencia(membro, ref)
            self.db.execute("""INSERT INTO leituras VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(servidor,personagem) DO UPDATE SET id=excluded.id,
                revisao=excluded.revisao,schema=excluded.schema,criado=excluded.criado,
                expira=excluded.expira,conteudo=excluded.conteudo""",
                            (ref.servidor, ref.personagem, lid, ref.revisao, schema,
                             self.agora(), self.agora() + DIA, envelope))
            self._salvar_resumo(ref, campos)
            # Consome o ticket; a mesma resposta não pode gravar novamente.
            self.db.execute("UPDATE fontes SET geracao=geracao+1 WHERE servidor=? AND personagem=?",
                            (ref.servidor, ref.personagem))
        return lid

    def gravar_analise(self, membro: Membro, personagem: str, *, leitura_id: str,
                      campanha_revisao: str, resultado: dict):
        if not isinstance(resultado, dict) or len(json_bytes(resultado)) > MAX_JSON:
            raise ErroCarteira("Análise excede o limite de armazenamento.")
        texto(campanha_revisao, "Revisão da campanha", 200)
        with self._transacao():
            self._personagem(membro, personagem, Acao.ANALISAR)
            l = self.db.execute("SELECT * FROM leituras WHERE servidor=? AND personagem=?",
                                (membro.servidor, personagem)).fetchone()
            f = self._fonte(membro.servidor, personagem)
            if not l or l["id"] != leitura_id or l["expira"] <= self.agora() or f["estado"] != "ativa":
                raise Conflito("A leitura usada na análise não é mais atual.")
            envelope = self.cifra.cifrar(["analise", membro.servidor, personagem, leitura_id], resultado)
            self.db.execute("""INSERT INTO analises VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(servidor,personagem) DO UPDATE SET leitura_id=excluded.leitura_id,
                revisao=excluded.revisao,campanha_revisao=excluded.campanha_revisao,
                criado=excluded.criado,expira=excluded.expira,conteudo=excluded.conteudo""",
                            (membro.servidor, personagem, leitura_id, l["revisao"], campanha_revisao,
                             self.agora(), self.agora() + 7 * DIA, envelope))

    def detalhes(self, membro: Membro, personagem: str) -> dict:
        self._personagem(membro, personagem, Acao.VER_DETALHES)
        f = self._fonte(membro.servidor, personagem)
        if f["estado"] != "ativa":
            raise ErroCarteira("Reconecte a conta Google para consultar os dados privados.")
        saida = {"cartao": self.cartao(membro, personagem), "arquivo": f["arquivo"],
                 "revisao": f["revisao"], "contrato": f["contrato"], "leitura": None, "analise": None}
        l = self.db.execute("SELECT * FROM leituras WHERE servidor=? AND personagem=? AND expira>?",
                            (membro.servidor, personagem, self.agora())).fetchone()
        if l and l["revisao"] == f["revisao"]:
            saida["leitura"] = {"id": l["id"], "lido_em": l["criado"], "schema": l["schema"],
                                "fresca": self.agora() - l["criado"] <= 60,
                                "campos": self.cifra.abrir(["leitura", membro.servidor, personagem, l["id"]], l["conteudo"])}
        a = self.db.execute("SELECT * FROM analises WHERE servidor=? AND personagem=? AND expira>?",
                            (membro.servidor, personagem, self.agora())).fetchone()
        if a:
            saida["analise"] = {"fonte_atual": bool(l and a["leitura_id"] == l["id"] and a["revisao"] == f["revisao"]),
                                "analisado_em": a["criado"], "campanha_revisao": a["campanha_revisao"],
                                "resultado": self.cifra.abrir(["analise", membro.servidor, personagem, a["leitura_id"]], a["conteudo"])}
        return saida

    def desconectar(self, membro: Membro, conexao: str):
        self._membro(membro)
        with self._transacao():
            row = self.db.execute("SELECT usuario FROM conexoes WHERE id=?", (conexao,)).fetchone()
            if not row or row["usuario"] != membro.usuario:
                raise AcessoNegado("Conexão indisponível para este usuário.")
            self._bloquear_autorizacao(conexao)
            self.db.execute("UPDATE conexoes SET estado='desconectada',segredo=NULL,atualizado=? WHERE id=?",
                            (self.agora(), conexao))
            self.db.execute("UPDATE fontes SET geracao=geracao+1 WHERE conexao=?", (conexao,))
            self.db.execute("DELETE FROM web_fluxos WHERE conexao=?", (conexao,))
            self.db.execute("DELETE FROM leituras WHERE (servidor,personagem) IN (SELECT servidor,personagem FROM fontes WHERE conexao=?)",
                            (conexao,))
            self._auditar(membro.servidor, membro.usuario, None, "desconectar")

    def marcar_revogada(self, conexao: str, *, autorizacao: str) -> bool:
        """Operação interna após o adaptador Google confirmar revogação."""
        with self._transacao():
            atual = self.db.execute("SELECT autorizacao,estado FROM conexoes WHERE id=?", (conexao,)).fetchone()
            if not atual or atual[0] != autorizacao or atual[1] != "ativa":
                return False  # Resposta de uma autorização substituída não revoga a nova.
            self._bloquear_autorizacao(conexao)
            self.db.execute("UPDATE conexoes SET estado='revogada',segredo=NULL,atualizado=? WHERE id=?",
                            (self.agora(), conexao))
            self.db.execute("UPDATE fontes SET geracao=geracao+1 WHERE conexao=?", (conexao,))
            self.db.execute("DELETE FROM web_fluxos WHERE conexao=?", (conexao,))
            self.db.execute("DELETE FROM leituras WHERE (servidor,personagem) IN (SELECT servidor,personagem FROM fontes WHERE conexao=?)",
                            (conexao,))
            return True

    def registrar_saida(self, servidor: str, usuario: str):
        """Somente evento/consulta Discord confirmado pelo servidor, não input web."""
        with self._transacao():
            self.db.execute("UPDATE personagens SET ausente_em=COALESCE(ausente_em,?) WHERE servidor=? AND dono=?",
                            (self.agora(), servidor, usuario))

    def registrar_retorno(self, membro: Membro):
        self._membro(membro)
        with self._transacao():
            rows = self.db.execute("SELECT id,ausente_em FROM personagens WHERE servidor=? AND dono=? AND ausente_em IS NOT NULL",
                                   (membro.servidor, membro.usuario)).fetchall()
            for row in rows:
                if row["ausente_em"] + 30 * DIA <= self.agora():
                    self._remover(membro.servidor, row["id"])
                else:
                    self.db.execute("UPDATE personagens SET ausente_em=NULL WHERE servidor=? AND id=?",
                                    (membro.servidor, row["id"]))

    def _marcar_orfas(self):
        self.db.execute("""UPDATE conexoes SET sem_uso_desde=COALESCE(sem_uso_desde,?)
            WHERE NOT EXISTS(SELECT 1 FROM fontes WHERE conexao=conexoes.id)""", (self.agora(),))

    def _bloquear_autorizacao(self, conexao: str):
        self.db.execute("""INSERT OR IGNORE INTO remocoes.autorizacoes
            SELECT id,autorizacao,? FROM conexoes WHERE id=?""", (self.agora(), conexao))

    def _remover(self, servidor: str, personagem: str):
        self.db.execute("INSERT OR IGNORE INTO remocoes.exclusoes VALUES (?,?,?)",
                        (servidor, personagem, self.agora()))
        self.db.execute("DELETE FROM personagens WHERE servidor=? AND id=?", (servidor, personagem))
        self._marcar_orfas()

    def _reaplicar_remocoes(self):
        self.db.execute("""DELETE FROM personagens WHERE (servidor,id) IN
            (SELECT servidor,personagem FROM remocoes.exclusoes)""")
        self.db.execute("""UPDATE conexoes SET estado='revogada',segredo=NULL
            WHERE (id,autorizacao) IN (SELECT conexao,autorizacao FROM remocoes.autorizacoes)""")
        self.db.execute("""DELETE FROM leituras WHERE (servidor,personagem) IN
            (SELECT f.servidor,f.personagem FROM fontes f JOIN conexoes c ON c.id=f.conexao
            WHERE c.estado!='ativa')""")
        self._marcar_orfas()

    def excluir(self, membro: Membro, personagem: str, *, pedido: str):
        self._membro(membro)
        with self._transacao():
            chave, assinatura, anterior = self._pedido(membro, pedido, "excluir", [personagem])
            if anterior:
                return
            self._personagem(membro, personagem, Acao.EXCLUIR)
            self._remover(membro.servidor, personagem)
            self._salvar_pedido(membro, chave, "excluir", assinatura, personagem)
            self._auditar(membro.servidor, membro.usuario, personagem, "excluir")

    def apagar_usuario(self, usuario: str):
        """Operação interna após pedido global com identidade Discord comprovada.

        Serve inclusive a quem saiu do servidor. Não aceitar IDs arbitrários de
        um formulário web nem oferecer esta função a administradores de guild.
        """
        texto(usuario, "Usuário")
        with self._transacao():
            rows = self.db.execute("SELECT servidor,id FROM personagens WHERE dono=?", (usuario,)).fetchall()
            for row in rows:
                self._remover(row["servidor"], row["id"])
                self._auditar(row["servidor"], usuario, row["id"], "apagar_usuario")
            for row in self.db.execute("SELECT id FROM conexoes WHERE usuario=?", (usuario,)).fetchall():
                self._bloquear_autorizacao(row["id"])
            self.db.execute("DELETE FROM pedidos WHERE usuario=?", (usuario,))
            self.db.execute("DELETE FROM web_fluxos WHERE usuario=?", (usuario,))
            self.db.execute("DELETE FROM web_sessoes WHERE usuario=?", (usuario,))
            self.db.execute("DELETE FROM conexoes WHERE usuario=?", (usuario,))

    def limpar(self) -> dict[str, int]:
        """Manutenção local. Não consulta nenhuma planilha nem o Discord."""
        contagens = {}
        with self._transacao():
            ausentes = self.db.execute("SELECT servidor,id FROM personagens WHERE ausente_em<=?",
                                       (self.agora() - 30 * DIA,)).fetchall()
            for row in ausentes:
                self._remover(row["servidor"], row["id"])
            contagens["personagens"] = len(ausentes)
            self.limpar_imagens()
            for tabela, campo, prazo in (("leituras", "expira", 0), ("analises", "expira", 0),
                                         ("web_fluxos", "expira", 0), ("previas_cartao", "expira", 0),
                                         ("pedidos", "criado", 7 * DIA), ("auditoria", "criado", 90 * DIA)):
                contagens[tabela] = self.db.execute(f"DELETE FROM {tabela} WHERE {campo}<=?",
                                                    (self.agora() - prazo,)).rowcount
            self._marcar_orfas()
            contagens["conexoes"] = self.db.execute("DELETE FROM conexoes WHERE sem_uso_desde<=?",
                                                   (self.agora() - DIA,)).rowcount
            # Backups com mais de 30 dias são recusados na restauração.
            contagens["remocoes"] = self.db.execute("DELETE FROM remocoes.exclusoes WHERE criado<=?",
                                                   (self.agora() - 31 * DIA,)).rowcount
            contagens["autorizacoes"] = self.db.execute("DELETE FROM remocoes.autorizacoes WHERE criado<=?",
                                                       (self.agora() - 31 * DIA,)).rowcount
        return contagens

    def rotacionar_chave(self, nova_chave: bytes):
        """Reescreve todos os envelopes numa transação. Guardar chave antiga dos backups."""
        nova = Cifra((nova_chave,))
        with self._transacao():
            for row in self.db.execute("SELECT id,usuario,autorizacao FROM conexoes WHERE segredo IS NOT NULL").fetchall():
                ctx = ["conexao", row["id"], row["usuario"], row["autorizacao"]]
                segredo = self.db.execute("SELECT segredo FROM conexoes WHERE id=?", (row["id"],)).fetchone()[0]
                envelope = nova.cifrar(ctx, self.cifra.abrir(ctx, segredo))
                self.db.execute("UPDATE conexoes SET segredo=? WHERE id=?", (envelope, row["id"]))
            for row in self.db.execute("SELECT servidor,id FROM personagens").fetchall():
                ctx = ["perfil", row["servidor"], row["id"]]
                perfil = self.db.execute("SELECT perfil FROM personagens WHERE servidor=? AND id=?",
                                         (row["servidor"], row["id"])).fetchone()[0]
                envelope = nova.cifrar(ctx, self.cifra.abrir(ctx, perfil))
                self.db.execute("UPDATE personagens SET perfil=? WHERE servidor=? AND id=?",
                                (envelope, row["servidor"], row["id"]))
            for tabela, campo in (("leituras", "id"), ("analises", "leitura_id")):
                for row in self.db.execute(f"SELECT servidor,personagem,{campo} FROM {tabela}").fetchall():
                    ctx = ["leitura" if tabela == "leituras" else "analise",
                           row["servidor"], row["personagem"], row[campo]]
                    conteudo = self.db.execute(f"SELECT conteudo FROM {tabela} WHERE servidor=? AND personagem=?",
                                               (row["servidor"], row["personagem"])).fetchone()[0]
                    envelope = nova.cifrar(ctx, self.cifra.abrir(ctx, conteudo))
                    self.db.execute(f"UPDATE {tabela} SET conteudo=? WHERE servidor=? AND personagem=?",
                                    (envelope, row["servidor"], row["personagem"]))
            for row in self.db.execute("SELECT * FROM resumos_cartao").fetchall():
                ctx = ["resumo", row["servidor"], row["personagem"]]
                self.db.execute("UPDATE resumos_cartao SET conteudo=? WHERE servidor=? AND personagem=?",
                                (nova.cifrar(ctx,self.cifra.abrir(ctx,row["conteudo"])),row["servidor"],row["personagem"]))
            for row in self.db.execute("SELECT * FROM previas_cartao").fetchall():
                ctx = ["previa",row["servidor"],row["personagem"],row["usuario"],row["id"]]
                self.db.execute("UPDATE previas_cartao SET conteudo=? WHERE id=?",
                                (nova.cifrar(ctx,self.cifra.abrir(ctx,row["conteudo"])),row["id"]))
            self.db.execute("DELETE FROM web_sessoes")
            self.db.execute("DELETE FROM web_fluxos")
            for row in self.db.execute("SELECT * FROM modelos_servidor").fetchall():
                ctx = ["modelo", row["servidor"]]
                self.db.execute("UPDATE modelos_servidor SET conteudo=? WHERE servidor=?",
                                (nova.cifrar(ctx, self.cifra.abrir(ctx, row["conteudo"])), row["servidor"]))
            self.db.execute("UPDATE meta SET valor=? WHERE chave='verificador'",
                            (nova.cifrar(["verificador", self.banco_id], "carteira-viva"),))
        self.cifra = nova

    def idioma_carteira(self,membro):
        self._membro(membro)
        r=self.db.execute('SELECT idioma FROM servidores WHERE id=?',(membro.servidor,)).fetchone()
        return r['idioma'] if r else 'pt-BR'

    def verificar_integridade(self):
        if self.db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ErroCarteira("Banco da Carteira com erro de integridade.")
        if self.db.execute("PRAGMA foreign_key_check").fetchone():
            raise ErroCarteira("Banco da Carteira com vínculos inválidos.")
        if self.db.execute("PRAGMA remocoes.integrity_check").fetchone()[0] != "ok":
            raise ErroCarteira("Registro de remoções com erro de integridade.")
