import json,re,sys,os,collections
v=sys.argv[1]
bf=f'bateria_{v}.json' if os.path.exists(f'bateria_{v}.json') else 'bateria_v6.json'
b={x['id']:x for x in json.load(open(bf))}
pro=json.load(open("/mnt/project-files/Closure Lab/Closure/dados/personagem/kaltsit/card.json"))['data']['extensions']['closure_lab']['termos_proibidos']
card=json.load(open("/mnt/project-files/Closure Lab/Closure/dados/personagem/kaltsit/card.json"))['data']['mes_example']
exs=[l.split(': ',1)[1] for l in card.split('\n') if l.startswith('{{char}}')]
emo=re.compile('[\U0001F300-\U0001FAFF☀-➿]')
gen=re.compile(r'\b(sozinh[oa]|cansad[oa]|obrigad[oa]|preocupad[oa]|pront[oa]|bem-vind[oa]|nov[oa] aqui)\b',re.I)
mestre_ok={13,14,12,30,36,39,40}
tot=collections.Counter(); falhas=[]
for m in ['haiku','sonnet']:
    R=[]
    for p in 'ab':
        f=f'r_{v}_{m}_{p}.json'
        if os.path.exists(f): R+=json.load(open(f))
    C=json.load(open(f'c_{v}_{m}.json')) if os.path.exists(f'c_{v}_{m}.json') else []
    n=len(R); c=collections.Counter()
    for r in R:
        t=r['resposta']; i=r['id']; w=len(t.split())
        def F(k,why): c[k]+=1; falhas.append((m,i,k,why,t))
        if '!' in t or emo.search(t) or '*' in t: F('formato','!/emoji/*')
        for x in pro:
            if re.search(r'(?<!\w)'+re.escape(x)+r'(?!\w)',t): F('proibido',x)
        if b[i]['de'].lower() in t.lower(): F('nome','vocativo')
        if 'mestre' in t.lower() and i not in mestre_ok: F('mestre','fora de decisão de mesa')
        if re.search(r'(me diga o que|o que mais|posso ajudar|precisa de algo|precisa de alguma|se tiver (uma )?dúvida|, faça\.|me pergunte)',t,re.I): F('fecho','oferece ajuda')
        g=gen.findall(t)
        if g: F('genero',','.join(g))
        if i in (1,23,32) and (re.search(r'obrigad|e você|como você',t,re.I) or w>8): F('cumprimento','quente/longo')
        lim=60 if i in (22,) else 50
        if i==16 and 'mestre' in t.lower(): F('triste','empurra pro mestre')
        if w>lim: F('tamanho',f'{w} palavras')
        if re.match(r'\s*não há registro',t,re.I): c['abre_nao_ha_registro']+=1
        for e in exs:
            if len(e)>25 and e[:25].lower() in t.lower(): F('copia','exemplo')
    ws=sorted(len(r['resposta'].split()) for r in R)
    cw=[len(r['resposta'].split()) for r in C]
    print(f"== {m}: {n} respostas, mediana {ws[n//2] if n else '-'} palavras, máx {ws[-1] if n else '-'} | conversa {len(C)} turnos, máx {max(cw) if cw else '-'} palavras")
    print('   ',dict(c))
    for r in C:
        t=r['resposta']
        if '!' in t or emo.search(t) or '*' in t or any(re.search(r'(?<!\w)'+re.escape(x)+r'(?!\w)',t) for x in pro) or gen.search(t) or len(t.split())>60:
            falhas.append((m,'conv'+str(r['turno']),'conversa','',t))
print('\nFALHAS:')
for f in falhas: print(f[0],f[1],f[2],f[3],'|',f[4][:160])
