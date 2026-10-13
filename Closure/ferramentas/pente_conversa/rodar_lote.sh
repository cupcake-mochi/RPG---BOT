#!/bin/bash
# roda as conversas de um braço: rodar_lote.sh <saida> <sis_clo> <lem_clo> <sis_kal> <lem_kal> [--aviso-antigo]
cd "$(dirname "$0")"; S=$1; mkdir -p "$S"
for f in testador seco papo fora mal novato; do
  for p in clo kal; do
    if [ $p = clo ]; then sis=$2; lem=$3; else sis=$4; lem=$5; fi
    o="$S/${p}_${f}_s1.json"
    if [ -f "$o" ] && python3 -c "import json,sys;sys.exit(0 if len(json.load(open('$o'))['turnos'])>=20 else 1)"; then continue; fi
    rm -f "$o"
    python3 simular.py --pers $p --sistema $sis --lembrete $lem --ficha $f --turnos 20 --saida "$S" $6 > "$S/${p}_${f}.log" 2>&1 || echo "FALHOU $p $f" >> "$S/falhas.txt"
  done
done
echo FIM >> "$S/falhas.txt"
