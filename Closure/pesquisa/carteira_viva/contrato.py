"""Contrato executável da etapa 1. Não importado pelo bot nem incluído no ZIP.

As identidades deste módulo devem vir de provedores verificados no servidor,
nunca diretamente do JSON enviado pelo navegador. A prova não implementa OAuth.
"""
from dataclasses import dataclass
from enum import Enum


class Acao(str, Enum):
    CADASTRAR = "cadastrar"
    VER_CARTAO = "ver_cartao"
    VER_DETALHES = "ver_detalhes"
    ANALISAR = "analisar"
    PERSONALIZAR = "personalizar"
    TROCAR_ARQUIVO = "trocar_arquivo"
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


@dataclass(frozen=True)
class Permissoes:
    revisores: frozenset[str] = frozenset()
    editores: frozenset[str] = frozenset()


def permitido(acao: Acao, membro: Membro, servidor: str, dono: str | None,
              permissoes: Permissoes = Permissoes(), *,
              operacao_liberada: bool = False, consentimento_edicao: bool = False) -> bool:
    """A consulta de membro/cargos atual é responsabilidade do adaptador Discord."""
    if not membro.presente or membro.servidor != servidor:
        return False
    if acao in (Acao.CADASTRAR, Acao.VER_CARTAO):
        return True
    admin = membro.dono_servidor or membro.administrador
    proprio = dono is not None and membro.usuario == dono
    if acao in (Acao.VER_DETALHES, Acao.ANALISAR):
        return proprio or admin or bool(membro.cargos & permissoes.revisores)
    if acao in (Acao.PERSONALIZAR, Acao.TROCAR_ARQUIVO):
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
    """Lista positiva: não enviar snapshot/links privados para ocultar no frontend."""
    return {chave: perfil[chave] for chave in PUBLICOS & autorizados if chave in perfil}
