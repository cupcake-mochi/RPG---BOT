"""Guia navega sem executar as operações que ensina e respeita os limites do Discord."""
import unittest
from unittest.mock import AsyncMock, MagicMock

from closure_bot import guias
from closure_bot.cogs.guias import GuiaNavegavel, Guias


def interacao():
    i = MagicMock()
    i.response.send_message = AsyncMock()
    i.response.edit_message = AsyncMock()
    i.original_response = AsyncMock()
    i.edit_original_response = AsyncMock()
    return i


class ConteudoDosGuias(unittest.TestCase):
    def test_atalhos_e_limites_das_paginas(self):
        for entrada, esperado in ((None, "geral"), ("  ", "geral"), ("MÍDIA", "midia"),
                                  ("aprovação", "custom"), ("Análise", "ficha"), ("inexistente", None)):
            self.assertEqual(guias.assunto(entrada), esperado)
        for tema in guias.ASSUNTOS:
            paginas = guias.paginas(tema)
            self.assertGreater(len(paginas), 0)
            for p in paginas:
                self.assertLessEqual(len(p), 6000)
                self.assertLessEqual(len(p.description), 4096)
                self.assertLessEqual(len(p.title), 256)
                self.assertTrue(p.footer.text.split(" · ")[1])

    def test_limites_humanos_e_custom_continuam_explicitos(self):
        textos = "\n".join(p.description for tema in ("ficha", "custom") for p in guias.paginas(tema))
        for trecho in ("Zero erros não é aprovação", "MESTRE VIU", "definição exata", "sem recálculo independente",
                       "Alma", "histórico", "prosa em bônus", "estados ativos"):
            self.assertIn(trecho, textos)


class NavegacaoDosGuias(unittest.IsolatedAsyncioTestCase):
    async def test_troca_assunto_reinicia_pagina_e_atualiza_botoes(self):
        v = GuiaNavegavel("ficha")
        self.addCleanup(v.stop)
        self.assertEqual([v.assuntos.row, v.seletor.row, v.proxima.row], [0, 1, 2])
        i = interacao()
        await v.ultima.callback(i)
        self.assertEqual(v.indice, len(v.paginas) - 1)
        self.assertTrue(v.proxima.disabled)
        v.assuntos._values = ["clima"]
        await v.assuntos.callback(i)
        self.assertEqual((v.tema, v.indice, len(v.paginas)), ("clima", 0, 1))
        self.assertTrue(v.seletor.disabled)
        self.assertFalse(v.assuntos.disabled)
        self.assertTrue(v.primeira.disabled and v.proxima.disabled)
        self.assertEqual(i.response.edit_message.call_args.kwargs["allowed_mentions"].to_dict()["parse"], [])
        v.assuntos._values = ["memoria"]
        await v.assuntos.callback(i)
        self.assertFalse(v.proxima.disabled)
        await v.mostrar(i, 100)
        self.assertEqual(v.indice, 1)
        await v.mostrar(i, -100)
        self.assertEqual(v.indice, 0)

    async def test_timeout_explica_como_reabrir_sem_pedir_nova_analise(self):
        v = GuiaNavegavel("ficha")
        v.mensagem = MagicMock(edit=AsyncMock())
        await v.on_timeout()
        self.assertTrue(all(item.disabled for item in v.children))
        rodape = v.mensagem.edit.call_args.kwargs["embed"].footer.text
        self.assertIn("/guia", rodape)
        self.assertNotIn("rode a análise", rodape)
        i = interacao()
        await v.mostrar(i, 1)
        v.assuntos._values = ["clima"]
        await v.assuntos.callback(i)
        i.response.edit_message.assert_not_awaited()
        self.assertEqual(v.tema, "ficha")
        self.assertEqual(i.response.send_message.await_count, 2)

    async def test_barra_e_privada_e_nao_consulta_bot(self):
        bot = MagicMock()
        c = Guias(bot)
        i = interacao()
        await c.guia.callback(c, i, "custom")
        chamada = i.response.send_message.call_args
        self.assertTrue(chamada.kwargs["ephemeral"])
        self.assertIs(chamada.kwargs["view"].mensagem, i.original_response.return_value)
        self.addCleanup(chamada.kwargs["view"].stop)
        self.assertEqual(bot.mock_calls, [])
        i = interacao()
        await c.pela_barra(i, "@everyone")
        self.assertNotIn("@everyone", i.response.send_message.call_args.args[0])
        self.assertNotIn("view", i.response.send_message.call_args.kwargs)
