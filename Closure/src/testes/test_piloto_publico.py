"""Limites de gasto/tentativas do piloto; API real nunca é usada nesta suíte."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import AsyncMock, patch

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('piloto_publico', RAIZ / 'ferramentas/validar_publico.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class Limites(unittest.IsolatedAsyncioTestCase):
    async def rodar(self, pasta, modelos, plano, **extra):
        args = NS(executar=True, env=None)
        cfg = NS(chaves={}, vertex_projeto='')
        with patch.object(p, 'PASTA', pasta), patch.object(p, 'pedidos', AsyncMock(return_value=plano)), \
             patch.object(p, 'carregar', return_value=cfg), patch.object(p, 'Modelos', return_value=modelos):
            return await p.executar(args)

    async def test_falha_fica_registrada_e_retomada_nao_envia_de_novo(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            modelos = NS(responder=AsyncMock(side_effect=p.Falhou('rede', 'simulada')))
            plano = [(dict(id='unico', pedido_sha256='abc', reserva_usd=.1, persona='closure'), [])]
            self.assertEqual(await self.rodar(pasta, modelos, plano), 1)
            self.assertEqual(json.loads((pasta / 'resultados.json').read_text())[0]['estado'], 'falha')
            self.assertEqual(await self.rodar(pasta, modelos, plano), 1)
            self.assertEqual(modelos.responder.await_count, 1)

    async def test_reserva_que_supera_teto_e_plano_alterado_nao_chamam_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            modelos = NS(responder=AsyncMock())
            plano = [(dict(id='unico', pedido_sha256='abc', reserva_usd=1.51, persona='closure'), [])]
            await self.rodar(pasta, modelos, plano)
            modelos.responder.assert_not_awaited()
            plano[0][0]['pedido_sha256'] = 'outro'
            with self.assertRaisesRegex(ValueError, 'Plano já registrado'):
                await self.rodar(pasta, modelos, plano)
            modelos.responder.assert_not_awaited()

    async def test_nunca_ultrapassa_24_tentativas(self):
        from closure_bot.modelo import Resposta
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            resposta = Resposta('ok', 'vertex', p.FLASH, 10, 2, 1, False)
            modelos = NS(responder=AsyncMock(return_value=resposta))
            plano = [(dict(id=str(i), pedido_sha256=str(i), reserva_usd=.01, persona='closure'), [])
                     for i in range(25)]
            self.assertEqual(await self.rodar(pasta, modelos, plano), 1)
            self.assertEqual(modelos.responder.await_count, 24)
            self.assertEqual(len(json.loads((pasta / 'resultados.json').read_text())), 24)
