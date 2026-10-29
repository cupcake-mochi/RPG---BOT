"""Observações privadas e limitadas; nunca são aprovação ou prova de conteúdo."""
from dataclasses import dataclass
import re

from .segredos import ErroCarteira

ETAPAS = frozenset(('origem_antes_copia', 'origem_antes_localizar', 'origem_apos_candidata',
                    'origem_financeiro', 'copia_candidata', 'copia_apos_origem', 'copia_antes_grade',
                    'copia_antes_envio', 'copia_fechamento', 'copia_leitura'))
LIMITE = 12


@dataclass(frozen=True, repr=False)
class ObservacaoVersao:
    etapa: str
    esperada: str | None
    observada: str

    def __post_init__(self):
        if (type(self.etapa) is not str or self.etapa not in ETAPAS or
                any(type(v) is not str or re.fullmatch(r'[0-9]{1,30}', v) is None
                    for v in (self.observada,) + (() if self.esperada is None else (self.esperada,)))):
            raise ErroCarteira('Observação de versão inválida.')


def conteudo_contexto(copia):
    # Só o histórico técnico fica fora do vínculo. Todos os campos de autoridade,
    # inclusive candidata/versão original, continuam invalidando o contexto.
    return {k: v for k, v in copia.items() if k != 'observacoes_versao'}
