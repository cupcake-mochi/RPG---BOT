"""Consulta privada sob demanda: Google, fila, banco e motor determinístico."""
import asyncio
from contextlib import suppress
from dataclasses import asdict
import time
from weakref import WeakValueDictionary

from .fila import Fila
from .cotas import Cotas
from .banco import digest
from .provedores import ErroProvedor
from .segredos import Conflito, ErroCarteira, json_bytes

SCHEMA = "carteira-analise-1"


def preparar_snapshot(leituras, versoes):
    from closure_bot.ficha_r53 import escolher_leitura, transicoes
    ficha = escolher_leitura(leituras)
    indice = next(i for i in reversed(range(len(leituras))) if leituras[i] is ficha)
    return {"ficha": {k: asdict(v) for k, v in ficha.items()},
            "versao_google": versoes[indice], "leituras_google": len(leituras),
            "em_transicao": len(transicoes(ficha))}


class Consultas:
    def __init__(self, dados, provedores, motor=None, *, agora=time.time, fila=None, esperas=(3, 6)):
        self.dados, self.provedores, self.motor = dados, provedores, motor
        self.agora, self.fila, self.esperas = agora, fila or Fila(), esperas
        self.renovacoes = WeakValueDictionary()
        self.cotas = Cotas()

    async def _banco(self, metodo, *args, **kw):
        return await self.dados.chamar("cadastro." + metodo, *args, **kw)

    async def _membro(self, servidor, usuario):
        return await self.provedores.membro(servidor, usuario)

    async def _contexto(self, servidor, usuario, personagem):
        membro = await self._membro(servidor, usuario)
        chave = await self._banco("contexto_leitura", membro, personagem)
        return membro, chave

    async def _atual(self, servidor, usuario, personagem, chave, leitura_id=None):
        m, atual = await self._contexto(servidor, usuario, personagem)
        if atual != chave:
            raise Conflito("A fonte ou a autorização mudou. Consulte a ficha novamente.")
        d = await self._banco("detalhes", m, personagem)
        if leitura_id is not None and (not d["leitura"] or d["leitura"]["id"] != leitura_id):
            raise Conflito("Outra leitura substituiu este resultado. Consulte novamente.")
        return m, d

    @staticmethod
    def _origem(d):
        l = d["leitura"]
        return {"arquivo": d["arquivo"], "revisao": d["revisao"], "leitura_id": l["id"],
                "lido_em": l["lido_em"], "schema": l["schema"],
                "versao_google": l["campos"]["versao_google"],
                "leituras_google": l["campos"]["leituras_google"],
                "em_transicao": l["campos"]["em_transicao"]}

    async def _renovar_google(self, membro, ref):
        """Trava compartilhada; token de acesso só em memória, refresh cifrado."""
        lock = self.renovacoes.setdefault(ref.conexao, asyncio.Lock())
        async with lock:
            membro = await self._membro(ref.servidor, membro.usuario)
            cred = await self._banco("_credencial", membro, ref)
            if cred.cliente != self.provedores.cfg.google_id:
                raise ErroCarteira("Reconecte a ficha no cliente Google atual.")
            async def manter_credencial():
                try:
                    async with asyncio.timeout(30):
                        try:
                            token = await self.provedores.renovar(cred.refresh_token)
                        except ErroProvedor as exc:
                            if exc.codigo == "revogada":
                                await self._banco("marcar_revogada", ref.conexao, autorizacao=cred.autorizacao)
                            raise
                        if token.refresh and token.refresh != cred.refresh_token:
                            await self._banco("_guardar_renovacao_google", ref.conexao,
                                              autorizacao=cred.autorizacao, refresh_anterior=cred.refresh_token,
                                              refresh_novo=token.refresh)
                        return token
                except TimeoutError:
                    raise ErroProvedor("temporario") from None

            # Cancelar a consulta não pode perder uma rotação já enviada ao
            # Google. Concluir só esta manutenção limitada, sob a mesma trava;
            # depois propagar o cancelamento antes de qualquer leitura de ficha.
            tarefa = asyncio.create_task(manter_credencial())
            cancelado = False
            while True:
                try:
                    token = await asyncio.shield(tarefa)
                    break
                except asyncio.CancelledError:
                    if tarefa.cancelled():
                        raise
                    cancelado = True
                except Exception:
                    if cancelado:
                        raise asyncio.CancelledError() from None
                    raise
            if cancelado:
                raise asyncio.CancelledError()
            membro = await self._membro(ref.servidor, membro.usuario)
            await self._banco("_credencial", membro, ref)
            return cred, token

    async def conferir_inicializacao(self, servidor, usuario, personagem, *, retomar=False):
        """Conferência interna somente de leitura; sem endpoint/criação."""
        from .conferencias_servico import conferir
        return await conferir(self, servidor, usuario, personagem, retomar=retomar)

    async def atualizar(self, servidor, usuario, personagem, *, forcar=False):
        m, chave = await self._contexto(servidor, usuario, personagem)
        d = await self._banco("detalhes", m, personagem)
        cache = d["leitura"]
        if (not forcar and cache and cache["fresca"] and cache["schema"] == SCHEMA):
            _, d = await self._atual(servidor, usuario, personagem, chave, cache["id"])
            return self._origem(d) | {"cache": True}

        async def ler():
            # A reserva acontece depois da deduplicação e só ao sair da fila.
            membro, atual = await self._contexto(servidor, usuario, personagem)
            if atual != chave:
                raise Conflito("A fonte mudou enquanto a consulta aguardava.")
            ref = await self._banco("reservar_leitura", membro, personagem)
            cred = None
            try:
                cred, token = await self._renovar_google(membro, ref)
                from closure_bot.ficha_r53 import transicoes
                leituras, versoes = [], []
                for tentativa in range(len(self.esperas) + 1):
                    if tentativa:
                        await asyncio.sleep(self.esperas[tentativa - 1])
                    await self.cotas.esperar(digest(cred.conta))
                    ficha, versao = await self.provedores.ler_analise(token.acesso, ref.arquivo)
                    leituras.append(ficha)
                    versoes.append(versao)
                    if not await asyncio.to_thread(transicoes, ficha):
                        break
                # Não misturar campos de respostas diferentes.
                campos = await asyncio.to_thread(preparar_snapshot, leituras, versoes)
                membro, _ = await self._atual(servidor, usuario, personagem, chave)
                lid = await self._banco("gravar_leitura", membro, ref, campos=campos, schema=SCHEMA)
                return lid
            except BaseException as exc:
                if cred is not None and isinstance(exc, ErroProvedor) and exc.codigo == "revogada":
                    await self._banco("marcar_revogada", ref.conexao, autorizacao=cred.autorizacao)
                with suppress(ErroCarteira):
                    await self._banco("invalidar_leitura", membro, ref)
                raise

        lid = await self.fila.executar(("leitura",) + chave, (servidor, usuario), ler)
        _, d = await self._atual(servidor, usuario, personagem, chave, lid)
        return self._origem(d) | {"cache": False}

    async def analisar(self, servidor, usuario, personagem):
        if self.motor is None:
            raise ErroCarteira("A análise ainda não foi configurada neste serviço.")
        # Análise explícita exige leitura atual; não certifica cache de 60 segundos.
        origem = await self.atualizar(servidor, usuario, personagem, forcar=True)
        m, chave = await self._contexto(servidor, usuario, personagem)
        campanha = await asyncio.to_thread(self.motor.campanha, servidor)
        lid = origem["leitura_id"]

        async def conferir():
            from closure_bot.ficha_leitor import Campo
            membro, d = await self._atual(servidor, usuario, personagem, chave, lid)
            ficha = {k: Campo(**v) for k, v in d["leitura"]["campos"]["ficha"].items()}
            resultado = await asyncio.to_thread(self.motor.conferir, ficha, campanha)
            if origem["em_transicao"]:
                resultado["nao_conferido"].append("Cartões ainda estavam salvando nesta leitura; espere e analise novamente.")
                if resultado["veredito"] == "aprovada":
                    resultado["veredito"] = "pendente"
            saida = {"origem": origem, "campanha": {"servidor": servidor, "nome": campanha.nome,
                     "revisao": campanha.revisao}, "mecanica": "R53", "analisado_em": self.agora(),
                     "motor_revisao": self.motor.revisao, "resultado": resultado}
            if len(json_bytes(saida)) > 2 * 1024 * 1024:
                raise ErroCarteira("O resultado ultrapassou o limite de resposta.")
            membro, _ = await self._atual(servidor, usuario, personagem, chave, lid)
            if (await asyncio.to_thread(self.motor.campanha, servidor)).revisao != campanha.revisao:
                raise Conflito("A campanha mudou durante a análise. Analise novamente.")
            await self._banco("gravar_analise", membro, personagem, leitura_id=lid,
                              campanha_revisao=campanha.revisao, resultado=saida)
            return saida

        await self.fila.executar(("analise",) + chave + (lid, campanha.revisao), (servidor, usuario), conferir)
        return await self.analise_salva(servidor, usuario, personagem)

    async def analise_salva(self, servidor, usuario, personagem):
        """Cada abertura/botão consulta novamente membro, fonte e campanha atuais."""
        if self.motor is None:
            raise ErroCarteira("A análise ainda não foi configurada neste serviço.")
        m, chave = await self._contexto(servidor, usuario, personagem)
        d = await self._banco("detalhes", m, personagem)
        campanha = await asyncio.to_thread(self.motor.campanha, servidor)
        a = d["analise"]
        if (not a or not a["fonte_atual"] or a["campanha_revisao"] != campanha.revisao or
                a["resultado"].get("motor_revisao") != self.motor.revisao):
            raise Conflito("Não há análise atual para esta fonte e campanha. Analise novamente.")
        await self._atual(servidor, usuario, personagem, chave, a["resultado"]["origem"]["leitura_id"])
        return a["resultado"]

    async def fechar(self):
        await self.fila.fechar()
