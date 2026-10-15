"""Números da entidade a partir de entradas individuais da ANALISE 2, pelo R51."""
import math

from .ficha_magia import inteiro, rotulo, valor

ATRIBUTOS = ("forca", "destreza", "constituicao", "inteligencia", "essencia")
NOMES = ("Força", "Destreza", "Constituição", "Inteligência", "Essência")


def conferir_numeros(ficha, magia, base, nivel, r, equipamento=None, catalogo=None):
    from .ficha_corretor import Problema
    from .ficha_equipamento import conferir_uso, ataques_armados, numero, vazio
    nome = rotulo(base)
    chaves = [base + f".atributo.{a}.{p}" for a in ATRIBUTOS for p in ("base", "buff", "total")]
    chaves += [base + ".buff." + c for c in ("vida", "defesa", "acerto", "cd", "deslocamento")]
    chaves += [base + ".equipamento." + str(i) for i in range(1, 4)]
    if not all(k in ficha for k in chaves):
        r.nao_conferido.append(f"{nome}: vida, Defesa, acerto, CD e movimento dependem de entradas da ANALISE 2")
        return

    def erro(k, esperado, ancora="construcao--entidades-atributos"):
        r.problemas.append(Problema("conta", k, str(esperado), str(valor(ficha, k)), ancora))

    def comparar(k, esperado, ancora="construcao--entidades-atributos"):
        if not numero(valor(ficha, k)) or valor(ficha, k) != esperado:
            erro(k, esperado, ancora)
        else:
            r.conferidos.append(f"{nome}: {k.removeprefix(base + '.') } {esperado}")

    def buff(k):
        v = valor(ficha, k)
        if v == "":
            return 0
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
            erro(k, "ajuste numérico finito")
            return None
        if v:
            r.notas.append(Problema("buff", k, "ajuste informado; confirmar com o mestre", str(v)))
        return v

    ajustes = {k: buff(k) for k in chaves if ".buff" in k}
    pontos = {a: valor(ficha, base + f".atributo.{a}.base") for a in ATRIBUTOS}
    for a, v in pontos.items():
        if not inteiro(v, 0, 6):
            erro(base + f".atributo.{a}.base", "inteiro de 0 a 6")
    if any(v is None for v in ajustes.values()) or any(not inteiro(v, 0, 6) for v in pontos.values()):
        r.nao_conferido.append(f"{nome}: números não certificados com atributos ou ajustes inválidos")
        return
    # Distribuição alcançável: os pontos acima de 3 precisam caber nos marcos.
    marcos = sum(n <= nivel for n in (6, 10, 14, 18, 22, 26, 30))
    if sum(pontos.values()) > 9 + marcos:
        erro(base + ".pontos", f"até {9 + marcos} pontos distribuídos")
    if sum(max(0, v - 3) for v in pontos.values()) > marcos:
        erro(base + ".pontos", "aumentos acima de 3 limitados aos marcos alcançados")
    if base + ".pontos" in ficha and str(valor(ficha, base + ".pontos")) != " · ".join(str(v) for v in pontos.values()):
        erro(base + ".pontos", "a mesma distribuição das cinco entradas individuais")
    totais = {a: v + ajustes[base + f".atributo.{a}.buff"] for a, v in pontos.items()}
    for a, v in totais.items():
        comparar(base + f".atributo.{a}.total", v)
    con, des = totais["constituicao"], totais["destreza"]
    crescimento = 4 if valor(ficha, base + ".tipo") == "Corpo amaldiçoado de criação" else 3
    comparar(base + ".vida.max", 5 + con + (crescimento + con) * (nivel - 1) + ajustes[base + ".buff.vida"],
             "construcao--entidades-vida-defesa")

    principal, secundaria, vestindo = [valor(ficha, base + ".equipamento." + str(i)) for i in range(1, 4)]
    uniformes, escudos, duas_maos = equipamento or ({}, {}, set())
    arma = catalogo.pecas.get(principal) if catalogo else None
    arma = arma if arma and arma.tipo == "arma" else None
    if ((not vazio(vestindo) and vestindo not in uniformes)
            or (not vazio(secundaria) and secundaria not in escudos and (catalogo is None or secundaria not in catalogo.pecas))
            or not vazio(principal) and not arma and principal not in duas_maos):
        r.nao_conferido.append(f"{nome}: Defesa depende de equipamento sem conta reconhecida")
    else:
        uniforme = uniformes.get(vestindo)
        escudo = escudos.get(secundaria) if principal not in duas_maos else None
        if uniforme:
            protecao = uniforme.protecao
            dex = min(des, uniforme.teto_destreza) if uniforme.teto_destreza is not None else des
        else:
            dono_atr = valor(ficha, "invocacoes.defesa_atributo")
            chave = {"Essência": "essencia", "Inteligência": "inteligencia"}.get(dono_atr)
            partes = [valor(ficha, f"atributo.{chave}.base"), valor(ficha, f"atributo.{chave}.corpo")] if chave else []
            if not partes or not numero(partes[0]) or partes[1] != "" and not numero(partes[1]):
                protecao = None
                r.nao_conferido.append(f"{nome}: falta atributo escolhido e válido do invocador para a Defesa")
            else:
                protecao = math.floor((partes[0] + (partes[1] or 0)) / 2)
            dex = des
        if protecao is not None:
            dex = min(dex, escudo.teto_destreza) if escudo and escudo.teto_destreza is not None else dex
            comparar(base + ".defesa", 10 + dex + protecao + (escudo.protecao if escudo else 0) + ajustes[base + ".buff.defesa"],
                     "construcao--entidades-vida-defesa")
    acerto = valor(ficha, base + ".atributo_acerto")
    dono = valor(ficha, "nivel")
    if acerto not in NOMES or dono not in magia.maestria:
        r.nao_conferido.append(f"{nome}: falta atributo de acerto ou nível válido do invocador")
    else:
        at = totais[ATRIBUTOS[NOMES.index(acerto)]] + magia.maestria[dono]
        comparar(base + ".cd", 8 + at + ajustes[base + ".buff.cd"])
        if arma and arma.maos:
            opcoes = ataques_armados(arma, totais, magia.maestria[dono], ajustes[base + ".buff.acerto"])
            achado = valor(ficha, base + ".acerto")
            if numero(achado) and achado in opcoes:
                r.conferidos.append(f"{nome}: acerto armado {achado:g} (desvantagem por falta de treino)")
                if len(opcoes) > 1:
                    r.nao_conferido.append(f"{nome}: acerto compatível com a arma; escolha de Fineza/corpo a corpo/arremesso deve estar registrada")
            else:
                p = Problema("conta", base + ".acerto", " ou ".join(f"{n:g}" for n in sorted(opcoes)) +
                             "; atributo da arma, com desvantagem", str(achado), "construcao--entidades-atributos")
                # A fórmula atual exporta o atributo escolhido da entidade mesmo com arma.
                (r.pendencias if numero(achado) and achado == at + ajustes[base + ".buff.acerto"] else r.problemas).append(p)
            r.pendencias.append(Problema("equipamento", base + ".equipamento.1",
                "ataques com arma têm desvantagem: a entidade não recebe treino", str(principal), "construcao--entidades-atributos"))
        elif not vazio(principal):
            r.nao_conferido.append(f"{nome}: ataque armado depende do atributo e requisitos da arma")
        else:
            comparar(base + ".acerto", at + ajustes[base + ".buff.acerto"])
    # O resultado de deslocamento exportado é a base, não o ajuste de carga em campo.
    comparar(base + ".deslocamento", 9 + ajustes[base + ".buff.deslocamento"], "construcao--entidades-definicao")
    conferir_uso(ficha, catalogo, r, base=base, atributos=totais)
    r.nao_conferido.append(f"{nome}: perícias e TR aguardam a próxima etapa")
