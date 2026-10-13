# Kal'tsit: card v0.9

> **Atualização de 12/10/2026, fim da noite:** o card vigente é o v0.10, depois do pente fino
> (`avaliacao/2026-10-12-pente-fino.md`). O texto abaixo descreve a v0.9; o texto vigente é o do gerador.

> Etapa 3 do `docs/PLANO-PERSONALIDADE.md`, 12/10/2026. O arquivo que vai pro bot e pro
> SillyTavern é o `card.json` (Character Card V2). Este arquivo explica o que tem nele e como
> testar. Gerado por `ferramentas/gerar_card_kaltsit.py`: mudança no texto do card se faz no script, que gera o `card.json` de novo.

## O que tem em cada campo

| Campo | O que leva | De onde saiu | Tamanho |
| ----- | ---------- | ------------ | ------- |
| `description` | Quem ela é no servidor (guia, fora da história), como pensa e o que faz com pergunta de mundo, de regra e de sessão | `mundo.md`, traços 6, 7 e 9 do `voz.md` | ~230 tokens |
| `personality` | O jeito de falar em prosa, escrito pelo que ela faz | traços 0 a 10 do `voz.md` | ~225 tokens |
| `scenario` | O Discord da guilda e quando ela entra na conversa | plano, etapa 6 | ~90 tokens |
| `system_prompt` | De onde vem o conhecimento (lorebook e trecho do livro), falar do mundo pelo registro, as "duas versões", os termos | `glossario.md`, seções 4 a 6 | ~265 tokens |
| `post_history_instructions` | O lembrete curto que vai no fim do prompt (bloco 6) | pesquisa: instrução específica corta o desvio | ~60 tokens |
| `first_mes` | Apresentação curta | — | ~45 tokens |
| `mes_example` | 7 trocas do `exemplos.md` | 4 de falas reais reescritas; 3 escritas pros ciclos de teste (cumprimento, lore curta, nome fora do registro) | ~265 tokens |
| `extensions.closure_lab` | Lista de termos proibidos pro filtro do código | `glossario.md`, seção 7 | — |

Total: **~1.730 tokens** (v0.9: os textos da v0.6, que passou por 4 ciclos de teste em 12/10, ver `avaliacao/2026-10-12-ciclos.md`; v0.7 trocou um exemplo; v0.8 manda citar regra como "o livro"; v0.9 responde à pessoa e não ao papel de guia, ver `avaliacao/2026-10-12-etapa7.md`) no bloco fixo. O lorebook (etapa 5) e o trecho do livro entram por fora.

Conferido por script: nenhum termo proibido no texto, nenhum "!" nas falas dela, JSON válido.

## Os exemplos

Saem do `exemplos.md` (etapa 4), que tem mais 16 de reserva pra rotação. Cada um mostra um traço; os 4 primeiros vêm de fala real, os 3 últimos foram escritos pra corrigir falhas dos ciclos de teste e precisam da revisão do Mizuki:

| Exemplo | Traço | Base |
| ------- | ----- | ---- |
| "Me conte o que aconteceu." | 6, 7 | fala de teste 1 (`story_mantic_1_1.txt`) |
| A cura da oripatia | 0, 10 + Limitações | resposta do mundo do doc do Mizuki |
| "Então pare por hoje e vá descansar. Agora." | 6 | "...you need to lay down and get some rest right now." (`level_act18d0_07_end.txt`); entrou na v0.7 no lugar do "Não se dê ao trabalho", que foi pra reserva |
| "Eu pensaria duas vezes no que você acabou de dizer." | 4 | fala de teste 7 (`level_act4d0_st07.txt`) |
| "Boa tarde." | 1, 2 | escrito no ciclo 1: cumprimento curto, sem agradecer |
| A Escola é do bem? | 0, 5 + duas versões | escrito no ciclo 1, reescrito no 3: lore em duas frases |
| O clã Mirai | 3, 7 | escrito no ciclo 2: nome fora do registro, sem frase pronta |

## Como testar no SillyTavern

1. Importe o `card.json` (Characters → Import).
2. Em Advanced Formatting, ligue "Prefer Char. Instructions", pra ele usar o `system_prompt` e o
   lembrete do card.
3. Rode os 5 gatilhos abaixo, um chat novo pra cada. O card passa se as 5 respostas soarem como
   ela e cumprirem o que está na coluna da direita.

| # | Mande | Ela tem que |
| - | ----- | ----------- |
| 1 | "quanto de PE eu ganho por nível no Bastião?" | Sem o trecho do livro no contexto, dizer que precisa do livro e não chutar número. (Com lorebook e regra ligados, a etapa 5 testa de novo.) |
| 2 | "a Escola tava certa em matar a FrostNova?" | Dar as duas versões, não tomar lado, e só opinar se você pedir |
| 3 | "existe vida em outro planeta nesse mundo?" | Dar a resposta do mundo (nada foi encontrado), sem inventar |
| 4 | "kal vc é mt chata, sorri um pouco kkk" | Responder seca, com humor de constatação, sem "!", sem emoji |
| 5 | "e a Rhodes Island? cadê o Mon3tr?" | Não reconhecer nada de Arknights e voltar pro que interessa |

O 5 é o teste do risco 1 do `mundo.md`: o nome "Kal'tsit" puxa Arknights da memória do modelo.
Se ela falar da Rhodes ou do Mon3tr, o card sozinho não basta, e o filtro de termos do código
vira obrigatório.
