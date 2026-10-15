"""Medições conservadoras de PCM mono 16 kHz; não classifica fala ou fontes."""
from array import array
import math
import sys

TAXA = 16000
JANELA = 320  # 20 ms; trabalho linear, no máximo 1500 janelas por anexo


def _tom(quadro):
    """Aceita só seno quase puro, após conferir cruzamentos e energia explicada."""
    media = sum(quadro) / len(quadro)
    sinal = [x - media for x in quadro]
    energia = sum(x*x for x in sinal)
    if energia < len(sinal):
        return None
    cruzamentos = [i - sinal[i] / (sinal[i+1] - sinal[i])
                   for i in range(len(sinal)-1) if sinal[i] <= 0 < sinal[i+1]]
    if len(cruzamentos) < 4:
        return None
    periodos = [b-a for a,b in zip(cruzamentos,cruzamentos[1:])]
    periodo = sum(periodos) / len(periodos)
    frequencia = TAXA / periodo
    if not 150 <= frequencia <= 3500 or max(abs(t-periodo) for t in periodos) > periodo*.025:
        return None
    # Projeção nos senos/cossenos: o sistema 2x2 também cobre janelas com
    # ciclos incompletos. Voz harmônica e ruído não bastam por ter uma altura.
    passo = math.tau * frequencia / TAXA
    seno = [math.sin(passo*i) for i in range(len(sinal))]
    cosseno = [math.cos(passo*i) for i in range(len(sinal))]
    ss=sum(x*x for x in seno); cc=sum(x*x for x in cosseno)
    sc=sum(x*y for x,y in zip(seno,cosseno))
    ys=sum(x*y for x,y in zip(sinal,seno)); yc=sum(x*y for x,y in zip(sinal,cosseno))
    det=ss*cc-sc*sc
    if det <= 0:
        return None
    a=(ys*cc-yc*sc)/det; b=(yc*ss-ys*sc)/det
    if (a*ys+b*yc)/energia < .985:
        return None
    return frequencia


def medir_tons(pcm: bytes) -> list[dict]:
    """Só relata trechos estáveis que explicam >=95% da energia do arquivo.

    Não significa ausência de voz ou silêncio entre trechos: essas conclusões
    não são produzidas aqui. Retorna vazio se a evidência for insuficiente.
    """
    if not pcm or len(pcm)%2 or len(pcm)>30*TAXA*2:
        return []
    amostras=array('h');amostras.frombytes(pcm)
    if sys.byteorder != 'little': amostras.byteswap()
    total=sum(x*x for x in amostras)
    if not total: return []
    trechos=[]; atual=None
    for inicio in range(0,len(amostras),JANELA):
        q=amostras[inicio:inicio+JANELA]
        freq=_tom(q) if len(q)==JANELA else None
        if freq is not None:
            if atual and inicio==atual['fim'] and abs(freq-atual['hz'])<=atual['hz']*.025:
                atual['fim']+=len(q);atual['energia']+=sum(x*x for x in q)
            else:
                atual={'inicio':inicio,'fim':inicio+len(q),'hz':freq,'energia':sum(x*x for x in q)}
                trechos.append(atual)
        else:
            atual=None
    trechos=[t for t in trechos if t['fim']-t['inicio'] >= TAXA*.08]
    # Não descreve arbitrariamente um áudio longo pela presença de um único
    # tom pequeno. Também evita enviar centenas de números ao prompt.
    if not trechos or len(trechos)>12 or sum(t['energia'] for t in trechos)/total<.95:
        return []
    return [{'inicio_s':round(t['inicio']/TAXA,2),'fim_s':round(t['fim']/TAXA,2),
             'frequencia_hz':round(t['hz'])} for t in trechos]


def resumo_sinais(pcm: bytes) -> str:
    trechos=medir_tons(pcm)
    if not trechos: return ''
    detalhes='; '.join(f"{t['inicio_s']:.2f}–{t['fim_s']:.2f} s, aproximadamente {t['frequencia_hz']} Hz" for t in trechos)
    return (f'Medição local do sinal: {len(trechos)} trecho(s) tonal(is) quase puro(s) e estável(is): {detalhes}. '
            'Limites aproximados de 20 ms; isto não identifica palavras, instrumento, objeto ou origem, '
            'não prova ausência de voz e não descreve o ambiente do canal.')
