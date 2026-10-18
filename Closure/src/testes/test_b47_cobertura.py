"""Regressões de cobertura B47: entradas próprias, herança e dependências."""
import unittest

from closure_bot.ficha_corretor import Aprovados, Resultado, conferir
from closure_bot.ficha_configuracao import ContextoB47, Efeito
from closure_bot.ficha_b47 import conferir_familias
from closure_bot.ficha_entidade_repertorio import conferir_repertorio_entidade
from testes.test_b47_integracao import completa, trocar, contexto, aprovar, REF
from testes.test_b47_derivados import efeito
from testes.test_b47_revisao import entidade


def trilha(base='Invocação Principal', *, caminho='Evocador'):
    f=trocar(completa(), caminho=caminho, trilha='Trilha sintética',
             custom__trilha__nome='Trilha sintética', custom__trilha__mestre_viu=0,
             custom__trilha__campo__caminho=caminho,
             custom__trilha__campo__base_do_livro=base)
    entidade(f)
    for i,nome in enumerate(('Mira','Área','Alcance','Controle','Auxiliares'),1):
        trocar(f,**{f'invocacao.1.familia.{i}':nome})
    if caminho=='Evocador':
        trocar(f,vida_max=14,energia_max=12)
    return trocar(f,invocacao__1__limite_familias=5,invocacao__1__limite_livres=2)


class TrilhaHerdada(unittest.TestCase):
    def test_familias_da_principal_herdadas_sem_trocar_nome_literal(self):
        f=trilha(); a=aprovar(f,'custom.trilha')
        r=conferir(f,REF,aprovados=a)
        self.assertFalse(any(p.campo.startswith('invocacao.1.limite_') or
                             p.campo=='invocacao.1.familias' for p in r.problemas),r.problemas)
        self.assertEqual(f['trilha'].valor,'Trilha sintética')
        self.assertIn('Trilha Trilha sintética',r.conferidos)

    def test_perfis_publicados_e_autonomia_herdam_separadamente(self):
        for base,abertas,livres in [('Invocação Principal',5,2),('Parceria',4,1),
                                   ('Múltiplas Invocações',4,1)]:
            for autonoma in (True,False):
                with self.subTest(base=base,autonoma=autonoma):
                    f=trilha(base);extra=int(not autonoma)
                    trocar(f,invocacao__1__autonomia='Autônoma' if autonoma else 'Não autônoma',
                           invocacao__1__limite_familias=abertas+extra,
                           invocacao__1__limite_livres=livres+extra)
                    for i,nome in enumerate(REF.magia.familias,1):
                        trocar(f,**{f'invocacao.1.familia.{i}':nome if i<=abertas+extra else ''})
                    c,r,ref=contexto(f,aprovar(f,'custom.trilha'))
                    conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r)
                    self.assertFalse(any('limite_' in p.campo for p in r.problemas),r.problemas)

    def test_sem_aprovacao_nao_certifica_perfil_padrao_por_engano(self):
        f=trilha();c,r,ref=contexto(f)
        self.assertEqual(conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r),(None,None))
        self.assertTrue(any('Trilha' in s and 'aprovação' in s for s in r.nao_conferido))

    def test_base_desconhecida_nao_e_tratada_como_nenhuma(self):
        f=trilha('Base inexistente');c,r,ref=contexto(f,aprovar(f,'custom.trilha'))
        self.assertFalse(c.registros['custom.trilha'].valida)
        self.assertEqual(conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r),(None,None))

    def test_nenhuma_nao_concede_principal(self):
        f=trilha('Nenhuma');c,r,ref=contexto(f,aprovar(f,'custom.trilha'))
        conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r)
        self.assertTrue(any(p.campo=='invocacao.1.limite_familias' and '3,' in p.esperado for p in r.problemas))

    def test_alterar_base_reabre_aprovacao(self):
        f=trilha();a=aprovar(f,'custom.trilha')
        trocar(f,custom__trilha__campo__base_do_livro='Parceria')
        c,r,ref=contexto(f,a)
        self.assertFalse(c.registros['custom.trilha'].aprovada)
        self.assertEqual(conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r),(None,None))

    def test_extras_da_principal_usam_base_aprovada(self):
        f=trocar(trilha(caminho='Bastião'),nivel=8,invocacao__1__talento_extra__1='Talento Próprio (CE 1)')
        c,r,ref=contexto(f,aprovar(f,'custom.trilha'))
        conferir_repertorio_entidade(f,ref,'invocacao.1',8,[],(set(),set()),r)
        self.assertFalse(any(p.campo=='invocacao.1.talento_extra.1' for p in r.problemas),r.problemas)

    def test_extras_sem_aprovacao_nao_sao_conferidos(self):
        f=trilha();c,r,ref=contexto(f)
        conferir_repertorio_entidade(f,ref,'invocacao.1',2,[],(set(),set()),r)
        self.assertFalse(any('escolhas extras separadas' in s for s in r.conferidos))


class TrocaIndependente(unittest.TestCase):
    def test_valor_fixo_independe_de_base_ausente_mas_nao_de_conflitos(self):
        c=ContextoB47(efeitos={'Vida máxima':[Efeito(1,'Vida máxima','trocar por',0,'teste','Decisão do mestre')]})
        self.assertEqual(c.aplicar('Vida máxima',None),0)
        self.assertIsNone(c.aplicar('PE máximo',None))
        c.alvos_invalidos.add('Vida máxima')
        self.assertIsNone(c.aplicar('Vida máxima',None))

    def test_vida_rolada_incompleta_preserva_troca_e_pendencia_da_rolagem(self):
        from closure_bot.ficha_corretor import RegrasDaCampanha
        f=efeito(trocar(completa(),regra__vida_rolada='Sim',vida_max=0),'Vida máxima',0,'trocar por')
        r=conferir(f,REF,RegrasDaCampanha(valores={'vida_rolada':'Sim'}))
        self.assertIn('vida.rolagem.2',[p.campo for p in r.pendencias])
        self.assertIn('Vida 0',r.conferidos)
        self.assertNotEqual(r.veredito,'aprovada')


class EspecializacaoCustom(unittest.TestCase):
    def test_especializacao_invalida_nao_certifica_bonus(self):
        for nivel,treino in [(2,1),(10,0)]:
            with self.subTest(nivel=nivel,treino=treino):
                f=trocar(completa(),nivel=nivel,custom__pericia__1__tipo='Perícia',
                         custom__pericia__1__nome='Runa sintética',custom__pericia__1__atributo='Inteligência',
                         custom__pericia__1__mestre_viu=0,personagem__pericia_custom__1__nome='Runa sintética',
                         personagem__pericia_custom__1__atributo='Inteligência',
                         personagem__pericia_custom__1__treino=treino,personagem__pericia_custom__1__especializacao=1,
                         personagem__pericia_custom__1__resultado=1+treino*REF.magia.maestria[nivel]+REF.magia.maestria[nivel]//2)
                r=conferir(f,REF,aprovados=aprovar(f,'custom.pericia.1'))
                self.assertIn('personagem.pericia_custom.1.especializacao',[p.campo for p in r.problemas])
                self.assertFalse(any('Runa sintética: bônus' in s for s in r.conferidos))

