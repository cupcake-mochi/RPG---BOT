"""Duas observações estritas, só de leitura, sem endpoint ou alteração de recibo."""
import copy

from .copias_banco import ReferenciaCopia, hash_texto
from .copias_google import observar, observar_fonte_diagnostico
from .diagnostico_grade import DiagnosticoGrade
from .grade_inicializacao import LeitorGradeRest
from .provedores import ErroProvedor
from .segredos import AcessoNegado, Conflito, ErroCarteira


async def diagnosticar(servico, servidor, usuario, ref, *, alvo, dominio):
    if type(ref) is not ReferenciaCopia or (servidor, usuario) != (ref.servidor, ref.ator):
        raise AcessoNegado('Diagnóstico pertence a outro contexto.')
    if type(dominio) is not str or dominio not in ('financeiro', 'progressao'):
        raise ErroCarteira('Escolha financeiro ou progressão para o diagnóstico.')
    if type(alvo) is not str or alvo not in ('origem', 'copia'):
        raise ErroCarteira('Escolha origem ou cópia para o diagnóstico.')
    b = servico._banco

    async def conferir_contexto():
        observado = None

        async def provar(m):
            nonlocal observado
            # Só o dono da conexão/operação pode ler. O banco prova isso com
            # o membro recém-observado; admin não é caminho alternativo aqui.
            observado = await b('contexto_diagnostico_copia', m, ref, alvo)
            return True

        m = await servico.provedores.membro_para_leitura(servidor, usuario, provar)
        return m, observado

    _, esperado = await conferir_contexto()

    async def executar():
        m, atual = await conferir_contexto()
        if atual != esperado:
            raise Conflito('O contexto mudou enquanto o diagnóstico aguardava.')
        arquivo, chave = esperado
        origem = (await b('contexto_copia', m, ref))['origem']
        cred, token = await servico._renovar_google(m, ref, para_copia=True)

        async def contexto():
            _, atual = await conferir_contexto()
            if atual != esperado:
                raise Conflito('A operação ou a autorização do diagnóstico mudou.')
            if servico.agora()+15 >= token.expira:
                raise ErroProvedor('expirado')
            return chave

        async def cota():
            await servico.cotas.esperar(hash_texto(cred.conta))

        async def privado():
            await contexto(); await cota(); await contexto()
            if alvo == 'origem':
                versao = await observar_fonte_diagnostico(servico.provedores, token.acesso, arquivo)
            else:
                v = await observar(servico.provedores, token.acesso, ref.operacao, origem, arquivo)
                versao = v.versao
            await contexto()
            return versao

        # Sem cache, retry de estabilidade, persistência ou comparação com a
        # versão do recibo. Ler uma versão nova aqui não a autoriza para escrita.
        d = DiagnosticoGrade()
        leitor = LeitorGradeRest(servico.provedores, contexto, cota)
        mudancas_antes, mudancas_apos = [], []
        try:
            for _ in range(2):
                antes = await privado()
                plano = await leitor.abrir(token.acesso, arquivo, dominio)
                mudancas_antes.append(antes != plano.versao)
                await d.observar(leitor, token.acesso, plano)
                mudancas_apos.append(await privado() != plano.versao)
            await contexto()
            resultado = d.comparar()
            resultado['versao_mudou_antes_coleta'] = mudancas_antes
            resultado['versao_mudou_apos_coleta'] = mudancas_apos
            return resultado
        finally:
            d.fechar()

    resultado = await servico.fila.executar(
        ('diagnostico_grade', ref.operacao, alvo, dominio, esperado[1]),
        (servidor, usuario), executar, prazo=1200, espera=1290)
    # Mesmo os clientes coalescidos reconferem acesso depois da fila. Cada um
    # recebe sua própria cópia do resumo, nunca o objeto partilhado pelo job.
    _, atual = await conferir_contexto()
    if atual != esperado:
        raise Conflito('O contexto mudou antes de entregar o diagnóstico.')
    return copy.deepcopy(resultado)
