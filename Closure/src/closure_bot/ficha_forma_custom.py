"""Montagem de Forma B47 aprovada a partir dos campos estruturados, sem executar prosa."""
import math
import re
from .ficha_configuracao import valor
from .ficha_magia import lista
from .ficha_personagem_motor import forma as calcular_forma


def conferir(ficha,magia,base,nivel,problemas,certos,pulou,*,entidade=False,basica=False,liberacao=False,familias=None):
    from .ficha_corretor import Problema
    ctx=magia.contexto
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
        if pecas.count(n)>p.repeticoes or classe<p.minima or classe==0 and p.peso!='Leve':
            erro('pecas',f'{n}: respeitar repetição, Classe mínima e Classe 0 Leve')
        if p.familia and p.familia not in abertas:erro('pecas',f'{n}: Família {p.familia} aberta nesta ficha')
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
    longe=sum(1 if n=='Longe' else 3 if n=='Muito Longe' else 0 for n in pecas)
    maior=sum(1 if n=='Maior' else 3 if n=='Muito Maior' else 0 for n in pecas)
    try:
        definicao=cat.obter('forma',nome)
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
        saldo-=int(bool(pecas));saldo+=int(bool(pecas) and bool(restricoes))
    else:
        orcamento=magia.especiais[classe] if entidade else magia.classes[classe][1]
        saldo=orcamento-montada['custo']-gasto+montada['utilizada']
        if saldo<0:erro('pecas',f'montagem dentro de {orcamento} pontos');return
    # A liberação e interações nomeadas conservam exigências próprias ainda verificadas manualmente.
    especiais={'Remate','Salto','Queima','Estilhaço','Toca a Alma','Rajada','Mais Um','Junto','Inescapável','Corrói'}
    if liberacao or any(ctx.aliases.get('melhoria:'+n,n) in especiais for n in pecas):
        pulou.append(base+': interações da Forma custom com Liberação/peças especiais não automatizadas; dano não certificado')
    else:
        modo=montada['resultado']
        if classe and modo==0:saldo=min(saldo,4*classe)
        if classe and modo==1:saldo=min(saldo,orcamento-montada['custo'])
        dado=6 if entidade and classe==0 else 8
        esperado=('Sem dano' if modo==3 else f'{3*saldo} de vida temp.' if modo==2 else
                  f'Cura {saldo}d{dado}' if modo==1 and saldo else 'Sem cura' if modo==1 else f'{saldo}d{dado}' if saldo else 'Sem dano')
        texto=str(valor(ficha,base+'.dano'))
        if texto!=esperado and not re.fullmatch(re.escape(esperado)+rf' = {saldo*(dado+1)//2}',texto):
            erro('dano',esperado)
        else:certos.append(base+': benefício numérico da Forma custom '+esperado)
    alcance=str(valor(ficha,base+'.alcance'))
    if base+'.alcance' not in ficha:pulou.append(base+': alcance não exportado')
    elif alcance.casefold()!=montada['alcance'].casefold():erro('alcance',montada['alcance'])
    else:certos.append(base+': alcance/área '+alcance)
    resolucao=montada['resolucao']
    if resolucao=='Acerto' and any(p.familia=='Controle' for p in usadas):resolucao='Acerto + TR'
    if entidade:
        pulou.append(base+': apresentação/resolução numérica de Forma custom de entidade ainda requer conferência')
    elif any(n in ('Certeiro','Rajada','Inescapável') for n in pecas):
        pulou.append(base+': resolução com peças especiais ainda não automatizada nesta Forma custom')
    elif valor(ficha,base+'.resolve')!=resolucao:erro('resolve',resolucao)
    else:certos.append(base+': resolução '+resolucao)
    pulou.append(base+': requisitos livres, aplicação e efeito narrativo da Forma custom exigem mestre')
