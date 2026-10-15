"""Aquisição e capacidade do repertório pelo livro, sem usar os totais da ficha.

As posições 1–5 de passiva são pagas, 6–12 são de Leque no contrato atual.
Concessões de Origem sem posição própria são tratadas por possibilidades, sem
inventar qual Talento foi recebido gratuitamente nem converter aplicações em vagas.
"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Repertorio:
    progressao: dict
    talentos: dict
    dominios: dict

    @classmethod
    def do_livro(cls, livro):
        progressao = {}
        for a in ("progressao--prog-tabela-inicial", "progressao--prog-tabela-avancada"):
            for linha in livro[a].splitlines():
                v = re.fullmatch(r"\| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", linha)
                if v:
                    nivel, maestria, espacos, refino, classe, ce, zero = map(int, v.groups())
                    progressao[nivel] = (espacos, ce)
        talentos = {}
        for a, ce in (("catalogo--cat-passivas-1", 1), ("catalogo--cat-passivas-2-recursos", 2),
                      ("catalogo--cat-passivas-2-protecao", 2), ("catalogo--cat-passivas-3", 3)):
            for n in re.findall(r"^#### (.+)$", livro[a], re.M):
                talentos[n] = (ce, a)
        for a in ("rotas--rota-passivas-marciais", "rotas--rota-passivas-resposta"):
            for n, ce in re.findall(r"^##### ([^\n]+)\n\n\*\*Categoria de Efeito: ([123])\.\*\*", livro[a], re.M):
                talentos[n] = (int(ce), a)
        dominios, nivel_anterior, refino_anterior = {}, 0, 0
        for n, c, req in re.findall(r"^\| (Incompleta|Completa|Sem Barreiras) \| (\d+) \| ([^|]+) \|", livro["poderes--degraus"], re.M):
            nv = re.search(r"[Nn]ível (\d+)", req)
            rf = re.search(r"refino (\d+)", req)
            nivel_anterior = max(nivel_anterior, int(nv[1]) if nv else 0)
            refino_anterior = max(refino_anterior, int(rf[1]) if rf else 0)
            dominios[n] = (int(c), nivel_anterior, refino_anterior, "especialização em Ocultismo" in req)
        guardas = {"fundamento--repertorio": "2 + metade do nível", "fundamento--selo": "máximo é cinco Talentos pagos",
                   "progressao--prog-marcos": "não uma vaga livre para comprar Talento",
                   "catalogo--cat-regra-propria": "Ao melhorar de Categoria de Efeito 2 para 3",
                   "origens--latente-beneficios": "Manifestação Instintiva", "origens--receptaculo-excecoes": "Traço Incorporado",
                   "origens--corpo-ninhada-gemeos": "Construção Especializada",
                   "origens--origem-receptaculo": "dois feitiços adicionais",
                   "origens--restricao-menores-corporais": "Prática Cotidiana",
                   "catalogo--cat-passivas-3": "PE máximo aumenta em 3 × sua maior Classe",
                   "catalogo--cat-mira": "+2 no ataque ou +2 na CD"}
        if (set(progressao) != set(range(1, 31)) or len(talentos) != 20 or len(dominios) != 3
                or any(t not in livro[a] for a, t in guardas.items())):
            raise ValueError("o livro mudou a aquisição do repertório: revise o corretor")
        return cls(progressao, talentos, dominios)


def origem(ficha):
    from .ficha_magia import valor
    partes = str(valor(ficha, "origem")).split(" · ", 1)
    return partes[0], partes[1] if len(partes) == 2 else ""


def zeros_adicionais(ficha):
    from .ficha_magia import valor
    return 2 if origem(ficha) == ("Restrição Celestial", "Restrição corporal") and "Prática Cotidiana" in (
        valor(ficha, "origem.menor_1"), valor(ficha, "origem.menor_2")) else 0


def conferir_repertorio(ficha, ref, r):
    from .ficha_corretor import Problema, refino
    from .ficha_magia import ativa, bases, inteiro, valor
    if ref.magia is None:
        return
    regras = ref.magia.repertorio
    nivel = valor(ficha, "nivel")
    if not inteiro(nivel, 1):
        r.nao_conferido.append("repertório: falta nível válido")
        return
    inicio = len(r.problemas)
    incerto = False
    def erro(k, esperado, ancora="fundamento--repertorio"):
        r.problemas.append(Problema("conta", k, esperado, str(valor(ficha, k)), ancora))
    def comparar(k, n, ancora):
        if k not in ficha:
            r.nao_conferido.append(f"repertório: resultado {k} não exportado")
        elif (valor(ficha, k) != n and not (n == 0 and valor(ficha, k) == "De graça")) or isinstance(valor(ficha, k), bool):
            erro(k, str(n), ancora)
        else:
            r.conferidos.append(f"Repertório: capacidade {n} espaços" if k == "espacos_de_feitico" else f"Regra Própria: {n} espaços ocupados")
    espacos, teto_ce = regras.progressao[nivel]
    comparar("espacos_de_feitico", espacos, "fundamento--repertorio")
    marcos = sum(n <= nivel for n in ref.marcos)
    escolhas = {}
    for k in ("corpo", "refino", "leque"):
        chave = "marco." + k
        v = valor(ficha, chave)
        if chave not in ficha:
            escolhas[k] = None
        elif not inteiro(v, 0, marcos):
            erro(chave, f"inteiro de 0 a {marcos}", "progressao--prog-marcos")
            escolhas[k] = None
        else:
            escolhas[k] = v
    if all(v is not None for v in escolhas.values()) and sum(escolhas.values()) > marcos:
        erro("marco.leque", f"Corpo + Refino + Leque até {marcos} escolhas", "progressao--prog-marcos")
        escolhas["leque"] = None
    leque = escolhas["leque"]
    if leque is None:
        incerto = True
        r.nao_conferido.append("repertório: concessões de Leque dependem de escolhas de marco válidas")
    base_origem, variante = origem(ficha)
    rota = ("Sem Técnica" if variante == "Sem Técnica" and base_origem in ref.aceitam_sem_tecnica else
            "Técnica Marcial com energia" if base_origem == "Corpo Amaldiçoado" else
            "Técnica Marcial sem energia" if (base_origem, variante) == ("Restrição Celestial", "Sem Energia") else "Fundamento")
    origem_valida = base_origem in ref.origens and (variante == "" and base_origem != "Restrição Celestial"
        or variante == "Sem Técnica" and base_origem in ref.aceitam_sem_tecnica
        or base_origem == "Restrição Celestial" and variante in ref.ramos_restricao)
    if not origem_valida:
        incerto = True
    if origem_valida and "tecnica.rota.nome" in ficha and valor(ficha, "tecnica.rota.nome") != rota:
        erro("tecnica.rota.nome", rota, "origens--origens")
    # Não usamos o texto explicativo da menor como prova de uma concessão.
    menores = {valor(ficha, "origem.menor_1"), valor(ficha, "origem.menor_2")}
    concessao = {"Latente": "Manifestação Instintiva", "Receptáculo": "Traço Incorporado",
                 "Corpo Amaldiçoado": "Construção Especializada"}.get(base_origem)
    gratuita = bool(concessao and concessao in menores)
    extras = 2 if base_origem == "Receptáculo" and valor(ficha, "origem.marcante") == "Coexistência" else 0
    if valor(ficha, "origem.ce4"):
        if (base_origem, variante) != ("Restrição Celestial", "Restrição corporal"):
            erro("origem.ce4", "CE4 exclusivo da Restrição corporal", "origens--restricao-ce4")
        else:
            r.nao_conferido.append("CE4 da Origem: fora dos espaços/pagos; efeito e permissão precisam de conferência do mestre")

    talentos = []
    for k in sorted((k for k in ficha if re.fullmatch(r"passiva\.\d+", k)), key=lambda k: int(k.split(".")[1])):
        antes_talento = (len(r.problemas), len(r.pendencias))
        nome = str(valor(ficha, k))
        if not nome:
            if valor(ficha, k + ".texto"):
                r.pendencias.append(Problema("escolha", k, "nome do Talento", ""))
                incerto = True
            continue
        n = int(k.split(".")[1])
        if not 1 <= n <= 12:
            erro(k, "posição de Talento de 1 a 12 do contrato ANALISE", "fundamento--selo")
            incerto = True
        conhecido = regras.talentos.get(nome)
        propria = re.fullmatch(r"Talento Próprio \(CE ([123])\)", nome)
        ce = conhecido[0] if conhecido else int(propria[1]) if propria else valor(ficha, k + ".categoria")
        ancora = conhecido[1] if conhecido else "catalogo--cat-passiva-propria"
        if ce == "":
            r.pendencias.append(Problema("escolha", k + ".categoria", "Categoria do Talento", ""))
            incerto = True
            continue
        if not inteiro(ce, 1, 3):
            erro(k + ".categoria", "CE 1, 2 ou 3; CE4 usa o campo próprio da Origem", "fundamento--selo")
            incerto = True
            continue
        if k + ".categoria" in ficha and valor(ficha, k + ".categoria") == "":
            r.pendencias.append(Problema("escolha", k + ".categoria", "Categoria do Talento", ""))
            incerto = True
        elif k + ".categoria" in ficha and (valor(ficha, k + ".categoria") != ce or isinstance(valor(ficha, k + ".categoria"), bool)):
            erro(k + ".categoria", str(ce), ancora)
        if ce > teto_ce:
            erro(k, f"Talento até CE {teto_ce} no nível {nivel}", ancora)
        if not conhecido:
            incerto = True
            r.nao_conferido.append(f"Talento {n}: {nome}, CE {ce}; aprovação de conteúdo próprio aguarda CONFIGURAÇÃO")
        elif antes_talento == (len(r.problemas), len(r.pendencias)):
            r.conferidos.append(f"Talento {n}: {nome}, CE {ce} (categoria e nível atual)")
        talentos.append((n, nome, ce, bool(conhecido)))
    if talentos:
        r.nao_conferido.append("Talentos: compatibilidade com a técnica e textos personalizados ainda exigem conferência")

    # A Origem não tem posição própria na lista antiga. Só opções CE1 sem duplicação
    # podem representar essa concessão, e a vinculação permanece revisão manual.
    origens_possiveis = [None]
    if gratuita:
        incerto = True
        origens_possiveis += [n for n, nome, ce, conhecido in talentos if ce == 1 and conhecido
                             and sum(t[1] == nome for t in talentos) == 1]
        r.nao_conferido.append("Talento gratuito da Origem: falta vinculação estruturada da escolha; conta por possibilidades, sem certificar a aquisição")
    custos_talentos = []
    for isento in origens_possiveis:
        pagos = [t for t in talentos if t[0] <= 5 and t[0] != isento]
        ganhos = [t for t in talentos if t[0] > 5 and t[0] != isento]
        if len(ganhos) <= (leque if leque is not None else marcos):
            custos_talentos.append(sum(t[2] for t in pagos))
    if not custos_talentos:
        erro("marco.leque", f"Talentos de Leque até {leque if leque is not None else marcos}, além de eventual CE1 da Origem", "progressao--prog-marcos")
        incerto = True

    categoria = valor(ficha, "tecnica.regra_propria.categoria")
    regra_custo = 0
    if categoria != "":
        if not inteiro(categoria, 1, 3):
            erro("tecnica.regra_propria.categoria", "CE 1, 2 ou 3", "catalogo--cat-regra-propria")
            incerto = True
        else:
            regra_custo = categoria - 1
            if categoria > teto_ce:
                erro("tecnica.regra_propria.categoria", f"até CE {teto_ce} no nível {nivel}", "catalogo--cat-regra-propria")
            comparar("tecnica.regra_propria.espacos", regra_custo, "catalogo--cat-regra-propria")
            r.nao_conferido.append("Regra Própria: custo não aprova o texto; aprovação aguarda CONFIGURAÇÃO")
    elif valor(ficha, "tecnica.regra_propria.texto"):
        r.pendencias.append(Problema("escolha", "tecnica.regra_propria.categoria", "Categoria da Regra Própria", ""))
        incerto = True

    dominio_custo = 0
    degrau = valor(ficha, "dominio.degrau")
    if degrau:
        if degrau not in regras.dominios:
            erro("dominio.degrau", "degrau do livro", "poderes--degraus")
            incerto = True
        else:
            dominio_custo, nv, rf, precisa_ocultismo = regras.dominios[degrau]
            if rota != "Fundamento":
                erro("dominio.degrau", "Expansão exclusiva da rota Fundamento", "poderes--degraus")
            # Requisitos cumulativos: o terceiro degrau conserva nível 14 da Completa.
            if nivel < nv:
                erro("dominio.degrau", f"nível mínimo {nv}", "poderes--degraus")
            if escolhas["refino"] is None:
                incerto = True
                r.nao_conferido.append("Domínio: falta escolha válida de Refino para conferir o requisito")
            elif refino(nivel, escolhas["refino"], ref) < rf:
                erro("dominio.degrau", f"Refino mínimo {rf}", "poderes--degraus")
            if precisa_ocultismo and any(valor(ficha, k) != 1 or isinstance(valor(ficha, k), bool) for k in ("pericia.ocultismo.treino", "pericia.ocultismo.especialista")):
                erro("dominio.degrau", "treino e especialização em Ocultismo", "poderes--degraus")
            custo = valor(ficha, "dominio.custo")
            if "dominio.custo" in ficha and custo != dominio_custo and custo != f"{dominio_custo} espaços":
                erro("dominio.custo", f"{dominio_custo} espaços no total", "poderes--degraus")
            r.nao_conferido.append("Domínio: requisitos e espaços não conferem Acerto/Efeito, aplicação ou histórico dos degraus")
    elif valor(ficha, "dominio.nome") or valor(ficha, "dominio.texto"):
        r.pendencias.append(Problema("escolha", "dominio.degrau", "degrau do Domínio", ""))
        incerto = True

    entidades = []
    for b in bases(ficha, r"invocacao\.\d+"):
        cartas = any(ativa(ficha, c) for c in bases(ficha, re.escape(b) + r"\.(?:bas|esp|ext)\.\d+"))
        if not valor(ficha, b + ".nome") and not cartas:
            continue
        aquisicao = valor(ficha, b + ".aquisicao")
        if aquisicao == "Espaço conhecido":
            entidades.append(b)
        elif aquisicao not in ref.magia.aquisicoes:
            incerto = True
    if entidades:
        r.nao_conferido.append("Invocações por espaço: conferir se a Regra/Descrição prevê criar, chamar ou controlar entidades")

    # A ausência de posições pode ocultar escolhas e impede afirmar um total completo.
    necessarias = {f"passiva.{n}" for n in range(1, 13)} | {f"feitico.{n}.nome" for n in range(1, 37)}
    necessarias |= {f"invocacao.{n}.nome" for n in range(1, 13)}
    origem_chaves = {"origem", "origem.marcante", "origem.menor_1", "origem.menor_2"}
    necessarias |= {"tecnica.regra_propria.categoria", "dominio.degrau", "marco.corpo", "marco.refino", "marco.leque"} | origem_chaves
    if not necessarias <= ficha.keys():
        incerto = True
        r.nao_conferido.append("repertório: faltam posições/entradas para certificar o total completo")
    if not origem_valida or not origem_chaves <= ficha.keys():
        r.nao_conferido.append("repertório: concessões da Origem incompletas impedem fechar a conta")
        return
    feiticos = sum(ativa(ficha, b) for b in bases(ficha, r"feitico\.\d+"))
    aplicacoes = (leque or 0) + extras
    gastos = {c + regra_custo + dominio_custo + len(entidades) + max(0, feiticos - aplicacoes) for c in custos_talentos}
    # A falta de Leque pode esconder até os demais marcos; não transforma zero em certeza.
    if leque is None:
        gastos = {c + regra_custo + dominio_custo + len(entidades) + max(0, feiticos - marcos - extras) for c in custos_talentos}
    if gastos and min(gastos) > espacos:
        erro("repertorio", f"até {espacos} espaços; mínimo ocupado {min(gastos)}", "fundamento--repertorio")
    elif len(gastos) == 1 and not incerto and len(r.problemas) == inicio:
        r.conferidos.append(f"Repertório: {next(iter(gastos))} de {espacos} espaços comuns ocupados; {aplicacoes} aplicações gratuitas disponíveis")
    elif gastos:
        r.nao_conferido.append("repertório: conta parcial por possibilidades; concessões/custos incompletos não certificam o total")
