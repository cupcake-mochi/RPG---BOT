"""Tentativas web cifradas. Todos os métodos rodam no worker único do cadastro."""
from concurrent.futures import ThreadPoolExecutor
import asyncio
import hmac
import json
import secrets

from .banco import Cadastro, CredencialGoogle, digest, texto
from .permissoes import Acao, Membro
from .segredos import AcessoNegado, Conflito, ErroCarteira


class ErroFluxo(ErroCarteira):
    def __init__(self, codigo="expirada"):
        self.codigo = codigo
        super().__init__("Esta conexão expirou ou mudou. Abra uma nova solicitação pelo Discord.")


def nome_cookie(fid: str, segura: bool) -> str:
    return ("__Host-" if segura else "") + "cv_" + fid[:24]


class Fluxos:
    def __init__(self, cadastro: Cadastro, origem: str, cliente_google: str):
        self.c, self.origem, self.cliente = cadastro, origem, cliente_google
        from .sessoes import Sessoes
        self.sessoes = Sessoes(cadastro)

    def _row(self, ticket):
        if not isinstance(ticket, str) or not 30 <= len(ticket) <= 100:
            raise ErroFluxo()
        row = self.c.db.execute("SELECT * FROM web_fluxos WHERE id=? AND expira>?",
                                (digest(ticket), self.c.agora())).fetchone()
        if not row:
            raise ErroFluxo()
        r = dict(row)
        d = self.c.cifra.abrir(["fluxo", r["id"]], r["dados"])
        if d["origem"] != self.origem:
            raise ErroFluxo()
        return r, d

    def _sessao(self, ticket, cookie, csrf=None, fases=None):
        r, d = self._row(ticket)
        if (not isinstance(cookie, str) or not r["cookie"] or
                not hmac.compare_digest(r["cookie"], digest(cookie))):
            raise AcessoNegado("Reabra a conexão no mesmo navegador.")
        if csrf is not None and (not isinstance(csrf, str) or not hmac.compare_digest(d["csrf"], csrf)):
            raise AcessoNegado("Confirmação da sessão inválida.")
        if fases is not None and r["fase"] not in fases:
            raise ErroFluxo("etapa")
        return r, d

    def _salvar(self, r, d):
        self.c.db.execute("""UPDATE web_fluxos SET fase=?,cookie=?,estado=?,provedor=?,conexao=?,dados=? WHERE id=?""",
                          (r["fase"], r["cookie"], r["estado"], r["provedor"], r["conexao"],
                           self.c.cifra.cifrar(["fluxo", r["id"]], d), r["id"]))

    def criar(self, membro: Membro, acao: str, personagem: str | None):
        self.c._membro(membro)
        if (acao not in ("cadastro", "troca", "reconectar", "modelo") or
                (acao in ("troca", "reconectar") and not personagem) or (acao == "modelo" and personagem is not None)):
            raise ErroCarteira("Ação de conexão inválida.")
        if acao == "modelo":
            self.c._autorizar(membro, Acao.CONFIGURAR)
        with self.c._transacao():
            ativos = self.c.db.execute("""SELECT count(*) FROM web_fluxos WHERE usuario=? AND expira>?
                AND fase NOT IN ('concluido','cancelado','falhou')""", (membro.usuario, self.c.agora())).fetchone()[0]
            recentes = self.c.db.execute("SELECT count(*) FROM web_fluxos WHERE usuario=? AND criado>?",
                                         (membro.usuario, self.c.agora() - 60)).fetchone()[0]
            if ativos >= 3 or recentes >= 10:
                raise ErroFluxo("limite")
            conexoes = self.c.db.execute("""SELECT id,autorizacao,estado FROM conexoes
                WHERE usuario=? LIMIT 21""", (membro.usuario,)).fetchall()
            if len(conexoes) > 20:
                raise ErroFluxo("limite")
            ticket = secrets.token_urlsafe(32)
            config = self.c.db.execute("SELECT idioma FROM servidores WHERE id=?", (membro.servidor,)).fetchone()
            d = {"ticket": ticket, "origem": self.origem, "acao": acao, "personagem": personagem,
                 "csrf": secrets.token_urlsafe(32), "idioma": config[0] if config else "pt-BR",
                 "baselines": {x["id"]: [x["autorizacao"], x["estado"]] for x in conexoes}}
            conexao = None
            if acao == "modelo":
                d["modelo_revisao"] = self.c.revisar_modelo(membro)["revisao"]
            if acao in ("troca", "reconectar"):
                p = self.c._personagem(membro, personagem, Acao.TROCAR_ARQUIVO)
                f = self.c._fonte(membro.servidor, personagem)
                conexao = f["conexao"]
                d.update(revisao=f["revisao"], arquivo_anterior=f["arquivo"], conexao_alvo=conexao)
                d["nome_atual"] = self.c.cartao(membro, personagem)["perfil"]["nome"]
            self.c.db.execute("INSERT INTO web_fluxos VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                              (digest(ticket), membro.servidor, membro.usuario, self.c.agora(),
                               self.c.agora() + 600, "novo", None, None, None, conexao,
                               self.c.cifra.cifrar(["fluxo", digest(ticket)], d)))
            return ticket

    def abrir(self, ticket, cookie_novo):
        with self.c._transacao():
            r, d = self._row(ticket)
            if r["fase"] != "novo":
                self._sessao(ticket, cookie_novo)
                return False
            r.update(cookie=digest(cookie_novo), fase="identificar")
            self._salvar(r, d)
            return True

    def contexto(self, ticket):
        r, _ = self._row(ticket)
        return {"id": r["id"], "servidor": r["servidor"], "usuario": r["usuario"]}

    def estado(self, ticket, cookie):
        r, d = self._sessao(ticket, cookie)
        saida = {"fase": r["fase"], "csrf": d["csrf"], "idioma": d["idioma"],
                 "acao": d["acao"], "previa": d.get("previa"), "resultado": d.get("resultado")}
        saida["nome_atual"] = d.get("nome_atual")
        if r["fase"] == "google":
            rows = self.c.db.execute("""SELECT id FROM conexoes WHERE usuario=? AND cliente_hash=?
                AND estado='ativa' ORDER BY id LIMIT 20""", (r["usuario"], digest(self.cliente))).fetchall()
            saida["conexoes"] = [x[0] for x in rows if not d.get("conexao_alvo") or x[0] == d["conexao_alvo"]]
        return saida

    def login(self, ticket, cookie, csrf, provedor):
        fases = {"discord": ("identificar",), "google": ("google", "picker", "revisar")}
        if provedor not in fases:
            raise ErroFluxo()
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, csrf, fases[provedor])
            estado, verificador = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
            d.pop("google", None); d.pop("previa", None)
            d["oauth"] = {"estado": estado, "verificador": verificador}
            r.update(fase="oauth_" + provedor, estado=digest(estado), provedor=provedor)
            self._salvar(r, d)
            return d["oauth"]

    def consumir_retorno(self, estado, provedor, cookie):
        with self.c._transacao():
            if not isinstance(estado, str) or not 30 <= len(estado) <= 100:
                raise ErroFluxo()
            row = self.c.db.execute("SELECT * FROM web_fluxos WHERE estado=? AND provedor=?",
                                    (digest(estado), provedor)).fetchone()
            if not row:
                raise ErroFluxo()
            d = self.c.cifra.abrir(["fluxo", row["id"]], row["dados"])
            r, d = self._sessao(d["ticket"], cookie, fases=("oauth_" + provedor,))
            oauth = d.pop("oauth")
            r.update(fase="processando_" + provedor, estado=None)
            self._salvar(r, d)
            return {"ticket": d["ticket"], "servidor": r["servidor"], "usuario": r["usuario"], **oauth}

    def por_estado(self, estado, provedor):
        row = self.c.db.execute("SELECT id FROM web_fluxos WHERE estado=? AND provedor=?",
                                (digest(estado), provedor)).fetchone()
        if not row:
            raise ErroFluxo()
        return row[0]

    def identificar(self, ticket, cookie, novo_cookie, membro):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, fases=("processando_discord",))
            if (membro.servidor, membro.usuario, membro.presente) != (r["servidor"], r["usuario"], True):
                raise AcessoNegado("Entre com a conta que iniciou a conexão.")
            if d["acao"] == "modelo":
                self.c._autorizar(membro, Acao.CONFIGURAR)
            r.update(cookie=digest(novo_cookie), fase="google", provedor=None)
            d["csrf"] = secrets.token_urlsafe(32)
            self._salvar(r, d)

    def _baseline(self, d, conexao):
        if conexao and d["baselines"].get(conexao["id"]) != [conexao["autorizacao"], conexao["estado"]]:
            raise Conflito("A conexão mudou durante a solicitação. Reabra pelo Discord.")

    def preparar_uso(self, ticket, cookie, csrf, cid):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, csrf, ("google",))
            x = self.c.db.execute("SELECT * FROM conexoes WHERE id=? AND usuario=? AND estado='ativa' AND cliente_hash=?",
                                  (cid, r["usuario"], digest(self.cliente))).fetchone()
            if not x or (d.get("conexao_alvo") and x["id"] != d["conexao_alvo"]):
                raise AcessoNegado("Escolha uma conexão sua e compatível.")
            self._baseline(d, x)
            obj = self.c.cifra.abrir(["conexao", x["id"], x["usuario"], x["autorizacao"]], x["segredo"])
            r.update(fase="renovando", conexao=cid)
            self._salvar(r, d)
            return {"id": cid, "credencial": CredencialGoogle(obj["conta"], obj["cliente"], obj["refresh"], x["autorizacao"])}

    def google_ok(self, ticket, cookie, *, conta, token, reutilizada=False):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, fases=("processando_google", "renovando"))
            x = self.c.db.execute("SELECT * FROM conexoes WHERE usuario=? AND conta_hash=? AND cliente_hash=?",
                                  (r["usuario"], digest(conta), digest(self.cliente))).fetchone()
            if d.get("conexao_alvo") and (not x or x["id"] != d["conexao_alvo"]):
                raise AcessoNegado("Use a conta Google vinculada a este personagem.")
            self._baseline(d, x)
            refresh = None if reutilizada else token.refresh
            if refresh is None and (not x or x["estado"] != "ativa"):
                raise ErroFluxo("consentimento")
            d["google"] = {"conta": conta, "acesso": token.acesso, "refresh": refresh,
                           "expira": token.expira, "conexao": x["id"] if x else None}
            r.update(fase="picker", provedor=None, conexao=x["id"] if x else None)
            self._salvar(r, d)
            return d.get("arquivo_anterior") if d["acao"] == "reconectar" else None

    def google(self, ticket, cookie, csrf=None):
        r, d = self._sessao(ticket, cookie, csrf, ("picker", "revisar", "validando", "confirmando"))
        g = d["google"]
        if g["expira"] <= self.c.agora() + 15:
            raise ErroFluxo("expirada")
        if g["conexao"]:
            x = self.c.db.execute("SELECT * FROM conexoes WHERE id=?", (g["conexao"],)).fetchone()
            if not x:
                raise ErroFluxo()
            self._baseline(d, x)
        return g.copy()

    def preparar_selecao(self, ticket, cookie, csrf):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, csrf, ("picker", "revisar"))
            g = self.google(ticket, cookie, csrf)
            r["fase"] = "validando"
            self._salvar(r, d)
            return g

    def arquivo_ok(self, ticket, cookie, previa):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, fases=("validando",))
            if d["acao"] == "reconectar" and previa["arquivo"] != d["arquivo_anterior"]:
                raise Conflito("A reconexão deve usar o arquivo já vinculado.")
            d["previa"] = previa
            r["fase"] = "revisar"
            self._salvar(r, d)

    def preparar_confirmacao(self, ticket, cookie, csrf, nome, responsabilidade):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, csrf, ("revisar", "concluido"))
            if r["fase"] == "concluido":
                return {"resultado": d["resultado"]}
            if responsabilidade is not True:
                raise ErroFluxo("responsabilidade")
            g = self.google(ticket, cookie, csrf)
            d["nome_confirmado"] = texto(nome or d["previa"]["nome"], "Nome do personagem", 100)
            r["fase"] = "confirmando"
            self._salvar(r, d)
            return {"google": g, "previa": d["previa"]}

    def finalizar(self, ticket, cookie, membro, previa):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, fases=("confirmando",))
            if (membro.servidor, membro.usuario, membro.presente) != (r["servidor"], r["usuario"], True):
                raise AcessoNegado("A participação no servidor mudou.")
            g = self.google(ticket, cookie)
            if any(previa[k] != d["previa"][k] for k in ("arquivo", "contrato")):
                raise Conflito("A ficha mudou durante a confirmação.")
            if d["acao"] == "modelo":
                from .modelos import referencia_validada
                if referencia_validada(previa) != referencia_validada(d["previa"]):
                    raise Conflito("O modelo mudou durante a confirmação.")
                resultado = self.c.configurar_modelo(membro, escolha="servidor", revisao=d["modelo_revisao"], previa=previa)
                return self._concluir(r, d, resultado)
            if d["acao"] in ("troca", "reconectar"):
                self.c._personagem(membro, d["personagem"], Acao.TROCAR_ARQUIVO)
                f = self.c._fonte(membro.servidor, d["personagem"])
                if f["revisao"] != d["revisao"] or f["conexao"] != d["conexao_alvo"]:
                    raise Conflito("O arquivo vinculado mudou durante a confirmação.")
            atual = self.c.db.execute("SELECT * FROM conexoes WHERE usuario=? AND conta_hash=? AND cliente_hash=?",
                                      (membro.usuario, digest(g["conta"]), digest(self.cliente))).fetchone()
            self._baseline(d, atual)
            cid = self.c.conectar(membro, conta=g["conta"], cliente=self.cliente, refresh_token=g["refresh"])
            if d["acao"] == "cadastro":
                resultado = self.c.cadastrar(membro, conexao=cid, arquivo=previa["arquivo"], nome=d["nome_confirmado"],
                                             contrato=previa["contrato"], responsabilidade=True, pedido=r["id"])
            else:
                if d["acao"] == "troca":
                    self.c.trocar_arquivo(membro, d["personagem"], arquivo=previa["arquivo"], conexao=cid,
                                          contrato=previa["contrato"], revisao=d["revisao"], pedido=r["id"])
                resultado = self.c.cartao(membro, d["personagem"])
            return self._concluir(r, d, resultado)

    def _concluir(self, r, d, resultado):
        # Modelo não chama conectar: o OAuth do administrador não vira acesso do jogador.
        d = {k: d[k] for k in ("ticket", "csrf", "idioma", "acao", "origem")}
        d["resultado"] = resultado
        r.update(fase="concluido", conexao=None, estado=None, provedor=None)
        self._salvar(r, d)
        return resultado

    def encerrar(self, ticket, cookie, csrf, *, falhou=False):
        with self.c._transacao():
            r, d = self._sessao(ticket, cookie, csrf)
            if r["fase"] in ("concluido", "cancelado", "falhou"):
                return
            d = {k: d[k] for k in ("ticket", "csrf", "idioma", "acao", "origem")}
            r.update(fase="falhou" if falhou else "cancelado", estado=None, provedor=None, conexao=None)
            self._salvar(r, d)

    def limpar(self):
        self.sessoes.limpar()
        return self.c.limpar()


class DadosAsync:
    """Uma thread cria, usa e fecha o SQLite; a fila é limitada pelo serviço HTTP."""
    def __init__(self, cfg, *, agora):
        self.cfg, self.agora = cfg, agora
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="carteira-db")
        self.store = None

    async def iniciar(self):
        def criar():
            c = Cadastro(self.cfg.banco, self.cfg.chaves, agora=self.agora)
            self.store = Fluxos(c, self.cfg.origem, self.cfg.google_id)
            c.limpar()
        await asyncio.wrap_future(self.executor.submit(criar))

    async def chamar(self, metodo, *args, **kwargs):
        def executar():
            alvo = self.store.c if metodo.startswith("cadastro.") else self.store.sessoes if metodo.startswith("sessoes.") else self.store
            return getattr(alvo, metodo.removeprefix("cadastro.").removeprefix("sessoes."))(*args, **kwargs)
        return await asyncio.wrap_future(self.executor.submit(executar))

    async def fechar(self):
        if self.store:
            await asyncio.wrap_future(self.executor.submit(self.store.c.fechar))
        self.executor.shutdown(wait=True, cancel_futures=True)
