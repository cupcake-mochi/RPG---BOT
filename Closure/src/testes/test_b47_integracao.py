"""B47: fixtures sintéticas por chave, sem gerador completo, Google ou modelos."""
import copy
import io
import json
import random
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from closure_bot.ficha_leitor import Campo, de_linhas
from closure_bot.ficha_corretor import Referencias, RegrasDaCampanha, Aprovados, Resultado, conferir
from closure_bot.ficha_esquema import campos_b47, tipo
from closure_bot.ficha_configuracao import ContextoB47, PADRAO, conferir_regras, conferir_efeitos, impressao_exata
from closure_bot.ficha_custom import preparar_custom
from closure_bot.ficha_b47 import conferir_familias, conferir_contas_b47, conferir_treinos

RAIZ=Path(__file__).resolve().parents[2]
REF=Referencias.do_livro(RAIZ/'dados')


def trocar(f, **valores):
    for k,v in valores.items():
        k=k.replace('__','.')
        f[k]=Campo(v,campos_b47().get(k,{}).get('origem',''),campos_b47().get(k,{}).get('parte','entrada'))
    return f


def completa():
    f={k:Campo(0 if tipo(k)=='booleano' else '',v['origem'],v['parte']) for k,v in campos_b47().items()}
    trocar(f,formato__versao=11,ficha__sistema='Ciclo Maldito',ficha__livro='Ciclo Maldito R51',nome='Exemplo sintético',
           caminho='Bastião',trilha='Muro',origem='Latente',nivel=2,marco__corpo=0,marco__leque=0,marco__refino=0,
           vida_max=23,energia_max=8,integridade_max=26,protecao=1,defesa=13,espacos_de_feitico=3,
           trocou_por_arma='Não trocou',tecnica__rota__nome='Fundamento',morrendo_aguentar=6,morrendo_insistir_1=8,morrendo_insistir_2=12)
    for a,v in zip(('forca','destreza','constituicao','inteligencia','essencia'),(3,2,2,1,1)):
        trocar(f,**{f'atributo.{a}.base':v,f'atributo.{a}.corpo':0})
    for k,v in PADRAO.items():trocar(f,**{'regra.'+k:v})
    livro=json.loads((RAIZ/'src/closure_bot/recursos/b47-livro.json').read_text())
    for k,v in livro['xp'].items():trocar(f,**{'regra.xp.'+k:v})
    for i,k in enumerate(k for k in f if k.startswith('tecnica.familia.')):
        trocar(f,**{k:'Livre' if i<2 else 'Fechada' if i<5 else 'Neutra'})
    trocar(f,regra__familias_total=9,regra__familias_neutras=4)
    return f


def contexto(f,aprovados=None):
    r=Resultado('aprovada');c=ContextoB47(aprovados=aprovados or Aprovados())
    ref=preparar_custom(f,REF,c,r)
    from dataclasses import replace
    ref=replace(ref,magia=replace(ref.magia,contexto=c))
    return c,r,ref


def aprovar(f,raiz):
    c,r,ref=contexto(f)
    return Aprovados({c.registros[raiz].impressao:'mestre sintético'})


class Contrato(unittest.TestCase):
    def test_fixture_completa_executa_contas_sem_certificar_partes_ausentes(self):
        r=conferir(completa(),REF)
        self.assertEqual(r.problemas,[])
        self.assertIn('Vida 23',r.conferidos)
        self.assertEqual(r.veredito,'pendente')
        self.assertTrue(any('Carga:' in s for s in r.nao_conferido))

    def test_ordem_e_endereco_nao_sao_identidade(self):
        f=completa();linhas=list(f.items());random.Random(5).shuffle(linhas)
        novo={k:Campo(v.valor,'OUTRA!ZZ999',v.parte) for k,v in linhas}
        a,b=conferir(f,REF),conferir(novo,REF)
        self.assertEqual(a.veredito,b.veredito)
        self.assertEqual(set(a.conferidos),set(b.conferidos))

    def test_faltante_nao_e_vazio_nem_zero(self):
        f=completa();del f['efeito.30.valor']
        r=conferir(f,REF)
        self.assertEqual(r.veredito,'pendente')
        self.assertFalse(r.conferidos)
        self.assertTrue(any('exportação completa' in p.esperado for p in r.pendencias))

    def test_linha_extra_nao_muda_identidade_nem_certifica_variante(self):
        f=trocar(completa(),**{'extra.desconhecida':'007'})
        r=conferir(f,REF)
        self.assertTrue(any('extra.desconhecida' in s for s in r.nao_conferido))
        self.assertIn('Vida 23',r.conferidos)

    def test_ficha_branca_nao_aprova_personagem(self):
        f=completa();trocar(f,nome='',caminho='',origem='',trilha='',nivel='')
        r=conferir(f,REF)
        self.assertNotEqual(r.veredito,'aprovada')
        self.assertIn('nome',[p.campo for p in r.pendencias])

    def test_adulteracao_sem_avisos(self):
        f=trocar(completa(),vida_max=999,defesa=999)
        r=conferir(f,REF)
        self.assertEqual(r.veredito,'reprovada')
        self.assertTrue({'vida_max','defesa'}<={p.campo for p in r.problemas})

    def test_entrada_nao_numerica_nao_quebra_nem_vira_zero(self):
        for k in ('marco.refino','atributo.forca.base','invocacao.1.atributo.forca.buff'):
            f=trocar(completa(),**{k:'muito'})
            r=conferir(f,REF)
            self.assertEqual(r.veredito,'reprovada')
            self.assertFalse(r.conferidos)


class CampanhaEfeitos(unittest.TestCase):
    def test_regra_declarada_divergente_nao_dirige_conta(self):
        f=trocar(completa(),regra__atributos_pontos=999,regra__atributos_pontos__campanha=999)
        r=conferir(f,REF)
        self.assertTrue(any(p.regra=='campanha' for p in r.problemas))

    def test_campanha_autorizada_e_usada(self):
        f=trocar(completa(),regra__atributos_pontos=10,regra__atributos_pontos__campanha=10,atributo__forca__base=4)
        c=RegrasDaCampanha(nome='teste',valores={'atributos_pontos':10})
        r=conferir(f,REF,c)
        self.assertFalse(any(p.regra=='campanha' for p in r.problemas))

    def test_zero_de_campanha_e_explicito(self):
        f=trocar(completa(),regra__deslocamento_base=0,regra__deslocamento_base__campanha=0)
        r=Resultado('aprovada');rs=conferir_regras(f,RegrasDaCampanha(valores={'deslocamento_base':0}),r)
        self.assertEqual(rs['deslocamento_base'],0);self.assertEqual(r.problemas,[])

    def efeito(self,f,i=1,**kw):
        dados={'ligado':1,'caixa':'Vida máxima','como':'somar','valor':2,'tipo_de_fonte':'Decisão do mestre','fonte':'concessão sintética'}
        dados.update(kw)
        return trocar(f,**{f'efeito.{i}.{k}':v for k,v in dados.items()})

    def test_somar_uma_vez_e_fontes_nao_sao_autorizacao(self):
        f=self.efeito(trocar(completa(),vida_max=25))
        r=conferir(f,REF)
        self.assertFalse(any(p.campo=='vida_max' for p in r.problemas))
        self.assertTrue(any(p.regra=='aprovação' and p.campo=='efeito.1' for p in r.pendencias))

    def test_trocar_por_zero_sobrepoe_soma_e_buff(self):
        f=self.efeito(trocar(completa(),vida_max=0,buff__vida=7),como='trocar por',valor=0)
        self.efeito(f,2,valor=123)
        r=conferir(f,REF)
        self.assertIn('Vida 0',r.conferidos)

    def test_duas_trocas_impedem_certificacao(self):
        f=self.efeito(completa(),como='trocar por',valor=20);self.efeito(f,2,como='trocar por',valor=20)
        r=conferir(f,REF)
        self.assertTrue(any('somente uma troca' in p.esperado for p in r.problemas))
        self.assertFalse(any(c.startswith('Vida ') for c in r.conferidos))

    def test_desligado_nao_soma_nem_exige_fonte(self):
        f=self.efeito(completa(),ligado=0,valor=999,fonte='')
        self.assertIn('Vida 23',conferir(f,REF).conferidos)

    def test_efeito_invalido_nao_vira_numero(self):
        for kw in ({'valor':'007x'},{'fonte':''},{'caixa':'inventada'},{'como':'multiplicar'}):
            f=self.efeito(completa(),**kw);r=conferir(f,REF)
            self.assertTrue(any(p.campo=='efeito.1' for p in r.problemas),kw)

    def test_vida_rolada_por_dado_e_ausencia(self):
        f=trocar(completa(),regra__vida_rolada='Sim',vida__rolagem__2=8,vida_max=24)
        c=RegrasDaCampanha(valores={'vida_rolada':'Sim'})
        self.assertIn('Vida 24',conferir(f,REF,c).conferidos)
        for v in ('',0,13):
            trocar(f,vida__rolagem__2=v);r=conferir(f,REF,c)
            self.assertFalse(any(x.startswith('Vida ') for x in r.conferidos))
            self.assertTrue(any(p.campo=='vida.rolagem.2' for p in r.problemas+r.pendencias))


class Custom(unittest.TestCase):
    def melhoria(self):
        return trocar(completa(),custom__melhoria__1__nome='Alias *?~',custom__melhoria__1__base='Longe',custom__melhoria__1__mestre_viu=1)

    def test_mestre_viu_nao_aprova(self):
        c,r,ref=contexto(self.melhoria())
        self.assertNotIn('Alias *?~',ref.magia.melhorias)
        self.assertTrue(any(p.regra=='aprovação' for p in r.pendencias))

    def test_aprovacao_e_heranca(self):
        f=self.melhoria();ap=aprovar(f,'custom.melhoria.1');c,r,ref=contexto(f,ap)
        self.assertEqual(ref.magia.melhorias['Alias *?~'].peso,REF.magia.melhorias['Longe'].peso)
        self.assertEqual(c.aliases['melhoria:Alias *?~'],'Longe')

    def test_alteracao_invalida_aprovacao(self):
        f=self.melhoria();ap=aprovar(f,'custom.melhoria.1')
        for texto in ('efeito novo','007','1,5','=1+1'):
            novo=trocar(copy.deepcopy(f),custom__melhoria__1__efeito=texto)
            c,r,ref=contexto(novo,ap)
            self.assertFalse(c.registros['custom.melhoria.1'].aprovada)

    def test_mudar_lembrete_nao_muda_conteudo(self):
        f=self.melhoria();ap=aprovar(f,'custom.melhoria.1');trocar(f,custom__melhoria__1__mestre_viu=0)
        self.assertTrue(contexto(f,ap)[0].registros['custom.melhoria.1'].aprovada)

    def test_nome_literal_nao_e_padrao(self):
        f=self.melhoria();trocar(f,custom__melhoria__2__nome='Alias outros',custom__melhoria__2__base='Longe',custom__melhoria__2__mestre_viu=0)
        c,r,ref=contexto(f)
        self.assertFalse(any('colisão' in p.esperado for p in r.problemas))

    def test_duplicata_casefold_e_colisao_livro(self):
        f=self.melhoria();trocar(f,custom__melhoria__2__nome='alias *?~',custom__melhoria__2__base='Longe',custom__melhoria__2__mestre_viu=0)
        c,r,ref=contexto(f)
        self.assertFalse(c.registros['custom.melhoria.1'].valida)
        trocar(f,custom__melhoria__1__nome='Longe');c,r,ref=contexto(f)
        self.assertFalse(c.registros['custom.melhoria.1'].valida)

    def test_heranca_nao_sobrescreve_nao_explicito(self):
        f=trocar(completa(),custom__restricao__1__nome='Frequência nova',custom__restricao__1__base='Uma Vez',
                 custom__restricao__1__frequencia='Não',custom__restricao__1__mestre_viu=0)
        c,r,ref=contexto(f,aprovar(f,'custom.restricao.1'))
        self.assertEqual(c.registros['custom.restricao.1'].efetivos['frequencia'],'Não')

    def test_forma_zero_e_nao_sobrescrevem_base(self):
        f=trocar(completa(),custom__forma__1__tipo='Forma',custom__forma__1__nome='Explosão sem dano',custom__forma__1__base='Explosão',
                 custom__forma__1__peso=0,custom__forma__1__resultado=0,custom__forma__1__exige_tr='Não',custom__forma__1__classe_zero='Não',custom__forma__1__mestre_viu=0)
        c,r,ref=contexto(f,aprovar(f,'custom.forma.1'))
        d=c.registros['custom.forma.1']
        self.assertTrue(d.valida,r.problemas)
        self.assertEqual(d.efetivos['peso'],0)
        self.assertFalse(d.efetivos['exige_tr'])

    def test_tipo_de_entidade_tres_modos_independentes(self):
        f=trocar(completa(),custom__tipo_entidade__1__nome='Outro corpo',custom__tipo_entidade__1__base='Shikigami de criação',
                 custom__tipo_entidade__1__vida='Corpo de criação',custom__tipo_entidade__1__talisma='Não usa',custom__tipo_entidade__1__mestre_viu=0)
        c,r,ref=contexto(f,aprovar(f,'custom.tipo_entidade.1'))
        d=c.registros['custom.tipo_entidade.1']
        self.assertEqual((d.efetivos['vida'],d.efetivos['talisma'],d.efetivos['reserva_pe']),('Corpo de criação','Não usa','Normal da entidade'))

    def test_forma_herdada_e_usada_na_montagem(self):
        f=trocar(completa(),custom__forma__1__tipo='Forma',custom__forma__1__nome='Projétil *?~',custom__forma__1__base='Projétil',
                 custom__forma__1__mestre_viu=0,feitico__1__nome='Teste',feitico__1__forma='Projétil *?~',feitico__1__classe=1,
                 feitico__1__pe='3 PE',feitico__1__dano='3d8',feitico__1__alcance='18 m, um alvo',feitico__1__resolve='Acerto')
        r=conferir(f,REF,aprovados=aprovar(f,'custom.forma.1'))
        self.assertFalse(any(p.campo.startswith('feitico.1.') for p in r.problemas),r.problemas)
        self.assertTrue(any('benefício numérico da Forma custom 3d8' in c for c in r.conferidos))

    def test_tipo_aprovado_altera_vida_sem_ligar_talisma(self):
        from closure_bot.ficha_entidade import conferir_numeros
        f=trocar(completa(),custom__tipo_entidade__1__nome='Corpo próprio',custom__tipo_entidade__1__vida='Corpo de criação',
                 custom__tipo_entidade__1__mestre_viu=0,invocacao__1__tipo='Corpo próprio',invocacao__1__vida__max=13)
        for a,v in zip(('forca','destreza','constituicao','inteligencia','essencia'),(3,2,2,1,1)):
            trocar(f,**{f'invocacao.1.atributo.{a}.base':v,f'invocacao.1.atributo.{a}.buff':0,f'invocacao.1.atributo.{a}.total':v})
        c,r,ref=contexto(f,aprovar(f,'custom.tipo_entidade.1'))
        conferir_numeros(f,ref.magia,'invocacao.1',2,r)
        self.assertFalse(any(p.campo=='invocacao.1.vida.max' for p in r.problemas),r.problemas)
        self.assertIn('Invocação 1: vida.max 13',r.conferidos)
        self.assertEqual(c.registros['custom.tipo_entidade.1'].efetivos['talisma'],'Não usa')


class TreinosCustom(unittest.TestCase):
    def ficha(self,**kw):
        f=trocar(completa(),custom__pericia__1__tipo='Perícia',custom__pericia__1__nome='007',custom__pericia__1__atributo='Força',
                 custom__pericia__1__mestre_viu=0,personagem__pericia_custom__1__nome='007',personagem__pericia_custom__1__atributo='Força',
                 personagem__pericia_custom__1__treino=1,personagem__pericia_custom__1__especializacao=0,
                 personagem__pericia_custom__1__bonus=2,personagem__pericia_custom__1__resultado=6)
        return trocar(f,**kw)

    def test_bonus_e_ajuste_resultado_e_total(self):
        f=self.ficha();c,r,ref=contexto(f,aprovar(f,'custom.pericia.1'));conferir_treinos(f,ref,c,r)
        self.assertFalse(any(p.campo=='personagem.pericia_custom.1.resultado' for p in r.problemas),r.problemas)
        self.assertIn('007: bônus +6',r.conferidos)
        self.assertTrue(any(p.campo=='personagem.pericia_custom.1.bonus' for p in r.pendencias))

    def test_resultado_adulterado(self):
        f=self.ficha(personagem__pericia_custom__1__resultado=999);c,r,ref=contexto(f,aprovar(f,'custom.pericia.1'));conferir_treinos(f,ref,c,r)
        self.assertTrue(any(p.campo=='personagem.pericia_custom.1.resultado' for p in r.problemas))

    def test_treino_custom_gasta_o_orcamento_existente(self):
        f=self.ficha()
        for slug in list(REF.testes.pericias)[:10]:trocar(f,**{f'pericia.{slug}.treino':1})
        c,r,ref=contexto(f,aprovar(f,'custom.pericia.1'));conferir_treinos(f,ref,c,r)
        self.assertTrue(any(p.campo=='treinos' and p.regra=='treinos' for p in r.problemas))

    def test_oficio_custom_sem_treino_nao_concede_beneficio(self):
        f=trocar(self.ficha(),custom__oficio__1__tipo='Ofício',custom__oficio__1__nome='Costura *?~',custom__oficio__1__atributo='Destreza',
                 custom__oficio__1__mestre_viu=0,personagem__oficio_custom__1__nome='Costura *?~',personagem__oficio_custom__1__atributo='Destreza',
                 personagem__oficio_custom__1__treino=0,personagem__oficio_custom__1__especializacao=0,personagem__oficio_custom__1__bonus=0,
                 personagem__oficio_custom__1__resultado=3)
        c,r,ref=contexto(f,aprovar(f,'custom.oficio.1'));conferir_treinos(f,ref,c,r)
        self.assertTrue(any(p.campo=='personagem.oficio_custom.1.resultado' for p in r.problemas))  # DES 2, sem maestria

    def test_especializacao_precoce_e_treino_ausente(self):
        f=self.ficha(personagem__pericia_custom__1__treino=0,personagem__pericia_custom__1__especializacao=1)
        c,r,ref=contexto(f,aprovar(f,'custom.pericia.1'));conferir_treinos(f,ref,c,r)
        self.assertTrue(any(p.campo=='personagem.pericia_custom.1.especializacao' for p in r.problemas))

    def test_efeito_por_nome_nao_por_indice(self):
        f=self.ficha(personagem__pericia_custom__1__bonus=0,personagem__pericia_custom__1__resultado=9,
                     efeito__1__ligado=1,efeito__1__caixa='Perícia · 007',efeito__1__como='somar',efeito__1__valor=5,
                     efeito__1__tipo_de_fonte='Decisão do mestre',efeito__1__fonte='Teste')
        c,r,ref=contexto(f,aprovar(f,'custom.pericia.1'));conferir_efeitos(f,c,r);conferir_treinos(f,ref,c,r)
        self.assertFalse(any(p.campo=='personagem.pericia_custom.1.resultado' for p in r.problemas),r.problemas)
        self.assertIn('007: bônus +9',r.conferidos)


class Familias(unittest.TestCase):
    def test_nao_herda_livre_da_tecnica(self):
        f=completa();trocar(f,custom__familia__1__nome='Família *?~',custom__familia__1__estado='Livre',custom__familia__1__mestre_viu=0,
                          invocacao__1__familia__3='Família *?~',invocacao__1__limite_familias=3,invocacao__1__limite_livres=1)
        c,r,ref=contexto(f)
        livres,abertas=conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r)
        self.assertIn('Família *?~',abertas);self.assertNotIn('Família *?~',livres)

    def test_entidades_independentes(self):
        f=trocar(completa(),invocacao__1__familia__1='Mira',invocacao__2__familia__1='Área',
                 invocacao__1__limite_familias=3,invocacao__1__limite_livres=1,invocacao__2__limite_familias=3,invocacao__2__limite_livres=1)
        c,r,ref=contexto(f)
        self.assertEqual(conferir_familias(f,ref.magia,'invocacao.1',r.problemas)[0],{'Mira'})
        self.assertEqual(conferir_familias(f,ref.magia,'invocacao.2',r.problemas)[0],{'Área'})

    def test_nove_vagas_nao_concedem_nove_escolhas(self):
        f=completa()
        for i,n in enumerate(REF.magia.familias,1):trocar(f,**{f'invocacao.1.familia.{i}':n})
        c,r,ref=contexto(f);conferir_familias(f,ref.magia,'invocacao.1',r.problemas)
        self.assertTrue(any(p.campo=='invocacao.1.familias' for p in r.problemas))

    def test_nao_autonoma_livre_conta_no_total_e_na_prioridade(self):
        f=trocar(completa(),invocacao__1__autonomia='Não autônoma',invocacao__1__limite_familias=4,invocacao__1__limite_livres=2,
                 invocacao__1__familia__1='Mira',invocacao__1__familia__2='Área',invocacao__1__familia__3='Alcance',invocacao__1__familia__4='Tempo')
        c,r,ref=contexto(f);livres,abertas=conferir_familias(f,ref.magia,'invocacao.1',r.problemas,r)
        self.assertEqual((livres,abertas),({'Mira','Área'},{'Mira','Área','Alcance','Tempo'}));self.assertEqual(r.problemas,[])


class Painel(unittest.TestCase):
    def test_pendencias_e_limites_nao_pintam_aprovacao_integral(self):
        from closure_bot.cogs.ficha import paginas
        f=completa();r=conferir(f,REF)
        p=paginas(r,f,SimpleNamespace(chave='closure',nome='Closure',avatar_url=None))
        self.assertEqual(p[0].colour.value,0xD4A017)
        self.assertIn('parcial',' '.join(c.value for c in p[0].fields).lower())
        self.assertTrue(any('Limites da análise' in e.footer.text for e in p))


class CadastroConfiavel(unittest.TestCase):
    def test_servidores_nao_compartilham_autorizacao(self):
        from closure_bot.ficha_configuracao import carregar_campanha
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'campanhas.json'
            p.write_text(json.dumps({'1':{'nome':'primeira','regras':{'atributos_pontos':10},'aprovados':{'hash-sintetico':'mestre'}}}))
            c,a=carregar_campanha(p,1);outra,b=carregar_campanha(p,2)
            self.assertEqual(c.valores['atributos_pontos'],10)
            self.assertIn('hash-sintetico',a.impressoes)
            self.assertEqual((outra.valores,b.impressoes),({},{}))

    def test_cli_preserva_outros_servidores_e_aprova_hash(self):
        import csv
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cadastro.json';p.write_text(json.dumps({'2':{'nome':'preservar'}}))
            f=trocar(completa(),custom__melhoria__1__nome='Longe próprio',custom__melhoria__1__base='Longe',custom__melhoria__1__mestre_viu=0)
            csvfile=Path(d)/'sintetica.csv'
            with csvfile.open('w',newline='') as out:
                w=csv.writer(out);w.writerow(['chave','valor','célula','parte'])
                w.writerows([k,v.valor,v.celula,v.parte] for k,v in f.items())
            cmd=[str(RAIZ/'.venv/bin/python'),str(RAIZ/'ferramentas/ficha_campanha.py'),'aprovar','--servidor','1',
                 '--cadastro',str(p),'--ficha',str(csvfile),'--campo','custom.melhoria.1','--por','mestre sintético']
            result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            dados=json.loads(p.read_text())
            self.assertEqual(dados['2'],{'nome':'preservar'})
            self.assertEqual(len(dados['1']['aprovados']),1)
            self.assertTrue(next(iter(dados['1']['aprovados'])).startswith('b47-v2:'))
            self.assertNotIn('sintetica.csv',p.read_text())

    def test_regra_invalida_nao_cai_silenciosamente_no_livro(self):
        from closure_bot.ficha_configuracao import carregar_campanha
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cadastro.json';p.write_text(json.dumps({'1':{'regras':{'atributos_pontos':-1}}}))
            with self.assertRaises(ValueError):carregar_campanha(p,1)


if __name__=='__main__':unittest.main()
