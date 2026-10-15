"""Retomada manual após o único timeout já revisado da bateria mista v10.

Não repete tentativas. Mantém o plano/orçamento original, inclusive a reserva
incerta. Sem --executar só confere a retomada. Não é continuação automática.
"""
import argparse
import asyncio
from dataclasses import asdict
from datetime import datetime
import fcntl
import json

import bateria_mista as b


def conferir():
    p = json.loads((b.PASTA / "plano.json").read_text())
    aprovacao = json.loads((b.RAIZ / "pesquisa/privado/aprovacao-bateria-mista-v10.json").read_text())
    if p != b.plano() or aprovacao["plano_sha256"] != b.digest(p):
        raise ValueError("Plano/runtime diverge do aprovado")
    rs = json.loads((b.PASTA / "respostas.json").read_text())
    falhas = [x for x in rs if x["estado"] != "ok"]
    if len(falhas) != 1 or falhas[0]["id"] != "clo_musica" or falhas[0].get("codigo") != "rede":
        raise ValueError("Esta retomada cobre somente o timeout clo_musica revisado")
    if [r["id"] for r in rs] != [c["id"] for c in p["casos"][:len(rs)]]:
        raise ValueError("Resultados fora da sequência original")
    if any(r["plano_sha256"] != b.digest(p) for r in rs):
        raise ValueError("Resultado de outro plano")
    if (datetime.now(b.FUSO) - datetime.fromisoformat(falhas[0]["quando"])).total_seconds() < 120:
        raise ValueError("Aguardar intervalo de recuperação; nenhuma chamada feita")
    return p, rs


async def continuar(p, rs, modelos):
    for c in p["casos"][len(rs):]:
        q = b.montar(c, rs)
        margem = b.reserva(q["input"])
        if b.gasto(rs) + margem > p["teto_estimado_cheio_usd"]:
            print("Parada preventiva pelo orçamento original.", flush=True)
            return 1
        b.gravar(b.PRIVADO / (c["id"] + ".json"), q)
        item = {**c, "plano_sha256": b.digest(p), "pedido_sha256": b.digest(q["input"]),
                "ativadas": q["ativadas"], "estado": "iniciada", "reserva_usd": margem,
                "quando": datetime.now(b.FUSO).isoformat(), "retomada_revisada": True}
        rs.append(item)
        b.gravar(b.PASTA / "respostas.json", rs)
        try:
            r = await modelos.responder(q["input"], persona=c["pers"], gatilho="bateria_mista_v10", so_pagos=True)
            item.update(asdict(r))
            completo = r.tokens_entrada is not None and r.tokens_saida is not None
            item["reserva_usd"] = 0 if completo else margem
            item["custo_sem_promocao_usd"] = b.custo_usd(b.FLASH, r.tokens_entrada, r.tokens_saida,
                tokens_cache=r.tokens_cache or 0, sem_promocao=True) if completo else None
            item["estado"] = "ok" if completo and not r.cortada and r.modelo == b.FLASH else "invalida"
            b.gravar(b.PASTA / "respostas.json", rs)
            print(f"{len(rs)}/48 {c['id']}: {item['estado']}; acumulado cheio/reserva US$ {b.gasto(rs):.6f}", flush=True)
            if item["estado"] != "ok":
                return 1
        except b.Falhou as e:
            item.update(estado="falhou", codigo=e.codigo)
            if isinstance(e.codigo, int) and 400 <= e.codigo <= 599:
                item["reserva_usd"] = 0
            b.gravar(b.PASTA / "respostas.json", rs)
            print(f"Parada após nova falha {e.codigo}; sem repetição.", flush=True)
            return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--executar", action="store_true")
    args = ap.parse_args()
    with (b.PASTA / ".execucao.lock").open("a") as trava:
        fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
        p, rs = conferir()
        print(f"{len(rs)} tentativas preservadas; até {48-len(rs)} inéditas restantes.", flush=True)
        if not args.executar:
            return 0
        cfg = b.carregar()
        if not cfg.chaves.get("vertex") or not cfg.vertex_projeto:
            raise ValueError("Falta chave/rota global configurada")
        registro = b.Registro(cfg.banco, cfg.chave_do_banco)
        try:
            modelos = b.Modelos([("vertex", b.FLASH)], cfg.chaves, registro, raciocinio="low",
                vertex_projeto=cfg.vertex_projeto, teto_preco="cheio", gasto_externo_usd=cfg.gasto_externo_usd)
            # Exceção já aprovada para esta bateria. A soma local acima inclui
            # as 33 tentativas anteriores; este valor não concede outro US$ 1,20.
            modelos.teto_usd = modelos.gasto_do_mes() + max(0, b.TETO - b.gasto(rs))
            return asyncio.run(continuar(p, rs, modelos))
        finally:
            registro.fechar()


if __name__ == "__main__":
    raise SystemExit(main())
