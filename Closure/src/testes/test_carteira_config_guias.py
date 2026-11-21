import unittest
from pathlib import Path
import tempfile

from closure_bot.config import carregar


def _carregar(**extra):
    pasta = Path(tempfile.mkdtemp())
    return carregar(pasta / "nao_existe", ambiente={"DISCORD_TOKEN": "x", "BANCO": str(pasta / "b.sqlite3"), **extra})


class ConfigCarteiraNasGuias(unittest.TestCase):
    def test_sem_variaveis_fica_desligado(self):
        c = _carregar()
        self.assertEqual((c.carteira_url, c.carteira_token), ("", ""))

    def test_as_duas_variaveis_vem_juntas(self):
        with self.assertRaises(ValueError):
            _carregar(CARTEIRA_API_URL="https://carteira.exemplo")
        with self.assertRaises(ValueError):
            _carregar(CARTEIRA_SERVICE_TOKEN="s" * 40)

    def test_origem_sem_barra_final_e_segredo_fora_do_repr(self):
        c = _carregar(CARTEIRA_API_URL=" https://carteira.exemplo/ ", CARTEIRA_SERVICE_TOKEN="segredo-" + "s" * 40)
        self.assertEqual(c.carteira_url, "https://carteira.exemplo")
        self.assertNotIn("segredo-", repr(c))


if __name__ == "__main__":
    unittest.main()
