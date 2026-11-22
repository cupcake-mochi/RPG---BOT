"""Site da Carteira na Discloud: páginas públicas, arquivo de início e pacote TYPE=site."""
import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile

from aiohttp.test_utils import TestClient, TestServer
from cryptography.fernet import Fernet

from carteira_viva.web import criar_app
from testes.test_carteira_provedores import configuracao

RAIZ = Path(__file__).resolve().parents[2]


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


inicio = _modulo("iniciar_carteira_teste", RAIZ / "iniciar_carteira.py")
pacote = _modulo("empacotar_carteira_teste", RAIZ / "ferramentas" / "empacotar_carteira.py")


class PaginasPublicas(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.client = TestClient(TestServer(criar_app(configuracao(Path(self.tmp.name) / "db.sqlite3"))))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        self.tmp.cleanup()

    async def test_inicio_privacidade_e_termos_abrem_sem_login(self):
        textos = {}
        for caminho in ("/", "/privacidade", "/termos"):
            r = await self.client.get(caminho, allow_redirects=False)
            self.assertEqual(r.status, 200, caminho)
            self.assertEqual(r.content_type, "text/html")
            self.assertIn("default-src 'self'", r.headers["Content-Security-Policy"])
            textos[caminho] = await r.text()
        for caminho, html in textos.items():
            # CSP sem unsafe-inline: nada de style= nem script embutido.
            self.assertNotRegex(html, r"\sstyle=|<script(?![^>]*\ssrc=)", caminho)
            self.assertIn('href="/privacidade"' if caminho != "/privacidade" else 'href="/termos"', html)
        self.assertIn("api-services-user-data-policy", textos["/privacidade"])
        self.assertIn("drive.file", textos["/privacidade"])

    async def test_imagem_das_guias_e_servida_e_o_resto_do_static_nao(self):
        r = await self.client.get("/static/guias.png")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.content_type, "image/png")
        self.assertTrue((await r.read()).startswith(b"\x89PNG"))
        self.assertEqual((await self.client.get("/static/inicio.html")).status, 404)
        self.assertIn('rel="icon" href="/static/guias.png"', await (await self.client.get("/")).text())

    async def test_comandos_citados_na_politica_existem_na_ponte(self):
        from carteira_viva.ponte_discord import ConectarFicha
        nomes = {"/" + g.name + " " + c.name for g in (ConectarFicha.grupo, ConectarFicha.grupo_en) for c in g.commands}
        html = await (await self.client.get("/privacidade")).text() + await (await self.client.get("/")).text()
        citados = set(re.findall(r"<code>(/(?:personagem|character) [a-z_]+)</code>", html))
        self.assertTrue(citados)
        self.assertLessEqual(citados, nomes)


class Demonstracao(unittest.IsolatedAsyncioTestCase):
    async def test_demo_mantem_o_proprio_menu_e_ganha_as_paginas(self):
        from carteira_viva.demo import preparar
        async with TestClient(TestServer(preparar(8765))) as c:
            self.assertIn("demonstração local", await (await c.get("/")).text())
            for caminho in ("/privacidade", "/termos"):
                self.assertEqual((await c.get(caminho)).status, 200)


class ArquivoDeInicio(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_le_so_carteira_e_o_ambiente_vence(self):
        (self.pasta / ".env").write_text("DISCORD_TOKEN=do-bot\nCARTEIRA_GUILDS='1,2'\n# CARTEIRA_X=nao\nCARTEIRA_PUBLIC_ORIGIN=https://a.discloud.app\n",
                                         encoding="utf-8")
        amb = inicio.preparar_ambiente(self.pasta, {"CARTEIRA_GUILDS": "9"})
        self.assertNotIn("DISCORD_TOKEN", amb)
        self.assertNotIn("CARTEIRA_X", amb)
        self.assertEqual(amb["CARTEIRA_GUILDS"], "9")
        self.assertEqual(amb["CARTEIRA_PUBLIC_ORIGIN"], "https://a.discloud.app")
        self.assertEqual(Path(amb["CARTEIRA_DATABASE_PATH"]), self.pasta / "var" / "carteira.sqlite3")
        self.assertNotIn("CARTEIRA_BOOK_DATA", amb)

    def test_motor_so_liga_com_livro_e_campanhas_juntos(self):
        (self.pasta / "dados" / "sistema").mkdir(parents=True)
        self.assertNotIn("CARTEIRA_BOOK_DATA", inicio.preparar_ambiente(self.pasta, {}))
        (self.pasta / "var").mkdir(exist_ok=True)
        (self.pasta / "var" / "ficha-campanhas.json").write_text("{}")
        amb = inicio.preparar_ambiente(self.pasta, {})
        self.assertEqual(Path(amb["CARTEIRA_BOOK_DATA"]), self.pasta / "dados")
        self.assertEqual(Path(amb["CARTEIRA_CAMPAIGNS_PATH"]), self.pasta / "var" / "ficha-campanhas.json")

    def test_recusa_modo_de_desenvolvimento(self):
        with self.assertRaises(SystemExit):
            inicio.preparar_ambiente(self.pasta, {"CARTEIRA_DEV": "1"})


class PacoteDoSite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def montar(self, **kw):
        return pacote.empacotar("guias-carteira", saida=self.pasta / "site.zip", **kw)

    def test_config_de_site_e_nada_de_segredo_ou_banco(self):
        with zipfile.ZipFile(self.montar()) as z:
            nomes = set(z.namelist())
            config = z.read("discloud.config").decode()
        self.assertIn("TYPE=site\n", config)
        self.assertIn("ID=guias-carteira\n", config)
        self.assertIn("MAIN=iniciar_carteira.py\n", config)
        self.assertIn("RAM=512\n", config)
        self.assertTrue({"iniciar_carteira.py", "requirements.txt", "src/carteira_viva/web.py",
                         "src/carteira_viva/static/privacidade.html", "src/closure_bot/ficha_corretor.py",
                         "dados/sistema/livro.jsonl"} <= nomes)
        self.assertFalse([n for n in nomes if n == ".env" or n.endswith((".sqlite3", ".db", ".pyc")) or "__pycache__" in n])
        self.assertNotIn("var/ficha-campanhas.json", nomes)

    def test_subdominio_ram_e_env_conferidos(self):
        for sub in ("Guias", "a.discloud.app", "-x", ""):
            with self.subTest(sub=sub), self.assertRaises(SystemExit):
                pacote.empacotar(sub, saida=self.pasta / "x.zip")
        with self.assertRaises(SystemExit):
            self.montar(ram=256)
        env = self.pasta / ".env-site"
        env.write_text("CARTEIRA_GUILDS=1\nDISCORD_TOKEN=do-bot\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.montar(env=env)
        env.write_text("CARTEIRA_GUILDS=1\nCARTEIRA_DEV=1\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.montar(env=env)
        self.assertFalse((self.pasta / "site.zip").exists())

    def test_gerar_env_sorteia_segredos_e_pede_o_resto(self):
        env = self.pasta / "site.env"
        pacote.gerar_env(env)
        valores = dict(l.split("=", 1) for l in env.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#"))
        self.assertEqual(set(valores), set(pacote.OBRIGATORIAS))
        Fernet(valores["CARTEIRA_ENCRYPTION_KEYS"].encode())
        self.assertGreaterEqual(len(valores["CARTEIRA_SERVICE_TOKEN"]), 32)
        with self.assertRaises(SystemExit):
            pacote.gerar_env(env)
        with self.assertRaises(SystemExit) as falta:
            self.montar(env=env)
        self.assertIn("CARTEIRA_PUBLIC_ORIGIN", str(falta.exception))

    def test_pacote_extraido_sobe_sozinho(self):
        """Extrai numa pasta vazia e sobe o app só com o que veio no .zip, com motor e páginas."""
        camp = self.pasta / "campanhas.json"
        camp.write_text("{}", encoding="utf-8")
        env = self.pasta / ".env-site"
        env.write_text("\n".join([
            "CARTEIRA_PUBLIC_ORIGIN=https://guias-carteira.discloud.app",
            "CARTEIRA_ENCRYPTION_KEYS=" + Fernet.generate_key().decode(),
            "CARTEIRA_SERVICE_TOKEN=" + "s" * 40, "CARTEIRA_DISCORD_CLIENT_ID=1",
            "CARTEIRA_DISCORD_CLIENT_SECRET=x", "CARTEIRA_DISCORD_BOT_TOKEN=x", "CARTEIRA_GOOGLE_CLIENT_ID=x",
            "CARTEIRA_GOOGLE_CLIENT_SECRET=x", "CARTEIRA_GOOGLE_PROJECT_NUMBER=1", "CARTEIRA_PICKER_API_KEY=x",
            "CARTEIRA_GUILDS=111"]) + "\n", encoding="utf-8")
        destino = self.pasta / "app"
        with zipfile.ZipFile(self.montar(campanhas=camp, env=env)) as z:
            z.extractall(destino)
        roteiro = self.pasta / "roteiro.py"
        roteiro.write_text(textwrap.dedent("""
            import asyncio, sys
            from pathlib import Path
            app_dir = Path(sys.argv[1])
            sys.path[:0] = [str(app_dir), str(app_dir / "src")]
            import iniciar_carteira
            iniciar_carteira.preparar_ambiente(app_dir)
            from aiohttp.test_utils import TestClient, TestServer
            from carteira_viva.config_web import ConfigWeb
            from carteira_viva.web import criar_app, CONSULTAS
            import carteira_viva, closure_bot
            assert Path(carteira_viva.__file__).is_relative_to(app_dir), carteira_viva.__file__
            assert Path(closure_bot.__file__).is_relative_to(app_dir), closure_bot.__file__
            async def main():
                app = criar_app(ConfigWeb.do_ambiente())
                async with TestClient(TestServer(app)) as c:
                    for caminho in ("/saude", "/", "/privacidade", "/termos", "/carteira"):
                        r = await c.get(caminho)
                        assert r.status == 200, (caminho, r.status)
                    assert app[CONSULTAS].motor is not None
                assert (app_dir / "var" / "carteira.sqlite3").is_file()
                print("subiu")
            asyncio.run(main())
        """), encoding="utf-8")
        amb = {k: v for k, v in os.environ.items() if not k.startswith("CARTEIRA_")} | {"PYTHONUTF8": "1"}
        r = subprocess.run([sys.executable, "-I", str(roteiro), str(destino)], cwd=self.pasta, env=amb,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-3000:])
        self.assertIn("subiu", r.stdout)


if __name__ == "__main__":
    unittest.main()
