"""Ponte pro prompt do site: o aviso de repetição vale de uma conversa pra outra, e o estado do bot entra no pedido.

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


@unittest.skipUnless(PRONTO, "sem Node ou sem a página do site baixada")
class EstadoDoBot(unittest.TestCase):
    ESTADO = {"bloco": "[Estado agora: plantão; 22:10 em Brasília; canal cheio; carga 2.\nQuem fala: rafa (pronomes: ele/dele).]",
              "lembretes": ["Carga alta: uma frase, sem piada.", "Paciência baixa com esta pessoa.", "Pessoa nova: forma neutra."]}

    def _ultimo(self, hora, **extra):
        return site_prompt.montar("clo", "closure, o que é Integridade?", nome="rafa", hora=hora, **extra)["input"][-1]["content"]

    def test_sem_estado_fica_o_da_pagina(self):
        self.assertIn("canal normal; carga 0.", self._ultimo((22, 10)))

    def test_o_bloco_do_bot_entra_no_lugar_do_da_pagina(self):
        ultimo = self._ultimo((22, 10), estado=self.ESTADO)
        self.assertIn(self.ESTADO["bloco"] + "\n\n[Mensagem]", ultimo)
        self.assertNotIn("canal normal; carga 0.", ultimo)
        self.assertEqual(ultimo.count("[Estado agora:"), 1)

    def test_no_plantao_entram_duas_linhas_no_fim_do_lembrete(self):
        ultimo = self._ultimo((22, 10), estado=self.ESTADO)
        self.assertTrue(ultimo.endswith("]\n[Carga alta: uma frase, sem piada.]\n[Paciência baixa com esta pessoa.]"), ultimo[-200:])

    def test_fora_do_plantao_a_linha_da_pagina_vem_antes_e_sobra_uma(self):
        ultimo = self._ultimo((14, 0), estado=self.ESTADO)
        self.assertRegex(ultimo, r"\[Fora do plantão: [^\]]+\]\n\[Carga alta: uma frase, sem piada\.\]$")
        self.assertNotIn("Paciência baixa", ultimo)


if __name__ == "__main__":
    unittest.main()
