"""Arquivos sintéticos e HTTP/modelo simulados; nenhum consumo pago."""
import asyncio
import base64
import io
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from PIL import Image
from closure_bot.midia import AVISO
from closure_bot.midia_anexos import Anexos, Preparo, decodificar, url_discord, AVISO_ATIVO, AVISO_VISUAL, AVISO_REPRESENTACAO
from closure_bot.midia_preparar import MAX_BYTES
from closure_bot.modelo import Modelos, montar_corpo, reserva_midia, Falhou, FLASH
from closure_bot.registro import Registro
from closure_bot.config import carregar


def foto(tamanho=(800, 600), formato='PNG'):
    b = io.BytesIO()
    Image.new('RGB', tamanho, 'red').save(b, format=formato)
    return b.getvalue()


def wav(segundos=1, *, silencio=False, amostra=1):
    b = io.BytesIO()
    with wave.open(b, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((b'\0\0' if silencio else amostra.to_bytes(2, 'little', signed=True)) * int(segundos * 16000))
    return b.getvalue()


def pedido(p):
    e = [{'role': 'user', 'content': 'sistema ' + AVISO}, {'role': 'user', 'content': 'O que aparece?'}]
    p.aplicar(e)
    return e


def mensagem(nome='foto.png', **attrs):
    a = SimpleNamespace(filename=nome, size=500, url='https://cdn.discordapp.com/attachments/12/34/foto.png')
    for k, v in attrs.items(): setattr(a, k, v)
    return SimpleNamespace(channel=SimpleNamespace(id=10), attachments=[a])


class Decodificacao(unittest.IsolatedAsyncioTestCase):
    async def test_orientacao_visual_so_quando_imagem_foi_enviada(self):
        imagem=await decodificar(foto(),'imagem')
        audio=await decodificar(wav(),'audio')
        for preparado,esperado in [(imagem,True),(audio,False),(Preparo(nota='GIF não analisado'),False),(Preparo(),False)]:
            with self.subTest(esperado=esperado,nota=preparado.nota):
                e=pedido(preparado)
                self.assertEqual(AVISO_VISUAL in e[0]['content'],esperado)
                self.assertEqual(AVISO_REPRESENTACAO in e[0]['content'],esperado)
                self.assertNotIn(AVISO_VISUAL,preparado.historico)
                self.assertNotIn(AVISO_REPRESENTACAO,preparado.historico)

    async def test_foto_reduzida_sem_exif_e_reserva(self):
        p = await decodificar(foto((1500, 1000)), 'imagem')
        data = base64.b64decode(p.partes[0]['inlineData']['data'])
        with Image.open(io.BytesIO(data)) as im:
            self.assertEqual(im.size, (768, 512)); self.assertFalse(im.getexif())
        e = pedido(p)
        self.assertNotIn(AVISO, e[0]['content']); self.assertIn(AVISO_ATIVO, e[0]['content'])
        self.assertEqual(reserva_midia(e), 4096)
        self.assertEqual(montar_corpo(e)['contents'][-1]['parts'][1], p.partes[0])
        self.assertNotIn(p.partes[0]['inlineData']['data'], p.historico + repr(p))

    async def test_gif_amostragem_temporal_e_quadro_final(self):
        b = io.BytesIO()
        frames = [Image.new('RGB', (60, 60), c) for c in ('red', 'green', 'blue', 'yellow')]
        frames[0].save(b, format='GIF', save_all=True, append_images=frames[1:], duration=[100, 100, 1000, 100])
        p = await decodificar(b.getvalue(), 'imagem')
        self.assertEqual(len(p.partes), 6)
        self.assertIn('0.20 s', p.partes[2]['text']); self.assertIn('1.20 s', p.partes[4]['text'])
        self.assertIn('não foram enviados', p.nota)
        self.assertGreater(reserva_midia(pedido(p)), 3 * 4096)

    async def test_imagem_grande_corrompida_e_animacao_longa_recusadas(self):
        b = io.BytesIO(); f = [Image.new('RGB', (20, 20), c) for c in ('red', 'blue')]
        f[0].save(b, format='GIF', save_all=True, append_images=f[1:], duration=10000)
        for dados in (foto((2100, 2000)), b'nao sou imagem', b.getvalue()):
            with self.subTest(tamanho=len(dados)):
                with self.assertRaises(ValueError): await decodificar(dados, 'imagem')

    async def test_audio_normalizado_e_duracao_maxima(self):
        p = await decodificar(wav(30), 'audio')
        with wave.open(io.BytesIO(base64.b64decode(p.partes[0]['inlineData']['data']))) as w:
            self.assertEqual((w.getnchannels(), w.getframerate(), w.getnframes()), (1, 16000, 480000))
        self.assertEqual(reserva_midia(pedido(p)), 2048)
        with self.assertRaises(ValueError): await decodificar(wav(30.1), 'audio')
        with self.assertRaises(ValueError): await decodificar(b'#EXTM3U\nfile:///etc/passwd', 'audio')

    async def test_silencio_exato_local_sem_descartar_sinal_fraco(self):
        p = await decodificar(wav(silencio=True), 'audio')
        self.assertTrue(p.silencio)
        self.assertFalse(p.partes)
        self.assertEqual(reserva_midia(pedido(p)), 0)
        self.assertIn('conferido localmente', p.historico)
        self.assertIsNotNone(p.resposta_local("Kal'tsit, pode transcrever esse áudio?"))
        self.assertIsNone(p.resposta_local('Pode transcrever esse áudio? Quanto custa a katana?'))
        self.assertIsNone(p.resposta_local('Quanto custa uma katana?'))
        p.nota += '; os demais não foram analisados'
        self.assertIn('só o primeiro', p.resposta_local(''))
        fraco = await decodificar(wav(), 'audio')
        self.assertFalse(fraco.silencio)
        self.assertTrue(fraco.partes)
        with self.assertRaises(ValueError):
            await decodificar(wav(30.1, silencio=True), 'audio')

    async def test_excesso_de_bytes_recusado_antes_de_processar(self):
        with self.assertRaises(ValueError): await decodificar(b'a' * (MAX_BYTES + 1), 'imagem')

    async def test_ogg_mp3_flac_e_m4a(self):
        import imageio_ffmpeg, subprocess
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / 'fala.wav'; origem.write_bytes(wav(amostra=10000))
            for ext, codec in (('ogg', 'libopus'), ('mp3', 'libmp3lame'), ('flac', 'flac'), ('m4a', 'aac')):
                with self.subTest(ext=ext):
                    saida = Path(pasta) / ('voz.' + ext)
                    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-i', str(origem),
                                    '-c:a', codec, str(saida)], check=True, capture_output=True)
                    p = await decodificar(saida.read_bytes(), 'audio')
                    self.assertEqual(p.partes[0]['inlineData']['mimeType'], 'audio/wav')


class Entrada(unittest.IsolatedAsyncioTestCase):
    def test_url_exata_sem_usuario_porta_ou_redirecionamento(self):
        self.assertTrue(url_discord('https://cdn.discordapp.com/attachments/12/34/test.png?ex=123'))
        for url in ('http://cdn.discordapp.com/attachments/a', 'https://cdn.discordapp.com.evil/attachments/a',
                    'https://cdn.discordapp.com@localhost/attachments/a', 'https://127.0.0.1/attachments/a',
                    'https://cdn.discordapp.com:444/attachments/a', 'https://cdn.discordapp.com/outro/a'):
            self.assertFalse(url_discord(url))

    def test_config_desligada_e_validacao(self):
        self.assertFalse(carregar(Path('/nao-existe'), ambiente={}).midia_ativa)
        c = carregar(Path('/nao-existe'), ambiente={'MIDIA_ATIVA':'1','MIDIA_CANAIS':'10,20'})
        self.assertTrue(c.midia_ativa); self.assertEqual(c.midia_canais, {10,20})
        for e in ({'MIDIA_ATIVA':'talvez'}, {'MIDIA_CANAIS':'10,-1'}):
            with self.assertRaises(ValueError): carregar(Path('/nao-existe'), ambiente=e)

    async def test_desligado_canal_diferente_e_arquivo_grande_nao_baixam(self):
        baixar = AsyncMock()
        for a, m in ((Anexos(download=baixar), mensagem()),
                     (Anexos(ativo=True, canais={20}, download=baixar), mensagem()),
                     (Anexos(ativo=True, download=baixar), mensagem(size=MAX_BYTES+1)),
                     (Anexos(ativo=True, download=baixar), mensagem('arquivo.html'))):
            self.assertFalse((await a.contexto(m)).partes)
        baixar.assert_not_awaited()

    async def test_primeiro_anexo_e_recusa_falha_sem_imaginar(self):
        preparar = AsyncMock(return_value=Preparo([{'text':'quadro'}], 'uma imagem', 4096))
        baixar = AsyncMock(return_value=b'foto'); a = Anexos(ativo=True, download=baixar, preparar=preparar)
        m = mensagem(); m.attachments *= 2
        p = await a.contexto(m)
        self.assertIn('demais não foram analisados', p.nota)
        preparar.assert_awaited_once_with(b'foto', 'imagem')
        preparar.side_effect = ValueError()
        p = await a.contexto(m)
        self.assertFalse(p.partes); self.assertIn('não analisado', p.nota)

    async def test_ocupado_e_cancelamento_liberam_vaga(self):
        iniciado, terminar = asyncio.Event(), asyncio.Event()
        async def download(url):
            iniciado.set(); await terminar.wait(); return b'foto'
        a = Anexos(ativo=True, download=download)
        task = asyncio.create_task(a.contexto(mensagem())); await iniciado.wait()
        p = await a.contexto(mensagem()); self.assertIn('ocupado', p.nota)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError): await task
        self.assertFalse(a._vaga.locked())


class Orcamento(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.p = await decodificar(foto(), 'imagem')
        self.r = Registro(':memory:'); self.addCleanup(self.r.fechar)
        self.enviar = AsyncMock(return_value={'usageMetadata':{'promptTokenCount':1200,'candidatesTokenCount':20},
            'candidates':[{'content':{'parts':[{'text':'Uma imagem vermelha.'}]}, 'finishReason':'STOP'}]})

    async def test_apenas_vertex_flash_e_uma_tentativa(self):
        m = Modelos([('gemini',FLASH),('vertex','gemini-3.1-flash-lite')], {'gemini':'g','vertex':'v'}, self.r, enviar=self.enviar)
        await m.responder(pedido(self.p), usar_argon=True)
        self.assertIn('aiplatform.googleapis.com', self.enviar.call_args.args[0])
        self.assertIn(FLASH, self.enviar.call_args.args[0]); self.assertEqual(self.enviar.await_count,1)
        self.enviar.reset_mock();self.enviar.side_effect = Falhou(400,'simulado')
        with self.assertRaises(Falhou): await m.responder(pedido(self.p))
        self.assertEqual(self.enviar.await_count,1)

    async def test_reserva_visual_barra_chamada_e_timeout_conserva_custo(self):
        m = Modelos([('vertex', FLASH)], {'vertex':'v'}, self.r, enviar=self.enviar, teto_usd=.009)
        with self.assertRaises(Falhou): await m.responder(pedido(self.p))
        self.enviar.assert_not_awaited()
        m.teto_usd=9;self.enviar.side_effect = Falhou('rede','simulado')
        with self.assertRaises(Falhou): await m.responder(pedido(self.p))
        reserva=self.r._db.execute('SELECT reserva_sem_uso_usd FROM chamadas_api').fetchone()[0]
        self.assertGreater(reserva, .010)

    async def test_historico_tipo_e_midia_mista_nao_passam(self):
        e = pedido(self.p);e.append({'role':'user','content':'de novo'})
        with self.assertRaises(ValueError): montar_corpo(e)
        with self.assertRaises(ValueError): montar_corpo(pedido(self.p), modelo='gemini-4-argon')
        e=pedido(self.p);e[-1]['midias'] *= 4
        with self.assertRaises(ValueError): montar_corpo(e)
