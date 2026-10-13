# uso: bash rodar.sh PAGINA_ATUAL.html   (roda de dentro de "Closure Lab/Closure")
set -e
A=avaliacao-perguntas/2026-10-13; B=$A/rodada2/bateria; T=$(mktemp -d)
python3 $A/rodada2/proposta/aplicar3.py "$1" $T/v3.html >/dev/null
for p in atual v3; do f=$1; [ $p = v3 ] && f=$T/v3.html; printf "%-6s" $p
  for b in $A/bateria/bateria.json $B/holdout.json $B/buracos.json; do node $A/bateria/montar.js $f $b $T/o.json kal 14 >/dev/null; python3 $A/bateria/avaliar2.py $b $T/o.json | head -1 | tr '\n' ' '; done
  node $A/bateria/montar.js $f $B/conversas.json $T/c.json kal 14 >/dev/null
  python3 - $B/conversas.json $T/c.json <<'PY'
import json,sys
B={q['id']:q for q in json.load(open(sys.argv[1]))}; O=json.load(open(sys.argv[2]))
tem=lambda o:'[Livro, âncora' in o['input'][-1]['content']
c=[o for o in O if B[o['id']]['lab']=='C']; r=[o for o in O if B[o['id']]['lab']=='R']
print(f'| papo comum com livro {sum(map(tem,c))}/{len(c)} | regra com livro {sum(map(tem,r))}/{len(r)}')
PY
done
