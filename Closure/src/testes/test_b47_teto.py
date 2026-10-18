"""Quebra Coisa entra no teto; não multiplica efeitos secundários ou alvos."""
import unittest

from testes.test_b47_integracao import completa, trocar
from testes.test_b47_revisao import forma, montagem, entidade


class TetoObjetos(unittest.TestCase):
    def ficha(self,custom=False,**valores):
        f=forma() if custom else trocar(completa(),nivel=10,feitico__1__nome='Teste',
                    feitico__1__classe=3,feitico__1__forma='Projétil',feitico__1__pe='9 PE',
                    feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
        return trocar(f,feitico__1__pecas='Quebra Coisa',feitico__1__dano='6d8 = 27',**valores)

    def test_teto_12_inclui_dano_dobrado_contra_objeto(self):
        # Classe 3: saldo 9 - 2 = 7. Sete dobrado passa de 12; seis cabe.
        for custom in (False,True):
            with self.subTest(custom=custom):
                f=self.ficha(custom);_,r=montagem(f)
                self.assertFalse(r.problemas,r.problemas)
                self.assertTrue(any('6d8' in s for s in r.conferidos))
                trocar(f,feitico__1__dano='7d8')
                _,r=montagem(f)
                self.assertIn('feitico.1.dano',[p.campo for p in r.problemas])

    def test_adicional_nao_reaplica_multiplicador(self):
        # Saldo 6; 5*2 + floor(5/2) = 12. Os 2d8 não dobram de novo.
        for custom in (False,True):
            f=self.ficha(custom)
            trocar(f,feitico__1__pecas='Quebra Coisa · Salto',feitico__1__restricoes='Gesto',
                   feitico__1__dano='5d8 = 22 · +2d8')
            _,r=montagem(f)
            self.assertFalse(r.problemas,r.problemas)
            trocar(f,feitico__1__dano='6d8 · +3d8')
            _,r=montagem(f)
            self.assertIn('feitico.1.dano',[p.campo for p in r.problemas])

    def test_remate_e_quebra_coisa_tem_alvos_distintos(self):
        f=self.ficha()
        trocar(f,feitico__1__pecas='Quebra Coisa · Remate',feitico__1__restricoes='Gesto · Sangra')
        _,r=montagem(f)
        self.assertFalse(r.problemas,r.problemas)
        # Dobra em objetos OU aumenta 25% em criaturas; não faz 2*1,25.
        self.assertIn('Feitiço 1: dano-base 6d8',r.conferidos)

    def test_liberacao_tambem_obedece_teto(self):
        for custom in (False,True):
            f=self.ficha(custom)
            for sufixo in ('nome','classe','forma','pecas','pe','alcance','resolve','dano'):
                trocar(f,**{'liberacao.1.'+sufixo:f['feitico.1.'+sufixo].valor})
            trocar(f,liberacao__1__pe='14 PE')
            # A interface de montagem recebe liberação explicitamente.
            from testes.test_b47_integracao import contexto
            from testes.test_b47_revisao import aprovar_tudo
            from closure_bot.ficha_magia import conferir_montagem
            c,r,ref=contexto(f,aprovar_tudo(f))
            conferir_montagem(f,ref.magia,'liberacao.1',10,r.problemas,r.conferidos,r.nao_conferido,
                             liberacao=True,familias=(set(),set(ref.magia.familias)))
            self.assertFalse(r.problemas,r.problemas)
            self.assertTrue(any('6d8' in s for s in r.conferidos))

    def test_entidade_com_adicionais_usa_mesmo_teto(self):
        f=self.ficha();entidade(f,nivel=10)
        trocar(f,invocacao__1__esp__1__nome='Teste',invocacao__1__esp__1__classe=3,
               invocacao__1__esp__1__forma='Projétil',invocacao__1__esp__1__pecas='Quebra Coisa · Salto',
               invocacao__1__esp__1__restricoes='Gesto',invocacao__1__esp__1__pe='9 PE',
               invocacao__1__esp__1__dano='5d8 · +2d8',invocacao__1__esp__1__alcance='18 m, um alvo',
               invocacao__1__esp__1__resolve='Ataque +5')
        _,r=montagem(f,'invocacao.1.esp.1',entidade=True,livres=('Castigo','Área'))
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('dano-base 5d8' in s for s in r.conferidos))

    def test_alias_aprovado_tambem_reduz_teto(self):
        f=self.ficha()
        trocar(f,custom__melhoria__1__tipo='Melhoria',custom__melhoria__1__nome='Demolição sintética',
               custom__melhoria__1__base='Quebra Coisa',custom__melhoria__1__mestre_viu=0,
               feitico__1__pecas='Demolição sintética')
        _,r=montagem(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertIn('Feitiço 1: dano-base 6d8',r.conferidos)
