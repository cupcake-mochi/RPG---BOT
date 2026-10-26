"""Grade Google simulada, comparada com os leitores existentes."""
import copy
import csv
import io
from pathlib import Path
import unittest
from urllib.parse import parse_qs
import httpx
from carteira_viva.leitura_google import da_grade
from carteira_viva.provedores import Provedores, ErroProvedor
from closure_bot.ficha_leitor import FichaIlegivel, de_csv, de_xlsx
from testes.test_carteira_provedores import configuracao
ARQUIVO = "arquivo_ficticio_para_teste_001"


def celula(valor, *, formula=False):
    tipo = "boolValue" if type(valor) is bool else "numberValue" if type(valor) in (int, float) else "stringValue"
    return {"effectiveValue": {tipo: valor}, "userEnteredValue": {"formulaValue": "=formula_ficticia()"} if formula else {tipo: valor}}


def grade(linhas):
    return {"spreadsheetId": ARQUIVO, "sheets": [{"properties": {"title": "ANALISE"},
            "data": [{"rowData": [{"values": [celula(v) for v in linha]} for linha in linhas]}]}]}


def linhas_ficha(f):
    return [["chave", "valor", "célula", "parte"]] + [[k, c.valor, c.celula, c.parte] for k, c in f.items()]


class GradeTeste(unittest.TestCase):
    def setUp(self):
        self.linhas = [["chave", "valor", "célula", "parte"], ["formato.versao", 12, "", "cabeçalho"],
                       ["nome", "001", "CARTEIRA!A1", "entrada"], ["nivel", 0, "", "entrada"],
                       ["origem", "FALSE", "", "entrada"], ["vida_max", "", "", "resultado"]]
        self.g = grade(self.linhas)

    def test_paridade_csv_e_xlsx_conserva_texto_zero_vazio(self):
        from openpyxl import Workbook
        buf = io.StringIO(); csv.writer(buf).writerows(self.linhas)
        livro = Workbook(); livro.active.title = "ANALISE"
        for linha in self.linhas: livro.active.append(linha)
        x = io.BytesIO(); livro.save(x); livro.close()
        f = da_grade(self.g, ARQUIVO)
        self.assertEqual(f, de_csv(buf.getvalue())); self.assertEqual(f, de_xlsx(x.getvalue()))
        self.assertEqual(f["nome"].valor, "001"); self.assertEqual(f["origem"].valor, "FALSE")
        self.assertEqual(f["nivel"].valor, 0); self.assertEqual(f["vida_max"].valor, "")

    def test_formula_sem_cache(self):
        self.g["sheets"][0]["data"][0]["rowData"][3]["values"][1] = {"userEnteredValue": {"formulaValue": "=SECRETO()"}}
        with self.assertRaisesRegex(FichaIlegivel, "sem resultado calculado em ANALISE!B4"): da_grade(self.g, ARQUIVO)

    def test_formula_com_resultado_vazio(self):
        self.g["sheets"][0]["data"][0]["rowData"][-1]["values"][1] = celula("", formula=True)
        self.assertEqual(da_grade(self.g, ARQUIVO)["vida_max"].valor, "")

    def test_erro_em_todas_as_colunas_sem_expor_mensagem(self):
        for col in range(4):
            g = copy.deepcopy(self.g)
            g["sheets"][0]["data"][0]["rowData"][2]["values"][col] = {"effectiveValue": {"errorValue": {"type": "ERROR", "message": "confidencial"}}}
            with self.subTest(col=col), self.assertRaises(FichaIlegivel) as erro: da_grade(g, ARQUIVO)
            self.assertNotIn("confidencial", str(erro.exception))

    def test_duplicata(self):
        self.g["sheets"][0]["data"][0]["rowData"].append(copy.deepcopy(self.g["sheets"][0]["data"][0]["rowData"][2]))
        with self.assertRaisesRegex(FichaIlegivel, "duplicada"): da_grade(self.g, ARQUIVO)

    def test_limite_sentinela_e_range_deslocado(self):
        for mudar in (lambda d: d.update(startRow=1), lambda d: d.update(startColumn=1), lambda d: d.update(rowData=[{}] * 20002)):
            g = copy.deepcopy(self.g); mudar(g["sheets"][0]["data"][0])
            with self.subTest(mudar=mudar), self.assertRaises(FichaIlegivel): da_grade(g, ARQUIVO)

    def test_id_aba_cabecalho(self):
        for mutar in (lambda g: g.update(spreadsheetId="outra"), lambda g: g.update(sheets=[]),
                      lambda g: g["sheets"][0]["properties"].update(title="FICHA"),
                      lambda g: g["sheets"][0]["data"][0]["rowData"].pop(0)):
            g=copy.deepcopy(self.g); mutar(g)
            with self.subTest(mutar=mutar), self.assertRaises(FichaIlegivel): da_grade(g, ARQUIVO)

    def test_nao_inventa_campo_ausente(self): self.assertNotIn("ataque.atributo", da_grade(self.g, ARQUIVO))

    def test_nan_rejeitado(self):
        self.g["sheets"][0]["data"][0]["rowData"][3]["values"][1] = celula(float("nan"))
        with self.assertRaises(FichaIlegivel): da_grade(self.g, ARQUIVO)


class GoogleCompletoTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.requests=[]; self.outra_versao=False; self.negado=False
        self.g = grade([["chave", "valor", "célula", "parte"], ["formato.versao", 12]])
        self.prov = Provedores(configuracao(Path("nao_criar.sqlite3")), transporte=httpx.MockTransport(self.handler))

    def handler(self, req):
        self.requests.append(req)
        if req.url.host == "sheets.googleapis.com": return httpx.Response(200, json=self.g)
        if self.negado: return httpx.Response(403)
        v = "2" if self.outra_versao and len(self.requests)>1 else "1"
        return httpx.Response(200, json={"id": ARQUIVO, "mimeType": "application/vnd.google-apps.spreadsheet", "isAppAuthorized": True, "version": v})

    async def test_tres_chamadas_somente_analise_com_bearer(self):
        f, versao = await self.prov.ler_analise("token_ficticio", ARQUIVO)
        self.assertEqual(versao, "1"); self.assertIn("formato.versao", f); self.assertEqual(len(self.requests),3)
        self.assertTrue(all(r.method=="GET" and r.headers["Authorization"]=="Bearer token_ficticio" for r in self.requests))
        query=parse_qs(self.requests[1].url.query.decode())
        self.assertEqual(query["ranges"], ["'ANALISE'!A1:D20002"]); self.assertIn("effectiveValue", query["fields"][0])
        self.assertNotIn("token_ficticio", str(self.requests[1].url))

    async def test_versao_alterada(self):
        self.outra_versao=True
        with self.assertRaises(ErroProvedor) as exc: await self.prov.ler_analise("falso", ARQUIVO)
        self.assertEqual(exc.exception.codigo,"alterada")

    async def test_acesso_negado_sem_exportacao_publica(self):
        self.negado=True
        with self.assertRaises(ErroProvedor): await self.prov.ler_analise("falso", ARQUIVO)
        self.assertEqual(len(self.requests),1)

    async def test_id_malicioso_sem_rede(self):
        with self.assertRaises(ErroProvedor): await self.prov.ler_analise("falso", "https://127.0.0.1/")
        self.assertFalse(self.requests)

    async def test_resposta_grande(self):
        self.prov.transporte=httpx.MockTransport(lambda _: httpx.Response(200, content=b" "*(1025)))
        with self.assertRaises(ErroProvedor) as exc: await self.prov._json("https://sheets.googleapis.com/falso", "falso",limite=1024)
        self.assertEqual(exc.exception.codigo,"tamanho")
