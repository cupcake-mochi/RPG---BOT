"""Preferências públicas por servidor; ausências nunca autorizam a lore privada."""
from __future__ import annotations

from dataclasses import dataclass

NOVA_TERRA_PADRAO = frozenset({1361766037405564988, 1357866906341736488, 1480606366090526893})
IDIOMAS = frozenset({"pt-BR", "en"})


@dataclass(frozen=True)
class OpcoesServidor:
    idioma: str = "pt-BR"
    nova_terra: bool = False
    cargos: tuple[int, ...] = ()
    revisao: int = 0

    def contexto(self, guild_id: int) -> str:
        return f"{guild_id}:{'nova-terra' if self.nova_terra else 'original'}"


def administrador(membro, permissoes=None) -> bool:
    p = permissoes if permissoes is not None else getattr(membro, "guild_permissions", None)
    return bool(p and (p.administrator is True or p.manage_guild is True))


def autorizado(membro, opcoes: OpcoesServidor, permissoes=None) -> bool:
    return administrador(membro, permissoes) or any(
        getattr(cargo, "id", None) in opcoes.cargos for cargo in getattr(membro, "roles", ()))
