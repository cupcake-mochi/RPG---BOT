"""Excluir personagem e apagar dados pelo Discord: confirmação de quem pediu, nada sem clicar."""
import unittest
from unittest.mock import AsyncMock, MagicMock

try:
    import discord
except ImportError:  # pragma: no cover
    discord = None


def _interacao(usuario=222):
    i = MagicMock()
    i.guild_id, i.user.id = 111, usuario
    i.response.defer = AsyncMock(); i.response.send_message = AsyncMock(); i.response.edit_message = AsyncMock()
    i.followup.send = AsyncMock()
    return i


@unittest.skipIf(discord is None, "discord.py não instalado")
class ExclusaoPeloDiscord(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from carteira_viva.ponte_discord import ConectarFicha
        self.cog = ConectarFicha(None, "https://carteira.exemplo", "s" * 40)
        self.cog.api.pedir = AsyncMock()
        self.pid = "a" * 32

    def view(self, i):
        return i.followup.send.call_args.kwargs["view"]

    async def test_excluir_pergunta_antes_e_so_apaga_no_clique_do_dono(self):
        self.cog.api.pedir.return_value = {"responsavel": "222", "perfil": {"nome": "Ayla"}}
        i = _interacao()
        await self.cog.pedir_exclusao(i, self.pid)
        self.assertEqual([c.args[2] for c in self.cog.api.pedir.call_args_list], ["cartao_salvo"])
        self.assertIn("Ayla", i.followup.send.call_args.args[0])
        view = self.view(i)
        self.assertFalse(await view.interaction_check(_interacao(999)))
        self.assertTrue(await view.interaction_check(_interacao()))
        clique = _interacao()
        await view.confirmar(clique)
        chamada = self.cog.api.pedir.call_args
        self.assertEqual(chamada.args[2], "excluir")
        self.assertEqual(chamada.kwargs["personagem"], self.pid)
        self.assertRegex(chamada.kwargs["pedido"], "^[0-9a-f]{32}$")
        self.assertIn("excluído", clique.followup.send.call_args.args[0])

    async def test_excluir_personagem_alheio_nem_oferece_o_botao(self):
        self.cog.api.pedir.return_value = {"responsavel": "999", "perfil": {"nome": "Outro"}}
        i = _interacao()
        await self.cog.pedir_exclusao(i, self.pid)
        self.assertNotIn("view", i.followup.send.call_args.kwargs)
        self.assertEqual(self.cog.api.pedir.await_count, 1)

    async def test_apagar_dados_cancelar_nao_chama_o_servico(self):
        i = _interacao()
        await self.cog.pedir_apagar_dados(i)
        self.cog.api.pedir.assert_not_awaited()
        clique = _interacao()
        await self.view(i).cancelar(clique)
        self.cog.api.pedir.assert_not_awaited()
        self.assertIn("Nada foi apagado", clique.response.edit_message.call_args.kwargs["content"])

    async def test_apagar_dados_confirmado(self):
        i = _interacao()
        await self.cog.pedir_apagar_dados(i)
        clique = _interacao()
        await self.view(i).confirmar(clique)
        self.assertEqual(self.cog.api.pedir.call_args.args, (111, 222, "apagar_meus_dados"))
        self.assertIn("myaccount.google.com/permissions", clique.followup.send.call_args.args[0])

    async def test_cliente_so_aceita_as_novas_acoes_no_formato_certo(self):
        from carteira_viva.cliente_discord import ClienteCarteira, FalhaCarteira
        api = ClienteCarteira("https://carteira.exemplo", "s" * 40)
        with self.assertRaises(FalhaCarteira):
            await api.pedir(1, 2, "excluir")
        with self.assertRaises(FalhaCarteira):
            await api.pedir(1, 2, "apagar_meus_dados", personagem=self.pid)


if __name__ == "__main__":
    unittest.main()
