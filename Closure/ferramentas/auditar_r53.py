"""Confere a migração integral R52/R53 contra o registro do produtor, sem rede."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]
FONTE = Path('sistema/05-material/livro/ciclo-maldito-r41')


def blocos(path):
    return {b['ancora']: b for b in map(json.loads, path.read_text(encoding='utf-8').splitlines())}


def normalizar(texto, capitulo):
    texto = re.sub(r'<!--.*?-->', '', texto or '', flags=re.S).strip()
    # O registro editorial usa títulos relativos; o livro os hierarquiza.
    texto = re.sub(r'(?m)^#+ ', '# ', texto)
    # O parser guarda a abertura do capítulo em capitulo_titulo, fora do bloco.
    prefixo = '# ' + capitulo + '\n\n'
    return texto[len(prefixo):] if texto.startswith(prefixo) else texto


def auditar(antes, depois, alteracoes):
    modificadas = {k for k in antes.keys() | depois.keys()
                   if antes.get(k, {}).get('texto') != depois.get(k, {}).get('texto')}
    registros = []
    for item in alteracoes:
        k = item['bloco']
        capitulo = depois.get(k, antes.get(k, {})).get('capitulo_titulo', '')
        a, b = antes.get(k, {}).get('texto', ''), depois.get(k, {}).get('texto', '')
        registros.append(dict(id=item['id'], ancora=k, capitulo=capitulo,
            tipo='adicionado' if k not in antes else 'removido' if k not in depois else 'modificado',
            antes_confere=normalizar(a, capitulo) == normalizar(item['antes'], capitulo),
            depois_confere=normalizar(b, capitulo) == normalizar(item['depois'], capitulo),
            antes_sha256=hashlib.sha256(a.encode()).hexdigest(),
            depois_sha256=hashlib.sha256(b.encode()).hexdigest()))
    identificadas = [r['ancora'] for r in registros]
    return dict(blocos_antes=len(antes), blocos_depois=len(depois), alteracoes=len(registros),
        registro_oficial_confere=all(r['antes_confere'] and r['depois_confere'] for r in registros),
        sem_alteracoes_fora_do_registro=modificadas == set(identificadas),
        sem_duplicatas=len(identificadas) == len(set(identificadas)),
        por_capitulo=dict(Counter(r['capitulo'] for r in registros)), blocos=registros)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--saida', required=True, type=Path)
    args = p.parse_args()
    fonte = args.repo / FONTE
    manifesto = json.loads((RAIZ / 'dados/sistema/MANIFESTO.json').read_text())
    alteracoes = json.loads((fonte / 'revisao-de-regras/alteracoes/R52-para-R53.json').read_text())
    r = auditar(blocos(RAIZ / 'dados/sistema/legado-r52.jsonl'),
                blocos(RAIZ / 'dados/sistema/livro.jsonl'), alteracoes)
    r.update(fonte='cupcake-mochi/JJK---Project@' + manifesto['commit'], edicao=manifesto['edicao_livro'],
             livro_completo_sha256=hashlib.sha256((fonte / 'LIVRO-COMPLETO.md').read_bytes()).hexdigest(),
             escopo='Texto por âncora; somente cabeçalhos relativos, títulos de capítulo e comentários HTML normalizados. Não certifica respostas do modelo.')
    r['fonte_integral_confere'] = r['livro_completo_sha256'] == manifesto['texto_sha256']
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    ok = all(r[k] for k in ('registro_oficial_confere', 'sem_alteracoes_fora_do_registro', 'sem_duplicatas', 'fonte_integral_confere'))
    print(f"{r['alteracoes']} alterações; corpus {r['blocos_antes']} → {r['blocos_depois']}; confere: {ok}")
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
