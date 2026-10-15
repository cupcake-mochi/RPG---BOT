"""Decodificador isolado de anexos. Entrada/saída por pipes; nunca abre URLs."""
from __future__ import annotations

import base64
import io
import json
import subprocess
import sys
import wave

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 4_000_000
MAX_QUADROS = 120
MAX_TRABALHO = 40_000_000
LADO = 768
AUDIO_SEGUNDOS = 30


def imagem(dados: bytes) -> dict:
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    with Image.open(io.BytesIO(dados), formats=['PNG', 'JPEG', 'WEBP', 'GIF']) as original:
        w, h = original.size
        if w * h > MAX_PIXELS:
            raise ValueError('imagem acima de 4 milhões de pixels')
        duracoes = []
        # Não confia em n_frames informado pelo arquivo; limita a varredura.
        for i in range(MAX_QUADROS + 1):
            try:
                original.seek(i)
            except EOFError:
                break
            if i >= MAX_QUADROS or (i + 1) * w * h > MAX_TRABALHO:
                raise ValueError('animação excede o limite de quadros ou pixels')
            duracoes.append(max(20, int(original.info.get('duration', 100))))
        animada = len(duracoes) > 1
        total = sum(duracoes)
        if animada and total > 15_000:
            raise ValueError('animação maior que 15 segundos')
        indices = [0]
        if animada:
            acumulado, meio = 0, 0
            for i, d in enumerate(duracoes):
                acumulado += d
                if acumulado >= total / 2:
                    meio = i
                    break
            indices = sorted({0, meio, len(duracoes) - 1})
        partes = []
        for i in indices:
            original.seek(i)
            foto = ImageOps.exif_transpose(original).convert('RGBA')
            foto.thumbnail((LADO, LADO))
            fundo = Image.new('RGB', foto.size, 'white')
            fundo.paste(foto, mask=foto.getchannel('A'))
            destino = io.BytesIO()
            fundo.save(destino, format='JPEG', quality=80)
            if animada:
                partes.append({'text': f'Quadro em {sum(duracoes[:i]) / 1000:.2f} s; amostra parcial da animação.'})
            partes.append({'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(destino.getvalue()).decode()}})
        return {'partes': partes, 'reserva': 4096 * len(indices),
                'nota': (f'{len(indices)} quadros de animação ({total / 1000:.2f} s); movimentos entre os quadros não foram enviados'
                         if animada else 'uma imagem reduzida; detalhes e textos pequenos podem estar ilegíveis')}


def formato_audio(dados):
    if dados[:4] == b'RIFF' and dados[8:12] == b'WAVE':
        return 'wav'
    if dados[:4] == b'OggS':
        return 'ogg'
    if dados[:4] == b'fLaC':
        return 'flac'
    if dados[:3] == b'ID3' or (len(dados) > 1 and dados[0] == 255 and dados[1] & 224 == 224):
        return 'mp3'
    if dados[4:8] == b'ftyp':
        return 'mov'
    if dados[:4] == b'\x1aE\xdf\xa3':
        return 'matroska'
    raise ValueError('formato de áudio não reconhecido')


def audio(dados: bytes) -> dict:
    import imageio_ffmpeg
    formato = formato_audio(dados)
    # Somente stdin/stdout: demuxer fixo e protocolos sem arquivo/rede.
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-cpucount', '1', '-hide_banner', '-loglevel', 'error',
           '-nostdin', '-threads', '1', '-filter_threads', '1', '-filter_complex_threads', '1', '-protocol_whitelist', 'pipe',
           '-f', formato, '-i', 'pipe:0', '-t', str(AUDIO_SEGUNDOS + 1),
           '-map', '0:a:0', '-vn', '-sn', '-dn', '-ac', '1', '-ar', '16000',
           '-threads', '1', '-f', 's16le', 'pipe:1']
    resultado = subprocess.run(cmd, input=dados, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
    pcm = resultado.stdout
    if resultado.returncode or not pcm or len(pcm) % 2:
        raise ValueError('áudio inválido ou não decodificável')
    if len(pcm) > AUDIO_SEGUNDOS * 32000:
        raise ValueError('áudio maior que 30 segundos; envie um trecho menor')
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(pcm)
    return {'partes': [{'inlineData': {'mimeType': 'audio/wav', 'data': base64.b64encode(buf.getvalue()).decode()}}],
            'reserva': 2048, 'nota': f'um áudio de {len(pcm) / 32000:.2f} segundos; sem vídeo'}


def main():
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_STACK, (1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
    resource.setrlimit(resource.RLIMIT_FSIZE, (2 * 1024 * 1024,) * 2)
    try:
        dados = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(dados) > MAX_BYTES:
            raise ValueError('arquivo maior que 5 MB')
        resultado = imagem(dados) if sys.argv[1] == 'imagem' else audio(dados)
    except Exception:
        # Nunca devolve caminhos, conteúdo do anexo ou diagnóstico do codec.
        resultado = {'erro': 'arquivo inválido, formato não aceito ou acima dos limites de processamento'}
    sys.stdout.write(json.dumps(resultado))


if __name__ == '__main__':
    main()
