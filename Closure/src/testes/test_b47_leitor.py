"""Fixtures sintéticas pequenas: sem Google, dados privados ou cálculo de planilha."""
import io
import unittest
from openpyxl import Workbook
from closure_bot.ficha_leitor import de_linhas, de_csv, de_xlsx, FichaIlegivel
from closure_bot.ficha_esquema import campos_b47, variante


class LeitorB47(unittest.TestCase):
    def test_manifesto_entregue(self):
        campos = campos_b47()
        self.assertEqual(len(campos), 8190)  # auditoria da base, não condição de leitura
        self.assertIn('custom.familia.10.nome', campos)
        self.assertNotIn('custom.familia.11.nome', campos)
        self.assertIn('invocacao.12.familia.9', campos)

    def test_texto_literal_independe_da_aparencia(self):
        for valor in ('007', '1,5', 'VERDADEIRO', 'FALSO', '*?~', '=1+1', ' texto '):
            for chave in ('nome', 'custom.dano.1.definicao', 'custom.forma.1.alcance_escada', 'invocacao.1.nome'):
                with self.subTest(valor=valor, chave=chave):
                    self.assertEqual(de_linhas([[chave, valor]])[chave].valor, valor)

    def test_numeros_booleanos_vazio_zero_ausente(self):
        f = de_linhas([['formato.versao','11'], ['efeito.1.valor','1,5'], ['custom.dano.1.mestre_viu','FALSO'],
                       ['vida.rolagem.2',''], ['vida.rolagem.3','0']])
        self.assertEqual([f[k].valor for k in f], [11,1.5,0,'',0])
        self.assertNotIn('vida.rolagem.4', f)

    def test_duplicada_e_erros_nao_desaparecem(self):
        with self.assertRaisesRegex(FichaIlegivel, 'duplicada'):
            de_linhas([['nome','a'],['nome','b']])
        for erro in ('#REF!', '#DIV/0!', '#CALC!'):
            with self.assertRaisesRegex(FichaIlegivel, 'fórmula'):
                de_linhas([['vida_max',erro]])

    def test_formula_sem_cache_parcial_tambem_rejeitada(self):
        w=Workbook();s=w.active;s.title='ANALISE'
        s.append(['chave','valor','célula','parte'])
        s.append(['formato.versao','11','','cabeçalho'])
        s.append(['nome','teste','','entrada'])
        s.append(['defesa','=10+1','','resultado'])
        b=io.BytesIO();w.save(b)
        with self.assertRaisesRegex(FichaIlegivel,'sem resultado calculado'):
            de_xlsx(b.getvalue())

    def test_colisao_v4_nao_e_aceita_por_numero(self):
        self.assertIsNone(variante(de_linhas([['formato.versao','4'],['regra.nivel_inicial','2']])))
        self.assertEqual(variante(de_linhas([['formato.versao','4'],['tr.fisico.bonus','2']])), 'legado-tr-v4')
        self.assertIsNone(variante(de_csv('chave,valor\nformato.versao,99\nnome,007\n')))

    def test_csv_truncado_ou_campo_excessivo_tem_erro_de_leitura(self):
        import csv
        for texto in ('chave,valor\nformato.versao,11\nnome,"texto interrompido',
                      'chave,valor\nformato.versao,11\nnome,'+'x'*(csv.field_size_limit()+1)):
            with self.subTest(tamanho=len(texto)), self.assertRaisesRegex(FichaIlegivel,'CSV.*malformado'):
                de_csv(texto)

    def test_csv_com_aspas_e_quebras_preserva_texto_valido(self):
        texto='chave,valor\nformato.versao,11\nnome,"Nome, com ""aspas"""\ncustom.dano.1.definicao,"=literal\nsegunda linha *?~"\n'
        f=de_csv(texto)
        self.assertEqual(f['nome'].valor,'Nome, com "aspas"')
        self.assertEqual(f['custom.dano.1.definicao'].valor,'=literal\nsegunda linha *?~')


if __name__ == '__main__':
    unittest.main()
