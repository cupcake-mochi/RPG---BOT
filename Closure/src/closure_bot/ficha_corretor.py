"""Corretor da ficha (fase 3): funções puras, sem IA. Recebe as chaves da aba ANALISE (ficha_leitor.py) e devolve a
lista de problemas, cada um com regra, campo, esperado, encontrado e âncora do livro.

O bot nunca acredita na ficha: o jogador é dono da cópia e pode mexer em tudo, até na aba oculta. A ordem é a do
docs/PLANEJAMENTO.md e do ESQUEMA-ANALISE.md da ficha:
  1. formato: `formato.versao` que o bot não conhece recebe aviso, sem correção;
  2. regras da campanha: vêm do bot (RegrasDaCampanha), nunca da ficha; hoje só o padrão do livro;
  3. conteúdo custom: registro dos aprovados por impressão digital do texto (estrutura pronta, a ficha ainda não tem
     a aba CONFIGURAÇÃO, que é a fase 2 do B47);
  4. nomes: Caminho e Trilha contra o catálogo, Origem contra o capítulo de Origens do livro;
  5. contas: vida, PE, Integridade, proteção e Defesa refeitas a partir das entradas e comparadas com os resultados;
     feitiços e invocações têm conferência parcial de montagem em ficha_magia.py; entradas ausentes são declaradas;
  6. avisos: os que a própria ficha acende, só como primeiro filtro.

As fórmulas são as do livro R51. As tabelas que dá pra tirar do texto do
livro (uniformes, escudos, níveis de marco, Origens) são lidas dele em `Referencias.do_livro`, não escritas aqui.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from .ficha_leitor import Campo
from .ficha_magia import Magia

FORMATOS_CONHECIDOS = {1}
# O que a ficha mostra quando a pessoa ainda não escolheu: vale como vazio.
NAO_ESCOLHIDO = {"", "—", "-", "escolha seu caminho", "escolha sua trilha", "escolha sua origem"}

ANCORA = {
    "vida_max": "progressao--prog-atualizar", "energia_max": "progressao--prog-atualizar",
    "integridade_max": "dano--alma", "defesa": "equip--eqp-protecao", "protecao": "aptidoes--apt-cobrir",
    "caminho": "ab--ab-caminho", "trilha": "ab--ab-caminho", "origem": "origens--origens",
}


@dataclass(frozen=True)
class Problema:
    regra: str        # "formato", "escolha", "nome", "conta", "aviso", "buff" ou "origem"
    campo: str        # a chave da ANALISE
    esperado: str
    encontrado: str
    ancora: str = ""  # âncora do livro que manda na regra ("" quando quem manda é a própria ficha)


@dataclass
class Resultado:
    veredito: str                                         # "aprovada", "reprovada" ou "formato desconhecido"
    problemas: list[Problema] = field(default_factory=list)
    pendencias: list[Problema] = field(default_factory=list)  # falta ou pede atenção, sem reprovar (sobra, Força...)
    notas: list[Problema] = field(default_factory=list)   # pro mestre conferir: Buff/Debuff, Origem que a ficha não calcula
    nao_conferido: list[str] = field(default_factory=list)  # o que faltou entrada ou ainda não tem conta no bot
    conferidos: list[str] = field(default_factory=list)     # o que o bot conferiu e bateu ("Vida 23", "Origem Latente")


@dataclass(frozen=True)
class RegrasDaCampanha:
    """As regras de cada campanha vêm do cadastro do bot, nunca da ficha. Padrão: o livro, sem mudança.
    Hoje só a variante que mexe numa conta conferida: a vida por nível rolada no dado do Caminho
    (ab--ab-equipamento, com permissão do mestre), que deixa a vida sem valor exato pra conferir."""
    nome: str = "livro"
    vida_por_nivel: str = "fixa"  # "fixa" ou "rolada"


LIVRO = RegrasDaCampanha()


def impressao_digital(tipo: str, nome: str, campos: dict[str, str]) -> str:
    """Conteúdo custom (Origem, Caminho, arma...): o mestre aprova esta impressão; se o texto mudar depois, ela muda.
    Normaliza caixa, acento e espaços, pra uma vírgula a mais não parecer outro conteúdo."""
    def limpo(texto) -> str:
        texto = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode().lower()
        return " ".join(texto.split())
    corpo = json.dumps([limpo(tipo), limpo(nome), sorted((limpo(k), limpo(v)) for k, v in campos.items())],
                       ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(corpo.encode()).hexdigest()


@dataclass
class Aprovados:
    """Registro do conteúdo custom aprovado pelo mestre, por campanha. Só a estrutura: guardar em disco e o comando do
    mestre ficam pra quando a ficha tiver a aba CONFIGURAÇÃO (B47, fase 2)."""
    impressoes: dict[str, str] = field(default_factory=dict)  # impressão -> quem aprovou e quando

    def aprovar(self, tipo: str, nome: str, campos: dict[str, str], por: str) -> str:
        chave = impressao_digital(tipo, nome, campos)
        self.impressoes[chave] = por
        return chave

    def aprovado(self, tipo: str, nome: str, campos: dict[str, str]) -> bool:
        return impressao_digital(tipo, nome, campos) in self.impressoes


# Capacidades de Origem que mudam conta ou contagem e que a ficha (B47, fase 1) não calcula. Sem isso o bot reprovaria
# uma ficha certa. O nome é conferido no texto da âncora ao carregar as Referencias: se o livro mudar, falha alto.
TREINO_EXTRA = {  # treinos além dos 9 ou 10 da criação: quantos a ficha pode mostrar "a mais" (ofício conta 1)
    "Duas Vidas": (1, "origens--origem-encarnado", "Conhecimento Reavivado"),  # marcante do Encarnado
    "Aprendizado Complementar": (2, "origens--restricao-beneficios", "uma perícia ou dois Ofícios"),
    "Arquivo de Procedimentos": (1, "origens--corpo-ninhada-gemeos", "treino em um deles por vez"),
}
ESPECIALIZACAO_EXTRA = {"Especialidade Antiga": (10, "origens--encarnado-beneficios", "sem precisar escolher Corpo")}
PE_EXTRA = {  # a ficha não soma no PE máximo: o jogador põe no Buff de energia, e o bot confere se pôs o valor certo
    "Núcleo Dependente": ("origens--corpo-inteiro-manutencao", "Essência + quantidade de marcos alcançados"),
    "Reserva Excedente": ("origens--restricao-menores-corporais", "PE máximos aumentam em 2 × Essência"),
}
SEM_INTEGRIDADE = {"Núcleo Dependente": ("origens--corpo-inteiro-manutencao", "não possui barra de Integridade")}

# Marcantes da Restrição corporal: Defesa fixada em 0, sem bônus nem penalidade; o Quebradiço também tem metade da vida
DEFESA_ZERO = {"Corpo Debilitado": "origens--restricao-debilitado", "Corpo Quebradiço": "origens--restricao-quebradico",
               "Corpo Exaurido": "origens--restricao-exaurido"}
VIDA_METADE = {"Corpo Quebradiço": "origens--restricao-quebradico"}


@dataclass(frozen=True)
class Peca:
    protecao: int
    teto_destreza: int | None  # None: sem teto


@dataclass(frozen=True)
class Referencias:
    caminhos: dict[str, dict]          # nome -> {"vida1", "vidaNv", "peNv", "trilhas"}
    origens: tuple[str, ...]           # as sete, do capítulo de Origens
    ramos_restricao: tuple[str, ...]   # "Sem Energia", "Restrição corporal"
    aceitam_sem_tecnica: tuple[str, ...]
    marcos: tuple[int, ...]            # níveis de marco (6, 10, ...)
    refino_maximo: int
    uniformes: dict[str, Peca]         # "Traje 1" ... "Revestimento 3"
    escudos: dict[str, Peca]           # "Broquel", "Médio", "Torre"
    duas_maos: frozenset[str] = frozenset()  # armas de duas mãos: com elas na mão principal, o escudo não conta
    magia: Magia | None = None

    @classmethod
    def do_livro(cls, dados: Path) -> "Referencias":
        """Lê o catálogo (Caminhos) e o livro (o resto) de dados/sistema/. Falha alto se o livro mudar de forma."""
        sistema = Path(dados) / "sistema"
        catalogo = json.loads((sistema / "catalogos.json").read_text(encoding="utf-8"))
        livro = {}
        with open(sistema / "livro.jsonl", encoding="utf-8") as arquivo:
            for linha in arquivo:
                bloco = json.loads(linha)
                livro[bloco["ancora"]] = bloco["texto"]

        def bloco(ancora: str) -> str:
            if ancora not in livro:
                raise ValueError(f"o livro não tem mais a âncora {ancora}")
            return livro[ancora]

        origens = tuple(nome.strip() for nome in re.findall(r"^\| ([^|]+?) \| [^|]+ \| [^|]+ \|$", bloco("origens--origens"), re.M)
                        if nome.strip() != "Origem")
        restricao = bloco("origens--origem-restricao")
        ramos = tuple(r for r in ("Sem Energia", "Restrição corporal") if f"**{r}**" in restricao)
        aceitam = re.search(r"acompanha \*\*([^*]+)\*\*", bloco("origens--origem-sem-tecnica"))
        aceitam_sem_tecnica = tuple(re.split(r", | ou ", aceitam.group(1))) if aceitam else ()
        texto_marcos = bloco("aptidoes--apt-marcos")
        niveis = re.search(r"Nos níveis \*\*([\d, e]+)\*\*", texto_marcos)
        teto = re.search(r"até o limite (\d+)", texto_marcos)
        uniformes = {f"Traje {d}": p for d, p in _tabela_de_pecas(bloco("equip--eqp-traje")).items()}
        escudo = bloco("equip--eqp-escudo")
        revestimentos, _, escudos = escudo.partition("#### Escudos")
        uniformes.update({f"Revestimento {d}": p for d, p in _tabela_de_pecas(revestimentos).items()})
        duas_maos = set()
        for ancora, texto in livro.items():
            if ancora.startswith("equip--eqa-"):
                for nome in re.findall(r"^\| ([^|]+?) \| 2 \| \d*d\d+", texto, re.M):
                    duas_maos.update({nome.strip(), re.sub(r"\s*\(.*\)$", "", nome.strip())})  # "Kanabō (clava pesada)"
        conferir_texto = {**TREINO_EXTRA, **ESPECIALIZACAO_EXTRA, **{k: (0, *v) for k, v in PE_EXTRA.items()},
                          **{k: (0, a, "Defesa fica fixada em 0") for k, a in DEFESA_ZERO.items()},
                          **{k: (0, a, "vida máxima é metade da normal") for k, a in VIDA_METADE.items()}}
        validacoes = list(conferir_texto.items()) + [(nome, (0, *v)) for nome, v in SEM_INTEGRIDADE.items()]
        for nome, (*_, ancora, trecho) in validacoes:
            if trecho not in bloco(ancora) or nome not in bloco(ancora):
                raise ValueError(f"o livro mudou a capacidade {nome} ({ancora}): revise o corretor")
        try:
            magia = Magia.do_livro(livro)
        except KeyError as erro:
            raise ValueError(f"o livro mudou: referência de magia ausente ({erro})") from erro
        referencias = cls(
            caminhos={c["nome"]: c for c in catalogo["CAMINHOS"]}, origens=origens, ramos_restricao=ramos,
            aceitam_sem_tecnica=aceitam_sem_tecnica,
            marcos=tuple(int(n) for n in re.findall(r"\d+", niveis.group(1))) if niveis else (),
            refino_maximo=int(teto.group(1)) if teto else 0, uniformes=uniformes, escudos=_tabela_de_pecas(escudos),
            duas_maos=frozenset(duas_maos), magia=magia)
        if len(origens) != 7 or len(ramos) != 2 or not referencias.marcos or len(uniformes) != 6 or len(referencias.escudos) != 3 \
                or not duas_maos:
            raise ValueError("o livro mudou de forma: Origens, ramos, marcos, uniformes ou escudos não fecham")
        return referencias


def _tabela_de_pecas(texto: str) -> dict[str, Peca]:
    """Linhas "| 1 | +1 | Sem teto | ..." ou "| Broquel | +1 | 5 | ..." -> {"1": Peca(1, None), "Broquel": Peca(1, 5)}."""
    pecas = {}
    for nome, protecao, teto in re.findall(r"^\| ([^|]+?) \| \+(\d+) \| ([^|]+?) \|", texto, re.M):
        pecas[nome.strip()] = Peca(int(protecao), None if not teto.strip().isdigit() else int(teto))
    return pecas


# ---------- avisos da ficha ----------
# Texto que a ficha mostra quando está tudo certo, ou que é só informação.
_AVISO_OK = re.compile(r"^(\d+ de \d+|—|Treinada|Cumprido|Sem escudo|Sem requisito de Força|Força \d+ de \d+|Liberado no .*|Tudo escolhido.*)$")
# Erro: passou do limite, falta escolher ou pede patente maior. Nota: penalidade que o livro permite.
_AVISO_ERRO = re.compile(r"a mais|passou de|nenhum acima de|Especialização só no nível|^Falta:|^Pede ")
_AVISO_NOTA = re.compile(r"^Falta Força|^Não cumprido|^Sem treino|^Trava Selo")


def classificar_aviso(chave: str, valor) -> str | None:
    """"erro" (reprova), "pendente" (falta ou pede atenção, sem reprovar), "nota" (pro mestre) ou None (apagado).
    Os erros calculados por feitiço e invocação são erro sempre que têm texto; os avisos deles são nota. Texto
    desconhecido vira nota: nunca some calado."""
    texto = str(valor).strip()
    if texto in ("", "0"):
        return None
    # Este aviso só testa se há escudo: não verifica o Selo da técnica (ausente na ANALISE).
    # Sem impacto confirmado, não gera pendência. Outros avisos de Selo continuam classificados.
    if chave == "aviso.selo" and texto == "Trava Selo de gesto":
        return None
    if chave.endswith((".erros", ".pontos_acima")):
        return "erro"
    if chave.endswith(".avisos"):
        return "nota"
    if _AVISO_ERRO.search(texto):
        return "erro"
    if _AVISO_NOTA.search(texto):
        return "pendente"  # o livro deixa usar com penalidade, mas a pessoa precisa saber
    if _AVISO_OK.match(texto):
        if re.fullmatch(r"(\d+) de \d+", texto) and not texto.startswith("0 ") and chave in _SOBRA_E_PENDENCIA:
            return "pendente"  # sobrou ponto ou TR por escolher
        return None
    return "nota"


# "N de M" nestes é o que ainda falta distribuir; as perícias e ofícios em falta já acendem aviso.escolhas_de_pericia.
_SOBRA_E_PENDENCIA = {"aviso.pontos_disponiveis", "aviso.testes_disponiveis"}
# Os três avisos podem vir do mesmo contador. O resumo é a melhor representação.
_TREINOS = ("aviso.escolhas_de_pericia", "aviso.pericias_disponiveis", "aviso.oficios_disponiveis")


# ---------- contas ----------
def _numero(ficha: dict[str, Campo], chave: str) -> int | float | None:
    valor = ficha.get(chave, Campo("", "", "")).valor
    return valor if isinstance(valor, (int, float)) and not isinstance(valor, bool) else None


def _bonus(ficha: dict[str, Campo], chave: str) -> int | float:
    """Buff/Debuff: a ficha soma o valor se for número e ignora o resto, e o bot faz o mesmo."""
    return _numero(ficha, chave) or 0


def _texto(ficha: dict[str, Campo], chave: str) -> str:
    valor = str(ficha.get(chave, Campo("", "", "")).valor).strip()
    return "" if valor.lower() in NAO_ESCOLHIDO else valor


def _atributo(ficha: dict[str, Campo], nome: str) -> int | float:
    return (_numero(ficha, f"atributo.{nome}.base") or 0) + (_numero(ficha, f"atributo.{nome}.corpo") or 0)


ROTULO = {"vida_max": "Vida", "energia_max": "PE", "integridade_max": "Integridade", "protecao": "Proteção", "defesa": "Defesa"}


def _comparar(ficha, chave: str, esperado, problemas: list[Problema], certos: list[str] | None = None) -> None:
    encontrado = ficha.get(chave, Campo("", "", "")).valor
    if encontrado != esperado:
        problemas.append(Problema("conta", chave, _fmt(esperado), _fmt(encontrado), ANCORA.get(chave, "")))
    elif certos is not None:
        certos.append(f"{ROTULO.get(chave, chave)} {_fmt(esperado)}")


def _fmt(valor) -> str:
    if valor == "":
        return "vazio"
    return str(int(valor)) if isinstance(valor, float) and valor.is_integer() else str(valor)


def refino(nivel: int, marcos_de_refino: int, ref: Referencias) -> int:
    """1 no nível 1, +1 a cada marco passado e +1 a cada marco em que escolheu Refino, até o teto (aptidoes--apt-marcos)."""
    passados = sum(1 for n in ref.marcos if n <= nivel)
    return min(ref.refino_maximo, 1 + passados + min(passados, max(0, marcos_de_refino)))


def conferir_contas(ficha: dict[str, Campo], ref: Referencias, regras: RegrasDaCampanha = LIVRO,
                    certos: list[str] | None = None, pendencias: list[Problema] | None = None) -> tuple[list[Problema], list[str]]:
    problemas: list[Problema] = []
    pulou: list[str] = []
    certos = certos if certos is not None else []
    pendencias = pendencias if pendencias is not None else []
    nivel = _numero(ficha, "nivel")
    if not isinstance(nivel, int) or nivel < 1:
        return problemas, ["vida, PE, Integridade e Defesa: nível vazio ou inválido"]
    constituicao, essencia, destreza = (_atributo(ficha, a) for a in ("constituicao", "essencia", "destreza"))

    caminho = ref.caminhos.get(_texto(ficha, "caminho"))
    if caminho is None:
        pulou.append("vida e PE: sem Caminho do livro escolhido")
    else:
        if regras.vida_por_nivel == "fixa":
            base = caminho["vida1"] + constituicao + (caminho["vidaNv"] + constituicao) * (nivel - 1)
            vida = base + _bonus(ficha, "buff.vida")
            metade = [n for n in VIDA_METADE if n in _capacidades(ficha)]
            encontrada = ficha.get("vida_max", Campo("", "", "")).valor
            if metade and encontrada in (max(1, vida // 2), max(1, base // 2)):
                certos.append(f"Vida {_fmt(encontrada)} (metade, {metade[0]})")
            elif metade:
                pendencias.append(Problema("origem", "vida_max", f"metade da normal ({_fmt(max(1, base // 2))}) por {metade[0]}, "
                                           "e a ficha não aplica sozinha", _fmt(encontrada), VIDA_METADE[metade[0]]))
            else:
                _comparar(ficha, "vida_max", vida, problemas, certos)
        else:
            pulou.append("vida: a campanha rola a vida por nível")
        _comparar(ficha, "energia_max", caminho["peNv"] * nivel + _bonus(ficha, "buff.energia"), problemas, certos)

    integridade = 20 + (essencia + 5) * (nivel - 1) + _bonus(ficha, "buff.integridade")
    sem_integridade = [n for n in SEM_INTEGRIDADE if n in _capacidades(ficha)]
    if sem_integridade:
        encontrada = ficha.get("integridade_max", Campo("", "", "")).valor
        esperado = f"sem barra de Integridade ({sem_integridade[0]})"
        ancora = SEM_INTEGRIDADE[sem_integridade[0]][0]
        if encontrada in ("", 0):
            certos.append(f"Sem barra de Integridade ({sem_integridade[0]})")
        elif encontrada == integridade:
            pendencias.append(Problema("origem", "integridade_max", esperado, _fmt(encontrada), ancora))
        else:
            problemas.append(Problema("conta", "integridade_max", esperado, _fmt(encontrada), ancora))
    else:
        _comparar(ficha, "integridade_max", integridade, problemas, certos)

    # Defesa = 10 + Destreza permitida + proteção (equip--eqp-protecao). Uniforme troca a proteção passiva; escudo soma.
    vestindo, secundaria = _texto(ficha, "em_uso.vestindo"), _texto(ficha, "em_uso.secundaria")
    uniforme = ref.uniformes.get(vestindo)
    principal = _texto(ficha, "em_uso.principal")
    # com arma de duas mãos na principal, o escudo não está empunhado e não conta (equip--eqp-protecao); a ficha faz igual
    escudo = None if principal in ref.duas_maos else ref.escudos.get(secundaria)
    if vestindo and uniforme is None:
        pulou.append(f"Defesa: uniforme desconhecido ({vestindo})")
        return problemas, pulou
    # Na rota sem energia a proteção passiva é a Defesa sem Armadura, pela Lapidação (rotas--rota-defesa): a mesma conta
    # e a mesma progressão do Refino (começa em 1, +1 por marco e +1 quando escolhida, teto 10), e a ficha usa a mesma célula.
    if uniforme is not None:
        protecao = uniforme.protecao
    else:
        protecao = 1 + refino(nivel, int(_numero(ficha, "marco.refino") or 0), ref) // 3
    tetos = [p.teto_destreza for p in (uniforme, escudo) if p is not None and p.teto_destreza is not None]
    protecao += (escudo.protecao if escudo else 0) + _bonus(ficha, "buff.protecao")
    _comparar(ficha, "protecao", protecao, problemas, certos)
    defesa = 10 + (min([destreza, *tetos]) if tetos else destreza) + protecao + _bonus(ficha, "buff.defesa")
    zero = [n for n in DEFESA_ZERO if n in _capacidades(ficha)]
    if zero:
        encontrada = ficha.get("defesa", Campo("", "", "")).valor
        if encontrada == 0:
            certos.append(f"Defesa 0 ({zero[0]})")
        elif encontrada == defesa:
            # Só a fórmula normal conhecida recebe a tolerância pela divergência da ficha.
            pendencias.append(Problema("origem", "defesa", f"fica 0 por {zero[0]}, e a ficha não aplica sozinha", _fmt(encontrada),
                                       DEFESA_ZERO[zero[0]]))
        else:
            problemas.append(Problema("conta", "defesa", "0", _fmt(encontrada), DEFESA_ZERO[zero[0]]))
    else:
        _comparar(ficha, "defesa", defesa, problemas, certos)
    return problemas, pulou


def conferir_feiticos(ficha: dict[str, Campo], ref: Referencias, resultado: Resultado | None = None) -> list[Problema]:
    from .ficha_magia import conferir_feiticos as magia_feiticos
    r = resultado if resultado is not None else Resultado("aprovada")
    if ref.magia is None:
        r.nao_conferido.append("feitiços: referências de magia indisponíveis")
        return []
    antes = len(r.problemas)
    magia_feiticos(ficha, ref.magia, r)
    return r.problemas[antes:]


def conferir_invocacoes(ficha: dict[str, Campo], ref: Referencias, resultado: Resultado | None = None) -> list[Problema]:
    from .ficha_magia import conferir_invocacoes as magia_invocacoes
    r = resultado if resultado is not None else Resultado("aprovada")
    if ref.magia is None:
        r.nao_conferido.append("invocações: referências de magia indisponíveis")
        return []
    antes = len(r.problemas)
    magia_invocacoes(ficha, ref.magia, ref.marcos, r)
    return r.problemas[antes:]


# ---------- nomes ----------
def conferir_nomes(ficha: dict[str, Campo], ref: Referencias, certos: list[str] | None = None) -> list[Problema]:
    """Caminho, Trilha e Origem sem escolher reprovam (o Mizuki, 14/10/2026): a criação entrega os três no nível 2."""
    problemas = []
    for chave, rotulo in (("caminho", "um Caminho"), ("trilha", "uma Trilha"), ("origem", "uma Origem")):
        if not _texto(ficha, chave):
            problemas.append(Problema("escolha", chave, f"escolher {rotulo}", "vazio", ANCORA[chave]))
    nome_caminho = _texto(ficha, "caminho")
    caminho = ref.caminhos.get(nome_caminho)
    if nome_caminho and caminho is None:
        problemas.append(Problema("nome", "caminho", "um Caminho do livro", nome_caminho, ANCORA["caminho"]))
    trilha = _texto(ficha, "trilha").partition(" · ")[0]  # "Batedor · Yumi": a variante é a arma da Trilha
    if trilha and caminho is not None and trilha not in caminho["trilhas"]:
        problemas.append(Problema("nome", "trilha", f"uma Trilha de {nome_caminho}: {', '.join(caminho['trilhas'])}",
                                  _texto(ficha, "trilha"), ANCORA["trilha"]))
    origem_inteira = _texto(ficha, "origem")
    if origem_inteira:
        origem, _, variante = origem_inteira.partition(" · ")
        if origem not in ref.origens:
            problemas.append(Problema("nome", "origem", f"uma das Origens: {', '.join(ref.origens)}", origem_inteira, ANCORA["origem"]))
        elif origem == "Restrição Celestial" and variante not in ref.ramos_restricao:
            problemas.append(Problema("nome", "origem", f"Restrição Celestial com um ramo: {' ou '.join(ref.ramos_restricao)}",
                                      origem_inteira, "origens--origem-restricao"))
        elif variante and origem != "Restrição Celestial" and (variante != "Sem Técnica" or origem not in ref.aceitam_sem_tecnica):
            problemas.append(Problema("nome", "origem", f"{origem} sozinha ou com Sem Técnica", origem_inteira,
                                      "origens--origem-sem-tecnica"))
    if certos is not None:
        nomes = [problema.campo for problema in problemas]
        certos.extend(f"{rotulo} {_texto(ficha, chave)}" for chave, rotulo in
                      (("caminho", "Caminho"), ("trilha", "Trilha"), ("origem", "Origem")) if _texto(ficha, chave) and chave not in nomes)
    return problemas


# ---------- Origem que a ficha não calcula ----------
def _capacidades(ficha: dict[str, Campo]) -> set[str]:
    return {_texto(ficha, k) for k in ("origem.marcante", "origem.menor_1", "origem.menor_2")} - {""}


def _a_mais(texto: str) -> int:
    achou = re.search(r"(\d+) a mais", texto)
    return int(achou.group(1)) if achou else 0


def treinos_da_origem(ficha: dict[str, Campo]) -> tuple[int, list[str]]:
    """Quantos treinos e especializações "a mais" a Origem justifica, e de quais capacidades."""
    caps, nivel = _capacidades(ficha), _numero(ficha, "nivel") or 0
    fontes = [n for n in TREINO_EXTRA if n in caps] + [n for n, (desde, *_) in ESPECIALIZACAO_EXTRA.items() if n in caps and nivel >= desde]
    return sum(TREINO_EXTRA[n][0] if n in TREINO_EXTRA else 1 for n in fontes), fontes


def pe_da_origem(ficha: dict[str, Campo], ref: Referencias) -> list[tuple[str, int]]:
    caps, nivel, essencia = _capacidades(ficha), _numero(ficha, "nivel") or 0, _atributo(ficha, "essencia")
    extras = []
    if "Núcleo Dependente" in caps:
        extras.append(("Núcleo Dependente", int(essencia + sum(1 for n in ref.marcos if n <= nivel) * (essencia // 2))))
    if "Reserva Excedente" in caps:
        extras.append(("Reserva Excedente", int(2 * essencia)))
    return extras


# ---------- tudo ----------
def conferir(ficha: dict[str, Campo], ref: Referencias, regras: RegrasDaCampanha = LIVRO) -> Resultado:
    formato = ficha.get("formato.versao", Campo("", "", "")).valor
    if formato not in FORMATOS_CONHECIDOS:
        return Resultado("formato desconhecido", [Problema("formato", "formato.versao", " ou ".join(map(str, sorted(FORMATOS_CONHECIDOS))),
                                                           _fmt(formato))])
    resultado = Resultado("aprovada")
    resultado.problemas += conferir_nomes(ficha, ref, resultado.conferidos)
    contas, pulou = conferir_contas(ficha, ref, regras, resultado.conferidos, resultado.pendencias)
    resultado.problemas += contas
    resultado.nao_conferido += pulou
    conferir_feiticos(ficha, ref, resultado)
    conferir_invocacoes(ficha, ref, resultado)
    resultado.nao_conferido.append("feitiços e invocações: texto, Famílias, Classe 0 pessoal, Técnica Máxima e ajustes não estão completos na ANALISE")
    treinos, fontes = treinos_da_origem(ficha)
    notas_de_treino: dict[int, Problema] = {}
    for chave, campo in ficha.items():
        # Buff/Debuff entra na conta como a ficha faz, e vai pra lista do mestre conferir de onde veio
        if chave.startswith("buff.") and campo.valor not in ("", 0):
            resultado.notas.append(Problema("buff", chave, "", _fmt(campo.valor), ""))
        if campo.parte != "aviso":
            continue
        tipo = classificar_aviso(chave, campo.valor)
        excesso = _a_mais(str(campo.valor)) if chave in _TREINOS else 0
        if tipo == "erro" and excesso and excesso <= treinos:
            # a ficha conta como "a mais" o treino que a Origem dá: não reprova, e o mestre confere se é esse
            nota = Problema("origem", chave, f"até {treinos} a mais por {', '.join(fontes)}", str(campo.valor),
                            "origens--origens")
            anterior = notas_de_treino.get(excesso)
            if anterior is None or _TREINOS.index(chave) < _TREINOS.index(anterior.campo):
                notas_de_treino[excesso] = nota
        elif tipo:
            aviso = Problema("aviso", chave, "", str(campo.valor), "")
            {"erro": resultado.problemas, "pendente": resultado.pendencias, "nota": resultado.notas}[tipo].append(aviso)
    resultado.notas.extend(notas_de_treino.values())
    buff_pe = _bonus(ficha, "buff.energia")
    for nome, extra in pe_da_origem(ficha, ref):
        if extra and buff_pe != extra:
            resultado.pendencias.append(Problema("origem", "energia_max", f"+{extra} de {nome} no Buff de PE",
                                                 f"Buff de PE {_fmt(buff_pe)}", PE_EXTRA[nome][0]))
    if resultado.problemas:
        resultado.veredito = "reprovada"
    return resultado
