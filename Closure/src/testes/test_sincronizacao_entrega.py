"""Proveniência e proteção contra regressão de edição; sem rede."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'ferramentas'))
import sincronizar as s


class EntregaAprovada(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.entrega = self.raiz / 'livro-diagramado-r52'
        self.entrega.mkdir()
        (self.entrega/'LEIA-ME-R52.md').write_text('# Ciclo Maldito — R52\n')
        (self.entrega/'LIVRO-COMPLETO.md').write_text('texto aprovado')
        pdf = self.entrega/'output/pdf/Ciclo-Maldito-R52.pdf'
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b'pdf de teste')
        self.saida = self.raiz/'saida'
        self.saida.mkdir()

    def rodar(self, *args):
        with patch.object(s, 'SAIDA', str(self.saida)), patch.object(s, 'achar_repo', return_value=('repo', 'v0.364')), \
             patch.object(s, 'edicao_do_livro', return_value='R51'), \
             patch.object(s, 'blocos_do_livro', return_value=[{'capitulo': 5, 'capitulo_titulo': 'Origens'}]) as blocos, \
             patch.object(s, 'catalogos', return_value={'teste': 1}), patch.object(s, 'commit', return_value=('abc', 'data')), \
             patch.object(sys, 'argv', ['sincronizar', '--repo', 'repo', *args]), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            resultado = s.main()
        return resultado, blocos

    def test_entrega_registra_hashes_sem_caminho_privado_ou_commit_falso(self):
        ret, blocos = self.rodar('--entrega-livro', str(self.entrega))
        self.assertEqual(ret, 0)
        m = json.loads((self.saida/'MANIFESTO.json').read_text())
        self.assertEqual(m['edicao_livro'], 'R52')
        self.assertIsNone(m['commit'])
        self.assertIsNone(m['commit_livro'])
        self.assertEqual(m['commit_catalogos'], 'abc')
        self.assertEqual(len(m['fonte_livro']['texto_sha256']), 64)
        self.assertNotIn(str(self.raiz), json.dumps(m))
        blocos.assert_called_once_with('repo', self.entrega/'LIVRO-COMPLETO.md')

    def test_entrega_incompleta_nao_grava_nada(self):
        (self.entrega/'LEIA-ME-R52.md').unlink()
        ret, _ = self.rodar('--entrega-livro', str(self.entrega))
        self.assertEqual(ret, 1)
        self.assertEqual(list(self.saida.iterdir()), [])

    def test_nao_regrede_para_repo_antigo_sem_autorizacao_explicita(self):
        antigo = self.saida/'MANIFESTO.json'
        antigo.write_text('{"edicao_livro":"R52"}')
        ret, blocos = self.rodar()
        self.assertEqual(ret, 1)
        self.assertEqual(antigo.read_text(), '{"edicao_livro":"R52"}')
        blocos.assert_not_called()
        ret, _ = self.rodar('--permitir-retrocesso')
        self.assertEqual(ret, 0)
        self.assertEqual(json.loads(antigo.read_text())['edicao_livro'], 'R51')
