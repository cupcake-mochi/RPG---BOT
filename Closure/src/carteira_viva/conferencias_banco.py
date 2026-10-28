"""Estado privado de conferências REST somente de leitura, não de inicialização.

Retoma entre domínios completos. Nunca guarda uma grade, token ou cursor de
página. Os métodos são internos e exigem Membro/Referência autenticados.
"""
from dataclasses import asdict, dataclass
import hashlib
import math
import re
import secrets
import time

from .conferencia_inicializacao import ConferenciaGrade, FLAGS, abrir_recibo
from .contrato_inicializacao import CONTRATO_SHA256
from .permissoes import Acao
from .segredos import AcessoNegado, Conflito, ErroCarteira, json_bytes

DOMINIOS = ('financeiro', 'progressao')
PRAZO = 1800
MAX_ESTADO = 32 * 1024
PROTOCOLO = 'carteira-conferencias-persistidas-1'


def _hash(valor):
    return hashlib.sha256(json_bytes(valor)).hexdigest()


def _erro():
    raise Conflito('Conferência indisponível ou desatualizada. Inicie outra leitura.') from None


@dataclass(frozen=True, repr=False)
class BilheteConferencia:
    """Objeto do backend. Não serializar nem aceitar do navegador."""
    servidor: str
    personagem: str
    operacao: str
    revisao: int


class Conferencias:
    def contexto_conferencia_rest(self, membro, ref):
        with self._transacao():
            self._referencia(membro, ref)
            chave = self.contexto_leitura(membro, ref.personagem)
            servidor = self.db.execute('SELECT revisao FROM servidores WHERE id=?', (membro.servidor,)).fetchone()[0]
            modelo = self.db.execute('SELECT revisao FROM modelos_servidor WHERE servidor=?', (membro.servidor,)).fetchone()
            return _hash([PROTOCOLO, CONTRATO_SHA256, asdict(ref), chave, servidor, modelo[0] if modelo else 0])

    @staticmethod
    def _ctx_conferencia(row):
        return ['conferencias_rest', row['servidor'], row['personagem'], row['operacao']]

    def _abrir_conferencia(self, membro, row):
        from .banco import ReferenciaLeitura
        if row is None: _erro()
        if len(row['conteudo']) > MAX_ESTADO: _erro()
        d = self.cifra.abrir(self._ctx_conferencia(row), row['conteudo'])
        campos = {'protocolo', 'contrato', 'operacao', 'revisao', 'criado', 'expira',
                  'referencia', 'contexto', 'versao_drive', 'dominios'}
        if (type(d) is not dict or set(d) != campos or d['protocolo'] != PROTOCOLO or
                d['contrato'] != CONTRATO_SHA256 or type(d['referencia']) is not dict or
                set(d['referencia']) != set(ReferenciaLeitura.__dataclass_fields__) or
                type(d['dominios']) is not list or len(d['dominios']) > 2 or
                type(d['revisao']) is not int or d['revisao'] != len(d['dominios']) or
                not isinstance(d['versao_drive'], str) or not re.fullmatch('[0-9]{1,30}', d['versao_drive']) or
                not isinstance(d['contexto'], str) or not re.fullmatch('[a-f0-9]{64}', d['contexto']) or
                not isinstance(d['operacao'], str) or not re.fullmatch('[a-f0-9]{32}', d['operacao'])): _erro()
        for k in ('criado', 'expira'):
            if type(d[k]) not in (int, float) or not math.isfinite(d[k]): _erro()
        if (any(d[k] != row[k] for k in ('operacao', 'revisao', 'criado', 'expira')) or
                d['expira'] - d['criado'] != PRAZO or not d['criado'] <= self.agora() < d['expira']): _erro()
        ref = ReferenciaLeitura(**d['referencia'])
        if (ref.servidor, ref.personagem) != (row['servidor'], row['personagem']): _erro()
        if ref.ator != row['ator']: _erro()
        if membro.usuario != ref.ator:
            raise AcessoNegado('Conferência pertence a outra pessoa.')
        if _hash([PROTOCOLO, self.contexto_conferencia_rest(membro, ref), d['operacao']]) != d['contexto']: _erro()
        for i, item in enumerate(d['dominios']):
            if type(item) is not dict or set(item) != {'recibo', 'resultado'}: _erro()
            # Revalida metadados e hash do resultado também ao reabrir/rotacionar.
            recibo = item['recibo']
            envelope = self.cifra.cifrar(['recibo_rest', d['contexto'], ref.arquivo, DOMINIOS[i]], recibo)
            abrir_recibo(self.cifra, envelope, contexto=d['contexto'], arquivo=ref.arquivo,
                         dominio=DOMINIOS[i], versao_drive=d['versao_drive'])
            resultado = item['resultado']
            if (type(resultado) is not dict or _hash(resultado) != recibo['resultado'] or
                    resultado.get('conferencia_parcial_concluida') is not True or
                    resultado.get('dominio') != DOMINIOS[i] or
                    any(resultado.get(k) is not False for k in FLAGS)): _erro()
        return d, ref

    @staticmethod
    def _bilhete(row):
        return BilheteConferencia(row['servidor'], row['personagem'], row['operacao'], row['revisao'])

    def _conferencia(self, membro, bilhete):
        if (type(bilhete) is not BilheteConferencia or bilhete.servidor != membro.servidor or
                type(bilhete.revisao) is not int or not 0 <= bilhete.revisao <= 2 or
                not isinstance(bilhete.operacao, str) or not re.fullmatch('[a-f0-9]{32}', bilhete.operacao)): _erro()
        row = self.db.execute('SELECT * FROM conferencias_rest WHERE servidor=? AND personagem=?',
                              (bilhete.servidor, bilhete.personagem)).fetchone()
        d, ref = self._abrir_conferencia(membro, row)
        if bilhete != self._bilhete(row): _erro()
        return d, ref

    def iniciar_conferencia_rest(self, membro, ref, *, versao_drive):
        """Versão de plano recém-aberto pelo leitor confiável. Sem criar arquivo."""
        if not isinstance(versao_drive, str) or not re.fullmatch('[0-9]{1,30}', versao_drive): _erro()
        with self._transacao():
            contexto = self.contexto_conferencia_rest(membro, ref)
            row = self.db.execute('SELECT * FROM conferencias_rest WHERE servidor=? AND personagem=?',
                                  (ref.servidor, ref.personagem)).fetchone()
            if row and row['expira'] > self.agora():
                d, _ = self._abrir_conferencia(membro, row)
                if d['contexto'] != _hash([PROTOCOLO, contexto, d['operacao']]) or d['versao_drive'] != versao_drive: _erro()
                return self._bilhete(row)
            inicio = self.agora()
            operacao = secrets.token_hex(16)
            d = dict(protocolo=PROTOCOLO, contrato=CONTRATO_SHA256, operacao=operacao,
                     revisao=0, criado=inicio, expira=inicio + PRAZO, referencia=asdict(ref),
                     contexto=_hash([PROTOCOLO, contexto, operacao]), versao_drive=versao_drive, dominios=[])
            row = dict(servidor=ref.servidor, personagem=ref.personagem, ator=ref.ator, **d)
            envelope = self.cifra.cifrar(self._ctx_conferencia(row), d)
            self.db.execute('''INSERT INTO conferencias_rest VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(servidor,personagem) DO UPDATE SET ator=excluded.ator,operacao=excluded.operacao,
                revisao=excluded.revisao,criado=excluded.criado,expira=excluded.expira,conteudo=excluded.conteudo''',
                (ref.servidor, ref.personagem, ref.ator, d['operacao'], 0, inicio, d['expira'], envelope))
            return self._bilhete(row)

    def retomar_conferencia_rest(self, membro, personagem):
        """Não consulta Google. Reflete estado histórico; nunca é autorização de escrita."""
        with self._transacao():
            row = self.db.execute('SELECT * FROM conferencias_rest WHERE servidor=? AND personagem=?',
                                  (membro.servidor, personagem)).fetchone()
            self._abrir_conferencia(membro, row)
            return self._bilhete(row)

    def contexto_operacao_rest(self, membro, bilhete):
        with self._transacao():
            d, ref = self._conferencia(membro, bilhete)
            return ref, d['contexto'], d['versao_drive'], DOMINIOS[len(d['dominios']):]

    def gravar_conferencia_rest(self, membro, bilhete, conferencia):
        """Só objeto completo do auditor; não aceita um JSON/recibo enviado pelo cliente."""
        if type(conferencia) is not ConferenciaGrade: _erro()
        with self._transacao():
            d, ref = self._conferencia(membro, bilhete)
            i = len(d['dominios'])
            p = conferencia._plano
            if (i == len(DOMINIOS) or (p.arquivo, p.contexto, p.versao, p.dominio) !=
                    (ref.arquivo, d['contexto'], d['versao_drive'], DOMINIOS[i])): _erro()
            recibo = abrir_recibo(self.cifra, conferencia.recibo(self.cifra), contexto=d['contexto'],
                                 arquivo=ref.arquivo, dominio=DOMINIOS[i], versao_drive=d['versao_drive'])
            resultado = conferencia.publico()
            if _hash(resultado) != recibo['resultado']: _erro()
            d['dominios'].append(dict(recibo=recibo, resultado=resultado))
            d['revisao'] += 1
            envelope = self.cifra.cifrar(self._ctx_conferencia(dict(servidor=ref.servidor,
                personagem=ref.personagem, operacao=bilhete.operacao)), d)
            if len(envelope) > MAX_ESTADO: raise ErroCarteira('Conferência excede o limite de armazenamento.')
            n = self.db.execute('''UPDATE conferencias_rest SET revisao=?,conteudo=?
                WHERE servidor=? AND personagem=? AND operacao=? AND revisao=?''',
                (d['revisao'], envelope, ref.servidor, ref.personagem, bilhete.operacao, bilhete.revisao)).rowcount
            if n != 1: _erro()
            return BilheteConferencia(ref.servidor, ref.personagem, bilhete.operacao, d['revisao'])

    def resultado_conferencia_rest(self, membro, bilhete):
        with self._transacao():
            d, _ = self._conferencia(membro, bilhete)
            return dict(dominios_conferidos=len(d['dominios']), leitura_historica=True,
                        resultados=[x['resultado'] for x in d['dominios']], **FLAGS)

    def descartar_conferencia_rest(self, membro, bilhete):
        """Descarta só histórico local. Não limpa fonte, diário GS ou arquivo Google."""
        with self._transacao():
            if (type(bilhete) is not BilheteConferencia or bilhete.servidor != membro.servidor or
                    type(bilhete.revisao) is not int): _erro()
            self._personagem(membro, bilhete.personagem, Acao.VER_DETALHES)
            row = self.db.execute('SELECT * FROM conferencias_rest WHERE servidor=? AND personagem=?',
                                  (bilhete.servidor, bilhete.personagem)).fetchone()
            if row is None or bilhete != self._bilhete(row): _erro()
            d = self.cifra.abrir(self._ctx_conferencia(row), row['conteudo'])
            if row['ator'] != membro.usuario or d['referencia']['ator'] != membro.usuario:
                raise AcessoNegado('Conferência pertence a outra pessoa.')
            # Uma fonte/modelo alterado pode ser descartado explicitamente;
            # nenhum resultado antigo é adotado na operação seguinte.
            self.db.execute('DELETE FROM conferencias_rest WHERE servidor=? AND personagem=?',
                            (bilhete.servidor, bilhete.personagem))


async def conferir_dominio_persistido(dados, membro, bilhete, provedores, acesso, *,
                                     revalidar_contexto, aguardar_cota, agora=time.monotonic):
    """Adaptador interno de um domínio, compatível com o worker DadosAsync.

    Revalida banco/prazo também por GET e após a cota. O callback externo deve
    consultar membro/cargos atuais e obter contexto_operacao_rest com esse membro. O
    chamador renova OAuth e usa a fila; este método não oferece rota pública.
    Interrupção antes do commit conserva só os domínios anteriores completos.
    """
    import asyncio
    from .grade_inicializacao import LeitorGradeRest

    async def banco(metodo, *args):
        return await dados.chamar('cadastro.' + metodo, *args)

    ref, contexto, versao, restantes = await banco('contexto_operacao_rest', membro, bilhete)
    if not restantes: _erro()

    async def revalidar():
        atual = await revalidar_contexto()
        _, esperado, _, _ = await banco('contexto_operacao_rest', membro, bilhete)
        if atual != contexto or esperado != contexto: _erro()
        return contexto

    leitor = LeitorGradeRest(provedores, revalidar, aguardar_cota, agora=agora)
    plano = await leitor.abrir(acesso, ref.arquivo, restantes[0])
    if (plano.contexto, plano.versao) != (contexto, versao): _erro()
    conferencia = ConferenciaGrade(plano)
    for i in range(len(plano.faixas)):
        await banco('contexto_operacao_rest', membro, bilhete)
        pagina = await leitor.pagina(acesso, plano, i)
        await banco('contexto_operacao_rest', membro, bilhete)
        await asyncio.to_thread(conferencia.receber, i, pagina)
    await leitor.confirmar(acesso, plano)
    await asyncio.to_thread(conferencia.concluir)
    return await banco('gravar_conferencia_rest', membro, bilhete, conferencia)
