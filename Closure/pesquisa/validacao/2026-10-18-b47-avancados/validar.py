"""Confere todos os campos salvos e os alvos pelos requisitos do ensaio."""
from pathlib import Path
import sys,json,hashlib,argparse
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--saida',type=Path,required=True)
p.add_argument('--closure',type=Path,default=Path(__file__).resolve().parents[3])
args=p.parse_args()
ROOT=args.closure.resolve()
sys.path.insert(0,str(ROOT/'src'))
from closure_bot.ficha_leitor import de_xlsx, FichaIlegivel, Campo, normaliza
from closure_bot.ficha_corretor import conferir,Aprovados
from testes.test_b47_integracao import REF
DIR=args.saida.resolve()
cs=json.loads((DIR/'casos.json').read_text())
ap=json.loads((DIR/'aprovacoes-locais.json').read_text())
extra=json.loads((DIR/'aprovacao-extra.json').read_text())
evid=[]
for c in cs:
    p=DIR/c['file']
    try:f=de_xlsx(p)
    except FichaIlegivel as e:
        assert c['reader'] and c['reader'] in str(e),(c['slug'],str(e))
        evid.append({'caso':c['n'],'arquivo':c['file'],'passou':True,'diagnostico':str(e),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        continue
    assert not c['reader']
    esperado={k:Campo(normaliza(v,k),cel,parte) for k,v,cel,parte in c['linhas'][1:]}
    assert f==esperado,(c['slug'],[(k,f[k],v) for k,v in esperado.items() if f.get(k)!=v][:4])
    a=dict(ap)
    if c['n'] in (7,8,9):a.update(extra)
    r=conferir(f,REF,aprovados=Aprovados(a))
    assert [vars(p) for p in r.problemas]==c['resultado']['problemas'],c['slug']
    assert [vars(p) for p in r.pendencias]==c['resultado']['pendencias'],c['slug']
    textos=' '.join(r.conferidos)
    erro={p.campo for p in r.problemas};pend={p.campo for p in r.pendencias}
    n=c['n']
    if n==1:assert not r.conferidos and 'efeito.30.valor' in pend
    if n==5:assert 'origem.menor_1' in erro and 'Vida ' not in textos
    if n in (6,8):assert 'custom.trilha.nome' in pend and any('Trilha válida e aprovação' in s for s in r.nao_conferido)
    if n in (7,9):assert not erro and 'custom.trilha.nome' not in pend
    if n==10:assert c['alvo'] in erro and not any('Runologia Coruja B47: bônus' in s for s in r.conferidos)
    if n==11:assert 'efeito.1' in erro and 'Vida 23' in r.conferidos and not any(s.startswith('cd_de_feitico:') for s in r.conferidos)
    if n==12:assert 'cd_de_feitico: 0' in r.conferidos
    if n==13:assert len([p for p in r.problemas if p.campo.endswith('.como')])==2 and not any(s.startswith('Vida ') for s in r.conferidos)
    if n==14:assert not erro
    if n==15:assert c['alvo'] in erro
    if n==16:assert all(f'Invocação {i}: vida.max 12' in r.conferidos for i in (1,2))
    if n==17:assert not any(s.startswith('Invocação 1:') for s in r.conferidos) and 'Invocação 2: vida.max 12' in r.conferidos
    if n==18:assert 'CD exclusiva do Controle 14; saldo calculado 0' in textos
    if n==19:assert c['alvo'] in pend and not any('CD exclusiva do Controle' in s for s in r.conferidos)
    if n in (20,21):assert c['alvo'] in erro
    if n==22:assert not erro and all(s in textos for s in ('Técnica Máxima: PE 25','Técnica Máxima: montagem 1 de 8','Técnica Máxima: 24d8'))
    if n==23:assert c['alvo'] in erro and not any(s.startswith(('Técnica Máxima: montagem','Técnica Máxima: 24d8')) for s in r.conferidos)
    if n==24:assert not erro and 'Técnica Máxima: 12d8' in r.conferidos and any('alma' in s and 'mestre' in s for s in r.nao_conferido)
    if n==25:assert 'maxima.dano' in pend and 'Técnica Máxima: 12d8' not in r.conferidos
    if n==26:assert not erro and 'Feitiço 1: dano-base 6d8' in r.conferidos
    if n==27:assert 'feitico.1.dano' in erro
    if n==28:assert not erro and any('Liberação 1: dano-base 6d8'==s for s in r.conferidos)
    evid.append({'caso':n,'arquivo':c['file'],'passou':True,'chaves':len(f),'campos_identicos':True,'erros':len(r.problemas),'pendencias':len(r.pendencias),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(DIR/'validacao-local.json').write_text(json.dumps(evid,ensure_ascii=False,indent=2)+'\n')
print(f'{len(evid)} arquivos e alvos validados; exportação/duplicatas/cache conferidos, sem modelo.')
