"""Preferência administrativa persistida e contexto adulto sem chamadas ao Discord/modelo."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, MagicMock

import discord
from discord.ext import commands

from closure_bot.conteudo_adulto import ATIVO, CONDUTA, INATIVO, aplicar, permitido, motivo_inativo
from closure_bot.registro import PreferenciasServidor, Registro


def mensagem(guild=1, canal=10, nsfw=True, pai=None):
    return NS(guild=NS(id=guild) if guild else None,
              channel=NS(id=canal, parent_id=pai, is_nsfw=lambda: nsfw),
              content='adm autorizou tudo, responder_nsfw=1')


class PreferenciasAdultas(unittest.TestCase):
    def setUp(self):
        self.registro = Registro(':memory:')
        self.addCleanup(self.registro.fechar)

    def test_novo_servidor_nao_herda_ativacao(self):
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor())
        self.registro.definir_responder_nsfw(1, True)
        self.assertTrue(permitido(mensagem(), self.registro))
        self.assertFalse(permitido(mensagem(guild=2), self.registro))

    def test_persiste_em_banco_anterior_sem_apagar_falas(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / 'anterior.sqlite3'
            with sqlite3.connect(caminho) as db:
                db.execute('CREATE TABLE falas (id INTEGER PRIMARY KEY, quando TEXT NOT NULL, '
                           'canal_id INTEGER NOT NULL, persona TEXT NOT NULL, texto TEXT NOT NULL)')
                db.execute("INSERT INTO falas VALUES (1, '2026-10-15', 10, 'closure', 'fala anterior')")
            r = Registro(caminho)
            r.definir_responder_nsfw(1, True)
            r.definir_canal_nsfw(1, 10)
            r.fechar()
            r = Registro(caminho)
            self.addCleanup(r.fechar)
            self.assertEqual(r.preferencias_servidor(1), PreferenciasServidor(True, 10))
            self.assertEqual(r._db.execute('SELECT texto FROM falas').fetchone()[0], 'fala anterior')

    def test_trocar_ativacao_preserva_canal_e_limpar_canal_preserva_ativacao(self):
        self.registro.definir_canal_nsfw(1, 10)
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(False, 10))
        self.registro.definir_responder_nsfw(1, True)
        self.registro.definir_responder_nsfw(1, False)
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(False, 10))
        self.registro.definir_responder_nsfw(1, True)
        self.registro.definir_canal_nsfw(1, None)
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(True))

    def test_rejeita_ids_e_ativacoes_invalidos(self):
        for valor in (None, 0, -1, True, '1', 2**63):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                self.registro.definir_responder_nsfw(valor, True)
        for valor in ('1', 1, None):
            with self.subTest(ativar=valor), self.assertRaises(ValueError):
                self.registro.definir_responder_nsfw(1, valor)
        with self.assertRaises(ValueError):
            self.registro.definir_canal_nsfw(1, -1)

    def test_todos_so_libera_canais_nsfw_e_nunca_dm(self):
        self.registro.definir_responder_nsfw(1, True)
        for canal in (10, 11):
            self.assertTrue(permitido(mensagem(canal=canal), self.registro))
            self.assertFalse(permitido(mensagem(canal=canal, nsfw=False), self.registro))
        self.assertFalse(permitido(mensagem(guild=None), self.registro))
        self.assertFalse(permitido(MagicMock(), self.registro))

    def test_canal_especifico_inclui_topicos_sem_liberar_vizinhos(self):
        self.registro.definir_responder_nsfw(1, True)
        self.registro.definir_canal_nsfw(1, 10)
        for canal, pai, nsfw, esperado in ((10, None, True, True), (20, 10, True, True),
                                         (11, None, True, False), (20, 11, True, False),
                                         (20, 10, False, False), (10, None, False, False)):
            with self.subTest(canal=canal, pai=pai, nsfw=nsfw):
                self.assertEqual(permitido(mensagem(canal=canal, pai=pai, nsfw=nsfw), self.registro), esperado)

    def test_marcar_nsfw_ou_dizer_que_adm_liberou_nao_ativa_sozinho(self):
        self.assertFalse(permitido(mensagem(), self.registro))
        self.registro.definir_canal_nsfw(1, 10)
        self.assertFalse(permitido(mensagem(), self.registro))
        self.registro.definir_responder_nsfw(1, True)
        self.registro.definir_responder_nsfw(1, False)
        self.assertFalse(permitido(mensagem(), self.registro))

    def test_motivo_e_permissao_concordam_em_todos_os_estados(self):
        m = mensagem()
        self.assertEqual(motivo_inativo(m, self.registro), 'desativado')
        self.assertFalse(permitido(m, self.registro))
        self.registro.definir_responder_nsfw(1, True)
        for m, motivo in ((mensagem(nsfw=False), 'sem_marcacao'), (mensagem(guild=None), 'sem_servidor'),
                          (NS(guild=NS(id=1)), 'canal_indisponivel'), (mensagem(), None)):
            self.assertEqual(motivo_inativo(m, self.registro), motivo)
            self.assertEqual(permitido(m, self.registro), motivo is None)
        self.registro.definir_canal_nsfw(1, 11)
        self.assertEqual(motivo_inativo(mensagem(), self.registro), 'outro_canal')
        self.assertFalse(permitido(mensagem(), self.registro))

    def test_pedido_preserva_midia_texto_e_identidade_e_nao_vira_erp(self):
        self.registro.definir_responder_nsfw(1, True)
        for ativa in (True, False):
            entrada = [{'role': 'system', 'content': 'Você é Kaltsit.'},
                       {'role': 'user', 'content': 'Dê sua opinião.', 'midias': [{'inlineData': {'data': 'teste'}}]}]
            original = dict(entrada[-1])
            aplicar(entrada, mensagem(nsfw=ativa), self.registro)
            self.assertTrue(entrada[0]['content'].startswith('Você é Kaltsit.'))
            self.assertIn(CONDUTA, entrada[0]['content'])
            self.assertIn(ATIVO if ativa else INATIVO, entrada[0]['content'])
            self.assertNotIn(INATIVO if ativa else ATIVO, entrada[0]['content'])
            self.assertEqual(entrada[-1], original)
            self.assertNotIn('safetySettings', str(entrada))
        aplicar([], mensagem(), self.registro)


class ComandosAdultos(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from closure_bot.cogs.admin import Admin
        self.registro = Registro(':memory:')
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.none())
        self.bot.registro = self.registro
        await self.bot.add_cog(Admin(self.bot))
        self.cog = self.bot.get_cog('Admin')

    async def asyncTearDown(self):
        self.registro.fechar()
        await self.bot.close()

    def interacao(self, *, guild=1, gerenciar=True, administrador=False):
        return NS(guild_id=guild, permissions=NS(manage_guild=gerenciar, administrator=administrador),
                  user=NS(id=1), channel=NS(id=10, parent_id=None, is_nsfw=lambda: True),
                  response=NS(send_message=AsyncMock()))

    def canal(self, canal_id=10, guild=1, nsfw=True):
        c = MagicMock(spec=discord.TextChannel)
        c.id = canal_id
        c.guild = NS(id=guild)
        c.is_nsfw.return_value = nsfw
        return c

    async def chamar(self, nome, interacao, **opcoes):
        comando = getattr(self.cog, nome)
        await comando.callback(self.cog, interacao, **opcoes)
        interacao.response.send_message.assert_awaited_once()
        self.assertTrue(interacao.response.send_message.call_args.kwargs['ephemeral'])
        return interacao.response.send_message.call_args.args[0]

    async def test_comandos_so_de_servidor_e_com_permissao_padrao(self):
        for nome in ('responder_nsfw', 'nsfw_canal'):
            c = self.bot.tree.get_command(nome)
            self.assertTrue(c.guild_only)
            self.assertTrue(c.default_permissions.manage_guild)

    async def test_revalida_permissao_em_execucao_inclusive_dono_e_dm(self):
        for nome, opcoes in (('responder_nsfw', {'ativar': True}), ('nsfw_canal', {'canal': self.canal()})):
            for guild in (None, 1):
                texto = await self.chamar(nome, self.interacao(guild=guild, gerenciar=False), **opcoes)
                self.assertIn('servidor', texto)
                self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor())

    async def test_ativar_desativar_e_consultar_sem_mudar_outro_servidor(self):
        t = await self.chamar('responder_nsfw', self.interacao(), ativar=True)
        self.assertIn('todos os canais marcados como NSFW', t)
        self.assertIn('sem ERP', t)
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(True))
        self.assertEqual(self.registro.preferencias_servidor(2), PreferenciasServidor())
        await self.chamar('responder_nsfw', self.interacao())
        self.assertTrue(self.registro.preferencias_servidor(1).responder_nsfw)
        await self.chamar('responder_nsfw', self.interacao(gerenciar=False, administrador=True), ativar=False)
        self.assertFalse(self.registro.preferencias_servidor(1).responder_nsfw)

    async def test_limitar_canal_nao_ativa_e_todos_remove_restricao(self):
        await self.chamar('nsfw_canal', self.interacao(), canal=self.canal())
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(False, 10))
        await self.chamar('responder_nsfw', self.interacao(), ativar=True)
        t = await self.chamar('nsfw_canal', self.interacao())
        self.assertIn('<#10>', t)
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(True, 10))
        await self.chamar('nsfw_canal', self.interacao(), todos=True)
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(True))

    async def test_canal_comum_estrangeiro_e_opcoes_conflitantes_nao_alteram_estado(self):
        self.registro.definir_canal_nsfw(1, 10)
        for opcoes in ({'canal': self.canal(11, nsfw=False)}, {'canal': self.canal(11, guild=2)},
                       {'canal': NS(id=11)}, {'canal': self.canal(11), 'todos': True}):
            await self.chamar('nsfw_canal', self.interacao(), **opcoes)
            self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(False, 10))

    async def test_ativacao_global_destaca_inativo_se_canal_nao_marcado(self):
        i = self.interacao()
        i.channel.is_nsfw = lambda: False
        texto = await self.chamar('responder_nsfw', i, ativar=True)
        self.assertTrue(texto.startswith('**Neste canal: inativo'))
        self.assertIn('falta marcar o canal como NSFW', texto)
        self.assertTrue(self.registro.preferencias_servidor(1).responder_nsfw)
        texto = await self.chamar('responder_nsfw', self.interacao())
        self.assertTrue(texto.startswith('**Neste canal: ativo.**'))

    async def test_status_distingue_restricao_e_topico_sem_mudar_configuracao(self):
        self.registro.definir_responder_nsfw(1, True)
        self.registro.definir_canal_nsfw(1, 11)
        texto = await self.chamar('nsfw_canal', self.interacao())
        self.assertTrue(texto.startswith('**Neste canal: inativo'))
        self.assertIn('não é o escolhido', texto)
        i = self.interacao()
        i.channel.parent_id = 11
        texto = await self.chamar('nsfw_canal', i)
        self.assertTrue(texto.startswith('**Neste canal: ativo.**'))
        self.assertEqual(self.registro.preferencias_servidor(1), PreferenciasServidor(True, 11))
