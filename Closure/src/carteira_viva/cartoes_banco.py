"""Projeção básica e confirmação de apresentação; nenhuma aprovação mecânica."""
import hashlib
import json
import secrets
from .permissoes import Acao, PUBLICOS, permitido
from .segredos import Conflito, ErroCarteira, json_bytes

EDITAVEIS = frozenset({'titulo','frase','cor','idade','cla'})


class Cartoes:
    def _resumo_cartao(self, servidor, personagem):
        r=self.db.execute('SELECT * FROM resumos_cartao WHERE servidor=? AND personagem=?',(servidor,personagem)).fetchone()
        if r is None: return {}, None
        f=self._fonte(servidor,personagem)
        if r['revisao']!=f['revisao']: return {}, None
        return self.cifra.abrir(['resumo',servidor,personagem],r['conteudo']),r['lido_em']

    def _salvar_resumo(self, ref, campos):
        if not isinstance(campos.get('ficha'),dict): return
        publico={}
        for k,limite in (('nome',100),('origem',200),('caminho',200)):
            c=campos['ficha'].get(k,{})
            v=c.get('valor') if isinstance(c,dict) else None
            if isinstance(v,str) and v.strip(): publico[k]=v.strip()[:limite]
        envelope=self.cifra.cifrar(['resumo',ref.servidor,ref.personagem],publico)
        self.db.execute('INSERT OR REPLACE INTO resumos_cartao VALUES (?,?,?,?,?)',
                        (ref.servidor,ref.personagem,ref.revisao,self.agora(),envelope))

    def dono_personagem(self,membro,personagem):
        return self._personagem(membro,personagem)['dono']

    def cartao_galeria(self,membro,personagem):
        r=self._personagem(membro,personagem)
        card=self.cartao(membro,personagem)
        _,hora=self._resumo_cartao(membro.servidor,personagem)
        f=self._fonte(membro.servidor,personagem)
        leitura=self.db.execute('SELECT id FROM leituras WHERE servidor=? AND personagem=? AND expira>?',
                                (membro.servidor,personagem,self.agora())).fetchone()
        return card|{'lido_em':hora,'precisa_atualizar':not (hora is not None and self.agora()-hora<=60 and leitura and f['estado']=='ativa'),
            'capacidades':{a.value:permitido(a,membro,membro.servidor,r['dono'],self._permissoes(membro.servidor))
                            for a in (Acao.VER_DETALHES,Acao.ANALISAR,Acao.PERSONALIZAR,Acao.TROCAR_ARQUIVO,Acao.EXCLUIR)}}

    def perfil_editavel(self,membro,personagem):
        r=self._personagem(membro,personagem,Acao.PERSONALIZAR)
        return {'perfil':self.cifra.abrir(['perfil',membro.servidor,personagem],r['perfil']),
                'campos_publicos':json.loads(r['campos_publicos']),'base':self._base_cartao(membro,personagem)}

    def _base_cartao(self,membro,personagem):
        r=self._personagem(membro,personagem,Acao.PERSONALIZAR)
        config=self.db.execute('SELECT revisao FROM servidores WHERE id=?',(membro.servidor,)).fetchone()[0]
        f=self._fonte(membro.servidor,personagem)
        return hashlib.sha256(json_bytes([r['perfil'].hex(),r['campos_publicos'],config,f['revisao']])).hexdigest()

    def preparar_cartao(self,membro,personagem,*,alteracoes,campos_publicos,imagem=None,base_esperada=None):
        with self._transacao():
            atual=self.perfil_editavel(membro,personagem)
            if base_esperada is not None and base_esperada!=atual['base']:
                raise Conflito('O cartão mudou desde que o formulário foi aberto.')
            if not isinstance(alteracoes,dict) or set(alteracoes)-EDITAVEIS:
                raise ErroCarteira('Altere apenas os campos de apresentação permitidos.')
            perfil=dict(atual['perfil'])
            for k,v in alteracoes.items():
                if v is None: perfil.pop(k,None)
                else: perfil[k]=v
            if imagem is not None:
                if imagem=='': perfil.pop('imagem_id',None)
                elif self.db.execute('SELECT 1 FROM imagens WHERE id=? AND servidor=? AND personagem=?',
                                     (imagem,membro.servidor,personagem)).fetchone(): perfil['imagem_id']=imagem
                else: raise ErroCarteira('Imagem indisponível para este personagem.')
            campos=frozenset(campos_publicos)
            if not campos<=PUBLICOS or 'nome' not in campos: raise ErroCarteira('Campos públicos inválidos.')
            self._perfil(membro.servidor,personagem,perfil) # valida antes de criar a prévia
            if self.db.execute('SELECT count(*) FROM previas_cartao WHERE usuario=? AND expira>?',
                               (membro.usuario,self.agora())).fetchone()[0]>=5:
                raise ErroCarteira('Conclua ou cancele uma das prévias antes de abrir outra.')
            pid=secrets.token_hex(16)
            dados={'perfil':perfil,'campos_publicos':sorted(campos)}
            envelope=self.cifra.cifrar(['previa',membro.servidor,personagem,membro.usuario,pid],dados)
            self.db.execute('INSERT INTO previas_cartao VALUES (?,?,?,?,?,?,?)',
                            (pid,membro.servidor,personagem,membro.usuario,self._base_cartao(membro,personagem),self.agora()+600,envelope))
            card=self.cartao_galeria(membro,personagem)
            from .permissoes import cartao_publico
            autorizados=json.loads(self.db.execute('SELECT campos_publicos FROM servidores WHERE id=?',(membro.servidor,)).fetchone()[0])
            resumo,_=self._resumo_cartao(membro.servidor,personagem)
            card['perfil']=cartao_publico(perfil|resumo,campos&frozenset(autorizados))
            return {'previa':pid,'cartao':card,'expira_em':600}

    def _previa(self,membro,personagem,previa):
        self._personagem(membro,personagem,Acao.PERSONALIZAR)
        r=self.db.execute('SELECT * FROM previas_cartao WHERE id=? AND servidor=? AND personagem=? AND usuario=? AND expira>?',
                          (previa,membro.servidor,personagem,membro.usuario,self.agora())).fetchone()
        if not r: raise Conflito('Esta prévia expirou ou já foi encerrada.')
        return r

    def confirmar_cartao(self,membro,personagem,previa):
        with self._transacao():
            r=self._previa(membro,personagem,previa)
            if r['base']!=self._base_cartao(membro,personagem): raise Conflito('O cartão ou a fonte mudou. Abra uma prévia nova.')
            obj=self.cifra.abrir(['previa',membro.servidor,personagem,membro.usuario,previa],r['conteudo'])
            self.personalizar(membro,personagem,perfil=obj['perfil'],campos_publicos=obj['campos_publicos'])
            self.db.execute('DELETE FROM previas_cartao WHERE id=?',(previa,))
            return self.cartao_galeria(membro,personagem)

    def cancelar_cartao(self,membro,personagem,previa):
        with self._transacao():
            self._previa(membro,personagem,previa)
            self.db.execute('DELETE FROM previas_cartao WHERE id=?',(previa,))

    def registrar_imagem(self,membro,personagem,imagem):
        self.pode_enviar_imagem(membro,personagem)
        self.db.execute('INSERT INTO imagens VALUES (?,?,?,?)',(imagem,membro.servidor,personagem,self.agora()))

    def pode_enviar_imagem(self,membro,personagem):
        self._personagem(membro,personagem,Acao.PERSONALIZAR)
        config=self.db.execute('SELECT campos_publicos FROM servidores WHERE id=?',(membro.servidor,)).fetchone()
        if 'imagem_id' not in json.loads(config[0]): raise ErroCarteira('Imagens não estão permitidas neste servidor.')
        if self.db.execute('SELECT count(*) FROM imagens i JOIN personagens p ON p.servidor=i.servidor AND p.id=i.personagem WHERE p.dono=? AND i.criado>?',
                           (membro.usuario,self.agora()-86400)).fetchone()[0]>=10:
            raise ErroCarteira('Limite de dez imagens por dia atingido. Tente amanhã.')

    def configuracao_cartoes(self,membro):
        self._autorizar(membro,Acao.CONFIGURAR)
        self._servidor(membro.servidor)
        r=self.db.execute('SELECT * FROM servidores WHERE id=?',(membro.servidor,)).fetchone()
        p=self._permissoes(membro.servidor)
        return {'revisores':sorted(p.revisores),'editores':sorted(p.editores),'campos_publicos':json.loads(r['campos_publicos']),'idioma':r['idioma']}

    def alterar_revisor(self,membro,cargo,permitir_cargo):
        with self._transacao():
            c=self.configuracao_cartoes(membro)
            revisores=set(c['revisores'])
            if permitir_cargo:revisores.add(cargo)
            else:revisores.discard(cargo)
            self.configurar(membro,revisores=revisores,editores=c['editores'],campos_publicos=c['campos_publicos'],idioma=c['idioma'])

    def limpar_imagens(self):
        ativos=set(self.imagens_ativas())
        for r in self.db.execute('SELECT id FROM imagens WHERE criado<=?',(self.agora()-86400,)).fetchall():
            if r['id'] not in ativos: self.db.execute('DELETE FROM imagens WHERE id=?',(r['id'],))

    def imagem_cartao(self,membro,personagem,*,previa=None):
        if previa:
            r=self._previa(membro,personagem,previa)
            obj=self.cifra.abrir(['previa',membro.servidor,personagem,membro.usuario,previa],r['conteudo'])
            return obj['perfil'].get('imagem_id') if 'imagem_id' in obj['campos_publicos'] else None
        return self.cartao(membro,personagem)['perfil'].get('imagem_id')

    def imagens_ativas(self):
        # Inclui prévias válidas; não apagar arquivo que ainda aguarda confirmação.
        usados=set()
        for r in self.db.execute('SELECT servidor,id,perfil FROM personagens'):
            obj=self.cifra.abrir(['perfil',r['servidor'],r['id']],r['perfil']); usados.add(obj.get('imagem_id'))
        for r in self.db.execute('SELECT * FROM previas_cartao WHERE expira>?',(self.agora(),)):
            obj=self.cifra.abrir(['previa',r['servidor'],r['personagem'],r['usuario'],r['id']],r['conteudo']);usados.add(obj['perfil'].get('imagem_id'))
        return sorted(x for x in usados if x)
