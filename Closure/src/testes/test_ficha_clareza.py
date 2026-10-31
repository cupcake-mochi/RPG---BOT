"""Regressões sintéticas; nenhuma ficha ou identificação real é armazenada."""
import copy
import json
import re
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from closure_bot.ficha_corretor import Problema
from closure_bot.ficha_leitor import Campo
from closure_bot.cogs.ficha import _linha
from closure_bot.ficha_ingles import line
import testes.test_ficha_repertorio as repertorio
from testes.test_ficha_repertorio import ficha
from testes.test_b47_integracao import completa, trocar, contexto


class Categorias(unittest.TestCase):
    setUpClass = classmethod(repertorio.RepertorioDoLivro.setUpClass.__func__)
    analisar = repertorio.RepertorioDoLivro.analisar
    campos_com_erro = repertorio.RepertorioDoLivro.campos_com_erro

    def test_rotulo_ce_equivale_ao_numero_sem_mudar_entrada(self):
        for nome, ce in [('Reserva Profunda', 3), ('Afinidade', 3), ('Talento sintético', 2)]:
            a = ficha(18, passiva__1=nome, passiva__1__categoria=ce)
            b = copy.deepcopy(a)
            b['passiva.1.categoria'] = Campo(f'CE {ce}', '', 'entrada')
            antes = copy.deepcopy(b)
            self.assertEqual(self.analisar(a), self.analisar(b))
            self.assertEqual(b, antes)

    def test_rotulo_nao_oculta_categoria_errada_nivel_ou_valor_invalido(self):
        for ce in ('CE 2', 'CE 4', True, 'CE 3 extra', 'CE 03', 3.0):
            with self.subTest(ce=ce):
                f = ficha(18, passiva__1='Reserva Profunda', passiva__1__categoria=ce)
                self.assertIn('passiva.1.categoria', self.campos_com_erro(f))
        self.assertIn('passiva.1', self.campos_com_erro(
            ficha(2, passiva__1='Reserva Profunda', passiva__1__categoria='CE 3')))


class Mensagens(unittest.TestCase):
    def test_fluxo_motor_painel_pt_en_preserva_erros_e_nao_confia_na_coluna_c(self):
        from testes.test_r53 import completa_r53, gravar, REF
        from closure_bot.ficha_corretor import conferir
        from closure_bot.cogs.ficha import paginas
        from closure_bot.idiomas import usar
        from types import SimpleNamespace
        f = completa_r53()
        gravar(f, 'classe0.1', 0, nome='Pulso sintético', m1='Fura')
        r = conferir(f, REF)
        self.assertTrue(any(p.regra == 'aviso' and p.encontrado == 'Classe 0 aceita somente Melhoria Leve'
                            for p in r.problemas))
        antes = copy.deepcopy((f, r))
        for idioma, trecho in [('pt-BR', 'Melhoria Média'), ('en', 'Medium or Heavy')]:
            with usar(idioma):
                ps = paginas(r, f, SimpleNamespace(chave='closure', nome='Closure', avatar_url=''))
            textos = '\n'.join(c.value for p in ps for c in p.fields)
            self.assertIn('Pulso sintético', textos)
            self.assertIn(trecho, textos)
            self.assertTrue(all(len(p) <= 6000 and all(len(c.value) <= 1024 for c in p.fields) for p in ps))
        self.assertEqual(antes, (f, r))

    def test_divergencia_do_motor_nao_vira_explicacao_do_aviso_exportado(self):
        p = Problema('conta', 'r53.maxima.1.avisos', 'aviso diferente', 'Orçamento excedido')
        self.assertIn('aviso diferente', _linha(p, self.cartao('maxima.1')))
        self.assertIn('aviso diferente', line(p, self.cartao('maxima.1')))

    def test_nome_com_espaco_explica_sem_corrigir_identidade(self):
        f = trocar(completa(), custom__1__tipo='Marcante', custom__1__nome='Nome sintético ',
                   custom__1__campo__origem='Origem sintética')
        antes = copy.deepcopy(f)
        _, r, _ = contexto(f)
        p = next(p for p in r.problemas if p.campo == 'custom.1.nome')
        self.assertIn('fim', p.esperado)
        self.assertNotIn('único', p.esperado)
        self.assertEqual(f, antes)
        self.assertIn('Nome sintético', _linha(p, f))
        self.assertIn('trailing', line(p, f))

    def cartao(self, id_):
        return {f'r53.{id_}.entrada': Campo(json.dumps([id_, 'Cartão sintético']), '', '')}

    def test_ampliacao_legivel_sem_sumir_o_aviso(self):
        p = Problema('aviso', 'r53.feitico.1.avisos', 'cartão sem este aviso mecânico',
                     'Ampliação altera funções ou peças: m1 · m2 · m3')
        f = self.cartao('feitico.1')
        txt = _linha(p, f)
        self.assertIn('Cartão sintético', txt)
        self.assertIn('Melhoria 3', txt)
        self.assertIn('Classes', txt)
        self.assertNotIn('m1', txt)
        self.assertIn('Improvement 3', line(p, f))

    def test_classe_zero_explicita_categoria_e_desconto(self):
        p = Problema('aviso', 'r53.classe0.1.avisos', '', 'Classe 0 aceita somente Melhoria Leve')
        txt = _linha(p, self.cartao('classe0.1'))
        self.assertIn('Média', txt)
        self.assertIn('desconto', txt)

    def test_orcamento_sem_inventar_conta_quando_dados_faltam(self):
        p = Problema('aviso', 'r53.maxima.1.avisos', '', 'Orçamento excedido')
        f = self.cartao('maxima.1')
        self.assertIn('orçamento', _linha(p, f))
        for k,v in dict(orcamento=8, base_funcoes=0, custo_forma=5,
                        melhorias_pagas=14, devolucao=0, saldo=-11).items():
            f['r53.maxima.1.' + k] = Campo(str(v), '', '')
        self.assertIn('11 pontos', _linha(p, f))
        self.assertIn('8 − 0 − 5 − 14 + 0 = -11', _linha(p, f))
        f['r53.maxima.1.saldo'] = Campo('-99', '', '')
        self.assertNotIn('99 pontos', _linha(p, f))


class LivroNosMundos(unittest.TestCase):
    def test_adaptacao_narrativa_e_continuacao_recebem_fontes_de_montagem(self):
        from testes.test_servidor_publico import FontesDoPrompt
        FontesDoPrompt.setUpClass()
        ponte = FontesDoPrompt.ponte
        primeira = ('Me explique como eu alteraria esse feitiço para ser uma espécie de bônus de dano concentrado? '
                    'Como uma extensão de ataques corpo a corpo. A descrição usa lâminas de ar.')
        segunda = 'Compreendo, porém como seria caso eu desse tipo um dano adicional em golpes corpo a corpo, é possível isso?'
        for persona in ('kal', 'clo'):
            for nt in (False, True):
                for pergunta, anteriores in [(primeira, []), (segunda, [primeira]),
                    ('Como posso adaptar meu feitiço para causar dano extra com uma espada?', []),
                    ('How can I adapt my spell to give bonus damage to melee attacks?', [])]:
                    p = ponte.montar(persona, pergunta, estado={'nova_terra': nt}, hora=(19, 0),
                        turnos=[{'de': 'user', 'nome': 'Pessoa', 'texto': t} for t in anteriores])
                    texto = p['input'][-1]['content']
                    for ancora in ('fundamento--formas', 'fundamento--pontos', 'catalogo--melhoria-efeito-proprio'):
                        self.assertIn('[Livro, âncora ' + ancora + ']', texto)
        for pergunta in ('E como altero a cor da minha camiseta?', 'Compreendo, porém você gosta de café?'):
            p = ponte.montar('kal', pergunta, turnos=[{'de':'user','nome':'Pessoa','texto':primeira}])
            self.assertNotIn('[Livro, âncora catalogo--melhoria-efeito-proprio]', p['input'][-1]['content'])

    def test_mesmos_trechos_e_limite_da_lore_nao_bloqueia_livro(self):
        from testes.test_servidor_publico import FontesDoPrompt
        FontesDoPrompt.setUpClass()
        ponte = FontesDoPrompt.ponte
        for persona in ('kal', 'clo'):
            for pergunta in ('Como funciona Integridade?', 'Como funciona Ritual?',
                             'Qual o limite de Talentos pagos?', 'Como funciona a Ampliação de feitiço?'):
                textos = []
                for nt in (False, True):
                    p = ponte.montar(persona, pergunta, estado={'nova_terra': nt}, hora=(22, 0))
                    texto = '\n'.join(m['content'] for m in p['input'])
                    textos.append(re.findall(r'\[Livro, âncora ([^]]+)\]\n(.*?)(?=\n\n\[|$)', texto, re.S))
                self.assertTrue(textos[0])
                self.assertEqual(*textos)
        p = ponte.montar('clo', 'O que sabemos de Shiki em Siracusa?', estado={'nova_terra': True})
        texto = '\n'.join(m['content'] for m in p['input'])
        self.assertNotIn('livro R52', texto)
        self.assertIn('não limita a consulta às regras', texto)
