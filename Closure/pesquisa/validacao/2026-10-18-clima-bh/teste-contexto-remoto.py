"""Somente clima: ensaios locais e uma consulta Open-Meteo; sem modelo ou Discord."""
import asyncio
import sys
import time
sys.path.insert(0, "src")
from closure_bot.clima import ServicoClima, contexto_clima, fala_de_clima, lugar_citado

AMOSTRA = {'latitude': 35.7, 'longitude': 139.6875, 'generationtime_ms': 0.1647472381591797, 'utc_offset_seconds': 32400, 'timezone': 'Asia/Tokyo', 'timezone_abbreviation': 'GMT+9', 'elevation': 40.0, 'current_units': {'time': 'iso8601', 'interval': 'seconds', 'temperature_2m': '°C', 'apparent_temperature': '°C', 'relative_humidity_2m': '%', 'weather_code': 'wmo code', 'wind_speed_10m': 'km/h', 'is_day': ''}, 'current': {'time': '2026-10-14T02:00', 'interval': 900, 'temperature_2m': 18.2, 'apparent_temperature': 20.5, 'relative_humidity_2m': 98, 'weather_code': 1, 'wind_speed_10m': 4.2, 'is_day': 0}, 'daily_units': {'time': 'iso8601', 'temperature_2m_max': '°C', 'temperature_2m_min': '°C', 'sunrise': 'iso8601', 'sunset': 'iso8601'}, 'daily': {'time': ['2026-10-14'], 'temperature_2m_max': [23.8], 'temperature_2m_min': [18.0], 'sunrise': ['2026-10-14T05:46'], 'sunset': ['2026-10-14T17:07']}}
PERGUNTAS = [
    "qual o clima atual de bh?", "qual o clima atual de Belo Horizonte?",
    "Kal, qual a temperatura atual de BH?", "como está o tempo atual de bh?",
    "qual o clima agora de bh?", "qual o clima hoje de bh?", "qual o clima atual em bh?",
]
for pergunta in PERGUNTAS:
    esperado = "Belo Horizonte" if "Belo Horizonte" in pergunta else ("BH" if "BH" in pergunta else "bh")
    assert fala_de_clima(pergunta) and lugar_citado(pergunta) == esperado, pergunta
    print("PASS extração:", pergunta)

async def main():
    urls = []
    async def buscar(url):
        urls.append(url)
        if "geocoding" in url:
            if "name=Belo%20Horizonte&" not in url:
                return {}
            return {"results": [{"name": "Belo Horizonte", "admin1": "Minas Gerais", "country": "Brasil",
                "latitude": -19.9, "longitude": -43.9, "population": 2500000}]}
        assert "latitude=-19.9&longitude=-43.9" in url
        return AMOSTRA
    s = ServicoClima(buscar=buscar)
    for pergunta in (PERGUNTAS[0], PERGUNTAS[2]):
        linha = await contexto_clima(s, pergunta)
        assert linha.startswith("[Belo Horizonte, Minas Gerais, Brasil agora (") and "Tóquio" not in linha
    assert len(urls) == 2
    print("PASS contexto de BH e cache sem Tóquio")
    linha = await contexto_clima(s, "qual o clima atual de Xyzabcqq?")
    assert "não achou" in linha and "Tóquio" not in linha
    print("PASS cidade inexistente sem Tóquio")
    async def falhar(url):
        raise TimeoutError("indisponibilidade simulada")
    assert await contexto_clima(ServicoClima(buscar=falhar), PERGUNTAS[0]) is None
    print("PASS falha de rede sem Tóquio")
    anterior = len(urls)
    assert await contexto_clima(s, "o clima da mesa ficou pesado") is None and len(urls) == anterior
    print("PASS conversa cotidiana sem consulta")
    t = time.monotonic()
    linha = await contexto_clima(ServicoClima(), PERGUNTAS[0])
    assert linha and linha.startswith("[Belo Horizonte, Minas Gerais, Brasil agora ("), linha
    print("PASS rede real Open-Meteo:", linha)
    print("LATENCIA_REDE_S:", round(time.monotonic() - t, 3))
    print("RESULTADO: 12/12; nenhum modelo; nenhuma mensagem ao Discord")
asyncio.run(main())
