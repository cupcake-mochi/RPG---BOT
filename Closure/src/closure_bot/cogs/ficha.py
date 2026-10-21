"""Correção de ficha pela aba oculta ANALISE (fase 3 do docs/PLANEJAMENTO.md). LIGADO desde 14/10/2026.

`/ficha analisar` (e `GC:ficha`, em cogs/atalho.py) com o link da planilha aberta ou o .xlsx anexo: lê a aba (ficha_leitor.py), confere sem IA
(ficha_corretor.py) e responde no canal com um painel paginado: o que precisa corrigir (reprova), o que falta ou pede atenção
(sobra de pontos, TR por escolher, falta de Força: avisa sem reprovar), o que o mestre confere (Buff/Debuff e Origem
que a ficha não calcula), o que bateu e o que ainda não é conferido. A frase de abertura é fixa, uma por guia e
por veredito, com o nome e o avatar de quem está de plantão (o Mizuki, 14/10/2026: "na voz dela, no chat", com
mensagem fixa se o modelo complicar). O bot nunca escreve na ficha.

Com LIGADO = False o setup não registra o comando. As regras de cada campanha e o registro dos aprovados ainda são só
estrutura (ficha_corretor.RegrasDaCampanha e Aprovados): por enquanto toda ficha é conferida pelo livro.
"""
from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from collections import OrderedDict
from datetime import datetime
from functools import partial

import discord
from discord import app_commands
from discord.ext import commands

from ..ficha_corretor import LIVRO, Problema, Referencias, Resultado, conferir
from ..ficha_leitor import Campo, FichaIlegivel, de_link, de_xlsx
from ..ficha_paginacao import enviar_relatorio
from ..ficha_r53 import escolher_leitura, rotulo_chave, transicoes
from ..plantao import CLOSURE, FUSO, KALTSIT, de_plantao

log = logging.getLogger(__name__)

LIGADO = True  # ligado pelo Mizuki em 14/10/2026, depois do pente fino contra o livro e a ficha
LIMITE_ANEXO = 10_000_000  # a ficha baixada tem uns 1,5 MB
# R53: a troca de Classe salva de forma assíncrona. Releitura limitada do link antes de concluir;
# o que continuar em transição fica pendente, sem aprovar nem reprovar o cartão.
ESPERAS_TRANSICAO = (3, 6)


# Frase fixa de abertura: uma por guia e por veredito, no jeito de cada uma (sem "!" em regra, como nos cards).
FALA = {
    KALTSIT: {"aprovada": "Conferi a ficha. O que eu consigo conferir bate com o livro.",
              "reprovada": "Conferi a ficha. Tem coisa pra corrigir antes da mesa.",
              "formato desconhecido": "Essa ficha é de um formato que eu não conheço. Baixe a versão atual da ficha."},
    CLOSURE: {"aprovada": "Passei o pente fino na ficha e o que dá pra conferir tá batendo.",
              "reprovada": "Passei o pente fino na ficha e achei umas coisas pra arrumar.",
              "formato desconhecido": "Esse formato de ficha eu não conheço. Pega a versão nova da ficha?"},
}
FALA[KALTSIT]["pendente"] = "A conferência é parcial. Os pontos que precisam de revisão estão separados no painel."
FALA[CLOSURE]["pendente"] = "O pente fino ficou parcial. Separei os pontos de atenção e o que ainda precisa de conferência."
COR = {"aprovada": 0x2E8B57, "pendente": 0xD4A017, "reprovada": 0xCC0102, "formato desconhecido": 0xD4A017}
# Nome legível de cada aviso da ficha; o que não estiver aqui aparece pela chave.
ROTULOS = {"aviso.escolhas_de_pericia": "Perícias e ofícios", "aviso.pontos_disponiveis": "Pontos de atributo",
           "aviso.pericias_disponiveis": "Perícias", "aviso.oficios_disponiveis": "Ofícios",
           "aviso.testes_disponiveis": "Testes de Resistência", "aviso.grau": "Grau do uniforme",
           "aviso.forca_p": "Força da mão principal", "aviso.forca_s": "Força da mão secundária",
           "aviso.forca_v": "Força do uniforme", "aviso.requisito": "Requisito de Força", "aviso.treino": "Treino da arma",
           "aviso.selo": "Selo", "aviso.vagas_de_pacto": "Vagas de pacto", "caminho": "Caminho", "trilha": "Trilha",
           "origem": "Origem", "vida_max": "Vida", "energia_max": "PE", "integridade_max": "Integridade",
           "protecao": "Proteção", "defesa": "Defesa", "formato.versao": "Formato da ficha",
           "repertorio": "Repertório", "espacos_de_feitico": "Espaços de repertório",
           "marco.leque": "Marcos de Leque", "marco.corpo": "Marcos de Corpo", "marco.refino": "Marcos de Refino",
           "tecnica.rota.nome": "Rota de criação", "tecnica.regra_propria.categoria": "Categoria da Regra Própria",
           "tecnica.regra_propria.espacos": "Espaços da Regra Própria", "dominio.degrau": "Degrau do Domínio",
           "dominio.custo": "Espaços do Domínio", "origem.ce4": "Talento CE4 da Origem",
           "em_uso.principal": "Arma principal", "em_uso.secundaria": "Mão secundária",
           "em_uso.vestindo": "Uniforme", "carga": "Carga", "carga.total": "Carga total",
           "carga.limite": "Limite de carga", "carga.ajuste_limite": "Buff/Debuff do limite de carga",
           "treinos": "Escolhas de treino", "tr": "Testes de Resistência",
           "atributos.base": "Pontos de atributo por criação e marcos", "atributos.corpo": "Pontos de Corpo"}


def _rotulo(chave: str) -> str:
    if chave in ROTULOS:
        return ROTULOS[chave]
    cartao = rotulo_chave(chave)
    if cartao:
        return cartao
    if chave.startswith("buff."):
        return "Buff/Debuff de " + chave[5:].replace("_", " ")
    partes = chave.split(".")
    if partes[0] == "passiva" and len(partes) >= 2:
        return "Talento " + partes[1] + (" · " + _nome_do_valor(".".join(partes[2:])) if len(partes) > 2 else "")
    if partes[0] in ("feitico", "liberacao", "invocacao", "zero") and len(partes) > 1 and partes[1].isdigit():
        nome = {"feitico": "Feitiço", "liberacao": "Liberação", "invocacao": "Invocação", "zero": "Classe 0"}[partes[0]] + f" {partes[1]}"
        resto = partes[2:]
        if len(partes) > 3 and partes[2] in ("bas", "esp", "ext"):
            nome += " · " + {"bas": "básica", "esp": "especial", "ext": "habilidade da Trilha"}[partes[2]] + " " + partes[3]
            resto = partes[4:]
        return nome + (" · " + _nome_do_valor(".".join(resto)) if resto else "")
    if partes[0] == "maxima":
        return "Técnica Máxima · " + _nome_do_valor(".".join(partes[1:]))
    return _nome_do_valor(chave)


ATRIBUTOS = {"forca": "Força", "destreza": "Destreza", "constituicao": "Constituição",
             "inteligencia": "Inteligência", "essencia": "Essência"}
VALORES = {"vida": "Vida", "vida.max": "Vida", "vida_max": "Vida", "energia_max": "PE", "pe": "PE", "dano": "dano-base",
           "classe": "Classe", "nivel": "nível", "retorno": "retorno", "entrada": "entrada", "cd": "CD",
           "acerto": "acerto", "defesa": "Defesa", "deslocamento": "deslocamento", "pecas": "Melhorias",
           "restricoes": "Restrições", "pontos": "atributos", "nome": "nome", "forma": "Forma",
           "nivel_fixo": "nível de aquisição", "familias": "Famílias", "montagem": "montagem"}


def _nome_do_valor(chave: str) -> str:
    partes = chave.split(".")
    if len(partes) >= 3 and partes[0] == "custom":
        tipo = {"pericia": "Perícia própria", "oficio": "Ofício próprio", "origem": "Origem própria",
                "melhoria": "Melhoria própria", "restricao": "Restrição própria", "forma": "Forma própria"}.get(partes[1])
        if tipo:
            if partes[2].isdigit():
                return tipo + " " + partes[2] + (" · " + _nome_do_valor(".".join(partes[3:])) if len(partes) > 3 else "")
            return tipo + " · " + _nome_do_valor(".".join(partes[2:]))
    if partes[0] in ("pericia", "oficio", "tr", "equipavel", "item") and len(partes) >= 2:
        tipo = {"pericia": "Perícia", "oficio": "Ofício", "tr": "TR", "equipavel": "Equipável", "item": "Item"}[partes[0]]
        nomes_tr = {"fisico": "Físico", "vigor": "Vigor", "intelecto": "Intelecto", "espirito": "Espírito"}
        nome = nomes_tr.get(partes[1], partes[1].replace("_", " ").title()) if tipo == "TR" else partes[1].replace("_", " ").title()
        campos = {"atributo": "atributo", "ajuste": "Buff/Debuff", "bonus": "bônus",
                  "especialista": "especialização", "quantidade": "quantidade", "volume": "Volume", "nome": "nome"}
        return tipo + " " + nome + (" · " + campos.get(partes[-1], partes[-1]) if len(partes) > 2 else "")
    if partes[0] == "atributo" and len(partes) >= 2:
        nome = ATRIBUTOS.get(partes[1], partes[1])
        return "Buff/Debuff de " + nome if partes[-1] == "buff" else nome
    if partes[0] == "buff":
        return "Buff/Debuff de " + VALORES.get(".".join(partes[1:]), " ".join(partes[1:]))
    return VALORES.get(chave, chave.replace("_", " ").replace(".", " · "))


def _quantidade(numero: int, singular: str, plural: str | None = None) -> str:
    return f"{numero} " + (singular if numero == 1 else plural or singular + "s")


def _linha(p: Problema) -> str:
    if p.regra == "buff":
        valor = p.encontrado
        if re.fullmatch(r"\d+(?:[.,]\d+)?", valor):
            valor = "+" + valor
        return f"**{_rotulo(p.campo)}**: {valor}"
    if p.regra in ("conta", "formato"):
        return f"**{_rotulo(p.campo)}**: está {p.encontrado}, o certo é {p.esperado}"
    if p.regra in ("equipamento", "carga", "talento", "testes", "custom", "configuração", "campanha", "aprovação", "informação", "famílias", "progressão", "treinos", "aptidão"):
        return f"**{_rotulo(p.campo)}** (`{p.campo}`): {p.esperado} (informado: {p.encontrado})" + (f" · regra `{p.ancora}`" if p.ancora else "")
    if p.regra == "escolha":
        return f"**{_rotulo(p.campo)}**: falta {p.esperado.removeprefix('escolher ')}"
    if p.regra == "nome":
        return f"**{_rotulo(p.campo)}**: {p.encontrado} não é {p.esperado}"
    if p.regra == "origem" and p.campo == "energia_max":
        return f"**PE**: falta pôr {p.esperado.removeprefix('+')} (hoje o {p.encontrado})"
    if p.regra == "origem" and p.campo == "integridade_max":
        return f"**Integridade**: {p.esperado}; desconsidere o valor {p.encontrado} da ficha"
    if p.regra == "origem" and p.campo in ("defesa", "vida_max"):
        return f"**{_rotulo(p.campo)}**: está {p.encontrado}, mas {p.esperado}; ajuste com o Buff/Debuff"
    if p.regra == "origem":
        return f"**{_rotulo(p.campo)}**: {p.encontrado}; a Origem permite {p.esperado.removeprefix('até ')}"
    if re.fullmatch(r"\d+ de \d+", p.encontrado):  # pontos ou Testes de Resistência ainda por distribuir
        verbo = "distribuir" if p.campo == "aviso.pontos_disponiveis" else "escolher"
        return f"**{_rotulo(p.campo)}**: faltam {verbo} {p.encontrado}"
    return f"**{_rotulo(p.campo)}**: {p.encontrado}"


def _base(resultado: Resultado, ficha: dict[str, Campo], persona) -> discord.Embed:
    nome = str(ficha.get("nome", Campo("", "", "")).valor).strip()
    titulo = f"Ficha de {nome}" if nome else "Ficha sem nome"
    if not nome:
        caminho = str(ficha.get("caminho", Campo("", "", "")).valor).strip()
        nivel = ficha.get("nivel", Campo("", "", "")).valor
        if caminho and f"Caminho {caminho}" in resultado.conferidos:
            titulo = f"Ficha de {caminho}"
            if isinstance(nivel, int) and not isinstance(nivel, bool) and nivel > 0:
                titulo += f", nível {nivel}"
    cor = COR["pendente"] if resultado.veredito == "aprovada" and (resultado.pendencias or resultado.nao_conferido or resultado.notas) else COR.get(resultado.veredito, 0xCC0102)
    visual = "pendente" if resultado.veredito=="aprovada" and (resultado.pendencias or resultado.nao_conferido or resultado.notas) else resultado.veredito
    embed = discord.Embed(title=titulo[:256], color=cor,
                          description=FALA.get(persona.chave, FALA[KALTSIT]).get(visual, ""))
    embed.set_author(name=persona.nome, icon_url=persona.avatar_url or None)
    return embed


def _dividir(texto: str, limite=950) -> list[str]:
    """Preserva o conteúdo completo, inclusive uma linha sem espaços maior que um campo."""
    partes = []
    while len(texto) > limite:
        corte = texto.rfind(" ", 0, limite + 1)
        if corte < limite // 2:
            corte = limite
        partes.append(texto[:corte])
        texto = texto[corte:].lstrip(" ")
    if texto:
        partes.append(texto)
    return partes


def _campos(nome: str, linhas: list[str]) -> list[tuple[str, str]]:
    campos, partes = [], []
    for linha in linhas:
        partes.extend(_dividir("• " + linha))
    atual = ""
    for parte in partes:
        if atual and len(atual) + len(parte) + 1 > 1000:
            campos.append((nome, atual))
            atual = ""
        atual += ("\n" if atual else "") + parte
    if atual:
        campos.append((nome, atual))
    return campos


def _valor_legivel(texto: str) -> str:
    if " " not in texto:
        return texto
    chave, valor = texto.split(" ", 1)
    if re.fullmatch(r"-?\d+(?:\.\d+)?", valor):
        if chave in ("entrada", "retorno"):
            valor += " PE"
        elif chave == "deslocamento":
            valor += " m"
        elif chave == "acerto" and not valor.startswith("-"):
            valor = "+" + valor
    return _nome_do_valor(chave) + " " + valor


GRUPO = re.compile(r"^((?:Feitiço|Liberação|Classe 0) \d+|Técnica Máxima|Invocação \d+(?: · (?:(?:básica|especial|habilidade da Trilha|Liberação) \d+|Técnica Máxima))?): (.*)$")


def _nome_grupo(grupo: str, ficha: dict[str, Campo]) -> str:
    chave = grupo.replace(" · Técnica Máxima", " · tm").replace("Técnica Máxima", "maxima").replace("Classe 0", "zero")
    for de, para in (("Feitiço", "feitico"), ("Liberação", "liberacao"), ("Invocação", "invocacao"), (" · tm", ".tm"),
                     ("habilidade da Trilha", "ext"), ("básica", "bas"), ("especial", "esp")):
        chave = chave.replace(de, para)
    chave = chave.replace(" · ", ".").replace(" ", ".") + ".nome"
    nome = str(ficha.get(chave, Campo("", "", "")).valor).strip()
    nome = discord.utils.escape_mentions(discord.utils.escape_markdown(nome))
    return (grupo + (" — " + nome if nome else ""))[:220]


def paginas(resultado: Resultado, ficha: dict[str, Campo], persona, manifesto: dict | None = None) -> list[discord.Embed]:
    """Resumo e páginas por assunto. Só apresenta o Resultado; não refaz nem altera contas."""
    saida: list[tuple[str, discord.Embed]] = []

    def adicionar(categoria, campos, *, estado="aprovada", estados_por_campo=None):
        atual = None
        prioridade = {"aprovada": 0, "pendente": 1, "reprovada": 2}
        for nome, valor in campos:
            if atual is None or len(atual) + len(nome) + len(valor) > 3800 or len(atual.fields) >= 8:
                atual = _base(resultado, ficha, persona)
                atual.description = f"**{categoria}**"
                estado_atual = estado
                atual.colour = discord.Colour(COR[estado_atual])
                saida.append((categoria, atual))
            estado_campo = (estados_por_campo or {}).get(nome, estado)
            if prioridade[estado_campo] > prioridade[estado_atual]:
                estado_atual = estado_campo
                atual.colour = discord.Colour(COR[estado_atual])
            atual.add_field(name=nome[:256], value=valor, inline=False)

    resumo = _base(resultado, ficha, persona)
    estado = resultado.veredito.capitalize()
    if resultado.veredito in ("aprovada", "pendente"):
        if resultado.pendencias:
            estado = "Conferência parcial; pendências abertas"
        elif resultado.notas:
            estado = "Conferência parcial; ajustes para o mestre"
        elif resultado.nao_conferido:
            estado = "Conferência parcial; há partes não conferidas"
    titulo_estado = f"{estado} nas verificações feitas" if resultado.veredito != "formato desconhecido" else "Formato desconhecido — análise não realizada"
    resumo.add_field(name="Resultado", value=f"**{titulo_estado}**\n"
                     + " · ".join((_quantidade(len(resultado.problemas), "erro"), _quantidade(len(resultado.pendencias), "pendência"),
                                    _quantidade(len(resultado.notas), "ajuste") + " para o mestre")), inline=False)
    revisao = [("❌ Precisa corrigir", resultado.problemas), ("⚠️ Falta ou pede atenção", resultado.pendencias),
               ("👀 Pro mestre conferir", resultado.notas)]
    for nome, problemas in revisao:
        if problemas:
            linhas, tamanho = [], 0
            for p in problemas[:3]:
                linha = _linha(p)
                if tamanho + len(linha) > 600:
                    break
                linhas.append(linha)
                tamanho += len(linha) + 3
            valor = "\n".join("• " + l for l in linhas)
            if len(linhas) < len(problemas):
                valor += f"\n• Mais {len(problemas) - len(linhas)} na página Correções e revisão."
            resumo.add_field(name=nome, value=valor, inline=False)
    pessoais, grupos, testes = [], OrderedDict(), OrderedDict()
    for linha in resultado.conferidos:
        numerico = re.fullmatch(r"(.+): bônus ([+-]\d+(?:\.\d+)?)", linha)
        if numerico:
            nome, valor = numerico.groups()
            entidade = re.match(r"^(Invocação \d+) · (.+)$", nome)
            if entidade:
                categoria, nome = entidade.groups()
            else:
                categoria = "Testes de Resistência" if nome.startswith("TR ") else "Perícias e Ofícios"
            testes.setdefault(categoria, []).append(f"**{nome}**: {valor}")
            continue
        m = GRUPO.match(linha)
        if m:
            grupos.setdefault(m[1], []).append(_valor_legivel(m[2]))
        else:
            pessoais.append(linha)
    basicos, extras = [], []
    for prefixos in (("Caminho ", "Trilha ", "Origem "), ("Vida ", "PE ", "Integridade "), ("Proteção ", "Defesa ")):
        linha = " · ".join(t for t in pessoais if t.startswith(prefixos))
        if linha:
            basicos.append(linha)
    extras = [t for t in pessoais if not t.startswith(("Caminho ", "Trilha ", "Origem ", "Vida ", "PE ", "Integridade ", "Proteção ", "Defesa "))]
    if basicos:
        resumo.add_field(name="✅ Conferido e certo", value="\n".join(basicos)[:1000], inline=False)
    if grupos:
        inv = {re.match(r"Invocação \d+", g)[0] for g in grupos if g.startswith("Invocação ")}
        habilidades = sum(not re.fullmatch(r"Invocação \d+", g) for g in grupos)
        resumo.add_field(name="Detalhes conferidos", value=_quantidade(habilidades, "habilidade") + " · "
                         + _quantidade(len(inv), "invocação", "invocações") + ". Use o seletor ou as setas para consultar.", inline=False)
    if testes:
        resumo.add_field(name="TR e perícias", value=f"{sum(map(len, testes.values()))} bônus conferidos. Veja a página TR e perícias.", inline=False)
    if resultado.nao_conferido:
        resumo.add_field(name="⏳ Ainda não conferido", value="Conferência parcial: há itens para revisão manual. Veja a página Limites da análise.", inline=False)
    saida.append(("Resumo", resumo))
    campos_revisao = []
    for nome, problemas in revisao:
        if problemas:
            campos_revisao += _campos(nome, [_linha(p) for p in problemas])
    # A prioridade acompanha apenas os campos presentes em cada página,
    # inclusive quando erros e pendências ocupam páginas diferentes.
    adicionar("Correções e revisão", campos_revisao, estado="pendente",
              estados_por_campo={"❌ Precisa corrigir": "reprovada"})
    adicionar("Personagem", _campos("Outros valores conferidos", extras))
    campos_testes = []
    for categoria, linhas in testes.items():
        campos_testes += _campos(categoria, linhas)
    adicionar("TR e perícias", campos_testes)
    feiticos, entidades = [], OrderedDict()
    for grupo, linhas in grupos.items():
        if re.fullmatch(r"Invocação \d+", grupo):
            linhas_agrupadas = []
            usadas = set()
            for prefixos in (("nível ", "Classe "), ("Vida ", "Defesa ", "acerto ", "CD ", "deslocamento "),
                             ("entrada ", "retorno "), tuple(a + " " for a in ATRIBUTOS.values())):
                partes = [l for l in linhas if l.startswith(prefixos)]
                usadas.update(partes)
                if partes:
                    linhas_agrupadas.append(" · ".join(partes))
            linhas_agrupadas.extend(l for l in linhas if l not in usadas)
        else:
            linhas_agrupadas = [" · ".join(linhas)]
        campos = _campos(_nome_grupo(grupo, ficha), linhas_agrupadas)
        if grupo.startswith("Invocação "):
            entidade = re.match(r"Invocação \d+", grupo)[0]
            entidades.setdefault(entidade, []).extend(campos)
        else:
            feiticos.extend(campos)
    adicionar("Feitiços e técnicas", feiticos)
    for nome, campos in entidades.items():
        adicionar(nome, campos)
    limites = OrderedDict()
    for linha in resultado.nao_conferido:
        if ": " in linha:
            assunto, detalhe = linha.split(": ", 1)
            limites.setdefault(detalhe, []).append(assunto)
        else:
            limites.setdefault(linha, []).append("Conferência manual")
    campos_limites = []
    for detalhe, assuntos in limites.items():
        assuntos = list(dict.fromkeys(assuntos))
        nome = " · ".join(assuntos)
        linhas = [detalhe] if len(nome) <= 220 else [" · ".join(assuntos[i:i+8]) for i in range(0, len(assuntos), 8)] + [detalhe]
        campos_limites += _campos(nome if len(nome) <= 220 else "Vários itens", linhas)
    adicionar("Limites da análise", campos_limites, estado="pendente")
    visual = "pendente" if resultado.veredito=="aprovada" and (resultado.pendencias or resultado.nao_conferido or resultado.notas) else resultado.veredito
    livro = (manifesto or {}).get("edicao_livro")
    for i, (categoria, embed) in enumerate(saida):
        embed.set_footer(text=f"Página {i + 1} de {len(saida)} · {categoria} · Veredito geral: {visual} · livro"
                         + (f" {livro}" if livro else "") + (" · controles por 10 min" if len(saida) > 1 else "")
                         + " · o mestre pode recusar mesmo com tudo certo")
    return [embed for _, embed in saida]


def painel(resultado: Resultado, ficha: dict[str, Campo], persona, manifesto: dict | None = None) -> discord.Embed:
    """Compatibilidade para quem só precisa do resumo da análise."""
    return paginas(resultado, ficha, persona, manifesto)[0]


class Ficha(commands.Cog):
    grupo = app_commands.Group(name="ficha", description="Correção de ficha do Ciclo Maldito.")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.referencias = Referencias.do_livro(bot.config.dados)
        self.campanhas = bot.config.dados.parent / "src" / "var" / "ficha-campanhas.json"

    async def analisar_fonte(self, *, link: str | None = None, arquivo: discord.Attachment | None = None, servidor: int | None = None) -> list[discord.Embed] | str:
        """Lê e confere a ficha. Devolve as páginas, ou o erro de leitura. Serve à barra e ao GC:ficha."""
        leituras = 1
        try:
            if arquivo is not None:
                if not arquivo.filename.lower().endswith(".xlsx") or arquivo.size > LIMITE_ANEXO:
                    raise FichaIlegivel("o anexo precisa ser a ficha em .xlsx")
                ficha = await asyncio.to_thread(de_xlsx, await arquivo.read())
            elif link:
                ficha, leituras = await self._ler_estavel(link)
            else:
                raise FichaIlegivel("mande o link da ficha aberta pra leitura ou o .xlsx anexo")
        except FichaIlegivel as erro:
            return f"Não deu pra ler a ficha: {erro}."
        from ..ficha_configuracao import carregar_campanha
        try:
            regras, aprovados = carregar_campanha(self.campanhas, servidor)
            resultado = await asyncio.to_thread(conferir, ficha, self.referencias, regras, aprovados)
        except (ValueError, OSError) as erro:
            log.error("cadastro de campanha indisponível: %s", type(erro).__name__)
            return "Não deu para carregar a configuração autorizada desta campanha. O operador precisa conferir o cadastro do bot."
        if leituras > 1:
            restantes = len(transicoes(ficha))
            resultado.nao_conferido.append(f"Cartões R53: link lido {leituras} vezes porque havia cartão salvando"
                                           + (f"; {restantes} ainda em transição na leitura usada" if restantes else "; a leitura usada já estava estável"))
        log.info("ficha analisada: %s, %d problema(s)", resultado.veredito, len(resultado.problemas))
        persona = self.bot.personas[de_plantao(datetime.now(FUSO))]
        return paginas(resultado, ficha, persona, getattr(self.bot, "manifesto", None))

    async def _ler_estavel(self, link: str) -> tuple[dict[str, Campo], int]:
        """Lê o link e, se algum cartão R53 estiver no meio de um salvamento, relê poucas vezes."""
        from ..ficha_esquema import variante
        leituras = [await de_link(link)]
        for espera in ESPERAS_TRANSICAO:
            atual = escolher_leitura(leituras)
            if variante(atual) != "r53-v12" or not transicoes(atual):
                return atual, len(leituras)
            await asyncio.sleep(espera)
            try:
                leituras.append(await de_link(link))
            except FichaIlegivel:
                break  # a última leitura válida continua valendo
        return escolher_leitura(leituras), len(leituras)

    @grupo.command(name="guia", description="Como enviar a ficha, entender o painel e revisar o restante com o mestre.")
    async def guia(self, interacao: discord.Interaction) -> None:
        await self.bot.get_cog("Guias").pela_barra(interacao, "ficha")

    @grupo.command(name="analisar", description="Confere a ficha pelo link da planilha ou pelo .xlsx anexo.")
    @app_commands.describe(link="Link da ficha no Google Planilhas, aberta pra leitura", arquivo="A ficha baixada em .xlsx")
    async def analisar(self, interacao: discord.Interaction, link: str | None = None,
                       arquivo: discord.Attachment | None = None) -> None:
        if (link is None) == (arquivo is None):
            await interacao.response.send_message("Mande o link da ficha ou o .xlsx, um dos dois.", ephemeral=True)
            return
        await interacao.response.defer(thinking=True)  # o painel fica no canal, pra o mestre ver
        resposta = await self.analisar_fonte(link=link, arquivo=arquivo, servidor=interacao.guild_id)
        # depois do defer público o Discord não deixa nem o aviso de erro ser só pra quem pediu
        await enviar_relatorio(resposta, partial(interacao.followup.send, wait=True, allowed_mentions=discord.AllowedMentions.none()))


async def setup(bot: commands.Bot) -> None:
    if not LIGADO:
        return
    try:
        cog = Ficha(bot)
    except (OSError, ValueError) as erro:  # livro ou catálogo faltando ou fora de forma: o resto do bot sobe igual
        log.error("correção de ficha desligada: %s", erro)
        return
    await bot.add_cog(cog)
