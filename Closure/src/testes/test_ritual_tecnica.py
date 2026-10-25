"""Ritual e Técnica Inata pela rota estruturada da Origem (livro ou custom aprovada), na ANALISE 12."""
import unittest
from dataclasses import replace

from closure_bot.ficha_b47 import _rota_estruturada, conferir_aptidoes
from closure_bot.ficha_configuracao import ContextoB47
from closure_bot.ficha_corretor import Aprovados, Resultado, conferir
from closure_bot.ficha_custom import preparar_custom
from test_b47_integracao import trocar
from test_r53 import REF, completa_r53


def ritual(origem='Latente', inteligencia=5, nivel=10):
    f = completa_r53()
    trocar(f, nivel=nivel, origem=origem, aptidao__1='Ritual', **{'atributo.inteligencia.base': inteligencia})
    return f


def origem_custom(f, rota, base='Nenhuma', nome='Origem sintética'):
    trocar(f, origem=nome, custom__1__tipo='Origem', custom__1__nome=nome, custom__1__mestre_viu=0,
           custom__1__campo__base_do_livro=base, custom__1__campo__rota=rota)
    for i, (pericia, _) in enumerate(list(REF.testes.pericias.values())[:4], 1):
        trocar(f, **{f'custom.1.campo.pericia_{i}': pericia})
    return f


def contexto(f, aprovar=False):
    c = ContextoB47(aprovados=Aprovados(), r53=True)
    ref = preparar_custom(f, REF, c, Resultado('aprovada'))
    if aprovar:
        c = ContextoB47(aprovados=Aprovados({d.impressao: 'mestre sintético' for d in c.registros.values()}), r53=True)
        ref = preparar_custom(f, REF, c, Resultado('aprovada'))
    return c, replace(ref, magia=replace(ref.magia, contexto=c))


def avisos_tecnica(f, aprovar=False):
    """Roda só a conferência de Aptidões, como conferir_b47 faz depois de resolver a Origem."""
    c, ref = contexto(f, aprovar)
    r = Resultado('aprovada')
    conferir_aptidoes(f, ref, c, r)
    erros = [p.esperado for p in r.problemas if 'Técnica Inata' in p.esperado]
    pendentes = [p.esperado for p in r.pendencias if 'Técnica Inata' in p.esperado]
    return erros, pendentes, r


class RotaDaOrigem(unittest.TestCase):
    def test_rotas_do_livro(self):
        c, _ = contexto(completa_r53())
        for origem, rota in [('Latente', 1), ('Descendente', 1), ('Restrição Celestial · Restrição corporal', 1),
                             ('Latente · Sem Técnica', 2), ('Híbrido · Sem Técnica', 2),
                             ('Corpo Amaldiçoado', 3), ('Restrição Celestial · Sem Energia', 4)]:
            with self.subTest(origem=origem):
                self.assertEqual(_rota_estruturada(origem, c), rota)
        for origem in ('', 'Origem inventada', 'Inventada · Sem Técnica'):
            with self.subTest(origem=origem):
                self.assertIsNone(_rota_estruturada(origem, c))

    def test_rota_de_origem_custom_so_com_cadastro_aprovado(self):
        for rota, esperado in [('Fundamento', 1), ('Manejos', 2), ('Técnica Marcial com energia', 3),
                               ('Técnica Marcial sem energia', 4)]:
            with self.subTest(rota=rota):
                f = origem_custom(completa_r53(), rota)
                self.assertIsNone(_rota_estruturada('Origem sintética', contexto(f)[0]))
                self.assertEqual(_rota_estruturada('Origem sintética', contexto(f, aprovar=True)[0]), esperado)


class RitualTecnicaInata(unittest.TestCase):
    def test_origem_do_livro_com_tecnica_nao_gera_pendencia(self):
        for origem in ('Latente', 'Receptáculo', 'Restrição Celestial · Restrição corporal'):
            with self.subTest(origem=origem):
                erros, pendentes, _ = avisos_tecnica(ritual(origem))
                self.assertEqual((erros, pendentes), ([], []))

    def test_sem_tecnica_e_tecnica_marcial_sao_erro_e_nao_pendencia(self):
        # Livro, Ritual e Pactos: Técnica Marcial e Sem Técnica não adquirem Ritual; sem energia também não.
        for origem in ('Latente · Sem Técnica', 'Corpo Amaldiçoado', 'Restrição Celestial · Sem Energia'):
            with self.subTest(origem=origem):
                erros, pendentes, _ = avisos_tecnica(ritual(origem))
                self.assertEqual(len(erros), 1, erros)
                self.assertEqual(pendentes, [])

    def test_origem_custom_aprovada_usa_a_rota_cadastrada(self):
        f = origem_custom(ritual(), 'Fundamento')
        self.assertEqual(avisos_tecnica(f, aprovar=True)[:2], ([], []))
        f = origem_custom(ritual(), 'Manejos')
        erros, pendentes, _ = avisos_tecnica(f, aprovar=True)
        self.assertEqual((len(erros), pendentes), (1, []))

    def test_origem_custom_com_base_do_livro_segue_a_visao_mecanica(self):
        # conferir_b47 troca a custom com base pela base (+ Sem Técnica quando a ROTA é Manejos).
        for base, rota, erro in [('Encarnado', 'Fundamento', False), ('Encarnado', 'Manejos', True)]:
            with self.subTest(rota=rota):
                f = origem_custom(ritual(), rota, base=base)
                r = conferir(f, REF, aprovados=contexto(f, aprovar=True)[0].aprovados)
                textos = [p.esperado for p in r.problemas + r.pendencias if 'Técnica Inata' in p.esperado]
                self.assertEqual(bool([p for p in r.problemas if 'Técnica Inata' in p.esperado]), erro, textos)
                self.assertFalse(any('Técnica Inata' in p.esperado for p in r.pendencias), textos)

    def test_origem_custom_sem_aprovacao_mantem_pendencia_informativa(self):
        f = origem_custom(ritual(), 'Fundamento')
        erros, pendentes, _ = avisos_tecnica(f)
        self.assertEqual(erros, [])
        self.assertEqual(len(pendentes), 1)
        self.assertIn('rota da Origem não está confirmada', pendentes[0])

    def test_demais_requisitos_de_ritual_continuam(self):
        _, _, r = avisos_tecnica(ritual(inteligencia=4))
        self.assertTrue(any('exige Inteligência 5' in p.esperado for p in r.problemas))
        _, _, r = avisos_tecnica(ritual(nivel=9))
        self.assertTrue(any('nível ou Refino' in p.esperado for p in r.problemas))
        # Sem Técnica reprova pela Técnica e pelo atributo, sem um apagar o outro.
        erros, _, r = avisos_tecnica(ritual('Latente · Sem Técnica', inteligencia=4))
        self.assertEqual(len(erros), 1)
        self.assertTrue(any('exige Inteligência 5' in p.esperado for p in r.problemas))

    def test_ficha_inteira_sem_falso_alerta_de_tecnica(self):
        r = conferir(ritual('Latente'), REF)
        self.assertNotEqual(r.veredito, 'formato desconhecido')
        self.assertFalse(any('Técnica Inata' in p.esperado for p in r.problemas + r.pendencias))
        r = conferir(ritual('Latente · Sem Técnica'), REF)
        self.assertTrue(any('Técnica Inata' in p.esperado for p in r.problemas))


if __name__ == '__main__':
    unittest.main()
