"""Seletor do Discord: URLs/prévias simuladas, GIF e MP4 sintéticos, sem API."""
import asyncio
import base64
import io
import subprocess
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image
from closure_bot import midia_gifs as gifs
from closure_bot.midia import Midias
from closure_bot.midia_anexos import Anexos, decodificar
from closure_bot.modelo import montar_corpo, reserva_midia
from testes.test_midia_anexos import pedido

LINK = 'https://klipy.com/gifs/anime-my-dress-up-darling-3'
CDN = 'https://static.klipy.com/ii/4493325008d34b7bf8cd6813cd5c1619/d4/7f/Nloy6vTYGBXbdhLIC53.mp4'
PROXY = 'https://images-ext-1.discordapp.net/external/TgkYerDJEnilAgBC1JyGTiCoxS7BSiSuf-5fZ_-OeLU/https/' + CDN.split('https://')[1]


def mensagem(link=LINK, url=CDN, proxy=PROXY):
    return NS(id=123, content='Olha este GIF: '+link, attachments=[], channel=NS(id=10),
              embeds=[NS(url=link, video=NS(url=url, proxy_url=proxy))])


def gif():
    frames = [Image.new('RGB', (96, 64), cor) for cor in ('red', 'green', 'blue')]
    buf = io.BytesIO()
    frames[0].save(buf, format='GIF', save_all=True, append_images=frames[1:], duration=400)
    return buf.getvalue()


def mp4(segundos=None, fps=10):
    import imageio_ffmpeg
    base = [imageio_ffmpeg.get_ffmpeg_exe(), '-cpucount', '1', '-loglevel', 'error', '-threads', '1', '-filter_threads', '1']
    if segundos is None:
        entrada = ['-f', 'gif', '-i', 'pipe:0', '-vf', f'fps={fps}']
    else:
        entrada = ['-f', 'lavfi', '-i', f'color=c=blue:s=96x64:r={fps}:d={segundos}']
    return subprocess.run(base + entrada + ['-an', '-threads', '1', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-movflags', 'frag_keyframe+empty_moov', '-f', 'mp4', 'pipe:1'], input=gif(), capture_output=True, check=True).stdout


class Enderecos(unittest.TestCase):
    def test_link_real_e_proxy_correspondente(self):
        self.assertEqual(gifs.pagina(LINK), ('klipy', '/gifs/anime-my-dress-up-darling-3'))
        self.assertEqual(gifs.escolher(mensagem(), LINK), (PROXY, 'gif_video'))
        self.assertEqual(gifs.tipo_midia(CDN, 'klipy'), 'gif_video')

    def test_dominios_credenciais_caminhos_e_troca_de_provedor(self):
        for url in ['http://static.klipy.com/a.gif', 'https://static.klipy.com.evil/a.gif',
                    'https://static.klipy.com@127.0.0.1/a.gif', 'https://static.klipy.com:444/a.gif',
                    'https://static.klipy.com/../a.gif', 'https://static.klipy.com/%2e%2e/a.gif',
                    PROXY.replace('static.klipy.com', '127.0.0.1'), PROXY.replace('/https/', '/http/'),
                    PROXY.replace('images-ext-1.discordapp.net', 'evil.example'),
                    'https://static.klipy.com/a.png', 'https://static.klipy.com/a.m3u8']:
            with self.subTest(url=url): self.assertIsNone(gifs.tipo_midia(url, 'klipy'))
        self.assertIsNone(gifs.tipo_midia(CDN, 'tenor'))
        self.assertIsNone(gifs.pagina('https://klipy.com/gifs/a/../../etc'))
        self.assertIsNone(gifs.pagina('https://youtu.be/DeumyOzKqgI'))
        self.assertIsNone(gifs.pagina('https:///gifs/teste'))

    def test_nao_usa_embed_de_outro_link_nem_miniatura_estatica(self):
        m=mensagem(); m.embeds[0].url='https://klipy.com/gifs/outro'
        self.assertIsNone(gifs.escolher(m, LINK))
        m=mensagem(url=CDN.replace('.mp4','.png'), proxy=None)
        self.assertIsNone(gifs.escolher(m, LINK))

    def test_tenor_giphy_e_query_preservada(self):
        for link, url in [('https://tenor.com/view/test-gif-12345','https://media.tenor.com/abcd/ok.gif'),
                          ('https://giphy.com/gifs/test-abc123','https://media2.giphy.com/media/abc123/giphy.gif?cid=teste')]:
            self.assertEqual(gifs.escolher(mensagem(link,url,None), link), (url,'imagem'))


class Fluxo(unittest.IsolatedAsyncioTestCase):
    async def test_http_sem_redirecionamento_e_limite_no_fluxo(self):
        class Resposta:
            def __init__(self, status=200, tamanho=None, chunks=(b'gif',)):
                self.status=status;self.content_length=tamanho;self.content=self;self.chunks=chunks
            async def __aenter__(self):return self
            async def __aexit__(self,*a):pass
            async def iter_chunked(self,*a):
                for c in self.chunks:yield c
        for resposta, ok in [(Resposta(),True),(Resposta(302),False),(Resposta(tamanho=gifs.MAX_BYTES+1),False),
                             (Resposta(chunks=(b'x'*gifs.MAX_BYTES,b'x')),False)]:
            sessao=MagicMock();sessao.__aenter__=AsyncMock(return_value=sessao)
            sessao.__aexit__=AsyncMock(return_value=False);sessao.get.return_value=resposta
            with patch('aiohttp.ClientSession',return_value=sessao):
                if ok:self.assertEqual(await gifs.baixar(PROXY,'klipy'),b'gif')
                else:
                    with self.assertRaises(ValueError):await gifs.baixar(PROXY,'klipy')
            sessao.get.assert_called_once_with(PROXY,allow_redirects=False)

    async def test_http_origem_invalida_recusada_antes_da_rede(self):
        with patch('aiohttp.ClientSession') as sessao:
            with self.assertRaises(ValueError):await gifs.baixar('https://localhost/a.mp4','klipy')
            sessao.assert_not_called()

    async def test_previa_tardia_busca_uma_vez_e_mensagem_editada_recusa(self):
        m=mensagem(); m.embeds=[];m.channel.fetch_message=AsyncMock(return_value=mensagem())
        with patch.object(gifs.asyncio,'sleep',new=AsyncMock()):
            self.assertEqual(await gifs.resolver(m,LINK),(PROXY,'gif_video'))
            m.channel.fetch_message.assert_awaited_once_with(123)
            m.channel.fetch_message.return_value.content='editei'
            with self.assertRaises(ValueError):await gifs.resolver(m,LINK)

    async def test_sem_previa_nao_adivinha_url_nem_busca_site(self):
        m=mensagem();m.embeds=[]
        with self.assertRaises(ValueError):await gifs.resolver(m,LINK)

    async def test_desligado_ou_outro_canal_nao_resolve(self):
        resolver=AsyncMock();download=AsyncMock()
        for ativo,canais in [(False,()),(True,{20})]:
            a=Anexos(ativo=ativo,canais=canais,resolver_gif=resolver,download_gif=download)
            self.assertFalse((await a.contexto(mensagem())).partes)
        resolver.assert_not_awaited();download.assert_not_awaited()

    async def test_mp4_real_normalizado_ate_o_corpo_e_metadados_sem_conflito(self):
        a=Anexos(ativo=True,download_gif=AsyncMock(return_value=mp4()))
        m=mensagem();p=await a.contexto(m)
        self.assertEqual(p.links_analisados,(LINK,))
        self.assertEqual(len([x for x in p.partes if 'inlineData' in x]),3)
        e=pedido(p);self.assertGreaterEqual(reserva_midia(e),3*4096)
        corpo=montar_corpo(e)
        blobs=[x['inlineData'] for x in corpo['contents'][-1]['parts'] if 'inlineData' in x]
        cores=[]
        for b in blobs:
            self.assertEqual(b['mimeType'],'image/jpeg')
            with Image.open(io.BytesIO(base64.b64decode(b['data']))) as im:cores.append(im.getpixel((10,10)))
        self.assertGreater(cores[0][0],200);self.assertGreater(cores[-1][2],200)
        self.assertIn('áudio não foram enviados',p.nota)
        metadados=Midias(AsyncMock(side_effect=AssertionError('não consultar YouTube')))
        self.assertEqual(await metadados.contexto(m,m.content,links_analisados=p.links_analisados),'')
        self.assertNotIn(blobs[0]['data'],p.historico+repr(p))

    async def test_gif_puro_primeiro_link_e_anexo_tem_prioridade(self):
        url=CDN.replace('.mp4','.gif')
        resolver=AsyncMock(return_value=(url,'imagem'))
        a=Anexos(ativo=True,resolver_gif=resolver,download_gif=AsyncMock(return_value=gif()))
        m=mensagem();m.content+=' https://klipy.com/gifs/outro'
        p=await a.contexto(m);self.assertTrue(p.partes);self.assertIn('primeiro GIF',p.nota)
        resolver.assert_awaited_once_with(m,LINK)
        resolver.reset_mock();m.attachments=[NS(filename='arquivo.html')]
        self.assertFalse((await a.contexto(m)).partes);resolver.assert_not_awaited()

    async def test_falha_provedor_invalido_arquivo_ruim_e_youtube(self):
        download=AsyncMock(return_value=b'arquivo invalido')
        a=Anexos(ativo=True,resolver_gif=AsyncMock(return_value=('https://localhost/a.gif','imagem')),download_gif=download)
        self.assertIn('não analisado',(await a.contexto(mensagem())).nota);download.assert_not_awaited()
        a.resolver_gif=AsyncMock(return_value=(CDN.replace('.mp4','.gif'),'imagem'))
        self.assertFalse((await a.contexto(mensagem())).partes)
        a.resolver_gif.reset_mock()
        self.assertFalse((await a.contexto(mensagem(link='https://youtu.be/DeumyOzKqgI'))).partes)
        a.resolver_gif.assert_not_awaited()

    async def test_video_longo_quadros_demais_e_playlist_recusados(self):
        for raw in [mp4(16,fps=1), mp4(5,fps=30),b'#EXTM3U\nhttps://localhost/segredo']:
            with self.assertRaises(ValueError):await decodificar(raw,'gif_video')

    async def test_cancelamento_libera_processamento(self):
        iniciou=asyncio.Event()
        async def resolver(*a):iniciou.set();await asyncio.Future()
        a=Anexos(ativo=True,resolver_gif=resolver)
        t=asyncio.create_task(a.contexto(mensagem()));await iniciou.wait()
        self.assertIn('ocupado',(await a.contexto(mensagem())).nota)
        t.cancel()
        with self.assertRaises(asyncio.CancelledError):await t
        self.assertFalse(a._vaga.locked())
