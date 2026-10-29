"""Coleta REST interna de dois domínios; não executa/inicializa/conclui fichas.

Seletores vêm deste contrato de servidor, nunca de formulário/URL do jogador.
Os diários PropertiesService, imagens, mesclas e validações não são coletados.
"""
from dataclasses import dataclass, field
import asyncio
import math
import re
import time
from urllib.parse import urlencode

from .provedores import ARQUIVO, ErroProvedor
from .segredos import ErroCarteira

MAX_CELULAS = 4096
MAX_BYTES = 4 * 1024 * 1024
TIMEOUT_HTTP = 15
CAMPOS = ('spreadsheetId,sheets(properties(sheetId,title,gridProperties(rowCount,columnCount)),'
          'data(startRow,startColumn,rowData(values(userEnteredValue,effectiveValue,note,'
          'userEnteredFormat(numberFormat)))))')
META = 'spreadsheetId,sheets(properties(sheetId,title,gridProperties(rowCount,columnCount)))'
# Fonte: produtor 2427024, financeiro.gs (operações/guardas) e progressao.gs
# (Dados/Missoes/Preservados). Apenas dependências diretas, sem expansão recursiva.
FIXAS = {
    'financeiro': (('FICHA PESSOAL', 'AW15:AZ87'), ('FICHA PESSOAL', 'BC15:BF87'),
        ('FICHA PESSOAL', 'BI15:BL87'), ('FICHA PESSOAL', 'BO15:BR87'),
        ('FICHA PESSOAL', 'O86:O86'), ('FICHA PESSOAL', 'BI11:BI11'),
        ('FICHA PESSOAL', 'BO11:BO11'), ('FICHA PESSOAL', 'W86:W86'),
        ('DADOS_SALARIOS', 'L2:N2'), ('DADOS_SALARIOS', 'Q2:Q8'),
        ('DADOS_SALARIOS', 'P11:P11'), ('DADOS_SALARIOS', 'AA2:AA2'),
        ('CONFIGURAÇÃO', 'O38:O39'), ('CONFIGURAÇÃO', 'E46:G46'),
        ('CARTEIRA', 'AH3:AH3'), ('CARTEIRA', 'AT3:AT3'), ('FICHA', 'AH11:AH11'),
        ('FICHA', 'AN11:AN11')),
    'progressao': (('CONFIGURAÇÃO', 'C46:H46'), ('DADOS', 'CY47:CZ47'),
        ('DADOS', 'CY54:CZ54'), ('DADOS', 'AQ5:AR33'), ('FICHA', 'AH11:AH11'),
        ('FICHA', 'AN11:AN11'), ('FICHA PESSOAL', 'AW15:BS87'),
        ('CONFIGURAÇÃO', 'C65:G93')),
}
LIVROS = (('EXTRATO', 3), ('SALÁRIOS', 12), ('DADOS_SALARIOS', 10))


def _erro(codigo='formato'):
    raise ErroProvedor(codigo) from None


def _inteiro(v, minimo=0, maximo=10000000):
    return type(v) is int and minimo <= v <= maximo


def _coluna(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _retangulo(a1):
    import re
    m = re.fullmatch(r'([A-Z]+)([1-9][0-9]*):([A-Z]+)([1-9][0-9]*)', a1)
    if not m: _erro()
    def col(s):
        n = 0
        for c in s: n = n * 26 + ord(c) - 64
        return n
    c1, r1, c2, r2 = col(m[1]), int(m[2]), col(m[3]), int(m[4])
    if r2 < r1 or c2 < c1: _erro()
    return r1 - 1, c1 - 1, r2, c2


@dataclass(frozen=True, repr=False)
class _Faixa:
    aba: str
    grade: tuple
    pos: tuple

    def a1(self):
        r, c, fim_r, fim_c = self.pos
        return f"'{self.aba}'!{_coluna(c + 1)}{r + 1}:{_coluna(fim_c)}{fim_r}"


@dataclass(frozen=True, repr=False)
class PlanoGrade:
    """Objeto privado do backend; nunca serializar para o cliente ou restaurar dele."""
    arquivo: str
    versao: str
    dominio: str
    contexto: str
    faixas: tuple
    inicio: float
    dono: object

    def progresso(self):
        return {'paginas': len(self.faixas), 'criacao_disponivel': False,
                'conferencia_conjunta_concluida': False, 'consistencia_temporal_verificada': False,
                'imagens_atuais_conferidas': False}


@dataclass(frozen=True, repr=False)
class CelulaGrade:
    entrada: tuple | None = field(repr=False)
    resultado: tuple | None = field(repr=False)
    nota: str = field(repr=False)
    formato_numero: tuple | None = field(repr=False)


@dataclass(frozen=True, repr=False)
class PaginaGrade:
    """Dados privados transitórios. Sem conversão de datas ou execução de fórmulas."""
    faixa: _Faixa
    celulas: tuple


def _valor(v, *, entrada=False):
    if type(v) is not dict: _erro()
    if not v: return None
    if len(v) != 1: _erro()
    k, x = next(iter(v.items()))
    if k == 'errorValue': _erro('recalculo')
    if k in ('stringValue', 'formulaValue'):
        if type(x) is not str or len(x) > 50000: _erro()
        if k == 'formulaValue' and (not entrada or not x.startswith('=')): _erro()
    elif k == 'boolValue':
        if type(x) is not bool: _erro()
    elif k == 'numberValue':
        if type(x) not in (int, float): _erro()
        try:
            finito = math.isfinite(x)
        except OverflowError:
            finito = False
        if not finito: _erro()
    else: _erro()
    return k, x


def _celula(obj):
    if type(obj) is not dict or set(obj) - {'userEnteredValue', 'effectiveValue', 'note', 'userEnteredFormat'}:
        _erro()
    nota = obj.get('note', '')
    if type(nota) is not str or len(nota) > 50000: _erro()
    fmt = obj.get('userEnteredFormat', {})
    if type(fmt) is not dict or set(fmt) - {'numberFormat'}: _erro()
    numero = fmt.get('numberFormat')
    if numero is not None:
        if (type(numero) is not dict or set(numero) - {'type', 'pattern'} or
                numero.get('type') not in {'TEXT', 'NUMBER', 'PERCENT', 'CURRENCY', 'DATE', 'TIME', 'DATE_TIME', 'SCIENTIFIC'} or
                type(numero.get('pattern', '')) is not str or len(numero.get('pattern', '')) > 1000): _erro()
        numero = numero['type'], numero.get('pattern', '')
    return CelulaGrade(_valor(obj.get('userEnteredValue', {}), entrada=True),
                       _valor(obj.get('effectiveValue', {})), nota, numero)


class LeitorGradeRest:
    """Só GET no arquivo escolhido. Não é coordenador nem endpoint público.

    Callbacks obrigatórios reconferem contexto/cargos/conexão e reservam cota
    para CADA GET. Ainda exige composição confiável desse contexto no serviço
    e fila externa. Plano só vale nesta instância/processo, por até 30 minutos.
    """
    def __init__(self, provedores, revalidar_contexto, aguardar_cota, *, agora=time.monotonic):
        if not callable(revalidar_contexto) or not callable(aguardar_cota):
            raise ValueError("Contexto e controle de cota são obrigatórios.")
        self._p, self._agora, self._dono = provedores, agora, object()
        self._revalidar, self._cota = revalidar_contexto, aguardar_cota

    def _prazo(self, inicio):
        t = self._agora()
        if (type(t) not in (int, float) or not math.isfinite(t) or
                type(inicio) not in (int, float) or not math.isfinite(inicio) or not 0 <= t - inicio < 1800):
            _erro('expirado')

    async def _callback(self, fn, inicio):
        self._prazo(inicio)
        try:
            async with asyncio.timeout(1800 - (self._agora() - inicio)):
                return await fn()
        except asyncio.CancelledError:
            raise
        except TimeoutError:
            _erro('expirado')
        except ErroCarteira:
            _erro('acesso')
        except Exception:
            _erro('temporario')

    async def _contexto(self, inicio, esperado=None):
        self._prazo(inicio)
        valor = await self._callback(self._revalidar, inicio)
        self._prazo(inicio)
        if not isinstance(valor, str) or not re.fullmatch(r'[a-f0-9]{64}', valor): _erro('acesso')
        if esperado is not None and valor != esperado: _erro('acesso')
        return valor

    async def _antes(self, inicio, contexto):
        await self._contexto(inicio, contexto)
        await self._callback(self._cota, inicio)
        # Cargo/conexão podem mudar enquanto a cota aguarda.
        await self._contexto(inicio, contexto)

    async def _http(self, fn, inicio):
        self._prazo(inicio)
        restante = 1800 - (self._agora() - inicio)
        try:
            async with asyncio.timeout(min(TIMEOUT_HTTP, restante)):
                return await fn()
        except TimeoutError:
            _erro('expirado' if restante <= TIMEOUT_HTTP else 'temporario')

    async def _versao(self, acesso, arquivo, inicio, contexto, esperada=None):
        await self._antes(inicio, contexto)
        v = await self._http(lambda: self._p.versao_arquivo(acesso, arquivo), inicio)
        await self._contexto(inicio, contexto)
        if esperada is not None and v != esperada:
            from .provedores import VersaoAlterada
            raise VersaoAlterada(esperada, v)
        return v

    async def _get(self, acesso, arquivo, campos, inicio, contexto, faixa=None):
        q = {'fields': campos}
        if faixa is not None: q['ranges'] = faixa
        await self._antes(inicio, contexto)
        obj = await self._http(lambda: self._p._json(
            'https://sheets.googleapis.com/v4/spreadsheets/' + arquivo + '?' + urlencode(q),
            acesso, limite=MAX_BYTES), inicio)
        await self._contexto(inicio, contexto)
        return obj

    @staticmethod
    def _abas(obj, arquivo):
        if type(obj) is not dict or set(obj) - {'spreadsheetId', 'sheets'} or obj.get('spreadsheetId') != arquivo:
            _erro()
        sheets = obj.get('sheets')
        if type(sheets) is not list or not 1 <= len(sheets) <= 100: _erro()
        grades, ids = {}, set()
        for sheet in sheets:
            if type(sheet) is not dict or set(sheet) - {'properties', 'data'}: _erro()
            p = sheet.get('properties', {})
            if type(p) is not dict or set(p) != {'sheetId', 'title', 'gridProperties'}: _erro()
            nome, sid, grid = p['title'], p['sheetId'], p['gridProperties']
            if type(nome) is not str or not nome or len(nome) > 100 or nome in grades or not _inteiro(sid, 0, 2147483647) or sid in ids: _erro()
            if (type(grid) is not dict or set(grid) != {'rowCount', 'columnCount'} or
                    not _inteiro(grid['rowCount'], 1) or not _inteiro(grid['columnCount'], 1, 18278)): _erro()
            grades[nome] = sid, grid['rowCount'], grid['columnCount']
            ids.add(sid)
        return grades

    async def abrir(self, acesso, arquivo, dominio):
        if not isinstance(arquivo, str) or not ARQUIVO.fullmatch(arquivo) or type(dominio) is not str or dominio not in FIXAS:
            _erro()
        inicio = self._agora(); self._prazo(inicio)
        contexto = await self._contexto(inicio)
        versao = await self._versao(acesso, arquivo, inicio, contexto)
        meta = await self._get(acesso, arquivo, META, inicio, contexto)
        grades = self._abas(meta, arquivo)
        if any('data' in s for s in meta['sheets']): _erro()
        faixas = []
        def adicionar(nome, pos):
            grade = grades.get(nome)
            r, c, fim_r, fim_c = pos
            if not grade or fim_r > grade[1] or fim_c > grade[2]: _erro()
            passo = MAX_CELULAS // (fim_c - c)
            if passo < 1: _erro()
            for a in range(r, fim_r, passo):
                faixas.append(_Faixa(nome, grade, (a, c, min(a + passo, fim_r), fim_c)))
        for nome, a1 in FIXAS[dominio]: adicionar(nome, _retangulo(a1))
        if dominio == 'financeiro':
            for nome, colunas in LIVROS:
                grade = grades.get(nome)
                if not grade or not 2 <= grade[1] <= 5000: _erro('tamanho')
                adicionar(nome, (1, 0, grade[1], colunas))
        self._prazo(inicio)
        await self._versao(acesso, arquivo, inicio, contexto, versao)
        self._prazo(inicio)
        return PlanoGrade(arquivo, versao, dominio, contexto, tuple(faixas), inicio, self._dono)

    async def pagina(self, acesso, plano, indice):
        if type(plano) is not PlanoGrade or plano.dono is not self._dono or type(indice) is not int or not 0 <= indice < len(plano.faixas):
            _erro()
        self._prazo(plano.inicio)
        faixa = plano.faixas[indice]
        await self._versao(acesso, plano.arquivo, plano.inicio, plano.contexto, plano.versao)
        self._prazo(plano.inicio)
        obj = await self._get(acesso, plano.arquivo, CAMPOS, plano.inicio, plano.contexto, faixa.a1())
        grades = self._abas(obj, plano.arquivo)
        if grades != {faixa.aba: faixa.grade}: _erro('alterada')
        s = obj['sheets'][0]; blocos = s.get('data')
        if type(blocos) is not list or len(blocos) != 1 or type(blocos[0]) is not dict: _erro()
        bloco = blocos[0]; r, c, fim_r, fim_c = faixa.pos
        if (set(bloco) - {'startRow', 'startColumn', 'rowData'} or
                type(bloco.get('startRow', 0)) is not int or bloco.get('startRow', 0) != r or
                type(bloco.get('startColumn', 0)) is not int or bloco.get('startColumn', 0) != c): _erro()
        linhas = bloco.get('rowData', [])
        if type(linhas) is not list or len(linhas) > fim_r - r: _erro()
        def montar():
            out = []
            for i in range(fim_r - r):
                row = linhas[i] if i < len(linhas) else {}
                if type(row) is not dict or set(row) - {'values'}: _erro()
                vals = row.get('values', [])
                if type(vals) is not list or len(vals) > fim_c - c: _erro()
                out.append(tuple(_celula(vals[j] if j < len(vals) else {}) for j in range(fim_c - c)))
            return tuple(out)
        celulas = await asyncio.to_thread(montar)
        self._prazo(plano.inicio)
        await self._versao(acesso, plano.arquivo, plano.inicio, plano.contexto, plano.versao)
        self._prazo(plano.inicio)
        return PaginaGrade(faixa, celulas)

    async def confirmar(self, acesso, plano):
        """Última observação autenticada; não certifica cobertura ou cria ficha."""
        if type(plano) is not PlanoGrade or plano.dono is not self._dono:
            _erro()
        await self._versao(acesso, plano.arquivo, plano.inicio, plano.contexto, plano.versao)
