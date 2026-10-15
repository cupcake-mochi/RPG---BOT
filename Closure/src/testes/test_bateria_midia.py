import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock
from closure_bot.modelo import Resposta, FLASH

spec=importlib.util.spec_from_file_location('bateria_midia',Path(__file__).resolve().parents[2]/'ferramentas/bateria_midia.py')
bateria=importlib.util.module_from_spec(spec);spec.loader.exec_module(bateria)

class Bateria(unittest.IsolatedAsyncioTestCase):
    def plano(self,teto=1):
        return {'casos':[{'id':str(i),'persona':'closure','reserva_cheia_usd':.10} for i in range(2)],'teto_cheio_usd':teto}

    async def test_conta_apenas_faltantes_e_respeita_orcamento(self):
        with tempfile.TemporaryDirectory() as pasta:
            p=Path(pasta);m=AsyncMock()
            m.responder.return_value=Resposta('ok','vertex',FLASH,100,10,30,False)
            plano=self.plano();pedidos={'0':[], '1':[]}
            self.assertEqual(await bateria.executar(plano,pedidos,m,p),0)
            self.assertEqual(m.responder.await_count,2)
            self.assertEqual(await bateria.executar(plano,pedidos,m,p),0)
            self.assertEqual(m.responder.await_count,2)
        with tempfile.TemporaryDirectory() as pasta:
            m.responder.reset_mock()
            self.assertEqual(await bateria.executar(self.plano(.05),pedidos,m,Path(pasta)),1)
            m.responder.assert_not_awaited()

    async def test_interrupcao_preserva_intencao_e_impede_repetir(self):
        with tempfile.TemporaryDirectory() as pasta:
            p=Path(pasta);m=AsyncMock();m.responder.side_effect=RuntimeError('reinício simulado')
            with self.assertRaises(RuntimeError): await bateria.executar(self.plano(),{'0':[],'1':[]},m,p)
            rs=json.loads((p/'respostas.json').read_text())
            self.assertEqual(rs[0]['estado'],'iniciada');self.assertEqual(rs[0]['reserva_usd'],.1)
            with self.assertRaises(ValueError): await bateria.executar(self.plano(),{'0':[],'1':[]},m,p)
            self.assertEqual(m.responder.await_count,1)
