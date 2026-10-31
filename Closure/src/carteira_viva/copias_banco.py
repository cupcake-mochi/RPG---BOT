"""Diário interno de cópia; não é cadastro, inicialização ou permissão de escrita.

O estado enviada é gravado ANTES do POST. Depois disso só se reconcilia por
marcador: uma resposta perdida nunca permite repetir files.copy automaticamente.
"""
from dataclasses import dataclass
import hashlib
import re
import secrets

from .modelos import OFICIAIS
from .observacoes_copia import ObservacaoVersao, LIMITE, conteudo_contexto
from .segredos import AcessoNegado, Conflito, ErroCarteira, json_bytes


@dataclass(frozen=True, repr=False)
class ReferenciaCopia:
    servidor: str
    ator: str
    operacao: str
    conexao: str


def hash_texto(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _mesma_candidata(d, destino):
    """Mesma candidata com versão nova: só se o modifiedTime da primeira observação
    não mudou. A versão da candidata nunca foi lida nem usada como conteúdo; a prova
    de conteúdo começa na identificação (ref_destino)."""
    c = d.get('candidata') or {}
    return (c.get('arquivo') == destino.arquivo and destino.modificado is not None and
            d.get('candidata_modificado') == destino.modificado)


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
                     destino=None, versao_destino=None, protocolo_copia=2, candidata=None)
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
        if type(d.get('protocolo_copia', 1)) is not int or d.get('protocolo_copia', 1) not in (1, 2):
            raise Conflito('Protocolo de cópia não suportado. Não continue esta operação.')
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

    def contexto_diagnostico_copia(self, membro, ref, alvo):
        """Leitura interna de operação existente; não emite permissão de escrita.

        O piloto usa somente modelo particular, nunca as oficiais. Não recebe
        ID de arquivo, não cria intenção, não muda estado/versão/retencão.
        """
        d = self.contexto_copia(membro, ref)
        if type(alvo) is not str or alvo not in ('origem', 'copia'):
            raise ErroCarteira('Escolha origem ou cópia para o diagnóstico.')
        if d['modelo'] != 'servidor' or d['estado'] not in ('preparada', 'enviada', 'identificada'):
            raise Conflito('O diagnóstico exige operação existente de um modelo particular.')
        arquivo = d['origem']
        if alvo == 'copia':
            if d['estado'] == 'preparada' or d['versao_origem'] is None:
                raise Conflito('O diagnóstico da cópia exige envio com versão original registrada.')
            candidata = d.get('candidata')
            arquivo = d['destino'] if d['estado'] == 'identificada' else (
                candidata.get('arquivo') if type(candidata) is dict else None)
            if not arquivo or arquivo == d['origem'] or self.db.execute(
                    'SELECT 1 FROM fontes WHERE arquivo=?', (arquivo,)).fetchone():
                raise Conflito('O diagnóstico da cópia exige candidata não cadastrada já registrada.')
        oficiais = {re.search(r'/d/([A-Za-z0-9_-]+)', x['url']).group(1) for x in OFICIAIS}
        if arquivo in oficiais or d['origem'] in oficiais:
            raise Conflito('Este piloto não diagnostica fichas oficiais.')
        contexto = hashlib.sha256(json_bytes(['diagnostico_grade_v1', ref.servidor,
            ref.ator, ref.operacao, alvo, conteudo_contexto(d)])).hexdigest()
        return arquivo, contexto

    def _guardar_copia(self, ref, d):
        self.db.execute('UPDATE copias_rest SET estado=?,atualizado=?,conteudo=? WHERE operacao=?',
            (d['estado'], self.agora(), self.cifra.cifrar(self._ctx_copia(dict(
                servidor=ref.servidor, ator=ref.ator, operacao=ref.operacao)), d), ref.operacao))

    def fixar_versao_copia(self, membro, ref, versao, impressao=None):
        from .equivalencia_versao import Impressao
        if not isinstance(versao, str) or not re.fullmatch(r'[0-9]{1,30}', versao):
            raise ErroCarteira('Versão de modelo inválida.')
        if impressao is not None and (type(impressao) is not Impressao or impressao.versao != versao):
            raise ErroCarteira('Impressão da origem inválida.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            if (d['estado'] != 'preparada' or d['versao_origem'] not in (None, versao) or
                    d['versao_configurada'] not in (None, versao)):
                raise Conflito('O modelo mudou. A cópia não foi enviada.')
            novo = {**d, 'versao_origem': versao}
            if impressao is not None:
                if d.get('ref_origem') not in (None, impressao.dados()):
                    raise Conflito('A origem já tem outra referência. Não substitua.')
                novo['ref_origem'] = impressao.dados()
            self._guardar_copia(ref, novo)

    def registrar_equivalencia_copia(self, membro, ref, alvo, impressao):
        """Versão nova do mesmo arquivo com mesmo modifiedTime e conteúdo. Não altera recibo."""
        from .equivalencia_versao import ALVOS, Impressao, LIMITE_EQUIVALENCIAS, confere
        if alvo not in ALVOS or type(impressao) is not Impressao:
            raise ErroCarteira('Equivalência inválida.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            referencia = d.get('ref_origem' if alvo == 'origem' else 'ref_destino')
            base = d['versao_origem'] if alvo == 'origem' else d['versao_destino']
            if (referencia is None or base is None or base != referencia.get('versao') or
                    not confere(referencia, impressao)):
                raise Conflito('A versão nova não tem o mesmo conteúdo e modificação. Não continue.')
            eq = dict(d.get('equivalencias') or {})
            lista = list(eq.get(alvo, []))
            if impressao.versao == base or any(e['versao'] == impressao.versao for e in lista):
                return
            if len(lista) >= LIMITE_EQUIVALENCIAS:
                raise Conflito('O arquivo mudou de versão vezes demais. Não continue esta operação.')
            eq[alvo] = lista + [impressao.dados()]
            # Prova técnica não é uma nova transição da cópia. Preservar o
            # atualizado original, usado pela retenção das identificadas.
            self.db.execute('UPDATE copias_rest SET conteudo=? WHERE operacao=?',
                (self.cifra.cifrar(self._ctx_copia(dict(servidor=ref.servidor,
                    ator=ref.ator, operacao=ref.operacao)), {**d, 'equivalencias': eq}), ref.operacao))

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

    def registrar_observacao_copia(self, membro, ref, observacao):
        if type(observacao) is not ObservacaoVersao:
            raise ErroCarteira('Use a observação tipada do adaptador interno.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            historico = d.get('observacoes_versao', [])
            evento = dict(etapa=observacao.etapa, esperada=observacao.esperada,
                          observada=observacao.observada)
            # Contagens repetidas não aumentam o volume nem renovam a primeira observação.
            if historico and all(historico[-1][k] == v for k, v in evento.items()):
                evento = {**historico[-1], 'ultimo_em': self.agora(),
                          'vezes': min(historico[-1]['vezes'] + 1, 1000000000)}
                historico = historico[:-1]
            else:
                evento.update(primeiro_em=self.agora(), ultimo_em=self.agora(), vezes=1)
            # O diagnóstico não renova a retenção da cópia identificada.
            novo = {**d, 'observacoes_versao': (historico + [evento])[-LIMITE:]}
            ctx = self._ctx_copia(dict(servidor=ref.servidor, ator=ref.ator, operacao=ref.operacao))
            self.db.execute('UPDATE copias_rest SET conteudo=? WHERE operacao=?',
                            (self.cifra.cifrar(ctx, novo), ref.operacao))

    def registrar_candidata_copia(self, membro, ref, destino):
        """Identidade e versão da primeira observação; não certifica inicialização."""
        from .copias_google import DestinoCopia
        if type(destino) is not DestinoCopia:
            raise ErroCarteira('Use a observação do adaptador Google.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            candidata = dict(arquivo=destino.arquivo, versao=destino.versao)
            if (d['estado'] != 'enviada' or d['versao_origem'] is None or destino.operacao != ref.operacao or
                    destino.origem != d['origem'] or destino.arquivo == d['origem'] or
                    self.db.execute('SELECT 1 FROM fontes WHERE arquivo=?', (destino.arquivo,)).fetchone()):
                raise Conflito('A candidata não pertence a uma cópia pendente e não cadastrada.')
            if d.get('candidata') is not None:
                if d['candidata'] != candidata and not _mesma_candidata(d, destino):
                    raise Conflito('A candidata mudou após a primeira observação. Não adote outra versão.')
                return
            novo = {**d, 'candidata': candidata}
            if destino.modificado is not None:
                novo['candidata_modificado'] = destino.modificado
            self._guardar_copia(ref, novo)

    def registrar_destino_copia(self, membro, ref, destino, impressao=None):
        from .copias_google import DestinoCopia
        from .equivalencia_versao import Impressao, versoes_aceitas
        if type(destino) is not DestinoCopia:
            raise ErroCarteira('Use a observação do adaptador Google.')
        if impressao is not None and (type(impressao) is not Impressao or impressao.versao != destino.versao or
                                      impressao.modificado != destino.modificado):
            raise ErroCarteira('Impressão do destino inválida.')
        with self._transacao():
            d = self.contexto_copia(membro, ref)
            if (d['estado'] not in ('enviada', 'identificada') or d['versao_origem'] is None or destino.operacao != ref.operacao or
                    destino.origem != d['origem'] or destino.arquivo == d['origem'] or
                    d['destino'] not in (None, destino.arquivo)):
                raise Conflito('A cópia observada não pertence a esta operação.')
            if d['estado'] == 'identificada':
                if destino.versao not in versoes_aceitas(d, 'destino'):
                    raise Conflito('A cópia foi alterada após a identificação. Não renove sua prova de criação.')
                return dict(copia_identificada=True, inicializacao_concluida=False, criacao_disponivel=False)
            if (d.get('protocolo_copia', 1) == 2 or d.get('candidata') is not None) and d.get('candidata') != dict(
                    arquivo=destino.arquivo, versao=destino.versao) and not _mesma_candidata(d, destino):
                raise Conflito('Confira a candidata antes de identificar a cópia. Não altere sua versão.')
            novo = {**d, 'estado': 'identificada', 'destino': destino.arquivo, 'versao_destino': destino.versao}
            if impressao is not None:
                novo['ref_destino'] = impressao.dados()
            self._guardar_copia(ref, novo)
            # Nunca publicar IDs privados ou chamar identificada de inicializada.
            return dict(copia_identificada=True, inicializacao_concluida=False, criacao_disponivel=False)
