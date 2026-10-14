"""Regra de plantão: quem responde, por horário e por nome. Rodar de src/:  python3 -m unittest discover -s testes"""
import unittest
from datetime import datetime, timezone

from closure_bot.plantao import CLOSURE, FUSO, KALTSIT, de_plantao, decidir, nomes_chamados


def hora(h, m=0):
    return datetime(2026, 10, 13, h, m, tzinfo=FUSO)


class Turnos(unittest.TestCase):
    def test_viradas(self):
        self.assertEqual(de_plantao(hora(8, 59)), CLOSURE)
        self.assertEqual(de_plantao(hora(9, 0)), KALTSIT)
        self.assertEqual(de_plantao(hora(20, 59)), KALTSIT)
        self.assertEqual(de_plantao(hora(21, 0)), CLOSURE)
        self.assertEqual(de_plantao(hora(3, 40)), CLOSURE)

    def test_converte_de_outro_fuso(self):
        # 12h em UTC são 9h em Brasília
        self.assertEqual(de_plantao(datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)), KALTSIT)
        self.assertEqual(de_plantao(datetime(2026, 10, 13, 11, 59, tzinfo=timezone.utc)), CLOSURE)


class Nomes(unittest.TestCase):
    def test_formas_do_nome(self):
        for texto in ("kal, o que é Integridade?", "Kal'tsit, tudo bem?", "KALTSIT me ajuda", "oi kal’tsit", "e aí Kal"):
            self.assertEqual(nomes_chamados(texto), [KALTSIT], texto)
        for texto in ("oi closure", "Closure!", "closure, o que é Refino?", "valeu, CLOSURE."):
            self.assertEqual(nomes_chamados(texto), [CLOSURE], texto)

    def test_nao_acha_dentro_de_outra_palavra(self):
        for texto in ("o kalango fugiu", "disclosure do contrato", "calma aí", "enclosures"):
            self.assertEqual(nomes_chamados(texto), [], texto)

    def test_ordem_em_que_aparecem(self):
        self.assertEqual(nomes_chamados("closure, a kal'tsit falou isso"), [CLOSURE, KALTSIT])
        self.assertEqual(nomes_chamados("a kal disse que a closure sabe"), [KALTSIT, CLOSURE])


class Decisoes(unittest.TestCase):
    def test_ninguem_chamado(self):
        self.assertIsNone(decidir("alguém sabe quanto custa a Técnica Máxima?", hora(22)))

    def test_nome_no_turno(self):
        d = decidir("closure, o que é Integridade?", hora(22))
        self.assertEqual((d.persona, d.motivo, d.fora_do_plantao), (CLOSURE, "nome", False))

    def test_nome_fora_do_turno_responde_a_propria(self):
        d = decidir("closure vc tá aí?", hora(14, 12))
        self.assertEqual((d.persona, d.fora_do_plantao), (CLOSURE, True))
        d = decidir("kal, o que é Integridade?", hora(23))
        self.assertEqual((d.persona, d.fora_do_plantao), (KALTSIT, True))

    def test_mencao_sem_nome_vai_pra_quem_esta_de_plantao(self):
        d = decidir("<@123> como funciona o descanso?", hora(10), mencionou_bot=True)
        self.assertEqual((d.persona, d.motivo, d.fora_do_plantao), (KALTSIT, "mencao", False))
        d = decidir("<@123> como funciona o descanso?", hora(2), mencionou_bot=True)
        self.assertEqual(d.persona, CLOSURE)

    def test_resposta_sem_nome_vai_pra_quem_esta_de_plantao(self):
        d = decidir("mas e no descanso longo?", hora(15), respondeu_ao_bot=True)
        self.assertEqual((d.persona, d.motivo), (KALTSIT, "resposta"))

    def test_nome_vence_mencao_e_resposta(self):
        d = decidir("closure, e você, concorda?", hora(15), respondeu_ao_bot=True, mencionou_bot=True)
        self.assertEqual((d.persona, d.motivo, d.fora_do_plantao), (CLOSURE, "nome", True))

    def test_as_duas_citadas_vale_quem_abre_a_mensagem(self):
        d = decidir("closure, a kal'tsit falou de tarde que eu devia refazer a ficha. vc concorda?", hora(22, 10))
        self.assertEqual(d.persona, CLOSURE)
        d = decidir("closure, a kal'tsit falou que eu devia refazer a ficha", hora(14))
        self.assertEqual((d.persona, d.fora_do_plantao), (CLOSURE, True))
        d = decidir("<@123> kal, a closure disse outra coisa ontem", hora(22), mencionou_bot=True)
        self.assertEqual((d.persona, d.fora_do_plantao), (KALTSIT, True))

    def test_as_duas_citadas_sem_vocativo_vai_pra_quem_esta_de_plantao(self):
        d = decidir("quem é mais legal, a kal ou a closure?", hora(22))
        self.assertEqual((d.persona, d.fora_do_plantao), (CLOSURE, False))
        d = decidir("quem é mais legal, a kal ou a closure?", hora(10))
        self.assertEqual(d.persona, KALTSIT)


class RespostaAUmaFala(unittest.TestCase):
    """Quem responde a uma fala continua com quem a disse, mesmo fora do plantão dela."""

    def test_resposta_a_fala_dela_fica_com_ela(self):
        from datetime import datetime

        from closure_bot.plantao import CLOSURE, FUSO, KALTSIT, decidir

        noite = datetime(2026, 10, 13, 23, 0, tzinfo=FUSO)
        d = decidir("mas e no descanso longo?", noite, respondeu_ao_bot=True, respondeu_a=KALTSIT)
        self.assertEqual((d.persona, d.motivo, d.fora_do_plantao), (KALTSIT, "resposta", True))
        # nome escrito na mensagem vale mais do que a fala respondida
        self.assertEqual(decidir("closure, e você, concorda?", noite, respondeu_ao_bot=True, respondeu_a=KALTSIT).persona, CLOSURE)
        # resposta a mensagem do bot que não é fala de ninguém (o painel de clima): quem está de plantão
        self.assertEqual(decidir("que frio", noite, respondeu_ao_bot=True).persona, CLOSURE)
        self.assertEqual(decidir("que frio", noite, respondeu_ao_bot=True, respondeu_a="outra coisa").persona, CLOSURE)


if __name__ == "__main__":
    unittest.main()
