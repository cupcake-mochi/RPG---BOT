# Peneira de API grátis pro site de teste

13/10/2026. Pergunta do Mizuki: tem alguma API gratuita boa pro bot fora Gemini, Claude e GPT, pros amigos testarem mais?

## Tamanho do prompt

Medido com o prompt real que a página monta (card v0.20 / v0.14, lorebook e livro): **2,9 a 4,4 mil tokens** na primeira mensagem, crescendo com o histórico (até 24 falas). Contado pelo `usageMetadata` do Gemini.

## Peneira

| Opção | Limite grátis (fonte) | Resultado |
|---|---|---|
| Gemini 3.8 / 3.7 / 3.6 / 3.5 Flash e 3 Flash Preview (chave grátis atual) | 20 pedidos por dia **cada modelo** (erro 429 `GenerateRequestsPerDayPerProjectPerModel-FreeTier = 20`, medido) | Bons, mas 3.7 e 3 Preview deram 503 "alta demanda" e levaram 20 a 120 s. Servem de primeira tentativa do botão Padrão. |
| Gemini 3.1 Flash-Lite | cota própria, número não aparece na doc (fica em aistudio.google.com/rate-limit) | 1,7 a 2,8 s, respostas certas nas perguntas de regra e no tom. **Escolhido como base.** |
| Gemini 3.5 Flash-Lite | cota própria | 1 s quando respondeu; depois 503. Reserva. |
| Gemini 2.5 Flash-Lite | cota própria | 0,7 a 11 s; respostas mais secas. Última reserva. |
| Gemma 4 31B (mesma chave) | cota própria | Erro 500 em 2 de 3 e 36 s na que respondeu. Descartado. |
| Gemini Pro (3.1 preview) | cota grátis 0 (429, medido) | Descartado. |
| Cerebras | **Não tem mais plano grátis**: virou crédito único de US$ 5 que vence em 30 dias (desde 21/07/2026; unificado em 05/10/2026). Só gpt-oss-120b e Qwen 3.8 27B. [doc](https://inference-docs.cerebras.ai/support/rate-limits), [histórico](https://www.usagepricing.com/blueprint/activity/cerebras-2026-10-05-qwen-3-8-developer-tier-merge) | Descartado (corrige o que eu disse antes na thread). |
| Mistral (plano Experiment) | grátis, sem cartão, **exige telefone** e as conversas **podem ser usadas pra treino**; limites por conta, não publicados. Tem Mistral Medium 3.5 e Large 4. [ajuda](https://help.mistral.ai/en/articles/455206-how-can-i-try-the-api-for-free-with-the-experiment-plan) | **Única externa que passa.** Não testada (precisa da chave). |
| Groq | gpt-oss-120b / Qwen 3.8 27B: 8 mil tokens/min e 200 mil/dia [doc](https://console.groq.com/docs/rate-limits) | ~2 mensagens por minuto e ~50 por dia com esse prompt. Fica como opção, fora da fila padrão. |
| OpenRouter `:free` | 50 por dia (1.000 com US$ 10 comprados) [doc](https://openrouter.ai/docs/api-reference/limits) | Pouco. Opção, fora da fila. |

## O que entrou no site

Fila por botão: se um modelo esgota, cai ou demora mais de 60 s, o próximo responde, e a conversa salva diz qual modelo deu cada fala.

- Rápido: 3.1 Flash-Lite → 3.5 Flash-Lite → 2.5 Flash-Lite → Mistral Medium (se houver chave)
- Padrão: 3.8 Flash → 3.5 Flash → 3 Flash Preview → Mistral Medium → fila do Rápido

Atenção: a chave do Gemini é a mesma do pente fino da personalidade; os dois gastam a mesma cota por modelo.
