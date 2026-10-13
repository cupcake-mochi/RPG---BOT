# Custos, limites e regras de acesso de APIs de LLM para um bot de personagem no Discord (estado em 12/10/2026)

> Notas de método (valem para o documento inteiro):
> - Data da coleta: 12/10/2026. Toda cifra abaixo traz a data da fonte quando a fonte a informa.
> - Câmbio usado nas conversões: US$ 1 = R$ 4,99 (compra 4,9863 / venda 4,9876, cotação de 12/10/2026 11:27) — [AwesomeAPI USD-BRL](https://economia.awesomeapi.com.br/json/last/USD-BRL). Valores em BRL não incluem IOF nem spread do cartão.
> - "MTok" = 1 milhão de tokens. Preços em USD por MTok, salvo indicação.
> - Três páginas primárias não puderam ser abertas diretamente (code.claude.com "Legal and compliance", help.openai.com artigo 8156019, e o painel aistudio.google.com/rate-limit, que exige login). Onde isso acontece, o item está marcado como "via resumo de busca" ou "fonte secundária".

## 1. Assinaturas de consumidor (Claude Pro/Max, Google AI Pro/Ultra, ChatGPT Plus/Pro) incluem acesso ou crédito de API utilizável por um bot de Discord?

### Takeaway
Em outubro de 2026 a resposta mudou em relação a 2025: Claude Max (não o Pro) e Google AI Pro/Ultra passaram a incluir crédito mensal de API (US$ 100–200 no Max; US$ 10 no Google AI Pro; US$ 40–100 no Ultra), enquanto o ChatGPT Plus/Pro continua sem API incluída. Nenhuma assinatura entrega uma "chave de API ilimitada": o que existe é crédito pré-pago em conta de desenvolvedor separada, cobrado a preço normal de API.

### Cited Findings

**Anthropic**
- Planos Claude Max e Team incluem crédito mensal para a Claude API: US$ 100 (Max 5x), US$ 200 (Max 20x), US$ 20 por assento Standard e US$ 100 por assento Premium no Team (pool limitado a US$ 500). "Free, Pro, and Enterprise plans aren't eligible." — [Claude Platform docs, "API credits for Max and Team plans"](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
- O crédito cobre Claude API, Claude Managed Agents, Claude Agent SDK e playground; não cobre Claude Code nem "extra usage" nos apps. — [Claude Platform docs](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
- Para resgatar: vincular uma organização do Claude Console ao plano em Settings > Billing no claude.ai; não é preciso cadastrar meio de pagamento na Claude Platform. Assinante novo só pode resgatar após 7 dias no plano elegível. — [Claude Platform docs](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
- O crédito expira ao fim de cada ciclo de cobrança, sem acúmulo. Quando acaba e não há outro saldo, "API requests stop until your next monthly API credits arrive. Usage is never charged to your Claude plan." — [Claude Platform docs](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
- Organizações vinculadas a plano elegível sobem para, no mínimo, o tier "Start" de rate limit (e "Build" se o crédito mensal passar de US$ 200). — [Claude Platform docs](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
- O anúncio dos créditos para Max e Team é datado de 07/10/2026. — [Claude Help Center, artigo 15036540](https://support.claude.com/articles/15036540); [Claude Help Center, artigo 17154008 (via resumo de busca)](https://support.claude.com/en/articles/17154008)
- Histórico do "Agent SDK credit": em maio de 2026 a Anthropic anunciou um crédito mensal separado para Agent SDK / `claude -p` / apps de terceiros (US$ 20 no Pro, US$ 100 no Max 5x, US$ 200 no Max 20x), previsto para 15/06/2026. — [GIGAZINE, 14/05/2026](https://www.gigazine.net/gsc_news/en/20260514-anthropic-claude-agent-sdk-credits); [aiweekly.co](https://aiweekly.co/alerts/anthropic-caps-claude-agent-sdk-credits-by-plan-tier)
- Segundo a leitura da página do Help Center feita em 12/10/2026, a nota de 15/06/2026 descreve uma pausa nessa mudança, e a nota mais recente (07/10/2026) diz que Max e Team "now include monthly API credits"; Agent SDK, `claude -p` e apps de terceiros "can also still be used against subscription limits". — [Claude Help Center, artigo 15036540](https://support.claude.com/articles/15036540); um resumo de busca do mesmo artigo descreveu o crédito de 15/06 como vigente, o que contradiz a leitura direta — [resultado de busca para o artigo 15036540](https://support.claude.com/en/articles/15036540)
- Novos usuários da API recebem "a small amount of free credits to test the API"; não há free tier permanente. — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Google**
- Google AI Pro (US$ 19,99/mês) inclui "$10 GenAI and Cloud monthly credit"; a tabela comparativa lista US$ 40 por usuário/mês no Google AI Ultra (20 TB) e US$ 100 por usuário/mês no Google AI Ultra (30 TB). — [Google Developer Program, plans and pricing](https://developers.google.com/program/plans-and-pricing)
- Os benefícios do antigo Google Developer Program Premium foram incorporados às assinaturas Google AI Pro/Ultra a partir de 27/01/2026. — [agentdeals.dev (fonte secundária)](https://agentdeals.dev/google-developer-program-2026)
- A assinatura não inclui uma chave de API; o crédito precisa ser aplicado manualmente a uma conta de faturamento do Google Cloud para valer na Gemini API, e uma chave de API "direta" continua cobrada normalmente. — [developersdigest.tech (fonte secundária)](https://www.developersdigest.tech/blog/google-ai-pro-vs-gemini-api-for-developers-2026); [smartscope.blog (fonte secundária)](https://smartscope.blog/en/blog/gemini-api-pro-ultra-monthly-credits-2026/)
- A Gemini API tem free tier próprio, independente de assinatura; no free tier o conteúdo enviado é usado para melhorar produtos do Google, no pago não. — [Gemini API pricing, atualizado em 09/10/2026](https://ai.google.dev/gemini-api/docs/pricing)
- Passar do free tier para o Tier 1 exige apenas vincular uma conta de faturamento ativa ao projeto; a mudança costuma ser instantânea. — [Gemini API rate limits, atualizado em 09/10/2026](https://ai.google.dev/gemini-api/docs/rate-limits)

**OpenAI**
- O artigo oficial "Is API usage included in ChatGPT Plus?" e o de cobrança afirmam que ChatGPT e a plataforma de API têm sistemas de cobrança separados e que o uso de API é cobrado à parte da assinatura. — [OpenAI Help Center, artigo 8156019 (via resumo de busca; a página devolveu HTTP 403 na leitura direta)](https://help.openai.com/en/articles/8156019-is-api-usage-included-in-chatgpt-plus)
- A página "What is ChatGPT Plus?" lista o plano a US$ 20/mês e marca o uso de API como separado. — [OpenAI Help Center, artigo 6950777 (via resumo de busca)](https://help.openai.com/en/articles/6950777)

### Inferences
- Com o câmbio de R$ 4,99, o crédito do Google AI Pro vale cerca de R$ 50/mês e o do Claude Max 5x cerca de R$ 499/mês em API. Cruzando com a estimativa da seção 5, US$ 10/mês cobre um bot de 1.000 mensagens/dia em Flash-Lite com cache, e US$ 100/mês cobre com folga 5.000 mensagens/dia em Claude Haiku 5.5.
- O que decide o caso da Anthropic é qual plano o usuário assina: se for Claude Pro, não há crédito de API (pela documentação de 10/2026); se for Max, há US$ 100–200/mês que tornam o bot praticamente "grátis" dentro do que já é pago.
- Crédito de API usado com chave do Console é uso de API normal (ver seção 2), ou seja, é o caminho permitido para um bot que atende outras pessoas, ao contrário de usar o login da assinatura.

### Gaps
- Não li os "program terms" do crédito (anthropic.com/legal/credit-terms); não sei se há restrição específica de uso além dos termos comerciais.
- Status exato do "Agent SDK credit" de 15/06/2026 (pausado, revisto ou substituído pelo crédito de API de 07/10/2026): as duas leituras do mesmo artigo do Help Center divergem. Conferir o artigo 15036540 antes de afirmar.
- Não confirmei em página oficial do Google a validade do crédito (uma fonte secundária fala em 1 ano) nem o passo a passo para aplicá-lo à Gemini API.
- Não encontrei confirmação oficial sobre ChatGPT Pro (US$ 200) incluir qualquer crédito de API; a evidência achada cobre o Plus. Um resumo de busca menciona que ferramentas de terceiros conectadas podem usar a franquia do Plus com aprovação do usuário, mas não consegui abrir a página para verificar o alcance disso.

## 2. O que os termos dizem sobre usar a assinatura de consumidor (ou token OAuth, ou cliente web não oficial) para alimentar um bot automatizado que atende terceiros? Quais os riscos documentados?

### Takeaway
Os três provedores proíbem ou restringem esse uso: a Anthropic veda acesso automatizado fora de chave de API e veda disponibilizar a conta a terceiros; o Google suspendeu contas pagas em fevereiro de 2026 por uso de OAuth em cliente de terceiro; os termos da OpenAI proíbem extração automatizada. O caminho permitido é sempre a API com chave própria.

### Cited Findings

**Anthropic**
- Consumer Terms, seção 3, proíbe: "Except when you are accessing our Services via an Anthropic API Key or where we otherwise explicitly permit it, to access the Services through automated or non-human means, whether through a bot, script, or otherwise." — [Anthropic Consumer Terms, vigência 08/10/2025](https://www.anthropic.com/legal/consumer-terms)
- Seção 2: "You may not share your Account login information, Anthropic API key, or Account credentials with anyone else. You also may not make your Account available to anyone else." — [Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms)
- Seção 12: a Anthropic pode suspender ou encerrar o acesso "at any time without notice"; se o encerramento for por violação dos termos, não há reembolso da assinatura. — [Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms)
- O uso de chave de API é regido pelos Commercial Terms, não pelos Consumer Terms. — [Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms)
- Em 19/02/2026 a Anthropic atualizou a página "Legal and compliance" do Claude Code: tokens OAuth dos planos Free, Pro e Max são para uso exclusivo no Claude Code e no Claude.ai; a empresa "does not permit third parties to provide Claude.ai logins or use Free, Pro, or Max plan credentials" para rotear requisições em nome de usuários. — [GIGAZINE, 20/02/2026 (fonte secundária; a página primária code.claude.com não pôde ser aberta)](https://gigazine.net/gsc_news/en/20260220-anthropic-third-party-block); [WinBuzzer, 19/02/2026](https://winbuzzer.com/2026/02/19/anthropic-bans-claude-subscription-oauth-in-third-party-apps-xcxwbn/)
- Thariq Shihipar (Anthropic), em 18/02/2026: "If you're building a business on top of the Agent SDK, you should use an API key instead." A matéria relata bloqueios técnicos contra ferramentas de terceiros que se passavam pelo cliente oficial desde janeiro de 2026 e fluxos de trabalho interrompidos, mas não relata banimentos de conta pela Anthropic. — [GIGAZINE, 20/02/2026](https://gigazine.net/gsc_news/en/20260220-anthropic-third-party-block)
- O crédito mensal do plano é dimensionado para experimentação e automação individual; times com automação compartilhada em produção devem usar a Claude Platform com chave de API. — [Claude Help Center, artigo 15036540 (via resumo de busca)](https://support.claude.com/articles/15036540)

**Google**
- Em fevereiro de 2026 o Google restringiu/suspendeu contas Google AI Ultra e Antigravity que acessavam modelos Gemini pelo OAuth do OpenClaw; assinantes de US$ 249,99/mês perderam acesso sem aviso. — [OECD AI Incidents, 23/02/2026](https://oecd.ai/en/incidents/2026-02-23-ce89); [Google AI Developers Forum, tópico 122778](https://discuss.ai.google.dev/t/account-restricted-without-warning-google-ai-ultra-oauth-via-openclaw/122778)
- O suporte do Google, citado no fórum, disse que a suspensão afeta o Gemini CLI e qualquer serviço que use a "Cloud Code Private API"; um usuário relatou que após 3 semanas de espera a conta não foi restaurada. — [Google AI Developers Forum, tópico 122778](https://discuss.ai.google.dev/t/account-restricted-without-warning-google-ai-ultra-oauth-via-openclaw/122778)
- Há relatos de que alguns afetados perderam também Gmail/Workspace; essa extensão vem de cobertura secundária. — [OECD AI Incidents](https://oecd.ai/en/incidents/2026-02-23-ce89); [GIGAZINE, 24/02/2026](https://gigazine.net/gsc_news/en/20260224-google-gemini-openclaw-accounts-banned)
- Termos adicionais da Gemini API (vigência 23/03/2026): é proibido "attempt to reverse engineer, extract or replicate any component of the Services"; é preciso ter 18 anos ou mais, e não se pode usar os serviços em cliente "directed towards or is likely to be accessed by individuals under the age of 18". — [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms)
- Nos "Unpaid Services" (free tier), o Google usa o conteúdo enviado e as respostas para melhorar produtos, e revisores humanos podem ler; "Do not submit sensitive, confidential, or personal information to the Unpaid Services." Nos "Paid Services" os prompts não são usados para melhorar produtos. — [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms)

**OpenAI**
- Os Terms of Use de consumidor listam entre os usos proibidos engenharia reversa e extração automatizada ou programática de dados ou saídas; violações podem levar a suspensão ou encerramento da conta. — [OpenAI Terms of Use (ROW)](https://openai.com/en-GB/policies/row-terms-of-use/); análise do dispositivo em [ConductAtlas (fonte secundária)](https://conductatlas.com/platform/openai/terms-of-use-row/provision/CA-P-017130/prohibition-on-automated-data-or-output-extraction/)
- Os Business Terms regem o uso das APIs e serviços para desenvolvedores. — [OpenAI Terms of Use](https://www.openai.com/terms)

### Inferences
- Um bot de Discord que responde a dezenas de pessoas usando o login/cookie/token OAuth de uma assinatura de consumidor viola pelo menos duas cláusulas da Anthropic (acesso automatizado sem chave de API e disponibilizar a conta a terceiros) e a cláusula de extração automatizada da OpenAI. Clientes web reverse-engineered caem no mesmo enquadramento.
- O risco mais grave documentado é o do Google, porque a conta de consumidor é a mesma do Gmail/Drive; perder a conta por causa de um bot de hobby tem custo desproporcional.
- A cláusula de idade da Gemini API (cliente "provável de ser acessado por menores de 18") é um ponto de atenção para um servidor de Discord de comunidade de jogo, onde é plausível haver menores. Isso vale para o uso da API com chave, não só para a assinatura.
- No free tier da Gemini API, as mensagens dos membros do servidor são usadas para treino/melhoria e podem ser lidas por revisores; no tier pago não. Para um bot que processa conversa de terceiros, isso pesa a favor do tier pago.

### Gaps
- Não consegui abrir a página primária "Legal and compliance" do Claude Code (code.claude.com bloqueado pela ferramenta); as citações de 19/02/2026 vêm de imprensa.
- Não encontrei relatos confiáveis e datados de 2026 de banimento de conta da Anthropic ou da OpenAI especificamente por bot de Discord rodando em assinatura; os casos documentados são do Google (OpenClaw).
- Não pesquisei as políticas de uso (usage policies) de cada provedor sobre conteúdo de roleplay em si (conteúdo adulto, personagens de terceiros etc.).
- Não li os termos atuais de "Sign in with ChatGPT"/Codex; há discussão em fórum de que usos programáticos documentados seriam permitidos, mas é leitura de um usuário, não posição oficial — [OpenAI Developer Community](https://community.openai.com/t/building-a-browser-to-codex-bridge-via-codex-mcp-server-tou-clarification-needed/1375345).

## 3. Limites atuais do free tier da Gemini API (RPM, TPM, RPD) por modelo, como mudaram entre 2025 e 2026, limites e preços do Tier 1, e por que um bot pequeno estoura o free tier

### Takeaway
O Google deixou de publicar tabela fixa de limites; o que está documentado é que o free tier encolheu muito desde dezembro de 2025. Em setembro de 2026 o AI Studio mostrava cerca de 20 requisições/dia para os modelos Flash e 500/dia para os Flash-Lite, o que é incompatível com um bot que responde 200+ mensagens por dia. O Tier 1 (basta vincular faturamento) remove o gargalo diário, mas seus números exatos só aparecem no painel da própria conta.

### Cited Findings

**O que a documentação oficial diz (09/10/2026)**
- Os limites são medidos em RPM, TPM (tokens de entrada por minuto) e RPD; estourar qualquer um gera erro de rate limit. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- "Rate limits are applied per project, not per API key." A cota de RPD zera à meia-noite do horário do Pacífico. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- A página não lista mais valores de RPM/TPM/RPD por modelo; remete ao painel aistudio.google.com/rate-limit e avisa que os limites não são garantidos e a capacidade real pode variar. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- Qualificação dos tiers: Free = projeto ativo; Tier 1 = conta de faturamento vinculada (teto de cobrança US$ 250); Tier 2 = US$ 100 de gasto acumulado + 3 dias desde o primeiro pagamento (teto US$ 2.000); Tier 3 = US$ 1.000 + 30 dias. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- Há também limite de gasto em janela móvel de 10 minutos: US$ 10 no Tier 1, US$ 50 no Tier 2, US$ 200 no Tier 3; estourar devolve `429 RESOURCE_EXHAUSTED`. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- Modelos com free tier em 09/10/2026: Gemini 3.8 Flash, 3.6 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3 Flash Preview, 2.5 Pro, 2.5 Flash, 2.5 Flash-Lite. Gemini 3.1 Pro Preview não tem free tier. O gemini-1.5-flash-8b não aparece mais na página de preços. — [Gemini API pricing, 09/10/2026](https://ai.google.dev/gemini-api/docs/pricing)

**Números reportados (fontes secundárias, conflitantes)**
- Setembro de 2026, segundo o que "o AI Studio reporta": 20 RPD para Gemini 3.8/3.7/3.6/3.5 Flash; 500 RPD para Gemini 3.5 Flash-Lite e 3.1 Flash-Lite; RPM e TPM não informados. — [scriptbyai.com](https://www.scriptbyai.com/gemini-api-free-tier-limits/)
- Outra tabela de 2026 dá ao Gemini 3.1 Flash-Lite 15 RPM, 250.000 TPM e 1.000 RPD, contradizendo os 500 RPD acima. — [aipromptshub.co (via resumo de busca)](https://aipromptshub.co/blog/gemini-api-free-tier-rate-limits)
- Um retrato anterior da própria documentação do Google listava: Gemini 2.5 Pro 5 RPM / 125.000 TPM / 100 RPD; Gemini 2.5 Flash 10 RPM / 250.000 TPM / 250 RPD; Gemini 2.5 Flash-Lite 15 RPM / 250.000 TPM / 1.000 RPD. E um retrato ainda mais antigo: Gemini 2.0 Flash 15 RPM / 1.000.000 TPM / 1.500 RPD. — [Gemini API rate limits, versão .md.txt (via resumo de busca)](https://ai.google.dev/gemini-api/docs/rate-limits.md.txt)
- Na primeira semana de dezembro de 2025, muitos desenvolvedores passaram a receber 429; relatos dizem que o Gemini 2.5 Flash caiu de ~250 RPD para ~20 RPD e que o 2.5 Pro sumiu do free tier para muitas contas. São observações de blogs, sem anúncio oficial localizado. — [CometAPI](https://www.cometapi.com/is-free-gemini-2-5-pro-api-fried-changes-to-the-free-quota-in-2025/); [DEV Community](https://dev.to/anna001/is-free-gemini-25-pro-api-fried-changes-to-the-free-quota-in-2025-200h)
- Um post de 07/05/2026 afirma que os modelos Pro foram removidos do free tier em abril de 2026 e ainda cita ~15 RPM / ~1.500 RPD para Flash. — [TinkerLLM, 07/05/2026](https://tinkerllm.com/blog/gemini-api-free-tier-limits-rate-quotas/); isso conflita com a página oficial de 09/10/2026, que lista free tier para o Gemini 2.5 Pro — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

**Tier 1**
- Números de Tier 1 divergem entre guias: um de fevereiro de 2026 fala em 150–300 RPM, 1M TPM e 1.500 RPD; outro, em ~1.000 RPM, 1M TPM e 10K RPD para a classe Flash em meados de 2026. — [aipromptshub.co](https://aipromptshub.co/limits/gemini-rate-limits-2026); [apisrouter.com](https://apisrouter.com/it/gemini-api-cost-guide) (ambos via resumo de busca)
- Tópicos do fórum de desenvolvedores no início de 2026 relatam contas que continuaram com cotas de free tier depois de ativar faturamento e usuários presos no Tier 1. — [Google AI Developers Forum](https://discuss.ai.google.dev/t/stuck-in-tier-1-429-billing-cap-reached-but-promo-credits-prevent-spending-out-of-pocket-for-tier-2/140412)
- Preços pagos (por MTok, 09/10/2026): 2.5 Flash-Lite US$ 0,10 entrada / US$ 0,40 saída; 3.1 Flash-Lite US$ 0,25 / US$ 1,50; 3.5 Flash-Lite US$ 0,30 / US$ 2,50; 2.5 Flash US$ 0,30 / US$ 2,50; 3.8 e 3.6 Flash US$ 0,75 / US$ 3,75 (com preço de 2027 já listado em US$ 1,50 / US$ 7,50). — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

### Inferences
- Por que o bot estourava: (a) com ~20 RPD nos modelos Flash, 200 mensagens/dia é 10 vezes a cota; mesmo 500 RPD de Flash-Lite não cobre 1.000 mensagens/dia; (b) o limite é por projeto, então criar várias chaves no mesmo projeto não soma cota; (c) conversa de Discord vem em rajadas, e várias pessoas falando no mesmo minuto batem em 10–15 RPM mesmo com cota diária sobrando; (d) cada retry depois de um 429 e cada "regenerar" consome mais uma requisição; (e) a cota zera à meia-noite do Pacífico (04:00 ou 05:00 de Brasília, conforme horário de verão dos EUA), ou seja, se esgotar no começo da noite brasileira o bot fica mudo no horário de pico do servidor.
- TPM dificilmente é o limite que estoura: com prompt de ~8.000 tokens, 250.000 TPM equivale a ~30 requisições por minuto, acima do RPM reportado.
- Dos três modelos que o usuário usava, o gemini-1.5-flash-8b não consta mais na tabela oficial de preços de 10/2026 (indício de que foi descontinuado), e os dois 2.5 seguem listados.
- Vincular faturamento (Tier 1) é a mudança de maior efeito: custa centavos por dia no volume do bot (ver seção 5) e tira o RPD de 20–500 do caminho. O teto de cobrança de US$ 250 e o limite de US$ 10 por 10 minutos funcionam como proteção contra conta-surpresa.

### Gaps
- Não foi possível confirmar em fonte primária os valores exatos de RPM/TPM/RPD do free tier nem do Tier 1 em outubro de 2026: o Google só os mostra no painel logado. Os números acima são de terceiros e conflitam (500 vs 1.000 RPD para Flash-Lite). O usuário deve conferir em aistudio.google.com/rate-limit no próprio projeto.
- Não localizei anúncio oficial do Google sobre os cortes de dezembro de 2025.
- Não confirmei data de desligamento do gemini-1.5-flash-8b nem cronograma de descontinuação dos modelos 2.5.
- Requisitos de Tier 2 divergem entre a página oficial atual (US$ 100 + 3 dias) e espelhos antigos (US$ 250 + 30 dias); usei a oficial.

## 4. Preços atuais por milhão de tokens dos modelos mais adequados a roleplay (Anthropic, Google, OpenAI), com descontos de prompt caching e batch e tamanho mínimo de prompt cacheável

### Takeaway
Em outubro de 2026 os modelos pequenos dos três provedores convergiram para a faixa de US$ 0,05–0,30 por MTok de entrada: Claude Haiku 5.5 (US$ 0,10 / 0,50), Gemini 2.5 Flash-Lite (US$ 0,10 / 0,40) e gpt-6-luna (US$ 0,10 / 0,50) ou gpt-5-nano (US$ 0,05 / 0,40). Leitura de cache custa cerca de 10% da entrada nos três, e batch dá 50% de desconto, mas batch não serve para chat em tempo real.

### Cited Findings

**Anthropic (Claude API)** — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

| Modelo | Entrada | Escrita cache 5 min | Escrita cache 1 h | Leitura cache | Saída | Batch (entrada / saída) |
|---|---|---|---|---|---|---|
| Claude Haiku 5.5 (prompt até 100k tokens) | $0,10 | $0,125 | $0,20 | $0,01 | $0,50 | $0,05 / $0,25 |
| Claude Haiku 4.5 | $1,00 | $1,25 | $2,00 | $0,10 | $5,00 | $0,50 / $2,50 |
| Claude Sonnet 5.5 | $2,00 | $2,50 | $4,00 | $0,10 | $10,00 | $1,00 / $5,00 |
| Claude Sonnet 5 | $2,00 | $2,50 | $4,00 | $0,20 | $10,00 | $1,00 / $5,00 |
| Claude Sonnet 4.6 | $3,00 | $3,75 | $6,00 | $0,30 | $15,00 | $1,50 / $7,50 |
| Claude Opus 5.5 | $4,00 | $5,00 | $8,00 | $0,20 | $20,00 | $2,00 / $10,00 |
| Claude Opus 5 | $5,00 | $6,25 | $10,00 | $0,50 | $25,00 | $2,50 / $12,50 |

- Multiplicadores de cache: escrita de 5 min = 1,25x a entrada; escrita de 1 h = 2x; leitura = 0,1x (0,05x no Opus 5.5 e Sonnet 5.5). O cache de 5 min se paga após uma leitura; o de 1 h, após duas. — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Tamanho mínimo cacheável: 512 tokens (Haiku 5.5, Sonnet 5.5, Opus 5.5, Opus 5); 1.024 (Sonnet 5, Sonnet 4.6, Opus 4.8); 2.048 (Opus 4.7); 4.096 (Haiku 4.5, Opus 4.6, Opus 4.5). Prompt menor que o mínimo simplesmente não é cacheado, sem erro. — [Claude Platform docs, Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Cache automático: basta um campo `cache_control` no nível superior da requisição; cada leitura renova o TTL de 5 min sem custo extra. A correspondência é exata (inclusive espaços) e segue a ordem `tools` → `system` → `messages`; qualquer mudança antes do ponto de corte invalida o que vem depois. — [Claude Platform docs, Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- Batch API: 50% de desconto em entrada e saída, processamento assíncrono; acumula com cache. — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Modelos Claude 4.7 em diante usam um tokenizador novo que gera aproximadamente 30% mais tokens para o mesmo texto. — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- O Haiku 5.5 tem preço maior (5x) para requisições com prompt acima de 100.000 tokens. — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Rate limits no tier Start (o mais baixo padrão): 1.000 RPM, 2.000.000 tokens de entrada/min e 400.000 de saída/min para Haiku 5.5, Haiku 4.5 e Sonnet 5.5; teto de gasto de US$ 500/mês. Tokens lidos do cache não contam para o limite de entrada por minuto. Organizações novas podem começar num tier "Evaluation" com limites menores. — [Claude Platform docs, Rate limits](https://platform.claude.com/docs/en/api/rate-limits)

**Google (Gemini API, tier pago)** — [Gemini API pricing, 09/10/2026](https://ai.google.dev/gemini-api/docs/pricing)

| Modelo | Entrada | Saída | Cache (leitura) | Armazenamento de cache (por MTok/hora) | Batch (entrada / saída) |
|---|---|---|---|---|---|
| Gemini 2.5 Flash-Lite | $0,10 | $0,40 | $0,01 | $1,00 | $0,05 / $0,20 |
| Gemini 3.1 Flash-Lite | $0,25 | $1,50 | $0,025 | $1,00 | $0,125 / $0,75 |
| Gemini 3.5 Flash-Lite | $0,30 | $2,50 | $0,03 | $1,00 | $0,15 / $1,25 |
| Gemini 2.5 Flash | $0,30 | $2,50 | $0,03 | $1,00 | $0,15 / $1,25 |
| Gemini 3 Flash Preview | $0,50 | $3,00 | $0,05 | $1,00 | $0,25 / $1,50 |
| Gemini 3.6 Flash / 3.8 Flash (preço 2026 → 2027) | $0,75 → $1,50 | $3,75 → $7,50 | $0,075 → $0,15 | $0,50 → $1,00 | $0,375 / $1,875 |
| Gemini 2.5 Pro (até 200k) | $1,25 | $10,00 | $0,125 | $4,50 | $0,625 / $5,00 |
| Gemini 3.1 Pro Preview (até 200k) | $2,00 | $12,00 | $0,20 | $4,50 | $1,00 / $6,00 |

- Cache implícito é ligado automaticamente nos modelos Gemini 2.5 e posteriores, sem configuração; a economia é repassada quando a requisição acerta o cache. Mínimo de tokens para cache implícito: 2.048 (2.5 Flash, 2.5 Pro) e 4.096 (3.6 Flash, 3.8 Flash, 3.1 Pro Preview). — [Gemini API, Context caching](https://ai.google.dev/gemini-api/docs/caching)
- Gemma 4 aparece como modelo aberto gratuito no free tier, sem preço pago. — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

**OpenAI** — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)

| Modelo | Entrada | Entrada em cache | Saída | Batch/Flex (entrada / saída) |
|---|---|---|---|---|
| gpt-5-nano | $0,05 | $0,005 | $0,40 | $0,025 / $0,20 |
| gpt-6-luna | $0,10 | $0,01 | $0,50 | $0,05 / $0,25 |
| gpt-4.1-nano | $0,10 | $0,025 | $0,40 | $0,05 / $0,20 |
| gpt-4o-mini | $0,15 | $0,075 | $0,60 | $0,075 / $0,30 |
| gpt-5.6-luna | $0,20 | $0,02 | $1,20 | $0,10 / $0,60 |
| gpt-5.4-nano | $0,20 | $0,02 | $1,25 | $0,10 / $0,625 |
| gpt-5-mini | $0,25 | $0,025 | $2,00 | $0,125 / $1,00 |
| gpt-4.1-mini | $0,40 | $0,10 | $1,60 | $0,20 / $0,80 |
| gpt-5.4-mini | $0,75 | $0,075 | $4,50 | $0,375 / $2,25 |
| gpt-5.1 / gpt-5 | $1,25 | $0,125 | $10,00 | $0,625 / $5,00 |
| gpt-6-sol / gpt-6.1-sol | $2,00 | $0,20 / $0,10 | $10,00 | $1,00 / $5,00 |
| gpt-5.6-terra | $2,00 | $0,20 | $12,00 | $1,00 / $6,00 |
| gpt-5.5 | $5,00 | $0,50 | $30,00 | $2,50 / $15,00 |

- Prompt caching é automático nos modelos suportados. Em GPT-5.6 e posteriores: mínimo de 1.024 tokens de prefixo, leitura a 0,1x da entrada (0,05x no GPT-6.1 Sol), escrita a 1,25x, TTL de 30 min a partir da última escrita ou reuso. Em modelos anteriores: entradas duram tipicamente 5–10 min de inatividade (até 1 h) no modo `in_memory`, ou até 24 h no modo `24h`. — [OpenAI, Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
- A página de preços não traz data de publicação; a única nota datada diz que o preço promocional do GPT-5.6 Sol vale pelo menos até 21/11/2026. — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)

### Inferences
- Para persona em PT-BR com respostas curtas, o custo é dominado pela entrada (5.000–8.000 tokens de entrada contra 150 de saída), então o preço de entrada e o de leitura de cache importam muito mais que o de saída.
- O Haiku 5.5 custa um décimo do Haiku 4.5 e tem mínimo de cache de 512 tokens (contra 4.096), o que muda a conta da Anthropic em relação a 2025: Claude deixou de ser a opção cara para bot de hobby.
- O efeito do tokenizador novo da Anthropic (cerca de 30% mais tokens) significa que um prompt de "5.000 tokens" medido em outro provedor pode ser faturado como ~6.500 no Haiku 5.5; a comparação direta de preço por MTok subestima o custo do Claude nessa proporção.
- Batch (50% de desconto) não se aplica a respostas de chat em tempo real; serviria só para tarefas de fundo, como resumir histórico durante a madrugada.
- Cache explícito do Gemini cobra armazenamento por hora (US$ 1,00/MTok/h): manter um character card de 6.000 tokens em cache 24 h por dia custaria cerca de US$ 4,32/mês só de armazenamento, mais do que a economia obtida a 200 mensagens/dia. Para volume baixo, o cache implícito é o que faz sentido.

### Gaps
- Não verifiquei a qualidade de cada modelo pequeno para roleplay em português do Brasil (aderência à persona, naturalidade); os preços não dizem nada sobre isso.
- A página de caching do Gemini não informou o mínimo de tokens para cache implícito nos modelos Flash-Lite, nem o TTL padrão ou o desconto exato; o desconto de 90% é deduzido da tabela de preços (leitura de cache = 10% da entrada).
- Não confirmei se o cache implícito do Gemini cobra armazenamento (a tabela de preços lista armazenamento para "context caching" sem distinguir).
- Não sei se gpt-5-nano, gpt-6-luna e os Gemini Flash-Lite 3.x consomem tokens de raciocínio ("thinking") faturados como saída por padrão; se consumirem, o custo de saída real fica acima dos 150 tokens assumidos.
- Não li a documentação de modelos da OpenAI para entender o posicionamento dos nomes luna/terra/sol/astra; inferi pelo preço que "luna" é a faixa pequena.

## 5. Estimativa de custo trabalhada: system prompt de 3.000–6.000 tokens + ~2.000 de histórico + ~150 de saída, a 200, 1.000 e 5.000 mensagens/dia, com e sem cache

### Takeaway
No modelo mais barato de cada provedor, o bot custa de US$ 1 a US$ 5 por mês a 200 mensagens/dia, de US$ 5 a US$ 26 a 1.000/dia e de US$ 26 a US$ 131 a 5.000/dia; com cache do system prompt, o teto cai para cerca de US$ 50/mês mesmo no volume máximo. Para o tamanho real do servidor (centenas de mensagens/dia), a conta fica abaixo de R$ 30/mês.

### Cited Findings
Preços-base usados no cálculo (todos de 10/2026):
- Claude Haiku 5.5: US$ 0,10 entrada, US$ 0,01 leitura de cache, US$ 0,50 saída. — [Claude Platform docs, Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Gemini 2.5 Flash-Lite: US$ 0,10 / US$ 0,01 / US$ 0,40. Gemini 3.1 Flash-Lite: US$ 0,25 / US$ 0,025 / US$ 1,50. — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- gpt-5-nano: US$ 0,05 / US$ 0,005 / US$ 0,40. gpt-6-luna: US$ 0,10 / US$ 0,01 / US$ 0,50. — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- Câmbio: R$ 4,99 por dólar em 12/10/2026. — [AwesomeAPI USD-BRL](https://economia.awesomeapi.com.br/json/last/USD-BRL)

### Inferences
Premissas do cálculo (meu, a partir dos preços citados): mês de 30 dias (6.000, 30.000 e 150.000 mensagens/mês); cada mensagem = system prompt + 2.000 tokens de histórico + 150 de saída; "sem cache" = toda a entrada a preço cheio; "com cache" = system prompt 100% lido do cache e histórico a preço cheio (cenário ideal, sem contar escritas de cache); sem tokens de raciocínio; sem IOF.

**Cenário A — system prompt de 3.000 tokens (5.000 de entrada por mensagem)**

| Modelo | Custo por 1.000 msgs (sem cache) | 200/dia sem cache | 1.000/dia sem cache | 5.000/dia sem cache | 200/dia com cache | 1.000/dia com cache | 5.000/dia com cache |
|---|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | $0,575 | $3,45 (R$ 17) | $17,25 (R$ 86) | $86,25 (R$ 430) | $1,83 (R$ 9) | $9,15 (R$ 46) | $45,75 (R$ 228) |
| Gemini 2.5 Flash-Lite | $0,560 | $3,36 (R$ 17) | $16,80 (R$ 84) | $84,00 (R$ 419) | $1,74 (R$ 9) | $8,70 (R$ 43) | $43,50 (R$ 217) |
| Gemini 3.1 Flash-Lite | $1,475 | $8,85 (R$ 44) | $44,25 (R$ 221) | $221,25 (R$ 1.104) | $4,80 (R$ 24) | $24,00 (R$ 120) | $120,00 (R$ 599) |
| gpt-5-nano | $0,310 | $1,86 (R$ 9) | $9,30 (R$ 46) | $46,50 (R$ 232) | $1,05 (R$ 5) | $5,25 (R$ 26) | $26,25 (R$ 131) |
| gpt-6-luna | $0,575 | $3,45 (R$ 17) | $17,25 (R$ 86) | $86,25 (R$ 430) | $1,83 (R$ 9) | $9,15 (R$ 46) | $45,75 (R$ 228) |

**Cenário B — system prompt de 6.000 tokens (8.000 de entrada por mensagem)**

| Modelo | Custo por 1.000 msgs (sem cache) | 200/dia sem cache | 1.000/dia sem cache | 5.000/dia sem cache | 200/dia com cache | 1.000/dia com cache | 5.000/dia com cache |
|---|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | $0,875 | $5,25 (R$ 26) | $26,25 (R$ 131) | $131,25 (R$ 655) | $2,01 (R$ 10) | $10,05 (R$ 50) | $50,25 (R$ 251) |
| Gemini 2.5 Flash-Lite | $0,860 | $5,16 (R$ 26) | $25,80 (R$ 129) | $129,00 (R$ 644) | $1,92 (R$ 10) | $9,60 (R$ 48) | $48,00 (R$ 240) |
| Gemini 3.1 Flash-Lite | $2,225 | $13,35 (R$ 67) | $66,75 (R$ 333) | $333,75 (R$ 1.665) | $5,25 (R$ 26) | $26,25 (R$ 131) | $131,25 (R$ 655) |
| gpt-5-nano | $0,460 | $2,76 (R$ 14) | $13,80 (R$ 69) | $69,00 (R$ 344) | $1,14 (R$ 6) | $5,70 (R$ 28) | $28,50 (R$ 142) |
| gpt-6-luna | $0,875 | $5,25 (R$ 26) | $26,25 (R$ 131) | $131,25 (R$ 655) | $2,01 (R$ 10) | $10,05 (R$ 50) | $50,25 (R$ 251) |

**Referência: modelos uma faixa acima (cenário B, 1.000 msgs/dia)**
- Claude Sonnet 5.5: US$ 525/mês sem cache (R$ 2.620), US$ 183/mês com cache (R$ 913). Claude Haiku 4.5: US$ 262,50 sem cache, US$ 100,50 com cache.
- Gemini 2.5 Flash e 3.5 Flash-Lite: US$ 83,25 sem cache, US$ 34,65 com cache. Gemini 3.8 Flash (preço de 2026): US$ 196,88 sem cache, US$ 75,38 com cache.
- gpt-5-mini: US$ 69,00 sem cache, US$ 28,50 com cache. gpt-5.4-mini: US$ 200,25 sem cache, US$ 78,75 com cache.

**Ressalvas que alteram os números**
- Tokenizador da Anthropic: aplicando os ~30% a mais de tokens, o Haiku 5.5 no cenário B passa de US$ 5,25 / 26,25 / 131,25 para cerca de US$ 6,83 / 34,12 / 170,62 sem cache, e de US$ 2,01 / 10,05 / 50,25 para cerca de US$ 2,61 / 13,07 / 65,33 com cache.
- O cenário "com cache" é teto de economia. A 200 mensagens/dia (em média uma a cada 7 minutos, porém em rajadas), o cache de 5 minutos da Anthropic expira com frequência; no pior caso, em que toda requisição reescreve o cache (1,25x), o Haiku 5.5 sairia por US$ 3,90 (cenário A) ou US$ 6,15 (cenário B) por mês, mais caro que sem cache. Com TTL de 1 hora (escrita a 2x) ou com conversa concentrada em rajadas, o resultado se aproxima da coluna "com cache". O mesmo raciocínio vale para o TTL de 30 minutos da OpenAI (escrita a 1,25x em GPT-5.6+).
- A 5.000 mensagens/dia (uma a cada ~17 segundos em média), o cache fica quente quase o tempo todo e a coluna "com cache" é realista.
- Em canal com vários usuários, só a parte fixa (character card, regras) é estável; o histórico muda a cada mensagem e foi mantido a preço cheio. Cachear também o histórico é possível em conversa linear e reduziria mais o custo.
- Com crédito de assinatura: US$ 10/mês do Google AI Pro cobre o cenário B a 1.000 msgs/dia em Gemini 2.5 Flash-Lite com cache (US$ 9,60) e todos os cenários de 200 msgs/dia; US$ 100/mês do Claude Max 5x cobre todos os cenários do Haiku 5.5 com cache e os de até 1.000 msgs/dia sem cache.

### Gaps
- Os valores assumem saída de exatamente 150 tokens e nenhum token de raciocínio; não medi o comportamento real de cada modelo.
- Não medi a taxa real de acerto de cache num canal de Discord; o custo real fica entre as colunas "sem cache" e "com cache".
- BRL sem IOF/spread; não levantei a alíquota de IOF vigente para compra internacional em cartão em 10/2026.
- "Mais barato viável" foi escolhido por preço e por estar na tabela oficial atual, não por teste de qualidade em roleplay PT-BR; se o Gemini 2.5 Flash-Lite ou o gpt-5-nano forem fracos demais para a persona, a comparação relevante passa a ser 3.1 Flash-Lite, gpt-6-luna e Haiku 5.5.

## 6. Alternativas mais baratas ou gratuitas via API: OpenRouter (modelos gratuitos e limites), Groq, Cerebras, Mistral, DeepSeek, Together, Fireworks, NanoGPT, Featherless, Infermatic, ArliAI e serviços flat-rate voltados a roleplay

### Takeaway
Existem três famílias de alternativa: free tiers de inferência rápida (Groq, Cerebras, OpenRouter `:free`), que em 2026 têm limites de tokens por dia pequenos demais para prompts de 5–8 mil tokens; APIs pagas baratas (DeepSeek, modelos via OpenRouter), na mesma faixa de preço dos modelos pequenos dos grandes provedores; e assinaturas flat-rate de roleplay (ArliAI US$ 10–30, Featherless US$ 25), que dão tokens ilimitados com poucas requisições paralelas. Com os preços de 10/2026, nenhuma delas é claramente mais barata que Haiku 5.5 / Flash-Lite / gpt-6-luna para este bot.

### Cited Findings

**OpenRouter**
- Modelos `:free`: 20 requisições por minuto; 50 requisições por dia para quem comprou menos de US$ 10 em créditos (no total histórico) e 1.000 por dia para quem comprou ao menos US$ 10. — [OpenRouter docs, Limits](https://openrouter.ai/docs/api-reference/limits)
- Saldo negativo causa erro 402 inclusive em modelos gratuitos; erros 429 do provedor de origem também ocorrem e o roteamento com fallback pode contorná-los. — [OpenRouter docs, Limits](https://openrouter.ai/docs/api-reference/limits)
- Preços de modelos pagos recomendados para roleplay (verificados em 16/06/2026, por MTok entrada/saída): `deepseek/deepseek-v3.2` US$ 0,23 / 0,34 (131K de contexto, "cheap, reliable default" para cenas longas); `sao10k/l3.3-euryale-70b` US$ 0,65 / 0,75; `gryphe/mythomax-l2-13b` US$ 0,06 / 0,06 (contexto de 4K); `z-ai/glm-4.6` US$ 0,43 / 1,74; `mistralai/mistral-large-2512` US$ 0,50 / 1,50; `nousresearch/hermes-4-405b` US$ 1,00 / 3,00; `deepseek/deepseek-r1-0528` US$ 0,50 / 2,15. — [OpenRouter blog, guia SillyTavern (18/06/2026, atualizado em 24/09/2026)](https://openrouter.ai/blog/tutorials/sillytavern-openrouter/)
- O mesmo guia nota que variantes gratuitas costumam ter janela de contexto menor que a paga, cita `meta-llama/llama-3.3-70b-instruct:free` como boa opção gratuita "quando disponível", e explica os sufixos `:nitro` (provedor mais rápido) e `:floor` (mais barato). Abortar um stream só interrompe a cobrança em provedores que suportam cancelamento. — [OpenRouter blog](https://openrouter.ai/blog/tutorials/sillytavern-openrouter/)
- A disponibilidade de modelos gratuitos muda com frequência; existe um roteador `openrouter/free` que escolhe um modelo gratuito aleatoriamente. — [OpenRouter docs, Free Models Router](https://openrouter.ai/docs/guides/routing/routers/free-router.md)
- Um guia de terceiros afirma que a capacidade gratuita é um pool compartilhado e que modelos populares devolvem 429 mesmo com uso baixo, piorando à noite (horário dos EUA) e nos fins de semana; o guia não apresenta dados. — [apisrouter.com](https://apisrouter.com/openrouter-free-tier-limits)

**Groq**
- Tabela de limites consultada em 10/2026 (a página tem abas "Free Plan" e "Developer Plan" e o texto descreve os valores como base do plano Developer; a atribuição ao free tier fica incerta): `openai/gpt-oss-120b`, `openai/gpt-oss-20b` e `qwen/qwen3.8-27b` com 30 RPM, 1.000 RPD, 8.000 TPM e 200.000 tokens por dia. — [Groq docs, Rate limits](https://console.groq.com/docs/rate-limits)

**Cerebras**
- Free Trial: `gpt-oss-120b` e `qwen-3.8-27b` com 5 RPM, 30.000 TPM não cacheados (90.000 TPM no total), 1M tokens por hora e 1M tokens por dia. Pay-as-you-go: 1.000 RPM e 1M TPM não cacheados (gpt-oss-120b), sem teto horário ou diário. — [Cerebras docs, Rate limits](https://inference-docs.cerebras.ai/support/rate-limits)

**DeepSeek (API direta)**
- `deepseek-flash` (DeepSeek-V4.1-Flash, contexto de 1M, com visão): cache hit US$ 0,006, cache miss US$ 0,30, saída US$ 1,20 por MTok em horário de pico; metade disso fora do pico (US$ 0,003 / 0,15 / 0,60). `deepseek-v4-pro`: US$ 0,044 / 1,32 / 3,96 no pico. — [DeepSeek API docs, Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing)
- Horário de pico: 01:00–04:00 e 06:00–10:00 UTC, de segunda a sexta, exceto feriados chineses; todo o resto é fora de pico. Limite de concorrência: 2.500 (flash) e 500 (pro). — [DeepSeek API docs](https://api-docs.deepseek.com/quick_start/pricing)

**Mistral**
- Rastreadores de terceiros descrevem o tier gratuito "Experiment" da La Plateforme com ~1 bilhão de tokens/mês e ~1 requisição/segundo (500.000 TPM), sem cartão, com número de telefone verificado, e com dados podendo ser usados para treino; as fontes divergem (uma lista 2 req/min) e não achei a documentação oficial. — [free-llm-api-resources (mintlify)](https://mintlify.com/cheahjs/free-llm-api-resources/providers/free/mistral-plateforme); [freellm.net](https://freellm.net/providers/mistral-ai)

**Serviços flat-rate voltados a roleplay**
- ArliAI (10/2026): Free US$ 0 (1 requisição por vez, 12K de contexto, respostas atrasadas); Starter US$ 10/mês (1 paralela, modelos até 31B, 16K); Core US$ 15 (1 paralela, até 355B, 32K); Plus US$ 20 (1 paralela, 128K); Pro US$ 30 (2 paralelas, 256K); Max US$ 160 (6 paralelas). Requisições e tokens ilimitados nos planos pagos; 10% de desconto no anual. — [ArliAI pricing](https://www.arliai.com/pricing)
- Featherless (10/2026): plano Chat US$ 25/mês, 4 unidades de concorrência, contexto de 32K, tokens ilimitados, catálogo de mais de 40.000 modelos; plano Developer US$ 50/mês em créditos, 100 unidades de concorrência, cobrado por token. — [Featherless pricing](https://featherless.ai/pricing)
- NanoGPT: comentários do Reddit de fevereiro de 2026 falam em assinatura de US$ 8/mês para modelos open source com limite de 60M tokens por semana; uma fonte verificada em 31/08/2026 lista US$ 12/mês com 60M tokens de entrada por semana, válido para API e web. Requisições cobertas pela assinatura ainda contam para o limite de requisições por dia, que zera à meia-noite UTC. — [infrabase.ai (fonte secundária)](https://infrabase.ai/inference-apis/nanogpt); [NanoGPT docs, Rate limits](https://docs.nano-gpt.com/api-reference/miscellaneous/rate-limits.md); [snapshot de r/SillyTavernAI, 02/2026](https://reddit.sentinel-team.org/posts/1r7o0dc/snapshots/2026-02-27T16%3A12%3A57.42274Z)

### Inferences
- Groq e Cerebras gratuitos não comportam este bot: 8.000 TPM (Groq) equivale a uma única requisição de 8.000 tokens por minuto, e 200.000 tokens/dia a ~25–40 mensagens; 1M tokens/dia (Cerebras) a ~125–200 mensagens/dia com 5 RPM. Servem como fallback de emergência, não como motor principal, a menos que o prompt seja reduzido para ~1.500 tokens.
- OpenRouter `:free` com US$ 10 depositados uma única vez (1.000 req/dia, 20 RPM) cobre no papel 200–1.000 mensagens/dia a custo zero, mas com disponibilidade instável do pool gratuito e contexto reduzido. É razoável como camada de fallback gratuita.
- DeepSeek direto fora do pico custa, no cenário B, cerca de US$ 7,74/mês a 200 msgs/dia sem cache e US$ 2,45 com cache; no pico, o dobro. O pico (01:00–10:00 UTC em dias úteis) cai entre 22:00 e 07:00 de Brasília, ou seja, a noite brasileira até 22:00 é cobrada a preço fora de pico.
- `deepseek/deepseek-v3.2` no OpenRouter custa ~US$ 11,35/mês no cenário B a 200 msgs/dia e ~US$ 56,73 a 1.000/dia (sem cache), acima de Haiku 5.5, Flash-Lite e gpt-6-luna. A vantagem dos modelos abertos via OpenRouter em 2026 é menos filtro e estilo de prosa, não preço.
- Flat-rate (ArliAI Starter/Core a US$ 10–15, cerca de R$ 50–75) só compensa em relação à API por token acima de ~1.000–2.000 mensagens/dia, e traz um gargalo próprio: 1 requisição paralela significa fila quando duas pessoas falam ao mesmo tempo. O contexto de 16K do Starter comporta o prompt de 8.000 tokens, com pouca folga.
- O plano gratuito da ArliAI (12K de contexto, 1 requisição por vez, respostas atrasadas) é a única opção "ilimitada e gratuita" encontrada, com latência imprevisível.

### Gaps
- Infermatic: nenhuma informação de preço de 2026 encontrada.
- Together e Fireworks: não pesquisados nesta rodada (preços por token de modelos abertos; sem dado coletado).
- NanoGPT: preço da assinatura (US$ 8 vs US$ 12) não confirmado em página oficial; a página /subscription não exibiu conteúdo.
- Não consegui extrair a lista atual de modelos `:free` do OpenRouter (a consulta ao endpoint de modelos voltou incompleta); conferir em openrouter.ai/models filtrando por preço zero.
- Limites do free tier do Groq: a página não deixou claro se os valores mostrados são do plano Free ou do Developer.
- Reputação de confiabilidade: não obtive tópicos de 2026 de r/SillyTavernAI ou r/LocalLLaMA com conteúdo verificável além de um snapshot sobre NanoGPT; as afirmações de instabilidade do pool gratuito do OpenRouter vêm de um blog sem dados.
- Não verifiquei a qualidade em PT-BR dos modelos abertos de roleplay (Euryale, MythoMax etc.), que são ajustados majoritariamente em inglês.

## 7. Técnicas práticas para ficar abaixo dos rate limits: fila de requisições, cooldown por usuário, fallback multi-modelo, tiers de chave/projeto, prompt caching, corte de contexto, sumarização

### Takeaway
A medida de maior efeito é sair do free tier (vincular faturamento ou usar crédito de assinatura), porque os limites pagos mais baixos (1.000 RPM na Anthropic) estão ordens de grandeza acima do que um servidor pequeno gera. O restante — fila, respeitar `retry-after`, cache do character card, histórico curto, fallback entre modelos — reduz custo e evita rajadas.

### Cited Findings
- Gemini: limites valem por projeto e não por chave; RPD zera à meia-noite do Pacífico; os limites dependem do tier e sobem automaticamente com gasto acumulado. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- Anthropic usa token bucket: a capacidade é reposta continuamente, e um limite de 60 RPM pode ser aplicado como 1 requisição por segundo, de modo que rajadas curtas geram 429. — [Claude Platform docs, Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- A resposta 429 da Anthropic traz o cabeçalho `retry-after` com os segundos a esperar; tentativas antes disso falham. Cabeçalhos `anthropic-ratelimit-*-remaining` mostram o saldo de requisições e tokens. — [Claude Platform docs, Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- Na Anthropic, tokens lidos do cache não contam para o limite de tokens de entrada por minuto, então o cache aumenta a vazão efetiva além de baratear. — [Claude Platform docs, Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- É possível definir um teto de gasto próprio abaixo do teto do tier, e limites de gasto e de taxa por workspace. — [Claude Platform docs, Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- Aumentos bruscos de uso podem disparar "acceleration limits" (429) na Anthropic; a recomendação é subir o tráfego gradualmente. — [Claude Platform docs, Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- Cache da Anthropic exige prefixo idêntico: carimbos de hora ou conteúdo por requisição dentro do trecho cacheado quebram o cache; a ordem é `tools` → `system` → `messages`. — [Claude Platform docs, Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- OpenAI: cache automático a partir de 1.024 tokens de prefixo; `prompt_cache_key` agrupa requisições que compartilham prefixo (em modelos anteriores ao GPT-5.6 ajuda no roteamento ao mesmo cache). — [OpenAI, Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
- Gemini: cache implícito automático em modelos 2.5+, com mínimo de 2.048 a 4.096 tokens conforme o modelo. — [Gemini API, Context caching](https://ai.google.dev/gemini-api/docs/caching)
- OpenRouter: manter provedores de fallback habilitados melhora a confiabilidade; `:floor` roteia para o provedor mais barato. — [OpenRouter blog, guia SillyTavern](https://openrouter.ai/blog/tutorials/sillytavern-openrouter/)
- Frontends de chat disparam uma nova requisição a cada swipe, regeneração ou turno de grupo, e retries consomem cota; a prática recomendada é repetir só falhas de rate limit, limitar o número de tentativas e respeitar o tempo de espera pedido pelo servidor. — [apisrouter.com](https://apisrouter.com/openrouter-free-tier-limits); [aireiter.com](https://aireiter.com/es/blog/fix-openrouter-429)
- Tetos de proteção do Gemini pago: US$ 250 de cobrança no Tier 1 e US$ 10 por janela de 10 minutos. — [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

### Inferences
- Fila única com limitador global: uma fila assíncrona no bot com um token bucket ajustado abaixo do RPM do provedor (por exemplo, 1 requisição a cada 5–6 segundos para um free tier de 10–15 RPM) transforma rajadas em espera curta em vez de erro 429.
- Cooldown por usuário e por canal (por exemplo, 1 resposta a cada 10–20 segundos por pessoa) e resposta apenas quando o bot é mencionado ou respondido reduzem o volume mais do que qualquer otimização de prompt; responder a toda mensagem do canal é o padrão que mais consome cota.
- Agrupar mensagens: se três pessoas falam em 5 segundos, uma única chamada com as três mensagens no histórico substitui três chamadas.
- Backoff que respeita `retry-after`, com número máximo de tentativas; nunca repetir em laço, porque cada tentativa conta para o RPD nos free tiers.
- Fallback em cascata: modelo principal pago barato → segundo provedor pago → modelo gratuito (OpenRouter `:free` ou Cerebras) → mensagem "em personagem" avisando que está ocupada. Como os limites são por modelo e por provedor, a cascata soma cotas de forma legítima.
- Não tentar multiplicar cota de free tier com várias chaves no mesmo projeto (não funciona, pois o limite é por projeto); criar vários projetos ou contas para burlar cota não foi verificado nos termos e carrega risco de suspensão (ver seção 2).
- Estrutura do prompt para cache: character card e regras fixas no início, sem data/hora, sem nome do usuário, sem contadores; partes variáveis (histórico, quem está falando, hora atual) no fim. Com Haiku 5.5 o mínimo de 512 tokens é atingido por qualquer card; com Gemini 3.x Flash o mínimo de 4.096 exige um card de pelo menos esse tamanho para haver cache.
- Escolha de TTL: em servidor com conversa esparsa, o cache de 1 hora da Anthropic (escrita a 2x) tende a render mais que o de 5 minutos; em horário de conversa contínua, o de 5 minutos basta.
- Corte de contexto: janela deslizante com teto fixo de tokens de histórico (os 2.000 da premissa) mantém custo e TPM previsíveis; cortar o histórico em blocos (e não mensagem a mensagem) preserva mais prefixo cacheável.
- Sumarização: resumir o histórico antigo em um parágrafo de memória a cada N mensagens, de preferência com o modelo mais barato e, se não houver pressa, via Batch (50% de desconto), em vez de carregar o log inteiro.
- Enxugar o character card de 6.000 para 3.000 tokens reduz o custo sem cache em cerca de 35% (cenário B para A), mas com cache a diferença quase desaparece (US$ 2,01 contra US$ 1,83 no Haiku 5.5 a 200 msgs/dia); com cache funcionando, o tamanho do card deixa de ser o fator de custo.
- Limitar `max_tokens` da resposta (por exemplo, 300) evita respostas longas inesperadas; definir teto de gasto mensal no console de cada provedor protege contra laços de retry ou abuso por algum membro.

### Gaps
- Não encontrei fonte primária que trate especificamente de bots de Discord; as técnicas acima são aplicação geral dos mecanismos documentados pelos provedores.
- Não verifiquei nos termos do Google se criar múltiplos projetos para somar cota de free tier é explicitamente proibido; a página de termos consultada não aborda o ponto.
- Não testei na prática a taxa de acerto de cache implícito do Gemini com prompts de persona, nem o comportamento do cache quando o bot atende vários canais com o mesmo card.
