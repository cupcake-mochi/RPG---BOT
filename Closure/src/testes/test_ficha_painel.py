"""Apresentação, limites do Discord e navegação sem nova leitura, conta ou API."""
import asyncio
import copy
import json
import threading
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock
from unittest.mock import patch

import discord

from closure_bot.cogs.ficha import paginas
from closure_bot.ficha_corretor import Problema, Referencias, Resultado, conferir, conferir_feiticos, conferir_invocacoes
from closure_bot.ficha_leitor import Campo, de_linhas
from closure_bot.ficha_paginacao import PaginasFicha, enviar_relatorio

RAIZ = Path(__file__).resolve().parents[2]
PERSONA = SimpleNamespace(chave="closure", nome="Closure", avatar_url=None)


def texto(paineis):
    return "\n".join(c.name + "\n" + c.value for p in paineis for c in p.fields)


class Apresentacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")

    def ficha(self, numero):
        return de_linhas(json.loads((RAIZ / f"src/testes/dados/ficha_v2_montagem_{numero}.json").read_text()))

    def test_abertura_parcial_sem_pendencias_nao_afirma_que_existem_pendencias(self):
        for guia in ('closure', 'kaltsit'):
            with self.subTest(guia=guia):
                r = Resultado('pendente', nao_conferido=['Histórico exige revisão do mestre'])
                persona = SimpleNamespace(chave=guia, nome=guia, avatar_url=None)
                ps = paginas(r, {}, persona)
                self.assertNotIn('pendências', ps[0].description.lower())
                self.assertIn('0 pendências', texto(ps[:1]))
                self.assertEqual(r.veredito, 'pendente')

    def resultado(self, ficha, numero):
        if numero == 4:
            return conferir(ficha, self.ref)
        # As fixtures 1–3 guardam as entradas de magia/entidade, sem a ficha inteira.
        # O cabeçalho abaixo reproduz os valores pessoais dos painéis enviados pelo usuário.
        r = Resultado("aprovada")
        conferir_feiticos(ficha, self.ref, r)
        conferir_invocacoes(ficha, self.ref, r)
        self.assertEqual(r.problemas, [])
        trilha = "Invocação Principal" if numero == 3 else "Parceria"
        valores = (121, 102, 148, 13) if numero == 1 else (128, 108, 156, 14)
        vida, pe, integridade, defesa = valores
        r.conferidos[:0] = ["Caminho Evocador", "Trilha " + trilha, "Origem Latente", f"Vida {vida}",
                            f"PE {pe}", f"Integridade {integridade}", "Proteção 1", f"Defesa {defesa}"]
        return r

    def test_quatro_fichas_preservam_resultado_e_dados_com_resumo_menor(self):
        for numero in (1, 2, 3, 4):
            with self.subTest(numero=numero):
                ficha = self.ficha(numero)
                resultado = self.resultado(ficha, numero)
                antes = copy.deepcopy((ficha, resultado))
                ps = paginas(resultado, ficha, PERSONA, {"edicao_livro": "R51"})
                self.assertEqual(antes, (ficha, resultado))
                self.assertEqual(resultado.veredito, "aprovada")
                self.assertLessEqual(len(ps[0]), 2500)
                self.assertGreater(len(ps), 1)
                self.assertTrue(resultado.nao_conferido)  # fixtures têm limites mecânicos reais
                self.assertIn("Conferência parcial", texto(ps[:1]))
                for i, p in enumerate(ps):
                    self.assertTrue(p.footer.text.startswith(f"Página {i+1} de {len(ps)} · "))
                    self.assertEqual(p.author.name, "Closure")
                    self.assertNotEqual(p.colour.value, 0xCC0102)  # nenhum erro nessas fichas
                    self.assertIn("Veredito geral: pendente", p.footer.text)
                    self.assertLessEqual(len(p), 6000)
                    self.assertLessEqual(len(p.fields), 25)
                    self.assertTrue(all(0 < len(c.value) <= 1024 and len(c.name) <= 256 for c in p.fields))
                self.assertNotIn("atributo.constituicao.total", texto(ps))
                self.assertNotIn("não estão completos na ANALISE", texto(ps))
                self.assertIn("Selo", texto(ps))

    def test_domada_mostra_nome_do_buff_e_numeros_legiveis(self):
        ficha = self.ficha(2)
        ps = paginas(self.resultado(ficha, 2), ficha, PERSONA)
        self.assertIn("**Invocação 1 · Buff/Debuff de Constituição**: +1", texto(ps[:1]))
        self.assertIn("**Invocação 1 · Buff/Debuff de Vida**: +2", texto(ps[:1]))
        inv = [p for p in ps if " · Invocação 1 · " in p.footer.text]
        for valor in ("Vida 34", "Defesa 13", "acerto +5", "CD 13", "entrada 2 PE", "retorno 4 PE", "Constituição 3"):
            self.assertIn(valor, texto(inv))
        self.assertNotIn("vida.max", texto(inv))

    def test_cores_e_alertas_continuam_no_resumo(self):
        erro = Problema("conta", "defesa", "13", "19")
        pendencia = Problema("aviso", "aviso.testes_disponiveis", "", "1 de 2")
        for r, cor in ((Resultado("reprovada", problemas=[erro], pendencias=[pendencia]), 0xCC0102),
                       (Resultado("aprovada", pendencias=[pendencia]), 0xD4A017),
                       (Resultado("aprovada"), 0x2E8B57)):
            ps = paginas(r, {}, PERSONA)
            self.assertEqual(ps[0].colour.value, cor)
            if r.problemas:
                self.assertIn("está 19, o certo é 13", texto(ps[:1]))
            if r.pendencias:
                self.assertIn("faltam escolher 1 de 2", texto(ps[:1]))

    def test_erro_global_nao_contamina_valores_conferidos_ou_limites(self):
        r = Resultado("reprovada", problemas=[Problema("conta", "defesa", "13", "19")],
                      pendencias=[Problema("informação", "tr", "escolher dois TR", "um")],
                      conferidos=["Repertório: capacidade 3 espaços", "Atletismo: bônus +4",
                                  "Feitiço 1: dano-base 2d8", "Invocação 2: vida.max 12"],
                      nao_conferido=["Carga: faltam quantidades"])
        antes = copy.deepcopy(r)
        ps = paginas(r, {}, PERSONA)
        cores = {p.description.strip("*"): p.colour.value for p in ps[1:]}
        self.assertEqual(ps[0].colour.value, 0xCC0102)
        self.assertEqual(cores["Correções e revisão"], 0xCC0102)
        self.assertEqual(cores["Limites da análise"], 0xD4A017)
        for categoria in ("Personagem", "TR e perícias", "Feitiços e técnicas", "Invocação 2"):
            self.assertEqual(cores[categoria], 0x2E8B57, categoria)
        self.assertTrue(all("Veredito geral: reprovada" in p.footer.text for p in ps))
        self.assertEqual(r, antes)  # apresentação não altera a avaliação

    def test_resumo_distingue_pendencias_ajustes_e_partes_nao_conferidas(self):
        p = Problema('informação', 'tr', 'revisão', 'pendente')
        casos = [
            ({'nao_conferido': ['Aprendizado e autorização ficam com o mestre']}, 'há partes não conferidas'),
            ({'notas': [p], 'nao_conferido': ['Limite humano']}, 'ajustes para o mestre'),
            ({'pendencias': [p], 'nao_conferido': ['Limite humano']}, 'pendências abertas'),
        ]
        for veredito in ('aprovada', 'pendente'):
            for campos, esperado in casos:
                with self.subTest(veredito=veredito, campos=campos):
                    r = Resultado(veredito, **campos)
                    antes = copy.deepcopy(r)
                    ps = paginas(r, {}, PERSONA)
                    resumo = texto(ps[:1])
                    self.assertIn('Conferência parcial; ' + esperado, resumo)
                    if not r.pendencias:
                        self.assertIn('0 pendências', resumo)
                        self.assertNotIn('pendências abertas', resumo)
                    self.assertEqual(r, antes)
                    self.assertEqual(ps[0].colour.value, 0xD4A017)
                    self.assertIn('Veredito geral: pendente', ps[0].footer.text)
                    for limite in r.nao_conferido:
                        self.assertIn(limite, texto(ps))

    def test_cor_da_revisao_respeita_quebra_entre_erros_e_pendencias(self):
        erros = [Problema("conta", f"erro.{i}", "E" * 300, "A" * 100) for i in range(25)]
        pendencias = [Problema("informação", f"falta.{i}", "P" * 300, "vazio") for i in range(35)]
        r = Resultado("reprovada", problemas=erros, pendencias=pendencias)
        ps = [p for p in paginas(r, {}, PERSONA) if p.description == "**Correções e revisão**"]
        vermelhas = [p for p in ps if any(c.name == "❌ Precisa corrigir" for c in p.fields)]
        amarelas = [p for p in ps if all(c.name != "❌ Precisa corrigir" for c in p.fields)]
        self.assertTrue(vermelhas and amarelas)
        self.assertTrue(all(p.colour.value == 0xCC0102 for p in vermelhas))
        self.assertTrue(all(p.colour.value == 0xD4A017 for p in amarelas))

    def test_pendencia_ou_revisao_do_mestre_nao_vira_erro(self):
        for campo in ("pendencias", "notas"):
            with self.subTest(campo=campo):
                r = Resultado("pendente", conferidos=["Repertório: capacidade 3 espaços"],
                              **{campo: [Problema("aviso", "tr", "revisão", "pendente")]})
                ps = paginas(r, {}, PERSONA)
                self.assertEqual(ps[0].colour.value, 0xD4A017)
                self.assertEqual(next(p for p in ps if p.description == "**Correções e revisão**").colour.value, 0xD4A017)
                self.assertEqual(next(p for p in ps if p.description == "**Personagem**").colour.value, 0x2E8B57)

    def test_cores_locais_preservam_identidade_das_duas_guias(self):
        r = Resultado("reprovada", problemas=[Problema("conta", "defesa", "13", "19")],
                      conferidos=["Repertório: capacidade 3 espaços"])
        for chave, nome in (("kaltsit", "Kal'tsit"), ("closure", "Closure")):
            with self.subTest(guia=chave):
                ps = paginas(r, {}, SimpleNamespace(chave=chave, nome=nome, avatar_url=None))
                self.assertTrue(all(p.author.name == nome for p in ps))
                self.assertEqual(ps[0].colour.value, 0xCC0102)
                self.assertEqual(ps[-1].colour.value, 0x2E8B57)

    def test_aviso_de_dados_ausentes_e_so_do_formato_antigo(self):
        ficha = self.ficha(4)
        self.assertEqual(ficha["formato.versao"].valor, 2)
        r = conferir(ficha, self.ref)
        self.assertFalse(any("não estão completos na ANALISE" in l for l in r.nao_conferido))
        self.assertTrue(r.nao_conferido)  # Não transforma exportação completa em conferência integral.
        ficha["formato.versao"] = Campo(1, "", "entrada")
        antigo = conferir(ficha, self.ref)
        self.assertTrue(any("não estão completos na ANALISE" in l for l in antigo.nao_conferido))

    def test_relatorio_grande_preserva_todos_os_itens_e_texto_longo(self):
        erros = [Problema("aviso", f"aviso.caso_{i}", "", f"marcador-{i:03d}") for i in range(180)]
        longo = "INICIO_LONGO " + "x" * 7000 + " FIM_LONGO"
        r = Resultado("reprovada", problemas=erros, nao_conferido=[longo])
        ps = paginas(r, {"nome": Campo("N" * 700, "", "entrada")}, PERSONA)
        completo = texto(ps)
        for i in range(180):
            self.assertIn(f"marcador-{i:03d}", completo)
        self.assertIn("INICIO_LONGO", completo)
        self.assertIn("FIM_LONGO", completo)
        for p in ps:
            self.assertLessEqual(len(p), 6000)
            self.assertLessEqual(len(p.title), 256)
            self.assertTrue(all(len(c.value) <= 1024 for c in p.fields))

    def test_limites_repetidos_agrupam_assuntos_sem_apagar_itens(self):
        r = Resultado("aprovada", nao_conferido=[f"Feitiço {i}: falta conferir Selo e texto" for i in range(100)])
        ps = paginas(r, {}, PERSONA)
        limites = [p for p in ps if " · Limites da análise · " in p.footer.text]
        for i in range(100):
            self.assertIn(f"Feitiço {i}", texto(limites))
        self.assertEqual(texto(limites).count("falta conferir Selo e texto"), 1)


class Navegacao(unittest.IsolatedAsyncioTestCase):
    def paginas(self, quantidade=5):
        ps = []
        for i in range(quantidade):
            p = discord.Embed(title=f"página-{i}")
            p.set_footer(text=f"Página {i+1} de {quantidade} · seção-{i} · livro R51")
            ps.append(p)
        return ps

    def interacao(self):
        return SimpleNamespace(response=SimpleNamespace(edit_message=AsyncMock(), send_message=AsyncMock()),
                               edit_original_response=AsyncMock())

    async def test_quatro_botoes_e_seletor_trocam_a_mesma_mensagem(self):
        ps = self.paginas()
        view = PaginasFicha(ps)
        i = self.interacao()
        self.assertTrue(view.primeira.disabled and view.anterior.disabled)
        componentes = view.to_components()
        self.assertEqual([len(linha["components"]) for linha in componentes], [1, 4])
        await view.proxima.callback(i)
        self.assertEqual(view.indice, 1)
        self.assertIs(i.response.edit_message.call_args.kwargs["embed"], ps[1])
        await view.ultima.callback(i)
        self.assertEqual(view.indice, 4)
        self.assertTrue(view.proxima.disabled and view.ultima.disabled)
        await view.anterior.callback(i)
        self.assertEqual(view.indice, 3)
        await view.primeira.callback(i)
        self.assertEqual(view.indice, 0)
        view.seletor._values = ["2"]
        await view.seletor.callback(i)
        self.assertEqual(view.indice, 2)
        self.assertEqual([o.value for o in view.seletor.options if o.default], ["2"])
        view.stop()

    async def test_seletor_com_mais_de_25_paginas_e_limites(self):
        view = PaginasFicha(self.paginas(60))
        i = self.interacao()
        await view.ultima.callback(i)
        self.assertEqual(len(view.seletor.options), 25)
        self.assertIn("59", [o.value for o in view.seletor.options])
        await view.mostrar(i, -10)
        self.assertEqual(view.indice, 0)
        await view.mostrar(i, 900)
        self.assertEqual(view.indice, 59)
        view.stop()

    async def test_cliques_simultaneos_nao_perdem_passos(self):
        view = PaginasFicha(self.paginas())
        interacoes = [self.interacao() for _ in range(3)]
        # Side effect assíncrono, como a espera de rede ao editar a mensagem.
        async def editar(**kw):
            await asyncio.sleep(0)
        for i in interacoes:
            i.response.edit_message.side_effect = editar
        await asyncio.gather(*(view.proxima.callback(i) for i in interacoes))
        self.assertEqual(view.indice, 3)
        view.stop()

    async def test_timeout_volta_ao_resumo_desativa_controles_e_nao_apaga_analise(self):
        ps = self.paginas()
        view = PaginasFicha(ps)
        view.mensagem = SimpleNamespace(edit=AsyncMock())
        ultimo_clique = self.interacao()
        await view.ultima.callback(ultimo_clique)
        await view.on_timeout()
        self.assertTrue(view.is_finished())
        self.assertTrue(all(c.disabled for c in view.children))
        enviado = ultimo_clique.edit_original_response.call_args.kwargs["embed"]
        view.mensagem.edit.assert_not_called()
        self.assertEqual(enviado.title, ps[0].title)
        self.assertIn("Controles encerrados", enviado.footer.text)
        self.assertNotIn("Controles encerrados", ps[0].footer.text)
        i = self.interacao()
        await view.proxima.callback(i)
        i.response.send_message.assert_awaited_once()
        i.response.edit_message.assert_not_called()

    async def test_timeout_sem_cliques_usa_mensagem_do_envio(self):
        view = PaginasFicha(self.paginas())
        view.mensagem = SimpleNamespace(edit=AsyncMock())
        await view.on_timeout()
        view.mensagem.edit.assert_awaited_once()
        self.assertTrue(view.is_finished())

    async def test_participantes_distintos_folheiam_painel_publico_e_timeout_usa_ultimo_clique(self):
        view = PaginasFicha(self.paginas())
        view.mensagem = SimpleNamespace(edit=AsyncMock())
        autora, participante = self.interacao(), self.interacao()
        autora.user = SimpleNamespace(id=101)
        participante.user = SimpleNamespace(id=202)
        self.assertTrue(await view.interaction_check(autora))
        self.assertTrue(await view.interaction_check(participante))
        await view.proxima.callback(autora)
        await view.proxima.callback(participante)
        self.assertEqual(view.indice, 2)
        await view.on_timeout()
        participante.edit_original_response.assert_awaited_once()
        autora.edit_original_response.assert_not_called()
        self.assertTrue(all(item.disabled for item in view.children))
        await view.proxima.callback(autora)
        autora.response.send_message.assert_awaited_once()
        self.assertEqual(autora.response.edit_message.await_count, 1)

    async def test_envio_de_texto_painel_unico_e_paginado(self):
        enviar = AsyncMock(return_value=SimpleNamespace(edit=AsyncMock()))
        await enviar_relatorio("Não deu pra ler a ficha.", enviar)
        enviar.assert_awaited_with("Não deu pra ler a ficha.")
        await enviar_relatorio(self.paginas(1), enviar)
        self.assertNotIn("view", enviar.call_args.kwargs)
        ps = self.paginas()
        await enviar_relatorio(ps, enviar)
        view = enviar.call_args.kwargs["view"]
        self.assertIs(enviar.call_args.kwargs["embed"], ps[0])
        self.assertIs(view.mensagem, enviar.return_value)
        view.stop()

    async def test_barra_publica_envia_controles_e_folhear_nao_rele_a_ficha(self):
        # A suíte do Discord recarrega extensões: use a classe da mesma instância
        # de módulo onde o leitor será substituído, sem manter referência antiga.
        from closure_bot.cogs.ficha import Ficha
        ficha = de_linhas(json.loads((RAIZ / "src/testes/dados/ficha_v2_montagem_4.json").read_text()))
        bot = SimpleNamespace(config=SimpleNamespace(dados=RAIZ / "dados"),
                              personas={"closure": PERSONA, "kaltsit": PERSONA}, manifesto={"edicao_livro": "R51"})
        cog = Ficha(bot)
        mensagem = SimpleNamespace(edit=AsyncMock())
        interacao = SimpleNamespace(guild_id=123, response=SimpleNamespace(defer=AsyncMock()),
                                    followup=SimpleNamespace(send=AsyncMock(return_value=mensagem)))
        with patch("closure_bot.cogs.ficha.de_link", AsyncMock(return_value=ficha)) as ler:
            await cog.analisar.callback(cog, interacao, link="https://exemplo.invalid/ficha")
            interacao.response.defer.assert_awaited_once_with(thinking=True)
            envio = interacao.followup.send.call_args.kwargs
            self.assertTrue(envio["wait"])
            self.assertFalse(envio.get("ephemeral", False))
            view = envio["view"]
            self.assertIsInstance(view, PaginasFicha)
            await view.proxima.callback(self.interacao())
            await view.ultima.callback(self.interacao())
            ler.assert_awaited_once_with("https://exemplo.invalid/ficha")
            self.assertIs(view.mensagem, mensagem)
            view.stop()

    async def test_leitura_xlsx_e_contas_nao_bloqueiam_eventos_do_discord(self):
        from closure_bot.cogs.ficha import Ficha
        bot = SimpleNamespace(config=SimpleNamespace(dados=RAIZ / "dados"),
                              personas={"closure": PERSONA, "kaltsit": PERSONA}, manifesto={})
        cog = Ficha(bot)
        arquivo = SimpleNamespace(filename="teste.xlsx", size=100, read=AsyncMock(return_value=b"xlsx"))
        ficha = {"nome": Campo("Ensaio de responsividade", "", "entrada")}
        loop = asyncio.get_running_loop()
        progressos = []

        def trabalho_sincrono(retorno):
            evento = threading.Event()
            # Simula o processamento pesado aguardando outro evento do loop.
            # Executado no loop principal, esse evento não progride a tempo.
            loop.call_soon_threadsafe(evento.set)
            progressos.append(evento.wait(1))
            return retorno

        with patch("closure_bot.cogs.ficha.de_xlsx", side_effect=lambda _: trabalho_sincrono(ficha)), \
             patch("closure_bot.cogs.ficha.conferir", side_effect=lambda *args: trabalho_sincrono(Resultado("aprovada"))):
            paineis = await cog.analisar_fonte(arquivo=arquivo, servidor=123)
        self.assertEqual(progressos, [True, True])
        self.assertEqual(paineis[0].title, "Ficha de Ensaio de responsividade")


if __name__ == "__main__":
    unittest.main()
