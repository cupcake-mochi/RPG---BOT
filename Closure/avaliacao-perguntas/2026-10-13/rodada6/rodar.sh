# uso: bash rodar.sh PAGINA_ATUAL.html   (de dentro de "Closure Lab/Closure")
set -e
A=avaliacao-perguntas/2026-10-13; B2=$A/rodada2/bateria; T=$(mktemp -d)
python3 $A/rodada6/proposta/aplicar6.py "$1" $T/v4.html >/dev/null
for p in atual v6; do f=$1; [ $p = v6 ] && f=$T/v4.html; printf "%-6s" $p
  for b in $A/bateria/bateria.json $B2/holdout.json $A/bateria/holdout2.json $A/bateria/holdout3.json $A/bateria/holdout4.json $A/bateria/holdout5.json $B2/buracos.json $B2/buracos_rodada10.json $B2/conversa_rodada11.json $B2/conversa_rodada12.json $B2/conversa_rodada13.json; do
    node $A/bateria/montar.js $f $b $T/o.json kal 14 >/dev/null; python3 $A/bateria/avaliar2.py $b $T/o.json | head -1 | sed -E "s#o.json acerto#$(basename $b .json)#; s/livro em conversa comum/papo/" | tr '\n' ' '; done
  node $A/bateria/montar.js $f $B2/conversas.json $T/c.json kal 14 >/dev/null
  python3 - $B2/conversas.json $T/c.json <<'PY'
import json,sys
B={q['id']:q for q in json.load(open(sys.argv[1]))}; O=json.load(open(sys.argv[2]))
tem=lambda o:'[Livro, âncora' in o['input'][-1]['content']
c=[o for o in O if B[o['id']]['lab']=='C']; r=[o for o in O if B[o['id']]['lab']=='R']
print(f'| conversas: papo com livro {sum(map(tem,c))}/{len(c)}, regra com livro {sum(map(tem,r))}/{len(r)}')
PY
done
