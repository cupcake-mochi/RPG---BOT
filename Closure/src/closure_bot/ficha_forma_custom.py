"""Montagem de Forma B47 aprovada a partir dos campos estruturados, sem executar prosa."""
import math
import re
from .ficha_configuracao import valor
from .ficha_magia import lista
from .ficha_personagem_motor import forma as calcular_forma


def conferir(ficha,magia,base,nivel,problemas,certos,pulou,*,entidade=False,basica=False,liberacao=False,familias=None,pendencias=None):
    from .ficha_corretor import Problema
    ctx=magia.contexto
    pendencias=pendencias if pendencias is not None else []
    inicio=len(problemas)
    classe=valor(ficha,base+'.classe')
    nome=valor(ficha,base+'.forma')
    pecas=lista(ficha,base+'.pecas');restricoes=lista(ficha,base+'.restricoes')
    def erro(campo,esperado):
        problemas.append(Problema('conta',base+'.'+campo,esperado,str(valor(ficha,base+'.'+campo)),'fundamento--pontos'))
    livres,abertas=familias or (None,None)
    if livres is None or abertas is None:
        pulou.append(base+': falta validar Famílias antes da Forma custom');return
    if any(p not in magia.melhorias for p in pecas) or any(p not in magia.restricoes for p in restricoes):
        pulou.append(base+': peça sem definição mecânica aprovada impede fechar a montagem');return
    usadas=[magia.melhorias[p] for p in pecas]
    limite=1 if classe==0 else 2 if classe<=2 else 3 if classe<=4 else 4
    if len(pecas)>limite:erro('pecas',f'até {limite} Melhorias')
    for n in pecas:
        p=magia.melhorias[n]
        identidade=ctx.aliases.get('melhoria:'+n,n)
        if sum(ctx.aliases.get('melhoria:'+outro,outro)==identidade for outro in pecas)>p.repeticoes or classe<p.minima or classe==0 and p.peso!='Leve':
            erro('pecas',f'{n}: respeitar repetição, Classe mínima e Classe 0 Leve')
        if p.familia and p.familia not in abertas:erro('pecas',f'{n}: Família {p.familia} aberta nesta ficha')
    if len(problemas)>inicio:
        pulou.append(base+': montagem inválida impede certificar benefício/alcance da Forma custom')
        return
    custo=lambda p:magia.preco(p,classe) if classe else 0
    gasto=sum(max(1,custo(p.peso)-(max(1,classe//2) if entidade else math.ceil(classe/2) if p.familia in livres else 0))
              if p.familia in livres else custo(p.peso) for p in usadas) if classe else len(pecas)
    # Motor puro extraído do contrato entregue: escadas e identidade da base, sem endereços de planilha.
    cat=ctx.catalogo_personagem
    for d in ctx.registros.values():
        if d.tipo=='restricao' and d.valida and d.aprovada:
            cat.livro['restricoes'][d.nome]={'nome':ctx.aliases.get('restricao:'+d.nome,d.nome),
                'devolve':1 if d.efetivos['devolucao']=='Leve' else 2,
                'frequencia':int(d.efetivos.get('frequencia')=='Sim')}
    pecas_regras=[ctx.aliases.get('melhoria:'+n,n) for n in pecas]
    longe=sum(1 if n=='Longe' else 3 if n=='Muito Longe' else 0 for n in pecas_regras)
    maior=sum(1 if n=='Maior' else 3 if n=='Muito Maior' else 0 for n in pecas_regras)
    try:
        definicao=cat.obter('forma',nome)
        if not definicao:
            erro('forma','definição estruturada válida da Forma custom');return
        identidade=definicao.get('identidade','')
        nomes_res=[re.sub(r' \((Leve|Média)\)$','',ctx.aliases.get('restricao:'+n,n)) for n in restricoes]
        presentes=pecas_regras+nomes_res
        for a,b in [('Atrasar','Parado'),('Silencioso','Gesto'),('Passo','Parado'),('Passo','Atrasar'),
                    ('Rápido','Reação'),('Barulho','Assinatura'),('Remate','Aquecer')]:
            if a in presentes and b in presentes:erro('pecas',f'não combinar {a} com {b}')
        if liberacao and (definicao.get('resultado')==1 or any(n in ('Rápido','Reação','Inescapável','Toca a Alma') for n in pecas_regras)):
            erro('pecas','Liberação não cura, exige Ação Completa e não aceita Inescapável/Toca a Alma')
        if identidade in ('Toque','Aura','Onda') and any(n in ('Longe','Muito Longe') for n in pecas_regras):
            erro('pecas',f'{identidade} não aceita aumento de distância')
        if 'Inescapável' in pecas_regras and (identidade!='Projétil' or len(pecas)>1 or restricoes or definicao.get('restricao_embutida')):
            erro('pecas','Inescapável: só identidade Projétil, sem outra Melhoria ou Restrição')
        if 'Junto' in pecas_regras and identidade not in ('Cura','Apoio'):
            erro('pecas','Junto somente em identidade Cura/Apoio')
        if 'Mais Um' in pecas_regras and identidade not in ('Projétil','Toque','Efeito'):
            erro('pecas','Mais Um exige identidade com alvo individual')
        if 'Rajada' in pecas_regras and (identidade not in ('Projétil','Toque') or 'Certeiro' in pecas_regras or definicao.get('resolucao')!='Acerto'):
            erro('pecas','Rajada exige alvo individual e ataque')
        if 'Terreno' in pecas_regras and identidade not in ('Explosão','Aura','Cone','Linha','Onda'):
            erro('pecas','Terreno exige identidade de Forma de área')
        if 'Corrói' in pecas_regras and 'Mira' not in livres:erro('pecas','Corrói exige Mira Livre')
        if len(problemas)>inicio:
            pulou.append(base+': combinações inválidas impedem certificar a Forma custom')
            return
        montada=calcular_forma(cat,nome,'entidade' if entidade else 'personagem',classe,longe=longe,maior=maior,
                              livre=definicao.get('familia') in livres,
                              familias_abertas=abertas,melhorias=gasto,restricoes=restricoes)
    except ValueError as e:
        erro('forma',str(e));return
    for aviso in montada.get('avisos',[]):erro('forma',aviso)
    if not montada.get('valido'):return
    if classe==0:
        if len(restricoes)+(montada['restricao_embutida'] is not None)>1 or any(magia.restricoes[n][0]!='Leve' for n in restricoes):
            erro('restricoes','somente uma Restrição Leve, contando a embutida')
        saldo=(1 if nivel<5 else 2 if nivel<17 else 3) if entidade else (2 if nivel<5 else 3 if nivel<11 else 4 if nivel<17 else 5 if nivel<25 else 6)
        saldo=max(0,saldo-int(bool(pecas))+int(bool(pecas) and bool(restricoes or montada['restricao_embutida'])))
    else:
        orcamento=magia.especiais[classe] if entidade else magia.classes[classe][1]
        saldo=orcamento-montada['custo']-gasto+montada['utilizada']
        if saldo<0:erro('pecas',f'montagem dentro de {orcamento} pontos');return
    if len(problemas)>inicio:
        pulou.append(base+': Restrições inválidas impedem certificar benefício da Forma custom')
        return
    modo=montada['resultado']
    if classe and modo==1:saldo=min(saldo,orcamento-montada['custo'])
    if classe and liberacao:saldo+=classe
    if classe and modo==0:
        def cabe(d):
            adicionais=sum(d//2 for n in pecas_regras if n in ('Salto','Queima','Estilhaço'))
            return d*(1.25 if 'Remate' in pecas_regras else 1)+adicionais<=4*classe
        saldo=max(d for d in range(saldo+1) if cabe(d))
    alma='Toca a Alma' in pecas_regras
    mistura_alma=alma and any(n in ('Salto','Queima','Estilhaço','Rajada','Mais Um') for n in pecas_regras)
    if alma:
        pulou.append(base+': Toca a Alma exige Regra autorizada que trate da alma; conta não concede permissão')
    if mistura_alma:
        pulou.append(base+': interação de Alma com adicionais/distribuição exige revisão; dano não certificado')
    else:
        if alma:saldo//=2
        faces=6 if entidade and classe==0 else 8
        esperado=('Sem dano' if modo==3 else f'{3*saldo} de vida temp.' if modo==2 else
                  f'Cura {saldo}d{faces}' if modo==1 and saldo else 'Sem cura' if modo==1 else f'{saldo}d{faces}' if saldo else 'Sem dano')
        adicionais=sum(saldo//2 for n in pecas_regras if n in ('Salto','Queima','Estilhaço')) if classe and modo==0 else 0
        texto=str(valor(ficha,base+'.dano'))
        if modo in (0,1) and saldo:
            m=re.fullmatch(r'(?:Cura\s*:?[ ]*)?(\d+)d(6|8)(?: = (\d+))?((?:\s*·?\s*\+\s*\d+d8)*)',texto)
            bate=bool(m and int(m[1])==saldo and int(m[2])==faces and
                      (m[3] is None or int(m[3])==saldo*(faces+1)//2) and
                      sum(map(int,re.findall(r'\+\s*(\d+)d8',m[4])))==adicionais)
            if modo==1 and not texto.startswith('Cura'):bate=False
        else:bate=texto==esperado
        if not bate:erro('dano',esperado+(f' +{adicionais}d8 adicionais' if adicionais else ''))
        else:certos.append(base+': benefício numérico da Forma custom '+esperado)
    if any(n in ('Rajada','Mais Um','Junto') for n in pecas_regras):
        pulou.append(base+': benefício total não se multiplica; distribuição por tiros/alvos exige registro antes da rolagem')
    if 'Remate' in pecas_regras and 'Condicional' in nomes_res:
        pulou.append(base+': Remate não combina com Condicional de vida/duração; conferir o gatilho escrito')
    alcance_esperado=montada['alcance']
    if identidade in ('Projétil','Toque'):
        alvos=pecas_regras.count('Mais Um')
        if alvos:alcance_esperado+=f' · +{alvos} alvo'+('s' if alvos>1 else '')
        if 'Rajada' in pecas_regras:
            tiros=(max(1,classe-1)+1 if classe else 1) if entidade else classe+1
            alcance_esperado+=f' · {tiros} tiro'+('s' if tiros>1 else '')
    alcance=str(valor(ficha,base+'.alcance'))
    if base+'.alcance' not in ficha:pulou.append(base+': alcance não exportado')
    elif alcance.casefold()!=alcance_esperado.casefold():erro('alcance',alcance_esperado)
    else:certos.append(base+': alcance/área '+alcance)
    resolucao=montada['resolucao']
    def exige_tr(n):
        d=next((d for d in ctx.registros.values() if d.tipo=='melhoria' and d.nome==n and d.valida and d.aprovada),None)
        if d and d.efetivos.get('exige_tr') in ('Sim','Não'):
            return d.efetivos['exige_tr']=='Sim'
        return n in ('Prende','Cerca') or n.startswith('Condição: ') or magia.melhorias[n].familia=='Controle' and n not in ('Terreno','Desarma o Feitiço')
    controle=montada['exige_tr'] and resolucao=='Acerto' or any(exige_tr(n) for n in pecas)
    if resolucao=='Acerto' and controle:resolucao='Acerto + TR'
    if 'Certeiro' in pecas_regras:resolucao='TR para metade'
    if 'Inescapável' in pecas_regras:resolucao='Automático'
    if entidade:
        from .ficha_efeitos import _conferir_bonus_entidade
        escolha=valor(ficha,base+'.resolucao_escolha')
        if escolha not in ('','Ataque','TR Físico','TR Vigor','TR Intelecto','TR Espírito'):
            erro('resolucao_escolha','resolução válida da entidade')
        elif resolucao=='Automático':
            esperado='Automático' if 'Inescapável' in pecas_regras else 'Sem rolagem'
            if valor(ficha,base+'.resolve')!=esperado:erro('resolve',esperado)
            else:certos.append(base+': resolução '+esperado)
        else:
            ataque=(escolha=='Ataque' or not escolha and montada['resolucao']=='Acerto') and 'Certeiro' not in pecas_regras
            tipo='Ataque' if ataque else escolha if escolha.startswith('TR') else 'TR'
            if not _conferir_bonus_entidade(ficha,magia,base,tipo,str(valor(ficha,base+'.resolve')),ataque,controle,
                                          pecas_regras,problemas,certos,pulou,pendencias):
                pulou.append(base+': faltam entradas para conferir bônus da resolução da entidade')
    elif valor(ficha,base+'.resolve')!=resolucao:erro('resolve',resolucao)
    else:certos.append(base+': resolução '+resolucao)
    pulou.append(base+': requisitos livres, aplicação e efeito narrativo da Forma custom exigem mestre')
