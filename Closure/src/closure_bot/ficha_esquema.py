"""Identidade e tipos semânticos da ANALISE. Células são diagnóstico, nunca identidade."""
import csv
import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def campos_b47():
    with (Path(__file__).parent / 'recursos/b47-campos.tsv').open(encoding='utf-8') as f:
        return {r['chave']: r for r in csv.DictReader(f, delimiter='\t')}


def tipo(chave):
    if chave == 'dominio.degrau':
        return 'texto'
    campo = campos_b47().get(chave)
    if campo and campo['booleano'] == '1':
        return 'booleano'
    if re.fullmatch(r'(?:pericia|oficio|tr)\.[^.]+\.(?:treino|especialista)|sequela\.\d+|treino_arma\..+|personagem\.(?:pericia|oficio)_custom\.\d+\.(?:treino|especializacao)', chave):
        return 'booleano'
    # Enumerações e texto não passam pelo conversor numérico, mesmo que pareçam números.
    if re.fullmatch(r'custom\.forma\.\d+\.(?:peso|resultado)', chave):
        return 'numero'
    if chave.startswith(('aviso.', 'custom.')):
        if re.fullmatch(r'custom\.\d+\.campo\.(?:forca|volume|preco|protecao|desgaste|recarga)', chave):
            return 'numero'
        if re.fullmatch(r'custom\.caminho\.campo\.(?:vida_inicial|vida_por_nivel|pe_por_nivel)', chave):
            return 'numero'
        if re.fullmatch(r'custom\.(?:aptidao|talento|talento_entidade)\.\d+\.(?:categoria|nivel_minimo|refino_minimo)', chave):
            return 'numero'
        return 'texto'
    if chave.startswith('regra.'):
        return 'texto' if chave in ('regra.vida_rolada', 'regra.vida_rolada.campanha') else 'numero'
    if re.fullmatch(r'formato\.versao|nivel|xp|xp\.total|exaustao|sequela\.extras|vida\.rolagem\.\d+|atributo\.[^.]+\.(?:base|corpo)|marco\..+|marcos\.escolhidos|buff\..+|(?:vida|energia|integridade)_max|defesa|protecao|maestria|espacos_de_feitico|classe_maxima|refino_de_graca|classe_0_gratis|morrendo_(?:aguentar|insistir_1|insistir_2)|tecnica\.regra_propria\.(?:categoria|espacos)|dominio\.(?:degrau|custo|refino|corrida)|(?:passiva|aptidao)\.\d+\.categoria|carga\.(?:total|limite|ajuste_limite)', chave):
        return 'numero'
    if re.fullmatch(r'(?:pericia|oficio|tr)\.[^.]+\.(?:ajuste|bonus)|(?:equipavel|item)\.\d+\.(?:grau|volume|quantidade)|personagem\.(?:pericia|oficio)_custom\.\d+\.(?:bonus|resultado)', chave):
        return 'numero'
    if re.fullmatch(r'(?:feitico|liberacao|zero)\.\d+\.classe|(?:feitico|liberacao|zero)\.\d+\.pe|maxima\.pe', chave):
        return 'numero'
    if chave.startswith('invocacao.'):
        resto = re.sub(r'^invocacao\.\d+\.', '', chave)
        if re.fullmatch(r'(?:nivel|nivel_fixo|classe|vida\.max|entrada|retorno|acerto|cd|defesa|deslocamento|limite_familias|limite_livres)|atributo\.[^.]+\.(?:base|buff|total)|buff\..+|(?:bas|esp|ext)\.\d+\.(?:classe|pe)|(?:talento|talento_extra)\.\d+\.categoria|(?:pericia\.\d+|tr\.[^.]+)\.bonus|carga\.(?:total|limite)|carga\.item\.\d+\.volume', resto):
            return 'numero'
    if re.fullmatch(r'efeito\.\d+\.valor', chave):
        return 'numero'
    return 'texto'


def variante(ficha):
    formato = getattr(ficha.get('formato.versao'), 'valor', None)
    configuracao = any(k.startswith(('regra.', 'efeito.', 'custom.')) for k in ficha)
    if formato == 11:
        return 'b47-v11'
    if formato in (1, 2) and not configuracao:
        return f'legado-v{formato}'
    if formato == 4 and not configuracao and any(k.startswith(('carga.', 'pericia.', 'oficio.', 'tr.')) and k.endswith(('.bonus', '.total')) for k in ficha):
        return 'legado-tr-v4'
    return None
