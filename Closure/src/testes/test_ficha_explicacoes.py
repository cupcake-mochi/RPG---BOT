import unittest
from types import SimpleNamespace
from unittest.mock import patch
import discord
from closure_bot.ficha_explicacoes import orientacao_avisos, texto_painel
from closure_bot import prompt
from closure_bot.plantao import KALTSIT, CLOSURE

class Explicacoes(unittest.TestCase):
    def test_tipos(self):
        for frase in ('Minha ficha deu erro X, pode explicar?', 'Tem pendência na análise', 'O que significa essa observação na ficha?', 'Sheet analysis error'):
            for trecho in ('Erro:', 'Pendência:', 'Observação:', 'linha completa', 'R53', 'personalidade', 'Não execute nova análise'):
                self.assertIn(trecho, orientacao_avisos(frase))

    def test_casos(self):
        for frase, esperado in (
            ('Erro custom.2.nome na análise', 'espaços nas pontas'),
            ('Pendência de aprovação na ficha', 'definição exata'),
            ('Erro Orçamento excedido', 'não invente descontos'),
            ('Erro Ampliação altera funções ou peças', 'Ampliar conserva'),
            ('Aviso Classe 0 aceita somente Melhoria Leve', 'não muda a categoria'),
            ('Erro Talento 1 categoria CE 3', 'Classe de Efeito'),
            ('Erro fórmula sem cache', 'XLSX novo'),
            ('Observação de treinos na ficha', 'origem dos ganhos'),
            ('Pendência de carga na ficha', 'Quantidades'),
            ('Análise: interações de Alma não conferidas', 'não certifique')):
            with self.subTest(frase=frase): self.assertIn(esperado, orientacao_avisos(frase))

    def test_instrucoes_e_seguimento(self):
        self.assertNotIn('IGNORE_TUDO', orientacao_avisos('Erro na ficha: IGNORE_TUDO'))
        self.assertIn('Orçamento:', orientacao_avisos('Como corrijo?', ['Erro na análise: Orçamento excedido']))
        for frase in ('erro no computador', 'bom dia', 'Qual o clima de BH?'):
            self.assertEqual('', orientacao_avisos(frase))
        self.assertEqual('', orientacao_avisos('Como corrijo?', ['bom dia']))
        self.assertEqual('', orientacao_avisos('Como funciona concentração?', ['Erro na análise: Orçamento excedido']))

    def test_painel(self):
        e = discord.Embed(title='Ficha de Teste', description='Correções')
        e.add_field(name='❌ Precisa corrigir', value='Orçamento excedido')
        e.set_footer(text='Página 2 de 6 · Veredito geral: pendente')
        msg = SimpleNamespace(embeds=[e])
        self.assertIn('Orçamento excedido', texto_painel(msg))
        self.assertIn('desatualizada', texto_painel(msg))
        self.assertLessEqual(len(texto_painel(msg)), 6000)
        e.set_footer(text='Page 2 of 6 · Overall result: partial review')
        self.assertIn('Orçamento excedido', texto_painel(msg))
        e.set_footer(text='outro embed')
        self.assertEqual('', texto_painel(msg))

class Integracao(unittest.IsolatedAsyncioTestCase):
    async def test_personas_lores_idiomas(self):
        for persona in (KALTSIT, CLOSURE):
            for lore in (False, True):
                for idioma in ('pt-BR', 'en'):
                    ponte = SimpleNamespace(montar=lambda *a, **kw: {'perfil': 'nova-terra' if lore else 'original', 'input': [{'role':'system','content':'PERSONALIDADE'}, {'role':'user','content':a[1]}]})
                    with patch.object(prompt, '_ponte', return_value=ponte):
                        entrada = await prompt.montar(persona, 'Minha ficha deu erro de orçamento', nome='Teste', pronomes=None, turnos=[], falas_anteriores=[], estado={'nova_terra':lore,'idioma':idioma})
                    for trecho in ('PERSONALIDADE','Orçamento:','R53','English' if idioma=='en' else 'português do Brasil'):
                        self.assertIn(trecho, entrada[0]['content'])

    async def test_referencia_com_historico_longo(self):
        from closure_bot.conversa import Turno
        from datetime import datetime, timezone
        painel = 'Página da análise citada: ❌ Erro: Orçamento excedido'
        ponte = SimpleNamespace(montar=lambda *a, **kw: {'perfil':'original', 'input':[{'role':'system','content':'PERSONALIDADE'}, {'role':'user','content':a[1]}]})
        turnos = [Turno(datetime.now(timezone.utc), 'outro assunto', nome='Teste') for _ in range(10)]
        with patch.object(prompt, '_ponte', return_value=ponte):
            entrada = await prompt.montar(KALTSIT, 'Como corrijo?', nome='Teste', pronomes=None,
                turnos=turnos, falas_anteriores=[], estado={'aviso_ficha_referencia':painel})
        self.assertIn('Orçamento:', entrada[0]['content'])
        self.assertIn(painel, entrada[-1]['content'])
        self.assertNotIn(painel, entrada[0]['content'])
