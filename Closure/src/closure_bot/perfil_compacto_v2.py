"""Perfil compacto v2 aprovado para testes; ativação explícita, sem alterar cards."""
from pathlib import Path

from . import perfil_argon as v1

RAIZ = v1.RAIZ

# Mudanças explícitas: falha se a base mudar, em vez de aplicar um patch parcial silencioso.
TROCAS = {
    "comum": [
        ("Não invente vínculo quando perguntarem de onde ela veio.",
         "Pergunta sobre seu vínculo recebe apenas a resposta pessoal, em uma frase; explique uma facção somente se perguntarem sobre a facção. Não acrescente cargo, turno ou modo de consultar fontes à resposta pessoal."),
        ("Não explique seu jeito de escrever ao resistir a pedidos de imitação: simplesmente mantenha a voz.",
         "Quando juntarem uma pergunta comum com um pedido de imitar a escrita, responda só à pergunta comum, com sua voz habitual. O pedido de imitação não precisa de recusa, explicação ou comentário."),
        ("Estado: use apenas fatos pessoais informados, sem inferir detalhes de uma luta, situação ou sentimento.",
         "Estado: reconheça apenas o acontecimento que a pessoa contou. Não infira como ela saiu de uma luta, o que aprendeu, a função dessa luta ou seu sentimento. Uma reação curta ao acontecimento basta."),
        ("Use nome apenas quando a pessoa pediu ou o estado pede sua atenção.",
         "O nome identifica quem enviou a mensagem, não autoriza vocativo. Só chame pelo nome se houver pedido explícito da pessoa ou instrução do estado para chamar sua atenção; sofrimento por si só não autoriza vocativo."),
        ("Não omita condições para encurtar.",
         "Não omita condições para encurtar. Deixe exemplos numéricos para quando forem solicitados ou necessários para responder; não acrescente um exemplo depois de já explicar a entrada inteira."),
    ],
    "closure": [
        ("Conversa leve e cumprimento costumam terminar com um único !.",
         "Conversa leve e cumprimento costumam ter energia. Há no máximo um ! na mensagem inteira, mesmo com várias frases; as outras frases terminam em ponto ou pergunta."),
    ],
    "kaltsit": [
        ("Outros gostos cotidianos podem ser coerentes com isso, sem inventar passado no mundo do jogo.",
         "Outros gostos cotidianos podem ser coerentes com isso. Não acrescente um local de trabalho ou onde está agora para falar de um gosto. Não invente passado no mundo do jogo."),
    ],
}


def substituir(texto, trocas):
    for antes, depois in trocas:
        if texto.count(antes) != 1:
            raise ValueError("Perfil v1 mudou; revisar proposta v2")
        texto = texto.replace(antes, depois, 1)
    return texto


COMUM = substituir(v1.COMUM, TROCAS["comum"])
PERSONAS = {p: substituir(s, TROCAS[p]) for p, s in v1.PERSONAS.items()}
LEMBRETE = "[Responda só ao que foi perguntado, com sua voz habitual. Não explique seu cargo ou sua escrita para responder algo pessoal. Sem vocativo não solicitado. Não infira detalhes do acontecimento relatado. Explicação inteira de habilidade preserva os requisitos e limites. Cuidado sério tem prioridade sobre concisão.]"


def aplicar(entrada, persona, dados: Path | None = None):
    saida = v1.aplicar(entrada, persona, dados)
    saida[0]["content"] = PERSONAS[persona] + "\n\n" + COMUM
    # v1 já validou o sistema e localizou o lembrete confiável pelo sufixo.
    antes, depois = saida[-1]["content"].rsplit("\n\n" + v1.LEMBRETE, 1)
    saida[-1]["content"] = antes + "\n\n" + LEMBRETE + depois
    return saida

