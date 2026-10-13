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

    def test_ultimas_falas_por_personagem_e_canal(self):
        for i in range(8):
            self.r.guardar_fala(canal_id=7, persona="closure", texto=f"fala {i}")
        self.r.guardar_fala(canal_id=7, persona="kaltsit", texto="da kal")
        self.r.guardar_fala(canal_id=8, persona="closure", texto="outro canal")
        self.assertEqual(self.r.ultimas_falas(canal_id=7, persona="closure"), [f"fala {i}" for i in range(2, 8)])
        self.assertEqual(self.r.ultimas_falas(canal_id=7, persona="kaltsit"), ["da kal"])
        self.assertEqual(self.r.ultimas_falas(canal_id=9, persona="closure"), [])

    def test_falas_antigas_sao_apagadas(self):
        from closure_bot.registro import FALAS_GUARDADAS

        for i in range(FALAS_GUARDADAS + 5):
            self.r.guardar_fala(canal_id=7, persona="closure", texto=f"fala {i}")
        self.r.guardar_fala(canal_id=7, persona="kaltsit", texto="fica")
        total = self.r._db.execute("SELECT COUNT(*) FROM falas WHERE persona = 'closure'").fetchone()[0]
        self.assertEqual(total, FALAS_GUARDADAS)
        self.assertEqual(self.r.ultimas_falas(canal_id=7, persona="kaltsit"), ["fica"])

    def test_fala_de_mais_de_um_turno_nao_conta(self):
        from datetime import datetime, timedelta, timezone

        agora = datetime(2026, 10, 13, 22, 0, tzinfo=timezone.utc)
        self.r.guardar_fala(canal_id=7, persona="closure", texto="de ontem", quando=agora - timedelta(hours=13))
        self.r.guardar_fala(canal_id=7, persona="closure", texto="de hoje", quando=agora - timedelta(hours=2))
        self.assertEqual(self.r.ultimas_falas(canal_id=7, persona="closure", agora=agora), ["de hoje"])
        self.assertEqual(self.r.ultimas_falas(canal_id=7, persona="closure", agora=agora, horas=24), ["de ontem", "de hoje"])

    def test_dias_de_conversa_contam_pelo_dia_de_brasilia(self):
        from datetime import datetime, timezone

        def chamou(dia, hora, persona="closure", autor=9):
            self.r.registrar_gatilho(canal_id=7, autor_id=autor, persona=persona, motivo="nome", fora_do_plantao=False,
                                     quando=datetime(2026, 10, dia, hora, 0, tzinfo=timezone.utc))
        chamou(13, 1)   # 22h do dia 12 em Brasília
        chamou(13, 2)   # 23h do dia 12: o mesmo dia
        chamou(13, 4)   # 1h do dia 13
        chamou(14, 12, persona="kaltsit")
        chamou(14, 12, autor=10)
        self.assertEqual(self.r.dias_de_conversa(autor_id=9, persona="closure"), 2)
        self.assertEqual(self.r.dias_de_conversa(autor_id=9, persona="kaltsit"), 1)
        self.assertEqual(self.r.dias_de_conversa(autor_id=11, persona="closure"), 0)

    def test_respostas_desde(self):
        from datetime import datetime, timedelta, timezone

        self.r.registrar_mensagem(message_id=1, canal_id=7, persona="closure")
        self.r.registrar_mensagem(message_id=2, canal_id=8, persona="closure")
        self.r.registrar_mensagem(message_id=3, canal_id=7, persona="kaltsit")
        agora = datetime.now(timezone.utc)
        self.assertEqual(self.r.respostas_desde(persona="closure", desde=agora - timedelta(hours=1)), 2)
        self.assertEqual(self.r.respostas_desde(persona="closure", desde=agora + timedelta(minutes=1)), 0)

    def test_paciencia_e_ficha_vao_e_voltam(self):
        from datetime import datetime, timezone

        from closure_bot.registro import Ficha

        agora = datetime(2026, 10, 13, 22, 0, tzinfo=timezone.utc)
        self.assertIsNone(self.r.paciencia(autor_id=9, persona="closure"))
        self.r.gravar_paciencia(autor_id=9, persona="closure", valor=2, desde=agora, pergunta="abc", pergunta_quando=agora)
        lida = self.r.paciencia(autor_id=9, persona="closure")
        self.assertEqual((lida.valor, lida.desde, lida.pergunta, lida.pergunta_quando), (2, agora, "abc", agora))
        self.assertEqual(self.r.ficha(9), Ficha())
        self.r.gravar_ficha(9, Ficha("ela/dela", ("joga com Bastião", "mesa do Tiago")))
        self.assertEqual(self.r.ficha(9), Ficha("ela/dela", ("joga com Bastião", "mesa do Tiago")))

    def test_apagar_pessoa_leva_tudo_dela_e_so_dela(self):
        from datetime import datetime, timezone

        from closure_bot.registro import Ficha

        agora = datetime(2026, 10, 13, 22, 0, tzinfo=timezone.utc)
        for autor in (9, 10):
            self.r.registrar_gatilho(canal_id=7, autor_id=autor, persona="closure", motivo="nome", fora_do_plantao=False)
            self.r.gravar_paciencia(autor_id=autor, persona="closure", valor=1, desde=agora, pergunta=None, pergunta_quando=None)
            self.r.gravar_ficha(autor, Ficha("ele/dele", ("fato",)))
            self.r.guardar_mensagem_do_dia(message_id=100 + autor, autor_id=autor, persona="closure", texto="closure, oi")
        self.r.apagar_pessoa(9)
        self.assertEqual([m.autor_id for m in self.r.mensagens_do_dia()], [10])
        self.assertEqual((self.r.ficha(9), self.r.paciencia(autor_id=9, persona="closure"), self.r.dias_de_conversa(autor_id=9, persona="closure")),
                         (Ficha(), None, 0))
        self.assertEqual((self.r.ficha(10).pronomes, self.r.paciencia(autor_id=10, persona="closure").valor, self.r.dias_de_conversa(autor_id=10, persona="closure")),
                         ("ele/dele", 1, 1))

    def test_mensagens_do_dia_e_limite_de_fatos(self):
        from closure_bot.registro import FATOS_MAX, Ficha

        for n in (3, 1, 2):
            self.r.guardar_mensagem_do_dia(message_id=n, autor_id=9, persona="closure", texto=f"mensagem {n}")
        self.assertEqual([m.texto for m in self.r.mensagens_do_dia()], ["mensagem 1", "mensagem 2", "mensagem 3"])
        self.r.apagar_mensagens_do_dia([1, 2])
        self.assertEqual([m.message_id for m in self.r.mensagens_do_dia()], [3])
        self.r.apagar_mensagens_do_dia()
        self.assertEqual(self.r.mensagens_do_dia(), [])
        self.r.gravar_ficha(9, Ficha(None, tuple(f"fato {n}" for n in range(FATOS_MAX + 4))))
        self.assertEqual(self.r.ficha(9).fatos, tuple(f"fato {n}" for n in range(4, FATOS_MAX + 4)))

    def test_cria_a_pasta_do_banco(self):
        caminho = Path(tempfile.mkdtemp()) / "var" / "bot.sqlite3"
        Registro(caminho).fechar()
        self.assertTrue(caminho.exists())


try:
    import cryptography  # noqa: F401
except ImportError:  # pragma: no cover
    cryptography = None


@unittest.skipIf(cryptography is None, "cryptography não instalada")
class BancoCifrado(unittest.TestCase):
    def setUp(self):
        from closure_bot.registro import Cofre, Ficha

        self.Ficha = Ficha
        self.caminho = Path(tempfile.mkdtemp()) / "bot.sqlite3"
        self.chave = Cofre.nova_chave()
        r = Registro(self.caminho, self.chave)
        r.guardar_fala(canal_id=7, persona="closure", texto="Opa, rafa! Como tá o Ren?")
        r.guardar_mensagem_do_dia(message_id=1, autor_id=9, persona="closure", texto="closure, meu Bastião é o Ren")
        r.gravar_ficha(9, Ficha("ele/dele", ("joga com um Bastião chamado Ren",)))
        r.fechar()

    def test_o_texto_nao_aparece_no_arquivo(self):
        bruto = self.caminho.read_bytes()
        for trecho in ("Ren", "Bastião", "ele/dele", "Opa"):
            self.assertNotIn(trecho.encode(), bruto, trecho)

    def test_com_a_chave_tudo_volta(self):
        r = Registro(self.caminho, self.chave)
        self.assertEqual(r.ultimas_falas(canal_id=7, persona="closure"), ["Opa, rafa! Como tá o Ren?"])
        self.assertEqual([m.texto for m in r.mensagens_do_dia()], ["closure, meu Bastião é o Ren"])
        self.assertEqual(r.ficha(9), self.Ficha("ele/dele", ("joga com um Bastião chamado Ren",)))
        r.fechar()

    def test_sem_a_chave_ou_com_outra_ela_esquece_em_vez_de_mostrar_letra_embaralhada(self):
        from closure_bot.registro import Cofre

        for chave in (None, Cofre.nova_chave()):
            r = Registro(self.caminho, chave)
            self.assertEqual((r.ultimas_falas(canal_id=7, persona="closure"), r.mensagens_do_dia(), r.ficha(9)), ([], [], self.Ficha()))
            r.fechar()

    def test_texto_antigo_gravado_em_claro_continua_abrindo(self):
        velho = Path(tempfile.mkdtemp()) / "bot.sqlite3"
        r = Registro(velho)
        r.guardar_fala(canal_id=7, persona="closure", texto="fala em claro")
        r.gravar_ficha(9, self.Ficha(None, ("fato em claro",)))
        r.fechar()
        r = Registro(velho, self.chave)
        self.assertEqual((r.ultimas_falas(canal_id=7, persona="closure"), r.ficha(9).fatos), (["fala em claro"], ("fato em claro",)))
        r.fechar()


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
