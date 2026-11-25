"""Planeja o preenchimento da ficha criada: identidade, atributos, Origem, Caminho e treinos.

Só planeja. Recebe o que foi lido da cópia e devolve as células a escrever; nada aqui fala com o
Google. A escrita pela API não dispara o onEdit da ficha, então o que o script dela faz na escolha
do Caminho e da Trilha está repetido aqui e comparado com o original nos testes. Células, cartas e
treinos vêm de criacao_mapa.json, gerado por ferramentas/gerar_criacao_mapa.js.
"""
from dataclasses import dataclass, field
import json
from pathlib import Path
import re

MAPA = json.loads((Path(__file__).parent / "criacao_mapa.json").read_text(encoding="utf-8"))
PESSOAL, PROGRESSAO = "FICHA PESSOAL", "DADOS_PROGRESSAO"
FAIXAS = ("CARTEIRA!O8:AK22", "FICHA!D8:AS205", "'FICHA PESSOAL'!D10:AT87", "DADOS_PROGRESSAO!M2:V7",
          "DADOS_PROGRESSAO!AA2:AB21", "DADOS_PROGRESSAO!CB2:CC10", "DADOS_CONFIG!S2:S8",
          "DADOS_CUSTOM!CP2:CS160")
SEM_CAMINHO, SEM_TRILHA = "Escolha seu Caminho", "Escolha sua Trilha"
TROCAS = {0: "Não trocou", 1: "1 arma (-2 pericias)", 2: "2 armas (-4 pericias)"}
CURTOS = {"nome", "jogador", "idade", "altura", "olhos", "cabelo", "pele", "genero"}
CELULA = re.compile(r"([A-Z]{1,3})([1-9][0-9]{0,4})")


class Recusa(ValueError):
    """A ficha não permite esta escolha. Os textos vão pro jogador."""
    def __init__(self, *motivos):
        super().__init__(" ".join(motivos))
        self.motivos = motivos


class JaPreenchido(Recusa):
    """Há um valor do jogador na célula; só troca com a confirmação dele."""
    def __init__(self, campos):
        super().__init__("Estes campos já têm um valor na ficha: " + ", ".join(campos) + ".")
        self.campos = tuple(campos)


@dataclass(frozen=True)
class Escrita:
    aba: str
    celula: str
    valor: str | int | bool | None       # None só mexe na nota
    nota: str | None = None              # None não mexe na nota
    negritos: tuple = ()


@dataclass
class Plano:
    escritas: list = field(default_factory=list)
    alturas: dict = field(default_factory=dict)   # {(aba, linha): pixels}
    avisos: list = field(default_factory=list)


def posicao(celula):
    m = CELULA.fullmatch(celula)
    if not m:
        raise ValueError("Célula inválida.")
    coluna = 0
    for letra in m[1]:
        coluna = coluna * 26 + ord(letra) - 64
    return int(m[2]), coluna


def _letras(coluna):
    s = ""
    while coluna:
        coluna, resto = divmod(coluna - 1, 26)
        s = chr(65 + resto) + s
    return s


class Leitura:
    """Valores de values:batchGet (UNFORMATTED_VALUE) endereçáveis por aba e célula."""
    def __init__(self, resposta):
        self.v = {}
        for faixa in resposta["valueRanges"]:
            aba, _, a1 = faixa["range"].rpartition("!")
            aba = aba.strip("'")
            l1, c1 = posicao(a1.split(":")[0])
            for y, linha in enumerate(faixa.get("values", [])):
                for x, valor in enumerate(linha):
                    self.v[aba, l1 + y, c1 + x] = valor

    def de(self, aba, celula):
        return self.v.get((aba, *posicao(celula)), "")

    def faixa(self, aba, a1):
        (l1, c1), (l2, c2) = map(posicao, a1.split(":"))
        return [[self.v.get((aba, y, x), "") for x in range(c1, c2 + 1)] for y in range(l1, l2 + 1)]


def conferir(lido):
    """Rótulos fora do lugar: a ficha não é a que o mapa conhece e nada pode ser escrito."""
    esperado = [(c["aba"], c["rotulo"], c["texto_rotulo"]) for c in MAPA["identidade"] + MAPA["escolhas"]]
    esperado += [("FICHA", a["rotulo"], a["nome"]) for a in MAPA["atributos"]]
    esperado += [("FICHA", m["rotulo"], m["nome"]) for k in ("pericias", "oficios", "testes") for m in MAPA[k]]
    fora = [f"{aba}!{cel}" for aba, cel, texto in esperado if str(lido.de(aba, cel)).strip() != texto]
    caixas = [m["caixa"] for k in ("pericias", "oficios", "testes") for m in MAPA[k]]
    fora += [f"FICHA!{c}" for c in caixas if type(lido.de("FICHA", c)) is not bool]
    fora += [f"{PESSOAL}!{c['caixa']}" for c in MAPA["treino"]["caixas"] if type(lido.de(PESSOAL, c["caixa"])) is not bool]
    return fora


def _texto(valor, limite):
    if type(valor) is not str:
        raise Recusa("Texto inválido.")
    valor = valor.replace("\r\n", "\n").strip()
    if len(valor) > limite or re.search("[\x00-\x09\x0b-\x1f\x7f]", valor):
        raise Recusa(f"O texto precisa ter até {limite} caracteres.")
    return valor


def _campos(grupo, lido, novos, confirmados):
    """Valida chaves e conflitos; devolve [(campo, valor)] só do que muda."""
    por_chave = {c["chave"]: c for c in MAPA[grupo]}
    if not set(novos) <= set(por_chave):
        raise Recusa("Campo desconhecido.")
    muda, conflito = [], []
    for chave, valor in novos.items():
        c = por_chave[chave]
        atual = lido.de(c["aba"], c["celula"])
        if str(atual) == str(valor):
            continue
        if atual not in ("", c["fabrica"]) and chave not in confirmados:
            conflito.append(chave)
        muda.append((c, valor))
    if conflito:
        raise JaPreenchido(conflito)
    return muda


def linhas_do_texto(texto, largura):
    m = MAPA["metrica"]
    larguras, espaco = m["larguras"], m["larguras"][" "]
    n = 0
    for paragrafo in texto.split("\n"):
        n += 1
        linha = None
        for palavra in filter(None, paragrafo.split(" ")):
            w = sum(larguras.get(u, m["media"]) for u in _utf16(palavra))
            if linha is None:
                linha = w
            elif linha + espaco + w <= largura:
                linha += espaco + w
            else:
                n += 1
                linha = w
    return n


def _utf16(texto):
    """Unidades UTF-16, como o JavaScript da ficha mede o texto."""
    bruto = texto.encode("utf-16-le")
    return [chr(int.from_bytes(bruto[i:i + 2], "little")) for i in range(0, len(bruto), 2)]


def alturas_que_esticam(grupo, textos):
    m = MAPA["metrica"]
    h = {c["linha"] + k: m["minima"] for c in grupo for k in range(c["linhas"])}
    for c, texto in zip(grupo, textos):
        if not texto:
            continue
        pede = linhas_do_texto(texto, c["largura"]) * m["linha"] + m["respiro"] - c["folga"]
        linhas = range(c["linha"], c["linha"] + c["linhas"])
        tem = sum(h[k] for k in linhas)
        if pede > tem:
            mais = -int(-(pede - tem) // c["linhas"])
            for k in linhas:
                h[k] += mais
    return h


def _esticar(plano, nome, lido, novos=None):
    novos = novos or {}
    grupo = MAPA["esticam"][nome]
    textos = [" · ".join(t for t in (str(novos.get(a, lido.de(PESSOAL, a))) for a in c["celulas"]) if t) for c in grupo]
    plano.alturas |= {(PESSOAL, k): v for k, v in alturas_que_esticam(grupo, textos).items()}


def identidade(lido, novos, confirmados=()):
    limpos = {k: _texto(v, 100 if k in CURTOS else 4000) for k, v in novos.items()}
    plano = Plano()
    muda = _campos("identidade", lido, limpos, confirmados)
    for c, valor in muda:
        plano.escritas.append(Escrita(c["aba"], c["celula"], valor or c["fabrica"]))
    if any(c["aba"] == PESSOAL for c, _ in muda):
        _esticar(plano, "identidade", lido, {e.celula: e.valor for e in plano.escritas if e.aba == PESSOAL})
    return plano


def limites(lido):
    nomes = ("nivel_inicial", "pontos", "teto_criacao", "teto", "pericias_com_oficio", "oficios", "pericias_sem_oficio")
    v = [linha[0] for linha in lido.faixa("DADOS_CONFIG", "S2:S8")]
    if any(type(x) not in (int, float) or x != int(x) for x in v):
        raise Recusa("A CONFIGURAÇÃO da ficha tem um número inválido. Confira as regras de campanha.")
    return dict(zip(nomes, map(int, v)))


def na_criacao(lido):
    """A ficha ainda está no nível em que a campanha começa."""
    return str(lido.de("FICHA", MAPA["leituras"]["nivel"])) == str(limites(lido)["nivel_inicial"])


def _so_na_criacao(lido):
    if not na_criacao(lido):
        raise Recusa("Essa ficha já passou do nível inicial. O que muda ao subir de nível se preenche na planilha.")


def atributos(lido, novos, confirmados=()):
    _so_na_criacao(lido)
    celulas = {a["nome"]: a["celula"] for a in MAPA["atributos"]}
    if set(novos) != set(celulas) or any(type(v) is not int for v in novos.values()):
        raise Recusa("Preencha os cinco atributos com números inteiros.")
    lim, erros = limites(lido), []
    if any(v < 0 or v > lim["teto_criacao"] for v in novos.values()):
        erros.append(f"Na criação, cada atributo vai de 0 a {lim['teto_criacao']}.")
    total = sum(novos.values())
    if total > lim["pontos"]:
        erros.append(f"São {lim['pontos']} pontos; você usou {total}.")
    if erros:
        raise Recusa(*erros)
    mexidos = [n for n, c in celulas.items() if lido.de("FICHA", c) not in ("", 0, novos[n])]
    if mexidos and "atributos" not in confirmados:
        raise JaPreenchido(mexidos)
    plano = Plano([Escrita("FICHA", c, novos[n]) for n, c in celulas.items() if lido.de("FICHA", c) != novos[n]])
    if total < lim["pontos"]:
        resta = lim["pontos"] - total
        plano.avisos.append("Sobra 1 ponto de atributo." if resta == 1 else f"Sobram {resta} pontos de atributo.")
    return plano


def menus(lido):
    """Opções que a própria cópia oferece agora. Marcante e menores seguem a Origem escrita nela."""
    def coluna(aba, a1, pular=()):
        return [x for x in dict.fromkeys(str(linha[0]).strip() for linha in lido.faixa(aba, a1)) if x and x not in pular]
    trilhas = {}
    for trilha, caminho in lido.faixa(PROGRESSAO, "AA2:AB21"):
        if trilha and caminho:
            trilhas.setdefault(caminho, []).append(trilha)
    return dict(origem=coluna("DADOS_CUSTOM", "CS2:CS39"), marcante=coluna("DADOS_CUSTOM", "CP2:CP160"),
                menor=coluna("DADOS_CUSTOM", "CQ2:CQ160"), caminho=coluna(PROGRESSAO, "M2:M7"), trilhas=trilhas)


def origem(lido, nome, confirmados=()):
    if nome not in menus(lido)["origem"]:
        raise Recusa("Essa Origem não está no menu da ficha.")
    muda = _campos("escolhas", lido, {"origem": nome}, confirmados)
    plano = Plano([Escrita(c["aba"], c["celula"], v) for c, v in muda])
    if plano.escritas:
        presas = [c["chave"] for c in MAPA["escolhas"] if c["chave"] in ("marcante", "menor1", "menor2") and lido.de(c["aba"], c["celula"])]
        if presas:
            plano.avisos.append("Confira a marcante e as menores: elas dependem da Origem.")
    return plano


def capacidades(lido, novos, confirmados=(), a_mao=()):
    """Marcante e menores pelos menus. Chamar com uma leitura feita depois de escrever a Origem.

    A altura das caixas sai em altura_capacidades(), porque o texto delas é fórmula. `a_mao` são as
    caixas em que o jogador escreveu por cima da fórmula: quem a devolve é o script da ficha, e só
    na escolha feita na planilha."""
    if not set(novos) <= {"marcante", "menor1", "menor2"}:
        raise Recusa("Campo desconhecido.")
    m = menus(lido)
    for chave, valor in novos.items():
        if valor not in m["marcante" if chave == "marcante" else "menor"]:
            raise Recusa("Essa capacidade não está no menu da ficha pra sua Origem.")
    final = {c["chave"]: novos.get(c["chave"], lido.de(c["aba"], c["celula"])) for c in MAPA["escolhas"]}
    if final["menor1"] and final["menor1"] == final["menor2"] and not str(final["menor1"]).startswith("✎"):
        raise Recusa("As duas menores precisam ser diferentes.")
    muda = _campos("escolhas", lido, novos, confirmados)
    if any(c["chave"] in a_mao and not v.startswith("✎") for c, v in muda):
        raise Recusa("Há um texto escrito à mão na caixa dessa capacidade. Troque o menu na planilha, "
                     "que aí a ficha traz o texto do livro.")
    plano = Plano([Escrita(c["aba"], c["celula"], v) for c, v in muda])
    if any(str(v).startswith("✎") for v in novos.values()):
        plano.avisos.append("Capacidade criada com o mestre: escreva o texto na FICHA PESSOAL e confirme com ele.")
    return plano


def altura_capacidades(lido):
    plano = Plano()
    _esticar(plano, "capacidades", lido)
    return plano


def notas_vivas(lido):
    """Notas da FICHA PESSOAL cujo texto é fórmula da DADOS. Chamar com uma leitura depois da escrita."""
    return Plano([Escrita(PESSOAL, str(caixa), None, str(texto)) for texto, caixa in lido.faixa("DADOS", "DL5:DM9")
                  if CELULA.fullmatch(str(caixa))])


def _treino(caminho, todas):
    return {c["caixa"]: caminho in todas or c["categoria"] in MAPA["treino"]["conjurador"] for c in MAPA["treino"]["caixas"]}


def _cartas(lido, caminho, trilha):
    livro = {(h["fonte"], h["dono"], h["nivel"]): h for h in MAPA["livro"]}
    autos = lido.faixa(PROGRESSAO, "CB2:CC10")
    for carta, auto in zip(MAPA["cartas"], autos):
        fontes = ("Caminho com a Trilha", "Caminho") if carta["fonte"] == "Caminho" else ("Trilha",)
        if carta["fonte"] == "Caminho":
            h = livro.get((fontes[0], trilha, carta["nivel"])) or livro.get((fontes[1], caminho, carta["nivel"]))
        else:
            h = livro.get(("Trilha", trilha, carta["nivel"]))
        conhecidas = [x for x in MAPA["livro"] if x["fonte"] in fontes and x["nivel"] == carta["nivel"]]
        novo = dict(nome=h["nome"], texto=h["texto"]) if h else dict(nome="", texto="")
        fica = {}
        for n, k in enumerate(("nome", "texto")):
            atual = str(lido.de("FICHA", carta[k]))
            automaticos = [x[k] for x in conhecidas] + [str(auto[n])]
            fica[k] = novo[k] if atual == "" or atual in automaticos else atual
        yield carta, novo, fica, h


def caminho(lido, escolhido, trilha=None, confirmados=()):
    """Caminho e Trilha, com tudo que o script da ficha faria. `trilha=None` mantém a que couber."""
    m = menus(lido)
    if escolhido not in m["caminho"]:
        raise Recusa("Esse Caminho não está no menu da ficha. Caminho próprio da mesa: escolha na planilha.")
    campos = {c["chave"]: c for c in MAPA["escolhas"]}
    antes = lido.de("FICHA", campos["caminho"]["celula"])
    trilha_antes = lido.de("FICHA", campos["trilha"]["celula"])
    if trilha is None:
        trilha = trilha_antes if trilha_antes in m["trilhas"].get(escolhido, []) else SEM_TRILHA
    elif trilha != SEM_TRILHA and trilha not in m["trilhas"].get(escolhido, []):
        raise Recusa("Essa Trilha não é desse Caminho.")
    novos = {"caminho": escolhido}
    # A Trilha que sai porque é de outro Caminho não é conflito: o script da ficha também a limpa.
    if trilha_antes in m["trilhas"].get(escolhido, []):
        novos["trilha"] = trilha
    _campos("escolhas", lido, novos, confirmados)
    plano = Plano()

    def poe(aba, celula, valor, nota=None, negritos=()):
        if lido.de(aba, celula) != valor or nota is not None:
            plano.escritas.append(Escrita(aba, celula, valor, nota, tuple(map(tuple, negritos))))

    poe("FICHA", campos["caminho"]["celula"], escolhido)
    poe("FICHA", campos["trilha"]["celula"], trilha)
    if antes != escolhido:
        tabela = {l[0]: [p for p in l[5:7] if p] for l in lido.faixa(PROGRESSAO, "M2:S7")}
        caixas = {p["nome"]: p["caixa"] for p in MAPA["pericias"]}
        fixas = tabela[escolhido]
        if not set(fixas) <= set(caixas):
            raise Recusa("As perícias fixas desse Caminho não estão na ficha.")
        for p in tabela.get(antes, []):
            if p not in fixas and p in caixas:
                poe("FICHA", caixas[p], False, "")
        for p in fixas:
            poe("FICHA", caixas[p], True, "Treinado pelo Caminho " + escolhido)
        todas = {l[0] for l in lido.faixa(PROGRESSAO, "M2:V7") if l[9] == "Todas"}
        for caixa, marcada in _treino(escolhido, todas).items():
            poe(PESSOAL, caixa, marcada)
        poe("FICHA", MAPA["troca_arma"]["celula"], TROCAS[0])
    for carta, novo, fica, h in _cartas(lido, escolhido, trilha):
        poe("FICHA", carta["nome"], fica["nome"])
        nota = novo["texto"] if novo["texto"] and fica["texto"] != novo["texto"] else ""
        mudou = fica["texto"] != str(lido.de("FICHA", carta["texto"]))
        if mudou or nota:
            poe("FICHA", carta["texto"], fica["texto"], nota, h["negritos"] if h and mudou and fica["texto"] == h["texto"] else ())
        if mudou:
            altura = h["altura"] if h else MAPA["altura_vazia"]
            plano.alturas |= {("FICHA", carta["linha"] + k): altura for k in range(MAPA["linhas_da_carta"])}
    for n, (carta, novo, fica, h) in enumerate(_cartas(lido, escolhido, trilha)):
        poe(PROGRESSAO, f"CB{n + 2}", novo["nome"])
        poe(PROGRESSAO, f"CC{n + 2}", novo["texto"])
    categoria = MAPA["trilhas_categoria"].get(trilha)
    if categoria and trilha != trilha_antes:
        plano.avisos.append(f"{trilha}: combine a categoria de arma ({categoria[1]}) e escreva na FICHA.")
        if categoria[0] == escolhido and lido.de("FICHA", MAPA["categoria_trilha"]) == "":
            poe("FICHA", MAPA["categoria_trilha"], f"Escolha a categoria de arma ({categoria[1]})")
    return plano


def treinos(lido, *, pericias, oficios, testes, tr_fisico=None, troca=0, confirmados=()):
    """Escolhas completas (as fixas do Caminho entram sozinhas). Passou da conta é recusa; faltou é aviso."""
    _so_na_criacao(lido)
    nomes = {k: {m["nome"]: m["caixa"] for m in MAPA[k]} for k in ("pericias", "oficios", "testes")}
    pedido = dict(pericias=pericias, oficios=oficios, testes=testes)
    for k, escolhidos in pedido.items():
        if len(set(escolhidos)) != len(escolhidos) or not set(escolhidos) <= set(nomes[k]):
            raise Recusa("Treino repetido ou fora da ficha.")
    if type(troca) is not int or troca not in TROCAS or tr_fisico not in (None, "FORÇA", "DESTREZA"):
        raise Recusa("Escolha inválida.")
    atual = lido.de("FICHA", next(c["celula"] for c in MAPA["escolhas"] if c["chave"] == "caminho"))
    linha = next((l for l in lido.faixa(PROGRESSAO, "M2:U7") if l[0] == atual), None)
    if linha is None:
        raise Recusa("Escolha o Caminho antes dos treinos.")
    if troca and linha[8] != "Sim":
        raise Recusa(f"{atual} não troca perícia por arma.")
    lim, fixas = limites(lido), [p for p in linha[5:7] if p]
    todas = list(dict.fromkeys([*fixas, *pericias]))
    com_oficio, sem_oficio = lim["pericias_com_oficio"] - 2 * troca, lim["pericias_sem_oficio"] - 2 * troca
    teto = com_oficio if oficios else max(com_oficio, sem_oficio)
    erros = []
    if len(todas) > teto:
        erros.append(f"São até {teto} perícias{' com ofícios' if oficios else ''}; você marcou {len(todas)}.")
    if len(oficios) > lim["oficios"]:
        erros.append(f"São até {lim['oficios']} ofícios; você marcou {len(oficios)}.")
    if len(testes) > 2:
        erros.append(f"São 2 Testes de Resistência; você marcou {len(testes)}.")
    if erros:
        raise Recusa(*erros)
    plano = Plano()
    pedido["pericias"] = todas
    atual_tr, atual_troca = (lido.de("FICHA", c) for c in (MAPA["tr_fisico"], MAPA["troca_arma"]["celula"]))
    conflito = [k for k, caixas in nomes.items()
                if any(lido.de("FICHA", c) is True and n not in pedido[k] for n, c in caixas.items())]
    if tr_fisico and atual_tr not in ("", "FORÇA", tr_fisico):
        conflito.append("tr_fisico")
    if atual_troca not in ("", TROCAS[0], TROCAS[troca]):
        conflito.append("troca")
    conflito = [k for k in conflito if k not in confirmados]
    if conflito:
        raise JaPreenchido(conflito)
    for k, caixas in nomes.items():
        for nome, caixa in caixas.items():
            if lido.de("FICHA", caixa) is not (nome in pedido[k]):
                plano.escritas.append(Escrita("FICHA", caixa, nome in pedido[k]))
    if tr_fisico and atual_tr != tr_fisico:
        plano.escritas.append(Escrita("FICHA", MAPA["tr_fisico"], tr_fisico))
    if atual_troca != TROCAS[troca]:
        plano.escritas.append(Escrita("FICHA", MAPA["troca_arma"]["celula"], TROCAS[troca]))
    if len(todas) < com_oficio or (len(todas) < sem_oficio and len(oficios) < lim["oficios"]):
        plano.avisos.append("Ainda faltam perícias ou ofícios.")
    if len(testes) < 2:
        plano.avisos.append(f"Falta{'m' if len(testes) == 0 else ''} {2 - len(testes)} Teste{'s' if not testes else ''} de Resistência.")
    if todas:
        plano.avisos.append("Confirme com o mestre as perícias da Origem e de onde veio cada Teste de Resistência.")
    return plano


def pedido(plano, abas):
    """Corpo do batchUpdate. `abas` é {título: sheetId} lido da própria cópia."""
    reqs = []
    for e in plano.escritas:
        linha, coluna = posicao(e.celula)
        if e.valor is None:
            valor = None
        elif type(e.valor) is bool:
            valor = {"boolValue": e.valor}
        elif type(e.valor) is int:
            valor = {"numberValue": e.valor}
        elif type(e.valor) is str:
            # stringValue é literal: "=A1" digitado pelo jogador continua texto.
            valor = {"stringValue": e.valor} if e.valor else None
        else:
            raise ValueError("Valor fora do tipo.")
        celula, campos = {}, [] if e.valor is None else ["userEnteredValue"]
        if valor:
            celula["userEnteredValue"] = valor
        if type(e.valor) is str:
            campos.append("textFormatRuns")
            fim, trechos = len(e.valor.encode("utf-16-le")) // 2, []
            for a, b in e.negritos:
                trechos.append({"startIndex": a, "format": {"bold": True}})
                if b < fim:
                    trechos.append({"startIndex": b, "format": {}})
            if trechos:
                celula["textFormatRuns"] = trechos
        if e.nota is not None:
            campos.append("note")
            if e.nota:
                celula["note"] = e.nota
        reqs.append({"updateCells": {"range": {"sheetId": abas[e.aba], "startRowIndex": linha - 1, "endRowIndex": linha,
                     "startColumnIndex": coluna - 1, "endColumnIndex": coluna}, "rows": [{"values": [celula]}],
                     "fields": ",".join(campos)}})
    for (aba, linha), px in sorted(plano.alturas.items()):
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": abas[aba], "dimension": "ROWS",
                     "startIndex": linha - 1, "endIndex": linha}, "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    return {"requests": reqs}
