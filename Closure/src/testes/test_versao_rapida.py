"""Versão rápida da ficha (Ficha---RPG-JJK, etapas 3 a 5, PRs 155-157, 26/11/2026).

A ficha nova manda as mesmas chaves da ANALISE no mesmo endereço, mas 11.202 delas em branco: os cartões `r53.*`
(etapas 3 e 4, cartão de preencher), as Melhorias, Restrições e Formas custom e os avisos delas, e os campos de
base / mestre viu / definição / requisitos do tipo e do talento de entidade (etapa 5, lista simples). A regra
abaixo foi conferida contra a ANALISE gerada na main da ficha (85a596b): pega exatamente as 11.202.
As oficiais antigas continuam mandando valor nessas chaves; as duas têm de funcionar.
"""
import re
import unittest

from closure_bot.ficha_corretor import Aprovados, conferir
from closure_bot.ficha_leitor import Campo
from closure_bot.ficha_r53 import VERSAO_RAPIDA, versao_rapida
from test_r53 import REF, completa_r53

EM_BRANCO = re.compile(
    r'r53\.(?!(?:montagem\.esquema|entrada\.campos|versao\.campos)$).+'
    r'|custom\.(?:melhoria|restricao|forma)\.\d+\..+'
    r'|aviso\.custom\.(?:melhoria|restricao|forma|tipo_entidade|talento_entidade)\.\d+'
    r'|custom\.tipo_entidade\.\d+\.(?:base|mestre_viu|definicao)'
    r'|custom\.talento_entidade\.\d+\.(?:base|mestre_viu|requisitos)')


def rapida(f=None):
    f = dict(completa_r53() if f is None else f)
    for k, c in f.items():
        if EM_BRANCO.fullmatch(k):
            f[k] = Campo('', c.celula, c.parte)
    return f


def trocar(f, **kv):
    f = dict(f)
    for k, v in kv.items():
        f[k] = Campo(v, f[k].celula, f[k].parte)
    return f


def golem(f):
    """Como o teste no Google da etapa 5: tipo e talento novos só com os campos que a lista simples tem."""
    return trocar(f, **{'custom.tipo_entidade.1.nome': 'Golem Teste', 'custom.tipo_entidade.1.vida': 'Corpo de criação',
                        'custom.tipo_entidade.1.reserva_pe': 'Maldição domada',
                        'custom.tipo_entidade.1.efeito': 'Golem de pedra (descrição livre)',
                        'custom.talento_entidade.1.nome': 'Pele de Pedra Teste',
                        'custom.talento_entidade.1.categoria': 1, 'custom.talento_entidade.1.efeito': 'Pele dura'})


def resumo(r):
    return [(p.regra, p.campo, p.esperado) for p in r.problemas + r.pendencias + r.notas]


class VersaoRapida(unittest.TestCase):
    def test_a_fixture_tem_as_chaves_que_ficaram_em_branco(self):
        f = completa_r53()
        n = sum(1 for k in f if EM_BRANCO.fullmatch(k))
        self.assertGreater(n, 10000)
        self.assertFalse(versao_rapida(f))
        self.assertTrue(versao_rapida(rapida(f)))

    def test_chaves_vazias_nao_viram_erro_nem_aviso(self):
        velha, nova = conferir(completa_r53(), REF), conferir(rapida(), REF)
        self.assertEqual(nova.problemas, [])
        self.assertEqual(resumo(nova), resumo(velha))
        self.assertEqual(nova.veredito, velha.veredito)
        campos = [p.campo for p in nova.problemas + nova.pendencias + nova.notas]
        self.assertFalse([c for c in campos if EM_BRANCO.fullmatch(c)])

    def test_cartao_com_nome_diz_que_ficou_com_o_mestre(self):
        nova = conferir(trocar(rapida(), **{'feitico.1.nome': 'Rajada'}), REF)
        self.assertIn(VERSAO_RAPIDA, nova.nao_conferido)
        self.assertEqual(nova.problemas, [])
        # Sem nenhum cartão com nome, não há o que avisar.
        self.assertNotIn(VERSAO_RAPIDA, conferir(rapida(), REF).nao_conferido)
        # A oficial antiga manda os menus padrão no cartão vazio: continua no caminho de sempre.
        self.assertNotIn(VERSAO_RAPIDA, conferir(trocar(completa_r53(), **{'feitico.1.nome': 'Rajada'}), REF).nao_conferido)

    def test_tipo_e_talento_de_entidade_em_lista_simples(self):
        f = golem(rapida())
        r = conferir(f, REF)
        self.assertEqual(r.problemas, [])
        pendentes = {(p.regra, p.campo) for p in r.pendencias}
        self.assertIn(('aprovação', 'custom.tipo_entidade.1.nome'), pendentes)
        self.assertIn(('aprovação', 'custom.talento_entidade.1.nome'), pendentes)
        self.assertFalse([p for p in r.pendencias if p.campo.endswith('.mestre_viu')])

    def test_tipo_aprovado_vale_na_invocacao(self):
        from test_b47_integracao import contexto
        f = golem(rapida())
        c, _, _ = contexto(f)
        aprovados = Aprovados({c.registros[k].impressao: 'mestre sintético'
                               for k in ('custom.tipo_entidade.1', 'custom.talento_entidade.1')})
        c, r, ref = contexto(f, aprovados)
        tipo = c.registros['custom.tipo_entidade.1']
        self.assertTrue(tipo.valida and tipo.aprovada)
        self.assertEqual((tipo.efetivos['vida'], tipo.efetivos['talisma'], tipo.efetivos['reserva_pe']),
                         ('Corpo de criação', 'Não usa', 'Maldição domada'))
        self.assertIn('Golem Teste', ref.magia.tipos)
        self.assertTrue(c.registros['custom.talento_entidade.1'].valida)
        self.assertEqual(r.problemas, [])

    def test_oficial_antiga_continua_conferindo_a_caixa(self):
        velha = golem(completa_r53())
        self.assertEqual(conferir(velha, REF).problemas, [])  # mestre_viu 0, como a oficial manda
        errada = conferir(trocar(velha, **{'custom.tipo_entidade.1.mestre_viu': 'talvez'}), REF)
        self.assertIn(('custom', 'custom.tipo_entidade.1.mestre_viu'), {(p.regra, p.campo) for p in errada.problemas})

    def test_outros_cadastros_ainda_exigem_a_caixa(self):
        # Só tipo e talento de entidade perderam o MESTRE VIU; uma Família custom sem a caixa ainda é defeito.
        f = trocar(rapida(), **{'custom.familia.1.nome': 'Família Teste', 'custom.familia.1.estado': 'Neutra',
                                'custom.familia.1.mestre_viu': ''})
        r = conferir(f, REF)
        self.assertIn(('custom', 'custom.familia.1.mestre_viu'), {(p.regra, p.campo) for p in r.problemas})


if __name__ == '__main__':
    unittest.main()
