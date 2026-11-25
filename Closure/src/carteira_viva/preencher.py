"""Lê e preenche a ficha do próprio jogador, um passo por vez.

Cada passo é um único batchUpdate na planilha que o dono cadastrou: ou entra tudo, ou nada. Antes,
confere na própria ficha se ela é a oficial que o mapa conhece e se nada mudou desde que o jogador
viu a tela; depois, lê de novo e só diz que salvou se os valores estão lá. A API do Google não tem
trava por célula: entre a leitura e a escrita sobra uma janela curta, e por isso o passo mostra de
volta o que ficou na ficha. Quais células, quem decide é criacao_plano.
"""
import asyncio
import hashlib
import logging
import re
from urllib.parse import urlencode

import httpx

from . import criacao_plano as cp
from .banco import digest
from .criacao_plano import MAPA, PESSOAL, Escrita, Plano
from .modelos import OFICIAIS
from .provedores import ARQUIVO, ErroProvedor
from .segredos import Conflito, ErroCarteira, json_bytes

PASSOS = ("identidade", "atributos", "origem", "capacidades", "caminho", "treinos")
FAIXAS = cp.FAIXAS + ("CARTEIRA!AH4:AT4", "ANALISE!A1:B8", "DADOS!DL4:DM9")
ABAS = ("CARTEIRA", "FICHA", PESSOAL, cp.PROGRESSAO, "DADOS_CONFIG", "DADOS_CUSTOM", "ANALISE", "DADOS")
TEXTOS = {"marcante": "D45", "menor1": "R45", "menor2": "AH45"}
DESATUALIZADA = "Bot: desatualizada · marque ao lado"
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets/"
IDS_OFICIAIS = frozenset(re.search(r"/d/([A-Za-z0-9_-]+)", x["url"]).group(1) for x in OFICIAIS)
PRAZO, ESPERA, ENVIO = 150, 200, 60
RELER = 3  # segundos antes de reler quando o Google não respondeu à escrita


class Mudou(Conflito):
    """A ficha mudou desde que o jogador viu a tela. `estado` é como ela está agora."""
    codigo = "mudou"

    def __init__(self, estado):
        super().__init__("A ficha mudou enquanto você preenchia.")
        self.estado = estado


class Ficha:
    """Uma leitura da planilha: valores, abas e o que a ANALISE diz dela."""
    def __init__(self, folhas, valores, formulas, fim=0):
        self.folhas, self.fim = folhas, fim      # fim: última linha da ANALISE
        self.lido = cp.Leitura(valores)
        self.abas = {p["title"]: p["sheetId"] for p in folhas}
        self.linha_estado = next((linha for (aba, linha, coluna), v in self.lido.v.items()
                                  if aba == "ANALISE" and coluna == 1 and v == "analise.estado"), None)
        caixas = cp.Leitura(formulas)
        # O texto da capacidade nasce como fórmula; sem fórmula, o jogador escreveu por cima.
        self.a_mao = {k for k, c in TEXTOS.items() if not str(caixas.de(PESSOAL, c)).startswith("=")}

    @property
    def exportacao(self):
        return str(self.lido.de("ANALISE", f"B{self.linha_estado}")) if self.linha_estado else ""

    def conferir(self):
        """Oficial do Ciclo Maldito R53, com tudo onde o mapa espera. Só depois disso se escreve."""
        chaves = {str(l[0]): str(l[1]) for l in self.lido.faixa("ANALISE", "A1:B8")}
        certa = (chaves.get("formato.versao"), chaves.get("ficha.versao"), chaves.get("ficha.sistema")) == (
            "13", "R53", "Ciclo Maldito")
        fora = cp.conferir(self.lido)
        if str(self.lido.de("FICHA", "AH10")).strip() != "NÍVEL":
            fora.append("FICHA!AH10")
        if [str(x) for x in self.lido.faixa("DADOS", "DL4:DM4")[0]] != ["texto da nota", "caixa da nota"]:
            fora.append("DADOS!DL4")
        if self.linha_estado is None:
            fora.append("ANALISE!analise.estado")
        if not certa or fora:
            # Só nomes de células do mapa: ajuda a achar o que mudou sem expor a ficha.
            logging.getLogger(__name__).warning("Preencher: ficha fora do formato (%s%s)",
                                                "" if certa else "versão; ", ", ".join(fora[:5]))
            raise ErroProvedor("formato")


def valores_do_passo(passo, lido):
    """O que o passo pode escrever, mais o que decide a conta dele. É o que não pode ter mudado."""
    def celulas(grupo):
        return [lido.de(c["aba"], c["celula"]) for c in MAPA[grupo]]

    def caixas(*grupos):
        return [lido.de("FICHA", m["caixa"]) for g in grupos for m in MAPA[g]]
    nivel = lido.de("FICHA", MAPA["leituras"]["nivel"])
    if passo == "identidade":
        return celulas("identidade")
    if passo == "atributos":
        return [[lido.de("FICHA", a["celula"]) for a in MAPA["atributos"]], nivel, lido.faixa("DADOS_CONFIG", "S2:S8")]
    if passo == "origem":
        return celulas("escolhas")[2:3]
    if passo == "capacidades":
        return [celulas("escolhas")[2:], [lido.de(PESSOAL, c) for c in TEXTOS.values()]]
    if passo == "caminho":
        return [celulas("escolhas")[:2], caixas("pericias"), lido.de("FICHA", MAPA["troca_arma"]["celula"]),
                lido.de("FICHA", MAPA["categoria_trilha"]),
                [lido.de(PESSOAL, c["caixa"]) for c in MAPA["treino"]["caixas"]],
                [[lido.de("FICHA", c["nome"]), lido.de("FICHA", c["texto"])] for c in MAPA["cartas"]]]
    if passo == "treinos":
        return [celulas("escolhas")[:1], caixas("pericias", "oficios", "testes"), lido.de("FICHA", MAPA["tr_fisico"]),
                lido.de("FICHA", MAPA["troca_arma"]["celula"]), nivel, lido.faixa("DADOS_CONFIG", "S2:S8")]
    raise ErroCarteira("Passo desconhecido.")


def base_do_passo(passo, lido):
    return hashlib.sha256(json_bytes([passo, valores_do_passo(passo, lido)])).hexdigest()[:32]


def descrever(ficha, arquivo):
    """O que a página mostra. Menus e limites são os da própria planilha, agora."""
    lido = ficha.lido
    escolhas = {c["chave"]: str(lido.de(c["aba"], c["celula"])) for c in MAPA["escolhas"]}
    leituras = {k: str(lido.de("FICHA", c)) for k, c in MAPA["leituras"].items()}
    linha = next((l for l in lido.faixa(cp.PROGRESSAO, "M2:U7") if l[0] == escolhas["caminho"]), None)
    try:
        limites, criacao = cp.limites(lido), cp.na_criacao(lido)
    except cp.Recusa:
        limites, criacao = None, False

    def caixas(grupo):
        return [{"nome": x["nome"], "marcada": lido.de("FICHA", x["caixa"]) is True} for x in MAPA[grupo]]

    def identidade(c):
        valor = lido.de(c["aba"], c["celula"])
        return {"chave": c["chave"], "rotulo": c["texto_rotulo"], "curto": c["chave"] in cp.CURTOS,
                "valor": "" if valor == c["fabrica"] else str(valor)}
    troca = str(lido.de("FICHA", MAPA["troca_arma"]["celula"]))
    return {
        "arquivo": "https://docs.google.com/spreadsheets/d/" + arquivo + "/edit",
        "bases": {p: base_do_passo(p, lido) for p in PASSOS},
        "criacao": criacao, "limites": limites, "leituras": leituras, "exportacao": ficha.exportacao,
        "identidade": [identidade(c) for c in MAPA["identidade"]],
        "atributos": [{"nome": a["nome"], "valor": lido.de("FICHA", a["celula"])} for a in MAPA["atributos"]],
        "escolhas": escolhas, "fabrica": {c["chave"]: c["fabrica"] for c in MAPA["escolhas"]}, "menus": cp.menus(lido),
        "textos": {k: str(lido.de(PESSOAL, c)) for k, c in TEXTOS.items()}, "a_mao": sorted(ficha.a_mao),
        "treinos": {"pericias": caixas("pericias"), "oficios": caixas("oficios"), "testes": caixas("testes"),
                    "fixas": [p for p in linha[5:7] if p] if linha else [], "pode_trocar": bool(linha and linha[8] == "Sim"),
                    "troca": next((n for n, t in cp.TROCAS.items() if t == troca), 0),
                    "tr_fisico": str(lido.de("FICHA", MAPA["tr_fisico"]))},
    }


def _lista(v):
    if type(v) is not list or len(v) > 60 or any(type(x) is not str or len(x) > 100 for x in v):
        raise ErroCarteira("Campos inesperados.")
    return v


def planejar(passo, ficha, dados, confirmados):
    lido = ficha.lido
    if type(dados) is not dict or any(type(k) is not str for k in dados):
        raise ErroCarteira("Campos inesperados.")
    if passo == "identidade":
        return cp.identidade(lido, dados, confirmados)
    if passo == "atributos":
        return cp.atributos(lido, dados, confirmados)
    if passo == "treinos":
        if set(dados) != {"pericias", "oficios", "testes", "tr_fisico", "troca"}:
            raise ErroCarteira("Campos inesperados.")
        listas = {k: _lista(dados[k]) for k in ("pericias", "oficios", "testes")}
        return cp.treinos(lido, **listas, tr_fisico=dados["tr_fisico"], troca=dados["troca"], confirmados=confirmados)
    if any(type(v) is not str for v in dados.values()):
        raise ErroCarteira("Campos inesperados.")
    if passo == "origem" and set(dados) == {"origem"}:
        return cp.origem(lido, dados["origem"], confirmados)
    if passo == "capacidades":
        return cp.capacidades(lido, dados, confirmados, ficha.a_mao)
    if passo == "caminho" and {"caminho"} <= set(dados) <= {"caminho", "trilha"}:
        return cp.caminho(lido, dados["caminho"], dados.get("trilha"), confirmados)
    raise ErroCarteira("Campos inesperados.")


def depois_do_passo(passo, plano, lido):
    """Segunda escrita: o que sai de fórmula e só existe depois que a ficha recalculou."""
    if passo == "capacidades":
        return cp.altura_capacidades(lido)
    forca = next(a["celula"] for a in MAPA["atributos"] if a["nome"] == "Força")
    if passo == "caminho" or any((e.aba, e.celula) == ("FICHA", forca) for e in plano.escritas):
        return cp.notas_vivas(lido)
    return Plano()


def marcar_exportacao(ficha, plano):
    """O que o gancho do onEdit faria: a exportação que o bot lê deixou de valer."""
    if ficha.exportacao != "em_dia":
        return
    plano.escritas.append(Escrita("ANALISE", f"B{ficha.linha_estado}", "desatualizada"))
    if (type(ficha.lido.de("CARTEIRA", "AT4")) is bool and
            str(ficha.lido.de("CARTEIRA", "AH4")).startswith("Bot:")):
        plano.escritas.append(Escrita("CARTEIRA", "AH4", DESATUALIZADA))


class Preencher:
    def __init__(self, consultas, provedores):
        self.c, self.p = consultas, provedores
        self.travas, self.tarefas = {}, set()

    def _trava(self, arquivo):
        # O mesmo arquivo pode estar cadastrado em dois servidores.
        if len(self.travas) > 256:
            self.travas = {k: v for k, v in self.travas.items() if v.locked()}
        return self.travas.setdefault(arquivo, asyncio.Lock())

    async def _abrir(self, servidor, usuario, pid):
        for tentativa in range(2):
            membro = await self.c._membro(servidor, usuario)
            ref = await self.c._banco("contexto_preencher", membro, pid)
            if not ARQUIVO.fullmatch(ref.arquivo) or ref.arquivo in IDS_OFICIAIS:
                raise ErroProvedor("oficial")
            try:
                cred, token = await self.c._renovar_google(membro, ref)
                break
            except Conflito:
                # Outra leitura da mesma ficha começou nesse meio-tempo.
                if tentativa:
                    raise
        await self.p.observar_arquivo(token.acesso, ref.arquivo)
        return ref, cred, token.acesso

    async def _ler(self, cred, acesso, arquivo):
        # Três leituras por vez, dentro do limite por conta do Google (a escrita tem cota própria).
        await self.c.cotas.esperar(digest(cred.conta))
        meta = await self.p._json(SHEETS + arquivo + "?" + urlencode({
            "fields": "spreadsheetId,sheets(properties(sheetId,title,gridProperties(rowCount)))"}), acesso)
        folhas = [s["properties"] for s in meta.get("sheets", [])]
        linhas = {p["title"]: p.get("gridProperties", {}).get("rowCount") for p in folhas}
        if meta.get("spreadsheetId") != arquivo or not set(ABAS) <= set(linhas) or type(linhas["ANALISE"]) is not int:
            raise ErroProvedor("formato")
        return await self._valores(cred, acesso, arquivo, folhas, linhas["ANALISE"])

    async def _valores(self, cred, acesso, arquivo, folhas, fim):
        async def lote(faixas, forma):
            await self.c.cotas.esperar(digest(cred.conta))
            url = SHEETS + arquivo + "/values:batchGet?" + urlencode(
                [("ranges", f) for f in faixas] + [("valueRenderOption", forma)])
            obj = await self.p._json(url, acesso, limite=4 * 1024 * 1024)
            if obj.get("spreadsheetId") != arquivo or len(obj.get("valueRanges", [])) != len(faixas):
                raise ErroProvedor("formato")
            return obj
        # As linhas analise.estado e analise.exportada_em ficam no fim da aba.
        valores, formulas = await asyncio.gather(
            lote(FAIXAS + (f"ANALISE!A{max(9, fim - 40)}:B{max(9, fim)}",), "UNFORMATTED_VALUE"),
            lote([f"'{PESSOAL}'!{c}" for c in TEXTOS.values()], "FORMULA"))
        ficha = Ficha(folhas, valores, formulas, fim)
        ficha.conferir()
        return ficha

    async def _enviar(self, acesso, arquivo, corpo):
        """Um POST, sem repetir. Devolve None ou o código do que deu errado; quem confirma é a releitura."""
        if not ARQUIVO.fullmatch(arquivo) or arquivo in IDS_OFICIAIS:
            raise ErroProvedor("oficial")
        try:
            async with httpx.AsyncClient(timeout=ENVIO, follow_redirects=False, trust_env=False,
                                         transport=self.p.transporte) as client:
                resp = await client.post(SHEETS + arquivo + ":batchUpdate?fields=spreadsheetId", content=json_bytes(corpo),
                                         headers={"Authorization": "Bearer " + acesso, "Content-Type": "application/json"})
        except httpx.HTTPError:
            return "escrita_incerta"
        if resp.status_code == 200:
            return None
        logging.getLogger(__name__).warning("Preencher: o Google respondeu %d à escrita", resp.status_code)
        return "escrita_recusada" if resp.status_code in (400, 401, 403, 404) else "escrita_incerta"

    def _terminou(self, tarefa):
        self.tarefas.discard(tarefa)
        if not tarefa.cancelled():
            tarefa.exception()

    async def fechar(self):
        if self.tarefas:
            _, presas = await asyncio.wait(list(self.tarefas), timeout=20)
            for t in presas:
                t.cancel()
            await asyncio.gather(*presas, return_exceptions=True)

    async def estado(self, servidor, usuario, pid):
        async def ler():
            ref, cred, acesso = await self._abrir(servidor, usuario, pid)
            ficha = await self._ler(cred, acesso, ref.arquivo)
            await self.c._banco("conferir_preencher", await self.c._membro(servidor, usuario), ref)
            return descrever(ficha, ref.arquivo)
        return await self.c.fila.executar(("preencher", servidor, usuario, pid), (servidor, usuario), ler)

    async def salvar(self, servidor, usuario, pid, passo, *, dados, base, confirmados=()):
        if passo not in PASSOS or type(base) is not str or not re.fullmatch(r"[0-9a-f]{32}", base):
            raise ErroCarteira("Campos inesperados.")
        confirmados = frozenset(_lista(confirmados if type(confirmados) is list else list(confirmados)))
        marca = hashlib.sha256(json_bytes([dados, base, sorted(confirmados)])).hexdigest()

        async def gravar():
            ref, cred, acesso = await self._abrir(servidor, usuario, pid)

            async def travado():
                async with self._trava(ref.arquivo):
                    return await self._gravar(ref, cred, acesso, passo, dados, base, confirmados)
            # Fechar a aba cancela o pedido HTTP. A escrita que já começou vai até o fim, com a trava.
            tarefa = asyncio.create_task(travado())
            self.tarefas.add(tarefa)
            tarefa.add_done_callback(self._terminou)
            return await asyncio.shield(tarefa)
        # Clique duplo manda o mesmo pedido: entra no que já está rodando.
        return await self.c.fila.executar(("preencher", servidor, usuario, pid, passo, marca), (servidor, usuario),
                                          gravar, prazo=PRAZO, espera=ESPERA)

    async def _gravar(self, ref, cred, acesso, passo, dados, base, confirmados):
        ficha = await self._ler(cred, acesso, ref.arquivo)
        if base != base_do_passo(passo, ficha.lido):
            # Repetição de um pedido que já entrou não é conflito.
            try:
                feito = not planejar(passo, ficha, dados, confirmados).escritas
            except cp.Recusa:
                feito = False
            if not feito:
                raise Mudou(descrever(ficha, ref.arquivo))
        plano = planejar(passo, ficha, dados, confirmados)
        avisos = list(plano.avisos)
        if plano.escritas:
            if ficha.exportacao == "exportando":
                raise cp.Recusa("A ficha está no meio de uma exportação pro bot. Termine a exportação "
                                "(caixa Bot na CARTEIRA) e salve de novo.")
            marcar_exportacao(ficha, plano)
            # Autorização de agora, não a da abertura: quem saiu do servidor não escreve.
            membro = await self.c._membro(ref.servidor, ref.ator)
            await self.c._banco("marcar_preenchimento", membro, ref, passo)
            try:
                erro = await self._enviar(acesso, ref.arquivo, cp.pedido(plano, ficha.abas))
                if erro == "escrita_incerta":
                    await asyncio.sleep(RELER)
                ficha = await self._valores(cred, acesso, ref.arquivo, ficha.folhas, ficha.fim)
                if any(ficha.lido.de(e.aba, e.celula) != e.valor for e in plano.escritas):
                    raise ErroProvedor(erro or "escrita_incerta")
                mais = depois_do_passo(passo, plano, ficha.lido)
                if (mais.escritas or mais.alturas) and await self._enviar(acesso, ref.arquivo, cp.pedido(mais, ficha.abas)):
                    avisos.append("A escolha entrou, mas as notas e a altura das caixas não foram atualizadas.")
            finally:
                await self.c._banco("marcar_preenchimento", membro, ref)
        return descrever(ficha, ref.arquivo) | {"avisos": avisos, "gravou": bool(plano.escritas)}
