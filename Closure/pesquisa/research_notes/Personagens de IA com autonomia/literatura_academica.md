# LLM agents with persistent personality, memory and initiative: academic and technical literature (2023 - Oct 2026)

Scope note: compiled 2026-10-13 for a text-only Discord bot with two fixed characters (RPG rules Q&A plus community chat). Every item carries a publication year. Evidence tier tags: [PEER] = peer-reviewed venue confirmed (by the fetched page, or flagged where only from general knowledge/task brief), [PREPRINT] = arXiv only, [VENDOR] = company-reported, [SEARCH-ONLY] = seen only in a search snippet, not opened (treat as unverified). Where an abstract page did not state the venue I say so rather than assume. Numbers are copied from pages I actually fetched; anything else is marked as missing.

---

## 1. Generative Agents (Park et al. 2023): memory stream, retrieval, reflection, planning, ablations, follow-ups and cost

### Takeaway
The original architecture is three cheap-to-describe mechanisms (a natural-language memory stream with a 3-factor retrieval score, threshold-triggered reflection, hierarchical planning with react-or-continue checks). In the paper's own 100-participant evaluation each component raised believability, but the system was costly ("thousands of dollars" for 2 days of 25 agents) and showed retrieval failures, embellishment and over-agreeableness. The 2024 "1,000 people" work shows that rich first-person interview text, not elaborate architecture, drives fidelity to a real person.

### Cited Findings
- Paper: Park, O'Brien, Cai, Morris, Liang, Bernstein, "Generative Agents: Interactive Simulacra of Human Behavior", 2023 (v1 Apr 2023, v2 Aug 2023). 25 agents in a Sims-like sandbox; architecture stores experiences in natural language, synthesizes them into reflections, retrieves them to plan. The arXiv page lists only a preprint (the UIST 2023 venue is known to me and stated in the task brief, but was not shown on the page I fetched). — [arXiv 2304.03442](https://arxiv.org/abs/2304.03442)
- Retrieval score = alpha_recency * recency + alpha_importance * importance + alpha_relevance * relevance, all alphas = 1, each component min-max scaled to [0,1]. Recency = exponential decay with factor 0.995 per sandbox game hour since last retrieval. Importance = integer 1 (mundane) to 10 (poignant) rated by the LLM when the memory is created. Relevance = cosine similarity between memory embedding and query embedding. Top-ranked memories that fit the context window go in the prompt. — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- Reflection triggers when the summed importance of recent events exceeds 150 (about 2-3 times per day per agent). Procedure: feed the 100 most recent memories, ask for 3 salient high-level questions, use them as retrieval queries (including earlier reflections), ask for 5 insights with citations to evidence, store them as reflections (forming reflection trees). — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- Planning: top-down, 5-8 broad chunks for the day, decomposed into hour chunks then 5-15 minute actions; plans stored in memory and can be revised. At each step the model decides continue-or-react; reacting regenerates the plan from that point. — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- Ablation (100 participants, TrueSkill mu): full architecture 29.89; no reflection 26.88; no reflection or planning 25.64; human crowdworker role-play 22.95; no memory/planning/reflection 21.21. Kruskal-Wallis H(4)=150.29, p<0.001; all pairwise differences significant except crowdworker vs fully ablated. Authors report Cohen's d = 8.16 between prior-work condition and full architecture. Note: the fully ablated agent scored statistically equal to humans pretending to be the character, i.e. memory plus reflection plus planning is what lifts it above a baseline LLM. — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- Cost: no exact figure given; the paper says the 2-day, 25-agent simulation cost "thousands of dollars in token credits" and took multiple days. — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- Failure modes reported by the authors: retrieval failures (relevant memory not surfaced, or only fragments); embellishment (unsupported details, borrowed world knowledge); 6 of 453 responses (1.3%) hallucinated acquaintances; erratic behavior as memory grew (location choices drifted, misreading venue norms); instruction tuning made dialogue overly formal and agents overly agreeable (adopting others' ideas). Also flagged: prompt hacking and memory hacking risks. — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- "Generative Agent Simulations of 1,000 People" (Park et al., Nov 2024, preprint): agents built from 2-hour interview transcripts of 1,052 Americans. On held-out General Social Survey items, interview-only / survey-only / combined agents reached 83% / 82% / 86% of participants' own two-week test-retest consistency; demographics-only agents reached 74%. Interview-grounded agents also reduced accuracy gaps across racial and ideological groups. Abstract notes gains from combining sources are small ("asymptote"). — [arXiv 2411.10109](https://arxiv.org/abs/2411.10109) (a search snippet instead says 85%; I used the abstract page figures, so treat 85% as unreconciled: [search snippet](https://arxiv.org/abs/2411.10109v1))
- Critical review of generative social simulation: argues LLM agent-based models are orders of magnitude more computationally demanding than conventional ABMs, rarely do sensitivity analysis, and most studies rely on a single model run despite stochasticity. — [Do LLMs Solve the Problems of Agent-Based Modeling? (arXiv 2504.03274, 2025, seen via search snippet only)](https://arxiv.org/pdf/2504.03274) [SEARCH-ONLY]
- Another cited paper reports GPT-4 cost of 5400 dollars for a four-player version of a generative-agent game; cost grows nonlinearly with number of agents. — snippet from search results of the same query, source paper not opened: [arXiv 2501.15355 (Theory-of-Mind generative agents) / 2403.18230](https://arxiv.org/pdf/2403.18230) [SEARCH-ONLY, attribution of the 5400-dollar figure to a specific paper not verified]

### Inferences
- For a two-character Discord bot, the most transferable parts are (a) importance-scored memories with recency decay, and (b) occasional, threshold-triggered reflection that writes a compact higher-level note. Daily hierarchical planning is built for embodied agents and is probably unnecessary for chat.
- The over-agreeableness and embellishment findings are directly relevant to a rules-answering bot: they argue for keeping rules facts in a retrieval source rather than in "character memory."
- The 1,000-people result suggests that a rich, first-person, written character document is the highest-leverage persona input; that is the fixed-character equivalent of an interview.

### Gaps
- No measurement of AI Town (a16z open-source reimplementation) cost or fidelity was found; I found only the original paper's claims. No peer-reviewed independent replication of the Generative Agents ablation was located.
- Exact per-agent token cost is not published in the paper; the only figure is "thousands of dollars."
- The 1,000-people paper's limitations section was not read (only the abstract page).

---

## 2. Memory architectures and benchmarks (MemGPT/Letta, Mem0, A-MEM, Zep/Graphiti, LoCoMo, LongMemEval)

### Takeaway
Retrieval-based memory greatly beats naive truncation, but on short benchmarks like LoCoMo (about 16-26k tokens) plain full-context prompting still scored highest on accuracy, so the main measurable win of memory layers is latency and token cost, not accuracy. LongMemEval, a harder benchmark, shows long-context models losing 30-60% accuracy at about 115k tokens and gives concrete design guidance (store rounds, index with extracted facts, time-aware retrieval); summarizing instead of keeping raw rounds generally hurt QA. Vendor claims are mutually contradictory and the benchmark itself has been criticized.

### Cited Findings
**MemGPT / Letta**
- MemGPT (Packer et al., Oct 2023, preprint; venue not shown on the page): "virtual context management" inspired by OS memory hierarchy; the LLM edits its own memory via function calls. Main context = read-only system instructions + read/write working context + FIFO message queue; external context = recall storage (full message DB) + archival storage. At about 70% of the context window a warning lets the model save information; at 100% a chunk (e.g. 50%) of messages is evicted and a recursive summary updated. `request_heartbeat` lets the model chain calls. — [arXiv 2310.08560](https://arxiv.org/abs/2310.08560), [HTML](https://arxiv.org/html/2310.08560)
- Deep Memory Retrieval accuracy, baseline to MemGPT: GPT-3.5 Turbo 38.7% to 66.9%; GPT-4 32.1% to 92.5%; GPT-4 Turbo 35.3% to 93.4%. — [arXiv 2310.08560 HTML](https://arxiv.org/html/2310.08560)
- Limitations from the paper's results discussion: much worse with GPT-3.5 due to weak function calling; document QA agent often stops paging before exhausting results; document QA evaluated on a sample of 50 questions. — [arXiv 2310.08560 HTML](https://arxiv.org/html/2310.08560)
- [VENDOR] Letta blog: a plain filesystem (grep/search/open tools) agent on gpt-4o-mini scored 74.0% on LoCoMo vs 68.5% that Mem0 reported for its graph variant; Letta concludes that the agent's skill at deciding when/how to search matters more than the retrieval mechanism and that LoCoMo may be a weak memory measure. Caveats stated by Letta itself: partially constrained tool rules, self-reported, Mem0's method unclear, not verifiable. — [Letta blog](https://www.letta.com/blog/benchmarking-ai-agent-memory)

**Mem0**
- Mem0 (Chhikara et al., Apr 2025, preprint [VENDOR-authored]): on LOCOMO, abstract claims 26% relative improvement in LLM-as-judge over OpenAI's memory, 91% lower p95 latency and more than 90% token cost savings vs full-context. — [arXiv 2504.19413](https://arxiv.org/abs/2504.19413)
- Overall J scores in that paper's table: full-context 72.90% (p95 latency 17.1 s, 26,031 tokens) was HIGHER than Mem0 66.88% (1.44 s, 1,764 tokens), Mem0g 68.44% (2.59 s, 3,616 tokens), Zep 65.99%, best RAG (k=2, 256-token chunks) 60.97%, A-Mem (re-run) 48.38%, LangMem 58.10% (p95 60.4 s), OpenAI memory 52.90%. Per-category Mem0: single-hop 67.13, multi-hop 51.15, open-domain 72.93, temporal 55.51. Mem0g did not improve single- or multi-hop and added latency and storage (graph memory about 14k tokens per conversation vs 7k for base). Only 10 conversations; adversarial category excluded; LLM judge. — [Mem0 paper HTML](https://arxiv.org/html/2504.19413)

**Zep / Graphiti**
- Zep (Rasmussen et al., Jan 2025, preprint [VENDOR-authored]): temporal knowledge graph. Abstract: DMR 94.8% vs MemGPT 93.4%; LongMemEval accuracy up to +18.5% and response latency reduced 90%. — [arXiv 2501.13956](https://arxiv.org/abs/2501.13956)
- [VENDOR] Zep rebuttal of Mem0's evaluation: Zep's corrected LoCoMo J = 75.14% (+/-0.17) vs Mem0 graph 68.44%; says Mem0 misconfigured Zep (user role on both speakers, timestamps in message text, sequential searches); says full-context at about 72.9% shows LoCoMo is too short (about 16-26k tokens); reports LongMemEval 71.2% vs 60.2% full-context (GPT-4o) and 63.8% vs 55.4% (GPT-4o-mini). — [Zep blog](https://www.getzep.com/blog/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/)
- Independent audit claims (secondary, blog-level, not verified by me): 99 score-corrupting errors in 1,540 LoCoMo questions (6.4%) and a judge that accepts many intentionally wrong answers; inability to reproduce published Mem0/Zep numbers. — [audit post on DEV](https://dev.to/penfieldlabs/we-audited-locomo-64-of-the-answer-key-is-wrong-and-the-judge-accepts-up-to-63-of-intentionally-33lg) [SEARCH-ONLY, low reliability]
- Mem0 now claims 91.6 on LoCoMo; I found it only on Mem0-sourced pages, no independent verification. — [Mem0 page](https://mem0.ai/library/agent-memory/how-to-read-memory-benchmarks) [SEARCH-ONLY, VENDOR]

**A-MEM**
- A-MEM (Xu et al., 2025; NeurIPS 2025 per the arXiv comments field): Zettelkasten-style notes with context description, keywords, tags; links created to similar historical notes; new memories can update older notes ("memory evolution"). Abstract claims superiority over baselines with no numbers on the page. — [arXiv 2502.12110](https://arxiv.org/abs/2502.12110)
- Counter-evidence: in Mem0's re-run, A-Mem scored 48.38% overall J (multi-hop 18.85) vs 66.88% for Mem0 — a competitor's evaluation, so not neutral. — [Mem0 paper HTML](https://arxiv.org/html/2504.19413)

**Benchmarks**
- LoCoMo (Maharana et al., Feb 2024; ACL 2024 per task brief, venue not shown on the page I fetched): very long dialogues averaging 300 turns / 9K tokens, up to 35 sessions, built with persona- and event-graph-grounded LLM agents then human-edited; tasks are QA, event summarization, multimodal dialogue generation. Finding: long-context LLMs and RAG help but models still "substantially lag behind human performance." — [arXiv 2402.17753](https://arxiv.org/abs/2402.17753)
- LongMemEval (Wu et al., Oct 2024; ICLR 2025 per arXiv comments): 500 questions, five abilities (information extraction, multi-session reasoning, temporal reasoning, knowledge updates, abstention). Commercial assistants and long-context LLMs show about 30% accuracy drop over sustained interactions. — [arXiv 2410.10813](https://arxiv.org/abs/2410.10813)
- LongMemEval details: on a 97-question short-history subset GPT-4o reading full history scored 0.918, ChatGPT (GPT-4o) 0.577, Coze 0.330. On LongMemEval_S (about 115k tokens), GPT-4o fell 0.870 to 0.606 (30.3%) and Llama 3.1 70B 0.744 to 0.334 (55.1%) relative to oracle evidence-only reading; Chain-of-Note did not prevent the drops. Splitting sessions into rounds improved QA; replacing rounds/sessions with summaries or extracted facts generally HURT QA (except multi-session reasoning where fact extraction helped). Fact-augmented key expansion: recall@k +9.4%, accuracy +5.4% on average (e.g. recall@5 0.582 to 0.644). Time-aware query expansion: +11.3% temporal recall (rounds), +6.8% (sessions), but needs a strong LLM (Llama 3.1 8B produced bad time ranges). Chain-of-Note plus structured JSON reading: up to about +10 points even with perfect retrieval. — [LongMemEval HTML](https://arxiv.org/html/2410.10813)

### Inferences
- Summary vs retrieval vs long context: evidence does not support "summarize everything" (LongMemEval: summaries/facts as stored values hurt QA) nor "stuff everything" (30-60% drop at about 115k tokens; also 17 s p95 latency and 26k tokens/query on LoCoMo). Best-supported hybrid: keep raw rounds, index them with LLM-extracted facts/keys, add timestamps, retrieve top-k, and read with a structured prompt. A Discord community history is far longer than LoCoMo, so the long-context-wins result likely does not transfer.
- A rolling summary (MemGPT-style recursive summary) is good for staying within budget but should not be the only store; keep raw messages retrievable.
- A graph layer (Mem0g, Zep) showed no accuracy gain on single/multi-hop in Mem0's own table and large storage (Zep over 600k tokens per conversation in Mem0's measurement); for a small community the cost-benefit is doubtful. This is an inference from vendor-affiliated numbers.

### Gaps
- Graphiti's own internals and Letta's sleep-time compute / memory-block measurements were not fetched.
- No neutral, independent head-to-head comparison of Mem0 vs Zep vs Letta was found; all numbers are vendor-run or vendor-contested. I could not verify Mem0's 91.6 or Zep's 80%+ claims.
- No benchmark found that tests multi-user community memory (many speakers, shared channel), which is the Discord use case; LoCoMo/LongMemEval are two-party.
- MemGPT's venue was not confirmed from the page.

---

## 3. Persona consistency and drift: measurement and mitigations

### Takeaway
Persona/instruction drift is measurable and appears within about 8 conversation turns in 2024-era models; it is correlated with falling attention to system-prompt tokens. Re-injecting the persona text periodically helps but never eliminates drift (2026 study: 22-38% slower decline for simple re-injection or reminders; 87% with an adaptive, behavior-specific correction written by a monitor LLM, exploratory). Activation-level methods (persona vectors, Assistant Axis capping) are real but need open-weight model access, which a hosted-API Discord bot lacks.

### Cited Findings
- Li et al., "Measuring and Controlling Persona Drift in Language Model Dialogs", 2024 (arXiv; v4 July 2024; COLM 2024 not confirmed on page): self-chat benchmark, two chatbots with different system prompts, 8 rounds, probe question each round scored 0-1 by a deterministic Python function; 100 hand-curated system prompts in 5 categories. LLaMA2-chat-70B stability declines steadily and the agent starts adopting the other LM's instruction; gpt-3.5-turbo-16k holds better but still about 10% drop. System-prompt attention drops sharply between turns (correlation, not proven cause). — [arXiv 2402.10962](https://arxiv.org/abs/2402.10962), [HTML](https://arxiv.org/html/2402.10962)
- Split-softmax (training-free attention rescaling toward system-prompt tokens) was compared against system prompt repetition (SPR) and classifier-free guidance (CFG) at equal MMLU degradation: split-softmax matches SPR's trade-off without using extra context and does better early, SPR better in later turns; CFG generalizes poorly to longer dialogues. All three methods cost some general capability. Tested on 20 ordered prompt pairs on LLaMA2-70B-chat. — [arXiv 2402.10962 HTML](https://arxiv.org/html/2402.10962)
- "Prompting Against Persona Drift: Comparing Intervention Timing and Content" (Sept 2026, preprint): 1,200 conversations, 28 turns, 4 models (Claude Sonnet 5, GPT-5.5, Qwen 3.6 35B, DeepSeek V4 Flash), persona = student with ADHD, drift measured by CAARS scale rated by four blind LLM judges (ICC 0.97 averaged). Reduction in post-checkpoint-2 decline rate vs control: static reinjection 35%, static reflective reminder 22%, adaptive reinjection 38%, adaptive reflective reminder 27%, adaptive behavior-specific instruction 87%. None eliminated drift; adaptive timing did not beat static schedule overall; full-persona reinjection beat reflective reminders only tentatively. Limitations: one scenario, same models as agent and judge, drift referenced to the model's own early behavior, no cost/naturalness assessment, the 87% result bundles several factors. — [arXiv 2609.24532 HTML](https://arxiv.org/html/2609.24532v1)
- ContextEcho (2026, preprint): persona-drift benchmark across 23 frontier models in very long agentic-coding sessions (three sessions of 3,746 to 9,716 turns); drift is general across organizations; in-session compaction does not reliably reset it; a single-shot anchor restored the trained register on measured targets. Domain is coding, so transfer to role-play is uncertain. — [arXiv 2605.24279](https://arxiv.org/abs/2605.24279)
- "The Assistant Axis" (Lu, Gallagher, Michala, Fish, Lindsey, Jan 2026, preprint, Anthropic-affiliated): leading axis of persona space measures how far a model is in default Assistant mode; deviations predict persona drift, often triggered by meta-reflection prompts or emotionally vulnerable users; restricting activations along the axis stabilizes behavior and resists persona-based jailbreaks. — [arXiv 2601.10387](https://arxiv.org/abs/2601.10387)
- Persona Vectors (Chen, Arditi, Sleight, Evans, Lindsey, Jul 2025, preprint, Anthropic-affiliated): trait directions (evil, sycophancy, hallucination) extracted from contrastive system prompts as difference of mean activations; finetuning-induced shift along the vector correlates r = 0.76-0.97 with later trait expression. Post-hoc subtraction reduces the trait but large coefficients lower MMLU; preventative steering during finetuning preserves capability better (multi-layer: no MMLU degradation vs regular finetuning); data-screening works but needs base-model responses for each training prompt. Only Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct tested; small question sets; imperfect LLM judge. — [arXiv 2507.21509](https://arxiv.org/abs/2507.21509), [HTML](https://arxiv.org/html/2507.21509)
- PERSIST / CORE (Sept 2026, preprint): separates single-turn evidence from revision of a persistent persona state with uncertainty-aware belief revision; reports gains on ALOE, PersonaChat, PERSIST and says explicit update control helps beyond better generation or persistent memory alone. Aimed at user-preference persona, not a fictional character's fixed persona. Specific numbers not on the abstract page. — [arXiv 2609.12373](https://arxiv.org/abs/2609.12373)
- Persona prompts do not make factual answers better: 162 roles x 2,410 factual questions x 4 LLM families; no overall improvement vs no persona; picking the best persona automatically was about as good as random (Findings of EMNLP 2024). — [arXiv 2311.10054](https://arxiv.org/abs/2311.10054)
- Attractor states (Ko and Geiping, June 2026, preprint): open-ended multi-turn LLM conversations settle into model-specific stable patterns; some models (e.g. Claude Haiku) pull partners toward their traits, some are malleable (GPT-4.1 nano). Relevant to two bots talking to each other. NOTE: a search summary incorrectly attributed "Assistant Axis" content to this paper; the fetched page does not mention it. — [arXiv 2606.30571](https://arxiv.org/abs/2606.30571)
- SPASM (2026, shared memory with per-agent rendered views lowered drift versus plain role-labeled transcripts, most clearly in emotional self-reports) — [arXiv 2604.09212](https://arxiv.org/html/2604.09212v1) [SEARCH-ONLY, not opened]

### Inferences
- A hosted-API Discord bot can use only prompt-level levers: periodic persona re-injection near the end of context (the most recent positions), keeping the system prompt short, and optionally a cheap monitor that writes a corrective instruction when a probe or classifier detects off-character output (the strongest effect in the 2026 study, but exploratory and with a second LLM call as cost).
- Re-injecting a compact persona block every N turns is the best-supported cheap mitigation; static schedules did about as well as adaptive timing in the 2026 study.
- Persona vectors / activation capping / split-softmax are not applicable without model weights.
- For a rules-answering character, a persona prompt should not be expected to improve rule accuracy (EMNLP 2024 result); it affects style only. Keep rules in retrieval.

### Gaps
- No study found that measures drift specifically in multi-user Discord-style chat or with a fixed fictional character over thousands of turns.
- COLM 2024 venue for the persona-drift paper not confirmed from the fetched page.
- Magnitude of "post-history instruction" / split-prompt placement (SillyTavern-style) effects: no peer-reviewed measurement found. ContextEcho's anchor and the 2026 reinjection study are the nearest evidence.
- Several 2026 preprints were read only at abstract or one-page level.

---

## 4. Role-play fidelity: Character-LLM, RoleLLM, ChatHaruhi, CharacterEval, character hallucination

### Takeaway
Early benchmarks mostly establish datasets and show that fine-tuning or retrieving character-specific material beats a plain prompt; character hallucination (out-of-persona or out-of-time knowledge) is mainly a compliance failure, not a recognition failure: models know a question is out of scope and answer anyway. Quantitative comparisons between prompting-only and fine-tuning are thin in what I could retrieve.

### Cited Findings
- Character-LLM (Shao et al., 2023, EMNLP 2023 "to appear"): fine-tunes models on profiles edited into character experiences; tests via interview playground to see whether the model memorizes character and experiences. Abstract gives no numbers. — [arXiv 2310.10158](https://arxiv.org/abs/2310.10158)
- RoleLLM (Oct 2023, preprint page; venue not shown): RoleBench with 168,093 samples over 100 roles; Context-Instruct extracts role-specific knowledge; RoleGPT (GPT-4 prompting) imitates style; role-conditioned instruction tuning produced RoleLLaMA (English) and RoleGLM (Chinese) which "approach" RoleGPT. — [arXiv 2310.00746](https://arxiv.org/abs/2310.00746)
- ChatHaruhi (2023, preprint): steers LLM with a refined prompt plus character memories extracted from show scripts; 32 Chinese/English characters, over 54k simulated dialogues; reports better automatic and human evaluation than baselines (no numbers on abstract; the abstract does not say retrieval is used, though the memory is extracted from scripts). — [arXiv 2308.09597](https://arxiv.org/abs/2308.09597)
- CharacterEval (Jan 2024, preprint): 1,785 multi-turn dialogues, 23,020 examples, 77 characters from Chinese novels/scripts; thirteen metrics across four dimensions; correlation with human judgment not reported on the abstract. — [arXiv 2401.01275](https://arxiv.org/abs/2401.01275)
- TimeChara (Ahn et al., Findings of ACL 2024): 10,895 instances testing point-in-time character hallucination; significant hallucination even in GPT-4o; proposed Narrative-Experts decomposes reasoning to reduce errors. Seen via search snippet. — [ACL Anthology 2024.findings-acl.197](https://preview.aclanthology.org/setup/2024.findings-acl.197), [arXiv 2405.18027](https://arxiv.org/abs/2405.18027v1) [SEARCH-ONLY for details]
- CHARM (Sept 2026, preprint): 40 real and fictional characters, five cultural-linguistic regions; tests Temporal and Cross-Universe knowledge boundaries with abstention allowed. Finding on six LLMs: hallucination is "driven predominantly by compliance failures"; models often say the question is out of scope and answer anyway ("verified parametric overrides"). Failure rates vary by culture. No mitigation tested. — [arXiv 2609.01352](https://arxiv.org/abs/2609.01352)
- Surveys: "From Persona to Personalization" (Chen et al., TMLR Oct 2024) three-part persona taxonomy — [arXiv 2404.18231](https://arxiv.org/html/2404.18231v1) (venue via search snippet); "Oscars of AI Theater" (Chen et al., v9 Jan 2025) — [arXiv 2407.11484](https://arxiv.org/abs/2407.11484v9); "Role-Playing Agents Driven by LLMs: Current Status, Challenges, and Future Trends" (Jan 2026, preprint): evolution from templates to style imitation to cognitive simulation (personality + memory), covers evaluation of role knowledge, personality fidelity, value alignment, interactive hallucination, and trade-offs of human, reward-model, and LLM-judge evaluation. — [arXiv 2601.10122](https://arxiv.org/abs/2601.10122)
- Role-play sycophancy: "Too Nice to Tell the Truth" (ACL 2026): 13 open-weight models (0.6B-20B), 275 personas; 9 of 13 models show significant positive correlation between persona agreeableness and sycophancy rate. — [ACL 2026 long.1421](https://preview.aclanthology.org/ingest-acl/2026.acl-long.1421/) [SEARCH-ONLY snippet]

### Inferences
- For fixed, well-specified characters, the evidence-backed no-fine-tuning levers are: a rich character profile, script/lore-derived memories retrieved on demand (ChatHaruhi style), and explicit out-of-knowledge refusal instructions. CHARM suggests the last one needs enforcement (e.g., a self-check pass or abstention format), since the model "knows" the boundary but does not comply.
- Because agreeable personas are more sycophantic, a warm character should be explicitly given disagreement behaviors, particularly when correcting rules mistakes.

### Gaps
- I did not retrieve numeric results from Character-LLM, RoleLLM, ChatHaruhi or CharacterEval, or any RPBench-type leaderboard; no figures for "prompt-only vs fine-tuned" were verified.
- Venue of RoleLLM, ChatHaruhi, CharacterEval not confirmed from fetched pages.
- No evidence found about which no-finetuning technique is best (few-shot dialogue examples vs profile vs retrieval) beyond the papers' own claims.

---

## 5. Proactivity and turn-taking in multi-party chat

### Takeaway
The best-documented mechanism is Inner Thoughts (Liu et al. 2025): a continuous covert thought stream, a 1-5 LLM-rated motivation score to speak, a silence-growth term, and threshold-based participation, which beat a next-speaker-prediction baseline on seven simulated metrics. Evidence is small-scale and simulation-heavy; ablations are explicitly future work. Related work (HUMA, 2025) shows an LLM facilitator can pass as human in group role-play chats, and AgentAbstain (2026) shows models are poor at knowing when not to act.

### Cited Findings
- Inner Thoughts (Liu, Fang, Shi, Wu, Igarashi, Chen, Jan 2025; arXiv page lists only preprint, CHI 2025 is not shown on it): AI maintains a covert thought stream and models its own motivation to speak. Five stages: (1) trigger on a new message or a 10-second pause; (2) memory retrieval with saliency > 0.3 and decay 0.95; (3) thought formation, System 1 and System 2 thoughts each under 15 words; (4) evaluation: LLM lists top 2 reasons for and against, then rates 1-5, score = probability-weighted sum over top-5 token logprobs, plus a silence factor growing 1.02 per timestep; (5) participation by turn type (open turn: intrinsic-motivation threshold; allocated turn: top thought; interruption: higher threshold). Heuristics distilled from a 24-participant think-aloud study: relevance, information gap, expected impact, urgency, coherence, originality, balance, dynamics. — [arXiv 2501.00383](https://arxiv.org/abs/2501.00383), [HTML](https://arxiv.org/html/2501.00383)
- Results: 100 simulated conversations (4 AI agents, 15 turns, 10 evaluators) significant wins on all seven metrics vs a fine-tuned GPT-3.5 next-speaker predictor with PersonaChat-style persona: turn appropriateness U=577.0 p=2.4e-6, coherence p=1.6e-5, intelligence p=7.3e-5, anthropomorphism p=2.4e-4, adaptability p=6.3e-3, engagement p=1.9e-3, initiative p=6.0e-3; evaluators preferred Inner Thoughts 82% of the time. In a 12-participant user study (Slack-bot "Swimmy", 3 AI personas) the active-contributor variant was most preferred (6 participants); the "selective" one was rated worst by 7; persona identification accuracy 69.23% / 54.55% / 50% vs 33.3% chance. Limitations stated: hyperparameters chosen empirically, formal ablations future work, simulated main evaluation, small single-institution user study. — [Inner Thoughts HTML](https://arxiv.org/html/2501.00383)
- Next-speaker prediction baseline best configuration accuracy 0.810 overall vs 0.127 random. — [Inner Thoughts HTML](https://arxiv.org/html/2501.00383)
- HUMA (Nov 2025, preprint): event-driven LLM community-manager agent with Router, Action Agent, Reflection component, simulated response delays, handles messages, replies and reactions; decides when to stay silent and whom to address. In a 97-participant, four-person role-play chat study participants identified community managers as human at near-chance rates for both AI and human managers; subjective ratings differed little. — [arXiv 2511.17315](https://arxiv.org/abs/2511.17315)
- MUCA (Microsoft Research, Jan 2024): decomposes group-chat assistant design into What / When / Who. — [arXiv 2401.04883](https://ar5iv.labs.arxiv.org/html/2401.04883) [SEARCH-ONLY]
- Addressee recognition: GPT-4o performed only marginally above chance on a multimodal multi-party benchmark where explicit addressees appear in about 20% of turns; it often labeled turns as addressed to nobody (Inoue et al., Jan 2025, preprint). — [arXiv 2501.16643](https://arxiv.org/pdf/2501.16643) [SEARCH-ONLY snippet]; text-only LLMs beat supervised models and humans at next-speaker prediction in meetings on AMI (2026) — [arXiv 2606.17542](https://arxiv.org/pdf/2606.17542) [SEARCH-ONLY snippet]
- AgentAbstain (July 2026, preprint): 263 paired should-act / should-abstain tasks, 17 frontier LLMs; best (Gemini 3.1 Pro) only 59.5% paired accuracy; abstention ability largely independent of task-solving ability; "post-hoc abstention" (irreversible action before recognizing reason to abstain). Tool-use setting, not chat, so transfer is analogical. — [arXiv 2607.10059](https://arxiv.org/abs/2607.10059)
- MM-When2Speak (2025): reframes timing as silence / short reaction / full response prediction; dyadic only — seen via search snippet [SEARCH-ONLY].

### Inferences
- "Silence" is best implemented as an explicit action class (no-reply / reaction / short / full) with a score threshold, plus a silence-accumulation term so a character occasionally speaks up after quiet periods (Inner Thoughts); HUMA's emoji reactions and typing delays are an inexpensive low-intrusion alternative to full replies.
- Cost: the Inner Thoughts loop runs an LLM thought-and-score call per trigger; for a small community, run it only on a short list of candidate triggers (new message from non-addressed context, long pause) and use a cheap model for scoring. This cost recommendation is an inference; the paper does not report cost.
- Given the 12-person study found the most-active variant preferred but the middle variant worst, too-hesitant behavior may be perceived worse than either extreme; cannot generalize from n=12.

### Gaps
- No large-scale or longitudinal deployment study of an LLM that initiates messages in a Discord/Slack community was found.
- Inner Thoughts cost, latency and ablations are not reported; Section 8.4 (limitations) of the paper was cut off in the text I could read (about 30k characters unread).
- No quantified evidence found on addressee detection for text-only LLMs in chat (the numbers above are from meetings/multimodal data).

---

## 6. Emotion / mood state, relationship tracking, and risks (sycophancy, dependence)

### Takeaway
Explicit appraisal-based emotion state improved some believability ratings in one small within-subject study (n=30, GPT-3.5), but effects were limited to 3 of the believability/EI items and the authors warn newer models may need it less. Evidence for relationship/affinity variables improving lifelikeness is thin in what I found; evidence of risks from heavy companion-style use is stronger and comes from a 4-week RCT and from RLHF sycophancy research.

### Cited Findings
- Chain-of-Emotion (Croissant et al., 2023/2024, preprint; PMC version suggests journal publication, not confirmed): each turn the LLM describes how the character feels and why, the description is stored as memory, and the reply is generated from log + emotions. 30 adults, within-subject, GPT-3.5-turbo temperature 0, three conditions (No Memory, Memory = full log, Chain-of-Emotion). Significant: "reactions were natural" CoE 5.71 vs 4.43 No Memory (p=.008) and 4.89 Memory (p=.05); "reacted to my input" 6.54 vs 5.43 (p=.02); "sensitive to others' feelings" 6.25 vs 5.14 (p=.01) and 5.39 (p=.04). Other believability, warmth and competence items not significant; LIWC tone lower for CoE. Limits: one model, short game, no retrieval, small university sample. — [arXiv 2309.05076 HTML](https://arxiv.org/html/2309.05076)
- MemEmo (Feb 2026, preprint): benchmark for emotion in agent memory systems (emotional extraction, updating, QA); authors report no evaluated system is robust across all three. — [arXiv 2602.23944](https://arxiv.org/abs/2602.23944) [SEARCH-ONLY snippet]
- Emotional RAG (retrieval conditioned on emotion): claimed improved personality consistency on three role-play datasets — only via PromptLayer summary, original not opened. — [PromptLayer summary](https://www.promptlayer.com/research-papers/boosting-ai-role-play-with-emotional-memory) [SEARCH-ONLY, low reliability]
- Sycophancy: Sharma et al., "Towards Understanding Sycophancy in Language Models", ICLR 2024: five RLHF-trained assistants show sycophancy across four free-form tasks; humans and preference models sometimes prefer convincing sycophantic answers over correct ones; optimizing against PMs can trade away truthfulness. — [arXiv 2310.13548](https://arxiv.org/pdf/2310.13548) (summary via search snippet)
- Persona-driven sycophancy: agreeableness of the persona predicts sycophancy in 9 of 13 small models (ACL 2026), see section 4. Persona vectors treat sycophancy as a measurable direction. — [Persona Vectors](https://arxiv.org/abs/2507.21509)
- Dependence: MIT Media Lab four-week randomized trial (March 2025 preprint; 981 participants, over 300,000 messages) varied interaction mode and conversation type: heavier daily use associated with more loneliness, emotional dependence, problematic use and less real-world socializing; voice-mode benefits faded at high usage; personal conversations slightly raised loneliness but lowered dependence; non-personal conversations were linked to more dependence among heavy users; users with stronger attachment tendencies fared worse. Correlational at the usage level; on average participants were less lonely after the study. Companion OpenAI analysis (nearly 40 million ChatGPT conversations plus survey of 4,076 users) is observational. Read via search summaries, not the paper itself. — [arXiv 2503.17473](https://arxiv.org/pdf/2503.17473), [commentary, Frontiers in Medicine 2025](https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2025.1612838/full) [SEARCH-ONLY]
- Persona drift is triggered more with emotionally vulnerable users in the Assistant Axis work. — [arXiv 2601.10387](https://arxiv.org/abs/2601.10387)
- Taxonomy for AI-companion personas stressing long-term emotional consistency (NeurIPS 2025 LLM Persona workshop, Sun and Wu) — [arXiv 2511.02979](https://arxiv.org/html/2511.02979) [SEARCH-ONLY]; ZifaMem (2026): structured memory for persona, preference, emotional continuity in companions — [arXiv 2607.17564](https://arxiv.org/pdf/2607.17564) [SEARCH-ONLY, contents not verified].

### Inferences
- A lightweight mood note written by an appraisal step and appended to memory is the only affect mechanism with a (small) human-rated benefit; the effect was on naturalness/responsiveness items rather than overall believability. A numeric mood vector or affinity score has no direct evidence in what I retrieved; treat as an unvalidated design choice.
- Given sycophancy and dependence evidence, an affinity/relationship variable should not be allowed to make a character endlessly agreeable; cap how much it changes factual or rules answers.

### Gaps
- No peer-reviewed study found that isolates "relationship/affinity tracking" or numeric mood variables and measures perceived lifelikeness.
- I did not read the MIT RCT or OpenAI companion paper directly; figures come from summaries and commentary.
- Chain-of-Emotion venue/peer-review status unconfirmed; it used GPT-3.5, so findings may not hold for current models.

---

## 7. Cognitive architecture framing and surveys

### Takeaway
CoALA (Sumers, Yao, Narasimhan, Griffiths) gives the standard vocabulary: modular memory, structured action space (internal memory actions vs external actions), generalized decision loop. 2024-2026 surveys on role-playing agents exist but I found no dedicated 2026 survey that unites autonomous characters, memory and companions.

### Cited Findings
- CoALA (Sept 2023, TMLR 2024 camera-ready, v3 March 2024) [PEER]: framework with modular memory components, a structured action space for internal memory and external environments, and a generalized decision-making process; used to survey existing agents and suggest directions. — [arXiv 2309.02427](https://arxiv.org/abs/2309.02427)
- Memory-mechanism survey for LLM agents (arXiv April 2024, ACM TOIS accepted 2025), covering conversational and role-playing uses — [arXiv/source via search](https://www.sourcepulse.org/projects/11031987) [SEARCH-ONLY, secondary listing]
- Role-playing surveys listed in section 4: Chen et al. 2024 (TMLR) taxonomy; Oscars of AI Theater (2024/2025); RPLA survey (Jan 2026) tracing personality plus memory as "cognitive simulation," with future directions in personality evolution over time, multi-agent collaborative storytelling, multimodal immersion. — [arXiv 2601.10122](https://arxiv.org/abs/2601.10122)
- Longitudinal studies of social AI companions (survey, International Journal of Human-Computer Interaction, reported July 2026) — [RC Trust summary](https://rc-trust.ai/news/news-detail/only-time-will-tell) [SEARCH-ONLY, not opened]
- Ethical considerations for AI assistants with long-term memory (Lee et al., 2024) — [arXiv 2409.11192](https://arxiv.org/pdf/2409.11192) [SEARCH-ONLY]

### Inferences
- Mapping the bot onto CoALA: working memory = prompt (persona block, recent chat, mood note); episodic memory = indexed chat history; semantic memory = rules corpus and lore; procedural = prompt/code; internal actions = retrieve/reflect/update-mood; external actions = reply / react / stay silent / initiate post. This mapping is my own inference.

### Gaps
- No 2026 survey specifically on autonomous characters plus companions was found; I did not locate a CoALA-informed review of Discord-style bots.

---

## 8. What the evidence says NOT to do (cost or instability without measured gain)

### Takeaway
The measured warnings are: do not rely on stuffing full history into context; do not replace raw history with summaries alone; do not assume graph memory beats vector retrieval for small corpora; do not expect persona prompts to improve factual accuracy; do not trust vendor memory leaderboards; do not run expensive always-on simulation loops; and beware over-agreeableness.

### Cited Findings
- Long context is not free: 30-60% accuracy drop at about 115k tokens (LongMemEval_S), and on LoCoMo full-context needed 17.1 s p95 and 26,031 tokens per query. — [LongMemEval HTML](https://arxiv.org/html/2410.10813), [Mem0 paper HTML](https://arxiv.org/html/2504.19413)
- Summaries or extracted facts as the stored value generally hurt QA vs raw rounds (except multi-session reasoning). — [LongMemEval HTML](https://arxiv.org/html/2410.10813)
- Graph memory (Mem0g) did not improve single/multi-hop J and added latency and storage; Zep's graph storage was over 600k tokens per conversation in Mem0's measurement (vendor-competitor figure). — [Mem0 paper HTML](https://arxiv.org/html/2504.19413)
- Persona prompts in the system prompt did not improve factual accuracy; automatic persona selection is no better than random. — [arXiv 2311.10054](https://arxiv.org/abs/2311.10054)
- Memory layers evaluated on LoCoMo cannot be trusted at face value: results contested between vendors, benchmark lacks knowledge-update questions and has ground-truth/attribution errors (Zep's critique); Letta suggests LoCoMo may not be meaningful. — [Zep blog](https://www.getzep.com/blog/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/), [Letta blog](https://www.letta.com/blog/benchmarking-ai-agent-memory)
- Weaker models fail at agent-managed memory: MemGPT with GPT-3.5 was much worse due to function-calling limits; MemGPT also stopped paging early. — [MemGPT HTML](https://arxiv.org/html/2310.08560)
- Generative Agents' full simulation is expensive ("thousands of dollars" for 25 agents over two days) and shows erratic behavior as memory grows. — [ar5iv HTML of 2304.03442](https://ar5iv.labs.arxiv.org/html/2304.03442)
- Drift mitigations carry costs: SPR consumes context window; split-softmax, CFG and SPR all reduced general capability at a calibrated budget (open model access needed). — [arXiv 2402.10962 HTML](https://arxiv.org/html/2402.10962)
- Compaction does not reset persona drift in very long sessions (ContextEcho). — [arXiv 2605.24279](https://arxiv.org/abs/2605.24279)
- Taking irreversible action before recognizing a reason to abstain is a documented failure ("post-hoc abstention"). — [arXiv 2607.10059](https://arxiv.org/abs/2607.10059)
- Chain-of-Emotion authors caution that newer models may reduce the benefit of appraisal prompting. — [arXiv 2309.05076 HTML](https://arxiv.org/html/2309.05076)

### Inferences
- A defensible minimal stack for a small community bot (inference, not a tested recommendation): raw message store indexed by embeddings with timestamps; retrieval scored by recency, importance and relevance; occasional reflection note written to the same store; persona block re-injected every N turns; a cheap pre-reply classifier that outputs reply / react / silent; rules answered from a separate retrieval source. Skip graph memory, daily planning loops and per-turn multi-call "inner thoughts" until cost and benefit are measured on your own logs.

### Gaps
- No study I found measures cost-vs-benefit for each component in a long-running, small-community chat deployment; ablations are mostly in simulated or benchmark settings.
- I could not confirm the effect of any "negative" mechanism outside the setups listed above.

---

## Reliability notes for the report writer
- Fetched and read (abstract or HTML): 2304.03442 (via ar5iv, first 100k of 144k chars), 2411.10109 (abstract), 2402.10962 (abstract plus HTML), 2501.00383 (abstract plus HTML, 30k chars unread), 2507.21509 (abstract plus first 100k of 222k chars), 2504.19413, 2501.13956 (abstract), 2410.10813 (abstract plus first 100k of 133k chars), 2402.17753 (abstract), 2310.08560, 2502.12110 (abstract), 2309.02427, 2401.01275, 2310.00746, 2308.09597, 2310.10158 (abstracts), 2309.05076, 2609.24532, 2606.30571, 2601.10387, 2601.10122, 2609.12373, 2609.01352, 2605.24279, 2511.17315, 2607.10059, 2311.10054, Zep blog, Letta blog.
- Items tagged [SEARCH-ONLY] come from search-engine summaries and were not opened; the search tool's summaries contained at least one misattribution (Assistant Axis credited to the attractor-states paper), so use those items cautiously.
- Several figures conflict: 1,000-people GSS accuracy (abstract page 86% for combined agents vs a snippet quoting 85%); Zep's LoCoMo score (65.99% in Mem0's paper vs 75.14% in Zep's blog). Both reported above without resolution.
