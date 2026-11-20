"""Cadastros crus B47, aprovação exata e extensão conservadora dos catálogos.

Herança só usa bases publicadas, nunca os resultados ou os avisos do jogador.
"""
import copy
import json
import re
from dataclasses import dataclass, field, replace
from decimal import Decimal
from pathlib import Path

from .ficha_configuracao import valor, numero, inteiro, problema, impressao_exata

CAPACIDADES = {'familia':10,'melhoria':30,'restricao':30,'pericia':10,'oficio':10,'dano':10,
               'forma':10,'aptidao':10,'talento':10,'tipo_entidade':10,'talento_entidade':20}


@dataclass
class Definicao:
    chave: str
    tipo: str
    nome: str
    campos: dict
    efetivos: dict = field(default_factory=dict)
    valida: bool = True
    aprovada: bool = False
    impressao: str = ''


def definicoes(ficha):
    grupos = {}
    for chave, campo in ficha.items():
        m = re.fullmatch(r'(custom\.(?:\d+|caminho|trilha|[a-z_]+\.\d+))\.(.+)', chave)
        if m:
            grupos.setdefault(m[1], {})[m[2]] = campo.valor
    saida = []
    for raiz, campos in sorted(grupos.items()):
        partes = raiz.split('.')
        tipo = str(campos.get('tipo','')) if partes[1].isdigit() else partes[1]
        nome = campos.get('nome','')
        usados = {k:v for k,v in campos.items() if k not in ('mestre_viu','tipo','nome') and v not in ('',None)}
        # Defaults de cartões não são cadastros de personagem.
        defaults = {'base':'Nenhuma','modalidade':'Melhoria','estado':'Neutra','tipo':''}
        # Cartões vazios da B47 nativa já vêm com estes menus selecionados.
        # O default só deixa de ativar o cartão; permanece nos campos e no
        # hash quando houver nome, conteúdo ou MESTRE VIU preenchido.
        if tipo == 'caminho':
            defaults.update({'campo.troca_pericias_por_arma':'Não', 'campo.treino_de_arma':'Todas'})
        elif tipo == 'trilha':
            defaults['campo.base_do_livro'] = 'Nenhuma'
        relevantes = {k:v for k,v in usados.items() if defaults.get(k) != v
                      and not (k == 'controle_compat' and str(v).upper() in ('0','FALSE','FALSO'))}
        if nome or relevantes or campos.get('mestre_viu',0) not in ('',0):
            saida.append(Definicao(raiz,tipo,nome,campos))
    return saida


def catalogos_r53():
    """Peças publicadas da R53 pelo rótulo que a ficha usa como BASE; pesos no vocabulário do cadastro."""
    from .r53.modelo import CAT
    pesos = {1: 'Leve', 2: 'Média', 3: 'Pesada'}
    melhorias, restricoes = {}, {}
    for o in CAT['opcoes']:
        if o['tipo'] == 'melhorias':
            melhorias[o['rotulo']] = {'peso': pesos[o['peso']], 'familia': o['familia'], 'repeticoes': o['repeticoes'],
                                      'minima': o['classe_minima'], 'identidade': o['rotulo_base']}
        else:
            restricoes[o['rotulo']] = {'devolucao': pesos[o['peso']], 'identidade': o['rotulo_base'],
                                       'frequencia': 'Sim' if o['frequencia'] else 'Não'}
    return melhorias, restricoes


def catalogos(ref, r53=False):
    livro = json.loads((Path(__file__).parent/'recursos/b47-livro.json').read_text(encoding='utf-8'))
    m = ref.magia
    tabelas = {
        'familia': {n:{} for n in m.familias},
        'melhoria': {n:{'peso':p.peso,'familia':p.familia,'repeticoes':p.repeticoes,'minima':p.minima,'identidade':n} for n,p in m.melhorias.items()},
        'restricao': {n:{'devolucao':p,'identidade':re.sub(r' \((Leve|Média)\)$','',n),
                         'frequencia':'Sim' if re.sub(r' \((Leve|Média)\)$','',n) in ('Uma Vez','Condicional','Aquecer','Dívida') else 'Não'} for n,(p,_) in m.restricoes.items()},
        'forma': {n:{'peso':p,'identidade':n, **livro['formas'].get(n,{})} for n,p in m.formas.items()},
        'talento': {n:{'categoria':p,'identidade':n} for n,(p,_) in m.repertorio.talentos.items()},
        'aptidao': {a['nome']:{**a,'identidade':a['nome']} for a in livro['aptidoes']},
        'tipo_entidade': {n:{'vida':'Corpo de criação' if n=='Corpo amaldiçoado de criação' else 'Normal da entidade',
                              'talisma':'Usa' if n=='Shikigami de criação' else 'Não usa',
                              'reserva_pe':'Maldição domada' if n=='Maldição domada' else 'Normal da entidade',
                              'identidade':n} for n in m.tipos},
        'talento_entidade': {n:{'categoria':p,'identidade':n} for n,p in m.talentos_entidade.items()},
        'pericia': {n:dict(v) for n,v in livro['pericias'].items()},
        'oficio': {n:({'atributo':v} if isinstance(v,str) else dict(v)) for n,v in livro['oficios'].items()},
        'caminho': {n:dict(v) for n,v in livro['caminhos'].items()},
        'trilha': {n:{'caminho':c} for c, v in ref.caminhos.items() for n in v['trilhas']},
        'Origem': {o['menu']:dict(o) for o in livro['origens']},
        'Marcante': {c['nome']:dict(c) for o in livro['origens'] for c in o['marcantes']},
        'Menor': {c['nome']:dict(c) for o in livro['origens'] for c in o.get('menores',[])},
    }
    if r53:
        tabelas['melhoria'], tabelas['restricao'] = catalogos_r53()
    for tipo in ('Arma','Escudo','Uniforme','Ferramenta amaldiçoada','Item comum'):
        tabelas[tipo] = {n:{'equipamento':p} for n,p in ref.equipamento.pecas.items()} if tipo!='Item comum' else {n:{'volume':float(p)} for n,p in ref.equipamento.itens.items()}
    tabelas['Ferramenta amaldiçoada'].update(tabelas['Item comum'])
    person = json.loads((Path(__file__).parent/'recursos/b47-personagem-livro.json').read_text(encoding='utf-8'))
    for grupo in ('forma','aptidao','talento'):
        tabelas[grupo]={x['nome']:dict(x) for x in person[grupo]}
    return tabelas


def preparar_custom(ficha, ref, ctx, r):
    tabelas = catalogos(ref, ctx.r53)
    registros = definicoes(ficha)
    molde_3a=json.loads((Path(__file__).parent/'recursos/b47-3a.json').read_text(encoding='utf-8'))
    from .ficha_personagem_motor import compilar
    livro_personagem = json.loads((Path(__file__).parent/'recursos/b47-personagem-livro.json').read_text(encoding='utf-8'))
    livro_personagem['nivel_ce']={int(k):v for k,v in livro_personagem['nivel_ce'].items()}
    crus = {}
    for grupo in ('forma','aptidao','talento'):
        crus[grupo] = []
        for i in range(1,11):
            raw = {k.rsplit('.',1)[1]:c.valor for k,c in ficha.items() if k.startswith(f'custom.{grupo}.{i}.')}
            raw={('ce' if k=='categoria' else 'classe_0' if k=='classe_zero' else k):v for k,v in raw.items()}
            for k in ('mestre_viu','exige_tr','classe_0'):
                if raw.get(k) in ('Sim','Não'):
                    raw[k]=raw[k]=='Sim'
                elif k=='mestre_viu' and raw.get(k) in (0,1):
                    raw[k]=bool(raw[k])
            crus[grupo].append(raw)
    ctx.catalogo_personagem = compilar(livro_personagem,crus,{'forma':10,'aptidao':10,'talento':10},
        familias=[d.nome for d in registros if d.tipo=='familia'])
    nomes = {}
    for d in registros:
        nomes.setdefault((d.tipo,str(d.nome).casefold()),[]).append(d)
    referencias = copy.deepcopy(ref)
    # dataclasses congeladas contêm catálogos próprios; não se modifica o catálogo global.
    m = referencias.magia
    motor_atualizado=False
    for d in sorted(registros,key=lambda d:d.tipo in ('forma','aptidao','talento')):
        if d.tipo in ('forma','aptidao','talento') and not motor_atualizado:
            # O contrato permite Restrição custom embutida. Validar o cadastro
            # antes de compilar Formas; aprovação é exigida separadamente no uso.
            restricoes={x.nome:{'nome':x.efetivos.get('identidade',x.nome),
                               'devolve':1 if x.efetivos['devolucao']=='Leve' else 2,
                               'frequencia':int(x.efetivos.get('frequencia')=='Sim')}
                        for x in ctx.registros.values() if x.tipo=='restricao' and x.valida}
            ctx.catalogo_personagem=compilar(livro_personagem,crus,{'forma':10,'aptidao':10,'talento':10},
                familias=[x.nome for x in registros if x.tipo=='familia'],restricoes=restricoes)
            motor_atualizado=True
        def falha(campo, texto):
            d.valida = False
            problema(r,d.chave+'.'+campo,texto,d.campos.get(campo,''),regra='custom')
        if not isinstance(d.nome,str) or not d.nome.strip():
            falha('nome','preencha o nome do cadastro')
        else:
            if d.nome.strip()!=d.nome:
                posicao = 'no início e no fim' if d.nome.lstrip()!=d.nome and d.nome.rstrip()!=d.nome else 'no início' if d.nome.lstrip()!=d.nome else 'no fim'
                falha('nome',f'remova os espaços em branco {posicao} do nome; mantenha o mesmo nome nas escolhas que usam este cadastro')
            if ' · ' in d.nome:
                falha('nome','retire o separador de lista ( · ) do nome do cadastro')
        p = d.chave.split('.')
        if p[1].isdigit():
            if not inteiro(int(p[1]),1,25) or d.tipo not in ('Origem','Marcante','Menor','Arma','Escudo','Uniforme','Item comum','Ferramenta amaldiçoada'):
                falha('tipo','um dos oito tipos 3a e índice de 1 a 25')
        elif p[1] not in ('caminho','trilha') and (p[1] not in CAPACIDADES or not inteiro(int(p[2]),1,CAPACIDADES.get(p[1],0))):
            falha('nome','índice dentro da capacidade B47 atual')
        if len(nomes[d.tipo,str(d.nome).casefold()])>1 or any(str(n).casefold()==str(d.nome).casefold() for n in tabelas.get(d.tipo,{})):
            falha('nome','nome sem colisão com livro ou outro cadastro; comparação literal')
        if d.campos.get('mestre_viu','') not in (0,1) or isinstance(d.campos.get('mestre_viu'),bool):
            falha('mestre_viu','caixa 0/1; lembrete não autoriza conteúdo')
        if p[1].isdigit() and d.tipo in molde_3a['campos']:
            from .ficha_testes import chave as slug
            campos={slug(n) for grupo in molde_3a['campos'][d.tipo] for n in grupo}
            requeridos={'Origem':['pericia_1','pericia_2','pericia_3','pericia_4','rota'],
                'Marcante':['origem'],'Menor':['origem'],'Arma':['categoria','mao','tipo_de_dano','dado','forca','volume'],
                'Escudo':['protecao','teto_de_destreza','forca','volume'],
                'Uniforme':['grau_minimo','protecao','teto_de_destreza','forca','volume'],
                'Item comum':['volume'],'Ferramenta amaldiçoada':['base','grau']}[d.tipo]
            for k in requeridos:
                if d.campos.get('campo.'+k,'')=='':falha('campo.'+k,'campo obrigatório de '+d.tipo)
            for k,v in d.campos.items():
                if k.startswith('campo.') and v!='' and k[6:] not in campos:
                    falha(k,'campo não utilizado neste tipo deve ficar vazio')
                if k.startswith('campo.') and k[6:] in {'forca','volume','preco','protecao','teto_de_destreza','desgaste','recarga'} and v!='':
                    admite_traco=k[6:] in {'forca','teto_de_destreza','desgaste','recarga'}
                    if not numero(v) and not (admite_traco and v=='—'):
                        # Teto é enumeração híbrida: o texto numérico tem semântica numérica.
                        if not (k.endswith('teto_de_destreza') and str(v).isdecimal()):falha(k,'número finito ou traço nos campos permitidos')
            pool_campo={'categoria':'categorias','mao':'maos','tipo_de_dano':'danos','rota':'rotas','oficio':'oficios',
                        'grau':'graus','grau_minimo':'graus',**{f'pericia_{i}':'pericias' for i in range(1,5)},
                        **{f'propriedade_{i}':'propriedades' for i in range(1,5)}}
            for k,pool in pool_campo.items():
                v=d.campos.get('campo.'+k,'')
                tipo_extra={'pericias':'pericia','oficios':'oficio','danos':'dano'}.get(pool)
                extras=[x.nome for x in registros if tipo_extra and x.tipo==tipo_extra]
                if v!='' and str(v) not in {str(x) for x in molde_3a['listas'][pool]+extras}:
                    falha('campo.'+k,'opção literal válida no catálogo')
            if d.tipo=='Origem':
                pericias=[d.campos.get(f'campo.pericia_{i}','') for i in range(1,5)]
                if len(set(pericias))!=4:falha('campo.pericia_1','quatro perícias diferentes')
                base_origem=d.campos.get('campo.base_do_livro','')
                if base_origem not in ('','Nenhuma'):
                    publicadas=list(tabelas['Origem'])
                    rotas=('Fundamento','Manejos') if base_origem in publicadas[:5] else (
                        'Técnica Marcial sem energia',) if 'Sem Energia' in base_origem else (
                        'Técnica Marcial com energia',) if base_origem=='Corpo Amaldiçoado' else ('Fundamento',)
                    if d.campos.get('campo.rota') not in rotas:
                        falha('campo.rota','ROTA compatível com o pacote herdado da BASE DO LIVRO')
            if sum(x.chave.split('.')[1].isdigit() and str(x.nome).casefold()==str(d.nome).casefold() for x in registros)>1:
                falha('nome','nome único entre os 25 cadastros compartilhados 3a')
        campo_base = 'campo.base' if d.tipo=='Ferramenta amaldiçoada' else 'campo.base_do_livro' if d.tipo in ('Origem','trilha') else 'base'
        base = d.campos.get(campo_base,'')
        tem_base = base not in ('','Nenhuma')
        heranca = tabelas.get(d.tipo,{}).get(base)
        if tem_base and heranca is None and d.tipo=='Ferramenta amaldiçoada':
            candidato=next((x for x in registros if x.nome==base and x.tipo in ('Arma','Escudo','Uniforme','Item comum')),None)
            if candidato:
                heranca={'base_custom':{k:v for k,v in candidato.campos.items() if k!='mestre_viu'}}
        if tem_base and heranca is None:
            falha('base','base publicada válida do mesmo catálogo; herança custom encadeada não admitida')
        d.efetivos = copy.deepcopy(heranca or {})
        # Vazio herda; zero e Não sobrescrevem. Não se resolve prosa em números.
        d.efetivos.update({k:v for k,v in d.campos.items() if k not in ('nome','mestre_viu') and v!=''})
        if d.tipo in ('pericia','oficio') and any(str(n).casefold()==str(d.nome).casefold() for g in ('pericia','oficio') for n in tabelas[g]):
            falha('nome','nome sem colisão com Perícias ou Ofícios do livro')
        if d.tipo in ('pericia','oficio') and sum(x.tipo in ('pericia','oficio') and str(x.nome).casefold()==str(d.nome).casefold() for x in registros)>1:
            falha('nome','nome único entre Perícias e Ofícios custom')
        if d.tipo=='familia' and d.campos.get('estado') not in ('Livre','Neutra','Fechada'):
            falha('estado','Livre, Neutra ou Fechada')
        if d.tipo in ('pericia','oficio'):
            from .ficha_testes import ATRIBUTOS
            if d.campos.get('tipo') != ('Perícia' if d.tipo=='pericia' else 'Ofício'):
                falha('tipo','tipo fixo do catálogo')
            if d.campos.get('atributo') not in ATRIBUTOS.values():
                falha('atributo','um dos cinco atributos')
        if d.tipo in ('melhoria','restricao'):
            peso = 'devolucao' if d.tipo=='restricao' else 'peso'
            if d.efetivos.get(peso) not in (('Leve','Média') if d.tipo=='restricao' else ('0','Leve','Média','Pesada') if d.tipo=='forma' else ('Leve','Média','Pesada')):
                falha(peso,'peso válido ou base que o forneça')
            for k in ('exige_tr','frequencia','classe_zero'):
                if k in d.efetivos and d.efetivos[k] not in ('','Sim','Não'):
                    falha(k,'Sim ou Não; vazio herda')
            if d.tipo=='melhoria' and d.campos.get('modalidade','Melhoria') not in ('','Melhoria','Condição'):
                falha('modalidade','Melhoria ou Condição')
            if d.tipo=='melhoria' and d.campos.get('modalidade')=='Condição':
                if ctx.r53:
                    # R53 nomeia cada Condição como rótulo próprio do catálogo ("Condição · Cego").
                    if tem_base and not str(base).startswith('Condição · '):
                        falha('base','Condição publicada como base')
                elif tem_base and not str(base).startswith('Condição: '):
                    # O catálogo também possui aliases sem prefixo: reconhecidos pelo mesmo objeto do livro.
                    if base not in m.melhorias or 'Condição: '+base not in m.melhorias:
                        falha('base','Condição publicada como base')
                if not d.campos.get('familia') and not tem_base:
                    d.efetivos['familia']='Controle'
                if d.campos.get('exige_tr')=='Não':
                    falha('exige_tr','Condição exige TR')
                d.efetivos['exige_tr']='Sim'
        if d.tipo == 'talento_entidade' and not inteiro(d.efetivos.get('categoria'),1,3):
            falha('categoria','Categoria 1, 2 ou 3, explícita ou herdada')
        if d.tipo=='tipo_entidade':
            for campo, opcoes, padrao in [('vida',('Normal da entidade','Corpo de criação'),'Normal da entidade'),
                                           ('talisma',('Não usa','Usa'),'Não usa'),
                                           ('reserva_pe',('Normal da entidade','Maldição domada'),'Normal da entidade')]:
                d.efetivos.setdefault(campo,padrao)
                if d.efetivos[campo] not in opcoes:
                    falha(campo,' / '.join(opcoes))
        if d.tipo in ('forma','aptidao','talento'):
            n=int(d.chave.rsplit('.',1)[1])
            for msg in ctx.catalogo_personagem.avisos[d.tipo][n-1]:
                falha('nome',msg)
            efetivo=ctx.catalogo_personagem.obter(d.tipo,d.nome)
            if efetivo:
                d.efetivos=efetivo
        # controle_compat chegou na R53; desmarcado, não muda a identidade de um cadastro já aprovado.
        proprios={k:v for k,v in d.campos.items() if k not in ('mestre_viu','nome') and not (k=='controle_compat' and str(v).upper() in ('','0','FALSE','FALSO'))}
        assinatura={'crus':proprios,'base':_serializavel(heranca or {})}
        if d.tipo=='forma':
            emb=d.efetivos.get('restricao_embutida')
            dependencia=next((x for x in ctx.registros.values() if x.tipo=='restricao' and x.nome==emb),None)
            if dependencia:
                assinatura['dependencias']={'restricao_embutida':dependencia.impressao}
        d.impressao=impressao_exata(d.tipo,d.nome,assinatura)
        d.aprovada = bool(ctx.aprovados and d.impressao in ctx.aprovados.impressoes)
        ctx.registros[d.chave]=d
        if not d.aprovada:
            problema(r,d.chave+'.nome','aprovação do mestre para esta definição exata; MESTRE VIU não é autorização',d.nome,pendente=True,regra='aprovação')
        if d.valida and d.tipo == "familia":
            ctx.familias[d.nome] = d.campos["estado"]
        if not d.valida or not d.aprovada:
            continue
        if d.tipo=='familia':
            ctx.familias[d.nome]=d.campos['estado']
        elif d.tipo=='melhoria':
            from .ficha_magia import Melhoria
            base_peca=m.melhorias.get(base)
            familia=d.efetivos.get('familia','')
            familia='' if familia=='Nenhuma' else familia
            if familia and familia not in m.familias and familia not in [x.nome for x in registros if x.tipo=='familia' and x.valida and x.aprovada]:
                falha('familia','Família do livro ou custom aprovada')
                continue
            m.melhorias[d.nome]=Melhoria(d.efetivos['peso'],familia,'',base_peca.repeticoes if base_peca else 1,base_peca.minima if base_peca else 0)
        elif d.tipo=='restricao':
            m.restricoes[d.nome]=d.efetivos['devolucao'],''
        elif d.tipo=='talento':
            m.repertorio.talentos[d.nome]=(d.efetivos['ce'],'')
        elif d.tipo=='talento_entidade':
            m.talentos_entidade[d.nome]=d.efetivos['categoria']
        elif d.tipo=='forma':
            m.formas[d.nome]=('0','Leve','Média','Pesada')[d.efetivos['peso']]
        if d.tipo in ('melhoria','restricao','forma') and tem_base:
            ctx.aliases[d.tipo+':'+d.nome]=base
    for d in registros:
        if d.tipo not in ('Marcante','Menor'):continue
        parent=d.campos.get('campo.origem','')
        origem=next((o for o in registros if o.tipo=='Origem' and o.nome==parent and o.valida),None)
        livro_parent=tabelas['Origem'].get(parent)
        if livro_parent is None and origem is None:
            d.valida=False
            problema(r,d.chave+'.campo.origem','Origem publicada ou cadastro válido',parent,regra='custom')
            continue
        base=origem.campos.get('campo.base_do_livro','') if origem else parent
        if d.tipo=='Marcante' and base not in ('','Nenhuma','Restrição Celestial · Restrição corporal'):
            d.valida=False
            problema(r,d.chave+'.campo.origem','marcante própria somente para Restrição corporal ou Origem do zero; respeitar R52',base,regra='custom',ancora='origens--origens')
    return ampliar_referencias(referencias,ctx,r)


def ampliar_referencias(ref,ctx,r):
    """Campos estruturados aprovados estendem contas existentes; prosa continua manual."""
    from .ficha_corretor import Peca
    from .ficha_equipamento import Equipamento
    caminhos=copy.deepcopy(ref.caminhos)
    origens=list(ref.origens)
    tipos=list(ref.magia.tipos)
    duas_maos=set(ref.duas_maos)
    for d in sorted(ctx.registros.values(),key=lambda d:d.tipo=='Ferramenta amaldiçoada'):
        if not d.valida or not d.aprovada:
            continue
        c=d.campos
        if d.tipo=='caminho':
            campos=('vida_inicial','vida_por_nivel','pe_por_nivel')
            ns=[c.get('campo.'+k,'') for k in campos]
            if not all(inteiro(v) for v in ns):
                problema(r,d.chave,'Vida/PE inteiros não negativos no Caminho',ns,regra='custom')
                continue
            dado=c.get('campo.dado_de_vida','')
            m=re.fullmatch(r'd(4|6|8|10|12|20)',str(dado))
            if not m:
                problema(r,d.chave+'.campo.dado_de_vida','d4/d6/d8/d10/d12/d20',dado,regra='custom')
                continue
            caminhos[d.nome]={'vida1':ns[0],'vidaNv':ns[1],'peNv':ns[2],'dadoVida':int(m[1]),'trilhas':[]}
        elif d.tipo=='Origem':
            origens.append(d.nome)
            r.nao_conferido.append(d.chave+': rota, concessões e exceções da Origem custom exigem conferir a base e capacidades; descrição não concede números')
        elif d.tipo=='tipo_entidade':
            tipos.append(d.nome)
        elif d.tipo in ('Arma','Escudo','Uniforme','Ferramenta amaldiçoada','Item comum'):
            def campo(k):return c.get('campo.'+k,'')
            base=campo('base')
            p=ref.equipamento.pecas.get(base)
            if d.tipo=='Ferramenta amaldiçoada':
                # A base pode ser um registro básico aprovado, nunca outra ferramenta.
                p=ref.equipamento.pecas.get(base)
                v=campo('volume')
                if v!='' and (not numero(v) or v<0):
                    d.valida=False
                    problema(r,d.chave+'.campo.volume','Volume numérico não negativo ou vazio para herdar',v,regra='custom')
                    continue
                item=ref.equipamento.itens.get(base)
                if p is None and item is None:
                    r.nao_conferido.append(d.chave+': base de ferramenta sem mecânica numérica comprovada')
                    continue
                if p is None:
                    ref.equipamento.itens[d.nome]=Decimal(str(v)) if v!='' else item
                else:
                    ref.equipamento.pecas[d.nome]=replace(p,volume=Decimal(str(v))) if v!='' else p
                    if p.maos==2:duas_maos.add(d.nome)
                    for tabela in (ref.escudos,ref.uniformes):
                        if base in tabela:tabela[d.nome]=tabela[base]
                r.nao_conferido.append(d.chave+': grau, estigma, desgaste e efeitos livres da ferramenta exigem conferência do mestre')
                continue
            volume,forca=campo('volume'),campo('forca')
            if forca=='—':forca=0
            if not numero(volume) or volume<0 or d.tipo!='Item comum' and (not inteiro(forca)):
                problema(r,d.chave,'Volume numérico não negativo e Força inteira quando aplicável',(volume,forca),regra='custom')
                continue
            if d.tipo=='Item comum':
                ref.equipamento.itens[d.nome]=Decimal(str(volume));continue
            maos=campo('mao')
            if d.tipo=='Arma' and str(maos) not in ('1','2'):
                problema(r,d.chave+'.campo.mao','1 ou 2',maos,regra='custom');continue
            props={campo('propriedade_'+str(i)) for i in range(1,5)}
            tipo='arma' if d.tipo=='Arma' else 'escudo' if d.tipo=='Escudo' else 'uniforme'
            disparo=campo('categoria') in ('Yumi','Balestra','Arma de Fogo')
            ref.equipamento.pecas[d.nome]=Equipamento(forca,Decimal(str(volume)),int(maos) if d.tipo=='Arma' else int(d.tipo=='Escudo'),
                'Fineza' in props,disparo,campo('categoria')=='Arma de Fogo','Longo Alcance' in props and not disparo,tipo)
            if d.tipo=='Arma' and int(maos)==2:duas_maos.add(d.nome)
            if d.tipo in ('Escudo','Uniforme'):
                protecao,teto=campo('protecao'),campo('teto_de_destreza')
                if isinstance(teto,str) and teto.isdecimal():teto=int(teto)
                if not numero(protecao) or teto not in ('','Sem teto','—') and not numero(teto):
                    problema(r,d.chave,'Proteção numérica e teto numérico ou Sem teto',(protecao,teto),regra='custom');continue
                (ref.escudos if d.tipo=='Escudo' else ref.uniformes)[d.nome]=Peca(protecao,teto if numero(teto) else None)
            if d.tipo=='Arma':
                r.nao_conferido.append(d.chave+': categoria, propriedades condicionais e treino da arma custom requerem revisão')
        if any(c.get(k) for k in ('efeito','requisitos','campo.talento_ce_4')):
            r.nao_conferido.append(d.chave+': texto/requisitos e concessões livres não viram benefícios numéricos automaticamente')
    for d in ctx.registros.values():
        if d.tipo=='trilha' and d.valida and d.aprovada:
            caminho=d.campos.get('campo.caminho','')
            if caminho not in caminhos:
                problema(r,d.chave+'.campo.caminho','Caminho do livro ou custom aprovado',caminho,regra='custom')
            else:
                caminhos[caminho]['trilhas']=list(caminhos[caminho]['trilhas'])+[d.nome]
            r.nao_conferido.append(d.chave+': habilidades textuais da Trilha e concessões exclusivas exigem conferência manual')
    return replace(ref,caminhos=caminhos,origens=tuple(origens),duas_maos=frozenset(duas_maos),magia=replace(ref.magia,tipos=tuple(tipos)))


def _serializavel(obj):
    if hasattr(obj,'__dataclass_fields__'):
        from dataclasses import asdict
        return _serializavel(asdict(obj))
    if isinstance(obj,dict):
        return {k:_serializavel(v) for k,v in obj.items()}
    if isinstance(obj,(tuple,list)):
        return [_serializavel(v) for v in obj]
    return str(obj) if isinstance(obj,Decimal) else obj
