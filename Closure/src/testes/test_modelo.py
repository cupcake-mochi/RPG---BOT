"""Camada da IA: formato do pedido, leitura da resposta, fila com reserva e registro de cada tentativa.
Rodar de src/:  python3 -m unittest discover -s testes"""
import unittest

from closure_bot.modelo import URLS, Falhou, Modelos, custo_usd, ler_fila, ler_resposta, montar_corpo
from closure_bot.registro import Registro

ENTRADA = [{"role": "user", "content": "PROMPT DE SISTEMA"}, {"role": "user", "content": "ana: oi"},
           {"role": "assistant", "content": "Oi."}, {"role": "user", "content": "ana: e a Integridade?"}]
BOA = {"candidates": [{"content": {"parts": [{"text": "pensando", "thought": True}, {"text": " Integridade é... "}]},
                       "finishReason": "STOP"}],
       "usageMetadata": {"promptTokenCount": 8000, "candidatesTokenCount": 40, "thoughtsTokenCount": 110}}


class Formato(unittest.TestCase):
    def test_fila(self):
        self.assertEqual(ler_fila("vertex:gemini-3.8-flash, gemini:gemini-3.1-flash-lite,outro:x,vertex:"),
                         [("vertex", "gemini-3.8-flash"), ("gemini", "gemini-3.1-flash-lite")])

    def test_corpo_igual_ao_do_site(self):
        corpo = montar_corpo(ENTRADA)
        self.assertEqual(corpo["system_instruction"], {"parts": [{"text": "PROMPT DE SISTEMA"}]})
        self.assertEqual([c["role"] for c in corpo["contents"]], ["user", "model", "user"])
        self.assertEqual(corpo["generationConfig"], {"temperature": 0.8, "maxOutputTokens": 2048})

    def test_le_texto_sem_o_raciocinio_e_soma_os_tokens(self):
        self.assertEqual(ler_resposta(BOA), ("Integridade é...", False, 8000, 150))

    def test_resposta_cortada(self):
        dados = {"candidates": [{"content": {"parts": [{"text": "meia resp"}]}, "finishReason": "MAX_TOKENS"}]}
        self.assertEqual(ler_resposta(dados), ("meia resp", True, None, None))

    def test_vazia_e_bloqueada(self):
        with self.assertRaises(Falhou) as c:
            ler_resposta({"candidates": [{"finishReason": "SAFETY"}]})
        self.assertEqual(c.exception.codigo, "bloqueado")
        with self.assertRaises(Falhou) as c:
            ler_resposta({})
        self.assertEqual(c.exception.codigo, "vazio")


class Preco(unittest.TestCase):
    def test_tabela(self):
        self.assertAlmostEqual(custo_usd("gemini-3.8-flash", 8000, 150), 0.0065625)
        self.assertAlmostEqual(custo_usd("gemini-3.8-flash", 8000, 150, ano=2027), 0.013125)
        self.assertAlmostEqual(custo_usd("gemini-3.1-flash-lite", 1_000_000, 1_000_000), 1.75)

    def test_modelo_fora_da_tabela_conta_pelo_mais_caro(self):
        self.assertAlmostEqual(custo_usd("modelo-novo", 1_000_000, 0), 1.50)


class Fila(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.registro = Registro(":memory:")
        self.pedidos = []
        self.respostas = {}

    def tearDown(self):
        self.registro.fechar()

    async def _enviar(self, url, corpo, chave):
        self.pedidos.append((url, chave))
        resultado = self.respostas.get(url, BOA)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado

    def _modelos(self, fila, chaves, teto=9.0):
        return Modelos(ler_fila(fila), chaves, self.registro, enviar=self._enviar, teto_usd=teto)

    def _linhas(self):
        return self.registro._db.execute("SELECT modelo, persona, gatilho, tokens_entrada, tokens_saida, ok, erro FROM chamadas_api ORDER BY id").fetchall()

    async def test_primeiro_da_fila_responde_e_fica_registrado(self):
        m = self._modelos("vertex:gemini-3.8-flash,gemini:gemini-3.1-flash-lite", {"vertex": "CHAVE-V", "gemini": "CHAVE-G"})
        r = await m.responder(ENTRADA, persona="closure", gatilho="nome")
        self.assertEqual((r.texto, r.provedor, r.modelo, r.tokens_entrada, r.tokens_saida, r.cortada),
                         ("Integridade é...", "vertex", "gemini-3.8-flash", 8000, 150, False))
        self.assertEqual(self.pedidos, [(URLS["vertex"].format(modelo="gemini-3.8-flash"), "CHAVE-V")])
        self.assertEqual(self._linhas(), [("vertex:gemini-3.8-flash", "closure", "nome", 8000, 150, 1, None)])

    async def test_cai_pra_reserva_quando_o_primeiro_falha(self):
        m = self._modelos("vertex:gemini-3.8-flash,gemini:gemini-3.1-flash-lite", {"vertex": "CHAVE-V", "gemini": "CHAVE-G"})
        self.respostas[URLS["vertex"].format(modelo="gemini-3.8-flash")] = Falhou(429, "cota")
        r = await m.responder(ENTRADA, persona="kaltsit")
        self.assertEqual((r.provedor, r.modelo), ("gemini", "gemini-3.1-flash-lite"))
        linhas = self._linhas()
        self.assertEqual([(l[0], l[5]) for l in linhas], [("vertex:gemini-3.8-flash", 0), ("gemini:gemini-3.1-flash-lite", 1)])
        self.assertIn("429", linhas[0][6])

    async def test_provedor_sem_chave_sai_da_fila(self):
        m = self._modelos("vertex:gemini-3.8-flash,gemini:gemini-3.1-flash-lite", {"vertex": "", "gemini": "CHAVE-G"})
        self.assertEqual(m.fila, [("gemini", "gemini-3.1-flash-lite")])
        await m.responder(ENTRADA)
        self.assertEqual(len(self.pedidos), 1)

    async def test_todos_falham_levanta_o_ultimo_erro(self):
        m = self._modelos("vertex:a,gemini:b", {"vertex": "V", "gemini": "G"})
        self.respostas[URLS["vertex"].format(modelo="a")] = Falhou(500, "x")
        self.respostas[URLS["gemini"].format(modelo="b")] = {"candidates": [{"finishReason": "SAFETY"}]}
        with self.assertRaises(Falhou) as c:
            await m.responder(ENTRADA)
        self.assertEqual(c.exception.codigo, "bloqueado")
        self.assertEqual(len(self._linhas()), 2)

    async def test_gasto_do_mes_so_conta_o_pago_que_deu_certo(self):
        m = self._modelos("gemini:gemini-3.8-flash,vertex:gemini-3.8-flash", {"vertex": "V", "gemini": "G"})
        r = self.registro
        r.registrar_chamada(modelo="vertex:gemini-3.8-flash", tokens_entrada=1_000_000, tokens_saida=100_000)
        r.registrar_chamada(modelo="gemini:gemini-3.8-flash", tokens_entrada=5_000_000, tokens_saida=500_000)  # gratuito
        r.registrar_chamada(modelo="vertex:gemini-3.8-flash", ok=False, erro="500")                          # falhou
        r.registrar_chamada(modelo="vertex:gemini-3.1-flash-lite", tokens_entrada=1_000_000, tokens_saida=0)
        self.assertAlmostEqual(m.gasto_do_mes(), 0.75 + 0.375 + 0.25)

    async def test_no_teto_o_pago_sai_da_fila_e_o_gratuito_segue(self):
        m = self._modelos("vertex:gemini-3.8-flash,gemini:gemini-3.1-flash-lite", {"vertex": "V", "gemini": "G"}, teto=1.0)
        self.registro.registrar_chamada(modelo="vertex:gemini-3.8-flash", tokens_entrada=2_000_000, tokens_saida=0)  # US$ 1,50
        r = await m.responder(ENTRADA)
        self.assertEqual(r.provedor, "gemini")
        self.assertEqual([u for u, _ in self.pedidos], [URLS["gemini"].format(modelo="gemini-3.1-flash-lite")])

    async def test_no_teto_sem_gratuito_nao_chama_ninguem(self):
        m = self._modelos("vertex:gemini-3.8-flash", {"vertex": "V", "gemini": ""}, teto=1.0)
        self.registro.registrar_chamada(modelo="vertex:gemini-3.8-flash", tokens_entrada=2_000_000, tokens_saida=0)
        with self.assertRaises(Falhou) as c:
            await m.responder(ENTRADA)
        self.assertEqual(c.exception.codigo, "teto")
        self.assertEqual(self.pedidos, [])

    async def test_gratuito_primeiro_so_gasta_quando_a_cota_acaba(self):
        m = self._modelos("gemini:gemini-3.8-flash,vertex:gemini-3.8-flash", {"vertex": "V", "gemini": "G"})
        self.assertEqual((await m.responder(ENTRADA)).provedor, "gemini")
        self.respostas[URLS["gemini"].format(modelo="gemini-3.8-flash")] = Falhou(429, "cota do dia")
        self.assertEqual((await m.responder(ENTRADA)).provedor, "vertex")

    async def test_sem_chave_nenhuma(self):
        with self.assertRaises(Falhou) as c:
            await self._modelos("vertex:a", {"vertex": "", "gemini": ""}).responder(ENTRADA)
        self.assertEqual(c.exception.codigo, "sem_chave")


if __name__ == "__main__":
    unittest.main()
