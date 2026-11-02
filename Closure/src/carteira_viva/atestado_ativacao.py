"""Atestado de ativação por efeito observado ("pulso"), sem acesso ao Google.

As rotinas instaladas pelo responsável gravam um pulso na própria planilha ao
concluir cada execução real. Este módulo só classifica pulsos já lidos; não lê,
não escreve e não libera criação. O dono controla tudo na planilha, então isto
protege contra instalação falha, não contra um dono que forje pulsos (decisão
do mantenedor em 02/11; ver docs/carteira-viva/ATIVACAO-PULSO-2026-11-02.md).
"""
from dataclasses import dataclass
import re

from .segredos import ErroCarteira

ROTINAS = ('diario', 'edicao', 'abertura')
TIPOS = ('instalacao',) + ROTINAS
LIMITE_DIARIO = 26 * 3600
TOLERANCIA_FUTURO = 300
_ID = re.compile(r'[A-Za-z0-9_-]{1,128}')

NAO_ATIVADA = 'nao_ativada'
AGUARDANDO = 'aguardando'
ATIVA = 'ativa'
PARADA = 'parada'
INCONSISTENTE = 'inconsistente'


@dataclass(frozen=True)
class Pulso:
    rotina: str
    operacao: str
    arquivo: str
    sequencia: int
    quando: float

    def __post_init__(self):
        if (self.rotina not in TIPOS or type(self.operacao) is not str or not _ID.fullmatch(self.operacao)
                or type(self.arquivo) is not str or not _ID.fullmatch(self.arquivo)
                or type(self.sequencia) is not int or self.sequencia < 1
                or type(self.quando) not in (int, float) or self.quando <= 0):
            raise ErroCarteira('Pulso inválido.')

    @classmethod
    def de_dados(cls, d):
        if not isinstance(d, dict) or set(d) != {'rotina', 'operacao', 'arquivo', 'sequencia', 'quando'}:
            raise ErroCarteira('Pulso inválido.')
        return cls(**d)


@dataclass(frozen=True)
class Atestado:
    estado: str
    motivo: str
    maximos: tuple = ()

    @property
    def ativa(self):
        return self.estado == ATIVA


def _maximos(pulsos):
    m = {}
    for p in pulsos:
        m[p.rotina] = max(m.get(p.rotina, 0), p.sequencia)
    return m


def avaliar(pulsos, *, operacao, arquivo, agora, anterior=None, limite_diario=LIMITE_DIARIO):
    """Classifica os pulsos de uma leitura.

    `anterior` são os máximos de sequência da última leitura guardada pelo bot
    (`Atestado.maximos`); servem só para recusar contador que volta.
    """
    pulsos = tuple(pulsos)
    if any(type(p) is not Pulso for p in pulsos):
        raise ErroCarteira('Pulso inválido.')
    if not pulsos:
        return Atestado(NAO_ATIVADA, 'Nenhum pulso desta ficha.')

    for p in pulsos:
        if p.operacao != operacao or p.arquivo != arquivo:
            return Atestado(INCONSISTENTE, 'Pulso de outra operação ou de outra planilha.')
        if p.quando > agora + TOLERANCIA_FUTURO:
            return Atestado(INCONSISTENTE, 'Pulso com horário no futuro.')

    vistos = set()
    for p in pulsos:
        if (p.rotina, p.sequencia) in vistos:
            return Atestado(INCONSISTENTE, f'Rotina {p.rotina} repetiu a sequência {p.sequencia}; pode estar duplicada.')
        vistos.add((p.rotina, p.sequencia))
    for r in TIPOS:
        seq = sorted((p for p in pulsos if p.rotina == r), key=lambda p: p.sequencia)
        if any(b.quando < a.quando for a, b in zip(seq, seq[1:])):
            return Atestado(INCONSISTENTE, f'Sequência da rotina {r} fora da ordem dos horários.')

    maximos = _maximos(pulsos)
    for r, v in dict(anterior or {}).items():
        if maximos.get(r, 0) < v:
            return Atestado(INCONSISTENTE, f'Contador da rotina {r} voltou desde a última leitura.')
    chave = tuple(sorted(maximos.items()))

    diarios = [p.quando for p in pulsos if p.rotina == 'diario']
    if diarios:
        if agora - max(diarios) > limite_diario:
            return Atestado(PARADA, 'A rotina diária não roda há mais de 26 horas; reative na planilha.', chave)
    else:
        inicio = min(p.quando for p in pulsos)
        if agora - inicio > limite_diario:
            return Atestado(PARADA, 'A rotina diária nunca rodou desde a ativação; reative na planilha.', chave)

    faltam = [r for r in ROTINAS if r not in maximos]
    if faltam:
        texto = {'diario': 'esperar a primeira rotina diária (3h)',
                 'abertura': 'abrir a ficha uma vez', 'edicao': 'editar a ficha uma vez'}
        return Atestado(AGUARDANDO, 'Falta ' + ', '.join(texto[r] for r in faltam) + '.', chave)
    return Atestado(ATIVA, 'As três rotinas foram vistas funcionando.', chave)
