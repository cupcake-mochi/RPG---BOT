# Validação da pesquisa 1: "Bot de personagem, modelo ou API"

> 12/10/2026. Reconferi na fonte primária as afirmações que decidem algo no relatório. Legenda: ✅ confere · 🔼 estava "não confirmado" e agora confirma · ✏️ corrigir · ⚠️ continua aberto.

| # | Afirmação no relatório | Resultado | Fonte reconferida |
|---|---|---|---|
| 1 | Gemini 2.5 Flash-Lite custa US$ 0,10 entrada / US$ 0,40 saída por MTok | ✅ (cache US$ 0,01) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| 2 | Gemini 2.5 Flash (modelo do bot antigo) entra na conta com preço próprio | ✅ US$ 0,30 / US$ 2,50 (saída inclui tokens de raciocínio) | idem |
| 3 | Gemini 3.6/3.8 Flash dobram de preço em 2027 | ✅ US$ 0,75/3,75 até 31/12/2026, US$ 1,50/7,50 a partir de 01/01/2027 | idem |
| 4 | Gemini 3.1 Flash-Lite | ✅ US$ 0,25 / US$ 1,50, sem aumento anunciado | idem |
| 5 | Claude Haiku 5.5 a US$ 0,10 / US$ 0,50; Sonnet 5.5 a US$ 2 / US$ 10 | ✅ (Haiku vale até 100 mil tokens de prompt; acima disso US$ 0,50 / US$ 2,50) | [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| 6 | Tokenizador novo gera ~30% mais tokens | ✅ vale para "Claude 4.7 and later models", o que inclui os 5.5 | idem |
| 7 | Limites da Gemini são por projeto, não por chave; cota diária zera à meia-noite do Pacífico | ✅ | [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) |
| 8 | Free tier por modelo não é publicado, só no AI Studio | ✅ | idem |
| 9 | Tier 1 = vincular faturamento, costuma valer na hora; teto US$ 250 e US$ 10 por 10 min | ✅ | idem |
| 10 | No gratuito o Google usa o conteúdo e humanos podem ler; no pago, não | ✅ "human reviewers may read, annotate, and process your API input and output" (gratuito); pago "doesn't use your prompts" | [Gemini API terms](https://ai.google.dev/gemini-api/terms) |
| 11 | Termos da Gemini vetam cliente provavelmente acessado por menores de 18 | ✅ "likely to be accessed by individuals under the age of 18" | idem |
| 12 | Consumer Terms da Anthropic proíbem acesso por bot/script fora de chave de API | ✅ seção 3, item 7, vigente desde 08/10/2025 | [Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms) |
| 13 | Claude Max tem crédito de API (US$ 100 no 5x, US$ 200 no 20x); Free, Pro e Enterprise não | 🔼 confirmado. **O Claude Pro do Mizuki não tem crédito de API.** Crédito expira a cada ciclo, sem acumular | [Claude API credits](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers) |
| 14 | Google AI Pro traz US$ 10/mês de crédito de GenAI/Cloud | 🔼 confirmado, e ✏️ a fonte citada estava errada. A página citada (Developer Program) não fala do AI Pro; quem confirma é o blog oficial do Google de 27/01/2026: AI Pro "$10 per month in Google Cloud credits", Ultra US$ 100, utilizáveis na Gemini API. **Ressalva:** o blog diz "via AI Studio ou Vertex AI", mas o AI Studio passou a ser pré-pago, e uma resposta do suporte do Google Cloud de 29/06/2026 (repassada por um usuário no fórum, não é documentação oficial) diz que o crédito "cannot be transferred to the PrePay Payments Account or used to fund prepaid credits in Google AI Studio" e recomenda a Gemini API pela **Vertex AI**. Na prática, conte com o crédito só pela Vertex | [blog.google](https://blog.google/innovation-and-ai/technology/developers-tools/gdp-premium-ai-pro-ultra/) · [fórum Google](https://discuss.google.dev/t/end-of-google-cloud-developer-program-premium/324980) · [fórum AI, jun/2026](https://discuss.ai.google.dev/t/using-ai-pro-plan-benefit-google-ai-studio-api-credits/170841) |
| 15 | ChatGPT Plus/Pro não inclui API | 🔼 confirmado: "API usage is billed separately from your ChatGPT subscription". Nenhuma menção a crédito no Pro | [OpenAI Help](https://help.openai.com/en/articles/8156019-is-api-usage-included-in-chatgpt-plus) |
| 16 | OpenAI fechou fine-tuning para quem nunca usou desde 07/05/2026; novos jobs acabam em 06/01/2027 | ✅ e há uma data intermediária: 02/07/2026 fechou também para quem não rodou inferência de modelo afinado | [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations) |
| 17 | KuaiRP: LoRA "extremely insensitive to the injection of world knowledge"; Qwen3-8B cai de 24,83 para 12,53 em ferramentas | ✅ seção 3.2 e Tabela 5 (BFCL v4, "Overall Acc"). O resumo da página não traz isso; está no texto completo | [KuaiRP HTML](https://arxiv.org/html/2609.11127) |
| 18 | Unsloth: mínimo de 100 linhas, ideal mais de 1.000 | ✅ | [Unsloth datasets guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/datasets-guide) |
| 19 | "Não há texto oficial da Closure em pt-BR nem tradução de fã" | ✅ reforçado pelas pesquisas 2 e 3 | dados do jogo |
| 20 | Hipótese: File/Dialogue da wiki em chinês porque a Closure não saiu no global | 🔼 confirmado: global "TBA", operadora lançada só no CN em 30/04/2026 | [wiki.gg, lançamentos](https://arknights.wiki.gg/wiki/Operator/List/Release) |

## Conflito interno entre pesquisas

- Pesquisa 1, passo 3: escrever os exemplos **já em pt-BR**, porque exemplo em inglês + "responda em português" tende a sair português traduzido.
- Pesquisa 2, frente 3: deixar as falas **buscadas por similaridade em inglês** no prompt.
- As duas são inferência; nenhuma tem fonte. Resolução: os exemplos fixos do card ficam em pt-BR (sem mudança). Para as falas buscadas, a escolha inglês vs. pt-BR fica **em aberto e vai para o teste cego**. Ajustei a nota da pesquisa 2 para dizer isso.

## O que não reconferi

- Preços e limites de terceiros (OpenRouter, Groq, Cerebras, ArliAI, Featherless, RunPod, Vast), números da RX 580 e planos da Discloud. Não decidem a recomendação; o relatório já trata como estimativa.
- Números dos artigos de chat em grupo (Time to Talk) e do Character-LLM/RoleLLM.

## Veredito

A recomendação central se mantém. Duas mudanças de peso para a decisão de plano: **Claude Pro não dá crédito de API** e **Google AI Pro dá US$ 10/mês utilizáveis na Gemini API pela Vertex AI (não pelo AI Studio pré-pago)**, o que, pelas estimativas do relatório, cobre um bot no Gemini 2.5 Flash-Lite com folga.
