"""Clima: leitura da resposta da API, busca de lugar, gatilho por assunto, linha do bloco 4, cache e painel diário.

Os arquivos em testes/dados/ são respostas reais da Open-Meteo, guardadas em 13/10/2026.
Rodar de src/:  python3 -m unittest discover -s testes
"""
import json
import unittest
from datetime import datetime
from pathlib import Path

from closure_bot.clima import (TOLERANCIA, TOQUIO, VALIDADE, Lugar, ServicoClima, acao_painel, contexto_clima,
                               fala_de_clima, interpretar, interpretar_lugar, linha_bloco4, lugar_citado)
from closure_bot.plantao import FUSO

DADOS = Path(__file__).parent / "dados"
EXEMPLO = json.loads((DADOS / "clima_open_meteo.json").read_text(encoding="utf-8"))
KYOTO = json.loads((DADOS / "lugar_kyoto.json").read_text(encoding="utf-8"))
PARIS = json.loads((DADOS / "lugar_paris.json").read_text(encoding="utf-8"))


class Leitura(unittest.TestCase):
    def test_interpreta_a_resposta_real(self):
        c = interpretar(EXEMPLO)
        self.assertEqual((c.lugar, c.temperatura, c.sensacao, c.umidade, c.vento_kmh), ("Tóquio", 18, 20, 98, 4))
        self.assertEqual((c.condicao, c.minima, c.maxima), ("poucas nuvens", 18, 24))
        self.assertEqual((c.nascer, c.por_do_sol, c.hora_local, c.de_dia), ("05:46", "17:07", "02:00", False))

    def test_codigo_desconhecido_nao_inventa_descricao(self):
        resposta = json.loads(json.dumps(EXEMPLO))
        resposta["current"]["weather_code"] = 42
        self.assertEqual(interpretar(resposta).condicao, "condição 42")

    def test_resposta_fora_do_formato_levanta_erro(self):
        with self.assertRaises(KeyError):
            interpretar({"current": {}})

    def test_linha_do_bloco_4(self):
        self.assertEqual(
            linha_bloco4(interpretar(EXEMPLO)),
            "[Tóquio agora (02:00 de lá, noite): 18 °C, sensação de 20 °C, poucas nuvens, umidade 98%, "
            "vento 4 km/h; hoje entre 18 °C e 24 °C.]",
        )
        self.assertTrue(linha_bloco4(interpretar(EXEMPLO, "Quioto, Japão")).startswith("[Quioto, Japão agora ("))


class Lugares(unittest.TestCase):
    def test_resposta_real_de_quioto(self):
        lugar = interpretar_lugar(KYOTO)
        self.assertEqual(lugar.nome, "Quioto, Japão")
        self.assertAlmostEqual(lugar.latitude, 35.02, places=1)

    def test_fica_o_mais_populoso(self):
        self.assertEqual(interpretar_lugar(PARIS).nome, "Paris, Ilha de França, França")

    def test_sem_resultado(self):
        self.assertIsNone(interpretar_lugar({"generationtime_ms": 0.07}))

    def test_nome_que_vai_pro_prompt_nao_leva_colchete(self):
        lugar = interpretar_lugar({"results": [{"name": "X]\n[Ordem", "latitude": 1, "longitude": 2, "country": "Y"}]})
        self.assertNotRegex(lugar.nome, r"[\[\]\n]")


class Gatilho(unittest.TestCase):
    def test_mensagens_que_puxam_o_clima(self):
        for texto in ("closure, como tá o clima em Tóquio?", "kal, tá chovendo aí?", "quantos graus tá fazendo?",
                      "como está o tempo aí?", "tá frio em tóquio?", "qual a temperatura lá?", "vai chover em Tóquio hoje?",
                      "closure, previsão do tempo pra sessão", "tá nevando lá?", "muito calor aí?",
                      "closure, tá fazendo frio em Curitiba?", "kal, qual o clima de Quioto agora?", "chove em Londres?"):
            self.assertTrue(fala_de_clima(texto), texto)

    def test_mensagens_que_nao_puxam(self):
        for texto in ("quanto tempo dura a concentração?", "dano de frio ignora redução?", "não tenho tempo hoje",
                      "o clima da mesa ficou pesado", "closure, o que é Integridade?", "faz tempo que não jogo",
                      "tô com calor, vou parar a ficha", "a técnica dele é de chuva de lâminas",
                      "dano de frio em área funciona como?", "o clima pesou na sessão"):
            self.assertFalse(fala_de_clima(texto), texto)

    def test_lugar_citado(self):
        casos = {
            "closure, como tá o clima em são paulo hoje?": "são paulo",
            "kal, qual o clima de Quioto agora?": "Quioto",
            "tá chovendo em Belo Horizonte?": "Belo Horizonte",
            "quantos graus tá fazendo em Osaka, closure?": "Osaka",
            "previsão do tempo em Nova York pra amanhã": "Nova York",
            "qual a temperatura no Rio de Janeiro agora": "Rio de Janeiro",
            "kal, qual a temperatura de Osaka?": "Osaka",
            "closure, tá fazendo frio em Curitiba?": "Curitiba",
        }
        for texto, esperado in casos.items():
            self.assertEqual(lugar_citado(texto), esperado, texto)

    def test_sem_lugar_vale_toquio(self):
        for texto in ("kal, tá chovendo aí?", "como tá o clima em Tóquio?", "vai chover em tokyo hoje?",
                      "closure, previsão do tempo pra sessão", "tá chovendo aí? preciso de ajuda na ficha",
                      "como tá o tempo aí? em que nível libera Trilha?", "closure, o que é Integridade?"):
            self.assertIsNone(lugar_citado(texto), texto)


class Servico(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.agora = 1000.0
        self.urls = []
        self.falhar = False
        self.lugares = {"Quioto": KYOTO, "kyoto": KYOTO, "paris": PARIS}

    async def _buscar(self, url):
        self.urls.append(url)
        if self.falhar:
            raise TimeoutError("sem rede")
        if "geocoding" in url:
            nome = url.split("name=")[1].split("&")[0]
            return self.lugares.get(nome, {"generationtime_ms": 0.1})
        return EXEMPLO

    def _servico(self):
        return ServicoClima(buscar=self._buscar, relogio=lambda: self.agora)

    async def test_reaproveita_a_leitura_por_15_minutos(self):
        s = self._servico()
        primeira = await s.agora()
        self.agora += VALIDADE - 1
        self.assertIs(await s.agora(), primeira)
        self.assertEqual(len(self.urls), 1)
        self.agora += 2
        await s.agora()
        self.assertEqual(len(self.urls), 2)

    async def test_cada_lugar_tem_a_sua_leitura(self):
        s = self._servico()
        await s.agora()
        outra = await s.agora(Lugar("Quioto, Japão", 35.02, 135.75))
        self.assertEqual(outra.lugar, "Quioto, Japão")
        self.assertEqual(len(self.urls), 2)
        self.assertIn("latitude=35.02&longitude=135.75", self.urls[1])

    async def test_falha_sem_leitura_anterior_devolve_none(self):
        self.falhar = True
        self.assertIsNone(await self._servico().agora())

    async def test_falha_usa_a_leitura_antiga_ate_o_limite(self):
        s = self._servico()
        antiga = await s.agora()
        self.falhar = True
        self.agora += VALIDADE + 60
        self.assertIs(await s.agora(), antiga)
        self.agora += TOLERANCIA
        self.assertIsNone(await s.agora())

    async def test_procurar_guarda_o_resultado_e_conhece_toquio(self):
        s = self._servico()
        self.assertIs(await s.procurar("Tóquio"), TOQUIO)
        self.assertEqual(self.urls, [])
        self.assertEqual((await s.procurar("Quioto")).nome, "Quioto, Japão")
        await s.procurar("quioto")
        self.assertEqual(len(self.urls), 1)
        self.assertIsNone(await s.procurar("xyzabcqq"))

    async def test_nome_do_lugar_vai_escapado_na_url(self):
        s = self._servico()
        await s.procurar("são paulo&x=1")
        self.assertIn("name=s%C3%A3o%20paulo%26x%3D1&", self.urls[0])
        await s.procurar("nova york")
        self.assertIn("name=Nova%20Iorque&", self.urls[1])

    async def test_contexto_so_quando_a_mensagem_puxa(self):
        s = self._servico()
        self.assertIsNone(await contexto_clima(s, "closure, o que é Integridade?"))
        self.assertEqual(self.urls, [])
        self.assertTrue((await contexto_clima(s, "kal, tá chovendo aí?")).startswith("[Tóquio agora ("))

    async def test_contexto_de_outro_lugar(self):
        s = self._servico()
        linha = await contexto_clima(s, "closure, como tá o clima em kyoto?")
        self.assertTrue(linha.startswith("[Quioto, Japão agora ("), linha)

    async def test_contexto_de_lugar_que_nao_existe(self):
        linha = await contexto_clima(self._servico(), 'closure, tá chovendo em Xyzabcqq"]?')
        self.assertEqual(linha, '[Clima: o monitor não achou o lugar "Xyzabcqq".]')

    async def test_contexto_com_a_busca_fora_do_ar(self):
        self.falhar = True
        self.assertIsNone(await contexto_clima(self._servico(), "closure, como tá o clima em kyoto?"))
        self.assertIsNone(await contexto_clima(self._servico(), "kal, tá chovendo aí?"))


class PainelDiario(unittest.TestCase):
    def _hora(self, h, dia=13):
        return datetime(2026, 10, dia, h, 5, tzinfo=FUSO)

    def test_posta_uma_vez_por_dia_depois_das_6h(self):
        self.assertIsNone(acao_painel(self._hora(5), None, None, "chuva|18"))
        self.assertEqual(acao_painel(self._hora(6), None, None, "chuva|18"), "postar")
        self.assertEqual(acao_painel(self._hora(6), "2026-10-12", "chuva|18", "chuva|18"), "postar")
        self.assertIsNone(acao_painel(self._hora(7), "2026-10-13", "chuva|18", "chuva|18"))

    def test_edita_quando_o_tempo_muda(self):
        self.assertEqual(acao_painel(self._hora(9), "2026-10-13", "chuva|18", "chuva|19"), "editar")
        self.assertEqual(acao_painel(self._hora(9), "2026-10-13", "chuva|18", "nublado|18"), "editar")

    def test_de_madrugada_ainda_edita_o_de_ontem_nao(self):
        # virou o dia e ainda não são 6h: nada de postar, e o painel de ontem fica como está
        self.assertIsNone(acao_painel(self._hora(2, dia=14), "2026-10-13", "chuva|18", "chuva|12"))


class DesenhoDoTempo(unittest.TestCase):
    def test_emoji_e_icone_saem_do_codigo_e_de_ser_dia_ou_noite(self):
        from dataclasses import replace

        from closure_bot.clima import emoji_do_tempo, interpretar

        self.assertEqual([emoji_do_tempo(c) for c in (0, 2, 3, 45, 53, 61, 81, 73, 95, 1234)], ["☀️", "⛅", "☁️", "🌫️", "🌦️", "🌧️", "🌧️", "🌨️", "⛈️", "☁️"])
        self.assertEqual((emoji_do_tempo(0, de_dia=False), emoji_do_tempo(61, de_dia=False)), ("🌙", "🌧️"))
        leitura = interpretar(json.loads((DADOS / "clima_open_meteo.json").read_text(encoding="utf-8")))
        chuva_de_dia = replace(leitura, codigo=61, de_dia=True)
        self.assertEqual(chuva_de_dia.icone, "https://openweathermap.org/img/wn/10d@2x.png")
        self.assertTrue(replace(leitura, codigo=0, de_dia=False).icone.endswith("/01n@2x.png"))

    def test_chance_de_chuva_e_opcional_na_leitura(self):
        from closure_bot.clima import interpretar

        resposta = json.loads((DADOS / "clima_open_meteo.json").read_text(encoding="utf-8"))
        self.assertIsNone(interpretar(resposta).chuva_hoje)  # a amostra guardada é de antes de o bot pedir esse campo
        resposta["daily"]["precipitation_probability_max"] = [62.4]
        self.assertEqual(interpretar(resposta).chuva_hoje, 62)


if __name__ == "__main__":
    unittest.main()
