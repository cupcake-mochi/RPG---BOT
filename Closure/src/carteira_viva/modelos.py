"""Escolha do modelo por servidor. Nenhuma cópia ou escrita no Google.

ANALISE 12/R53 é compatibilidade de leitura, não um contrato de inicialização.
A criação fica fechada até o produtor comprovar limpeza e automações em cópias.
"""
import re

from closure_bot.recursos_publicos import FICHA_ERA_REVOLUCAO, FICHA_CICLO_MALDITO
from .permissoes import Acao
from .segredos import Conflito, ErroCarteira

OFICIAIS = (
    {"id": "era", "nome": "Era da Revolução", "url": FICHA_ERA_REVOLUCAO},
    {"id": "ciclo", "nome": "Ciclo Maldito", "url": FICHA_CICLO_MALDITO},
)
SINAIS = frozenset({"extrato_presente", "estado_salarial_presente", "emissao_presente", "salarios_presentes"})


class CriacaoBloqueada(ErroCarteira):
    codigo = "modelo_bloqueado"

    def __init__(self):
        super().__init__("Criação indisponível: inicialização limpa e automações ainda não comprovadas.")


def referencia_validada(previa):
    """Só recebe resultado do adaptador Google, nunca JSON do navegador."""
    if not isinstance(previa, dict):
        raise ErroCarteira("Modelo inválido.")
    campos = ("arquivo", "nome_arquivo", "versao_drive", "contrato", "revisao_livro")
    if any(not isinstance(previa.get(k), str) or not previa[k].strip() for k in campos):
        raise ErroCarteira("Modelo incompleto.")
    if (not re.fullmatch(r"[A-Za-z0-9_-]{20,200}", previa["arquivo"]) or
            len(previa["nome_arquivo"]) > 200 or not re.fullmatch(r"[0-9]{1,30}", previa["versao_drive"]) or
            previa["contrato"] != "analise-12" or previa["revisao_livro"] != "R53" or
            not isinstance(previa.get("sinais"), list) or any(x not in SINAIS for x in previa["sinais"])):
        raise ErroCarteira("Modelo incompatível.")
    return {**{k: previa[k] for k in campos}, "sinais": sorted(set(previa["sinais"]))}


class Modelos:
    def _modelo(self, servidor):
        row = self.db.execute("SELECT * FROM modelos_servidor WHERE servidor=?", (servidor,)).fetchone()
        if not row:
            return 0, {"escolha": "oficiais"}
        return row["revisao"], self.cifra.abrir(["modelo", servidor], row["conteudo"])

    def modelos(self, membro):
        self._membro(membro)
        revisao, d = self._modelo(membro.servidor)
        # O arquivo e o nome privado do modelo personalizado não saem para membros.
        return {"revisao": revisao, "escolha": d["escolha"], "oficiais": [dict(x) for x in OFICIAIS],
                "personalizado": d["escolha"] == "servidor", "criacao_disponivel": False,
                "motivo": "inicializacao_nao_comprovada", "parametros_suportados": []}

    def revisar_modelo(self, membro):
        self._autorizar(membro, Acao.CONFIGURAR)
        revisao, d = self._modelo(membro.servidor)
        return {"revisao": revisao, **d}

    def configurar_modelo(self, membro, *, escolha, revisao, previa=None):
        self._autorizar(membro, Acao.CONFIGURAR)
        if escolha not in ("oficiais", "era", "ciclo", "servidor") or type(revisao) is not int or revisao < 0:
            raise ErroCarteira("Escolha de modelo inválida.")
        d = {"escolha": escolha}
        if escolha == "servidor":
            d["referencia"] = referencia_validada(previa)
        elif previa is not None:
            raise ErroCarteira("Use o Picker para configurar um modelo personalizado.")
        with self._transacao():
            atual, _ = self._modelo(membro.servidor)
            if atual != revisao:
                raise Conflito("O modelo do servidor mudou. Abra uma nova solicitação.")
            self._servidor(membro.servidor)
            self.db.execute("""INSERT INTO modelos_servidor VALUES (?,?,?)
                ON CONFLICT(servidor) DO UPDATE SET revisao=excluded.revisao,conteudo=excluded.conteudo""",
                            (membro.servidor, revisao + 1, self.cifra.cifrar(["modelo", membro.servidor], d)))
            self._auditar(membro.servidor, membro.usuario, None, "configurar_modelo")
            return self.modelos(membro)

    def criar_por_modelo(self, membro, *, modelo, parametros=None):
        self._membro(membro)
        # Sem flag de ambiente ou parâmetro cliente para contornar esta barreira.
        # Nem ausência de sinais na sondagem permite copiar uma ficha.
        raise CriacaoBloqueada()
