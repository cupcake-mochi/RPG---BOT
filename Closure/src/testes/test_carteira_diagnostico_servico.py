"""Serviço/banco reais, transporte fictício; não usa Google ou Discord."""
import asyncio
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

import httpx

from carteira_viva.diagnostico_grade import DiagnosticoGrade
from carteira_viva.grade_inicializacao import FIXAS
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from carteira_viva.provedores import ErroProvedor, MIME
from testes import test_carteira_financeiro_rest as fixture_financeiro
from testes.test_carteira_grade_inicializacao import ARQUIVO
from testes.test_carteira_modelos import referencia


class DiagnosticoServicoTeste(unittest.IsolatedAsyncioTestCase):
    # Reusar só fixtures/helpers, sem herdar e repetir toda a classe de testes.
    asyncSetUp = fixture_financeiro.FinanceiroRestTeste.asyncSetUp
    asyncTearDown = fixture_financeiro.FinanceiroRestTeste.asyncTearDown
    b = fixture_financeiro.FinanceiroRestTeste.b
    executar_no_worker = fixture_financeiro.FinanceiroRestTeste.executar_no_worker

    async def http(self, req):
        if req.url.host == 'www.googleapis.com' and req.url.path.rsplit('/', 1)[-1] == self.fonte:
            self.req.append(req)
            if self.http_hook: await self.http_hook(req)
            return httpx.Response(200, json={**dict(id=self.fonte, mimeType=MIME,
                isAppAuthorized=True, trashed=False, version=self.source_version,
                ownedByMe=True, shared=False, permissions=[dict(type='user', role='owner')]),
                **getattr(self, 'source_patch', {})})
        if req.url.host == 'sheets.googleapis.com' and self.fonte in req.url.path:
            self.req.append(req)
            if self.http_hook: await self.http_hook(req)
            fake = httpx.Request(req.method, str(req.url).replace(self.fonte, ARQUIVO), headers=req.headers)
            resp = self.data.http(fake); obj = json.loads(resp.content)
            obj['spreadsheetId'] = self.fonte
            return httpx.Response(resp.status_code, json=obj)
        if getattr(self, 'sem_membro', False) and req.url.host == 'discord.com' and '/members/' in req.url.path:
            self.req.append(req); return httpx.Response(404)
        if getattr(self, 'falhar_sheets', False) and req.url.host == 'sheets.googleapis.com':
            self.req.append(req); return httpx.Response(429)
        return await fixture_financeiro.FinanceiroRestTeste.http(self, req)

    async def diagnosticar(self, *, alvo='copia', dominio='financeiro', ref=None):
        return await self.s.diagnosticar_grade_copia('111', '222', ref or self.ref,
                                                   alvo=alvo, dominio=dominio)

    def sheets(self):
        return [r for r in self.req if r.url.host == 'sheets.googleapis.com']

    async def estado_copia(self, **trocas):
        def mudar(c):
            d = c.contexto_copia(self.m, self.ref)
            c._guardar_copia(self.ref, {**d, **trocas})
        await self.executar_no_worker(mudar)

    async def test_copia_identificada_so_le_sem_mudar_diario_ou_criar_personagem(self):
        antes = await self.b('contexto_copia', self.m, self.ref)
        dados_antes = repr(self.data.mapa)
        r = await self.diagnosticar()
        self.assertTrue(all(a['coleta_completa'] for a in r['amostras']))
        self.assertEqual(r['versao_mudou_apos_coleta'], [False, False])
        self.assertEqual(r['versao_mudou_antes_coleta'], [False, False])
        self.assertEqual(r['paginas_com_mudanca'], dict.fromkeys(r['paginas_com_mudanca'], 0))
        self.assertEqual(await self.b('contexto_copia', self.m, self.ref), antes)
        self.assertEqual(repr(self.data.mapa), dados_antes)
        self.assertIsNone(await self.b('estado_financeiro', self.m, self.ref))
        self.assertFalse(await self.b('listar', self.m)); self.assertFalse(self.posts)
        self.assertFalse(any(q.method != 'GET' for q in self.req if q.url.host in ('www.googleapis.com', 'sheets.googleapis.com')))
        for chave in ('criacao_disponivel', 'conferencia_conjunta_concluida',
                      'consistencia_temporal_verificada', 'imagens_atuais_conferidas'):
            self.assertIs(r[chave], False)
        texto = json.dumps(r)
        for segredo in (ARQUIVO, self.fonte, self.ref.operacao, 'ficticio', 'nota privada', 'histórico privado'):
            self.assertNotIn(segredo, texto)
        # Só as duas observações completas da renovação comum consultam roles.
        # Todas as conferências de contexto continuam com GET novo do membro.
        self.assertEqual(sum(q.url.path.endswith('/roles') for q in self.req), 2)

    async def test_origem_derivada_do_banco_pode_ser_lida_sem_marcador_de_copia(self):
        r = await self.diagnosticar(alvo='origem')
        self.assertTrue(all(a['coleta_completa'] for a in r['amostras']))
        self.assertTrue(all(self.fonte in q.url.path for q in self.sheets()))
        self.assertFalse(any(ARQUIVO in q.url.path for q in self.req if q.url.host == 'www.googleapis.com'))
        self.assertFalse(self.posts)

    async def test_versao_nova_diagnosticada_nao_e_adotada_pelo_financeiro(self):
        self.data.versao = '8'; self.source_version = '8'
        await self.diagnosticar()
        d = await self.b('contexto_copia', self.m, self.ref)
        self.assertEqual((d['versao_origem'], d['versao_destino'], d['candidata']['versao']), ('7', '7', '7'))
        self.source_version = '7'
        with self.assertRaises(Conflito): await self.s.inicializar_financeiro_celulas('111', '222', self.ref)
        self.assertFalse(self.posts)

    async def test_candidata_pendente_nao_e_identificada_pelo_diagnostico(self):
        await self.estado_copia(estado='enviada', destino=None, versao_destino=None)
        r = await self.diagnosticar()
        self.assertTrue(r['amostras'][0]['coleta_completa'])
        d = await self.b('contexto_copia', self.m, self.ref)
        self.assertEqual(d['estado'], 'enviada'); self.assertIsNone(d['destino'])

    async def test_sem_candidata_so_permite_diagnostico_da_origem(self):
        await self.estado_copia(estado='enviada', destino=None, versao_destino=None, candidata=None)
        with self.assertRaises(Conflito): await self.diagnosticar()
        self.assertFalse(any(r.url.host != 'discord.com' for r in self.req))
        self.assertTrue((await self.diagnosticar(alvo='origem'))['amostras'][0]['coleta_completa'])

    async def test_preparada_e_backup_sem_versao_original_recusados_antes_do_google(self):
        for estado, versao in [('preparada', '7'), ('enviada', None)]:
            await self.estado_copia(estado=estado, versao_origem=versao)
            with self.assertRaises(Conflito): await self.diagnosticar()
        self.assertFalse(any(r.url.host != 'discord.com' for r in self.req))

    async def test_origem_preparada_pode_ser_diagnosticada_sem_armar_ou_fixar_versao(self):
        await self.estado_copia(estado='preparada', versao_origem=None, destino=None,
                               versao_destino=None, candidata=None)
        antes = await self.b('contexto_copia', self.m, self.ref)
        r = await self.diagnosticar(alvo='origem')
        self.assertTrue(r['amostras'][0]['coleta_completa'])
        self.assertEqual(await self.b('contexto_copia', self.m, self.ref), antes)
        self.assertFalse(any(q.method != 'GET' for q in self.req if q.url.host in ('www.googleapis.com', 'sheets.googleapis.com')))
        self.assertFalse(self.posts)
        with self.assertRaises(Conflito): await self.b('armar_envio_copia', self.m, self.ref)

    async def test_referencia_cliente_ator_ou_servidor_diferentes_sem_rede(self):
        for servidor, usuario, ref in [('111', '999', self.ref), ('999', '222', self.ref),
                                      ('111', '222', {'arquivo': ARQUIVO})]:
            with self.assertRaises(AcessoNegado):
                await self.s.diagnosticar_grade_copia(servidor, usuario, ref, alvo='copia', dominio='financeiro')
        self.assertFalse(self.req)

    async def test_alvo_e_dominio_arbitrarios_recusados_sem_rede(self):
        for alvo, dominio in [(ARQUIVO, 'financeiro'), ('copia', "'FICHA'!A1:Z99"),
                              ({}, 'financeiro'), ('origem', True)]:
            with self.assertRaises(ErroCarteira): await self.diagnosticar(alvo=alvo, dominio=dominio)
        self.assertFalse(self.req)

    async def test_copia_cadastrada_em_outra_mesa_recusa_antes_do_google(self):
        await self.b('cadastrar', replace(self.m, servidor='mesa2'), conexao=self.cid, arquivo=ARQUIVO,
                     nome='Fictício', contrato='analise-12', responsabilidade=True, pedido='x')
        with self.assertRaises(Conflito): await self.diagnosticar()
        self.assertFalse(any(r.url.host != 'discord.com' for r in self.req))

    async def test_admin_ou_revisor_nao_usam_conexao_do_dono(self):
        for m in (replace(self.m, usuario='999', administrador=True),
                  replace(self.m, usuario='999', dono_servidor=True),
                  replace(self.m, usuario='999', cargos=frozenset({'revisor'}))):
            with self.assertRaises(AcessoNegado): await self.b('contexto_diagnostico_copia', m, self.ref, 'copia')
        self.assertFalse(self.req)

    async def test_modelo_oficial_recusa_mesmo_quando_disfarcado_de_particular(self):
        from carteira_viva.modelos import OFICIAIS
        import re
        origem = re.search(r'/d/([A-Za-z0-9_-]+)', OFICIAIS[0]['url']).group(1)
        def trocar(c):
            config = c.revisar_modelo(replace(self.m, administrador=True))
            nova = {**referencia(), 'arquivo': origem}
            c.configurar_modelo(replace(self.m, administrador=True), escolha='servidor', revisao=config['revisao'], previa=nova)
            row = c.db.execute('SELECT * FROM copias_rest WHERE operacao=?', (self.ref.operacao,)).fetchone()
            d = c.cifra.abrir(c._ctx_copia(row), row['conteudo'])
            d.update(c._origem_modelo_copia('111', 'servidor')); c._guardar_copia(self.ref, d)
        await self.executar_no_worker(trocar)
        with self.assertRaises(Conflito): await self.diagnosticar()
        self.assertFalse(any(r.url.host != 'discord.com' for r in self.req))

    async def test_privacidade_e_marcadores_recusados_antes_das_celulas(self):
        for patch_meta in ({'shared': True}, {'ownedByMe': False}, {'driveId': 'outro-drive'},
                           {'permissions': []}, {'appProperties': {}}, {'trashed': True}):
            self.meta_patch = patch_meta
            with self.subTest(patch=patch_meta), self.assertRaises(ErroProvedor): await self.diagnosticar()
        self.assertFalse(self.sheets()); self.assertFalse(self.posts)

    async def test_fonte_compartilhada_ou_sem_propriedade_privada_recusa(self):
        for p in ({'shared': True}, {'ownedByMe': False}, {'permissions': []}, {'trashed': True}):
            self.source_patch = p
            with self.assertRaises(ErroProvedor): await self.diagnosticar(alvo='origem')
        self.assertFalse(self.sheets())

    async def test_perda_de_privacidade_no_fechamento_nao_entrega_resumo(self):
        n = 0
        async def hook(req):
            nonlocal n
            if req.url.host == 'www.googleapis.com' and 'ownedByMe' in req.url.params.get('fields', ''):
                n += 1
                if n == 2: self.meta_patch = {'shared': True}
        self.http_hook = hook
        with self.assertRaises(ErroProvedor): await self.diagnosticar()
        self.assertEqual(n, 2); self.assertFalse(self.posts)

    async def test_cota_revalida_revogacao_antes_de_acessar_arquivo(self):
        async def revogar(): await self.b('desconectar', self.m, self.cid)
        self.cotas.hook = revogar
        with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(any(r.url.host in ('www.googleapis.com', 'sheets.googleapis.com') for r in self.req))

    async def test_membro_sai_durante_cota_nao_acessa_arquivo(self):
        async def sair(): self.sem_membro = True
        self.cotas.hook = sair
        with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(any(r.url.host in ('www.googleapis.com', 'sheets.googleapis.com') for r in self.req))

    async def test_mudanca_de_configuracao_durante_pagina_descarta_resumo(self):
        async def mudar(req):
            if req.url.host == 'sheets.googleapis.com' and 'ranges' in req.url.params:
                await self.b('configurar_modelo', replace(self.m, administrador=True), escolha='ciclo', revisao=1)
        self.http_hook = mudar
        with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(self.posts)

    async def test_mudanca_enquanto_aguarda_fila_recusa_antes_de_renovar(self):
        executar = self.s.fila.executar
        async def mudar(*args, **kwargs):
            await self.b('configurar_modelo', replace(self.m, administrador=True), escolha='ciclo', revisao=1)
            return await executar(*args, **kwargs)
        with patch.object(self.s.fila, 'executar', side_effect=mudar):
            with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(any(r.url.host != 'discord.com' for r in self.req))

    async def test_revogacao_depois_da_fila_recusa_entrega(self):
        executar = self.s.fila.executar
        async def revogar(*args, **kwargs):
            r = await executar(*args, **kwargs)
            await self.b('desconectar', self.m, self.cid)
            return r
        with patch.object(self.s.fila, 'executar', side_effect=revogar):
            with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(self.posts)

    async def test_mudanca_de_versao_preserva_parcial_sem_repetir_ate_estabilizar(self):
        mudou = False
        async def hook(req):
            nonlocal mudou
            if req.url.host == 'sheets.googleapis.com' and 'ranges' in req.url.params and not mudou:
                mudou = True; self.data.versao = '8'
        self.http_hook = hook
        r = await self.diagnosticar()
        self.assertFalse(r['amostras'][0]['coleta_completa'])
        self.assertTrue(r['amostras'][0]['versao_divergente'])
        self.assertTrue(r['amostras'][1]['coleta_completa'])
        self.assertEqual(r['paginas_comparadas'], 0)
        self.assertTrue(all(v is None for v in r['paginas_com_mudanca'].values()))
        self.assertFalse(self.posts)

    async def test_mudanca_apos_confirmacao_e_indicada_sem_adotar_versao(self):
        n = 0
        async def hook(req):
            nonlocal n
            if req.url.host == 'www.googleapis.com' and 'ownedByMe' in req.url.params.get('fields', ''):
                n += 1
                if n == 2: self.data.versao = '8'
        self.http_hook = hook
        r = await self.diagnosticar()
        self.assertEqual(r['versao_mudou_apos_coleta'], [True, False])
        self.assertTrue(r['versoes_iniciais_diferentes'])
        self.assertEqual((await self.b('contexto_copia', self.m, self.ref))['versao_destino'], '7')

    async def test_mudanca_entre_privacidade_e_abertura_tambem_e_indicada(self):
        primeira = True
        async def hook(req):
            nonlocal primeira
            if (req.url.host == 'www.googleapis.com' and
                    'ownedByMe' not in req.url.params.get('fields', '') and primeira):
                primeira = False; self.data.versao = '8'
        self.http_hook = hook
        r = await self.diagnosticar()
        self.assertEqual(r['versao_mudou_antes_coleta'], [True, False])
        self.assertEqual((await self.b('contexto_copia', self.m, self.ref))['versao_destino'], '7')

    async def test_progressao_e_dominio_fixo_suportado_sem_escrita(self):
        r = await self.diagnosticar(dominio='progressao')
        self.assertTrue(all(x['coleta_completa'] for x in r['amostras']))
        self.assertEqual(sum('ranges' in q.url.params for q in self.sheets()), 4)
        self.assertEqual(sum(len(q.url.params.get_list('ranges')) for q in self.sheets()), 2*len(FIXAS['progressao']))
        self.assertFalse(self.posts)

    async def test_lotes_reduzem_rede_com_mesmo_resumo_e_cobertura(self):
        from carteira_viva.grade_inicializacao import LeitorGradeRest
        resultados, contagens = [], []
        for agrupar in (False, True):
            self.req.clear()
            def criar(*args, **kwargs):
                kwargs['agrupar'] = agrupar
                return LeitorGradeRest(*args, **kwargs)
            with patch('carteira_viva.diagnostico_servico.LeitorGradeRest', side_effect=criar):
                resultados.append(await self.diagnosticar(dominio='progressao'))
            contagens.append((len(self.req),
                sum(r.url.host == 'sheets.googleapis.com' for r in self.req),
                sum(r.url.host == 'www.googleapis.com' for r in self.req),
                sum('/members/' in r.url.path for r in self.req)))
        self.assertEqual(resultados[0], resultados[1])
        self.assertEqual(contagens, [(253, 18, 42, 188), (109, 6, 18, 80)])
        self.assertEqual(resultados[1]['paginas_comparadas'], 8)
        self.assertFalse(resultados[1]['criacao_disponivel'])

    async def test_registrar_copia_durante_leitura_impede_entrega(self):
        async def cadastrar(req):
            if req.url.host == 'sheets.googleapis.com' and 'ranges' in req.url.params:
                await self.b('cadastrar', replace(self.m, servidor='mesa2'), conexao=self.cid, arquivo=ARQUIVO,
                             nome='Fictício', contrato='analise-12', responsabilidade=True, pedido='x')
        self.http_hook = cadastrar
        with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(self.posts)

    async def test_origem_cadastrada_so_pode_ser_lida_sem_alterar_personagem(self):
        p = await self.b('cadastrar', self.m, conexao=self.cid, arquivo=self.fonte, nome='Fonte fictícia',
                         contrato='analise-12', responsabilidade=True, pedido='x')
        antes = await self.b('detalhes', self.m, p['id'])
        await self.diagnosticar(alvo='origem')
        self.assertEqual(await self.b('detalhes', self.m, p['id']), antes)
        self.assertFalse(self.posts)

    async def test_reautorizacao_durante_renovacao_nao_herda_operacao(self):
        async def reconectar(req):
            if req.url.host == 'oauth2.googleapis.com':
                await self.b('conectar', self.m, conta='conta-ficticia', cliente=self.cfg.google_id,
                             refresh_token='refresh-novo-ficticio')
        self.http_hook = reconectar
        with self.assertRaises(ErroCarteira): await self.diagnosticar()
        self.assertFalse(self.sheets())

    async def test_resumo_descartado_no_erro_apaga_hashes_da_coleta_anterior(self):
        d = DiagnosticoGrade(); n = 0
        async def hook(req):
            nonlocal n
            if req.url.host == 'www.googleapis.com' and 'ownedByMe' in req.url.params.get('fields', ''):
                n += 1
                if n == 3: self.meta_patch = {'shared': True}
        self.http_hook = hook
        with patch('carteira_viva.diagnostico_servico.DiagnosticoGrade', return_value=d):
            with self.assertRaises(ErroProvedor): await self.diagnosticar()
        self.assertTrue(d._fechado); self.assertFalse(d._chave); self.assertFalse(d._amostras)

    async def test_429_na_leitura_nao_repete_chamada_nem_entrega_parcial(self):
        self.falhar_sheets = True
        with self.assertRaises(ErroProvedor): await self.diagnosticar()
        self.assertEqual(len(self.sheets()), 1); self.assertFalse(self.posts)

    async def test_token_revogado_nao_acessa_arquivos(self):
        self.token_erro = True
        with self.assertRaises(ErroProvedor) as erro: await self.diagnosticar()
        self.assertEqual(erro.exception.codigo, 'revogada')
        self.assertFalse(any(r.url.host in ('www.googleapis.com', 'sheets.googleapis.com') for r in self.req))
        with self.assertRaises(ErroCarteira): await self.b('contexto_copia', self.m, self.ref)

    async def test_expiracao_do_token_na_cota_nao_acessa_arquivo(self):
        async def expirar(): self.clock[0] += 3590
        self.cotas.hook = expirar
        with self.assertRaises(ErroProvedor) as erro: await self.diagnosticar()
        self.assertEqual(erro.exception.codigo, 'expirado')
        self.assertFalse(any(r.url.host in ('www.googleapis.com', 'sheets.googleapis.com') for r in self.req))

    async def test_recibo_legado_identificado_e_diagnosticado_sem_reescrever_protocolo(self):
        def legado(c):
            d = c.contexto_copia(self.m, self.ref)
            d.pop('protocolo_copia'); d.pop('candidata')
            c._guardar_copia(self.ref, d)
        await self.executar_no_worker(legado)
        await self.diagnosticar()
        d = await self.b('contexto_copia', self.m, self.ref)
        self.assertNotIn('protocolo_copia', d); self.assertNotIn('candidata', d)
        self.assertEqual(d['versao_destino'], '7')

    async def test_configuracao_de_modelo_oficial_nao_abre_este_piloto(self):
        def oficial(c):
            c.configurar_modelo(replace(self.m, administrador=True), escolha='ciclo', revisao=1)
            row = c.db.execute('SELECT * FROM copias_rest WHERE operacao=?', (self.ref.operacao,)).fetchone()
            d = c.cifra.abrir(c._ctx_copia(row), row['conteudo'])
            d.update(c._origem_modelo_copia('111', 'ciclo')); c._guardar_copia(self.ref, d)
        await self.executar_no_worker(oficial)
        with self.assertRaises(Conflito): await self.diagnosticar()
        self.assertFalse(any(r.url.host != 'discord.com' for r in self.req))

    async def test_pedidos_coalescem_e_resumos_nao_compartilham_objetos(self):
        iniciou = asyncio.Event(); liberar = asyncio.Event()
        async def hook(req):
            if req.url.host == 'sheets.googleapis.com': iniciou.set(); await liberar.wait()
        self.http_hook = hook
        t1 = asyncio.create_task(self.diagnosticar()); await asyncio.wait_for(iniciou.wait(), 5)
        t2 = asyncio.create_task(self.diagnosticar())
        async def esperar():
            while not any(p.clientes == 2 for p in self.s.fila.pedidos.values()): await asyncio.sleep(0)
        await asyncio.wait_for(esperar(), 5); liberar.set()
        a, b = await asyncio.gather(t1, t2)
        a['amostras'][0]['paginas_lidas'] = -1
        self.assertGreater(b['amostras'][0]['paginas_lidas'], 0)
        # As mesmas 21 faixas cabem em seis lotes; duas aberturas + 12 lotes.
        self.assertEqual(len(self.sheets()), 14)
        self.assertEqual(sum(len(q.url.params.get_list('ranges')) for q in self.sheets()), 42)
        self.assertEqual(sum(r.url.host == 'oauth2.googleapis.com' for r in self.req), 1)

    async def test_ultimo_cancelamento_fecha_comparador_e_nao_envia_post(self):
        iniciou = asyncio.Event(); liberar = asyncio.Event(); d = DiagnosticoGrade()
        async def hook(req):
            if req.url.host == 'sheets.googleapis.com': iniciou.set(); await liberar.wait()
        self.http_hook = hook
        with patch('carteira_viva.diagnostico_servico.DiagnosticoGrade', return_value=d):
            tarefa = asyncio.create_task(self.diagnosticar()); await asyncio.wait_for(iniciou.wait(), 5)
            tarefa.cancel()
            with self.assertRaises(asyncio.CancelledError): await tarefa
            async def esperar():
                while not d._fechado: await asyncio.sleep(0)
            await asyncio.wait_for(esperar(), 5)
        self.assertFalse(d._chave); self.assertFalse(d._amostras); self.assertFalse(self.posts)
