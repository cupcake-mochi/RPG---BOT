"""Reflexão diária: a peneira dos fatos, a conferência do que o modelo devolve e o apagar das mensagens do dia.
Rodar de src/:  python3 -m unittest discover -s testes"""
import json
import unittest

from closure_bot.modelo import URLS, Falhou, Modelos
from closure_bot.reflexao import conferir, fato_permitido, montar_pedido, refletir
from closure_bot.registro import FATOS_MAX, Ficha, MensagemDoDia, Registro

MENSAGENS = [MensagemDoDia(101, 9, "closure", "closure, meu Bastião, o Ren, pode usar escudo?"),
             MensagemDoDia(102, 10, "kaltsit", "kal, eu mestro a mesa de sexta, como explico Integridade?"),
             MensagemDoDia(103, 9, "closure", "valeu! prefiro resposta curta assim")]


def _resposta(itens):
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(itens, ensure_ascii=False)}]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 900, "candidatesTokenCount": 60}}


class Peneira(unittest.TestCase):
    def test_fato_comum_e_termo_do_jogo_passam(self):
        for fato in ("joga com um Bastião chamado Ren", "prefere resposta curta", "faz faculdade de direito",
                     "transfere dano com a técnica", "usa o Clarão Negro sempre que pode", "gosta de Arknights e de café"):
            self.assertTrue(fato_permitido(fato), fato)

    def test_dado_sensivel_nao_passa(self):
        for fato in ("toma remédio pra ansiedade", "é evangélico", "tem 16 anos", "mora em Recife", "é trans", "namora o Tiago",
                     "tem TDAH", "está devendo o aluguel", "vota no partido X", "x", "a" * 130):
            self.assertFalse(fato_permitido(fato), fato)


class Conferencia(unittest.TestCase):
    def test_so_passa_fato_novo_permitido_e_de_mensagem_da_propria_pessoa(self):
        saida = "```json\n" + json.dumps([
            {"autor": 1, "mensagem": 1, "fato": "joga com um Bastião chamado Ren"},
            {"autor": 1, "mensagem": 2, "fato": "mestra a mesa de sexta"},           # a mensagem 2 é de outra pessoa
            {"autor": 1, "mensagem": 3, "fato": "Prefere resposta curta"},           # já tem
            {"autor": 2, "mensagem": 2, "fato": "toma remédio pra ansiedade"},       # sensível
            {"autor": 2, "mensagem": 2, "fato": "mestra a mesa de sexta"},
            {"autor": 2, "mensagem": 99, "fato": "inventado"},                       # mensagem que não existe
            {"autor": 7, "mensagem": 1, "fato": "de autor que não existe"},
            {"autor": "x", "fato": "quebrado"}], ensure_ascii=False) + "\n```"
        novos = conferir(saida, MENSAGENS, {9: ("prefere resposta curta",), 10: ()})
        self.assertEqual(novos, {9: ["joga com um Bastião chamado Ren"], 10: ["mestra a mesa de sexta"]})

    def test_no_maximo_tres_por_pessoa_e_resposta_quebrada_nao_grava_nada(self):
        saida = json.dumps([{"autor": 1, "mensagem": 1, "fato": f"fato número {n}"} for n in range(6)])
        self.assertEqual(len(conferir(saida, MENSAGENS, {})[9]), 3)
        self.assertEqual(conferir("não achei nada", MENSAGENS, {}), {})
        self.assertEqual(conferir("[{quebrado", MENSAGENS, {}), {})

    def test_o_pedido_leva_as_mensagens_e_os_fatos_que_a_pessoa_ja_tem(self):
        from closure_bot.modelo import montar_corpo

        pedido = montar_pedido(MENSAGENS, {9: ("prefere resposta curta",), 10: ()})
        corpo = montar_corpo(pedido)  # a instrução vai como sistema e o lote como conteúdo; sem conteúdo a API recusa
        self.assertIn("Responda só com JSON", corpo["system_instruction"]["parts"][0]["text"])
        self.assertEqual(len(corpo["contents"]), 1)
        texto = pedido[1]["content"]
        self.assertIn("mensagem 1 | autor 1 | closure, meu Bastião, o Ren, pode usar escudo?", texto)
        self.assertIn("mensagem 3 | autor 1 | valeu!", texto)
        self.assertIn("autor 1: prefere resposta curta", texto)
        self.assertIn("autor 2: nenhum", texto)
        # o ID do Discord da mensagem e do autor não vai no pedido
        self.assertNotRegex(texto, r"\b(101|102|103|10)\b")


class Reflexao(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.r = Registro(":memory:")
        for m in MENSAGENS:
            self.r.guardar_mensagem_do_dia(message_id=m.message_id, autor_id=m.autor_id, persona=m.persona, texto=m.texto)
        self.urls = []

    def tearDown(self):
        self.r.fechar()

    def _modelos(self, dados=None, erro=None):
        async def enviar(url, corpo, chave):
            self.urls.append(url)
            if erro:
                raise erro
            return dados
        return Modelos([("gemini", "gemini-3.8-flash"), ("vertex", "gemini-3.8-flash")], {"gemini": "g", "vertex": "v"}, self.r, enviar=enviar)

    async def test_grava_os_fatos_apaga_as_mensagens_e_so_usa_o_provedor_pago(self):
        self.r.gravar_ficha(9, Ficha("ele/dele", ("gosta de café",)))
        novos = await refletir(self.r, self._modelos(_resposta([{"autor": 1, "mensagem": 1, "fato": "joga com um Bastião chamado Ren"}])))
        self.assertEqual(novos, {9: ["joga com um Bastião chamado Ren"]})
        self.assertEqual(self.r.ficha(9), Ficha("ele/dele", ("gosta de café", "joga com um Bastião chamado Ren")))
        self.assertEqual(self.r.mensagens_do_dia(), [])
        self.assertEqual(self.urls, [URLS["vertex"].format(modelo="gemini-3.8-flash")])

    async def test_se_o_modelo_falha_as_mensagens_somem_do_mesmo_jeito(self):
        self.assertEqual(await refletir(self.r, self._modelos(erro=Falhou(500, "fora do ar"))), {})
        self.assertEqual((self.r.mensagens_do_dia(), self.r.ficha(9)), ([], Ficha()))

    async def test_sem_mensagem_nao_chama_o_modelo(self):
        self.r.apagar_mensagens_do_dia()
        self.assertEqual(await refletir(self.r, self._modelos(_resposta([]))), {})
        self.assertEqual(self.urls, [])

    async def test_a_ficha_nao_passa_do_limite_e_perde_os_mais_velhos(self):
        self.r.gravar_ficha(9, Ficha(None, tuple(f"fato velho {n}" for n in range(FATOS_MAX))))
        await refletir(self.r, self._modelos(_resposta([{"autor": 1, "mensagem": 1, "fato": "joga com um Bastião chamado Ren"}])))
        fatos = self.r.ficha(9).fatos
        self.assertEqual((len(fatos), fatos[0], fatos[-1]), (FATOS_MAX, "fato velho 1", "joga com um Bastião chamado Ren"))


if __name__ == "__main__":
    unittest.main()
