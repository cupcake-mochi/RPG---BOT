"""Casos de contrato para testar o consumidor; não recalcula o produtor."""
from pathlib import Path
import sys, json, copy, argparse
from dataclasses import asdict
from types import SimpleNamespace

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base',type=Path,required=True)
p.add_argument('--custom',type=Path,required=True)
p.add_argument('--saida',type=Path,required=True)
p.add_argument('--closure',type=Path,default=Path(__file__).resolve().parents[3])
args=p.parse_args()
ROOT=args.closure.resolve()
sys.path.insert(0, str(ROOT/'src'))
from closure_bot.ficha_leitor import de_xlsx, Campo
from closure_bot.ficha_corretor import conferir, Aprovados
from closure_bot.cogs.ficha import paginas
from closure_bot.ficha_testes import chave
from testes.test_b47_integracao import REF, trocar, aprovar
from testes.test_b47_revisao import entidade
from testes.test_b47_derivados import efeito

OUT=args.saida.resolve();OUT.mkdir(parents=True,exist_ok=True)
BASE=de_xlsx(args.base)
CUSTOM=de_xlsx(args.custom)
# Aprovação local sintética; não lê nem instala cadastro operacional.
AP=aprovar(CUSTOM,'custom.pericia.1').impressoes
CASOS=[]

def novo(): return copy.deepcopy(BASE)

def subir(f,n):
    trocar(f,nivel=n)
    for k in ('maestria','classe_maxima','refino_de_graca','classe_0_gratis','iniciativa','morrendo_prazo','cd_de_feitico','conjuracao','corpo_a_corpo','a_distancia'):
        trocar(f,**{k:''})
    # Valores sintéticos pela progressão publicada, sem inferir entradas dos resultados.
    trocar(f,vida_max=14+9*(n-1),energia_max=4*n,integridade_max=20+6*(n-1),
           protecao=1,defesa=13,espacos_de_feitico={10:9,17:13}[n],
           morrendo_aguentar={10:24,17:40}[n],morrendo_insistir_1={10:32,17:53}[n],morrendo_insistir_2={10:45,17:75}[n])
    return f

def familias(f,*necessarias,livre=()):
    estados={k:c.valor for k,c in f.items() if k.startswith('tecnica.familia.')}
    for nome in necessarias:
        alvo='tecnica.familia.'+chave(nome)
        if alvo not in estados:continue
        if estados[alvo]=='Fechada':
            outro=next(k for k,v in estados.items() if v=='Neutra' and not any(k.endswith('.'+chave(n)) for n in necessarias))
            estados[outro]='Fechada';estados[alvo]='Neutra'
    for nome in livre:
        alvo='tecnica.familia.'+chave(nome)
        if estados[alvo]!='Livre':
            outro=next(k for k,v in estados.items() if v=='Livre' and not any(k.endswith('.'+chave(n)) for n in livre))
            estados[outro]=estados[alvo];estados[alvo]='Livre'
    trocar(f,**estados)
    return f

def registrar(slug,titulo,f,alvo,esperado,*,incompleto=False,cache=False,duplicada=False,reader=None,aprovacao_extra=None):
    n=len(CASOS)+1
    trocar(f,nome=f'B47-A{n:02d} · {titulo}')
    if incompleto:del f['efeito.30.valor']
    aprovado=dict(AP)
    if aprovacao_extra:aprovado.update(aprovacao_extra)
    r=conferir(f,REF,aprovados=Aprovados(aprovado)) if not reader else None
    ps=paginas(r,f,SimpleNamespace(chave='kaltsit',nome="Kal'tsit",avatar_url=None)) if r else []
    c={'n':n,'slug':slug,'titulo':titulo,'nome':f['nome'].valor,'file':f'{n:02d}-{slug}.xlsx',
       'alvo':alvo,'esperado':esperado,'reader':reader,'sem_cache':cache,'duplicada':duplicada,
       'linhas':[['chave','valor','célula','parte']]+[[k,c.valor,c.celula,c.parte] for k,c in f.items()],
       'resultado':asdict(r) if r else None,'paginas':[p.to_dict() for p in ps]}
    CASOS.append(c)

registrar('incompleta','Exportação incompleta',novo(),'efeito.30.valor','Ausência não vira zero; nenhuma conta certificada',incompleto=True)
registrar('sem-cache','Fórmula sem cache',novo(),'vida_max','Erro de leitura claro',cache=True,reader='fórmula sem resultado calculado')
registrar('erro-formula','Erro de fórmula',trocar(novo(),vida_max='#REF!'),'vida_max','Erro de leitura claro',reader='erro de fórmula em vida_max')
registrar('duplicada','Chave duplicada',novo(),'vida_max','Duplicata recusada',duplicada=True,reader='chave duplicada na ANALISE: vida_max')
registrar('origem','Origem incompatível',trocar(novo(),origem='Receptáculo',origem__marcante='Conflito',origem__menor_1='Conselho Interior',origem__menor_2='Memória Corporal'),'origem.menor_1','Exige Coexistência; Vida não certificada')

t=trocar(novo(),caminho='Evocador',trilha='Trilha Coruja Avançada B47',vida_max=14,energia_max=12,
         custom__trilha__nome='Trilha Coruja Avançada B47',custom__trilha__mestre_viu=0,
         custom__trilha__campo__caminho='Evocador',custom__trilha__campo__base_do_livro='Invocação Principal',
         morrendo_aguentar=4,morrendo_insistir_1=5,morrendo_insistir_2=7)
entidade(t)
for i,nome in enumerate(('Mira','Área','Alcance','Controle','Auxiliares'),1):trocar(t,**{f'invocacao.1.familia.{i}':nome})
trocar(t,invocacao__1__limite_familias=5,invocacao__1__limite_livres=2)
extra=aprovar(t,'custom.trilha').impressoes
registrar('trilha-pendente','Trilha sem aprovação',copy.deepcopy(t),'custom.trilha','Perfil não certificado antes da aprovação')
registrar('trilha-aprovada','Trilha herdada aprovada',copy.deepcopy(t),'invocacao.1.limite_familias','5 abertas e 2 Livres pela base Principal',aprovacao_extra=extra)
registrar('trilha-alterada','Base de Trilha alterada',trocar(copy.deepcopy(t),custom__trilha__campo__base_do_livro='Parceria'),'custom.trilha','Aprovação reaberta; perfil não presumido',aprovacao_extra=extra)
na=trocar(copy.deepcopy(t),invocacao__1__autonomia='Não autônoma',invocacao__1__limite_familias=6,invocacao__1__limite_livres=3,invocacao__1__familia__6='Castigo')
registrar('nao-autonoma','Trilha e não autônoma',na,'invocacao.1.limite_familias','6 abertas e 3 Livres',aprovacao_extra=extra)

s=novo()
for k,c in CUSTOM.items():
    if k.startswith(('custom.pericia.1.','personagem.pericia_custom.1.')):s[k]=c
trocar(s,personagem__pericia_custom__1__especializacao=1,personagem__pericia_custom__1__treino=1,personagem__pericia_custom__1__resultado=2)
registrar('especializacao','Especialização prematura',s,'personagem.pericia_custom.1.especializacao','Erro: requer nível 10; bônus dependente não certificado')
registrar('efeito-invalido','Efeito com valor inválido',efeito(novo(),'CD de feitiço','inválido'),'efeito.1','Erro da linha; CD não certificada; Vida preservada')
z=efeito(trocar(novo(),cd_de_feitico=0,buff__cd_de_feitico=9),'CD de feitiço',0,'trocar por')
efeito(z,'CD de feitiço',77,i=2,fonte='Outra fonte sintética')
registrar('troca-zero','Troca por zero',z,'cd_de_feitico','CD 0 independe do seletor ausente e sobrepõe Buff/soma')
co=efeito(novo(),'Vida máxima',20,'trocar por');efeito(co,'Vida máxima',20,'trocar por',i=2,fonte='Segunda troca sintética')
registrar('conflito','Duas trocas conflitantes',co,'vida_max','Conflito impede certificar Vida')

cu=novo()
for i,nome in ((1,'Runa*'),(2,'Runas')):
    trocar(cu,**{f'custom.pericia.{i}.{k}':v for k,v in dict(tipo='Perícia',nome=nome,atributo='Inteligência',mestre_viu=0).items()})
    trocar(cu,**{f'personagem.pericia_custom.{i}.{k}':v for k,v in dict(nome=nome,atributo='Inteligência',treino=0,especializacao=0,bonus=0,resultado=1 if i==1 else 8).items()})
efeito(cu,'Perícia · Runas',7)
registrar('curinga-valido','Nomes com curinga literal',copy.deepcopy(cu),'personagem.pericia_custom.1.resultado','Runa* 1 e Runas 8; aprovação continua separada')
registrar('curinga-errado','Efeito cruzado indevido',trocar(cu,personagem__pericia_custom__1__resultado=8),'personagem.pericia_custom.1.resultado','Reprova Runa* 8; esperado 1')

en=entidade(entidade(novo()),2)
registrar('entidades-validas','Duas entidades válidas',copy.deepcopy(en),'invocacao.2.vida.max','Contas independentes nas duas entidades')
trocar(en,invocacao__1__atributo__forca__base=6,invocacao__1__pontos='6 · 2 · 2 · 1 · 1')
registrar('entidades-isoladas','Uma entidade inválida',en,'invocacao.1.pontos','Não certifica 1; preserva Vida 12 da entidade 2')

def controle(pecas='Prende · Precisão',resolve='Ataque +6 · TR CD 14',dano='Sem dano'):
    f=entidade(novo())
    trocar(f,invocacao__1__familia__1='Controle',invocacao__1__familia__2='Mira',invocacao__1__esp__1__nome='Prisão de teste',invocacao__1__esp__1__classe=1,
           invocacao__1__esp__1__forma='Projétil',invocacao__1__esp__1__pecas=pecas,invocacao__1__esp__1__pe='3 PE',
           invocacao__1__esp__1__dano=dano,invocacao__1__esp__1__alcance='18 m, um alvo',invocacao__1__esp__1__resolve=resolve)
    return f
registrar('controle-14','Controle saldo zero correto',controle(),'invocacao.1.esp.1.resolve','CD exclusiva 14 com saldo calculado zero')
registrar('controle-produtor','Controle fórmula conhecida',controle(resolve='Ataque +6 · TR CD 12'),'invocacao.1.esp.1.resolve','Pendência específica da fórmula conhecida; não certifica CD14')
registrar('controle-999','Controle CD adulterada',controle(resolve='Ataque +6 · TR CD 999'),'invocacao.1.esp.1.resolve','CD999 é erro, sem tolerância')
registrar('controle-positivo','Controle com saldo positivo',controle(pecas='Prende',resolve='Ataque +4 · TR CD 14',dano='1d8'),'invocacao.1.esp.1.resolve','Reprova bônus indevido; esperado CD12')

def maxima(forma='Projétil',pecas='Precisão',montagem='1 de 8',dano='24d8 = 108'):
    f=familias(subir(novo(),17),'Mira','Alcance',livre=() if 'Toca a Alma' in pecas else ('Mira',))
    return trocar(f,maxima__nome='Máxima avançada',maxima__forma=forma,maxima__pecas=pecas,maxima__pe=25,maxima__montagem=montagem,maxima__dano=dano)
registrar('maxima-valida','Máxima válida',maxima(),'maxima.montagem','25 PE, 1 de 8 e 24d8')
registrar('maxima-incompativel','Máxima incompatível',maxima(forma='Toque',pecas='Longe',montagem='1 de 8'),'maxima.pecas','Toque com Longe rejeitado; dano não certificado')
registrar('maxima-alma','Máxima com Alma correta',maxima(pecas='Toca a Alma',montagem='3 de 8',dano='12d8 = 54'),'maxima.dano','12d8 conferido; permissão continua humana')
registrar('maxima-produtor','Máxima com fórmula fixa',maxima(pecas='Toca a Alma',montagem='3 de 8'),'maxima.dano','24d8 fixos geram pendência específica')

def objeto(dano='6d8 = 27'):
    f=familias(subir(novo(),10),'Castigo')
    return trocar(f,feitico__1__nome='Demolição avançada',feitico__1__classe=3,feitico__1__forma='Projétil',feitico__1__pecas='Quebra Coisa',feitico__1__pe='9 PE',feitico__1__dano=dano,feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
registrar('objeto-6','Objeto dentro do teto',objeto(),'feitico.1.dano','6d8 dobram a12; conferido')
registrar('objeto-7','Objeto excede teto',objeto('7d8'),'feitico.1.dano','7d8 excedem teto12 após dobrar')
li=objeto()
for sufixo in ('nome','classe','forma','pecas','pe','alcance','resolve','dano'):trocar(li,**{'liberacao.1.'+sufixo:li['feitico.1.'+sufixo].valor})
trocar(li,liberacao__1__pe='14 PE')
registrar('liberacao','Liberação com teto',li,'liberacao.1.dano','Liberação 14PE e 6d8; mesmo teto')

for c in CASOS:
    r=c['resultado']
    print(c['n'],c['slug'],f"{len(r['problemas'])}e/{len(r['pendencias'])}p" if r else 'leitura',
          [(p['campo'],p['esperado'][:110]) for p in r['problemas']] if r else c['reader'])
(OUT/'casos.json').write_text(json.dumps(CASOS,ensure_ascii=False,indent=2)+'\n')
(OUT/'aprovacao-extra.json').write_text(json.dumps(extra,ensure_ascii=False,indent=2)+'\n')

(OUT/'aprovacoes-locais.json').write_text(json.dumps(AP,ensure_ascii=False,indent=2)+'\n')
