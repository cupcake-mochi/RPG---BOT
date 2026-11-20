"""Atestado de ativação da cópia: lê o pulso, avalia e guarda. Sem endpoint.

Leitura só por pedido do jogador (abrir a tela ou conferir); nada em segundo
plano. Abrir a tela reaproveita a última leitura por até 5 min; conferir e
qualquer decisão que dependa do estado leem de novo. Nunca escreve no Google.
"""
from .atestado_ativacao import ATIVA, avaliar, ilegivel
from .copias_banco import ReferenciaCopia, hash_texto
from .leitor_pulso import ler
from .provedores import ErroProvedor
from .segredos import AcessoNegado, Conflito

TRAVA = 300


def _publico(d, reaproveitado):
    return dict(estado=d['estado'], codigo=d['codigo'], faltam=list(d['faltam']),
                lido_em=d['lido_em'], reaproveitado=reaproveitado)


async def conferir(servico, servidor, usuario, ref, *, forcar=False):
    if type(ref) is not ReferenciaCopia or (servidor, usuario) != (ref.servidor, ref.ator):
        raise AcessoNegado('Atestado pertence a outro contexto.')
    if type(forcar) is not bool:
        raise AcessoNegado('Pedido de atestado inválido.')
    b = servico._banco
    m = await servico._membro(servidor, usuario)
    arquivo, esperado = await b('contexto_atestado', m, ref)
    if not forcar:
        salvo = await b('atestado_salvo', m, ref)
        if salvo is not None and 0 <= servico.agora() - salvo['lido_em'] < TRAVA:
            return _publico(salvo, True)

    async def executar():
        m = await servico._membro(servidor, usuario)
        cred, token = await servico._renovar_google(m, ref, para_copia=True)

        async def contexto():
            atual = await b('contexto_atestado', await servico._membro(servidor, usuario), ref)
            if atual != (arquivo, esperado):
                raise Conflito('A cópia ou a autorização mudou enquanto o atestado aguardava.')
            if servico.agora() + 15 >= token.expira:
                raise ErroProvedor('expirado')

        await contexto()
        await servico.cotas.esperar(hash_texto(cred.conta))
        await contexto()
        pulsos, problema = await ler(servico.provedores, token.acesso, arquivo)
        await contexto()
        m = await servico._membro(servidor, usuario)
        salvo = await b('atestado_salvo', m, ref)
        agora = servico.agora()
        a = ilegivel(problema) if problema else avaliar(
            pulsos, operacao=ref.operacao, arquivo=arquivo, agora=agora,
            anterior=(salvo or {}).get('maximos') or None)
        return await b('registrar_atestado', m, ref, a, agora)

    d = await servico.fila.executar(('atestado_ativacao', ref.operacao), (servidor, usuario), executar,
                                    prazo=120, espera=180)
    return _publico(d, False)


async def exigir_ativa(servico, servidor, usuario, ref):
    """Portão do cadastro da cópia criada: sempre lê na hora, nunca usa a trava.

    Sem chamador nesta etapa: a criação continua bloqueada pelos demais critérios.
    """
    d = await conferir(servico, servidor, usuario, ref, forcar=True)
    if d['estado'] != ATIVA:
        raise Conflito('As automações da ficha ainda não foram vistas funcionando.')
    return d


async def recomecar(servico, servidor, usuario, ref):
    if type(ref) is not ReferenciaCopia or (servidor, usuario) != (ref.servidor, ref.ator):
        raise AcessoNegado('Atestado pertence a outro contexto.')
    m = await servico._membro(servidor, usuario)
    await servico._banco('recomecar_atestado', m, ref)
    return await conferir(servico, servidor, usuario, ref, forcar=True)
