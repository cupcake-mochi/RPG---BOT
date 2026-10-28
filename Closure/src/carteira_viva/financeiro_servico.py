"""Células financeiras de cópia nova: um envio, depois somente reconciliação.

Sem rota pública. Não inicializa PropertiesService nem libera criação. A API
Sheets não oferece aqui compare-and-swap contra uma edição simultânea do dono;
essa limitação continua bloqueando a liberação pública da criação.
"""
from .copias_banco import ReferenciaCopia, hash_texto
from .copias_google import observar
from .financeiro_google import enviar
from .financeiro_plano import medir
from .grade_inicializacao import LeitorGradeRest
from .provedores import ErroProvedor
from .segredos import AcessoNegado, Conflito


async def inicializar(servico, servidor, usuario, ref):
    if type(ref) is not ReferenciaCopia or (servidor, usuario) != (ref.servidor, ref.ator):
        raise AcessoNegado('Inicialização pertence a outro contexto.')
    b = servico._banco

    async def executar():
        m = await servico._membro(servidor, usuario)
        copia, esperado = await b('contexto_financeiro', m, ref)
        cred, token = await servico._renovar_google(m, ref, para_copia=True)

        async def contexto():
            m = await servico._membro(servidor, usuario)
            _, atual = await b('contexto_financeiro', m, ref)
            if atual != esperado:
                raise Conflito('O contexto da cópia mudou.')
            if servico.agora()+15 >= token.expira:
                raise ErroProvedor('expirado')
            return esperado

        async def cota():
            await servico.cotas.esperar(hash_texto(cred.conta))

        async def rede(fn, *args):
            await contexto(); await cota(); await contexto()
            r = await fn(*args)
            await contexto()
            return r

        async def destino():
            return await rede(observar, servico.provedores, token.acesso, ref.operacao,
                              copia['origem'], copia['destino'])

        async def origem():
            v = await rede(servico.provedores.versao_arquivo, token.acesso, copia['origem'])
            if v != copia['versao_origem']:
                raise Conflito('O modelo mudou depois da cópia.')

        await contexto()
        await origem()
        await destino()
        m = await servico._membro(servidor, usuario)
        estado = await b('estado_financeiro', m, ref)
        if estado is None:
            leitor = LeitorGradeRest(servico.provedores, contexto, cota)
            plano = await medir(leitor, token.acesso, copia['destino'])
            m = await servico._membro(servidor, usuario)
            estado = await b('preparar_financeiro', m, ref, plano)
        if estado['estado'] == 'preparada':
            await origem()
            # A espera da escrita vem antes da última observação do destino.
            # Esperar depois dela usaria uma versão potencialmente envelhecida.
            await cota(); await contexto()
            observado = await destino()
            m = await servico._membro(servidor, usuario)
            envio = await b('armar_financeiro', m, ref, observado.versao)
            if envio is not None:
                # O diário já está enviada. Qualquer erro/cancelamento não autoriza retry.
                await enviar(servico.provedores, token.acesso, envio)
                await contexto()
        await destino()
        leitor = LeitorGradeRest(servico.provedores, contexto, cota)
        atual = await medir(leitor, token.acesso, copia['destino'])
        await origem()
        fechamento = await destino()
        if fechamento.versao != atual.versao:
            raise Conflito('A cópia mudou após a leitura. Não registre a conferência nem repita a escrita.')
        m = await servico._membro(servidor, usuario)
        return await b('registrar_financeiro', m, ref, atual)

    return await servico.fila.executar(('financeiro_celulas', ref.operacao), (servidor, usuario), executar,
                                      prazo=1200, espera=1290)
