"""Diário das células financeiras de cópias próprias ainda não cadastradas.

Não aceita arquivo, plano JSON ou faixa do navegador. PropertiesService e os
demais domínios continuam pendentes, mesmo com as células conferidas.
"""
import re

from .contrato_inicializacao import CONTRATO_SHA256
from .conferencia_inicializacao import FLAGS
from .financeiro_plano import PlanoFinanceiro, hash_obj
from .modelos import OFICIAIS
from .segredos import Conflito, ErroCarteira, json_bytes

PRAZO = 1800


class EnvioFinanceiro:
    """Capacidade interna consumível, emitida só depois de persistir enviada."""
    def __init__(self, arquivo, pedidos):
        self.arquivo, self._pedidos, self._usado = arquivo, pedidos, False

    def consumir(self):
        if self._usado:
            raise Conflito('Este envio já foi consumido. Reconcilie a leitura.')
        self._usado = True
        return self._pedidos

    def __repr__(self):
        return '<EnvioFinanceiro interno>'


class Financeiro:
    def contexto_financeiro(self, membro, ref):
        d = self.contexto_copia(membro, ref)
        oficiais = {re.search(r'/d/([A-Za-z0-9_-]+)', x['url']).group(1) for x in OFICIAIS}
        if (d['estado'] != 'identificada' or not d['destino'] or d['destino'] in oficiais or
                d['destino'] == d['origem'] or self.db.execute(
                    'SELECT 1 FROM fontes WHERE arquivo=?', (d['destino'],)).fetchone()):
            raise Conflito('Somente uma cópia nova, comprovada e ainda não cadastrada pode ser inicializada.')
        return d, hash_obj([CONTRATO_SHA256, ref.servidor, ref.ator, ref.operacao, d])

    @staticmethod
    def _ctx_financeiro(ref):
        return ['financeiro_celulas', ref.servidor, ref.ator, ref.operacao]

    def estado_financeiro(self, membro, ref):
        copia, contexto = self.contexto_financeiro(membro, ref)
        row = self.db.execute('SELECT * FROM financeiro_rest WHERE operacao=?', (ref.operacao,)).fetchone()
        if row is None:
            return None
        d = self.cifra.abrir(self._ctx_financeiro(ref), row['conteudo'])
        if (d['contexto'] != contexto or d['contrato'] != CONTRATO_SHA256 or
                d['arquivo'] != copia['destino'] or d['estado'] != row['estado'] or
                not row['criado'] <= self.agora() < row['expira']):
            raise Conflito('Inicialização fora do contexto ou prazo original. Não envie outra escrita.')
        return d

    def preparar_financeiro(self, membro, ref, plano):
        if type(plano) is not PlanoFinanceiro:
            raise ErroCarteira('Use o planejamento completo do leitor financeiro.')
        with self._transacao():
            copia, contexto = self.contexto_financeiro(membro, ref)
            if (plano.arquivo != copia['destino'] or plano.versao != copia['versao_destino'] or
                    plano.contexto != contexto):
                raise Conflito('A cópia mudou desde sua criação. Não inicialize esse arquivo.')
            atual = self.estado_financeiro(membro, ref)
            if atual:
                if (atual['layout'], atual['antes'], atual['depois']) != (plano.layout, plano.antes, plano.depois):
                    raise Conflito('Outro planejamento já ocupa esta operação.')
                return atual
            d = dict(contrato=CONTRATO_SHA256, contexto=contexto, arquivo=plano.arquivo,
                versao_original=plano.versao, layout=plano.layout, antes=plano.antes, depois=plano.depois,
                pedidos=plano.pedidos.decode(), estado='preparada', versao_observada=None)
            if len(json_bytes(d)) > 32768:
                raise ErroCarteira('Diário financeiro excede o limite.')
            t = self.agora()
            self.db.execute('INSERT INTO financeiro_rest VALUES (?,?,?,?,?)',
                (ref.operacao, 'preparada', t, t+PRAZO, self.cifra.cifrar(self._ctx_financeiro(ref), d)))
            return d

    def _guardar_financeiro(self, ref, d):
        self.db.execute('UPDATE financeiro_rest SET estado=?,conteudo=? WHERE operacao=?',
                        (d['estado'], self.cifra.cifrar(self._ctx_financeiro(ref), d), ref.operacao))

    def armar_financeiro(self, membro, ref, versao):
        with self._transacao():
            d = self.estado_financeiro(membro, ref)
            if not d:
                raise Conflito('Planeje antes de inicializar.')
            if d['estado'] != 'preparada':
                return None  # Enviada/conferida não permitem outro POST.
            if versao != d['versao_original']:
                raise Conflito('A cópia mudou antes da escrita.')
            self._guardar_financeiro(ref, {**d, 'estado': 'enviada'})
            return EnvioFinanceiro(d['arquivo'], d['pedidos'].encode()) if d['antes'] != d['depois'] else None

    def registrar_financeiro(self, membro, ref, leitura):
        if type(leitura) is not PlanoFinanceiro:
            raise ErroCarteira('Use a leitura completa de conferência.')
        with self._transacao():
            d = self.estado_financeiro(membro, ref)
            if (not d or d['estado'] not in ('enviada', 'conferida') or leitura.arquivo != d['arquivo'] or
                    leitura.contexto != d['contexto'] or leitura.layout != d['layout']):
                raise Conflito('A estrutura ou o contexto mudou. Não repita a limpeza.')
            status = 'aguardando_leitura'
            if leitura.antes == d['depois']:
                if leitura.conferencia['erros'] == 0 and leitura.conferencia['pendencias'] == 0:
                    self._guardar_financeiro(ref, {**d, 'estado': 'conferida', 'versao_observada': leitura.versao})
                    status = 'celulas_conferidas'
                else:
                    status = 'aguardando_recalculo'
            elif leitura.antes != d['antes'] or d['estado'] == 'conferida':
                raise Conflito('Há alteração inesperada na cópia. Não repita a escrita.')
            return dict(estado=status, financeiro_celulas_conferidas=status == 'celulas_conferidas',
                financeiro_concluido=False, propriedades_apps_script_pendentes=True, **FLAGS)
