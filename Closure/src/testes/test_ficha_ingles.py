"""English is a display boundary: numbers, flags, definitions and user names stay canonical."""
import copy
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from closure_bot.idiomas import usar
from closure_bot.cogs.ficha import paginas,COR
from closure_bot.ficha_corretor import Resultado,Problema,conferir,Referencias
from closure_bot.ficha_leitor import Campo,de_xlsx
from closure_bot.ficha_ingles import detail,patterns,line

PERSONA=NS(chave='kaltsit',nome="Kal'tsit",avatar_url=None)
ROOT=Path(__file__).resolve().parents[2]

class EnglishAnalysis(unittest.TestCase):
    def test_display_preserves_result_raw_values_and_colors_by_page(self):
        raw='Origem Própria CANARIO **Keep This**'
        r=Resultado('reprovada',problemas=[Problema('conta','vida_max','23','999')],
            pendencias=[Problema('aprovação','custom.origem.1.nome','aprovação da capacidade custom pelo mestre',raw,'abc')],
            conferidos=['Vida 23','PE 8','Caminho Bastião','Trilha Muro','Origem Latente','Feitiço 1: dano 2d8'],
            nao_conferido=['Treinos: totais compatíveis não provam origem de cada escolha nem quando uma especialização foi adquirida'])
        original=copy.deepcopy(r)
        with usar('en'):pages=paginas(r,{'nome':Campo(raw,'','')},PERSONA,{'edicao_livro':'R52'})
        self.assertEqual(r,original)
        alltext=json.dumps([p.to_dict() for p in pages],ensure_ascii=False)
        self.assertIn('reported 999; expected 23',alltext)
        self.assertIn('GM approval of the custom ability',alltext)
        self.assertIn(raw,alltext)
        self.assertIn('`custom.origem.1.nome`',alltext)
        self.assertIn('**Spells and techniques**',alltext)
        self.assertEqual(next(p for p in pages if p.description=='**Spells and techniques**').color.value,COR['aprovada'])
        self.assertEqual(pages[0].color.value,COR['reprovada'])
        for p in pages:
            self.assertLessEqual(len(p),6000)
            self.assertTrue(all(len(f.value)<=1024 and len(f.name)<=256 for f in p.fields))
            self.assertTrue(p.footer.text.startswith('Page '))
        with usar('pt-BR'):self.assertTrue(paginas(r,{},PERSONA)[0].title.startswith('Ficha'))
    def test_all_audited_patterns_match_and_preserve_captured_data(self):
        data,_=patterns()
        for pt,en in data.items():
            # Already-formatted values must not undergo another numeric conversion.
            val=lambda m:'CANARIO_'+m[1]
            original=re.sub(r'\{(\d+)(?::[^}]+)?\}',val,pt)
            expected=re.sub(r'\{(\d+)(?::[^}]+)?\}',val,en)
            self.assertEqual(detail(original),expected,pt)
        self.assertEqual(detail('texto arbitrário CANARIO_USUARIO'),'texto arbitrário CANARIO_USUARIO')
    def test_articles_in_known_instructions_are_english_but_reported_values_stay_raw(self):
        self.assertEqual(detail('escolha um Caminho'), 'choose a Path')
        self.assertEqual(detail('escolha uma Trilha'), 'choose a Branch')
        self.assertIn('escolha um Caminho', line(Problema('escolha', 'caminho', 'escolha um Caminho', 'escolha um Caminho')))

    def test_long_reports_keep_every_issue(self):
        problems=[Problema('custom',f'custom.forma.{i}.nome','cadastro próprio completo e aprovado pelo mestre',f'CUSTOM_{i:03d}') for i in range(70)]
        with usar('en'):pages=paginas(Resultado('reprovada',problemas=problems),{},PERSONA)
        text='\n'.join(f.value for p in pages for f in p.fields)
        for i in range(70):self.assertIn(f'CUSTOM_{i:03d}',text)
        self.assertTrue(all(len(p)<=6000 and all(len(f.value)<=1024 for f in p.fields) for p in pages))
    def test_real_fixture_counts_unchanged_between_languages(self):
        path=Path(__file__).parent/'dados/ficha_analise_kaori.xlsx'
        if not path.exists():self.skipTest('fixture unavailable')
        sheet=de_xlsx(path);r=conferir(sheet,Referencias.do_livro(ROOT/'dados'));before=copy.deepcopy(r)
        with usar('en'):ps=paginas(r,sheet,PERSONA)
        self.assertEqual(r,before)
        self.assertIn(str(len(r.problemas))+' error(s)',ps[0].fields[0].value)
        self.assertNotIn('Não deu',json.dumps([p.to_dict() for p in ps]))
