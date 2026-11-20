"""Atestado de ativação com serviço e SQL reais, transporte fictício; sem Google."""
import json
import unittest

from cryptography.fernet import Fernet
import httpx

from carteira_viva.atestado_servico import TRAVA, exigir_ativa
from carteira_viva.copias_banco import ReferenciaCopia
from carteira_viva.segredos import AcessoNegado, Conflito
from testes import test_carteira_financeiro_rest as fixture_financeiro
from testes.test_carteira_grade_inicializacao import ARQUIVO

H = 3600


class AtestadoServicoTeste(unittest.IsolatedAsyncioTestCase):
    # Reusar só fixtures/helpers, sem herdar e repetir toda a classe de testes.
    asyncSetUp_base = fixture_financeiro.FinanceiroRestTeste.asyncSetUp
    asyncTearDown = fixture_financeiro.FinanceiroRestTeste.asyncTearDown
    b = fixture_financeiro.FinanceiroRestTeste.b
    executar_no_worker = fixture_financeiro.FinanceiroRestTeste.executar_no_worker

    async def asyncSetUp(self):
        self.metas = []
        await self.asyncSetUp_base()
        self.req.clear()

    async def http(self, req):
        if (req.url.host == 'sheets.googleapis.com' and req.method == 'GET' and
                'developerMetadata' in req.url.params.get('fields', '')):
            self.req.append(req)
            self.assertEqual(req.url.path, '/v4/spreadsheets/' + ARQUIVO)
            return httpx.Response(200, json=dict(spreadsheetId=ARQUIVO, developerMetadata=self.metas))
        return await fixture_financeiro.FinanceiroRestTeste.http(self, req)

    def pulsar(self, rotina, seq, horas_atras, arquivo=ARQUIVO):
        chave = 'r53_pulso_' + rotina
        atual = next((m for m in self.metas if m['metadataKey'] == chave), None)
        item = dict(rotina=rotina, operacao=self.ref.operacao, arquivo=arquivo, sequencia=seq,
                    quando=self.agora() - horas_atras * H)
        if atual is None:
            atual = dict(metadataKey=chave, visibility='DOCUMENT', location=dict(locationType='SPREADSHEET'),
                         metadataValue=json.dumps(dict(versao=1, itens=[])))
            self.metas.append(atual)
        d = json.loads(atual['metadataValue']); d['itens'] = (d['itens'] + [item])[-5:]
        atual['metadataValue'] = json.dumps(d)

    def ativar(self):
        self.clock[0] = 1_800_000_000.0
        self.pulsar('instalacao', 1, 20); self.pulsar('abertura', 1, 19)
        self.pulsar('edicao', 1, 19); self.pulsar('diario', 1, 5)

    def leituras(self):
        return [r for r in self.req if 'developerMetadata' in r.url.params.get('fields', '')]

    async def conferir(self, **kw):
        return await self.s.conferir_ativacao_copia('111', '222', self.ref, **kw)

    async def test_sem_pulso_depois_ativa_e_so_le_com_get(self):
        d = await self.conferir()
        self.assertEqual((d['estado'], d['codigo'], d['reaproveitado']), ('nao_ativada', 'sem_pulso', False))
        self.ativar()
        d = await self.conferir(forcar=True)
        self.assertEqual((d['estado'], d['codigo']), ('ativa', 'ativa'))
        self.assertNotIn('maximos', d)
        google = [r for r in self.req if r.url.host in ('sheets.googleapis.com', 'www.googleapis.com')]
        self.assertTrue(google)
        self.assertTrue(all(r.method == 'GET' for r in google))
        self.assertFalse(self.posts)

    async def test_abrir_reaproveita_5_min_e_conferir_le_de_novo(self):
        self.ativar()
        await self.conferir(); self.assertEqual(len(self.leituras()), 1)
        self.clock[0] += TRAVA - 1
        d = await self.conferir()
        self.assertTrue(d['reaproveitado']); self.assertEqual(len(self.leituras()), 1)
        d = await self.conferir(forcar=True)
        self.assertFalse(d['reaproveitado']); self.assertEqual(len(self.leituras()), 2)
        self.clock[0] += TRAVA
        await self.conferir(); self.assertEqual(len(self.leituras()), 3)

    async def test_portao_sempre_rele_mesmo_dentro_da_trava(self):
        self.ativar(); await self.conferir()
        self.metas.clear()  # rotinas sumiram depois da última leitura
        with self.assertRaises(Conflito):
            await exigir_ativa(self.s, '111', '222', self.ref)
        self.assertEqual(len(self.leituras()), 2)
        self.ativar()
        self.assertEqual((await exigir_ativa(self.s, '111', '222', self.ref))['estado'], 'ativa')

    async def test_maximo_guardado_nunca_desce_e_recomeco_so_apos_contador_voltou(self):
        self.ativar(); self.pulsar('diario', 2, 1)
        await self.conferir()
        with self.assertRaises(Conflito):
            await self.s.recomecar_ativacao_copia('111', '222', self.ref)
        # Versão antiga restaurada no Drive: o metadado volta junto.
        self.metas.clear(); self.ativar()
        d = await self.conferir(forcar=True)
        self.assertEqual((d['estado'], d['codigo']), ('inconsistente', 'contador_voltou'))
        salvo = await self.b('atestado_salvo', self.m, self.ref)
        self.assertEqual(salvo['maximos']['diario'], 2)
        d = await self.s.recomecar_ativacao_copia('111', '222', self.ref)
        self.assertEqual(d['estado'], 'ativa')
        aud = await self.executar_no_worker(lambda c: c.db.execute(
            "SELECT count(*) FROM auditoria WHERE acao='atestado_recomecado'").fetchone()[0])
        self.assertEqual(aud, 1)

    async def test_copia_da_ficha_explica_que_precisa_ativar_nela(self):
        self.ativar(); self.pulsar('diario', 2, 1, arquivo='b' * 44)
        self.assertEqual((await self.conferir())['codigo'], 'copia_de_outra_ficha')

    async def test_pulso_ilegivel_nao_conta_como_ausente(self):
        self.metas.append(dict(metadataKey='r53_pulso_diario', metadataValue='{', visibility='DOCUMENT',
                               location=dict(locationType='SPREADSHEET')))
        self.assertEqual((await self.conferir())['codigo'], 'pulso_ilegivel')

    async def test_outro_usuario_ou_referencia_forjada_nao_le(self):
        with self.assertRaises(AcessoNegado):
            await self.s.conferir_ativacao_copia('111', '333', self.ref)
        falsa = ReferenciaCopia('111', '222', 'operacao-inexistente', self.ref.conexao)
        with self.assertRaises(Exception):
            await self.s.conferir_ativacao_copia('111', '222', falsa)
        with self.assertRaises(AcessoNegado):
            await self.s.conferir_ativacao_copia('111', '222', self.ref, forcar='sim')
        self.assertFalse(self.leituras())

    async def test_copia_nao_identificada_nao_tem_atestado(self):
        def voltar(c):
            with c._transacao():
                c._guardar_copia(self.ref, {**c.contexto_copia(self.m, self.ref), 'estado': 'enviada'})
        await self.executar_no_worker(voltar)
        with self.assertRaises(Conflito):
            await self.conferir()
        self.assertFalse(self.leituras())

    async def test_rotacao_de_chave_e_remocao_da_copia(self):
        self.ativar(); await self.conferir()
        nova = Fernet.generate_key()
        await self.executar_no_worker(lambda c: c.rotacionar_chave(nova))
        self.assertEqual((await self.b('atestado_salvo', self.m, self.ref))['estado'], 'ativa')

        def apagar(c):
            with c._transacao():
                c.db.execute('DELETE FROM copias_rest WHERE operacao=?', (self.ref.operacao,))
            return c.db.execute('SELECT count(*) FROM atestados_rest').fetchone()[0]
        self.assertEqual(await self.executar_no_worker(apagar), 0)


if __name__ == '__main__':
    unittest.main()
