# Plano de montagem da personalidade e da vida da personagem

> Escrito em 12/10/2026. É o detalhe da **fase 4** do `PLANEJAMENTO.md`, que vem antes da
> montagem do bot (decisão do Mizuki). Serve pra qualquer personagem do top 10: onde
> aparece `<personagem>`, entra a escolhida. Tudo que sai daqui mora em `dados/personagem/`.

## Resumo

O método das pesquisas se sustenta, conferido nas fontes primárias, com **três ajustes**:

1. **Os exemplos fixos ficam em pt-BR, e as falas buscadas no corpus entram em inglês só como
   referência de atitude e assunto.** As duas pesquisas se contradiziam nesse ponto e nenhum
   estudo resolve; o teste cego decide (etapa 7).
2. **A ficha de voz tem que sair de contagem, não de memória.** Rodando o corpus da Closure:
   o "Heh heh~", tratado como bordão dela, aparece em **6 de 1.557 falas**; "money" aparece 3
   vezes e "LMD" 5. A ideia que a gente tinha da voz dela estava errada nos dois traços mais
   citados.
3. **O teste "quem falou" precisa filtrar o gatilho.** Em 762 das 1.557 falas da Closure, a
   fala anterior é dela mesma; só servem as que respondem a outra pessoa. E a fala de
   história tem mediana de 11 palavras, contra ~4 de humano no chat, então o teste de
   fidelidade e o teste de conversa no Discord são separados.

A "vida" da personagem (rotina, humor, relações, iniciativa) entra como **estado calculado
pelo código**, sem chamada extra de API, mais uma reflexão em lote por dia. É a versão barata
da arquitetura de Generative Agents.

## Validação do método

| Pilar | O que a pesquisa disse | Conferido onde | Veredito |
| ----- | ---------------------- | -------------- | --------- |
| Voz tirada da fala, não de perfil escrito | Perfil escrito antes contradiz a fala e o modelo imita o perfil | BEYOND DIALOGUE ([2408.10903](https://arxiv.org/abs/2408.10903)); contagem no `historia_en_US.jsonl` | **Confirmado**, e o corpus mostrou na prática: os traços "de memória" da Closure eram raros |
| Falas reais buscadas por similaridade (ChatHaruhi) | Busca as falas parecidas com a mensagem e põe no prompt | PDF do [ChatHaruhi](https://arxiv.org/pdf/2308.09597): embedding, cosseno, as M mais próximas, até ~1.500 tokens de memória e ~1.200 de histórico | **Confirmado.** Mas o ganho dele vem de reusar a fala original na mesma língua; aqui ela vira tradução, então o efeito não se transfere inteiro |
| Exemplos EN no prompt, resposta em pt-BR | Relatório 1: tende a sair "português traduzido". Relatório 2: manter o índice em EN | Nenhum estudo achado nos dois relatórios nem agora | **Em aberto.** Ajuste 1 acima, decidido no teste cego |
| Lembrete específico no fim do prompt | Reinjetar persona corta 35–38% do desvio; instrução específica corta 87% | Resumo de [2609.24532](https://arxiv.org/abs/2609.24532); desvio aparece em até 8 rodadas ([Li et al., 2402.10962](https://arxiv.org/abs/2402.10962)) | **Confirmado.** Os dois estudos não são de personagem de ficção |
| Nome conhecido ajuda o modelo | Anonimizar o nome derruba o desempenho | [2603.03915](https://www.alphaxiv.org/abs/2603.03915) | **Confirmado.** Personagem muito presente na internet (Amiya, Kal'tsit, W) ganha voz "de graça" mas traz junto lore de memória, que pode estar errada ou ser de versão CN. Personagem de nicho depende mais do card |
| LLM-juiz não serve como nota final | Melhor LLM ~69% vs humanos 90,8% em dizer quem fala | Resumo do [PersonaEval](https://arxiv.org/abs/2508.10014v1) | **Confirmado** |
| Memória, reflexão e plano dão "vida" | Generative Agents | Resumo de [Park et al., 2304.03442](https://arxiv.org/abs/2304.03442): observação, plano e reflexão contribuem pra credibilidade, segundo a ablação | **Confirmado, com custo.** Lá cada passo é chamada de modelo; aqui a rotina e o humor viram regra no código e só a reflexão usa API, uma vez por dia |

Continua sem resposta: número mínimo de avaliadores e de falas pro teste cego (20 falas e 3 a
5 pessoas segue sendo chute razoável), e se existe tradução de fã pt-BR em grupo fechado.

## As etapas

Cada etapa salva o próprio arquivo assim que fecha. As etapas 1 a 5 e o teste da 7 rodam no
SillyTavern, antes de existir bot. A 6 é desenhada agora e implementada depois da fase 1.

### Etapa 0: extrair e delimitar o canon

- Rodar o extrator do corpus pro nome escolhido, **juntando as variantes** (alter, títulos,
  "???" antes da revelação). Saída: `dados/corpus_<id>/`, igual ao da Closure.
- Puxar as falas de operadora e o arquivo pessoal: em EN se a operadora já saiu no global, só
  em CN se não.
- Escrever `dados/personagem/canon.md`: fatos com a fonte de cada um, e uma linha de **corte
  de tempo** (até qual evento ela "sabe" das coisas). Fato que mudou depois (retcon, revelação
  em evento posterior, diferença entre CN e global) fica marcado.
- **Pronto quando:** o corpus tem a contagem esperada da lista de falantes, e cada fato do
  canon tem fonte.

### Etapa 1: ficha de voz

- Script de contagem sobre o corpus EN: tamanho de fala, pontuação, interjeições, como ela
  chama cada pessoa, palavras que voltam, com quem ela mais fala.
- Leitura humana de ~100 falas de situações diferentes: humor, quando fica séria, o que ela
  nunca faz.
- Saída: `dados/personagem/voz.md`. **Cada traço cita 2 ou 3 falas reais e a frequência.**
  Traço que não tem fala pra citar sai da ficha.
- **Pronto quando:** nenhum traço da ficha é só impressão.

### Etapa 2: regras de transcrição pra pt-BR

- `dados/personagem/glossario.md`: tratamento fixo do Doutor e dos outros, nomes próprios
  (inglês do global ou o pt-BR oficial do Endfield), termos do universo, como ficam as
  interjeições e a pontuação dela, como refazer trocadilho.
- Nível de gíria: leve e atual, sem regionalismo forte nem meme datado.
- **Pronto quando:** 10 falas de teste transcritas por duas pessoas diferentes seguindo o
  glossário saem parecidas.

### Etapa 3: card

- Um ou dois parágrafos de prosa com fatos concretos, uma seção curta do jeito de falar
  (resumo da etapa 1) e o glossário. Traços escritos pelo que ela faz, não por proibição.
- Campos do Character Card V2, em `dados/personagem/card.json`.
- **Pronto quando:** abre no SillyTavern e a conversa de teste soa como ela em 5 gatilhos.

### Etapa 4: banco de exemplos em pt-BR

- 12 a 20 trocas curtas, transcritas a mão de falas reais: conversa à toa, ajuda técnica,
  provocação, momento sério, pergunta de regra do Ciclo Maldito, pergunta que ela não sabe.
- Tamanho de Discord: uma ou duas frases. Aberturas variadas, nenhum bordão repetido.
- 3 a 5 ficam fixos no prompt; o resto é reserva pra rotação, se os logs mostrarem cópia.
- Saída: `dados/personagem/exemplos.md`.

### Etapa 5: lorebook

> Pra Kal'tsit (12/10/2026): o lorebook é do **mundo do Ciclo Maldito** e do servidor, não de
> Arknights. A fonte é o doc de lore do mundo do Mizuki; o doc do arco (Balança Quebrada) fica de
> fora, porque é segredo de campanha. Ela é guia do mundo e do sistema, fora do arco.

- 30 a 80 entradas acionadas por palavra-chave, cada uma escrita como "fato + o que ela acha
  disso". Chaves com e sem acento, apelido e nome em inglês.
- No máximo 2 ou 3 entradas sempre ligadas.
- O índice de falas EN por similaridade (ajuste 1) fica pronto aqui, mas só entra no prompt
  se ganhar no teste.
- Saída: `dados/personagem/lorebook.json`.

### Etapa 6: vida da personagem

Desenho agora, em `dados/personagem/vida.md`; código depois da fase 1.

- **Premissa no servidor:** por que ela está no Discord da guilda e o que ela faz ali. É a
  decisão que mais muda o tom, e é do Mizuki.
- **Rotina:** tabela por horário de Brasília e dia da semana (trabalhando, comendo, dormindo,
  de folga), tirada do papel dela no mundo do Ciclo Maldito (pra Kal'tsit, ver `mundo.md`; o
  canon de Arknights não vale). O código põe o estado atual no bloco 4 do
  prompt. Sem chamada extra.
  > Pra Kal'tsit (12/10/2026): ela fica **fora da história**, então não tem rotina no mundo.
  > A rotina vira a do servidor: horário de plantão no Discord, véspera e dia de sessão de mesa,
  > movimento do canal. Ela não come, dorme nem trabalha "no mundo"; no máximo está ou não está
  > de plantão.
- **Humor e energia:** duas ou três variáveis simples que sobem e descem com o horário e com o
  que acontece no canal. Mudam a chance de ela entrar na conversa e o tom do lembrete. Sem
  chamada extra.
- **Relações:** a ficha de 5 a 15 fatos por pessoa que o primeiro relatório já previa, mais
  um apelido e um nível de intimidade que muda devagar.
- **Calendário:** aniversário dela, eventos do jogo, sessões de mesa do Ciclo Maldito. Ela
  comenta antes e depois.
- **Iniciativa:** posts espontâneos raros, com teto por dia e só em horário em que ela
  "está acordada".
- **Reflexão diária:** uma chamada por dia em lote resume o canal e atualiza as fichas das
  pessoas.
- **Limites:** canon, card e regras nunca são graváveis pela conversa; memória é dado, não
  instrução; comando pra cada um ver e apagar a própria ficha.

### Etapa 7: avaliação

> Pra Kal'tsit (12/10/2026): sem o teste cego, porque ninguém do servidor joga Arknights. No
> lugar, nota de 1 a 5 dos jogadores no canal de teste (acertou, ajudou, jeito agrada). Ver
> `dados/personagem/kaltsit/avaliacao/2026-10-12-etapa7.md`.

- **Teste de fidelidade:** ~20 falas reais que **respondem a outra pessoa** (filtro do ajuste
  3) e que não entraram no card nem nos exemplos, transcritas pelo glossário, misturadas com
  ~20 respostas do bot pros mesmos gatilhos, pedindo a mesma extensão. 3 a 5 pessoas que
  conhecem a personagem apontam quais são do jogo. Meta: acerto perto de 50%.
- **Nota de 1 a 5** nos 6 critérios do CharacterEval já escolhidos.
- **Teste de conversa no Discord**, separado: bateria de 15 a 20 mensagens do primeiro
  relatório, conversa de 30 turnos (desvio), busca de cópia literal dos exemplos e card com
  nome trocado (quanto vem do nosso texto e quanto da memória do modelo).
- **A/B do ajuste 1:** com e sem as falas EN buscadas, mesma bateria.
- Resultado em `dados/personagem/avaliacao/<data>.md`, pra comparar versões.

### Etapa 8: congelar a v1

- `dados/personagem/VERSAO.md` com a versão e o que mudou. Qualquer mudança de card, exemplo,
  modelo ou parâmetro roda a etapa 7 de novo e muda uma variável por vez.

## O que depende do Mizuki

- Escolher a personagem (abre a etapa 0).
- A premissa dela no servidor (etapa 6).
- Revisar as transcrições e o glossário (etapas 2 e 4): é trabalho de autor, não de script.
- Juntar 3 a 5 pessoas que conhecem a personagem pro teste cego (etapa 7).
