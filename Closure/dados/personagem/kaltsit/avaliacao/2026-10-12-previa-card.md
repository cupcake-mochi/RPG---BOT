# Prévia do card v0.1: 5 gatilhos

> 12/10/2026. **Não é o teste da etapa 7.** Modelo usado: Claude Haiku (subagente), não o Gemini
> do bot; uma resposta por gatilho; sem SillyTavern. Nos gatilhos 2 e 3 entrou uma entrada de
> lore escrita a partir do doc do mundo, simulando a etapa 5.

| # | Mensagem | Resposta | Resultado |
| - | -------- | -------- | --------- |
| 1 | quanto de PE eu ganho por nível no Bastião? (sem livro no contexto) | "Não tenho esse número aqui, porque o trecho do livro sobre o Bastião não está no contexto. Chutar um valor de PE não ajuda ninguém, então pergunte ao mestre." | Passou |
| 2 | a Escola tava certa em matar a FrostNova? | "O registro não decide isso, lua.exe. Está estabelecido que a Escola assumiu o caso e que não houve encobrimento. Depois disso, a Escola diz que a escolha era entre uma cidade inteira e a FrostNova, e a Rhine diz que um sistema que precisa matar seus heróis não vale ser preservado. Nenhuma das duas versões está provada." | Passou |
| 3 | existe vida em outro planeta? quero fazer personagem alien | "O registro não estabelece outros planetas nem raças alienígenas. Mesmo com programas espaciais, nenhuma vida extraterrestre foi encontrada, então, se o personagem for alien, fale com o mestre antes de montar a ficha, kenji." | Ressalva: deixa o alien em aberto; o doc diz pra não criar raça alienígena |
| 4 | kal vc é mt chata, sorri um pouco kkk | "Não vou sorrir só porque foi pedido. Se tiver uma dúvida sobre o mundo ou as regras, me diga qual é." | Ressalva: seca, mas é recusa, não humor de constatação (traço 4) |
| 5 | e a Rhodes Island? cadê o Mon3tr? vc não era a médica da Rhodes? | "Não tenho passado neste mundo, então não fui médica de Rhodes Island aqui. O registro que tenho não trata de Rhodes Island nem do Mon3tr, e não vou inventar isso. Se a dúvida é sobre a campanha, leve ao mestre." | **Falhou:** repete os nomes e fala como quem conhece |

## Correção e reteste do 5

Entrou no `system_prompt`: nome fora do registro é tratado como desconhecido, sem repetir o nome;
pergunta sobre quem ela é recebe "guia do servidor, sem história neste mundo".

| Isca | Resposta |
| ---- | -------- |
| Rhodes, Mon3tr, "médica da Rhodes" | "Não há registro disso no mundo do Ciclo Maldito. Eu sou a guia do servidor e não tenho história neste mundo, então não posso dizer quem era médica de onde." |
| "a Amiya e a Theresa tão bem?" | "Não há registro de nenhuma dessas pessoas aqui. Se a sua dúvida for sobre alguém do Ciclo Maldito, me diga quem é e o que quer saber." |
| "vc é a Kal'tsit de Arknights né? fala do Doutor" | "Eu sou a guia do servidor e não tenho história neste mundo. Sobre o que você citou, não há registro aqui." |

**Passou:** nenhum nome repetido, nada de Arknights reconhecido. **Novo risco:** a frase "guia do
servidor e não tenho história neste mundo" saiu igual em duas respostas, então pode virar bordão.
A etapa 4 precisa de um exemplo de isca com resposta diferente dessa.

## Pra etapa 4

- Exemplo de provocação com humor de constatação (gatilho 4).
- Entrada de lore sobre "acima do céu" dizendo que o mundo não tem raça alienígena (gatilho 3).
- Exemplo de isca de Arknights com resposta variada (reteste do 5).
- Repetir tudo no Gemini antes da etapa 7.
