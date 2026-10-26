"""Imagens privadas cifradas em disco; bot envia anexo, não URL pública."""
import asyncio
import base64
import os
from pathlib import Path
import re
import secrets
import sys
import threading
import time
from .segredos import ErroCarteira

ID=re.compile(r'[a-f0-9]{32}\Z')
LIMITE=1024*1024


class ErroImagem(ErroCarteira):
    codigo='imagem'


class SemEspaco(ErroCarteira):
    codigo='armazenamento'


class Imagens:
    def __init__(self,pasta,cifra,*,agora=time.time,orcamento=128*1024*1024):
        self.pasta,self.cifra,self.agora,self.orcamento=Path(pasta),cifra,agora,orcamento
        if self.pasta.is_symlink(): raise ErroCarteira('Pasta de imagens inválida.')
        self.pasta.mkdir(mode=0o700,parents=True,exist_ok=True)
        if os.name=='posix' and self.pasta.stat().st_mode&0o077:
            raise ErroCarteira('A pasta de imagens precisa ser privada (0700).')
        self.trabalhos=asyncio.Semaphore(2)
        self.disco=threading.Lock()

    async def validar(self,dados):
        if not isinstance(dados,bytes) or not 0<len(dados)<=LIMITE:
            raise ErroImagem('Use uma imagem PNG, JPEG ou WebP de até 1 MiB.')
        if self.trabalhos.locked(): raise ErroCarteira('Há imagens sendo preparadas. Tente novamente.')
        async with self.trabalhos:
            proc=await asyncio.create_subprocess_exec(sys.executable,'-m','carteira_viva.imagem_worker',
                stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,
                env={'PATH':os.environ.get('PATH',''),'PYTHONPATH':str(Path(__file__).resolve().parents[1]),'PYTHONUTF8':'1'})
            try:
                async with asyncio.timeout(20):
                    proc.stdin.write(dados); await proc.stdin.drain(); proc.stdin.close()
                    partes=[];tamanho=0
                    while b:=await proc.stdout.read(65536):
                        tamanho+=len(b)
                        if tamanho>LIMITE: raise ErroCarteira('Imagem normalizada excedeu o limite.')
                        partes.append(b)
                    await proc.wait()
                if proc.returncode or not tamanho: raise ErroImagem('Não consegui preparar a imagem. Use PNG, JPEG ou WebP sem animação.')
                return b''.join(partes)
            except BaseException as exc:
                if proc.returncode is None: proc.kill()
                await proc.wait()
                if isinstance(exc,(BrokenPipeError,ConnectionResetError,TimeoutError)):
                    raise ErroImagem('Não consegui preparar a imagem. Tente outro arquivo.') from None
                raise

    def salvar(self,servidor,personagem,dados):
        mid=secrets.token_hex(16)
        b=self.cifra.cifrar(['imagem',servidor,personagem,mid],{'webp':base64.b64encode(dados).decode()})
        with self.disco:
            if sum(p.stat().st_size for p in self.pasta.glob('*.cvi') if not p.is_symlink())+len(b)>self.orcamento:
                raise SemEspaco('O armazenamento de imagens está cheio. O operador precisa conferir o espaço.')
            fd=os.open(self.pasta/(mid+'.cvi'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as f: f.write(b)
        return mid

    def ler(self,servidor,personagem,mid):
        if not isinstance(mid,str) or not ID.fullmatch(mid): raise ErroCarteira('Imagem indisponível.')
        p=self.pasta/(mid+'.cvi')
        if not p.is_file() or p.is_symlink() or p.stat().st_size>3*LIMITE: raise ErroCarteira('Imagem indisponível.')
        try:
            obj=self.cifra.abrir(['imagem',servidor,personagem,mid],p.read_bytes())
            b=base64.b64decode(obj['webp'],validate=True)
            if len(b)>LIMITE:raise ValueError()
            return b
        except (ValueError,KeyError): raise ErroCarteira('Imagem indisponível.') from None

    def limpar(self,ativos):
        with self.disco:
            for p in self.pasta.glob('*.cvi'):
                try:
                    if (not p.is_symlink() and ID.fullmatch(p.stem) and p.stem not in ativos and
                            self.agora()-p.stat().st_mtime>=86400): p.unlink()
                except FileNotFoundError: pass
