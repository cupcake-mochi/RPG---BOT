"""Cópia interna com diário. Não limpa nem entrega um personagem novo."""
from .copias_google import enviar, procurar, observar, PRAZO_JOB_COPIA
from .segredos import Conflito
from .copias_banco import hash_texto
from .equivalencia_versao import impressao, provar
from .grade_inicializacao import LeitorGradeRest
from .observacoes_copia import ObservacaoVersao


async def copiar(servico, servidor, usuario, *, conexao, modelo, pedido):
    b = servico._banco
    membro = await servico._membro(servidor, usuario)
    ref = await b('preparar_copia_modelo', membro, conexao=conexao, modelo=modelo, pedido=pedido)

    async def executar():
        m = await servico._membro(servidor, usuario)
        inicial = await b('contexto_copia', m, ref)
        if inicial['estado'] != 'preparada' and inicial['versao_origem'] is None:
            raise Conflito('A versão da origem não ficou registrada. Não identifique ou reenvie esta cópia.')
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

        async def observar_arquivo(p, acesso, arquivo):
            return await p.observar_arquivo(acesso, arquivo)

        async def obs(arquivo):
            return await rede(observar_arquivo, arquivo)

        async def revalidar():
            # Contexto estável desta operação para o leitor; o banco é reconferido em contexto().
            await contexto()
            return hash_texto('impressao_copia:' + ref.operacao + ':' + cred.conta)

        async def cota():
            await servico.cotas.esperar(hash_texto(cred.conta))

        async def medir_impressao(arquivo):
            leitor = LeitorGradeRest(servico.provedores, revalidar, cota, agrupar=True)
            return await impressao(leitor, obs, token.acesso, arquivo)

        async def conferir_origem(etapa):
            m, d = await contexto()
            v, mod = await obs(d['origem'])
            m, d = await contexto()
            esperada = d['versao_origem'] if d['estado'] != 'preparada' else (
                d['versao_origem'] or d['versao_configurada'])
            await b('registrar_observacao_copia', m, ref, ObservacaoVersao(etapa, esperada, v))
            if esperada is not None and v != esperada:
                async def registrar(imp):
                    m2, _ = await contexto()
                    await b('registrar_equivalencia_copia', m2, ref, 'origem', imp)
                    await b('registrar_observacao_copia', m2, ref, ObservacaoVersao('origem_equivalente', esperada, v))
                if d['estado'] == 'preparada' or not await provar(
                        d, 'origem', v, mod, lambda: medir_impressao(d['origem']), registrar):
                    raise Conflito('O modelo mudou durante a cópia. Não inicialize esse arquivo.')
            return v, mod

        m, d = await contexto()
        if d['estado'] == 'preparada':
            v, _ = await conferir_origem('origem_antes_copia')
            # Referência de conteúdo da origem antes do POST (versão e modifiedTime estáveis).
            ref_origem = await medir_impressao(d['origem'])
            if ref_origem.versao != v:
                raise Conflito('O modelo mudou durante a cópia. Não inicialize esse arquivo.')
            m, d = await contexto()
            await b('fixar_versao_copia', m, ref, v, ref_origem)
            # A cota e as permissões vêm antes da transação que arma o envio.
            await servico.cotas.esperar(hash_texto(cred.conta))
            m, d = await contexto()
            armado = await b('armar_envio_copia', m, ref)
            if armado:
                # Reconferir após a transação assíncrona: desconexão ou expiração
                # nesse intervalo impede o POST, mas não rearma o envio durável.
                await contexto()
                arquivo = await enviar(servico.provedores, token.acesso, ref.operacao, d['origem'])
                await contexto()
            else:
                arquivo = await rede(procurar, ref.operacao, d['origem'])
        elif d['estado'] == 'enviada':
            await conferir_origem('origem_antes_localizar')
            arquivo = await rede(procurar, ref.operacao, d['origem'])
        else:
            await conferir_origem('origem_antes_localizar')
            arquivo = d['destino']
        destino = await rede(observar, ref.operacao, d['origem'], arquivo)
        m, d = await contexto()
        esperada = d['versao_destino'] if d['estado'] == 'identificada' else (
            d.get('candidata') or {}).get('versao')
        await b('registrar_observacao_copia', m, ref, ObservacaoVersao('copia_candidata', esperada, destino.versao))
        if d['estado'] == 'enviada':
            await b('registrar_candidata_copia', m, ref, destino)
        await conferir_origem('origem_apos_candidata')
        final = await rede(observar, ref.operacao, d['origem'], arquivo)
        m, d = await contexto()
        await b('registrar_observacao_copia', m, ref, ObservacaoVersao(
            'copia_apos_origem', destino.versao, final.versao))
        if final.versao != destino.versao and (final.modificado is None or final.modificado != destino.modificado):
            raise Conflito('A candidata mudou durante a conferência da origem. Não inicialize esse arquivo.')
        ref_destino = None
        if d['estado'] == 'enviada':
            # Referência de conteúdo da cópia, da versão que será identificada.
            ref_destino = await medir_impressao(arquivo)
            if (ref_destino.versao, ref_destino.modificado) != (final.versao, final.modificado):
                raise Conflito('A candidata mudou durante a conferência da origem. Não inicialize esse arquivo.')
        m, d = await contexto()
        return await b('registrar_destino_copia', m, ref, final, ref_destino)

    return await servico.fila.executar(('copia_modelo', ref.operacao), (servidor, usuario), executar,
                                       prazo=PRAZO_JOB_COPIA, espera=PRAZO_JOB_COPIA + 90)
