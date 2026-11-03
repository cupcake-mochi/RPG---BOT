"""O bot nunca escreve na área do pulso de ativação (metadados de desenvolvedor).

O produtor grava `r53_pulso_*`; o bot só lê. Varredura do código e dos corpos
reais do único POST do bot (financeiro).
"""
import json
from pathlib import Path
import re
import unittest

from carteira_viva import leitor_pulso
from testes import test_carteira_financeiro_rest as fixture_financeiro

RAIZ = Path(leitor_pulso.__file__).parent
ESCRITA = re.compile(r'(create|update|delete)DeveloperMetadata|developerMetadata[^\n]*:(search|batchUpdate)', re.I)


class PulsoSemEscritaTeste(unittest.TestCase):
    def test_nenhum_modulo_monta_escrita_de_metadado(self):
        for f in sorted(RAIZ.rglob('*')):
            if f.suffix in ('.py', '.js', '.html') and f.is_file():
                with self.subTest(f.name):
                    self.assertIsNone(ESCRITA.search(f.read_text(encoding='utf8')))

    def test_leitor_so_faz_get(self):
        fonte = Path(leitor_pulso.__file__).read_text(encoding='utf8')
        self.assertNotIn('POST', fonte); self.assertNotIn('batchUpdate', fonte)
        self.assertIn('provedor._json(', fonte)  # _json só faz GET


class PostFinanceiroSemMetadadoTeste(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = fixture_financeiro.FinanceiroRestTeste.asyncSetUp
    asyncTearDown = fixture_financeiro.FinanceiroRestTeste.asyncTearDown
    b = fixture_financeiro.FinanceiroRestTeste.b
    http = fixture_financeiro.FinanceiroRestTeste.http
    aplicar_pedidos = fixture_financeiro.FinanceiroRestTeste.aplicar_pedidos
    inicializar = fixture_financeiro.FinanceiroRestTeste.inicializar

    async def test_post_real_do_financeiro_nao_toca_metadados(self):
        await self.inicializar()
        self.assertEqual(len(self.posts), 1)
        for pedido in self.posts[0]['requests']:
            self.assertFalse(any('DeveloperMetadata' in k or 'developerMetadata' in k for k in pedido))
        self.assertNotIn('eveloperMetadata', json.dumps(self.posts[0]))


if __name__ == '__main__':
    unittest.main()
