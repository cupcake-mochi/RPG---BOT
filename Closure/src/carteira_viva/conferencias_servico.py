"""Conferência privada de fontes cadastradas, na fila e OAuth do serviço.

Não cria cópias, não escreve no Google e não oferece rota/comando público.
"""
from .banco import digest
from .conferencias_banco import conferir_dominio_persistido
from .provedores import ErroProvedor
from .segredos import AcessoNegado, Conflito, ErroCarteira

PRAZO = 1200
ESPERA = 1290


async def conferir(servico, servidor, usuario, personagem, *, retomar=False):
    if type(retomar) is not bool:
        raise ErroCarteira('Escolha de retomada inválida.')
    b = servico._banco
    membro, fonte = await servico._contexto(servidor, usuario, personagem)
    anterior = await b('retomar_conferencia_rest', membro, personagem) if retomar else None
    chave = ('conferencia_rest', usuario, anterior.operacao if anterior else 'nova') + fonte

    async def executar():
        membro, atual = await servico._contexto(servidor, usuario, personagem)
        if atual != fonte:
            raise Conflito('A fonte ou a autorização mudou enquanto aguardava a fila.')
        if anterior:
            bilhete = await b('retomar_conferencia_rest', membro, personagem)
            if bilhete.operacao != anterior.operacao:
                raise Conflito('Outra operação substituiu esta conferência.')
            ref, contexto, versao, restantes = await b('contexto_operacao_rest', membro, bilhete)
        else:
            ref = await b('reservar_conferencia_rest', membro, personagem)
            bilhete = None
            contexto = await b('contexto_conferencia_rest', membro, ref)
        cred, token = await servico._renovar_google(membro, ref)

        async def validar_contexto(m):
            if bilhete is None:
                observado = await b('contexto_conferencia_rest', m, ref)
            else:
                _, observado, _, _ = await b('contexto_operacao_rest', m, bilhete)
            if observado != contexto:
                raise Conflito('O contexto mudou durante a conferência.')
            if servico.agora() + 15 >= token.expira:
                # Retomada renova novamente; não gravar um domínio incompleto.
                raise ErroProvedor('expirado')
            return observado

        async def confirmar_basico(m):
            try:
                await validar_contexto(m)
            except AcessoNegado:
                # Pode ter acesso por Administrator/dono do servidor; esses
                # privilégios precisam da observação completa, nunca de suposição.
                return False
            return True

        async def revalidar():
            # GET novo do membro em cada contexto. O banco prova se os cargos
            # atuais/dono da ficha bastam; não é TTL nem cache de autorização.
            m = await servico.provedores.membro_para_leitura(servidor, usuario, confirmar_basico)
            return await validar_contexto(m)

        async def cota():
            await servico.cotas.esperar(digest(cred.conta))

        async def observar_versao():
            await revalidar()
            await cota()
            await revalidar()  # Acesso pode mudar enquanto a cota aguarda.
            v = await servico.provedores.versao_arquivo(token.acesso, ref.arquivo)
            await revalidar()
            return v

        if bilhete is None:
            versao = await observar_versao()
            membro = await servico._membro(servidor, usuario)
            bilhete = await b('iniciar_conferencia_rest', membro, ref, versao_drive=versao)
            _, contexto, _, restantes = await b('contexto_operacao_rest', membro, bilhete)
        else:
            # Inclusive se os dois domínios já foram salvos antes da interrupção.
            if await observar_versao() != versao:
                raise Conflito('A versão do arquivo mudou. Não continue esta conferência.')

        for _ in restantes:
            await revalidar()
            membro = await servico._membro(servidor, usuario)
            bilhete = await conferir_dominio_persistido(servico.dados, membro, bilhete,
                servico.provedores, token.acesso, revalidar_contexto=revalidar, aguardar_cota=cota)
        await revalidar()
        return bilhete

    bilhete = await servico.fila.executar(chave, (servidor, usuario), executar, prazo=PRAZO, espera=ESPERA)
    membro = await servico._membro(servidor, usuario)
    # Cada cliente coalescido abre sua própria cópia privada e revalida o acesso.
    return await b('resultado_conferencia_rest', membro, bilhete)
