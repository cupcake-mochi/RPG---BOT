"""Diário interno de cópia; não é cadastro, inicialização ou permissão de escrita.

O estado enviada é gravado ANTES do POST. Depois disso só se reconcilia por
marcador: uma resposta perdida nunca permite repetir files.copy automaticamente.
"""
from dataclasses import dataclass
import hashlib
import re
import secrets

from .modelos import OFICIAIS
from .segredos import AcessoNegado, Conflito, ErroCarteira


@dataclass(frozen=True, repr=False)
class ReferenciaCopia:
    servidor: str
    ator: str
    operacao: str
    conexao: str


def hash_texto(s):
    return hashlib.sha256(s.encode()).hexdigest()


class Copias:
    @staticmethod
    def _ctx_copia(row):
        return ['copia_rest', row['servidor'], row['ator'], row['operacao']]

    def _origem_modelo_copia(self, servidor, modelo):
        revisao, config = self._modelo(servidor)
        escolha = config['escolha']
        if (modelo not in ('era', 'ciclo', 'servidor') or
                (escolha != 'oficiais' and escolha != modelo) or
                (escolha == 'oficiais' and modelo == 'servidor')):
            raise Conflito('O modelo do servidor mudou. Confira a escolha novamente.')
        if modelo == 'servidor':
            arquivo = config['referencia']['arquivo']
            versao = config['referencia']['versao_drive']
        else:
            url = next(x['url'] for x in OFICIAIS if x['id'] == modelo)
            arquivo = re.search(r'/d/([A-Za-z0-9_-]+)', url).group(1)
            versao = None
        return dict(modelo=modelo, modelo_revisao=revisao, origem=arquivo, versao_configurada=versao)

    def preparar_copia_modelo(self, membro, *, conexao, modelo, pedido):
        """Adaptador interno. Não aceitar esses dados de uma rota pública de criação."""
        self._membro(membro)
        if not isinstance(pedido, str) or not 1 <= len(pedido.strip()) <= 200:
            raise ErroCarteira('Identificação de pedido inválida.')
        with self._transacao():
            c = self._conexao_do_dono(membro, conexao)
            origem = self._origem_modelo_copia(membro.servidor, modelo)
            chave = hash_texto(pedido)
            row = self.db.execute('SELECT * FROM copias_rest WHERE servidor=? AND ator=? AND pedido=?',
                                 (membro.servidor, membro.usuario, chave)).fetchone()
            if row:
                d = self.cifra.abrir(self._ctx_copia(row), row['conteudo'])
                if row['conexao'] != conexao or d['modelo'] != modelo:
                    raise Conflito('Este pedido já foi usado em outra cópia.')
                ref = ReferenciaCopia(membro.servidor, membro.usuario, row['operacao'], conexao)
                self.contexto_copia(membro, ref)
                return ref
            n = self.db.execute('SELECT count(*) FROM copias_rest WHERE servidor=? AND ator=?',
                                (membro.servidor, membro.usuario)).fetchone()[0]
            if n >= 64 or self.db.execute('SELECT count(*) FROM copias_rest').fetchone()[0] >= 10000:
                raise ErroCarteira('Limite de operações de cópia. Aguarde a revisão dos registros.')
            if self.db.execute("SELECT 1 FROM copias_rest WHERE servidor=? AND ator=? AND estado!='identificada'",
                               (membro.servidor, membro.usuario)).fetchone():
                raise Conflito('Há uma cópia pendente. Reconcilie esse pedido antes de iniciar outro.')
            self._servidor(membro.servidor)
            op = secrets.token_hex(32)
            d = dict(**origem, autorizacao=c['autorizacao'], estado='preparada', versao_origem=None,
                     destino=None, versao_destino=None)
            row = dict(servidor=membro.servidor, ator=membro.usuario, operacao=op)
            self.db.execute('INSERT INTO copias_rest VALUES (?,?,?,?,?,?,?,?,?)',
                (membro.servidor, membro.usuario, op, conexao, chave, 'preparada', self.agora(), self.agora(),
                 self.cifra.cifrar(self._ctx_copia(row), d)))
            self.db.execute('UPDATE conexoes SET sem_uso_desde=NULL WHERE id=?', (conexao,))
            return ReferenciaCopia(membro.servidor, membro.usuario, op, conexao)

    def contexto_copia(self, membro, ref):
        self._membro(membro)
        if (type(ref) is not ReferenciaCopia or
                (membro.servidor, membro.usuario) != (ref.servidor, ref.ator)):
            raise AcessoNegado('Cópia pertence a outro contexto.')
        row = self.db.execute('SELECT * FROM copias_rest WHERE servidor=? AND ator=? AND operacao=? AND conexao=?',
                             (ref.servidor, ref.ator, ref.operacao, ref.conexao)).fetchone()
        if row is None:
            raise Conflito('Registro de cópia indisponível.')
        c = self._conexao_do_dono(membro, ref.conexao)
        d = self.cifra.abrir(self._ctx_copia(row), row['conteudo'])
        origem = self._origem_modelo_copia(ref.servidor, d['modelo'])
        if (d['estado'] != row['estado'] or c['autorizacao'] != d['autorizacao'] or
                any(d[k] != v for k, v in origem.items())):
            raise Conflito('Modelo ou autorização mudou. Não continue a cópia anterior.')
        return d

    def _credencial_copia(self, membro, ref):
        from .banco import CredencialGoogle
        self.contexto_copia(membro, ref)
        c = self._conexao_do_dono(membro, ref.conexao)
        obj = self.cifra.abrir(['conexao', c['id'], c['usuario'], c['autorizacao']], c['segredo'])
        if hash_texto(obj['conta']) != c['conta_hash'] or hash_texto(obj['cliente']) != c['cliente_hash']:
            raise ErroCarteira('Identidade da conexão inconsistente.')
        return CredencialGoogle(obj['conta'], obj['cliente'], obj['refresh'], c['autorizacao'])

    def _guardar_copia(self, ref, d):
        self.db.execute('UPDATE copias_rest SET estado=?,atualizado=?,conteudo=? WHERE operacao=?',
            (d['estado'], self.agora(), self.cifra.cifrar(self._ctx_copia(dict(
                servidor=ref.servidor, ator=ref.ator, operacao=ref.operacao)), d), ref.operacao))

    def fixar_versao_copia(self, membro, ref, versao):
        if not isinstance(versao, str) or not re.fullmatch(r'[0-9]{1,30}', versao):
            raise ErroCarteira('Versão de modelo inválida.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            if (d['estado'] != 'preparada' or d['versao_origem'] not in (None, versao) or
                    d['versao_configurada'] not in (None, versao)):
                raise Conflito('O modelo mudou. A cópia não foi enviada.')
            self._guardar_copia(ref, {**d, 'versao_origem': versao})

    def armar_envio_copia(self, membro, ref):
        """Transação única entre processos. False nunca autoriza outro POST."""
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            if d['estado'] != 'preparada':
                return False
            if d['versao_origem'] is None:
                raise Conflito('Confira a versão do modelo antes da cópia.')
            self._guardar_copia(ref, {**d, 'estado': 'enviada'})
            return True

    def registrar_destino_copia(self, membro, ref, destino):
        from .copias_google import DestinoCopia
        if type(destino) is not DestinoCopia:
            raise ErroCarteira('Use a observação do adaptador Google.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            if (d['estado'] not in ('enviada', 'identificada') or destino.operacao != ref.operacao or
                    destino.origem != d['origem'] or destino.arquivo == d['origem'] or
                    d['destino'] not in (None, destino.arquivo)):
                raise Conflito('A cópia observada não pertence a esta operação.')
            if d['estado'] == 'identificada' and d['versao_destino'] != destino.versao:
                raise Conflito('A cópia foi alterada após a identificação. Não renove sua prova de criação.')
            self._guardar_copia(ref, {**d, 'estado': 'identificada', 'destino': destino.arquivo,
                                     'versao_destino': destino.versao})
            # Nunca publicar IDs privados ou chamar identificada de inicializada.
            return dict(copia_identificada=True, inicializacao_concluida=False, criacao_disponivel=False)
