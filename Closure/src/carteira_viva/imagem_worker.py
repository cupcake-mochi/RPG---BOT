"""Decodifica imagem em processo sem credenciais; entrada/saída limitadas."""
import io
import sys
import warnings


def main():
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024))
        resource.setrlimit(resource.RLIMIT_CPU,(3,3))
        from PIL import Image,ImageOps
        Image.MAX_IMAGE_PIXELS=4_000_000
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        dados=sys.stdin.buffer.read(1024*1024+1)
        if len(dados)>1024*1024: return 2
        with Image.open(io.BytesIO(dados)) as img:
            if img.format not in ('PNG','JPEG','WEBP') or getattr(img,'n_frames',1)!=1 or img.width*img.height>4_000_000:
                return 2
            img.load(); limpa=ImageOps.exif_transpose(img).convert('RGBA')
            limpa.thumbnail((1024,1024))
            saida=io.BytesIO(); limpa.save(saida,format='WEBP',quality=85,method=4)
        b=saida.getvalue()
        if len(b)>1024*1024: return 2
        sys.stdout.buffer.write(b)
        return 0
    except Exception:
        return 2


if __name__=='__main__': raise SystemExit(main())
