"""Cadastro definitivo: somente dados fictícios, sem rede ou bot conectado."""
from dataclasses import replace
import os
import shutil
import struct
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet

from carteira_viva import esquema
from carteira_viva.backup import MAGIC, gravar_backup, limpar_backups, restaurar_backup, restaurar_remocoes
from carteira_viva.banco import Cadastro, DIA, MAX_JSON
from carteira_viva.permissoes import Membro, PUBLICOS
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira


class Fixtures:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = Path(self.tmp.name)
        self.path = self.pasta / "cadastro.sqlite3"
        self.chave = Fernet.generate_key()
        self.clock = [180000.0]
        self.agora = lambda: self.clock[0]
        self.c = Cadastro(self.path, (self.chave,), agora=self.agora)
        self.m = Membro("mesa-a", "jogador-a")
        self.outro = replace(self.m, usuario="jogador-b")
        self.admin = replace(self.outro, administrador=True)
        self.contador = 0

    def tearDown(self):
        self.c.fechar()
        self.tmp.cleanup()

    def pedido(self):
        self.contador += 1
        return f"pedido-ficticio-{self.contador}"

    def conectar(self, membro=None, **kw):
        return self.c.conectar(membro or self.m, conta=kw.get("conta", "conta-ficticia"),
                               cliente=kw.get("cliente", "cliente-ficticio"),
                               refresh_token=kw.get("refresh", "refresh-ficticio-secreto"))

    def autorizacao(self, cid):
        return self.c.db.execute("SELECT autorizacao FROM conexoes WHERE id=?", (cid,)).fetchone()[0]

    def revogar(self, cid):
        return self.c.marcar_revogada(cid, autorizacao=self.autorizacao(cid))

    def criar(self, membro=None, arquivo=None, conexao=None):
        membro = membro or self.m
        return self.c.cadastrar(membro, conexao=conexao or self.conectar(membro),
                                arquivo=arquivo or self.pedido(), nome="Personagem fictício",
                                contrato="r53-v12", responsabilidade=True, pedido=self.pedido())

    def leitura(self, p, campos=None, membro=None):
        membro = membro or self.m
        ref = self.c.reservar_leitura(membro, p["id"])
        return self.c.gravar_leitura(membro, ref, campos=campos or {"vida": 12}, schema="analise12")

    def analise(self, p, lid=None):
        self.c.gravar_analise(self.m, p["id"], leitura_id=lid or self.leitura(p),
                             campanha_revisao="campanha-ficticia-1", resultado={"erros": [], "pendencias": ["Exemplo"]})

    def reabrir(self, chaves=None):
        self.c.fechar()
        self.c = Cadastro(self.path, chaves or (self.chave,), agora=self.agora)


class BancoTeste(Fixtures, unittest.TestCase):
    def test_flags_de_permissao_nao_aceitam_texto_ou_numeros(self):
        for campo in ("presente", "administrador", "dono_servidor", "gerenciar_servidor"):
            for valor in ("false", 1, None):
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    replace(self.m, **{campo: valor})

    def test_multiplos_personagens_por_jogador_e_servidor(self):
        a, b = self.criar(), self.criar()
        outro_servidor = replace(self.m, servidor="mesa-b")
        c = self.criar(outro_servidor)
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(len(self.c.listar(self.m)), 2)
        self.assertEqual(self.c.listar(outro_servidor)[0]["id"], c["id"])
        self.assertEqual(self.c.listar(self.outro), [])

    def test_galeria_de_outro_jogador_e_paginacao(self):
        for _ in range(5): self.criar()
        primeira = self.c.listar(self.outro, dono=self.m.usuario, limite=2)
        segunda = self.c.listar(self.outro, dono=self.m.usuario, depois=primeira[-1]["id"], limite=2)
        self.assertEqual(len(primeira), 2)
        self.assertFalse({p["id"] for p in primeira} & {p["id"] for p in segunda})
        for n in (0, 51, True):
            with self.subTest(n=n), self.assertRaises(ErroCarteira): self.c.listar(self.m, limite=n)

    def test_id_alheio_nao_expoe_outro_servidor(self):
        p = self.criar()
        m = replace(self.m, servidor="mesa-b", administrador=True)
        for func in (self.c.cartao, self.c.detalhes, self.c.reservar_leitura):
            with self.subTest(func=func), self.assertRaises(AcessoNegado): func(m, p["id"])

    def test_membro_ausente_recusado(self):
        p = self.criar()
        ausente = replace(self.m, presente=False)
        with self.assertRaises(AcessoNegado): self.c.listar(ausente)
        with self.assertRaises(AcessoNegado): self.c.cartao(ausente, p["id"])

    def test_conexao_normalizada_entre_personagens_e_servidores(self):
        cid = self.conectar()
        self.criar(conexao=cid)
        self.criar(replace(self.m, servidor="mesa-b"), conexao=cid)
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM conexoes").fetchone()[0], 1)
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM fontes").fetchone()[0], 2)

    def test_conexao_de_outro_usuario_nao_cadastra(self):
        cid = self.conectar()
        with self.assertRaises(AcessoNegado):
            self.c.cadastrar(self.outro, conexao=cid, arquivo="falso", nome="Falso", contrato="r53",
                              responsabilidade=True, pedido=self.pedido())
        self.assertFalse(self.c.listar(self.outro))

    def test_exige_declaracao_de_responsabilidade(self):
        cid = self.conectar()
        with self.assertRaises(ErroCarteira):
            self.c.cadastrar(self.m, conexao=cid, arquivo="a", nome="A", contrato="r53",
                              responsabilidade=False, pedido=self.pedido())
        self.assertFalse(self.c.listar(self.m))

    def test_cadastro_repetido_e_chave_reutilizada(self):
        cid = self.conectar()
        kw = dict(conexao=cid, arquivo="arquivo-a", nome="A", contrato="r53", responsabilidade=True, pedido="mesmo-pedido")
        a = self.c.cadastrar(self.m, **kw)
        self.assertEqual(self.c.cadastrar(self.m, **kw), a)
        with self.assertRaises(Conflito): self.c.cadastrar(self.m, **{**kw, "nome": "B"})
        self.assertEqual(len(self.c.listar(self.m)), 1)

    def test_arquivo_duplicado_nao_toma_posse_e_outro_servidor_independente(self):
        a = self.criar(arquivo="arquivo-igual")
        with self.assertRaises(Conflito): self.criar(self.outro, arquivo="arquivo-igual")
        b = self.criar(replace(self.m, servidor="mesa-b"), arquivo="arquivo-igual")
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(self.c.cartao(self.m, a["id"])["responsavel"], self.m.usuario)

    def test_admin_e_dono_revisam_sem_tomar_posse(self):
        p = self.criar()
        for m in (self.admin, replace(self.outro, dono_servidor=True)):
            with self.subTest(m=m):
                self.assertEqual(self.c.detalhes(m, p["id"])["cartao"]["id"], p["id"])
                with self.assertRaises(AcessoNegado): self.c.excluir(m, p["id"], pedido=self.pedido())

    def test_cargos_de_revisao_configurados_na_hora_e_sem_heranca(self):
        p = self.criar()
        lore = replace(self.outro, gerenciar_servidor=True, cargos=frozenset({"lore"}))
        with self.assertRaises(AcessoNegado): self.c.detalhes(lore, p["id"])
        with self.assertRaises(AcessoNegado): self.c.configurar(lore, revisores=("lore",))
        self.c.configurar(self.admin, revisores=("revisor",), editores=("editor",))
        revisor = replace(self.outro, cargos=frozenset({"revisor"}))
        self.assertIsNotNone(self.c.detalhes(revisor, p["id"]))
        with self.assertRaises(AcessoNegado): self.c.detalhes(replace(self.outro, cargos=frozenset({"editor"})), p["id"])
        self.c.configurar(self.admin, revisores=())
        with self.assertRaises(AcessoNegado): self.c.detalhes(revisor, p["id"])

    def test_revisor_nao_personaliza_nem_troca_arquivo(self):
        p = self.criar()
        self.c.configurar(self.admin, revisores=("revisor",))
        r = replace(self.outro, cargos=frozenset({"revisor"}))
        with self.assertRaises(AcessoNegado):
            self.c.personalizar(r, p["id"], perfil={"nome": "Invadido"}, campos_publicos={"nome"})
        with self.assertRaises(AcessoNegado):
            self.c.trocar_arquivo(r, p["id"], arquivo="outro", conexao=self.conectar(r), contrato="r53", revisao=1, pedido=self.pedido())

    def test_perfil_filtro_duplo_e_sem_dados_privados_no_cartao(self):
        p = self.criar()
        self.leitura(p, {"segredo_mecanico": 99})
        self.c.personalizar(self.m, p["id"], perfil={"nome": "Teste", "idade": 0, "cla": "Clã fictício", "cor": 0},
                            campos_publicos={"nome", "idade", "cla", "cor"})
        self.c.configurar(self.admin, campos_publicos={"nome", "idade", "cor"})
        card = self.c.cartao(self.outro, p["id"])
        self.assertEqual(card["perfil"], {"nome": "Teste", "idade": 0, "cor": 0})
        for campo in ("arquivo", "conexao", "conta", "refresh", "leitura", "analise"):
            self.assertNotIn(campo, card)
        self.assertNotIn("segredo_mecanico", str(card))
        with self.assertRaises(ErroCarteira):
            self.c.personalizar(self.m, p["id"], perfil={"nome": "A", "google_url": "privado"}, campos_publicos={"nome"})

    def test_cor_e_campos_invalidos_recusados(self):
        p = self.criar()
        for perfil in ({"nome": "A", "cor": True}, {"nome": "A", "cor": 0x1000000},
                       {"nome": "A", "idade": -1}, {"nome": ""}):
            with self.subTest(perfil=perfil), self.assertRaises(ErroCarteira):
                self.c.personalizar(self.m, p["id"], perfil=perfil, campos_publicos={"nome"})

    def test_privado_nao_vaza_credenciais(self):
        p = self.criar()
        details = self.c.detalhes(self.m, p["id"])
        self.assertNotIn("refresh-ficticio-secreto", str(details))
        ref = self.c.reservar_leitura(self.m, p["id"])
        segredo = self.c._credencial(self.m, ref)
        self.assertEqual(segredo.refresh_token, "refresh-ficticio-secreto")
        self.assertNotIn("refresh-ficticio-secreto", repr(segredo))

    def test_renovacao_sem_token_conserva_so_identidade_correta(self):
        cid = self.conectar()
        self.assertEqual(self.conectar(refresh=None), cid)
        for kw in ({"conta": "outra"}, {"cliente": "outro"}):
            with self.subTest(kw=kw), self.assertRaises(ErroCarteira): self.conectar(refresh=None, **kw)
        self.revogar(cid)
        with self.assertRaises(ErroCarteira): self.conectar(refresh=None)

    def test_revogacao_global_e_reconexao(self):
        cid = self.conectar()
        a = self.criar(conexao=cid)
        outra_mesa = replace(self.m, servidor="mesa-b")
        b = self.criar(outra_mesa, conexao=cid)
        c = self.criar(self.outro)
        self.leitura(a)
        self.revogar(cid)
        for m, p in ((self.m, a), (outra_mesa, b)):
            with self.subTest(m=m), self.assertRaises(ErroCarteira): self.c.detalhes(m, p["id"])
        self.assertIsNotNone(self.c.detalhes(self.outro, c["id"]))
        self.assertEqual(self.conectar(refresh="novo-refresh"), cid)
        self.assertIsNone(self.c.detalhes(self.m, a["id"])["leitura"])

    def test_desconectar_nao_apaga_personagens_ou_outro_dono(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        with self.assertRaises(AcessoNegado): self.c.desconectar(self.admin, cid)
        self.c.desconectar(self.m, cid)
        self.assertEqual(len(self.c.listar(self.m)), 1)
        with self.assertRaises(ErroCarteira): self.c.detalhes(self.m, p["id"])
        self.assertIsNone(self.c.db.execute("SELECT segredo FROM conexoes WHERE id=?", (cid,)).fetchone()[0])

    def test_resposta_revogada_antiga_nao_derruba_nova_autorizacao(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        antiga = self.autorizacao(cid)
        self.conectar(refresh="refresh-novo")
        self.assertFalse(self.c.marcar_revogada(cid, autorizacao=antiga))
        self.assertIsNotNone(self.c.detalhes(self.m, p["id"]))

    def test_leitura_anterior_a_revogacao_nao_grava_apos_reconexao(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        ref = self.c.reservar_leitura(self.m, p["id"])
        self.revogar(cid)
        self.conectar(refresh="refresh-novo")
        with self.assertRaises(Conflito): self.c.gravar_leitura(self.m, ref, campos={"velho": 1}, schema="r53")

    def test_troca_preserva_perfil_e_torna_analise_antiga(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        self.analise(p)
        args = dict(arquivo="arquivo-novo", conexao=cid, contrato="r53-v12", revisao=1, pedido="troca")
        self.c.trocar_arquivo(self.m, p["id"], **args)
        self.c.trocar_arquivo(self.m, p["id"], **args)
        d = self.c.detalhes(self.m, p["id"])
        self.assertEqual(d["revisao"], 2)
        self.assertEqual(d["cartao"]["perfil"], p["perfil"])
        self.assertIsNone(d["leitura"])
        self.assertFalse(d["analise"]["fonte_atual"])

    def test_troca_conflitante_preserva_fonte_anterior(self):
        cid = self.conectar()
        a, b = self.criar(conexao=cid), self.criar(arquivo="ocupado", conexao=cid)
        antes = self.c.detalhes(self.m, a["id"])
        with self.assertRaises(Conflito):
            self.c.trocar_arquivo(self.m, a["id"], arquivo="ocupado", conexao=cid, contrato="r53", revisao=1, pedido=self.pedido())
        self.assertEqual(self.c.detalhes(self.m, a["id"]), antes)
        self.assertIsNotNone(self.c.cartao(self.m, b["id"]))

    def test_troca_de_conta_e_revisao_vencida_recusadas(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        novo = self.conectar(conta="outra-conta")
        with self.assertRaises(ErroCarteira):
            self.c.trocar_arquivo(self.m, p["id"], arquivo="novo", conexao=novo, contrato="r53", revisao=1, pedido=self.pedido())
        self.c.trocar_arquivo(self.m, p["id"], arquivo="novo", conexao=cid, contrato="r53", revisao=1, pedido=self.pedido())
        with self.assertRaises(Conflito):
            self.c.trocar_arquivo(self.m, p["id"], arquivo="velho", conexao=cid, contrato="r53", revisao=1, pedido=self.pedido())

    def test_leitura_antiga_apos_troca_nao_grava(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        ref = self.c.reservar_leitura(self.m, p["id"])
        self.c.trocar_arquivo(self.m, p["id"], arquivo="novo", conexao=cid, contrato="r53", revisao=1, pedido=self.pedido())
        with self.assertRaises(Conflito): self.c.gravar_leitura(self.m, ref, campos={"vida": 99}, schema="r53")
        self.assertIsNone(self.c.detalhes(self.m, p["id"])["leitura"])

    def test_leituras_concorrentes_e_ticket_consumido(self):
        p = self.criar()
        a = self.c.reservar_leitura(self.m, p["id"])
        b = self.c.reservar_leitura(self.m, p["id"])
        with self.assertRaises(Conflito): self.c.gravar_leitura(self.m, a, campos={"antigo": 1}, schema="r53")
        self.c.gravar_leitura(self.m, b, campos={"novo": 1}, schema="r53")
        with self.assertRaises(Conflito): self.c.gravar_leitura(self.m, b, campos={"repetido": 1}, schema="r53")

    def test_leitura_preserva_zero_vazio_ausente_e_revalida_ator(self):
        p = self.criar()
        ref = self.c.reservar_leitura(self.m, p["id"])
        with self.assertRaises(AcessoNegado): self.c.gravar_leitura(self.outro, ref, campos={}, schema="r53")
        campos = {"zero": 0, "vazio": "", "nulo": None}
        self.c.gravar_leitura(self.m, ref, campos=campos, schema="r53")
        d = self.c.detalhes(self.m, p["id"])
        self.assertEqual(d["leitura"]["campos"], campos)
        self.assertNotIn("ausente", d["leitura"]["campos"])

    def test_perda_de_cargo_entre_reserva_e_gravacao(self):
        p = self.criar()
        self.c.configurar(self.admin, revisores=("revisor",))
        membro = replace(self.outro, cargos=frozenset({"revisor"}))
        ref = self.c.reservar_leitura(membro, p["id"])
        self.c.configurar(self.admin, revisores=())
        with self.assertRaises(AcessoNegado): self.c.gravar_leitura(membro, ref, campos={}, schema="r53")

    def test_analise_da_leitura_antiga_recusada(self):
        p = self.criar()
        lid = self.leitura(p)
        self.leitura(p, {"vida": 20})
        with self.assertRaises(Conflito): self.analise(p, lid)

    def test_cache_e_retencao_da_analise(self):
        p = self.criar()
        self.analise(p)
        self.clock[0] += 61
        self.assertFalse(self.c.detalhes(self.m, p["id"])["leitura"]["fresca"])
        self.clock[0] += DIA
        d = self.c.detalhes(self.m, p["id"])
        self.assertIsNone(d["leitura"])
        self.assertFalse(d["analise"]["fonte_atual"])
        self.clock[0] += 7 * DIA
        self.assertIsNone(self.c.detalhes(self.m, p["id"])["analise"])
        self.c.limpar()
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM leituras").fetchone()[0], 0)
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM analises").fetchone()[0], 0)

    def test_json_invalido_e_tamanho_recusados_sem_gravar(self):
        p = self.criar()
        ref = self.c.reservar_leitura(self.m, p["id"])
        for campos in ({"n": float("nan")}, {"grande": "x" * MAX_JSON}):
            with self.subTest(tamanho=len(str(campos))), self.assertRaises(ErroCarteira):
                self.c.gravar_leitura(self.m, ref, campos=campos, schema="r53")
        self.assertIsNone(self.c.detalhes(self.m, p["id"])["leitura"])

    def test_exclusao_imediata_repetivel_e_sem_apagar_outro(self):
        cid = self.conectar()
        a, b = self.criar(conexao=cid), self.criar(conexao=cid)
        self.analise(a)
        self.c.excluir(self.m, a["id"], pedido="remover-a")
        self.c.excluir(self.m, a["id"], pedido="remover-a")
        self.assertEqual(len(self.c.listar(self.m)), 1)
        self.assertIsNotNone(self.c.detalhes(self.m, b["id"]))
        with self.assertRaises(AcessoNegado): self.c.cartao(self.m, a["id"])
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM leituras").fetchone()[0], 0)
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM remocoes.exclusoes").fetchone()[0], 1)

    def test_falha_de_exclusao_reverte_tambem_registro_de_remocoes(self):
        p = self.criar()
        self.c.db.execute("""CREATE TRIGGER simular_falha BEFORE DELETE ON personagens
            BEGIN SELECT RAISE(ABORT,'falha-sintetica'); END""")
        with self.assertRaises(sqlite3.IntegrityError): self.c.excluir(self.m, p["id"], pedido="falha")
        self.assertIsNotNone(self.c.cartao(self.m, p["id"]))
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM remocoes.exclusoes").fetchone()[0], 0)

    def test_saida_retorno_e_expiracao(self):
        p = self.criar()
        self.c.registrar_saida(self.m.servidor, self.m.usuario)
        self.assertFalse(self.c.listar(self.outro, dono=self.m.usuario))
        with self.assertRaises(AcessoNegado): self.c.detalhes(self.admin, p["id"])
        self.clock[0] += 29 * DIA
        self.c.registrar_retorno(self.m)
        self.assertTrue(self.c.listar(self.m))
        self.c.registrar_saida(self.m.servidor, self.m.usuario)
        self.clock[0] += 30 * DIA
        self.c.registrar_retorno(self.m)
        self.assertFalse(self.c.listar(self.m))

    def test_limpeza_remove_ausentes_orfaos_pedidos_e_auditoria(self):
        p = self.criar()
        self.c.registrar_saida(self.m.servidor, self.m.usuario)
        self.clock[0] += 30 * DIA
        self.assertEqual(self.c.limpar()["personagens"], 1)
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM conexoes").fetchone()[0], 1)
        self.clock[0] += DIA
        self.assertEqual(self.c.limpar()["conexoes"], 1)
        self.clock[0] += 91 * DIA
        self.c.limpar()
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM pedidos").fetchone()[0], 0)
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM auditoria").fetchone()[0], 0)

    def test_apagar_usuario_abrange_servidores_e_nao_outros_donos(self):
        self.criar()
        self.criar(replace(self.m, servidor="mesa-b"))
        outro = self.criar(self.outro)
        self.c.apagar_usuario(self.m.usuario)
        self.assertFalse(self.c.listar(self.m))
        self.assertFalse(self.c.listar(replace(self.m, servidor="mesa-b")))
        self.assertIsNotNone(self.c.cartao(self.outro, outro["id"]))
        self.assertEqual(self.c.db.execute("SELECT count(*) FROM conexoes WHERE usuario=?", (self.m.usuario,)).fetchone()[0], 0)

    def test_orfao_so_expira_quando_nao_tem_vinculos(self):
        cid = self.conectar()
        a, b = self.criar(conexao=cid), self.criar(conexao=cid)
        self.c.excluir(self.m, a["id"], pedido=self.pedido())
        self.clock[0] += 2 * DIA
        self.c.limpar()
        self.assertIsNotNone(self.c.detalhes(self.m, b["id"]))
        orfao = self.conectar(conta="sem-personagem")
        self.clock[0] += DIA
        self.c.limpar()
        self.assertIsNone(self.c.db.execute("SELECT id FROM conexoes WHERE id=?", (orfao,)).fetchone())

    def test_reinicio_e_cifra_obrigatoria(self):
        p = self.criar()
        self.analise(p)
        self.reabrir()
        self.assertTrue(self.c.detalhes(self.m, p["id"])["analise"]["fonte_atual"])
        raw = self.path.read_bytes()
        for valor in (b"refresh-ficticio-secreto", "Personagem fictício".encode(), b'"vida"'):
            self.assertNotIn(valor, raw)
        with self.assertRaises(ErroCarteira): Cadastro(self.pasta / "sem-chave.sqlite3", ())
        self.assertFalse((self.pasta / "sem-chave.sqlite3").exists())

    def test_envelope_copiado_nao_atravessa_contexto(self):
        a, b = self.criar(), self.criar()
        self.c.db.execute("""UPDATE personagens SET perfil=(SELECT perfil FROM personagens WHERE id=?) WHERE id=?""",
                          (a["id"], b["id"]))
        with self.assertRaises(ErroCarteira): self.c.cartao(self.m, b["id"])

    def test_rotacao_preserva_conexoes_perfis_leituras_analises(self):
        p = self.criar()
        self.analise(p)
        antes = self.c.detalhes(self.m, p["id"])
        nova = Fernet.generate_key()
        self.c.rotacionar_chave(nova)
        self.reabrir((nova,))
        self.assertEqual(self.c.detalhes(self.m, p["id"]), antes)
        with self.assertRaises(ErroCarteira): Cadastro(self.path, (self.chave,), agora=self.agora)

    def test_rotacao_falha_reverte_todos_os_envelopes(self):
        p = self.criar()
        self.leitura(p)
        self.c.db.execute("UPDATE leituras SET conteudo=?", (b"invalido",))
        before = self.c.db.execute("SELECT segredo FROM conexoes").fetchone()[0]
        with self.assertRaises(ErroCarteira): self.c.rotacionar_chave(Fernet.generate_key())
        self.assertEqual(before, self.c.db.execute("SELECT segredo FROM conexoes").fetchone()[0])
        self.reabrir()
        self.assertTrue(self.c.listar(self.m))

    def test_permissoes_de_arquivos_privados(self):
        if os.name != "posix": self.skipTest("Permissões POSIX")
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.c.remocoes.stat().st_mode & 0o777, 0o600)

    def test_integridade_de_vinculos(self):
        self.criar()
        self.c.verificar_integridade()
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.db.execute("UPDATE fontes SET conexao='inexistente'")


class RecuperacaoTeste(Fixtures, unittest.TestCase):
    """Casos de recuperação compartilham as mesmas fixtures, sem repetir a suíte base."""

    def test_backup_cifrado_e_restore_preservam_dados(self):
        p = self.criar()
        self.analise(p)
        copia = gravar_backup(self.c, self.pasta / "copia.cvb")
        self.assertNotIn(b"SQLite format", copia.read_bytes())
        self.assertNotIn(b"refresh-ficticio-secreto", copia.read_bytes())
        novo = self.pasta / "restaurado.sqlite3"
        restaurar_backup(copia, novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as r:
            self.assertEqual(r.detalhes(self.m, p["id"]), self.c.detalhes(self.m, p["id"]))
            r.verificar_integridade()

    def test_restore_nao_ressuscita_personagem_excluido_depois_do_backup(self):
        a, b = self.criar(), self.criar()
        copia = gravar_backup(self.c, self.pasta / "antes.cvb")
        self.c.excluir(self.m, a["id"], pedido=self.pedido())
        novo = self.pasta / "depois.sqlite3"
        restaurar_backup(copia, novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as r:
            with self.assertRaises(AcessoNegado): r.cartao(self.m, a["id"])
            self.assertIsNotNone(r.cartao(self.m, b["id"]))

    def test_backup_do_registro_de_remocoes_pode_ser_recuperado(self):
        p = self.criar()
        copia = gravar_backup(self.c, self.pasta / "cadastro.cvb")
        self.c.excluir(self.m, p["id"], pedido=self.pedido())
        ledger_backup = gravar_backup(self.c, self.pasta / "remocoes.cvb", registro_remocoes=True)
        ledger = self.pasta / "ledger-recuperado.sqlite3"
        restaurar_remocoes(ledger_backup, ledger, (self.chave,), agora=self.agora)
        destino = self.pasta / "recuperado.sqlite3"
        restaurar_backup(copia, destino, (self.chave,), remocoes=ledger, agora=self.agora)
        with Cadastro(destino, (self.chave,), remocoes=ledger, agora=self.agora) as r:
            self.assertFalse(r.listar(self.m))

    def test_ausencia_ou_ledger_de_outro_banco_recusados(self):
        self.criar()
        copia = gravar_backup(self.c, self.pasta / "backup.cvb")
        destino = self.pasta / "restaurado.sqlite3"
        with self.assertRaises(ErroCarteira):
            restaurar_backup(copia, destino, (self.chave,), remocoes=self.pasta / "nao-existe", agora=self.agora)
        with Cadastro(self.pasta / "outro.sqlite3", (self.chave,), agora=self.agora) as outro:
            with self.assertRaises(ErroCarteira):
                restaurar_backup(copia, destino, (self.chave,), remocoes=outro.remocoes, agora=self.agora)
        self.assertFalse(destino.exists())

    def test_backup_alterado_truncado_chave_errada_e_destino_existente(self):
        self.criar()
        copia = gravar_backup(self.c, self.pasta / "backup.cvb")
        for mode in ("alterado", "truncado", "chave", "extra"):
            data = copia.read_bytes()
            if mode == "alterado": data = data[:100] + bytes([data[100] ^ 1]) + data[101:]
            if mode == "truncado": data = data[:-20]
            if mode == "extra": data += b"extra"
            ruim = self.pasta / f"{mode}.cvb"
            ruim.write_bytes(data)
            destino = self.pasta / f"{mode}.sqlite3"
            keys = (Fernet.generate_key(),) if mode == "chave" else (self.chave,)
            with self.subTest(mode=mode), self.assertRaises(ErroCarteira):
                restaurar_backup(ruim, destino, keys, remocoes=self.c.remocoes, agora=self.agora)
            self.assertFalse(destino.exists())
        before = self.path.read_bytes()
        with self.assertRaises(ErroCarteira):
            restaurar_backup(copia, self.path, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        self.assertEqual(before, self.path.read_bytes())
        with self.assertRaises(ErroCarteira): gravar_backup(self.c, copia)

    def test_backup_expirado_recusado_mesmo_apos_limpeza_do_ledger(self):
        p = self.criar()
        copia = gravar_backup(self.c, self.pasta / "backup.cvb")
        self.c.excluir(self.m, p["id"], pedido=self.pedido())
        self.clock[0] += 32 * DIA
        self.c.limpar()
        with self.assertRaises(ErroCarteira):
            restaurar_backup(copia, self.pasta / "velho.sqlite3", (self.chave,), remocoes=self.c.remocoes, agora=self.agora)

    def test_backup_antigo_usa_chave_antiga_apos_rotacao(self):
        p = self.criar()
        copia = gravar_backup(self.c, self.pasta / "antes.cvb")
        nova = Fernet.generate_key()
        self.c.rotacionar_chave(nova)
        destino = self.pasta / "antigo.sqlite3"
        restaurar_backup(copia, destino, (nova, self.chave), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(destino, (nova, self.chave), remocoes=self.c.remocoes, agora=self.agora) as r:
            self.assertTrue(r.cartao(self.m, p["id"]))

    def test_restore_nao_revalida_conexao_desconectada_ou_revogada(self):
        for tipo in ("desconectada", "revogada"):
            with self.subTest(tipo=tipo):
                cid = self.conectar(conta=tipo)
                p = self.criar(conexao=cid)
                self.analise(p)
                copia = gravar_backup(self.c, self.pasta / f"{tipo}.cvb")
                if tipo == "desconectada": self.c.desconectar(self.m, cid)
                else: self.revogar(cid)
                novo = self.pasta / f"{tipo}.sqlite3"
                restaurar_backup(copia, novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
                with Cadastro(novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as r:
                    with self.assertRaises(ErroCarteira): r.detalhes(self.m, p["id"])

    def test_reconexao_nova_nao_e_revogada_pelo_registro_antigo(self):
        cid = self.conectar()
        p = self.criar(conexao=cid)
        self.revogar(cid)
        self.conectar(refresh="refresh-reauth")
        copia = gravar_backup(self.c, self.pasta / "nova-auth.cvb")
        destino = self.pasta / "nova-auth.sqlite3"
        restaurar_backup(copia, destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as r:
            self.assertIsNotNone(r.detalhes(self.m, p["id"]))

    def test_backup_em_varios_blocos_e_reordenacao_recusada(self):
        p = self.criar()
        self.leitura(p, {"texto_ficticio": "x" * 1200000})
        copia = gravar_backup(self.c, self.pasta / "grande.cvb")
        novo = self.pasta / "grande.sqlite3"
        restaurar_backup(copia, novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(novo, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as r:
            self.assertEqual(len(r.detalhes(self.m, p["id"])["leitura"]["campos"]["texto_ficticio"]), 1200000)
        data = copia.read_bytes()
        pos, frames = len(MAGIC) + 16, []
        while pos < len(data):
            n = struct.unpack("!I", data[pos:pos + 4])[0]
            frames.append(data[pos:pos + 4 + n])
            pos += 4 + n
        self.assertGreaterEqual(len(frames), 4)
        frames[1], frames[2] = frames[2], frames[1]
        ruim = self.pasta / "reordenado.cvb"
        ruim.write_bytes(data[:len(MAGIC) + 16] + b"".join(frames))
        with self.assertRaises(ErroCarteira):
            restaurar_backup(ruim, self.pasta / "reordenado.sqlite3", (self.chave,), remocoes=self.c.remocoes, agora=self.agora)

    def test_retencao_so_remove_backups_autenticados_deste_cadastro(self):
        velho = gravar_backup(self.c, self.pasta / "velho.cvb")
        with Cadastro(self.pasta / "outro.sqlite3", (self.chave,), agora=self.agora) as outro:
            alheio = gravar_backup(outro, self.pasta / "alheio.cvb")
        invalido = self.pasta / "invalido.cvb"
        invalido.write_bytes(b"preservar para inspecao")
        self.clock[0] += 31 * DIA
        novo = gravar_backup(self.c, self.pasta / "novo.cvb")
        self.assertEqual(limpar_backups(self.pasta, (self.chave,), banco_id=self.c.banco_id, agora=self.agora), 1)
        self.assertFalse(velho.exists())
        self.assertTrue(alheio.exists())
        self.assertTrue(invalido.exists())
        self.assertTrue(novo.exists())


class MigracaoTeste(Fixtures, unittest.TestCase):
    def test_abertura_preserva_banco_criado_por_outro_inicializador(self):
        p = self.criar()
        alvo = self.pasta / "abertura-concorrente.sqlite3"
        ledger = alvo.with_suffix(".remocoes.sqlite3")
        from carteira_viva.banco import arquivo_privado
        def outro_criou(path):
            if path == alvo:
                shutil.copyfile(self.path, alvo)
                shutil.copyfile(self.c.remocoes, ledger)
                return False
            return arquivo_privado(path)
        with patch("carteira_viva.banco.arquivo_privado", side_effect=outro_criou):
            with Cadastro(alvo, (self.chave,), agora=self.agora) as outra:
                self.assertEqual(outra.cartao(self.m, p["id"])["id"], p["id"])
        self.assertTrue(alvo.exists())
        self.assertTrue(ledger.exists())

    def preparar_v1(self):
        p = self.criar()
        self.c.fechar()
        db = sqlite3.connect(self.path)
        db.executescript("DROP TABLE pedidos; DROP TABLE auditoria; PRAGMA user_version=1;")
        db.close()
        return p

    def test_migracao_v1_para_v2_preserva_cadastro_e_cifra(self):
        p = self.preparar_v1()
        self.c = Cadastro(self.path, (self.chave,), agora=self.agora)
        self.assertEqual(self.c.db.execute("PRAGMA user_version").fetchone()[0], esquema.VERSAO)
        self.assertEqual(self.c.cartao(self.m, p["id"])["perfil"], p["perfil"])
        self.assertTrue(self.c.db.execute("SELECT name FROM sqlite_master WHERE name='pedidos'").fetchone())
        self.c.verificar_integridade()

    def test_falha_de_migracao_nao_deixa_metade_do_schema(self):
        self.preparar_v1()
        with patch.dict(esquema.MIGRACOES, {2: (esquema.MIGRACOES[2][0], "SQL INVALIDO")}):
            with self.assertRaises(sqlite3.OperationalError): Cadastro(self.path, (self.chave,), agora=self.agora)
        db = sqlite3.connect(self.path)
        try:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 1)
            self.assertFalse(db.execute("SELECT name FROM sqlite_master WHERE name='pedidos'").fetchone())
            self.assertEqual(db.execute("SELECT count(*) FROM personagens").fetchone()[0], 1)
        finally:
            db.close()
        self.c = Cadastro(self.path, (self.chave,), agora=self.agora)

    def test_chave_errada_nao_migra(self):
        self.preparar_v1()
        with self.assertRaises(ErroCarteira): Cadastro(self.path, (Fernet.generate_key(),), agora=self.agora)
        db = sqlite3.connect(self.path)
        self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 1)
        db.close()
        self.c = Cadastro(self.path, (self.chave,), agora=self.agora)

    def test_versao_futura_recusada(self):
        self.c.db.execute("PRAGMA user_version=99")
        with self.assertRaises(ErroCarteira): Cadastro(self.path, (self.chave,), agora=self.agora)
        self.assertEqual(self.c.db.execute("PRAGMA user_version").fetchone()[0], 99)

    def test_banco_alheio_nao_e_adotado(self):
        path = self.pasta / "conversas.sqlite3"
        db = sqlite3.connect(path)
        db.execute("CREATE TABLE fichas (nome TEXT)")
        db.execute("INSERT INTO fichas VALUES ('preservar')")
        db.commit(); db.close()
        before = path.read_bytes()
        with self.assertRaises(ErroCarteira): Cadastro(path, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        self.assertEqual(before, path.read_bytes())

    def test_falta_de_registro_de_exclusoes_bloqueia_abertura(self):
        self.criar()
        ledger = self.c.remocoes
        self.c.fechar()
        ledger.rename(ledger.with_suffix(".guardado"))
        before = self.path.read_bytes()
        with self.assertRaises(ErroCarteira): Cadastro(self.path, (self.chave,), agora=self.agora)
        self.assertFalse(ledger.exists())
        self.assertEqual(before, self.path.read_bytes())

    def test_falha_inicial_remove_arquivos_incompletos(self):
        path = self.pasta / "novo.sqlite3"
        with patch.dict(esquema.MIGRACOES, {2: ("SQL INVALIDO",)}):
            with self.assertRaises(sqlite3.OperationalError): Cadastro(path, (self.chave,), agora=self.agora)
        self.assertFalse(path.exists())
        self.assertFalse(path.with_suffix(".remocoes.sqlite3").exists())


if __name__ == "__main__":
    unittest.main()
