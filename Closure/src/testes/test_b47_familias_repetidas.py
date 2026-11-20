"""Erro de Famílias repetido no painel do GC:ficha (Discord, 19/11/2026, 21:55).

Ficha formato 13 preenchida, nível 17, com Máxima, mandada como .xlsx: "7 erros", mas "regra · familias livres" e
"regra · familias fechadas" apareciam duas vezes cada. Com cartão ou Máxima, `ficha_magia.escolhas_familias` (legado)
e `ficha_b47.conferir_b47` chamam `conferir_familias` cada um, e os dois erros saíam dobrados. A oficial em branco
não tem cartão nem Máxima, então lá cada um saía uma vez só.
"""
import io
import unittest
from collections import Counter

import openpyxl

from closure_bot.ficha_b47 import _sem_repetidos
from closure_bot.ficha_corretor import Problema, conferir
from closure_bot.ficha_leitor import Campo, de_csv, de_xlsx
from test_r53 import REF, completa_r53, csvfile_texto

FAMILIAS = ('regra.familias_livres', 'regra.familias_fechadas')


def ficha_13(*, maxima):
    """Ficha 13 em dia com todas as Famílias da Técnica em Neutra (0 Livres, 0 Fechadas)."""
    f = completa_r53()
    f['formato.versao'] = Campo(13, '', 'cabeçalho')
    f['analise.estado'] = Campo('em_dia', '', '')
    f['analise.exportada_em'] = Campo('2026-11-19T12:40:00', '', '')
    for k in [k for k in f if k.startswith('tecnica.familia.')]:
        f[k] = Campo('Neutra', f[k].celula, f[k].parte)
    if maxima:
        f['nivel'] = Campo(17, f['nivel'].celula, f['nivel'].parte)
        f['maxima.nome'] = Campo('Teste R67 Explosão', f['maxima.nome'].celula, f['maxima.nome'].parte)
    return f


def xlsx(f):
    """Aba ANALISE como o .xlsx baixado do Google (valores já calculados)."""
    livro = openpyxl.Workbook()
    aba = livro.active
    aba.title = 'ANALISE'
    aba.append(['chave', 'valor', 'célula', 'parte'])
    for k, c in f.items():
        aba.append([k, c.valor, c.celula, c.parte])
    memoria = io.BytesIO()
    livro.save(memoria)
    return memoria.getvalue()


def contagem(resultado):
    return Counter(p.campo for p in resultado.problemas if p.campo in FAMILIAS)


class FamiliasUmaVez(unittest.TestCase):
    def test_cada_erro_de_familia_aparece_uma_vez(self):
        for maxima in (False, True):
            for leitura, ler in (('link', lambda f: de_csv(csvfile_texto(f))), ('xlsx', lambda f: de_xlsx(xlsx(f)))):
                with self.subTest(maxima=maxima, leitura=leitura):
                    r = conferir(ler(ficha_13(maxima=maxima)), REF)
                    self.assertEqual(r.veredito, 'reprovada')
                    self.assertEqual(contagem(r), {c: 1 for c in FAMILIAS})

    def test_nenhum_problema_identico_repetido(self):
        r = conferir(de_xlsx(xlsx(ficha_13(maxima=True))), REF)
        for lista in (r.problemas, r.pendencias, r.notas):
            repetidos = [p for p, n in Counter(repr(p) for p in lista).items() if n > 1]
            self.assertFalse(repetidos, repetidos)

    def test_com_e_sem_maxima_dao_o_mesmo_erro_de_familia(self):
        sem = [p for p in conferir(de_csv(csvfile_texto(ficha_13(maxima=False))), REF).problemas if p.campo in FAMILIAS]
        com = [p for p in conferir(de_csv(csvfile_texto(ficha_13(maxima=True))), REF).problemas if p.campo in FAMILIAS]
        self.assertEqual(sem, com)


class SemRepetidos(unittest.TestCase):
    def test_tira_so_o_identico_e_mantem_a_ordem(self):
        a = Problema('famílias', 'regra.familias_livres', '2 conforme campanha autorizada', '0', 'fundamento--familias')
        b = Problema('famílias', 'regra.familias_fechadas', '3 conforme campanha autorizada', '0', 'fundamento--familias')
        self.assertEqual(_sem_repetidos([a, b, a, b]), [a, b])

    def test_erros_diferentes_continuam(self):
        base = ('famílias', 'regra.familias_livres', '2 conforme campanha autorizada', '0', 'fundamento--familias')
        variantes = [Problema(*base)]
        for i in range(5):
            v = list(base)
            v[i] = v[i] + ' outro' if i != 3 else '1'
            variantes.append(Problema(*v))
        variantes.append(Problema(*base[:3], 0, base[4]))  # 0 número ≠ '0' texto
        self.assertEqual(_sem_repetidos(variantes), variantes)

    def test_aceita_encontrado_em_lista(self):
        a = Problema('famílias', 'invocacao.1.familias', 'até 3', ['Área', 'Área'])
        self.assertEqual(_sem_repetidos([a, Problema(*vars(a).values())]), [a])


if __name__ == '__main__':
    unittest.main()
