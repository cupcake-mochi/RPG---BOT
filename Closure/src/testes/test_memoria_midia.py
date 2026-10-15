"""Reinício, privacidade e metadados; sem Discord/YouTube/Gemini reais."""
import asyncio
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from closure_bot.conversa import Conversas, TURNOS_MAX
from closure_bot.registro import Registro, Cofre
from closure_bot.plantao import FUSO
from closure_bot.midia import Midias, video_id, AVISO

AGORA = datetime(2026, 10, 15, 12, 0, tzinfo=FUSO)


class Persistencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.arquivo = Path(self.tmp.name) / 'banco.sqlite'
        self.chave = Cofre.nova_chave()
        self.reg = Registro(self.arquivo, self.chave)
        self.addCleanup(lambda: self.reg.fechar())
        self.conv = Conversas(self.reg)

    def par(self, canal=7, persona='kaltsit', pessoa=42, quando=AGORA):
        self.conv.anotar(canal, persona, quando, 'minha música', nome='Alex', autor_id=pessoa, midia='título confirmado')
        self.conv.anotar(canal, persona, quando, 'resposta da guia', autor_id=pessoa)

    def test_reabrir_recupera_cifrado_e_separado(self):
        self.par()
        self.reg.fechar()
        self.assertNotIn(b'minha m', self.arquivo.read_bytes())
        self.assertNotIn(b'Alex', self.arquivo.read_bytes())
        self.reg = Registro(self.arquivo, self.chave)
        nova = Conversas(self.reg)
        t = nova.turnos(7, 'kaltsit', AGORA + timedelta(minutes=5))
        self.assertEqual((t[0].texto, t[0].midia), ('minha música', 'título confirmado'))
        self.assertEqual(nova.turnos(7, 'closure', AGORA), [])
        self.assertEqual(nova.turnos(8, 'kaltsit', AGORA), [])

    def test_expira_sem_consulta_ao_canal(self):
        self.par()
        self.conv.limpar(AGORA + timedelta(minutes=30))
        self.assertEqual(self.reg._db.execute('SELECT count(*) FROM conversas_recentes').fetchone()[0], 0)
        self.assertEqual(self.reg._db.execute('SELECT count(*) FROM participantes_conversa').fetchone()[0], 0)

    def test_corte_das_4h30_e_limite(self):
        antes = AGORA.replace(hour=4, minute=20)
        self.par(quando=antes)
        self.assertEqual(self.conv.turnos(7, 'kaltsit', antes + timedelta(minutes=10)), [])
        for i in range(20):
            self.conv.anotar(7, 'kaltsit', AGORA, str(i), autor_id=42)
        self.assertEqual(len(self.conv.turnos(7, 'kaltsit', AGORA)), TURNOS_MAX)
        self.assertEqual(self.conv.turnos(7, 'kaltsit', AGORA)[0].texto, '8')

    def test_apagar_pessoa_remove_fio_e_respostas_associadas(self):
        self.par()
        self.par(pessoa=43)
        self.par(canal=8, pessoa=43)
        self.reg.guardar_fala(canal_id=7, persona='kaltsit', texto='resposta com informação da pessoa')
        self.reg.apagar_pessoa(42)
        self.assertEqual(self.conv.turnos(7, 'kaltsit', AGORA), [])
        self.assertEqual(len(self.conv.turnos(8, 'kaltsit', AGORA)), 2)
        self.assertEqual(self.reg._db.execute('SELECT count(*) FROM falas WHERE canal_id=7').fetchone()[0], 0)

    def test_protecao_em_andamento_e_liberada_mesmo_com_erro(self):
        with self.assertRaises(RuntimeError):
            with self.reg.proteger_dados({42}) as a, self.reg.proteger_dados({42}) as b:
                self.reg.apagar_pessoa(42)
                self.assertEqual(a.apagados, {42})
                self.assertEqual(b.apagados, {42})
                raise RuntimeError("simulado")
        self.assertEqual(self.reg._leituras, [])
        with self.reg.proteger_dados({42}) as nova:
            self.assertEqual(nova.apagados, set())

    def test_chave_errada_nao_manda_cifra_ao_modelo(self):
        self.par()
        self.reg.cofre = Cofre(Cofre.nova_chave())
        self.assertEqual(self.conv.turnos(7, 'kaltsit', AGORA), [])


class Metadados(unittest.IsolatedAsyncioTestCase):
    def mensagem(self, anexos=(), embeds=()):
        return SimpleNamespace(attachments=anexos, embeds=embeds)

    def test_url_so_aceita_youtube_e_id_validos(self):
        for u in ('https://youtu.be/DeumyOzKqgI?t=2', 'https://www.youtube.com/watch?v=DeumyOzKqgI',
                  'https://youtube.com/shorts/DeumyOzKqgI'):
            self.assertEqual(video_id(u), 'DeumyOzKqgI')
        for u in ('https://youtube.com.evil/watch?v=DeumyOzKqgI', 'https://youtube.com@localhost/watch?v=DeumyOzKqgI',
                  'http://127.0.0.1/a', 'https://youtube.com:123/watch?v=DeumyOzKqgI', 'https://youtu.be/../../a'):
            self.assertIsNone(video_id(u))

    async def test_reconhece_sem_embed_e_reutiliza_cache(self):
        buscar = AsyncMock(return_value={'title': 'Adele - Skyfall', 'author_name': 'AdeleVEVO'})
        midias = Midias(buscar)
        texto = 'ouvi isso https://youtu.be/DeumyOzKqgI'
        a = await midias.contexto(self.mensagem(), texto)
        b = await midias.contexto(self.mensagem(), texto)
        self.assertIn('Adele - Skyfall', a)
        self.assertEqual(a, b)
        buscar.assert_awaited_once_with('DeumyOzKqgI')
        self.assertNotIn('piano', a)

    async def test_falha_nao_inventa_e_cache_expira(self):
        buscar = AsyncMock(side_effect=TimeoutError)
        tempo = [0]
        midias = Midias(buscar, lambda: tempo[0])
        for _ in range(2):
            self.assertIn('indisponível', await midias.contexto(self.mensagem(), 'https://youtu.be/DeumyOzKqgI'))
        self.assertEqual(buscar.await_count, 1)
        tempo[0] = 61
        await midias.contexto(self.mensagem(), 'https://youtu.be/DeumyOzKqgI')
        self.assertEqual(buscar.await_count, 2)

    async def test_gif_e_anexo_nao_sao_visao_e_link_arbitrario_nao_e_buscado(self):
        buscar = AsyncMock()
        midias = Midias(buscar)
        m = self.mensagem([SimpleNamespace(filename='reacao.gif')])
        texto = await midias.contexto(m, 'https://localhost/segredo')
        self.assertIn('não analisado', texto)
        buscar.assert_not_awaited()
        self.assertEqual(await midias.contexto(self.mensagem(), 'oi'), '')

    async def test_maximo_dois_videos_e_limite_textual(self):
        buscar = AsyncMock(return_value={'title': 'x' * 10000})
        m = Midias(buscar)
        t = await m.contexto(self.mensagem(), ' '.join('https://youtu.be/' + i * 11 for i in 'abcdef'))
        self.assertEqual(buscar.await_count, 2)
        self.assertLess(len(t), 700)

    async def test_previa_do_discord_identifica_quando_consulta_falha(self):
        m = Midias(AsyncMock(side_effect=TimeoutError))
        embed = SimpleNamespace(url='https://www.youtube.com/watch?v=DeumyOzKqgI', title='Adele - Skyfall')
        texto = await m.contexto(self.mensagem(embeds=[embed]), 'https://youtu.be/DeumyOzKqgI')
        self.assertIn('Adele - Skyfall', texto)
        self.assertIn('prévia textual do Discord', texto)
        self.assertNotIn('indisponível', texto)

    async def test_metadados_historicos_fora_da_busca_e_id_fora_do_prompt(self):
        from closure_bot.prompt import montar
        from closure_bot.conversa import Turno
        ponte = SimpleNamespace(montar=lambda *a, **kw: {'input': [
            {'role': 'user', 'content': 'sistema'}, {'role': 'user', 'content': kw['turnos'][0]['texto']},
            {'role': 'user', 'content': 'atual'}]})
        t = Turno(AGORA, 'ouvi uma música', 'Alex', 987654321, 'Adele - Skyfall')
        with patch('closure_bot.prompt._ponte', return_value=ponte):
            p = await montar('kaltsit', 'conhece?', nome='Alex', pronomes=None, turnos=[t], falas_anteriores=[], estado={})
        self.assertIn('Adele - Skyfall', p[1]['content'])
        self.assertIn(AVISO, p[0]['content'])
        self.assertNotIn('987654321', str(p))
