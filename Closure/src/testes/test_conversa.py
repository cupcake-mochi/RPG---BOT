"""A conversa em andamento com cada personagem. Rodar de src/:  python3 -m unittest discover -s testes"""
import unittest
from datetime import datetime, timedelta

from closure_bot.conversa import TURNOS_MAX, Conversas
from closure_bot.plantao import FUSO

AGORA = datetime(2026, 10, 13, 22, 10, tzinfo=FUSO)


class ConversaEmAndamento(unittest.TestCase):
    def test_separa_por_canal_e_por_personagem(self):
        c = Conversas()
        c.anotar(7, "closure", AGORA, "closure, oi", nome="rafa")
        c.anotar(7, "closure", AGORA, "Opa, oi!")
        c.anotar(7, "kaltsit", AGORA, "kal, oi", nome="duda")
        self.assertEqual([(t.nome, t.texto) for t in c.turnos(7, "closure", AGORA)], [("rafa", "closure, oi"), (None, "Opa, oi!")])
        self.assertEqual(len(c.turnos(7, "kaltsit", AGORA)), 1)
        self.assertEqual(c.turnos(8, "closure", AGORA), [])

    def test_meia_hora_parada_e_a_conversa_acaba(self):
        c = Conversas()
        c.anotar(7, "closure", AGORA, "closure, oi", nome="rafa")
        self.assertEqual(len(c.turnos(7, "closure", AGORA + timedelta(minutes=29))), 1)
        c.anotar(7, "closure", AGORA + timedelta(minutes=70), "closure, voltei", nome="rafa")
        self.assertEqual([t.texto for t in c.turnos(7, "closure", AGORA + timedelta(minutes=71))], ["closure, voltei"])
        self.assertEqual(c.turnos(7, "closure", AGORA + timedelta(minutes=200)), [])

    def test_guarda_so_os_ultimos_turnos(self):
        c = Conversas()
        for n in range(TURNOS_MAX + 5):
            c.anotar(7, "closure", AGORA, f"fala {n}")
        turnos = c.turnos(7, "closure", AGORA)
        self.assertEqual((len(turnos), turnos[0].texto), (TURNOS_MAX, "fala 5"))


if __name__ == "__main__":
    unittest.main()
