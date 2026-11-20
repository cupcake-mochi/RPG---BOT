"""ANALISE estática (formato 13, Ficha---RPG-JJK ESQUEMA-ANALISE.md de 17/11/2026) sem quebrar a ficha viva (12).

As fixtures são o CSV que o link da ficha devolve (gviz, `headers=1`): a ficha R53 sintética completa, e no 13 as duas
chaves novas no fim da aba, sem célula nem parte, como o Apps Script grava. Nada de dado de jogador nem IA paga.
"""
import unittest
from dataclasses import asdict
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from closure_bot.ficha_corretor import conferir
from closure_bot.ficha_leitor import Campo, de_csv, exportacao_pendente
from closure_bot.idiomas import catalogo, usar
from test_ficha_painel import PERSONA, RAIZ
from test_r53 import REF, completa_r53, csvfile_texto

EXPORTADA_EM = '2026-11-17T14:03:00'


def csv_da_ficha(formato=12, estado=None, exportada_em=''):
    """CSV da ANALISE. `estado=None`: a ficha nunca rodou o script (sem as chaves novas)."""
    ficha = completa_r53()
    ficha['formato.versao'] = Campo(formato, '', 'cabeçalho')
    if estado is not None:
        ficha['analise.estado'] = Campo(estado, '', '')
        ficha['analise.exportada_em'] = Campo(exportada_em, '', '')
    return csvfile_texto(ficha)


def _cog():
    from closure_bot.cogs.ficha import Ficha
    bot = SimpleNamespace(config=SimpleNamespace(dados=RAIZ / 'dados'),
                          personas={'closure': PERSONA, 'kaltsit': PERSONA}, manifesto={})
    return Ficha(bot)


class Leitura(unittest.TestCase):
    def test_csv_13_le_as_chaves_novas_como_texto(self):
        ficha = de_csv(csv_da_ficha(13, 'em_dia', EXPORTADA_EM))
        self.assertEqual(ficha['formato.versao'].valor, 13)
        self.assertEqual(ficha['analise.estado'], Campo('em_dia', '', ''))
        self.assertEqual(ficha['analise.exportada_em'].valor, EXPORTADA_EM)

    def test_quem_pode_ser_conferida(self):
        casos = [((12, None), None), ((12, 'viva'), None), ((13, 'em_dia'), None),
                 ((13, 'desatualizada'), 'desatualizada'), ((13, 'exportando'), 'exportando'),
                 ((13, 'viva'), 'viva'), ((13, ''), 'ausente'), ((13, None), 'ausente'),
                 # exportação que parou no meio numa ficha que ainda era 12: parte da coluna já está congelada
                 ((12, 'exportando'), 'exportando'), ((11, None), None)]
        for (formato, estado), esperado in casos:
            with self.subTest(formato=formato, estado=estado):
                ficha = {'formato.versao': Campo(formato, '', 'cabeçalho')}
                if estado is not None:
                    ficha['analise.estado'] = Campo(estado, '', '')
                self.assertEqual(exportacao_pendente(ficha), esperado)


class Conferencia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.viva = conferir(de_csv(csv_da_ficha(12)), REF)

    def test_12_viva_continua_conferida(self):
        self.assertNotIn(self.viva.veredito, ('formato desconhecido', 'exportação pendente'))

    def test_12_com_estado_viva_igual_a_sem_estado(self):
        resultado = conferir(de_csv(csv_da_ficha(12, 'viva')), REF)
        self.assertEqual(asdict(resultado), asdict(self.viva))

    def test_13_em_dia_confere_igual_a_12_viva(self):
        resultado = conferir(de_csv(csv_da_ficha(13, 'em_dia', EXPORTADA_EM)), REF)
        self.assertEqual(asdict(resultado), asdict(self.viva))
        self.assertFalse([n for n in resultado.nao_conferido if n.startswith('analise.')])

    def test_13_fora_de_em_dia_nao_confere_dado_velho(self):
        for estado in ('desatualizada', 'exportando', None):
            with self.subTest(estado=estado), \
                 patch('closure_bot.ficha_b47.conferir_b47', side_effect=AssertionError('não conferir')):
                resultado = conferir(de_csv(csv_da_ficha(13, estado, EXPORTADA_EM)), REF)
                self.assertEqual(resultado.veredito, 'exportação pendente')
                self.assertEqual([(p.campo, p.esperado, p.encontrado) for p in resultado.problemas],
                                 [('analise.estado', 'em_dia', estado or 'ausente')])

    def test_formato_14_continua_desconhecido(self):
        resultado = conferir(de_csv(csv_da_ficha(14, 'em_dia')), REF)
        self.assertEqual(resultado.veredito, 'formato desconhecido')


class RespostaAoJogador(unittest.IsolatedAsyncioTestCase):
    async def _analisar(self, texto):
        cog = _cog()
        with patch('closure_bot.cogs.ficha.de_link', AsyncMock(return_value=de_csv(texto))), \
             patch('closure_bot.cogs.ficha.conferir', side_effect=AssertionError('não conferir')) as conferiu:
            resposta = await cog.analisar_fonte(link='https://exemplo/ficha', servidor=123)
        return resposta, conferiu

    async def test_desatualizada_pede_exportacao_no_pc_e_no_celular(self):
        resposta, conferiu = await self._analisar(csv_da_ficha(13, 'desatualizada', EXPORTADA_EM))
        conferiu.assert_not_called()
        self.assertIsInstance(resposta, str)
        for trecho in ('editada depois da última exportação', EXPORTADA_EM, 'Bot > Exportar para o bot',
                       'CARTEIRA', 'exportando N/T · marque de novo', 'me chame de novo'):
            self.assertIn(trecho, resposta)

    async def test_exportando_explica_que_parou_no_meio(self):
        resposta, _ = await self._analisar(csv_da_ficha(13, 'exportando'))
        self.assertIn('parou no meio', resposta)
        self.assertNotIn('Última exportação', resposta)
        self.assertIn('Bot > Exportar para o bot', resposta)

    async def test_13_em_dia_vira_painel(self):
        cog = _cog()
        with patch('closure_bot.cogs.ficha.de_link', AsyncMock(return_value=de_csv(csv_da_ficha(13, 'em_dia')))):
            paineis = await cog.analisar_fonte(link='https://exemplo/ficha', servidor=123)
        self.assertIsInstance(paineis, list)
        self.assertTrue(paineis[0].title.startswith('Ficha de'))

    def test_pedido_tem_traducao_inglesa(self):
        from closure_bot.cogs.ficha import MOTIVO_EXPORTACAO, pedido_de_exportacao
        for motivo in (*MOTIVO_EXPORTACAO.values(), 'a ficha não diz se a análise está em dia'):
            self.assertIn(motivo, catalogo())
        with usar('en'):
            texto = pedido_de_exportacao('desatualizada', EXPORTADA_EM)
        self.assertIn('edited after the last export', texto)
        self.assertIn('Bot > Exportar para o bot', texto)
        self.assertNotIn('Exporte e me chame', texto)


if __name__ == '__main__':
    unittest.main()
