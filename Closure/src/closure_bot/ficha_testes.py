"""TR, perícias e Ofícios: contas das entradas da ANALISE 4, sem IA.

Totais de treinos não provam a origem temporal de cada escolha. O atributo de um
Ofício pode mudar com a tarefa, mas a perícia conserva o atributo do catálogo.
"""
from dataclasses import dataclass
import math
import re
import unicodedata

from .ficha_equipamento import numero
from .ficha_magia import inteiro, valor, bases


def chave(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", texto.strip()).strip("_")


ATRIBUTOS = {"forca": "Força", "destreza": "Destreza", "constituicao": "Constituição",
             "inteligencia": "Inteligência", "essencia": "Essência"}
ABREV = dict(zip(("for", "des", "con", "int", "ess"), ATRIBUTOS))
TRS = {"fisico": ("Físico", None), "vigor": ("Vigor", "constituicao"),
       "intelecto": ("Intelecto", "inteligencia"), "espirito": ("Espírito", "essencia")}


def atributo(texto):
    n = chave(texto)
    return n if n in ATRIBUTOS else ABREV.get(n)


def bonus(texto):
    if numero(texto):
        return texto
    if isinstance(texto, str) and re.fullmatch(r"[+−-]?\d+(?:[.,]\d+)?", texto.strip()):
        return float(texto.replace("−", "-").replace(",", "."))
    return None


@dataclass(frozen=True)
class RegrasTestes:
    pericias: dict
    oficios: dict
    bases: tuple
    trocam_arma: frozenset

    @classmethod
    def do_livro(cls, livro, catalogo):
        pericias = {chave(n): (n, chave(a)) for a, nomes in catalogo["PERICIAS"] for n in nomes}
        oficios = {chave(n): (n, chave(a)) for n, a in re.findall(
            r"^\| ([^|]+) \| (Força|Destreza|Constituição|Inteligência|Essência) \|", livro["pericias--oficios"], re.M)}
        bases = re.search(r"criação reúne \*\*(\w+) perícias e (\w+) ofícios\*\*, ou \*\*(\w+) perícias sem ofícios", livro["ab--ab-origem"])
        palavras = {"nove": 9, "dois": 2, "dez": 10}
        guardas = {"ab--ab-origem": "Escolha dois diferentes", "geral--pericias": "metade da maestria",
                   "progressao--prog-marcos": "A partir do nível 10",
                   "construcao--entidades-atributos": "4 + metade da Inteligência",
                   "origens--restricao-beneficios": "uma perícia ou dois Ofícios"}
        trocam = {"Guia": "guia--guia", "Emanador": "emanador--ema-base", "Evocador": "evocador--evocador"}
        if (not bases or any(n not in palavras for n in bases.groups()) or len(pericias) != 23 or len(oficios) != 11
                or any(t not in livro[a] for a, t in guardas.items())
                or any("duas" not in livro[a] or "arma específica" not in livro[a] for a in trocam.values())):
            raise ValueError("o livro mudou TR/perícias/Ofícios: revise o corretor")
        return cls(pericias, oficios, ((palavras[bases[1]], palavras[bases[2]]), (palavras[bases[3]], 0)), frozenset(trocam))


def conferir_testes(ficha, ref, r):
    """Retorna os avisos antigos substituídos por conferência independente completa."""
    from .ficha_corretor import Problema
    ignorar = set()
    if valor(ficha, "formato.versao") != 4 or ref.testes is None or ref.magia is None:
        r.nao_conferido.append("TR/perícias/Ofícios: resultados e ajustes completos exigem a ANALISE 4")
        return ignorar
    nivel = valor(ficha, "nivel")
    if not inteiro(nivel, 1):
        r.nao_conferido.append("TR/perícias: falta nível válido para recalcular Maestria")
        return ignorar
    maestria = ref.magia.maestria[nivel]

    def problema(k, esperado, ancora="geral--pericias", pendente=False):
        (r.pendencias if pendente else r.problemas).append(
            Problema("testes", k, esperado, str(valor(ficha, k)), ancora))

    def comparar(k, esperado, nome):
        if k not in ficha:
            r.nao_conferido.append(f"{nome}: resultado não exportado na ANALISE")
        elif bonus(valor(ficha, k)) != esperado:
            problema(k, f"bônus {esperado:+g}")
        else:
            r.conferidos.append(f"{nome}: bônus {esperado:+g}")

    def ajuste(k):
        if k not in ficha:
            return None
        n = valor(ficha, k)
        if n == "":
            return 0
        if not numero(n):
            problema(k, "ajuste numérico finito")
            return None
        if n:
            r.notas.append(Problema("buff", k, "confirmar a origem do ajuste com o mestre", str(n)))
        return n

    def atributos(base=""):
        out = {}
        for a in ATRIBUTOS:
            ks = [base + f"atributo.{a}.{p}" for p in (("base", "buff") if base else ("base", "corpo"))]
            if not all(k in ficha for k in ks):
                continue
            v, extra = (valor(ficha, k) for k in ks)
            if (not inteiro(v, 0, 6) or extra != "" and not numero(extra)
                    or not base and extra != "" and not inteiro(extra, 0, 6)):
                problema(ks[0] if not inteiro(v, 0, 6) else ks[1], "atributo base de 0 a 6 e ajuste numérico finito")
                continue
            out[a] = v + (extra or 0)
            if not base and out[a] > 6:
                problema(ks[1], "atributo total pessoal até 6", "progressao--prog-marcos")
                del out[a]
        return out

    def checkbox(k):
        v = valor(ficha, k)
        if k not in ficha:
            return None
        if isinstance(v, bool) or v not in (0, 1):
            problema(k, "marcação 0 ou 1")
            return None
        return v

    atrs = atributos()
    corpo = valor(ficha, "marco.corpo")
    marcos = sum(n <= nivel for n in ref.marcos)
    if len(atrs) == 5 and inteiro(corpo, 0, marcos):
        pontos_base = [valor(ficha, f"atributo.{a}.base") for a in ATRIBUTOS]
        pontos_corpo = [valor(ficha, f"atributo.{a}.corpo") or 0 for a in ATRIBUTOS]
        for k, total, teto in (("atributos.base", sum(pontos_base), 9 + marcos),
                                ("atributos.corpo", sum(pontos_corpo), corpo)):
            if total != teto:
                problema(k, f"distribuir {teto} pontos nesta parcela; há {total}", "progressao--prog-marcos", total < teto)
        if sum(max(0, n - 3) for n in pontos_base) > marcos:
            problema("atributos.base", "valores acima de 3 limitados aos pontos de marco alcançados", "progressao--prog-marcos")
        ignorar.add("aviso.pontos_disponiveis")
    treinos, especiais = {}, {}
    for tipo, tabela in (("pericia", ref.testes.pericias), ("oficio", ref.testes.oficios)):
        treinos[tipo], especiais[tipo] = {}, {}
        for slug, (nome, padrao) in tabela.items():
            base = f"{tipo}.{slug}"
            t, e = checkbox(base + ".treino"), checkbox(base + ".especialista")
            treinos[tipo][slug], especiais[tipo][slug] = t, e
            ks = [base + "." + k for k in ("atributo", "ajuste", "bonus")]
            if None in (t, e) or not all(k in ficha for k in ks):
                r.nao_conferido.append(f"{nome}: faltam entradas de treino, especialização, atributo, ajuste ou bônus")
                continue
            if e and not t:
                problema(base + ".especialista", "especialização exige treino na mesma competência")
            if e and nivel < 10:
                problema(base + ".especialista", "especialização a partir do nível 10", "progressao--prog-marcos")
            a = atributo(valor(ficha, base + ".atributo"))
            if a is None or tipo == "pericia" and a != padrao:
                problema(base + ".atributo", ATRIBUTOS[padrao] if tipo == "pericia" else "atributo válido para a tarefa")
                continue
            if tipo == "oficio" and t and a != padrao:
                r.notas.append(Problema("testes", base + ".atributo",
                    f"padrão {ATRIBUTOS[padrao]}; confirmar a tarefa que usa {ATRIBUTOS[a]}", str(valor(ficha, base + ".atributo")), "pericias--oficios"))
            b = ajuste(base + ".ajuste")
            if a not in atrs or b is None:
                r.nao_conferido.append(f"{nome}: atributo/ajuste inválido ou ausente impede conferir o bônus")
                continue
            if e and (not t or nivel < 10):
                continue
            comparar(base + ".bonus", atrs[a] + t * maestria + e * (maestria // 2) + b, nome)
    r.nao_conferido.append("Ofício sem treino: bônus exibido não autoriza tentativa; improvisação e atributo da tarefa dependem do mestre")

    tr = {}
    for slug, (nome, fixo) in TRS.items():
        base = "tr." + slug
        t = tr[slug] = checkbox(base + ".treino")
        if t is None or not all(base + "." + k in ficha for k in ("atributo", "ajuste", "bonus")):
            r.nao_conferido.append(f"TR {nome}: faltam entradas ou resultado")
            continue
        a = atributo(valor(ficha, base + ".atributo"))
        if (slug == "fisico" and a not in ("forca", "destreza")) or (fixo and a != fixo):
            problema(base + ".atributo", "Força ou Destreza, escolha fixa" if not fixo else ATRIBUTOS[fixo], "ab--ab-origem")
            continue
        b = ajuste(base + ".ajuste")
        if b is not None and a in atrs:
            comparar(base + ".bonus", atrs[a] + t * maestria + b, "TR " + nome)
    if all(v is not None for v in tr.values()):
        n = sum(tr.values())
        if n != 2:
            problema("tr", "escolher dois TR diferentes" if n < 2 else "somente dois TR treinados da criação", "ab--ab-origem", n < 2)
        ignorar.add("aviso.testes_disponiveis")

    if all(v is not None for grupo in (*treinos.values(), *especiais.values()) for v in grupo.values()):
        corpo = valor(ficha, "marco.corpo")
        if inteiro(corpo, 0, sum(n <= nivel for n in ref.marcos)) and all(k in ficha for k in (
                "origem", "origem.marcante", "origem.menor_1", "origem.menor_2", "trocou_por_arma", "caminho")):
            p, o = sum(treinos["pericia"].values()), sum(treinos["oficio"].values())
            s = sum(v for grupo in especiais.values() for v in grupo.values())
            _conferir_quantidades(ficha, ref, r, nivel, corpo, p, o, s, problema)
            ignorar.update(("aviso.escolhas_de_pericia", "aviso.pericias_disponiveis", "aviso.oficios_disponiveis"))
        else:
            r.nao_conferido.append("treinos: concessões de Corpo/Origem e troca por arma incompletas impedem fechar a quantidade")
    for base in bases(ficha, r"invocacao\.\d+"):
        if valor(ficha, base + ".nome"):
            _entidade(ficha, ref, r, base, maestria, atributos, ajuste, comparar, problema)
    return ignorar


def _conferir_quantidades(ficha, ref, r, nivel, corpo, p, o, s, problema):
    from .ficha_corretor import Problema
    from .ficha_repertorio import origem
    base, variante = origem(ficha)
    marcante = valor(ficha, "origem.marcante")
    menores = {valor(ficha, "origem.menor_1"), valor(ficha, "origem.menor_2")}
    opcoes = set(ref.testes.bases)
    fontes = []
    for tem, nome, ganhos in (
        (base == "Encarnado" and marcante == "Duas Vidas", "Duas Vidas", ((1, 0), (0, 1))),
        ((base, variante) == ("Restrição Celestial", "Sem Energia") and "Aprendizado Complementar" in menores,
         "Aprendizado Complementar", ((1, 0), (0, 2))),
        (base == "Corpo Amaldiçoado" and "Arquivo de Procedimentos" in menores,
         "Arquivo de Procedimentos", ((1, 0), (0, 1)))):
        if tem:
            opcoes = {(a + x, b + y) for a, b in opcoes for x, y in ganhos}
            fontes.append(nome)
    gratis = int(base == "Encarnado" and marcante == "Duas Vidas" and "Especialidade Antiga" in menores and nivel >= 10)
    troca = valor(ficha, "trocou_por_arma")
    custo = {"Não trocou": 0, "1 arma (-2 pericias)": 2, "2 armas (-4 pericias)": 4}.get(troca)
    if custo is None or custo and valor(ficha, "caminho") not in ref.testes.trocam_arma:
        problema("trocou_por_arma", "troca por arma permitida no Caminho e registrada", "ab--ab-caminho")
        return
    opcoes = {(a - custo, b) for a, b in opcoes}
    possibilidades = []
    for a, b in opcoes:
        gasto = max(0, p - a) + max(0, o - b) + max(0, s - gratis)
        if gasto <= corpo:
            possibilidades.append(max(0, a - p) + max(0, b - o) + corpo - gasto + max(0, gratis - s))
    if not possibilidades:
        problema("treinos", f"perícias, Ofícios e especializações dentro das concessões de criação, {corpo} Corpo e Origem", "ab--ab-origem")
    elif min(possibilidades):
        problema("treinos", f"completar pelo menos {min(possibilidades)} escolha(s) de treino/especialização", "ab--ab-origem", True)
    else:
        r.conferidos.append(f"Treinos: {p} perícias, {o} Ofícios e {s} especializações compatíveis com as concessões")
    if fontes or gratis:
        r.notas.append(Problema("testes", "treinos", "confirmar vínculo das concessões: " + ", ".join(fontes + (["Especialidade Antiga"] if gratis else [])), "totais por possibilidades", "origens--origens"))
    r.nao_conferido.append("Treinos: totais compatíveis não provam origem de cada escolha nem quando uma especialização foi adquirida")


def _entidade(ficha, ref, r, base, maestria, atributos, ajuste, comparar, problema):
    nome_entidade = base.replace("invocacao.", "Invocação ")
    atrs = atributos(base + ".")
    escolhido = valor(ficha, base + ".tr_treinado")
    nomes = {n: k for k, (n, _) in TRS.items()}
    if escolhido not in nomes:
        problema(base + ".tr_treinado", "escolher um TR treinado da entidade", "construcao--entidades-atributos", escolhido == "")
    for slug, (nome, fixo) in TRS.items():
        a = fixo or atributo(valor(ficha, base + ".atributo_fisico"))
        if not fixo and a not in ("forca", "destreza"):
            problema(base + ".atributo_fisico", "Força ou Destreza, escolha fixa", "construcao--entidades-atributos")
            continue
        b = ajuste(base + ".buff.tr." + slug)
        if escolhido in nomes and a in atrs and b is not None:
            comparar(base + ".tr." + slug + ".bonus", atrs[a] + (maestria if escolhido == nome else 0) + b,
                     nome_entidade + " · TR " + nome)
    nomes_pericias = {n: a for n, a in ref.testes.pericias.values()}
    selecionadas = []
    completo = True
    for i in range(1, 8):
        k = base + f".pericia.{i}"
        if k not in ficha:
            completo = False
            continue
        n = valor(ficha, k)
        if not n:
            continue
        if n in selecionadas:
            problema(k, "perícias distintas, sem treino duplicado", "construcao--entidades-atributos")
        selecionadas.append(n)
        if n not in nomes_pericias:
            r.nao_conferido.append(f"{base}: perícia/Ofício próprio ({n}) precisa de permissão e atributo; não certificado")
            completo = False
            continue
        a = nomes_pericias[n]
        if a in atrs:
            comparar(k + ".bonus", atrs[a] + maestria, f"{nome_entidade} · {n}")
    if completo and "inteligencia" in atrs:
        # Buff pode ser temporário; ele não prova aquisição permanente de um treino.
        original = valor(ficha, base + ".atributo.inteligencia.base")
        limites = {4 + math.floor(n / 2) for n in (original, atrs["inteligencia"])}
        quantidade = len(set(selecionadas))
        if quantidade > max(limites):
            problema(base + ".pericias", f"até {max(limites)} perícias pelos atributos", "construcao--entidades-atributos")
        elif quantidade < min(limites):
            problema(base + ".pericias", f"escolher ao menos {min(limites)} perícias distintas", "construcao--entidades-atributos", True)
        elif len(limites) > 1:
            r.nao_conferido.append(f"{base}: quantidade de perícias depende da duração/origem do ajuste de Inteligência")
        else:
            r.conferidos.append(f"{nome_entidade}: {quantidade} perícias distintas")
