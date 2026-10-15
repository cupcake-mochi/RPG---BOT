"""Medições com tons variados e negativos; nenhuma chamada de modelo."""
import io
import math
import random
import struct
import unittest
import wave
from pathlib import Path
from closure_bot.audio_sinais import medir_tons, resumo_sinais
from closure_bot.midia_anexos import decodificar, AVISO_AUDIO, Preparo


def sinal(trechos, segundos=2, amplitude=6000):
    return b''.join(struct.pack('<h', int(sum(amplitude*math.sin(math.tau*f*i/16000)
                        for a,b,f in trechos if a<=i/16000<b))) for i in range(int(segundos*16000)))


class Medidas(unittest.TestCase):
    def test_contagens_frequencias_e_volumes_variados(self):
        for n,f,amp in [(1,220,500),(2,440,8000),(3,880,12000),(5,1234,3000)]:
            with self.subTest(n=n,f=f,amp=amp):
                pcm=sinal([(i*.3,i*.3+.2,f) for i in range(n)],amplitude=amp)
                med=medir_tons(pcm)
                self.assertEqual(len(med),n)
                for i,t in enumerate(med):
                    self.assertAlmostEqual(t['inicio_s'],i*.3,delta=.021)
                    self.assertAlmostEqual(t['fim_s'],i*.3+.2,delta=.021)
                    self.assertAlmostEqual(t['frequencia_hz'],f,delta=2)

    def test_ruido_acorde_estalos_e_sinal_constante_nao_viram_tons_puros(self):
        rng=random.Random(27)
        ruido=b''.join(struct.pack('<h',rng.randint(-8000,8000)) for _ in range(32000))
        acorde=sinal([(0,2,440),(0,2,660)],amplitude=4000)
        estalos=b'\0\0'*500+b'\xff\x7f'+b'\0\0'*10000
        for pcm in (ruido,acorde,estalos,b'\x10\x27'*32000,b'\0\0'*32000,b''):
            with self.subTest(tamanho=len(pcm)):
                self.assertEqual(medir_tons(pcm),[])

    def test_tom_pequeno_em_audio_misto_nao_descreve_tudo(self):
        rng=random.Random(12)
        ruido=b''.join(struct.pack('<h',rng.randint(-6000,6000)) for _ in range(16000))
        self.assertEqual(medir_tons(sinal([(0,.2,440)],segundos=1)+ruido),[])
        self.assertEqual(medir_tons(b'a'),[])
        self.assertEqual(medir_tons(b'\0\0'*(31*16000)),[])

    def test_medidas_nao_afirmam_origem_ou_ausencia_de_fala(self):
        nota=resumo_sinais(sinal([(0,.3,500)]))
        self.assertIn('não prova ausência de voz',nota)
        self.assertIn('não identifica palavras',nota)


class Integracao(unittest.IsolatedAsyncioTestCase):
    async def test_bipes_originais_chegam_com_medidas_sem_mudar_os_bytes(self):
        path=Path(__file__).resolve().parents[2]/'pesquisa/validacao/2026-10-15-midia/arquivos/tres-bipes.wav'
        raw=path.read_bytes();p=await decodificar(raw,'audio')
        self.assertIn('3 trecho(s)',p.nota)
        self.assertIn('660 Hz',p.nota)
        import base64
        with wave.open(io.BytesIO(raw)) as w: original=w.readframes(w.getnframes())
        with wave.open(io.BytesIO(base64.b64decode(p.partes[0]['inlineData']['data']))) as w:
            self.assertEqual(w.readframes(w.getnframes()),original)
        e=[{'role':'user','content':'sistema'},{'role':'user','content':'Qual o som?'}]
        p.aplicar(e)
        self.assertIn(AVISO_AUDIO,e[0]['content'])
        self.assertIn('3 trecho(s)',e[-1]['content'])

    async def test_fala_da_bateria_nao_recebe_classificacao_tonal(self):
        path=Path(__file__).resolve().parents[2]/'pesquisa/validacao/2026-10-15-midia/arquivos/fala.wav'
        p=await decodificar(path.read_bytes(),'audio')
        self.assertNotIn('Medição local',p.nota)
        self.assertTrue(p.partes)

    def test_imagens_e_texto_nao_recebem_instrucao_de_escuta(self):
        for p in (Preparo(),Preparo([{'inlineData':{'mimeType':'image/jpeg','data':'x'}}])):
            e=[{'role':'user','content':'sistema'},{'role':'user','content':'Oi'}]
            p.aplicar(e)
            self.assertNotIn(AVISO_AUDIO,e[0]['content'])
