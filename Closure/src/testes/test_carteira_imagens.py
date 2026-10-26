import base64
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock,patch
from PIL import Image
from cryptography.fernet import Fernet
from carteira_viva.imagens import Imagens,ErroImagem,SemEspaco
from carteira_viva.segredos import Cifra,ErroCarteira


def png():
    b=io.BytesIO();Image.new('RGB',(32,32),'teal').save(b,format='PNG');return b.getvalue()


class ImagensTeste(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.clock=[100000.];self.chave=Fernet.generate_key();self.m=Imagens(Path(self.tmp.name)/'imagens',Cifra((self.chave,)),agora=lambda:self.clock[0])
    async def asyncTearDown(self):self.tmp.cleanup()
    async def test_normaliza_em_worker_sem_metadata_e_salva_cifrado(self):
        b=await self.m.validar(png());mid=self.m.salvar('s','p',b)
        with Image.open(io.BytesIO(b)) as img:self.assertEqual(img.format,'WEBP');self.assertEqual(img.size,(32,32));self.assertFalse(img.getexif())
        arquivo=self.m.pasta/(mid+'.cvi');self.assertNotIn(b,arquivo.read_bytes());self.assertEqual(self.m.ler('s','p',mid),b)
        if os.name=='posix':self.assertEqual(arquivo.stat().st_mode&0o777,0o600)
    async def test_formato_falso_svg_html_url_e_tamanho(self):
        for b in (b'<svg/>',b'<html>oi</html>',b'http://127.0.0.1',b'GIF89a',b'',b'x'*(1024*1024+1)):
            with self.subTest(b=b[:15]),self.assertRaises(ErroCarteira):await self.m.validar(b)
    async def test_animacao_recusada(self):
        b=io.BytesIO();a=Image.new('RGB',(10,10),'red');a.save(b,format='WEBP',save_all=True,append_images=[Image.new('RGB',(10,10),'blue')],duration=100)
        with self.assertRaises(ErroImagem):await self.m.validar(b.getvalue())
    async def test_imagem_grande_em_pixels_recusada(self):
        b=io.BytesIO();Image.new('1',(3000,3000)).save(b,format='PNG')
        with self.assertRaises(ErroImagem):await self.m.validar(b.getvalue())
    async def test_contexto_travessia_e_arquivo_ausente(self):
        mid=self.m.salvar('s','p',b'webp-ficticio')
        for s,p,m in (('outro','p',mid),('s','outro',mid),('s','p','../segredo'),('s','p','a'*32)):
            with self.subTest(s=s,p=p,m=m),self.assertRaises(ErroCarteira):self.m.ler(s,p,m)
    async def test_limpeza_preserva_ativo_e_jovem(self):
        velho=self.m.salvar('s','p',b'1');ativo=self.m.salvar('s','p',b'2');novo=self.m.salvar('s','p',b'3')
        for mid in (velho,ativo):os.utime(self.m.pasta/(mid+'.cvi'),(1,1))
        self.m.limpar({ativo})
        self.assertFalse((self.m.pasta/(velho+'.cvi')).exists());self.assertTrue((self.m.pasta/(ativo+'.cvi')).exists());self.assertTrue((self.m.pasta/(novo+'.cvi')).exists())
    async def test_orcamento_nao_enche_disco(self):
        self.m.orcamento=1
        with self.assertRaises(SemEspaco):self.m.salvar('s','p',b'aa')
        self.assertFalse(list(self.m.pasta.iterdir()))
    async def test_worker_interrompido_vira_erro_seguro(self):
        from types import SimpleNamespace
        proc=SimpleNamespace(stdin=SimpleNamespace(write=lambda _:None,drain=AsyncMock(side_effect=BrokenPipeError())),returncode=2,wait=AsyncMock())
        with patch('asyncio.create_subprocess_exec',AsyncMock(return_value=proc)):
            with self.assertRaises(ErroImagem):await self.m.validar(png())
        proc.wait.assert_awaited_once()
    async def test_backup_de_imagem_exige_chave_anterior(self):
        import shutil
        mid=self.m.salvar('s','p',b'webp-ficticio')
        novo=Fernet.generate_key();destino=Path(self.tmp.name)/'restaurado'
        shutil.copytree(self.m.pasta,destino)
        restaurado=Imagens(destino,Cifra((novo,self.chave)))
        self.assertEqual(restaurado.ler('s','p',mid),b'webp-ficticio')
