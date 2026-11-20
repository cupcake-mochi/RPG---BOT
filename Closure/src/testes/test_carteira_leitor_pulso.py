"""Leitor do pulso: um GET com máscara de campos e validação estrita; sem Google."""
import asyncio
import json
import unittest

from carteira_viva.leitor_pulso import CAMPOS, ler
from carteira_viva.provedores import ErroProvedor

ARQ = 'a' * 44
OP = 'operacao_sintetica_0001'


def item(rotina, seq=1, quando=1_800_000_000, arq=ARQ):
    return dict(rotina=rotina, operacao=OP, arquivo=arq, sequencia=seq, quando=quando)


def meta(rotina, itens, chave=None, vis='DOCUMENT', local='SPREADSHEET'):
    return dict(metadataKey=chave or 'r53_pulso_' + rotina, metadataValue=json.dumps(dict(versao=1, itens=itens)),
                visibility=vis, location=dict(locationType=local))


class Provedor:
    def __init__(self, metas, sid=ARQ):
        self.obj, self.urls = dict(spreadsheetId=sid, developerMetadata=metas), []

    async def _json(self, url, acesso, **kw):
        self.urls.append(url)
        return self.obj


def rodar(prov, arq=ARQ):
    return asyncio.run(ler(prov, 'acesso-ficticio', arq))


class LeitorPulsoTeste(unittest.TestCase):
    def test_le_pulsos_validos_com_um_get_e_ignora_metadados_alheios(self):
        prov = Provedor([meta('diario', [item('diario', 1), item('diario', 2, 1_800_086_400)]),
                         meta('edicao', [item('edicao')]),
                         dict(metadataKey='outra_coisa', metadataValue='{', visibility='PROJECT')])
        pulsos, problema = rodar(prov)
        self.assertIsNone(problema)
        self.assertEqual([(x.rotina, x.sequencia) for x in pulsos], [('diario', 1), ('diario', 2), ('edicao', 1)])
        self.assertEqual(len(prov.urls), 1)
        self.assertIn('/v4/spreadsheets/' + ARQ + '?fields=', prov.urls[0])
        self.assertNotIn(':', prov.urls[0].split('/v4/spreadsheets/')[1].split('?')[0])  # sem :batchUpdate etc.
        self.assertIn('developerMetadata', CAMPOS)

    def test_sem_metadado_e_lista_vazia(self):
        self.assertEqual(rodar(Provedor([])), ((), None))
        prov = Provedor([]); del prov.obj['developerMetadata']
        self.assertEqual(rodar(prov), ((), None))

    def test_ilegivel_ou_duplicado_nunca_vira_ausencia(self):
        ruins = {
            'project': [meta('diario', [item('diario')], vis='PROJECT')],
            'aba': [meta('diario', [item('diario')], local='SHEET')],
            'rotina_desconhecida': [meta('outra', [item('diario')])],
            'rotina_trocada': [meta('diario', [item('edicao')])],
            'json': [dict(meta('diario', []), metadataValue='{lixo')],
            'vazio': [meta('diario', [])],
            'muitos': [meta('diario', [item('diario', i) for i in range(1, 7)])],
            'campo_extra': [meta('diario', [dict(item('diario'), extra=1)])],
            'sequencia_texto': [meta('diario', [dict(item('diario'), sequencia='1')])],
            'versao': [dict(meta('diario', [item('diario')]), metadataValue=json.dumps(dict(versao=2, itens=[item('diario')])))],
            'grande': [dict(meta('diario', [item('diario')]), metadataValue=' ' * 5000)],
            'lista': None,
        }
        for nome, metas in ruins.items():
            with self.subTest(nome):
                prov = Provedor(metas)
                if metas is None:
                    prov.obj['developerMetadata'] = {'x': 1}
                self.assertEqual(rodar(prov), ((), 'pulso_ilegivel'))
        dup = [meta('diario', [item('diario')]), meta('diario', [item('diario', 2)])]
        self.assertEqual(rodar(Provedor(dup)), ((), 'pulso_duplicado'))

    def test_outra_planilha_ou_id_invalido_recusa(self):
        with self.assertRaises(ErroProvedor):
            rodar(Provedor([], sid='b' * 44))
        with self.assertRaises(ErroProvedor):
            rodar(Provedor([]), arq='curto/../x')


if __name__ == '__main__':
    unittest.main()
