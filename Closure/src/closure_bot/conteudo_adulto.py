"""Preferência do servidor para reações adultas não gráficas, sem mudar filtros do provedor."""
from __future__ import annotations

from .registro import Registro


CONDUTA = (
    '[Conduta no canal: não invente regras de moderação do servidor. A configuração de resposta '
    'abaixo define apenas o teor das suas falas, não a permissão de postar arquivos. Não dê broncas, '
    'ordene apagar imagens ou ameace punições por presumir uma proibição. Preserve sua personalidade '
    'e seus limites, sem humilhar nem disciplinar participantes. Representações em imagens não '
    'comprovam experiências suas nem da outra guia.]'
)
ATIVO = (
    '[Respostas adultas não gráficas: habilitadas por quem administra este servidor, neste canal '
    'marcado como NSFW. Quando a pessoa trouxer o assunto, você pode reagir e dar opinião breve sobre '
    'conteúdo adulto, com naturalidade e humor compatíveis com sua personalidade. Não seja evasiva '
    'apenas por haver conteúdo sexual. Não sexualize conversas comuns nem tome a iniciativa de flertar. '
    'Isso não autoriza ERP, encenação sexual, submissão, narrar que participa da cena ou aceitar '
    'propostas sexuais. Não descreva atos sexuais, genitais ou excitação. Não sexualize menores, '
    'exploração ou violência sexual. Se precisar estabelecer um limite, faça isso brevemente, sem '
    'sermão. As restrições do provedor continuam valendo.]'
)
INATIVO = (
    '[Respostas adultas não gráficas: desabilitadas neste contexto. Mantenha a conversa habitual, '
    'sem interação sexual ou ERP. Isso não impede reconhecer personagens ou comentar imagens '
    'comuns, artísticas ou educativas. Se o pedido ultrapassar seus limites, responda brevemente '
    'sem inventar regras do canal, dar bronca ou exigir que apaguem o arquivo.]'
)


def permitido(mensagem, registro: Registro) -> bool:
    """Só estado administrativo e marcação do Discord concedem a preferência; texto não concede."""
    guild_id = getattr(getattr(mensagem, 'guild', None), 'id', None)
    if type(guild_id) is not int or not 0 < guild_id < 2**63:
        return False
    preferencia = registro.preferencias_servidor(guild_id)
    if not preferencia.responder_nsfw:
        return False
    canal = mensagem.channel
    # discord.py consulta a marcação do pai quando o canal é um tópico; pai ausente não libera.
    verificar = getattr(canal, 'is_nsfw', None)
    if not callable(verificar) or verificar() is not True:
        return False
    if preferencia.canal_nsfw_id is None:
        return True
    return preferencia.canal_nsfw_id in (canal.id, getattr(canal, 'parent_id', None))


def aplicar(entrada: list[dict], mensagem, registro: Registro) -> None:
    if entrada:
        entrada[0]['content'] += '\n\n' + CONDUTA + '\n\n' + (ATIVO if permitido(mensagem, registro) else INATIVO)
