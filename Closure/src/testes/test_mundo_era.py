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
    def test_nomes_com_cargo_dois_pontos_e_apostrofo_nao_sao_descartados(self):
        nomes, curtos = importar_mundo.nomes_publicados("**Localização:** exemplo\n* **Capital:** **Montelupe**.\n* **Capital — Atual:** exemplo.\n* **Expansão Urbana:** exemplo.\n* **Volsinii:** cidade.\n* **Shiki Zen’in — Capo dei capi de Volsinii:** personagem.\n**Cellinia Texas**, sua namorada.\n**Northern Court**.\n* **Porto Lungmen — Distrito comercial:** local fictício de teste.")
        self.assertTrue({"montelupe", "volsinii", "shiki zen'in", "shiki zenin", "cellinia texas"} <= nomes)
        self.assertEqual(curtos, {"shiki": {"shiki zen'in"}, "cellinia": {"cellinia texas"}})
        self.assertFalse({"capital", "expansao urbana", "localizacao", "northern"} & nomes)

    def test_reindexacao_preserva_fontes_e_nao_cria_abreviacao_ambigua(self):
        dados = {"arquivo_sha256": "original", "documentos": [
            {"fonte": f"01-Regioes-Extras/0{i}-Teste/Texto-para-Discord.txt", "tipo": "regiao", "titulo": f"Teste{i}", "sha256": "fonte", "secoes": [{"titulo": "Política", "texto": texto}]}
            for i, texto in enumerate(("* **Shiki Zen'in — Conselheiro:** pessoa.", "* **Shiki Tanaka:** outra pessoa."), 1)]}
        antes = json.loads(json.dumps(dados))
        depois = importar_mundo.reindexar(dados)
        self.assertEqual(dados, antes)
        self.assertEqual(depois["arquivo_sha256"], "original")
        for original, novo in zip(dados["documentos"], depois["documentos"]):
            self.assertEqual(original["secoes"], novo["secoes"])
            self.assertEqual(original["sha256"], novo["sha256"])
            self.assertNotIn("shiki", novo["apelidos"])
        self.assertEqual(importar_mundo.reindexar(depois), depois)

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
        p = site_prompt.montar(pers, q, hora=(14, 0), estado={"nova_terra": True, **kw.pop("estado", {})}, **kw)
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

    def test_shiki_e_variantes_recuperam_situacao_atual_nas_duas_guias(self):
        for pers in ("kal", "clo"):
            for nome in ("Shiki", "Shiki Zen'in", "Shiki Zen’in", "Shiki Zenʼin", "Shiki Zenin", "SHÍKI ZEN'IN"):
                with self.subTest(pers=pers, nome=nome):
                    p, ctx = self.consultar("Quem é " + nome + "?", pers)
                    era = [n for n in p["ativadas"] if n.startswith("Era:")]
                    self.assertIn("Situação Atual — Siracusano II", era[0])
                    for fato in ("Capo dei capi de Volsinii", "nem substitui a autoridade nacional", "Signora Sicilia", "Cellinia Texas", "sua namorada"):
                        self.assertIn(fato, ctx)
                    self.assertNotIn("Siracusa / Apresentação", "\n".join(era))

    def test_nomes_de_pessoas_e_locais_priorizam_o_trecho_proprio(self):
        casos = [("Cellinia", "Situação Atual"), ("Cellinia Texas", "Situação Atual"),
                 ("Londinium", "Capital"), ("Montelupe", "Capital"), ("Max D.C.", "Capital"),
                 ("Volsinii", "Regiões e Cidades de Importância"), ("Zeruertza", "Cidades e Localidades de Importância")]
        for nome, secao in casos:
            with self.subTest(nome=nome):
                p, _ = self.consultar("Fale sobre " + nome)
                era = [n for n in p["ativadas"] if n.startswith("Era:")]
                self.assertIn(secao, era[0])
                self.assertNotIn("/ Apresentação", era[0])

    def test_nomes_nao_casam_por_prefixo_e_rotulos_nao_ativam_lore(self):
        for q in ("O que é Shikigami?", "Qual é a capital do Texas?", "Qual a localização?", "O centro religioso da minha cidade", "Northern é uma palavra em inglês?", "Expansão urbana é tema da minha aula"):
            with self.subTest(q=q):
                p, ctx = self.consultar(q)
                self.assertNotIn("Shiki Zen'in", ctx)
                self.assertFalse(any(n.startswith("Era:") for n in p["ativadas"]))

    def test_indice_embutido_corresponde_ao_json_atual(self):
        dados_embutidos = json.loads(site_prompt.nucleo().read_text().split("const D = ", 1)[1].split(";\n", 1)[0])
        self.assertEqual(dados_embutidos["mundo"], json.loads(importar_mundo.SAIDA.read_text()))

    def test_todos_os_nomes_indexados_recuperam_a_fonte_correspondente(self):
        import quickjs
        contexto = quickjs.Context()
        contexto.set_time_limit(30)
        contexto.eval((site_prompt.AQUI / "antes.js").read_text() + site_prompt.nucleo().read_text())
        auditoria = json.loads(contexto.eval('''JSON.stringify((() => {
          const falhas = []; let casos = 0;
          for (const d of D.mundo.documentos.filter(d => d.tipo === "regiao" && d.titulo !== "Terra Indice")) {
            for (const nome of d.apelidos) {
              casos++;
              const resultado = consultarMundo("Fale sobre " + nome);
              if (!resultado.nomes.some(n => n.startsWith("Era: " + d.titulo + " /")))
                falhas.push({nome, fonte: d.titulo, recuperadas: resultado.nomes});
            }
          }
          return {casos, falhas};
        })())'''))
        self.assertGreater(auditoria["casos"], 300)
        self.assertEqual(auditoria["falhas"], [])

    def test_o_material_privado_nao_esta_no_nucleo_publicavel(self):
        nucleo = site_prompt.nucleo().read_text()
        for pasta in ("04-Reservado-Mizuki", "05-Registros-Complementares", "06-Recursos-Visuais"):
            self.assertNotIn(pasta, nucleo)
        self.assertIn('"mundo": "era-2026-10-18-v2"', nucleo)

    def test_repeticao_de_fato_publicado_nao_vira_bordao_proibido(self):
        frase = "Não possui uma capital nacional conhecida."
        turnos = [{"de": "bot", "pers": "kal", "texto": frase}] * 3
        p, _ = self.consultar("Durin tem capital?", turnos=turnos)
        self.assertNotIn('"Não possui uma capital nacional conhecida"', p["input"][-1]["content"])
