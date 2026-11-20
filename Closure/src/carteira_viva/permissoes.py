"""Capacidades de personagens; independentes dos cargos de idioma e lore."""
from dataclasses import dataclass
from enum import Enum


class Acao(str, Enum):
    CADASTRAR = "cadastrar"
    VER_CARTAO = "ver_cartao"
    VER_DETALHES = "ver_detalhes"
    ANALISAR = "analisar"
    PERSONALIZAR = "personalizar"
    TROCAR_ARQUIVO = "trocar_arquivo"
    EXCLUIR = "excluir"
    CONFIGURAR = "configurar"
    EDITAR_JOGO = "editar_jogo"


@dataclass(frozen=True)
class Membro:
    servidor: str
    usuario: str
    presente: bool = True
    dono_servidor: bool = False
    administrador: bool = False
    gerenciar_servidor: bool = False
    cargos: frozenset[str] = frozenset()
    nome: str = ""

    def __post_init__(self):
        if (not isinstance(self.servidor, str) or not self.servidor.strip() or
                not isinstance(self.usuario, str) or not self.usuario.strip() or
                any(type(x) is not bool for x in (self.presente, self.dono_servidor,
                                                  self.administrador, self.gerenciar_servidor)) or
                not isinstance(self.nome,str) or len(self.nome)>100 or not isinstance(self.cargos, frozenset) or
                any(not isinstance(x, str) or not x.strip() for x in self.cargos)):
            raise ValueError("Identidade de membro inválida.")


@dataclass(frozen=True)
class Permissoes:
    revisores: frozenset[str] = frozenset()
    editores: frozenset[str] = frozenset()


def permitido(acao: Acao, membro: Membro, servidor: str, dono: str | None,
              permissoes: Permissoes = Permissoes(), *,
              operacao_liberada: bool = False, consentimento_edicao: bool = False) -> bool:
    if not membro.presente or membro.servidor != servidor:
        return False
    if acao in (Acao.CADASTRAR, Acao.VER_CARTAO):
        return True
    admin = membro.dono_servidor or membro.administrador
    proprio = dono is not None and membro.usuario == dono
    if acao in (Acao.VER_DETALHES, Acao.ANALISAR):
        return proprio or admin or bool(membro.cargos & permissoes.revisores)
    if acao in (Acao.PERSONALIZAR, Acao.TROCAR_ARQUIVO, Acao.EXCLUIR):
        return proprio
    if acao == Acao.CONFIGURAR:
        return admin
    if acao == Acao.EDITAR_JOGO:
        return (operacao_liberada and consentimento_edicao and
                (proprio or admin or bool(membro.cargos & permissoes.editores)))
    return False


PUBLICOS = frozenset({"nome", "titulo", "frase", "idade", "cla", "origem",
                     "caminho", "imagem_id", "cor"})


def cartao_publico(perfil: dict, autorizados: frozenset[str]) -> dict:
    return {chave: perfil[chave] for chave in PUBLICOS & autorizados if chave in perfil}
