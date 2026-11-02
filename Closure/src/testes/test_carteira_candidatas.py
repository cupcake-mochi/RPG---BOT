"""Candidatas e diagnósticos: SQLite real, dados fictícios, sem rede."""
from dataclasses import replace
import unittest
from cryptography.fernet import Fernet
from carteira_viva.banco import Cadastro,DIA
from carteira_viva.backup import gravar_backup,restaurar_backup
from carteira_viva.copias_google import DestinoCopia
from carteira_viva.observacoes_copia import ObservacaoVersao,LIMITE
from carteira_viva.segredos import Conflito,AcessoNegado,ErroCarteira
from testes.test_carteira_banco import Fixtures
ARQUIVO='copia_ficticia_das_candidatas_001'

class CandidatasBanco(Fixtures,unittest.TestCase):
    def preparar(self):
        self.cid=self.conectar()
        self.ref=self.c.preparar_copia_modelo(self.m,conexao=self.cid,modelo='ciclo',pedido='ficticio')
        self.c.fixar_versao_copia(self.m,self.ref,'9007199254740993');self.c.armar_envio_copia(self.m,self.ref)
        self.dest=DestinoCopia(ARQUIVO,'9007199254740994',self.ref.operacao,self.ctx()['origem'])
    def ctx(self):return self.c.contexto_copia(self.m,self.ref)
    def identificar(self):
        self.c.registrar_candidata_copia(self.m,self.ref,self.dest);self.c.registrar_destino_copia(self.m,self.ref,self.dest)
    def evento(self,n='9007199254740995'):return ObservacaoVersao('copia_leitura','9007199254740994',n)

    def test_nova_intencao_exige_candidata_e_nao_cria_personagem(self):
        self.preparar();self.assertEqual(self.ctx()['protocolo_copia'],2)
        with self.assertRaises(Conflito):self.c.registrar_destino_copia(self.m,self.ref,self.dest)
        self.identificar();self.assertEqual(self.ctx()['versao_destino'],'9007199254740994');self.assertFalse(self.c.listar(self.m))

    def test_candidata_so_apos_envio_e_tipada_sem_id_do_cliente(self):
        self.preparar()
        with self.assertRaises(ErroCarteira):self.c.registrar_candidata_copia(self.m,self.ref,{'arquivo':ARQUIVO})
        d=self.ctx();self.c._guardar_copia(self.ref,{**d,'estado':'preparada'})
        with self.assertRaises(Conflito):self.c.registrar_candidata_copia(self.m,self.ref,self.dest)

    def test_candidata_nao_muda_de_arquivo_ou_versao_apos_reinicio(self):
        self.preparar();self.c.registrar_candidata_copia(self.m,self.ref,self.dest);self.reabrir()
        for legado in (False,True):
            if legado:
                d=self.ctx();d.pop('protocolo_copia');self.c._guardar_copia(self.ref,d)
            for dest in [replace(self.dest,versao='9007199254740995'),replace(self.dest,arquivo='outra_copia_ficticia_001')]:
                with self.subTest(legado=legado,dest=dest),self.assertRaises(Conflito):self.c.registrar_candidata_copia(self.m,self.ref,dest)
                with self.assertRaises(Conflito):self.c.registrar_destino_copia(self.m,self.ref,dest)
        self.assertEqual(self.ctx()['candidata']['versao'],'9007199254740994');self.assertIsNone(self.ctx()['destino'])

    def test_outro_usuario_admin_e_servidor_nao_adicionam_diagnostico(self):
        self.preparar()
        for m in [self.outro,self.admin,replace(self.m,servidor='outra')]:
            with self.assertRaises(AcessoNegado):self.c.registrar_observacao_copia(m,self.ref,self.evento())
            with self.assertRaises(AcessoNegado):self.c.registrar_candidata_copia(m,self.ref,self.dest)

    def test_arquivo_ja_cadastrado_em_outra_mesa_nao_vira_candidata(self):
        self.preparar()
        self.c.cadastrar(replace(self.m,servidor='mesa-ficticia-2'),conexao=self.cid,arquivo=ARQUIVO,
            nome='Fictício',contrato='analise-12',responsabilidade=True,pedido='outro-cadastro')
        with self.assertRaises(Conflito):self.c.registrar_candidata_copia(self.m,self.ref,self.dest)
        self.assertIsNone(self.ctx()['candidata'])

    def test_diagnostico_nao_aceita_prosa_segredos_ou_json_do_cliente(self):
        self.preparar()
        with self.assertRaises(ErroCarteira):self.c.registrar_observacao_copia(self.m,self.ref,{})
        for a,b,c in [('qualquer','1','2'),('copia_leitura','url-privada','2'),('copia_leitura','1','token-privado'),('copia_leitura',True,'2'),('copia_leitura','1','1'*31),('copia_leitura',None,None)]:
            with self.subTest(a=a,b=b,c=c),self.assertRaises(ErroCarteira):ObservacaoVersao(a,b,c)
        self.assertNotIn('9007199254740994',repr(self.evento()))

    def test_historico_limitado_repeticao_conserva_primeiro_horario(self):
        self.preparar();self.c.registrar_observacao_copia(self.m,self.ref,self.evento())
        inicial=self.ctx()['observacoes_versao'][0]['primeiro_em'];self.clock[0]+=9
        self.c.registrar_observacao_copia(self.m,self.ref,self.evento());e=self.ctx()['observacoes_versao'][0]
        self.assertEqual(e['vezes'],2);self.assertEqual(e['primeiro_em'],inicial);self.assertEqual(e['ultimo_em'],self.agora())
        for i in range(LIMITE+10):self.c.registrar_observacao_copia(self.m,self.ref,self.evento(str(i+10)))
        self.assertEqual(len(self.ctx()['observacoes_versao']),LIMITE)

    def test_diagnostico_nao_muda_vinculo_mas_campo_de_autoridade_muda(self):
        self.preparar();self.identificar();antes,chave=self.c.contexto_financeiro(self.m,self.ref)
        self.c.registrar_observacao_copia(self.m,self.ref,self.evento());depois,nova=self.c.contexto_financeiro(self.m,self.ref)
        self.assertEqual(chave,nova);self.assertEqual(antes['versao_destino'],depois['versao_destino'])
        self.c._guardar_copia(self.ref,{**depois,'versao_destino':'9007199254740995'})
        self.assertNotEqual(chave,self.c.contexto_financeiro(self.m,self.ref)[1])

    def test_diagnostico_nao_renova_retencao_da_copia_identificada(self):
        self.preparar();self.identificar();t=self.c.db.execute('select atualizado from copias_rest').fetchone()[0]
        self.clock[0]+=29*DIA;self.c.registrar_observacao_copia(self.m,self.ref,self.evento())
        self.assertEqual(self.c.db.execute('select atualizado from copias_rest').fetchone()[0],t)
        self.clock[0]+=2*DIA;self.c.limpar();self.assertEqual(self.c.db.execute('select count(*) from copias_rest').fetchone()[0],0)

    def test_rotacao_backup_restore_conservam_candidata_sem_replay(self):
        self.preparar();self.c.registrar_candidata_copia(self.m,self.ref,self.dest);self.c.registrar_observacao_copia(self.m,self.ref,self.evento());antes=self.ctx()
        nova=Fernet.generate_key();self.c.rotacionar_chave(nova);self.assertEqual(antes,self.ctx())
        bak=self.pasta/'dados.cvb';dest=self.pasta/'restaurado.sqlite3';gravar_backup(self.c,bak)
        restaurar_backup(bak,dest,(nova,self.chave),remocoes=self.path.with_suffix('.remocoes.sqlite3'),agora=self.agora)
        with Cadastro(dest,(nova,self.chave),remocoes=self.path.with_suffix('.remocoes.sqlite3'),agora=self.agora) as c:
            self.assertEqual(c.contexto_copia(self.m,self.ref),antes);self.assertFalse(c.armar_envio_copia(self.m,self.ref))

    def test_exclusao_global_restore_nao_ressuscitam_candidata_e_diagnostico(self):
        self.preparar();self.c.registrar_candidata_copia(self.m,self.ref,self.dest);self.c.registrar_observacao_copia(self.m,self.ref,self.evento())
        bak=self.pasta/'dados.cvb';dest=self.pasta/'restaurado.sqlite3';gravar_backup(self.c,bak);self.c.apagar_usuario(self.m.usuario)
        restaurar_backup(bak,dest,(self.chave,),remocoes=self.path.with_suffix('.remocoes.sqlite3'),agora=self.agora)
        with Cadastro(dest,(self.chave,),remocoes=self.path.with_suffix('.remocoes.sqlite3'),agora=self.agora) as c:self.assertEqual(c.db.execute('select count(*) from copias_rest').fetchone()[0],0)

    def test_copia_historica_sem_protocolo_nao_adota_nova_versao(self):
        self.preparar();d=self.ctx();d.pop('protocolo_copia');d.pop('candidata');self.c._guardar_copia(self.ref,d)
        self.c.registrar_destino_copia(self.m,self.ref,self.dest)
        with self.assertRaises(Conflito):self.c.registrar_destino_copia(self.m,self.ref,replace(self.dest,versao='9007199254740995'))

    def test_protocolo_futuro_booleano_e_texto_sao_recusados(self):
        self.preparar();d=self.ctx()
        for v in [3,True,'2']:
            self.c._guardar_copia(self.ref,{**d,'protocolo_copia':v})
            with self.assertRaises(Conflito):self.ctx()
        self.c._guardar_copia(self.ref,d)
