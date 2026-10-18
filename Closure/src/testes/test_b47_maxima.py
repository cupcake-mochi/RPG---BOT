"""Revisão da Máxima: contas separadas, catálogo e dependências de aprovação."""
import unittest

from closure_bot.ficha_magia import conferir_maxima
from testes.test_b47_integracao import completa, trocar, contexto, REF
from testes.test_b47_revisao import aprovar_tudo


def maxima(**valores):
    return trocar(completa(), nivel=17, maxima__nome='Máxima sintética',
                  maxima__forma='Projétil', maxima__pe=25,
                  maxima__montagem='0 de 8', maxima__dano='24d8 = 108', **valores)


def analisar(f, *, livres=(), abertas=None, aprovados=True):
    c,r,ref=contexto(f,aprovar_tudo(f) if aprovados else None)
    conferir_maxima(f,ref.magia,r,(set(livres),set(REF.magia.familias) if abertas is None else set(abertas)))
    return c,r


class MaximaB47(unittest.TestCase):
    def test_tabela_independente_dos_pontos_e_preco_de_forma_sem_desconto(self):
        for nivel,pe,dados,pontos,custo in [(17,25,24,8,3),(21,30,28,12,3),(26,35,32,16,4)]:
            with self.subTest(nivel=nivel):
                f=maxima();trocar(f,nivel=nivel,maxima__pe=pe,maxima__dano=f'{dados}d8',
                                 maxima__forma='Linha',maxima__montagem=f'{custo} de {pontos}')
                _,r=analisar(f,livres=('Área',))
                self.assertFalse(r.problemas,r.problemas)
                self.assertIn(f'Técnica Máxima: montagem {custo} de {pontos}',r.conferidos)
                self.assertIn(f'Técnica Máxima: {dados}d8',r.conferidos)

    def test_montagem_exportada_e_conferida_sem_confiar_no_aviso(self):
        for texto in ('999 de 8','0 de 99',0):
            with self.subTest(texto=texto):
                _,r=analisar(trocar(maxima(),maxima__montagem=texto))
                self.assertIn('maxima.montagem',[p.campo for p in r.problemas])
                self.assertNotIn('Técnica Máxima: montagem 0 de 8',r.conferidos)

    def test_resultado_vazio_e_informacao_insuficiente_nao_zero(self):
        _,r=analisar(trocar(maxima(),maxima__montagem=''))
        self.assertIn('maxima.montagem',[p.campo for p in r.pendencias])
        self.assertNotIn('Técnica Máxima: montagem 0 de 8',r.conferidos)

    def test_montagem_invalida_nao_certifica_dano_nem_montagem(self):
        for forma,pecas in [('Projétil','Inescapável'),('Toque','Longe'),
                            ('Cura','Mais Um'),('Projétil','Junto'),
                            ('Explosão','Rajada'),('Projétil','Terreno'),
                            ('Projétil','Corrói'),('Projétil','Rápido · Reação')]:
            with self.subTest(forma=forma,pecas=pecas):
                _,r=analisar(trocar(maxima(),maxima__forma=forma,maxima__pecas=pecas))
                self.assertTrue(any(p.campo in ('maxima.pecas','maxima.forma') for p in r.problemas),r.problemas)
                self.assertFalse(any(s.startswith(('Técnica Máxima: montagem','Técnica Máxima: 24d8')) for s in r.conferidos))
                self.assertIn('Técnica Máxima: PE 25',r.conferidos)

    def test_familia_fechada_e_excesso_de_orcamento_bloqueiam_dependentes(self):
        casos=[dict(maxima__pecas='Precisão'),dict(maxima__pecas='Fura · Salto')]
        for i,campos in enumerate(casos):
            with self.subTest(caso=i):
                _,r=analisar(trocar(maxima(),**campos),abertas=('Alcance',) if i==0 else None)
                self.assertIn('maxima.pecas',[p.campo for p in r.problemas])
                self.assertFalse(any(s.startswith(('Técnica Máxima: montagem','Técnica Máxima: 24d8')) for s in r.conferidos))

    def test_alias_aprovado_preserva_incompatibilidade_e_repeticao(self):
        for base,pecas in [('Inescapável','Peça sintética'),('Precisão','Precisão · Peça sintética')]:
            with self.subTest(base=base):
                f=trocar(maxima(),custom__melhoria__1__tipo='Melhoria',custom__melhoria__1__nome='Peça sintética',
                         custom__melhoria__1__base=base,custom__melhoria__1__mestre_viu=0,maxima__pecas=pecas)
                _,r=analisar(f,livres=('Mira',))
                self.assertIn('maxima.pecas',[p.campo for p in r.problemas])
                self.assertFalse(any(s.startswith('Técnica Máxima: montagem') for s in r.conferidos))

    def test_forma_custom_preserva_identidade_e_exige_aprovacao(self):
        f=trocar(maxima(),custom__forma__1__tipo='Forma',custom__forma__1__nome='Forma sintética',
                 custom__forma__1__base='Toque',custom__forma__1__mestre_viu=0,
                 maxima__forma='Forma sintética',maxima__pecas='Longe')
        _,r=analisar(f)
        self.assertIn('maxima.pecas',[p.campo for p in r.problemas])
        trocar(f,maxima__pecas='',maxima__montagem='0 de 8')
        _,r=analisar(f,aprovados=False)
        self.assertFalse(any(s.startswith(('Técnica Máxima: montagem','Técnica Máxima: 24d8')) for s in r.conferidos))
        self.assertTrue(any('aprovação' in s for s in r.nao_conferido))

    def test_quantidade_generica_da_cura_nao_inventa_tipo_contraditorio(self):
        # O produtor exporta só a quantidade genérica, inclusive para Cura.
        for texto in ('24d8','Cura 24d8 = 108'):
            _,r=analisar(trocar(maxima(),maxima__forma='Cura',maxima__dano=texto,maxima__montagem='5 de 8'))
            self.assertFalse(r.problemas,r.problemas)
        _,r=analisar(trocar(maxima(),maxima__dano='Cura 24d8'))
        self.assertIn('maxima.dano',[p.campo for p in r.problemas])

    def test_alma_simples_confere_metade_mas_nao_autoriza_regra(self):
        _,r=analisar(trocar(maxima(),maxima__pecas='Toca a Alma',maxima__montagem='3 de 8',maxima__dano='12d8 = 54'))
        self.assertFalse(r.problemas,r.problemas)
        self.assertIn('Técnica Máxima: 12d8',r.conferidos)
        self.assertTrue(any('alma' in s and 'mestre' in s for s in r.nao_conferido))

    def test_distribuicao_e_adicionais_de_alma_permanecem_explicitos(self):
        for pecas,custo in [('Rajada',3),('Toca a Alma · Queima',8)]:
            with self.subTest(pecas=pecas):
                _,r=analisar(trocar(maxima(),maxima__pecas=pecas,maxima__montagem=f'{custo} de 8'))
                self.assertFalse(r.problemas,r.problemas)
                self.assertTrue(any('distribuição' in s or 'interação' in s for s in r.nao_conferido))
                self.assertNotIn('Técnica Máxima: 24d8',r.conferidos)

    def test_formula_fixa_do_produtor_nao_e_confundida_com_alma_conferida(self):
        for texto,pendente in [('24d8 = 108',True),('999d8',False)]:
            with self.subTest(texto=texto):
                _,r=analisar(trocar(maxima(),maxima__pecas='Toca a Alma',maxima__montagem='3 de 8',maxima__dano=texto))
                self.assertIn('maxima.dano',[p.campo for p in (r.pendencias if pendente else r.problemas)])
                self.assertNotIn('Técnica Máxima: 12d8',r.conferidos)
