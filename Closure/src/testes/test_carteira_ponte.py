"""A ponte mantém o link privado e não aceita redirecionamento de serviço."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import unittest

from carteira_viva.ponte_discord import ConectarFicha


class PonteTeste(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.cog = ConectarFicha(None, "https://carteira.example", "ficticio_" * 5)
        self.i = SimpleNamespace(guild_id=111, user=SimpleNamespace(id=222), locale="pt-BR",
                                 response=SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock()),
                                 followup=SimpleNamespace(send=AsyncMock()))

    async def test_dm_recusada_sem_rede(self):
        self.i.guild_id = None
        with patch("carteira_viva.ponte_discord.aiohttp.ClientSession") as session:
            await self.cog.iniciar(self.i, "cadastro")
        session.assert_not_called()
        self.assertTrue(self.i.response.send_message.call_args.kwargs["ephemeral"])

    async def executar(self, url, status=200):
        resposta = AsyncMock()
        resposta.status = status
        resposta.json.return_value = {"url": url}
        request = AsyncMock()
        request.__aenter__.return_value = resposta
        client = SimpleNamespace(post=lambda *a, **kw: request)
        sessao = AsyncMock()
        sessao.__aenter__.return_value = client
        with patch("carteira_viva.ponte_discord.aiohttp.ClientSession", return_value=sessao):
            await self.cog.iniciar(self.i, "troca", "personagem_ficticio")
        return self.i.followup.send.call_args

    async def test_link_privado_e_defer_privado(self):
        call = await self.executar("https://carteira.example/conectar?ticket=ficticio")
        self.assertTrue(self.i.response.defer.call_args.kwargs["ephemeral"])
        self.assertTrue(call.kwargs["ephemeral"])
        self.assertEqual(call.kwargs["view"].children[0].url, "https://carteira.example/conectar?ticket=ficticio")

    async def test_destino_alheio_nao_chega_ao_usuario(self):
        call = await self.executar("https://outro.example/conectar?ticket=ficticio")
        self.assertNotIn("view", call.kwargs)
        self.assertNotIn("outro.example", call.args[0])
        self.assertTrue(call.kwargs["ephemeral"])

    async def test_falha_em_ingles_sem_expor_resposta(self):
        self.i.locale = "en-US"
        call = await self.executar("https://carteira.example/conectar", status=403)
        self.assertIn("Could not open", call.args[0])
        self.assertNotIn("view", call.kwargs)
