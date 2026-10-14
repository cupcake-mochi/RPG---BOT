"""Correção de ficha pela aba oculta ANALISE (fase 3 do docs/PLANEJAMENTO.md). Pronto e DESLIGADO.

`/ficha analisar` com o link da planilha aberta ou o .xlsx anexo: lê a aba (ficha_leitor.py), confere sem IA
(ficha_corretor.py) e responde no canal com um painel: o que precisa corrigir, o que o mestre confere (Buff/Debuff e
avisos que o livro permite), o que bateu e o que ainda não é conferido. A frase de abertura é fixa, uma por guia e
por veredito, com o nome e o avatar de quem está de plantão (o Mizuki, 14/10/2026: "na voz dela, no chat", com
mensagem fixa se o modelo complicar). O bot nunca escreve na ficha.

Fica desligado (LIGADO = False) até o Mizuki pedir: o setup não registra o comando no servidor. As regras de cada
campanha e o registro dos aprovados ainda são só estrutura (ficha_corretor.RegrasDaCampanha e Aprovados).
"""
from __future__ import annotations

import logging
import re
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from ..ficha_corretor import LIVRO, Problema, Referencias, Resultado, conferir
from ..ficha_leitor import Campo, FichaIlegivel, de_link, de_xlsx
from ..plantao import CLOSURE, FUSO, KALTSIT, de_plantao

log = logging.getLogger(__name__)

LIGADO = False
LIMITE_ANEXO = 10_000_000  # a ficha baixada tem uns 1,5 MB


# Frase fixa de abertura: uma por guia e por veredito, no jeito de cada uma (sem "!" em regra, como nos cards).
FALA = {
    KALTSIT: {"aprovada": "Conferi a ficha. O que eu consigo conferir bate com o livro.",
              "reprovada": "Conferi a ficha. Tem coisa pra corrigir antes da mesa.",
              "formato desconhecido": "Essa ficha é de um formato que eu não conheço. Baixe a versão atual da ficha."},
    CLOSURE: {"aprovada": "Passei o pente fino na ficha e o que dá pra conferir tá batendo.",
              "reprovada": "Passei o pente fino na ficha e achei umas coisas pra arrumar.",
              "formato desconhecido": "Esse formato de ficha eu não conheço. Pega a versão nova da ficha?"},
}
COR = {"aprovada": 0x2E8B57, "reprovada": 0xCC0102, "formato desconhecido": 0xD4A017}
# Nome legível de cada aviso da ficha; o que não estiver aqui aparece pela chave.
ROTULOS = {"aviso.escolhas_de_pericia": "Perícias e ofícios", "aviso.pontos_disponiveis": "Pontos de atributo",
           "aviso.pericias_disponiveis": "Perícias", "aviso.oficios_disponiveis": "Ofícios",
           "aviso.testes_disponiveis": "Testes de Resistência", "aviso.grau": "Grau do uniforme",
           "aviso.forca_p": "Força da mão principal", "aviso.forca_s": "Força da mão secundária",
           "aviso.forca_v": "Força do uniforme", "aviso.requisito": "Requisito de Força", "aviso.treino": "Treino da arma",
           "aviso.selo": "Selo", "aviso.vagas_de_pacto": "Vagas de pacto", "caminho": "Caminho", "trilha": "Trilha",
           "origem": "Origem", "vida_max": "Vida", "energia_max": "PE", "integridade_max": "Integridade",
           "protecao": "Proteção", "defesa": "Defesa", "formato.versao": "Formato da ficha"}


def _rotulo(chave: str) -> str:
    if chave in ROTULOS:
        return ROTULOS[chave]
    if chave.startswith("buff."):
        return "Buff/Debuff de " + chave[5:].replace("_", " ")
    partes = chave.split(".")
    if partes[0] in ("feitico", "liberacao", "invocacao") and len(partes) > 1 and partes[1].isdigit():
        return {"feitico": "Feitiço", "liberacao": "Liberação", "invocacao": "Invocação"}[partes[0]] + f" {partes[1]}"
    return chave


def _linha(p: Problema) -> str:
    if p.regra in ("conta", "formato"):
        return f"**{_rotulo(p.campo)}**: está {p.encontrado}, o certo é {p.esperado}"
    if p.regra == "escolha":
        return f"**{_rotulo(p.campo)}**: falta {p.esperado.removeprefix('escolher ')}"
    if p.regra == "nome":
        return f"**{_rotulo(p.campo)}**: {p.encontrado} não é {p.esperado}"
    if re.fullmatch(r"\d+ de \d+", p.encontrado):  # pontos ou Testes de Resistência ainda por distribuir
        return f"**{_rotulo(p.campo)}**: sobram {p.encontrado}"
    return f"**{_rotulo(p.campo)}**: {p.encontrado}"


def _campo(linhas: list[str]) -> str:
    """Até 1024 caracteres por campo do embed; o que não couber vira "e mais N"."""
    texto, usadas = "", 0
    for linha in linhas:
        if len(texto) + len(linha) + 40 > 1024:
            break
        texto += ("\n" if texto else "") + "• " + linha
        usadas += 1
    if usadas < len(linhas):
        texto += f"\n• e mais {len(linhas) - usadas}"
    return texto


def painel(resultado: Resultado, ficha: dict[str, Campo], persona, manifesto: dict | None = None) -> discord.Embed:
    """O que o comando responde: veredito, o que corrigir, o que o mestre confere, o que bateu e o que falta conferir."""
    nome = str(ficha.get("nome", Campo("", "", "")).valor).strip() or "sem nome"
    embed = discord.Embed(title=f"Ficha de {nome}", color=COR.get(resultado.veredito, 0xCC0102),
                          description=FALA.get(persona.chave, FALA[KALTSIT]).get(resultado.veredito, ""))
    embed.set_author(name=persona.nome, icon_url=persona.avatar_url or None)
    if resultado.problemas:
        embed.add_field(name="❌ Precisa corrigir", value=_campo([_linha(p) for p in resultado.problemas]), inline=False)
    if resultado.notas:
        embed.add_field(name="👀 Pro mestre conferir", value=_campo([_linha(p) for p in resultado.notas]), inline=False)
    if resultado.conferidos:
        embed.add_field(name="✅ Conferido e certo", value=_campo(resultado.conferidos), inline=False)
    if resultado.nao_conferido:
        embed.add_field(name="⏳ Ainda não conferido", value=_campo(resultado.nao_conferido), inline=False)
    livro = (manifesto or {}).get("edicao_livro")
    embed.set_footer(text=f"Veredito: {resultado.veredito} · regras do livro" + (f" {livro}" if livro else "")
                          + " · o mestre pode recusar mesmo com tudo certo")
    return embed


class Ficha(commands.Cog):
    grupo = app_commands.Group(name="ficha", description="Correção de ficha do Ciclo Maldito.")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.referencias = Referencias.do_livro(bot.config.dados)

    @grupo.command(name="analisar", description="Confere a ficha pelo link da planilha ou pelo .xlsx anexo.")
    @app_commands.describe(link="Link da ficha no Google Planilhas, aberta pra leitura", arquivo="A ficha baixada em .xlsx")
    async def analisar(self, interacao: discord.Interaction, link: str | None = None,
                       arquivo: discord.Attachment | None = None) -> None:
        if (link is None) == (arquivo is None):
            await interacao.response.send_message("Mande o link da ficha ou o .xlsx, um dos dois.", ephemeral=True)
            return
        await interacao.response.defer(thinking=True)  # o painel fica no canal, pra o mestre ver
        try:
            if arquivo is not None:
                if not arquivo.filename.lower().endswith(".xlsx") or arquivo.size > LIMITE_ANEXO:
                    raise FichaIlegivel("o anexo precisa ser a ficha em .xlsx")
                ficha = de_xlsx(await arquivo.read())
            else:
                ficha = await de_link(link)
        except FichaIlegivel as erro:
            # depois do defer público o Discord não deixa a resposta ser só pra quem pediu
            await interacao.followup.send(f"Não deu pra ler a ficha: {erro}.")
            return
        resultado = conferir(ficha, self.referencias, LIVRO)  # campanha: o livro, até existir o cadastro
        log.info("ficha analisada por %s: %s, %d problema(s)", interacao.user.id, resultado.veredito, len(resultado.problemas))
        persona = self.bot.personas[de_plantao(datetime.now(FUSO))]
        await interacao.followup.send(embed=painel(resultado, ficha, persona, getattr(self.bot, "manifesto", None)))


async def setup(bot: commands.Bot) -> None:
    if LIGADO:
        await bot.add_cog(Ficha(bot))
