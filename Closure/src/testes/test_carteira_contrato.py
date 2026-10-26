"""Etapa 1: contrato e fluxo simulados, sem rede ou credenciais reais."""
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

from cryptography.fernet import Fernet, InvalidToken

LAB = Path(__file__).resolve().parents[2] / "pesquisa"
sys.path.insert(0, str(LAB))
from carteira_viva.contrato import Acao, Membro, Permissoes, cartao_publico, permitido
from carteira_viva.prova_local import AutorizacaoGoogle, ArquivoGoogle, Prova, Recusa, Revogada
sys.path.remove(str(LAB))


class PermissoesTeste(unittest.TestCase):
    def setUp(self):
        self.dono = Membro("mesa-a", "jogador-a")
        self.outro = Membro("mesa-a", "jogador-b")
        self.roles = Permissoes(frozenset({"revisao"}), frozenset({"edicao"}))

    def pode(self, acao, membro, **kw):
        return permitido(acao, membro, "mesa-a", "jogador-a", self.roles, **kw)

    def test_cadastro_livre_e_cartao(self):
        self.assertTrue(self.pode(Acao.CADASTRAR, self.outro))
        self.assertTrue(self.pode(Acao.VER_CARTAO, self.outro))
        self.assertFalse(self.pode(Acao.ANALISAR, self.outro))

    def test_dono_acessa_sem_admin(self):
        for acao in (Acao.ANALISAR, Acao.VER_DETALHES, Acao.TROCAR_ARQUIVO, Acao.PERSONALIZAR):
            with self.subTest(acao=acao): self.assertTrue(self.pode(acao, self.dono))

    def test_admin_revisa_mas_nao_toma_posse(self):
        for admin in (replace(self.outro, administrador=True), replace(self.outro, dono_servidor=True)):
            with self.subTest(admin=admin):
                self.assertTrue(self.pode(Acao.CONFIGURAR, admin))
                self.assertTrue(self.pode(Acao.ANALISAR, admin))
                self.assertFalse(self.pode(Acao.TROCAR_ARQUIVO, admin))

    def test_gerenciar_servidor_e_lore_nao_abrem_privado(self):
        user = replace(self.outro, gerenciar_servidor=True, cargos=frozenset({"lore", "idioma"}))
        self.assertFalse(self.pode(Acao.VER_DETALHES, user))
        self.assertFalse(self.pode(Acao.CONFIGURAR, user))

    def test_revisao_nao_e_edicao(self):
        user = replace(self.outro, cargos=frozenset({"revisao"}))
        self.assertTrue(self.pode(Acao.ANALISAR, user))
        self.assertFalse(self.pode(Acao.EDITAR_JOGO, user,
                                  operacao_liberada=True, consentimento_edicao=True))

    def test_editor_precisa_operacao_e_consentimento(self):
        for user in (self.dono, replace(self.outro, administrador=True),
                     replace(self.outro, cargos=frozenset({"edicao"}))):
            with self.subTest(user=user):
                self.assertFalse(self.pode(Acao.EDITAR_JOGO, user))
                self.assertFalse(self.pode(Acao.EDITAR_JOGO, user, operacao_liberada=True))
                self.assertTrue(self.pode(Acao.EDITAR_JOGO, user,
                                         operacao_liberada=True, consentimento_edicao=True))

    def test_sem_membro_ou_outro_servidor_recusa_tudo(self):
        for user in (replace(self.dono, presente=False, administrador=True),
                     replace(self.dono, servidor="mesa-b", administrador=True)):
            for acao in Acao:
                with self.subTest(user=user, acao=acao): self.assertFalse(self.pode(acao, user))

    def test_remocao_de_cargo_revoga_acesso(self):
        user = replace(self.outro, cargos=frozenset({"revisao"}))
        self.assertTrue(self.pode(Acao.ANALISAR, user))
        self.assertFalse(self.pode(Acao.ANALISAR, replace(user, cargos=frozenset())))

    def test_dto_publico_nao_vaza_snapshot_ou_link(self):
        perfil = {"nome": "Teste", "idade": 0, "frase": "", "snapshot": {"segredo": 1},
                  "google_url": "privado", "refresh_token": "segredo", "cor": None}
        self.assertEqual(cartao_publico(perfil, frozenset(perfil)),
                         {"nome": "Teste", "idade": 0, "frase": "", "cor": None})
        self.assertEqual(cartao_publico(perfil, frozenset()), {})


class FluxoTeste(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "somente-teste.sqlite3"
        self.key = Fernet.generate_key()
        self.clock = [1000.0]
        self.prova = Prova(self.path, self.key, lambda: self.clock[0])
        self.user = Membro("mesa-a", "jogador-a")
        self.auth = AutorizacaoGoogle("conta-ficticia-a", "refresh-ficticio-secreto")
        self.file = ArquivoGoogle("arquivo-ficticio-a", self.auth.conta)
        self.session = "sessao-ficticia-a"

    def tearDown(self):
        self.prova.fechar()
        self.temp.cleanup()

    def preparar(self, arquivo=None, personagem=None, user=None):
        user = user or self.user
        estado = self.prova.iniciar(user, personagem)
        self.prova.identificar_discord(estado, user, self.session)
        self.prova.receber_google(estado, user, self.session, self.auth)
        self.prova.selecionar(estado, user, self.session, arquivo or self.file)
        return estado

    def cadastrar(self, arquivo=None, user=None):
        return self.prova.confirmar(self.preparar(arquivo, user=user), user or self.user, self.session)

    def test_cadastro_e_dois_personagens(self):
        a = self.cadastrar()
        b = self.cadastrar(replace(self.file, arquivo="arquivo-b"))
        self.assertNotEqual(a["personagem"], b["personagem"])
        self.assertEqual(a["dono"], b["dono"])

    def test_outra_identidade_discord(self):
        s = self.prova.iniciar(self.user)
        with self.assertRaises(Recusa):
            self.prova.identificar_discord(s, replace(self.user, usuario="outro"), self.session)

    def test_outro_servidor(self):
        s = self.prova.iniciar(self.user)
        with self.assertRaises(Recusa):
            self.prova.identificar_discord(s, replace(self.user, servidor="outra"), self.session)

    def test_callback_google_sem_discord(self):
        s = self.prova.iniciar(self.user)
        with self.assertRaises(Recusa):
            self.prova.receber_google(s, self.user, self.session, self.auth)

    def test_callback_google_de_outra_sessao(self):
        s = self.prova.iniciar(self.user)
        self.prova.identificar_discord(s, self.user, self.session)
        with self.assertRaises(Recusa):
            self.prova.receber_google(s, self.user, "outra-sessao", self.auth)

    def test_expiracao(self):
        s = self.prova.iniciar(self.user)
        self.clock[0] += 600
        with self.assertRaises(Recusa): self.prova.identificar_discord(s, self.user, self.session)

    def test_callback_google_repetido(self):
        s = self.preparar()
        with self.assertRaises(Recusa): self.prova.receber_google(s, self.user, self.session, self.auth)

    def test_confirmacao_repetida(self):
        s = self.preparar()
        self.prova.confirmar(s, self.user, self.session)
        with self.assertRaises(Recusa): self.prova.confirmar(s, self.user, self.session)

    def test_escopo_amplo_e_token_ausente(self):
        for auth in (replace(self.auth, escopos=frozenset({"drive"})),
                     replace(self.auth, refresh_token="")):
            with self.subTest(auth=auth):
                s = self.prova.iniciar(self.user)
                self.prova.identificar_discord(s, self.user, self.session)
                with self.assertRaises(Recusa): self.prova.receber_google(s, self.user, self.session, auth)

    def test_picker_nao_basta_para_provar_acesso(self):
        for arquivo in (replace(self.file, autorizado_app=False), replace(self.file, lixeira=True),
                        replace(self.file, mime="application/pdf"), replace(self.file, conta="outra"),
                        replace(self.file, contrato_compativel=False)):
            with self.subTest(arquivo=arquivo):
                with self.assertRaises(Recusa): self.preparar(arquivo)

    def test_cancelamento_nao_cria_vinculo(self):
        s = self.preparar()
        self.prova.cancelar(s, self.user, self.session)
        with self.assertRaises(Recusa): self.prova.confirmar(s, self.user, self.session)
        self.assertEqual(self.prova.db.execute("SELECT count(*) FROM vinculos").fetchone()[0], 0)

    def test_sem_membro_na_confirmacao(self):
        s = self.preparar()
        with self.assertRaises(Recusa):
            self.prova.confirmar(s, replace(self.user, presente=False), self.session)

    def test_duplicata_nao_toma_dono(self):
        a = self.cadastrar()
        other = replace(self.user, usuario="outro")
        s = self.preparar(user=other)
        with self.assertRaises(Recusa): self.prova.confirmar(s, other, self.session)
        self.assertEqual(self.prova.vinculo(self.user.servidor, a["personagem"])["dono"], self.user.usuario)

    def test_mesmo_arquivo_outro_servidor_isolado(self):
        a = self.cadastrar()
        other = replace(self.user, servidor="mesa-b")
        b = self.cadastrar(user=other)
        self.assertNotEqual(a["personagem"], b["personagem"])
        self.assertIsNone(self.prova.vinculo(self.user.servidor, b["personagem"]))

    def test_troca_preserva_id_incrementa_revisao(self):
        a = self.cadastrar()
        s = self.preparar(replace(self.file, arquivo="nova"), a["personagem"])
        b = self.prova.confirmar(s, self.user, self.session)
        self.assertEqual(a["personagem"], b["personagem"])
        self.assertEqual(b["revisao"], 2)
        self.assertEqual(b["arquivo"], "nova")

    def test_troca_invalida_preserva_original(self):
        a = self.cadastrar()
        with self.assertRaises(Recusa):
            self.preparar(replace(self.file, autorizado_app=False), a["personagem"])
        self.assertEqual(self.prova.vinculo(self.user.servidor, a["personagem"]), a)

    def test_conflito_no_commit_da_troca_preserva_os_dois_cadastros(self):
        a = self.cadastrar()
        b = self.cadastrar(replace(self.file, arquivo="ocupado"))
        s = self.preparar(replace(self.file, arquivo="ocupado"), a["personagem"])
        with self.assertRaises(Recusa): self.prova.confirmar(s, self.user, self.session)
        self.assertEqual(self.prova.vinculo(self.user.servidor, a["personagem"]), a)
        self.assertEqual(self.prova.vinculo(self.user.servidor, b["personagem"]), b)

    def test_estado_e_sessao_nao_sao_guardados_em_texto(self):
        s = self.preparar()
        row = dict(self.prova.db.execute("SELECT * FROM fluxos").fetchone())
        self.assertNotIn(s, str(row))
        self.assertNotIn(self.session, str(row))
        self.assertNotIn(self.auth.refresh_token, str(row))

    def test_leitura_alheia_recusa_antes_de_chamar_provedor(self):
        a = self.cadastrar()
        with self.assertRaises(Recusa):
            self.prova.ler(replace(self.user, usuario="outro"), a["personagem"],
                           lambda _: self.fail("Não renovar"), lambda *_: self.fail("Não ler"))

    def test_troca_concorrente_detecta_revisao(self):
        a = self.cadastrar()
        s1 = self.preparar(replace(self.file, arquivo="nova1"), a["personagem"])
        s2 = self.preparar(replace(self.file, arquivo="nova2"), a["personagem"])
        self.prova.confirmar(s1, self.user, self.session)
        with self.assertRaises(Recusa): self.prova.confirmar(s2, self.user, self.session)
        self.assertEqual(self.prova.vinculo(self.user.servidor, a["personagem"])["arquivo"], "nova1")

    def test_troca_arquivo_nao_troca_conta(self):
        a = self.cadastrar()
        s = self.prova.iniciar(self.user, a["personagem"])
        self.prova.identificar_discord(s, self.user, self.session)
        with self.assertRaises(Recusa):
            self.prova.receber_google(s, self.user, self.session, replace(self.auth, conta="outra"))

    def test_troca_arquivo_alheio_recusa(self):
        a = self.cadastrar()
        with self.assertRaises(Recusa):
            self.prova.iniciar(replace(self.user, usuario="outro", administrador=True), a["personagem"])

    def test_persistencia_cifrada_e_leitura_apos_reinicio(self):
        a = self.cadastrar()
        self.prova.fechar()
        self.assertNotIn(self.auth.refresh_token.encode(), self.path.read_bytes())
        self.assertNotIn(self.auth.refresh_token, repr(self.auth))
        self.prova = Prova(self.path, self.key, lambda: self.clock[0])
        calls = []
        def renovar(token):
            self.assertEqual(token, self.auth.refresh_token)
            calls.append("renovou")
            return "access-ficticio"
        def ler(token, arquivo, faixa):
            self.assertEqual((token, arquivo, faixa), ("access-ficticio", self.file.arquivo, "ANALISE!A1:B3"))
            return [["vida", 0], ["vazio", ""], ["ausente"]]
        result = self.prova.ler(self.user, a["personagem"], renovar, ler)
        self.assertEqual(calls, ["renovou"])
        self.assertEqual(result["dados"], [["vida", 0], ["vazio", ""], ["ausente"]])

    def test_reinicio_invalida_operacao_incompleta(self):
        s = self.preparar()
        self.prova.fechar()
        self.prova = Prova(self.path, self.key, lambda: self.clock[0])
        with self.assertRaises(Recusa): self.prova.confirmar(s, self.user, self.session)

    def test_revogacao_exige_reconexao(self):
        a = self.cadastrar()
        def renovar(_): raise Revogada()
        with self.assertRaisesRegex(Recusa, "Reconecte"):
            self.prova.ler(self.user, a["personagem"], renovar, lambda *_: self.fail("Não deveria ler"))
        self.assertEqual(self.prova.vinculo(self.user.servidor, a["personagem"])["ativo"], 0)
        s = self.preparar(personagem=a["personagem"])
        self.assertEqual(self.prova.confirmar(s, self.user, self.session)["ativo"], 1)

    def test_falha_transitoria_nao_revoga(self):
        a = self.cadastrar()
        def renovar(_): raise TimeoutError()
        with self.assertRaises(TimeoutError): self.prova.ler(self.user, a["personagem"], renovar, lambda *_: [])
        self.assertEqual(self.prova.vinculo(self.user.servidor, a["personagem"])["ativo"], 1)

    def test_revogacao_afeta_vinculos_da_mesma_conexao_sem_afetar_outro_dono(self):
        a = self.cadastrar()
        b = self.cadastrar(user=replace(self.user, servidor="mesa-b"))
        c = self.cadastrar(replace(self.file, arquivo="outro-arquivo"),
                           replace(self.user, usuario="outro-dono"))
        def renovar(_): raise Revogada()
        with self.assertRaises(Recusa):
            self.prova.ler(self.user, a["personagem"], renovar, lambda *_: [])
        self.assertEqual(self.prova.vinculo("mesa-b", b["personagem"])["ativo"], 0)
        self.assertEqual(self.prova.vinculo("mesa-a", c["personagem"])["ativo"], 1)

    def test_leitura_em_voo_descarta_fonte_antiga(self):
        a = self.cadastrar()
        def ler(*_):
            s = self.preparar(replace(self.file, arquivo="nova"), a["personagem"])
            self.prova.confirmar(s, self.user, self.session)
            return [["dados-antigos"]]
        with self.assertRaisesRegex(Recusa, "fonte mudou"):
            self.prova.ler(self.user, a["personagem"], lambda _: "fake", ler)

    def test_envelope_de_outro_contexto_recusado(self):
        a = self.cadastrar()
        b = self.cadastrar(replace(self.file, arquivo="b"), replace(self.user, usuario="outro"))
        self.prova.db.execute("""UPDATE vinculos SET segredo=(SELECT segredo FROM vinculos WHERE personagem=?)
            WHERE personagem=?""", (b["personagem"], a["personagem"]))
        with self.assertRaises(Recusa):
            self.prova.ler(self.user, a["personagem"], lambda _: self.fail("Não renovar"), lambda *_: [])

    def test_chave_incorreta_nao_decripta(self):
        a = self.cadastrar()
        self.prova.cifra = Fernet(Fernet.generate_key())
        with self.assertRaises(InvalidToken):
            self.prova.ler(self.user, a["personagem"], lambda _: self.fail("Não renovar"), lambda *_: [])


if __name__ == "__main__":
    unittest.main()
