import unittest

from carteira_viva.atestado_ativacao import (
    ATIVA, AGUARDANDO, CODIGOS, INCONSISTENTE, NAO_ATIVADA, PARADA, Pulso, avaliar, ilegivel)
from carteira_viva.textos_ativacao import passos, risco_escrita, texto_estado
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


class CodigoTeste(unittest.TestCase):
    """O código escolhe o texto PT/EN; cada caminho do classificador tem um."""
    def test_cada_estado_tem_codigo_proprio(self):
        casos = [
            ([], 'sem_pulso'),
            ([p('instalacao', 1, AGORA - H)], 'falta'),
            (ativa(), 'ativa'),
            (ativa() + [p('diario', 2, AGORA - H, op='op_2')], 'outra_operacao'),
            (ativa() + [p('diario', 2, AGORA - H, arq='arquivo_2')], 'copia_de_outra_ficha'),
            (ativa() + [p('diario', 2, AGORA + H)], 'horario_futuro'),
            (ativa() + [p('diario', 1, AGORA - H)], 'sequencia_repetida'),
            (ativa() + [p('diario', 2, AGORA - 30 * H)], 'fora_de_ordem'),
            ([x for x in ativa() if x.rotina != 'diario'] + [p('diario', 1, AGORA - 27 * H)], 'diario_atrasado'),
            ([p('instalacao', 1, AGORA - 27 * H)], 'diario_nunca_rodou'),
        ]
        for pulsos, codigo in casos:
            with self.subTest(codigo=codigo):
                a = avaliar_(pulsos)
                self.assertEqual(a.codigo, codigo)
                self.assertIn(a.codigo, CODIGOS)
        self.assertEqual(avaliar_(ativa(), anterior={'diario': 3}).codigo, 'contador_voltou')

    def test_falta_lista_so_o_que_o_jogador_ainda_precisa_fazer(self):
        a = avaliar_([p('instalacao', 1, AGORA - H), p('abertura', 1, AGORA - H)])
        self.assertEqual(a.faltam, ('diario', 'edicao'))

    def test_leitura_ilegivel_nunca_vira_ausencia_de_pulso(self):
        for codigo in ('pulso_ilegivel', 'pulso_duplicado'):
            self.assertEqual(ilegivel(codigo).estado, INCONSISTENTE)
        with self.assertRaises(ErroCarteira):
            ilegivel('sem_pulso')


class TextosTeste(unittest.TestCase):
    def test_todo_codigo_tem_texto_pt_e_en_e_motivo_da_falta(self):
        for codigo in CODIGOS:
            d = dict(estado=ATIVA, codigo=codigo, faltam=['diario', 'edicao'], lido_em=AGORA - 600)
            pt, en = texto_estado(d, 'pt-BR', AGORA), texto_estado(d, 'en', AGORA)
            self.assertNotEqual(pt, en)
            self.assertIn('10 min', pt)
        d = dict(estado=AGUARDANDO, codigo='falta', faltam=['diario', 'edicao'], lido_em=AGORA)
        self.assertIn('3h', texto_estado(d, 'pt-BR', AGORA))
        self.assertIn('editar', texto_estado(d, 'pt-BR', AGORA))
        self.assertIn('agora', texto_estado(d, 'pt-BR', AGORA))
        self.assertNotIn('abrir', texto_estado(d, 'pt-BR', AGORA))

    def test_passos_e_aviso_de_risco_nos_dois_idiomas(self):
        self.assertEqual(len(passos('pt-BR')), len(passos('en')))
        self.assertIn('3h', ' '.join(passos('pt-BR')))
        self.assertIn('pode se perder', risco_escrita('pt-BR'))
        self.assertIn('may be lost', risco_escrita('en'))
        with self.assertRaises(ErroCarteira):
            passos('fr')
        with self.assertRaises(ErroCarteira):
            texto_estado(dict(estado='outro', codigo='ativa', lido_em=AGORA), 'pt-BR', AGORA)


if __name__ == '__main__':
    unittest.main()
