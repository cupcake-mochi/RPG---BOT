"""Comparação privada e transitória de duas leituras REST estritas.

Não observa páginas recusadas pelo leitor, não adota versões e não autoriza
escrita. HMACs só são comparáveis nesta instância e nunca saem no resumo.
"""
import hashlib
import hmac
import json
import math
import secrets
import time
import weakref
from contextlib import aclosing

from .grade_inicializacao import (
    CelulaGrade, LeitorGradeRest, MAX_BYTES, MAX_CELULAS, PaginaGrade, PlanoGrade,
    _celula,
)
from .provedores import VersaoAlterada
from .segredos import ErroCarteira

PRAZO = 1800
MAX_PAGINAS = 128
CATEGORIAS = ('literais', 'formulas', 'resultados', 'notas', 'formatos_numericos')
NAO_COBERTO = (
    'fora_das_faixas', 'outros_formatos', 'imagens', 'mesclas', 'validacoes',
    'protecoes', 'comentarios', 'nomes_definidos', 'configuracao_planilha',
    'metadados_drive', 'propriedades_apps_script', 'codigo_apps_script',
)


def _erro():
    raise ErroCarteira('Diagnóstico de grade indisponível ou incompatível.') from None


def _numero(valor):
    # A API descreve números como double. 1 e 1.0 têm o mesmo valor; bool
    # continua separado pelo tipo ExtendedValue, e texto nunca vira número.
    if type(valor) is float:
        return int(valor) if valor.is_integer() else valor.hex()
    return valor


def _valor(valor):
    if valor is None:
        return None
    tipo, conteudo = valor
    return tipo, _numero(conteudo) if tipo == 'numberValue' else conteudo


class DiagnosticoGrade:
    """Uso interno em piloto: duas coletas, mesma fonte/contexto, até 30 min.

    Recebe planos do leitor autenticado existente. Cada chamada usa os mesmos
    callbacks de autorização/cota e as mesmas guardas de versão, sem rede extra.
    Não persistir esta instância, não serializar __dict__ e fechar no finally.
    Não é recibo, certificado, fingerprint global ou teste da causa da mudança.
    """
    def __init__(self, *, agora=time.monotonic):
        self._agora = agora
        self._inicio = agora()
        self._chave = secrets.token_bytes(32)
        self._amostras = []
        self._ocupado = False
        self._fechado = False

    def __repr__(self):
        return '<DiagnosticoGrade privado>'

    def fechar(self):
        self._chave = b''
        self._amostras.clear()
        self._fechado = True

    def _prazo(self):
        atual = self._agora()
        if (self._fechado or type(atual) not in (int, float) or
                type(self._inicio) not in (int, float) or
                not math.isfinite(atual) or not math.isfinite(self._inicio) or
                not 0 <= atual - self._inicio < PRAZO):
            self.fechar()
            _erro()

    @staticmethod
    def _serializar(valor):
        try:
            b = json.dumps(valor, ensure_ascii=False, separators=(',', ':'),
                           allow_nan=False).encode('utf-8')
        except (TypeError, ValueError, UnicodeError):
            _erro()
        if len(b) > MAX_BYTES:
            _erro()
        return b

    def _hash(self, valor):
        return hmac.digest(self._chave, self._serializar(valor), hashlib.sha256)

    def _pagina(self, faixa, pagina):
        if type(pagina) is not PaginaGrade or pagina.faixa is not faixa:
            _erro()
        r, c, r2, c2 = faixa.pos
        linhas = pagina.celulas
        if (not 0 < (r2-r)*(c2-c) <= MAX_CELULAS or
                type(linhas) is not tuple or len(linhas) != r2-r):
            _erro()
        campos = [hmac.new(self._chave, cat.encode('ascii'), hashlib.sha256)
                  for cat in CATEGORIAS]
        tamanho = 0
        for linha in linhas:
            if type(linha) is not tuple or len(linha) != c2-c:
                _erro()
            for x in linha:
                if type(x) is not CelulaGrade:
                    _erro()
                # O DTO sozinho não comprova que veio de uma resposta validada.
                # Reusar a gramática fechada evita valores estranhos no resumo.
                try:
                    obj = dict(userEnteredValue=dict([x.entrada]) if x.entrada else {},
                               effectiveValue=dict([x.resultado]) if x.resultado else {},
                               note=x.nota)
                    if x.formato_numero is not None:
                        tipo, padrao = x.formato_numero
                        obj['userEnteredFormat'] = {'numberFormat': {'type': tipo, 'pattern': padrao}}
                    if _celula(obj) != x:
                        _erro()
                except (TypeError, ValueError):
                    _erro()
                entrada = _valor(x.entrada)
                formula = entrada is not None and entrada[0] == 'formulaValue'
                valores = (None if formula else entrada, entrada if formula else None,
                           _valor(x.resultado), x.nota, x.formato_numero)
                tamanho += len(self._serializar(valores))
                if tamanho > MAX_BYTES:
                    _erro()
                for resumo, valor in zip(campos, valores):
                    # JSON escapa as quebras de linha dentro de valores; o
                    # delimitador fixa as posições sem reter uma grade paralela.
                    resumo.update(self._serializar(valor) + b'\n')
        return tuple(h.digest() for h in campos)

    async def observar(self, leitor, acesso, plano):
        """Guarda só hashes de páginas aceitas; mudança encerra amostra parcial.

        Não repete/coleta de novo automaticamente. A segunda coleta precisa de
        outro plano aberto explicitamente pelo piloto, sem mudar nenhum recibo.
        Revogação, outros erros e cancelamento descartam TODO o diagnóstico.
        """
        self._prazo()
        if self._ocupado or len(self._amostras) >= 2:
            _erro()
        if (type(leitor) is not LeitorGradeRest or type(plano) is not PlanoGrade or
                plano.dono is not leitor._dono or type(plano.faixas) is not tuple or
                not 0 < len(plano.faixas) <= MAX_PAGINAS):
            _erro()
        # Não reter ID, contexto, nomes de abas, valores ou versão em claro.
        vinculo = self._hash([plano.arquivo, plano.dominio, plano.contexto])
        grade = self._hash([(f.aba, f.grade, f.pos) for f in plano.faixas])
        if self._amostras and self._amostras[0]['vinculo'] != vinculo:
            _erro()
        if self._amostras and self._amostras[0]['plano']() is plano:
            _erro()
        amostra = dict(vinculo=vinculo, grade=grade,
                       plano=weakref.ref(plano),
                       paginas_previstas=len(plano.faixas), paginas=[],
                       versao=self._hash(plano.versao), completa=False,
                       versao_divergente=False)
        self._ocupado = True
        try:
            async with aclosing(leitor.paginas(acesso, plano)) as paginas:
                async for i, pagina in paginas:
                    self._prazo()
                    amostra['paginas'].append(self._pagina(plano.faixas[i], pagina))
                    del pagina
            await leitor.confirmar(acesso, plano)
            self._prazo()
            amostra['completa'] = True
        except VersaoAlterada:
            self._prazo()
            amostra['versao_divergente'] = True
        except BaseException:
            # Inclui cancelamento: não deixar uma amostra com aparência de sucesso.
            self.fechar()
            raise
        finally:
            self._ocupado = False
        self._amostras.append(amostra)
        return self._estado(amostra)

    @staticmethod
    def _estado(amostra):
        return dict(paginas_previstas=amostra['paginas_previstas'],
                    paginas_lidas=len(amostra['paginas']),
                    coleta_completa=amostra['completa'],
                    versao_divergente=amostra['versao_divergente'])

    def comparar(self):
        self._prazo()
        if self._ocupado or len(self._amostras) != 2:
            _erro()
        a, b = self._amostras
        compativel = a['grade'] == b['grade']
        comuns = min(len(a['paginas']), len(b['paginas'])) if compativel else 0
        mudancas = {cat: sum(x[i] != y[i] for x, y in zip(a['paginas'][:comuns], b['paginas'][:comuns]))
                    if comuns else None for i, cat in enumerate(CATEGORIAS)}
        return dict(escopo='faixas_do_leitor_rest', amostras=[self._estado(a), self._estado(b)],
                    cobertura_compativel=compativel, paginas_comparadas=comuns,
                    versoes_iniciais_diferentes=a['versao'] != b['versao'],
                    paginas_com_mudanca=mudancas, nao_coberto=list(NAO_COBERTO),
                    criacao_disponivel=False, conferencia_conjunta_concluida=False,
                    consistencia_temporal_verificada=False, imagens_atuais_conferidas=False)
