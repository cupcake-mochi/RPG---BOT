"""Confere recuperação das tabelas de preço por item, sem rede ou modelo.

Exclui exemplos de compras em conjunto e nomes repetidos; a auditoria verifica
fontes e linhas literais, não cálculos nem a qualidade da resposta gerada.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'ferramentas/prompt_do_site'))
import site_prompt


def itens():
    encontrados = []
    for b in map(json.loads, (RAIZ / 'dados/sistema/livro.jsonl').read_text().splitlines()):
        if not b['ancora'].startswith('equip--') or b['ancora'] == 'equip--eqc-inicial':
            continue
        preco = False
        for linha in b['texto'].splitlines():
            if not linha.startswith('|'):
                preco = False
                continue
            celulas = linha.split('|')[1:-1]
            if any('Preço' in c for c in celulas):
                preco = True
                continue
            if not preco or re.match(r'^\|\s*:?-', linha):
                continue
            nome = re.sub(r'\([^)]*\)|[*`]', '', celulas[0]).strip()
            if nome:
                encontrados.append({'item': nome, 'esperada': b['ancora'], 'linha': linha})
    contagem = Counter(x['item'].casefold() for x in encontrados)
    return [x for x in encontrados if contagem[x['item'].casefold()] == 1]


def auditar():
    resultados = []
    for item in itens():
        for tipo, msg in (
            ('direta', f'Quanto custa {item["item"]} no livro?'),
            ('mista', f'A gente estava falando de música e antes eu estava ouvindo Skyfall, mas por sinal, tinha pedido o valor de {item["item"]} no livro, quanto está?'),
        ):
            pedido = site_prompt.montar('kal', msg, nome='Alex', hora=(14, 0))
            contexto = pedido['input'][-1]['content'].split('[Mensagem]', 1)[0]
            fontes = re.findall(r'\[Livro, âncora ([^\]]+)\]', contexto)
            resultados.append({**item, 'tipo': tipo, 'pergunta': msg, 'fontes': fontes,
                               'achou': item['esperada'] in fontes and item['linha'] in contexto})
    return {'escopo': 'fontes e linhas de preços únicos; sem modelo ou rede', 'total': len(resultados),
            'passaram': sum(x['achou'] for x in resultados), 'casos': resultados}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--saida', type=Path, required=True)
    args = p.parse_args()
    r = auditar()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n')
    print(f'{r["passaram"]}/{r["total"]} consultas com fonte e linha esperadas')
    for c in r['casos']:
        if not c['achou']:
            print(c['tipo'], c['item'], '->', c['fontes'])
    sys.exit(int(r['passaram'] != r['total']))
