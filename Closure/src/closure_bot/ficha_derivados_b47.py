"""Contas derivadas B47. Resultado exportado nunca escolhe uma entrada ausente.

Alguns seletores e ajustes não pertencem ao contrato 11 entregue. Nesses casos
validamos apenas contradições ou resultados independentes dessas entradas e
explicamos exatamente o que impede certificar o restante.
"""
import math
import re

from .ficha_configuracao import valor, numero, inteiro, problema
from .ficha_testes import ATRIBUTOS, TRS, atributo


def resultado_numerico(v, apresentacao='numero'):
    if numero(v):
        return v
    if not isinstance(v, str):
        return None
    padrao = {'numero': r'([+−-]?\d+(?:[.,]\d+)?)',
              'd20': r'd20\s*\+\s*([+−-]?\d+(?:[.,]\d+)?)',
              'metros': r'([+−-]?\d+(?:[.,]\d+)?)\s*m'}[apresentacao]
    m = re.fullmatch(padrao, v.strip())
    return float(m[1].replace('−', '-').replace(',', '.')) if m else None


def conferir_derivados(ficha, ref, ctx, r):
    n = valor(ficha, 'nivel')
    if not inteiro(n, 1, 30):
        return
    maestria = ref.magia.maestria[n]
    atrs = {}
    for a in ATRIBUTOS:
        v, c = [valor(ficha, f'atributo.{a}.{p}') for p in ('base', 'corpo')]
        if numero(v) and (c == '' or numero(c)):
            atrs[a] = v + (c or 0)

    def ajuste(k):
        v = valor(ficha, 'buff.' + k)
        if v == '':
            return 0
        if not numero(v):
            problema(r, 'buff.' + k, 'ajuste numérico finito', v, regra='conta')
            return None
        if v:
            problema(r, 'buff.' + k, 'confirmar fonte e ausência de duplicação com BÔNUS E MUDANÇAS',
                     v, pendente=True, regra='aprovação')
        return v

    def comparar(k, esperado, modo='numero', ancora='geral--testes'):
        v = valor(ficha, k)
        if esperado is None:
            r.nao_conferido.append(f'{k}: entradas insuficientes ou efeitos em conflito')
        elif v == '':
            problema(r, k, f'exportar resultado calculado ({esperado:g})', v,
                     pendente=True, regra='informação', ancora=ancora)
        elif resultado_numerico(v, modo) != esperado:
            problema(r, k, f'{esperado:g}', v, regra='conta', ancora=ancora)
        else:
            r.conferidos.append(f'{k}: {esperado:g}')

    comparar('maestria', maestria, ancora='progressao--prog-tabela-inicial')
    comparar('classe_maxima', ref.magia.classe_maxima(n), ancora='fundamento--pontos')
    marcos = sum(m <= n for m in ref.marcos)
    comparar('refino_de_graca', min(ref.refino_maximo, 1 + marcos), ancora='aptidoes--apt-marcos')
    comparar('classe_0_gratis', 2 + sum(m <= n for m in (5, 11, 17)),
             ancora='fundamento--classezero')
    b = ajuste('iniciativa')
    comparar('iniciativa', ctx.aplicar('Iniciativa', atrs['destreza'] + b)
             if 'destreza' in atrs and b is not None else None, 'd20')

    # O contrato omite Z67/AK67/AE70 (seletores pessoais). Nem a coordenada nem
    # os valores iniciais da ficha são identidade ou escolha do personagem.
    for k, caixa, parcela, modo in [('cd_de_feitico', 'CD de feitiço', 8, 'numero'),
                                    ('conjuracao', 'Conjuração', 0, 'd20'),
                                    ('corpo_a_corpo', 'Corpo a corpo', 0, 'd20'),
                                    ('a_distancia', 'À distância', 0, 'd20')]:
        b = ajuste(k)
        trocas = [e for e in ctx.efeitos.get(caixa, []) if e.como == 'trocar por']
        if len(trocas) == 1:
            comparar(k, ctx.aplicar(caixa, 0), modo)
        elif len(trocas) > 1 or b is None or len(atrs) != 5:
            comparar(k, None, modo)
        else:
            possibilidades = {ctx.aplicar(caixa, a + maestria + parcela + b) for a in atrs.values()}
            v = valor(ficha, k)
            if v != '' and resultado_numerico(v, modo) not in possibilidades:
                problema(r, k, 'resultado compatível com um atributo: ' + ', '.join(f'{x:g}' for x in sorted(possibilidades)),
                         v, regra='conta')
            elif v == '':
                problema(r, k, 'resultado calculado e atributo selecionado', v, pendente=True, regra='informação')
        r.nao_conferido.append(f'{k}: seletor do atributo pessoal não exportado pela B47; não se deduz a escolha do resultado')

    # A falta de quantidade/Volume e do Buff de limite impede reconstruir a
    # punição de carga. Ainda assim, resultados fora de TODAS as possibilidades
    # (parado, meia marcha, marcha normal) são divergências demonstráveis.
    b = ajuste('deslocamento')
    exaustao = valor(ficha, 'exaustao')
    if exaustao == '':
        exaustao = 0  # N(caixa vazia) é zero no estado do personagem.
    if not inteiro(exaustao, 0, 3):
        problema(r, 'exaustao', 'degrau inteiro de 0 a 3', exaustao, regra='conta')
    elif b is not None:
        base = ctx.regras['deslocamento_base'] + b
        teto = 4.5 if exaustao >= 2 else math.inf
        possibilidades = {ctx.aplicar('Deslocamento', v) for v in (0, min(teto, base / 2), min(teto, base))}
        if None in possibilidades:
            comparar('deslocamento', None, 'metros')
        elif len(possibilidades) == 1:
            comparar('deslocamento', possibilidades.pop(), 'metros')
        else:
            v = valor(ficha, 'deslocamento')
            if v != '' and resultado_numerico(v, 'metros') not in possibilidades:
                problema(r, 'deslocamento', 'metros dentro das possibilidades de carga/Força: ' +
                         ', '.join(f'{x:g}' for x in sorted(possibilidades)), v, regra='conta', ancora='geral--carga')
            elif v == '':
                problema(r, 'deslocamento', 'resultado calculado em metros', v, pendente=True, regra='informação')
            r.nao_conferido.append('deslocamento: carga/ajuste de limite não exportados impedem escolher a penalidade efetiva')
    sequela = [valor(ficha, f'sequela.{i}') for i in range(1, 4)]
    extras = valor(ficha, 'sequela.extras')
    if extras == '':
        extras = 0
    if all(type(v) is int and v in (0, 1) for v in sequela) and inteiro(extras):
        prazo = max(0, ctx.regras['morrendo_prazo'] - sum(sequela) - extras)
        esperado = 'Derrotado na hora' if prazo == 0 else f'{prazo} ' + ('rodada' if prazo == 1 else 'rodadas')
        v = valor(ficha, 'morrendo_prazo')
        if v == '':
            problema(r, 'morrendo_prazo', esperado, v, pendente=True, regra='informação', ancora='dano--morrendo')
        elif v != esperado:
            problema(r, 'morrendo_prazo', esperado, v, regra='conta', ancora='dano--morrendo')
        else:
            r.conferidos.append('morrendo_prazo: ' + esperado)
    else:
        problema(r, 'sequela.extras', 'Sequelas 0/1 e extras inteiras não negativas', extras, regra='conta')

    trs = [valor(ficha, 'tr.' + slug + '.treino') for slug in TRS]
    if any(type(v) is not int or v not in (0, 1) for v in trs):
        problema(r, 'tr', 'marcar cada treino como 0/1', trs, regra='treinos', ancora='ab--ab-origem')
    elif sum(trs) != 2:
        problema(r, 'tr', 'escolher exatamente dois TR diferentes', trs,
                 pendente=sum(trs) < 2, regra='treinos', ancora='ab--ab-origem')
    else:
        r.conferidos.append('TR: dois treinos diferentes; bônus não exportados permanecem não conferidos')


def conferir_tr_entidade(ficha, ctx, r, base):
    escolhido = valor(ficha, base + '.tr_treinado')
    if escolhido not in {nome for nome, _ in TRS.values()}:
        problema(r, base + '.tr_treinado', 'um TR treinado da entidade', escolhido,
                 pendente=escolhido == '', regra='treinos', ancora='construcao--entidades-atributos')
    if atributo(valor(ficha, base + '.atributo_fisico')) not in ('forca', 'destreza'):
        problema(r, base + '.atributo_fisico', 'Força ou Destreza, escolha fixa',
                 valor(ficha, base + '.atributo_fisico'), pendente=valor(ficha, base + '.atributo_fisico') == '',
                 regra='treinos', ancora='construcao--entidades-atributos')
    for slug in TRS:
        k = base + '.buff.tr.' + slug
        v = valor(ficha, k)
        if v != '' and not numero(v):
            problema(r, k, 'ajuste numérico finito', v, regra='conta')
        elif v:
            problema(r, k, 'confirmar origem do ajuste de TR', v, pendente=True, regra='aprovação')
    r.nao_conferido.append(base + ': resultados de TR não exportados pela B47; escolha/ajustes conferidos separadamente')
