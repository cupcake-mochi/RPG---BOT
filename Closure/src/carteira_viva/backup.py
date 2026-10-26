"""Backups locais cifrados em blocos; restauração somente para destino novo.

O registro de remoções mais recente é obrigatório para recuperar o cadastro.
Não substituir um banco que esteja aberto no serviço por esta função.
"""
import base64
import math
import os
from pathlib import Path
import secrets
import sqlite3
import struct
from tempfile import TemporaryDirectory
import time

from .banco import Cadastro, DIA, LEDGER_ID, arquivo_privado
from .segredos import Cifra, ErroCarteira

MAGIC = b"CVBAK1\0"
BLOCO = 1024 * 1024
MAX_FRAME = 2 * 1024 * 1024
MAX_BANCO = 2 * 1024 * 1024 * 1024


def _frame(out, cifra, nonce, indice, valor):
    envelope = cifra.cifrar(["backup", nonce.hex(), str(indice)], valor)
    out.write(struct.pack("!I", len(envelope)))
    out.write(envelope)


def _publicar(origem: Path, destino: Path):
    os.link(origem, destino)
    if hasattr(os, "O_DIRECTORY"):
        fd = os.open(destino.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def gravar_backup(cadastro: Cadastro, destino: Path, *, registro_remocoes: bool = False) -> Path:
    """O operador deve manter também uma cópia atual do ledger de exclusões."""
    destino = Path(destino).absolute()
    if destino.exists() or destino.is_symlink():
        raise ErroCarteira("Escolha um arquivo novo para o backup.")
    destino.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    cadastro.verificar_integridade()
    with TemporaryDirectory(prefix=".carteira-backup-", dir=destino.parent) as pasta:
        raw = Path(pasta) / "copia.sqlite3"
        arquivo_privado(raw)
        db = sqlite3.connect(raw)
        try:
            cadastro.db.backup(db, name="remocoes" if registro_remocoes else "main")
            if not registro_remocoes:
                db.execute("PRAGMA secure_delete=ON")
                db.execute("DELETE FROM web_fluxos")
                if db.execute("PRAGMA user_version").fetchone()[0]>=4:
                    db.execute("DELETE FROM previas_cartao")
                db.commit()
        finally:
            db.close()
        if raw.stat().st_size > MAX_BANCO:
            raise ErroCarteira("Backup excede o limite desta versão.")
        pronto = Path(pasta) / "backup.cvb"
        arquivo_privado(pronto)
        nonce = secrets.token_bytes(16)
        with pronto.open("wb") as out, raw.open("rb") as src:
            out.write(MAGIC + nonce)
            _frame(out, cadastro.cifra, nonce, 0,
                   {"formato": 1, "tipo": "remocoes" if registro_remocoes else "cadastro",
                    "banco_id": cadastro.banco_id, "criado": cadastro.agora()})
            indice = 1
            while bloco := src.read(BLOCO):
                _frame(out, cadastro.cifra, nonce, indice, {"dados": base64.b64encode(bloco).decode("ascii")})
                indice += 1
            _frame(out, cadastro.cifra, nonce, indice, {"fim": True})
            out.flush()
            os.fsync(out.fileno())
        # Hard link publica sem sobrescrever arquivo criado por outro processo.
        _publicar(pronto, destino)
    return destino


def _extrair(arquivo: Path, raw: Path, cifra: Cifra, agora: float, tipo: str) -> dict:
    arquivo_privado(raw)
    total = 0
    with Path(arquivo).open("rb") as src, raw.open("wb") as out:
        if src.read(len(MAGIC)) != MAGIC:
            raise ErroCarteira("Formato de backup inválido.")
        nonce = src.read(16)
        if len(nonce) != 16:
            raise ErroCarteira("Backup incompleto.")
        indice = 0
        while True:
            tamanho = src.read(4)
            if len(tamanho) != 4:
                raise ErroCarteira("Backup incompleto.")
            n = struct.unpack("!I", tamanho)[0]
            if not 0 < n <= MAX_FRAME:
                raise ErroCarteira("Bloco de backup inválido.")
            envelope = src.read(n)
            if len(envelope) != n:
                raise ErroCarteira("Backup incompleto.")
            valor = cifra.abrir(["backup", nonce.hex(), str(indice)], envelope)
            if indice == 0:
                meta = valor
                if (not isinstance(meta, dict) or meta.get("formato") != 1 or meta.get("tipo") != tipo or
                        not isinstance(meta.get("banco_id"), str) or
                        type(meta.get("criado")) not in (int, float) or not math.isfinite(meta["criado"])):
                    raise ErroCarteira("Metadados de backup inválidos.")
                if not 0 <= agora - meta["criado"] <= 30 * DIA:
                    raise ErroCarteira("Backup fora do prazo de restauração de 30 dias.")
            elif valor == {"fim": True}:
                if src.read(1):
                    raise ErroCarteira("Backup contém dados depois do encerramento.")
                return meta
            else:
                try:
                    bloco = base64.b64decode(valor["dados"], validate=True)
                except (KeyError, TypeError, ValueError):
                    raise ErroCarteira("Bloco de backup inválido.") from None
                if not 0 < len(bloco) <= BLOCO:
                    raise ErroCarteira("Bloco de backup inválido.")
                total += len(bloco)
                if total > MAX_BANCO:
                    raise ErroCarteira("Backup excede o limite desta versão.")
                out.write(bloco)
            indice += 1


def restaurar_backup(arquivo: Path, destino: Path, chaves: tuple[bytes, ...], *,
                      remocoes: Path, agora=time.time) -> Path:
    """Exige ledger ATUAL externo ao backup. Não recupera dados Google nem permissões."""
    destino, remocoes = Path(destino).absolute(), Path(remocoes).absolute()
    if destino.exists() or destino.is_symlink():
        raise ErroCarteira("Restaure para um arquivo novo com o serviço parado.")
    if not remocoes.is_file() or remocoes.is_symlink():
        raise ErroCarteira("Informe o registro de remoções atual antes de restaurar.")
    destino.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    cifra = Cifra(chaves)
    with TemporaryDirectory(prefix=".carteira-restaurar-", dir=destino.parent) as pasta:
        raw = Path(pasta) / "cadastro.sqlite3"
        meta = _extrair(arquivo, raw, cifra, agora(), "cadastro")
        with Cadastro(raw, chaves, remocoes=remocoes, agora=agora) as cadastro:
            if cadastro.banco_id != meta["banco_id"]:
                raise ErroCarteira("Identidade do backup inválida.")
            cadastro.verificar_integridade()
            # Abertura já reaplicou remoções antes de expor qualquer leitura.
        _publicar(raw, destino)
    return destino


def restaurar_remocoes(arquivo: Path, destino: Path, chaves: tuple[bytes, ...], *, agora=time.time) -> Path:
    """Recupera a cópia MAIS RECENTE do ledger antes de restaurar o cadastro.

    Não há como inferir exclusões posteriores a um ledger perdido. O operador
    deve recuperar o registro atual; não escolher automaticamente um ledger antigo.
    """
    destino = Path(destino).absolute()
    if destino.exists() or destino.is_symlink():
        raise ErroCarteira("Escolha um destino novo para o registro de remoções.")
    destino.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with TemporaryDirectory(prefix=".carteira-remocoes-", dir=destino.parent) as pasta:
        raw = Path(pasta) / "remocoes.sqlite3"
        meta = _extrair(arquivo, raw, Cifra(chaves), agora(), "remocoes")
        db = sqlite3.connect(raw)
        try:
            if (db.execute("PRAGMA application_id").fetchone()[0] != LEDGER_ID or
                    db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or
                    db.execute("SELECT banco_id FROM meta").fetchone()[0] != meta["banco_id"]):
                raise ErroCarteira("Registro de remoções inválido.")
        finally:
            db.close()
        _publicar(raw, destino)
    return destino


def limpar_backups(pasta: Path, chaves: tuple[bytes, ...], *, banco_id: str, agora=time.time) -> int:
    """Remove só arquivos .cvb próprios, autenticados e fora da retenção.

    Metadados corrompidos, arquivos de outro banco e links são preservados para inspeção
    do operador. Nunca procurar recursivamente nem excluir por nome/data do SO.
    """
    cifra = Cifra(chaves)
    apagados = 0
    for arquivo in Path(pasta).glob("*.cvb"):
        if not arquivo.is_file() or arquivo.is_symlink():
            continue
        try:
            with arquivo.open("rb") as src:
                if src.read(len(MAGIC)) != MAGIC:
                    continue
                nonce, size = src.read(16), src.read(4)
                if len(nonce) != 16 or len(size) != 4:
                    continue
                tamanho = struct.unpack("!I", size)[0]
                if not 0 < tamanho <= MAX_FRAME:
                    continue
                meta = cifra.abrir(["backup", nonce.hex(), "0"], src.read(tamanho))
            if (not isinstance(meta, dict) or meta.get("formato") != 1 or meta.get("banco_id") != banco_id or
                    meta.get("tipo") not in ("cadastro", "remocoes") or
                    type(meta.get("criado")) not in (int, float) or not math.isfinite(meta["criado"])):
                continue
            if agora() - meta["criado"] > 30 * DIA:
                arquivo.unlink()
                apagados += 1
        except (OSError, ErroCarteira):
            continue
    return apagados
