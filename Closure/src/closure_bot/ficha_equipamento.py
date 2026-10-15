"""Requisitos tabelados de equipamento; inventário incompleto não certifica carga.

O catálogo vem do livro. Nomes próprios, anatomia e autorizações não são deduzidos
da aparência nem dos avisos calculados da planilha.
"""
from dataclasses import dataclass
from decimal import Decimal
import math
import re


def numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def vazio(v):
    return v in ("", "—", "-", "Soco")


@dataclass(frozen=True)
class Equipamento:
    forca: int
    volume: Decimal
    maos: int = 0
    fineza: bool = False
    disparo: bool = False
    fogo: bool = False
    arremesso: bool = False
    tipo: str = "arma"


@dataclass(frozen=True)
class CatalogoEquipamento:
    pecas: dict[str, Equipamento]
    patentes: dict[str, int]

    @classmethod
    def do_livro(cls, livro):
        pecas = {}
        for a, texto in livro.items():
            if not a.startswith("equip--eqa-"):
                continue
            disparo = fogo = False
            for linha in texto.splitlines():
                if linha.startswith("#### "):
                    categoria = linha.removeprefix("#### ")
                    disparo = categoria in ("Yumi", "Balestra", "Arma de Fogo")
                    fogo = categoria == "Arma de Fogo"
                p = [s.strip() for s in linha.strip("|").split("|")]
                if len(p) != 7 or p[1] not in ("1", "2"):
                    continue
                nome, maos, dano, prop, forca, vol, preco = p
                e = Equipamento(0 if forca == "—" else int(forca), Decimal(vol.replace(",", ".")),
                                int(maos), "Fineza" in prop, disparo, fogo, "Longo Alcance" in prop and not disparo)
                for alias in (nome, re.sub(r"\s*\(.*\)$", "", nome)):
                    if alias in pecas and pecas[alias] != e:
                        raise ValueError("o livro tem nomes ambíguos de equipamento")
                    pecas[alias] = e
        for a, prefixo in (("equip--eqp-traje", "Traje "), ("equip--eqp-escudo", "Revestimento ")):
            for linha in livro[a].splitlines():
                p = [s.strip() for s in linha.strip("|").split("|")]
                if len(p) not in (5, 6) or not re.fullmatch(r"\+\d+", p[1]):
                    continue
                nome, _, _, forca, vol = p[:5]
                pecas[prefixo + nome if nome.isdigit() else nome] = Equipamento(
                    int(forca) if forca.isdigit() else 0, Decimal(vol.replace(",", ".")),
                    1 if nome in ("Broquel", "Médio", "Torre") else 0,
                    tipo="escudo" if nome in ("Broquel", "Médio", "Torre") else "uniforme")
        patentes = {n: int(g) for n, g in re.findall(r"^\| ([^|]+) \| Grau (\d+) ou superior", livro["equip--eqc-dinheiro"], re.M)}
        guardas = {"geral--carga": "5 + Força", "equip--eq-equipamento": "Sem a Força exigida",
                   "equip--eqp-protecao": "recebe sua proteção e seus benefícios",
                   "equip--eqc-dinheiro": "Revestimento 3", "campo--inv-carga": "5 + Força"}
        if len(patentes) != 3 or not all(n in pecas for n in ("Katana", "Besta", "Pistola", "Traje 3", "Revestimento 3", "Torre")) or any(
                t not in livro[a] for a, t in guardas.items()):
            raise ValueError("o livro mudou os requisitos/carga: revise o corretor")
        return cls(pecas, patentes)


def conferir_uso(ficha, catalogo, r, *, base="", atributos=None):
    """Falta de Força é pendência, nunca perda de proteção nem reprovação.

    Nas entidades só há três peças exportadas. A soma é um subtotal do equipamento,
    sem autorizar armazenamento/passageiros e sem certificar a carga completa.
    """
    from .ficha_corretor import Problema
    from .ficha_magia import valor, rotulo
    entidade = bool(base)
    nome = rotulo(base) if entidade else "Equipamento"
    campos = ([base + f".equipamento.{i}" for i in range(1, 4)] if entidade else
              ["em_uso.principal", "em_uso.secundaria", "em_uso.vestindo"])
    if catalogo is None or not all(k in ficha for k in campos):
        r.nao_conferido.append(f"{nome}: faltam entradas/referências de equipamento")
        return
    if atributos is None:
        partes = [valor(ficha, "atributo.forca." + p) for p in ("base", "corpo")]
        forca = partes[0] + (partes[1] or 0) if numero(partes[0]) and (partes[1] == "" or numero(partes[1])) else None
    else:
        forca = atributos.get("forca")
    principal = catalogo.pecas.get(valor(ficha, campos[0]))
    soma = Decimal(0)
    completo = True
    for i, k in enumerate(campos):
        n = valor(ficha, k)
        if vazio(n):
            continue
        e = catalogo.pecas.get(n)
        if e is None:
            completo = False
            r.nao_conferido.append(f"{nome}: equipamento próprio ou não reconhecido ({n})")
            continue
        soma += e.volume  # um escudo guardado ainda pesa
        em_uso = i != 1 or principal is None or principal.maos != 2
        if em_uso and forca is not None and forca < e.forca:
            aviso = ficha.get(("aviso.forca_p", "aviso.forca_s", "aviso.forca_v")[i]) if not entidade else None
            # O aviso coincidente já será exibido pela conferência central. Se ele
            # sumiu ou foi adulterado, a conta independente ainda gera a pendência.
            if aviso is None or aviso.parte != "aviso" or aviso.valor != f"Falta Força: {forca:g} de {e.forca}":
                r.pendencias.append(Problema("equipamento", k,
                    f"Força {e.forca} para usar {n} sem penalidade; deslocamento pela metade",
                    f"Força {forca:g}", "equip--eq-equipamento" if e.maos and n not in ("Broquel", "Médio", "Torre") else "equip--eqp-protecao"))
        if not entidade and (n in ("Revestimento 2", "Revestimento 3") or e.fogo):
            grau = str(valor(ficha, "grau"))
            ordem = {"Grau 4": 4, "Grau 3": 3, "Grau 2": 2, "Grau 1": 1, "Especial": 0, "Grau Especial": 0}.get(grau)
            teto = catalogo.patentes["Armas de fogo e sua munição" if e.fogo else n]
            if ordem is None:
                r.nao_conferido.append(f"{nome}: patente ausente/desconhecida para {n}")
            elif ordem > teto:
                destino = r.notas if e.fogo else r.problemas
                destino.append(Problema("equipamento", k, f"Grau {teto} ou superior" +
                    (" ou autorização prévia" if e.fogo else ""), grau, "equip--eqc-dinheiro"))
    if forca is None:
        r.nao_conferido.append(f"{nome}: Força de entrada ausente/inválida impede conferir requisitos e carga")
    elif entidade and completo:
        limite = Decimal(str(5 + forca))
        r.conferidos.append(f"{nome}: equipamento listado {soma} Volume; limite básico {limite}")
        if soma > limite:
            r.pendencias.append(Problema("carga", base + ".equipamento",
                "reduzir a carga para se deslocar" if soma > 2 * limite else "deslocamento pela metade enquanto acima do limite",
                f"{soma} de {limite} Volume apenas nas peças listadas", "campo--inv-carga"))
    r.nao_conferido.append(f"{nome}: anatomia e carga adicional/total precisam de conferência" if entidade else
        "Carga pessoal: a ANALISE não exporta quantidade dos equipáveis, Volume dos itens livres nem Buff do limite; total não certificado")


def ataques_armados(e, atributos, maestria, buff):
    """Bônus possíveis sem inventar a escolha Fineza/corpo a corpo/arremesso."""
    chaves = {"destreza"} if e.disparo else {"forca", "destreza"} if e.fineza or e.arremesso else {"forca"}
    return {atributos[k] + maestria + buff for k in chaves}
