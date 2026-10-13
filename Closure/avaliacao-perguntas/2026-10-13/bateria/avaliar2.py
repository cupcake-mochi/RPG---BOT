import signal; signal.signal(signal.SIGPIPE, signal.SIG_DFL)
import json,sys
B={q['id']:q for q in json.load(open(sys.argv[1]))}
for arq in sys.argv[2:]:
    O=json.load(open(arq)); ok=tot=fp=nn=0; ruins=[]
    for o in O:
        q=B[o['id']]; c=o['input'][-1]['content']
        anc=[m.split(']')[0] for m in c.split('[Livro, âncora ')[1:]]
        if q['gold']=='nenhum':
            nn+=1
            if anc: fp+=1; ruins.append(('FP',o['id'],q['msg'],anc))
        elif q['gold']:
            tot+=1; hit=any(g in anc for g in q['gold']); ok+=hit
            if not hit: ruins.append(('XX',o['id'],q['msg'],anc))
    print(arq.split('/')[-1], f'acerto {ok}/{tot}; livro em conversa comum {fp}/{nn}')
    for r in ruins: print('   ',*r)
