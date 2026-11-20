"""Recuperação real do SQLite, corrida de conclusão e ciclo de vida; dados fictícios."""
import asyncio
from dataclasses import replace
import unittest
from cryptography.fernet import Fernet

from carteira_viva.backup import gravar_backup, restaurar_backup
from carteira_viva.banco import Cadastro
from carteira_viva.conferencia_inicializacao import FLAGS, ConferenciaGrade
from carteira_viva.conferencias_banco import conferir_dominio_persistido, PRAZO
from carteira_viva.modelos import CriacaoBloqueada
from carteira_viva.segredos import AcessoNegado, Conflito, ErroCarteira
from testes.test_carteira_banco import Fixtures, schema_historico
from testes.test_carteira_conferencia_inicializacao import Dados
from testes.test_carteira_grade_inicializacao import ARQUIVO


class Worker:
    def __init__(self, banco): self.banco = banco
    async def chamar(self, metodo, *args):
        return getattr(self.banco, metodo.removeprefix('cadastro.'))(*args)


class ConferenciasBancoTeste(Fixtures, unittest.IsolatedAsyncioTestCase):
    def preparar(self):
        p = self.criar(arquivo=ARQUIVO)
        ref = self.c.reservar_leitura(self.m, p['id'])
        c = Dados('financeiro')
        c.contexto = self.c.contexto_conferencia_rest(self.m, ref)
        b = self.c.iniciar_conferencia_rest(self.m, ref, versao_drive=c.versao)
        c.contexto = self.c.contexto_operacao_rest(self.m, b)[1]
        return p, ref, c, b

    async def rodar(self, c, b):
        return await conferir_dominio_persistido(Worker(self.c), self.m, b, c.p, 'credencial_ficticia',
            revalidar_contexto=c.revalidar, aguardar_cota=c.cota, agora=lambda: c.tempo)

    def quantidade(self):
        return self.c.db.execute('SELECT count(*) FROM conferencias_rest').fetchone()[0]

    async def test_interrupcao_na_pagina_nao_avanca_e_reinicio_rele_desde_zero(self):
        p, ref, c, b = self.preparar()
        async def parar():
            if c.cotas == 10: raise asyncio.CancelledError()
        c.ao_esperar = parar
        with self.assertRaises(asyncio.CancelledError): await self.rodar(c, b)
        self.reabrir()
        b2 = self.c.retomar_conferencia_rest(self.m, p['id'])
        self.assertEqual(b, b2)
        c.ao_esperar = None; c.requests.clear(); c.cotas = 0
        b2 = await self.rodar(c, b2)
        # Lotes: 50 faixas financeiras em 37 GETs, 3 cotas cada (antes 154).
        self.assertEqual(b2.revisao, 1); self.assertEqual(c.cotas, 115)
        self.assertEqual(self.c.resultado_conferencia_rest(self.m, b2)['dominios_conferidos'], 1)

    async def test_reinicio_entre_dominios_nao_rele_financeiro_e_nunca_libera_criacao(self):
        p, ref, c, b = self.preparar(); b = await self.rodar(c, b)
        self.reabrir(); b = self.c.retomar_conferencia_rest(self.m, p['id'])
        d = Dados(); d.contexto = c.contexto
        b = await self.rodar(d, b)
        r = self.c.resultado_conferencia_rest(self.m, b)
        # Progressão: 8 faixas em 2 lotes (antes 28 cotas).
        self.assertEqual(d.cotas, 10); self.assertEqual(r['dominios_conferidos'], 2)
        self.assertEqual([x['dominio'] for x in r['resultados']], ['financeiro', 'progressao'])
        self.assertTrue(r['leitura_historica'])
        for k in FLAGS: self.assertIs(r[k], False)
        with self.assertRaises(Conflito): await self.rodar(d, b)
        with self.assertRaises(CriacaoBloqueada): self.c.criar_por_modelo(self.m, modelo='ciclo')

    async def test_duas_conclusoes_concorrentes_so_uma_consume_revisao(self):
        _, _, c, b = self.preparar()
        a = await c.conferir()
        primeiro = self.c.gravar_conferencia_rest(self.m, b, a)
        with self.assertRaises(Conflito): self.c.gravar_conferencia_rest(self.m, b, a)
        self.assertEqual(primeiro.revisao, 1)
        self.assertEqual(self.c.resultado_conferencia_rest(self.m, primeiro)['dominios_conferidos'], 1)

    async def test_versao_mudou_apos_reinicio_recusa_sem_avancar(self):
        p, _, c, b = self.preparar(); b = await self.rodar(c, b); self.reabrir()
        d = Dados(); d.contexto = c.contexto; d.versao = '999'
        with self.assertRaises(Conflito): await self.rodar(d, b)
        self.assertEqual(self.c.retomar_conferencia_rest(self.m, p['id']), b)
        self.assertFalse(any('ranges' in r.url.params for r in d.requests))

    async def test_mutacao_na_confirmacao_final_nao_persiste_dominio(self):
        _, _, c, b = self.preparar()
        disparou = []
        def trocar():
            # 115 = cota da confirmação final com lotes; o teste exige que dispare.
            if c.cotas == 115: c.versao = '999'; disparou.append(True)
        c.final_hook = trocar
        with self.assertRaises(ErroCarteira): await self.rodar(c, b)
        self.assertEqual(disparou, [True])
        self.assertEqual(self.c.resultado_conferencia_rest(self.m, b)['dominios_conferidos'], 0)

    async def test_residuo_real_e_salvo_como_erro_sem_guardar_texto_privado(self):
        _, _, c, b = self.preparar(); c.literal('EXTRATO', 5000, 3, 'RESIDUO_SECRETO_FICTICIO')
        b = await self.rodar(c, b); r = self.c.resultado_conferencia_rest(self.m, b)
        self.assertGreater(r['resultados'][0]['erros'], 0)
        self.assertNotIn('RESIDUO_SECRETO_FICTICIO', str(r))
        row = self.c.db.execute('SELECT * FROM conferencias_rest').fetchone()
        d = self.c.cifra.abrir(self.c._ctx_conferencia(row), row['conteudo'])
        self.assertNotIn('RESIDUO_SECRETO_FICTICIO', str(d))
        for s in (ARQUIVO, 'credencial_ficticia', 'RESIDUO_SECRETO_FICTICIO', c.contexto):
            self.assertNotIn(s.encode(), row['conteudo'])
        self.assertLess(len(row['conteudo']), 32768)

    async def test_conclusao_fora_da_ordem_incompleta_ou_json_nao_avanca(self):
        _, _, c, b = self.preparar()
        d = Dados(); d.contexto = c.contexto; errado = await d.conferir()
        plano = await c.leitor.abrir('x', ARQUIVO, 'financeiro')
        for a in (errado, ConferenciaGrade(plano), errado.publico()):
            with self.subTest(tipo=type(a)), self.assertRaises(ErroCarteira):
                self.c.gravar_conferencia_rest(self.m, b, a)
        self.assertEqual(b.revisao, 0)

    def test_prazo_nao_renova_em_repeticao_ou_reinicio(self):
        p, ref, c, b = self.preparar(); self.clock[0] += PRAZO - 1
        self.assertEqual(self.c.iniciar_conferencia_rest(self.m, ref, versao_drive=c.versao), b)
        self.reabrir(); self.clock[0] += 1
        with self.assertRaises(Conflito): self.c.retomar_conferencia_rest(self.m, p['id'])
        self.assertEqual(self.c.limpar()['conferencias_rest'], 1)
        novo = self.c.iniciar_conferencia_rest(self.m, ref, versao_drive=c.versao)
        self.assertNotEqual(novo.operacao, b.operacao)

    async def test_expira_durante_cota_nao_salva_nem_renova_prazo(self):
        _, _, c, b = self.preparar()
        async def expirar(): self.clock[0] += PRAZO
        c.ao_esperar = expirar
        with self.assertRaises(ErroCarteira): await self.rodar(c, b)
        self.assertEqual(self.c.db.execute('SELECT revisao FROM conferencias_rest').fetchone()[0], 0)
        self.assertFalse(c.requests)

    def test_relogio_atrasado_e_metadado_adulterado_recusados(self):
        p, _, _, _ = self.preparar(); self.clock[0] -= 1
        with self.assertRaises(Conflito): self.c.retomar_conferencia_rest(self.m, p['id'])
        self.clock[0] += 1
        self.c.db.execute('UPDATE conferencias_rest SET expira=expira+100')
        with self.assertRaises(Conflito): self.c.retomar_conferencia_rest(self.m, p['id'])

    def test_membro_comum_outro_admin_ou_outro_servidor_nao_retomam(self):
        p, _, _, b = self.preparar()
        for m in (self.outro, self.admin, replace(self.m, presente=False), replace(self.m, servidor='outro')):
            with self.subTest(m=m), self.assertRaises(ErroCarteira): self.c.retomar_conferencia_rest(m, p['id'])
        with self.assertRaises(Conflito): self.c.contexto_operacao_rest(self.m, replace(b, revisao=1))

    def test_nova_reserva_modelo_e_configuracao_invalidam_contexto(self):
        for tipo in ('reserva', 'modelo', 'config'):
            with self.subTest(tipo=tipo):
                p, _, _, b = self.preparar()
                if tipo == 'reserva': self.c.reservar_leitura(self.m, p['id'])
                elif tipo == 'modelo':
                    rev = self.c.modelos(self.admin)['revisao']
                    self.c.configurar_modelo(self.admin, escolha='ciclo', revisao=rev)
                else: self.c.db.execute('UPDATE servidores SET revisao=revisao+1')
                with self.assertRaises(Conflito): self.c.resultado_conferencia_rest(self.m, b)
                self.c.apagar_usuario(self.m.usuario)

    def test_reautorizacao_revogacao_desconexao_removem_historico(self):
        for tipo in ('reautorizar', 'revogar', 'desconectar'):
            with self.subTest(tipo=tipo):
                p, ref, _, _ = self.preparar()
                if tipo == 'reautorizar': self.conectar()
                elif tipo == 'revogar': self.revogar(ref.conexao)
                else: self.c.desconectar(self.m, ref.conexao)
                self.assertEqual(self.quantidade(), 0)
                self.c.apagar_usuario(self.m.usuario)

    def test_troca_exclusao_e_pedido_global_removem_estado(self):
        for tipo in ('troca', 'excluir', 'global'):
            with self.subTest(tipo=tipo):
                p, ref, _, b = self.preparar()
                if tipo == 'troca':
                    self.c.trocar_arquivo(self.m, p['id'], conexao=ref.conexao, arquivo=self.pedido(), contrato='r53', revisao=ref.revisao, pedido=self.pedido())
                elif tipo == 'excluir': self.c.excluir(self.m, p['id'], pedido=self.pedido())
                else: self.c.apagar_usuario(self.m.usuario)
                self.assertEqual(self.quantidade(), 0)
                self.c.apagar_usuario(self.m.usuario)

    async def test_rotacao_preserva_resultado_e_cifra_antiga_nao_abre(self):
        p, _, c, b = self.preparar(); b = await self.rodar(c, b)
        antes = self.c.resultado_conferencia_rest(self.m, b)
        nova = Fernet.generate_key(); self.c.rotacionar_chave(nova); self.reabrir((nova,))
        self.assertEqual(self.c.resultado_conferencia_rest(self.m, b), antes)
        with self.assertRaises(ErroCarteira): Cadastro(self.path, (self.chave,), agora=self.agora)

    def test_backup_nao_restaura_trabalho_pendente(self):
        p, _, _, _ = self.preparar(); backup = self.pasta / 'dados.cvb'
        gravar_backup(self.c, backup); destino = self.pasta / 'recuperado.sqlite3'
        restaurar_backup(backup, destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora)
        with Cadastro(destino, (self.chave,), remocoes=self.c.remocoes, agora=self.agora) as c:
            self.assertEqual(c.cartao(self.m, p['id'])['id'], p['id'])
            self.assertEqual(c.db.execute('SELECT count(*) FROM conferencias_rest').fetchone()[0], 0)

    def test_migracao6_preserva_dados_e_rejeita_envelope_corrompido(self):
        p, _, _, _ = self.preparar()
        schema_historico(self.c.db,6);self.reabrir()
        self.assertEqual(self.c.cartao(self.m, p['id'])['id'], p['id']); self.assertEqual(self.quantidade(), 0)
        ref = self.c.reservar_leitura(self.m, p['id'])
        self.c.iniciar_conferencia_rest(self.m, ref, versao_drive='12')
        self.c.db.execute("UPDATE conferencias_rest SET conteudo=x'00'")
        with self.assertRaises(ErroCarteira): self.c.retomar_conferencia_rest(self.m, p['id'])

    def test_descartar_so_local_e_nao_aceita_bilhete_antigo(self):
        p, ref, c, b = self.preparar(); self.c.descartar_conferencia_rest(self.m, b)
        self.assertEqual(self.quantidade(), 0)
        novo = self.c.iniciar_conferencia_rest(self.m, ref, versao_drive=c.versao)
        self.assertNotEqual(novo.operacao, b.operacao)
        with self.assertRaises(Conflito): self.c.contexto_operacao_rest(self.m, b)
        self.assertEqual(self.c.cartao(self.m, p['id'])['id'], p['id'])

    async def test_revogacao_enquanto_aguarda_cota_nao_emite_get(self):
        _, ref, c, b = self.preparar()
        async def revogar(): self.revogar(ref.conexao)
        c.ao_esperar = revogar
        with self.assertRaises(ErroCarteira): await self.rodar(c, b)
        self.assertFalse(c.requests); self.assertEqual(self.quantidade(), 0)

    async def test_worker_real_em_thread_recupera_operacao_e_grava_dominio(self):
        from carteira_viva.fluxos import DadosAsync
        from testes.test_carteira_provedores import configuracao
        p, _, c, b = self.preparar(); self.c.fechar()
        worker = DadosAsync(configuracao(self.path, chaves=(self.chave,)), agora=self.agora)
        await worker.iniciar()
        try:
            b = await worker.chamar('cadastro.retomar_conferencia_rest', self.m, p['id'])
            b = await conferir_dominio_persistido(worker, self.m, b, c.p, 'ficticio',
                revalidar_contexto=c.revalidar, aguardar_cota=c.cota, agora=lambda: c.tempo)
            r = await worker.chamar('cadastro.resultado_conferencia_rest', self.m, b)
            self.assertEqual(r['dominios_conferidos'], 1)
        finally:
            await worker.fechar()
            self.c = Cadastro(self.path, (self.chave,), agora=self.agora)

    async def test_dois_processos_nao_confirmam_bilhete_ja_consumido(self):
        p, _, c, b = self.preparar(); a = await c.conferir()
        with Cadastro(self.path, (self.chave,), agora=self.agora) as outro:
            copia = outro.retomar_conferencia_rest(self.m, p['id'])
            novo = self.c.gravar_conferencia_rest(self.m, b, a)
            with self.assertRaises(Conflito): outro.gravar_conferencia_rest(self.m, copia, a)
            self.assertEqual(outro.retomar_conferencia_rest(self.m, p['id']), novo)

    def test_envelope_de_outro_personagem_nao_pode_ser_transplantado(self):
        p, _, _, _ = self.preparar()
        row = self.c.db.execute('SELECT * FROM conferencias_rest').fetchone()
        outro = self.criar(arquivo='arquivo_descartavel_sintetico_002', conexao=self.c._fonte(self.m.servidor, p['id'])['conexao'])
        ref = self.c.reservar_leitura(self.m, outro['id'])
        self.c.iniciar_conferencia_rest(self.m, ref, versao_drive='12')
        self.c.db.execute('UPDATE conferencias_rest SET conteudo=? WHERE personagem=?', (row['conteudo'], outro['id']))
        with self.assertRaises(ErroCarteira): self.c.retomar_conferencia_rest(self.m, outro['id'])
        self.assertIsNotNone(self.c.retomar_conferencia_rest(self.m, p['id']))

    def test_descartar_historico_desatualizado_nao_recicla_resultado(self):
        p, ref, c, b = self.preparar()
        self.c.configurar_modelo(self.admin, escolha='era', revisao=0)
        with self.assertRaises(Conflito): self.c.retomar_conferencia_rest(self.m, p['id'])
        with self.assertRaises(AcessoNegado): self.c.descartar_conferencia_rest(self.admin, b)
        self.c.descartar_conferencia_rest(self.m, b)
        novo = self.c.iniciar_conferencia_rest(self.m, ref, versao_drive=c.versao)
        self.assertEqual(novo.revisao, 0); self.assertNotEqual(novo.operacao, b.operacao)

    def test_exclusao_global_do_revisor_apaga_operacao_sem_apagar_personagem_alheio(self):
        p, _, c, _ = self.preparar()
        self.c.apagar_usuario(self.admin.usuario)
        self.assertEqual(self.quantidade(), 1)
        b = self.c.retomar_conferencia_rest(self.m, p['id']); self.c.descartar_conferencia_rest(self.m, b)
        ref = self.c.reservar_leitura(self.admin, p['id'])
        self.c.iniciar_conferencia_rest(self.admin, ref, versao_drive=c.versao)
        self.c.apagar_usuario(self.admin.usuario)
        self.assertEqual(self.quantidade(), 0)
        self.assertEqual(self.c.cartao(self.m, p['id'])['id'], p['id'])

    async def test_nova_operacao_nao_adota_auditoria_da_anterior_mesmo_arquivo_e_versao(self):
        _, ref, c, b = self.preparar(); anterior = await c.conferir()
        self.c.descartar_conferencia_rest(self.m, b)
        novo = self.c.iniciar_conferencia_rest(self.m, ref, versao_drive=c.versao)
        with self.assertRaises(Conflito): self.c.gravar_conferencia_rest(self.m, novo, anterior)
        self.assertEqual(self.c.resultado_conferencia_rest(self.m, novo)['dominios_conferidos'], 0)
