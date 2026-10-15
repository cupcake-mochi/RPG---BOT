"""Comparação v16/v17: prepara sem API; execução só após aprovação de 24 chamadas."""
from __future__ import annotations
import argparse
import asyncio
import copy
from datetime import datetime
import fcntl
import hashlib
import io
import json
import math
from pathlib import Path
import random
import shutil
import struct
import sys
import wave

import bateria_midia as base
from closure_bot.midia import AVISO
from closure_bot.midia_anexos import decodificar
from closure_bot.modelo import FLASH, Modelos
from closure_bot.config import carregar
from closure_bot.registro import Registro
from closure_bot.prompt import montar
from closure_bot.plantao import FUSO
from closure_bot.vida import Estado

RAIZ=Path(__file__).resolve().parents[1]
PASTA=RAIZ/'pesquisa/validacao/2026-10-15-audio-v17'
TETO=1.50
CASOS=[
 ('tres-bipes.wav','Descreva esse som. Tem alguém falando?','Três tons separados; não inventar palavras, objeto ou ambiente.'),
 ('cinco-tons.wav','O que muda nesse áudio e quantos sons separados aparecem?','Cinco tons em alturas alternadas; contagem e pausas corretas, sem atribuir origem.'),
 ('acordes.wav','O que você ouve aqui?','Tons sobrepostos/acordes que mudam; não afirmar pessoa, instrumento específico ou gravação conhecida.'),
 ('ruido.wav','Pode descrever o áudio?','Ruído/chiado; não inventar fala nem atribuir uma fonte específica.'),
 ('fala-baixa.wav','Pode responder ao que eu disse no áudio?','Reconhecer conclusão do desenho e contentamento, sem inventar outro assunto.'),
 ('fala-ruido.wav','O que eu disse? Tem outro som junto?','Reconhecer desenho/contentamento e ruído de fundo; não inventar origem do ruído.')]


def gravar_wav(destino, amostras, taxa=16000):
 with wave.open(str(destino),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(taxa)
  w.writeframes(b''.join(struct.pack('<h',max(-32768,min(32767,int(x)))) for x in amostras))


def gerar():
 pasta=PASTA/'arquivos';pasta.mkdir(parents=True,exist_ok=True)
 origem=RAIZ/'pesquisa/validacao/2026-10-15-midia/arquivos'
 shutil.copyfile(origem/'tres-bipes.wav',pasta/'tres-bipes.wav')
 gravar_wav(pasta/'cinco-tons.wav',[6000*math.sin(math.tau*(440 if int(i/4800)%2==0 else 880)*i/16000)
     if i<5*4800 and i%4800<3200 else 0 for i in range(32000)])
 acordes=[(220,275,330),(260,325,390),(300,375,450)]
 gravar_wav(pasta/'acordes.wav',[sum(2000*math.sin(math.tau*f*i/16000) for f in acordes[i//16000]) for i in range(48000)])
 rng=random.Random(17015)
 gravar_wav(pasta/'ruido.wav',[rng.randint(-6000,6000) for _ in range(48000)])
 with wave.open(str(origem/'fala.wav')) as w:
  taxa=w.getframerate();raw=w.readframes(w.getnframes())
 voz=[v[0] for v in struct.iter_unpack('<h',raw)]
 gravar_wav(pasta/'fala-baixa.wav',[x*.08 for x in voz],taxa)
 gravar_wav(pasta/'fala-ruido.wav',[x+rng.randint(-1200,1200) for x in voz],taxa)


async def preparar():
 gerar();casos=[];pedidos={}
 anterior=json.loads((PASTA/'base-v16.json').read_text())['aviso']
 for arq,texto,criterio in CASOS:
  raw=(PASTA/'arquivos'/arq).read_bytes();p=await decodificar(raw,'audio')
  assert p.partes and not p.silencio
  for persona,hora in [('closure',22),('kaltsit',14)]:
   estado=Estado(persona,datetime(2026,10,15,hora,10,tzinfo=FUSO),'quieto',0,'Alex',None,0,0,3,())
   comum=await montar(persona,texto,nome='Alex',pronomes=None,turnos=[],falas_anteriores=[],estado=estado.para_a_ponte())
   for variante in ('v16','v17'):
    e=copy.deepcopy(comum)
    if variante=='v17': p.aplicar(e)
    else:
     # Mesmo áudio normalizado; só nota de duração e aviso da versão anterior.
     e[0]['content']=e[0]['content'].replace(AVISO,anterior) if AVISO in e[0]['content'] else e[0]['content']+'\n\n'+anterior
     e[-1]['content']+='\n\n[Mídia deste turno] '+p.nota.split('; Medição local')[0]
     e[-1]['midias']=copy.deepcopy(p.partes)
    ident=persona+'_'+Path(arq).stem+'_'+variante;pedidos[ident]=e
    casos.append({'id':ident,'persona':persona,'variante':variante,'arquivo':arq,'mensagem':texto,'criterio':criterio,
       'arquivo_sha256':hashlib.sha256(raw).hexdigest(),'pedido_sha256':base.digest(e),'reserva_cheia_usd':base.reserva(e)})
 arquivos=['src/closure_bot/audio_sinais.py','src/closure_bot/midia_anexos.py','src/closure_bot/midia_preparar.py',
           'src/closure_bot/modelo.py','src/closure_bot/prompt.py','src/var/site/nucleo.js',
           'ferramentas/bateria_audio_v17.py','ferramentas/bateria_midia.py']
 plano={'modelo':FLASH,'esforco':'low','chamadas_maximas':24,'teto_cheio_usd':TETO,'casos':casos,
   'repetir':False,'fallback':False,'fontes_sha256':{n:hashlib.sha256((RAIZ/n).read_bytes()).hexdigest() for n in arquivos}}
 return plano,pedidos


async def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--executar',action='store_true')
 ap.add_argument('--orcamento-extra-aprovado',action='store_true');args=ap.parse_args()
 plano,pedidos=await preparar();dest=PASTA/'plano.json'
 if dest.exists() and json.loads(dest.read_text())!=plano:raise ValueError('Plano alterado; revisar antes de substituir')
 base.gravar(dest,plano)
 base.gravar(PASTA/'prompts.json',{k:[{kk:vv for kk,vv in m.items() if kk!='midias'} for m in v] for k,v in pedidos.items()})
 if not args.executar:
  print('Sem API. Chamadas:',len(pedidos),'soma das reservas cheias:',sum(c['reserva_cheia_usd'] for c in plano['casos']))
  return 0
 if not args.orcamento_extra_aprovado:raise ValueError('Exige nova aprovação de quantidade/custo')
 cfg=carregar()
 if not cfg.chaves.get('vertex') or not cfg.vertex_projeto:raise ValueError('Falta rota global Vertex')
 reg=Registro(cfg.banco,cfg.chave_do_banco)
 try:
  modelos=Modelos([('vertex',FLASH)],cfg.chaves,reg,raciocinio='low',vertex_projeto=cfg.vertex_projeto,
                  teto_preco='cheio',gasto_externo_usd=cfg.gasto_externo_usd)
  modelos.teto_usd=max(modelos.teto_usd,modelos.gasto_do_mes()+TETO)
  with (PASTA/'.execucao.lock').open('a') as trava:
   fcntl.flock(trava,fcntl.LOCK_EX|fcntl.LOCK_NB)
   return await base.executar(plano,pedidos,modelos,PASTA)
 finally:reg.fechar()

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
