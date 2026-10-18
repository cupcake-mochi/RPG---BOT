"""Extrai somente dados JSON dos GS entregues; não executa JS, gerador ou rede.

Uso: python ferramentas/auditar_contrato_b47.py /workspace/Ficha---RPG-JJK
"""
import argparse
import csv
import json
import re
from pathlib import Path

FRAGMENTOS = ('Analise.gs', 'AnaliseFontes.gs', 'CriacaoAnalise.gs',
              'ProgressaoAnalise.gs', 'PecasAnalise1.gs', 'PersonagemAnalise.gs', 'EntidadesAnalise.gs')


def extrair(raiz):
    celulas = {}
    for nome in FRAGMENTOS:
        texto = (Path(raiz) / 'apps-script' / nome).read_text(encoding='utf-8')
        inicio = re.search(r'var \w+\s*=\s*\[', texto)
        dados, _ = json.JSONDecoder().raw_decode(texto[inicio.end()-1:])
        for aba in dados:
            if aba['nome'] != 'ANALISE':
                raise ValueError('fragmento de outra aba')
            for linha, coluna, valor, *_ in aba['vals']:
                if (linha, coluna) in celulas and celulas[linha, coluna] != valor:
                    raise ValueError(f'fragmentos divergentes: {linha}, {coluna}')
                celulas[linha, coluna] = valor
    linhas = [[celulas.get((r, c), '') for c in range(1, 5)]
              for r in sorted({r for r, c in celulas}) if r > 1]
    if any(not k or not parte for k, _, _, parte in linhas) or len({r[0] for r in linhas}) != len(linhas):
        raise ValueError('contrato incompleto ou duplicado')
    return linhas


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('produtor', type=Path)
    p.add_argument('--saida', type=Path, default=Path(__file__).resolve().parents[1] / 'src/closure_bot/recursos/b47-campos.tsv')
    args = p.parse_args()
    linhas = extrair(args.produtor)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['chave', 'parte', 'origem', 'booleano'])
        for chave, formula, origem, parte in linhas:
            # Origem é fórmula de um literal nos fragmentos complementares.
            if origem.startswith('="') and origem.endswith('"'):
                origem = origem[2:-1].replace('""', '"')
            w.writerow([chave, parte, origem, int(formula.startswith('=N('))])
    print(f'{len(linhas)} chaves extraídas sem executar o produtor')


if __name__ == '__main__':
    main()
