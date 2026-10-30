"""Versão nova do Drive sem edição: prova por conteúdo, nunca adoção.

Experimento nativo de 30/10: o Google sobe `version` sem mudar `modifiedTime`.
Uma versão diferente só é equivalente à referência quando o `modifiedTime` é
idêntico E a impressão de conteúdo do contrato financeiro (hash `conteudo` da
medição: entradas, notas e formatos, sem resultados recalculáveis, sem arquivo
nem contexto na semente) é igual.
As versões originais dos recibos continuam imutáveis; as equivalências ficam
num campo técnico separado, fora do hash de contexto.
"""
from dataclasses import dataclass
import re

from .provedores import MODIFICADO, VersaoAlterada
from .segredos import ErroCarteira

ALVOS = ('origem', 'destino')
LIMITE_EQUIVALENCIAS = 8


@dataclass(frozen=True, repr=False)
class Impressao:
    versao: str
    modificado: str
    conteudo: str

    def __post_init__(self):
        if (type(self.versao) is not str or not re.fullmatch(r'[0-9]{1,30}', self.versao) or
                type(self.modificado) is not str or not MODIFICADO.fullmatch(self.modificado) or
                type(self.conteudo) is not str or not re.fullmatch(r'[a-f0-9]{64}', self.conteudo)):
            raise ErroCarteira('Impressão de conteúdo inválida.')

    def __repr__(self):
        return '<Impressao privada>'

    def dados(self):
        return dict(versao=self.versao, modificado=self.modificado, conteudo=self.conteudo)


def versoes_aceitas(copia, alvo):
    """Versão de referência imutável mais as já provadas equivalentes."""
    if alvo not in ALVOS:
        raise ErroCarteira('Alvo de equivalência inválido.')
    base = copia['versao_origem'] if alvo == 'origem' else copia['versao_destino']
    extras = (copia.get('equivalencias') or {}).get(alvo, [])
    return ({base} | {e['versao'] for e in extras}) - {None}


def confere(referencia, impressao):
    """Só a prova completa vale: mesmo modifiedTime e mesmo conteúdo."""
    if type(impressao) is not Impressao or type(referencia) is not dict:
        return False
    return (referencia.get('modificado') == impressao.modificado and
            referencia.get('conteudo') == impressao.conteudo)


async def impressao(leitor, observar, acesso, arquivo):
    """Mede o contrato financeiro com versão e modifiedTime estáveis do início ao fim.

    `observar(arquivo)` devolve (versao, modificado) já sob contexto/cota do chamador.
    Qualquer mudança durante a leitura recusa; não há nova tentativa aqui.
    """
    from .financeiro_plano import medir
    v1, m1 = await observar(arquivo)
    plano = await medir(leitor, acesso, arquivo)
    v2, m2 = await observar(arquivo)
    if (v1, m1) != (v2, m2) or plano.versao != v1:
        raise VersaoAlterada(v1, v2)
    return Impressao(v1, m1, plano.conteudo)


async def provar(copia, alvo, versao, modificado, gerar, registrar):
    """True só se a versão já é aceita ou se a prova completa foi feita e gravada.

    `gerar()` mede e devolve a Impressao atual; `registrar(imp)` grava no diário
    (que confere de novo contra a referência). False: o chamador recusa como antes.
    """
    if versao in versoes_aceitas(copia, alvo):
        return True
    referencia = copia.get('ref_origem' if alvo == 'origem' else 'ref_destino')
    if referencia is None or modificado is None or referencia.get('modificado') != modificado:
        return False
    atual = await gerar()
    if atual.versao != versao or not confere(referencia, atual):
        return False
    await registrar(atual)
    return True
