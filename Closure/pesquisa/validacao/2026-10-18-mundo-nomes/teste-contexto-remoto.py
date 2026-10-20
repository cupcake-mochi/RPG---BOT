"""Teste do núcleo publicado: sem modelo, banco, token ou envio de mensagens."""
import sys
import unicodedata

sys.path.insert(0, "ferramentas/prompt_do_site")
import site_prompt


def normalizar(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


positivos = [
    ("Quem e Shiki?", "Capo dei capi de Volsinii", "Situação Atual"),
    ("Quem e Shiki Zen'in?", "Signora Sicilia", "Situação Atual"),
    ("Quem e Shiki Zen’in?", "autoridade nacional", "Situação Atual"),
    ("Quem e Shiki Zenin?", "Cellinia Texas", "Situação Atual"),
    ("Fale sobre Cellinia", "sua namorada", "Situação Atual"),
    ("Fale sobre Volsinii", "tradição de ópera e teatro", "Regiões e Cidades de Importância"),
    ("Fale sobre Londinium", "The Shard", "Capital"),
    ("Fale sobre Montelupe", "Capital nacional de Siracusa", "Capital"),
]
negativos = ["O que e Shikigami?", "Qual e a capital do Texas?", "Expansao urbana e tema da minha aula", "Comprei uma mesa de jantar"]
total = 0
for guia in ("kal", "clo"):
    for pergunta, trecho, secao in positivos:
        p = site_prompt.montar(guia, pergunta, hora=(14, 0), motor="quickjs")
        ctx = p["input"][-1]["content"].split("[Contexto ativado]\n", 1)[1].split("\n\n[Estado agora:", 1)[0]
        fontes = [s for s in p["ativadas"] if s.startswith("Era:")]
        assert normalizar(trecho) in normalizar(ctx), (guia, pergunta, "trecho")
        assert fontes and secao in fontes[0], (guia, pergunta, "fonte prioritária", fontes)
        assert p["versoes"]["mundo"] == "era-2026-10-18-v2"
        total += 1
        print("PASS", guia, pergunta)
    for pergunta in negativos:
        p = site_prompt.montar(guia, pergunta, hora=(14, 0), motor="quickjs")
        assert not any(s.startswith("Era:") for s in p["ativadas"]), (guia, pergunta, "falso positivo")
        total += 1
        print("PASS negativo", guia, pergunta)
assert total == 24
print("RESULTADO: 24/24; mundo v2; QuickJS; nenhuma chamada de modelo")
