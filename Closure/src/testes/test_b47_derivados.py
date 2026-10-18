"""Contas e lacunas reais do contrato: casos pequenos, sem calcular planilhas."""
import unittest

from closure_bot.ficha_corretor import Resultado, Aprovados, conferir
from closure_bot.ficha_configuracao import conferir_efeitos, impressao_exata
from closure_bot.ficha_derivados_b47 import conferir_derivados, resultado_numerico, conferir_tr_entidade
from closure_bot.ficha_b47 import conferir_familias
from closure_bot.ficha_magia import conferir_montagem
from testes.test_b47_integracao import completa, trocar, contexto, aprovar, REF


def ficha():
    return trocar(completa(),maestria=1,classe_maxima=1,refino_de_graca=1,classe_0_gratis=2,
                  iniciativa='d20 + 2',cd_de_feitico=10,conjuracao='d20 + 2',corpo_a_corpo='d20 + 4',
                  a_distancia='d20 + 3',deslocamento='9 m',morrendo_prazo='3 rodadas',
                  tr__fisico__treino=1,tr__espirito__treino=1)


def efeito(f, caixa, n, como='somar', i=1, fonte='Decisão sintética'):
    return trocar(f,**{f'efeito.{i}.{k}':v for k,v in dict(ligado=1,caixa=caixa,como=como,valor=n,
                        tipo_de_fonte='Decisão do mestre',fonte=fonte).items()})


def derivados(f):
    c,r,ref=contexto(f)
    conferir_efeitos(f,c,r)
    conferir_derivados(f,ref,c,r)
    return r


class Derivados(unittest.TestCase):
    def test_validos_separam_conta_e_seletor_ausente(self):
        r=derivados(ficha())
        self.assertFalse(r.problemas,r.problemas)
        self.assertIn('iniciativa: 2',r.conferidos)
        self.assertFalse(any(c.startswith('conjuracao:') for c in r.conferidos))
        self.assertTrue(any('conjuracao: seletor' in c for c in r.nao_conferido))

    def test_iniciativa_adulterada_sem_aviso(self):
        r=derivados(trocar(ficha(),iniciativa='d20 + 999'))
        self.assertIn('iniciativa',[p.campo for p in r.problemas])

    def test_efeito_soma_iniciativa_uma_vez(self):
        f=efeito(trocar(ficha(),iniciativa='d20 + 7',buff__iniciativa=2),'Iniciativa',3)
        r=derivados(f)
        self.assertFalse(any(p.campo=='iniciativa' for p in r.problemas))
        self.assertIn('iniciativa: 7',r.conferidos)
        self.assertIn('buff.iniciativa',[p.campo for p in r.pendencias])

    def test_troca_zero_independe_do_atributo_omitido(self):
        for caixa,k,saida in [('Conjuração','conjuracao','d20 + 0'),('CD de feitiço','cd_de_feitico',0),
                               ('Corpo a corpo','corpo_a_corpo','d20 + 0'),('À distância','a_distancia','d20 + 0')]:
            with self.subTest(caixa=caixa):
                f=efeito(trocar(ficha(),**{k:saida,'buff.'+k:9}),caixa,0,'trocar por')
                efeito(f,caixa,77,i=2,fonte='Outra fonte')
                r=derivados(f)
                self.assertIn(k+': 0',r.conferidos)
                self.assertFalse(any(p.campo==k for p in r.problemas))

    def test_resultados_impossiveis_sao_divergencias_mesmo_sem_seletor(self):
        for k in ('cd_de_feitico','conjuracao','corpo_a_corpo','a_distancia'):
            r=derivados(trocar(ficha(),**{k:999}))
            self.assertIn(k,[p.campo for p in r.problemas])

    def test_soma_na_cd_nao_escolhe_atributo_pelo_total(self):
        r=derivados(efeito(trocar(ficha(),cd_de_feitico=13),'CD de feitiço',3))
        self.assertFalse(any(p.campo=='cd_de_feitico' for p in r.problemas))
        self.assertFalse(any(c.startswith('cd_de_feitico:') for c in r.conferidos))

    def test_resultados_vazios_sao_informacao_insuficiente(self):
        r=derivados(trocar(ficha(),iniciativa='',maestria='',morrendo_prazo=''))
        self.assertTrue({'iniciativa','maestria','morrendo_prazo'}<={p.campo for p in r.pendencias})
        self.assertFalse(r.problemas)

    def test_erro_em_ajuste_nao_vira_zero(self):
        r=derivados(trocar(ficha(),buff__iniciativa='muito'))
        self.assertIn('buff.iniciativa',[p.campo for p in r.problemas])
        self.assertFalse(any(c.startswith('iniciativa:') for c in r.conferidos))

    def test_formatacao_restrita_nao_converte_texto_livre(self):
        self.assertEqual(resultado_numerico('d20 + -1,5','d20'),-1.5)
        self.assertEqual(resultado_numerico('4,5 m','metros'),4.5)
        for v in ('=1+1','007*?~','VERDADEIRO',False,'d20 + 2 + 999'):
            self.assertIsNone(resultado_numerico(v,'d20'))

    def test_progressao_derivada_nao_depende_do_resultado(self):
        r=derivados(trocar(ficha(),maestria=999,classe_maxima=7,refino_de_graca=10,classe_0_gratis=99))
        self.assertTrue({'maestria','classe_maxima','refino_de_graca','classe_0_gratis'}<={p.campo for p in r.problemas})

    def test_classe_zero_gratis_nao_e_quantidade_de_dados(self):
        f=trocar(ficha(),nivel=30,maestria=REF.magia.maestria[30],classe_maxima=7,refino_de_graca=8,classe_0_gratis=5)
        r=derivados(f)
        self.assertFalse(any(p.campo in ('classe_0_gratis','refino_de_graca') for p in r.problemas))

    def test_janela_sequelas_extras_e_derrota(self):
        for extras,esperado in [(0,'2 rodadas'),(1,'1 rodada'),(2,'Derrotado na hora'),(10,'Derrotado na hora')]:
            r=derivados(trocar(ficha(),sequela__1=1,sequela__extras=extras,morrendo_prazo=esperado))
            self.assertFalse(any(p.campo=='morrendo_prazo' for p in r.problemas))
            self.assertIn('morrendo_prazo: '+esperado,r.conferidos)

    def test_sequela_invalida_nao_certifica_janela(self):
        for v in (-1,1.5,'duas'):
            r=derivados(trocar(ficha(),sequela__extras=v))
            self.assertIn('sequela.extras',[p.campo for p in r.problemas])
            self.assertFalse(any(c.startswith('morrendo_prazo:') for c in r.conferidos))

    def test_dois_tr_independem_de_avisos_exportados(self):
        for quantos in (0,1,2,3,4):
            f=ficha()
            for i,k in enumerate(('fisico','vigor','intelecto','espirito')):trocar(f,**{'tr.'+k+'.treino':int(i<quantos)})
            r=derivados(f)
            self.assertEqual(any(p.campo=='tr' for p in r.pendencias),quantos<2)
            self.assertEqual(any(p.campo=='tr' for p in r.problemas),quantos>2)

    def test_tr_entidades_independentes(self):
        f=trocar(ficha(),invocacao__1__tr_treinado='Físico',invocacao__1__atributo_fisico='FORÇA',
                 invocacao__2__tr_treinado='Vigor',invocacao__2__atributo_fisico='DESTREZA')
        c,r,ref=contexto(f)
        for b in ('invocacao.1','invocacao.2'):conferir_tr_entidade(f,c,r,b)
        self.assertFalse(r.problemas+r.pendencias)
        trocar(f,invocacao__2__atributo_fisico='Essência')
        conferir_tr_entidade(f,c,r,'invocacao.2')
        self.assertEqual([p.campo for p in r.problemas],['invocacao.2.atributo_fisico'])


class Deslocamento(unittest.TestCase):
    def test_sem_inventario_nao_certifica_marcha(self):
        for v in ('9 m','4,5 m','0 m'):
            r=derivados(trocar(ficha(),deslocamento=v))
            self.assertFalse(any(p.campo=='deslocamento' for p in r.problemas))
            self.assertFalse(any(c.startswith('deslocamento:') for c in r.conferidos))

    def test_marcha_impossivel_e_exaustao(self):
        for exaustao,v in [(0,'999 m'),(2,'9 m'),(3,'9 m')]:
            r=derivados(trocar(ficha(),exaustao=exaustao,deslocamento=v))
            self.assertIn('deslocamento',[p.campo for p in r.problemas])

    def test_troca_apos_penalidades_sobrepoe_buff_e_soma(self):
        f=efeito(trocar(ficha(),buff__deslocamento=10,exaustao=3,deslocamento='0 m'),'Deslocamento',0,'trocar por')
        efeito(f,'Deslocamento',20,i=2,fonte='Segunda fonte')
        self.assertIn('deslocamento: 0',derivados(f).conferidos)

    def test_campanha_zero_e_entrada_nao_exportada(self):
        f=trocar(ficha(),deslocamento='0 m');c,r,ref=contexto(f);c.regras['deslocamento_base']=0
        conferir_derivados(f,ref,c,r)
        self.assertIn('deslocamento: 0',r.conferidos)


class EfeitosFamilias(unittest.TestCase):
    def test_efeito_altera_total_sem_alterar_livres_ou_tecnica(self):
        f=efeito(trocar(ficha(),invocacao__1__familia__1='Área',invocacao__1__limite_familias=4,invocacao__1__limite_livres=1),
                 'Invocações · famílias da trilha',1)
        c,r,ref=contexto(f);conferir_efeitos(f,c,r)
        livres,abertas=conferir_familias(f,ref.magia,'invocacao.1',r.problemas)
        self.assertEqual(livres,{'Área'})
        self.assertFalse(r.problemas)
        self.assertFalse(any('famílias da trilha' in s for s in r.nao_conferido))

    def test_troca_total_antes_do_bonus_nao_autonoma(self):
        f=efeito(trocar(ficha(),invocacao__1__autonomia='Não autônoma',invocacao__1__limite_familias=6,
                        invocacao__1__limite_livres=2),'Invocações · famílias da trilha',5,'trocar por')
        c,r,ref=contexto(f);conferir_efeitos(f,c,r)
        conferir_familias(f,ref.magia,'invocacao.1',r.problemas)
        self.assertFalse(r.problemas,r.problemas)

    def test_fracao_conflito_e_limite_nove(self):
        for v in (1.5,10,-1):
            f=efeito(ficha(),'Invocações · famílias da trilha',v,'trocar por')
            c,r,ref=contexto(f);conferir_efeitos(f,c,r)
            self.assertEqual(conferir_familias(f,ref.magia,'invocacao.1',r.problemas),(None,None))
            self.assertTrue(r.problemas)

    def test_duas_linhas_identicas_aprovadas_nao_contam_duas_vezes(self):
        f=efeito(ficha(),'Iniciativa',2);efeito(f,'Iniciativa',2,i=2)
        campos={k:f['efeito.1.'+k].valor for k in ('caixa','como','valor','tipo_de_fonte','fonte')}
        a=Aprovados({impressao_exata('efeito','Decisão sintética',campos):'mestre'})
        c,r,ref=contexto(f,a);conferir_efeitos(f,c,r);conferir_derivados(f,ref,c,r)
        self.assertIsNone(c.aplicar('Iniciativa',2))
        self.assertFalse(any(s.startswith('iniciativa:') for s in r.conferidos))
        self.assertIn('efeito.2',[p.campo for p in r.pendencias])

    def test_invalido_nao_certifica_alvo_ignorando_a_linha(self):
        f=efeito(ficha(),'Iniciativa','não é número')
        r=derivados(f)
        self.assertFalse(any(s.startswith('iniciativa:') for s in r.conferidos))

    def test_nome_literal_com_curinga_nao_recebe_efeito_da_outra_pericia(self):
        from closure_bot.ficha_b47 import conferir_treinos
        f=ficha()
        for i,n in [(1,'Runa*'),(2,'Runas')]:
            trocar(f,**{f'custom.pericia.{i}.{k}':v for k,v in dict(tipo='Perícia',nome=n,atributo='Inteligência',mestre_viu=0).items()})
            trocar(f,**{f'personagem.pericia_custom.{i}.{k}':v for k,v in dict(nome=n,atributo='Inteligência',treino=0,especializacao=0,bonus=0,resultado=1 if i==1 else 8).items()})
        efeito(f,'Perícia · Runas',7)
        c,r,ref=contexto(f);conferir_efeitos(f,c,r);conferir_treinos(f,ref,c,r)
        self.assertFalse(any(p.campo.endswith('.resultado') for p in r.problemas),r.problemas)
        self.assertEqual(c.aplicar('Perícia · Runa*',1),1)
        trocar(f,personagem__pericia_custom__1__resultado=8)
        c,r,ref=contexto(f);conferir_efeitos(f,c,r);conferir_treinos(f,ref,c,r)
        self.assertIn('personagem.pericia_custom.1.resultado',[p.campo for p in r.problemas])


class FormasHerdadas(unittest.TestCase):
    def preparar(self,base='Projétil',**campos):
        f=trocar(ficha(),custom__forma__1__tipo='Forma',custom__forma__1__nome='Forma sintética',
                 custom__forma__1__base=base,custom__forma__1__mestre_viu=0,**campos)
        c,r,ref=contexto(f,aprovar(f,'custom.forma.1'))
        return f,c,r,ref

    def montagem(self,f,c,r,ref,b='feitico.1',**kwargs):
        conferir_montagem(f,ref.magia,b,valor_nivel(f),r.problemas,r.conferidos,r.nao_conferido,
                          familias=(set(REF.magia.familias),set(REF.magia.familias)),**kwargs)

    def test_herdada_nao_perde_proibicao_inescapavel(self):
        f,c,r,ref=self.preparar('Toque',feitico__1__classe=2,feitico__1__nome='Teste',feitico__1__forma='Forma sintética',
                               feitico__1__pecas='Inescapável',feitico__1__pe='6 PE')
        self.montagem(f,c,r,ref)
        self.assertTrue(any('Inescapável: só Projétil' in p.esperado for p in r.problemas))
        self.assertFalse(any('dano-base' in s for s in r.conferidos))

    def test_herdada_confere_liberacao_pelas_regras_da_base(self):
        f,c,r,ref=self.preparar(nivel=10,liberacao__1__classe=3,liberacao__1__nome='Teste',liberacao__1__forma='Forma sintética',
                               liberacao__1__pe='14 PE',liberacao__1__dano='12d8',liberacao__1__alcance='18 m, um alvo',liberacao__1__resolve='Acerto')
        self.montagem(f,c,r,ref,'liberacao.1',liberacao=True)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('dano-base 12d8' in s for s in r.conferidos))

    def test_desconto_forma_livre_personagem_usa_contrato_atual(self):
        f,c,r,ref=self.preparar('Explosão',nivel=6,feitico__1__classe=2,feitico__1__nome='Teste',feitico__1__forma='Forma sintética',
                               feitico__1__pe='6 PE',feitico__1__dano='5d8',feitico__1__alcance='Raio 3 m, a 18 m',feitico__1__resolve='TR, metade')
        self.montagem(f,c,r,ref)
        self.assertFalse(any(p.campo=='feitico.1.dano' for p in r.problemas),r.problemas)
        # Classe 2: seis pontos, Forma Leve custa 1 após desconto, restam 5d8.
        self.assertTrue(any('dano-base 5d8' in s for s in r.conferidos))

    def test_forma_alterada_mantem_motor_estruturado(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,feitico__1__classe=1,feitico__1__nome='Teste',feitico__1__forma='Forma sintética',
                               feitico__1__pe='3 PE',feitico__1__dano='3d8',feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
        self.montagem(f,c,r,ref)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('benefício numérico da Forma custom 3d8' in s for s in r.conferidos))

    def test_montagem_invalida_nao_certifica_beneficio(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,feitico__1__classe=1,feitico__1__nome='Teste',feitico__1__forma='Forma sintética',
                               feitico__1__pe='3 PE',feitico__1__pecas='Longe · Longe · Longe',feitico__1__dano='3d8')
        self.montagem(f,c,r,ref)
        self.assertTrue(r.problemas)
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_forma_alterada_nao_perde_incompatibilidade_rapido_reacao(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,nivel=10,feitico__1__classe=3,feitico__1__nome='Teste',
                               feitico__1__forma='Forma sintética',feitico__1__pecas='Rápido · Reação',feitico__1__pe='9 PE')
        self.montagem(f,c,r,ref)
        self.assertTrue(any('não combinar Rápido com Reação' in p.esperado for p in r.problemas))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_forma_alterada_conserva_identidade_da_base(self):
        f,c,r,ref=self.preparar('Toque',custom__forma__1__peso=0,feitico__1__classe=1,feitico__1__nome='Teste',
                               feitico__1__forma='Forma sintética',feitico__1__pecas='Inescapável',feitico__1__pe='3 PE')
        self.montagem(f,c,r,ref)
        self.assertTrue(any('Inescapável: só identidade Projétil' in p.esperado for p in r.problemas))
        self.assertFalse(any('benefício numérico' in s for s in r.conferidos))

    def test_liberacao_alterada_calcula_saldo_e_remate_no_teto(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,nivel=10,liberacao__1__classe=3,liberacao__1__nome='Teste',
                               liberacao__1__forma='Forma sintética',liberacao__1__pecas='Remate',liberacao__1__pe='14 PE',
                               liberacao__1__dano='9d8 = 40',liberacao__1__alcance='18 m, um alvo',liberacao__1__resolve='Acerto')
        self.montagem(f,c,r,ref,'liberacao.1',liberacao=True)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('benefício numérico da Forma custom 9d8' in s for s in r.conferidos))
        trocar(f,liberacao__1__dano='10d8 = 45')
        r.problemas.clear();self.montagem(f,c,r,ref,'liberacao.1',liberacao=True)
        self.assertIn('liberacao.1.dano',[p.campo for p in r.problemas])

    def test_adicionais_contam_no_teto_e_nao_alteram_media_base(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,nivel=10,feitico__1__classe=3,feitico__1__nome='Teste',
                               feitico__1__forma='Forma sintética',feitico__1__pecas='Salto',feitico__1__pe='9 PE',
                               feitico__1__dano='8d8 = 36 · +4d8',feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
        self.montagem(f,c,r,ref)
        self.assertFalse(r.problemas,r.problemas)
        trocar(f,feitico__1__dano='8d8 = 54 · +4d8')
        r.problemas.clear();self.montagem(f,c,r,ref)
        self.assertIn('feitico.1.dano',[p.campo for p in r.problemas])

    def test_rajada_confere_total_sem_multiplicar_por_tiros(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,nivel=6,feitico__1__classe=2,feitico__1__nome='Teste',
                               feitico__1__forma='Forma sintética',feitico__1__pecas='Rajada',feitico__1__pe='6 PE',
                               feitico__1__dano='5d8',feitico__1__alcance='18 m, um alvo · 3 tiros',feitico__1__resolve='Acerto')
        self.montagem(f,c,r,ref)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('distribuição por tiros/alvos' in s for s in r.nao_conferido))
        trocar(f,feitico__1__dano='15d8')
        r.problemas.clear();self.montagem(f,c,r,ref)
        self.assertIn('feitico.1.dano',[p.campo for p in r.problemas])

    def test_alma_simples_conta_metade_sem_conceder_permissao(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,nivel=10,feitico__1__classe=3,feitico__1__nome='Teste',
                               feitico__1__forma='Forma sintética',feitico__1__pecas='Toca a Alma',feitico__1__pe='9 PE',
                               feitico__1__dano='4d8',feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
        self.montagem(f,c,r,ref)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('Regra autorizada' in s for s in r.nao_conferido))

    def test_resolucao_custom_da_entidade_confere_bonus_independente(self):
        f,c,r,ref=self.preparar(custom__forma__1__peso=0,invocacao__1__atributo_acerto='Força',
                               invocacao__1__atributo__forca__base=2,invocacao__1__esp__1__classe=1,
                               invocacao__1__esp__1__nome='Teste',invocacao__1__esp__1__forma='Forma sintética',
                               invocacao__1__esp__1__pe='3 PE',invocacao__1__esp__1__resolve='Ataque +3',
                               invocacao__1__esp__1__dano='2d8',invocacao__1__esp__1__alcance='18 m, um alvo')
        self.montagem(f,c,r,ref,'invocacao.1.esp.1',entidade=True)
        self.assertFalse(r.problemas,r.problemas)
        self.assertTrue(any('bônus da resolução Ataque +3' in s for s in r.conferidos))
        trocar(f,invocacao__1__esp__1__resolve='Ataque +999')
        r.problemas.clear();self.montagem(f,c,r,ref,'invocacao.1.esp.1',entidade=True)
        self.assertIn('invocacao.1.esp.1.resolve',[p.campo for p in r.problemas])


class HerancaOrigemEquipamento(unittest.TestCase):
    def origem(self,base='Encarnado',rota='Fundamento'):
        f=trocar(ficha(),custom__1__tipo='Origem',custom__1__nome='Origem sintética',custom__1__mestre_viu=0,
                 custom__1__campo__base_do_livro=base,custom__1__campo__rota=rota,origem='Origem sintética')
        for i,(nome,_) in enumerate(list(REF.testes.pericias.values())[:4],1):trocar(f,**{f'custom.1.campo.pericia_{i}':nome})
        return f

    def test_pacote_herdado_conserva_concessao_de_treino(self):
        f=trocar(self.origem(),origem__marcante='Duas Vidas')
        for slug in list(REF.testes.pericias)[:10]:trocar(f,**{f'pericia.{slug}.treino':1})
        for slug in list(REF.testes.oficios)[:2]:trocar(f,**{f'oficio.{slug}.treino':1})
        r=conferir(f,REF,aprovados=aprovar(f,'custom.1'))
        self.assertFalse(any(p.campo=='treinos' for p in r.problemas+r.pendencias),r.problemas+r.pendencias)
        self.assertTrue(any(c.startswith('Treinos: 10 perícias, 2 Ofícios') for c in r.conferidos))
        self.assertTrue(any(c=='Origem Origem sintética (base Encarnado)' for c in r.conferidos))
        self.assertEqual(f['origem'].valor,'Origem sintética')

    def test_rota_contraditoria_nao_herda_beneficios(self):
        f=self.origem(rota='Técnica Marcial sem energia')
        c,r,ref=contexto(f)
        self.assertFalse(c.registros['custom.1'].valida)
        self.assertIn('custom.1.campo.rota',[p.campo for p in r.problemas])

    def test_sem_base_nao_aceita_capacidade_de_outra_origem(self):
        f=trocar(self.origem('Nenhuma'),origem__marcante='Duas Vidas')
        r=conferir(f,REF,aprovados=aprovar(f,'custom.1'))
        self.assertIn('origem.marcante',[p.campo for p in r.problemas])
        self.assertFalse(any(c.startswith('Vida ') for c in r.conferidos))

    def test_menor_custom_exige_marcante_vinculada(self):
        f=trocar(self.origem(),origem__marcante='Duas Vidas',origem__menor_1='Menor sintética',
                 custom__2__tipo='Menor',custom__2__nome='Menor sintética',custom__2__mestre_viu=0,
                 custom__2__campo__origem='Origem sintética',custom__2__campo__exige_marcante='Outra marcante')
        r=conferir(f,REF,aprovados=aprovar(f,'custom.1'))
        self.assertIn('origem.menor_1',[p.campo for p in r.problemas])

    def ferramenta(self,base='Torre',volume=''):
        return trocar(ficha(),custom__1__tipo='Ferramenta amaldiçoada',custom__1__nome='Ferramenta sintética',
                      custom__1__mestre_viu=0,custom__1__campo__base=base,custom__1__campo__grau='Grau 4',
                      custom__1__campo__volume=volume)

    def test_ferramenta_herda_protecao_e_sobrescreve_volume_zero(self):
        f=self.ferramenta(volume=0)
        c,r,ref=contexto(f,aprovar(f,'custom.1'))
        self.assertFalse(r.problemas,r.problemas)
        self.assertEqual(ref.escudos['Ferramenta sintética'],REF.escudos['Torre'])
        self.assertEqual(ref.equipamento.pecas['Ferramenta sintética'].volume,0)

    def test_ferramenta_duas_maos_nao_concede_escudo_em_uso(self):
        f=trocar(self.ferramenta('Espadão'),em_uso__principal='Ferramenta sintética',em_uso__secundaria='Torre')
        c,r,ref=contexto(f,aprovar(f,'custom.1'))
        self.assertIn('Ferramenta sintética',ref.duas_maos)
        from closure_bot.ficha_b47 import conferir_contas_b47
        certos=[];pendencias=[]
        problemas,_=conferir_contas_b47(f,ref,None,certos,pendencias)
        self.assertFalse(any(p.campo in ('defesa','protecao') for p in problemas),problemas)

    def test_ferramenta_base_item_comum(self):
        base=next(iter(REF.equipamento.itens))
        f=self.ferramenta(base,0)
        c,r,ref=contexto(f,aprovar(f,'custom.1'))
        self.assertFalse(r.problemas,r.problemas)
        self.assertEqual(ref.equipamento.itens['Ferramenta sintética'],0)

    def test_mudar_base_custom_invalida_aprovacao_da_ferramenta(self):
        f=self.ferramenta('Item sintético')
        trocar(f,custom__2__tipo='Item comum',custom__2__nome='Item sintético',custom__2__mestre_viu=0,custom__2__campo__volume=2)
        c,r,_=contexto(f)
        a=Aprovados({d.impressao:'mestre' for d in c.registros.values()})
        c,r,ref=contexto(f,a)
        self.assertTrue(c.registros['custom.1'].aprovada)
        trocar(f,custom__2__campo__volume=3)
        c,r,ref=contexto(f,a)
        self.assertFalse(c.registros['custom.1'].aprovada)
        self.assertNotIn('Ferramenta sintética',ref.equipamento.itens)


class ReservaProfunda(unittest.TestCase):
    def conferir_pe(self,f):
        from closure_bot.ficha_b47 import conferir_contas_b47
        c,r,ref=contexto(f,aprovar(f,'custom.talento.1'))
        conferir_efeitos(f,c,r)
        ps,nc=conferir_contas_b47(f,ref,None,r.conferidos,r.pendencias)
        r.problemas+=ps;r.nao_conferido+=nc
        return r

    def preparar(self):
        return trocar(ficha(),custom__talento__1__tipo='Talento',custom__talento__1__nome='Reserva sintética',
                      custom__talento__1__base='Reserva Profunda',custom__talento__1__mestre_viu=0,
                      passiva__1='Reserva sintética',energia_max=11)

    def test_herda_ganho_numerico_sem_executar_descricao(self):
        r=self.conferir_pe(self.preparar())
        self.assertIn('PE 11',r.conferidos)
        self.assertFalse(any(p.campo=='energia_max' for p in r.problemas))

    def test_efeito_identificado_nao_soma_duas_vezes(self):
        f=efeito(self.preparar(),'PE máximo',3,fonte='Reserva sintética')
        r=self.conferir_pe(f)
        self.assertIn('PE 11',r.conferidos)
        self.assertFalse(any(p.campo=='energia_max' for p in r.problemas))

    def test_buff_ambiguo_nao_recebe_certificacao_duplicada(self):
        r=self.conferir_pe(trocar(self.preparar(),buff__energia=3))
        self.assertFalse(any(c.startswith('PE ') for c in r.conferidos))
        self.assertIn('energia_max',[p.campo for p in r.pendencias])


def valor_nivel(f):
    return f['nivel'].valor


if __name__=='__main__':
    unittest.main()
