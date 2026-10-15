"""Exportação oficial preenchida e recalculada no LibreOffice, sem fórmulas simuladas."""
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest

from closure_bot.cogs.ficha import paginas
from closure_bot.ficha_corretor import Referencias, conferir
from closure_bot.ficha_leitor import Campo, de_xlsx

RAIZ = Path(__file__).resolve().parents[2]


def contrato(nome):
    return {k: (p, c) for k, p, c in (l.split("\t") for l in
            (RAIZ / "dados/ficha" / nome).read_text().splitlines()
            if l and not l.startswith(("#", "chave\t")))}


class AnaliseV4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = Referencias.do_livro(RAIZ / "dados")
        cls.fichas = {n: de_xlsx(RAIZ / f"src/testes/dados/ficha_analise_v4_{n}.xlsx")
                      for n in ("pessoal", "especialista", "domada")}

    def ficha(self, nome="pessoal", **trocas):
        f = copy.deepcopy(self.fichas[nome])
        for k, v in trocas.items():
            k = k.replace("__", ".")
            antigo = f[k]
            f[k] = Campo(v, antigo.celula, antigo.parte)
        return f

    def test_contrato_preserva_as_4896_chaves_e_origens(self):
        antigo, novo = contrato("analise-chaves-v2.tsv"), contrato("analise-chaves.tsv")
        self.assertEqual(len(novo), 5381)
        self.assertTrue(antigo.items() <= novo.items())
        for nome, f in self.fichas.items():
            with self.subTest(nome=nome):
                self.assertEqual(f["formato.versao"].valor, 4)
                self.assertEqual({k: (c.parte, c.celula) for k, c in f.items()}, novo)
                self.assertFalse(any(str(c.valor).startswith(("#NAME", "#REF", "#VALUE", "#DIV/0", "#N/A")) for c in f.values()))

    def test_pessoal_e_domada_recalculadas_sem_erro_ou_pendencia(self):
        for nome in ("pessoal", "domada"):
            r = conferir(self.ficha(nome), self.ref)
            self.assertEqual((r.veredito, r.problemas, r.pendencias), ("aprovada", [], []))
        r = conferir(self.ficha("domada"), self.ref)
        self.assertIn("Invocação 1 · TR Vigor: bônus +5", r.conferidos)
        self.assertIn("Invocação 1 · Atletismo: bônus +4", r.conferidos)

    def test_especialista_nativo_e_divergencia_de_volume_amarela(self):
        r = conferir(self.ficha("especialista"), self.ref)
        self.assertEqual((r.veredito, r.problemas), ("aprovada", []))
        self.assertIn("Atletismo: bônus +7", r.conferidos)
        self.assertEqual({p.campo for p in r.pendencias}, {"item.1.volume", "carga.total"})
        ps = paginas(r, self.fichas["especialista"], SimpleNamespace(nome="Closure", chave="closure", avatar_url=None))
        self.assertTrue(all(p.colour.value == 0xD4A017 for p in ps))

    def test_resultados_adulterados_reprovam_sem_precisar_de_aviso(self):
        for nome, campos in (("pessoal", ("tr.fisico.bonus", "pericia.atletismo.bonus", "oficio.conducao.bonus", "carga.total", "carga.limite")),
                             ("domada", ("invocacao.1.tr.vigor.bonus", "invocacao.1.pericia.1.bonus", "invocacao.1.carga.total"))):
            for k in campos:
                with self.subTest(nome=nome, campo=k):
                    r = conferir(self.ficha(nome, **{k: 999}), self.ref)
                    self.assertEqual(r.veredito, "reprovada")
                    self.assertIn(k, [p.campo for p in r.problemas])

    def test_treino_faltante_e_pendente_sem_triplicar_aviso(self):
        f = self.ficha(pericia__atletismo__treino=0, pericia__atletismo__bonus=3)
        # Mesmo se o aviso legado estiver vazio, a falta sai das escolhas reais.
        r = conferir(f, self.ref)
        self.assertFalse(r.problemas)
        self.assertEqual([p.campo for p in r.pendencias], ["treinos"])

    def test_entrada_ausente_nao_certifica_conta_nem_inventa_zero(self):
        f = self.ficha()
        del f["pericia.atletismo.ajuste"]
        del f["item.12.quantidade"]
        r = conferir(f, self.ref)
        self.assertFalse(any(s.startswith(("Atletismo:", "Carga pessoal:")) for s in r.conferidos))
        self.assertTrue(any("faltam posições" in s for s in r.nao_conferido))

    def test_formato_de_configuracao_nao_e_aceito_sem_integracao(self):
        r = conferir(self.ficha(formato__versao=3), self.ref)
        self.assertEqual(r.veredito, "formato desconhecido")

    def test_bonus_ficam_na_pagina_propria_sem_inchar_resumo(self):
        f = self.ficha("domada"); r = conferir(f, self.ref)
        ps = paginas(r, f, SimpleNamespace(nome="Closure", chave="closure", avatar_url=None))
        testes = [p for p in ps if " · TR e perícias · " in p.footer.text]
        self.assertTrue(testes)
        texto = "\n".join(c.name + "\n" + c.value for p in testes for c in p.fields)
        for s in ("TR Físico", "Atletismo", "Condução", "Invocação 1", "+5"):
            self.assertIn(s, texto)
        self.assertNotIn("**Atletismo**", "\n".join(c.value for c in ps[0].fields))
        for p in ps:
            self.assertLessEqual(len(p), 6000)
            self.assertTrue(all(len(c.value) <= 1024 for c in p.fields))
