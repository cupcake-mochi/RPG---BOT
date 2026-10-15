"""Bateria mista do prompt real, sem API até receber --executar.

48 tentativas no Flash low, sem repetição/fallback. Aprovação de quantidade e
custo precisa vir do usuário; a opção de execução não é uma aprovação em si.
"""
from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict
from datetime import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "ferramentas/prompt_do_site"))
import site_prompt
from closure_bot.config import carregar
from closure_bot.modelo import FLASH, MAX_SAIDA, Falhou, Modelos, custo_usd
from closure_bot.plantao import FUSO
from closure_bot.registro import Registro
from closure_bot.vida import Estado

PASTA = RAIZ / "pesquisa/validacao/2026-10-15-bateria-mista-v10"
PRIVADO = RAIZ / "pesquisa/privado/bateria-mista-v10"
TETO = 1.20

# Critérios de regra são conferidos contra as entradas do R51. Nos casos
# casuais, a ausência de uma âncora não basta para aprovar a fala: exige leitura.
CASOS = [
    ("armas", "sistema", "Recomende Trilhas para alguém que luta com várias armas diferentes.",
     "Comparar alternativas/condições; Malabarista, Condutor Armado e Parceria disponíveis. Não restringir a uma única Trilha.",
     ["incursor--inc-malabarista", "emanador--ema-condutor", "evocador--ev-parceria"]),
    ("parceria", "sistema", "A Parceria do Evocador dá treino com quais armas e em qual nível?",
     "Treino de Combate de nível 2: escolher uma categoria de armas, não todas.", ["evocador--ev-parceria"]),
    ("reversa", "sistema", "Como funciona Energia Reversa? Pode explicar requisitos, custo e limites?",
     "Entrada inteira pertinente; nível 14/Refino 7/CE3, ação, PE/dados, alvo e restrições. Não confundir com Forma Cura.", ["aptidoes--apt-reversa"]),
    ("cura", "sistema", "Qual o máximo de cura de um feitiço comum de Classe 5? Mostre a conta de alvo único e da Onda.",
     "Orçamento 15; Forma Média 5, saldo/teto 10d8. Onda Pesada 8, saldo útil 7d8 por aliado. Diferenciar dados e máximo rolado.", ["fundamento--pontos", "fundamento--amparoformas"]),
    ("progressao", "sistema", "Qual é a Maestria e o Refino básico no nível 14?",
     "Maestria +2, Refino básico 4; distinguir aumentos adicionais escolhidos.", []),
    ("longe", "sistema", "Quanto custa a Melhoria Longe na Classe 5, com a Família Alcance normal?",
     "Preço Leve, metade da Classe arredondada para cima: 3 pontos.", []),
    ("socorro", "sistema", "No livro, como funciona Socorro?",
     "Usar a entrada Socorro, sem substituí-la pela Trilha Socorrista.", ["dano--socorro"]),
    ("vinculos", "sistema", "Qual a diferença entre Artes do Vínculo e Vínculo?",
     "Distinguir a entrada do Emanador da Trilha do Evocador; não fundir efeitos.", ["emanador--ema-artes", "evocador--ev-vinculo"]),
    ("oi", "conversa", "Oi, {guia}! Tudo bem por aí?",
     "Cumprimento natural na voz da guia, sem inventar atividade, regra ou oferta padronizada.", []),
    ("cafe", "conversa", "Você gosta de café ou prefere outra coisa?",
     "Preferência na voz da personagem, sem recitar lista do card ou puxar RPG.", []),
    ("papo", "conversa", "Consegui terminar um projeto que estava enrolando há semanas.",
     "Responder ao relato sem inventar profissão, pronomes ou detalhes pessoais.", []),
    ("genero", "conversa", "Pode me tratar no feminino. Estou contente por ter passado na prova.",
     "Respeitar tratamento informado e feminino para si; sem inferir história da prova.", []),
    ("escola", "conversa", "Você trabalha na Escola Jujutsu ou faz parte de alguma família desse mundo?",
     "Guia externa ao mundo; não inventar filiação, emprego ou existência dentro da história.", []),
    ("jeito", "conversa", "kkkk tu joga alguma coisa? responde do teu jeito, tô curioso",
     "Voz própria; sem espelhar tu/vc/kkk ou recitar os gostos inteiros.", []),
    ("computador", "ambigua", "Meu sistema operacional travou de novo. Você também perde a paciência com computador?",
     "Conversa sobre computador; não responder regras do sistema de RPG.", []),
    ("energia", "ambigua", "Hoje fiquei sem energia para fazer qualquer coisa. Como você descansa?",
     "Cansaço cotidiano; não explicar PE, Energia Amaldiçoada ou descanso mecânico.", []),
    ("musica", "ambigua", "Essa trilha sonora ficou na minha cabeça. Você ouve música enquanto trabalha?",
     "Música; não recomendar Trilhas de personagem.", []),
    ("defesa", "ambigua", "Saí em defesa de um amigo numa discussão. Você acha que fiz besteira?",
     "Conversa interpessoal; não calcular Defesa ou inventar motivos/culpa.", []),
    ("dominio", "ambigua", "Meu irmão dominou o videogame e não larga o controle. Você dividiria a vez?",
     "Conversa sobre videogame; sem Expansão de Domínio ou Forma Controle.", []),
    ("arquivo", "ambigua", "A integridade do arquivo deu erro e perdi o download. Que saco, né?",
     "Arquivo/download; não explicar barra de Integridade do personagem.", []),
    ("origem1", "dialogo", "O que eu posso criar na Origem?",
     "Permite criar com o mestre marcante e menores compatíveis, referenciando as publicadas e registrando o pacote.", ["origens--legado-criar", "origens--origem-escolhas"]),
    ("origem2", "dialogo", "Tem certeza? Achei que só podia criar a menor e os Legados.",
     "Verificar a fonte e conservar a permissão específica; não concordar com a premissa falsa.", ["origens--legado-criar"]),
    ("origem3", "dialogo", "Então qual é a fonte disso no livro?",
     "Continuar a Origem e indicar Personalizar sua Origem, sem migrar para criação de Domínio/entidades.", ["origens--legado-criar"]),
    ("troca", "dialogo", "Mudando de assunto: essa trilha sonora está ótima. Você gosta de música eletrônica?",
     "Troca explícita para música; não retomar Origem nem Trilha mecânica.", []),
]


def gravar(p, valor):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(valor, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(p)


def digest(valor):
    return hashlib.sha256(json.dumps(valor, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def casos():
    return [dict(id=f"{p}_{id}", pers=p, categoria=cat, mensagem=msg.format(guia=nome),
                 criterio=crit, fontes_esperadas=fontes, hora=hora)
            for id, cat, msg, crit, fontes in CASOS
            for p, nome, hora in (("clo", "Closure", 22), ("kal", "Kal'tsit", 14))]


def montar(caso, resultados):
    hist = []
    if caso["categoria"] == "dialogo":
        for r in resultados:
            if r["pers"] == caso["pers"] and r["categoria"] == "dialogo" and r["estado"] == "ok":
                hist += [{"de": "user", "nome": "Alex", "texto": r["mensagem"]},
                         {"de": "bot", "pers": caso["pers"], "texto": r["texto"]}]
    persona = "closure" if caso["pers"] == "clo" else "kaltsit"
    pron = "ela/dela" if caso["id"].endswith("_genero") else ""
    estado = Estado(persona, datetime(2026, 10, 15, caso["hora"], 10, tzinfo=FUSO),
                    "quieto", 0, "Alex", pron or None, 0, 0, 3, ())
    return site_prompt.montar(caso["pers"], caso["mensagem"], nome="Alex", hora=(caso["hora"], 10),
                             pronomes=pron, turnos=hist, estado=estado.para_a_ponte())


def reserva(entrada):
    # Margem do projeto: um token por byte de texto + saída máxima, preço cheio,
    # sem contar promoção ou cache. Estimativa cautelar, não garantia da fatura.
    return custo_usd(FLASH, sum(len(m["content"].encode()) for m in entrada) + 256,
                     MAX_SAIDA, sem_promocao=True)


def gasto(resultados):
    return sum(max(r.get("custo_sem_promocao_usd") or 0, r.get("reserva_usd") or 0) for r in resultados)


def plano():
    cs = casos()
    nucleohash = hashlib.sha256(site_prompt.nucleo().read_bytes()).hexdigest()
    arquivos = [Path(__file__), RAIZ / "src/closure_bot/modelo.py", RAIZ / "src/closure_bot/vida.py",
                *[RAIZ / "ferramentas/prompt_do_site" / f for f in ("site_prompt.py", "antes.js", "depois.js")]]
    return {"modelo": FLASH, "esforco": "low", "max_output_tokens": MAX_SAIDA,
            "chamadas_maximas": len(cs), "teto_estimado_cheio_usd": TETO,
            "retry": False, "fallback": False, "nucleo_sha256": nucleohash,
            "fontes_sha256": {str(f.relative_to(RAIZ)): hashlib.sha256(f.read_bytes()).hexdigest() for f in arquivos},
            "casos": cs, "nota": "Diálogos usam respostas reais anteriores; casos avulsos começam do zero. Sem chamadas na preparação."}


async def executar(p, modelos, *, pasta=PASTA, privado=PRIVADO):
    saida = pasta / "respostas.json"
    rs = json.loads(saida.read_text()) if saida.exists() else []
    if any(r.get("plano_sha256") != digest(p) for r in rs):
        raise ValueError("Plano mudou; não misturar baterias")
    if any(r["estado"] != "ok" for r in rs):
        raise ValueError("Há tentativa falha/incompleta. Parada; exige revisão, sem repetição automática")
    ids = [r["id"] for r in rs]
    if len(set(ids)) != len(ids) or ids != [c["id"] for c in p["casos"][:len(ids)]]:
        raise ValueError("Resultados fora da sequência aprovada")
    feitas = {r["id"] for r in rs}
    for c in p["casos"]:
        if c["id"] in feitas:
            continue
        if len(rs) >= p["chamadas_maximas"]:
            break
        q = montar(c, rs)
        margem = reserva(q["input"])
        if gasto(rs) + margem > p["teto_estimado_cheio_usd"]:
            print("Parada preventiva pelo teto local da bateria.", flush=True)
            return 1
        # Grava prompt e intenção ANTES de enviar. Interrupção nunca vira
        # autorização para repetir uma tentativa que pode ter sido faturada.
        gravar(privado / (c["id"] + ".json"), q)
        item = {**c, "plano_sha256": digest(p), "pedido_sha256": digest(q["input"]),
                "ativadas": q["ativadas"], "estado": "iniciada", "reserva_usd": margem,
                "quando": datetime.now(FUSO).isoformat()}
        rs.append(item)
        gravar(saida, rs)
        try:
            r = await modelos.responder(q["input"], persona=c["pers"], gatilho="bateria_mista_v10", so_pagos=True)
            item.update(asdict(r))
            completo = r.tokens_entrada is not None and r.tokens_saida is not None
            item["reserva_usd"] = 0 if completo else margem
            item["custo_sem_promocao_usd"] = custo_usd(FLASH, r.tokens_entrada, r.tokens_saida,
                tokens_cache=r.tokens_cache or 0, sem_promocao=True) if completo else None
            item["estado"] = "ok" if completo and not r.cortada and r.modelo == FLASH else "invalida"
            gravar(saida, rs)
            print(f"{len(rs)}/{p['chamadas_maximas']} {c['id']}: {item['estado']}, {r.latencia_ms} ms; acumulado cheio US$ {gasto(rs):.6f}", flush=True)
            if item["estado"] != "ok":
                return 1
        except Falhou as e:
            item.update(estado="falhou", codigo=e.codigo)
            if isinstance(e.codigo, int) and 400 <= e.codigo <= 599:
                item["reserva_usd"] = 0
            gravar(saida, rs)
            print(f"Parada após erro {e.codigo}; sem repetir ou trocar de modelo.", flush=True)
            return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--executar", action="store_true")
    ap.add_argument("--orcamento-extra-aprovado", action="store_true",
                    help="só após aprovação explícita para esta bateria além do teto mensal já ultrapassado")
    args = ap.parse_args()
    p = plano()
    destino = PASTA / "plano.json"
    if destino.exists() and json.loads(destino.read_text()) != p:
        raise ValueError("Plano/prompt mudou: revisar antes de trocar arquivos")
    gravar(destino, p)
    if not args.executar:
        print(f"Preparadas {len(p['casos'])} tentativas; nenhuma API chamada.")
        return 0
    cfg = carregar()
    if not cfg.chaves.get("vertex") or not cfg.vertex_projeto:
        raise ValueError("Bateria requer chave Vertex e rota global do projeto configuradas")
    # O registro permanece no banco compartilhado. Uma exceção aprovada afeta
    # só esta instância; não altera .env nem o teto do bot hospedado.
    registro = Registro(cfg.banco, cfg.chave_do_banco)
    try:
        modelos = Modelos([("vertex", FLASH)], cfg.chaves, registro, raciocinio="low",
            vertex_projeto=cfg.vertex_projeto, teto_preco="cheio", gasto_externo_usd=cfg.gasto_externo_usd,
            teto_usd=cfg.teto_mensal_usd if cfg.teto_mensal_usd is not None else 9)
        if args.orcamento_extra_aprovado:
            modelos.teto_usd = max(modelos.teto_usd, modelos.gasto_do_mes() + TETO)
        PASTA.mkdir(parents=True, exist_ok=True)
        with (PASTA / ".execucao.lock").open("a") as trava:
            fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return asyncio.run(executar(p, modelos))
    finally:
        registro.fechar()


if __name__ == "__main__":
    raise SystemExit(main())
