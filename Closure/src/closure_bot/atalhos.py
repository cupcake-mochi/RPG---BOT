"""Atalhos públicos: nomes fixos e destinos permitidos para cada servidor."""
from __future__ import annotations
from .idiomas import tr

import re
import unicodedata

PUBLICOS = {"ajuda", "guia", "ficha", "livro", "clima", "ping", "status"}
SO_NA_BARRA = {"meus_dados", "meus_pronomes", "meu_fato", "esquecer_fato", "apagar_meus_dados",
               "clima_canal", "clima_canal_desligar", "teste_webhook", "responder_nsfw", "nsfw_canal", "atalho", "idioma", "language", "lnt", "lore_nova_terra", "cargo_admin"}
OUTROS_NOMES = {"guide": "guia", "sheet": "ficha", "character": "ficha", "analyze": "ficha", "analyse": "ficha", "book": "livro", "rules": "livro", "weather": "clima","help": "ajuda", "comandos": "ajuda", "tempo": "clima", "sistema": "livro", "pdf": "livro",
                "analisar": "ficha", "analise": "ficha"}
CURTOS = {"a": "ajuda", "g": "guia", "f": "ficha", "l": "livro", "c": "clima", "p": "ping", "s": "status",
          "gc": "guia criar", "gp": "guia planilha", "gf": "guia ficha", "gm": "guia mestre",
          "ab": "ajuda abreviacoes"}
MAX_ATALHOS = 20


def limpo(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower().strip()


def destinos() -> dict[str, str]:
    from .guias import ASSUNTOS
    return {"ajuda": "Ajuda", "ficha": "Analisar uma ficha", "livro": "Abrir o livro", "clima": "Consultar clima",
            "ping": "Conferir conexão", "status": "Ver estado do bot", "guia": "Escolher um guia",
            "ajuda abreviacoes": "Abreviações",
            **{f"guia {tema}": f"Guia: {titulo}" for tema, (titulo, _) in ASSUNTOS.items()}}


def nome_proprio(nome: str) -> str:
    nome = limpo(nome)
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,23}", nome):
        raise ValueError(tr('Use um nome de até 24 caracteres: letras, números ou _, começando por uma letra.'))
    if nome in PUBLICOS | SO_NA_BARRA | OUTROS_NOMES.keys() | CURTOS.keys() | {"atalhos"}:
        raise ValueError(tr('Esse nome já pertence a um comando ou atalho do bot. Escolha outro.'))
    return nome


def validar(nome: str, destino: str) -> tuple[str, str]:
    nome = nome_proprio(nome)
    if destino not in destinos():
        raise ValueError(tr('Escolha um destino da lista. Atalhos só abrem comandos públicos do bot.'))
    return nome, destino


def validos(personalizados: dict[str, str] | None) -> dict[str, str]:
    saida = {}
    for nome, destino in (personalizados or {}).items():
        try:
            chave, alvo = validar(nome, destino)
        except (ValueError, TypeError, AttributeError):
            continue
        saida[chave] = alvo
    return dict(sorted(saida.items()))


def resolver(nome: str, resto: str, personalizados: dict[str, str] | None = None) -> tuple[str, str]:
    nome = limpo(nome)
    alvo = CURTOS.get(nome) or OUTROS_NOMES.get(nome)
    if nome == "atalhos":
        alvo = "ajuda abreviacoes"
    if alvo is None:
        alvo = validos(personalizados).get(nome, nome)
    comando, _, argumento = alvo.partition(" ")
    return comando, " ".join(p for p in (argumento, resto) if p)


def orientacao(personalizados: dict[str, str] | None = None) -> str:
    """Informação do produto para as duas personagens; não é um fato pessoal."""
    texto = (
        "[Recursos reais deste bot: /ajuda ou GC:ajuda lista os comandos e tem a página Abreviações. "
        "GC:guia criar ensina a criação até EMITIR; GC:guia planilha explica abas/configurações; "
        "GC:guia ficha ou /ficha guia explica a análise; GC:guia mestre ou /ficha mestre orienta a revisão humana. "
        "GC:ficha LINK ou /ficha analisar confere a ficha sem IA; também aceita XLSX anexo. "
        "Atalhos públicos: " + "; ".join(f"GC:{nome} = GC:{alvo}" for nome, alvo in CURTOS.items()) + ". "
        "Os nomes completos continuam funcionando. /atalho definir, remover e listar configuram atalhos do servidor "
        "e exigem Gerenciar servidor. Esses comandos não aprovam customizações. "
        "O livro tem tema normal e tema escuro em /livro ou GC:book. "
        "/idioma ou /language escolhe português ou inglês por servidor; /lnt liga ou desliga a lore Nova Terra. "
        "Essas duas configurações exigem Gerenciar servidor ou cargo delegado por /cargo_admin; só a gerência delega cargos. "
        "A Arquivista tem idioma próprio, configurado separadamente. "
        "GC:guide, GC:sheet, GC:book e GC:weather também são nomes aceitos. "
        "Quando receber URLs de recursos públicos neste pedido, pode enviá-las diretamente: não precisa mandar o usuário digitar um comando para obter um link. Falar de um comando não o executa nem registra aprovação."
    )
    extras = validos(personalizados)
    if extras:
        texto += " Atalhos deste servidor: " + "; ".join(f"GC:{n} = GC:{d}" for n, d in extras.items()) + "."
    return texto + "]"
