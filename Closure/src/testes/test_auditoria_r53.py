"""A comparação editorial conserva números, custos e limitações, sem tolerância textual ampla."""
import importlib.util
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('auditoria_r53', RAIZ / 'ferramentas/auditar_r53.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class Auditoria(unittest.TestCase):
    def test_normaliza_somente_hierarquia_e_titulo_de_capitulo(self):
        antes = {'a': {'texto': '### Cura\n\nCusta 5 PE.', 'capitulo_titulo': 'Fundamento'}}
        depois = {'a': {'texto': '#### Cura\n\nCusta 6 PE.', 'capitulo_titulo': 'Fundamento'}}
        item = dict(id='1', bloco='a', antes='# Cura\n\nCusta 5 PE.', depois='# Cura\n\nCusta 6 PE.')
        self.assertTrue(a.auditar(antes, depois, [item])['registro_oficial_confere'])
        item['depois'] = '# Cura\n\nCusta 5 PE.'
        self.assertFalse(a.auditar(antes, depois, [item])['registro_oficial_confere'])
        self.assertEqual(a.normalizar('# Fundamento\n\ntexto', 'Fundamento'), 'texto')
        self.assertEqual(a.normalizar('# Outro título\n\ntexto', 'Fundamento'), '# Outro título\n\ntexto')

    def test_alteracao_omitida_ou_duplicada_nao_passa(self):
        b = {'a': {'texto': '2 PE', 'capitulo_titulo': 'Custo'}}
        c = dict(id='1', bloco='a', antes='', depois='2 PE')
        self.assertFalse(a.auditar({}, b, [])['sem_alteracoes_fora_do_registro'])
        self.assertFalse(a.auditar({}, b, [c, c])['sem_duplicatas'])

    def test_corpus_corrente_e_legado_nao_se_misturam(self):
        atual = a.blocos(RAIZ / 'dados/sistema/livro.jsonl')
        legado = a.blocos(RAIZ / 'dados/sistema/legado-r52.jsonl')
        self.assertIn('fundamento--funcoes', atual)
        self.assertNotIn('fundamento--amparoformas', atual)
        self.assertIn('fundamento--amparoformas', legado)
        self.assertNotIn('fundamento--funcoes', legado)
        self.assertEqual(len(atual), 576)
