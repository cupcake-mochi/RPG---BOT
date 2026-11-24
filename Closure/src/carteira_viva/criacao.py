"""Criar ficha vazia: copia a oficial do Ciclo no Drive do jogador e cadastra a cópia.

Não escreve célula nenhuma: a oficial já está limpa e o jogador preenche. O diário
(copias_rest) é gravado antes do POST, então uma resposta perdida é procurada pelo
marcador no Drive em vez de virar outra cópia. O registro sai quando a ficha é
cadastrada; pedido abandonado expira em um dia.
"""
import asyncio
import logging
import re
import secrets

from .copias_banco import ReferenciaCopia, hash_texto
from .copias_google import DestinoCopia, PRAZO_JOB_COPIA, enviar, observar, procurar
from .permissoes import Acao
from .segredos import Conflito, ErroCarteira

MODELO = "ciclo"
DIA = 86400
# Sem resposta do Google, só depois disto vale repetir a cópia: passou o tempo do
# POST (120 s) e da busca do Drive enxergar o arquivo.
ESPERA_COPIA = 180


def _erro(codigo):
    from .provedores import ErroProvedor
    return ErroProvedor(codigo)


class Criacoes:
    """Parte do cadastro. Só o serviço chama; nada aqui recebe ID de arquivo do navegador."""

    def modelo_criacao(self, membro):
        from .modelos import CriacaoBloqueada
        self._autorizar(membro, Acao.CADASTRAR)
        try:
            return self._origem_modelo_copia(membro.servidor, MODELO)["origem"]
        except Conflito:
            # Servidor que escolheu a Era ou um modelo próprio: ainda não criamos a partir deles.
            raise CriacaoBloqueada() from None

    def _criacao(self, membro, ref):
        d = self.contexto_copia(membro, ref)
        if d.get("uso") != "vazia":
            raise Conflito("Este registro de cópia não é de criação.")
        return d

    def contexto_criacao(self, membro, ref):
        self.modelo_criacao(membro)
        return self._criacao(membro, ref)

    def preparar_criacao(self, membro, *, conexao, nome, pedido):
        self.modelo_criacao(membro)
        chave = hash_texto("vazia:" + pedido)
        with self._transacao():
            c = self._conexao_do_dono(membro, conexao)
            origem = self._origem_modelo_copia(membro.servidor, MODELO)
            retomar = None
            rows = self.db.execute("SELECT * FROM copias_rest WHERE servidor=? AND ator=? ORDER BY criado,operacao",
                                   (membro.servidor, membro.usuario)).fetchall()
            for row in rows:
                d = self.cifra.abrir(self._ctx_copia(row), row["conteudo"])
                if d.get("uso") != "vazia":
                    if row["estado"] != "identificada":
                        raise Conflito("Há uma cópia pendente de outro tipo.")
                    continue
                mesma = d["conta"] == c["conta_hash"] and d["origem"] == origem["origem"]
                velha = row["atualizado"] + ESPERA_COPIA <= self.agora()
                if row["estado"] == "preparada" or (not mesma and velha):
                    # Nunca saiu pro Google, ou saiu por outra conta que já não dá pra conferir.
                    self.db.execute("DELETE FROM copias_rest WHERE operacao=?", (row["operacao"],))
                elif not mesma:
                    if row["estado"] != "identificada":
                        raise _erro("copia_incerta")
                else:
                    # Uma só por vez: 'enviada' é única pelo índice; identificada sem cadastro é retomada.
                    retomar = retomar or (row, d)
            if retomar:
                row, d = retomar
                d.update(origem, autorizacao=c["autorizacao"], nome=nome)
                self.db.execute("UPDATE copias_rest SET conexao=?,pedido=?,conteudo=? WHERE operacao=?",
                                (conexao, chave, self.cifra.cifrar(self._ctx_copia(row), d), row["operacao"]))
                return ReferenciaCopia(membro.servidor, membro.usuario, row["operacao"], conexao)
            if len(rows) >= 64 or self.db.execute("SELECT count(*) FROM copias_rest").fetchone()[0] >= 10000:
                raise ErroCarteira("Limite de operações de cópia.")
            self._servidor(membro.servidor)
            op = secrets.token_hex(32)
            d = dict(**origem, autorizacao=c["autorizacao"], estado="preparada", versao_origem=None, destino=None,
                     versao_destino=None, protocolo_copia=2, candidata=None, uso="vazia", conta=c["conta_hash"],
                     nome=nome)
            row = dict(servidor=membro.servidor, ator=membro.usuario, operacao=op)
            self.db.execute("INSERT INTO copias_rest VALUES (?,?,?,?,?,?,?,?,?)",
                            (membro.servidor, membro.usuario, op, conexao, chave, "preparada", self.agora(),
                             self.agora(), self.cifra.cifrar(self._ctx_copia(row), d)))
            self.db.execute("UPDATE conexoes SET sem_uso_desde=NULL WHERE id=?", (conexao,))
            return ReferenciaCopia(membro.servidor, membro.usuario, op, conexao)

    def identificar_criacao(self, membro, ref, destino):
        if type(destino) is not DestinoCopia:
            raise ErroCarteira("Use a observação do adaptador Google.")
        with self._transacao():
            d = self._criacao(membro, ref)
            if (d["estado"] != "enviada" or destino.operacao != ref.operacao or destino.origem != d["origem"] or
                    self.db.execute("SELECT 1 FROM fontes WHERE arquivo=?", (destino.arquivo,)).fetchone()):
                raise Conflito("A cópia observada não pertence a esta criação.")
            # Sem prender a versão: o jogador pode abrir a própria cópia antes do cadastro.
            self._guardar_copia(ref, {**d, "estado": "identificada", "destino": destino.arquivo,
                                      "versao_destino": destino.versao})

    def reiniciar_criacao(self, membro, ref):
        """Cópia não encontrada depois da espera: volta a poder ser pedida. False se ainda é cedo."""
        with self._transacao():
            d = self._criacao(membro, ref)
            quando = self.db.execute("SELECT atualizado FROM copias_rest WHERE operacao=?", (ref.operacao,)).fetchone()[0]
            if d["estado"] != "enviada" or quando + ESPERA_COPIA > self.agora():
                return False
            self._guardar_copia(ref, {**d, "estado": "preparada", "versao_origem": None})
            return True

    def descartar_criacao(self, membro, ref):
        with self._transacao():
            self._criacao(membro, ref)
            self.db.execute("DELETE FROM copias_rest WHERE operacao=?", (ref.operacao,))
            self._marcar_orfas()

    def concluir_criacao(self, membro, ref, contrato):
        with self._transacao():
            d = self.contexto_criacao(membro, ref)
            if d["estado"] != "identificada":
                raise Conflito("A cópia ainda não foi identificada.")
            cartao = self.cadastrar(membro, conexao=ref.conexao, arquivo=d["destino"], nome=d["nome"],
                                    contrato=contrato, responsabilidade=True, pedido="criar:" + ref.operacao)
            self.db.execute("DELETE FROM copias_rest WHERE operacao=?", (ref.operacao,))
            self._auditar(membro.servidor, membro.usuario, cartao["id"], "criar_ficha")
            return {**cartao, "arquivo": d["destino"]}

    def limpar_criacoes(self):
        """Pedido abandonado não segura a conexão Google além de um dia."""
        n = 0
        for row in self.db.execute("SELECT * FROM copias_rest WHERE atualizado<=?", (self.agora() - DIA,)).fetchall():
            if self.cifra.abrir(self._ctx_copia(row), row["conteudo"]).get("uso") == "vazia":
                n += self.db.execute("DELETE FROM copias_rest WHERE operacao=?", (row["operacao"],)).rowcount
        return n


def nome_do_arquivo(nome):
    limpo = re.sub("[\x00-\x1f\x7f‪-‮⁦-⁩]", " ", nome)
    return "Ficha - " + " ".join(limpo.split())[:100]


async def criar_ficha(servico, servidor, usuario, ref, *, esperas=(5, 15)):
    """Roda na fila das consultas. Devolve o cartão cadastrado e o ID da cópia."""
    from .provedores import ErroProvedor
    b, p = servico._banco, servico.provedores

    async def localizar(acesso, origem):
        for espera in (0, *esperas):
            await asyncio.sleep(espera)
            try:
                return await procurar(p, acesso, ref.operacao, origem)
            except ErroProvedor as exc:
                if exc.codigo not in ("copia_incerta", "temporario"):
                    raise
        raise ErroProvedor("copia_incerta")

    async def copiar(acesso, d):
        versao, _ = await p.observar_arquivo(acesso, d["origem"])
        m = await servico._membro(servidor, usuario)
        await b("fixar_versao_copia", m, ref, versao)
        if not await b("armar_envio_copia", m, ref):
            raise Conflito("Esta cópia já foi enviada.")
        # Desconexão entre armar e enviar impede o POST.
        await b("contexto_criacao", await servico._membro(servidor, usuario), ref)
        try:
            return await enviar(p, acesso, ref.operacao, d["origem"], nome=nome_do_arquivo(d["nome"]))
        except ErroProvedor as exc:
            if exc.codigo != "copia_incerta":
                raise
            # O Google pode ter copiado mesmo sem responder: procurar, nunca repetir aqui.
            return await localizar(acesso, d["origem"])

    async def validar(acesso, arquivo):
        for espera in (*esperas, None):
            try:
                return await p.validar_arquivo(acesso, arquivo)
            except ErroProvedor as exc:
                # A cópia recém-criada pode demorar um pouco pra responder pela API.
                if espera is None or exc.codigo not in ("acesso", "temporario", "formato"):
                    raise
                await asyncio.sleep(espera)

    async def executar():
        m = await servico._membro(servidor, usuario)
        d = await b("contexto_criacao", m, ref)
        cred, token = await servico._renovar_google(m, ref, para_copia=True)
        acesso = token.acesso
        await servico.cotas.esperar(hash_texto(cred.conta))
        try:
            if d["estado"] == "preparada":
                arquivo = await copiar(acesso, d)
            elif d["estado"] == "enviada":
                try:
                    arquivo = await localizar(acesso, d["origem"])
                except ErroProvedor as exc:
                    if exc.codigo != "copia_incerta" or not await b("reiniciar_criacao", m, ref):
                        raise
                    arquivo = await copiar(acesso, d)
            else:
                arquivo = d["destino"]
            # Confere também na retomada: cópia na lixeira ou compartilhada não é cadastrada.
            destino = await observar(p, acesso, ref.operacao, d["origem"], arquivo)
        except ErroProvedor as exc:
            if exc.codigo in ("copia_invalida", "copia_ambigua"):
                # Não serve e não vai servir: libera um pedido novo sem mexer no arquivo do jogador.
                await b("descartar_criacao", m, ref)
            raise
        m = await servico._membro(servidor, usuario)
        if d["estado"] != "identificada":
            await b("identificar_criacao", m, ref, destino)
        previa = await validar(acesso, arquivo)
        m = await servico._membro(servidor, usuario)
        return await b("concluir_criacao", m, ref, previa["contrato"])

    return await servico.fila.executar(("criar", ref.operacao), (servidor, usuario), executar,
                                       prazo=PRAZO_JOB_COPIA, espera=PRAZO_JOB_COPIA + 90)


def codigo_de_erro(exc):
    """Código público e curto; o texto do erro não vai pra página nem pro diário."""
    if isinstance(exc, ErroCarteira):
        codigo = getattr(exc, "codigo", "conflito" if isinstance(exc, Conflito) else "solicitacao")
    else:
        codigo = "temporario" if isinstance(exc, TimeoutError) else "interno"
    logging.getLogger(__name__).warning("Criação de ficha não concluída (%s, %s)", codigo, type(exc).__name__)
    return codigo
