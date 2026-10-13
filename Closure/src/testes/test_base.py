"""Configuração, registro e leitura dos dados. Rodar de src/:  python3 -m unittest discover -s testes"""
import tempfile
import unittest
from pathlib import Path

from closure_bot.config import DADOS, carregar, ler_env
from closure_bot.dados import carregar_personas, ler_manifesto, resumo_manifesto
from closure_bot.registro import Registro


class Configuracao(unittest.TestCase):
    def _env(self, texto):
        pasta = tempfile.mkdtemp()
        arquivo = Path(pasta) / ".env"
        arquivo.write_text(texto, encoding="utf-8")
        return arquivo

    def test_le_o_arquivo(self):
        arquivo = self._env('# comentário\nDISCORD_TOKEN="abc"\nGUILD_ID=123\n\nCANAIS=10, 20,x\nAVATAR_CLOSURE=https://exemplo/c.png\n')
        self.assertEqual(ler_env(arquivo)["DISCORD_TOKEN"], "abc")
        c = carregar(arquivo, ambiente={})
        self.assertEqual((c.token, c.guild_id, c.dono_id), ("abc", 123, None))
        self.assertEqual(c.canais, frozenset({10, 20}))
        self.assertEqual(c.avatares, {"kaltsit": None, "closure": "https://exemplo/c.png"})

    def test_ambiente_vence_o_arquivo(self):
        arquivo = self._env("DISCORD_TOKEN=do_arquivo\n")
        self.assertEqual(carregar(arquivo, ambiente={"DISCORD_TOKEN": "do_ambiente"}).token, "do_ambiente")

    def test_sem_arquivo_nao_quebra(self):
        c = carregar(Path(tempfile.mkdtemp()) / "nao_existe", ambiente={})
        self.assertEqual((c.token, c.guild_id), ("", None))

    def test_canais_vazio_escuta_todos(self):
        self.assertTrue(carregar(self._env(""), ambiente={}).escuta(999))
        c = carregar(self._env("CANAIS=10"), ambiente={})
        self.assertTrue(c.escuta(10))
        self.assertFalse(c.escuta(11))


class RegistroSqlite(unittest.TestCase):
    def setUp(self):
        self.r = Registro(":memory:")

    def tearDown(self):
        self.r.fechar()

    def test_reconhece_mensagem_enviada(self):
        self.assertIsNone(self.r.persona_da_mensagem(1))
        self.r.registrar_mensagem(message_id=1, canal_id=7, persona="closure")
        self.assertEqual(self.r.persona_da_mensagem(1), "closure")

    def test_contagens(self):
        self.r.registrar_gatilho(canal_id=7, autor_id=9, persona="kaltsit", motivo="nome", fora_do_plantao=False)
        self.r.registrar_chamada(modelo="teste", persona="kaltsit", gatilho="nome", tokens_entrada=8000,
                                 tokens_saida=150, latencia_ms=900)
        self.r.registrar_chamada(modelo="teste", ok=False, erro="429")
        self.assertEqual(self.r.contagens(), {"chamadas_api": 2, "gatilhos": 1, "mensagens_bot": 0, "paineis_clima": 0})

    def test_painel_de_clima_por_servidor(self):
        self.r.definir_painel(guild_id=1, canal_id=71)
        self.r.definir_painel(guild_id=2, canal_id=72)
        self.r.marcar_painel(1, dia="2026-10-13", mensagem_id=710, estado="chuva|18")
        self.assertEqual((self.r.painel(1).dia, self.r.painel(1).mensagem_id, self.r.painel(2).dia), ("2026-10-13", 710, None))
        # trocar de canal zera o dia, pra sair um painel novo no canal novo
        self.r.definir_painel(guild_id=1, canal_id=73)
        self.assertEqual((self.r.painel(1).canal_id, self.r.painel(1).dia), (73, None))
        self.assertTrue(self.r.remover_painel(1))
        self.assertFalse(self.r.remover_painel(1))
        self.assertEqual([p.guild_id for p in self.r.paineis()], [2])

    def test_cria_a_pasta_do_banco(self):
        caminho = Path(tempfile.mkdtemp()) / "var" / "bot.sqlite3"
        Registro(caminho).fechar()
        self.assertTrue(caminho.exists())


class DadosDoProjeto(unittest.TestCase):
    """Lê os arquivos de verdade em dados/: quebra se o manifesto ou um card mudar de forma."""

    def test_manifesto(self):
        m = ler_manifesto(DADOS)
        self.assertEqual(m["sistema"], "Ciclo Maldito")
        self.assertIn(m["edicao_livro"], resumo_manifesto(m))

    def test_cards(self):
        p = carregar_personas(DADOS, {"closure": "https://exemplo/c.png"})
        self.assertEqual((p["kaltsit"].nome, p["closure"].nome), ("Kal'tsit", "Closure"))
        self.assertIsNone(p["kaltsit"].avatar_url)
        self.assertEqual(p["closure"].avatar_url, "https://exemplo/c.png")


if __name__ == "__main__":
    unittest.main()
