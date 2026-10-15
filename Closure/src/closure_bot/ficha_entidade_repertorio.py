"""Escolhas da Principal e aquisição/contas declaradas dos trunfos da domada.

As cartas de trunfo exportam texto, não peças estruturadas. Preço/dados compatíveis
não aprovam essa montagem nem provam que uma maldição tem técnica própria.
"""
from dataclasses import dataclass
import math
import re

from .ficha_magia import ativa, bases, inteiro, valor, rotulo


@dataclass(frozen=True)
class RegrasEntidade:
    extras: tuple[int, ...]
    maximas: dict
    dominios: dict

    @classmethod
    def do_livro(cls, livro):
        t = livro["evocador--ev-principal-especial"]
        niveis = re.search(r"Nos níveis ([\d, e]+) da invocação", t)
        maximas = {}
        for ini, fim, dados, pontos, pe in re.findall(
                r"^\| (\d+) a (\d+) \| (\d+)d8 \| (\d+) \| (\d+) PE \|$", livro["campo--inv-maxima"], re.M):
            for n in range(int(ini), int(fim) + 1):
                maximas[n] = (int(dados), int(pontos), int(pe))
        dominios, minimo, rf = {}, 0, 0
        for degrau, aquisicao, requisitos in re.findall(r"^\| (Incompleta|Completa|Sem Barreiras) \| ([^|]+) \| ([^|]+) \|$",
                                                        livro["campo--inv-dominio"], re.M):
            custo = re.search(r"total (\d+)", aquisicao) or re.search(r"(\d+) espaços", aquisicao)
            nv = re.search(r"[Nn]ível (\d+)", requisitos)
            refino = re.search(r"refino (\d+)", requisitos)
            minimo = max(minimo, int(nv[1]) if nv else 0)
            rf = max(rf, int(refino[1]) if refino else 0)
            if custo:
                dominios[degrau] = (int(custo[1]), minimo, rf, "especialização em Ocultismo" in requisitos)
        guardas = [("evocador--ev-principal-especial", "Todo talento concedido por Repertório Ampliado é de **Categoria de Efeito 1**"),
                   ("campo--inv-liberacao", "Somente maldições domadas com técnica própria"),
                   ("campo--inv-liberacao", "uma no nível 10, duas no 20 e três no 30"),
                   ("campo--inv-liberacao", "3 × Classe × 1,5 PE"),
                   ("campo--inv-dominio", "6 × a maior Classe"), ("campo--inv-dominio", "7 × essa Classe"),
                   ("campo--inv-maxima", "Não aceita Restrições")]
        if not niveis or len(dominios) != 3 or set(maximas) != set(range(17, 31)) or any(t not in livro[a] for a, t in guardas):
            raise ValueError("o livro mudou os extras/trunfos da entidade: revise o corretor")
        return cls(tuple(map(int, re.findall(r"\d+", niveis[1]))), maximas, dominios)


def conferir_repertorio_entidade(ficha, ref, base, nivel, cartas, familias, r):
    from .ficha_corretor import Problema, refino
    nome = rotulo(base)
    magia, regras = ref.magia, ref.entidades

    def erro(k, esperado, ancora):
        r.problemas.append(Problema("conta", k, esperado, str(valor(ficha, k)), ancora))

    def comparar(k, esperado, ancora, *, pe=False):
        if k not in ficha:
            r.nao_conferido.append(f"{nome}: resultado de trunfo não exportado ({k})")
            return
        achado = valor(ficha, k)
        if pe and isinstance(achado, str) and re.fullmatch(r"\d+ PE", achado):
            achado = int(achado.split()[0])
        if achado != esperado or isinstance(achado, bool):
            erro(k, str(esperado), ancora)
        else:
            r.conferidos.append(f"{nome}: {k.removeprefix(base + '.')} {esperado}")

    dono = valor(ficha, "nivel")
    principal = (valor(ficha, "caminho") == "Evocador" and valor(ficha, "trilha") == "Invocação Principal"
                 and inteiro(dono, 2))
    inicio = len(r.problemas)
    for k in ficha:
        m = re.fullmatch(re.escape(base) + r"\.(?:ext\.(\d+)\.nome|talento_extra\.(\d+))", k)
        if m and int(m[1] or m[2]) not in range(1, len(regras.extras) + 1) and valor(ficha, k):
            erro(k, "somente três escolhas extras da Principal", "evocador--ev-principal-especial")
    for i, abre in enumerate(regras.extras, 1):
        habilidade = base + f".ext.{i}"
        talento = base + f".talento_extra.{i}"
        tem_carta, t = ativa(ficha, habilidade), valor(ficha, talento)
        if not tem_carta and not t:
            continue
        ancora = "evocador--ev-principal-especial"
        if not principal or nivel < abre:
            erro(habilidade + ".nome" if tem_carta else talento,
                 f"escolha da Invocação Principal no nível {abre} da entidade, com dono Evocador/Trilha nível 2+", ancora)
        if tem_carta and t:
            erro(talento, "uma básica OU uma especial OU um Talento nesta escolha; não duas concessões", ancora)
        if t:
            ce = magia.talentos_entidade.get(t)
            propria = re.fullmatch(r"Talento Próprio \(CE ([123])\)", str(t))
            if propria:
                ce = int(propria[1])
            if ce is not None and ce != 1:
                erro(talento, "Talento permitido de CE1, inclusive nas escolhas dos níveis 16 e 24", ancora)
            elif ce is None:
                if t in magia.repertorio.talentos:
                    erro(talento, "Talento permitido no catálogo das entidades", "construcao--entidades-passivas-avancadas")
                else:
                    r.nao_conferido.append(f"{nome}: Talento extra próprio/desconhecido exige CE1 e aprovação do mestre")
            if propria:
                r.nao_conferido.append(f"{nome}: Categoria do Talento extra próprio não aprova seu efeito; aguarda CONFIGURAÇÃO")
    if any(base + f".talento_extra.{i}" not in ficha or base + f".ext.{i}.nome" not in ficha for i in range(1, 4)):
        r.nao_conferido.append(f"{nome}: faltam posições para conferir todas as escolhas extras da Trilha")
    elif len(r.problemas) == inicio:
        r.conferidos.append(f"{nome}: escolhas extras separadas das vagas normais; benefícios da Principal dependem de uma única ativa")

    for k in (k for k in ficha if re.fullmatch(re.escape(base) + r"\.talento\.\d+", k)):
        t = valor(ficha, k)
        propria = re.fullmatch(r"Talento Próprio \(CE ([123])\)", str(t))
        i = int(k.rsplit(".", 1)[1])
        if t and not 1 <= i <= len(magia.ganhos_talento):
            erro(k, "até oito ganhos de Talento da entidade", "construcao--entidades-passivas")
        if propria and 1 <= i <= len(magia.ganhos_talento) and int(propria[1]) > magia.ganhos_talento[i - 1][1]:
            erro(k, f"até CE {magia.ganhos_talento[i - 1][1]} nesse ganho", "construcao--entidades-passivas")
        if t and t in magia.repertorio.talentos and t not in magia.talentos_entidade:
            erro(k, "Talento permitido no catálogo das entidades", "construcao--entidades-passivas-avancadas")

    # Somente nome/descrição/escolha ativam o trunfo: fórmulas pré-preenchidas não.
    liberacoes = [b for b in bases(ficha, re.escape(base) + r"\.liberacao\.\d+")
                  if valor(ficha, b + ".nome") or valor(ficha, b + ".como")]
    maxima = bool(valor(ficha, base + ".tm.nome") or valor(ficha, base + ".tm.como"))
    dominio = bool(valor(ficha, base + ".exp.nome") or valor(ficha, base + ".exp.como") or valor(ficha, base + ".exp.degrau"))
    if not liberacoes and not maxima and not dominio:
        return
    if valor(ficha, base + ".tipo") != "Maldição domada":
        erro(base + ".tipo", "somente maldição domada com técnica própria pode ter trunfos", "campo--inv-liberacao")
        return
    r.nao_conferido.append(f"{nome}: técnica própria da domada, peças e escolhas dos trunfos em texto precisam de conferência; custos não aprovam a montagem")
    for b in liberacoes + ([base + ".tm"] if maxima else []) + ([base + ".exp"] if dominio else []):
        if not valor(ficha, b + ".nome"):
            r.pendencias.append(Problema("escolha", b + ".nome", "nome do trunfo", ""))
    if len(liberacoes) > nivel // 10:
        erro(base + ".liberacao", f"até {nivel // 10} Liberação(ões) pelo nível fixo da domada", "campo--inv-liberacao")
    for b in liberacoes:
        c = valor(ficha, b + ".classe")
        if not inteiro(c, 3, magia.classe_maxima(nivel)):
            erro(b + ".classe", f"Classe 3 até {magia.classe_maxima(nivel)}", "campo--inv-liberacao")
            continue
        comparar(b + ".pe", math.ceil(4.5 * c), "campo--inv-liberacao", pe=True)
        comparar(b + ".pontos", f"{magia.especiais[c]} pontos + {c}d8", "campo--inv-liberacao")
        comparar(b + ".acao", "Sua Ação Completa + a básica dela", "campo--inv-liberacao")
    if maxima:
        b = base + ".tm"
        if nivel not in regras.maximas:
            erro(b + ".nome", "Técnica Máxima a partir do nível 17 da domada", "campo--inv-maxima")
        else:
            dados, pontos, pe = regras.maximas[nivel]
            comparar(b + ".pe", pe, "campo--inv-maxima", pe=True)
            comparar(b + ".dados", f"{dados}d8 fixos · {pontos} pontos", "campo--inv-maxima")
            comparar(b + ".acao", "Sua Ação Completa + a básica dela", "campo--inv-maxima")
    if not dominio:
        return
    b, ancora = base + ".exp", "campo--inv-dominio"
    degrau = valor(ficha, b + ".degrau")
    req = regras.dominios.get(degrau)
    if req is None:
        r.pendencias.append(Problema("escolha", b + ".degrau", "degrau de Domínio do livro", str(degrau), ancora))
        return
    custo, minimo, rf, especializacao = req
    marcos_refino = valor(ficha, "marco.refino")
    if nivel < minimo:
        erro(b + ".degrau", f"nível {minimo}+ da domada", ancora)
    if not inteiro(marcos_refino, 0, sum(n <= dono for n in ref.marcos)):
        r.nao_conferido.append(f"{nome}: Domínio depende das escolhas válidas de Refino do dono")
    elif refino(dono, marcos_refino, ref) < rf:
        erro(b + ".degrau", f"Refino {rf}+ do invocador", ancora)
    if especializacao:
        r.nao_conferido.append(f"{nome}: Sem Barreiras exige especialização em Ocultismo do dono; conferência de perícias fica para a próxima etapa")
    especiais = sum(".esp." in c for c in cartas)
    capacidade = 1 + nivel // 4
    if especiais + custo > capacidade:
        erro(b + ".degrau", f"especiais + {custo} espaços do Domínio até {capacidade}", ancora)
    elif all(base + f".esp.{i}.nome" in ficha for i in range(1, 9)):
        r.conferidos.append(f"{nome}: especiais e Domínio ocupam {especiais + custo} de {capacidade} vagas normais")
    else:
        r.nao_conferido.append(f"{nome}: faltam posições de especiais para fechar a ocupação com Domínio")
    c = magia.classe_maxima(nivel)
    comparar(b + ".pe", (7 if degrau == "Sem Barreiras" else 6) * c, ancora, pe=True)
    livres, abertas = familias
    if livres is None or abertas is None:
        r.nao_conferido.append(f"{nome}: Acerto de Domínio depende das Famílias válidas")
        return
    p = magia.melhorias["Inescapável"]
    texto = str(valor(ficha, b + ".acerto"))
    if not re.fullmatch(r"Acerto \d+d8", texto):
        r.nao_conferido.append(f"{nome}: Acerto não numérico/ausente exige efeito de Domínio escrito e delimitado; não convertido em dano")
        return
    preco = max(1, c - (max(1, c // 2) if p.familia in livres else 0))
    comparar(b + ".acerto", f"Acerto {magia.especiais[c] - preco}d8", ancora)
    r.nao_conferido.append(f"{nome}: Acerto numérico compatível não define o tipo do Domínio; conferir dano/informação/regra de ambiente e permissões no texto")
