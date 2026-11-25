"""Autorização e registro do preenchimento. Nenhum conteúdo da ficha é guardado aqui."""
from .permissoes import Acao
from .segredos import Conflito, ErroCarteira


class BancoPreencher:
    def contexto_preencher(self, membro, personagem):
        """Referência da fonte atual, sem tomar a vez de uma leitura em andamento."""
        from .banco import ReferenciaLeitura
        self._personagem(membro, personagem, Acao.PREENCHER)
        f = self._fonte(membro.servidor, personagem)
        if f["estado"] != "ativa":
            raise ErroCarteira("Reconecte a conta Google para preencher a ficha.")
        return ReferenciaLeitura(membro.servidor, personagem, membro.usuario,
                                 f["revisao"], f["geracao"], f["arquivo"], f["conexao"])

    def conferir_preencher(self, membro, ref):
        atual = self.contexto_preencher(membro, ref.personagem)
        if (membro.servidor, membro.usuario, atual.revisao, atual.arquivo, atual.conexao) != (
                ref.servidor, ref.ator, ref.revisao, ref.arquivo, ref.conexao):
            raise Conflito("A fonte mudou. Abra o preenchimento de novo.")

    def marcar_preenchimento(self, membro, ref, passo=None):
        """O que foi lido antes da escrita deixa de valer, inclusive leitura em andamento."""
        with self._transacao():
            self.conferir_preencher(membro, ref)
            if passo is not None:
                self._auditar(membro.servidor, membro.usuario, ref.personagem, "preencher_" + passo)
            onde = (ref.servidor, ref.personagem)
            self.db.execute("UPDATE fontes SET geracao=geracao+1 WHERE servidor=? AND personagem=?", onde)
            self.db.execute("DELETE FROM leituras WHERE servidor=? AND personagem=?", onde)
            self.db.execute("DELETE FROM analises WHERE servidor=? AND personagem=?", onde)
