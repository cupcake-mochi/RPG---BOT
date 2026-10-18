"""Revisão B47: dependências, distribuição e Controle sem confiar em avisos."""
import unittest

from closure_bot.ficha_corretor import Aprovados, Resultado, conferir
from closure_bot.ficha_magia import conferir_montagem
from testes.test_b47_integracao import completa, trocar, contexto, REF


class RequisitosOrigem(unittest.TestCase):
    def ficha(self,origem='Receptáculo',marcante='Coexistência',menor='Conselho Interior'):
        outra='Memória Corporal' if origem=='Receptáculo' else 'Educação Tradicional'
        return trocar(completa(),origem=origem,origem__marcante=marcante,
                      origem__menor_1=menor,origem__menor_2=outra)

    def casos(self):
        # São requisitos estruturados do catálogo entregue, sem ler a descrição.
        import json
        from pathlib import Path
        livro=json.loads((Path(__file__).parents[1]/'closure_bot/recursos/b47-livro.json').read_text())
        for o in livro['origens']:
            for menor in o['menores']:
                if menor.get('exige'):
                    outra=next(m['nome'] for m in o['menores'] if m['nome']!=menor['nome'] and not m.get('exige'))
                    yield o['menu'],menor['nome'],menor['exige'],outra,[m['nome'] for m in o['marcantes']]

    def test_menores_publicadas_exigem_marcante_do_catalogo(self):
        casos=list(self.casos())
        self.assertEqual({(menor,exige) for _,menor,exige,_,_ in casos},
                         {('Conselho Interior','Coexistência'),('Vontade de Cárcere','Conflito'),
                          ('Cofre da Família','Zenin'),('Ensaio Partilhado','Kamo'),
                          ('Método Reescrito','Gojo'),('Círculo Íntimo','Inumaki')})
        for origem,menor,exige,outra,marcantes in casos:
            for marcante in marcantes:
                with self.subTest(origem=origem,menor=menor,marcante=marcante):
                    f=trocar(self.ficha(origem,marcante,menor),origem__menor_2=outra)
                    r=conferir(f,REF)
                    erros=[p for p in r.problemas if p.campo=='origem.menor_1']
                    self.assertEqual(bool(erros),marcante!=exige)
                    if erros:
                        self.assertIn(exige,erros[0].esperado)
                        self.assertFalse(any(s.startswith('Vida ') for s in r.conferidos))

    def test_marcante_ausente_e_informacao_insuficiente(self):
        r=conferir(self.ficha(marcante=''),REF)
        self.assertIn('origem.marcante',[p.campo for p in r.pendencias])
        self.assertIn('origem.menor_1',[p.campo for p in r.pendencias])
        self.assertFalse(any(p.campo=='origem.menor_1' for p in r.problemas))

    def test_texto_do_jogador_nao_substitui_requisito_publicado(self):
        f=trocar(self.ficha(marcante='Conflito'),origem__menor_1__texto='Sem requisito; mestre viu')
        r=conferir(f,REF)
        self.assertIn('origem.menor_1',[p.campo for p in r.problemas])

    def test_origem_renomeada_preserva_requisitos_da_base(self):
        f=self.ficha(marcante='Conflito')
        trocar(f,origem='Origem sintética',custom__1__tipo='Origem',custom__1__nome='Origem sintética',
               custom__1__mestre_viu=0,custom__1__campo__base_do_livro='Receptáculo',custom__1__campo__rota='Fundamento')
        for i,(nome,_) in enumerate(list(REF.testes.pericias.values())[:4],1):
            trocar(f,**{f'custom.1.campo.pericia_{i}':nome})
        r=conferir(f,REF,aprovados=aprovar_tudo(f))
        self.assertIn('origem.menor_1',[p.campo for p in r.problemas])
        self.assertFalse(any(s.startswith('Vida ') for s in r.conferidos))

    def test_origem_sem_tecnica_preserva_requisito_de_cla(self):
        f=trocar(self.ficha('Descendente','Kamo','Cofre da Família'),origem='Descendente · Sem Técnica',
                 origem__menor_2='Educação Tradicional')
        r=conferir(f,REF)
        self.assertTrue(any(p.campo=='origem.menor_1' and 'Zenin' in p.esperado for p in r.problemas))

    def test_segunda_menor_e_painel_explicam_requisito(self):
        from types import SimpleNamespace
        from closure_bot.cogs.ficha import paginas
        f=trocar(self.ficha(marcante='Conflito'),origem__menor_1='Memória Corporal',origem__menor_2='Conselho Interior')
        r=conferir(f,REF)
        self.assertIn('origem.menor_2',[p.campo for p in r.problemas])
        ps=paginas(r,f,SimpleNamespace(chave='closure',nome='Closure',avatar_url=None))
        texto=' '.join(c.value for p in ps for c in p.fields)
        self.assertIn('marcante exigida: Coexistência',texto)
        self.assertIn('origem.menor_2',texto)

    def test_menor_custom_com_marcante_ausente_fica_pendente(self):
        f=trocar(self.ficha(marcante='',menor='Menor sintética'),
                 custom__1__tipo='Menor',custom__1__nome='Menor sintética',custom__1__mestre_viu=0,
                 custom__1__campo__origem='Receptáculo',custom__1__campo__exige_marcante='Coexistência')
        r=conferir(f,REF,aprovados=aprovar_tudo(f))
        self.assertIn('origem.menor_1',[p.campo for p in r.pendencias])
        self.assertFalse(any(p.campo=='origem.menor_1' for p in r.problemas))


def aprovar_tudo(f):
    c,_,_=contexto(f)
    return Aprovados({d.impressao:'mestre sintético' for d in c.registros.values()})


def montagem(f,base='feitico.1',*,aprovados=None,livres=(),entidade=False,familias_extra=()):
    c,r,ref=contexto(f,aprovados if aprovados is not None else aprovar_tudo(f))
    conferir_montagem(f,ref.magia,base,f['nivel'].valor,r.problemas,r.conferidos,r.nao_conferido,
                     familias=(set(livres),set(REF.magia.familias)|set(familias_extra)),entidade=entidade,pendencias=r.pendencias)
    return c,r


def forma(base='Projétil',**extras):
    f=trocar(completa(),nivel=10,custom__forma__1__tipo='Forma',custom__forma__1__nome='Forma sintética',
             custom__forma__1__base=base,custom__forma__1__peso=0,custom__forma__1__mestre_viu=0,
             feitico__1__nome='Teste',feitico__1__classe=3,feitico__1__forma='Forma sintética',
             feitico__1__pe='9 PE',feitico__1__dano='9d8',feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
    return trocar(f,**extras)


class RestricaoEmbutida(unittest.TestCase):
    def ficha(self):
        return forma(custom__restricao__1__nome='Assinatura? sintética',custom__restricao__1__base='Gesto',
                     custom__restricao__1__mestre_viu=0,custom__forma__1__restricao_embutida='Assinatura? sintética',
                     feitico__1__pecas='Longe',feitico__1__dano='9d8',feitico__1__alcance='36 m, um alvo')

    def test_restricao_custom_embutida_valida_e_paga_so_melhoria(self):
        c,r=montagem(self.ficha())
        self.assertTrue(c.registros['custom.forma.1'].valida)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('benefício numérico da Forma custom 9d8' in s for s in r.conferidos))

    def test_aprovar_so_forma_nao_aprova_restricao_embutida(self):
        f=self.ficha();c,_,_=contexto(f)
        a=Aprovados({c.registros['custom.forma.1'].impressao:'mestre'})
        _,r=montagem(f,aprovados=a)
        self.assertTrue(any('custom.restricao.1.nome'==p.campo for p in r.pendencias))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))
        self.assertTrue(any('sem aprovação' in s for s in r.nao_conferido))

    def test_mudar_restricao_invalida_aprovacao_da_forma_tambem(self):
        f=self.ficha();a=aprovar_tudo(f)
        trocar(f,custom__restricao__1__devolucao='Média')
        c,_,_=contexto(f,a)
        self.assertFalse(c.registros['custom.restricao.1'].aprovada)
        self.assertFalse(c.registros['custom.forma.1'].aprovada)

    def test_mudar_lembrete_nao_invalida_aprovacao_da_dependencia(self):
        f=self.ficha();a=aprovar_tudo(f)
        trocar(f,custom__restricao__1__mestre_viu=1)
        c,_,_=contexto(f,a)
        self.assertTrue(c.registros['custom.restricao.1'].aprovada)
        self.assertTrue(c.registros['custom.forma.1'].aprovada)

    def test_embutida_e_explicita_nao_devolvem_duas_vezes_mesma_base(self):
        f=trocar(self.ficha(),feitico__1__restricoes='Gesto')
        _,r=montagem(f)
        self.assertTrue(any('Restrição repetida' in p.esperado for p in r.problemas))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_condicional_herda_frequencia_mesmo_com_sufixo_de_peso(self):
        for base in ('Condicional (Leve)','Condicional (Média)'):
            with self.subTest(base=base):
                f=forma(custom__restricao__1__nome='Gatilho sintético',custom__restricao__1__base=base,
                        custom__restricao__1__mestre_viu=0,feitico__1__restricoes='Gatilho sintético · Uma Vez')
                c,r=montagem(f)
                self.assertEqual(c.registros['custom.restricao.1'].efetivos['frequencia'],'Sim')
                self.assertTrue(any('Duas Restrições de frequência' in p.esperado for p in r.problemas))
                self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_frequencia_embutida_conta_com_restricao_selecionada(self):
        f=trocar(self.ficha(),custom__restricao__1__base='Condicional (Leve)',feitico__1__restricoes='Uma Vez')
        _,r=montagem(f)
        self.assertTrue(any('Duas Restrições de frequência' in p.esperado for p in r.problemas))

    def test_heranca_de_frequencia_respeita_nao_explicito(self):
        f=forma(custom__restricao__1__nome='Gatilho sintético',custom__restricao__1__base='Condicional (Leve)',
                custom__restricao__1__frequencia='Não',custom__restricao__1__mestre_viu=0,
                feitico__1__restricoes='Gatilho sintético · Uma Vez')
        c,r=montagem(f)
        self.assertEqual(c.registros['custom.restricao.1'].efetivos['frequencia'],'Não')
        self.assertFalse(any('frequência' in p.esperado for p in r.problemas))

    def test_tudo_ou_nada_considera_tr_da_condicao(self):
        f=forma(feitico__1__pecas='Condição: Lento',feitico__1__restricoes='Tudo ou Nada',
                feitico__1__dano='9d8',feitico__1__resolve='Acerto + TR')
        _,r=montagem(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('benefício numérico da Forma custom 9d8' in s for s in r.conferidos))
        trocar(f,feitico__1__pecas='')
        _,r=montagem(f)
        self.assertTrue(any('Tudo ou Nada exige TR' in p.esperado for p in r.problemas))

    def test_forma_nao_autoriza_familia_custom_pendente(self):
        f=forma(custom__familia__1__nome='Família sintética',custom__familia__1__estado='Neutra',
                custom__familia__1__mestre_viu=0,custom__forma__1__familia='Família sintética')
        c,_,_=contexto(f)
        a=Aprovados({c.registros['custom.forma.1'].impressao:'mestre'})
        _,r=montagem(f,aprovados=a,familias_extra=('Família sintética',))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))
        self.assertIn('custom.familia.1.nome',[p.campo for p in r.pendencias])
        _,r=montagem(f,familias_extra=('Família sintética',))
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('benefício numérico' in s for s in r.conferidos))


class LimitesMontagem(unittest.TestCase):
    def test_duas_condicoes_pesadas_nao_certificam_dano(self):
        f=forma(nivel=26,feitico__1__classe=7,feitico__1__pe='21 PE',
                feitico__1__pecas='Condição: Cego · Condição: Amedrontado',feitico__1__dano='7d8')
        _,r=montagem(f)
        self.assertTrue(any('uma condição Pesada' in p.esperado for p in r.problemas))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_inescapavel_nao_transforma_cura_em_automatica(self):
        f=forma(custom__forma__1__resultado=1,feitico__1__pecas='Inescapável',feitico__1__dano='Cura 6d8',feitico__1__resolve='Automático')
        _,r=montagem(f)
        self.assertTrue(any('Projétil de dano' in p.esperado for p in r.problemas))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_classe_acima_do_nivel_nao_certifica_motor_custom(self):
        f=forma(nivel=2,feitico__1__classe=3)
        _,r=montagem(f)
        self.assertIn('feitico.1.classe',[p.campo for p in r.problemas])
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_alias_de_condicao_pesada_conta_no_mesmo_limite(self):
        f=forma(nivel=26,custom__melhoria__1__nome='Cegueira sintética',custom__melhoria__1__base='Condição: Cego',
                custom__melhoria__1__mestre_viu=0,feitico__1__classe=7,feitico__1__pe='21 PE',
                feitico__1__pecas='Cegueira sintética · Condição: Amedrontado')
        _,r=montagem(f,livres=('Controle',))
        self.assertTrue(any('uma condição Pesada' in p.esperado for p in r.problemas))

    def test_condicoes_custom_sem_base_respeitam_limite_pesado(self):
        f=forma(nivel=26,feitico__1__classe=7,feitico__1__pe='21 PE',feitico__1__pecas='Condição sintética A · Condição sintética B')
        for i,sufixo in [(1,'A'),(2,'B')]:
            trocar(f,**{f'custom.melhoria.{i}.{k}':v for k,v in dict(nome='Condição sintética '+sufixo,peso='Pesada',modalidade='Condição',mestre_viu=0).items()})
        _,r=montagem(f,livres=('Controle',))
        self.assertTrue(any('uma condição Pesada' in p.esperado for p in r.problemas))

    def test_melhoria_de_controle_nao_e_condicao_por_supor_pelo_peso(self):
        f=forma(nivel=26,feitico__1__classe=7,feitico__1__pe='21 PE',feitico__1__dano='7d8',
                feitico__1__alcance='36 m, um alvo',feitico__1__pecas='Obstáculo sintético A · Obstáculo sintético B')
        for i,sufixo in [(1,'A'),(2,'B')]:
            trocar(f,**{f'custom.melhoria.{i}.{k}':v for k,v in dict(nome='Obstáculo sintético '+sufixo,peso='Pesada',modalidade='Melhoria',familia='Controle',exige_tr='Não',mestre_viu=0).items()})
        for nome in ('Forma sintética','Projétil'):
            trocar(f,feitico__1__forma=nome)
            _,r=montagem(f,livres=('Controle',))
            self.assertFalse(r.problemas,r.problemas)


def entidade(f,indice=1,nivel=2):
    b=f'invocacao.{indice}'
    valores={'nome':'Entidade sintética '+str(indice),'tipo':'Shikigami de técnica','aquisicao':'Espaço conhecido',
             'nivel':nivel,'classe':1,'entrada':1,'retorno':2,'pontos':'3 · 2 · 2 · 1 · 1',
             'vida.max':12,'defesa':12,'acerto':4,'cd':12,'deslocamento':9,'atributo_acerto':'Força',
             'tr_treinado':'Vigor','atributo_fisico':'Força','limite_familias':3,'limite_livres':1,
             'familia.1':'Mira','familia.2':'Área','familia.3':'Alcance'}
    for a,v in zip(('forca','destreza','constituicao','inteligencia','essencia'),(3,2,2,1,1)):
        valores['atributo.'+a+'.base']=v;valores['atributo.'+a+'.buff']=0;valores['atributo.'+a+'.total']=v
    for i,(nome,a) in enumerate(list(REF.testes.pericias.values())[:4],1):
        valores[f'pericia.{i}']=nome;valores[f'buff.pericia.{i}']=valores['atributo.'+a+'.base']+1
    trocar(f,**{b+'.'+k:v for k,v in valores.items()},invocacoes__defesa_atributo='Essência')
    return f


class DistribuicaoEntidade(unittest.TestCase):
    def test_distribuicao_valida_conserva_conferencias(self):
        r=conferir(entidade(completa()),REF)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('Invocação 1: vida.max 12'==s for s in r.conferidos))

    def test_falta_ponto_nao_certifica_numeros_dependentes(self):
        f=trocar(entidade(completa()),invocacao__1__atributo__forca__base=2,invocacao__1__pontos='2 · 2 · 2 · 1 · 1')
        r=conferir(f,REF)
        self.assertIn('invocacao.1.pontos',[p.campo for p in r.pendencias])
        self.assertFalse(any('Invocação 1' in s for s in r.conferidos))

    def test_resumo_adulterado_nao_certifica_contas_mesmo_com_numeros_corretos(self):
        r=conferir(trocar(entidade(completa()),invocacao__1__pontos='0 · 0 · 0 · 0 · 0'),REF)
        self.assertIn('invocacao.1.pontos',[p.campo for p in r.problemas])
        self.assertFalse(any('Invocação 1' in s for s in r.conferidos))

    def test_uma_entidade_invalida_nao_bloqueia_outra(self):
        f=entidade(entidade(completa()),2)
        trocar(f,invocacao__1__atributo__forca__base=6,invocacao__1__pontos='6 · 2 · 2 · 1 · 1')
        r=conferir(f,REF)
        self.assertFalse(any('Invocação 1' in s for s in r.conferidos))
        self.assertTrue(any('Invocação 2: vida.max 12'==s for s in r.conferidos))

    def test_atributo_vazio_nao_vira_zero(self):
        r=conferir(trocar(entidade(completa()),invocacao__1__atributo__forca__base=''),REF)
        self.assertIn('invocacao.1.atributo.forca.base',[p.campo for p in r.pendencias])
        self.assertFalse(any('Invocação 1' in s for s in r.conferidos))

    def test_resumo_vazio_e_informacao_insuficiente(self):
        r=conferir(trocar(entidade(completa()),invocacao__1__pontos=''),REF)
        self.assertIn('invocacao.1.pontos',[p.campo for p in r.pendencias])
        self.assertFalse(any(p.campo=='invocacao.1.pontos' for p in r.problemas))

    def test_distribuicao_invalida_preserva_pendencia_no_painel(self):
        from types import SimpleNamespace
        from closure_bot.cogs.ficha import paginas
        f=trocar(entidade(completa()),invocacao__1__atributo__forca__base=2,invocacao__1__pontos='2 · 2 · 2 · 1 · 1')
        r=conferir(f,REF)
        ps=paginas(r,f,SimpleNamespace(chave='closure',nome='Closure',avatar_url=None))
        texto=' '.join(c.value for p in ps for c in p.fields)
        self.assertIn('distribuir 9 pontos',texto)
        self.assertEqual(ps[0].colour.value,0xD4A017)


class ControleEntidade(unittest.TestCase):
    def ficha(self,*,zero=True,custom=True):
        f=entidade(forma(nivel=2))
        return trocar(f,invocacao__1__esp__1__nome='Controle sintético',invocacao__1__esp__1__classe=1,
                      invocacao__1__esp__1__forma='Forma sintética' if custom else 'Projétil',
                      invocacao__1__esp__1__pecas='Prende · Precisão' if zero else 'Prende',
                      invocacao__1__esp__1__pe='3 PE',invocacao__1__esp__1__dano='Sem dano' if zero else '1d8',
                      invocacao__1__esp__1__alcance='18 m, um alvo',
                      invocacao__1__esp__1__resolve='Ataque +6 · TR CD 14' if zero else 'Ataque +4 · TR CD 12')

    def analisar(self,f):
        return montagem(f,'invocacao.1.esp.1',entidade=True)[1]

    def test_saldo_zero_confere_cd_exclusiva_sem_usar_dano_exportado(self):
        r=self.analisar(self.ficha())
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('CD exclusiva do Controle 14; saldo calculado 0' in s for s in r.conferidos))
        self.assertTrue(any('rodada adicional e +2' in s for s in r.conferidos))

    def test_saldo_positivo_nao_aceita_bonus_de_cd_zero(self):
        f=self.ficha(zero=False);r=self.analisar(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('CD exclusiva do Controle 12; saldo calculado 1' in s for s in r.conferidos))
        trocar(f,invocacao__1__esp__1__resolve='Ataque +4 · TR CD 14')
        self.assertIn('invocacao.1.esp.1.resolve',[p.campo for p in self.analisar(f).problemas])

    def test_formula_atual_sem_bonus_obrigatorio_fica_pendente(self):
        f=trocar(self.ficha(),invocacao__1__esp__1__resolve='Ataque +6 · TR CD 12')
        r=self.analisar(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertIn('invocacao.1.esp.1.resolve',[p.campo for p in r.pendencias])
        self.assertFalse(any('CD exclusiva do Controle' in s for s in r.conferidos))
        trocar(f,invocacao__1__esp__1__resolve='Ataque +6 · TR CD 999')
        self.assertIn('invocacao.1.esp.1.resolve',[p.campo for p in self.analisar(f).problemas])

    def test_descartar_saldo_nao_compra_bonus(self):
        f=trocar(self.ficha(zero=False),invocacao__1__esp__1__dano='Sem dano')
        r=self.analisar(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('dano descartado' in s and 'saldo calculado 1' in s for s in r.nao_conferido))
        self.assertFalse(any('rodada adicional e +2' in s for s in r.conferidos))

    def test_alias_de_precisao_conserva_bonus_estruturado(self):
        f=trocar(self.ficha(),custom__melhoria__1__nome='Foco sintético',custom__melhoria__1__base='Precisão',
                 custom__melhoria__1__mestre_viu=0,invocacao__1__esp__1__pecas='Prende · Foco sintético')
        r=self.analisar(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('CD exclusiva do Controle 14' in s for s in r.conferidos))

    def test_exigir_tr_sem_familia_controle_nao_concede_bonus(self):
        f=trocar(self.ficha(),custom__melhoria__1__nome='Fagulha sintética',custom__melhoria__1__peso='Média',
                 custom__melhoria__1__familia='Mira',custom__melhoria__1__exige_tr='Sim',custom__melhoria__1__mestre_viu=0,
                 invocacao__1__esp__1__pecas='Fagulha sintética · Precisão',invocacao__1__esp__1__resolve='Ataque +6 · TR CD 12')
        r=self.analisar(f)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('não concede bônus de Controle' in s for s in r.conferidos))
        trocar(f,invocacao__1__esp__1__resolve='Ataque +6 · TR CD 14')
        self.assertIn('invocacao.1.esp.1.resolve',[p.campo for p in self.analisar(f).problemas])

    def test_forma_publicada_usa_mesmo_saldo_independente(self):
        for zero in (True,False):
            with self.subTest(zero=zero):
                r=self.analisar(self.ficha(zero=zero,custom=False))
                self.assertFalse(r.problemas,r.problemas)
                self.assertTrue(any('CD exclusiva do Controle' in s for s in r.conferidos))


if __name__=='__main__':
    unittest.main()
