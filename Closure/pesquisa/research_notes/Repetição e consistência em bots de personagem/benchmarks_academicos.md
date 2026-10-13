# Benchmarks acadêmicos de role-play / bots de personagem: consistência de persona e naturalidade

Escopo: o que benchmarks e artigos de 2023 a 2026 definem, medem e mitigam em relação a repetição, recitação do perfil, puxar tópico antigo de volta, perda de persona em conversa longa, comportamento de "assistente" fora do personagem (OOC) e explicação excessiva da própria identidade. Data de referência: outubro de 2026.

Nota de método: li as seções reais (HTML/PDF) de CharacterEval, CharacterBench, CoSER (parcial), PersonaGym (PDF da ACL), RoleLLM (PDF da ACL), RPEval e RMTBench. De SocialBench, TimeChara, InCharacter, Persona Drift, a RL multi-turno de Abdulhai et al. e PCL li só o abstract ou a página de resumo. Uma busca no arXiv (PersonaGym em HTML) foi bloqueada por limite de requisições, e por isso usei o PDF da ACL Anthology no lugar. Não li o RPBench (Boson AI).

## 1. Dimensões, rubricas e configuração de juiz de cada benchmark

### Takeaway
Quase todos os benchmarks repartem a qualidade de role-play em três blocos. O primeiro é a fidelidade ao personagem (conhecimento, persona, estilo de fala). O segundo é a capacidade conversacional ou credibilidade (fluência, coerência, "human-likeness", engajamento). O terceiro são riscos (moralidade, toxicidade, segurança). Juízes treinados em notas humanas (CharacterRM, CharacterJudge) se correlacionam bem mais com humanos do que o GPT-4 com prompt. Mesmo assim, "human-likeness" e "engagement" são justamente as dimensões em que até o melhor juiz é fraco (r em torno de 0,52 a 0,58).

### Cited Findings

**CharacterEval** (arXiv 2401.01275 v2, jan/2024; código, dados e reward model em github.com/morecry/CharacterEval)
- Usa 4 dimensões e 13 métricas — [CharacterEval](https://arxiv.org/html/2401.01275):
  - Conversational Ability: Fluency, Coherency, Consistency.
  - Character Consistency: Knowledge-Exposure, Knowledge-Accuracy, Knowledge-Hallucination, Persona-Behavior, Persona-Utterance.
  - Role-playing Attractiveness: Human-Likeness, Communication Skills, Expression Diversity, Empathy.
  - Personality Back-Testing: acurácia de MBTI contra 54 tipos de referência.
- Doze anotadores deram notas de 1 a 5, cada um num subconjunto esparso de métricas. Essas notas treinaram o CharacterRM, com base Baichuan2-13B — [CharacterEval](https://arxiv.org/html/2401.01275).
- Pearson com humanos, no geral: CharacterRM 0,631; GPT-4 0,362 (1-shot), 0,385 (2-shot) e 0,375 (3-shot) — [CharacterEval](https://arxiv.org/html/2401.01275).
- Por métrica, o CharacterRM vai melhor em Persona-Behavior (0,879) e Expression Diversity (0,765) e pior em Knowledge-Accuracy (0,336) e Empathy (0,385). Em Empathy o GPT-4 1-shot (0,407) supera o CharacterRM — [CharacterEval](https://arxiv.org/html/2401.01275).
- Os autores relatam viés de autopromoção do GPT-4 como juiz — [CharacterEval](https://arxiv.org/html/2401.01275).

**CharacterBench** (arXiv 2412.11912 v1, dez/2024; a página não informa venue)
- Tem 11 dimensões em 6 aspectos — [CharacterBench](https://arxiv.org/html/2412.11912):
  - Esparsas, que só aparecem quando a pergunta provoca: Memory Consistency, Fact Accuracy, Boundary Consistency, Attribute Consistency, Behavior Consistency, Emotional Self-regulation, Empathetic Responsiveness.
  - Densas, que aparecem em toda resposta: Morality Stability, Morality Robustness, Human-likeness, Engagement.
- O juiz é o CharacterJudge, fine-tune do Qwen2-7B-Chat com notas humanas, mais self-consistency por voto majoritário. Pearson médio com humanos (zh/en): 68/64. O melhor baseline, GLM-4 com target-oriented queries, fica em 48/47. O GPT-4-1106 fica em 45/46 com essas queries e 38/41 sem elas — [CharacterBench](https://arxiv.org/html/2412.11912).
- Ablação: sem self-consistency, 64/60; sem target-oriented queries, 51/48; sem as duas, 47/45 — [CharacterBench](https://arxiv.org/html/2412.11912).
- As dimensões em que o CharacterJudge vai pior são human-likeness (52/53) e engagement (58/53). Os baselines ficam muito abaixo nelas, entre ~9 e ~30 — [CharacterBench](https://arxiv.org/html/2412.11912).
- Os modelos tiram notas baixas em human-likeness (cerca de 2 a 3,4 de 5). Attribute consistency fica acima de behavior consistency. Moralidade satura (~4,7 a 4,9) e quase não separa os modelos — [CharacterBench](https://arxiv.org/html/2412.11912).
- A média é de 11,22 turnos por amostra — [CharacterBench](https://arxiv.org/html/2412.11912).

**RoleLLM / RoleBench** (Findings of ACL 2024, pp. 14743–14777)
- O corpus tem 168.093 amostras e 100 papéis (95 em inglês, 5 em chinês) — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- A métrica é ROUGE-L sobre três conjuntos de referência: RAW (acurácia geral), CUS (imitação do estilo de fala) e SPE (conhecimento específico do papel) — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- Há também win rate par a par julgado pelo GPT-4, com prompts adaptados do AlpacaEval, e por humanos. RoleLLaMA-7B contra RoleGPT: 55,8 pelo GPT-4 e 52,0 por humanos — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).

**PersonaGym** (Findings of EMNLP 2025, pp. 6999–7022; v1 no arXiv em jul/2024, com v3 e v4 depois)
- Tem 5 tarefas: Expected Action, Action Justification, Linguistic Habits, Persona Consistency e Toxicity Control — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).
- O PersonaScore é a média das notas de 1 a 5 de dois juízes, GPT-4o e LLaMA-3-70B, com temperatura 0. A rubrica de cada pergunta traz exemplos de resposta para cada nível de nota, gerados por LLM para aquela persona e aquela pergunta — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).
- Validação humana: 5 anotadores, 1.500 respostas, Fleiss' κ 0,71. Spearman médio com o PersonaScore 75,1% e Kendall-Tau 62,73% — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).
- Linguistic Habits é a tarefa mais difícil. Só GPT-4.1, GPT-4.5 e DeepSeek-V3 têm média de 4 ou mais — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).
- Tamanho não garante fidelidade: GPT-4.1 e LLaMA-3-8B empatam em 4,49, e o LLaMA-3-8B supera o LLaMA-3.3-70B — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).

**CoSER** (arXiv 2502.09082)
- A avaliação é "Given-Circumstance Acting" (GCA): o modelo-ator interpreta personagens de livros dentro da cena original, um modelo escolhe quem fala a seguir, e a simulação vai até 20 turnos — [CoSER](https://arxiv.org/html/2502.09082).
- São 4 dimensões — [CoSER](https://arxiv.org/html/2502.09082):
  - Anthropomorphism: self-identity, emotional depth, persona coherence, social interaction.
  - Character Fidelity: language style, knowledge, personality/behavior, relationships.
  - Storyline Quality.
  - Storyline Consistency.
- O juiz trabalha por penalidade. Críticos GPT-4o listam falhas contra a rubrica, cada uma com severidade de 1 a 5, e a nota é s = 100 − 5·Σv. Há correção de comprimento de +λ|M̄| com λ = 1,5, porque simulações longas acumulam mais falhas. Os pensamentos internos ficam de fora do que o juiz vê — [CoSER](https://arxiv.org/html/2502.09082).
- Exemplo de resultado: GPT-4o tem média 59,95 e anthropomorphism 48,93, mas BLEU de só 5,90 contra o diálogo original — [CoSER](https://arxiv.org/html/2502.09082).

**InCharacter** (ACL 2024 Long, pp. 1840–1873)
- Entrevista o personagem com 14 escalas psicológicas em 32 personagens. A personalidade medida bate com a percebida por humanos em até 80,7% dos casos. O método foi proposto em oposição ao autorrelato, isto é, o modelo responder o questionário diretamente — [InCharacter](https://aclanthology.org/2024.acl-long.102/).

**SocialBench** (Findings of ACL 2024, pp. 2108–2126)
- Avalia a "sociality" de agentes de role-play em nível individual e de grupo, com 500 personagens, mais de 6.000 prompts e 30.800 falas multi-turno. Ir bem no nível individual não implica ir bem no de grupo — [SocialBench](https://aclanthology.org/2024.findings-acl.125/).
- O nome "RoleInteract" aparece apenas na URL do GitHub do benchmark. A página da Anthology não confirma oficialmente que houve uma troca de nome — [SocialBench](https://aclanthology.org/2024.findings-acl.125/).

**TimeChara** (Findings of ACL 2024)
- Mede "point-in-time character hallucination": o personagem sabe de coisas que, no momento da história em que está, ainda não deveria saber. O dataset tem 10.895 instâncias. O GPT-4o tem alucinação significativa — [TimeChara](https://preview.aclanthology.org/setup/2024.findings-acl.197).

**RPEval** (arXiv 2505.13157; github.com/yelboudouri/RPEval)
- Tem 4 dimensões: emotional understanding (13 emoções), decision-making (sim/não), moral alignment (sim/não) e in-character consistency. Esta última vale 0 se a resposta revelar conhecimento fora do contexto do personagem. A pontuação é toda automática, por casamento de rótulo e filtro de palavra-chave, sem juiz LLM — [RPEval](https://arxiv.org/html/2505.13157v1).
- Em in-character consistency o GPT-4o tira 5,81%, contra 59,75% do Gemini-1.5-Pro e 48,13% do Llama-3.2-1B. Exemplo do artigo: um monge medieval perguntado sobre um filme moderno, e o GPT-4o responde com o nome do diretor — [RPEval](https://arxiv.org/html/2505.13157v1).

**RMTBench** (arXiv 2507.20352; Findings of EMNLP 2025, segundo a listagem da ACL Anthology)
- Tem 80 personagens e cerca de 8.156 falas de usuário. São diálogos de ~20 rodadas, mais alguns estendidos. O benchmark é centrado no usuário e só traz as falas dele, então o modelo gera todas as respostas da conversa — [RMTBench](https://arxiv.org/html/2507.20352v1).
- Tem 7 dimensões. Emotional Expression, Emotional Comprehension, Plot Advancement e Character Understanding valem para todos os cenários. Character Maintenance, Security e User Preference Awareness valem para cenários específicos e são julgadas em sim/não — [RMTBench](https://arxiv.org/html/2507.20352v1).
- O juiz é o Qwen2.5-72B, avaliando cada dimensão separadamente para reduzir o viés de comprimento. A concordância com humanos é de 0,78, enquanto os anotadores humanos ficam entre 0,77 e 0,84. Os próprios autores reconhecem que a correlação "não é tão alta" — [RMTBench](https://arxiv.org/html/2507.20352v1).
- Listagem na Anthology: [RMTBench EMNLP Findings](https://preview.aclanthology.org/new-sigs/2025.findings-emnlp.730/).

### Inferences
- O padrão é estável: o juiz que mais concorda com humanos é um modelo pequeno treinado em notas humanas para aquele benchmark, e não um LLM de ponta só com prompt (0,63 contra 0,38 no CharacterEval; 0,68 contra 0,45 no CharacterBench). Para quem monta um juiz automático, ancorar o juiz em exemplos rotulados por humanos rende mais do que escolher um modelo maior.
- "Human-likeness/naturalidade" é ao mesmo tempo a dimensão em que os modelos tiram menos nota e a que os juízes medem pior. Por isso, a avaliação dessa dimensão deveria ter amostragem humana.

### Gaps
- Não consegui ler o RPBench / RPBench-Auto (Boson AI). Não há dados dele aqui.
- No CoSER, faltaram as notas GCA de CoSER-8B/70B, a concordância juiz-humano e a lista completa de falhas da rubrica. O excerto lido não mostra uma falha "repetitive".
- Do SocialBench (dimensões detalhadas, como memória de longo prazo) e do TimeChara (números) só li o abstract.

## 2. Quem mede repetição, diversidade, "humanlikeness" e consistência em conversa longa

### Takeaway
Nenhum dos benchmarks lidos tem uma métrica explícita de repetição ou de bordão (distinct-n, self-BLEU) entre suas dimensões principais. A diversidade aparece como rubrica de juiz ("Expression Diversity" no CharacterEval) e a naturalidade como "Human-likeness" ou "Anthropomorphism". A consistência em conversa longa é medida por degradação ao longo dos turnos (CharacterEval, RMTBench) e por métricas de drift (Persona Drift, Abdulhai et al.). Todos encontram queda.

### Cited Findings
- O CharacterEval mede Expression Diversity por rubrica e não por métrica lexical. BC-NPC-Turbo tem a maior nota (2,336) e GPT-3.5 a menor (1,660). O artigo não traz achados sobre repetição — [CharacterEval](https://arxiv.org/html/2401.01275).
- No CharacterEval, a maioria dos modelos piora à medida que a conversa avança, inclusive o GPT-4. O InternLM-20B é exceção e se mantém estável. A explicação dos autores de que modelos de role-play não foram otimizados para diálogos longos é uma hipótese — [CharacterEval](https://arxiv.org/html/2401.01275).
- No RMTBench, modelos abertos pioram com o comprimento do diálogo e os fechados se mantêm ou melhoram levemente. Avaliar com "pseudo multi-turno", isto é, usando respostas pré-escritas como contexto, superestima as notas em ~4 pontos. Blocos isolados também pontuam acima de diálogos completos — [RMTBench](https://arxiv.org/html/2507.20352v1).
- O RMTBench não avalia repetição — [RMTBench](https://arxiv.org/html/2507.20352v1).
- Persona Drift (Li et al., arXiv 2402.10962 v4): dois chatbots instruídos conversam entre si (LLaMA2-chat-70B, GPT-3.5). Há drift significativo da instrução em até 8 rodadas. A causa proposta é o decaimento da atenção às instruções iniciais conforme a conversa cresce — [Persona Drift](https://arxiv.org/abs/2402.10962).
- Abdulhai et al. (NeurIPS 2025) definem três métricas automáticas de drift, todas validadas contra humanos — [NeurIPS 2025](https://proceedings.nips.cc/paper_files/paper/2025/hash/4c91443877f8388d8190c938ac5a4d4d-Abstract-Conference.html):
  - prompt-to-line: a fala bate com o prompt de persona?
  - line-to-line: a fala contradiz turnos anteriores?
  - Q&A consistency: as respostas a perguntas de sondagem ficam estáveis?
- O CharacterBench inclui Memory Consistency, uma dimensão esparsa sobre lembrar o que foi dito antes, numa média de 11,22 turnos por amostra. Não há achado sobre degradação longa — [CharacterBench](https://arxiv.org/html/2412.11912).
- O CoSER aplica correção de comprimento porque simulações longas acumulam mais falhas. É um reconhecimento metodológico de que a nota depende do tamanho da conversa — [CoSER](https://arxiv.org/html/2502.09082).

### Inferences
- A repetição e o uso excessivo de bordão, que são o problema prático do bot, não têm uma métrica padronizada nesses benchmarks. Quem quiser medi-los precisa combinar métricas lexicais simples (distinct-n, n-gramas repetidos entre turnos, frequência de bordão) com uma rubrica de juiz. A literatura aqui não oferece nada pronto.
- O achado de "pseudo multi-turno" do RMTBench importa na prática: testar o bot com histórico pré-escrito esconde a degradação real. O teste precisa deixar o próprio bot gerar o histórico.

### Gaps
- Não encontrei, nos artigos lidos, nenhum benchmark de role-play que relate distinct-n ou self-BLEU como dimensão central. Não fiz uma busca exaustiva por artigos menores que talvez o façam.
- Não achei estudo específico sobre "puxar tópico antigo de volta". O mais próximo é Memory Consistency (CharacterBench) e line-to-line consistency (Abdulhai et al.), que medem o oposto: contradizer o passado.

## 3. Cópia do prompt, recitação da descrição e excesso de aderência; OOC de assistente

### Takeaway
A recitação ou cópia literal do perfil não é medida diretamente em nenhum dos benchmarks lidos. A literatura cobre bem o lado oposto: quebrar o personagem com conduta de "assistente de IA" e usar conhecimento fora da época ou do mundo do personagem. Há sinais de que juízes LLM não punem persona fraca ou genérica, mas nenhum resultado específico sobre recitação.

### Cited Findings
- No PersonaGym, o Claude 3 Haiku tem a menor nota (3,64) e recusa o role-play ~8,5 vezes mais que o segundo colocado. As recusas costumam citar falta de "experiência pessoal" e ser um "AI Assistant". O Claude 3.5 Sonnet (4,51) quase não resiste — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).
- Também no PersonaGym, uma persona de escritor londrino recebe 4,5/4,5/4,0 dos juízes e 2,0/2,0/3,0 dos humanos, porque faltava o estilo linguístico esperado. O juiz LLM sub-pune persona superficial — [PersonaGym](https://aclanthology.org/2025.findings-emnlp.368.pdf).
- No CharacterEval, as recusas do GPT-3.5 do tipo "não posso interpretar" são atribuídas a excesso de alinhamento por RLHF — [CharacterEval](https://arxiv.org/html/2401.01275).
- No RMTBench, Character Maintenance é a dimensão que mais discrimina entre modelos. Até o Claude 3.5 às vezes revela ser uma IA — [RMTBench](https://arxiv.org/html/2507.20352v1).
- No RPEval, o GPT-4o tira 5,81% em in-character consistency porque responde com conhecimento que o personagem não teria — [RPEval](https://arxiv.org/html/2505.13157v1).
- No TimeChara, o personagem revela conhecimento posterior ao seu momento na história, e isso ocorre de forma significativa até no GPT-4o — [TimeChara](https://preview.aclanthology.org/setup/2024.findings-acl.197).
- No RoleLLM, os prompts de customização incluem nome, descrição e bordões ("catchphrases") do papel. O artigo não relata achado sobre cópia literal da descrição — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- O CoSER tem a sub-dimensão "self-identity" dentro de Anthropomorphism. É o lugar mais próximo de onde "explicar a própria identidade de forma artificial" seria punido, mas o excerto lido não detalha a falha — [CoSER](https://arxiv.org/html/2502.09082).

### Inferences
- A "recitação de traços" ("como um pirata, eu adoro o mar...") provavelmente passa sem penalidade por juízes LLM. O caso do escritor londrino mostra o juiz premiando aderência superficial. Se o projeto quiser controlar recitação, terá de criar uma rubrica própria ou um detector de sobreposição lexical entre a resposta e o texto do perfil.

### Gaps
- Não encontrei artigo que meça a sobreposição entre resposta e descrição do personagem, ou que chame isso de falha. É uma lacuna real da literatura lida, não prova de que tal artigo não exista.
- Não achei dados sobre "explicar a identidade em excesso" como falha nomeada.

## 4. Mitigações com evidência

### Takeaway
As mitigações com números são estas:
- Exemplos de diálogo no prompt (dialogue engineering) superam a descrição de traços (RoleLLM).
- Instruções de sistema ou fine-tune superam a recuperação de trechos crus para conhecimento do papel (RoleLLM).
- Fine-tune em dados de role-play autêntico (CoSER, RoleLLaMA).
- RL multi-turno com recompensa de consistência, que reduz inconsistência em mais de 55% (Abdulhai et al.).
- Split-softmax contra o decaimento de atenção (Persona Drift).
- Contraste "com perfil × sem perfil" em DPO (PCL), com ganhos pequenos.

Para lembretes no fim do contexto e instruções negativas, não encontrei evidência quantitativa nos artigos lidos.

### Cited Findings
- **Exemplos de diálogo contra descrição de traços.** No RoleGPT, avaliado pelo GPT-4 em dados chineses, few-shot dialogue engineering vence em 63,3% (rank médio 1,5), few-shot prompt engineering em 29,8% (rank 1,9) e zero-shot em 9,3% (rank 2,4). Os autores concluem que dialogue engineering é preferido a prompt engineering — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- **Recuperação contra instrução de sistema** (SPE, ROUGE-L) — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf):

  | Modelo | Recuperação | Instrução de sistema |
  |---|---|---|
  | RoleLLaMA | 36,7 | 38,1 |
  | RoleGLM | 25,3 | 34,1 |
  | RoleGPT | 23,6 | 23,4 (empate) |

  Para os modelos ajustados, a instrução de sistema é melhor e gasta menos contexto.
- **Context-Instruct contra recuperação** (SPE). A geração de dados de conhecimento a partir do perfil (Context-Instruct) chega a 38,1, contra 21,4 sem ela e 19,1 só com recuperação. Os autores atribuem parte da fraqueza da recuperação a fontes de perfil ruidosas e esparsas — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- **Fine-tune de estilo.** O RoCIT (LoRA) eleva CUS em relação aos baselines gerais, mas o RoleGPT, com prompt, ainda é mais forte em CUS (57,6 contra 32,9). O ganho em papéis não vistos é limitado, sem melhora notável em SPE — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- **Fine-tune em diálogos autênticos de livros (CoSER).** CoSER-8B/70B são LLaMA-3.1 com dados de 90% dos livros mais Tulu-3. O 70B "supera ou empata com o GPT-4o" e tem 75,80% no InCharacter e 93,47% no LifeChoice (dados do abstract) — [CoSER](https://arxiv.org/html/2502.09082).
- **RL multi-turno com recompensa de consistência.** Usar as métricas prompt-to-line, line-to-line e Q&A como recompensa reduz a inconsistência em mais de 55% nos domínios de paciente, aluno e parceiro de conversa social — [NeurIPS 2025](https://proceedings.nips.cc/paper_files/paper/2025/hash/4c91443877f8388d8190c938ac5a4d4d-Abstract-Conference.html).
- **Split-softmax.** É um método leve contra o decaimento de atenção à instrução e "compara favoravelmente" a dois baselines fortes. O abstract não diz quais são os baselines (não é possível confirmar que incluem repetir o system prompt) nem traz números — [Persona Drift](https://arxiv.org/abs/2402.10962).
- **PCL (Persona-Aware Contrastive Learning,** arXiv 2503.17662; a busca indica Findings of ACL 2025 em aclanthology.org/2025.findings-acl.1344**).** Junta auto-questionamento em 5 rodadas (Chain of Persona) com DPO contrastando respostas com e sem o perfil. Os ganhos de character consistency no CharacterEval são pequenos: Baichuan2-7B de 2,700 para 2,799 e GPT-4 de 2,697 para 2,785. Persona-Behavior caiu em vários modelos — [PCL](https://arxiv.org/html/2503.17662v1); [ACL Anthology PDF](https://aclanthology.org/2025.findings-acl.1344.pdf).
- **Narrative-Experts (TimeChara).** Decompor o raciocínio com "especialistas narrativos" reduz a alucinação de ponto no tempo. Os autores dizem que o problema continua em aberto — [TimeChara](https://preview.aclanthology.org/setup/2024.findings-acl.197).
- **Juízes treinados, como base para reranking.** CharacterRM (r = 0,631) e CharacterJudge (r ≈ 0,66) são juízes treinados que poderiam servir de reranker. O CharacterBench diz que o benchmark pode ser usado para otimizar com DPO, mas essa seção estava cortada na leitura — [CharacterEval](https://arxiv.org/html/2401.01275); [CharacterBench](https://arxiv.org/html/2412.11912).

### Inferences
- Para um bot de Discord sem fine-tune, a evidência mais direta é a do RoleLLM: dar falas de exemplo em vez de listar traços. Isso também deve reduzir a recitação de traços, porque o modelo imita forma em vez de citar conteúdo. Essa segunda parte é inferência, não foi medida.
- O decaimento de atenção (Persona Drift) dá base teórica para reinjetar a persona perto do fim do contexto. Ainda assim, não encontrei medição dessa técnica específica nos artigos lidos.

### Gaps
- **Lembretes no fim do contexto.** Nenhum número encontrado. O artigo de Persona Drift pode comparar com repetição de system prompt no corpo do texto, mas li só o abstract.
- **Instruções negativas** ("não repita", "não diga que é IA"). Não encontrei estudo com números dentro desse escopo.
- **Reranking por juiz em produção.** Há juízes disponíveis, mas não achei experimento que meça o efeito do reranking sobre repetição ou OOC.

## 5. Mudanças de status (versões, venues, retratações)

### Takeaway
Não encontrei retratações. Vários preprints foram publicados depois em conferências com versões revisadas no arXiv, e por isso é preciso citar a versão de venue quando ela existe.

### Cited Findings
- **PersonaGym:** arXiv 2407.18416 (jul/2024, versões v3 e v4) e publicação em Findings of EMNLP 2025. Os resultados da versão final incluem modelos de 2025 (GPT-4.1, GPT-4.5, DeepSeek-V3, LLaMA-3.3-70B) — [PersonaGym ACL](https://aclanthology.org/2025.findings-emnlp.368.pdf); [arXiv v4](https://arxiv.org/html/2407.18416v4).
- **RoleLLM:** arXiv 2310.00746 e publicação em Findings of ACL 2024 — [RoleLLM](https://aclanthology.org/2024.findings-acl.878.pdf).
- **SocialBench:** Findings of ACL 2024. "RoleInteract" aparece só na URL do GitHub. Que seja o nome anterior é provável, mas não está confirmado na página — [SocialBench](https://aclanthology.org/2024.findings-acl.125/).
- **InCharacter:** ACL 2024 Long — [InCharacter](https://aclanthology.org/2024.acl-long.102/).
- **TimeChara:** Findings of ACL 2024 — [TimeChara](https://preview.aclanthology.org/setup/2024.findings-acl.197).
- **Persona Drift:** arXiv 2402.10962, v4 de 25/07/2024 — [Persona Drift](https://arxiv.org/abs/2402.10962).
- **RMTBench:** arXiv 2507.20352 e Findings of EMNLP 2025. O texto da v1 tem inconsistências internas: diálogo estendido ">20" contra ">25" rodadas, e tamanho de bloco descrito de duas formas diferentes — [RMTBench](https://arxiv.org/html/2507.20352v1); [Anthology](https://preview.aclanthology.org/new-sigs/2025.findings-emnlp.730/).
- **CharacterEval** (v2, jan/2024) e **CharacterBench** (v1, dez/2024): as páginas lidas não mostram venue — [CharacterEval](https://arxiv.org/html/2401.01275); [CharacterBench](https://arxiv.org/html/2412.11912).
- **Abdulhai et al.:** NeurIPS 2025 — [NeurIPS](https://proceedings.nips.cc/paper_files/paper/2025/hash/4c91443877f8388d8190c938ac5a4d4d-Abstract-Conference.html).

### Inferences
- Os números do PersonaGym citados em blogs de 2024 (v1) podem não bater com a versão do EMNLP 2025, que trocou os modelos avaliados.

### Gaps
- Não verifiquei se CharacterEval (ACL 2024?), CharacterBench (AAAI 2025?) e CoSER (ICML 2025?) foram publicados em conferência. Os pontos de interrogação são suposições minhas, não confirmadas.
- Não procurei errata de cada artigo de forma sistemática.
