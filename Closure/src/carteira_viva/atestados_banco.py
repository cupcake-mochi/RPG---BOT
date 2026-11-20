"""Último atestado de ativação por operação de cópia; nunca libera criação.

Guarda só estado, código e os máximos de sequência por rotina, cifrados. Os
máximos nunca descem: uma leitura com contador menor vira `contador_voltou`, e
só o dono da operação zera a base, com registro em auditoria (restaurar uma
versão antiga no Drive volta o metadado junto).
"""
import hashlib
import re

from .atestado_ativacao import CODIGOS, INCONSISTENTE, ROTINAS, TIPOS, Atestado
from .modelos import OFICIAIS
from .segredos import Conflito, ErroCarteira, json_bytes

ESTADOS = ('nao_ativada', 'aguardando', 'ativa', 'parada', 'inconsistente')


class Atestados:
    @staticmethod
    def _ctx_atestado(servidor, ator, operacao):
        return ['atestado_ativacao', servidor, ator, operacao]

    def contexto_atestado(self, membro, ref):
        """Arquivo da cópia identificada e uma chave que muda se operação, destino ou autorização mudarem."""
        d = self.contexto_copia(membro, ref)
        oficiais = {re.search(r'/d/([A-Za-z0-9_-]+)', x['url']).group(1) for x in OFICIAIS}
        if d['estado'] != 'identificada' or not d['destino'] or d['destino'] in oficiais or d['destino'] == d['origem']:
            raise Conflito('Só a cópia nova identificada tem atestado de ativação.')
        chave = hashlib.sha256(json_bytes(['atestado_ativacao_v1', ref.servidor, ref.ator, ref.operacao,
                                           d['destino'], d['autorizacao']])).hexdigest()
        return d['destino'], chave

    def atestado_salvo(self, membro, ref):
        self.contexto_atestado(membro, ref)
        row = self.db.execute('SELECT * FROM atestados_rest WHERE operacao=?', (ref.operacao,)).fetchone()
        if row is None:
            return None
        d = self.cifra.abrir(self._ctx_atestado(ref.servidor, ref.ator, ref.operacao), row['conteudo'])
        if d['lido_em'] != row['lido']:
            raise ErroCarteira('Atestado de ativação inconsistente no banco.')
        return d

    def _guardar_atestado(self, ref, d):
        self.db.execute('INSERT INTO atestados_rest(operacao,lido,conteudo) VALUES (?,?,?) '
                        'ON CONFLICT(operacao) DO UPDATE SET lido=excluded.lido,conteudo=excluded.conteudo',
                        (ref.operacao, d['lido_em'], self.cifra.cifrar(
                            self._ctx_atestado(ref.servidor, ref.ator, ref.operacao), d)))

    def registrar_atestado(self, membro, ref, atestado, lido_em):
        if (type(atestado) is not Atestado or atestado.estado not in ESTADOS or atestado.codigo not in CODIGOS or
                type(lido_em) not in (int, float) or lido_em <= 0):
            raise ErroCarteira('Atestado de ativação inválido.')
        with self._transacao():
            anterior = self.atestado_salvo(membro, ref)
            maximos = dict((anterior or {}).get('maximos', {}))
            # Leitura inconsistente não sobe nem desce a base guardada.
            if atestado.estado != INCONSISTENTE:
                for r, v in atestado.maximos:
                    if r not in TIPOS or type(v) is not int or v < 1:
                        raise ErroCarteira('Atestado de ativação inválido.')
                    maximos[r] = max(maximos.get(r, 0), v)
            d = dict(estado=atestado.estado, codigo=atestado.codigo, motivo=atestado.motivo,
                     faltam=[r for r in atestado.faltam if r in ROTINAS], maximos=maximos, lido_em=lido_em)
            self._guardar_atestado(ref, d)
            return d

    def recomecar_atestado(self, membro, ref):
        """Só depois de `contador_voltou`; a próxima leitura não é reaproveitada."""
        with self._transacao():
            d = self.atestado_salvo(membro, ref)
            if d is None or d['codigo'] != 'contador_voltou':
                raise Conflito('Só dá para recomeçar a contagem depois de uma versão antiga restaurada.')
            novo = {**d, 'maximos': {}, 'lido_em': 0.0}  # força leitura nova
            self._guardar_atestado(ref, novo)
            self._auditar(ref.servidor, ref.ator, None, 'atestado_recomecado')
            return novo
