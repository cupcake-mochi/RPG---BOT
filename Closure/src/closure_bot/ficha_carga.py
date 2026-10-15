"""Carga da ANALISE 4: catálogo prevalece, entradas livres exigem revisão.

Os totais da ficha nunca fornecem uma quantidade ou um Volume que não foi exportado.
"""
from decimal import Decimal
import re

from .ficha_equipamento import numero, vazio
from .ficha_magia import valor, bases, inteiro


def conferir_carga(ficha, ref, r):
    if valor(ficha, "formato.versao") != 4 or ref.equipamento is None:
        return
    _conferir(ficha, ref, r)
    for base in bases(ficha, r"invocacao\.\d+"):
        if valor(ficha, base + ".nome"):
            _conferir(ficha, ref, r, base)


def _conferir(ficha, ref, r, base=""):
    from .ficha_corretor import Problema
    from .ficha_repertorio import origem
    prefixo = base + "." if base else ""
    nome = base.replace("invocacao.", "Invocação ") if base else "Carga pessoal"
    ancora = "campo--inv-carga" if base else "geral--carga"
    total_k, limite_k = prefixo + "carga.total", prefixo + "carga.limite"
    obrigatorias = {total_k, limite_k, prefixo + "atributo.forca.base",
                    prefixo + ("atributo.forca.buff" if base else "atributo.forca.corpo")}
    if base:
        obrigatorias |= {prefixo + f"equipamento.{i}" for i in range(1, 4)}
        obrigatorias |= {prefixo + f"carga.item.{i}.{k}" for i in range(1, 7) for k in ("nome", "volume")}
    else:
        obrigatorias |= {f"equipavel.{i}.{k}" for i in range(1, 9) for k in ("nome", "quantidade", "volume")}
        obrigatorias |= {f"item.{i}.{k}" for i in range(1, 13) for k in ("nome", "quantidade", "volume")}
        obrigatorias |= {"carga.ajuste_limite", "em_uso.vestindo"}
    if not obrigatorias <= ficha.keys():
        r.nao_conferido.append(f"{nome}: faltam posições/quantidades/Volumes/ajuste para conferir a carga completa")
        return

    def alerta(k, esperado, pendente=False):
        (r.pendencias if pendente else r.problemas).append(Problema("carga", k, esperado, str(valor(ficha, k)), ancora))

    def decimal(k, *, vazio_zero=False, quantidade=False):
        v = valor(ficha, k)
        if v == "" and vazio_zero:
            return Decimal(0)
        if v == "" and quantidade:
            return Decimal(1)
        if not numero(v) or (not k.endswith((".buff", ".corpo", "ajuste_limite")) and v < 0):
            alerta(k, "número finito" + (" não negativo" if not k.endswith((".buff", ".corpo", "ajuste_limite")) else ""), v == "")
            return None
        return Decimal(str(v))

    inicio = len(r.problemas)
    completo, livre = True, False
    soma = legado = Decimal(0)

    def comparar(k, esperado, antigo=None):
        v = valor(ficha, k)
        n = Decimal(str(v)) if numero(v) else None
        if n == esperado:
            return True
        if antigo is not None and n == antigo:
            alerta(k, f"valor do livro {esperado}; a fórmula antiga mostra {antigo}. Conferir a origem dos ajustes antes de alterar", True)
        else:
            alerta(k, f"Volume {esperado}")
        return False

    def declarado(k):
        nonlocal livre
        n = decimal(k)
        if n is not None:
            livre = True
            r.notas.append(Problema("carga", k, "confirmar com o mestre o Volume declarado", str(n), ancora))
        return n

    if base:
        for i in range(1, 4):
            k = prefixo + f"equipamento.{i}"
            n = valor(ficha, k)
            if vazio(n):
                continue
            e = ref.equipamento.pecas.get(n)
            if e is None:
                completo = False
                r.nao_conferido.append(f"{nome}: Volume de equipamento próprio/desconhecido ({n}) não exportado")
            else:
                soma += e.volume
                legado += e.volume
        for i in range(1, 7):
            k = prefixo + f"carga.item.{i}"
            n, v = valor(ficha, k + ".nome"), valor(ficha, k + ".volume")
            if not n:
                if v not in ("", 0):
                    alerta(k + ".nome", "identificar o objeto com Volume declarado", True)
                    completo = False
                continue
            # A linha não exporta quantidade. Seu Volume é sempre o total declarado,
            # mesmo quando o nome lembra um item tabelado.
            volume = declarado(k + ".volume")
            if volume is None:
                completo = False
            else:
                soma += volume
                legado += volume
        if any(valor(ficha, prefixo + f"carga.item.{i}.nome") for i in range(1, 7)):
            r.nao_conferido.append(f"{nome}: armazenamento adicional exige Talento compatível e anatomia; campo preenchido não prova essa autorização")
    else:
        integradas = origem(ficha)[0] == "Corpo Amaldiçoado" and "Ferramentas Integradas" in (
            valor(ficha, "origem.menor_1"), valor(ficha, "origem.menor_2"))
        inventario = {}
        for tipo, teto in (("equipavel", 8), ("item", 12)):
            for i in range(1, teto + 1):
                k = f"{tipo}.{i}"
                n = valor(ficha, k + ".nome")
                if not n:
                    if valor(ficha, k + ".quantidade") not in ("", 0) or valor(ficha, k + ".volume") not in ("", 0):
                        alerta(k + ".nome", "identificar a linha com quantidade/Volume", True)
                        completo = False
                    continue
                q = decimal(k + ".quantidade", quantidade=True)
                if q is None:
                    completo = False
                    continue
                e = ref.equipamento.pecas.get(n)
                canonico = re.sub(r"\s*\(.*\)$", "", n) if e else n
                inventario[canonico] = inventario.get(canonico, Decimal(0)) + q
                unidade = e.volume if e else ref.equipamento.itens.get(n)
                if integradas and n == "Ferramentas de ofício":
                    completo = False
                    r.nao_conferido.append("Carga: Ferramentas Integradas exige identificar qual conjunto foi integrado; isenção não presumida")
                    continue
                if unidade is not None:
                    v = q * unidade
                    antigo = q * Decimal("0.1") if tipo == "item" else v
                    comparar(k + ".volume", v, antigo if antigo != v else None)
                    soma += v
                    legado += antigo
                elif tipo == "item" or i > 6:
                    v = declarado(k + ".volume")
                    if v is None:
                        completo = False
                    else:
                        soma += v
                        legado += v
                else:
                    completo = False
                    r.nao_conferido.append(f"{nome}: Volume de {n} não vem de catálogo reconhecido nem de linha livre")
        vestindo = valor(ficha, "em_uso.vestindo")
        e = ref.equipamento.pecas.get(vestindo)
        if not vazio(vestindo):
            if e is None or e.tipo != "uniforme":
                completo = False
            else:
                soma += e.volume
                legado += e.volume
        for k in ("em_uso.principal", "em_uso.secundaria"):
            n = valor(ficha, k)
            canonico = re.sub(r"\s*\(.*\)$", "", n) if n in ref.equipamento.pecas else n
            if not vazio(n) and not inventario.get(canonico, 0):
                alerta(k, "registrar o equipamento em uso no inventário com quantidade positiva", True)

    forca = decimal(prefixo + "atributo.forca.base")
    extra = decimal(prefixo + ("atributo.forca.buff" if base else "atributo.forca.corpo"), vazio_zero=True)
    ajuste = Decimal(0) if base else decimal("carga.ajuste_limite", vazio_zero=True)
    if forca is None or extra is None or ajuste is None:
        completo = False
    if not completo:
        r.nao_conferido.append(f"{nome}: total não certificado com inventário/atributos incompletos")
        return
    if base:
        # A etapa antiga conhece só as três peças. Quando há inventário completo,
        # seu alerta de subtotal é substituído pelo da carga total, sem duplicação.
        r.pendencias[:] = [p for p in r.pendencias if not (p.regra == "carga" and p.campo == base + ".equipamento")]
    limite_legado = Decimal(5) + forca + extra + ajuste
    limite = limite_legado
    if not base and origem(ficha) == ("Restrição Celestial", "Sem Energia") and "Porte Incomum" in (
            valor(ficha, "origem.menor_1"), valor(ficha, "origem.menor_2")):
        nivel = valor(ficha, "nivel")
        if not inteiro(nivel, 1) or ref.magia is None:
            r.nao_conferido.append("Carga: Porte Incomum depende do nível válido para recalcular Maestria")
            return
        limite += ref.magia.maestria[nivel]
    if ajuste:
        r.notas.append(Problema("buff", "carga.ajuste_limite", "confirmar origem do ajuste", str(ajuste)))
    total_ok = comparar(total_k, soma, legado if soma != legado else None)
    limite_ok = comparar(limite_k, limite, limite_legado if limite != limite_legado else None)
    if limite <= 0:
        alerta(limite_k, "limite de carga positivo; revisar o Debuff", True)
    elif soma > limite:
        alerta(total_k, "reduzir a carga para voltar a se deslocar" if soma > 2 * limite else
               "deslocamento pela metade e desvantagem em TR Físico; as penalidades não se multiplicam", True)
    if total_ok and limite_ok and len(r.problemas) == inicio:
        r.conferidos.append(f"{nome}: {soma} de {limite} Volume" + (" pelas entradas declaradas" if livre else " pelo catálogo"))
