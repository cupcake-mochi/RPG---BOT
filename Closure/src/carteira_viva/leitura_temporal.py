"""Guarda interna, em memória, para páginas somente de leitura.

Não cria fichas, não habilita rotas, não guarda tokens e não publica resultados.
Callbacks são do integrador confiável, nunca URL/função enviada pelo navegador.
Versão Drive igual é observação de edição, não snapshot dos cálculos do Sheets.
"""
import asyncio
from dataclasses import dataclass, field, replace
import hashlib
import math
import re
import time

from .provedores import ARQUIVO, ErroProvedor
from .segredos import ErroCarteira, json_bytes

PROTOCOLO = "carteira-conferencia-pagina-1"
POR_PAGINA = 4
MAX_PERFIS = 631
SHA = re.compile(r"[a-f0-9]{64}\Z")
VERSAO = re.compile(r"[0-9]{1,30}\Z")
FLAGS = {"criacaoDisponivel", "conferenciaConjuntaConcluida",
         "imagensAtuaisConferidas", "consistenciaTemporalVerificada"}
CAMPOS_PLANO = {"protocolo", "assinatura", "sequencia", "perfis", "porPagina", "paginas"} | FLAGS
CAMPOS_PAGINA = CAMPOS_PLANO | {"pagina", "lidos", "estado"}


class ErroLeituraTemporal(ErroCarteira):
    def __init__(self, codigo):
        self.codigo = codigo
        mensagens = {"alterada": "A ficha mudou durante a leitura. Inicie uma nova conferência.",
                     "contexto": "O acesso ou a ficha vinculada mudou. Confira a conexão novamente.",
                     "expirada": "O prazo desta leitura terminou. Inicie uma nova conferência.",
                     "incompleta": "Ainda há páginas para conferir.",
                     "temporario": "Não foi possível ler esta página agora. Tente novamente.",
                     "ordem": "Esta página não é a próxima da leitura.",
                     "invalida": "Esta leitura não pode continuar. Inicie uma nova conferência."}
        super().__init__(mensagens.get(codigo, mensagens["invalida"]))


@dataclass(frozen=True)
class _Estado:
    arquivo: str = field(repr=False)
    assinatura_sequencia: str = field(repr=False)
    contexto: str = field(repr=False)
    versao_drive: str = field(repr=False)
    plano: dict = field(repr=False)
    inicio: float = field(repr=False)
    proxima: int = 0
    cadeia: str = field(default="", repr=False)


class GuardaLeitura:
    """Cada avanço só é aceito após versão e autorização serem reconferidas.

    Estado transitório por operação. Reinício do serviço exige leitura nova;
    não restaurar um cursor fornecido pelo cliente ou apagar diários do produtor.
    """
    def __init__(self, provedores, ler_plano, ler_pagina, revalidar_contexto, *,
                 agora=time.monotonic, duracao=1800):
        if type(duracao) not in (int, float) or not math.isfinite(duracao) or not 0 < duracao <= 3600:
            raise ValueError("Prazo de leitura inválido.")
        self._provedores, self._ler_plano, self._ler_pagina = provedores, ler_plano, ler_pagina
        self._revalidar, self._agora, self._duracao = revalidar_contexto, agora, duracao
        self._estado, self._invalidada, self._finalizada = None, False, False
        self._lock = asyncio.Lock()

    def _recusar(self, codigo="invalida"):
        self._invalidada = True
        self._finalizada = False
        raise ErroLeituraTemporal(codigo) from None

    async def _chamar(self, fn, *args, contexto=False):
        try:
            return await fn(*args)
        except asyncio.CancelledError:
            raise
        except ErroProvedor as exc:
            if exc.codigo in {"alterada", "conflito"}:
                self._recusar("alterada")
            if exc.codigo in {"acesso", "arquivo", "revogada", "expirado", "escopo"}:
                self._recusar("contexto")
            raise ErroLeituraTemporal("temporario") from None
        except ErroCarteira:
            self._recusar("contexto" if contexto else "invalida")
        except Exception:
            raise ErroLeituraTemporal("temporario") from None

    def _prazo(self, inicio):
        atual = self._agora()
        if not math.isfinite(inicio) or not math.isfinite(atual) or atual < inicio or atual - inicio >= self._duracao:
            self._recusar("expirada")

    async def _contexto(self, esperado=None):
        valor = await self._chamar(self._revalidar, contexto=True)
        if not isinstance(valor, str) or not SHA.fullmatch(valor) or esperado is not None and valor != esperado:
            self._recusar("contexto")
        return valor

    async def _versao(self, acesso, arquivo, esperada=None):
        valor = await self._chamar(self._provedores.versao_arquivo, acesso, arquivo)
        if not isinstance(valor, str) or not VERSAO.fullmatch(valor):
            self._recusar()
        if esperada is not None and valor != esperada:
            self._recusar("alterada")
        return valor

    def _objeto(self, obj, pagina=False):
        campos = CAMPOS_PAGINA if pagina else CAMPOS_PLANO
        if type(obj) is not dict or set(obj) != campos:
            self._recusar()
        if (obj["protocolo"] != PROTOCOLO or any(obj[k] is not False for k in FLAGS) or
                any(not isinstance(obj[k], str) or not SHA.fullmatch(obj[k]) for k in ("assinatura", "sequencia")) or
                type(obj["perfis"]) is not int or not 1 <= obj["perfis"] <= MAX_PERFIS or
                type(obj["porPagina"]) is not int or obj["porPagina"] != POR_PAGINA or
                type(obj["paginas"]) is not int or obj["paginas"] != (obj["perfis"] + POR_PAGINA - 1) // POR_PAGINA):
            self._recusar()
        return {k: obj[k] for k in CAMPOS_PLANO}

    @staticmethod
    def _hash(valor):
        return hashlib.sha256(json_bytes(valor)).hexdigest()

    def _ativa(self):
        if self._estado is None or self._invalidada:
            self._recusar()
        self._prazo(self._estado.inicio)
        return self._estado

    async def iniciar(self, acesso, arquivo, assinatura_sequencia):
        async with self._lock:
            if self._estado is not None or self._invalidada:
                self._recusar()
            if (not isinstance(arquivo, str) or not ARQUIVO.fullmatch(arquivo) or
                    not isinstance(assinatura_sequencia, str) or not SHA.fullmatch(assinatura_sequencia)):
                self._recusar()
            inicio = self._agora()
            self._prazo(inicio)
            contexto = await self._contexto()
            antes = await self._versao(acesso, arquivo)
            obj = await self._chamar(self._ler_plano, arquivo, assinatura_sequencia)
            plano = self._objeto(obj)
            await self._versao(acesso, arquivo, antes)
            await self._contexto(contexto)
            self._prazo(inicio)
            self._estado = _Estado(arquivo, assinatura_sequencia, contexto, antes, plano, inicio,
                                   cadeia=self._hash([PROTOCOLO, plano]))
            return self.progresso()

    async def avancar(self, acesso, pagina):
        async with self._lock:
            e = self._ativa()
            if type(pagina) is not int or pagina < 0 or pagina >= e.plano["paginas"]:
                raise ErroLeituraTemporal("ordem")
            if pagina != e.proxima and pagina != e.proxima - 1:
                raise ErroLeituraTemporal("ordem")
            await self._contexto(e.contexto)
            await self._versao(acesso, e.arquivo, e.versao_drive)
            # Repetição da última página aceita: não lê/aplica outra nem avança duas vezes.
            if pagina == e.proxima - 1:
                await self._contexto(e.contexto)
                self._prazo(e.inicio)
                return self.progresso()
            obj = await self._chamar(self._ler_pagina, e.arquivo, e.assinatura_sequencia,
                                     e.plano["assinatura"], pagina)
            base = self._objeto(obj, pagina=True)
            quantidade = min(POR_PAGINA, e.plano["perfis"] - pagina * POR_PAGINA)
            if (base != e.plano or type(obj["pagina"]) is not int or obj["pagina"] != pagina or
                    type(obj["lidos"]) is not int or obj["lidos"] != quantidade or
                    not isinstance(obj["estado"], str) or not SHA.fullmatch(obj["estado"])):
                self._recusar()
            await self._versao(acesso, e.arquivo, e.versao_drive)
            await self._contexto(e.contexto)
            self._prazo(e.inicio)
            self._estado = replace(e, proxima=e.proxima + 1,
                                   cadeia=self._hash([e.cadeia, pagina, obj["estado"]]))
            return self.progresso()

    async def finalizar(self, acesso):
        async with self._lock:
            e = self._ativa()
            if e.proxima != e.plano["paginas"]:
                raise ErroLeituraTemporal("incompleta")
            await self._contexto(e.contexto)
            await self._versao(acesso, e.arquivo, e.versao_drive)
            await self._contexto(e.contexto)
            self._prazo(e.inicio)
            self._finalizada = True
            return self.progresso()

    def progresso(self):
        e = self._estado
        return {"paginas_lidas": e.proxima if e else 0, "total_paginas": e.plano["paginas"] if e else 0,
                "leitura_concluida": bool(e and e.proxima == e.plano["paginas"]),
                "versao_drive_estavel_observada": self._finalizada and not self._invalidada,
                "leitura_historica": True, "invalidada": self._invalidada,
                "consistencia_temporal_verificada": False, "imagens_atuais_conferidas": False,
                "conferencia_conjunta_concluida": False, "criacao_disponivel": False}
