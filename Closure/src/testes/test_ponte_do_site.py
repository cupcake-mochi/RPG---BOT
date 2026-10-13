"""Ponte pro prompt do site: o aviso de repetição vale de uma conversa pra outra.

Precisa do Node e da página do site já baixada (src/var/site/nucleo.js); sem um dos dois, os testes são pulados.
Rodar de src/:  python3 -m unittest discover -s testes
"""
import shutil
import sys
import unittest
from pathlib import Path

PONTE = Path(__file__).resolve().parents[2] / "ferramentas" / "prompt_do_site"
sys.path.insert(0, str(PONTE))
import site_prompt  # noqa: E402

PRONTO = shutil.which("node") is not None and (site_prompt.CACHE / "nucleo.js").exists()
AVISO = "Você já usou nas suas últimas respostas:"


@unittest.skipUnless(PRONTO, "sem Node ou sem a página do site baixada")
class AvisoDeRepeticao(unittest.TestCase):
    def _ultimo(self, **extra):
        return site_prompt.montar("kal", "kal, tudo bem?", nome="rafa", hora=(14, 20), **extra)["input"][-1]["content"]

    def test_conversa_nova_sem_falas_nao_tem_aviso(self):
        self.assertNotIn("Você já usou", self._ultimo())

    def test_frase_repetida_em_conversas_anteriores_vira_aviso(self):
        falas = ["Tudo em ordem por aqui.", "Boa tarde. Tudo em ordem por aqui.", "O custo é esse mesmo."]
        ultimo = self._ultimo(falas_anteriores=falas)
        self.assertIn(AVISO, ultimo)
        self.assertIn('"Tudo em ordem por aqui"', ultimo)
        self.assertNotIn("nesta conversa:", ultimo.split(AVISO)[1])

    def test_fala_que_nao_se_repete_nao_vira_aviso(self):
        self.assertNotIn("Você já usou", self._ultimo(falas_anteriores=["Tudo em ordem por aqui.", "O custo é esse mesmo."]))

    def test_as_falas_anteriores_nao_entram_como_conversa(self):
        montado = site_prompt.montar("kal", "kal, tudo bem?", nome="rafa", hora=(14, 20),
                                     falas_anteriores=["Tudo em ordem por aqui.", "Tudo em ordem por aqui."])
        self.assertEqual(len(montado["input"]), 2)  # só o prompt de sistema e a mensagem atual

    def test_o_aviso_junta_a_conversa_atual_sem_duplicar(self):
        turnos = [{"de": "user", "nome": "rafa", "texto": "oi"}, {"de": "bot", "pers": "kal", "texto": "Tudo em ordem por aqui."}]
        ultimo = self._ultimo(turnos=turnos, falas_anteriores=["Tudo em ordem por aqui."])
        self.assertEqual(ultimo.count("Você já usou"), 1)
        self.assertIn(AVISO, ultimo)


if __name__ == "__main__":
    unittest.main()
