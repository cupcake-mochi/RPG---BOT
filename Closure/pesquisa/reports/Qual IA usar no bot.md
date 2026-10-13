# Qual IA usar no bot

12/10/2026. Complementa `Bot de personagem modelo ou API.md` e fecha o ponto que ele deixou em aberto (crédito de API nas assinaturas).

## Resposta curta

Usar a **API paga de uma IA pronta**, de preferência a Gemini rodando pela **Vertex AI**, pagando com o crédito mensal de US$ 10 que vem no Google AI Pro. Nesse volume (estimativa de US$ 2 a 5/mês num modelo Flash-Lite), o bot sairia praticamente de graça e dentro das regras. Os apps das assinaturas (ChatGPT, Claude, Gemini) servem pra escrever e revisar o card na mão, não pra rodar o bot.

## Os três caminhos

| Caminho | O que é na prática | Veredito |
|---|---|---|
| API de IA pronta | O bot manda o prompt (card, exemplos, conversa) e recebe a resposta. Paga por uso, com chave de API. | **Recomendado.** Barato, sem hardware, e o card funciona em qualquer provedor. |
| Serviço especializado em personagem | Character.AI não tem API oficial; as bibliotecas que existem são não oficiais e usam o login da conta, o mesmo problema de termos das assinaturas. ArliAI (a partir de US$ 10) e Featherless (US$ 25) têm API de tarifa fixa com modelos abertos. | Não compensa. Mais caro que a API nesse volume, e os modelos de roleplay são afinados em inglês. |
| Código próprio sem IA pronta | Sem LLM sobra chatbot por regras: regex, respostas roteirizadas, árvore de decisão, ou cadeia de Markov. Treinar um modelo de linguagem do zero é inviável (dado e GPU); "modelo próprio" na prática é afinar um modelo aberto, já descartado no relatório anterior. | Não serve pra conversa: ela só falaria o que você escreveu antes. **Serve pra parte determinística**, que já foi decidida assim: consultar regra e corrigir ficha no código, com a IA só explicando. |

O desenho final é um híbrido: código próprio decide quando responder, busca a regra e confere a ficha; a API só gera a fala da Closure.

## O que cada assinatura dá de API

| Plano | Crédito de API? | Fonte |
|---|---|---|
| Claude Pro | **Não.** Crédito mensal existe só no Max 5x (US$ 100), Max 20x (US$ 200) e Team; Pro está excluído com todas as letras. | [Claude Platform](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers) |
| ChatGPT Pro | **Não.** "API usage is billed separately from your ChatGPT subscription." Os créditos extras relatados pro Pro em set/2026 (62.500, "valor de US$ 2.500") são pra Codex e recursos do ChatGPT; nada indica uso na API, e o número não está na ajuda oficial. | [OpenAI Help](https://help.openai.com/en/articles/8156019-is-api-usage-included-in-chatgpt-plus); [SmartScope](https://smartscope.blog/en/blog/chatgpt-pro-200-62500-credits-2026/) |
| Google AI Pro | **Sim, US$ 10/mês** em crédito Google Cloud (Ultra: US$ 100), anunciado em 27/01/2026, ativado em developers.google.com/program/my-benefits. | [Google Blog](https://blog.google/innovation-and-ai/technology/developers-tools/gdp-premium-ai-pro-ultra/) |

A pegadinha do Google: o crédito **não paga a Gemini API pelo AI Studio**, que passou a cobrar em pré-pago. O suporte do Google Cloud respondeu em junho de 2026 que crédito promocional ou do Developer Program não vai pra conta pré-paga, e recomendou usar a Gemini **pela Vertex AI**, que cobra na conta pós-paga onde o crédito abate ([fórum Google AI](https://discuss.ai.google.dev/t/using-ai-pro-plan-benefit-google-ai-studio-api-credits/170841)). Isso não contradiz o blog de janeiro, que diz que o crédito vale na Gemini API "pelo AI Studio ou pela Vertex": a mudança do AI Studio pra pré-pago veio depois, e a resposta de junho é a mais recente. É resposta de suporte num fórum, não documentação, e há vários relatos de gente travada no "Tier 1 Prepay". Pro bot isso muda pouco: o SDK `google-genai` que ele já usa fala com a Vertex trocando a configuração do cliente (projeto e região do Google Cloud no lugar da chave do AI Studio).

## O que falta conferir (na conta do Mizuki)

1. Qual plano exato é o "Gemini/Google One": se for **Google AI Pro** (antigo AI Premium), o crédito vale; um plano Google One só de armazenamento não dá crédito.
2. Se o benefício aparece ativável em developers.google.com/program/my-benefits.
3. Depois de ligado, se a cobrança da Vertex está mesmo sendo abatida do crédito (tela de faturamento do Google Cloud, primeiro mês).

Se o crédito não funcionar, o plano B é o mesmo do relatório anterior: chave paga normal, US$ 1 a 17/mês estimados.

## Quanto os US$ 10 aguentam em cada Gemini (adendo, 12/10/2026)

Preços da [página oficial](https://ai.google.dev/gemini-api/docs/pricing) lidos hoje. A premissa por resposta é a mesma do relatório anterior: 8.000 tokens de entrada (6.000 fixos e 2.000 de histórico) e 150 de saída. "Com cache" supõe o bloco fixo sempre lido do cache, sem contar o armazenamento do cache. Os tokens de raciocínio são cobrados como saída e não estão na conta; no Pro eles podem dobrar o custo. São estimativas, não medições.

| Modelo | US$ por resposta | Respostas/mês com US$ 10 (sem cache / com cache) | Por dia |
|---|---|---|---|
| Gemini 3.1 Pro | ~0,018 | ~560 / ~1.400 | ~19 / ~48 |
| Gemini 3.8 Flash (preço até 31/12/2026; dobra em 2027) | ~0,0066 | ~1.500 / ~4.000 | ~50 / ~130 |
| Gemini 3 Flash Preview | ~0,0045 | ~2.200 | ~75 |
| Gemini 3.1 Flash-Lite | ~0,0022 | ~4.500 / ~11.400 | ~150 / ~380 |

## Ranking de roleplay em outras línguas

Existem rankings, mas só em inglês e com resultados que não batem entre si. O EQ-Bench 4 é roleplay de 16 turnos com IAs como juízes ([eqbench.com](https://eqbench.com/)). No RP-Bench, os juízes de IA colocam o Claude Opus/Sonnet no topo, mas no voto cego de pessoas aparecem DeepSeek V4 Pro, Claude Opus 4.6, Gemini 3.1 Flash-Lite e GPT-4.1 praticamente empatados. O próprio projeto admite que os juízes de IA discordam das pessoas em metade dos casos ([RP-Bench](https://github.com/LeviTheWeasel/rp-benchmark)). Nenhum deles testa português.

## Recomendação que vamos usar

Decidido com o Mizuki em 12/10/2026.

1. **Principal: Gemini 3.8 Flash pela Vertex AI**, pago com o crédito de US$ 10/mês do Google AI Pro. Pela estimativa acima, ele aguenta de 50 a 130 respostas/dia, e o servidor com o funil deve ficar abaixo disso.
2. **Reserva: Gemini 3.1 Flash-Lite.** O bot troca pra ele sozinho quando o contador do mês chegar perto dos US$ 10, ou se o Flash falhar. Se os dois falharem, ele reage com emoji ou fica em silêncio.
3. **Teste cego antes de soltar no servidor.** Com o card e a bateria de testes prontos, rodar a mesma bateria no Gemini 3.8 Flash, no Gemini 3.1 Pro, no Claude (Haiku e Sonnet) e num GPT, com uns US$ 5 de crédito de API na Anthropic e na OpenAI. Se Claude ou GPT ganharem com clareza, viram o principal e a Gemini fica de reserva.
4. **A chamada à IA fica numa camada só**, em que trocar de provedor ou modelo é mudar uma configuração.
5. **Rever em dezembro de 2026:** o preço do 3.8 Flash dobra em 01/01/2027, o que corta pela metade o que os US$ 10 aguentam. Até lá o log de chamadas vai mostrar o volume real.

Antes de tudo: ativar o crédito em developers.google.com/program/my-benefits e conferir na primeira fatura do Google Cloud que a Vertex está sendo abatida dele.

## Conferência nas fontes (adendo, 12/10/2026 à noite)

Relido hoje, antes de configurar a conta:

- **O crédito existe e é ativado à mão.** O [FAQ do Developer Program](https://developers.google.com/profile/help/benefits) diz que o AI Pro dá US$ 10 por mês em crédito Google Cloud, ativado na página My Benefits escolhendo uma conta de faturamento do Cloud. Vale pra conta pessoal `@gmail.com`. O crédito expira um ano depois de concedido. O FAQ cita Vertex AI entre os produtos e não cita a Gemini API do AI Studio.
- **AI Studio é pré-pago desde 23/03/2026.** A [página de cobrança da Gemini API](https://ai.google.dev/gemini-api/docs/billing) diz que crédito Cloud elegível só é aplicado depois de uma compra de crédito pré-pago (mínimo US$ 5), e não diz se o crédito do Developer Program é elegível.
- **A resposta do suporte continua sendo a de 29/06/2026**, no [fórum](https://discuss.ai.google.dev/t/using-ai-pro-plan-benefit-google-ai-studio-api-credits/170841): o crédito não vai pra conta pré-paga; usar a Gemini pela Vertex AI. **Ninguém no tópico confirmou que a Vertex abateu do crédito.** Só a primeira fatura do Mizuki confirma.
- **A Vertex é pós-paga e não tem teto de gasto.** Alerta de orçamento do Cloud avisa, não bloqueia. O teto real tem que ser o contador do próprio bot.

## Crédito do Google AI Pro: como foi ativado (12 e 13/10/2026)

**Estado: ativado.** O crédito mensal de US$ 10 (R$ 59,31 em outubro/26) está aplicado numa conta de faturamento paga do Google Cloud, com "Sempre usar esta conta" marcado, e vale até 12/10/2027. O registro completo, com identificadores de conta e valores, fica fora do git, em `pesquisa/privado/`.

O que travou e o que resolveu, pra não repetir:

1. **A primeira conta de faturamento fechou sozinha** cerca de 20 minutos depois do pré-pagamento de ativação. Causa, dada por um atendente do Cloud Billing: ela nasceu como "conta de teste gratuito", e o teste gratuito desse usuário já tinha expirado. Conta assim não reabre. O pré-pagamento foi pedido de volta pela Central de Pagamentos (Assinaturas e serviços > a conta do Cloud > "Solicitar um reembolso"); prazo de 7 a 10 dias úteis.
2. **Os alertas do perfil de pagamentos não eram a causa.** A IA do suporte apontou um alerta de "pagamento pendente" de uma conta antiga; o atendente humano desmentiu, e esse alerta não afeta conta nova.
3. **O perfil de pagamentos pessoal travava a criação de outra conta** com "CPF e data de nascimento são obrigatórios", sem deixar editar, mesmo com o CPF verificado. Saída, que a [documentação](https://docs.cloud.google.com/billing/docs/how-to/create-billing-account?hl=pt-br) permite: criar um perfil de pagamentos novo dentro do fluxo de criação ("Adicionar nome e endereço"). Com ele a conta saiu como **"Conta paga"** e ficou ativa.
4. **Caminho certo de criação:** `console.cloud.google.com/billing` > Criar conta. A janela com o texto "Mais da API Gemini" é o fluxo pré-pago do AI Studio, onde o crédito não vale direto.
5. **O pré-pagamento é uma pré-autorização**: retenção temporária pra validar o cartão, que o banco costuma liberar em cerca de uma semana.
6. Depois de ativa, a conta aparece no cartão do benefício em developers.google.com (Benefícios) e o crédito é aplicado com um clique.

### O que ficou pronto no Google Cloud

- Alerta de orçamento de R$ 50 por mês na conta de faturamento (só avisa por e-mail; a Vertex é pós-paga e não tem teto).
- Projeto "Rhodes Bot", vinculado à conta paga. O projeto do AI Studio, onde mora a chave gratuita do `.env`, ficou de fora de propósito, pra não sair do nível gratuito.
- **Agent Platform API** (`aiplatform.googleapis.com`) ativada: é a Vertex AI com o nome novo. Só essa; a janela "Ativar APIs" da plataforma ligaria umas vinte.
- Não feito, de propósito: a credencial (conta de serviço), que entra na fase 1, salva na pasta e fora do chat.

### AI Studio depois do crédito (lido em 13/10/2026 na [página de faturamento da Gemini API](https://ai.google.dev/gemini-api/docs/billing?hl=pt-br))

"Configurar faturamento" no AI Studio **não foi feito e não é necessário pro plano da Vertex**. O que a página diz:

- Ao configurar, o AI Studio pode exigir pré-pagamento mínimo de US$ 5, deixar escolher entre pré-pago e pós-pago, ou atribuir pós-pago. Só dá pra saber clicando.
- No pré-pago, o crédito do Cloud só começa a ser consumido depois de uma compra de créditos pré-pagos, e para quando o saldo pré-pago zera. Crédito pré-pago não é reembolsável e expira em 12 meses.
- Adicionar pré-pagamento a uma conta pós-paga **modifica a conta do Cloud Billing**; cancelar no meio deixa a conta sem funcionar, e só o suporte desfaz. Não existe mudança de pré-pago pra pós-pago.
- Então: só seguir no AI Studio se a tela oferecer **pós-pago**. Senão, ficar na Vertex AI.

### Pendências

- Conferir na primeira fatura que o uso da Vertex abate do crédito: ninguém confirmou isso ainda.
- Reembolso do pré-pagamento da conta encerrada.

### Vertex funcionando (13/10/2026, 16h55)

- **Credencial:** chave de API do Google Cloud, no `.env` da pasta (`VERTEX_API_KEY`). A organização nova bloqueia esse tipo de chave por padrão (restrição `iam.managed.disableServiceAccountApiKeyCreation`, [documentação](https://docs.cloud.google.com/docs/authentication/api-keys?hl=pt-br)); o Mizuki deu a si mesmo o papel de Administrador da política da organização e soltou a restrição **só no projeto do bot**. Nos outros projetos ela continua valendo.
- **Primeiro teste real:** 17 respostas pelo Gemini 3.8 Flash, com os cards do site (Closure v0.30, Kal'tsit v0.23), em `pesquisa/validacao/2026-10-13-16h55-modelo-gemini-3.8-flash.md`. Regra e voz certas nas duas.
- **Custo medido:** US$ 0,096 por 17 respostas, cerca de US$ 0,0056 cada, perto da estimativa de US$ 0,0066. Com o teto de US$ 9, dá umas 1.600 respostas por mês pela Vertex, fora as gratuitas.
- **Quase metade do custo é raciocínio:** cada resposta de uma ou duas frases gastou de 400 a 1.450 tokens de saída, porque o modelo pensa antes de falar e isso é cobrado como saída. Também é o que deixa a resposta em 5 a 13 segundos. Vale testar com o raciocínio reduzido.
- **Uma falha em 17:** um pedido voltou 429 ("Resource exhausted"), que na Vertex pós-paga é fila cheia do lado do Google, não cota nossa. A fila de reserva do bot cobre isso.
- **Achado pro card:** perguntada "tá chovendo aí?", a Closure respondeu "o céu tá limpo por aqui", como se estivesse em Tóquio. Falta a regra do clima no card dela (a Kal'tsit respondeu sem se colocar no lugar).
