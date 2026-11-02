"""Transporte HTTP real com respostas simuladas; nenhuma chamada Google."""
import asyncio
import copy
from pathlib import Path
import unittest
import httpx
from carteira_viva.grade_inicializacao import LeitorGradeRest, FIXAS, MAX_CELULAS, CAMPOS
from carteira_viva.provedores import Provedores, MIME, ErroProvedor
from carteira_viva.segredos import AcessoNegado
from testes.test_carteira_provedores import configuracao
ARQUIVO='arquivo_descartavel_sintetico_001'

def mascara(texto):
    # Gramática independente do transporte: paths do fields, listas e grupos.
    import re
    tokens=re.findall(r'[A-Za-z][A-Za-z0-9]*|[(),]',texto);i=0;paths=set()
    if ''.join(tokens)!=texto:raise ValueError('fields inválido')
    def lista(prefixo):
        nonlocal i
        while True:
            if i>=len(tokens) or not tokens[i][0].isalpha():raise ValueError('campo ausente')
            nome=tokens[i];i+=1
            if i<len(tokens) and tokens[i]=='(':
                i+=1;lista(prefixo+nome+'.')
                if i>=len(tokens) or tokens[i]!=')':raise ValueError('grupo aberto')
                i+=1
            else:paths.add(prefixo+nome)
            if i<len(tokens) and tokens[i]==',':i+=1
            else:break
    lista('')
    if i!=len(tokens):raise ValueError('grupo excedente')
    return paths

class Cenario:
    def __init__(self):
        self.contexto='c'*64;self.cotas=0;self.ao_esperar=None;self.versao='9007199254740993';self.tempo=10.;self.requests=[];self.alterar=None;self.depois=None;self.celulas=[]
        nomes=['FICHA PESSOAL','DADOS_SALARIOS','CONFIGURAÇÃO','CARTEIRA','FICHA','DADOS','EXTRATO','SALÁRIOS']
        self.grades={n:dict(sheetId=543479115+i,title=n,gridProperties=dict(rowCount=5000,columnCount=120)) for i,n in enumerate(nomes)}
        self.p=Provedores(configuracao(Path('nao_criar_grade.sqlite3')),transporte=httpx.MockTransport(self.http))
        self.leitor=LeitorGradeRest(self.p,self.revalidar,self.cota,agora=lambda:self.tempo)
    async def revalidar(self):return self.contexto
    async def cota(self):
        self.cotas+=1
        if self.ao_esperar:await self.ao_esperar()
    def linhas(self, nome, r, c, r2, c2):
        return copy.deepcopy(self.celulas)
    def http(self,req):
        self.requests.append(req)
        if req.url.host=='sheets.googleapis.com':
            try:mascara(req.url.params['fields'])
            except ValueError:return httpx.Response(400)
        if req.url.host=='www.googleapis.com':o=dict(id=ARQUIVO,mimeType=MIME,isAppAuthorized=True,trashed=False,version=self.versao)
        elif 'ranges' not in req.url.params:o=dict(spreadsheetId=ARQUIVO,sheets=[dict(properties=copy.deepcopy(v)) for v in self.grades.values()])
        else:
            from carteira_viva.grade_inicializacao import _retangulo
            sheets={}
            for faixa in req.url.params.get_list('ranges'):
                nome,a1=faixa.split('!');nome=nome.strip("'");r,c,r2,c2=_retangulo(a1)
                sheet=sheets.setdefault(nome,dict(properties=copy.deepcopy(self.grades[nome]),data=[]))
                sheet['data'].append(dict(startRow=r,startColumn=c,rowData=self.linhas(nome,r,c,r2,c2)))
            o=dict(spreadsheetId=ARQUIVO,sheets=list(sheets.values()))
            if self.depois:self.depois()
        if self.alterar:
            o=self.alterar(req,o)
            if isinstance(o,httpx.Response):return o
        return httpx.Response(200,json=o)
    async def abrir(self,dominio='financeiro'):
        self.plano=await self.leitor.abrir('credencial_ficticia',ARQUIVO,dominio);return self.plano
    async def pagina(self,i=0):return await self.leitor.pagina('credencial_ficticia',self.plano,i)

class GradeInicializacaoTeste(unittest.IsolatedAsyncioTestCase):
    async def test_divergencia_tipificada_guarda_versoes_so_para_diagnostico(self):
        from carteira_viva.provedores import VersaoAlterada
        c=Cenario();await c.abrir();original=c.versao;c.versao='9007199254740994'
        with self.assertRaises(VersaoAlterada) as erro:await c.pagina()
        self.assertEqual((erro.exception.esperada,erro.exception.observada),(original,c.versao))
        self.assertEqual(erro.exception.codigo,'alterada')
        for texto in (str(erro.exception),repr(erro.exception)):
            self.assertNotIn(original,texto);self.assertNotIn(c.versao,texto);self.assertNotIn(ARQUIVO,texto)

    async def test_mascara_http_valida_solicita_apenas_campos_necessarios(self):
        from carteira_viva.grade_inicializacao import META
        props={'sheets.properties.sheetId','sheets.properties.title','sheets.properties.gridProperties.rowCount','sheets.properties.gridProperties.columnCount','spreadsheetId'}
        self.assertEqual(mascara(META),props)
        self.assertEqual(mascara(CAMPOS),props|{'sheets.data.startRow','sheets.data.startColumn','sheets.data.rowData.values.userEnteredValue','sheets.data.rowData.values.effectiveValue','sheets.data.rowData.values.note','sheets.data.rowData.values.userEnteredFormat.numberFormat'})
        for mask in [CAMPOS+')',CAMPOS[:-1],CAMPOS+',',CAMPOS.replace('rowData(','rowData(,')]:
            with self.assertRaises(ValueError):mascara(mask)
    async def test_get_bearer_campos_limitados_e_repr_privado(self):
        c=Cenario();p=await c.abrir('progressao');c.celulas=[{'values':[{'userEnteredValue':{'formulaValue':'=A1'},'effectiveValue':{'numberValue':3},'note':'privado'}]}]
        x=await c.pagina();v=x.celulas[0][0]
        self.assertEqual(v.entrada,('formulaValue','=A1'));self.assertEqual(v.resultado,('numberValue',3));self.assertEqual(v.nota,'privado')
        self.assertEqual(p.versao,'9007199254740993');self.assertEqual(len(c.requests),6)
        for req in c.requests:
            self.assertEqual(req.method,'GET');self.assertIn(req.url.host,{'www.googleapis.com','sheets.googleapis.com'})
            self.assertEqual(req.headers['Authorization'],'Bearer credencial_ficticia');self.assertNotIn('credencial_ficticia',str(req.url))
        req=next(r for r in c.requests if 'ranges' in r.url.params);self.assertEqual(req.url.params['fields'],CAMPOS)
        for segredo in [ARQUIVO,'privado','=A1',p.versao,'credencial_ficticia']:self.assertNotIn(segredo,repr(p)+repr(x)+repr(v)+str(p.progresso()))
        self.assertTrue(all(v is False for k,v in p.progresso().items() if k!='paginas'))
    async def test_5000_linhas_sem_buracos_e_ultima_celula_lida(self):
        c=Cenario();p=await c.abrir()
        for nome,col in [('EXTRATO',3),('SALÁRIOS',12),('DADOS_SALARIOS',10)]:
            fs=[f for f in p.faixas[len(FIXAS['financeiro']):] if f.aba==nome]
            self.assertEqual(fs[0].pos[0],1);self.assertEqual(fs[-1].pos[2],5000)
            for a,b in zip(fs,fs[1:]):self.assertEqual(a.pos[2],b.pos[0])
            for f in fs:self.assertEqual((f.pos[1],f.pos[3]),(0,col))
        for f in p.faixas:
            r,col,r2,c2=f.pos;self.assertLessEqual((r2-r)*(c2-col),MAX_CELULAS)
        f=p.faixas[-1];h,w=f.pos[2]-f.pos[0],f.pos[3]-f.pos[1]
        c.celulas=[{} for _ in range(h)];c.celulas[-1]={'values':[{} for _ in range(w)]};c.celulas[-1]['values'][-1]={'effectiveValue':{'stringValue':'herdado'}}
        self.assertEqual((await c.pagina(len(p.faixas)-1)).celulas[-1][-1].resultado,('stringValue','herdado'))
    async def test_data_serial_booleano_zero_e_texto_com_igual_preservados(self):
        c=Cenario();await c.abrir('progressao');c.celulas=[{'values':[
            {'userEnteredValue':{'numberValue':46323},'effectiveValue':{'numberValue':46323},'userEnteredFormat':{'numberFormat':{'type':'DATE','pattern':'dd/mm/yyyy'}}},
            {'userEnteredValue':{'stringValue':'=texto'},'effectiveValue':{'stringValue':'=texto'}},
            {'userEnteredValue':{'boolValue':False},'effectiveValue':{'boolValue':False}}, {'effectiveValue':{'numberValue':0}}]}]
        x=(await c.pagina()).celulas[0];self.assertEqual(x[0].entrada,('numberValue',46323));self.assertEqual(x[0].formato_numero,('DATE','dd/mm/yyyy'))
        self.assertEqual(x[1].entrada,('stringValue','=texto'));self.assertEqual(x[2].resultado,('boolValue',False));self.assertEqual(x[3].resultado,('numberValue',0))
    async def test_formula_sem_resultado_nao_inventa_cache(self):
        c=Cenario();await c.abrir('progressao');c.celulas=[{'values':[{'userEnteredValue':{'formulaValue':'=IF(TRUE,"",1)'}}]}]
        p=await c.pagina();self.assertIsNone(p.celulas[0][0].resultado);self.assertIsNone(p.celulas[-1][-1].entrada)
        self.assertEqual(len(p.celulas),1);self.assertEqual(len(p.celulas[0]),6)
    async def test_dominios_arquivos_indices_arbitrarios_recusados_sem_rede(self):
        c=Cenario()
        for d in ['identidade',"'DADOS'!A1:ZZ9999",{},None,True]:
            with self.subTest(d=d),self.assertRaises(ErroProvedor):await c.leitor.abrir('falso',ARQUIVO,d)
        self.assertFalse(c.requests);await c.abrir();n=len(c.requests)
        for i in [-1,1.5,True,None,'0',len(c.plano.faixas)]:
            with self.subTest(i=i),self.assertRaises(ErroProvedor):await c.pagina(i)
        for arq in ['https://malicioso.tld/','abc',None]:
            with self.assertRaises(ErroProvedor):await c.leitor.abrir('falso',arq,'progressao')
        self.assertEqual(len(c.requests),n)
    async def test_plano_de_outra_instancia_ou_cliente_recusado(self):
        c=Cenario();p=await c.abrir();outro=LeitorGradeRest(c.p,c.revalidar,c.cota)
        for plano in [p,{},p.progresso()]:
            with self.assertRaises(ErroProvedor):await outro.pagina('falso',plano,0)
        self.assertEqual(len(c.requests),3)
    async def test_5001_linhas_grade_insuficiente_aba_ausente(self):
        for mut in [lambda c:c.grades['EXTRATO']['gridProperties'].update(rowCount=5001),lambda c:c.grades['SALÁRIOS']['gridProperties'].update(columnCount=11),lambda c:c.grades.pop('CARTEIRA')]:
            c=Cenario();mut(c)
            with self.assertRaises(ErroProvedor):await c.abrir()
    async def test_metadados_duplicados_ou_invalidos(self):
        for mut in [lambda o:o.update(spreadsheetId='outra'),lambda o:o['sheets'].append(copy.deepcopy(o['sheets'][0])),lambda o:o['sheets'][1]['properties'].update(sheetId=o['sheets'][0]['properties']['sheetId']),lambda o:o['sheets'][0]['properties']['gridProperties'].update(rowCount=True),lambda o:o['sheets'][0]['properties'].pop('title'),lambda o:o['sheets'][0].update(data=[])]:
            c=Cenario()
            def alterar(r,o):
                if r.url.host=='sheets.googleapis.com':mut(o)
                return o
            c.alterar=alterar
            with self.subTest(mut=mut),self.assertRaises(ErroProvedor):await c.abrir()
    async def test_edicao_durante_abertura_ou_pagina_sem_rebaseline(self):
        for fase in ['plano','pagina']:
            c=Cenario()
            if fase=='pagina':await c.abrir()
            def editar(r,o):
                if r.url.host=='sheets.googleapis.com':c.versao='9007199254740994'
                return o
            c.alterar=editar
            with self.assertRaises(ErroProvedor) as e:
                if fase=='plano':await c.abrir()
                else:await c.pagina()
            self.assertEqual(e.exception.codigo,'alterada')
            if fase=='pagina':
                c.alterar=None
                with self.assertRaises(ErroProvedor):await c.pagina()
                self.assertEqual(c.plano.versao,'9007199254740993')
    async def test_grade_renomeada_redimensionada_ou_aba_extra(self):
        for mut in [lambda o:o['sheets'][0]['properties']['gridProperties'].update(rowCount=4999),lambda o:o['sheets'][0]['properties'].update(title='Outra'),lambda o:o['sheets'].append(dict(properties=dict(sheetId=7,title='Extra',gridProperties=dict(rowCount=1,columnCount=1))))]:
            c=Cenario();await c.abrir()
            def alterar(r,o):
                if 'ranges' in r.url.params:mut(o)
                return o
            c.alterar=alterar
            with self.assertRaises(ErroProvedor):await c.pagina()
    async def test_blocos_ausentes_duplicados_deslocados_e_excessivos(self):
        for mut in [lambda s:s.pop('data'),lambda s:s.update(data=[]),lambda s:s['data'].append(copy.deepcopy(s['data'][0])),lambda s:s['data'][0].update(startRow=0),lambda s:s['data'][0].update(startColumn=True),lambda s:s['data'][0].update(rowData=[{},{}]),lambda s:s['data'][0].update(rowData=[{'values':[{}]*7}]),lambda s:s['data'][0].update(rowData=[{'values':'texto'}])]:
            c=Cenario();await c.abrir('progressao')
            def alterar(r,o):
                if 'ranges' in r.url.params:mut(o['sheets'][0])
                return o
            c.alterar=alterar
            with self.subTest(mut=mut),self.assertRaises(ErroProvedor):await c.pagina()
    async def test_tipos_invalidos_erro_sanitizado(self):
        for obj in [{'effectiveValue':{'errorValue':{'type':'ERROR','message':'DADO PRIVADO'}}},{'effectiveValue':{'numberValue':True}},{'effectiveValue':{'formulaValue':'=PRIVADO'}},{'userEnteredValue':{'formulaValue':'sem_igual'}},{'effectiveValue':{'stringValue':'x','boolValue':True}},{'note':[]},{'userEnteredFormat':{'numberFormat':{'type':'DESCONHECIDO'}}},{'userEnteredValue':{'stringValue':'x'*50001}},{'objetoDesconhecido':{}}]:
            c=Cenario();await c.abrir('progressao');c.celulas=[{'values':[obj]}]
            with self.subTest(obj=list(obj)),self.assertRaises(ErroProvedor) as e:await c.pagina()
            self.assertNotIn('PRIVADO',str(e.exception))
    async def test_numeros_nao_finitos_e_enormes_recusados_com_erro_sanitizado(self):
        for valor in [float('inf'), float('nan'), 10**400]:
            c=Cenario();await c.abrir('progressao');get=c.leitor._get
            async def direto(*a,**k):
                o=await get(*a,**k);o['sheets'][0]['data'][0]['rowData']=[{'values':[{'effectiveValue':{'numberValue':valor}}]}];return o
            c.leitor._get=direto
            with self.subTest(tipo=type(valor)),self.assertRaises(ErroProvedor):await c.pagina()
    async def test_fim_vazio_normalizado_sem_truncar(self):
        c=Cenario();await c.abrir();p=await c.pagina()
        self.assertEqual(len(p.celulas),73);self.assertTrue(all(len(l)==4 for l in p.celulas))
        self.assertTrue(all(x.entrada is None and x.resultado is None and x.nota=='' for l in p.celulas for x in l))
    async def test_erro_http_nao_segue_redirect_e_limite_resposta(self):
        for status in [302,401,403,404,429,500]:
            c=Cenario();await c.abrir();c.alterar=lambda r,o:httpx.Response(status,headers={'Location':'https://nao_seguir.tld/'})
            with self.assertRaises(ErroProvedor):await c.pagina()
            self.assertEqual(len(c.requests),4)
        c=Cenario();await c.abrir();c.alterar=lambda r,o:httpx.Response(200,content=b'x'*(4*1024*1024+1)) if 'ranges' in r.url.params else o
        with self.assertRaises(ErroProvedor) as e:await c.pagina()
        self.assertEqual(e.exception.codigo,'tamanho')
    async def test_prazo_inclui_abertura_pagina_e_ultima_espera(self):
        c=Cenario();await c.abrir();c.tempo+=1800;n=len(c.requests)
        with self.assertRaises(ErroProvedor):await c.pagina()
        self.assertEqual(len(c.requests),n)
        c=Cenario();await c.abrir();c.depois=lambda:setattr(c,'tempo',1810.)
        with self.assertRaises(ErroProvedor) as e:await c.pagina()
        self.assertEqual(e.exception.codigo,'expirado')
        for t in [float('nan'),float('inf'),None]:
            c=Cenario();c.tempo=t
            with self.assertRaises(ErroProvedor):await c.abrir()
            self.assertFalse(c.requests)
    async def test_cancelamento_nao_guarda_token_e_repeticao_so_le(self):
        c=Cenario();await c.abrir('progressao')
        async def cancelar(*a,**k):raise asyncio.CancelledError()
        get=c.leitor._get;c.leitor._get=cancelar
        with self.assertRaises(asyncio.CancelledError):await c.pagina()
        c.leitor._get=get
        for _ in range(2):await c.pagina()
        self.assertNotIn('credencial_ficticia',repr(c.leitor.__dict__));self.assertEqual(c.plano.versao,'9007199254740993')

    async def test_cada_get_reserva_cota_inclusive_observacoes_drive(self):
        c=Cenario();await c.abrir('progressao')
        for i in range(len(c.plano.faixas)):await c.pagina(i)
        self.assertEqual(c.cotas,len(c.requests));self.assertEqual(c.cotas,27) # Oitava página lê custos de XP na CONFIGURAÇÃO, não só seus resultados.
    async def test_contexto_alterado_durante_espera_nao_faz_rede(self):
        c=Cenario();await c.abrir();n=len(c.requests)
        async def mudar():c.contexto='d'*64
        c.ao_esperar=mudar
        with self.assertRaises(ErroProvedor) as e:await c.pagina()
        self.assertEqual(e.exception.codigo,'acesso');self.assertEqual(len(c.requests),n)
    async def test_revogacao_apos_resposta_impede_entrega_e_sanitiza_callback(self):
        c=Cenario();await c.abrir('progressao');c.depois=lambda:setattr(c,'contexto','d'*64)
        with self.assertRaises(ErroProvedor):await c.pagina()
        c=Cenario();await c.abrir()
        async def negar():raise AcessoNegado('SEGREDO PRIVADO')
        c.leitor._revalidar=negar
        with self.assertRaises(ErroProvedor) as e:await c.pagina()
        self.assertNotIn('SEGREDO',str(e.exception));self.assertTrue(e.exception.__suppress_context__)
    async def test_espera_de_cota_conta_no_prazo_e_contexto_invalido_recusa(self):
        c=Cenario();await c.abrir();n=len(c.requests)
        async def atrasar():c.tempo+=1800
        c.ao_esperar=atrasar
        with self.assertRaises(ErroProvedor):await c.pagina()
        self.assertEqual(len(c.requests),n)
        for ctx in ['',None,True,'id_pessoal']:
            c=Cenario();c.contexto=ctx
            with self.assertRaises(ErroProvedor):await c.abrir()
            self.assertFalse(c.requests)
    async def test_le_financeiro_inteiro_em_50_paginas_sem_escrita_ou_selo(self):
        c=Cenario();p=await c.abrir();total=0
        self.assertEqual(len(p.faixas),50)
        for i in range(len(p.faixas)):
            pagina=await c.pagina(i)
            total+=sum(len(linha) for linha in pagina.celulas)
        self.assertEqual(total,126168);self.assertEqual(len(c.requests),153)
        self.assertEqual(c.cotas,153)
        self.assertFalse(p.progresso()['criacao_disponivel'])

    async def test_prazo_absoluto_http_e_callback_cancelam_espera_pendente(self):
        from unittest.mock import patch
        async def pendurar(*a,**kw):await asyncio.sleep(60)
        for fase in ['drive','sheets']:
            c=Cenario();await c.abrir()
            if fase=='drive':c.p.versao_arquivo=pendurar
            else:c.p._json=pendurar
            with patch('carteira_viva.grade_inicializacao.TIMEOUT_HTTP',0.005):
                with self.assertRaises(ErroProvedor) as e:await c.pagina()
            self.assertEqual(e.exception.codigo,'temporario')
        c=Cenario();await c.abrir();c.tempo+=1799.995;c.leitor._cota=pendurar
        with self.assertRaises(ErroProvedor) as e:await c.pagina()
        self.assertEqual(e.exception.codigo,'expirado')
