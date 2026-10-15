"""Exemplos do livro e tentativas de converter concessões em espaços livres."""
import copy
import json
import unittest
from pathlib import Path

from closure_bot.ficha_corretor import Referencias, Resultado, conferir, conferir_feiticos
from closure_bot.ficha_leitor import Campo, de_linhas
from closure_bot.ficha_repertorio import conferir_repertorio

RAIZ = Path(__file__).resolve().parents[2]


def ficha(nivel=2, **trocas):
    valores = {'nivel': nivel, 'origem': 'Latente', 'origem.marcante': '', 'origem.menor_1': '',
               'origem.menor_2': '', 'marco.corpo': 0, 'marco.refino': 0, 'marco.leque': 0,
               'espacos_de_feitico': 2 + nivel // 2 + sum(n <= nivel for n in (6, 10, 14, 18, 22, 26, 30)),
               'tecnica.regra_propria.categoria': '', 'dominio.degrau': '', 'tecnica.rota.nome': 'Fundamento'}
    valores.update({f'passiva.{n}': '' for n in range(1, 13)})
    valores.update({f'feitico.{n}.nome': '' for n in range(1, 37)})
    valores.update({f'invocacao.{n}.nome': '' for n in range(1, 13)})
    valores.update({k.replace('__', '.'): v for k, v in trocas.items()})
    return {k: Campo(v, '', 'entrada') for k, v in valores.items()}


def por(f, **trocas):
    f.update({k.replace('__', '.'): Campo(v, '', 'entrada') for k, v in trocas.items()})


def feiticos(f, quantidade):
    for n in range(1, quantidade + 1):
        f[f'feitico.{n}.nome'] = Campo(f'Aplicação {n}', '', 'entrada')


class RepertorioDoLivro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / 'dados')

    def analisar(self, f):
        r = Resultado('aprovada')
        conferir_repertorio(f, self.ref, r)
        return r

    def campos_com_erro(self, f):
        return {p.campo for p in self.analisar(f).problemas}

    def test_tabela_de_espacos_sem_somar_marco_duas_vezes(self):
        for nivel, capacidade in ((1, 2), (2, 3), (5, 4), (10, 9), (14, 12), (20, 16), (26, 21), (30, 24)):
            f = ficha(nivel); r = self.analisar(f)
            self.assertEqual(r.problemas, [])
            self.assertIn(f'Repertório: capacidade {capacidade} espaços', r.conferidos)
            por(f, espacos_de_feitico=capacidade + 1)
            self.assertIn('espacos_de_feitico', self.campos_com_erro(f))

    def test_tres_aplicacoes_nivel_dois_e_quarta_excedente(self):
        f = ficha(); feiticos(f, 3)
        self.assertEqual(self.analisar(f).problemas, [])
        feiticos(f, 4)
        self.assertIn('repertorio', self.campos_com_erro(f))

    def test_leque_da_uma_aplicacao_e_um_talento(self):
        f = ficha(6, marco__leque=1, passiva__6='Instinto')
        feiticos(f, 7)  # seis espaços e uma aplicação adicional
        r = self.analisar(f)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any('6 de 6 espaços' in c for c in r.conferidos))
        por(f, passiva__7='Raiz')
        self.assertIn('marco.leque', self.campos_com_erro(f))

    def test_leque_nao_paga_invocacao_ou_talento_pago(self):
        f = ficha(6, marco__leque=1)
        for n in range(1, 8):
            por(f, **{f'invocacao__{n}__nome': 'Entidade', f'invocacao__{n}__aquisicao': 'Espaço conhecido'})
        self.assertIn('repertorio', self.campos_com_erro(f))
        g = ficha(6, marco__leque=1)
        for n in range(1, 6):
            por(g, **{f'passiva__{n}': 'Instinto'})
        por(g, tecnica__regra_propria__categoria=2, tecnica__regra_propria__espacos=1,
            dominio__degrau='Incompleta', dominio__custo='2 espaços')
        self.assertIn('repertorio', self.campos_com_erro(g))  # seis de capacidade, pelo menos oito ocupados

    def test_coexistencia_da_duas_aplicacoes_sem_aumentar_vagas(self):
        f = ficha(origem='Receptáculo', origem__marcante='Coexistência')
        feiticos(f, 5)
        self.assertEqual(self.analisar(f).problemas, [])
        feiticos(f, 6)
        self.assertIn('repertorio', self.campos_com_erro(f))
        g = ficha(origem='Receptáculo', origem__marcante='Coexistência')
        for n in range(1, 5):
            por(g, **{f'invocacao__{n}__nome': 'Entidade', f'invocacao__{n}__aquisicao': 'Espaço conhecido'})
        self.assertIn('repertorio', self.campos_com_erro(g))

    def test_outra_marcante_nao_recebe_coexistencia_por_texto(self):
        f = ficha(origem='Receptáculo', origem__marcante='Conflito', origem__marcante__texto='ganho dois feitiços')
        feiticos(f, 4)
        self.assertIn('repertorio', self.campos_com_erro(f))

    def test_talento_pago_tem_preco_e_nivel_do_catalogo(self):
        f = ficha(7, passiva__1='Eco', passiva__1__categoria=1)
        self.assertIn('passiva.1.categoria', self.campos_com_erro(f))
        self.assertFalse(any(c.startswith('Talento 1:') for c in self.analisar(f).conferidos))
        por(f, passiva__1__categoria=2)
        self.assertEqual(self.analisar(f).problemas, [])
        por(f, nivel=6, espacos_de_feitico=6)
        self.assertIn('passiva.1', self.campos_com_erro(f))
        self.assertFalse(any(c.startswith('Talento 1:') for c in self.analisar(f).conferidos))

    def test_cinco_ce_tres_custam_quinze_espacos(self):
        f = ficha(13)
        for n in range(1, 6):
            por(f, **{f'passiva__{n}': 'Escama'})
        r = self.analisar(f)
        self.assertTrue(any(p.campo == 'repertorio' and 'mínimo ocupado 15' in p.esperado for p in r.problemas))

    def test_sexto_nao_usa_slot_inventado_para_virar_gratuito(self):
        f = ficha(30, passiva__13='Raiz', marco__leque=7)
        self.assertIn('passiva.13', self.campos_com_erro(f))

    def test_regra_propria_cobra_so_dois_espacos_no_ce_tres(self):
        f = ficha(14, tecnica__regra_propria__categoria=3, tecnica__regra_propria__espacos=2)
        feiticos(f, 10)
        self.assertEqual(self.analisar(f).problemas, [])
        self.assertTrue(any('12 de 12 espaços' in c for c in self.analisar(f).conferidos))
        por(f, tecnica__regra_propria__espacos=3)
        self.assertIn('tecnica.regra_propria.espacos', self.campos_com_erro(f))

    def test_regra_inicial_gratis_nao_come_vaga(self):
        f = ficha(tecnica__regra_propria__categoria=1, tecnica__regra_propria__espacos='De graça')
        feiticos(f, 3)
        self.assertEqual(self.analisar(f).problemas, [])

    def test_dominio_soma_estagio_atual_sem_recomprar(self):
        f = ficha(14, marco__refino=1, dominio__degrau='Completa', dominio__custo='3 espaços',
                  tecnica__regra_propria__categoria=3, tecnica__regra_propria__espacos=2)
        feiticos(f, 7)
        self.assertEqual(self.analisar(f).problemas, [])
        feiticos(f, 8)
        self.assertIn('repertorio', self.campos_com_erro(f))

    def test_dominio_tem_requisito_de_refino_recalculado(self):
        f = ficha(10, dominio__degrau='Incompleta', dominio__custo='2 espaços', refino=99)
        self.assertIn('dominio.degrau', self.campos_com_erro(f))
        por(f, marco__refino=1)
        self.assertEqual(self.analisar(f).problemas, [])

    def test_sem_barreiras_conserva_requisitos_anteriores(self):
        f = ficha(26, marco__refino=3, dominio__degrau='Sem Barreiras', dominio__custo='5 espaços',
                  pericia__ocultismo__treino=1, pericia__ocultismo__especialista=1)
        self.assertEqual(self.analisar(f).problemas, [])
        por(f, pericia__ocultismo__treino=0)
        self.assertIn('dominio.degrau', self.campos_com_erro(f))
        por(f, pericia__ocultismo__treino=1, nivel=13, marco__refino=2, espacos_de_feitico=10)
        self.assertTrue(any('nível mínimo 14' in p.esperado for p in self.analisar(f).problemas))

    def test_rotas_sem_expansao_nao_usam_nome_calculado_para_burlar(self):
        for o in ('Latente · Sem Técnica', 'Corpo Amaldiçoado', 'Restrição Celestial · Sem Energia'):
            f = ficha(26, origem=o, marco__refino=3, dominio__degrau='Completa', dominio__custo='3 espaços',
                      tecnica__rota__nome='Fundamento')
            self.assertIn('dominio.degrau', self.campos_com_erro(f))
            self.assertIn('tecnica.rota.nome', self.campos_com_erro(f))

    def test_apenas_entidades_por_espaco_consumem_vagas(self):
        f = ficha()
        for n, aquisicao in enumerate(('Criação', 'Lista de ritual', 'Maldição domada'), 1):
            por(f, **{f'invocacao__{n}__nome': 'Entidade', f'invocacao__{n}__aquisicao': aquisicao})
        feiticos(f, 3)
        self.assertEqual(self.analisar(f).problemas, [])
        por(f, invocacao__4__nome='Nova', invocacao__4__aquisicao='Espaço conhecido')
        self.assertIn('repertorio', self.campos_com_erro(f))

    def test_gratuita_da_origem_nao_inventa_qual_foi(self):
        f = ficha(origem__menor_1='Manifestação Instintiva', passiva__1='Raiz', passiva__2='Leitura',
                  passiva__3='Instinto', passiva__4='Mão Firme')
        r = self.analisar(f)
        self.assertEqual(r.problemas, [])  # possibilidade de três pagos e um gratuito
        self.assertTrue(any('vinculação' in n for n in r.nao_conferido))
        self.assertFalse(any('espaços comuns ocupados' in c for c in r.conferidos))
        por(f, passiva__5='Farejador')
        self.assertIn('repertorio', self.campos_com_erro(f))

    def test_gratuita_de_origem_respeita_origem_e_ce(self):
        f = ficha(7, origem__menor_1='Manifestação Instintiva', passiva__6='Eco')
        self.assertIn('marco.leque', self.campos_com_erro(f))
        g = ficha(origem='Descendente', origem__menor_1='Manifestação Instintiva')
        feiticos(g, 4)
        self.assertIn('repertorio', self.campos_com_erro(g))

    def test_talento_proprio_nao_vira_aprovacao_de_efeito(self):
        f = ficha(13, passiva__1='Talento Próprio (CE 3)', passiva__1__categoria=3)
        r = self.analisar(f)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any('aguarda CONFIGURAÇÃO' in n for n in r.nao_conferido))
        self.assertFalse(any('espaços comuns ocupados' in c for c in r.conferidos))

    def test_categoria_faltante_vira_pendencia_sem_certificar_total(self):
        for nome in ('Talento personalizado', 'Instinto'):
            r = self.analisar(ficha(passiva__1=nome, passiva__1__categoria=''))
            self.assertEqual(r.problemas, [])
            self.assertEqual(r.pendencias[0].campo, 'passiva.1.categoria')
            self.assertFalse(any('espaços comuns ocupados' in c for c in r.conferidos))

    def test_campos_faltantes_nao_certificam_total_nem_recebem_zero(self):
        f = ficha(); del f['dominio.degrau']
        r = self.analisar(f)
        self.assertFalse(any('espaços comuns ocupados' in c for c in r.conferidos))
        f = ficha(); del f['marco.leque']; del f['origem.menor_1']
        feiticos(f, 4)
        self.assertNotIn('repertorio', self.campos_com_erro(f))

    def test_marcos_invalidos_nao_viram_descontos(self):
        for v in (-1, 10, True, 1.5, 'muitos'):
            f = ficha(6, marco__leque=v)
            self.assertIn('marco.leque', self.campos_com_erro(f))
        f = ficha(6, marco__leque=1, marco__refino=1)
        self.assertIn('marco.leque', self.campos_com_erro(f))

    def test_ce4_fora_dos_pagos_exclusivo_da_origem(self):
        f = ficha(origem__ce4='Rede Remota')
        self.assertIn('origem.ce4', self.campos_com_erro(f))
        f = ficha(origem='Restrição Celestial · Restrição corporal', origem__ce4='Rede Remota')
        self.assertEqual(self.analisar(f).problemas, [])
        self.assertTrue(any('fora dos espaços' in n for n in self.analisar(f).nao_conferido))
        por(f, passiva__1='CE4', passiva__1__categoria=4)
        self.assertIn('passiva.1.categoria', self.campos_com_erro(f))

    def test_pratica_cotidiana_amplia_quantidade_zero_sem_dar_espaco(self):
        f = ficha(origem='Restrição Celestial · Restrição corporal', origem__menor_1='Prática Cotidiana')
        # Só o filtro de quantidade desta função; as montagens têm a conferência própria.
        for n in range(1, 5):
            por(f, **{f'zero__{n}__nome': 'Uso', f'zero__{n}__classe': 0, f'zero__{n}__forma': 'Projétil',
                      f'zero__{n}__pe': 0, f'zero__{n}__dano': '2d8'})
        r = Resultado('aprovada'); conferir_feiticos(f, self.ref, r)
        self.assertFalse(any('quantidade de Classe 0' in p.esperado for p in r.problemas))
        feiticos(f, 4)
        self.assertIn('repertorio', self.campos_com_erro(f))

    def test_nao_altera_entradas_e_integracao_de_ficha_completa(self):
        linhas = json.loads((RAIZ / 'src/testes/dados/ficha_v2_montagem_4.json').read_text())
        f = ficha(); f.update(de_linhas(linhas)); original = copy.deepcopy(f)
        r = conferir(f, self.ref)
        self.assertEqual((r.veredito, r.problemas, r.pendencias), ('aprovada', [], []))
        self.assertTrue(any('espaços comuns ocupados' in c for c in r.conferidos))
        self.assertEqual(f, original)


if __name__ == '__main__':
    unittest.main()
