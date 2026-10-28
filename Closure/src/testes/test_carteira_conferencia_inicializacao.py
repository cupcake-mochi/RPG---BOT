"""Contrato real exportado, coleta HTTP simulada e decisões independentes de caches."""
import copy
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import httpx
from cryptography.fernet import Fernet
from carteira_viva.contrato_inicializacao import carregar,CONTRATO_SHA256,CAMINHO
from carteira_viva.conferencia_inicializacao import ConferenciaGrade,coletar_conferir,abrir_recibo,FLAGS
from carteira_viva.grade_inicializacao import LeitorGradeRest,PaginaGrade,_retangulo
from carteira_viva.segredos import Cifra,ErroCarteira
from carteira_viva.provedores import ErroProvedor
from testes.test_carteira_grade_inicializacao import Cenario,ARQUIVO

class Dados(Cenario):
    def __init__(self,dominio='progressao',nivel=10):
        super().__init__();self.dominio=dominio;self.mapa={};self.c=carregar();self.grades['CONFIGURAÇÃO']['gridProperties']['rowCount']=400
        def put(a,r,col,entrada,resultado=None,nota=''):
            d={'note':nota}
            if entrada is not None:d['userEnteredValue']=dict([entrada])
            if resultado is not None:d['effectiveValue']=dict([resultado])
            self.mapa[a,r,col]=d
        self.put=put
        def literal(a,r,c,v):put(a,r,c,('boolValue' if type(v) is bool else 'numberValue' if type(v) in (int,float) else 'stringValue',v),('boolValue' if type(v) is bool else 'numberValue' if type(v) in (int,float) else 'stringValue',v))
        self.literal=literal
        def formula(a,r,c,f,v):put(a,r,c,('formulaValue',f),('numberValue' if type(v) in (int,float) else 'stringValue',v))
        self.formula=formula
        if dominio=='financeiro':
            for op in self.c['financeiro']['operacoes']:
                if op['tipo']=='valor':
                    r,col,_,_=_retangulo(op['faixa']+':'+op['faixa']);literal(op['aba'],r+1,col+1,op['valor'])
            for g in self.c['financeiro']['guardas']:
                a=g['faixa'];r,col,_,_=_retangulo(a if ':' in a else a+':'+a)
                for i,row in enumerate(g['formulas']):
                    for j,fs in enumerate(row):formula(g['aba'],r+i+1,col+j+1,fs[0],0)
        else:
            p=self.c['progressao'];C='CONFIGURAÇÃO';D='DADOS';F='FICHA';M='FICHA PESSOAL'
            for rot in p['rotulos']:
                r,col,_,_=_retangulo(rot['celula']+':'+rot['celula']);literal(rot['aba'],r+1,col+1,rot['valor'])
            literal(C,46,5,2);literal(C,46,6,nivel);formula(C,46,7,p['regra'][0],nivel)
            for custo in p['custos']:
                r=custo['linha'];v=custo['livro'];literal(C,r,3,custo['nivel']);literal(C,r,5,v);formula(C,r,7,custo['formulas'][0],v)
            self.curva(nivel)
            literal(F,11,34,nivel);literal(D,54,104,0);formula(D,47,104,p['xp'],0);formula(F,11,40,'=DADOS!$CZ$47',0)
            for r in range(15,88):
                for g in p['missoes']:formula(M,r,g['coluna'],g['formulas'][0].replace('{linha}',str(r)),'')
        self.final_hook=None
    def curva(self,nivel,custo_custom=None):
        anterior=0 if nivel==1 else '—'
        for item in self.c['progressao']['curva']:
            n=item['nivel'];self.literal('DADOS',item['linha'],43,n)
            if n<nivel:v='—'
            elif n==nivel:v=0
            else:
                custo=self.c['progressao']['custos'][n-2]['livro']
                if custo_custom and n-1 in custo_custom:custo=custo_custom[n-1]
                v='Pendente' if anterior=='Pendente' or custo=='' else anterior+custo
            self.formula('DADOS',item['linha'],44,item['formula'],v);anterior=v
    def http(self,req):
        if 'ranges' in req.url.params:
            nome,a1=req.url.params['ranges'].split('!');nome=nome.strip("'");r,c,r2,c2=_retangulo(a1)
            self.celulas=[{'values':[copy.deepcopy(self.mapa.get((nome,i+1,j+1),{})) for j in range(c,c2)]} for i in range(r,r2)]
        if self.final_hook and req.url.host=='www.googleapis.com':self.final_hook()
        return super().http(req)
    async def conferir(self):return await coletar_conferir(self.leitor,'credencial_ficticia',ARQUIVO,self.dominio)

class ConferenciaInicializacaoTeste(unittest.IsolatedAsyncioTestCase):
    async def test_progresso_real_do_produtor_e_conta_final_independente(self):
        c=Dados();a=await c.conferir();r=a.publico()
        self.assertEqual((r['erros'],r['pendencias'],r['paginas_lidas']),(0,0,8))
        self.assertTrue(r['conferencia_parcial_concluida']);self.assertTrue(r['leitura_historica'])
        self.assertEqual(len(c.requests),28);self.assertEqual(c.cotas,28)
        for k in FLAGS:self.assertFalse(r[k])
        self.assertFalse(a._celulas)
    async def test_financeiro_5000_linhas_em_fluxo_sem_reter_grade(self):
        c=Dados('financeiro');a=await c.conferir();r=a.publico()
        self.assertEqual((r['erros'],r['pendencias'],r['paginas_lidas']),(0,0,50));self.assertEqual(len(c.requests),154)
        self.assertFalse(a._celulas);self.assertLess(len(repr(a)),100)
    async def test_ultimo_registro_nota_e_formula_vazia_continuam_residuos(self):
        c=Dados('financeiro');c.literal('EXTRATO',5000,3,'DADO PRIVADO')
        c.mapa['SALÁRIOS',5000,12]={'note':'NOTA PRIVADA'};c.formula('FICHA PESSOAL',15,49,'=""','')
        r=(await c.conferir()).publico();self.assertGreaterEqual(r['erros'],3)
        self.assertNotIn('PRIVADO',str(r));self.assertNotIn('PRIVADA',str(r));self.assertIn('nota_residual',str(r))
    async def test_emissao_nao_aceita_numero_no_lugar_de_bool_e_estado_json_exato(self):
        c=Dados('financeiro');c.literal('CARTEIRA',3,46,0);c.literal('DADOS_SALARIOS',2,12,'{}')
        r=(await c.conferir()).publico();self.assertGreater(r['erros'],0)
    async def test_formula_financeira_errada_nao_passa_com_cache_zero(self):
        c=Dados('financeiro');c.formula('FICHA',11,40,'=0',0)
        r=(await c.conferir()).publico();self.assertIn('formula_divergente',str(r))
    async def test_variantes_exatas_ptbr_do_contrato_sao_aceitas(self):
        for dominio in ['financeiro','progressao']:
            c=Dados(dominio)
            for x in c.mapa.values():
                e=x.get('userEnteredValue',{})
                if 'formulaValue' in e:
                    # Fórmulas da fixture não têm vírgula literal dentro de string.
                    e['formulaValue']=e['formulaValue'].replace(',',';')
            r=(await c.conferir()).publico();self.assertEqual(r['erros'],0,dominio)
    async def test_base_antiga_3700_recusada_mesmo_nivel_10(self):
        c=Dados();c.literal('DADOS',54,104,3700)
        r=(await c.conferir()).publico();self.assertGreater(r['erros'],0);self.assertNotIn('3700',str(r))
    async def test_custo_custom_fonte_muda_curva_esperada_sem_inferir_do_cache(self):
        c=Dados();c.literal('CONFIGURAÇÃO',74,6,2100);c.formula('CONFIGURAÇÃO',74,7,c.c['progressao']['custos'][9]['formulas'][0],2100)
        r=(await c.conferir()).publico();self.assertIn('resultado_divergente',str(r))
        c.curva(10,{10:2100});r=(await c.conferir()).publico();self.assertEqual((r['erros'],r['pendencias']),(0,0))
    async def test_custo_ausente_nao_e_deduzido_de_curva_cache_correto(self):
        c=Dados();c.literal('CONFIGURAÇÃO',74,5,'');c.formula('CONFIGURAÇÃO',74,7,c.c['progressao']['custos'][9]['formulas'][0],'')
        r=(await c.conferir()).publico();self.assertGreater(r['pendencias'],0);self.assertIn('custo_xp_insuficiente',str(r))
    async def test_prefixo_abaixo_do_piso_e_formula_adulterada_recusados(self):
        c=Dados();c.formula('DADOS',5,44,'=DADOS_CONFIG!$Z$3',0);c.formula('DADOS',6,44,'="—"','—')
        r=(await c.conferir()).publico();self.assertGreaterEqual(r['erros'],2)
    async def test_nivel_30_e_nivel_1_com_custo_explicito(self):
        c=Dados(nivel=30);r=(await c.conferir()).publico();self.assertEqual((r['erros'],r['pendencias']),(0,0))
        c=Dados(nivel=1);r=(await c.conferir()).publico();self.assertGreater(r['pendencias'],0)
        c.literal('CONFIGURAÇÃO',65,6,0);c.formula('CONFIGURAÇÃO',65,7,c.c['progressao']['custos'][0]['formulas'][0],0)
        c.curva(1,{1:0});r=(await c.conferir()).publico();self.assertEqual((r['erros'],r['pendencias']),(0,0))
    async def test_resultado_ausente_e_nota_de_missao_nao_viram_aprovacao(self):
        c=Dados();c.mapa['FICHA',11,40].pop('effectiveValue');c.mapa['FICHA PESSOAL',15,49]={'note':'salário privado'}
        r=(await c.conferir()).publico();self.assertGreater(r['pendencias'],0);self.assertGreater(r['erros'],0);self.assertNotIn('salário privado',str(r))
    async def test_formula_em_entrada_de_custo_ou_nivel_nao_usa_resultado(self):
        for aba,r,col in [('CONFIGURAÇÃO',46,6),('CONFIGURAÇÃO',74,5)]:
            c=Dados();c.formula(aba,r,col,'=10',10);out=(await c.conferir()).publico();self.assertGreater(out['erros']+out['pendencias'],0)
    async def test_limita_achados_sem_parar_conferencia_das_ultimas_paginas(self):
        c=Dados('financeiro')
        for i in range(100,130):c.literal('EXTRATO',i,1,'privado')
        c.literal('SALÁRIOS',5000,12,'privado')
        r=(await c.conferir()).publico();self.assertEqual(len(r['achados']),16);self.assertEqual(r['erros'],31);self.assertEqual(r['mais_achados'],15)
    async def test_paginas_faltantes_duplicadas_fora_de_ordem_e_de_outro_plano(self):
        c=Dados();p=await c.leitor.abrir('falso',ARQUIVO,'progressao');a=ConferenciaGrade(p)
        with self.assertRaises(ErroCarteira):a.concluir()
        pg=await c.leitor.pagina('falso',p,0)
        with self.assertRaises(ErroCarteira):a.receber(1,pg)
        with self.assertRaises(ErroCarteira):a.receber(0,PaginaGrade(pg.faixa,tuple()))
        self.assertEqual(a.publico()['paginas_lidas'],0);a.receber(0,pg)
        with self.assertRaises(ErroCarteira):a.receber(0,pg)
        outro=await c.leitor.abrir('falso',ARQUIVO,'progressao');b=ConferenciaGrade(outro)
        with self.assertRaises(ErroCarteira):b.receber(0,pg)
    async def test_ultima_observacao_drive_e_contexto_impedem_entrega(self):
        c=Dados();n=0
        def alterar():
            nonlocal n
            n+=1
            if n==19:c.versao='9007199254740994' # Última observação extra (2+2*8+1).
        c.final_hook=alterar
        with self.assertRaises(ErroProvedor):await c.conferir()
    async def test_recibo_cifrado_historico_sem_valores_e_vinculado_a_contexto(self):
        c=Dados();a=await c.conferir();cifra=Cifra((Fernet.generate_key(),));recibo=a.recibo(cifra)
        for s in [ARQUIVO,'9007199254740993','CONFIGURAÇÃO','=DADOS']:self.assertNotIn(s.encode(),recibo)
        args=dict(contexto=c.contexto,arquivo=ARQUIVO,dominio=c.dominio,versao_drive=c.versao)
        d=abrir_recibo(cifra,recibo,**args)
        self.assertTrue(d['leitura_historica']);self.assertTrue(all(d[k] is False for k in FLAGS));self.assertEqual(d['paginas'],8)
        for chave,valor in [('contexto','d'*64),('arquivo','outra_ficha_ficticia_001'),('dominio','financeiro'),('versao_drive','123')]:
            with self.assertRaises(ErroCarteira):abrir_recibo(cifra,recibo,**{**args,chave:valor})
        with self.assertRaises(ErroCarteira):abrir_recibo(cifra,recibo[:-4]+b'xxxx',**args)
    async def test_recibo_nao_pode_habilitar_escrita_e_snapshot(self):
        c=Dados();a=await c.conferir();cifra=Cifra((Fernet.generate_key(),));args=dict(contexto=c.contexto,arquivo=ARQUIVO,dominio=c.dominio,versao_drive=c.versao)
        d=abrir_recibo(cifra,a.recibo(cifra),**args)
        for chave in FLAGS:
            falso={**d,chave:True};envelope=cifra.cifrar(['recibo_rest',c.contexto,ARQUIVO,c.dominio],falso)
            with self.assertRaises(ErroCarteira):abrir_recibo(cifra,envelope,**args)
    async def test_recibo_incompleto_e_relatorio_mutavel_nao_corrompem_estado(self):
        c=Dados();p=await c.abrir();a=ConferenciaGrade(p)
        with self.assertRaises(ErroCarteira):a.recibo(Cifra((Fernet.generate_key(),)))
        c=Dados();c.literal('DADOS',54,104,3700);a=await c.conferir();r=a.publico();r['achados'][0]['codigo']='alterado';self.assertNotIn('alterado',str(a.publico()))
    async def test_contrato_pin_nao_aceita_regeneracao_ou_json_de_cliente(self):
        self.assertEqual(hashlib.sha256(CAMINHO.read_bytes()).hexdigest(),CONTRATO_SHA256)
        with TemporaryDirectory() as pasta:
            p=Path(pasta)/'contrato.json';p.write_bytes(CAMINHO.read_bytes()+b' ')
            with patch('carteira_viva.contrato_inicializacao.CAMINHO',p),self.assertRaises(ErroCarteira):carregar()

    async def test_plano_truncado_nao_parece_cobertura_completa(self):
        from dataclasses import replace
        for dominio in ['financeiro','progressao']:
            c=Dados(dominio);p=await c.leitor.abrir('falso',ARQUIVO,dominio)
            with self.assertRaises(ErroCarteira):ConferenciaGrade(replace(p,faixas=p.faixas[:-1]))
    async def test_recibo_recusa_dominio_livre_e_envelope_excessivo(self):
        c=Dados();a=await c.conferir();cifra=Cifra((Fernet.generate_key(),));args=dict(contexto=c.contexto,arquivo=ARQUIVO,dominio=c.dominio,versao_drive=c.versao)
        for k,v in [('dominio','outro'),('contexto','x'),('versao_drive',''),('arquivo','https://arbitrario.tld/')]:
            with self.assertRaises(ErroCarteira):abrir_recibo(cifra,a.recibo(cifra),**{**args,k:v})
        with self.assertRaises(ErroCarteira):abrir_recibo(cifra,b'x'*16385,**args)

    async def test_recibo_reabre_com_chaves_rotacionadas_sem_retornar_estado_bruto(self):
        c=Dados();c.literal('DADOS',54,104,3700);a=await c.conferir()
        antiga,nova=Fernet.generate_key(),Fernet.generate_key();cifra=Cifra((antiga,));recibo=a.recibo(cifra)
        args=dict(contexto=c.contexto,arquivo=ARQUIVO,dominio=c.dominio,versao_drive=c.versao)
        reaberto=Cifra((nova,antiga));d=abrir_recibo(reaberto,recibo,**args)
        self.assertGreater(d['erros'],0);self.assertNotIn('3700',str(d));self.assertNotIn('achados',d)
        rotacionado=reaberto.fernet.rotate(recibo);d=abrir_recibo(Cifra((nova,)),rotacionado,**args)
        self.assertFalse(d['criacao_disponivel'])
