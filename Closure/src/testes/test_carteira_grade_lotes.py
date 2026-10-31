"""GET com ranges repetidos: cobertura exata e recusa do lote inteiro."""
import asyncio
import copy
from dataclasses import replace
import unittest
from unittest.mock import patch

import httpx

from carteira_viva.diagnostico_grade import DiagnosticoGrade
from carteira_viva.grade_inicializacao import LeitorGradeRest, MAX_CELULAS, MAX_FAIXAS_LOTE
from carteira_viva.provedores import ErroProvedor, VersaoAlterada
from testes.test_carteira_conferencia_inicializacao import Dados
from testes.test_carteira_grade_inicializacao import Cenario, ARQUIVO


def agrupado(c):
    return LeitorGradeRest(c.p, c.revalidar, c.cota, agora=lambda: c.tempo, agrupar=True)


class LotesTeste(unittest.IsolatedAsyncioTestCase):
    async def preparar(self, dominio='progressao', *, dados=True):
        self.c = Dados(dominio) if dados else Cenario()
        self.l = agrupado(self.c)
        self.p = await self.l.abrir('credencial_ficticia', ARQUIVO, dominio)
        return self.c

    async def coletar(self):
        return [(i, p) async for i, p in self.l.paginas('credencial_ficticia', self.p)]

    async def test_particao_progressao_preserva_as_oito_faixas_em_dois_gets(self):
        c = await self.preparar(); n = len(c.requests)
        self.assertEqual(self.l.lotes(self.p), ((0, 1, 2, 3), (4, 5, 6, 7)))
        paginas = await self.coletar()
        self.assertEqual([i for i, _ in paginas], list(range(8)))
        self.assertEqual(len(c.requests)-n, 6)  # Dois Drive + um Sheets por lote.
        for i, p in paginas: self.assertIs(p.faixa, self.p.faixas[i])
        gets = [r for r in c.requests[n:] if 'ranges' in r.url.params]
        self.assertEqual(len(gets), 2)
        self.assertEqual([a for r in gets for a in r.url.params.get_list('ranges')], [f.a1() for f in self.p.faixas])
        self.assertTrue(all(r.method == 'GET' for r in c.requests))
        self.assertTrue(all('credencial_ficticia' not in str(r.url) for r in c.requests))

    async def test_resultado_e_identidade_iguais_ao_leitor_individual(self):
        c = await self.preparar(); a = await self.coletar()
        p2 = await c.leitor.abrir('ficticio', ARQUIVO, 'progressao')
        b = [(i, await c.leitor.pagina('ficticio', p2, i)) for i in range(len(p2.faixas))]
        self.assertEqual([(i, p.celulas) for i, p in a], [(i, p.celulas) for i, p in b])
        self.assertEqual(self.p.versao, p2.versao)

    async def test_ordem_de_abas_e_blocos_da_resposta_nao_troca_os_dados(self):
        c = await self.preparar(); esperado = await self.coletar()
        def inverter(req, obj):
            if 'ranges' in req.url.params:
                obj['sheets'].reverse()
                for s in obj['sheets']: s['data'].reverse()
            return obj
        c.alterar = inverter
        self.assertEqual([(i, p.celulas) for i, p in await self.coletar()],
                         [(i, p.celulas) for i, p in esperado])

    async def test_blocos_vazios_e_offsets_zero_omitidos_continuam_posicoes_exatas(self):
        c = await self.preparar('financeiro', dados=False)
        def omitir(req, obj):
            if 'ranges' in req.url.params:
                for s in obj['sheets']:
                    for b in s['data']:
                        b.pop('rowData')
                        if b['startColumn'] == 0: b.pop('startColumn')
            return obj
        c.alterar = omitir
        # Primeiro lote financeiro tem quatro retângulos de quatro colunas.
        ps = await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(len(ps), 4)
        self.assertTrue(all(x.entrada is None for p in ps for row in p.celulas for x in row))
        # Último lote pertence a livro cujo início de coluna é zero.
        ps = await self.l.lote('ficticio', self.p, len(self.l.lotes(self.p))-1)
        self.assertTrue(ps); self.assertEqual(ps[0].faixa.pos[1], 0)

    async def test_teto_e_ultima_linha_5000_nao_sao_truncados(self):
        c = await self.preparar('financeiro'); grupos = self.l.lotes(self.p)
        self.assertEqual([i for g in grupos for i in g], list(range(len(self.p.faixas))))
        self.assertLess(len(grupos), len(self.p.faixas))
        for g in grupos:
            self.assertLessEqual(len(g), MAX_FAIXAS_LOTE)
            self.assertLessEqual(sum((self.p.faixas[i].pos[2]-self.p.faixas[i].pos[0]) *
                                    (self.p.faixas[i].pos[3]-self.p.faixas[i].pos[1]) for i in g), MAX_CELULAS)
        c.literal('DADOS_SALARIOS', 5000, 10, 'cauda fictícia')
        ultimas = await self.l.lote('ficticio', self.p, len(grupos)-1)
        self.assertEqual(ultimas[-1].faixa.pos[2], 5000)
        self.assertEqual(ultimas[-1].celulas[-1][-1].entrada, ('stringValue', 'cauda fictícia'))

    async def test_sobreposicao_e_mesmo_inicio_nunca_compartilham_lote(self):
        await self.preparar()
        f = self.p.faixas[0]
        p = replace(self.p, faixas=(f, f, replace(f, pos=(45, 3, 46, 7))))
        self.assertEqual(self.l.lotes(p), ((0,), (1,), (2,)))

    async def test_lote_fora_do_plano_e_booleanos_recusados_sem_rede(self):
        c = await self.preparar(); n = len(c.requests)
        for indice in (-1, True, 0.0, '0', None, (0, 1), len(self.l.lotes(self.p))):
            with self.subTest(indice=indice), self.assertRaises(ErroProvedor):
                await self.l.lote('ficticio', self.p, indice)
        self.assertEqual(len(c.requests), n)

    async def test_plano_de_outro_leitor_e_json_recusados_sem_rede(self):
        c = await self.preparar(); n = len(c.requests)
        for p in (replace(self.p, dono=object()), self.p.progresso(), None):
            with self.assertRaises(ErroProvedor): await self.l.lote('ficticio', p, 0)
        self.assertEqual(len(c.requests), n)

    async def test_opcao_de_agrupamento_nao_aceita_flags_de_formulario(self):
        c = Cenario()
        for v in (1, 0, 'true', None, {}):
            with self.assertRaises(ValueError): LeitorGradeRest(c.p, c.revalidar, c.cota, agrupar=v)
        self.assertFalse(c.requests)

    async def test_bloco_posterior_invalido_nao_entrega_prefixo_do_lote(self):
        c = await self.preparar(); recebidas = []
        def invalidar(req, obj):
            if 'ranges' in req.url.params:
                obj['sheets'][-1]['data'][-1]['rowData'] = [{'values': [{'objetoDesconhecido': 'privado'}]}]
            return obj
        c.alterar = invalidar
        with self.assertRaises(ErroProvedor):
            async for i, p in self.l.paginas('ficticio', self.p): recebidas.append(i)
        self.assertFalse(recebidas)

    async def test_blocos_ausentes_duplicados_ou_estranhos_recusam(self):
        for tipo in ('ausente', 'duplicado', 'deslocado', 'booleano', 'extra', 'sem_data'):
            c = await self.preparar()
            def alterar(req, obj):
                if 'ranges' not in req.url.params: return obj
                s = obj['sheets'][-1]
                if tipo == 'ausente': s['data'].pop()
                elif tipo == 'duplicado': s['data'][-1] = copy.deepcopy(s['data'][0])
                elif tipo == 'deslocado': s['data'][-1]['startColumn'] += 1
                elif tipo == 'booleano': s['data'][-1]['startRow'] = True
                elif tipo == 'extra': s['data'].append(copy.deepcopy(s['data'][0]))
                else: s.pop('data')
                return obj
            c.alterar = alterar
            with self.subTest(tipo=tipo), self.assertRaises(ErroProvedor): await self.l.lote('ficticio', self.p, 0)

    async def test_aba_extra_removida_renomeada_ou_redimensionada_recusam(self):
        for tipo in ('extra', 'ausente', 'nome', 'dimensao'):
            c = await self.preparar()
            def alterar(req, obj):
                if 'ranges' not in req.url.params: return obj
                if tipo == 'extra': obj['sheets'].append(copy.deepcopy(obj['sheets'][0]))
                elif tipo == 'ausente': obj['sheets'].pop()
                elif tipo == 'nome': obj['sheets'][0]['properties']['title'] = 'outra aba'
                else: obj['sheets'][0]['properties']['gridProperties']['rowCount'] -= 1
                return obj
            c.alterar = alterar
            with self.subTest(tipo=tipo), self.assertRaises(ErroProvedor): await self.l.lote('ficticio', self.p, 0)

    async def test_grade_de_outro_arquivo_recusa_com_mensagem_sem_id(self):
        c = await self.preparar()
        def outro(req, obj):
            if 'ranges' in req.url.params: obj['spreadsheetId'] = 'arquivo_nao_autorizado_ficticio'
            return obj
        c.alterar = outro
        with self.assertRaises(ErroProvedor) as e: await self.l.lote('ficticio', self.p, 0)
        self.assertNotIn(ARQUIVO, str(e.exception))

    async def test_mudanca_na_resposta_recusa_todo_lote_sem_adotar_versao(self):
        c = await self.preparar(); original = self.p.versao
        c.depois = lambda: setattr(c, 'versao', '9007199254740994')
        with self.assertRaises(VersaoAlterada): await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(self.p.versao, original)
        n = len(c.requests)
        with self.assertRaises(VersaoAlterada): await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(len(c.requests), n+1)  # Só observação Drive, sem GET de células.

    async def test_segundo_lote_alterado_so_conserva_paginas_do_primeiro(self):
        c = await self.preparar(); n = 0; recebidas = []
        def mudar(req, obj):
            nonlocal n
            if 'ranges' in req.url.params:
                n += 1
                if n == 2: c.versao = '9007199254740994'
            return obj
        c.alterar = mudar
        with self.assertRaises(VersaoAlterada):
            async for i, p in self.l.paginas('ficticio', self.p): recebidas.append(i)
        self.assertEqual(recebidas, [0, 1, 2, 3])

    async def test_cota_revalida_contexto_sem_usar_credencial_antiga(self):
        c = await self.preparar(); n = len(c.requests)
        async def trocar(): c.contexto = 'd'*64
        c.ao_esperar = trocar
        with self.assertRaises(ErroProvedor) as e: await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(e.exception.codigo, 'acesso'); self.assertEqual(len(c.requests), n)

    async def test_cada_get_do_lote_mantem_contexto_cota_contexto_e_pos_checagem(self):
        c = await self.preparar(); eventos = []; original = c.http
        async def validar(): eventos.append('contexto'); return c.contexto
        async def cota(): eventos.append('cota')
        def http(req): eventos.append('get'); return original(req)
        c.p.transporte = httpx.MockTransport(http)
        l = LeitorGradeRest(c.p, validar, cota, agora=lambda: c.tempo, agrupar=True)
        p = await l.abrir('ficticio', ARQUIVO, 'progressao'); eventos.clear()
        await l.lote('ficticio', p, 0)
        self.assertEqual(eventos, ['contexto', 'cota', 'contexto', 'get', 'contexto']*3)

    async def test_erro_de_formula_em_bloco_posterior_nao_vira_amostra_parcial(self):
        c = await self.preparar(); d = DiagnosticoGrade(agora=lambda: c.tempo)
        def erro(req, obj):
            if 'ranges' in req.url.params:
                obj['sheets'][-1]['data'][-1]['rowData'] = [{'values': [
                    {'effectiveValue': {'errorValue': {'type': 'REF', 'message': 'privado'}}}]}]
            return obj
        c.alterar = erro
        with self.assertRaises(ErroProvedor) as e: await d.observar(self.l, 'ficticio', self.p)
        self.assertEqual(e.exception.codigo, 'recalculo')
        self.assertFalse(d._amostras); self.assertFalse(d._chave)

    async def test_429_nao_repete_ou_faz_fallback_para_paginas_individuais(self):
        c = await self.preparar()
        def falhar(req, obj): return httpx.Response(429) if 'ranges' in req.url.params else obj
        c.alterar = falhar
        with self.assertRaises(ErroProvedor): await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(sum('ranges' in r.url.params for r in c.requests), 1)

    async def test_limite_de_bytes_e_do_get_inteiro_sem_retry(self):
        c = await self.preparar(dados=False); c.celulas = [{'values': [{'note': 'x'*1000}]}]
        with patch('carteira_viva.grade_inicializacao.MAX_BYTES', 2000):
            with self.assertRaises(ErroProvedor) as e: await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(e.exception.codigo, 'tamanho')
        self.assertEqual(sum('ranges' in r.url.params for r in c.requests), 1)

    async def test_json_aninhado_dentro_do_teto_recusa_como_erro_do_provedor(self):
        c = await self.preparar(dados=False)
        corpo = b'[' * 200000 + b']' * 200000
        def aninhado(req, obj): return httpx.Response(200, content=corpo) if 'ranges' in req.url.params else obj
        c.alterar = aninhado
        with self.assertRaises(ErroProvedor) as e: await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(e.exception.codigo, 'temporario')
        self.assertEqual(sum('ranges' in r.url.params for r in c.requests), 1)

    async def test_expiracao_durante_get_nao_entrega_lote(self):
        c = await self.preparar(); c.depois = lambda: setattr(c, 'tempo', c.tempo+1800)
        with self.assertRaises(ErroProvedor) as e: await self.l.lote('ficticio', self.p, 0)
        self.assertEqual(e.exception.codigo, 'expirado')

    async def test_cancelar_get_nao_busca_outra_pagina(self):
        c = await self.preparar(); iniciou = asyncio.Event(); liberar = asyncio.Event()
        original = c.http
        async def http(req):
            if 'ranges' in req.url.params: iniciou.set(); await liberar.wait()
            return original(req)
        c.p.transporte = httpx.MockTransport(http)
        t = asyncio.create_task(self.l.lote('ficticio', self.p, 0)); await asyncio.wait_for(iniciou.wait(), 5)
        t.cancel()
        with self.assertRaises(asyncio.CancelledError): await t
        self.assertFalse(any('ranges' in r.url.params for r in c.requests))

    async def test_fechar_iterador_descarta_lote_sem_continuar_rede(self):
        c = await self.preparar(); it = self.l.paginas('ficticio', self.p)
        i, p = await anext(it); self.assertEqual(i, 0); n = len(c.requests)
        await it.aclose(); self.assertIsNone(it.ag_frame)
        self.assertEqual(len(c.requests), n)

    async def test_expiracao_entre_paginas_do_mesmo_lote_impede_entrega(self):
        c = await self.preparar(); it = self.l.paginas('ficticio', self.p)
        await anext(it); n = len(c.requests); c.tempo += 1800
        with self.assertRaises(ErroProvedor) as e: await anext(it)
        self.assertEqual(e.exception.codigo, 'expirado')
        self.assertIsNone(it.ag_frame); self.assertEqual(len(c.requests), n)

    async def test_hashes_logicos_iguais_entre_leitura_individual_e_agrupada(self):
        c = Dados('progressao'); d = DiagnosticoGrade(agora=lambda: c.tempo)
        try:
            a = await c.leitor.abrir('ficticio', ARQUIVO, 'progressao')
            await d.observar(c.leitor, 'ficticio', a)
            l = agrupado(c); b = await l.abrir('ficticio', ARQUIVO, 'progressao')
            await d.observar(l, 'ficticio', b)
            r = d.comparar()
            self.assertTrue(r['cobertura_compativel']); self.assertEqual(r['paginas_comparadas'], 8)
            self.assertTrue(all(v == 0 for v in r['paginas_com_mudanca'].values()))
        finally: d.fechar()

    async def test_pagina_individual_permanece_individual_mesmo_com_flag_ativa(self):
        c = await self.preparar(); n = len(c.requests)
        await self.l.pagina('ficticio', self.p, 0)
        self.assertEqual(len(c.requests)-n, 3)
        self.assertEqual(len(c.requests[-2].url.params.get_list('ranges')), 1)
