"""Sessão real cifrada: expiração, CSRF, rotação e retornos de uso único."""
import sqlite3
import unittest
from cryptography.fernet import Fernet
from testes.test_carteira_banco import Fixtures
from carteira_viva.sessoes import Sessoes,SessaoEncerrada
from carteira_viva.segredos import AcessoNegado,ErroCarteira

class SessoesTeste(Fixtures,unittest.TestCase):
    def setUp(self):
        super().setUp();self.s=Sessoes(self.c);self.cookie='a'*43;self.novo='b'*43
        self.s.abrir(None,self.cookie);self.csrf=self.s.estado(self.cookie)['csrf']
    def login(self):
        o=self.s.login(self.cookie,self.csrf,'111','c'*32);self.s.consumir(self.cookie,o['estado'])
        self.s.finalizar(self.cookie,o['estado'],self.novo,'222');return o
    def test_cookie_rotaciona_e_identidade_nao_vem_do_cliente(self):
        self.login();self.assertEqual(self.s.identidade(self.novo),'222')
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.cookie)
        self.assertNotEqual(self.s.estado(self.novo)['csrf'],self.csrf)
    def test_anonimo_nao_acessa_dados_e_reabrir_nao_rotaciona(self):
        self.assertFalse(self.s.abrir(self.cookie,'x'*43))
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.cookie)
    def test_csrf_e_cookie_de_outro_navegador_nao_consumem_estado(self):
        o=self.s.login(self.cookie,self.csrf,'111',None)
        with self.assertRaises(AcessoNegado):self.s.login(self.cookie,'errado','111',None)
        self.s.abrir(None,'z'*43)
        with self.assertRaises(SessaoEncerrada):self.s.consumir('z'*43,o['estado'])
        self.s.consumir(self.cookie,o['estado'])
    def test_estado_uso_unico_e_novo_login_invalida_retorno_antigo(self):
        a=self.s.login(self.cookie,self.csrf,'111',None);b=self.s.login(self.cookie,self.csrf,'111',None)
        with self.assertRaises(SessaoEncerrada):self.s.consumir(self.cookie,a['estado'])
        self.s.consumir(self.cookie,b['estado'])
        with self.assertRaises(SessaoEncerrada):self.s.consumir(self.cookie,b['estado'])
    def test_logout_durante_oauth_nao_ressuscita_sessao(self):
        o=self.s.login(self.cookie,self.csrf,'111',None);self.s.consumir(self.cookie,o['estado'])
        self.s.sair(self.cookie,self.csrf)
        with self.assertRaises(SessaoEncerrada):self.s.finalizar(self.cookie,o['estado'],self.novo,'222')
    def test_logout_autenticado_e_csrf_errado(self):
        self.login();csrf=self.s.estado(self.novo)['csrf']
        with self.assertRaises(AcessoNegado):self.s.sair(self.novo,'errado')
        self.assertEqual(self.s.identidade(self.novo),'222');self.s.sair(self.novo,csrf)
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.novo)
    def test_prazo_anonimo_dez_minutos(self):
        self.clock[0]+=600
        with self.assertRaises(SessaoEncerrada):self.s.estado(self.cookie)
    def test_inatividade_trinta_minutos_sem_reviver(self):
        self.login();self.clock[0]+=1800
        with self.assertRaises(SessaoEncerrada):self.s.conferir(self.novo,'222',tocar=True)
    def test_uso_renova_inatividade_mas_nao_maximo_oito_horas(self):
        self.login()
        for _ in range(16):self.clock[0]+=1700;self.s.conferir(self.novo,'222',tocar=True)
        self.clock[0]+=1600
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.novo)
    def test_dados_cifrados_e_sem_token_discord(self):
        o=self.s.login(self.cookie,self.csrf,'111','c'*32);raw=self.path.read_bytes()
        for v in (self.cookie,self.csrf,o['estado'],o['verificador']):self.assertNotIn(v.encode(),raw)
    def test_rotacao_encerra_sessao_preserva_personagem(self):
        p=self.criar();self.login();self.c.rotacionar_chave(Fernet.generate_key())
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.novo)
        self.assertEqual(self.c.cartao(self.m,p['id'])['id'],p['id'])
    def test_reinicio_encerra_sessao(self):
        self.login();self.reabrir();self.s=Sessoes(self.c)
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.novo)
    def test_limpeza(self):
        self.clock[0]+=601;self.s.limpar();self.assertEqual(self.c.db.execute('SELECT count(*) FROM web_sessoes').fetchone()[0],0)
    def test_migracao_v4_preserva_cadastro(self):
        p=self.criar();self.c.fechar();db=sqlite3.connect(self.path)
        db.executescript('DROP TABLE copias_rest; DROP TABLE conferencias_rest; DROP TABLE modelos_servidor; DROP TABLE web_sessoes; PRAGMA user_version=4;');db.close()
        from carteira_viva.banco import Cadastro
        self.c=Cadastro(self.path,(self.chave,),agora=self.agora);self.s=Sessoes(self.c)
        from carteira_viva.esquema import VERSAO
        self.assertEqual(self.c.cartao(self.m,p['id'])['id'],p['id']);self.assertEqual(self.c.db.execute('PRAGMA user_version').fetchone()[0],VERSAO)
    def test_backup_sem_sessoes(self):
        from carteira_viva.backup import gravar_backup,_extrair
        self.login();out=self.path.parent/'sessao.cvb';raw=self.path.parent/'sessao.sqlite3'
        gravar_backup(self.c,out);_extrair(out,raw,self.c.cifra,self.agora(),'cadastro')
        db=sqlite3.connect(raw);self.assertEqual(db.execute('SELECT count(*) FROM web_sessoes').fetchone()[0],0);db.close()

    def test_teto_de_sessoes_sem_crescimento_ilimitado(self):
        with self.c._transacao():
            r=self.c.db.execute('SELECT * FROM web_sessoes').fetchone()
            self.c.db.executemany('INSERT INTO web_sessoes VALUES (?,?,?,?,?,?,?,?)',[(str(n),r['criado'],r['usado'],None,'anonima',None,r['dados'],0) for n in range(511)])
        with self.assertRaises(ErroCarteira):self.s.abrir(None,'z'*43)
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM web_sessoes').fetchone()[0],512)
    def test_limite_de_tentativas_de_login(self):
        for _ in range(10):self.s.login(self.cookie,self.csrf,'111',None)
        with self.assertRaises(ErroCarteira):self.s.login(self.cookie,self.csrf,'111',None)

    def test_apagar_usuario_encerra_suas_sessoes_sem_afetar_outro(self):
        self.login();outro='x'*43;ativo='z'*43
        self.s.abrir(None,outro);o=self.s.login(outro,self.s.estado(outro)['csrf'],'111',None)
        self.s.consumir(outro,o['estado']);self.s.finalizar(outro,o['estado'],ativo,'999')
        self.c.apagar_usuario('222')
        with self.assertRaises(SessaoEncerrada):self.s.identidade(self.novo)
        self.assertEqual(self.s.identidade(ativo),'999')
