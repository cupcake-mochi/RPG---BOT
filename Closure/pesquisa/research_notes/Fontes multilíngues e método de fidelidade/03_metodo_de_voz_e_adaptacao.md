# Frente 3: método para construir a voz e adaptar para pt-BR

> Nota de pesquisa, 12/10/2026. Pergunta: com o corpus da frente 1 em mãos, qual o melhor jeito de transformar falas em CN/EN numa Closure que soe natural em pt-BR? Complementa os passos 1 a 3 do relatório anterior, que já cobrem card curto e diálogos de exemplo.

## Achados com fonte

- **Falas reais do personagem dentro do prompt funcionam melhor que só descrição.** O ChatHaruhi ([arXiv 2308.09597](https://arxiv.org/abs/2308.09597), 2023) controla o modelo com "an improved prompt and memories of the character extracted from scripts", em 32 personagens de anime/TV CN e EN, e relata ganho em avaliação automática e humana sobre os baselines. **Conferido no PDF (validação 12/10/2026):** ele busca os trechos de roteiro mais próximos da mensagem por similaridade de cosseno ("we extract the M samples from D that are closest (in cosine similarity) to f(q)"), com número de trechos variável e teto de ~1.500 tokens para os trechos e ~1.200 para o histórico. Usou um embedding chinês que permite busca entre línguas.
- **Perfil e fala podem se contradizer, e isso estraga a imitação.** O BEYOND DIALOGUE ([arXiv 2408.10903](https://arxiv.org/abs/2408.10903), 2024) mostra que usar um perfil pronto para gerar diálogo produz "inconsistencies and even conflicts between the dialogue and the profile", e que o modelo acaba imitando o perfil em vez da fala. A proposta deles é alinhar cada fala aos traços do perfil, frase por frase.
- **Extrair "características de fala" de respostas reais melhora a reprodução de uma pessoa sem treino.** Trabalho do AIWolfDial 2024 ([ACL Anthology](https://preview.aclanthology.org/setup/2024.aiwolfdial-1.2)) combina perfil, respostas a poucas perguntas e "extracted speaking characteristics from those responses". Só li o resumo; sem números.
- **Localização de voz é transcriação, não tradução literal.** Guia da LocalizeDirect ([2021](https://localizedirect.com/posts/transcreation-in-video-game-localization)): o texto pode mudar inteiro desde que mantenha o tom e "evoke the same emotions as the original"; trocadilho se reconstrói na língua de chegada; o registro acompanha o público. Exemplo citado: Salsicha para Shaggy no pt-BR.

## Método proposto (inferência, montado sobre os achados)

1. **Fonte principal: inglês, original chinês como árbitro.** O EN do global é tradução profissional e já transcriado para tom ocidental; o CN tem as falas mais recentes e as 38 falas de operadora. Quando EN e CN divergem em tom, o CN decide o que ela quis dizer e o EN mostra como soar natural fora do chinês.
2. **Ficha de voz tirada do corpus, não da memória.** Rodar análise sobre `dados/corpus_closure/historia_en_US.jsonl` (1.557 falas):
   - tamanho médio de fala, frequência de exclamação, risadinha ("Heh heh~"), til, reticências;
   - como ela chama cada pessoa (Doutor, Kal'tsit, Amiya, Warfarin, Cliffheart);
   - temas recorrentes (vender coisa, dinheiro, comida, cansaço de engenheira, piada de segredo pago);
   - o que ela **não** faz (nunca fica solene por muito tempo? quando fica?).
   Cada traço da ficha cita 2 ou 3 falas de exemplo do corpus, o que resolve o problema do BEYOND DIALOGUE: o perfil nasce da fala, não o contrário.
3. **Adaptação para pt-BR por transcriação, com regras escritas.**
   - "Heh heh~" vira algo como "Hehe~" (manter o til, é marca visual dela).
   - Tratamento do Doutor: definir uma forma única ("Doutor" ou "Doc") e não variar.
   - Gíria brasileira leve e atual, sem regionalismo forte nem meme datado.
   - Nomes próprios e termos do universo no inglês do global (Rhodes Island, Originium), salvo onde o glossário pt-BR oficial do Endfield usar outra forma (frente 2).
   - Trocadilho de dinheiro e comércio se refaz em português, não se traduz.
4. **Dois usos do corpus no bot, separados:**
   - **Fixos no card:** 3 a 5 falas transcriadas a mão (o passo 3 do relatório anterior).
   - **Buscadas por similaridade:** um índice das 1.557 falas EN (com a fala anterior como contexto), e o bot injeta 2 ou 3 falas parecidas com a conversa do momento, no estilo ChatHaruhi. Em que língua essas falas entram no prompt fica **em aberto**: a pesquisa 1 (passo 3) infere que exemplo em inglês puxa português com cara de tradução; deixar em inglês é mais barato e preserva o original. Nenhum dos dois lados tem fonte; decidir no teste cego (frente 4). (Ajustado na validação de 12/10/2026.)
5. **Fatos de lore** saem do corpus pela mesma busca, o que conversa com o passo 4 do relatório anterior (lorebook por palavra-chave).

## Lacunas

- Não achei estudo que meça se exemplos em outra língua no prompt (EN) mantêm o estilo numa resposta em pt-BR melhor ou pior que exemplos já traduzidos. A bateria de teste (frente 4) decide.
- Não achei guia de localização da Yostar ou da Gryphline sobre a voz da Closure.
