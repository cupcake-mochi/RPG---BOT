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
from .provedores import ErroProvedor, VersaoAlterada
from .observacoes_copia import ObservacaoVersao
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

        async def registrar(etapa, esperada, observada):
            atual = await servico._membro(servidor, usuario)
            await b('registrar_observacao_copia', atual, ref, ObservacaoVersao(etapa, esperada, observada))

        async def destino(etapa='copia_antes_grade'):
            r = await rede(observar, servico.provedores, token.acesso, ref.operacao,
                           copia['origem'], copia['destino'])
            await registrar(etapa, copia['versao_destino'], r.versao)
            return r

        async def origem():
            v = await rede(servico.provedores.versao_arquivo, token.acesso, copia['origem'])
            await registrar('origem_financeiro', copia['versao_origem'], v)
            if v != copia['versao_origem']:
                raise Conflito('O modelo mudou depois da cópia.')

        async def medir_copia():
            try:
                # Lotes validados no Google real (individual × agrupado iguais, 29/10).
                return await medir(LeitorGradeRest(servico.provedores, contexto, cota, agrupar=True),
                                   token.acesso, copia['destino'])
            except VersaoAlterada as exc:
                await registrar('copia_leitura', exc.esperada, exc.observada)
                raise

        await contexto()
        await origem()
        primeira = await destino()
        m = await servico._membro(servidor, usuario)
        estado = await b('estado_financeiro', m, ref)
        if (estado is None or estado['estado'] == 'preparada') and primeira.versao != copia['versao_destino']:
            raise Conflito('A cópia mudou desde a identificação. Não inicialize esse arquivo.')
        if estado is None:
            plano = await medir_copia()
            m = await servico._membro(servidor, usuario)
            estado = await b('preparar_financeiro', m, ref, plano)
        if estado['estado'] == 'preparada':
            await origem()
            # A espera da escrita vem antes da última observação do destino.
            # Esperar depois dela usaria uma versão potencialmente envelhecida.
            await cota(); await contexto()
            observado = await destino('copia_antes_envio')
            m = await servico._membro(servidor, usuario)
            envio = await b('armar_financeiro', m, ref, observado.versao)
            if envio is not None:
                # O diário já está enviada. Qualquer erro/cancelamento não autoriza retry.
                await enviar(servico.provedores, token.acesso, envio)
                await contexto()
        await destino()
        atual = await medir_copia()
        await origem()
        fechamento = await destino('copia_fechamento')
        if fechamento.versao != atual.versao:
            raise Conflito('A cópia mudou após a leitura. Não registre a conferência nem repita a escrita.')
        m = await servico._membro(servidor, usuario)
        return await b('registrar_financeiro', m, ref, atual)

    return await servico.fila.executar(('financeiro_celulas', ref.operacao), (servidor, usuario), executar,
                                      prazo=1200, espera=1290)
