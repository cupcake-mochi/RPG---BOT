"""Explicações de apresentação; não alteram resultados nem aprovam a ficha."""
import json
import math
import re

from discord.utils import escape_markdown, escape_mentions
from .ficha_configuracao import valor


def linha_clara(p, ficha, *, ingles=False):
    """Retorna None para manter a apresentação padrão dos demais avisos."""
    from .cogs.ficha import _rotulo
    from .ficha_ingles import label, detail

    def texto(pt, en):
        return en if ingles else pt

    nome = label(_rotulo(p.campo)) if ingles else _rotulo(p.campo)
    mensagem = None
    if (p.regra == 'custom' and p.campo.endswith('.nome') and
            p.esperado.startswith(('preencha o nome do cadastro', 'remova os espaços em branco', 'retire o separador de lista'))):
        posicao = re.fullmatch(r'custom\.(\d+)\.nome', p.campo)
        if posicao:
            nome = texto('Cadastro próprio ', 'Custom entry ') + posicao[1]
        encontrado = str(p.encontrado)
        if encontrado.strip():
            nome += ' · ' + escape_mentions(escape_markdown(encontrado.strip()))
        mensagem = detail(p.esperado) if ingles else p.esperado
        mensagem += texto('. Revise o nome em CONFIGURAÇÃO; alterar o cadastro pode exigir nova aprovação.',
                          '. Review the name in CONFIGURAÇÃO; changing the entry may require a new approval.')

    m = re.fullmatch(r'r53\.(.+)\.avisos', p.campo)
    if m and p.regra == 'aviso':
        raiz = 'r53.' + m[1]
        try:
            entrada = json.loads(valor(ficha, raiz + '.entrada'))
        except (ValueError, TypeError):
            entrada = None
        if isinstance(entrada, list) and len(entrada) >= 2 and entrada[0] == m[1] and isinstance(entrada[1], str):
            nome += ' · ' + escape_mentions(escape_markdown(entrada[1].strip()))
        aviso = p.encontrado
        if aviso.startswith('Ampliação altera funções ou peças: '):
            campos = aviso.split(': ', 1)[1].split(' · ')
            nomes = {'forma': texto('Forma', 'Form'), 'controle': texto('Controle', 'Control'),
                     'pessoal': texto('uso pessoal', 'personal use')}
            for prefixo, pt, en in [('m', 'Melhoria', 'Improvement'), ('r', 'Restrição', 'Restriction'),
                                    ('funcao', 'Função', 'Function')]:
                nomes.update({prefixo + str(n): texto(pt, en) + ' ' + str(n) for n in range(1, 5)})
            mudancas = ', '.join(nomes.get(c, c) for c in campos)
            mensagem = texto(
                f'As versões salvas em Classes diferentes não mantêm a mesma montagem ({mudancas}). '
                'Compare essas escolhas entre as versões. Ampliar conserva as compras; acrescentar ou trocar peças exige outra montagem.',
                f'The saved versions at different Classes do not keep the same build ({mudancas}). '
                'Compare these choices across versions. Scaling keeps the purchases; adding or replacing components requires another build.')
        elif aviso == 'Classe 0 aceita somente Melhoria Leve':
            mensagem = texto(
                'Há uma Melhoria Média ou Pesada nesta aplicação de Classe 0. Use somente Melhoria Leve; '
                'o desconto de Família reduz o preço, mas não muda a categoria da Melhoria.',
                'This Class 0 application contains a Medium or Heavy Improvement. Use only Light Improvements; '
                'a Family discount lowers the price, but does not change the Improvement category.')
        elif aviso == 'Orçamento excedido':
            mensagem = texto('As compras ultrapassam o orçamento. Revise a Forma, as Melhorias e as Restrições.',
                              'The purchases exceed the budget. Review the Form, Improvements and Restrictions.')
            try:
                crus = [valor(ficha, raiz + '.' + k) for k in
                        ('orcamento', 'base_funcoes', 'custo_forma', 'melhorias_pagas', 'devolucao', 'saldo')]
                if any(isinstance(v, bool) for v in crus):
                    raise ValueError('caixa não é orçamento')
                dados = list(map(float, crus))
                if all(math.isfinite(v) for v in dados):
                    b, f, forma, melhorias, devolucao, saldo = dados
                    if min(b, f, forma, melhorias, devolucao) >= 0 and saldo < 0 and b-f-forma-melhorias+devolucao == saldo:
                        conta = f'{b:g} − {f:g} − {forma:g} − {melhorias:g} + {devolucao:g} = {saldo:g}'
                        mensagem = texto(
                            f'A montagem excede o orçamento em {-saldo:g} pontos. A ficha informa: orçamento − funções − Forma − Melhorias + devolução = saldo: {conta}. Revise as compras.',
                            f'This build exceeds its budget by {-saldo:g} points. The sheet reports: budget − functions − Form − Improvements + refund = balance: {conta}. Review the purchases.')
            except (ValueError, TypeError, OverflowError):
                pass
        if mensagem is None:
            # Mantém também avisos novos, sem esconder a informação original.
            mensagem = detail(aviso) if ingles else aviso

    if mensagem is None and p.regra in ('conta', 'formato'):
        encontrado = escape_mentions(escape_markdown(str(p.encontrado))) or texto('(vazio)', '(empty)')
        esperado = (detail(p.esperado) if ingles else p.esperado) or texto('(vazio)', '(empty)')
        mensagem = texto(f'A ficha informa {encontrado}; a conferência indica {esperado}.',
                          f'The sheet reports {encontrado}; the check expects {esperado}.')
    calculado = re.fullmatch(r'exportar resultado calculado \(([^()]*)\)', p.esperado)
    if mensagem is None and p.regra == 'informação' and calculado and not str(p.encontrado).strip():
        mensagem = texto(
            f'A leitura não trouxe o resultado deste campo. O bot calculou {calculado[1]}. '
            'Aguarde a planilha terminar de calcular e envie uma nova análise; para XLSX, baixe o arquivo novamente. '
            'Se continuar vazio, confira a exportação da ficha, sem substituir a fórmula.',
            f'The data read from the sheet did not include this result. The bot calculated {calculado[1]}. '
            'Wait for the sheet to finish calculating, then submit another analysis; for XLSX, download a fresh file. '
            'If it is still empty, check the sheet export without replacing the formula.')
    if mensagem is None and p.regra in ('equipamento', 'carga', 'talento', 'testes', 'custom',
                                        'configuração', 'campanha', 'aprovação', 'informação',
                                        'famílias', 'progressão', 'treinos', 'aptidão'):
        esperado = detail(p.esperado) if ingles else p.esperado
        encontrado = escape_mentions(escape_markdown(str(p.encontrado)))
        mensagem = esperado.rstrip('.') + '.' if esperado else ''
        mensagem += texto(f' Na ficha: {encontrado}.' if encontrado else ' Esse campo não veio preenchido na leitura.',
                          f' In the sheet: {encontrado}.' if encontrado else ' This field was empty in the data read from the sheet.')
    return f'**{nome}**: {mensagem}' if mensagem is not None else None
