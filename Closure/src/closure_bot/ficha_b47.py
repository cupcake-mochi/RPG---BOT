"""Integração determinística do contrato 11; mantém o consumidor legado isolado."""
import math
import re
from dataclasses import replace

from .ficha_leitor import Campo
from .ficha_esquema import campos_b47
from .ficha_configuracao import (ContextoB47, conferir_regras, conferir_efeitos, valor,
                                numero, inteiro, problema)


def conferir_b47(ficha, ref, campanha, aprovados):
    from .ficha_corretor import Resultado, _conferir_legado
    from .ficha_custom import preparar_custom
    r = Resultado('aprovada')
    esquema = campos_b47()
    faltantes = set(esquema)-set(ficha)
    if faltantes:
        # Identidade por chave; nem ordem, quantidade de linhas ou coordenada física são validadas.
        por_grupo = {}
        for k in sorted(faltantes):
            por_grupo.setdefault(k.split('.')[0],[]).append(k)
        for grupo, chaves in por_grupo.items():
            problema(r,chaves[0],f'exportação completa; faltam {len(chaves)} chave(s) de {grupo}',
                     ', '.join(chaves[:4]),pendente=True,regra='informação')
        r.nao_conferido.append('Exportação incompleta: campos ausentes não equivalem a vazio, zero ou falso')
        # Não executar contas antigas que assumem zero diante de campos ausentes.
        r.veredito='pendente'
        return r
    for k, campo in ficha.items():
        if k not in esquema:
            r.nao_conferido.append(f'{k}: chave adicional de variante não reconhecida; significado não certificado')
        elif campo.parte != esquema[k]['parte']:
            problema(r,k,'parte '+esquema[k]['parte'],campo.parte,regra='formato')
        if str(campo.valor).strip().upper() in {'#REF!','#N/A','#NAME?','#VALUE!','#DIV/0!','#NUM!','#ERROR!','#SPILL!','#CALC!'}:
            problema(r,k,'resultado calculado sem erro de fórmula',campo.valor,regra='formato')
    if valor(ficha,'ficha.sistema')!='Ciclo Maldito':
        problema(r,'ficha.sistema','Ciclo Maldito',valor(ficha,'ficha.sistema'),regra='formato')
    invalidos = []
    for k,c in ficha.items():
        if re.fullmatch(r'atributo\.[^.]+\.(?:base|corpo)|marco\.(?:corpo|leque|refino)|invocacao\.\d+\.atributo\.[^.]+\.(?:base|buff)', k):
            if c.valor != '' and not numero(c.valor):
                problema(r,k,'entrada numérica finita',c.valor,regra='formato');invalidos.append(k)
            elif c.valor != '' and not k.endswith('.buff') and not inteiro(c.valor):
                problema(r,k,'pontos/escolhas inteiros não negativos',c.valor,regra='formato');invalidos.append(k)
    if invalidos or r.problemas:
        r.nao_conferido.append('Formato/entradas inválidos: contas dependentes não executadas')
        r.veredito='reprovada'
        return r
    ctx=ContextoB47(aprovados=aprovados)
    ctx.regras=conferir_regras(ficha,campanha,r)
    ref=preparar_custom(ficha,ref,ctx,r)
    ref=replace(ref,magia=replace(ref.magia,contexto=ctx))
    conferir_efeitos(ficha,ctx,r)
    if not conferir_origem(ficha,ctx,r):
        r.nao_conferido.append('Origem: escolhas incompatíveis impedem certificar as contas dependentes')
        r.veredito='reprovada'
        return r
    identidades = _identidades_validas(ficha,r)
    mecanica = ficha
    origem_custom=next((d for d in ctx.registros.values() if d.tipo=='Origem' and d.nome==valor(ficha,'origem') and d.valida and d.aprovada),None)
    if origem_custom:
        origem_base=origem_custom.campos.get('campo.base_do_livro','')
        if origem_base not in ('','Nenhuma'):
            # Visão interna para os cálculos existentes. Hashes e diagnósticos
            # continuam ligados ao cadastro literal, sem alterar a exportação.
            mecanica=dict(ficha)
            if origem_custom.campos.get('campo.rota')=='Manejos':
                origem_base+=' · Sem Técnica'
            c=ficha['origem']
            mecanica['origem']=Campo(origem_base,c.celula,c.parte)
    # A campanha vem do bot; uma regra adulterada na ficha nunca dirige o cálculo.
    antigo=_conferir_legado(mecanica,ref,campanha)
    if mecanica is not ficha:
        antigo.conferidos=[f'Origem {origem_custom.nome} (base {origem_base})' if c.startswith('Origem ') else c for c in antigo.conferidos]
    for d in ctx.registros.values():
        campo={'caminho':'caminho','trilha':'trilha','Origem':'origem'}.get(d.tipo)
        if campo and d.valida and not d.aprovada and valor(ficha,campo)==d.nome:
            antigo.problemas=[p for p in antigo.problemas if not (p.regra=='nome' and p.campo==campo)]
    for atributo in ('problemas','pendencias','notas','nao_conferido','conferidos'):
        getattr(r,atributo).extend(getattr(antigo,atributo))
    conferir_familias(ficha,ref.magia,'tecnica',r.problemas,r)
    for i in range(1,13):
        base=f'invocacao.{i}'
        if valor(ficha,base+'.nome') and base not in ctx.entidades_invalidas:
            conferir_familias(ficha,ref.magia,base,r.problemas,r)
            conferir_competencias_entidade(ficha,ref,ctx,r,base)
    conferir_progressao(ficha,ref,ctx,r)
    from .ficha_derivados_b47 import conferir_derivados
    conferir_derivados(ficha,ref,ctx,r)
    r.nao_conferido.append('Carga: B47 não exporta quantidades/Volumes e ajustes da variante TR-v4; inventário agregado não certifica carga integral')
    conferir_treinos(mecanica,ref,ctx,r)
    conferir_aptidoes(mecanica,ref,ctx,r)
    for d in ctx.registros.values():
        if d.nome in identidades and (not d.aprovada or not d.valida):
            r.conferidos=[c for c in r.conferidos if d.nome not in c]
    r.nao_conferido=list(dict.fromkeys(r.nao_conferido))
    r.veredito='reprovada' if r.problemas else 'pendente' if r.pendencias or r.nao_conferido or r.notas else 'aprovada'
    return r


def _identidades_validas(ficha,r):
    escolhas = {valor(ficha,k) for k in ('caminho','trilha','origem')}
    if not inteiro(valor(ficha,'nivel'),1,30):
        problema(r,'nivel','nível inteiro de 1 a 30',valor(ficha,'nivel'),pendente=True,regra='informação')
    if not str(valor(ficha,'nome')).strip():
        problema(r,'nome','identificar o personagem; ficha branca não aprova personagem','vazio',pendente=True,regra='informação')
    return escolhas


def conferir_origem(ficha,ctx,r):
    import json
    from pathlib import Path
    origens=json.loads((Path(__file__).parent/'recursos/b47-livro.json').read_text(encoding='utf-8'))['origens']
    nome=valor(ficha,'origem')
    pai=next((o for o in origens if o['menu']==nome or str(nome).endswith(' · Sem Técnica') and o['menu']==str(nome).split(' · ')[0]),None)
    propria=next((d for d in ctx.registros.values() if d.tipo=='Origem' and d.nome==nome and d.valida and d.aprovada),None)
    if propria:
        base=propria.campos.get('campo.base_do_livro','')
        pai=next((o for o in origens if o['menu']==base),None)
    if pai is None and propria is None:return True  # Nome/registro ausente é diagnosticado nas outras etapas.
    antes=len(r.problemas)
    vistas=set()
    for campo,grupo in [('origem.marcante','marcantes'),('origem.menor_1','menores'),('origem.menor_2','menores')]:
        escolhido=valor(ficha,campo)
        if not escolhido:
            problema(r,campo,'escolher capacidade da Origem','vazio',pendente=True,regra='informação',ancora='origens--origens');continue
        permitidas={c['nome']:c for c in pai[grupo]} if pai else {}
        exige=''
        registro=next((d for d in ctx.registros.values() if d.tipo==('Marcante' if grupo=='marcantes' else 'Menor') and d.nome==escolhido and d.valida),None)
        if registro and registro.campos.get('campo.origem') in (nome,pai['menu'] if pai else nome):
            if not registro.aprovada:
                problema(r,campo,'aprovação da capacidade custom pelo mestre',escolhido,pendente=True,regra='aprovação')
            exige=registro.campos.get('campo.exige_marcante','')
        elif escolhido not in permitidas:
            if 'mestre' in str(escolhido).casefold():
                problema(r,campo,'definição/aprovação verificável da capacidade criada',escolhido,pendente=True,regra='aprovação')
            else:
                problema(r,campo,'capacidade publicada ou cadastro válido vinculado a esta Origem',escolhido,regra='custom',ancora='origens--origens')
        elif grupo=='menores':
            exige=permitidas[escolhido].get('exige') or ''
        if grupo=='menores' and exige not in ('','—'):
            marcante=valor(ficha,'origem.marcante')
            if marcante!=exige:
                problema(r,campo,'marcante exigida: '+exige,marcante or 'vazio',
                         pendente=marcante=='',regra='informação' if marcante=='' else 'custom',
                         ancora='origens--origem-escolhas')
        if grupo=='menores' and escolhido in vistas:
            problema(r,campo,'duas menores distintas',escolhido,regra='custom',ancora='origens--origens')
        vistas.add(escolhido)
    return len(r.problemas)==antes


def conferir_familias(ficha,magia,raiz,problemas,r=None):
    from .ficha_corretor import Problema
    from .ficha_testes import chave
    ctx=magia.contexto
    nomes=set(magia.familias)|set(ctx.familias)
    def erro(k,texto,atual):
        problemas.append(Problema('famílias',k,texto,str(atual),
            'construcao--entidades-familias' if raiz!='tecnica' else 'fundamento--familias'))
    if raiz=='tecnica':
        estados={n:valor(ficha,'tecnica.familia.'+chave(n)) for n in magia.familias}
        estados.update(ctx.familias)
        if any(e not in ('Livre','Neutra','Fechada') for e in estados.values()):
            erro('tecnica.familias','escolher Livre, Neutra ou Fechada em cada Família',estados)
            return None,None
        livres={n for n,e in estados.items() if e=='Livre'}
        fechadas={n for n,e in estados.items() if e=='Fechada'}
        for campo,atual,esperado in [('familias_livres',len(livres),ctx.regras['familias_livres']),
                                      ('familias_fechadas',len(fechadas),ctx.regras['familias_fechadas'])]:
            if atual!=esperado:
                erro('regra.'+campo,f'{esperado} conforme campanha autorizada',atual)
        for campo,esperado in [('familias_total',len(estados)),('familias_neutras',len(estados)-ctx.regras['familias_livres']-ctx.regras['familias_fechadas'])]:
            if valor(ficha,'regra.'+campo)!=esperado:
                erro('regra.'+campo,f'{esperado}, recalculado do catálogo',valor(ficha,'regra.'+campo))
        return livres,nomes-fechadas
    from .ficha_configuracao import trilha_mecanica
    trilha=trilha_mecanica(ficha,ctx)
    if trilha is None:
        if r is not None:
            r.nao_conferido.append(raiz+': Famílias dependem de Trilha válida e aprovação da definição exata')
        return None,None
    perfil='principal' if trilha=='Invocação Principal' else 'parceria' if trilha in ('Parceria','Múltiplas Invocações') else 'padrao'
    autonomia=valor(ficha,raiz+'.autonomia') or 'Autônoma'
    if autonomia not in ('Autônoma','Não autônoma'):
        erro(raiz+'.autonomia','Autônoma ou Não autônoma',autonomia)
        return None,None
    extra=ctx.regras['invocacao_familias_livres_nao_autonoma'] if autonomia=='Não autônoma' else 0
    trilha_total=ctx.aplicar('Invocações · famílias da trilha',ctx.regras['invocacao_familias_abertas_'+perfil])
    if trilha_total is None:
        erro(raiz+'.limite_familias','resolver conflito dos efeitos de famílias da trilha','conflito')
        return None,None
    if not numero(trilha_total) or trilha_total != int(trilha_total):
        erro(raiz+'.limite_familias','total inteiro de Famílias abertas',trilha_total)
        return None,None
    total=int(trilha_total)+extra
    livres=ctx.regras['invocacao_familias_livres_'+perfil]+extra
    # As primeiras posições mantêm a prioridade; não se compactam espaços vazios.
    ordem=(1,2,6,7,8,9,3,4,5)
    escolhidas={i:valor(ficha,f'{raiz}.familia.{i}') for i in range(1,10)}
    abertas=[n for n in escolhidas.values() if n!='']
    livres_n={escolhidas[i] for i in ordem[:livres] if escolhidas[i]!=''}
    if not 0<=livres<=total<=9:
        erro(raiz+'.limite_familias','0 ≤ Livres ≤ total aberto ≤ nove vagas',(livres,total))
        return None,None
    for campo,esperado in [('limite_familias',total),('limite_livres',livres)]:
        if valor(ficha,raiz+'.'+campo)!=esperado:
            erro(raiz+'.'+campo,f'{esperado}, pela campanha e autonomia desta entidade',valor(ficha,raiz+'.'+campo))
    if len(abertas)>total or len(set(abertas))!=len(abertas) or any(n not in nomes for n in abertas):
        erro(raiz+'.familias',f'até {total} Famílias distintas e conhecidas; Livre conta no total',abertas)
        return None,None
    if r is not None and (len(abertas)<total or len(livres_n)<livres):
        problema(r,raiz+'.familias',f'completar {total} abertas, incluindo {livres} Livres',abertas,pendente=True,regra='informação')
    return livres_n,set(abertas)


def conferir_contas_b47(ficha,ref,regras,certos,pendencias):
    from .ficha_corretor import Resultado, Peca, _capacidades, DEFESA_ZERO, SEM_INTEGRIDADE, VIDA_METADE, refino
    r=Resultado('aprovada');ctx=ref.magia.contexto
    n=valor(ficha,'nivel')
    if not inteiro(n,1,30):
        return [],['vida, PE, Integridade e Defesa: nível vazio ou inválido']
    atrs={}
    for a in ('forca','destreza','constituicao','inteligencia','essencia'):
        base,corpo=[valor(ficha,f'atributo.{a}.{p}') for p in ('base','corpo')]
        if not numero(base) or corpo!='' and not numero(corpo):
            r.nao_conferido.append(f'atributo.{a}: falta base/Corpo numérico; contas dependentes não certificadas')
        else:
            atrs[a]=base+(corpo or 0)
    if len(atrs)!=5:
        return r.problemas,r.nao_conferido
    def buff(k):
        v=valor(ficha,'buff.'+k)
        if v=='':return 0
        if not numero(v):
            problema(r,'buff.'+k,'ajuste numérico finito',v)
            return None
        if v:
            problema(r,'buff.'+k,'confirmar origem e que não duplica BÔNUS E MUDANÇAS',v,pendente=True,regra='aprovação')
        return v
    def comparar(k,base,caixa):
        esperado=ctx.aplicar(caixa,base)
        if esperado is None:
            r.nao_conferido.append(f'{k}: entradas inválidas ou efeitos em conflito')
        elif not numero(valor(ficha,k)) or valor(ficha,k)!=esperado:
            problema(r,k,str(esperado),valor(ficha,k),regra='conta')
        else:
            certos.append(f'{ {"vida_max":"Vida","energia_max":"PE","integridade_max":"Integridade","protecao":"Proteção","defesa":"Defesa"}.get(k,k)} {esperado:g}')
        return esperado
    caminho=ref.caminhos.get(valor(ficha,'caminho'))
    caps=_capacidades(ficha)
    bvida,bpe,bint,bprot,bdef=[buff(k) for k in ('vida','energia','integridade','protecao','defesa')]
    if caminho and bvida is not None:
        vida=caminho['vida1']+atrs['constituicao']+(caminho['vidaNv']+atrs['constituicao'])*(n-1)
        if ctx.regras['vida_rolada']=='Sim':
            dado=caminho.get('dadoVida',int(str(caminho.get('dado','d'+str(caminho['vida1']))).removeprefix('d')))
            rolagens=[valor(ficha,f'vida.rolagem.{i}') for i in range(2,n+1)]
            if any(not inteiro(v,1,dado) for v in rolagens):
                for i,v in enumerate(rolagens,2):
                    if not inteiro(v,1,dado):
                        problema(r,f'vida.rolagem.{i}',f'resultado guardado de 1 a {dado}',v,pendente=v=='',regra='informação' if v=='' else 'conta')
                vida=None
            else:
                vida=caminho['vida1']+atrs['constituicao']*n+sum(rolagens)
        if vida is not None:
            vida+=bvida
            if caps&set(VIDA_METADE):vida=max(1,vida//2)
        comparar('vida_max',vida,'Vida máxima')
    else:r.nao_conferido.append('Vida: Caminho ou Buff inválido/não automatizado')
    if caminho and bpe is not None:
        pe=caminho['peNv']*n+bpe
        def talento_base(nome):
            d=next((d for d in ctx.registros.values() if d.tipo=='talento' and d.nome==nome and d.valida and d.aprovada),None)
            return d.efetivos.get('identidade',nome) if d else nome
        if any(talento_base(valor(ficha,f'passiva.{i}'))=='Reserva Profunda' for i in range(1,13)):
            extra=3*ref.magia.classe_maxima(n)
            explicitos=[e for e in ctx.efeitos.get('PE máximo',[]) if talento_base(e.fonte)=='Reserva Profunda' and e.como=='somar']
            if bpe or explicitos and sum(e.valor for e in explicitos)!=extra:
                problema(r,'energia_max',f'identificar os {extra} PE de Reserva Profunda uma única vez entre Buff e efeitos',
                         f'Buff {bpe}; efeitos identificados {sum(e.valor for e in explicitos)}',pendente=True,regra='aprovação',ancora='catalogo--cat-passivas-3')
                r.nao_conferido.append('PE: Reserva Profunda com ajuste de origem ambígua; total não certificado para evitar contagem dupla')
                pe=None
            elif not explicitos:
                pe+=extra
        comparar('energia_max',pe,'PE máximo')
    else:r.nao_conferido.append('PE: Caminho ou Buff inválido/não automatizado')
    if caps&set(SEM_INTEGRIDADE):
        if valor(ficha,'integridade_max') not in ('',0):
            problema(r,'integridade_max','sem barra de Integridade',valor(ficha,'integridade_max'),regra='conta')
    elif bint is not None:
        comparar('integridade_max',20+(atrs['essencia']+5)*(n-1)+bint,'Integridade máxima')
    uniforme=ref.uniformes.get(valor(ficha,'em_uso.vestindo'))
    if valor(ficha,'em_uso.vestindo') not in ('','—','-') and uniforme is None:
        r.nao_conferido.append('Defesa/Proteção: uniforme sem funcionamento autorizado conhecido')
    elif any(valor(ficha,'em_uso.'+k) not in ('','—','-','Soco') and valor(ficha,'em_uso.'+k) not in ref.equipamento.pecas for k in ('principal','secundaria')):
        r.nao_conferido.append('Defesa/Proteção: equipamento empunhado sem funcionamento autorizado conhecido')
    elif bprot is not None and bdef is not None:
        escudo=None if valor(ficha,'em_uso.principal') in ref.duas_maos else ref.escudos.get(valor(ficha,'em_uso.secundaria'))
        protecao=(uniforme.protecao if uniforme else 1+refino(n,int(valor(ficha,'marco.refino') or 0),ref)//3)+(escudo.protecao if escudo else 0)+bprot
        protecao=comparar('protecao',protecao,'Proteção')
        tetos=[p.teto_destreza for p in (uniforme,escudo) if p and p.teto_destreza is not None]
        defesa=None if protecao is None else 10+min([atrs['destreza'],*tetos])+protecao+bdef
        if caps&set(DEFESA_ZERO):defesa=0
        comparar('defesa',defesa,'Defesa')
    pendencias.extend(r.pendencias)
    return r.problemas,r.nao_conferido


def conferir_progressao(ficha,ref,ctx,r):
    n=valor(ficha,'nivel')
    if not inteiro(n,1,30):return
    marcos=sum(m<=n for m in ref.marcos)
    for parcela,teto in [('base',ctx.regras['atributos_pontos']+marcos),('corpo',valor(ficha,'marco.corpo'))]:
        vs=[valor(ficha,f'atributo.{a}.{parcela}') for a in ('forca','destreza','constituicao','inteligencia','essencia')]
        if all(v=='' or inteiro(v) for v in vs) and numero(teto):
            total=sum(v or 0 for v in vs)
            if total!=teto:
                problema(r,'atributos.'+parcela,f'distribuir {teto} pontos; há {total}',total,pendente=total<teto,regra='progressão',ancora='progressao--prog-marcos')
        else:
            problema(r,'atributos.'+parcela,'atributos inteiros não negativos',vs,regra='progressão')
    for a in ('forca','destreza','constituicao','inteligencia','essencia'):
        vs=[valor(ficha,f'atributo.{a}.{p}') for p in ('base','corpo')]
        if all(v=='' or numero(v) for v in vs):
            if sum(v or 0 for v in vs)>ctx.regras['atributos_teto']:
                problema(r,f'atributo.{a}.base',f'total até {ctx.regras["atributos_teto"]}',sum(v or 0 for v in vs),regra='progressão')
    bases=[valor(ficha,f'atributo.{a}.base') for a in ('forca','destreza','constituicao','inteligencia','essencia')]
    if all(inteiro(v) for v in bases) and sum(max(0,v-ctx.regras['atributos_teto_criacao']) for v in bases)>marcos:
        problema(r,'atributos.base','aumentos além do teto de criação limitados aos marcos alcançados',bases,regra='progressão')
    # Nível é editável na ficha: XP compatível não prova história de missões/feitos.
    r.nao_conferido.append('XP: nível manual, origem dos ganhos, Limiar e histórico de missões exigem registro do mestre')
    vida=valor(ficha,'vida_max') if any(c.startswith('Vida ') for c in r.conferidos) else None;classe=ref.magia.classe_maxima(n)
    if numero(vida):
        for k,fracao in [('morrendo_aguentar','morrendo_aguentar'),('morrendo_insistir_1','morrendo_insistir_1'),('morrendo_insistir_2','morrendo_insistir_2')]:
            esperado=math.ceil(round(vida*ctx.regras[fracao],10))
            if k!='morrendo_aguentar':esperado=min(esperado,ctx.regras['morrendo_teto']*classe)
            if valor(ficha,k)!=esperado:
                problema(r,k,str(esperado),valor(ficha,k),regra='conta',ancora='dano--morrendo')


def conferir_treinos(ficha,ref,ctx,r):
    from .ficha_testes import atributo, ATRIBUTOS, _conferir_quantidades
    n=valor(ficha,'nivel')
    if not inteiro(n,1,30):return
    contagens={'pericia':0,'oficio':0};especializacoes=0
    completo=True
    for tipo,tabela in [('pericia',ref.testes.pericias),('oficio',ref.testes.oficios)]:
        for slug,(nome,atr) in tabela.items():
            t,e=[valor(ficha,f'{tipo}.{slug}.{k}') for k in ('treino','especialista')]
            if t not in (0,1) or e not in (0,1):
                problema(r,f'{tipo}.{slug}.treino','treino e especialização 0/1',(t,e));completo=False;continue
            contagens[tipo]+=t;especializacoes+=e
            if e and (not t or n<10):
                problema(r,f'{tipo}.{slug}.especialista','especialização exige treino e nível 10+',e,regra='treinos')
                completo=False
    for tipo,limite in [('pericia',23),('oficio',11)]:
        vistos=set()
        for i in range(1,limite+1):
            base=f'personagem.{tipo}_custom.{i}'
            nome=valor(ficha,base+'.nome')
            t,e=[valor(ficha,base+'.'+k) for k in ('treino','especializacao')]
            if not nome:
                if t or e:
                    problema(r,base+'.nome','nome da competência com treino/especialização','vazio',pendente=True,regra='informação')
                continue
            if nome in vistos:
                problema(r,base+'.nome','não repetir competência',nome,regra='treinos')
            vistos.add(nome)
            d=next((d for d in ctx.registros.values() if d.tipo==tipo and d.nome==nome and d.valida),None)
            if d is None:
                problema(r,base+'.nome','cadastro válido da competência',nome,regra='custom');completo=False;continue
            if t not in (0,1) or e not in (0,1):
                problema(r,base+'.treino','marcação 0/1',(t,e));completo=False;continue
            contagens[tipo]+=t;especializacoes+=e
            if e and (not t or n<10):
                problema(r,base+'.especializacao','especialização exige treino e nível 10+',e,regra='treinos')
                completo=False
                continue
            a=atributo(valor(ficha,base+'.atributo'))
            padrao=atributo(d.campos.get('atributo',''))
            if a is None or tipo=='pericia' and a!=padrao:
                problema(r,base+'.atributo',str(d.campos.get('atributo','atributo válido')),valor(ficha,base+'.atributo'),regra='treinos');continue
            bs=[valor(ficha,f'atributo.{a}.{p}') for p in ('base','corpo')]
            if not numero(bs[0]) or bs[1]!='' and not numero(bs[1]):
                r.nao_conferido.append(base+': atributo insuficiente para conferir bônus');continue
            ajuste=valor(ficha,base+'.bonus')
            if ajuste=='':ajuste=0
            if not numero(ajuste):
                problema(r,base+'.bonus','ajuste numérico finito',ajuste,regra='treinos');continue
            if ajuste:
                problema(r,base+'.bonus','confirmar a origem e não duplicar efeitos',ajuste,pendente=True,regra='aprovação')
            esperado=ctx.aplicar(f'{"Perícia" if tipo=="pericia" else "Ofício"} · {nome}',sum(v or 0 for v in bs)+t*ref.magia.maestria[n]+e*(ref.magia.maestria[n]//2)+ajuste)
            if esperado is not None and valor(ficha,base+'.resultado')!=esperado:
                problema(r,base+'.resultado',str(esperado),valor(ficha,base+'.resultado'),regra='conta')
            elif esperado is not None and d.aprovada:
                r.conferidos.append(f'{nome}: bônus {esperado:+g}')
    if completo:
        def registrar(k,esperado,ancora='',pendente=False):
            problema(r,k,esperado,valor(ficha,k),pendente=pendente,regra='treinos',ancora=ancora)
        from .ficha_testes import RegrasTestes
        bases=((ctx.regras['pericias_com_oficio'],ctx.regras['oficios_criacao']),(ctx.regras['pericias_sem_oficio'],0))
        custom_ref=replace(ref,testes=replace(ref.testes,bases=bases))
        corpo=valor(ficha,'marco.corpo')
        if inteiro(corpo,0,sum(m<=n for m in ref.marcos)):
            _conferir_quantidades(ficha,custom_ref,r,n,corpo,contagens['pericia'],contagens['oficio'],especializacoes,registrar)
    r.nao_conferido.append('TR/perícias/Ofícios do livro: B47 não exporta os ajustes e bônus exclusivos da variante TR-v4; não se inventam resultados')


def conferir_aptidoes(ficha,ref,ctx,r):
    import itertools
    from .ficha_personagem_motor import Contexto, aptidoes
    from .ficha_corretor import refino
    from .ficha_testes import ATRIBUTOS
    n=valor(ficha,'nivel')
    if not inteiro(n,1,30):return
    marcos=sum(m<=n for m in ref.marcos)
    escolhidos=valor(ficha,'marco.refino')
    if not inteiro(escolhidos,0,marcos):return
    orcamentos=set()
    for escolhas in itertools.combinations(range(marcos),escolhidos):
        rf=1;apt=0
        for i in range(marcos):
            rf=min(ref.refino_maximo,rf+1)
            if i in escolhas:
                apt+=2 if rf==ref.refino_maximo else 1
                rf=min(ref.refino_maximo,rf+1)
        orcamentos.add(apt)
    origem=valor(ficha,'origem')
    sem_tecnica=str(origem).endswith(' · Sem Técnica')
    orcamentos={v+int(sem_tecnica) for v in orcamentos}
    rota=4 if origem=='Restrição Celestial · Sem Energia' else 3 if origem=='Corpo Amaldiçoado' else 2 if sem_tecnica else 1
    atributos={nome:(valor(ficha,f'atributo.{a}.base') or 0)+(valor(ficha,f'atributo.{a}.corpo') or 0) for a,nome in ATRIBUTOS.items()}
    contexto=Contexto(rota=rota,nivel=n,refino=refino(n,escolhidos,ref),escolhas=max(orcamentos),
                     atributos=atributos,origem=str(origem).split(' · ')[0],
                     historia_treinada=valor(ficha,'pericia.historia.treino')==1)
    nomes=[valor(ficha,f'aptidao.{i}') for i in range(1,13)]
    if any(d.nome in nomes and (not d.aprovada or not d.valida) for d in ctx.registros.values() if d.tipo=='aptidao'):
        r.nao_conferido.append('Aptidões/Bênçãos: definição selecionada sem aprovação válida; aquisição não certificada')
    else:
        resultado=aptidoes(ctx.catalogo_personagem,nomes,contexto)
        for mensagem in resultado['avisos']:
            sem_informacao=any(x in mensagem for x in ('aprendizado não registrado','Técnica Inata','aprendizado de clã'))
            problema(r,'aptidoes',mensagem,'seleções do personagem',pendente=sem_informacao,
                     regra='informação' if sem_informacao else 'aptidão',ancora='aptidoes--apt-marcos')
        if len(orcamentos)>1:
            r.nao_conferido.append('Aptidões: total no teto de Refino depende da ordem histórica dos marcos, não exportada')
    for grupo,padrao in [('talento',r'passiva\.\d+'),('aptidao',r'aptidao\.\d+')]:
        vistos=set()
        for k in ficha:
            if not re.fullmatch(padrao,k) or not valor(ficha,k):continue
            nome=valor(ficha,k)
            d=next((d for d in ctx.registros.values() if d.tipo==grupo and d.nome==nome and d.aprovada and d.valida),None)
            identidade=d.efetivos.get('identidade') or nome if d else nome
            if identidade in vistos:
                problema(r,k,'não repetir a mesma identidade/base por aliases diferentes',nome,regra='aptidão' if grupo=='aptidao' else 'talento')
            vistos.add(identidade)
    if any(nomes):
        r.nao_conferido.append('Aptidões/Bênçãos: concessões de Origem, aprendizado não exportado, requisitos livres e efeitos narrativos exigem mestre')


def conferir_competencias_entidade(ficha,ref,ctx,r,base):
    from .ficha_testes import atributo
    n=valor(ficha,'nivel')
    if not inteiro(n,1,30):return
    from .ficha_derivados_b47 import conferir_tr_entidade
    conferir_tr_entidade(ficha,ctx,r,base)
    escolhidas=[]
    nomes={nome:atr for nome,atr in ref.testes.pericias.values()}
    for d in ctx.registros.values():
        if d.tipo=='pericia' and d.valida and d.aprovada:
            nomes[d.nome]=atributo(d.campos.get('atributo'))
    for i in range(1,8):
        k=f'{base}.pericia.{i}'
        nome=valor(ficha,k)
        if not nome:continue
        if nome in escolhidas:
            problema(r,k,'treinos distintos',nome,regra='treinos')
        escolhidas.append(nome)
        a=nomes.get(nome)
        if a is None:
            r.nao_conferido.append(k+': competência sem atributo/definição aprovada');continue
        v,b=[valor(ficha,base+f'.atributo.{a}.{p}') for p in ('base','buff')]
        if not numero(v) or b!='' and not numero(b):continue
        esperado=v+(b or 0)+ref.magia.maestria[n]
        # Namespace histórico enganoso: buff.pericia é RESULTADO, nunca ajuste.
        out=base+f'.buff.pericia.{i}'
        if valor(ficha,out)!=esperado:
            problema(r,out,str(esperado),valor(ficha,out),regra='conta',ancora='construcao--entidades-atributos')
        else:r.conferidos.append(f'{base.replace("invocacao.","Invocação ")} · {nome}: bônus {esperado:+g}')
    inteligencia=valor(ficha,base+'.atributo.inteligencia.base')
    if inteiro(inteligencia,0,6):
        teto=4+inteligencia//2
        if len(escolhidas)!=teto:
            problema(r,base+'.pericias',f'{teto} perícias distintas pelo atributo base',len(escolhidas),
                     pendente=len(escolhidas)<teto,regra='treinos',ancora='construcao--entidades-atributos')
