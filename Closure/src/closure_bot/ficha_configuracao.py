"""Campanha autorizada e efeitos B47. Nenhuma autorização vem da planilha."""
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from .ficha_leitor import Campo

PADRAO = {
    'nivel_inicial': 2, 'atributos_pontos': 9, 'atributos_teto_criacao': 3, 'atributos_teto': 6,
    'pericias_com_oficio': 9, 'oficios_criacao': 2, 'pericias_sem_oficio': 10,
    'deslocamento_base': 9, 'morrendo_aguentar': .25, 'morrendo_insistir_1': 1/3,
    'morrendo_insistir_2': .5, 'morrendo_teto': 15, 'morrendo_prazo': 3, 'vida_rolada': 'Não',
    'invocacao_familias_abertas_padrao': 3, 'invocacao_familias_livres_padrao': 1,
    'invocacao_familias_abertas_parceria': 4, 'invocacao_familias_livres_parceria': 1,
    'invocacao_familias_abertas_principal': 5, 'invocacao_familias_livres_principal': 2,
    'invocacao_familias_livres_nao_autonoma': 1, 'familias_livres': 2, 'familias_fechadas': 3,
}


def numero(v):
    try:
        return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
    except OverflowError:
        return False


def inteiro(v, minimo=0, maximo=None):
    return isinstance(v, int) and not isinstance(v, bool) and v >= minimo and (maximo is None or v <= maximo)


def valor(ficha, chave):
    return ficha.get(chave, Campo('', '', '')).valor


def impressao_exata(tipo, nome, campos):
    """v2: conserva texto literal e tipo, sem apagar acentos, pontuação, zero ou falso."""
    corpo = json.dumps([tipo, nome, campos], ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return 'b47-v2:' + hashlib.sha256(corpo.encode()).hexdigest()


@dataclass(frozen=True)
class Efeito:
    indice: int
    caixa: str
    como: str
    valor: int | float
    fonte: str
    tipo_de_fonte: str


@dataclass
class ContextoB47:
    regras: dict = field(default_factory=lambda: dict(PADRAO))
    efeitos: dict = field(default_factory=dict)
    aprovados: object = None
    registros: dict = field(default_factory=dict)
    familias: dict = field(default_factory=dict)
    aliases: dict = field(default_factory=dict)
    catalogo_personagem: object = None

    def aplicar(self, caixa, base):
        efeitos = self.efeitos.get(caixa, [])
        trocas = [e.valor for e in efeitos if e.como == 'trocar por']
        if len(trocas) > 1 or base is None:
            return None
        return trocas[0] if trocas else base + sum(e.valor for e in efeitos)


def problema(r, campo, esperado, encontrado, *, pendente=False, regra='configuração', ancora=''):
    from .ficha_corretor import Problema
    (r.pendencias if pendente else r.problemas).append(Problema(regra, campo, esperado, str(encontrado), ancora))


def regras_autorizadas(campanha):
    regras = dict(PADRAO)
    for k, v in campanha.valores.items():
        if k not in PADRAO and not re.fullmatch(r'xp\.(?:[1-9]|[12][0-9])',k):
            raise ValueError(f'regra de campanha desconhecida: {k}')
        if k == 'vida_rolada':
            ok = v in ('Sim', 'Não')
        else:
            ok = numero(v) and v >= 0
            if k.startswith(('atributos_', 'pericias_', 'oficios_', 'invocacao_', 'familias_')) or k in ('nivel_inicial','morrendo_prazo'):
                ok = inteiro(v)
            if k == 'nivel_inicial':
                ok = inteiro(v, 1, 30)
            if k.startswith('invocacao_'):
                ok = inteiro(v, 0, 9)
        if not ok:
            raise ValueError(f'valor autorizado inválido: {k}')
        regras[k] = v
    if campanha.vida_por_nivel == 'rolada':
        regras['vida_rolada'] = 'Sim'
    return regras


def conferir_regras(ficha, campanha, r):
    regras = regras_autorizadas(campanha)
    # Curva publicada pelo produtor; nivel 1 -> 2 permanece ausente, nunca zero implícito.
    livro = json.loads((Path(__file__).parent/'recursos/b47-livro.json').read_text(encoding='utf-8'))
    for k, v in livro['xp'].items():
        regras.setdefault('xp.' + k, v)
    for k, esperado in regras.items():
        chave = 'regra.' + k
        if chave not in ficha:
            problema(r, chave, 'exportar a regra em uso', 'ausente', pendente=True, regra='informação')
            continue
        encontrado = valor(ficha, chave)
        igual = encontrado == esperado if not numero(esperado) else numero(encontrado) and math.isclose(encontrado, esperado, rel_tol=1e-9, abs_tol=1e-9)
        if not igual:
            problema(r, chave, f'{esperado} conforme campanha {campanha.nome}', encontrado, regra='campanha')
        declarada = valor(ficha, chave + '.campanha')
        if declarada != '' and (not numero(esperado) or not numero(declarada) or not math.isclose(declarada, esperado, rel_tol=1e-9, abs_tol=1e-9)) and declarada != esperado:
            problema(r, chave + '.campanha', f'{esperado} autorizado pelo bot; vazio usa o livro', declarada, regra='campanha')
    r.conferidos.append(f'Campanha de referência: {campanha.nome}; regras obtidas do bot')
    return regras


def conferir_efeitos(ficha, ctx, r):
    fontes = {'Pacto','Origem','Origem custom','Item','Técnica','Decisão do mestre'}
    alvos = {'Vida máxima','PE máximo','Integridade máxima','Defesa','Proteção','Iniciativa','CD de feitiço',
             'Conjuração','Corpo a corpo','À distância','Deslocamento','Limite de carga',
             'Invocações · teto de ativas','Invocações · famílias da trilha'}
    from .ficha_testes import RegrasTestes
    livro = json.loads((Path(__file__).parent/'recursos/b47-livro.json').read_text(encoding='utf-8'))
    for tipo in ('Perícia','Ofício','TR'):
        alvos.update(f'{tipo} · {n}' for n in livro[{'Perícia':'pericias','Ofício':'oficios','TR':'trs'}[tipo]])
    alvos.update(f'{"Perícia" if d.tipo=="pericia" else "Ofício"} · {d.nome}' for d in ctx.registros.values() if d.tipo in ('pericia','oficio') and d.valida)
    for i in range(1, 31):
        base = f'efeito.{i}'
        ligado = valor(ficha, base+'.ligado')
        if ligado not in ('',0,1) or isinstance(ligado, bool):
            problema(r, base+'.ligado','marcação 0 ou 1',ligado)
            continue
        if ligado != 1:
            continue
        caixa, como, n, tipo, fonte = [valor(ficha, base+'.'+k) for k in ('caixa','como','valor','tipo_de_fonte','fonte')]
        if caixa not in alvos or como not in ('somar','trocar por') or not numero(n) or tipo not in fontes or not str(fonte).strip():
            problema(r, base,'alvo conhecido, somar/trocar por, número finito e fonte identificada',f'{caixa}; {como}; {n}; {tipo}; {fonte}')
            continue
        e = Efeito(i,caixa,como,n,fonte,tipo)
        ctx.efeitos.setdefault(caixa, []).append(e)
        campos = {'caixa':caixa,'como':como,'valor':n,'tipo_de_fonte':tipo,'fonte':fonte}
        if not ctx.aprovados or impressao_exata('efeito', fonte, campos) not in ctx.aprovados.impressoes:
            problema(r, base, 'aprovação da fonte e aplicação desta definição exata pelo mestre', fonte, pendente=True, regra='aprovação')
    for caixa, efeitos in ctx.efeitos.items():
        if sum(e.como == 'trocar por' for e in efeitos) > 1:
            for e in efeitos:
                problema(r, f'efeito.{e.indice}.como','somente uma troca por caixa; conflito não resolvido',caixa)
        if caixa not in {'Vida máxima','PE máximo','Integridade máxima','Proteção','Defesa'} and not any(
                caixa == f'{"Perícia" if d.tipo=="pericia" else "Ofício"} · {d.nome}'
                for d in ctx.registros.values() if d.tipo in ('pericia','oficio')):
            r.nao_conferido.append(f'Efeito em {caixa}: aplicação numérica ainda não automatizada neste alvo; fonte/aprovação não certificam o resultado')


def carregar_campanha(arquivo, servidor):
    """Arquivo local confiável do operador, separado dos anexos/ANALISE dos jogadores."""
    from .ficha_corretor import RegrasDaCampanha, Aprovados
    if arquivo is None or not Path(arquivo).exists():
        return RegrasDaCampanha(), Aprovados()
    dados = json.loads(Path(arquivo).read_text(encoding='utf-8'))
    cadastro = dados.get(str(servidor), {})
    campanha = RegrasDaCampanha(nome=cadastro.get('nome','livro'), valores=cadastro.get('regras',{}))
    regras_autorizadas(campanha)
    return campanha, Aprovados(cadastro.get('aprovados',{}))
