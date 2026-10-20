"""Fluxos de clima reais, saída Discord capturada localmente, sem modelo/token/banco."""
import asyncio
import sys
from types import SimpleNamespace
sys.path.insert(0, 'src')
from closure_bot.clima import ServicoClima, contexto_clima, pergunta_clima
from closure_bot.cogs.clima import ComandoClima
from closure_bot.cogs.atalho import Atalho

class CanalLocal:
    def __init__(self):
        self.saidas = []
    async def send(self, texto=None, **kwargs):
        self.saidas.append((texto, kwargs))
        anexo = kwargs.get('file')
        if anexo:
            anexo.close()

async def main():
    servico = ServicoClima()
    anterior = None
    total = 0
    for texto, cidade in [('Closure, qual o clima atual de SP?', 'São Paulo'),
                          ('E de BH?', 'Belo Horizonte'), ('E em Curitiba?', 'Curitiba')]:
        linha = await contexto_clima(servico, texto, anterior)
        assert linha and linha.startswith('[' + cidade), (texto, linha)
        anterior = pergunta_clima(texto, anterior)
        total += 1
        print('PASS conversa:', texto, '->', linha, flush=True)
    anterior = pergunta_clima('Agora explica Maestria', anterior)
    assert anterior is None
    total += 1
    print('PASS troca de assunto encerra clima', flush=True)
    assert await contexto_clima(servico, 'E de BH?', anterior) is None
    total += 1
    print('PASS continuação sem assunto não dispara consulta', flush=True)
    clima = ComandoClima(SimpleNamespace(clima=servico))
    atalho = Atalho(SimpleNamespace(get_cog=lambda nome: clima if nome == 'ComandoClima' else None))
    canal = CanalLocal()
    for texto, cidade in [
        ('GC:clima E como tá o clima de Belo Horizonte?', 'Belo Horizonte'),
        ('GC:clima E de BH?', 'Belo Horizonte'), ('GC:clima BH', 'Belo Horizonte'),
        ('GC:clima qual o clima atual de SP?', 'São Paulo'),
    ]:
        mensagem = SimpleNamespace(content=texto, author=SimpleNamespace(bot=False), webhook_id=None,
                                   guild=object(), channel=canal)
        await atalho.on_message(mensagem)
        embed = canal.saidas[-1][1].get('embed')
        assert embed and cidade in embed.title, (texto, canal.saidas[-1][0])
        total += 1
        print('PASS comando:', texto, '->', embed.title, flush=True)
    embed, aviso = await clima.consultar('E como tá o clima de BH?')
    assert embed and 'Belo Horizonte' in embed.title and aviso is None
    total += 1
    print('PASS mesmo argumento na consulta do comando de barra', flush=True)
    embed, aviso = await clima.consultar('qual o clima atual de Xyzabcqq?')
    assert embed is None and 'Não achei' in aviso
    total += 1
    print('PASS cidade inexistente não vira Tóquio', flush=True)
    assert total == 11
    print('RESULTADO: 11/11; dados reais; comandos com saída local; nenhum modelo ou envio ao Discord', flush=True)
asyncio.run(main())
