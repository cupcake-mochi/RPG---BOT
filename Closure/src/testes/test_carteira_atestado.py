import unittest

from carteira_viva.atestado_ativacao import (
    ATIVA, AGUARDANDO, INCONSISTENTE, NAO_ATIVADA, PARADA, Pulso, avaliar)
from carteira_viva.segredos import ErroCarteira

OP, ARQ, H = 'op_1', 'arquivo_1', 3600
AGORA = 1_800_000_000.0


def p(rotina, seq, quando, op=OP, arq=ARQ):
    return Pulso(rotina, op, arq, seq, quando)


def ativa():
    return [p('instalacao', 1, AGORA - 20 * H), p('abertura', 1, AGORA - 19 * H),
            p('edicao', 1, AGORA - 19 * H), p('diario', 1, AGORA - 5 * H)]


def avaliar_(pulsos, **kw):
    return avaliar(pulsos, operacao=OP, arquivo=ARQ, agora=AGORA, **kw)


class AtestadoTeste(unittest.TestCase):
    def test_sem_pulso_nao_ativada(self):
        a = avaliar_([])
        self.assertEqual(a.estado, NAO_ATIVADA)
        self.assertFalse(a.ativa)

    def test_so_instalacao_fica_aguardando_e_diz_o_que_falta(self):
        a = avaliar_([p('instalacao', 1, AGORA - H)])
        self.assertEqual(a.estado, AGUARDANDO)
        self.assertFalse(a.ativa)
        for trecho in ('rotina diária', 'abrir a ficha', 'editar a ficha'):
            self.assertIn(trecho, a.motivo)

    def test_tres_rotinas_vistas_ficam_ativas(self):
        a = avaliar_(ativa())
        self.assertEqual(a.estado, ATIVA)
        self.assertTrue(a.ativa)
        b = avaliar_(ativa() + [p('diario', 2, AGORA - H)], anterior=dict(a.maximos))
        self.assertEqual(b.estado, ATIVA)

    def test_pulso_de_outra_operacao_ou_planilha_e_inconsistente(self):
        for extra in (p('diario', 2, AGORA - H, op='op_2'), p('diario', 2, AGORA - H, arq='arquivo_2')):
            self.assertEqual(avaliar_(ativa() + [extra]).estado, INCONSISTENTE)

    def test_sequencia_repetida_ou_voltando_e_inconsistente(self):
        self.assertEqual(avaliar_(ativa() + [p('diario', 1, AGORA - H)]).estado, INCONSISTENTE)
        self.assertEqual(avaliar_(ativa() + [p('diario', 2, AGORA - 30 * H)]).estado, INCONSISTENTE)
        self.assertEqual(avaliar_(ativa(), anterior={'diario': 3}).estado, INCONSISTENTE)

    def test_diario_antigo_ou_que_nunca_rodou_fica_parada(self):
        velho = [x for x in ativa() if x.rotina != 'diario'] + [p('diario', 1, AGORA - 27 * H)]
        self.assertEqual(avaliar_(velho).estado, PARADA)
        nunca = [p('instalacao', 1, AGORA - 27 * H), p('abertura', 1, AGORA - 26.5 * H)]
        self.assertEqual(avaliar_(nunca).estado, PARADA)

    def test_pulso_malformado_ou_no_futuro_nao_conta(self):
        with self.assertRaises(ErroCarteira):
            Pulso.de_dados(dict(rotina='diario', operacao=OP, arquivo=ARQ, sequencia=1, quando=AGORA, extra=1))
        for ruim in (dict(rotina='outra'), dict(sequencia=0), dict(sequencia=True), dict(operacao='a/b')):
            d = dict(rotina='diario', operacao=OP, arquivo=ARQ, sequencia=1, quando=AGORA) | ruim
            with self.assertRaises(ErroCarteira):
                Pulso.de_dados(d)
        with self.assertRaises(ErroCarteira):
            avaliar_([{'rotina': 'diario'}])
        self.assertEqual(avaliar_(ativa() + [p('diario', 2, AGORA + H)]).estado, INCONSISTENTE)


if __name__ == '__main__':
    unittest.main()
