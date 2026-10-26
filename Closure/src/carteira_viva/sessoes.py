"""Sessões da Carteira: identidade Discord, sem tokens OAuth persistidos."""
import hmac
import secrets

from .banco import digest
from .segredos import AcessoNegado, Conflito, ErroCarteira


class SessaoEncerrada(AcessoNegado):
    codigo = 'sessao'


def nome_cookie(segura):
    return '__Host-cv_carteira' if segura else 'cv_carteira'


class Sessoes:
    # Somente o worker único de DadosAsync usa este objeto/SQLite.
    def __init__(self, cadastro):
        self.c = cadastro

    def limpar(self):
        self.c.db.execute('''DELETE FROM web_sessoes WHERE
            criado<=? OR (fase='ativa' AND usado<=?) OR
            (fase!='ativa' AND criado<=?)''',
            (self.c.agora()-28800, self.c.agora()-1800, self.c.agora()-600))

    def _row(self, cookie):
        if not isinstance(cookie, str) or not 30<=len(cookie)<=100:
            raise SessaoEncerrada('Abra a Carteira novamente.')
        r = self.c.db.execute('SELECT * FROM web_sessoes WHERE id=?', (digest(cookie),)).fetchone()
        if not r or self.c.agora() >= min(r['criado']+(28800 if r['fase']=='ativa' else 600), r['usado']+1800):
            raise SessaoEncerrada('A sessão terminou.')
        return r

    def _dados(self, r):
        return self.c.cifra.abrir(['sessao', r['id']], r['dados'])

    def _csrf(self, r, csrf):
        if not isinstance(csrf,str) or not hmac.compare_digest(csrf,self._dados(r)['csrf']):
            raise AcessoNegado('Confirmação da sessão inválida.')

    def _gravar(self, cookie, *, usuario=None):
        self.limpar()
        if self.c.db.execute('SELECT count(*) FROM web_sessoes').fetchone()[0]>=512:
            raise ErroCarteira('Há sessões demais abertas.')
        dados={'csrf':secrets.token_urlsafe(32)}
        self.c.db.execute('INSERT INTO web_sessoes VALUES (?,?,?,?,?,?,?,?)',
            (digest(cookie),self.c.agora(),self.c.agora(),usuario,'ativa' if usuario else 'anonima',None,
             self.c.cifra.cifrar(['sessao',digest(cookie)],dados),0))
        return self.estado(cookie)

    def abrir(self, anterior, novo):
        try:
            self._row(anterior)
            return False
        except SessaoEncerrada:
            with self.c._transacao():
                if isinstance(anterior,str):self.c.db.execute('DELETE FROM web_sessoes WHERE id=?',(digest(anterior),))
                self._gravar(novo)
            return True

    def estado(self, cookie):
        r=self._row(cookie)
        return {'autenticado':r['fase']=='ativa','csrf':self._dados(r)['csrf'],
                'usuario':r['usuario'] if r['fase']=='ativa' else None,
                'expira_em':max(0,int(min(r['criado']+(28800 if r['fase']=='ativa' else 600),r['usado']+1800)-self.c.agora()))}

    def identidade(self,cookie,csrf=None):
        r=self._row(cookie)
        if csrf is not None:self._csrf(r,csrf)
        if r['fase']!='ativa':raise SessaoEncerrada('Entre com o Discord.')
        return r['usuario']

    def conferir(self,cookie,usuario,*,tocar=False):
        if self.identidade(cookie)!=usuario:raise SessaoEncerrada('A identidade mudou.')
        if tocar:self.c.db.execute('UPDATE web_sessoes SET usado=? WHERE id=?',(self.c.agora(),digest(cookie)))
        return self.estado(cookie)

    def login(self,cookie,csrf,servidor,personagem,*,idioma=None):
        with self.c._transacao():
            r=self._row(cookie);self._csrf(r,csrf)
            if r['fase']=='ativa':raise Conflito('Encerre a sessão para trocar de conta.')
            if r['tentativas']>=10:raise ErroCarteira('Reabra a Carteira para entrar.')
            estado,verificador=secrets.token_urlsafe(32),secrets.token_urlsafe(48)
            dados=self._dados(r)|{'verificador':verificador,'servidor':servidor,'personagem':personagem,'idioma':idioma}
            self.c.db.execute("UPDATE web_sessoes SET fase='oauth',estado=?,dados=?,tentativas=tentativas+1 WHERE id=?",
                (digest(estado),self.c.cifra.cifrar(['sessao',r['id']],dados),r['id']))
            return {'estado':estado,'verificador':verificador}

    def tem_estado(self,estado):
        return bool(self.c.db.execute('SELECT 1 FROM web_sessoes WHERE estado=?',(digest(estado),)).fetchone())

    def consumir(self,cookie,estado):
        with self.c._transacao():
            r=self._row(cookie)
            if r['fase']!='oauth' or not r['estado'] or not hmac.compare_digest(r['estado'],digest(estado)):
                raise SessaoEncerrada('Retorno de login inválido.')
            self.c.db.execute("UPDATE web_sessoes SET fase='processando' WHERE id=?",(r['id'],))
            d=self._dados(r)
            return {k:d[k] for k in ('verificador','servidor','personagem','idioma')}

    def finalizar(self,cookie,estado,novo,usuario):
        with self.c._transacao():
            r=self._row(cookie)
            if r['fase']!='processando' or r['estado']!=digest(estado):raise SessaoEncerrada('Retorno já usado.')
            if not isinstance(usuario,str) or not usuario.isdigit() or len(usuario)>22:raise AcessoNegado('Identidade inválida.')
            self.c.db.execute('DELETE FROM web_sessoes WHERE id=?',(r['id'],))
            return self._gravar(novo,usuario=usuario)

    def sair(self,cookie,csrf):
        with self.c._transacao():
            try:r=self._row(cookie)
            except SessaoEncerrada:return
            self._csrf(r,csrf)
            self.c.db.execute('DELETE FROM web_sessoes WHERE id=?',(r['id'],))

    def invalidar(self,cookie):
        if isinstance(cookie,str):self.c.db.execute('DELETE FROM web_sessoes WHERE id=?',(digest(cookie),))
