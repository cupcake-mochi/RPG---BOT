"""Piloto real PT/EN e original/Nova Terra. Sem API até --executar.

Exige aprovação humana de quantidade/custo. Uma tentativa por caso, sem
fallback. O diário é gravado antes do HTTP: retomadas não repetem pedidos.
Usa somente conversas fictícias e não altera o banco/teto da produção.
"""
from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict
import fcntl
import hashlib
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'src'))
from closure_bot.config import carregar
from closure_bot.modelo import FLASH, MAX_SAIDA, Falhou, Modelos, custo_usd
from closure_bot.prompt import montar

MAX_CHAMADAS = 24
TETO = 1.50
PASTA = RAIZ / 'pesquisa/validacao/2026-10-21-publico'


def salvar(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def casos():
    mensagens = {
        'pt-BR': [
            ('conversa', 'Finalmente terminei um projeto que vinha adiando. Como você comemora uma coisa assim?'),
            ('vinculo', 'Você trabalha em Rhodes Island? Como é sua relação com a outra guia?'),
            ('shiki', 'Quem é Shiki em Siracusa? Ele substitui a Signora Sicilia e manda na região inteira?'),
        ],
        'en': [
            ('conversa', 'I finally finished a project I had been putting off. How would you celebrate something like that?'),
            ('vinculo', 'Do you work at Rhodes Island? What is your relationship with the other guide?'),
            ('shiki', 'Who is Shiki in Siracusa? Has he replaced Signora Sicilia and taken over the entire region?'),
        ],
    }
    return [dict(id=f'{persona}_{idioma}_{mundo}_{nome}', persona=persona,
                 idioma=idioma, mundo=mundo, caso=nome, mensagem=msg)
            for mundo in ('original', 'nova-terra') for idioma in mensagens
            for persona in ('kaltsit', 'closure') for nome, msg in mensagens[idioma]]


async def pedidos():
    resultado = []
    for caso in casos():
        estado = {'nova_terra': caso['mundo'] == 'nova-terra', 'idioma': caso['idioma']}
        entrada = await montar(caso['persona'], caso['mensagem'], nome='Alex', pronomes=None,
                               turnos=[], falas_anteriores=[], estado=estado)
        digest = hashlib.sha256(json.dumps(entrada, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        reserva = custo_usd(FLASH, sum(len(m['content'].encode()) for m in entrada) + 256,
                            MAX_SAIDA, sem_promocao=True)
        resultado.append(({**caso, 'pedido_sha256': digest, 'reserva_usd': reserva}, entrada))
    return resultado


async def executar(args):
    PASTA.mkdir(parents=True, exist_ok=True)
    with (PASTA / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plano = await pedidos()
        destino = PASTA / 'resultados.json'
        registros = json.loads(destino.read_text()) if destino.exists() else []
        feitas = {r['id']: r for r in registros}
        print(f'{len(plano)} casos; máximo {MAX_CHAMADAS}; teto US$ {TETO:.2f}; sem repetição/fallback', flush=True)
        documento = {'modelo': FLASH, 'raciocinio': 'low', 'max_chamadas': MAX_CHAMADAS,
                     'teto_cheio_usd': TETO, 'casos': [c for c, _ in plano]}
        arquivo_plano = PASTA / 'plano.json'
        if arquivo_plano.exists() and json.loads(arquivo_plano.read_text()) != documento:
            raise ValueError('Plano já registrado com outras fontes/estado; preservar a evidência e não repetir chamadas')
        if not arquivo_plano.exists():
            salvar(arquivo_plano, documento)
        if not args.executar:
            return 0
        cfg = carregar(args.env)
        modelos = Modelos([('vertex', FLASH)], cfg.chaves, raciocinio='low', teto_usd=TETO,
                          teto_preco='cheio', vertex_projeto=cfg.vertex_projeto)
        for caso, entrada in plano:
            if caso['id'] in feitas:
                if feitas[caso['id']]['pedido_sha256'] != caso['pedido_sha256']:
                    raise ValueError('Fontes mudaram após tentativa; não repetir automaticamente')
                continue
            gasto = sum(r.get('custo_cheio_usd', r['reserva_usd']) for r in registros)
            if len(registros) >= MAX_CHAMADAS or gasto + caso['reserva_usd'] > TETO:
                print('Parada preventiva pelo limite aprovado', flush=True)
                break
            registro = {**caso, 'estado': 'tentativa_registrada'}
            registros.append(registro)
            salvar(destino, registros)
            try:
                resposta = await modelos.responder(entrada, persona=caso['persona'], gatilho='piloto-publico')
            except Falhou as exc:
                registro.update(estado='falha', erro=str(exc)[:250])
                salvar(destino, registros)
                print('Falha; piloto interrompido sem repetição', flush=True)
                return 1
            registro.update(estado='ok', resposta=asdict(resposta))
            if resposta.tokens_entrada is not None and resposta.tokens_saida is not None:
                registro['custo_cheio_usd'] = custo_usd(FLASH, resposta.tokens_entrada, resposta.tokens_saida,
                    tokens_cache=resposta.tokens_cache or 0, sem_promocao=True)
            salvar(destino, registros)
            print(f"{len(registros)}/{len(plano)} {caso['id']}: {resposta.latencia_ms} ms; "
                  f"US$ {sum(r.get('custo_cheio_usd', r['reserva_usd']) for r in registros):.6f}", flush=True)
            if resposta.cortada or resposta.tokens_entrada is None or resposta.tokens_saida is None:
                print('Consumo incompleto ou resposta cortada; interrompido', flush=True)
                return 1
        return 0 if len(registros) == len(plano) and all(r['estado'] == 'ok' for r in registros) else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--executar', action='store_true')
    p.add_argument('--env', type=Path, help='arquivo privado de configuração existente')
    raise SystemExit(asyncio.run(executar(p.parse_args())))
