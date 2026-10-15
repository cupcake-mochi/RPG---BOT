"""Decodificador isolado de anexos. Entrada/saída por pipes; nunca abre URLs."""
from __future__ import annotations

import base64
import io
import json
import math
import re
import subprocess
import sys
import wave

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 4_000_000
MAX_QUADROS = 120
MAX_TRABALHO = 40_000_000
LADO = 768
AUDIO_SEGUNDOS = 30


def gif_video(dados: bytes) -> dict:
    """MP4 de prévia de GIF: conta/limita quadros e envia só três imagens."""
    import imageio_ffmpeg
    from PIL import Image
    if dados[4:8] != b'ftyp':
        raise ValueError('prévia não é MP4')
    base = [imageio_ffmpeg.get_ffmpeg_exe(), '-cpucount', '1', '-hide_banner', '-nostdin',
            '-threads', '1', '-filter_threads', '1', '-filter_complex_threads', '1',
            '-protocol_whitelist', 'pipe', '-f', 'mov', '-i', 'pipe:0',
            '-map', '0:v:0', '-an', '-sn', '-dn']
    probe = subprocess.run(base + ['-vf', 'showinfo', '-frames:v', str(MAX_QUADROS + 1),
        '-t', '15.01', '-f', 'null', '-'], input=dados, stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE, timeout=5)
    log = probe.stderr.decode('utf-8', errors='replace')
    encontrados = re.findall(r'\bn:\s*(\d+)\s+pts:\s*\S+\s+pts_time:(\S+)\s+duration:\s*\S+\s+duration_time:(\S+).*?\bs:(\d+)x(\d+)', log)
    if probe.returncode or not 1 <= len(encontrados) <= MAX_QUADROS:
        raise ValueError('prévia inválida ou quadros demais')
    quadros = [(int(n), float(t), float(d), int(w), int(h)) for n, t, d, w, h in encontrados]
    if any(not math.isfinite(t + d) or t < 0 or d <= 0 or t + d > 15.001 or w*h > MAX_PIXELS
           for _, t, d, w, h in quadros) or sum(w*h for _, _, _, w, h in quadros) > MAX_TRABALHO:
        raise ValueError('prévia acima dos limites')
    duracao = max(t+d for _, t, d, _, _ in quadros)
    # A duração declarada também impede certificar só o início de um vídeo longo.
    declarada = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', log)
    if declarada and sum(float(x)*p for x, p in zip(declarada.groups(), (3600, 60, 1))) > 15.001:
        raise ValueError('prévia maior que 15 segundos')
    meio = next((q for q in quadros if q[1] + q[2] >= duracao/2), quadros[-1])
    selecionados = sorted({q[0]: q for q in (quadros[0], meio, quadros[-1])}.values())
    selecao = '+'.join(f'eq(n\\,{q[0]})' for q in selecionados)
    filtro = f"select={selecao},scale=w='min({LADO},iw)':h='min({LADO},ih)':force_original_aspect_ratio=decrease"
    resultado = subprocess.run(base + ['-loglevel', 'error', '-vf', filtro, '-fps_mode', 'passthrough',
        '-frames:v', str(len(selecionados)), '-threads', '1', '-c:v', 'ppm', '-pix_fmt', 'rgb24',
        '-f', 'image2pipe', 'pipe:1'], input=dados, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, timeout=5)
    if resultado.returncode:
        raise ValueError('não foi possível ler os quadros')
    pos, partes = 0, []
    for _, tempo, _, _, _ in selecionados:
        cab = re.match(rb'P6\s+(\d+)\s+(\d+)\s+255\n', resultado.stdout[pos:pos+80])
        if not cab:
            raise ValueError('quadro inválido')
        w, h = map(int, cab.groups())
        if not 0 < max(w, h) <= LADO:
            raise ValueError('quadro grande')
        pos += cab.end()
        foto = Image.frombytes('RGB', (w, h), resultado.stdout[pos:pos+w*h*3])
        pos += w*h*3
        buf = io.BytesIO(); foto.save(buf, format='JPEG', quality=80)
        partes += [{'text': f'Quadro em {tempo:.2f} s; amostra parcial da animação, sem áudio.'},
                   {'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(buf.getvalue()).decode()}}]
    if pos != len(resultado.stdout):
        raise ValueError('quadros extras')
    return {'partes': partes, 'reserva': 4096*len(selecionados),
            'nota': f'{len(selecionados)} quadros do GIF em prévia MP4 ({duracao:.2f} s); movimentos entre os quadros e áudio não foram enviados'}


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
    # Só silêncio digital exato após a conversão. Não usa limiar de volume
    # que poderia eliminar voz baixa ou confundir pausas com arquivo mudo.
    if not any(pcm):
        return {'partes': [], 'reserva': 0, 'silencio': True,
                'nota': 'anexo recebido e processado localmente; todas as amostras do áudio convertido são zero; nenhum áudio enviado ao modelo'}
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(pcm)
    if __package__:
        from .audio_sinais import resumo_sinais
    else:
        from audio_sinais import resumo_sinais
    medida = resumo_sinais(pcm)
    return {'partes': [{'inlineData': {'mimeType': 'audio/wav', 'data': base64.b64encode(buf.getvalue()).decode()}}],
            'reserva': 2048, 'nota': f'um áudio de {len(pcm) / 32000:.2f} segundos; sem vídeo' + ('; ' + medida if medida else '')}


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
        resultado = {'imagem': imagem, 'audio': audio, 'gif_video': gif_video}[sys.argv[1]](dados)
    except Exception:
        # Nunca devolve caminhos, conteúdo do anexo ou diagnóstico do codec.
        resultado = {'erro': 'arquivo inválido, formato não aceito ou acima dos limites de processamento'}
    sys.stdout.write(json.dumps(resultado))


if __name__ == '__main__':
    main()
