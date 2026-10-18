"""Alcance e resolução da montagem; resultados da ficha nunca são entradas das contas.

Não interpreta regras escritas em prosa nem inventa distribuição entre tiros/alvos.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass


def _tabela(texto):
    return {p[0]: p[1:] for l in texto.splitlines() if l.startswith("| ")
            and (p := [v.strip() for v in l.strip("|").split("|")])}


@dataclass(frozen=True)
class Medidas:
    bases: dict
    entidades: dict
    escadas: dict

    @classmethod
    def do_livro(cls, livro):
        texto = livro["fundamento--alcance"]
        tabelas = _tabela(texto)
        escadas = {k: tuple(float(n.replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", tabelas[k][0]))
                   for k in ("Distância ao alvo ou ponto", "Raio de esfera", "Comprimento de Cone ou Linha")}
        # A última distância é textual. Ela continua sendo o último degrau.
        if "visão a olho nu" not in tabelas["Distância ao alvo ou ponto"][0]:
            raise ValueError("o livro mudou a escada de alcance")
        escadas["Distância ao alvo ou ponto"] += (math.inf,)
        ent = _tabela(livro["construcao--entidades-medidas"])
        if (len(escadas["Raio de esfera"]) != 5 or len(escadas["Comprimento de Cone ou Linha"]) != 5
                or "Depois aumenta a largura de 1,5 m para 3 m e então 4,5 m" not in texto
                or "Especial 7" not in ent.get("Área básica", [])):
            raise ValueError("o livro mudou as medidas: revise as contas")
        return cls(tabelas, ent, escadas)

    def alcance(self, forma, classe, pecas, *, entidade=False, legado=False):
        """Texto usual da carta, calculado das bases/escadas do livro R51.

        legado só identifica a fórmula antiga de Linha, cuja largura não cresce.
        Não é aceito como número conferido.
        """
        faixa = 0 if classe == 0 else 1 if classe <= 5 else 2
        area_faixa = 0 if classe == 0 else 1 if classe <= 6 else 2
        longe = pecas.count("Longe") + 3 * pecas.count("Muito Longe")
        maior = pecas.count("Maior") + 3 * pecas.count("Muito Maior")
        def numeros(t):
            return [float(n.replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", t)]
        def base(pessoal, ent=None, *, area=False):
            tabela = self.entidades if entidade and ent else self.bases
            return numeros(tabela[ent if entidade and ent else pessoal][area_faixa if entidade and area else faixa])
        def sobe(escada, inicial, passos):
            esc = self.escadas[escada]
            if not passos:
                return inicial
            i = next(i for i, v in enumerate(esc) if v >= inicial)
            if esc[i] != inicial:
                i -= 1
            return esc[min(len(esc) - 1, i + passos)]
        def m(n):
            return "visão a olho nu" if math.isinf(n) else f"{n:g}".replace(".", ",") + " m"
        distancia, raio, comprimento = self.escadas
        extra = ""
        if forma in ("Projétil", "Toque"):
            alvos = pecas.count("Mais Um")
            if alvos:
                extra += f" · +{alvos} alvo" + ("s" if alvos > 1 else "")
            if "Rajada" in pecas:
                tiros = (max(1, classe - 1) + 1 if classe else 1) if entidade else classe + 1
                extra += f" · {tiros} tiro" + ("s" if tiros > 1 else "")
        if forma == "Projétil":
            texto = m(sobe(distancia, base(forma, "Projétil e ponto de Explosão")[0], longe)) + ", um alvo" + extra
        elif forma == "Toque":
            texto = m(base(forma, forma)[0]) + ", um alvo" + extra
        elif forma == "Explosão":
            if entidade:
                alcance = base(forma, "Projétil e ponto de Explosão")[0]
                r = base(forma, "Explosão e Aura: raio", area=True)[0]
            else:
                alcance, r = base(forma)
            texto = "raio " + m(sobe(raio, r, maior)) + ", a " + m(sobe(distancia, alcance, longe))
        elif forma in ("Aura", "Onda"):
            r = base(forma, "Explosão e Aura: raio" if forma == "Aura" else "Onda: raio", area=True)[0]
            texto = "raio " + m(sobe(raio, r, maior)) + ", em você"
        elif forma == "Cone":
            texto = "cone de " + m(sobe(comprimento, base(forma, "Cone: comprimento", area=True)[0], maior + longe))
        elif forma == "Linha":
            c, largura = base(forma, "Linha: comprimento × largura", area=True)
            # Longe só cresce comprimento; Maior continua pela largura após 60 m.
            c = sobe(comprimento, c, longe)
            for _ in range(maior):
                if c < self.escadas[comprimento][-1]:
                    c = sobe(comprimento, c, 1)
                elif not legado:
                    largura = min(4.5, largura + 1.5)
            texto = "linha de " + m(c) + " por " + m(largura)
        elif forma in ("Cura", "Apoio"):
            # Cura na Classe 0 é rejeitada na seleção antes desta conta.
            b = base("Cura e Apoio", forma)[0]
            if not entidade and forma == "Cura" and classe == 0:
                raise ValueError("Cura indisponível na Classe 0")
            texto = "um aliado a " + m(sobe(distancia, b, longe))
        else:
            texto = "fora de combate"
        return texto[:1].upper() + texto[1:]


def conferir_medidas(ficha, magia, base, classe, forma, pecas, problemas, certos, pulou, pendencias, *, entidade=False):
    from .ficha_magia import rotulo, valor
    from .ficha_corretor import Problema
    nome = rotulo(base)
    if forma in ("Cura", "Onda") and classe == 0:
        return
    if base + ".alcance" not in ficha:
        pulou.append(f"{nome}: alcance não exportado nesta ficha")
        return
    esperado = magia.medidas.alcance(forma, classe, pecas, entidade=entidade)
    encontrado = str(valor(ficha, base + ".alcance"))
    if encontrado.casefold() == esperado.casefold():
        certos.append(f"{nome}: alcance {esperado}")
        return
    legado = magia.medidas.alcance(forma, classe, pecas, entidade=entidade, legado=True)
    p = Problema("conta", base + ".alcance", esperado, encontrado,
                 "construcao--entidades-medidas" if entidade else "fundamento--alcance")
    if esperado != legado and encontrado.casefold() == legado.casefold():
        pendencias.append(p)
    else:
        problemas.append(p)


def melhoria_exige_tr(magia, nome):
    d=next((d for d in magia.contexto.registros.values() if d.tipo=='melhoria' and d.nome==nome and d.valida and d.aprovada),None) if magia.contexto else None
    if d and d.efetivos.get('exige_tr') in ('Sim','Não'):
        return d.efetivos['exige_tr']=='Sim'
    return (nome in ('Prende','Cerca') or nome.startswith('Condição: ') or
            nome in magia.melhorias and magia.melhorias[nome].familia=='Controle' and nome not in ('Terreno','Desarma o Feitiço'))


def eh_condicao(magia,nome):
    d=next((d for d in magia.contexto.registros.values() if d.tipo=='melhoria' and d.nome==nome),None) if magia.contexto else None
    identidade=magia.contexto.aliases.get('melhoria:'+nome,nome) if magia.contexto else nome
    return bool(d and d.efetivos.get('modalidade')=='Condição' or identidade.startswith('Condição: ') or 'Condição: '+identidade in magia.melhorias)


def conferir_resolucao(ficha, magia, base, forma, pecas, problemas, certos, pulou, *, entidade=False, pendencias=None,saldo_controle=None):
    from .ficha_magia import rotulo, valor
    from .ficha_corretor import Problema
    nome = rotulo(base)
    if base + ".resolve" not in ficha:
        pulou.append(f"{nome}: resolução não exportada nesta ficha")
        return
    controle = any(melhoria_exige_tr(magia,n) for n in pecas)
    bonus_controle=any(n in magia.melhorias and magia.melhorias[n].familia=='Controle' for n in pecas) if magia.contexto else None
    pecas = [magia.contexto.aliases.get('melhoria:'+n,n) for n in pecas] if magia.contexto else pecas
    automatico = forma in ("Cura", "Apoio", "Onda", "Efeito") or "Inescapável" in pecas
    escolhido = valor(ficha, base + ".resolucao_escolha") if entidade else ""
    opcoes = ("", "Ataque", "TR Físico", "TR Vigor", "TR Intelecto", "TR Espírito")
    if escolhido not in opcoes:
        problemas.append(Problema("escolha", base + ".resolucao_escolha", "resolução do livro", str(escolhido), "construcao--entidades-formas"))
        return
    ataque = escolhido == "Ataque" or not escolhido and forma in ("Projétil", "Toque")
    if "Certeiro" in pecas:
        ataque = False
    if not entidade:
        esperado = ("Automático" if automatico else "TR para metade" if "Certeiro" in pecas else
                    "Acerto + TR" if ataque and controle else "Acerto" if ataque else "TR, metade")
    else:
        if automatico:
            esperado = "Automático" if "Inescapável" in pecas else "Sem rolagem"
        else:
            esperado = "Ataque" if ataque else escolhido or "TR"
            texto = str(valor(ficha, base + ".resolve"))
            num = r"[+-−]?\d+(?:[.,]\d+)?"
            padrao = (r"Ataque(?: [+-−]\d+(?:[.,]\d+)?)?" + (r" · TR(?: CD " + num + r")?" if controle else "") if ataque else
                      re.escape(esperado) + r"(?: · CD " + num + r")?" + (r" · metade" if "Certeiro" in pecas else ""))
            if re.fullmatch(padrao, texto):
                if _conferir_bonus_entidade(ficha, magia, base, esperado, texto, ataque, controle, pecas,
                                            problemas, certos, pulou, pendencias,saldo_controle=saldo_controle,bonus_controle=bonus_controle):
                    return
                pulou.append(f"{nome}: tipo de resolução compatível; valores numéricos não certificados")
                return
    encontrado = str(valor(ficha, base + ".resolve"))
    # O livro permite trocar ataque por TR na criação. A carta pessoal não exporta
    # uma escolha separada: não reprova uma alternativa permitida nem a certifica.
    if (not entidade and not automatico and "Certeiro" not in pecas and "Rajada" not in pecas
            and encontrado != esperado and encontrado in ("TR, metade", "Acerto + TR" if controle else "Acerto")):
        pulou.append(f"{nome}: resolução alternativa exige conferir o TR e resultado escritos na aplicação")
        return
    if encontrado.casefold() != esperado.casefold():
        problemas.append(Problema("conta", base + ".resolve", esperado,
                                  str(valor(ficha, base + ".resolve")), "fundamento--conjurar"))
    else:
        certos.append(f"{nome}: resolução {esperado}")


def _conferir_bonus_entidade(ficha, magia, base, tipo, texto, ataque, controle, pecas,
                            problemas, certos, pulou, pendencias,*,saldo_controle=None,bonus_controle=None):
    from .ficha_magia import inteiro, valor, rotulo
    from .ficha_equipamento import numero
    from .ficha_entidade import ATRIBUTOS, NOMES
    from .ficha_corretor import Problema
    entidade = re.match(r"invocacao\.\d+", base)
    if not entidade:
        return False
    raiz = entidade[0]
    escolhido, dono = valor(ficha, raiz + ".atributo_acerto"), valor(ficha, "nivel")
    if escolhido not in NOMES or not inteiro(dono, 1) or dono not in magia.maestria:
        return False
    atr = ATRIBUTOS[NOMES.index(escolhido)]
    chaves = [raiz + f".atributo.{atr}.base", raiz + f".atributo.{atr}.buff",
              raiz + ".buff.acerto", raiz + ".buff.cd"]
    if not all(k in ficha for k in chaves):
        return False
    valores = [valor(ficha, k) for k in chaves]
    if not inteiro(valores[0], 0, 6) or any(v != "" and not numero(v) for v in valores[1:]):
        return False
    a, b, ba, bc = [v or 0 for v in valores]
    comum = a + b + magia.maestria[dono]
    precisao = 2 if "Precisão" in pecas else 0
    at, cd = comum + ba + precisao, 8 + comum + bc + (0 if ataque else precisao)
    # Sem saldo comprovado, a carta não distingue CD de dano/Controle. Na B47
    # o chamador pode informar o saldo independente; nunca se deriva do texto.
    cds = ({cd} if bonus_controle is False else {cd,cd+2} if saldo_controle is None else {cd+2} if saldo_controle==0 else {cd}) if controle else {cd}
    opcoes = ({f"Ataque {at:+g} · TR CD {n:g}" for n in cds} if ataque and controle else
              {f"Ataque {at:+g}"} if ataque else
              {f"{tipo} · CD {n:g}" + (" · metade" if "Certeiro" in pecas else "") for n in cds})
    normal = texto.replace("−", "-").replace(",", ".")
    if normal not in opcoes:
        p = Problema("conta", base + ".resolve", " ou ".join(sorted(opcoes)), texto, "catalogo--cat-mira")
        legado = not ataque and precisao and normal in {f"{tipo} · CD {n - 2:g}" +
            (" · metade" if "Certeiro" in pecas else "") for n in cds}
        if controle and saldo_controle==0:
            antiga=(f'Ataque {at:+g} · TR CD {cd:g}' if ataque else f'{tipo} · CD {cd:g}'+(' · metade' if 'Certeiro' in pecas else ''))
            legado=legado or normal==antiga
        (pendencias if legado and pendencias is not None else problemas).append(p)
    elif not controle:
        certos.append(f"{rotulo(base)}: bônus da resolução {texto}")
    if controle:
        if saldo_controle is None and bonus_controle is not False:
            pulou.append(f"{rotulo(base)}: CD do Controle e bônus pelo saldo zero precisam de revisão manual; valores não certificados")
        elif normal in opcoes:
            certos.append(f'{rotulo(base)}: CD exclusiva do Controle {next(iter(cds)):g}; saldo calculado {saldo_controle:g}' if bonus_controle is not False else
                          f'{rotulo(base)}: CD do TR {cd:g}; exigência de TR não concede bônus de Controle')
        else:
            pulou.append(f'{rotulo(base)}: CD do TR {next(iter(cds)):g} pela montagem; resultado divergente não certificado')
    pulou.append(f"{rotulo(base)}: TR escolhido e efeito no sucesso precisam estar registrados; conferir o texto")
    return True
