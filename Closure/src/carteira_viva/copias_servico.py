"""Cópia interna com diário. Não limpa nem entrega um personagem novo."""
from .copias_google import enviar, procurar, observar
from .segredos import Conflito
from .copias_banco import hash_texto


async def copiar(servico, servidor, usuario, *, conexao, modelo, pedido):
    b = servico._banco
    membro = await servico._membro(servidor, usuario)
    ref = await b('preparar_copia_modelo', membro, conexao=conexao, modelo=modelo, pedido=pedido)

    async def executar():
        m = await servico._membro(servidor, usuario)
        await b('contexto_copia', m, ref)
        cred, token = await servico._renovar_google(m, ref, para_copia=True)

        async def contexto():
            m = await servico._membro(servidor, usuario)
            if servico.agora() + 15 >= token.expira:
                from .provedores import ErroProvedor
                raise ErroProvedor('expirado')
            return m, await b('contexto_copia', m, ref)

        async def rede(funcao, *args):
            await contexto()
            await servico.cotas.esperar(hash_texto(cred.conta))
            await contexto()
            r = await funcao(servico.provedores, token.acesso, *args)
            await contexto()
            return r

        async def versao(p, acesso, origem):
            return await p.versao_arquivo(acesso, origem)

        m, d = await contexto()
        if d['estado'] == 'preparada':
            v = await rede(versao, d['origem'])
            m, d = await contexto()
            await b('fixar_versao_copia', m, ref, v)
            # A cota e as permissões vêm antes da transação que arma o envio.
            await servico.cotas.esperar(hash_texto(cred.conta))
            m, d = await contexto()
            armado = await b('armar_envio_copia', m, ref)
            if armado:
                arquivo = await enviar(servico.provedores, token.acesso, ref.operacao, d['origem'])
                await contexto()
            else:
                arquivo = await rede(procurar, ref.operacao, d['origem'])
        elif d['estado'] == 'enviada':
            arquivo = await rede(procurar, ref.operacao, d['origem'])
        else:
            arquivo = d['destino']
        destino = await rede(observar, ref.operacao, d['origem'], arquivo)
        v = await rede(versao, d['origem'])
        m, d = await contexto()
        if v != d['versao_origem']:
            raise Conflito('O modelo mudou durante a cópia. Não inicialize esse arquivo.')
        return await b('registrar_destino_copia', m, ref, destino)

    return await servico.fila.executar(('copia_modelo', ref.operacao), (servidor, usuario), executar)
