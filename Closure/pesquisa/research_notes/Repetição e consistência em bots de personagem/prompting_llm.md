# Prompt echo, negative instructions, multi-turn repetition and instruction placement in instruction-tuned LLMs

Scope: mechanisms and mitigations for a pt-BR persona Discord bot on Gemini Flash / Claude Haiku-class models. Research done 2026-10-13. Each claim carries a URL. Labels: **[tested]** = peer-reviewed or arXiv experimental work; **[vendor doc]** = official provider guidance (prescriptive, usually without published data); **[tech report]** = non-peer-reviewed vendor/company experiments; **[inference]** = my reasoning, not a source.

## Prompt echo / verbatim copying from the system prompt

### Takeaway
No paper I found measures "the model copies phrases from its system prompt" in persona chat directly, but the mechanism is well established: transformers have dedicated copy circuits (induction heads) that complete repeated token sequences from context, and both Anthropic and Google warn that examples and prompt style get imitated. The practical fix in vendor docs is to give diverse examples, match prompt style to the output you want, and explain the reason behind a rule instead of writing out a sample sentence.

### Cited Findings
- **[tested]** Induction heads are "attention heads that implement a simple algorithm to complete token sequences like [A][B] ... [A] -> [B]." Olsson et al. present them as a likely mechanism behind much in-context learning. Paper: "In-context Learning and Induction Heads" (Olsson, Elhage, Nanda, ... Olah; Anthropic; arXiv 2209.11895, 2022). — [arXiv](https://arxiv.org/abs/2209.11895)
- **[tested]** "Repetitions are not all alike: distinct mechanisms sustain repetition in language models" (Mahaut & Franzon, arXiv 2504.01100, 2025; rev. Nov 2025) finds that "ICL-induced repetition relies on a dedicated network of attention heads that progressively specialize over training." Repetition triggered by natural text works differently: it has no clear circuit and attends disproportionately to low-information tokens, which the authors read as a fallback when the model cannot retrieve relevant context. — [arXiv](https://arxiv.org/abs/2504.01100)
- **[vendor doc, Anthropic]** "Match your prompt style to the desired output. The formatting style used in your prompt may influence Claude's response style ... For example, removing markdown from your prompt can reduce the volume of markdown in the output." — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Anthropic]** Examples should be "Diverse: Cover edge cases and vary enough that Claude doesn't pick up unintended patterns." They should also be wrapped in `<example>` tags "so Claude can distinguish them from instructions". The doc recommends 3–5 examples. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Anthropic]** Explaining motivation generalizes better than a bare rule. The doc contrasts "NEVER use ellipses" with "Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them," and notes that "Claude is smart enough to generalize from the explanation." — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Anthropic]** For characters: "provide detailed information about the personality, background, and any specific traits or quirks. This helps the model better emulate and generalize the character's traits." It also says to "Provide a list of common scenarios and expected responses." — [Keep Claude in character](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/keep-claude-in-character)
- **[vendor doc, Google]** "Use specific and varied examples"; "if you include too many examples, the model may start to overfit the response to the examples." Google also asks that example formatting be consistent. — [Gemini API prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- **[tested, adjacent]** The model's preference for continuing what is already in its context is the basis of the "self-reinforcement" finding (see the multi-turn section). — [arXiv 2206.02369](https://arxiv.org/abs/2206.02369)

### Inferences
- **[inference]** A catchphrase, an odd word order or a quoted line in the system prompt ("ela fala tipo 'ué, sério?'") is a ready-made [A][B] sequence. Once the conversation produces [A] again, the copy circuit makes [B] likely. Quoted sample lines are the most copyable thing in a persona prompt.
- **[inference]** Ways to describe a behavior without handing over a phrase:
  - Describe the function and the reason instead of the surface form. For example, "she shortens replies when she is irritated, because she thinks the person is wasting her time" works better than a sample irritated line.
  - Give several varied examples clearly labeled as illustrations. Tag them, and say that they show tone, not text to reuse.
  - Avoid rare lexical items you don't want reused. Rare tokens are the most salient copy targets.
  - Write the prompt in the register you want back. Per "match prompt style", a prompt written in formal pt-BR with markdown headings pulls the output toward formal, markdown-heavy text.
- **[inference]** If an example must appear, several examples with different wording for the same function dilute any single phrase. That is what "diverse" in the Anthropic doc protects against.

### Gaps
- I found no controlled study measuring verbatim reuse rates of system-prompt phrases in chat outputs for Claude, Gemini or GPT. The evidence is mechanistic plus vendor guidance.
- I found no vendor doc that explicitly says "the model will copy quoted phrases from the system prompt". That remains practitioner lore.

## Negative instructions and "pink elephant" priming

### Takeaway
Tested evidence shows that LMs handle negated instructions poorly, and older work found that bigger models did worse ("inverse scaling"). Naming the forbidden thing primes it, enough that a dedicated fine-tuning method was built to suppress it. Both Anthropic and Google advise positive phrasing, or a stated reason, over bare prohibitions. Google also says broad negatives can make Gemini 3 over-index on them, and that negative constraints should go at the end of the prompt.

### Cited Findings
- **[tested]** "Can Large Language Models Truly Understand Prompts? A Case Study with Negated Prompts" (Jang, Ye, Seo; arXiv 2209.12711, 2022). The usual scaling law "does not hold when evaluating large LMs on tasks with negated prompts." Instead the authors find "an inverse scaling law" across 9 negated-prompt tasks. This held for pretrained models, InstructGPT and models fine-tuned on negated prompts, and all of them fell far below human performance. — [arXiv](https://arxiv.org/abs/2209.12711)
- **[tested]** "Inverse Scaling: When Bigger Isn't Better" (McKenzie et al., arXiv 2306.09479, 2023) collects inverse-scaling tasks, including negation-based ones (NeQA). — [arXiv PDF](https://arxiv.org/pdf/2306.09479)
- **[tested]** "Beyond Positive Scaling: How Negation Impacts Scaling Trends of Language Models" (Findings of ACL 2023) is the NeQA dataset paper. — [ACL Anthology](https://preview.aclanthology.org/setup/2023.findings-acl.472); [project site](https://sites.google.com/view/neqa)
- **[tested]** "Suppressing Pink Elephants with Direct Principle Feedback" (Castricato, Lile, Anand, Schoelkopf, Verma, Biderman; arXiv 2402.07896, 2024) frames "don't mention X" as a hard control problem. After DPF fine-tuning, a 13B LLaMA-2 "significantly outperforms Llama-2-13B-Chat and a prompted baseline" on avoiding the forbidden entity, so plain prompting was the weaker baseline. — [arXiv](https://arxiv.org/abs/2402.07896)
- **[vendor doc, Anthropic]** "Tell Claude what to do instead of what not to do. Instead of: 'Do not use markdown in your response'. Try: 'Your response should be composed of smoothly flowing prose paragraphs.'" — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Anthropic]** On newer Claude models, the doc says to "dial back any aggressive language": instead of "CRITICAL: You MUST use this tool when...", "use more normal prompting like 'Use this tool when...'". These models are "more responsive to the system prompt" and may overtrigger. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Google]** Open-ended negatives such as "do not infer" can make Gemini 3 "over-index on that instruction and fail to perform basic logic or arithmetic." The guide suggests saying what to use instead ("use the provided additional information"). It also says to put negative constraints at the end of the prompt, since the model may otherwise drop them. — [Vertex AI Gemini 3 prompting guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide)
- **[vendor doc, Google]** The general Gemini API guide still says "You can tell the model what to do and not to do". It does not forbid negatives outright. — [Gemini API prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- **[note]** Older versions of Google's prompt guide said that showing a pattern to follow beats showing an antipattern to avoid. When I fetched the current page (Oct 2026), that text was not there, so I cannot cite it as current. — [Gemini API prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)

### Inferences
- **[inference]** For a persona bot, "nunca diga 'kkkk'" or "não fale de X" puts the exact token in context, where the copy mechanism above can pick it up. Better to state the target behavior positively ("ri com palavras ou não ri"), or remove the trigger word entirely if it isn't needed.
- **[inference]** Where a prohibition is unavoidable, Google's guidance suggests three things: keep it narrow, give the alternative behavior and the reason, and place it at the end of the system instruction or near the latest turn. Avoid ALL-CAPS escalation, which Anthropic warns causes overtriggering on modern Claude.
- **[inference]** Note the tension: Google says to put negative constraints at the end, while Anthropic says to prefer positive framing. The two are compatible: write the rule positively and place it late.

### Gaps
- The negation-scaling studies (2022–2023) predate current RLHF'd chat models. I found no 2025–2026 benchmark that quantifies how well Claude Haiku 4.x or Gemini Flash 2.5/3 follow negative versus positive instructions.
- I found no published study of whether naming a banned phrase in the system prompt raises its output frequency in chat models (the pink-elephant effect under prompting alone). DPF only shows that prompting is a weak baseline.

## Repetition in multi-turn chat (self-reinforcing style)

### Takeaway
Repetition is self-reinforcing. The more a sentence already appears in context, the likelier it is to be produced again, and the model's own earlier turns count as context. Mitigations: keep the history window short, summarize old turns, avoid identical examples, and use sampling penalties where they exist. Gemini exposes presence and frequency penalties. Claude's API has none, and newer Claude models don't let you change the sampling settings at all.

### Cited Findings
- **[tested]** "Learning to Break the Loop: Analyzing and Mitigating Repetitions for Neural Text Generation" (Xu, Liu, Yan, Cai, Li, Li; arXiv 2206.02369, NeurIPS 2022). "Language models have a preference to repeat the previous sentence." There is a **self-reinforcement effect**: "the more times a sentence is repeated in the context, the higher the probability of continuing to generate that sentence." Also, "sentences with higher initial probabilities usually have a stronger self-reinforcement effect." The proposed fix (DITTO) is a training method, not a prompting one. — [arXiv](https://arxiv.org/abs/2206.02369)
- **[tested]** "Repetition In Repetition Out: Towards Understanding Neural Text Degeneration from the Data Perspective" (arXiv 2310.10226, NeurIPS 2023) links degeneration to repetition in the training data. — [arXiv PDF](https://arxiv.org/pdf/2310.10226)
- **[tested]** Mahaut & Franzon (2025) separate repetition learned from in-context examples, which has its own circuit, from "natural" repetition. Natural repetition fixates on low-information tokens when the model can't find relevant context. — [arXiv 2504.01100](https://arxiv.org/abs/2504.01100)
- **[tested]** "Measuring and Controlling Instruction (In)Stability in Language Model Dialogs" (Li, Liu, Bashkansky, Bau, Viégas, Pfister, Wattenberg; arXiv 2402.10962, COLM 2024) finds "a significant instruction drift within eight rounds of conversations" (LLaMA2-chat-70B, GPT-3.5, in self-chat). The authors tie the drift to attention decay over long exchanges and propose split-softmax as a mitigation. — [arXiv](https://arxiv.org/abs/2402.10962)
- **[vendor doc, Google]** For Gemini 3, "we strongly recommend keeping the temperature parameter at its default value of 1.0". Setting it below 1.0 "can cause unexpected behavior, such as looping or degraded performance." Lowering temperature to "stabilize" a persona can therefore increase repetition on Gemini 3. — [Vertex Gemini 3 guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide); [Gemini API prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- **[API doc, Google]** The Gemini `GenerationConfig` has `presence_penalty` ("Positive values penalize tokens that already appear in the generated text") and `frequency_penalty` ("Positive values penalize tokens that repeatedly appear in the generated text"). The Vertex type gives a range of [-2.0, 2.0]. — [google-genai SDK types.py](https://github.com/googleapis/python-genai/blob/main/google/genai/types.py)
- **[API doc, Anthropic]** The Claude Messages API has no frequency or presence penalty parameter; a search of the create-message reference found zero "penalty" fields. For `temperature`: "Models released after Claude Opus 4.6 do not support setting temperature. A value of 1.0 will be accepted for backwards compatibility, all other values will be rejected." `top_p` and `top_k` are likewise deprecated for those models. The default is 1.0 and the range is 0–1. — [Claude Messages API: create](https://platform.claude.com/docs/en/api/messages/create)
- **[vendor doc, Anthropic]** Diverse examples keep the model from picking up "unintended patterns" (cited above). — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Inferences
- **[inference]** In a Discord bot, every prior bot reply in history is in-context evidence of "how this character talks". If replies 1–3 open with the same interjection, the self-reinforcement result predicts reply 4 will too. This is the main source of the "personagem com tique" effect, more than the system prompt itself.
- **[inference]** Mitigations, ordered by expected leverage:
  1. Limit the raw history window to the last N exchanges and replace older turns with a neutral third-person summary. A summary strips the surface wording, so the old phrases are no longer there to copy.
  2. Optionally post-process stored bot turns before re-sending: detect repeated openers or n-grams across the last k bot replies, then either inject a short note near the latest turn naming the habit to vary, or regenerate.
  3. Vary the examples, or rotate a subset per request.
  4. On Gemini, try a modest `presence_penalty` or `frequency_penalty` and keep temperature at 1.0.
  5. On Claude, sampling cannot fix this, so it has to be handled through the prompt and the history.
- **[inference]** Gemini's penalties are documented against "the generated text". That likely means only the current response, so they would not stop the model reusing a phrase from an earlier turn. This is not confirmed (see Gaps).

### Gaps
- It is unclear whether Gemini's presence and frequency penalties count tokens from the prompt and history or only the current response. I also could not confirm which Gemini models (2.5 Flash, 3 Flash) accept them; developer forums report 400 errors on some models, but I did not verify this.
- I found no paper that quantifies cross-turn self-copying of style (as opposed to within-generation loops) in production chat models, or that compares summarizing against truncating history for repetition.

## Topic persistence, re-asking, and effects of long system prompts and per-turn reminders

### Takeaway
Tested work shows that LLMs degrade markedly in multi-turn settings: they lock onto early assumptions and fail to recover, and instruction adherence drifts within about eight turns. This explains bots that return to earlier topics or anchor on stale context. Vendor guidance favors a strong system prompt plus prepared scenarios. A non-peer-reviewed report shows that more input tokens and more distractors degrade performance, which argues for compact prompts.

### Cited Findings
- **[tested]** "LLMs Get Lost In Multi-Turn Conversation" (Laban, Hayashi, Zhou, Neville; arXiv 2505.06120, 2025). Top open- and closed-weight LLMs show "an average drop of 39% across six generation tasks" in multi-turn versus single-turn settings, across "200,000+ simulated conversations." The drop is "a minor loss in aptitude and a significant increase in unreliability." The paper also reports (body, not abstract) that models make early assumptions and over-rely on their own earlier answers. — [arXiv](https://arxiv.org/abs/2505.06120)
- **[tested]** Li et al. (2024): instruction drift within eight rounds, attributed to attention decay toward the system prompt as the dialog grows. — [arXiv 2402.10962](https://arxiv.org/abs/2402.10962)
- **[tech report]** "Context Rot: How Increasing Input Tokens Impacts LLM Performance" (Hong, Troynikov, Huber; Chroma, July 14 2025; not peer reviewed). Covers 18 LLMs, including GPT-4.1, Claude 4, Gemini 2.5 and Qwen3. "Across all experiments, model performance consistently degrades with increasing input length," and "even a single distractor reduces performance relative to the baseline." — [Chroma research](https://www.trychroma.com/research/context-rot)
- **[vendor doc, Google]** The Gemini 3 model "will sometimes ignore instructions in order to maintain adherence to the described persona". Google advises reviewing the persona and avoiding ambiguous situations. — [Vertex Gemini 3 guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide)
- **[vendor doc, Google]** Gemini 3 is "less verbose" by default; for a chattier style "you must explicitly steer the model to be chattier." — [Vertex Gemini 3 guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide)
- **[vendor doc, Anthropic]** Keeping a consistent character "requires deliberate prompting". Use the system prompt for role and personality, and "Prepare Claude for possible scenarios". The page has no per-turn reminder guidance, and prefill "is not supported on Claude 4.6 and later models." — [Keep Claude in character](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/keep-claude-in-character)

### Inferences
- **[inference]** Re-asking and returning to earlier topics fit Laban et al.'s "over-rely on early turns" finding together with self-reinforcement: an earlier topic that stays in the window keeps attracting attention. Dropping or summarizing resolved threads should reduce it.
- **[inference]** A short reminder injected near the latest turn counters attention decay (Li et al.) and the end-position advantage (see next section). But if the reminder is identical every turn, it becomes another repeated string that the model may echo. Keep it short, keep it about behavior (not sample phrases), and possibly vary or rotate it.
- **[inference]** A long persona prompt full of lore is "distractor" mass in the Context Rot sense. For Flash/Haiku-class models, keep the always-on persona core compact and move lore into retrieval or conditional injection.

### Gaps
- I found no controlled study isolating the effect of per-turn injected reminders on persona consistency or repetition for Claude or Gemini.
- Laban et al. and Li et al. did not test Claude Haiku or Gemini Flash specifically, according to the abstracts I read.

## Instruction placement (system vs last user turn) and long-context degradation for small models

### Takeaway
Tested work (Lost in the Middle) shows that models use information at the start and end of the context best and the middle worst. Both vendors say to put long material first and the instructions or query last. Google adds that critical restrictions should be the final line. The persona itself belongs in the system instruction.

### Cited Findings
- **[tested]** "Lost in the Middle: How Language Models Use Long Contexts" (Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang; arXiv 2307.03172; TACL 2024). "Performance can degrade significantly when changing the position of relevant information." It is best at the beginning or end and worst in the middle, "even for explicitly long-context models." — [arXiv](https://arxiv.org/abs/2307.03172)
- **[vendor doc, Anthropic]** For inputs of 20k tokens or more, "Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples." "Queries at the end can improve response quality by up to 30 percent in tests, especially with complex, multidocument inputs." Anthropic's internal tests are unpublished. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Anthropic]** "Setting a role in the system prompt focuses Claude's behavior and tone for your use case. Even a single sentence makes a difference." — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[vendor doc, Google]** "Place essential behavioral constraints, role definitions (persona), and output format requirements in the System Instruction or at the very beginning of the user prompt." Also: "When providing large amounts of context ... supply all the context first ... Place your specific instructions or questions at the very end of the prompt." — [Gemini API prompting strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- **[vendor doc, Google]** For Gemini 3, "place your core request and most critical restrictions as the final line of your instruction." Negative constraints placed early may be dropped. — [Vertex Gemini 3 guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide)
- **[tech report]** Performance degrades as input length grows, across all 18 models tested. — [Chroma Context Rot](https://www.trychroma.com/research/context-rot)

### Inferences
- **[inference]** Recommended layout for a Discord persona bot:
  1. The system instruction holds the stable persona core: who the character is, what they want and how they react, written in the target register.
  2. Then summarized memory or lore.
  3. Then a short window of recent turns.
  4. Then, attached to the latest user turn or as the last system note, a 1–3 line positive behavioral reminder, plus any current-turn constraint.

  This uses both the primacy position (persona) and the recency position (reminder), and keeps important material out of the middle.
- **[inference]** Flash/Haiku-class models are more exposed to long-context degradation than frontier models. Lost in the Middle and Context Rot both show degradation even in strong models, so a lean context is the safer default. No source quantified the small-vs-large gap for current models.

### Gaps
- I found no published head-to-head comparison of placing the same instruction in the system field versus the final user turn for Claude Haiku 4.x or Gemini Flash.
- Anthropic's "up to 30%" figure comes from internal, unpublished tests.
