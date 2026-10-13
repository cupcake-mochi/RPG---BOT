import json,re,sys,os,statistics as st
# uso: python3 nota_closure.py c5 c7 c8   (compara as versões; detalha a última)
D=os.path.dirname(os.path.abspath(__file__)); RAIZ=os.path.join(D,'..','..','..','..','..')
B={m['id']:m for m in json.load(open(f'{D}/bateria_c1.json'))}
card=json.load(open(f'{RAIZ}/dados/personagem/closure/card.json'))['data']
pro=card['extensions']['closure_lab']['termos_proibidos']
exs=[l.split(': ',1)[1] for l in card['mes_example'].split('\n') if l.startswith('{{char}}')]
conversa={1,15,17,18,21,23,24,25,32,37,401,402,403,404,405}
mal={16,34,35,36,38,112,406}
regra={2,3,4,5,6,27,33,102,103,110,111}
mundo=set(B)-conversa-mal-regra
emo=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
sono=re.compile(r'\b(sono|plant[ãa]o|dorm\w*|madrugada|cochil\w*|bocej\w*)',re.I)
puxa_sono={1,25,401,404,36,406}  # msgs que falam de horário, cansaço ou de como ela tá
ris=re.compile(r'\b(ha(ha)+|he(he)+|kk+|rs(rs)*)\b',re.I)
def medir(v,m):
    f=f'{D}/r_{v}_{m}_a.json'
    if not os.path.exists(f): return None
    R=json.load(open(f)); assert len(R)==58 and {r['id'] for r in R}==set(B), (v,m,len(R))
    c=dict(excl=0,excl_conv=0,excl_regra=0,excl_mundo=0,excl_mal=0,dupla=0,emoji=0,proib=0,ris=0,til=0,sono=0,sono_fora=0,sinto=0,nome=0,terceira=0,copia=0,acao=0)
    det=[]
    for r in R:
        t=r['resposta']; i=r['id']
        if '!' in t:
            c['excl']+=1
            for k,s in (('conv',conversa),('regra',regra),('mundo',mundo),('mal',mal)):
                if i in s: c['excl_'+k]+=1
            if i in regra|mundo|mal: det.append((i,'! fora de conversa',t))
        if '!!' in t: c['dupla']+=1; det.append((i,'!!',t))
        if emo.search(t): c['emoji']+=1; det.append((i,'emoji',t))
        if '*' in t: c['acao']+=1; det.append((i,'narra ação',t))
        for x in pro:
            if re.search(r'(?<!\w)'+re.escape(x)+r'(?!\w)',t): c['proib']+=1; det.append((i,'proibido: '+x,t))
        if ris.search(t): c['ris']+=1; det.append((i,'risada',t))
        if '~' in t: c['til']+=1; det.append((i,'~',t))
        if sono.search(t):
            c['sono']+=1
            if i not in puxa_sono: c['sono_fora']+=1; det.append((i,'sono/plantão sem a msg puxar',t))
        if re.match(r'\s*sinto muito',t,re.I): c['sinto']+=1
        if re.search(r'(?<!\w)'+re.escape(B[i]['de'])+r'(?!\w)',t,re.I): c['nome']+=1; det.append((i,'vocativo',t))
        if re.search(r'\ba Closure\b',t): c['terceira']+=1; det.append((i,'3ª pessoa',t))
        for e in exs:
            if len(e)>25 and e[:25].lower() in t.lower(): c['copia']+=1; det.append((i,'cópia de exemplo',t))
    w=[len(r['resposta'].split()) for r in R]
    c['mediana']=st.median(w); c['max']=max(w)
    c['med_conv']=st.median([len(r['resposta'].split()) for r in R if r['id'] in conversa])
    return c,det,{r['id']:r['resposta'] for r in R}
if __name__=='__main__':
    vs=sys.argv[1:]
    res={}
    for v in vs:
        for m in ('haiku','sonnet'):
            x=medir(v,m)
            if x: res[(v,m)]=x
    ks=['excl','excl_conv','excl_regra','excl_mundo','excl_mal','dupla','emoji','acao','proib','ris','til','sono','sono_fora','sinto','nome','terceira','copia','mediana','med_conv','max']
    print('medida'.ljust(12)+''.join(f'{v[1:]}{m[0].upper()}'.rjust(7) for v,m in res))
    for k in ks: print(k.ljust(12)+''.join(str(res[x][0][k]).rjust(7) for x in res))
    print(f'\n(conversa={len(conversa)} regra={len(regra)} mundo={len(mundo)} mal={len(mal)})')
    for x in res:
        if x[0]==vs[-1]:
            print(f'\n--- ocorrências {x} ---')
            for i,k,t in res[x][1]: print(i,'|',k,'|',t[:230])
