"""Plano privado das células financeiras. Não administra PropertiesService.

Só hashes e pedidos de reset do contrato sobrevivem à coleta. Não interpreta
fórmulas e não guarda histórico, notas pessoais ou uma cópia da grade.
"""
from dataclasses import dataclass, field
import asyncio
import hashlib

from .contrato_inicializacao import carregar, CONTRATO_SHA256
from .conferencia_inicializacao import ConferenciaGrade
from .grade_inicializacao import PlanoGrade, LIVROS, _retangulo
from .segredos import ErroCarteira, json_bytes


def hash_obj(obj):
    return hashlib.sha256(json_bytes(obj)).hexdigest()


def _vazio(e):
    return None if e in (None, ('stringValue', '')) else e


@dataclass(frozen=True, repr=False)
class PlanoFinanceiro:
    arquivo: str
    versao: str
    contexto: str
    layout: str
    antes: str
    depois: str
    pedidos: bytes = field(repr=False)
    paginas: int
    conferencia: dict = field(repr=False)


class MedicaoFinanceira:
    def __init__(self, plano):
        if type(plano) is not PlanoGrade or plano.dominio != 'financeiro':
            raise ErroCarteira('Use uma leitura financeira completa do serviço.')
        self.plano = plano
        self.auditor = ConferenciaGrade(plano)  # Verifica cobertura, contrato e guardas.
        self.guardas = {(op['aba'], p[0], p[1]): tuple(op['formulas'])
                        for op, p in self.auditor._ops if op['tipo'] == 'guarda'}
        self.layout = hash_obj([(f.aba, f.grade, f.pos) for f in plano.faixas])
        self.atual = self.projecao = hash_obj([CONTRATO_SHA256, plano.arquivo, plano.contexto, self.layout])
        self.n = 0
        self.alvos = []
        self.pedidos = []
        grades = {}
        ids = set()
        for f in plano.faixas:
            if f.aba in grades:
                if grades[f.aba] != f.grade:
                    raise ErroCarteira('Grade mudou durante o planejamento.')
            else:
                if f.grade[0] in ids:
                    raise ErroCarteira('Identificação de abas ambígua.')
                grades[f.aba] = f.grade
                ids.add(f.grade[0])
        for op in carregar()['financeiro']['operacoes']:
            if op['tipo'] == 'propriedade':
                continue  # Limite explícito na resposta, nunca concluir financeiro.
            a1 = op['faixa']
            p = list(_retangulo(a1 if ':' in a1 else a1 + ':' + a1))
            grade = grades[op['aba']]
            if (op['aba'], p[3]) in LIVROS:
                p[2] = grade[1]
            self.alvos.append((op, tuple(p)))
            r, c, r2, c2 = p
            cell = {}
            campo = 'note' if op['tipo'] == 'notas' else 'userEnteredValue'
            if op['tipo'] == 'valor':
                v = op['valor']
                k = 'boolValue' if type(v) is bool else 'stringValue' if type(v) is str else 'numberValue'
                cell = {'userEnteredValue': {k: v}}
            self.pedidos.append({'repeatCell': {'range': dict(sheetId=grade[0], startRowIndex=r,
                endRowIndex=r2, startColumnIndex=c, endColumnIndex=c2), 'cell': cell, 'fields': campo}})

    def receber(self, indice, pagina):
        self.auditor.receber(indice, pagina)
        f = pagina.faixa
        r, c, _, _ = f.pos
        agora, depois = [], []
        for i, linha in enumerate(pagina.celulas):
            a, d = [], []
            for j, x in enumerate(linha):
                entrada, nota = _vazio(x.entrada), x.nota
                guarda = self.guardas.get((f.aba, r+i, c+j))
                if guarda and (not entrada or entrada[0] != 'formulaValue' or entrada[1] not in guarda):
                    raise ErroCarteira('Fórmula financeira incompatível. Nada foi enviado.')
                e2, n2 = entrada, nota
                for op, p in self.alvos:
                    if op['aba'] != f.aba or not p[0] <= r+i < p[2] or not p[1] <= c+j < p[3]:
                        continue
                    if op['tipo'] == 'notas':
                        n2 = ''
                    else:
                        if entrada and entrada[0] == 'formulaValue' and not op.get('formulasLivres', False):
                            raise ErroCarteira('Há fórmula inesperada numa entrada financeira. Nada foi enviado.')
                        if op['tipo'] == 'limpar':
                            e2 = None
                        else:
                            v = op['valor']
                            e2 = ('boolValue' if type(v) is bool else 'stringValue' if type(v) is str else 'numberValue', v)
                # Caches podem recalcular. Não são uma prova de preservação das entradas.
                a.append((entrada, nota, x.formato_numero))
                d.append((e2, n2, x.formato_numero))
            agora.append(a)
            depois.append(d)
        self.atual = hash_obj([self.atual, indice, hash_obj(agora)])
        self.projecao = hash_obj([self.projecao, indice, hash_obj(depois)])
        self.n += 1

    def concluir(self):
        if self.n != len(self.plano.faixas):
            raise ErroCarteira('Leitura financeira incompleta.')
        self.auditor.concluir()
        pedidos = json_bytes({'requests': self.pedidos})
        if len(pedidos) > 16384:
            raise ErroCarteira('Pedido financeiro excede o limite.')
        return PlanoFinanceiro(self.plano.arquivo, self.plano.versao, self.plano.contexto, self.layout,
            self.atual, self.projecao, pedidos, self.n, self.auditor.publico())

async def medir(leitor, acesso, arquivo):
    plano = await leitor.abrir(acesso, arquivo, 'financeiro')
    m = MedicaoFinanceira(plano)
    for i in range(len(plano.faixas)):
        pagina = await leitor.pagina(acesso, plano, i)
        await asyncio.to_thread(m.receber, i, pagina)
    await leitor.confirmar(acesso, plano)
    return await asyncio.to_thread(m.concluir)
