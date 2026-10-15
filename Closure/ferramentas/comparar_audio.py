"""Compara a melhoria de áudio v17 com a orientação anterior, sob o contexto comum da v20."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import bateria_audio_v17 as anterior
import bateria_midia as base
from closure_bot.config import carregar
from closure_bot.conteudo_adulto import aplicar
from closure_bot.modelo import FLASH, Modelos
from closure_bot.registro import Registro

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / 'pesquisa/validacao/2026-10-15-audio-comparacao-v20'
TETO = 1.50


async def preparar():
    salvo = json.loads((anterior.PASTA / 'plano.json').read_text())
    originais = {c['id']: c for c in salvo['casos']}
    plano, pedidos = await anterior.preparar()
    assert len(pedidos) == len(plano['casos']) == 24
    pares = []
    registro = Registro(':memory:')
    try:
        for i in range(0, len(plano['casos']), 2):
            par = plano['casos'][i:i + 2]
            assert [c['variante'] for c in par] == ['v16', 'v17']
            a, b = (pedidos[c['id']] for c in par)
            assert a[-1]['midias'] == b[-1]['midias']
            for c in par:
                # A preparação do áudio e os pedidos propostos em v17 não mudaram;
                # hashes do código podem mudar por funções de imagem que não entram aqui.
                assert c['arquivo_sha256'] == originais[c['id']]['arquivo_sha256']
                assert c['pedido_sha256'] == originais[c['id']]['pedido_sha256']
                aplicar(pedidos[c['id']], SimpleNamespace(guild=None), registro)
                c['pedido_sha256'] = base.digest(pedidos[c['id']])
                c['reserva_cheia_usd'] = base.reserva(pedidos[c['id']])
            # Seis pares começam pela orientação antiga e seis pela nova.
            pares.extend(par if (i // 2) % 2 == 0 else reversed(par))
    finally:
        registro.fechar()
    arquivos = list(plano['fontes_sha256']) + [
        'ferramentas/comparar_audio.py', 'src/closure_bot/conteudo_adulto.py',
        'dados/personagem/kaltsit/card.json', 'dados/personagem/closure/card.json',
    ]
    plano.update(casos=pares, teto_cheio_usd=TETO,
                 comparacao='orientação/nota v16 contra orientação/medidas v17; contexto comum v20',
                 ordem='pares consecutivos; ordem de variante alternada por par',
                 fontes_sha256={n: hashlib.sha256((RAIZ / n).read_bytes()).hexdigest() for n in arquivos})
    assert sum(c['reserva_cheia_usd'] for c in pares) <= TETO
    return plano, pedidos


async def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--executar', action='store_true')
    ap.add_argument('--orcamento-extra-aprovado', action='store_true')
    args = ap.parse_args()
    plano, pedidos = await preparar()
    destino = PASTA / 'plano.json'
    if destino.exists() and json.loads(destino.read_text()) != plano:
        raise ValueError('Plano alterado; revisão necessária antes de substituir')
    base.gravar(destino, plano)
    base.gravar(PASTA / 'prompts.json', {
        k: [{kk: vv for kk, vv in m.items() if kk != 'midias'} for m in v] for k, v in pedidos.items()
    })
    print(f"24 pedidos conferidos; reservas cheias US$ {sum(c['reserva_cheia_usd'] for c in plano['casos']):.6f}.", flush=True)
    if not args.executar:
        return 0
    if not args.orcamento_extra_aprovado:
        raise ValueError('Exige aprovação de 24 chamadas e teto extra de US$ 1,50')
    recibo = json.loads((RAIZ / 'pesquisa/privado/aprovacao-audio-comparacao-v20.json').read_text())
    if recibo.get('chamadas') != 24 or recibo.get('teto_cheio_usd') != TETO or not recibo.get('aprovado'):
        raise ValueError('Aprovação incompatível')
    cfg = carregar()
    if not cfg.chaves.get('vertex') or not cfg.vertex_projeto:
        raise ValueError('Falta rota global Vertex')
    registro = Registro(cfg.banco, cfg.chave_do_banco)
    try:
        modelos = Modelos([('vertex', FLASH)], cfg.chaves, registro, raciocinio='low',
                          vertex_projeto=cfg.vertex_projeto, teto_preco='cheio',
                          gasto_externo_usd=cfg.gasto_externo_usd)
        # Limite só deste processo de avaliação; não grava configuração de hospedagem.
        modelos.teto_usd = max(modelos.teto_usd, modelos.gasto_do_mes() + TETO)
        with (PASTA / '.execucao.lock').open('a') as trava:
            fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return await base.executar(plano, pedidos, modelos, PASTA, gatilho='bateria_audio_comparacao_v20')
    finally:
        registro.fechar()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
