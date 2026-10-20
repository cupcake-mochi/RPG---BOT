"""Uma consulta por cidade à Open-Meteo, sem IA, chaves, banco ou Discord."""
import asyncio
import sys
import time
import unicodedata
sys.path.insert(0, 'src')
from closure_bot.clima import ServicoClima, contexto_clima

def normalizar(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn')

CASOS = [
    ('São Paulo', 'São Paulo'), ('rj', 'Rio de Janeiro'), ('Curitiba', 'Curitiba'),
    ('poa', 'Porto Alegre'), ('bsb', 'Brasília'), ('Manaus', 'Manaus'),
    ('Lisboa', 'Lisboa'), ('Tóquio', 'Tóquio'),
]
async def main():
    servico = ServicoClima()
    passou = 0
    for escrito, esperado in CASOS:
        t = time.monotonic()
        linha = await contexto_clima(servico, f'qual o clima atual de {escrito}?')
        ok = bool(linha and normalizar(linha).startswith('[' + normalizar(esperado) + ' agora ('))
        if not ok:
            ok = bool(linha and normalizar(linha).startswith('[' + normalizar(esperado) + ','))
        if ok:
            passou += 1
        print('PASS' if ok else 'FALHA', escrito, '->', esperado, f'{time.monotonic()-t:.3f}s', linha, flush=True)
    print(f'RESULTADO_CIDADES: {passou}/{len(CASOS)}; APIs reais gratuitas; nenhum modelo ou mensagem', flush=True)
    assert passou == len(CASOS)
asyncio.run(main())
