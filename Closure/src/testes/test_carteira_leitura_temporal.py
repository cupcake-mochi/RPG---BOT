"""Versionamento sem rede real; mudanças testadas nos limites dos awaits."""
import asyncio
import json
from pathlib import Path
import traceback
import unittest
import httpx
from carteira_viva.leitura_temporal import GuardaLeitura, ErroLeituraTemporal, PROTOCOLO, FLAGS
from carteira_viva.provedores import Provedores, ErroProvedor, MIME
from carteira_viva.segredos import AcessoNegado
from testes.test_carteira_provedores import configuracao

ARQUIVO = 'arquivo_sintetico_temporal_0001'
SEQ, ASS, CONTEXTO = 'a' * 64, 'b' * 64, 'c' * 64


def plano(perfis=9):
    return dict(protocolo=PROTOCOLO, assinatura=ASS, sequencia='d' * 64, perfis=perfis,
                porPagina=4, paginas=(perfis + 3) // 4, **{k: False for k in FLAGS})


class Cenario:
    def __init__(self, perfis=9):
        self.versao, self.contexto, self.tempo = '9007199254740993', CONTEXTO, 10.
        self.perfis, self.chamadas, self.contextos = perfis, [], 0
        self.requests, self.hook, self.transformar = [], None, None
        self.provedores = Provedores(configuracao(Path('nao_criar_temporal.sqlite3')),
                                     transporte=httpx.MockTransport(self.http))
        self.leitura = GuardaLeitura(self.provedores, self.ler_plano, self.ler_pagina,
                                     self.revalidar, agora=lambda: self.tempo)

    def http(self, req):
        self.requests.append(req)
        return httpx.Response(200, json=dict(id=ARQUIVO, mimeType=MIME, trashed=False,
                                             isAppAuthorized=True, version=self.versao))

    async def revalidar(self):
        self.contextos += 1
        return self.contexto

    async def ler_plano(self, arquivo, seq):
        self.chamadas.append(('plano', arquivo, seq))
        if self.hook: await self.hook('plano')
        obj = plano(self.perfis)
        return self.transformar(obj, 'plano') if self.transformar else obj

    async def ler_pagina(self, arquivo, seq, assinatura, pagina):
        self.chamadas.append(('pagina', arquivo, seq, assinatura, pagina))
        if self.hook: await self.hook('pagina')
        obj = dict(plano(self.perfis), pagina=pagina, lidos=min(4, self.perfis - 4 * pagina), estado='e' * 64)
        return self.transformar(obj, 'pagina') if self.transformar else obj

    async def iniciar(self): return await self.leitura.iniciar('token_ficticio', ARQUIVO, SEQ)
    async def pagina(self, indice): return await self.leitura.avancar('token_ficticio', indice)


class LeituraTemporalTeste(unittest.IsolatedAsyncioTestCase):
    async def completa(self, c):
        await c.iniciar()
        for i in range((c.perfis + 3) // 4): await c.pagina(i)
        return await c.leitura.finalizar('token_ficticio')

    async def test_fluxo_somente_get_sem_perder_precisao_ou_vazar_ids(self):
        c = Cenario(); out = await self.completa(c)
        self.assertEqual(out['paginas_lidas'], 3)
        self.assertTrue(out['versao_drive_estavel_observada'])
        self.assertTrue(out['leitura_historica'])
        for k in ['criacao_disponivel', 'conferencia_conjunta_concluida', 'consistencia_temporal_verificada',
                  'imagens_atuais_conferidas', 'invalidada']: self.assertFalse(out[k])
        self.assertEqual(c.leitura._estado.versao_drive, '9007199254740993')
        self.assertEqual([x[-1] for x in c.chamadas if x[0] == 'pagina'], [0, 1, 2])
        self.assertEqual(len(c.requests), 9)
        for req in c.requests:
            self.assertEqual(req.method, 'GET'); self.assertEqual(req.url.host, 'www.googleapis.com')
            self.assertIn('/drive/v3/files/', req.url.path)
            self.assertEqual(req.headers['Authorization'], 'Bearer token_ficticio')
            self.assertNotIn('token_ficticio', str(req.url))
        self.assertNotIn(ARQUIVO, str(out)); self.assertNotIn(ARQUIVO, repr(c.leitura._estado))
        self.assertNotIn('token_ficticio', repr(c.leitura.__dict__))

    async def test_contrato_real_do_produtor_em_vm_e_consumidor_concordam(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures/carteira_conferencia_pagina_v1.json').read_text())
        c = Cenario(2)
        async def ler_plano(arquivo, seq):
            self.assertEqual(arquivo, ARQUIVO); self.assertEqual(seq, fixture['assinaturaSequencia'])
            return fixture['plano']
        async def ler_pagina(arquivo, seq, assinatura, pagina):
            self.assertEqual(arquivo, ARQUIVO); self.assertEqual(seq, fixture['assinaturaSequencia'])
            self.assertEqual(assinatura, fixture['plano']['assinatura'])
            return fixture['paginas'][pagina]
        guarda = GuardaLeitura(c.provedores, ler_plano, ler_pagina, c.revalidar)
        await guarda.iniciar('falso', ARQUIVO, fixture['assinaturaSequencia'])
        await guarda.avancar('falso', 0)
        out = await guarda.finalizar('falso')
        self.assertTrue(out['versao_drive_estavel_observada'])
        self.assertFalse(out['criacao_disponivel'])

    async def test_edicao_durante_plano_nao_cria_estado(self):
        c = Cenario()
        async def editar(_): c.versao = '9007199254740994'
        c.hook = editar
        with self.assertRaises(ErroLeituraTemporal) as exc: await c.iniciar()
        self.assertEqual(exc.exception.codigo, 'alterada')
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)
        self.assertTrue(c.leitura.progresso()['invalidada'])

    async def test_edicao_entre_paginas_nao_executa_pagina_seguinte(self):
        c = Cenario(); await c.iniciar(); await c.pagina(0)
        c.versao = '9007199254740994'; n = len(c.chamadas)
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(1)
        self.assertEqual(len(c.chamadas), n)
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 1)

    async def test_edicao_e_retorno_ao_conteudo_original_nao_redefine_baseline(self):
        c = Cenario(); await c.iniciar()
        async def editar(_): c.versao = '9007199254740995'
        c.hook = editar
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)
        c.hook = None; c.versao = '9007199254740993'
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)

    async def test_edicao_apos_ultima_pagina_impede_finalizar(self):
        c = Cenario(1); await c.iniciar(); await c.pagina(0); c.versao = '42'
        with self.assertRaises(ErroLeituraTemporal): await c.leitura.finalizar('falso')
        self.assertFalse(c.leitura.progresso()['versao_drive_estavel_observada'])

    async def test_calculos_sem_edicao_nao_ganham_selo_de_snapshot(self):
        c = Cenario(5); await c.iniciar(); await c.pagina(0)
        c.transformar = lambda o, _: dict(o, estado='f' * 64)
        await c.pagina(1); out = await c.leitura.finalizar('falso')
        self.assertTrue(out['versao_drive_estavel_observada'])
        self.assertFalse(out['consistencia_temporal_verificada']); self.assertFalse(out['criacao_disponivel'])

    async def test_contexto_alterado_durante_await_descarta_pagina(self):
        c = Cenario(); await c.iniciar()
        async def mudar(_): c.contexto = 'f' * 64
        c.hook = mudar
        with self.assertRaises(ErroLeituraTemporal) as exc: await c.pagina(0)
        self.assertEqual(exc.exception.codigo, 'contexto')
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)

    async def test_contexto_sem_confirmacao_ou_negado_recusa_sem_rede_e_sem_vazamento(self):
        for valor in [None, False, True, '', 'contexto_livre']:
            with self.subTest(valor=valor):
                c = Cenario(); c.contexto = valor
                with self.assertRaises(ErroLeituraTemporal): await c.iniciar()
                self.assertFalse(c.requests)
        c = Cenario()
        async def negar(): raise AcessoNegado('SEGREDO não deve aparecer')
        c.leitura._revalidar = negar
        with self.assertRaises(ErroLeituraTemporal) as exc: await c.iniciar()
        self.assertNotIn('SEGREDO', ''.join(traceback.format_exception(exc.exception)))
        self.assertFalse(c.requests)

    async def test_revogacao_nao_faz_fallback_publico(self):
        c = Cenario(); await c.iniciar()
        c.provedores.transporte = httpx.MockTransport(lambda _: httpx.Response(403))
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)
        self.assertTrue(c.leitura.progresso()['invalidada'])
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)

    async def test_falha_temporaria_antes_e_depois_da_pagina_repete_mesmo_indice(self):
        for depois in [False, True]:
            with self.subTest(depois=depois):
                c = Cenario(); await c.iniciar(); n = 0
                def http(req):
                    nonlocal n
                    n += 1
                    return httpx.Response(503) if n == (2 if depois else 1) else c.http(req)
                c.provedores.transporte = httpx.MockTransport(http)
                with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)
                self.assertFalse(c.leitura.progresso()['invalidada'])
                self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)
                c.provedores.transporte = httpx.MockTransport(c.http); await c.pagina(0)
                self.assertEqual(c.leitura.progresso()['paginas_lidas'], 1)

    async def test_erro_do_produtor_nao_vaza_dados_ou_avanca(self):
        c = Cenario(); await c.iniciar()
        async def erro(_): raise RuntimeError('SEGREDO token_ficticio')
        c.hook = erro
        with self.assertRaises(ErroLeituraTemporal) as exc: await c.pagina(0)
        self.assertNotIn('SEGREDO', ''.join(traceback.format_exception(exc.exception)))
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)
        c.hook = None; await c.pagina(0)

    async def test_cancelamento_libera_trava_sem_perder_indice(self):
        c = Cenario(); await c.iniciar(); pronto, continuar = asyncio.Event(), asyncio.Event()
        async def esperar(_): pronto.set(); await continuar.wait()
        c.hook = esperar; task = asyncio.create_task(c.pagina(0)); await pronto.wait(); task.cancel()
        with self.assertRaises(asyncio.CancelledError): await task
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)
        c.hook = None; await c.pagina(0)

    async def test_duas_requisicoes_iguais_nao_duplicam_pagina(self):
        c = Cenario(); await c.iniciar(); await asyncio.gather(c.pagina(0), c.pagina(0))
        self.assertEqual(len([x for x in c.chamadas if x[0] == 'pagina']), 1)
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 1)

    async def test_repeticao_ainda_revalida_acesso_e_versao(self):
        c = Cenario(); await c.iniciar(); await c.pagina(0); n = len(c.chamadas)
        await c.pagina(0); self.assertEqual(len(c.chamadas), n); c.versao = '42'
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)

    async def test_indices_livres_pulos_ou_tipos_incorretos_nao_avancam(self):
        c = Cenario(); await c.iniciar()
        for pagina in [True, 0., -1, 1, 3, '0']:
            with self.subTest(pagina=pagina), self.assertRaises(ErroLeituraTemporal): await c.pagina(pagina)
        await c.pagina(0); await c.pagina(1)
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)

    async def test_plano_e_pagina_malformados_nao_sao_aceitos(self):
        mudancas = [dict(protocolo='outro'), dict(perfis=True), dict(perfis=632), dict(porPagina=8),
                    dict(paginas=500), dict(assinatura='x'), dict(sequencia='x'), dict(extra='SEGREDO'),
                    dict(criacaoDisponivel=True)]
        for fase in ['plano', 'pagina']:
            for mudar in mudancas:
                with self.subTest(fase=fase, mudar=mudar):
                    c = Cenario()
                    if fase == 'pagina': await c.iniciar()
                    c.transformar = lambda o, _, d=mudar: dict(o, **d)
                    with self.assertRaises(ErroLeituraTemporal):
                        if fase == 'plano': await c.iniciar()
                        else: await c.pagina(0)
                    self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)

    async def test_pagina_de_outro_plano_indice_quantidade_ou_estado_recusa(self):
        for mudar in [dict(assinatura='f' * 64), dict(sequencia='e' * 64), dict(pagina=1),
                      dict(pagina=True), dict(lidos=3), dict(lidos=True), dict(estado='x')]:
            with self.subTest(mudar=mudar):
                c = Cenario(); await c.iniciar(); c.transformar = lambda o, _, d=mudar: dict(o, **d)
                with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)
                self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)

    async def test_prazo_inclui_esperas_e_relogio_invalido_recusa(self):
        for duracao in [0, -1, True, '1', float('nan'), float('inf'), 3601]:
            c = Cenario()
            with self.assertRaises(ValueError):
                GuardaLeitura(c.provedores, c.ler_plano, c.ler_pagina, c.revalidar, duracao=duracao)
        c = Cenario(); await c.iniciar()
        async def esperar(_): c.tempo += 1800
        c.hook = esperar
        with self.assertRaises(ErroLeituraTemporal) as exc: await c.pagina(0)
        self.assertEqual(exc.exception.codigo, 'expirada')
        self.assertEqual(c.leitura.progresso()['paginas_lidas'], 0)
        for tempo in [float('nan'), float('inf')]:
            c = Cenario(); c.tempo = tempo
            with self.assertRaises(ErroLeituraTemporal): await c.iniciar()
            self.assertFalse(c.requests)

    async def test_finalizacao_exige_todas_paginas_e_revalida_contexto(self):
        c = Cenario(); await c.iniciar()
        with self.assertRaises(ErroLeituraTemporal) as exc: await c.leitura.finalizar('falso')
        self.assertEqual(exc.exception.codigo, 'incompleta'); self.assertFalse(c.leitura.progresso()['invalidada'])
        for i in range(3): await c.pagina(i)
        await c.leitura.finalizar('falso'); c.contexto = 'e' * 64
        with self.assertRaises(ErroLeituraTemporal): await c.leitura.finalizar('falso')
        self.assertFalse(c.leitura.progresso()['criacao_disponivel'])

    async def test_maximo_de_631_perfis_em_158_paginas_sem_truncar(self):
        c = Cenario(631); out = await self.completa(c)
        self.assertEqual(out['total_paginas'], 158); self.assertEqual(out['paginas_lidas'], 158)
        self.assertTrue(out['versao_drive_estavel_observada'])

    async def test_sem_iniciar_sem_reinicio_silencioso_ou_id_url(self):
        c = Cenario()
        with self.assertRaises(ErroLeituraTemporal): await c.pagina(0)
        c = Cenario(); await c.iniciar()
        with self.assertRaises(ErroLeituraTemporal): await c.iniciar()
        c = Cenario()
        with self.assertRaises(ErroLeituraTemporal): await c.leitura.iniciar('falso', 'https://127.0.0.1/', SEQ)
        self.assertFalse(c.requests)


class VersaoArquivoTeste(unittest.IsolatedAsyncioTestCase):
    def provedor(self, meta):
        return Provedores(configuracao(Path('nao_criar_versao.sqlite3')),
                          transporte=httpx.MockTransport(lambda _: httpx.Response(200, json=meta)))

    async def test_metadados_e_versao_invalida_recusados(self):
        base = dict(id=ARQUIVO, mimeType=MIME, isAppAuthorized=True, trashed=False, version='1')
        for versao in [None, '', True, 1, 1., 'v1', '-1', '1.0', '1\n', '1' * 31]:
            with self.subTest(versao=versao), self.assertRaises(ErroProvedor):
                await self.provedor(dict(base, version=versao)).versao_arquivo('falso', ARQUIVO)
        for meta in [[], {}, dict(base, id='outro'), dict(base, mimeType='text/plain'),
                     dict(base, isAppAuthorized=False), dict(base, trashed=True)]:
            with self.subTest(meta=meta), self.assertRaises(ErroProvedor):
                await self.provedor(meta).versao_arquivo('falso', ARQUIVO)

    async def test_analise_nao_aceita_versao_vazia_mesmo_igual_antes_depois(self):
        from testes.test_carteira_leitura import grade, ARQUIVO as arquivo_grade
        requests = []
        def handler(req):
            requests.append(req)
            if req.url.host == 'sheets.googleapis.com':
                return httpx.Response(200, json=grade([['chave', 'valor', 'célula', 'parte'], ['formato.versao', 12]]))
            return httpx.Response(200, json=dict(id=arquivo_grade, mimeType=MIME, isAppAuthorized=True, version=''))
        p = Provedores(configuracao(Path('nao_criar_versao.sqlite3')), transporte=httpx.MockTransport(handler))
        with self.assertRaises(ErroProvedor): await p.ler_analise('falso', arquivo_grade)
        self.assertEqual(len(requests), 1)
