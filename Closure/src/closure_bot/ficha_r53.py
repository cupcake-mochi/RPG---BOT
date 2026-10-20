"""Cartões R53 da ANALISE 12 (montagem esquema 2), sem IA e sem escrever na ficha.

A R53 manteve as 8.190 chaves B47 e acrescentou os 249 cartões editáveis no
lugar: `r53.<id>.entrada` é a aplicação ativa e `r53.<id>.versao.<classe>` a
versão preparada de cada Classe, ambas como arrays JSON descritos pelos
esquemas exportados. O núcleo de contas é o da própria ficha (`r53/`, cópia de
Ficha---RPG-JJK@4b22da5), avaliado com `registro_livre=True`, a modalidade da
interface final.

O que este módulo separa:
- conta e limite mecânico recalculados pelo bot: erro reprova;
- VÁLIDO/REVISAR do cartão: estado mecânico da ficha, nunca aprovação;
- COMO É (alvos, resolução, TR, duração, permissão da Regra e detalhes das
  peças): fica com o mestre. Campos legados vazios ou padrão não reprovam e
  também não comprovam autorização;
- leitura em transição (troca de Classe ou salvamento ainda em curso): não
  aprova, não reprova e não substitui a versão preparada já salva.
"""
from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path

from .ficha_configuracao import valor, problema

# Campos de cada versão por Classe (ficha-v01/montagens_r53.CAMPOS); a leitura usa o esquema exportado.
VERSAO_CAMPOS = ['classe', 'preparada', 'forma', 'funcao1', 'pontos1', 'funcao2', 'pontos2', 'funcao3', 'pontos3',
                 'm1', 'm2', 'm3', 'm4', 'r1', 'r1_valida', 'r2', 'r2_valida', 'controle', 'pessoal', 'permite_dano',
                 'permite_cura', 'permite_vt', 'permite_alma', 'origem_permissao', 'dest_dano', 'dest_cura', 'dest_vt',
                 'res_dano', 'dependencias', 'execucao', 'fragil_pago', 'migracao', 'tr_dano', 'tr_controle']
FIXAS = {'Classe 0', 'Básica', 'Técnica Máxima', 'Máxima de entidade'}
MAXIMAS = {'Técnica Máxima', 'Máxima de entidade'}
# Mesma lista de invariantes que a ficha usa para "Ampliação altera funções ou peças".
INVARIANTES = ['forma', 'funcao1', 'funcao2', 'funcao3', 'm1', 'm2', 'm3', 'm4', 'r1', 'r2', 'controle', 'pessoal']
FUNCOES = [('dano', 'Dano'), ('cura', 'Cura'), ('vt', 'PV temporários')]
VERSAO_MINIMA = {'classe', 'preparada', 'forma', 'funcao1', 'pontos1', 'funcao2', 'pontos2', 'funcao3', 'pontos3',
                 'm1', 'r1', 'tr_dano', 'tr_controle'}
ENTRADA_MINIMA = {'id', 'nome', 'classe', 'modalidade', 'dano', 'cura', 'vt', 'p_dano', 'p_cura', 'p_vt', 'tr_dano', 'tr_controle'}
BOOL = {'preparada', 'pessoal', 'dano', 'cura', 'vt', 'permite_dano', 'permite_cura', 'permite_vt', 'permite_alma',
        'r1_valida', 'r2_valida'}
INTEIROS = {'classe', 'nivel', 'classe_maxima', 'dados_zero', 'fragil_pago', 'p_dano', 'p_cura', 'p_vt',
            'pontos1', 'pontos2', 'pontos3'}
# Chaves exportadas uma a uma ao lado do JSON: conferem que a leitura veio de uma única recalculação.
ESPELHO_TEXTO = ['modalidade', 'forma', 'controle', 'dest_dano', 'dest_cura', 'dest_vt', 'res_dano', 'tr_dano',
                 'tr_controle', 'dependencias', 'execucao', 'origem_permissao']
ESPELHO_NUMERO = ['classe', 'p_dano', 'p_cura', 'p_vt']
ESPELHO_BOOL = ['dano', 'cura', 'vt']
RESULTADOS = ['orcamento', 'base_funcoes', 'custo_forma', 'melhorias_pagas', 'devolucao', 'saldo', 'dano_d8',
              'cura_d8', 'vida_temporaria', 'sem_uso', 'pe', 'cd_normal', 'cd_controle']
# Avisos do núcleo que não são conta: dependem do cadastro aprovado ou de migração.
AVISO_CADASTRO = ('Efeito Próprio/cadastro', 'Controle próprio:', 'Forma própria com Restrição embutida')
AVISO_MIGRACAO = ('Registro antigo exige revisão',)
AVISO_TRANSICAO = ('Versão não preparada',)
TRANSITORIO = re.compile(r'^(?:#|Loading|Carregando)', re.I)
NOMES_CAMPO = {'orcamento': 'orçamento', 'base_funcoes': 'base das funções', 'custo_forma': 'custo da Forma',
               'melhorias_pagas': 'Melhorias pagas', 'devolucao': 'devolução', 'saldo': 'saldo',
               'dano_d8': 'dano (d8)', 'cura_d8': 'cura (d8)', 'vida_temporaria': 'PV temporários',
               'sem_uso': 'saldo sem uso', 'pe': 'PE', 'cd_normal': 'CD', 'cd_controle': 'CD de Controle',
               'funcao': 'resumo da função', 'avisos': 'avisos do cartão', 'entrada': 'registro ativo',
               'nivel': 'nível', 'classe_maxima': 'Classe máxima', 'classe': 'Classe'}


@lru_cache(maxsize=1)
def contextos():
    return json.loads((Path(__file__).parent / 'r53/contextos.json').read_text(encoding='utf-8'))['contextos']


@lru_cache(maxsize=1)
def _nucleo():
    from .r53 import modelo
    return modelo, modelo.arvore(True)


def rotulo(id_):
    """Nome usado no painel; segue os grupos já existentes (Feitiço 1, Invocação 2 · especial 1)."""
    m = re.fullmatch(r'(feitico|liberacao|classe0)\.(\d+)', id_)
    if m:
        return {'feitico': 'Feitiço', 'liberacao': 'Liberação', 'classe0': 'Classe 0'}[m[1]] + ' ' + m[2]
    if id_ == 'maxima.1':
        return 'Técnica Máxima'
    m = re.fullmatch(r'entidade\.(\d+)\.(bas|esp|ext)\.(\d+)', id_)
    if m:
        return f"Invocação {m[1]} · " + {'bas': 'básica', 'esp': 'especial', 'ext': 'habilidade da Trilha'}[m[2]] + ' ' + m[3]
    m = re.fullmatch(r'entidade\.(\d+)\.liberacao\.(\d+)', id_)
    if m:
        return f'Invocação {m[1]} · Liberação {m[2]}'
    m = re.fullmatch(r'entidade\.(\d+)\.maxima\.1', id_)
    if m:
        return f'Invocação {m[1]} · Técnica Máxima'
    return id_


def rotulo_chave(chave):
    """`r53.feitico.1.saldo` -> `Feitiço 1 · saldo`; None se a chave não for de cartão R53."""
    if not chave.startswith('r53.'):
        return None
    resto = chave[4:]
    for id_ in sorted(contextos(), key=len, reverse=True):
        if resto == id_:
            return rotulo(id_)
        if resto.startswith(id_ + '.'):
            campo = resto[len(id_) + 1:]
            if campo.startswith('versao.'):
                c = campo.split('.', 1)[1]
                return rotulo(id_) + ' · versão ' + ('máxima' if c == 'maxima' else 'da Classe ' + c)
            return rotulo(id_) + ' · ' + NOMES_CAMPO.get(campo, campo.replace('_', ' '))
    return None


def _texto(v):
    return '' if v is None else str(v)


def _numero(v):
    """Valor exportado como texto (`&""`): número com vírgula ou ponto; None se não for número."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    s = _texto(v).strip()
    if re.fullmatch(r'-?\d+', s):
        return int(s)
    if re.fullmatch(r'-?\d+[.,]\d+', s):
        return float(s.replace(',', '.'))
    return None


def _booleano(v):
    if isinstance(v, bool):
        return v
    s = _texto(v).strip().upper()
    return True if s in ('TRUE', 'VERDADEIRO') else False if s in ('FALSE', 'FALSO') else None


def _esquema(ficha, chave, obrigatorios, erros):
    try:
        v = json.loads(_texto(valor(ficha, chave)))
        if not isinstance(v, list) or any(not isinstance(x, str) for x in v) or len(v) != len(set(v)) or not obrigatorios <= set(v):
            raise ValueError
        return v
    except (ValueError, TypeError):
        erros.append((chave, 'esquema de campos JSON exportado pela R53', 'formato'))
        return None


def _registro(ficha, chave, campos, erros):
    bruto = _texto(valor(ficha, chave))
    if TRANSITORIO.match(bruto.strip()):
        erros.append((chave, 'registro calculado; a planilha ainda estava recalculando', 'transicao'))
        return None
    try:
        raw = json.loads(bruto)
        if not isinstance(raw, list) or len(raw) != len(campos):
            raise ValueError('quantidade de campos')
        row = dict(zip(campos, raw))
        for k, v in row.items():
            if k in BOOL and type(v) is not bool:
                raise ValueError(k + ' precisa ser booleano')
            if k in INTEIROS and (type(v) is not int or v < 0):
                raise ValueError(k + ' precisa ser inteiro não negativo')
            if k == 'cd' and (type(v) not in (int, float) or not math.isfinite(v)):
                raise ValueError('cd precisa ser número')
            if k not in BOOL | INTEIROS | {'cd'} and not isinstance(v, str):
                raise ValueError(k + ' precisa ser texto')
        return row
    except (ValueError, TypeError) as erro:
        erros.append((chave, 'array JSON tipado conforme o esquema exportado (' + str(erro) + ')', 'formato'))
        return None


def decodificar(ficha):
    """Mesmas regras de `r53/contrato.py`, mas devolve os erros classificados em vez de parar no primeiro.

    -> (aplicacoes, erros): aplicacoes[id] = {'ativa': dict|None, 'versoes': {'3': dict, 'maxima': dict}}
       erros: [(chave, esperado, 'formato'|'transicao'|'informacao')]
    """
    erros = []
    if _texto(valor(ficha, 'r53.montagem.esquema')).strip() != '2':
        return {}, [('r53.montagem.esquema', 'esquema 2 da montagem R53', 'formato')]
    campos_versao = _esquema(ficha, 'r53.versao.campos', VERSAO_MINIMA, erros)
    campos_entrada = _esquema(ficha, 'r53.entrada.campos', ENTRADA_MINIMA, erros)
    if campos_versao is None or campos_entrada is None:
        return {}, erros
    out = {}
    for chave, campo in ficha.items():
        if not chave.startswith('r53.') or _texto(campo.valor) == '':
            continue
        m = re.fullmatch(r'r53\.(.+)\.versao\.(\d|maxima)', chave)
        if m:
            r = _registro(ficha, chave, campos_versao, erros)
            if r is None:
                continue
            if not r['preparada']:
                erros.append((chave, 'versão publicada somente depois de preparada', 'formato'))
            if m[2] != 'maxima' and r['classe'] != int(m[2]):
                erros.append((chave, 'Classe da versão igual à da chave', 'formato'))
            if r['classe'] > 7:
                erros.append((chave, 'Classe de 0 a 7', 'formato'))
            out.setdefault(m[1], dict(ativa=None, versoes={}))['versoes'][m[2]] = r
        elif re.fullmatch(r'r53\..+\.entrada', chave):
            id_ = chave[4:-8]
            r = _registro(ficha, chave, campos_entrada, erros)
            if r is None:
                out.setdefault(id_, dict(ativa=None, versoes={}))['ilegivel'] = True
                continue
            if r['id'] != id_:
                erros.append((chave, 'identidade do registro igual à da chave', 'formato'))
            out.setdefault(id_, dict(ativa=None, versoes={}))['ativa'] = r
    for id_, dados in out.items():
        if id_ not in contextos():
            erros.append(('r53.' + id_ + '.entrada', 'um dos 249 cartões publicados', 'formato'))
    return out, erros


def chave_versao(ativa):
    return 'maxima' if ativa['modalidade'] in MAXIMAS else str(ativa['classe'])


def _portas(id_, ativa):
    """Funções abertas no cartão, como a interface direta calcula."""
    modo = ativa['modalidade']
    fechada = ativa.get('fam_Amparo') == 'Fechada'
    extra = '.ext.' in id_
    portas = {'dano': True,
              'cura': not (modo in ('Classe 0', 'Básica') or 'Liberação' in modo) and not fechada,
              'vt': not (modo in ('Classe 0', 'Básica') or 'Máxima' in modo) and not fechada}
    if extra and ativa['classe'] == 0:
        portas['cura'] = portas['vt'] = False
    return portas


def divergencias_versao(id_, ativa, versao):
    """Campos em que o cartão visível ainda não corresponde à versão salva da Classe ativa."""
    diferentes = [k for k in ('forma', 'm1', 'm2', 'm3', 'm4', 'r1', 'r2', 'controle', 'pessoal', 'fragil_pago')
                  if k in versao and k in ativa and ativa[k] != versao[k]]
    if not ativa.get('preparada'):
        diferentes.append('preparada')
    fixa = contextos().get(id_, {}).get('modalidade') in FIXAS
    portas = _portas(id_, ativa)
    for i, (k, nome) in enumerate(FUNCOES, 1):
        escolhida = versao.get(f'funcao{i}') == nome
        pontos = versao.get(f'pontos{i}', 0)
        if fixa:
            esperado_flag, esperado_pontos = portas[k] and escolhida, 0
        else:
            esperado_pontos = pontos if portas[k] else 0
            esperado_flag = portas[k] and (pontos > 0 or escolhida)
        if ativa.get(k) != esperado_flag or ativa.get('p_' + k) != esperado_pontos:
            diferentes.append(k)
    return diferentes


def divergencias_espelho(ficha, id_, ativa):
    """Chaves individuais exportadas do mesmo cálculo que discordam do JSON ativo."""
    base = 'r53.' + id_ + '.'
    erradas = []
    for k in ESPELHO_TEXTO:
        if base + k in ficha and _texto(valor(ficha, base + k)) != _texto(ativa.get(k)):
            erradas.append(k)
    for k in ESPELHO_NUMERO:
        if base + k in ficha and _numero(valor(ficha, base + k)) != ativa.get(k):
            erradas.append(k)
    for k in ESPELHO_BOOL:
        if base + k in ficha and _booleano(valor(ficha, base + k)) is not ativa.get(k):
            erradas.append(k)
    return erradas


def transicoes(ficha, aplicacoes=None, erros=None):
    """Cartões que ainda não fecharam o salvamento nesta leitura: {id: motivo}."""
    if aplicacoes is None:
        aplicacoes, erros = decodificar(ficha)
    saida = {}
    for chave, _, tipo in erros or []:
        m = re.fullmatch(r'r53\.(.+)\.(?:entrada|versao\.(?:\d|maxima))', chave)
        if tipo == 'transicao' and m:
            saida[m[1]] = 'a planilha ainda estava recalculando o registro'
    for id_, dados in aplicacoes.items():
        ativa = dados.get('ativa')
        if not ativa or id_ in saida or id_ not in contextos():
            continue
        versao = dados['versoes'].get(chave_versao(ativa))
        if versao is None:
            saida[id_] = 'a Classe ativa ainda não tem versão salva'
            continue
        dif = divergencias_versao(id_, ativa, versao)
        if dif:
            saida[id_] = 'o cartão visível difere da versão salva (' + ', '.join(dif) + ')'
            continue
        esp = divergencias_espelho(ficha, id_, ativa)
        if esp:
            saida[id_] = 'a exportação ainda não terminou de atualizar (' + ', '.join(esp) + ')'
    return saida


def escolher_leitura(leituras):
    """Entre leituras repetidas do mesmo link, a mais recente sem transição; senão a com menos cartões em transição.

    Nunca mistura leituras: cada cartão é avaliado com os dados da mesma recalculação.
    """
    melhor, menor = None, None
    for ficha in leituras:
        n = len(transicoes(ficha))
        if menor is None or n <= menor:
            melhor, menor = ficha, n
    return melhor


def _catalogo_proprio(ativa, modelo):
    """Peças ou Forma fora do catálogo publicado da R53 (cadastro próprio)."""
    proprias = [ativa.get(k) for k in ('m1', 'm2', 'm3', 'm4', 'r1', 'r2') if ativa.get(k) and ativa.get(k) not in modelo.OPCOES]
    if ativa.get('forma') not in modelo.FORMAS:
        proprias.append(ativa.get('forma'))
    return proprias


def _requisito_trunfo(ficha, id_):
    m = re.fullmatch(r'entidade\.(\d+)\.(liberacao\.(\d)|maxima\.1)', id_)
    if not m:
        return ''
    base = 'invocacao.' + m[1]
    tipo, nivel = valor(ficha, base + '.tipo'), valor(ficha, base + '.nivel')
    if not isinstance(nivel, int) or isinstance(nivel, bool):
        return None
    minimo = 17 if m[2].startswith('maxima') else [10, 20, 30][int(m[3]) - 1]
    return '' if tipo == 'Maldição domada' and nivel >= minimo else 'Trunfo exige maldição domada com técnica própria e nível de aquisição'


def _ampliacao(id_, versoes):
    classes = contextos()[id_]['classes']
    if len(classes) <= 1:
        return ''
    preparadas = [versoes[str(c)] for c in classes if c is not None and str(c) in versoes]
    if not preparadas:
        return ''
    primeira = preparadas[0]
    mudou = [k for k in INVARIANTES if any(v.get(k) != primeira.get(k) for v in preparadas)]
    return 'Ampliação altera funções ou peças: ' + ' · '.join(mudou) if mudou else ''


def _juntar(*partes):
    return ' · '.join(p for p in partes if p)


def _mensagens(avisos):
    """Separa o texto do cartão em avisos individuais (núcleo usa '; ', a ficha junta extras com ' · ')."""
    saida = []
    for parte in re.split(r' · (?=Ampliação altera|Trunfo exige)', _texto(avisos)):
        saida.extend(p for p in parte.split('; ') if p)
    return saida


def _classificar(mensagem):
    if mensagem.startswith(AVISO_TRANSICAO):
        return 'transicao'
    if mensagem.startswith(AVISO_MIGRACAO):
        return 'migracao'
    if mensagem.startswith(AVISO_CADASTRO):
        return 'cadastro'
    return 'mecanico'


def _contexto_personagem(ficha, id_, ativa, r):
    """O núcleo recebe nível e Classe máxima da ficha; confere contra o restante da exportação."""
    m = re.match(r'entidade\.(\d+)\.', id_)
    pares = ([('nivel', f'invocacao.{m[1]}.nivel'), ('classe_maxima', f'invocacao.{m[1]}.classe')] if m
             else [('nivel', 'nivel'), ('classe_maxima', 'classe_maxima')])
    certo = True
    for campo, chave in pares:
        esperado = valor(ficha, chave)
        if isinstance(esperado, int) and not isinstance(esperado, bool) and ativa.get(campo) != esperado:
            problema(r, f'r53.{id_}.{campo}', f'{esperado}, igual a {chave} da ficha', ativa.get(campo), pendente=True, regra='informação')
            certo = False
    return certo


def conferir_cartoes(ficha, ctx, r):
    """Confere os cartões R53 e acrescenta ao Resultado do consumidor B47."""
    modelo, livre = _nucleo()
    from .r53.formulas import evaluate
    aplicacoes, erros = decodificar(ficha)
    em_transicao = transicoes(ficha, aplicacoes, erros)
    for chave, esperado, tipo in erros:
        # JSON quebrado ou fora do esquema não é estado transitório: aparece mesmo com o cartão em espera.
        if tipo == 'transicao':
            continue
        encontrado = _texto(valor(ficha, chave))
        if len(encontrado) > 120:
            encontrado = encontrado[:119] + '…'
        problema(r, chave, esperado, encontrado or 'vazio', regra='formato')
    if any(t == 'formato' and k in ('r53.montagem.esquema', 'r53.versao.campos', 'r53.entrada.campos') for k, _, t in erros):
        r.nao_conferido.append('Cartões R53: esquema exportado ausente ou desconhecido; nenhum cartão foi certificado')
        return
    vistos = set()
    narrativos, sem_recalculo = [], []
    for id_ in contextos():
        dados = aplicacoes.get(id_)
        if not dados:
            continue
        nome = rotulo(id_)
        ativa = dados.get('ativa')
        if ativa is None:
            if dados['versoes'] and not dados.get('ilegivel'):
                # Versões guardadas de um cartão sem nome não são aplicação ativa nem dado perdido.
                r.nao_conferido.append(f'{nome}: versões preparadas guardadas sem nome no cartão; não contam como aplicação ativa')
            continue
        vistos.add(id_)
        versao = dados['versoes'].get(chave_versao(ativa))
        if id_ in em_transicao:
            ultimo = ''
            if versao:
                ultimo = f' Última versão salva da Classe {versao["classe"]}: {versao.get("forma", "")}.'
            problema(r, f'r53.{id_}.entrada', 'leitura estável: espere a ficha terminar de salvar e analise de novo; '
                     'nada foi aprovado ou reprovado neste cartão', em_transicao[id_] + '.' + ultimo,
                     pendente=True, regra='informação')
            continue
        _contexto_personagem(ficha, id_, ativa, r)
        estado_ficha = 'VÁLIDO' if _texto(valor(ficha, f'r53.{id_}.avisos')) == '' else 'REVISAR'
        proprias = _catalogo_proprio(ativa, modelo)
        if proprias:
            for p in proprias:
                registro = next((d for d in ctx.registros.values() if d.nome == p and d.tipo in ('melhoria', 'restricao', 'forma')), None)
                if registro is None:
                    problema(r, f'r53.{id_}.entrada', 'Forma, Melhoria ou Restrição do catálogo R53 ou cadastro próprio da ficha', p, regra='custom')
                elif not registro.aprovada or not registro.valida:
                    problema(r, f'r53.{id_}.entrada', f'aprovação do mestre do cadastro {p} antes do uso no cartão', p,
                             pendente=True, regra='aprovação')
            sem_recalculo.append(nome)
            avisos = _mensagens(valor(ficha, f'r53.{id_}.avisos'))
        else:
            env = {**modelo.DEFAULTS, **ativa, '_familias': {}, '_formas': {}}
            for k, expr in livre.items():
                env[k] = evaluate(expr, env, modelo.OPCOES)
            requisito = _requisito_trunfo(ficha, id_)
            amp = _ampliacao(id_, dados['versoes'])
            exportado = _texto(valor(ficha, f'r53.{id_}.avisos'))
            if requisito is None:
                r.nao_conferido.append(f'{nome}: requisito do trunfo depende do tipo e do nível da entidade')
                requisito = next((m for m in _mensagens(exportado) if m.startswith('Trunfo exige')), '')
            esperado = _juntar(env['avisos'], requisito, amp)
            for k in RESULTADOS:
                achado = _numero(valor(ficha, f'r53.{id_}.{k}'))
                if achado is None or not math.isclose(achado, env[k], abs_tol=1e-9):
                    problema(r, f'r53.{id_}.{k}', _fmt(env[k]), _texto(valor(ficha, f'r53.{id_}.{k}')) or 'vazio', regra='conta',
                             ancora='fundamento--pontos')
            if exportado != esperado:
                problema(r, f'r53.{id_}.avisos', esperado or 'sem avisos (VÁLIDO)', exportado or 'sem avisos (VÁLIDO)', regra='conta')
            if _texto(valor(ficha, f'r53.{id_}.funcao')) != _texto(env['funcao']):
                r.notas.append(_problema('conta', f'r53.{id_}.funcao', _texto(env['funcao']), _texto(valor(ficha, f'r53.{id_}.funcao'))))
            avisos = _mensagens(esperado)
            resumo = _juntar(_texto(env['funcao']), f"{_fmt(env['pe'])} PE", f"saldo {_fmt(env['saldo'])}")
            r.conferidos.append(f"{nome}: R53 Classe {ativa['classe']} · {resumo} · ficha {estado_ficha}")
        for m in avisos:
            tipo = _classificar(m)
            if tipo == 'mecanico':
                problema(r, f'r53.{id_}.avisos', 'cartão sem este aviso mecânico', m, regra='aviso', ancora='fundamento--pontos')
            elif tipo == 'migracao':
                problema(r, f'r53.{id_}.avisos', 'registro antigo revisado pelo jogador e pelo mestre antes do uso', m,
                         pendente=True, regra='aprovação')
            elif tipo == 'cadastro':
                problema(r, f'r53.{id_}.avisos', 'cadastro próprio completo e aprovado pelo mestre', m, pendente=True, regra='aprovação')
            else:
                problema(r, f'r53.{id_}.avisos', 'versão preparada da Classe ativa', m, pendente=True, regra='informação')
        pecas = {ativa.get(k) for k in ('m1', 'm2', 'm3', 'm4', 'r1', 'r2')}
        if any(str(p).startswith('Toca a Alma') for p in pecas):
            problema(r, f'r53.{id_}.entrada', 'Regra que trata diretamente da alma, confirmada pelo mestre em COMO É',
                     'Toca a Alma', pendente=True, regra='aprovação', ancora='dano--alma')
        if any(str(p).startswith('Frágil') for p in pecas):
            r.notas.append(_problema('conta', f'r53.{id_}.entrada', 'Melhorias interrompíveis que somam o gasto de Frágil',
                                     f"Frágil {ativa.get('fragil_pago')}"))
        narrativos.append(nome)
    if narrativos:
        r.nao_conferido.append(' · '.join(narrativos) + ': COMO É (alvos, resolução, TR, duração, autorização da Regra '
                               'e detalhes das Melhorias/Restrições) fica com o mestre; campos padrão não reprovam nem autorizam')
    if sem_recalculo:
        r.nao_conferido.append(' · '.join(sem_recalculo) + ': usa cadastro próprio; contas mostradas pela ficha, sem recálculo do bot')
    if any(rotulo(i).startswith('Invocação') for i in vistos):
        r.nao_conferido.append('Cartões de invocação: CD e estados de Família vêm da ficha; o bot confere as Famílias da entidade à parte')
    if vistos:
        r.nao_conferido.append('Cartões R53: VÁLIDO/REVISAR é o estado mecânico da ficha, não aprovação do mestre nem do bot')


def _fmt(v):
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def _problema(regra, campo, esperado, encontrado, ancora=''):
    from .ficha_corretor import Problema
    return Problema(regra, campo, esperado, str(encontrado), ancora)
