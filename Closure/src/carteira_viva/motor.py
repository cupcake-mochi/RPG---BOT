"""Motor existente e campanha local confiável; nenhuma regra vem do navegador."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .segredos import ErroCarteira, json_bytes


@dataclass(frozen=True)
class Campanha:
    servidor: str
    revisao: str
    nome: str
    regras: object
    aprovados: object


class Motor:
    def __init__(self, dados: Path, campanhas: Path):
        from closure_bot.ficha_corretor import Referencias
        self.referencias = Referencias.do_livro(dados)
        self.campanhas = campanhas
        raiz = Path(__file__).resolve().parents[1]
        entradas = (list((raiz / "closure_bot").glob("ficha*.py")) +
                    list((raiz / "closure_bot" / "r53").glob("*.*")) +
                    list((raiz / "closure_bot" / "recursos").glob("*.*")) +
                    list((Path(dados) / "sistema").glob("*.*")) + [raiz / "var/site/nucleo.js"])
        h = hashlib.sha256()
        for caminho in sorted(p for p in entradas if p.is_file()):
            h.update(caminho.name.encode()); h.update(caminho.read_bytes())
        self.revisao = h.hexdigest()

    def campanha(self, servidor: str) -> Campanha:
        from closure_bot.ficha_corretor import RegrasDaCampanha, Aprovados
        from closure_bot.ficha_configuracao import regras_autorizadas
        try:
            # Falta de arquivo configurado é falha, não retorno silencioso ao livro.
            if self.campanhas.stat().st_size > 2 * 1024 * 1024:
                raise ValueError()
            with self.campanhas.open("rb") as f:
                corpo = f.read(2 * 1024 * 1024 + 1)
            if len(corpo) > 2 * 1024 * 1024:
                raise ValueError()
            todos = json.loads(corpo)
            if not isinstance(todos, dict):
                raise ValueError()
            cadastro = todos.get(servidor, {})
            if not isinstance(cadastro, dict):
                raise ValueError()
            if (not isinstance(cadastro.get("nome", "livro"), str) or
                    len(cadastro.get("nome", "livro")) > 200 or
                    not isinstance(cadastro.get("regras", {}), dict)):
                raise ValueError()
            regras = RegrasDaCampanha(nome=cadastro.get("nome", "livro"), valores=cadastro.get("regras", {}))
            regras_autorizadas(regras)
            aprovados = Aprovados(cadastro.get("aprovados", {}))
            if not isinstance(aprovados.impressoes, dict):
                raise ValueError()
            revisao = hashlib.sha256(json_bytes([servidor, cadastro])).hexdigest()
            return Campanha(servidor, revisao, regras.nome, regras, aprovados)
        except (OSError, ValueError, TypeError, AttributeError):
            raise ErroCarteira("Não foi possível carregar a campanha autorizada deste servidor.") from None

    def conferir(self, ficha, campanha: Campanha) -> dict:
        from closure_bot.ficha_corretor import conferir
        return asdict(conferir(ficha, self.referencias, campanha.regras, campanha.aprovados))
