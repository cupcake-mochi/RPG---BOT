"""Formatação editorial não muda a regra nem desliga as guardas do corretor."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from closure_bot.ficha_corretor import (
    DEFESA_ZERO, PE_EXTRA, SEM_INTEGRIDADE,
    TREINO_EXTRA, VIDA_METADE, Referencias,
)

RAIZ = Path(__file__).resolve().parents[2]


class GuardasEditoriais(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dados = Path(self.tmp.name)
        shutil.copytree(RAIZ / 'dados/sistema', self.dados / 'sistema')
        self.arquivo = self.dados / 'sistema/livro.jsonl'
        self.blocos = list(map(json.loads, self.arquivo.read_text().splitlines()))

    def alterar(self, ancora, antes, depois):
        novos = [dict(b) for b in self.blocos]
        bloco = next(b for b in novos if b['ancora'] == ancora)
        self.assertIn(antes, bloco['texto'])
        bloco['texto'] = bloco['texto'].replace(antes, depois)
        self.arquivo.write_text(''.join(json.dumps(b, ensure_ascii=False) + '\n' for b in novos))

    def test_r57_com_negrito_e_link_carrega_referencias(self):
        texto = next(b['texto'] for b in self.blocos if b['ancora'] == 'origens--encarnado-beneficios')
        self.assertIn('sem precisar escolher **Corpo** naquele **[Marco](#progressao--prog-marcos)**', texto)
        self.assertEqual(Referencias.do_livro(self.dados).refino_maximo, 10)

    def test_corpo_sem_negrito_continua_aceito(self):
        atual = Referencias.do_livro(self.dados)
        self.alterar('origens--encarnado-beneficios', '**Corpo**', 'Corpo')
        self.assertEqual(Referencias.do_livro(self.dados), atual)

    def test_mudanca_no_requisito_ou_nome_ainda_bloqueia(self):
        for antes, depois in (
            ('sem precisar escolher **Corpo**', 'precisa escolher **Corpo**'),
            ('sem precisar escolher **Corpo**', 'sem precisar escolher **Mente**'),
            ('Especialidade Antiga', 'Outra capacidade'),
        ):
            with self.subTest(depois=depois):
                self.alterar('origens--encarnado-beneficios', antes, depois)
                with self.assertRaisesRegex(ValueError, 'mudou a capacidade Especialidade Antiga'):
                    Referencias.do_livro(self.dados)

    def test_demais_guardas_conservam_comparacao_literal(self):
        guardas = {**TREINO_EXTRA, **{k: (0, *v) for k, v in PE_EXTRA.items()},
                   **{k: (0, a, 'Defesa fica fixada em 0') for k, a in DEFESA_ZERO.items()},
                   **{k: (0, a, 'vida máxima é metade da normal') for k, a in VIDA_METADE.items()},
                   **{k: (0, *v) for k, v in SEM_INTEGRIDADE.items()}}
        self.assertNotIn('Especialidade Antiga', guardas)
        for nome, (_, ancora, trecho) in guardas.items():
            for antes, depois in ((trecho, 'REGRA ALTERADA'), (nome, 'CAPACIDADE RENOMEADA')):
                with self.subTest(nome=nome, antes=antes):
                    self.alterar(ancora, antes, depois)
                    with self.assertRaisesRegex(ValueError, 'mudou a capacidade'):
                        Referencias.do_livro(self.dados)


if __name__ == '__main__':
    unittest.main()
