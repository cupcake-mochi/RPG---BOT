"""Contrato ANALISE 12 (R53): cartões diretos, transição, custom e painel. Fixtures sintéticas, sem Google."""
import asyncio
import hashlib
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from closure_bot.ficha_leitor import Campo, de_csv
from closure_bot.ficha_corretor import Aprovados, Referencias, conferir
from closure_bot.ficha_esquema import campos_b47, campos_r53, tipo, variante
from closure_bot.ficha_r53 import (VERSAO_CAMPOS, contextos, decodificar, escolher_leitura, rotulo, rotulo_chave,
                                   transicoes)
from closure_bot.r53 import modelo as M
from closure_bot.r53.formulas import evaluate

RAIZ = Path(__file__).resolve().parents[2]
REF = Referencias.do_livro(RAIZ / 'dados')
LIVRE = M.arvore(True)
PARTES = campos_r53()
ORIGEM = {  # Ficha---RPG-JJK@4b22da5420263a8885e28a508cbc39938dd9d9da
    'formulas.py': 'f6e8dbdbb3db49fd4eb12394902872827c236cee73300b6a9fd76c2b6981a096',
    'catalogo.json': '2f33003493824ed767427791368275b7b059f397f201ae9cc73fcb1b44b6442b',
}


def completa_r53():
    """Ficha B47 sintética completa promovida ao formato 12, com os 249 cartões vazios como na oficial publicada."""
    from test_b47_integracao import completa
    f = completa()
    for k, v in campos_r53().items():
        if k not in f:
            f[k] = Campo('0' if k.endswith('.controle_compat') else '', v['origem'], v['parte'])
    # Cartão vazio na oficial (lida em 19/10/2026): espelhos com os menus padrão, JSON de entrada vazio.
    padrao = {'classe': '1', 'forma': 'Projétil', 'dano': 'FALSE', 'cura': 'FALSE', 'vt': 'FALSE', 'p_dano': '0',
              'p_cura': '0', 'p_vt': '0', 'controle': 'Sem reforço', 'res_dano': 'Ataque', 'execucao': 'Comandada'}
    for id_, ctx in contextos().items():
        for k, v in {**padrao, 'modalidade': ctx['modalidade']}.items():
            chave = f'r53.{id_}.{k}'
            f[chave] = Campo(v, f[chave].celula, f[chave].parte)
    f['formato.versao'] = Campo(12, '', 'cabeçalho')
    f['ficha.livro'] = Campo('Ciclo Maldito R53', '', 'cabeçalho')
    f['r53.montagem.esquema'] = Campo('2', '', 'cabeçalho')
    f['r53.entrada.campos'] = Campo(json.dumps(M.INPUTS, ensure_ascii=False), '', 'cabeçalho')
    f['r53.versao.campos'] = Campo(json.dumps(VERSAO_CAMPOS, ensure_ascii=False), '', 'cabeçalho')
    return f


def _texto(v):
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def versao(classe, **campos):
    v = {k: M.DEFAULTS.get(k, '') for k in VERSAO_CAMPOS}
    v.update({f'funcao{i}': '' for i in (1, 2, 3)}, **{f'pontos{i}': 0 for i in (1, 2, 3)})
    v.update(classe=classe, preparada=True, r1_valida=True, r2_valida=True)
    v.update(campos)
    return v


def gravar(f, id_, classe, *, nome='Corte', nivel=2, classe_maxima=None, versoes=None, adulterar=None, **campos):
    """Simula o que a ficha exporta: versões, registro ativo e resultados do mesmo cálculo."""
    modo = contextos()[id_]['modalidade']
    pontos = {'p_dano': 0, 'p_cura': 0, 'p_vt': 0}
    pontos.update({k: campos.pop(k) for k in list(campos) if k in pontos})
    v = versao(classe, pontos1=pontos['p_dano'], pontos2=pontos['p_cura'], pontos3=pontos['p_vt'],
               funcao1='Dano' if pontos['p_dano'] else '', funcao2='Cura' if pontos['p_cura'] else '',
               funcao3='PV temporários' if pontos['p_vt'] else '', **campos)
    todas = dict(versoes or {})
    chave = 'maxima' if modo in ('Técnica Máxima', 'Máxima de entidade') else str(classe)
    todas.setdefault(chave, v)
    for c, reg in todas.items():
        f[f'r53.{id_}.versao.{c}'] = Campo(json.dumps([reg[k] for k in VERSAO_CAMPOS], ensure_ascii=False), '', 'entrada')
    ativa = {**M.DEFAULTS, **{k: v[k] for k in VERSAO_CAMPOS if k in M.INPUTS},
             'id': id_, 'nome': nome, 'classe': classe, 'modalidade': modo, 'nivel': nivel,
             'classe_maxima': classe_maxima if classe_maxima is not None else REF.magia.classe_maxima(nivel),
             'dano': pontos['p_dano'] > 0, 'cura': pontos['p_cura'] > 0, 'vt': pontos['p_vt'] > 0, **pontos}
    ativa.update((adulterar or {}).get('entrada', {}))
    env = {**ativa, '_familias': {}, '_formas': {}}
    for k, expr in LIVRE.items():
        env[k] = evaluate(expr, env, M.OPCOES)
    f[f'r53.{id_}.entrada'] = Campo(json.dumps([ativa[k] for k in M.INPUTS], ensure_ascii=False), '', 'entrada')
    for k in ['classe', 'modalidade', 'forma', 'dano', 'cura', 'vt', 'p_dano', 'p_cura', 'p_vt', 'controle', 'dest_dano',
              'dest_cura', 'dest_vt', 'res_dano', 'tr_dano', 'tr_controle', 'dependencias', 'execucao', 'origem_permissao',
              'orcamento', 'base_funcoes', 'custo_forma', 'melhorias_pagas', 'devolucao', 'saldo', 'dano_d8', 'cura_d8',
              'vida_temporaria', 'sem_uso', 'pe', 'cd_normal', 'cd_controle', 'funcao', 'avisos']:
        f[f'r53.{id_}.{k}'] = Campo(_texto(env[k]), '', PARTES[f'r53.{id_}.{k}']['parte'])
    for k, val in (adulterar or {}).items():
        if k != 'entrada':
            f[f'r53.{id_}.{k}'] = Campo(val, '', PARTES[f'r53.{id_}.{k}']['parte'])
    if id_ == 'feitico.1':
        f['feitico.1.nome'] = Campo(nome, '', 'entrada')
        f['feitico.1.classe'] = Campo(classe, '', 'entrada')
    return env


def csvfile_texto(f):
    import csv
    import io
    saida = io.StringIO()
    w = csv.writer(saida)
    w.writerow(['chave', 'valor', 'célula', 'parte'])
    w.writerows([k, v.valor, v.celula, v.parte] for k, v in f.items())
    return saida.getvalue()


def textos(r):
    return [p.campo + ' | ' + p.esperado + ' | ' + p.encontrado for p in r.problemas + r.pendencias]


class NucleoVendorizado(unittest.TestCase):
    def test_copia_identica_ao_commit_de_referencia(self):
        pasta = RAIZ / 'src/closure_bot/r53'
        for nome, sha in ORIGEM.items():
            self.assertEqual(hashlib.sha256((pasta / nome).read_bytes()).hexdigest(), sha, nome)

    def test_89_casos_verificados_no_google(self):
        # Mesma base do r53/testes/verificar.py; os 89 casos passaram nativamente em GOOGLE-89-FINAL.json.
        base = dict(tr_dano='Físico', tr_controle='Físico', preparada=True, origem_permissao='Caso de conferência do autor R53',
                    permite_dano=True, permite_cura=True, permite_vt=True, dest_dano='Inimigo válido',
                    dest_cura='Aliado disposto', dest_vt='Aliado disposto')
        casos = json.loads((RAIZ / 'src/testes/dados/r53-casos.json').read_text())
        self.assertEqual(len(casos), 89)
        for caso in casos:
            obtido = M.calcular({**base, **caso['entrada']}, catalogo_extra=caso.get('catalogo'),
                                familias_custom=caso.get('familias_custom'), formas_custom=caso.get('formas'))
            for k, v in caso['esperado'].items():
                with self.subTest(caso=caso['nome'], campo=k):
                    self.assertEqual(obtido[k], v)

    def test_registro_livre_dispensa_campos_narrativos_mas_nao_contas(self):
        env = M.calcular({'classe': 3, 'dano': True, 'p_dano': 9})
        self.assertIn('Registre a permissão', env['avisos'])
        livre = {**M.DEFAULTS, 'classe': 3, 'dano': True, 'p_dano': 10, 'preparada': True}
        for k, expr in LIVRE.items():
            livre[k] = evaluate(expr, livre, M.OPCOES)
        self.assertNotIn('Registre', livre['avisos'])
        self.assertIn('Distribuição excede o saldo', livre['avisos'])


class Manifesto(unittest.TestCase):
    def test_b47_preservada_e_novas_chaves(self):
        b47, r53 = campos_b47(), campos_r53()
        self.assertEqual(len(r53), 18393)  # 18.394 linhas com o cabeçalho, como na publicação oficial
        self.assertTrue(set(b47) <= set(r53))
        self.assertTrue(all(r53[k]['parte'] == b47[k]['parte'] for k in b47))
        self.assertEqual(sum(k.endswith('.controle_compat') for k in r53), 30)
        self.assertEqual(len(contextos()), 249)

    def test_variante_e_tipos(self):
        self.assertEqual(variante({'formato.versao': Campo(12, '', '')}), 'r53-v12')
        self.assertEqual(tipo('r53.feitico.1.entrada'), 'texto')
        self.assertEqual(tipo('r53.feitico.1.p_dano'), 'texto')

    def test_rotulos(self):
        self.assertEqual(rotulo('entidade.3.esp.2'), 'Invocação 3 · especial 2')
        self.assertEqual(rotulo('entidade.1.maxima.1'), 'Invocação 1 · Técnica Máxima')
        self.assertEqual(rotulo_chave('r53.classe0.2.saldo'), 'Classe 0 2 · saldo')
        self.assertEqual(rotulo_chave('r53.entidade.10.liberacao.2.versao.6'), 'Invocação 10 · Liberação 2 · versão da Classe 6')
        self.assertIsNone(rotulo_chave('feitico.1.nome'))


class Cartoes(unittest.TestCase):
    def test_oficial_vazia_sem_aplicacoes(self):
        f = completa_r53()
        self.assertEqual(decodificar(f), ({}, []))
        r = conferir(f, REF)
        self.assertEqual(r.problemas, [])
        self.assertEqual(r.veredito, 'pendente')
        self.assertFalse(any(p.campo.startswith('r53.') for p in r.pendencias))

    def test_cartao_valido_recalculado(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3)
        r = conferir(f, REF)
        self.assertEqual(r.problemas, [], textos(r))
        self.assertTrue(any(c.startswith('Feitiço 1: R53 Classe 1 · Dano 3d8') and 'ficha VÁLIDO' in c for c in r.conferidos), r.conferidos)
        self.assertTrue(any('COMO É' in s for s in r.nao_conferido))
        self.assertTrue(any('não aprovação' in s for s in r.nao_conferido))

    def test_destinatario_permissao_e_resolucao_padrao_nao_reprovam_nem_autorizam(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=2, p_cura=0, dest_dano='', origem_permissao='', permite_dano=False, res_dano='Ataque')
        r = conferir(f, REF)
        self.assertEqual(r.problemas, [], textos(r))
        self.assertTrue(any('campos padrão não reprovam nem autorizam' in s for s in r.nao_conferido))

    def test_resultado_adulterado_reprova(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3, adulterar={'dano_d8': '12'})
        r = conferir(f, REF)
        self.assertEqual(r.veredito, 'reprovada')
        self.assertTrue(any(p.campo == 'r53.feitico.1.dano_d8' and p.esperado == '3' for p in r.problemas))

    def test_limite_mecanico_do_cartao_reprova(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=4)  # orçamento 3
        r = conferir(f, REF)
        self.assertEqual(r.veredito, 'reprovada')
        self.assertIn('Distribuição excede o saldo', [p.encontrado for p in r.problemas])
        self.assertTrue(any('ficha REVISAR' in c for c in r.conferidos))

    def test_avisos_ocultados_pela_ficha_aparecem(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=4, adulterar={'avisos': ''})
        r = conferir(f, REF)
        self.assertTrue(any(p.campo == 'r53.feitico.1.avisos' and p.encontrado == 'sem avisos (VÁLIDO)' for p in r.problemas))

    def test_ampliacao_que_muda_pecas_reprova(self):
        f = completa_r53()
        outra = versao(1, m1='Precisão', pontos1=1, funcao1='Dano')
        gravar(f, 'feitico.1', 2, p_dano=6, versoes={'1': outra}, nivel=5)
        r = conferir(f, REF)
        self.assertIn('Ampliação altera funções ou peças: m1', [p.encontrado for p in r.problemas])

    def test_classe_maior_que_o_permitido_reprova(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 3, p_dano=3)  # nível 2: Classe máxima 1
        r = conferir(f, REF)
        self.assertIn('Classe indisponível', [p.encontrado for p in r.problemas])

    def test_nivel_do_registro_diferente_da_ficha_fica_pendente(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3, nivel=9)
        r = conferir(f, REF)
        self.assertTrue(any(p.campo == 'r53.feitico.1.nivel' for p in r.pendencias))

    def test_toca_a_alma_pede_o_mestre(self):
        f = completa_r53()
        trocar_nivel(f, 9)
        gravar(f, 'feitico.1', 3, p_dano=5, m1='Toca a Alma', nivel=9)
        r = conferir(f, REF)
        self.assertTrue(any(p.encontrado == 'Toca a Alma' and p.regra == 'aprovação' for p in r.pendencias), textos(r))

    def test_aviso_das_montagens_b47_nao_vale_no_formato_12(self):
        f = completa_r53()
        f['feitico.1.erros'] = Campo('Forma não autorizada pela regra B47', '', 'aviso')
        f['invocacao.2.esp.1.avisos'] = Campo('peça B47', '', 'aviso')
        r = conferir(f, REF)
        self.assertEqual(r.problemas, [])
        self.assertFalse(any('B47' in p.encontrado for p in r.notas))

    def test_formato_11_continua_igual(self):
        from test_b47_integracao import completa
        r = conferir(completa(), REF)
        self.assertEqual(r.problemas, [])
        self.assertFalse(any('R53' in s for s in r.nao_conferido))


def trocar_nivel(f, n):
    f['nivel'] = Campo(n, f['nivel'].celula, f['nivel'].parte)


class Transicao(unittest.TestCase):
    def test_classe_trocada_sem_versao_salva_nao_aprova_nem_reprova(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3)
        f['r53.feitico.1.versao.1'] = Campo('', '', 'entrada')
        self.assertIn('feitico.1', transicoes(f))
        r = conferir(f, REF)
        self.assertEqual([p for p in r.problemas if p.campo.startswith('r53.')], [])
        self.assertTrue(any(p.campo == 'r53.feitico.1.entrada' and p.regra == 'informação' for p in r.pendencias))
        self.assertFalse(any(c.startswith('Feitiço 1: R53') for c in r.conferidos))

    def test_cartao_ainda_diferente_da_versao_mostra_a_versao_salva(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3, adulterar={'entrada': {'forma': 'Toque'}})
        motivo = transicoes(f)['feitico.1']
        self.assertIn('forma', motivo)
        r = conferir(f, REF)
        p = next(p for p in r.pendencias if p.campo == 'r53.feitico.1.entrada')
        self.assertIn('Última versão salva da Classe 1: Projétil', p.encontrado)
        self.assertNotEqual(r.veredito, 'reprovada')

    def test_recalculo_em_curso(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3)
        f['r53.feitico.1.entrada'] = Campo('#N/A', '', 'entrada')
        self.assertIn('feitico.1', transicoes(f))
        r = conferir(f, REF)
        self.assertEqual([p for p in r.problemas if p.campo.startswith('r53.')], [])

    def test_espelho_desatualizado(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3, adulterar={'p_dano': '2'})
        self.assertIn('exportação', transicoes(f)['feitico.1'])

    def test_escolhe_leitura_estavel_mais_recente_sem_misturar(self):
        estavel, instavel = completa_r53(), completa_r53()
        gravar(estavel, 'feitico.1', 1, p_dano=3)
        gravar(instavel, 'feitico.1', 1, p_dano=3)
        instavel['r53.feitico.1.versao.1'] = Campo('', '', 'entrada')
        self.assertIs(escolher_leitura([instavel, estavel]), estavel)
        self.assertIs(escolher_leitura([estavel, instavel]), estavel)
        outra = completa_r53()
        self.assertIs(escolher_leitura([estavel, outra]), outra)

    def test_json_invalido_persistente_e_formato(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3)
        f['r53.feitico.1.versao.1'] = Campo('[1,', '', 'entrada')
        r = conferir(f, REF)
        self.assertTrue(any(p.campo == 'r53.feitico.1.versao.1' and p.regra == 'formato' for p in r.problemas))

    def test_valor_de_formato_truncado_tem_reticencias_so_quando_necessario(self):
        for tamanho in (119, 120, 121, 300):
            with self.subTest(tamanho=tamanho):
                f = completa_r53()
                gravar(f, 'feitico.1', 1, p_dano=3)
                original = 'x' * tamanho
                f['r53.feitico.1.entrada'] = Campo(original, '', 'entrada')
                r = conferir(f, REF)
                p = next(p for p in r.problemas if p.campo == 'r53.feitico.1.entrada' and p.regra == 'formato')
                self.assertEqual(p.encontrado, original if tamanho <= 120 else original[:119] + '…')
                self.assertEqual(r.veredito, 'reprovada')

    def test_versoes_sem_nome_nao_somem_nem_reprovam(self):
        f = completa_r53()
        f['r53.feitico.2.versao.1'] = Campo(json.dumps([versao(1)[k] for k in VERSAO_CAMPOS]), '', 'entrada')
        r = conferir(f, REF)
        self.assertEqual(r.problemas, [])
        self.assertTrue(any('versões preparadas guardadas sem nome' in s for s in r.nao_conferido))

    def test_esquema_ausente(self):
        f = completa_r53()
        f['r53.entrada.campos'] = Campo('', '', 'cabeçalho')
        r = conferir(f, REF)
        self.assertEqual(r.veredito, 'reprovada')
        self.assertTrue(any('esquema exportado ausente' in s for s in r.nao_conferido))

    def test_leitura_csv_preserva_json_e_texto(self):
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=3, nome='FALSE "aspas"')
        import csv, io
        saida = io.StringIO()
        w = csv.writer(saida)
        w.writerow(['chave', 'valor', 'célula', 'parte'])
        w.writerows([k, v.valor, v.celula, v.parte] for k, v in f.items())
        lida = de_csv(saida.getvalue())
        aplicacoes, erros = decodificar(lida)
        self.assertEqual(erros, [])
        self.assertEqual(aplicacoes['feitico.1']['ativa']['nome'], 'FALSE "aspas"')
        self.assertIs(aplicacoes['feitico.1']['ativa']['dano'], True)


class Custom(unittest.TestCase):
    def cadastro(self, f, **extra):
        valores = {'custom.melhoria.1.nome': 'Corte próprio', 'custom.melhoria.1.base': 'Precisão',
                   'custom.melhoria.1.mestre_viu': 0, **extra}
        for k, v in valores.items():
            f[k] = Campo(v, f[k].celula, f[k].parte)

    def test_base_do_catalogo_r53_e_uso_no_cartao(self):
        f = completa_r53()
        self.cadastro(f)
        gravar(f, 'feitico.1', 1, p_dano=1)
        f['r53.feitico.1.entrada'] = Campo(f['r53.feitico.1.entrada'].valor.replace('"m1": ""', ''), '', 'entrada')
        ativa = json.loads(f['r53.feitico.1.entrada'].valor)
        ativa[M.INPUTS.index('m1')] = 'Corte próprio'
        f['r53.feitico.1.entrada'] = Campo(json.dumps(ativa, ensure_ascii=False), '', 'entrada')
        v = json.loads(f['r53.feitico.1.versao.1'].valor)
        v[VERSAO_CAMPOS.index('m1')] = 'Corte próprio'
        f['r53.feitico.1.versao.1'] = Campo(json.dumps(v, ensure_ascii=False), '', 'entrada')
        r = conferir(f, REF)
        self.assertFalse(any(p.campo == 'custom.melhoria.1.base' for p in r.problemas), textos(r))
        self.assertTrue(any(p.campo == 'r53.feitico.1.entrada' and p.regra == 'aprovação' for p in r.pendencias))
        self.assertTrue(any('sem recálculo do bot' in s for s in r.nao_conferido))
        from closure_bot.ficha_configuracao import ContextoB47
        from closure_bot.ficha_corretor import Resultado
        from closure_bot.ficha_custom import preparar_custom
        c = ContextoB47(aprovados=Aprovados(), r53=True)
        preparar_custom(f, REF, c, Resultado('aprovada'))
        aprovado = Aprovados({c.registros['custom.melhoria.1'].impressao: 'mestre sintético'})
        r = conferir(f, REF, aprovados=aprovado)
        self.assertFalse(any(p.campo == 'r53.feitico.1.entrada' and p.regra == 'aprovação' for p in r.pendencias), textos(r))

    def test_base_b47_que_saiu_do_catalogo_e_recusada(self):
        f = completa_r53()
        self.cadastro(f, **{'custom.melhoria.1.base': 'Muito Longe'})
        r = conferir(f, REF)
        self.assertTrue(any(p.campo == 'custom.melhoria.1.base' for p in r.problemas))

    def test_controle_compat_desmarcado_preserva_aprovacao_existente(self):
        from closure_bot.ficha_configuracao import ContextoB47
        from closure_bot.ficha_corretor import Resultado
        from closure_bot.ficha_custom import preparar_custom
        from test_b47_integracao import completa
        def impressao(f, r53):
            for k, v in {'custom.familia.1.nome': 'Sombra', 'custom.familia.1.estado': 'Neutra', 'custom.familia.1.mestre_viu': 0,
                         'custom.melhoria.1.nome': 'Golpe próprio', 'custom.melhoria.1.peso': 'Leve',
                         'custom.melhoria.1.familia': 'Controle', 'custom.melhoria.1.mestre_viu': 0}.items():
                f[k] = Campo(v, '', 'configuração')
            c = ContextoB47(aprovados=Aprovados(), r53=r53)
            preparar_custom(f, REF, c, Resultado('aprovada'))
            return c.registros['custom.melhoria.1'].impressao, c.registros['custom.familia.1'].impressao
        antes = impressao(completa(), False)
        f = completa_r53()
        self.assertEqual(impressao(f, True), antes)
        f['custom.melhoria.1.controle_compat'] = Campo('1', '', 'configuração')
        depois = impressao(f, True)
        self.assertNotEqual(depois[0], antes[0])
        self.assertEqual(depois[1], antes[1])

    def test_cli_do_mestre_aprova_a_mesma_impressao_que_o_bot_confere(self):
        import csv
        import subprocess
        import sys
        import tempfile
        from closure_bot.ficha_configuracao import carregar_campanha
        f = completa_r53()
        self.cadastro(f)
        with tempfile.TemporaryDirectory() as d:
            cadastro, csvfile = Path(d) / 'cadastro.json', Path(d) / 'ficha.csv'
            with csvfile.open('w', newline='') as out:
                w = csv.writer(out)
                w.writerow(['chave', 'valor', 'célula', 'parte'])
                w.writerows([k, v.valor, v.celula, v.parte] for k, v in f.items())
            cmd = [sys.executable, str(RAIZ / 'ferramentas/ficha_campanha.py'), 'aprovar', '--servidor', '1', '--cadastro',
                   str(cadastro), '--ficha', str(csvfile), '--campo', 'custom.melhoria.1', '--por', 'mestre sintético']
            saida = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            _, aprovados = carregar_campanha(cadastro, '1')
        r = conferir(de_csv(csvfile_texto(f)), REF, aprovados=aprovados)
        self.assertFalse(any(p.campo.startswith('custom.melhoria.1') and p.regra == 'aprovação' for p in r.pendencias), textos(r))


class Painel(unittest.TestCase):
    def test_cartoes_r53_ganham_pagina_de_feiticos_e_rotulos(self):
        from closure_bot.cogs.ficha import paginas
        f = completa_r53()
        gravar(f, 'feitico.1', 1, p_dano=4)
        r = conferir(f, REF)
        persona = SimpleNamespace(chave='closure', nome='Closure', avatar_url=None)
        p = paginas(r, f, persona)
        texto = '\n'.join(c.name + '\n' + c.value for e in p for c in e.fields)
        self.assertIn('Feitiço 1 · avisos do cartão', texto)
        self.assertIn('Distribuição excede o saldo', texto)
        self.assertIn('Feitiço 1 — Corte', texto)


class ReleituraDoLink(unittest.IsolatedAsyncioTestCase):
    async def test_rele_ate_estabilizar_e_para_no_limite(self):
        from closure_bot.cogs import ficha as cog
        instavel, estavel = completa_r53(), completa_r53()
        gravar(instavel, 'feitico.1', 1, p_dano=3)
        gravar(estavel, 'feitico.1', 1, p_dano=3)
        instavel['r53.feitico.1.versao.1'] = Campo('', '', 'entrada')
        objeto = cog.Ficha.__new__(cog.Ficha)
        with patch.object(cog, 'de_link', AsyncMock(side_effect=[instavel, estavel])), patch.object(cog.asyncio, 'sleep', AsyncMock()):
            ficha, n = await objeto._ler_estavel('x')
        self.assertIs(ficha, estavel)
        self.assertEqual(n, 2)
        with patch.object(cog, 'de_link', AsyncMock(side_effect=[instavel] * 5)), patch.object(cog.asyncio, 'sleep', AsyncMock()) as dormir:
            ficha, n = await objeto._ler_estavel('x')
        self.assertEqual(n, 3)
        self.assertEqual(dormir.await_count, 2)
        from test_b47_integracao import completa
        with patch.object(cog, 'de_link', AsyncMock(return_value=completa())) as ler:
            await objeto._ler_estavel('x')
        self.assertEqual(ler.await_count, 1)


if __name__ == '__main__':
    unittest.main()
