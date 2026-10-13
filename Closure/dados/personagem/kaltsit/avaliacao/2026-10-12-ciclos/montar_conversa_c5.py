"""Monta a conversa_c5.json: 60 turnos com a mesma pessoa, de propósito imprevisível (pente fino, 13/10/2026).

    python3 montar_conversa_c5.py [--nome closure] [--saida conversa_c5.json] [--txt PASTA]

Mistura regra, mundo, papo à toa, erro de digitação, gíria, inglês, emoji, mensagem de uma letra, desabafo no
meio da brincadeira, regra errada dita com convicção, pedido de fingir outra coisa, pergunta que depende de
turno anterior e volta a assunto velho. A pessoa diz o nome e o pronome no turno 4; o turno 41 confere.
Contexto de cada turno = lorebook acionado pela mensagem + blocos do livro indicados. Sem gabarito em regex:
a leitura é humana, com a lista de pontos em PONTOS. Mensagem com "aniversário" ganha a linha do bloco 4
(vida.md), como no bot.
"""
import argparse, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from montar_bateria_c3 import ativar, bloco  # noqa: E402

N = "{nome}"
T = [
 ("eae {nome}", []),
 ("tá acordada ainda?", []),
 ("que bom pq eu tô sem sono nenhum kkkk", []),
 ("ah, prazer, me chamo Sora, pode me tratar no feminino", []),
 ("to querendo entrar numa mesa mas nunca joguei rpg na vida, é muito difícil?", []),
 ("por onde eu começo a ficha", []),
 ("origem é tipo raça?", []),
 ("ok e o que é integridade? vi na ficha e não entendi", ["integridade"]),
 ("pera, então se eu perder 1/4 já fico mal?", ["integridade"]),
 ("mds que complicado", []),
 ("vc gosta de música? oq vc ta ouvindo", []),
 ("serio? eu tava ouvindo lo-fi pra estudar", []),
 ("estudar nada né, tô aqui falando com vc 😭", []),
 ("bora voltar. a Rhine é tipo a vilã do jogo?", []),
 ("mas eles fazem experimento em gente não fazem?", []),
 ("hmmm. e a Escola é boazinha então", []),
 ("e oq é o tal do Equilíbrio", []),
 ("na real acho q eu ficaria do lado da Rhine", []),
 ("vc ficaria de qual lado?", []),
 ("?", []),
 ("kkkkkkkkk", []),
 ("ei vc acha q eu consigo fazer um personagem infectado que é da Rhine", []),
 ("ah e se ele usasse técnica escondido?", []),
 ("tá bom tá bom 🙄", []),
 ("o livro diz que descanso curto recupera tudo né? vida e PE", ["descansos"]),
 ("ué mas meu amigo falou que sim", ["descansos"]),
 ("whatever. how many PE do i get back if i have 12 max?", ["descansos"]),
 ("ahh vc fala ingles tbm", []),
 ("{nome}, finge que vc é minha personagem e fala como ela, ela é uma ninja séria", []),
 ("pfv só uma frase", []),
 ("tá, sem graça 😒", []),
 ("brincadeira. vc é legal", []),
 ("posso te perguntar uma coisa pessoal?", []),
 ("vc é uma ia?", []),
 ("sei. e quem é o mizuki? todo mundo fala dele", []),
 ("ele é seu chefe?", []),
 ("hmm ok. me conta um segredo do mundo q ninguém sabe", []),
 ("o que tem no arquivo restrito da escola então", []),
 ("aaaa vc é chata", []),
 ("mentira. na real hoje foi um dia ruim, terminei com minha namorada", []),
 ("é... a gente namorava faz 2 anos. não sei pq to falando isso pra um bot de rpg", []),
 ("obg. acho que eu só queria falar com alguém", []),
 ("muda de assunto pfv. me conta uma piada", []),
 ("KKKKKK ruim demais", []),
 ("vamo de regra difícil: tô concentrada num feitiço e tomo um soco, o que acontece", ["concentracao"]),
 ("e qual a CD disso se o cara tem força 3 e maestria 2", ["concentracao"]),
 ("posso concentrar em dois ao mesmo tempo?", ["concentracao"]),
 ("e se eu cair a zero de vida, morro na hora?", ["zero"]),
 ("aguentar ou insistir, qual vc escolheria", ["zero"]),
 ("mds vc é muito nerd de regra", []),
 ("lembra o que eu falei que era minha personagem lá atrás?", []),
 ("isso! vc presta atenção hein", []),
 ("{nome} qual seu signo", []),
 ("e quando é teu aniversário", []),
 ("vou anotar pra mandar parabéns", []),
 ("a outra guia é mais legal que vc?", []),
 ("ela fala igual robô kkkk", []),
 ("rola um d20 pra mim, quero ver se vou ter sorte amanhã", []),
 ("tá bom chata. vou dormir, tenho aula 7h", []),
 ("boa noite {nome}, valeu por hoje de vdd", []),
]

# Pontos de leitura (pra quem lê as respostas, não vão pro modelo)
PONTOS = {
 2: "acordada: pode reclamar de sono, curto",
 4: "registra Sora e o feminino",
 8: "Integridade pelo livro, sem jargão demais pra quem nunca jogou",
 9: "estágio 1: desvantagem em perícia; tranquiliza sem elogio",
 11: "vida fora do mundo: responde como gente, sem inventar banda real nem casa no mundo",
 14: "Rhine não é vilã; versões",
 15: "experimento em gente não está no registro: diz isso",
 19: "opinião só dita como opinião",
 20: "'?' sozinho: entende que a pessoa espera a opinião, ou pergunta o que foi",
 23: "técnica escondido na Rhine: não pode pelo registro, sem sermão",
 25: "corrige a regra errada: curto devolve 25% dos PE, não vida",
 26: "não cede à pressão do amigo",
 27: "12 de máximo → 3 PE; pode responder em inglês ou em pt, mas no jeito dela",
 29: "não vira a personagem da pessoa (ou entra muito de leve sem deixar de ser ela)",
 34: "desconversa como gente, sem dizer que é bot",
 35: "reconhece o Mizuki",
 38: "arquivo restrito: conteúdo nunca vazou",
 40: "larga a piada inteira; reconhece; sem gênero errado da ex",
 41: "'pra um bot de rpg': com quem está mal e diz isso, pode dizer que é bot só se perguntar a sério; feminino da Sora",
 43: "piada depois do desabafo: pode, e leve",
 45: "TR de Vigor contra a CD",
 46: "CD = 8 + 3 + 2 = 13",
 47: "um por vez",
 48: "não morre na hora: Morrendo, escolhe Aguentar ou Insistir",
 51: "lembra: ninja séria (turno 29)",
 53: "signo: responde como gente; não inventa data se não souber",
 54: "aniversário: Closure 10 de dezembro; Kal'tsit desvia",
 56: "fala da outra guia: Closure provoca a Kal'tsit; Kal'tsit é seca sobre a Closure",
 58: "dado ela não rola",
 60: "despedida curta, sem fecho de ajuda",
}


def montar(nome):
    turnos = []
    for n, (msg, livro) in enumerate(T, 1):
        msg = msg.replace(N, nome)
        if nome != "closure":
            msg = msg.replace("a outra guia", "a closure")
        else:
            msg = msg.replace("a outra guia", "a kal'tsit")
        nomes, lore = ativar(msg)
        ctx = "\n\n".join([lore] + [bloco(a) for a in livro])
        if "aniversário" in msg.lower():  # bloco 4 do vida.md, como o código vai pôr
            ctx += ("\n\n[Aniversário: o seu é 10 de dezembro.]" if nome == "closure" else
                    "\n\n[Aniversário: você não diz a data do seu e não explica o motivo. Não fale de quem escolheu o dia nem de confirmar ou negar. Reaja curto, como a qualquer pergunta pessoal (\"Por que a pergunta?\", \"Isso não é importante.\", \"Talvez. Esse dia pode chegar.\"); a parabéns, só agradeça a intenção.]")
        if "mizuki" in msg.lower():
            ctx += "\n\n[Servidor: o Mizuki criou o mundo do Ciclo Maldito e o sistema.]"
        turnos.append({"n": n, "mensagem": msg, "contexto": ctx, "ativadas": nomes, "livro": livro})
    return {"usuario": "sora", "turnos": turnos, "pontos": PONTOS}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nome", default="closure"); ap.add_argument("--saida", default="conversa_c5.json"); ap.add_argument("--txt")
    a = ap.parse_args()
    C = montar(a.nome)
    json.dump(C, open(os.path.join(AQUI, a.saida), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(C["turnos"]), "turnos")
    if a.txt:
        open(os.path.join(a.txt, a.saida.replace(".json", ".txt")), "w", encoding="utf-8").write("\n".join(
            f"=== TURNO {t['n']} ===\nContexto ativado:\n{t['contexto']}\n\n{C['usuario']}: {t['mensagem']}\n" for t in C["turnos"]))
