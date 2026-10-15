"""Contas de montagem pelo R51. Não usa o resultado ou o aviso da planilha como entrada.

A ANALISE v1 ainda omite escolhas do Fundamento e ajustes das entidades. Quando
essas entradas permitem mais de um resultado, não certifica uma conta exata.
"""
from __future__ import annotations

import itertools
import math
import re
import unicodedata
from dataclasses import dataclass

from .ficha_leitor import Campo

ERROS_PLANILHA = {"#NAME?", "#VALUE!", "#REF!", "#DIV/0!", "#N/A", "#NUM!", "#ERROR!", "#SPILL!"}


@dataclass(frozen=True)
class Melhoria:
    peso: str
    familia: str
    ancora: str
    repeticoes: int = 1
    minima: int = 0


@dataclass(frozen=True)
class Magia:
    # Classe -> nível mínimo, pontos pessoais, Leve, Média, Pesada
    classes: dict[int, tuple[int, int, int, int, int]]
    especiais: dict[int, int]
    formas: dict[str, str]
    melhorias: dict[str, Melhoria]
    restricoes: dict[str, tuple[str, str]]
    familias: tuple[str, ...]
    tipos: tuple[str, ...]
    aquisicoes: tuple[str, ...]
    maestria: dict[int, int]
    talentos_entidade: dict[str, int]
    ganhos_talento: tuple[tuple[int, int], ...]

    @classmethod
    def do_livro(cls, livro: dict[str, str]) -> Magia:
        classes = {int(c): tuple(map(int, vals)) for c, *vals in re.findall(
            r"^\| (\d) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$",
            livro["fundamento--pontos"], re.M)}
        especiais = {int(c): int(p) for c, p, _, _ in re.findall(
            r"^\| (\d) \| (\d+) \| (\d+) \| (\d+) \|$",
            livro["construcao--entidades-especiais"], re.M)}
        formas = {}
        for a in ("fundamento--formas", "fundamento--amparoformas"):
            for n, p in re.findall(r"^\| ([^|]+) \| (0|Leve|Média|Pesada) \|", livro[a], re.M):
                formas[n] = p
        familias = tuple(re.findall(r"^\| ([^|]+) \|", livro["fundamento--familias"], re.M)[1:])
        melhorias, restricoes, familia = {}, {}, ""
        for ancora, texto in livro.items():
            if not ancora.startswith("catalogo--cat-") or "passiva" in ancora:
                continue
            titulo = re.search(r"^### (.+)$", texto, re.M)
            if titulo and titulo[1] in familias:
                familia = titulo[1]
            for parte in re.split(r"(?m)^#### ", texto):
                nome = parte.splitlines()[0] if parte else ""
                peso = re.search(r"\*\*Preço: (Leve|Média|Pesada)\.\*\*", parte)
                devolve = re.search(r"\*\*Devolução: (Leve|Média)( ou Média)?\.\*\*", parte)
                if peso:
                    minimo = re.search(r"(?:Requer|Exige|exige) \*\*?Classe (\d+)", parte)
                    repeticoes = 2 if "Pode comprar duas vezes" in parte else 1
                    melhorias[nome] = Melhoria(peso[1], familia, ancora, repeticoes, int(minimo[1]) if minimo else 0)
                if devolve:
                    if devolve[2]:
                        for p in ("Leve", "Média"):
                            restricoes[f"{nome} ({p})"] = p, ancora
                    else:
                        restricoes[nome] = devolve[1], ancora
        # A entrada do livro reúne duas peças, com os preços explícitos.
        duracao = livro["catalogo--cat-tempo-duracao"]
        if "Concentrada - Leve; Duradoura - Média" not in duracao:
            raise ValueError("o livro mudou os preços de duração: revise as contas de magia")
        for n, p in (("Concentrada", "Leve"), ("Duradoura", "Média")):
            melhorias[n] = Melhoria(p, "Tempo", "catalogo--cat-tempo-duracao")
        for a, p in (("dano--leves", "Leve"), ("dano--medias", "Média"), ("dano--pesadas", "Pesada")):
            for n in re.findall(r"^##### (.+)$", livro[a], re.M):
                if n not in ("Remoção", "Testes de saída"):
                    melhorias[f"Condição: {n}"] = Melhoria(p, "Controle", "catalogo--cat-controle")
                    melhorias[n] = melhorias[f"Condição: {n}"]
        tipos = tuple(re.findall(r"^\| ([^|]+) \|", livro["construcao--entidades-tipos"], re.M)[1:])
        aquisicoes = tuple(re.findall(r"^\| ([^|]+) \|", livro["construcao--entidades-aquisicao"], re.M)[1:])
        guardas = {"fundamento--danolimites": "4 × Classe", "fundamento--familias": "arredondada para cima",
                   "construcao--entidades-familias": "arredondada para baixo", "fundamento--liberacao": "aumentado em 50%",
                   "construcao--entidades-saldo": "A Forma fica fora dessa conta"}
        if (set(classes) != set(range(1, 8)) or len(especiais) != 7 or len(formas) != 10 or len(familias) != 9
                or len(tipos) != 5 or len(aquisicoes) != 4 or len(melhorias) < 60 or len(restricoes) < 20
                or any(t not in livro[a] for a, t in guardas.items())):
            raise ValueError("o livro mudou de forma: revise as contas de magia")
        maestria = {int(n): int(m) for a in ("progressao--prog-tabela-inicial", "progressao--prog-tabela-avancada")
                    for n, m in re.findall(r"^\| (\d+) \| (\d+) \|", livro[a], re.M)}
        if set(maestria) != set(range(1, 31)):
            raise ValueError("o livro mudou a tabela de maestria")
        talentos = {n: 1 for n in re.findall(r"^\| ([^|]+) \| [^|]+ \| Talentos de Categoria 1\. \|$", livro["construcao--entidades-passivas"], re.M)}
        talentos.update({n: int(ce) for n, ce in re.findall(r"^\| ([^|]+) \| ([23]) \|", livro["construcao--entidades-passivas-avancadas"], re.M)})
        ganhos = tuple((int(n), int(ce)) for niveis, ce in re.findall(r"^\| ([\d, e]+) \| (\d) \|$", livro["construcao--entidades-passivas"], re.M)
                       for n in re.findall(r"\d+", niveis))
        if len(talentos) != 12 or len(ganhos) != 8:
            raise ValueError("o livro mudou os Talentos das entidades")
        return cls(classes, especiais, formas, melhorias, restricoes, familias, tipos, aquisicoes, maestria, talentos, ganhos)

    def classe_maxima(self, nivel: int) -> int:
        return max(c for c, v in self.classes.items() if v[0] <= nivel)

    def preco(self, peso: str, classe: int) -> int:
        return 0 if peso == "0" else self.classes[classe][{"Leve": 2, "Média": 3, "Pesada": 4}[peso]]


def valor(ficha: dict[str, Campo], chave: str):
    return ficha.get(chave, Campo("", "", "")).valor


def lista(ficha: dict[str, Campo], chave: str) -> list[str]:
    bruto = str(valor(ficha, chave))
    return [] if bruto in ERROS_PLANILHA else [p.strip() for p in bruto.split(" · ") if p.strip()]


def inteiro(v, minimo=0, maximo=30) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and minimo <= v <= maximo


def ativa(ficha: dict[str, Campo], base: str) -> bool:
    # Forma e Classe têm valores iniciais nas cartas vazias. Não criam um feitiço.
    if base.startswith("zero."):
        # Classe 0 exibe os dados da progressão mesmo sem nome/peças escolhidos.
        return bool(valor(ficha, base + ".nome") or lista(ficha, base + ".pecas") or lista(ficha, base + ".restricoes"))
    return bool(valor(ficha, base + ".nome") or lista(ficha, base + ".pecas") or lista(ficha, base + ".restricoes")
                or valor(ficha, base + ".pe") or valor(ficha, base + ".dano") or valor(ficha, base + ".texto"))


def bases(ficha: dict[str, Campo], padrao: str) -> list[str]:
    return sorted({k[:-5] for k in ficha if re.fullmatch(padrao + r"\.nome", k)},
                  key=lambda b: tuple(int(p) if p.isdigit() else p for p in b.split(".")))


def rotulo(base: str) -> str:
    p = base.split(".")
    nome = {"feitico": "Feitiço", "liberacao": "Liberação", "invocacao": "Invocação", "zero": "Classe 0"}[p[0]] + " " + p[1]
    if len(p) > 3:
        nome += " · " + {"bas": "básica", "esp": "especial", "ext": "habilidade da Trilha"}[p[2]] + " " + p[3]
    return nome


def escolhas_familias(ficha, magia, raiz, problemas):
    """None preserva a conferência conservadora de fichas antigas/incompletas.

    Na entidade: 1 = Livre, 2 = Livre da Principal, 3/4 = abertas, 5 = aberta da Trilha.
    São as posições do gerador, não a ordem da lista compactada da v1.
    """
    from .ficha_corretor import Problema
    entidade = raiz.startswith("invocacao.")
    chaves = ([f"{raiz}.familia.{i}" for i in range(1, 6)] if entidade else
              ["tecnica.familia." + re.sub(r"[^a-z0-9]+", "_", unicodedata.normalize('NFKD', f).encode('ascii', 'ignore').decode().lower())
               for f in magia.familias])
    if not all(k in ficha for k in chaves):
        return None, None
    def erro(esperado):
        problemas.append(Problema("escolha", raiz + ".familias", esperado,
                                  " · ".join(str(valor(ficha, k)) for k in chaves),
                                  "construcao--entidades-familias" if entidade else "fundamento--familias"))
    if entidade:
        trilha, dono = valor(ficha, "trilha"), valor(ficha, "nivel")
        principal = trilha == "Invocação Principal" and inteiro(dono, 2)
        adicional = trilha in ("Invocação Principal", "Parceria", "Múltiplas Invocações") and inteiro(dono, 2)
        indices = [0, 2, 3] + ([1] if principal else []) + ([4] if adicional else [])
        nomes = [valor(ficha, k) for k in chaves]
        abertas = [nomes[i] for i in indices]
        if (any(f not in magia.familias for f in abertas) or len(set(abertas)) != len(abertas)
                or any(nomes[i] for i in range(5) if i not in indices)):
            erro("Famílias distintas nas vagas permitidas da entidade e da Trilha")
            return None, None
        return {nomes[0]} | ({nomes[1]} if principal else set()), set(abertas)
    estados = [valor(ficha, k) for k in chaves]
    if (any(e not in ("Livre", "Neutra", "Fechada") for e in estados)
            or estados.count("Livre") != 2 or estados.count("Fechada") != 3):
        erro("duas Famílias Livres, três Fechadas e quatro Neutras")
        return None, None
    return {f for f, e in zip(magia.familias, estados) if e == "Livre"}, {f for f, e in zip(magia.familias, estados) if e != "Fechada"}


def conferir_montagem(ficha, magia, base, nivel, problemas, certos, pulou, *, entidade=False, basica=False, liberacao=False, familias=None):
    from .ficha_corretor import Problema
    nome = rotulo(base)
    def erro(sufixo, esperado, encontrado=None, ancora="fundamento--pontos"):
        problemas.append(Problema("conta", base + "." + sufixo, esperado,
                                  str(valor(ficha, base + "." + sufixo) if encontrado is None else encontrado), ancora))
    def comparar(sufixo, esperado, ancora):
        encontrado = valor(ficha, base + "." + sufixo)
        # PE vem como "3 PE" ou "Sem PE"; número normalizado também é aceito.
        if sufixo == "pe":
            if encontrado == "Sem PE":
                encontrado = 0
            elif isinstance(encontrado, str) and re.fullmatch(r"\d+ PE", encontrado):
                encontrado = int(encontrado.split()[0])
        if encontrado != esperado or isinstance(encontrado, bool):
            erro(sufixo, str(esperado), ancora=ancora)
        else:
            certos.append(f"{nome}: {'PE' if sufixo == 'pe' else sufixo} {esperado}")
    if not ativa(ficha, base):
        return
    if not valor(ficha, base + ".nome"):
        problemas.append(Problema("escolha", base + ".nome", "escolher o nome", ""))
    classe = valor(ficha, base + ".classe")
    minima = 0 if basica else 3 if liberacao else 1
    if not inteiro(classe, minima, 7) or (basica and classe != 0):
        erro("classe", "0" if basica else f"inteiro de {minima} a 7")
        return
    if not inteiro(nivel, 1):
        pulou.append(f"{nome}: falta nível válido para conferir a montagem")
        return
    if classe > magia.classe_maxima(nivel):
        erro("classe", f"até {magia.classe_maxima(nivel)} no nível {nivel}")
    if liberacao and nivel < 10:
        erro("classe", "Liberação só a partir do nível 10", ancora="fundamento--liberacao")
    comparar("pe", math.ceil(4.5 * classe) if liberacao else 3 * classe,
             "fundamento--liberacao" if liberacao else "construcao--entidades-especiais" if entidade else "fundamento--pontos")
    forma = str(valor(ficha, base + ".forma"))
    if forma not in magia.formas:
        erro("forma", "Forma do livro", ancora="fundamento--formas")
        return
    if any(str(valor(ficha, base + "." + c)) in ERROS_PLANILHA for c in ("pecas", "restricoes")):
        pulou.append(f"{nome}: as fórmulas de peças/Restrições estão com erro; montagem e dano não conferidos")
        return
    if (classe == 0 and forma in ("Cura", "Onda")) or (liberacao and forma in ("Cura", "Onda")):
        # Onda pode ser apoio numa Liberação; a ANALISE não traz a escolha.
        if liberacao and forma == "Onda":
            pulou.append(f"{nome}: Onda exige conferir com o mestre se foi montada como apoio; Liberação não cura")
        else:
            erro("forma", "Forma permitida nesta montagem", ancora="fundamento--liberacao" if liberacao else "fundamento--classezero")
    pecas, res = lista(ficha, base + ".pecas"), lista(ficha, base + ".restricoes")
    embutida = int(forma in ("Toque", "Aura") and classe > 0)
    limite = 1 if classe == 0 else 2 if classe <= 2 else 3 if classe <= 4 else 4
    if len(pecas) > limite:
        erro("pecas", f"até {limite} Melhorias")
    if len(res) + embutida > (1 if classe == 0 else 2):
        erro("restricoes", "até uma Leve" if classe == 0 else "até duas, contando Corpo a Corpo embutida")
    conhecidas = [magia.melhorias[n] for n in pecas if n in magia.melhorias]
    livres, abertas = familias if familias is not None else (None, None)
    if abertas is not None:
        fechadas = sorted({p.familia for p in conhecidas if p.familia and p.familia not in abertas})
        if fechadas:
            erro("pecas", "Melhorias de Famílias abertas; fechadas: " + ", ".join(fechadas), ancora="fundamento--familias")
        exige = "Área" if forma in ("Alvos", "Explosão", "Cone", "Linha", "Aura") else "Amparo" if forma in ("Cura", "Onda") else None
        if entidade and exige and exige not in abertas:
            erro("forma", f"{forma} exige {exige} aberta", ancora="construcao--entidades-formas")
    desconhecidas = [n for n in pecas if n not in magia.melhorias]
    if desconhecidas:
        pulou.append(f"{nome}: peças próprias ou não reconhecidas ({', '.join(desconhecidas)}); aprovação do mestre ainda não conferida")
    for nome_peca in set(pecas):
        p = magia.melhorias.get(nome_peca)
        if p and (pecas.count(nome_peca) > p.repeticoes or classe < p.minima or (classe == 0 and p.peso != "Leve")):
            erro("pecas", f"{nome_peca}: até {p.repeticoes} compra(s), Classe mínima {p.minima}" + (" e só Leve na Classe 0" if classe == 0 else ""), ancora=p.ancora)
    restricoes = [magia.restricoes[n] for n in res if n in magia.restricoes]
    if len(restricoes) != len(res):
        pulou.append(f"{nome}: Restrição própria ou não reconhecida; preço e aprovação do mestre não conferidos")
    if classe == 0 and any(p != "Leve" for p, _ in restricoes):
        erro("restricoes", "somente Restrição Leve", ancora="fundamento--classezero")
    nomes_res = [re.sub(r" \((Leve|Média)\)$", "", n) for n in res]
    if len(set(nomes_res)) != len(nomes_res) or (embutida and "Corpo a Corpo" in res):
        erro("restricoes", "não repetir devolução pelo mesmo impedimento", ancora="fundamento--restricoes")
    if sum(n in ("Uma Vez", "Condicional", "Aquecer", "Dívida") for n in nomes_res) > 1:
        erro("restricoes", "no máximo uma de frequência", ancora="fundamento--restricoes")
    if forma in ("Toque", "Aura", "Onda") and any(n in pecas for n in ("Longe", "Muito Longe")):
        erro("pecas", f"{forma} não aceita aumento de distância", ancora="catalogo--cat-alcance")
    pares = [("Atrasar", "Parado"), ("Silencioso", "Gesto"), ("Passo", "Parado"), ("Passo", "Atrasar"),
             ("Rápido", "Reação"), ("Barulho", "Assinatura")]
    for a, b in pares:
        if a in pecas + nomes_res and b in pecas + nomes_res:
            erro("pecas", f"não combinar {a} com {b}", ancora="fundamento--restricoes")
    if "Inescapável" in pecas and (forma != "Projétil" or len(pecas) > 1 or res or embutida):
        erro("pecas", "Inescapável: só Projétil, sem outra Melhoria ou Restrição", ancora="catalogo--cat-mira")
    if liberacao and any(n in pecas for n in ("Rápido", "Reação")):
        erro("pecas", "Liberação exige Ação Completa", ancora="fundamento--liberacao")
    pulou.append(f"{nome}: falta conferir {'Famílias, ' if abertas is None else ''}Selo, texto do efeito e resolução pela ficha completa")
    if (desconhecidas or len(restricoes) != len(res) or any(p.familia == "Controle" for p in conhecidas)
            or any(n in pecas for n in ("Toca a Alma", "Rajada", "Mais Um", "Junto", "Remate"))):
        pulou.append(f"{nome}: dano/benefício exige escolhas ou distribuição da ficha completa")
        return
    if classe == 0:
        inicial = (1 if nivel < 5 else 2 if nivel < 17 else 3) if entidade else (2 if nivel < 5 else 3 if nivel < 11 else 4 if nivel < 17 else 5 if nivel < 25 else 6)
        danos = {max(0, inicial - int(bool(pecas)) + int(bool(pecas) and bool(res)))}
        faces = 6 if entidade else 8
    else:
        orcamento = magia.especiais[classe] if entidade else magia.classes[classe][1]
        custo_forma = magia.preco(magia.formas[forma], classe)
        devolucao = (classe if embutida else 0) + sum(magia.preco(p, classe) for n, (p, _) in zip(res, restricoes)
                     if not (liberacao and n in ("Atrasar", "Parado")))
        usadas = sorted({p.familia for p in conhecidas})
        danos = set()
        # A v1 não identifica a Principal: admitir até duas Livres evita falso erro.
        opcoes = [livres] if livres is not None else [set(x) for qtd in range(min(2, len(usadas)) + 1) for x in itertools.combinations(usadas, qtd)]
        for livres_ in opcoes:
            desconto = max(1, classe // 2) if entidade else math.ceil(classe / 2)
            gasto = sum(max(1, magia.preco(p.peso, classe) - (desconto if p.familia in livres_ else 0)) for p in conhecidas)
            saldo = orcamento - custo_forma - gasto + min(2 * classe, gasto, devolucao)
            danos.add(saldo)
        if max(danos) < 0:
            erro("pecas", "montagem dentro do orçamento", ancora="construcao--entidades-saldo" if entidade else "fundamento--pontos")
            return
        danos = {d for d in danos if d >= 0}
        if forma in ("Cura", "Onda"):
            teto = orcamento - custo_forma
            danos = {min(d, teto) for d in danos}
        if liberacao:
            danos = {d + classe for d in danos}
        def cabe(d):
            extra = sum(d // 2 for n in pecas if n in ("Salto", "Queima", "Estilhaço"))
            return d * (1.25 if "Remate" in pecas else 1) + extra <= 4 * classe
        if forma not in ("Cura", "Onda", "Apoio", "Efeito"):
            danos = {max(d for d in range(inicial + 1) if cabe(d)) for inicial in danos}
        faces = 8
    # Com Famílias ausentes, só uma conta invariável pode ser certificada.
    if len(danos) != 1 or forma in ("Apoio", "Onda", "Efeito"):
        if len(danos) > 1 and forma not in ("Apoio", "Onda", "Efeito"):
            bruto = str(valor(ficha, base + ".dano"))
            match = re.match(r"(?:Cura\s*:?\s*)?(\d+)d(6|8)\b", bruto, re.I)
            if match and (int(match[1]) not in danos or int(match[2]) != faces):
                erro("dano", "dano-base dentro das possibilidades: " + ", ".join(f"{n}d{faces}" for n in sorted(danos)),
                     ancora="fundamento--danolimites")
        pulou.append(f"{nome}: dano/benefício não certificado sem Famílias e destino do saldo")
        return
    dado = next(iter(danos))
    texto = str(valor(ficha, base + ".dano"))
    esperado = f"{dado}d{faces}" if dado else "Sem dano"
    match = re.match(r"(?:Cura\s*:?\s*)?(\d+)d(6|8)\b", texto, re.I)
    bate = (bool(match) and int(match[1]) == dado and int(match[2]) == faces) or (dado == 0 and texto == "Sem dano")
    adicionais = sum(dado // 2 for n in pecas if n in ("Salto", "Queima", "Estilhaço")) if classe else 0
    parcelas = re.findall(r"\+\s*(\d+)d8", texto)
    if sum(map(int, parcelas)) != adicionais:
        bate = False
    media = re.search(r"=\s*(\d+)", texto)
    if media and int(media[1]) != math.floor(dado * (faces + 1) / 2):
        bate = False
    resto = re.sub(r"\+\s*\d+d8|=\s*\d+", "", texto)
    resto = re.sub(r"\d+d(?:6|8)", "", resto, count=1)
    if re.search(r"\d|[×*/]", resto):
        bate = False
    if not bate:
        erro("dano", esperado + (f" +{adicionais}d8 adicionais" if adicionais else ""), ancora="fundamento--danolimites")
    else:
        certos.append(f"{nome}: dano-base {esperado}")


def conferir_maxima(ficha, magia, resultado, familias=None):
    from .ficha_corretor import Problema
    if not (valor(ficha, "maxima.nome") or lista(ficha, "maxima.pecas") or valor(ficha, "maxima.texto")):
        return
    nivel = valor(ficha, "nivel")
    def erro(campo, esperado):
        resultado.problemas.append(Problema("conta", "maxima." + campo, esperado,
                                            str(valor(ficha, "maxima." + campo)), "fundamento--maxima"))
    if not valor(ficha, "maxima.nome"):
        erro("nome", "nome da Técnica Máxima preenchida")
    if not inteiro(nivel, 17):
        erro("nome", "Técnica Máxima a partir do nível 17")
        return
    classe = magia.classe_maxima(nivel)
    dados, pontos = (24, 8) if nivel < 21 else (28, 12) if nivel < 26 else (32, 16)
    if valor(ficha, "maxima.pe") != 5 * classe:
        erro("pe", str(5 * classe))
    else:
        resultado.conferidos.append(f"Técnica Máxima: PE {5 * classe}")
    pecas, forma = lista(ficha, "maxima.pecas"), valor(ficha, "maxima.forma")
    if forma not in magia.formas:
        erro("forma", "Forma do livro")
        return
    if len(pecas) > 4:
        erro("pecas", "até quatro Melhorias")
    conhecidas = [magia.melhorias[n] for n in pecas if n in magia.melhorias]
    livres, abertas = familias if familias else (None, None)
    if len(conhecidas) != len(pecas) or livres is None:
        resultado.nao_conferido.append("Técnica Máxima: falta conferir peças próprias ou escolhas válidas de Famílias")
        return
    gasto = magia.preco(magia.formas[forma], classe)
    for n in set(pecas):
        p = magia.melhorias[n]
        if pecas.count(n) > p.repeticoes or classe < p.minima or p.familia and p.familia not in abertas:
            erro("pecas", f"requisitos, repetição e Família aberta de {n}")
    gasto += sum(max(1, magia.preco(p.peso, classe) - (math.ceil(classe / 2) if p.familia in livres else 0)) for p in conhecidas)
    if gasto > pontos:
        erro("pecas", f"montagem de até {pontos} pontos; gasto {gasto}")
    else:
        resultado.conferidos.append(f"Técnica Máxima: montagem {gasto} de {pontos}")
    if forma in ("Efeito", "Apoio", "Onda") or any(n in pecas for n in ("Rajada", "Mais Um", "Junto", "Remate", "Toca a Alma", "Salto", "Queima", "Estilhaço")):
        resultado.nao_conferido.append("Técnica Máxima: aplicação e distribuição dos dados precisam de conferência")
    else:
        texto = str(valor(ficha, "maxima.dano"))
        if not re.fullmatch(rf"(?:Cura\s*:?\s*)?{dados}d8(?:\s*=\s*{dados * 9 // 2})?", texto, re.I):
            erro("dano", f"{dados}d8, separados dos pontos de montagem")
        else:
            resultado.conferidos.append(f"Técnica Máxima: {dados}d8")
    resultado.nao_conferido.append("Técnica Máxima: texto, requisitos e recarga precisam de conferência do mestre")


def conferir_feiticos(ficha, magia, resultado):
    from .ficha_corretor import Problema
    nivel = valor(ficha, "nivel")
    cartas = [b for b in bases(ficha, r"(?:feitico|liberacao|zero)\.\d+") if ativa(ficha, b)]
    familias = escolhas_familias(ficha, magia, "tecnica", resultado.problemas) if cartas or valor(ficha, "maxima.nome") or lista(ficha, "maxima.pecas") or valor(ficha, "maxima.texto") else None
    for base in cartas:
        conferir_montagem(ficha, magia, base, nivel, resultado.problemas, resultado.conferidos, resultado.nao_conferido,
                          liberacao=base.startswith("liberacao."), basica=base.startswith("zero."), familias=familias)
    liberacoes = [b for b in bases(ficha, r"liberacao\.\d+") if ativa(ficha, b)]
    if inteiro(nivel, 1) and len(liberacoes) > nivel // 10:
        resultado.problemas.append(Problema("conta", liberacoes[-1] + ".nome", f"até {nivel // 10} Liberação(ões) no nível {nivel}",
                                            str(len(liberacoes)), "fundamento--liberacao"))
    if any(ativa(ficha, b) for b in bases(ficha, r"(?:feitico|liberacao)\.\d+")):
        resultado.nao_conferido.append("repertório completo: concessões e compras fora dos espaços ainda precisam de conferência")
    zeros = [b for b in cartas if b.startswith("zero.")]
    if inteiro(nivel, 1) and len(zeros) > (2 if nivel < 5 else 3 if nivel < 11 else 4 if nivel < 17 else 5):
        resultado.problemas.append(Problema("conta", zeros[-1] + ".nome", "quantidade de Classe 0 da progressão", str(len(zeros)), "fundamento--classezero"))
    conferir_maxima(ficha, magia, resultado, familias)


def conferir_invocacoes(ficha, magia, marcos, resultado, equipamento=None):
    from .ficha_corretor import Problema
    dono = valor(ficha, "nivel")
    for base in bases(ficha, r"invocacao\.\d+"):
        cartas = [b for b in bases(ficha, re.escape(base) + r"\.(?:bas|esp|ext)\.\d+") if ativa(ficha, b)]
        if not valor(ficha, base + ".nome") and not cartas:
            continue
        def erro(campo, esperado, ancora="construcao--entidades-aquisicao"):
            resultado.problemas.append(Problema("conta", base + "." + campo, esperado, str(valor(ficha, base + "." + campo)), ancora))
        if not valor(ficha, base + ".nome"):
            erro("nome", "nome da entidade que tem habilidades preenchidas")
        tipo, aquis = valor(ficha, base + ".tipo"), valor(ficha, base + ".aquisicao")
        if tipo not in magia.tipos or aquis not in magia.aquisicoes or not inteiro(dono, 1):
            erro("aquisicao", "tipo, aquisição e nível do invocador válidos")
            continue
        esperada = "Maldição domada" if tipo == "Maldição domada" else "Criação" if tipo.endswith(" de criação") else None
        if (esperada and aquis != esperada) or (not esperada and aquis in ("Maldição domada", "Criação")):
            erro("aquisicao", f"aquisição compatível com {tipo}")
            continue
        fixo = valor(ficha, base + ".nivel_fixo")
        if aquis in ("Maldição domada", "Criação"):
            if not inteiro(fixo, 1, dono):
                erro("nivel_fixo", f"nível registrado de 1 a {dono}")
                continue
            if aquis == "Criação":
                classe_criada = magia.classe_maxima(fixo)
                fim = magia.classes.get(classe_criada + 1, (31,))[0] - 1
                nivel = min(dono, fim)
            else:
                nivel = fixo
        else:
            nivel = dono
        classe = magia.classe_maxima(nivel)
        entrada = math.ceil(classe / 2) if tipo == "Shikigami de criação" and valor(ficha, base + ".talisma") == "Com carga" else classe
        for campo, esperado in (("nivel", nivel), ("classe", classe), ("entrada", entrada), ("retorno", 2 * classe)):
            if valor(ficha, base + "." + campo) != esperado:
                erro(campo, str(esperado), "campo--inv-retorno" if campo == "retorno" else "construcao--entidades-progressao")
            else:
                resultado.conferidos.append(f"{rotulo(base)}: {'Classe' if campo == 'classe' else campo} {esperado}")
        pontos = lista(ficha, base + ".pontos")
        if len(pontos) != 5 or any(not re.fullmatch(r"[0-6]", n) for n in pontos):
            erro("pontos", "cinco atributos inteiros de 0 a 6", "construcao--entidades-atributos")
        elif sum(map(int, pontos)) > 9 + sum(n <= nivel for n in marcos):
            erro("pontos", f"até {9 + sum(n <= nivel for n in marcos)} distribuídos", "construcao--entidades-atributos")
        elif nivel < 6 and any(int(n) > 3 for n in pontos):
            erro("pontos", "até 3 por atributo antes do primeiro marco", "construcao--entidades-atributos")
        familias = escolhas_familias(ficha, magia, base, resultado.problemas)
        for tipo_carta, limite in (("bas", 1 if nivel < 11 else 2), ("esp", 1 + nivel // 4)):
            preenchidas = [b for b in cartas if f".{tipo_carta}." in b]
            if len(preenchidas) > limite:
                erro(tipo_carta, f"até {limite} habilidades conhecidas nessa progressão", "construcao--entidades-progressao")
        for i, (abre, teto) in enumerate(magia.ganhos_talento, 1):
            campo = f"talento.{i}"
            talento = valor(ficha, base + "." + campo)
            if not talento:
                continue
            if nivel < abre:
                erro(campo, f"vaga de Talento a partir do nível {abre}", "construcao--entidades-passivas")
            elif talento not in magia.talentos_entidade:
                resultado.nao_conferido.append(f"{rotulo(base)}: Talento próprio ou desconhecido ({talento}); aprovação aguardará CONFIGURAÇÃO")
            elif magia.talentos_entidade[talento] > teto:
                erro(campo, f"até CE {teto} na escolha do nível {abre}", "construcao--entidades-passivas")
        for b in cartas:
            conferir_montagem(ficha, magia, b, nivel, resultado.problemas, resultado.conferidos, resultado.nao_conferido,
                              entidade=True, basica=".bas." in b or (".ext." in b and valor(ficha, b + ".classe") == 0), familias=familias)
        from .ficha_entidade import conferir_numeros
        conferir_numeros(ficha, magia, base, nivel, resultado, equipamento)
        resultado.nao_conferido.append(f"{rotulo(base)}: {'Famílias, ' if familias[0] is None else ''}vagas extras da Trilha, Talentos, trunfos e texto da aquisição ainda precisam de conferência")
