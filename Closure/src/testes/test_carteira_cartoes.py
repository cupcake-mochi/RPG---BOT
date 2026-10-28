"""Apresentação, cache público mínimo e confirmação transacional em banco real."""
from dataclasses import replace
import sqlite3
import unittest
from unittest.mock import patch
from testes.test_carteira_banco import Fixtures, schema_historico
from carteira_viva.segredos import AcessoNegado,Conflito,ErroCarteira
from carteira_viva.permissoes import PUBLICOS
from cryptography.fernet import Fernet


class CartoesTeste(Fixtures,unittest.TestCase):
    def setUp(self):
        super().setUp();self.p=self.criar();self.pid=self.p['id']
    def previa(self,**kw):
        return self.c.preparar_cartao(self.m,self.pid,alteracoes=kw.get('alteracoes',{'titulo':'Título QA'}),campos_publicos=kw.get('campos',PUBLICOS),**{k:v for k,v in kw.items() if k in ('imagem','base_esperada')})
    def test_previa_nao_salva_antes_de_confirmar(self):
        p=self.previa();self.assertEqual(p['cartao']['perfil']['titulo'],'Título QA')
        self.assertNotIn('titulo',self.c.cartao(self.m,self.pid)['perfil'])
        self.c.confirmar_cartao(self.m,self.pid,p['previa'])
        self.assertEqual(self.c.cartao(self.m,self.pid)['perfil']['titulo'],'Título QA')
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
    def test_cancelar_e_expirar_nao_alteram_perfil(self):
        p=self.previa();self.c.cancelar_cartao(self.m,self.pid,p['previa'])
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
        p=self.previa();self.clock[0]+=601
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
        self.assertNotIn('titulo',self.c.cartao(self.m,self.pid)['perfil'])
    def test_outro_usuario_e_outro_servidor_nao_confirmam(self):
        p=self.previa()
        for m in (self.outro,replace(self.m,servidor='outra'),self.admin):
            with self.subTest(m=m),self.assertRaises(AcessoNegado):self.c.confirmar_cartao(m,self.pid,p['previa'])
    def test_conflito_conserva_edicao_nova(self):
        a=self.previa();b=self.previa(alteracoes={'titulo':'Mais novo'})
        self.c.confirmar_cartao(self.m,self.pid,b['previa'])
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,a['previa'])
        self.assertEqual(self.c.cartao(self.m,self.pid)['perfil']['titulo'],'Mais novo')
    def test_formulario_antigo_nao_sobrepoe(self):
        base=self.c.perfil_editavel(self.m,self.pid)['base']
        a=self.previa();self.c.confirmar_cartao(self.m,self.pid,a['previa'])
        with self.assertRaises(Conflito):self.previa(base_esperada=base)
    def test_troca_arquivo_invalida_previa(self):
        p=self.previa();cid=self.c._fonte(self.m.servidor,self.pid)['conexao']
        self.c.trocar_arquivo(self.m,self.pid,arquivo='arquivo-novo',conexao=cid,contrato='analise-12',revisao=1,pedido=self.pedido())
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
    def test_configuracao_mudou_nao_publica_campo_ocultado(self):
        p=self.previa();self.c.configurar(self.admin,campos_publicos={'nome'})
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
        self.assertEqual(set(self.c.cartao(self.m,self.pid)['perfil']),{'nome'})
    def test_limite_de_previas(self):
        for _ in range(5):self.previa()
        with self.assertRaises(ErroCarteira):self.previa()
    def test_campos_mecanicos_links_e_imagem_arbitraria_recusados(self):
        for d in ({'vida_max':999},{'arquivo':'http://interno'},{'nome':'outro'},{'imagem_id':'../../secreto'}):
            with self.subTest(d=d),self.assertRaises(ErroCarteira):self.previa(alteracoes=d)
        with self.assertRaises(ErroCarteira):self.previa(imagem='nao_existe')
    def test_valores_invalidos_recusados(self):
        for d in ({'titulo':'x'*201},{'frase':'x'*501},{'cor':True},{'cor':0x1000000},{'idade':-1},{'cla':object()}):
            with self.subTest(d=str(d)),self.assertRaises(ErroCarteira):self.previa(alteracoes=d)
    def test_rotacao_e_reinicio(self):
        p=self.previa();self.c.rotacionar_chave(Fernet.generate_key())
        # Troca da cifra muda o hash-base: prévia antiga é descartada.
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
    def test_reinicio_apaga_previas_preserva_perfil(self):
        p=self.previa();self.reabrir()
        with self.assertRaises(Conflito):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
        self.assertEqual(self.c.cartao(self.m,self.pid)['perfil']['nome'],'Personagem fictício')
    def test_resumo_somente_campos_publicos_em_fonte_atual(self):
        f={'ficha':{k:{'valor':v,'celula':'','parte':'entrada'} for k,v in {'nome':'Nome novo','origem':'Latente','caminho':'Bastião','vida_max':999,'historia':'segredo','arquivo':'privado'}.items()}}
        ref=self.c.reservar_leitura(self.m,self.pid);self.c.gravar_leitura(self.m,ref,campos=f,schema='carteira-analise-1')
        c=self.c.cartao_galeria(self.m,self.pid)
        self.assertEqual(c['perfil']['nome'],'Nome novo');self.assertNotIn('vida_max',c['perfil']);self.assertNotIn('historia',str(c));self.assertNotIn('arquivo',c)
        self.assertFalse(c['precisa_atualizar']);self.clock[0]+=61
        self.assertTrue(self.c.cartao_galeria(self.m,self.pid)['precisa_atualizar'])
    def test_resumo_mantem_zero_privado_e_data_de_leitura(self):
        ref=self.c.reservar_leitura(self.m,self.pid);self.c.gravar_leitura(self.m,ref,campos={'ficha':{'nome':{'valor':''},'nivel':{'valor':0}}},schema='carteira-analise-1')
        self.assertEqual(self.c.cartao(self.m,self.pid)['perfil']['nome'],'Personagem fictício')
        self.assertNotIn('nivel',self.c.cartao(self.m,self.pid)['perfil'])
    def test_imagem_de_outro_personagem_nao_pode_ser_usada(self):
        outro=self.criar();self.c.registrar_imagem(self.m,outro['id'],'a'*32)
        with self.assertRaises(ErroCarteira):self.previa(imagem='a'*32)
    def test_cota_de_imagem_nao_reinicia_ao_excluir_personagem(self):
        for n in range(10):self.c.registrar_imagem(self.m,self.pid,format(n,'032x'))
        self.c.excluir(self.m,self.pid,pedido=self.pedido())
        novo=self.criar()['id']
        with self.assertRaises(ErroCarteira):self.c.registrar_imagem(self.m,novo,'b'*32)
        self.clock[0]+=86401
        self.c.registrar_imagem(self.m,novo,'b'*32)
    def test_registro_de_imagem_e_cota_sao_atomicos(self):
        with patch.object(self.c,'_auditar',side_effect=RuntimeError('ficticio')):
            with self.assertRaises(RuntimeError):self.c.registrar_imagem(self.m,self.pid,'a'*32)
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM imagens').fetchone()[0],0)
    def test_revisores_nao_editam_e_idioma_nao_delega(self):
        self.c.configurar(self.admin,revisores={'rev'})
        m=replace(self.outro,cargos=frozenset({'rev'}))
        c=self.c.cartao_galeria(m,self.pid)
        self.assertTrue(c['capacidades']['analisar']);self.assertFalse(c['capacidades']['personalizar'])
        with self.assertRaises(AcessoNegado):self.c.configuracao_cartoes(m)
    def test_rollback_do_confirmar(self):
        p=self.previa()
        with patch.object(self.c,'_auditar',side_effect=RuntimeError('ficticio')):
            with self.assertRaises(RuntimeError):self.c.confirmar_cartao(self.m,self.pid,p['previa'])
        self.assertNotIn('titulo',self.c.cartao(self.m,self.pid)['perfil'])
        self.c.confirmar_cartao(self.m,self.pid,p['previa'])
    def test_migracao_v3_preserva_cadastro(self):
        self.c.fechar();db=sqlite3.connect(self.path)
        schema_historico(db,3);db.close()
        from carteira_viva.banco import Cadastro
        self.c=Cadastro(self.path,(self.chave,),agora=self.agora)
        self.assertEqual(self.c.cartao(self.m,self.pid)['id'],self.pid);self.c.verificar_integridade()
