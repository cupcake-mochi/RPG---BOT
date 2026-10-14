"""A "vida" das personagens no servidor: o estado do momento e o que elas sabem de quem fala.

O desenho é o de dados/personagem/kaltsit/vida.md (a Closure muda só o efeito, em closure/vida.md). Tudo aqui é
conta feita no código, sem chamada de modelo: carga, movimento do canal, paciência e intimidade. O resultado vira
o bloco de estado do pedido e, quando o estado pede, uma ou duas linhas no lembrete do fim.

Os cards não explicam a escala de intimidade, então o bloco não leva só o número: leva a frase de como ela trata
a pessoa naquele nível, tirada das tabelas do vida.md.
"""
from __future__ import annotations

import hashlib
import random
import re
import unicodedata
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta

from .plantao import APELIDOS, CLOSURE, FUSO, KALTSIT, de_plantao
from .registro import Registro

PACIENCIA_CHEIA = 3
RECUPERA_A_CADA = timedelta(hours=2)
REPETIU_EM = timedelta(minutes=30)
JANELA_DO_CANAL = timedelta(minutes=15)
DIAS_POR_NIVEL = (5, 15, 40, 100)  # dias diferentes de conversa pra chegar na intimidade 1, 2, 3 e 4

# Como ela trata a pessoa em cada nível de intimidade (vida.md da Kal'tsit, seção 4; da Closure, seção 4).
# Do nível 1 em diante a frase não promete lembrança: o que ela sabe da pessoa é só o que vier em "Fatos".
TRATO = {
    KALTSIT: (
        "pessoa nova: seja formal e explique mais",
        "já conversaram algumas vezes: não trate como pessoa nova",
        "conversam com frequência: se os fatos trouxerem uma dúvida antiga dela, pode lembrar numa frase",
        "conversam há muito tempo: o humor seco pode aparecer mais, e você pode ser franca sem amaciar",
        "conversam há muito tempo: humor seco e franqueza à vontade",
    ),
    CLOSURE: (
        "pessoa nova: explique mais, sem provocação",
        "já conversaram algumas vezes: brincadeira leve cabe",
        "conversam com frequência: se os fatos trouxerem uma dúvida antiga dela, pode provocar com isso",
        "conversam há muito tempo: provoque à vontade, e a cobrança em iene pode aparecer",
        "conversam há muito tempo: provoque à vontade, e a cobrança em iene pode aparecer",
    ),
}
# Linhas do lembrete do fim (vida.md da Kal'tsit, seção 9; da Closure, seção 5). A de fora do plantão é da página do site.
LEMBRETE_CARGA = {KALTSIT: "Carga alta: uma frase.", CLOSURE: "Carga alta: uma frase, sem piada."}
LEMBRETE_PACIENCIA = {KALTSIT: "Paciência baixa com esta pessoa: seca, sem explicar duas vezes.",
                      CLOSURE: "Paciência baixa com esta pessoa: curta, sem piada, sem explicar duas vezes."}
LEMBRETE_PESSOA_NOVA = {CLOSURE: "Pessoa nova: sem provocação."}

TIRA_DO_PERSONAGEM = re.compile(
    r"ignor\w+ (?:todas? )?(?:as |suas |tuas |essas )?(?:instru|regras|ordens)|esque[cç]a (?:tudo|as instru|suas instru)"
    r"|prompt (?:de |do )?sistema|system prompt|modo (?:desenvolvedor|dev|dan)\b|finja (?:que|ser)\b|aja como (?:se|um|uma)\b"
    r"|a partir de agora (?:voc[eê]|vc) [eé]\b", re.IGNORECASE)


def carga(respostas_na_ultima_hora: int) -> int:
    return sum(respostas_na_ultima_hora >= n for n in (5, 10, 20))


def movimento(mensagens_em_15_min: int) -> str:
    return "quieto" if mensagens_em_15_min < 3 else "normal" if mensagens_em_15_min <= 20 else "cheio"


def intimidade(dias_de_conversa: int) -> int:
    """0 a 4. Os degraus já garantem o "no máximo 1 por semana" do desenho: nenhum nível chega antes de 5 dias."""
    return sum(dias_de_conversa >= n for n in DIAS_POR_NIVEL)


def paciencia_agora(valor: int, desde: datetime, agora: datetime) -> int:
    """A paciência guardada mais o que o tempo devolveu: 1 a cada 2 h sem atrito, até 3."""
    return min(PACIENCIA_CHEIA, valor + max(0, int((agora - desde) / RECUPERA_A_CADA)))


def resumo(texto: str) -> str | None:
    """Impressão embaralhada da pergunta, sem o nome das guias, pra reconhecer repetição sem guardar o texto.

    Mensagem de menos de quatro palavras ("oi closure", "kkk") não tem resumo: repetir cumprimento não é atrito."""
    plano = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    nomes = {n for apelidos in APELIDOS.values() for a in apelidos for n in re.findall(r"\w+", a)}
    palavras = [p for p in re.findall(r"\w+", plano) if p not in nomes]
    return hashlib.sha256(" ".join(palavras).encode()).hexdigest()[:16] if len(palavras) >= 4 else None


def atrito(texto: str, *, resumo_anterior: str | None, quando_anterior: datetime | None, agora: datetime) -> str | None:
    """O que na mensagem gasta paciência: tentar tirá-la do personagem, ou repetir a mesma pergunta em 30 min.

    Provocação, que o desenho também conta, fica de fora: sem modelo não dá pra separar de brincadeira."""
    if TIRA_DO_PERSONAGEM.search(texto):
        return "tirar do personagem"
    r = resumo(texto)
    if r and r == resumo_anterior and quando_anterior and agora - quando_anterior <= REPETIU_EM:
        return "repetiu a pergunta"
    return None


CHANCE_DE_FATO_SOLTO = 1 / 3
_COMUNS = frozenset("para como voce você esta está isso essa esse aqui muito mais pode quando onde qual quem sobre mesa joga jogo "
                    "kal closure kaltsit hoje agora mesmo ainda tambem também que nao não uma uns com por sem dos das tem ter foi ser "
                    "sao são ele ela meu minha seu sua nos nas pra pro tudo bem bom boa dia noite tarde".split())


def _palavras(texto: str) -> set[str]:
    plano = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    return {p for p in re.findall(r"[a-z0-9]{3,}", plano) if p not in _COMUNS}


def escolher_fatos(fatos: tuple[str, ...], texto: str, sorteio: random.Random) -> tuple[str, ...]:
    """Quais fatos da ficha entram nesta resposta. Com todos, toda vez, ela puxa sempre o mesmo assunto (medido em 13/10).

    Entram os que têm palavra em comum com a mensagem, até dois, do mais novo pro mais velho. Sem nenhum assim,
    em uma de cada três respostas entra um fato sorteado; nas outras, nenhum."""
    da_mensagem = _palavras(texto)
    ligados = [f for f in reversed(fatos) if _palavras(f) & da_mensagem][:2]
    if ligados:
        return tuple(ligados)
    return (sorteio.choice(fatos),) if fatos and sorteio.random() < CHANCE_DE_FATO_SOLTO else ()


def _plano(texto: str) -> str:
    """Tira colchete e quebra de linha do que vem de gente (nome, pronomes, fato), pra não se passar por bloco do pedido."""
    return " ".join(re.sub(r"[\[\]\r\n]", " ", texto).split())


@dataclass(frozen=True)
class Estado:
    persona: str
    agora: datetime
    movimento: str
    carga: int
    nome: str
    pronomes: str | None
    dias: int
    intimidade: int
    paciencia: int
    fatos: tuple[str, ...]

    @property
    def no_plantao(self) -> bool:
        return de_plantao(self.agora) == self.persona

    def bloco(self) -> str:
        """O bloco de estado do pedido, no formato da página do site, com o que o bot sabe de verdade."""
        hora = self.agora.astimezone(FUSO)
        pronomes = f"pronomes: {_plano(self.pronomes)}" if self.pronomes else "pronomes não informados"
        if self.fatos:  # pano de fundo, como a memória de um assistente: saber não obriga a citar
            fatos = "; ".join(_plano(f) for f in self.fatos) + " (pano de fundo: use só se couber na conversa, sem acrescentar detalhe que não está aqui)"
        else:
            fatos = "nenhum a lembrar agora; não suponha nada sobre a pessoa"
        return (f"[Estado agora: {'plantão' if self.no_plantao else 'fora do plantão'}; {hora:%H:%M} em Brasília; "
                f"canal {self.movimento}; carga {self.carga}.\n"
                f"Quem fala: {_plano(self.nome) or 'alguém'} ({pronomes}). Como tratar: {TRATO[self.persona][self.intimidade]}.\n"
                f"Fatos sobre a pessoa: {fatos}.]")

    def lembretes(self) -> list[str]:
        """Linhas a mais no lembrete do fim, em ordem de prioridade. Quem monta o pedido usa no máximo duas,
        contando a de fora do plantão."""
        linhas = []
        if self.carga >= 2:
            linhas.append(LEMBRETE_CARGA[self.persona])
        if self.paciencia <= 1:
            linhas.append(LEMBRETE_PACIENCIA[self.persona])
        if self.intimidade == 0 and self.persona in LEMBRETE_PESSOA_NOVA:
            linhas.append(LEMBRETE_PESSOA_NOVA[self.persona])
        return linhas

    def para_a_ponte(self) -> dict:
        return {"bloco": self.bloco(), "lembretes": self.lembretes()}


class Vida:
    def __init__(self, registro: Registro, sorteio: random.Random | None = None):
        self._registro = registro
        self._sorteio = sorteio or random.Random()
        self._canais: dict[int, deque[datetime]] = {}  # hora das mensagens recentes de cada canal; some ao reiniciar

    def ouvir(self, canal_id: int, agora: datetime) -> None:
        """Toda mensagem de gente num canal que o bot escuta passa aqui. Só a hora fica, e só por 15 minutos."""
        fila = self._canais.setdefault(canal_id, deque())
        fila.append(agora)
        while fila and agora - fila[0] > JANELA_DO_CANAL:
            fila.popleft()

    def movimento(self, canal_id: int, agora: datetime) -> str:
        return movimento(sum(agora - quando <= JANELA_DO_CANAL for quando in self._canais.get(canal_id, ())))

    def chamada(self, *, autor_id: int, persona: str, texto: str, agora: datetime) -> str | None:
        """Atualiza a paciência da personagem com quem a chamou. Devolve o atrito encontrado, se houve."""
        guardada = self._registro.paciencia(autor_id=autor_id, persona=persona)
        valor = paciencia_agora(guardada.valor, guardada.desde, agora) if guardada else PACIENCIA_CHEIA
        motivo = atrito(texto, resumo_anterior=guardada.pergunta if guardada else None,
                        quando_anterior=guardada.pergunta_quando if guardada else None, agora=agora)
        if motivo:
            valor, desde = max(0, valor - 1), agora
        elif not guardada or valor == PACIENCIA_CHEIA:
            desde = agora
        else:  # o relógio da próxima recuperação continua de onde estava
            desde = guardada.desde + (valor - guardada.valor) * RECUPERA_A_CADA
        self._registro.gravar_paciencia(autor_id=autor_id, persona=persona, valor=valor, desde=desde,
                                        pergunta=resumo(texto), pergunta_quando=agora)
        return motivo

    def estado(self, *, persona: str, canal_id: int, autor_id: int, nome: str, agora: datetime, texto: str = "") -> Estado:
        """`texto` é a mensagem que ela vai responder: decide quais fatos da ficha entram (escolher_fatos)."""
        guardada = self._registro.paciencia(autor_id=autor_id, persona=persona)
        ficha = self._registro.ficha(autor_id)
        dias = self._registro.dias_de_conversa(autor_id=autor_id, persona=persona)
        return Estado(
            persona=persona, agora=agora, movimento=self.movimento(canal_id, agora),
            carga=carga(self._registro.respostas_desde(persona=persona, desde=agora - timedelta(hours=1))),
            nome=nome, pronomes=ficha.pronomes, dias=dias, intimidade=intimidade(dias),
            paciencia=paciencia_agora(guardada.valor, guardada.desde, agora) if guardada else PACIENCIA_CHEIA,
            fatos=escolher_fatos(ficha.fatos, texto, self._sorteio))
