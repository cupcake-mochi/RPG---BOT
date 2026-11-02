"""Diagnóstico sem afrouxar leitura; HTTP fictício, sem Google/Discord."""
import asyncio
from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from carteira_viva.diagnostico_grade import CATEGORIAS, DiagnosticoGrade, PRAZO
from carteira_viva.provedores import ErroProvedor
from carteira_viva.segredos import ErroCarteira
from testes.test_carteira_grade_inicializacao import Cenario, ARQUIVO


class DiagnosticoTeste(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.c = Cenario()
        self.d = DiagnosticoGrade(agora=lambda: self.c.tempo)
        self.addCleanup(self.d.fechar)

    async def observar(self, dominio='progressao'):
        plano = await self.c.abrir(dominio)
        return await self.d.observar(self.c.leitor, 'credencial_ficticia', plano)

    def dados_primeira_faixa(self, celula):
        def alterar(req, obj):
            if req.url.params.get('ranges') == "'CONFIGURAÇÃO'!C46:H46":
                obj['sheets'][0]['data'][0]['rowData'] = [{'values': [celula]}]
            return obj
        self.c.alterar = alterar

    async def test_duas_coletas_mesmo_conteudo_versoes_diferentes_sem_autorizar(self):
        await self.observar()
        self.c.versao = '9007199254740994'
        await self.observar()
        r = self.d.comparar()
        self.assertTrue(r['versoes_iniciais_diferentes'])
        self.assertTrue(r['cobertura_compativel'])
        self.assertEqual(r['paginas_comparadas'], len(self.c.plano.faixas))
        self.assertEqual(r['paginas_com_mudanca'], dict.fromkeys(CATEGORIAS, 0))
        for chave in ('criacao_disponivel', 'conferencia_conjunta_concluida',
                      'consistencia_temporal_verificada', 'imagens_atuais_conferidas'):
            self.assertIs(r[chave], False)
        self.assertIn('propriedades_apps_script', r['nao_coberto'])
        self.assertIn('fora_das_faixas', r['nao_coberto'])
        self.assertTrue(all(q.method == 'GET' for q in self.c.requests))

    async def test_cada_categoria_e_comparada_separadamente(self):
        base = {'userEnteredValue': {'formulaValue': '=1'},
                'effectiveValue': {'numberValue': 1}, 'note': 'nota privada',
                'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '0'}}}
        for categoria, alterada in [
            ('formulas', {**base, 'userEnteredValue': {'formulaValue': '=SUM(1)'}}),
            ('resultados', {**base, 'effectiveValue': {'numberValue': 2}}),
            ('notas', {**base, 'note': 'outra nota privada'}),
            ('formatos_numericos', {**base, 'userEnteredFormat': {'numberFormat': {'type': 'NUMBER', 'pattern': '0.0'}}}),
        ]:
            with self.subTest(categoria=categoria):
                self.d.fechar(); self.d = DiagnosticoGrade(agora=lambda: self.c.tempo)
                self.dados_primeira_faixa(base); await self.observar()
                self.dados_primeira_faixa(alterada); await self.observar()
                esperado = dict.fromkeys(CATEGORIAS, 0); esperado[categoria] = 1
                self.assertEqual(self.d.comparar()['paginas_com_mudanca'], esperado)

    async def test_literal_formula_e_resultado_igual_nao_escondem_troca(self):
        self.dados_primeira_faixa({'userEnteredValue': {'formulaValue': '=1'}, 'effectiveValue': {'numberValue': 1}})
        await self.observar()
        self.dados_primeira_faixa({'userEnteredValue': {'numberValue': 1}, 'effectiveValue': {'numberValue': 1}})
        await self.observar()
        esperado = dict.fromkeys(CATEGORIAS, 0); esperado.update(literais=1, formulas=1)
        self.assertEqual(self.d.comparar()['paginas_com_mudanca'], esperado)

    async def test_texto_booleano_zero_e_ausencia_nao_se_confundem(self):
        for a, b in [(None, {'stringValue': ''}), ({'boolValue': False}, {'numberValue': 0}),
                     ({'numberValue': 1}, {'stringValue': '1'})]:
            with self.subTest(a=a, b=b):
                self.d.fechar(); self.d = DiagnosticoGrade(agora=lambda: self.c.tempo)
                self.dados_primeira_faixa({'userEnteredValue': a} if a else {})
                await self.observar()
                self.dados_primeira_faixa({'userEnteredValue': b}); await self.observar()
                self.assertEqual(self.d.comparar()['paginas_com_mudanca']['literais'], 1)

    async def test_numeros_equivalentes_nao_simulam_edicao(self):
        self.dados_primeira_faixa({'userEnteredValue': {'numberValue': 1}, 'effectiveValue': {'numberValue': 0}})
        await self.observar()
        self.dados_primeira_faixa({'userEnteredValue': {'numberValue': 1.0}, 'effectiveValue': {'numberValue': -0.0}})
        await self.observar()
        self.assertEqual(self.d.comparar()['paginas_com_mudanca'], dict.fromkeys(CATEGORIAS, 0))

    async def test_mudanca_de_versao_durante_leitura_mantem_so_paginas_aceitas(self):
        contador = 0
        def mudar(req, obj):
            nonlocal contador
            if 'ranges' in req.url.params:
                contador += 1
                if contador == 2: self.c.versao = '9007199254740994'
            return obj
        self.c.alterar = mudar
        r = await self.observar()
        self.assertEqual(r['paginas_lidas'], 1)
        self.assertFalse(r['coleta_completa']); self.assertTrue(r['versao_divergente'])
        # O mesmo plano continua recusado; diagnóstico não alterou sua versão.
        self.c.alterar = None
        with self.assertRaises(ErroProvedor): await self.c.pagina()
        self.dados_primeira_faixa({'userEnteredValue': {'numberValue': 3}})
        await self.observar()
        r = self.d.comparar()
        self.assertEqual(r['paginas_comparadas'], 1)
        self.assertEqual(r['paginas_com_mudanca']['literais'], 1)
        self.assertFalse(r['amostras'][0]['coleta_completa'])

    async def test_mudanca_no_fechamento_nao_certifica_amostra_completa(self):
        plano = await self.c.abrir('progressao'); contagem = 0
        def mudar(req, obj):
            nonlocal contagem
            if req.url.host == 'www.googleapis.com':
                contagem += 1
                if contagem == 2*len(plano.faixas)+1: obj['version'] = '9007199254740994'
            return obj
        self.c.alterar = mudar
        r = await self.d.observar(self.c.leitor, 'ficticio', plano)
        self.assertEqual(r['paginas_lidas'], len(plano.faixas))
        self.assertFalse(r['coleta_completa']); self.assertTrue(r['versao_divergente'])

    async def test_nenhuma_pagina_em_comum_nao_retorna_zero_mudancas(self):
        p = await self.c.abrir('progressao'); self.c.versao = '9007199254740994'
        await self.d.observar(self.c.leitor, 'ficticio', p)
        await self.observar()
        r = self.d.comparar()
        self.assertEqual(r['paginas_comparadas'], 0)
        self.assertEqual(r['paginas_com_mudanca'], dict.fromkeys(CATEGORIAS))

    async def test_mudanca_de_dimensao_torna_cobertura_incomparavel(self):
        await self.observar()
        self.c.grades['CONFIGURAÇÃO']['gridProperties']['rowCount'] -= 1
        await self.observar()
        r = self.d.comparar()
        self.assertFalse(r['cobertura_compativel']); self.assertEqual(r['paginas_comparadas'], 0)
        self.assertEqual(r['paginas_com_mudanca'], dict.fromkeys(CATEGORIAS))

    async def test_contexto_ou_dominio_diferente_recusado_sem_nova_leitura(self):
        await self.observar()
        self.c.contexto = 'd'*64
        p = await self.c.abrir('progressao'); n = len(self.c.requests)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', p)
        self.assertEqual(len(self.c.requests), n)
        self.c.contexto = 'c'*64
        p = await self.c.abrir('financeiro'); n = len(self.c.requests)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', p)
        self.assertEqual(len(self.c.requests), n)

    async def test_mesmo_plano_terceira_amostra_e_resumo_precoce_recusados(self):
        with self.assertRaises(ErroCarteira): self.d.comparar()
        p = await self.c.abrir('progressao')
        await self.d.observar(self.c.leitor, 'ficticio', p)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', p)
        await self.observar()
        p = await self.c.abrir('progressao'); n = len(self.c.requests)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', p)
        self.assertEqual(len(self.c.requests), n)

    async def test_callback_de_acesso_mudado_nao_preserva_diagnostico_parcial(self):
        await self.observar()
        p = await self.c.abrir('progressao'); self.c.contexto = 'd'*64
        with self.assertRaises(ErroProvedor): await self.d.observar(self.c.leitor, 'ficticio', p)
        self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)
        with self.assertRaises(ErroCarteira): self.d.comparar()

    async def test_erro_http_e_cancelamento_descartam_tudo(self):
        for erro in (ErroProvedor('temporario'), asyncio.CancelledError()):
            with self.subTest(erro=type(erro).__name__):
                self.d.fechar(); self.d = DiagnosticoGrade(agora=lambda: self.c.tempo)
                await self.observar(); p = await self.c.abrir('progressao')
                with patch.object(self.c.leitor, 'pagina', side_effect=erro):
                    with self.assertRaises(type(erro)): await self.d.observar(self.c.leitor, 'ficticio', p)
                self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)

    async def test_expiracao_apaga_hashes_e_nao_renova_prazo(self):
        await self.observar(); self.c.tempo += PRAZO-1
        await self.observar(); self.d.comparar()
        self.c.tempo += 1
        with self.assertRaises(ErroCarteira): self.d.comparar()
        self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)

    async def test_resumo_e_repr_sem_valores_hashes_ids_versoes_ou_coordenadas(self):
        self.dados_primeira_faixa({'userEnteredValue': {'formulaValue': '=SEGREDO_DO_JOGADOR'},
                                  'note': 'nota privada do jogador'})
        await self.observar(); await self.observar()
        publico = json.dumps(self.d.comparar(), ensure_ascii=False)+repr(self.d)
        privado = repr(self.d.__dict__)
        for segredo in (ARQUIVO, 'credencial_ficticia', self.c.versao, 'c'*64,
                        'CONFIGURAÇÃO', '=SEGREDO_DO_JOGADOR', 'nota privada do jogador'):
            self.assertNotIn(segredo, publico); self.assertNotIn(segredo, privado)
        self.assertNotIn(self.d._amostras[0]['grade'].hex(), publico)

    async def test_hmacs_nao_comparaveis_entre_instancias_e_sem_rede_extra(self):
        p = await self.c.abrir('progressao'); n = len(self.c.requests)
        await self.d.observar(self.c.leitor, 'ficticio', p)
        self.assertEqual(len(self.c.requests)-n, 3*len(p.faixas)+1)
        outro = DiagnosticoGrade(agora=lambda: self.c.tempo)
        try:
            await outro.observar(self.c.leitor, 'ficticio', p)
            self.assertNotEqual(self.d._amostras[0]['paginas'], outro._amostras[0]['paginas'])
        finally: outro.fechar()

    async def test_deslocar_conteudo_dentro_da_pagina_nao_passa_por_igual(self):
        valores = [{'note': 'nota fictícia'}, {}]
        def alterar(req, obj):
            if req.url.params.get('ranges') == "'CONFIGURAÇÃO'!C46:H46":
                obj['sheets'][0]['data'][0]['rowData'] = [{'values': valores}]
            return obj
        self.c.alterar = alterar
        await self.observar()
        valores = [{}, {'note': 'nota fictícia'}]
        await self.observar()
        self.assertEqual(self.d.comparar()['paginas_com_mudanca']['notas'], 1)

    async def test_outra_fonte_nao_pode_ser_comparada_nem_se_conteudo_igual(self):
        await self.observar(); p = await self.c.abrir('progressao')
        outro = replace(p, arquivo='outra_fonte_descartavel_sintetica')
        n = len(self.c.requests)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', outro)
        self.assertEqual(len(self.c.requests), n)

    async def test_pagina_falsa_ou_celula_malformada_nao_deixam_hash_parcial(self):
        from carteira_viva.grade_inicializacao import CelulaGrade, PaginaGrade
        for tipo in ('faixa', 'celula', 'tipo'):
            with self.subTest(tipo=tipo):
                self.d.fechar(); self.d = DiagnosticoGrade(agora=lambda: self.c.tempo)
                await self.observar(); p = await self.c.abrir('progressao')
                pagina = await self.c.pagina()
                if tipo == 'faixa': falsa = replace(pagina, faixa=replace(pagina.faixa))
                elif tipo == 'tipo': falsa = pagina.__dict__
                else:
                    linhas = list(pagina.celulas); linha = list(linhas[0])
                    linha[0] = CelulaGrade(('numberValue', True), None, '', None)
                    linhas[0] = tuple(linha); falsa = PaginaGrade(pagina.faixa, tuple(linhas))
                with patch.object(self.c.leitor, 'pagina', return_value=falsa):
                    with self.assertRaises((ErroCarteira, ErroProvedor)):
                        await self.d.observar(self.c.leitor, 'ficticio', p)
                self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)

    async def test_limite_de_pagina_recusa_sem_reter_texto_ou_grade_grande(self):
        await self.observar(); p = await self.c.abrir('progressao')
        # Limite artificial baixo, sem alocar megabytes no teste.
        from carteira_viva.grade_inicializacao import CelulaGrade, PaginaGrade
        linhas = list((await self.c.pagina()).celulas); primeira = list(linhas[0])
        primeira[0] = CelulaGrade(('stringValue', 'x'*300), None, '', None)
        linhas[0] = tuple(primeira); pagina = PaginaGrade(p.faixas[0], tuple(linhas))
        with patch('carteira_viva.diagnostico_grade.MAX_BYTES', 250):
            # _pagina também limita o volume já parseado, não só a resposta HTTP.
            with self.assertRaises(ErroCarteira): self.d._pagina(p.faixas[0], pagina)

    async def test_fechamento_explicito_impede_reuso(self):
        await self.observar(); self.d.fechar(); p = await self.c.abrir('progressao')
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', p)
        with self.assertRaises(ErroCarteira): self.d.comparar()
        self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)

    async def test_paginas_excessivas_recusadas_antes_de_qualquer_get(self):
        p = await self.c.abrir('progressao'); n = len(self.c.requests)
        falso = replace(p, faixas=(p.faixas[0],)*129)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', falso)
        self.assertEqual(len(self.c.requests), n)

    async def test_expiracao_durante_pagina_descarta_primeira_amostra_tambem(self):
        await self.observar(); p = await self.c.abrir('progressao')
        def expirar(req, obj):
            if 'ranges' in req.url.params: self.c.tempo += PRAZO
            return obj
        self.c.alterar = expirar
        with self.assertRaises(ErroProvedor): await self.d.observar(self.c.leitor, 'ficticio', p)
        self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)

    async def test_erro_de_formula_na_resposta_nao_gera_amostra_completa(self):
        self.dados_primeira_faixa({'effectiveValue': {'errorValue': {'type': 'REF', 'message': 'privado'}}})
        with self.assertRaises(ErroProvedor) as e: await self.observar()
        self.assertEqual(e.exception.codigo, 'recalculo')
        self.assertFalse(self.d._amostras); self.assertFalse(self.d._chave)

    async def test_concorrencia_e_plano_de_outro_leitor_recusados(self):
        de_outro = await Cenario().abrir('progressao'); n = len(self.c.requests)
        with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', de_outro)
        self.assertEqual(len(self.c.requests), n)
        p = await self.c.abrir('progressao')
        iniciou = asyncio.Event(); liberar = asyncio.Event(); original = self.c.leitor.pagina
        async def pagina(*args):
            iniciou.set(); await liberar.wait(); return await original(*args)
        with patch.object(self.c.leitor, 'pagina', side_effect=pagina):
            tarefa = asyncio.create_task(self.d.observar(self.c.leitor, 'ficticio', p))
            await iniciou.wait()
            with self.assertRaises(ErroCarteira): await self.d.observar(self.c.leitor, 'ficticio', p)
            liberar.set(); await tarefa
