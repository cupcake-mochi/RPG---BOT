"""Identidade e tipos semânticos da ANALISE. Células são diagnóstico, nunca identidade."""
import csv
import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def campos_b47():
    with (Path(__file__).parent / 'recursos/b47-campos.tsv').open(encoding='utf-8') as f:
        return {r['chave']: r for r in csv.DictReader(f, delimiter='\t')}


EXP_ACERTO = re.compile(r'invocacao\.(?:[1-9]|1[0-2])\.exp\.acerto')


@lru_cache(maxsize=1)
def campos_r53():
    """ANALISE 12/13: as chaves B47, mais as novas da R53 (Ficha---RPG-JJK@4b22da5).

    Uma única mudança de parte: as 12 `invocacao.N.exp.acerto` são o texto "Acerto Nd8" calculado pela ficha, e
    saem como `resultado` desde a correção da Expansão da domada (Ficha---RPG-JJK, 07/11/2026). As cópias de antes
    ainda exportam `entrada`; `parte_aceita` aceita as duas."""
    with (Path(__file__).parent / 'recursos/r53-campos-novos.tsv').open(encoding='utf-8') as f:
        campos = {**campos_b47(), **{r['chave']: r for r in csv.DictReader(f, delimiter='\t')}}
    return {k: ({**v, 'parte': 'resultado'} if EXP_ACERTO.fullmatch(k) else v) for k, v in campos.items()}


def parte_aceita(chave, parte, esperada, *, r53=False):
    """A parte exportada bate com o esquema; no R53, `exp.acerto` em `entrada` ainda vem de cópia anterior a 07/11."""
    return parte == esperada or (r53 and parte == 'entrada' and EXP_ACERTO.fullmatch(chave) is not None)


@lru_cache(maxsize=1)
def campos_opcionais():
    """Chaves que a ficha passou a exportar depois do contrato, sem mudar o formato 12: reconhecidas quando vêm,
    sem pendência quando faltam (cópias antigas). 03/11/2026: as cartas Talento · Origem e Talento · Extra e as vagas
    grátis (Ficha---RPG-JJK, PENDENCIAS de 03/11/2026). 20/11/2026: as 91 chaves da Prática Cotidiana, no fim da
    ANALISE — os cartões 6 e 7 de Classe 0 (`r53.classe0.6/7.*` e `zero.6/7.*`) e as três auxiliares
    `origem.pratica_cotidiana.*` (Ficha---RPG-JJK@bc4bd46, 05/11/2026; lidas das oficiais exportadas em 19/11)."""
    campos = {}
    for nome in ('talentos-gratis-campos.tsv', 'pratica-cotidiana-campos.tsv'):
        with (Path(__file__).parent / 'recursos' / nome).open(encoding='utf-8') as f:
            campos.update({r['chave']: r for r in csv.DictReader(f, delimiter='\t')})
    return campos


def campos_analise():
    """17/11/2026, formato 13: o estado da exportação da ANALISE, no fim da aba, sem célula nem parte
    (Ficha---RPG-JJK, ESQUEMA-ANALISE.md). Aparecem também na ficha 12 que começou a exportar e parou no meio."""
    return {chave: {'chave': chave, 'parte': '', 'origem': '', 'booleano': '0'}
            for chave in ('analise.estado', 'analise.exportada_em')}


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
    if re.fullmatch(r'formato\.versao|nivel|xp|xp\.total|exaustao|sequela\.extras|vida\.rolagem\.\d+|atributo\.[^.]+\.(?:base|corpo)|marco\..+|marcos\.escolhidos|buff\..+|(?:vida|energia|integridade)_max|defesa|protecao|maestria|espacos_de_feitico|classe_maxima|refino_de_graca|classe_0_gratis|morrendo_(?:aguentar|insistir_1|insistir_2)|tecnica\.regra_propria\.(?:categoria|espacos)|dominio\.(?:degrau|custo|refino|corrida)|(?:passiva|aptidao)\.\d+\.categoria|passiva\.(?:origem|extra)\.categoria|vagas\.[a-z_]+|carga\.(?:total|limite|ajuste_limite)|origem\.pratica_cotidiana\.(?:vagas|anotados)', chave):
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
    # O 13 é o mesmo contrato do 12 com a coluna B congelada na exportação: mesmas chaves, mesmo sentido.
    if formato in (12, 13):
        return 'r53-v12'
    if formato in (1, 2) and not configuracao:
        return f'legado-v{formato}'
    if formato == 4 and not configuracao and any(k.startswith(('carga.', 'pericia.', 'oficio.', 'tr.')) and k.endswith(('.bonus', '.total')) for k in ficha):
        return 'legado-tr-v4'
    return None
