"""Clima agora, de Tóquio ou de outro lugar, pra as personagens poderem dizer como está.

Elas monitoram de longe, pelo computador: nenhuma das duas está no lugar (Mizuki, 13/10/2026).

Vem do bot antigo (Closure Legado), que usava a OpenWeatherMap com chave. Aqui a fonte é a Open-Meteo, que
não pede chave nem conta: https://open-meteo.com/en/docs (uso gratuito não comercial; dados em CC BY 4.0).

Usos:
  - /clima [lugar] mostra o painel, e o painel diário é postado num canal (cogs/clima.py);
  - contexto_clima(servico, texto) devolve a linha de dado pro bloco 4 do prompt quando a mensagem puxa o
    assunto, ou None. Como o sono da Closure, o clima só entra na conversa quando a mensagem puxa. É dado,
    nunca instrução.
"""
from __future__ import annotations

import logging
import re
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Callable
from urllib.parse import quote

log = logging.getLogger(__name__)

URL_CLIMA = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
             "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day"
             "&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
             "&timezone=auto&forecast_days=1")
URL_LUGAR = "https://geocoding-api.open-meteo.com/v1/search?name={nome}&count=10&language=pt&format=json"

VALIDADE = 15 * 60        # segundos em que a última leitura é reaproveitada (o legado também lia de 15 em 15 min)
TOLERANCIA = 3 * 60 * 60  # se a API falhar, a leitura antiga ainda serve por este tempo
MAX_LUGARES = 200         # teto do que fica guardado de busca de lugar, que vem de texto de usuário
HORA_DO_PAINEL = 6        # o painel diário sai na primeira leitura depois das 6h de Brasília, como no legado

# Códigos de tempo da OMM, como a Open-Meteo devolve em weather_code
CONDICOES = {
    0: "céu limpo", 1: "poucas nuvens", 2: "parcialmente nublado", 3: "nublado",
    45: "neblina", 48: "neblina com geada",
    51: "garoa fraca", 53: "garoa", 55: "garoa forte", 56: "garoa congelante", 57: "garoa congelante forte",
    61: "chuva fraca", 63: "chuva", 65: "chuva forte", 66: "chuva congelante", 67: "chuva congelante forte",
    71: "neve fraca", 73: "neve", 75: "neve forte", 77: "grãos de neve",
    80: "pancadas de chuva fracas", 81: "pancadas de chuva", 82: "pancadas de chuva fortes",
    85: "pancadas de neve", 86: "pancadas de neve fortes",
    95: "trovoada", 96: "trovoada com granizo", 99: "trovoada com granizo forte",
}


_EMOJI = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️", 95: "⛈️", 96: "⛈️", 99: "⛈️"}
_EMOJI.update({c: "🌦️" for c in (51, 53, 55, 56, 57)})
_EMOJI.update({c: "🌧️" for c in (61, 63, 65, 66, 67, 80, 81, 82)})
_EMOJI.update({c: "🌨️" for c in (71, 73, 75, 77, 85, 86)})
_ICONE = {0: "01", 1: "02", 2: "03", 3: "04", 45: "50", 48: "50", 95: "11", 96: "11", 99: "11"}
_ICONE.update({c: "09" for c in (51, 53, 55, 56, 57, 80, 81, 82)})
_ICONE.update({c: "10" for c in (61, 63, 65)})
_ICONE.update({c: "13" for c in (66, 67, 71, 73, 75, 77, 85, 86)})


def emoji_do_tempo(codigo: int, de_dia: bool = True) -> str:
    if not de_dia and codigo in (0, 1):
        return "🌙"
    return _EMOJI.get(codigo, "☁️")


@dataclass(frozen=True)
class Lugar:
    nome: str        # como aparece no painel e na linha do bloco 4: "Tóquio", "Quioto, Japão"
    latitude: float
    longitude: float


TOQUIO = Lugar("Tóquio", 35.6895, 139.6917)

# Jeitos de escrever que a busca em português não resolve sozinha
APELIDOS_DE_LUGAR = {"nova york": "Nova Iorque", "new york": "New York City",
                     # apelido de capital que a busca não conhece ("tá chovendo em bh?")
                     "bh": "Belo Horizonte", "sp": "São Paulo", "sampa": "São Paulo", "rj": "Rio de Janeiro",
                     "bsb": "Brasília", "poa": "Porto Alegre", "floripa": "Florianópolis", "cwb": "Curitiba"}
# Sigla de estado depois da cidade ("Belo Horizonte - MG", "belo horizonte/mg"): só ajuda a escolher entre homônimos.
ESTADOS = {"ac": "acre", "al": "alagoas", "ap": "amapa", "am": "amazonas", "ba": "bahia", "ce": "ceara",
           "df": "distrito federal", "es": "espirito santo", "go": "goias", "ma": "maranhao", "mt": "mato grosso",
           "ms": "mato grosso do sul", "mg": "minas gerais", "pa": "para", "pb": "paraiba", "pr": "parana",
           "pe": "pernambuco", "pi": "piaui", "rj": "rio de janeiro", "rn": "rio grande do norte",
           "rs": "rio grande do sul", "ro": "rondonia", "rr": "roraima", "sc": "santa catarina", "sp": "sao paulo",
           "se": "sergipe", "to": "tocantins"}


@dataclass(frozen=True)
class Clima:
    lugar: str
    temperatura: int
    sensacao: int
    umidade: int
    vento_kmh: int
    condicao: str
    minima: int
    maxima: int
    nascer: str      # "05:46", hora do lugar
    por_do_sol: str
    hora_local: str  # hora do lugar em que a leitura vale, "02:00"
    de_dia: bool
    codigo: int = 3              # código de tempo da OMM, de onde saem o emoji e o ícone do painel
    chuva_hoje: int | None = None  # maior chance de chuva do dia, em %; None quando a leitura não traz

    @property
    def emoji(self) -> str:
        return emoji_do_tempo(self.codigo, self.de_dia)

    @property
    def icone(self) -> str:
        """Endereço do desenho do tempo (os ícones públicos do OpenWeather, os mesmos do painel antigo)."""
        return f"https://openweathermap.org/img/wn/{_ICONE.get(self.codigo, '04')}{'d' if self.de_dia else 'n'}@2x.png"

    @property
    def estado(self) -> str:
        """O que precisa mudar pra o painel diário ser atualizado."""
        return f"{self.condicao}|{self.temperatura}"


def _sem_acento(texto: str) -> str:
    """Minúsculo e sem acento, com o mesmo tamanho do texto (em NFC), pra as posições continuarem valendo."""
    return "".join(unicodedata.normalize("NFD", c)[0] for c in unicodedata.normalize("NFC", texto).lower())


def interpretar(resposta: dict, lugar: str = TOQUIO.nome) -> Clima:
    """Converte a resposta da Open-Meteo. Levanta KeyError se a forma mudar, em vez de inventar valor."""
    atual, dia = resposta["current"], resposta["daily"]
    codigo = int(atual["weather_code"])
    return Clima(
        lugar=lugar,
        temperatura=round(atual["temperature_2m"]),
        sensacao=round(atual["apparent_temperature"]),
        umidade=round(atual["relative_humidity_2m"]),
        vento_kmh=round(atual["wind_speed_10m"]),
        condicao=CONDICOES.get(codigo, f"condição {codigo}"),
        minima=round(dia["temperature_2m_min"][0]),
        maxima=round(dia["temperature_2m_max"][0]),
        nascer=datetime.fromisoformat(dia["sunrise"][0]).strftime("%H:%M"),
        por_do_sol=datetime.fromisoformat(dia["sunset"][0]).strftime("%H:%M"),
        hora_local=datetime.fromisoformat(atual["time"]).strftime("%H:%M"),
        de_dia=bool(atual["is_day"]),
        codigo=codigo,
        chuva_hoje=_inteiro_ou_nada((dia.get("precipitation_probability_max") or [None])[0]),
    )


def _inteiro_ou_nada(valor) -> int | None:
    return None if valor is None else round(valor)


def interpretar_lugar(resposta: dict, regiao: str = "", exigir: bool = False) -> Lugar | None:
    """Da lista da busca, fica o lugar mais populoso: "Paris" é a da França, não a do Texas. Com `regiao` (o estado
    ou país escrito depois da cidade), os resultados dessa região vêm na frente; com `exigir`, só eles valem."""
    resultados = resposta.get("results") or []
    if not resultados:
        return None
    regiao = ESTADOS.get(_sem_acento(regiao).strip(), _sem_acento(regiao).strip())
    if regiao:
        da_regiao = [r for r in resultados
                     if regiao in _sem_acento(f"{r.get('admin1', '')} {r.get('country', '')}")]
        if exigir and not da_regiao:
            return None
        resultados = da_regiao or resultados
    melhor = max(resultados, key=lambda r: r.get("population") or 0)
    partes = [melhor["name"]]
    if melhor.get("admin1") and melhor["admin1"] != melhor["name"]:
        partes.append(melhor["admin1"])
    if melhor.get("country"):
        partes.append(melhor["country"])
    nome = re.sub(r"[\[\]\n\r]", " ", ", ".join(partes)).strip()  # vai pro prompt: sem colchete nem quebra de linha
    return Lugar(nome, float(melhor["latitude"]), float(melhor["longitude"]))


def linha_bloco4(clima: Clima) -> str:
    return (f"[{clima.lugar} agora ({clima.hora_local} de lá, {'dia' if clima.de_dia else 'noite'}): "
            f"{clima.temperatura} °C, sensação de {clima.sensacao} °C, {clima.condicao}, umidade {clima.umidade}%, "
            f"vento {clima.vento_kmh} km/h; hoje entre {clima.minima} °C e {clima.maxima} °C.]")


# Só o que fala do tempo lá fora. "Tempo" sozinho fica de fora ("quanto tempo dura?"), e "frio"/"calor" só
# contam com verbo de tempo ou lugar junto, porque também aparecem em regra ("dano de frio") e em conversa
# sobre quem escreve ("tô com calor").
_LOCAL = r"(em|no|na|nos|nas|ai|la)(?!\w)"
_GATILHOS = re.compile(
    r"(?<!\w)("
    r"weather\b|forecast (?:in|for|today|now)\b|temperature (?:in|of|for|today|now)\b|is it (?:raining|snowing)\b|"
    r"clima (em|no|na|nos|nas|ai|la|hoje|agora|por ai)(?!\w)|(qual|como) (e |ta |esta |anda )?o (clima|tempo)|"
    r"previsao do tempo|tempo (em|de) toquio|tempo (ai|la)(?!\w)|"
    r"temperatura (em|no|na|nos|nas|ai|la|hoje|agora)(?!\w)|qual (e )?a temperatura|quantos graus|"
    r"(ta|esta|vai) (chovendo|chover|nevando|nevar)|chove(ndo)? " + _LOCAL + r"|neva(ndo)? " + _LOCAL + r"|"
    r"(ta|esta|faz|fazendo|muito) (frio|calor|quente|sol) " + _LOCAL + r"|"
    r"(frio|calor|quente|sol|chuva|neve) (em toquio|ai|la)(?!\w)"
    r")"
)

# Depois do gatilho: "em são paulo hoje?" -> "são paulo". Para na pontuação ou numa destas palavras.
_PARADAS = {"hoje", "agora", "amanha", "ai", "la", "pra", "para", "e", "ou", "que", "ne", "hein", "ta", "esta",
            "closure", "kal", "kaltsit", "kal'tsit", "por", "favor", "pfv", "pfvr", "vc", "voce", "today", "now", "tomorrow", "please", "and"}
# "de/do/da" precisa do assunto do clima antes, com marcador temporal opcional:
# "clima atual de BH". Não captura "preciso de ajuda" nem "em" de outra frase.
_ANTES_DO_LUGAR = re.compile(
    r"(?<!\w)(?:(?:em|no|na|nos|nas|in|for)|"
    r"(?:clima|temperatura|tempo|weather|temperature|forecast)(?:\s+(?:atual|hoje|agora))?\s+(?:de|do|da|of))\s+"
)
_NAO_E_LUGAR = {"toquio", "tokyo", "o", "a", "tempo", "clima", "casa", "geral"}


def fala_de_clima(texto: str) -> bool:
    return bool(_GATILHOS.search(_sem_acento(texto)))


def lugar_citado(texto: str) -> str | None:
    """O lugar de que a mensagem pergunta o clima, como foi escrito; None se não cita lugar (vale Tóquio)."""
    original = unicodedata.normalize("NFC", texto)
    norm = _sem_acento(original)
    gatilho = _GATILHOS.search(norm)
    if not gatilho:
        return None
    # Só a frase da pergunta: do começo do gatilho até a primeira pontuação de fim depois dele.
    fim = re.search(r"[?!.\n]", norm[gatilho.end():])
    trecho_fim = gatilho.end() + fim.start() if fim else len(norm)
    for prep in _ANTES_DO_LUGAR.finditer(norm, gatilho.start(), trecho_fim):
        palavras = []
        for achou in re.finditer(r"[\w'’\-]+|[^\w\s]", norm[prep.end():trecho_fim]):
            if not re.match(r"[\w'’\-]+$", achou.group()) or achou.group() in _PARADAS or len(palavras) == 6:
                break
            palavras.append((prep.end() + achou.start(), prep.end() + achou.end()))
        if not palavras:
            continue
        nome = original[palavras[0][0]:palavras[-1][1]].strip()
        if _sem_acento(nome) in _NAO_E_LUGAR:
            continue
        return nome[:60]
    return None


def acao_painel(agora: datetime, postado_em: str | None, ultimo_estado: str | None, estado: str) -> str | None:
    """O que fazer com o painel diário: "postar" (uma vez por dia, depois das 6h), "editar" (o tempo mudou) ou None."""
    hoje = agora.date().isoformat()
    if postado_em != hoje:
        return "postar" if agora.hour >= HORA_DO_PAINEL else None
    return "editar" if estado != ultimo_estado else None


class ServicoClima:
    """Busca clima e lugares com cache. `buscar(url)` devolve o JSON; em produção é o aiohttp, no teste é uma função falsa."""

    def __init__(self, buscar: Callable[[str], Awaitable[dict]] | None = None, relogio: Callable[[], float] = time.monotonic):
        self._buscar = buscar or _buscar_http
        self._relogio = relogio
        self._leituras: dict[tuple[float, float], tuple[Clima, float]] = {}
        self._lugares: dict[str, Lugar | None] = {}

    async def agora(self, lugar: Lugar = TOQUIO) -> Clima | None:
        """A leitura atual do lugar, ou None se não há leitura recente e a API não respondeu."""
        chave = (round(lugar.latitude, 2), round(lugar.longitude, 2))
        ultimo, lido_em = self._leituras.get(chave, (None, 0.0))
        idade = self._relogio() - lido_em
        if ultimo and idade < VALIDADE:
            return ultimo
        try:
            resposta = await self._buscar(URL_CLIMA.format(lat=lugar.latitude, lon=lugar.longitude))
            ultimo = interpretar(resposta, lugar.nome)
            if len(self._leituras) >= MAX_LUGARES:
                self._leituras.clear()
            self._leituras[chave] = (ultimo, self._relogio())
        except Exception as erro:  # rede, tempo esgotado ou resposta fora do formato: nunca derruba o bot
            log.warning("clima: falha ao ler %s (%s)", lugar.nome, erro)
            if not ultimo or idade > TOLERANCIA:
                return None
        return ultimo

    async def procurar(self, nome: str) -> Lugar | None:
        """Acha o lugar pelo nome. None se a busca não achou; levanta se a busca falhou."""
        chave = _sem_acento(nome).strip()[:60]
        if chave in ("toquio", "tokyo"):
            return TOQUIO
        if chave not in self._lugares:
            if len(self._lugares) >= MAX_LUGARES:
                self._lugares.clear()
            self._lugares[chave] = await self._procurar_por_partes(nome.strip()[:60])
        return self._lugares[chave]

    async def _procurar_por_partes(self, nome: str) -> Lugar | None:
        """A busca só conhece o nome da cidade: "belo horizonte minas gerais" e "Belo Horizonte - MG" não acham nada.
        Sem resultado, tenta a parte antes do traço, da barra ou da vírgula, e depois tira palavras do fim (até
        cinco tentativas a mais); o que sobrou serve pra escolher o estado ou o país."""
        consulta = APELIDOS_DE_LUGAR.get(_sem_acento(nome).strip(), nome)
        lugar = interpretar_lugar(await self._buscar(URL_LUGAR.format(nome=quote(consulta))))
        if lugar:
            return lugar
        partes = re.split(r"\s*[-/,]\s*", consulta, maxsplit=1)
        cidade, resto = partes[0], (partes[1] if len(partes) > 1 else "")
        palavras = cidade.split()
        tentativas = [len(palavras)] if resto else []
        tentativas += [k for k in range(len(palavras) - 1, 0, -1)][:5]
        for k in tentativas:
            regiao = " ".join(palavras[k:] + resto.split())
            # o que foi cortado tem que ser o estado ou o país: "santa maria rio" não pode virar uma cidade italiana
            lugar = interpretar_lugar(await self._buscar(URL_LUGAR.format(nome=quote(" ".join(palavras[:k])))), regiao,
                                      exigir=True)
            if lugar:
                return lugar
        return None


# Continuação curta, ancorada na fala (não no meio de outra frase).
_SEGUE_CLIMA = re.compile(
    r"^\s*(?:(?:closure|kal(?:['’]?tsit)?)\s*[,!:]?\s*)?(?:e|and)\s+"
    r"(?=(?:em|no|na|nos|nas|de|do|da|in|for)\s+)"
)


def pergunta_clima(texto: str, anterior: str | None = None) -> str | None:
    """Resolve a pergunta explícita ou a troca de cidade após assunto meteorológico.

    A forma resolvida pode ser encadeada na memória existente; texto de outro
    assunto devolve None e encerra a continuidade, sem guardar estado novo.
    """
    original = unicodedata.normalize("NFC", texto)
    if fala_de_clima(original):
        return original
    segue = _SEGUE_CLIMA.search(_sem_acento(original)) if anterior and fala_de_clima(anterior) and len(texto) <= 80 else None
    if segue:
        return "como está o clima " + original[segue.end():]
    return None


def lugar_para_consulta(texto: str) -> str | None:
    """Comando já declara clima: aceita a cidade ou uma pergunta inteira sobre ela."""
    pergunta = pergunta_clima(texto, "qual o clima?")
    return lugar_citado(pergunta) if pergunta else texto.strip()


async def contexto_clima(servico: ServicoClima, texto: str, anterior: str | None = None) -> str | None:
    """Dado meteorológico para a pergunta; `anterior` pode ser a continuação resolvida."""
    texto = pergunta_clima(texto, anterior)
    if texto is None:
        return None
    citado = lugar_citado(texto)
    lugar = TOQUIO
    if citado:
        try:
            lugar = await servico.procurar(citado)
        except Exception as erro:
            log.warning("clima: falha ao procurar %r (%s)", citado, erro)
            return None
        if lugar is None:
            limpo = re.sub(r"[\[\]\"\n\r]", " ", citado).strip()
            return f'[Clima: o monitor não achou o lugar "{limpo}".]'
    leitura = await servico.agora(lugar)
    log.info("clima: contexto para %s; leitura=%s", lugar.nome, "disponível" if leitura else "indisponível")
    return linha_bloco4(leitura) if leitura else None


async def _buscar_http(url: str) -> dict:
    import aiohttp  # já vem com o discord.py

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as sessao:
        async with sessao.get(url) as resposta:
            resposta.raise_for_status()
            return await resposta.json()
