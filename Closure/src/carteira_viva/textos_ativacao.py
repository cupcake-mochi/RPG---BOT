"""Textos PT/EN do passo de ativação para a futura tela de criação.

Sem comando ou rota nesta etapa: a criação continua bloqueada. A tela
"Ativar automações" entra no fluxo de criação logo depois da cópia
inicializada (requisito registrado em docs/carteira-viva/ETAPA-7.md).
"""
from .atestado_ativacao import CODIGOS
from .segredos import ErroCarteira

ESTADOS = {
    'nao_ativada': ('Automações não ativadas', 'Automations not activated'),
    'aguardando': ('Ativação em andamento', 'Activation in progress'),
    'ativa': ('Automações funcionando', 'Automations working'),
    'parada': ('Automações paradas', 'Automations stopped'),
    'inconsistente': ('Ativação precisa de revisão', 'Activation needs review'),
}

FALTAM = {
    'diario': ('esperar a rotina diária das 3h (horário de Brasília)', 'wait for the daily 3 AM routine (Brasília time)'),
    'abertura': ('abrir a ficha uma vez', 'open the sheet once'),
    'edicao': ('editar qualquer campo da ficha uma vez', 'edit any field of the sheet once'),
}

MOTIVOS = {
    'sem_pulso': ('A ficha ainda não registrou nenhuma automação. Ative as automações na ficha.',
                  'The sheet has not recorded any automation yet. Activate the automations in the sheet.'),
    'outra_operacao': ('Esta ficha registra a ativação de outra criação. Ative as automações de novo nesta ficha.',
                       'This sheet records the activation of another creation. Activate the automations again in this sheet.'),
    'copia_de_outra_ficha': ('Esta planilha é uma cópia de outra ficha. Cópias não levam as automações: ative-as nesta planilha.',
                             'This spreadsheet is a copy of another sheet. Copies do not carry the automations: activate them in this one.'),
    'horario_futuro': ('A ficha registrou um horário no futuro. Confira o fuso e ative as automações de novo.',
                       'The sheet recorded a time in the future. Check the time zone and activate the automations again.'),
    'sequencia_repetida': ('Uma automação parece instalada duas vezes. Ative as automações de novo pela ficha.',
                           'An automation seems to be installed twice. Activate the automations again from the sheet.'),
    'fora_de_ordem': ('O registro das automações está fora de ordem. Ative as automações de novo pela ficha.',
                      'The automation record is out of order. Activate the automations again from the sheet.'),
    'contador_voltou': ('O registro das automações voltou para um ponto anterior. Se você restaurou uma versão antiga da ficha no Google, confirme para recomeçar a contagem.',
                        'The automation record went back to an earlier point. If you restored an older version of the sheet in Google, confirm to restart the count.'),
    'diario_atrasado': ('A rotina diária não roda há mais de 26 horas. Ative as automações de novo na ficha.',
                        'The daily routine has not run for more than 26 hours. Activate the automations again in the sheet.'),
    'diario_nunca_rodou': ('A rotina diária nunca rodou desde a ativação. Ative as automações de novo na ficha.',
                           'The daily routine never ran since activation. Activate the automations again in the sheet.'),
    'ativa': ('As três automações foram vistas funcionando.', 'All three automations were seen working.'),
    'pulso_ilegivel': ('O registro das automações na ficha está ilegível. Ative as automações de novo pela ficha.',
                       'The automation record in the sheet is unreadable. Activate the automations again from the sheet.'),
    'pulso_duplicado': ('O registro das automações aparece duplicado na ficha. Ative as automações de novo pela ficha.',
                        'The automation record appears twice in the sheet. Activate the automations again from the sheet.'),
}

PASSOS = (
    ('Ative as automações na ficha. O Google vai pedir autorização na sua conta.',
     'Activate the automations in the sheet. Google will ask for authorization on your account.'),
    ('Depois de ativar, abra a ficha e edite qualquer campo uma vez.',
     'After activating, open the sheet and edit any field once.'),
    ('Espere a rotina diária das 3h (horário de Brasília). A ficha só fica ativa depois dela.',
     'Wait for the daily 3 AM routine (Brasília time). The sheet only becomes active after it.'),
)

# Decisão de 02/11 (CONCORRENCIA-2026-11-02.md): o risco aceito aparece ao jogador.
RISCO_ESCRITA = (
    'O bot só escreve na sua ficha quando você pede. Se você mudar a mesma parte da ficha no Google enquanto o bot escreve, uma das mudanças pode se perder.',
    'The bot only writes to your sheet when you ask. If you change the same part of the sheet in Google while the bot is writing, one of the changes may be lost.',
)


def _i(idioma):
    if idioma not in ('pt-BR', 'en'):
        raise ErroCarteira('Idioma inválido.')
    return 1 if idioma == 'en' else 0


def texto_estado(d, idioma, agora):
    """`d` é o dicionário devolvido pelo serviço de atestado."""
    i = _i(idioma)
    if d.get('estado') not in ESTADOS or d.get('codigo') not in CODIGOS:
        raise ErroCarteira('Atestado de ativação inválido.')
    titulo = ESTADOS[d['estado']][i]
    if d['codigo'] == 'falta':
        itens = [FALTAM[r][i] for r in d.get('faltam', ()) if r in FALTAM]
        motivo = ('Falta: ' if i == 0 else 'Still needed: ') + '; '.join(itens) + '.'
    else:
        motivo = MOTIVOS[d['codigo']][i]
    minutos = max(0, int((agora - d['lido_em']) // 60)) if d.get('lido_em') else None
    if minutos is None:
        quando = ''
    elif minutos == 0:
        quando = ' Conferido agora.' if i == 0 else ' Checked just now.'
    else:
        quando = f' Conferido há {minutos} min.' if i == 0 else f' Checked {minutos} min ago.'
    return f'**{titulo}.** {motivo}{quando}'


def passos(idioma):
    i = _i(idioma)
    return [p[i] for p in PASSOS]


def risco_escrita(idioma):
    return RISCO_ESCRITA[_i(idioma)]
