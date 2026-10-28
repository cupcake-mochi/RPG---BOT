"""Conferência parcial determinística, só de leitura, com recibo cifrado histórico.

Não interpreta prosa nem concede autorizações. Não é diário de limpeza/escrita.
"""
import asyncio
import hashlib
import re

from .contrato_inicializacao import carregar, CONTRATO_SHA256
from .grade_inicializacao import PlanoGrade, PaginaGrade, CelulaGrade, _retangulo, LIVROS, ARQUIVO
from .segredos import ErroCarteira, json_bytes

PROTOCOLO_RECIBO = 'carteira-recibo-leitura-rest-1'
LIMITES = ('propriedades_apps_script', 'preservacao_global', 'imagens_automacoes_responsavel',
           'autorizacoes_e_requisitos_livres', 'consistencia_dos_calculos_externos')
FLAGS = dict(criacao_disponivel=False, conferencia_conjunta_concluida=False,
             consistencia_temporal_verificada=False, imagens_atuais_conferidas=False)
VAZIOS = (None, ('stringValue', ''))


def _erro():
    raise ErroCarteira('Leitura de inicialização incompleta ou incompatível.') from None


def _hash(obj):
    return hashlib.sha256(json_bytes(obj)).hexdigest()


def _literal(valor):
    tipo = 'boolValue' if type(valor) is bool else 'numberValue' if type(valor) in (int, float) else 'stringValue'
    return tipo, valor


class ConferenciaGrade:
    """Recebe páginas privadas do leitor, em ordem. Não recebe dados HTTP do jogador."""
    def __init__(self, plano):
        if type(plano) is not PlanoGrade or plano.dominio not in ('financeiro', 'progressao'): _erro()
        self._plano, self._contrato = plano, carregar()
        self._proxima, self._total, self._erros, self._pendencias = 0, 0, 0, 0
        self._achados, self._celulas, self._fechado = [], {}, False
        self._cadeia = _hash([CONTRATO_SHA256, plano.dominio, plano.contexto, plano.versao])
        self._ops = []
        if plano.dominio == 'financeiro':
            for op in self._contrato['financeiro']['operacoes']:
                if op['tipo'] == 'propriedade': continue
                pos = list(_retangulo(op['faixa'] if ':' in op['faixa'] else op['faixa'] + ':' + op['faixa']))
                if (op['aba'], pos[3]) in LIVROS:
                    candidatos = [f for f in plano.faixas if f.aba == op['aba']]
                    if not candidatos: _erro()
                    pos[2] = candidatos[0].grade[1]
                self._ops.append((op, tuple(pos)))
            for g in self._contrato['financeiro']['guardas']:
                r,c,_,_ = _retangulo(g['faixa'] if ':' in g['faixa'] else g['faixa'] + ':' + g['faixa'])
                for i,linha in enumerate(g['formulas']):
                    for j,fs in enumerate(linha):
                        self._ops.append((dict(tipo='guarda',aba=g['aba'],formulas=fs),(r+i,c+j,r+i+1,c+j+1)))
        necessarias=[(op['aba'],p) for op,p in self._ops]
        if plano.dominio=='progressao':
            p=self._contrato['progressao']
            necessarias=[('CONFIGURAÇÃO',(45,4,46,7)),('DADOS',(4,42,33,44)),
                         ('DADOS',(53,103,54,104)),('DADOS',(46,103,47,104)),
                         ('FICHA',(10,33,11,34)),('FICHA',(10,39,11,40))]
            for rot in p['rotulos']:
                a=rot['celula'];necessarias.append((rot['aba'],_retangulo(a+':'+a)))
            for item in p['custos']:
                r=item['linha'];necessarias.extend([('CONFIGURAÇÃO',(r-1,2,r,3)),('CONFIGURAÇÃO',(r-1,4,r,7))])
            for item in p['missoes']:
                c=item['coluna'];necessarias.append(('FICHA PESSOAL',(p['missoes_linhas'][0]-1,c-5,p['missoes_linhas'][1],c)))
        # União geométrica de retângulos: não alocar um set das 126 mil posições.
        for aba,p in necessarias:
            faixas=[f.pos for f in plano.faixas if f.aba==aba]
            cortes=sorted({p[0],p[2]}|{v for f in faixas for v in (f[0],f[2]) if p[0]<v<p[2]})
            for inicio,fim in zip(cortes,cortes[1:]):
                coberto=p[1]
                for f in sorted(faixas,key=lambda x:x[1]):
                    if f[0]<=inicio and f[2]>=fim and f[1]<=coberto:coberto=max(coberto,f[3])
                if coberto<p[3]:_erro()

    def __repr__(self):
        return '<ConferenciaGrade privada>'

    def _add(self, codigo, aba, r, c, pendente=False):
        self._total += 1
        if pendente: self._pendencias += 1
        else: self._erros += 1
        if len(self._achados) < 16:
            self._achados.append(dict(codigo=codigo, aba=aba, linha=r, coluna=c,
                                     tipo='pendencia' if pendente else 'erro'))

    def _formula(self, x, fs, aba, r, c):
        if not x.entrada or x.entrada[0] != 'formulaValue' or x.entrada[1] not in fs:
            self._add('formula_divergente',aba,r,c)

    def _valor(self, x, esperado, aba, r, c):
        if x.entrada != _literal(esperado): self._add('entrada_divergente',aba,r,c)
        self._resultado(x,esperado,aba,r,c)

    def _resultado(self, x, esperado, aba, r, c):
        if x.resultado is None:
            self._add('resultado_ausente',aba,r,c,True)
        elif x.resultado != _literal(esperado): self._add('resultado_divergente',aba,r,c)

    def receber(self, indice, pagina):
        if (self._fechado or type(indice) is not int or indice != self._proxima or
                indice >= len(self._plano.faixas) or type(pagina) is not PaginaGrade or
                pagina.faixa is not self._plano.faixas[indice]): _erro()
        f=pagina.faixa;r,c,r2,c2=f.pos
        if type(pagina.celulas) is not tuple or len(pagina.celulas)!=r2-r: _erro()
        dados=[]
        for i,linha in enumerate(pagina.celulas):
            if type(linha) is not tuple or len(linha)!=c2-c: _erro()
            valores=[]
            for j,x in enumerate(linha):
                if type(x) is not CelulaGrade: _erro()
                valores.append((x.entrada,x.resultado,x.nota,x.formato_numero))
            dados.append(valores)
        # Validar estrutura inteira antes de incorporar qualquer resultado.
        h=_hash(dados)
        for i,linha in enumerate(pagina.celulas):
            for j,x in enumerate(linha):
                row,col=r+i,c+j
                if self._plano.dominio=='progressao':
                    self._celulas[f.aba,row+1,col+1]=x
                else:
                    for op,p in self._ops:
                        if op['aba']!=f.aba or not p[0]<=row<p[2] or not p[1]<=col<p[3]:continue
                        t=op['tipo']
                        if t=='limpar' and (x.entrada not in VAZIOS or x.resultado not in VAZIOS):self._add('conteudo_residual',f.aba,row+1,col+1)
                        elif t=='notas' and x.nota:self._add('nota_residual',f.aba,row+1,col+1)
                        elif t=='valor':self._valor(x,op['valor'],f.aba,row+1,col+1)
                        elif t=='guarda':self._formula(x,op['formulas'],f.aba,row+1,col+1)
        self._cadeia=_hash([self._cadeia,indice,h]);self._proxima+=1

    def _get(self, aba, r, c):
        try:return self._celulas[aba,r,c]
        except KeyError:_erro()

    def _numero(self, x, aba, r, c, opcional=False):
        if opcional and x.entrada in VAZIOS and x.resultado in VAZIOS:return None
        e=x.entrada
        if not e or e[0]!='numberValue' or type(e[1]) not in (int,float) or not 0<=e[1]<=9007199254740991 or int(e[1])!=e[1]:
            self._add('inteiro_literal_necessario',aba,r,c,True);return None
        self._resultado(x,e[1],aba,r,c)
        return int(e[1])

    def _progressao(self):
        p=self._contrato['progressao'];F='FICHA';C='CONFIGURAÇÃO';D='DADOS';M='FICHA PESSOAL'
        for rot in p['rotulos']:
            a=rot['celula'];r,c,_,_=_retangulo(a+':'+a);self._valor(self._get(rot['aba'],r+1,c+1),rot['valor'],rot['aba'],r+1,c+1)
        base=self._get(C,46,5);override=self._get(C,46,6)
        # O domínio GS não aceita fórmula em nenhuma das duas entradas de nível.
        for col,x in [(5,base),(6,override)]:
            if x.entrada and x.entrada[0]=='formulaValue':self._add('formula_em_entrada_nivel',C,46,col)
        escolhido=base if override.entrada in VAZIOS and override.resultado in VAZIOS else override
        nivel=self._numero(escolhido,C,46,5 if escolhido is base else 6)
        self._formula(self._get(C,46,7),p['regra'],C,46,7)
        custos={}
        for item in p['custos']:
            r=item['linha'];n=item['nivel'];self._valor(self._get(C,r,3),n,C,r,3)
            e,f,g=[self._get(C,r,col) for col in (5,6,7)]
            self._formula(g,item['formulas'],C,r,7)
            escolhido=e if f.entrada in VAZIOS and f.resultado in VAZIOS else f
            custos[n]=self._numero(escolhido,C,r,5 if escolhido is e else 6,opcional=True)
            if custos[n] is not None:self._resultado(g,custos[n],C,r,7)
        if nivel is None or not p['piso']['minimo']<=nivel<=p['piso']['maximo']:
            self._add('nivel_inicial_invalido',C,46,7);return
        self._resultado(self._get(C,46,7),nivel,C,46,7)
        self._valor(self._get(F,11,34),nivel,F,11,34)
        self._valor(self._get(D,54,104),p['piso']['base'],D,54,104)
        # Acumulado relativo ao piso. Custos vêm de entradas E/F, não de AR/Z.
        anterior=p['piso']['base'] if nivel==1 else p['piso']['prefixo']
        for item in p['curva']:
            n,r=item['nivel'],item['linha'];self._valor(self._get(D,r,43),n,D,r,43)
            self._formula(self._get(D,r,44),[item['formula']],D,r,44)
            if n<nivel:esperado=p['piso']['prefixo']
            elif n==nivel:esperado=p['piso']['base']
            elif anterior is None or custos[n-1] is None:
                esperado=None;self._add('custo_xp_insuficiente',C,64+n-1,7,True)
            else:esperado=anterior+custos[n-1]
            if esperado is not None:self._resultado(self._get(D,r,44),esperado,D,r,44)
            anterior=esperado
        for r in range(p['missoes_linhas'][0],p['missoes_linhas'][1]+1):
            for g,item in enumerate(p['missoes']):
                col=item['coluna'];x=self._get(M,r,col)
                self._formula(x,[f.replace('{linha}',str(r)) for f in item['formulas']],M,r,col)
                if x.resultado not in VAZIOS and x.resultado!=('numberValue',0):self._add('xp_missao_residual',M,r,col)
                for c in range(col-4,col):
                    y=self._get(M,r,c)
                    if y.entrada not in VAZIOS or y.resultado not in VAZIOS:self._add('missao_residual',M,r,c)
                    if y.nota:self._add('nota_missao_residual',M,r,c)
        self._formula(self._get(D,47,104),[p['xp']],D,47,104)
        self._formula(self._get(F,11,40),['=DADOS!$CZ$47'],F,11,40)
        # Máximos não são inferidos destes resultados. Missões/base vazias exigem XP 0.
        self._resultado(self._get(D,47,104),0,D,47,104)
        self._resultado(self._get(F,11,40),0,F,11,40)

    def concluir(self):
        if self._proxima!=len(self._plano.faixas):_erro()
        if not self._fechado:
            if self._plano.dominio=='progressao':self._progressao()
            self._celulas.clear();self._fechado=True
        return self.publico()

    def publico(self):
        return dict(dominio=self._plano.dominio,paginas_lidas=self._proxima,
            conferencia_parcial_concluida=self._fechado,erros=self._erros,pendencias=self._pendencias,
            achados=[dict(x) for x in self._achados],mais_achados=self._total-len(self._achados),
            leitura_historica=True,limites=list(LIMITES),**FLAGS)

    def recibo(self,cifra):
        if not self._fechado:_erro()
        p=self._plano
        obj=dict(protocolo=PROTOCOLO_RECIBO,contrato=CONTRATO_SHA256,arquivo=p.arquivo,
                 contexto=p.contexto,dominio=p.dominio,versao_drive=p.versao,paginas=self._proxima,
                 estado=self._cadeia,resultado=_hash(self.publico()),erros=self._erros,pendencias=self._pendencias,
                 leitura_historica=True,**FLAGS)
        return cifra.cifrar(['recibo_rest',p.contexto,p.arquivo,p.dominio],obj)


def abrir_recibo(cifra,envelope,*,contexto,arquivo,dominio,versao_drive):
    """Só para backend com contexto esperado confiável. Não autoriza escrita/retomada."""
    if (not isinstance(contexto,str) or not re.fullmatch('[a-f0-9]{64}',contexto) or
            not isinstance(arquivo,str) or not ARQUIVO.fullmatch(arquivo) or
            dominio not in ('financeiro','progressao') or not isinstance(versao_drive,str) or
            not re.fullmatch('[0-9]{1,30}',versao_drive) or not isinstance(envelope,bytes) or len(envelope)>16384):_erro()
    obj=cifra.abrir(['recibo_rest',contexto,arquivo,dominio],envelope)
    chaves={'protocolo','contrato','arquivo','contexto','dominio','versao_drive','paginas','estado','resultado','erros','pendencias','leitura_historica'}|FLAGS.keys()
    if (type(obj) is not dict or set(obj)!=chaves or obj['protocolo']!=PROTOCOLO_RECIBO or
            obj['contrato']!=CONTRATO_SHA256 or obj['arquivo']!=arquivo or obj['contexto']!=contexto or
            obj['dominio']!=dominio or obj['versao_drive']!=versao_drive or obj['leitura_historica'] is not True or
            type(obj['paginas']) is not int or not 1<=obj['paginas']<=100 or
            any(obj[k] is not False for k in FLAGS) or
            any(type(obj[k]) is not int or not 0<=obj[k]<=1000000 for k in ('erros','pendencias')) or
            any(not isinstance(obj[k],str) or not re.fullmatch('[a-f0-9]{64}',obj[k]) for k in ('estado','resultado'))):_erro()
    return obj


async def coletar_conferir(leitor,acesso,arquivo,dominio):
    """Integra transporte real e validação determinística; ainda sem rota/diário de escrita."""
    plano=await leitor.abrir(acesso,arquivo,dominio);conferencia=ConferenciaGrade(plano)
    for i in range(len(plano.faixas)):
        pagina=await leitor.pagina(acesso,plano,i)
        await asyncio.to_thread(conferencia.receber,i,pagina)
    await leitor.confirmar(acesso,plano)
    await asyncio.to_thread(conferencia.concluir)
    return conferencia
