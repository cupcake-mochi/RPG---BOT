"""Modelos: persistência, fronteiras OAuth e transporte Google fictício."""
from dataclasses import replace
from pathlib import Path
import unittest

from cryptography.fernet import Fernet
import httpx

from carteira_viva.esquema import VERSAO
from carteira_viva.banco import Cadastro
from carteira_viva.modelos import CriacaoBloqueada, referencia_validada
from carteira_viva.provedores import Provedores, ErroProvedor
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from carteira_viva.sondagem_modelo import MAX_LINHAS_HISTORICO, faixas_sondagem, sondar
from carteira_viva.web import DADOS
from testes.test_carteira_banco import Fixtures, schema_historico
from testes.test_carteira_provedores import configuracao
from testes.test_carteira_web import WebFixture, ProvedorFicticio, F1


def referencia():
    return dict(arquivo=F1,nome_arquivo='Modelo sintético privado',nome='Modelo',contrato='analise-12',
                revisao_livro='R53',versao_drive='7',sinais=['extrato_presente','estado_salarial_presente'])


def grade():
    # Estrutura CellData; offsets reais, valores exclusivamente fictícios.
    def text(v): return {'userEnteredValue':{'stringValue':v},'effectiveValue':{'stringValue':v}}
    def formula(v): return {'userEnteredValue':{'formulaValue':v},'effectiveValue':{'numberValue':0}}
    def sheet(name,row,col,rows):
        return {'properties':{'title':name,'gridProperties':{'rowCount':1000,'columnCount':140}},
                'data':[{'startRow':row,'startColumn':col,'rowData':[{'values':r} for r in rows]}]}
    return {'spreadsheetId':F1,'sheets':[
        sheet('ANALISE',0,0,[[text('chave'),text('valor')],[text('formato.versao'),text('12')],
                            [text('ficha.versao'),text('R53')],[text('ficha.sistema'),text('Ciclo Maldito')],
                            [text('ficha.livro'),text('Ciclo Maldito R53')]]),
        sheet('FICHA',10,33,[[{'effectiveValue':{'numberValue':2}},{},{},{},{},{},formula('=DADOS!$CZ$47')]]),
        sheet('DADOS',46,103,[[formula("=SUM('FICHA PESSOAL'!BA15:BA87)")]]),
        sheet('CONFIGURAÇÃO',45,4,[[{}, {},formula('=IF(F46="";E46;F46)')]]),
        sheet('EXTRATO',1,0,[[text('dado fictício')]]),
        sheet('DADOS_SALARIOS',1,11,[[text('{"estado":"fictício"}')]]),
        sheet('SALÁRIOS',1,0,[]),sheet('FICHA PESSOAL',14,48,[])]}


class BancoModelos(Fixtures,unittest.TestCase):
    def salvar(self,**kw):
        return self.c.configurar_modelo(self.admin,escolha='servidor',revisao=0,previa=referencia(),**kw)

    def test_padrao_oficiais_sem_escolher_campanha(self):
        d=self.c.modelos(self.m)
        self.assertEqual(d['escolha'],'oficiais')
        self.assertEqual([x['id'] for x in d['oficiais']],['era','ciclo'])
        self.assertFalse(d['criacao_disponivel'])
        self.assertEqual(d['parametros_suportados'],[])
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM modelos_servidor').fetchone()[0],0)

    def test_configuracao_so_admin_nao_manage_guild_ou_revisor(self):
        self.c.configurar(self.admin,revisores=['revisor'])
        for m in (self.m,replace(self.m,gerenciar_servidor=True),replace(self.m,cargos=frozenset({'revisor'})),replace(self.admin,presente=False)):
            with self.subTest(m=m),self.assertRaises(AcessoNegado):
                self.c.configurar_modelo(m,escolha='era',revisao=0)
        self.c.configurar_modelo(replace(self.m,dono_servidor=True),escolha='era',revisao=0)

    def test_troca_modelo_nao_muda_personagens_fontes_ou_campanha(self):
        p=self.criar();self.analise(p)
        antes=self.c.detalhes(self.m,p['id'])
        self.salvar()
        self.c.configurar_modelo(self.admin,escolha='ciclo',revisao=1)
        self.assertEqual(self.c.detalhes(self.m,p['id']),antes)
        self.assertEqual(self.c.modelos(replace(self.m,servidor='outra'))['escolha'],'oficiais')
        self.assertEqual(self.criar()['perfil']['nome'],'Personagem fictício')

    def test_cas_impede_confirmação_antiga_apos_reset(self):
        self.salvar()
        self.c.configurar_modelo(self.admin,escolha='oficiais',revisao=1)
        with self.assertRaises(Conflito):self.c.configurar_modelo(self.admin,escolha='era',revisao=1)
        self.assertEqual(self.c.modelos(self.m)['revisao'],2)

    def test_referencia_cifrada_sem_expor_nome_arquivo_ou_grant(self):
        d=self.salvar()
        for valor in (F1,referencia()['nome_arquivo'],'versao_drive','sinais'):
            self.assertNotIn(valor,str(d))
        self.assertNotIn(F1.encode(),self.path.read_bytes())
        self.assertEqual(self.c.revisar_modelo(self.admin)['referencia']['arquivo'],F1)
        with self.assertRaises(AcessoNegado):self.c.revisar_modelo(self.m)
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM conexoes').fetchone()[0],0)

    def test_rotacao_reinicio_e_backup_preservam_modelo_sem_sessoes(self):
        from carteira_viva.backup import gravar_backup,restaurar_backup
        self.salvar();nova=Fernet.generate_key();self.c.rotacionar_chave(nova);self.reabrir((nova,))
        b=self.pasta/'modelo.cvb';gravar_backup(self.c,b)
        self.c.configurar_modelo(self.admin,escolha='oficiais',revisao=1)
        destino=self.pasta/'restaurado.sqlite3'
        restaurar_backup(b,destino,(nova,),remocoes=self.c.remocoes,agora=self.agora)
        with Cadastro(destino,(nova,),remocoes=self.c.remocoes,agora=self.agora) as restaurado:
            self.assertEqual(restaurado.revisar_modelo(self.admin)['referencia']['arquivo'],F1)
            self.assertEqual(restaurado.db.execute('SELECT count(*) FROM web_sessoes').fetchone()[0],0)

    def test_migracao_schema5_preserva_personagem(self):
        p=self.criar()
        schema_historico(self.c.db,5)
        self.reabrir()
        self.assertEqual(self.c.db.execute('PRAGMA user_version').fetchone()[0],VERSAO)
        self.assertEqual(self.c.cartao(self.m,p['id'])['perfil'],p['perfil'])

    def test_criacao_fechada_mesmo_sem_sinais_e_com_parametros_forcados(self):
        ref=referencia();ref['sinais']=[];ref['sondagem_versao']=2
        self.c.configurar_modelo(self.admin,escolha='servidor',revisao=0,previa=ref)
        for modelo in ('era','ciclo','servidor','desconhecido'):
            for params in (None,{}, {'nivel':5,'xp':0,'nivel_inicial':5,'habilitar':True}):
                with self.subTest(modelo=modelo,params=params),self.assertRaises(CriacaoBloqueada):
                    self.c.criar_por_modelo(self.m,modelo=modelo,parametros=params)
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM personagens').fetchone()[0],0)


class SondagemTeste(unittest.TestCase):
    def test_detecta_estado_antigo_com_emissao_vazia(self):
        self.assertEqual(sondar(grade()),['estado_salarial_presente','extrato_presente'])

    def test_cobre_livros_ate_ultima_linha_fisica_sem_truncar(self):
        faixas=faixas_sondagem(grade())
        self.assertIn("'EXTRATO'!A2:C1000",faixas)
        self.assertIn("'SALÁRIOS'!A2:L1000",faixas)
        self.assertIn("'DADOS_SALARIOS'!A2:J1000",faixas)
        g=grade();g['sheets'][4]['data'][0].update(startRow=999)
        g['sheets'][6]['data'][0].update(startRow=999,rowData=[{'values':[{'userEnteredValue':{'stringValue':'crédito antigo fictício'}}]}])
        self.assertIn('extrato_presente',sondar(g))
        self.assertIn('salarios_presentes',sondar(g))

    def test_grade_incompativel_ou_acima_do_limite_recusada_antes_dos_dados(self):
        for indice,chave,valor in ((4,'rowCount',MAX_LINHAS_HISTORICO+1),(6,'rowCount',True),
                                  (5,'columnCount',13),(7,'rowCount',86),(7,'columnCount',67)):
            g=grade();g['sheets'][indice]['properties']['gridProperties'][chave]=valor
            with self.subTest(indice=indice,chave=chave,valor=valor),self.assertRaises(ErroCarteira):faixas_sondagem(g)

    def test_registros_e_trocas_salariais_tardios_sem_expor_valores(self):
        g=grade();g['sheets'][5]['data'].append({'startRow':800,'startColumn':0,'rowData':[{'values':[
            {'userEnteredValue':{'stringValue':'identidade confidencial fictícia'}}, {},{},{},{},{},{},
            {'userEnteredValue':{'numberValue':45000}},{'userEnteredValue':{'stringValue':'Grau'}}]}]})
        sinais=sondar(g)
        self.assertIn('missoes_registradas',sinais);self.assertIn('trocas_salariais_presentes',sinais)
        self.assertNotIn('confidencial',str(sinais));self.assertNotIn('45000',str(sinais))

    def test_nota_salarial_sobrevive_sem_valor_na_missao(self):
        g=grade();g['sheets'][7]['data'][0]['rowData']=[{'values':[
            {'note':'Descrição pessoal fictícia\n[Salário: id-ficticio · data pendente]'}]}]
        sinais=sondar(g)
        self.assertIn('marcas_salariais_presentes',sinais);self.assertNotIn('missoes_preenchidas',sinais)
        self.assertNotIn('id-ficticio',str(sinais));self.assertNotIn('Descrição',str(sinais))

    def test_caixas_de_missao_e_dinheiro_nao_se_confundem_com_xp(self):
        g=grade();g['sheets'][7]['data'].extend([
            {'startRow':85,'startColumn':14,'rowData':[{'values':[{'userEnteredValue':{'formulaValue':'=0'},'effectiveValue':{'numberValue':0}}]}]},
            {'startRow':10,'startColumn':66,'rowData':[{'values':[{'userEnteredValue':{'stringValue':'✓ missão anterior'}}]}]},
            {'startRow':86,'startColumn':66,'rowData':[{'values':[{'userEnteredValue':{'stringValue':'Missão anterior'}}]}]}])
        sinais=sondar(g)
        self.assertIn('caixa_financeira_preenchida',sinais);self.assertIn('correcao_missao_pendente',sinais)
        self.assertIn('missoes_preenchidas',sinais)

    def test_referencia_distingue_sondagem_anterior_de_nova(self):
        antiga=referencia();nova={**antiga,'sondagem_versao':2,'sinais':['marcas_salariais_presentes','trocas_salariais_presentes']}
        self.assertEqual(referencia_validada(antiga)['sondagem_versao'],1)
        self.assertEqual(referencia_validada(nova)['sondagem_versao'],2)
        for valor in (True,0,3,'2'):
            with self.subTest(valor=valor),self.assertRaises(ErroCarteira):referencia_validada({**nova,'sondagem_versao':valor})

    def test_recusa_formula_substituida_aba_ausente_revisao_errada_e_erro(self):
        for mutate in (lambda g:g['sheets'].pop(),
                       lambda g:g['sheets'][1]['data'][0]['rowData'][0]['values'].__setitem__(6,{'effectiveValue':{'numberValue':0}}),
                       lambda g:g['sheets'][0]['data'][0]['rowData'][2]['values'][1]['effectiveValue'].update(stringValue='R54'),
                       lambda g:g['sheets'][2]['data'][0]['rowData'][0]['values'][0]['effectiveValue'].update(errorValue={'type':'REF'})):
            g=grade();mutate(g)
            with self.assertRaises(ErroCarteira):sondar(g)


class TransporteModelo(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.calls=[];self.changed=False;self.meta_calls=0;self.grid=grade()
        self.prov=Provedores(configuracao(Path('nao-criar.sqlite3')),transporte=httpx.MockTransport(self.handler))

    def handler(self,request):
        self.calls.append(request)
        if '/values/' in request.url.path:
            return httpx.Response(200,json={'values':[['formato.versao',12],['nome','Exemplo']]})
        if request.url.host=='sheets.googleapis.com':
            if 'ranges' not in request.url.params:
                return httpx.Response(200,json={'spreadsheetId':self.grid['spreadsheetId'],
                    'sheets':[{'properties':s['properties']} for s in self.grid['sheets']]})
            return httpx.Response(200,json=self.grid)
        self.meta_calls+=1
        return httpx.Response(200,json={'id':F1,'name':'Modelo fictício','mimeType':'application/vnd.google-apps.spreadsheet',
            'isAppAuthorized':True,'version':'8' if self.changed and self.meta_calls>1 else '7'})

    async def test_previa_so_leitura_e_sem_conteudo_financeiro(self):
        d=await self.prov.validar_modelo('access_ficticio',F1)
        self.assertEqual(d['sinais'],['estado_salarial_presente','extrato_presente'])
        self.assertNotIn('dado fictício',str(d));self.assertEqual(d['versao_drive'],'7')
        self.assertTrue(all(r.method=='GET' for r in self.calls))
        grid_request=next(r for r in self.calls if r.url.host=='sheets.googleapis.com' and 'ranges' in r.url.params)
        faixas=grid_request.url.params.get_list('ranges')
        self.assertEqual(len(faixas),15);self.assertIn("'EXTRATO'!A2:C1000",faixas)
        self.assertIn('note',grid_request.url.params['fields']);self.assertEqual(d['sondagem_versao'],2)

    async def test_grade_maior_nao_cai_para_amostra_que_parece_vazia(self):
        self.grid['sheets'][4]['properties']['gridProperties']['rowCount']=MAX_LINHAS_HISTORICO+1
        with self.assertRaises(ErroCarteira):await self.prov.validar_modelo('ficticio',F1)
        self.assertFalse(any('ranges' in r.url.params for r in self.calls))

    async def test_notas_privadas_viram_so_sinal_na_previa(self):
        self.grid['sheets'][7]['data'][0]['rowData']=[{'values':[{'note':'[Salário: segredo-ficticio · data pendente]'}]}]
        d=await self.prov.validar_modelo('ficticio',F1)
        self.assertIn('marcas_salariais_presentes',d['sinais']);self.assertNotIn('segredo-ficticio',str(d))

    async def test_arquivo_mudando_durante_leitura_e_recusado(self):
        self.changed=True
        with self.assertRaises(ErroProvedor):await self.prov.validar_modelo('ficticio',F1)

    async def test_id_invalido_nao_sai_na_rede(self):
        with self.assertRaises(ErroProvedor):await self.prov.validar_modelo('ficticio','https://alheio.invalid')
        self.assertEqual(self.calls,[])


class ProvedorModelo(ProvedorFicticio):
    admin=True
    versao='7'
    remover_admin=False
    sondagem_versao=2
    nota_posterior=False

    async def membro(self,s,u):
        return replace(await super().membro(s,u),administrador=self.admin)

    async def validar_modelo(self,acesso,arquivo):
        await super().validar_arquivo(acesso,arquivo)
        if self.remover_admin:self.admin=False
        d={**referencia(),'arquivo':arquivo,'versao_drive':self.versao,'sondagem_versao':self.sondagem_versao}
        if self.nota_posterior:d['sinais']=d['sinais']+['marcas_salariais_presentes']
        return d


class WebModeloTeste(WebFixture,unittest.IsolatedAsyncioTestCase):
    provedor_tipo=ProvedorModelo

    async def preparar(self):
        await self.comecar('modelo');await self.oauth('discord');await self.oauth('google');await self.selecionar()

    async def test_fluxo_modelo_sem_cadastro_ou_conexao_e_idempotente(self):
        await self.preparar()
        a=await self.confirmar();self.assertEqual(a.status,200,await a.text());d=await a.json()
        b=await self.confirmar();self.assertEqual(await b.json(),d)
        for table in ('personagens','fontes','conexoes'):
            self.assertEqual(await self.scalar('SELECT count(*) FROM '+table),0)
        self.assertEqual(await self.scalar('SELECT revisao FROM modelos_servidor'),1)
        await self.atualizar();self.assertNotIn('google',self.s);self.assertIsNone(self.s['previa'])

    async def test_membro_comum_nao_inicia_modelo(self):
        self.prov.admin=False
        r=await self.client.post('/interno/conexoes',json={'servidor':'111','usuario':'222','acao':'modelo'},headers={'Authorization':'Bearer '+self.cfg.servico_token})
        self.assertEqual(r.status,403)

    async def test_perda_admin_durante_confirmacao_nao_salva(self):
        await self.preparar();self.prov.remover_admin=True
        self.assertEqual((await self.confirmar()).status,403)
        self.assertEqual(await self.scalar('SELECT count(*) FROM modelos_servidor'),0)

    async def test_perda_admin_durante_selecao_nao_devolve_previa(self):
        await self.comecar('modelo');await self.oauth('discord');await self.oauth('google')
        self.prov.remover_admin=True
        self.assertEqual((await self.post('/api/selecionar',{'arquivo':F1})).status,403)
        self.assertEqual(await self.scalar('SELECT count(*) FROM modelos_servidor'),0)

    async def test_mudanca_de_arquivo_apos_previa_exige_novo_fluxo(self):
        await self.preparar();self.prov.versao='8'
        self.assertEqual((await self.confirmar()).status,409)
        self.assertEqual(await self.scalar('SELECT count(*) FROM modelos_servidor'),0)

    async def test_marca_salarial_nova_durante_confirmacao_invalida_previa(self):
        await self.preparar();self.prov.nota_posterior=True
        self.assertEqual((await self.confirmar()).status,409)
        self.assertEqual(await self.scalar('SELECT count(*) FROM modelos_servidor'),0)

    async def test_nao_confirma_resultado_de_outra_versao_de_sondagem(self):
        await self.preparar();self.prov.sondagem_versao=1
        self.assertEqual((await self.confirmar()).status,409)
        self.assertEqual(await self.scalar('SELECT count(*) FROM modelos_servidor'),0)

    async def test_configuracao_concorrente_nao_sobrescrita(self):
        await self.preparar()
        await self.app[DADOS].chamar('cadastro.configurar_modelo',replace(self.membro,administrador=True),escolha='era',revisao=0)
        self.assertEqual((await self.confirmar()).status,409)
        self.assertEqual((await self.app[DADOS].chamar('cadastro.modelos',self.membro))['escolha'],'era')

    async def test_cancelar_expirar_e_parametro_adulterado(self):
        await self.preparar()
        self.assertEqual((await self.post('/api/confirmar',{'responsabilidade':True,'nivel':5})).status,400)
        self.assertEqual((await self.post('/api/cancelar')).status,200)
        self.assertNotEqual((await self.confirmar()).status,200)
        self.clock[0]+=601
        self.assertEqual((await self.confirmar()).status,410)
        self.assertEqual(await self.scalar('SELECT count(*) FROM modelos_servidor'),0)

    async def test_rotacao_descarta_fluxo_modelo_transitorio(self):
        await self.preparar()
        await self.app[DADOS].chamar('cadastro.rotacionar_chave',Fernet.generate_key())
        self.assertEqual(await self.scalar('SELECT count(*) FROM web_fluxos'),0)
        self.assertEqual((await self.confirmar()).status,410)

    async def test_endpoint_criacao_recusa_parametros_sem_chamar_google(self):
        for modelo in ('era','ciclo','servidor'):
            r=await self.client.post('/interno/galeria/acao/criar_por_modelo',json={'servidor':'111','usuario':'222','modelo':modelo,'parametros':{'nivel':5}},headers={'Authorization':'Bearer '+self.cfg.servico_token})
            self.assertEqual(r.status,400);self.assertEqual((await r.json())['erro'],'modelo_bloqueado')
        self.assertEqual(self.prov.validacoes,0)
