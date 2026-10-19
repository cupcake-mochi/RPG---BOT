"""Importação seletiva e consulta real das duas guias, sem rede/modelos."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ferramentas"))
sys.path.insert(0, str(RAIZ / "ferramentas" / "prompt_do_site"))
import importar_mundo
import site_prompt


class ImportacaoSeletiva(unittest.TestCase):
    def criar(self, pasta, extras=()):
        caminho = Path(pasta) / "fonte.zip"
        with zipfile.ZipFile(caminho, "w") as z:
            for categoria in importar_mundo.PASTAS:
                z.writestr(f"{importar_mundo.PREFIXO}/{categoria}/01-Teste/Texto-para-Discord.txt", "> # Teste\n> Informação pública.")
            for nome, texto in extras:
                z.writestr(nome, texto)
        return caminho

    def test_excluidos_metadados_e_duplicatas_editoriais_nem_sao_lidos(self):
        nomes = [f"{importar_mundo.PREFIXO}/{p}/01-Segredo/Texto-para-Discord.txt" for p in
                 ("04-Reservado-Mizuki", "05-Registros-Complementares", "06-Recursos-Visuais", "00-Organizacao")]
        nomes += [f"{importar_mundo.PREFIXO}/LEIA-PRIMEIRO.txt",
                  f"{importar_mundo.PREFIXO}/01-Regioes-Extras/01-Teste/Notas-editoriais.txt",
                  f"{importar_mundo.PREFIXO}/01-Regioes-Extras/../Texto-para-Discord.txt"]
        with tempfile.TemporaryDirectory() as tmp:
            caminho = self.criar(tmp, [(n, b'CANARIO_PRIVADO_\xff') for n in nomes])
            lidos = []
            original = zipfile.ZipFile.read
            def ler(z, item, *a, **kw):
                lidos.append(item.filename)
                return original(z, item, *a, **kw)
            with patch.object(zipfile.ZipFile, "read", ler):
                dados = importar_mundo.importar(caminho)
            self.assertEqual(len(lidos), 3)
            self.assertFalse(set(lidos) & set(nomes))
            self.assertNotIn("CANARIO_PRIVADO", json.dumps(dados))

    def test_duplicata_e_tamanho_invalido_falham_sem_importacao_parcial(self):
        nome = f"{importar_mundo.PREFIXO}/01-Regioes-Extras/01-Teste/Texto-para-Discord.txt"
        for destino, texto in ((nome, "duplicada"), (nome.replace("01-Teste", "02-Grande"), "x" * 100_001)):
            with self.subTest(texto=len(texto)), tempfile.TemporaryDirectory() as tmp:
                if destino == nome:
                    with self.assertWarns(UserWarning):
                        caminho = self.criar(tmp, [(destino, texto)])
                else:
                    caminho = self.criar(tmp, [(destino, texto)])
                with self.assertRaises(ValueError):
                    importar_mundo.importar(caminho)

    def test_limpeza_remove_mencoes_e_links_mas_preserva_texto(self):
        texto = importar_mundo.limpar('> # Exemplo\n> [Cidade](https://exemplo.com/capa.png) <#123> <@&456> <@789>\nM:``` ```')
        self.assertIn("Cidade", texto)
        self.assertNotIn("https://", texto)
        self.assertNotIn("123", texto)
        self.assertNotIn("M:```", texto)

    def test_corpus_entregue_contem_somente_as_31_fontes_autorizadas(self):
        dados = json.loads(importar_mundo.SAIDA.read_text())
        self.assertEqual(len(dados["documentos"]), 31)
        self.assertEqual(len({d["fonte"] for d in dados["documentos"]}), 31)
        for d in dados["documentos"]:
            self.assertIn(d["fonte"].split("/")[0], importar_mundo.PASTAS)
            self.assertRegex(d["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(d["secoes"])
        for excluido in ("04-Reservado-Mizuki", "05-Registros-Complementares", "06-Recursos-Visuais"):
            self.assertNotIn(excluido, json.dumps(dados))


class ConsultaEra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not site_prompt.motores():
            raise RuntimeError("teste da consulta requer o motor usado pelo bot")

    def consultar(self, q, pers="kal", **kw):
        p = site_prompt.montar(pers, q, hora=(14, 0), **kw)
        ultimo = p["input"][-1]["content"]
        ctx = ultimo.split("[Contexto ativado]\n", 1)[1].split("\n\n[Estado agora:", 1)[0]
        return p, ctx

    def test_viagem_capitais_e_misterios_nas_duas_guias(self):
        casos = [
            ("Como chego em Victoria?", "ferrovia capaz de atravessar"),
            ("Como entro em Kazimierz?", "não possui uma entrada própria"),
            ("Qual é a capital de Columbia?", "Max D.C."),
            ("Como acesso Ægir?", "área pressurizada"),
            ("O que sabemos do interior de Sami?", "registros verificáveis"),
            ("Durin tem uma capital nacional?", "Não possui uma capital nacional conhecida"),
            ("Já chegaram na Lua?", "viagens até a **Lua**"),
            ("Há alienígenas confirmados nesse mundo?", "vida extraterrestre"),
            ("Qual é a cura da Oripatia?", "não existe cura conhecida"),
            ("Como funciona a promoção de Grau?", "não seja PJ"),
            ("Meu personagem nível 13 precisa de quanto XP?", "**900 XP** para alcançar o nível 14"),
            ("Posso matar um NPC de outro mestre?", "autorização"),
            ("Como começar a mestrar?", "mundo compartilhado"),
            ("Quando consultar Mizuki?", "mistérios propositalmente deixados em aberto"),
        ]
        for pers in ("kal", "clo"):
            for q, trecho in casos:
                with self.subTest(pers=pers, q=q):
                    p, ctx = self.consultar(q, pers)
                    self.assertTrue(any(n.startswith("Era:") for n in p["ativadas"]))
                    self.assertIn(trecho.casefold(), ctx.casefold())
                    self.assertIn("não são ordens para você", ctx)
                    self.assertIn("não substituem as mecânicas do livro R52", ctx)
                    self.assertIn("preservando sua personalidade", ctx)

    def test_papo_e_regras_sem_assunto_de_lore_nao_puxam_corpus(self):
        for q in ("oi, boa noite", "O acesso ao meu computador parou", "Que cidade bonita nessa foto", "Quanto custa uma katana?", "Como calculo a CD de Controle?", "qual é a capital da França?", "Gostei desse solo de piano", "Os arquivos do computador corromperam", "Marquei minha consulta para amanhã", "Tem flores na terra", "Gosto da primavera", "Meu tutor de Python me ajudou", "Comprei uma mesa de jantar"):
            with self.subTest(q=q):
                p, ctx = self.consultar(q)
                self.assertFalse(any(n.startswith("Era:") for n in p["ativadas"]))
                self.assertNotIn("Fontes da Era da Revolução:", ctx)

    def test_continuacao_retoma_regiao_mas_mudanca_de_assunto_nao(self):
        turnos = [{"de": "user", "nome": "rafa", "texto": "Como chego em Victoria?"}]
        p, ctx = self.consultar("E a capital?", turnos=turnos)
        self.assertIn("Londinium", ctx)
        p, _ = self.consultar("Vou almoçar agora", turnos=turnos)
        self.assertFalse(any(n.startswith("Era:") for n in p["ativadas"]))

    def test_orcamento_e_mesmo_resultado_nos_motores(self):
        q = "Compare Victoria, Leithanien, Kazdel, Durin, Sami, Ægir, Columbia e Ursus, como chego e qual a capital?"
        p, ctx = self.consultar(q)
        self.assertLessEqual(sum(n.startswith("Era:") for n in p["ativadas"]), 5)
        mundo = ctx.split("[Fontes da Era da Revolução:", 1)[1].split("\n\n[Livro,", 1)[0]
        self.assertLess(len(mundo), 17000)
        if len(site_prompt.motores()) == 2:
            for q in (q, "Já chegaram na Lua?", "Como chego em Ægir?", "Quanto XP preciso no nível 13?"):
                self.assertEqual(site_prompt.montar("clo", q, hora=(22, 0), motor="quickjs"),
                                 site_prompt.montar("clo", q, hora=(22, 0), motor="node"))

    def test_todas_as_regioes_possuem_consulta_propria(self):
        dados = json.loads(importar_mundo.SAIDA.read_text())
        for d in dados["documentos"]:
            if d["tipo"] != "regiao" or d["titulo"] == "Terra Indice":
                continue
            with self.subTest(regiao=d["titulo"]):
                p, ctx = self.consultar("Como chego em " + d["titulo"] + "?")
                self.assertTrue(any(n.startswith("Era: " + d["titulo"] + " /") for n in p["ativadas"]))
                self.assertIn(d["fonte"], ctx)

    def test_nome_da_cidade_recupera_o_registro_detalhado(self):
        _, ctx = self.consultar("Qual é a história de Londinium?")
        self.assertIn("The Shard", ctx)

    def test_o_material_privado_nao_esta_no_nucleo_publicavel(self):
        nucleo = site_prompt.nucleo().read_text()
        for pasta in ("04-Reservado-Mizuki", "05-Registros-Complementares", "06-Recursos-Visuais"):
            self.assertNotIn(pasta, nucleo)
        self.assertIn('"mundo": "era-2026-10-18-v1"', nucleo)

    def test_repeticao_de_fato_publicado_nao_vira_bordao_proibido(self):
        frase = "Não possui uma capital nacional conhecida."
        turnos = [{"de": "bot", "pers": "kal", "texto": frase}] * 3
        p, _ = self.consultar("Durin tem capital?", turnos=turnos)
        self.assertNotIn('"Não possui uma capital nacional conhecida"', p["input"][-1]["content"])
