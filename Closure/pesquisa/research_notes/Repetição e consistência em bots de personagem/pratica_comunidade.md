# Community practice for role-play character cards: repetition, catchphrases, parroting, old topics

Research date: 2026-10-13. Method note: reddit.com was blocked from the fetch tool, so no r/SillyTavernAI or r/CharacterAI threads could be read directly (one Reddit mirror snapshot was checked and turned out to be off-topic). Sources used: SillyTavern docs, rentry guides (Ali:Chat, kingbri MinimALIstic, OAI cards), sampler pull requests on GitHub (DRY, XTC) with their review threads, Anthropic's prompting docs, and a few 2026 practitioner blogs (Arcanum RPGs, WeavAI). WeavAI is promotional and Arcanum reports no data. Evidence labels used below: **[doc]** official documentation, **[opinion]** practitioner opinion with no test, **[anecdotal test]** informal demo or personal trial, **[untested by author]** the source itself says the claim is untested.

## 1. Card formats (prose, Ali:Chat, PList, W++, JSON) and what they do to repetition and verbatim copying

### Takeaway
None of the sources tested format against repetition in a controlled way. The community consensus (opinion) is that the model imitates what it is shown. Dialogue-style cards (Ali:Chat) give strong voice but carry a "leak" risk: example lines come back verbatim. Bracketed or pseudo-code formats (W++, JSON) mainly cost extra tokens. The defensible pattern is a compact trait list (PList) plus a few varied dialogue examples, and prose in the greeting and examples rather than in the description.

### Cited Findings
- **[doc]** SillyTavern says the description "can be any length and formatted in any style (free text, pseudo-code conversation style, etc.)" and sends readers to community guides (Trappu's PLists + Ali:Chat, AliCat's Ali:Chat, kingbri's minimalistic guide) for format choice. The docs take no position on which format is best. — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- **[doc]** The description is always sent, so "all important facts should be included here". In a 2048-token context, "a 1000-token character definition cuts the AI's 'memory' in half". — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- **[opinion]** Ali:Chat's core principle is "using dialogue as the formatting to express and reinforce traits". Its rule of thumb: "What you put in, is what you get out." — [Ali:Chat v1.5](https://rentry.co/alichat)
- **[opinion/anecdotal]** Ali:Chat admits verbatim leakage: "The bot's answers can occasionally 'leak' (quoted verbatim)". This can give accurate in-character speech but can also drag along unwanted environment details. Its proposed fix (square brackets) is explicitly untested ("I need to test this one more"). — [Ali:Chat v1.5](https://rentry.co/alichat)
- **[opinion]** Ali:Chat claims "There is high accuracy (generally) when your conversation overlaps the dialogue examples", and that example lines act as keys (a user action matching an example triggers the matching reaction). This is also the mechanism behind verbatim recall. — [Ali:Chat v1.5](https://rentry.co/alichat)
- **[opinion]** Recommended hybrid: put a PList on the first line of the Description followed by `<START>`, then dialogue that reinforces those traits. A PList in the Author's Note at about depth 4 "will have a much stronger effect". — [Ali:Chat v1.5](https://rentry.co/alichat)
- **[opinion]** kingbri: group traits into a single PList with semicolon-separated sections rather than many arrays. Use a full label such as "Character's persona" because a bare "Character:" "might make some models confused". Remove legacy separators ("dinkuses"). — [MinimALIstic (Ali:Chat Lite)](https://rentry.co/kingbri-chara-guide)
- **[anecdotal]** kingbri reports converting one card from about 1300 to 599 tokens with this format, and targets under 600 permanent tokens. — [MinimALIstic](https://rentry.co/kingbri-chara-guide)
- **[anecdotal test]** OAI-cards guide (April 2023, GPT-3.5/4 era, self-described subjective): "W++ is a made up pseudo code". `Appearance=("Tall" + "Short hair" + "Big breasts")` counts 15 tokens against 11 for the same thing in prose. The author argues the bigger problem is excess information, not syntax. — [OAI models and character creation](https://rentry.co/oaicards)
- **[opinion]** Same guide: "Using a long AI generated prose as your description is just as bad, if not worse." "The prose goes in example dialogue and the greeting." "Avoid repeating points": restating a trait across several examples biases the bot toward it. — [rentry.co/oaicards](https://rentry.co/oaicards)
- **[opinion]** Concrete behaviour beats adjective labels. Arcanum gives "Interrupts when excited" over "enthusiastic". WeavAI argues an adjective-only personality gives the model little to imitate, so it "runs out of phrasings and goes in circles". — [Arcanum, Jun 2026](https://arcanumrpgs.com/blog/how-to-write-a-character-card/); [WeavAI, Aug 2026](https://weavai.app/blog/en/2026/08/30/ai-roleplay-guide-show-dont-tell-catchphrases/)
- **[doc, Anthropic]** For Claude: "The formatting style used in your prompt may influence Claude's response style... removing markdown from your prompt can reduce the volume of markdown in the output." By implication, the card's surface form bleeds into the output. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[community bug report]** If `{{char}}` appears in a card whose title differs from the character's name, SillyTavern substitutes the card title for the name. Suggested fixes: name the card after the character or remove the macro. — [r/SillyTavernAI thread via mirror](https://reddit.sentinel-team.org/posts/1ravlnf/snapshots/2026-02-27T16%3A12%3A57.42274Z)

### Inferences
- Verbatim copying is mostly a function of how much literal, quotable dialogue sits in permanent context and how distinctive it is. Ali:Chat in the Description (permanent) maximizes that. Example dialogues in mes_example (temporary, pushed out later) reduce it over time.
- Applying Anthropic's "match prompt style to output" to cards: a description written in the character's own voice will be echoed in voice, while a neutral trait list is less likely to be quoted back verbatim.
- W++ and JSON are disfavoured mainly for token cost and because modern instruct/API models do not need them. No source showed they reduce or increase repetition.

### Gaps
- No controlled A/B test of format against repetition rate or verbatim-copy rate was found. Reddit threads with such tests could not be accessed (site blocked).
- JED and JSON-specific guidance and Risu/Agnai format docs were not reached.
- Trappu's PLists + Ali:Chat guide (rentry.co/plists_alichat_avakson) returned only a content-warning interstitial, so its content is unverified here.

## 2. Example dialogues (mes_example): count, variety, catchphrase loops, leakage

### Takeaway
Practitioners recommend few (2–3, or 3–5 per Anthropic) short, deliberately varied examples covering different situations, without repeated verbs or gestures, because "the AI likes to create patterns." Repeated actions or phrases across examples are the most commonly cited source of catchphrase and gesture loops. Examples also outweigh the description when the two conflict.

### Cited Findings
- **[doc]** Each example block starts with `<START>`. Blocks are inserted only when the context has free space and are removed one at a time as history grows ("only kept until chat history fills up the context"), with an option to force them to stay. — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- **[doc]** "The model is more likely to pick up the style and length constraints from the first message than anything else." — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- **[opinion]** kingbri: 3 short examples of 5–6 lines each (or 2 long ones of 7–8 lines), totalling 300–600 tokens. "Repeating actions will cause a bias when talking to a character". "more variation in example chats leads to more variation in RP". Over-reinforcing the name can push the model into third person. — [MinimALIstic](https://rentry.co/kingbri-chara-guide)
- **[opinion]** Ali:Chat: "the AI likes to create patterns". It warns against overlapping verbs across examples (e.g. "smiling") and says to keep examples open-ended and minimal. — [Ali:Chat v1.5](https://rentry.co/alichat)
- **[opinion]** OAI cards: too many examples push the description back in memory. Never put `{{user}}` lines or actions inside `{{char}}:` messages, because the bot learns to speak for the user. "Plain dialogue-only example chats will give you a lot more dialogue in the replies." — [rentry.co/oaicards](https://rentry.co/oaicards)
- **[opinion]** Arcanum (2026): 2–3 short exchanges covering range (an ordinary moment, a high-stakes or emotional one, a hard-limit refusal). "the examples win when they conflict with the description, so make them agree". If the voice is off, add example dialogue before rewriting the personality. — [Arcanum](https://arcanumrpgs.com/blog/how-to-write-a-character-card/)
- **[opinion, promotional source]** WeavAI: a single catchphrase repeated across replies causes looping. Instead, give a "linguistic fingerprint": speech endings, 3–4 rotating metaphors, and words the character never uses. Several dialogue sets for different scenarios beat many lines with the same meaning. No outcome data. — [WeavAI](https://weavai.app/blog/en/2026/08/30/ai-roleplay-guide-show-dont-tell-catchphrases/)
- **[doc, Anthropic]** "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure." Make them "Diverse: Cover edge cases and vary enough that Claude doesn't pick up unintended patterns", wrap them in `<example>` tags so they are distinguished from instructions, and use 3–5. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[anecdotal]** Ali:Chat names "leaking" (verbatim quoting of examples) as a known effect, both good and bad. — [Ali:Chat v1.5](https://rentry.co/alichat)

### Inferences
- A catchphrase that appears in two or more examples is effectively a few-shot instruction to say it every turn. The fix is variety, or none at all: describe the tic's frequency in prose ("rarely, only when…") rather than demonstrating it repeatedly.
- Wrapping examples in labelled tags, as Anthropic recommends for Claude, is the API-model analogue of `<START>` separators and should reduce examples being mistaken for chat history.

### Gaps
- No quantitative data on leakage rate versus number of examples.
- SillyTavern's "Example Messages Behavior" options (keep, gradually push out, always include) are not documented on the pages fetched. Only the "force them to stay" option is confirmed.

## 3. Negative instructions ("don't say X") and quoted phrases

### Takeaway
Guides consistently advise phrasing positively, describing what to do instead. Anthropic's own docs recommend the same for Claude, plus giving the reason behind a rule. The "pink elephant" priming claim (quoting a banned phrase makes it more likely) is widely repeated but was not backed by any test found here. One 2026 practitioner guide argues the opposite for hard limits (explicit prohibitions work), and one 2023 guide notes that GPT-class models handle negatives better than older local models.

### Cited Findings
- **[opinion]** "Try to avoid negative prompts as much as possible", though "OAI models seem to handle negative prompts much better". The guide quotes a forum suggestion to phrase as a state ("IS unable to contact") rather than "doesn't/can't". — [rentry.co/oaicards](https://rentry.co/oaicards)
- **[doc, Anthropic]** "Tell Claude what to do instead of what not to do", with the example: instead of "Do not use markdown", say "Your response should be composed of smoothly flowing prose paragraphs." — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[doc, Anthropic]** Give context or motivation for rules: "NEVER use ellipses" is weaker than explaining the text goes to a TTS engine. "Claude is smart enough to generalize from the explanation." — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- **[opinion, conflicting]** Arcanum: "Models follow concrete prohibitions far better than they infer them". State hard limits explicitly. No data. — [Arcanum](https://arcanumrpgs.com/blog/how-to-write-a-character-card/)
- **[anecdotal]** The DRY author states that prompting the model to avoid looping "has little effect" compared with sampling-level fixes (local-model context). — [DRY PR #5677](https://github.com/oobabooga/text-generation-webui/pull/5677)

### Inferences
- The two positions reconcile: prohibitions on *behaviours* ("never speaks for {{user}}") are fine, while prohibitions that *quote a specific phrase* put that exact token sequence into context, which few-shot and recency dynamics can amplify. The safer form names the category and the replacement ("vary greetings; open with an action relevant to the scene").
- For banning literal strings, sampling-side tools (DRY sequence matching, or backend banned-token lists where available) avoid putting the phrase into the prompt at all.

### Gaps
- No A/B test was found that measures whether quoting a banned phrase increases its frequency on current models. Reddit threads reportedly discussing this were inaccessible.
- SillyTavern/KoboldCpp "banned strings / anti-slop" features were not verified from docs in this pass.

## 4. Post-history instructions, Author's Note, depth-injected reminders

### Takeaway
Text near the end of the prompt has the strongest effect. Post-History Instructions (sent last) and in-chat Author's Notes or Character's Notes at shallow depth (0–4) are where practitioners put formatting, length and anti-repetition reminders, and sometimes a compact trait PList. Frequency is configurable: every turn, or every Nth user input.

### Cited Findings
- **[doc]** Post-History Instructions are sent after the main prompt and the user's message, so the AI sees them last and "usually" gives them higher priority than the Main Prompt. In Chat Completion they go last with the system role, falling back to user if the API lacks a system role. Per-character PHI exist ("Prefer Char. Instructions", with the `{{original}}` macro to keep the global one). — [SillyTavern Prompts](https://docs.sillytavern.app/usage/prompts/)
- **[doc]** In an existing chat, Main Prompt edits have limited effect "because message history sets the style". The docs suggest inserting instructions near the end of history (e.g. Author's Note), testing in a new chat, or editing history. — [SillyTavern Prompts](https://docs.sillytavern.app/usage/prompts/)
- **[doc]** Author's Note position is "After Scenario" or "In-chat at depth N". Depth 0 is the very end of history, and depth 4 sits before the last three messages. Frequency 1 means every user input, 4 every fourth input, 0 never. Notes closer to the bottom have a stronger effect. Uses: formatting and length reminders, reinforcing earlier instructions, temporary world info and character bias. — [SillyTavern Author's Note](https://docs.sillytavern.app/usage/core-concepts/authors-note/)
- **[doc]** Character's Note is injected at a fixed chat depth and is "usually used to reinforce certain character traits". — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- **[opinion]** A PList in the Author's Note at depth ~4 "will have a much stronger effect" than in the description. kingbri says the AN lets you "reduce character card token size while allowing us to preserve small details". — [Ali:Chat](https://rentry.co/alichat); [MinimALIstic](https://rentry.co/kingbri-chara-guide)
- **[opinion]** The jailbreak/last prompt "is the freshest in the memory and as such has the most weightage". Keep the main prompt short and reinforce formatting there until the history itself follows it. Remove OOC corrections from history, since a message left in memory signals the "response was adequate and acceptable" (author's theory). — [rentry.co/oaicards](https://rentry.co/oaicards)

### Inferences
- Because history "sets the style", the most effective anti-repetition lever after a loop starts is editing or deleting the looping messages, not adding more instructions. Ali:Chat says the same: "delete the looping text".
- A recurring reminder at depth 0–4 every turn is the norm. Its content should be short and positive (length, "advance the scene", "vary openings"), because a long block at depth 0 is itself a repeated pattern the model sees every turn.

### Gaps
- No measured comparison of injection frequency (every turn vs. every Nth) was found.

## 5. Handling repetition loops: rules, summarization, samplers (and API vs local)

### Takeaway
For local models the community's toolset is DRY (sequence-level penalty, the most endorsed), Min-P plus temperature, an optional mild classic repetition penalty, and XTC (contested). Classic repetition penalty distorts common words and does not reliably stop loops. For API models (Claude, Gemini, OpenAI) most of these samplers are unavailable; only temperature and, for some providers, frequency/presence penalty are exposed. The levers there are prompt-level: advance the scene, vary input, delete or regenerate the looping messages, and summarize.

### Cited Findings
- **[doc]** Repetition Penalty penalizes tokens by frequency in context (1 = off). A large Range "can break responses... common words like 'the, a, and,' etc. will be penalized the most". Slope strengthens the penalty toward the prompt end. Min P "can worsen repetition if set too high". DRY "penalizes tokens that would extend the input into a sequence that already occurred", and sequence breakers let names and the like repeat. XTC removes the top choices. — [SillyTavern Common Settings](https://docs.sillytavern.app/usage/common-settings/)
- **[anecdotal test]** DRY (p-e-w): the penalty is `multiplier * base^(n - allowed_length)`. It is off by default (multiplier 0); the demo values were 2/0.8/1.75 (the PR text doesn't label them) and the code default allowed_length is 2; default sequence breakers are `\n`, `:`, `"`, `*`. Claims: classic penalties "don't actually prevent looping" and distort grammar, and prompting against loops has little effect. Evidence is a Mistral-7B demo where the model repeated a line verbatim with no samplers and with rep-pen 1.3, but produced new text under DRY, plus ~20 hours of personal chat with "no traditional looping". Limits: paraphrased or situational repetition still occurs, long names can be corrupted (add them to breakers), "a strong incentive to loop with a strong penalty... will often produce garbage", and at merge time it worked only with transformers-based loaders. — [DRY PR #5677](https://github.com/oobabooga/text-generation-webui/pull/5677)
- **[anecdotal test]** XTC (p-e-w): it removes all likely tokens above a threshold except the least likely of them, with a given probability. Suggested settings are probability 0.5 and threshold 0.1 (LostRuins reports 0.15/0.5 "works very well" in KoboldCpp), combined with Min-P 0.02 and DRY 0.8. Claimed: "The creativity is off the charts, while the coherence is virtually unchanged". It breaks clichés like the name "Eldoria" and targets structural repetition by penalizing tokens "simply for being very likely". Reviewer side effects: Mistral Large "much dumber", a Nemo model losing context facts, a 123B model making "dumb mistakes", runaway verbosity and cut-off EOS. Evidence is one model, one prompt and mixed user reports. — [XTC PR #6335](https://github.com/oobabooga/text-generation-webui/pull/6335)
- **[opinion]** Sphiratrioth's popular presets use only Min-P, Temperature, DRY and an optional Repetition Penalty, with all others neutralized. "I am not a fan of XTC, it feels too 'loose'." — [Sphiratrioth presets](https://huggingface.co/sphiratrioth666/SillyTavern-Presets-Sphiratrioth)
- **[opinion]** Ali:Chat: "If responses are looping, then decrease dialogue overlap, increase repetition penalty, or delete the looping text." — [Ali:Chat](https://rentry.co/alichat)
- **[opinion]** Arcanum (July 2026), no data: loops come from stalled scenes ("the single most common cause of a loop") and from mirroring the user's input shape. Fixes: regenerate once, OOC "describe differently and advance", introduce an event or NPC decision, vary your own phrasing, add agency and pacing rules to the system prompt (the world advances and NPCs act on their own initiative), or switch model if one model tics regardless. Raising temperature alone doesn't fix a stalled plot. It attributes to Latitude (AI Dungeon) the advice to undo back past the first instance of a repetition. — [Arcanum](https://arcanumrpgs.com/blog/ai-roleplay-repetition-loop/)
- **[doc]** Summarize extension: it injects a running summary, with the same position choices as Author's Note, every X messages or words. It may lose details or hallucinate, so check and correct it. Generate the first summary when messages start dropping out of context, and use "Max messages" for more focused summaries on large-context models. — [SillyTavern Summarize](https://docs.sillytavern.app/extensions/summarize/)
- **[doc, Anthropic]** No roleplay- or repetition-specific guidance exists in Claude's best-practices page beyond the example-diversity advice. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Inferences
- **API vs local:** DRY, XTC, Min-P and classic rep-pen with range/slope are local-backend samplers (text-generation-webui, KoboldCpp, llama.cpp derivatives). Hosted Claude and Gemini through Chat Completion expose mostly temperature/top-p/top-k. Some OpenAI-compatible APIs (OpenAI, Mistral) expose frequency/presence penalties. For a Claude- or Gemini-based Discord bot, repetition control is therefore prompt- and context-side. This is an inference from the sampler docs, not a provider-by-provider verification.
- **Old topics:** none of the sources directly addresses the bot "bringing old topics back". The closest mechanisms are summaries (which re-inject past events every turn and so can keep old topics salient), Author's Notes (same risk), and Arcanum's "introduce something new" advice. A summary written as "resolved/closed" items versus "open threads" would be the natural mitigation, but no source tests this.

### Gaps
- No verified, current numbers for Claude/Gemini parameter support in SillyTavern (e.g., whether Gemini exposes presence/frequency penalty) were found in this pass.
- No community test was found on summaries reviving old topics.

## 6. Multi-user / group chat and Discord bots

### Takeaway
SillyTavern's group-chat machinery (reply-order strategies, talkativeness, swap vs. join cards, muting) is the best-documented reference for multi-speaker handling. It addresses who speaks, not repetition. Joining cards risks characters mixing traits. Discord-specific community guidance on short replies and dragging old topics was not found in reliable sources.

### Cited Findings
- **[doc]** Reply order options: Manual; Natural (activated by whole-word name mentions in the last message plus talkativeness, with a random pick if none, and self-mentions ignored unless "Allow Self Responses"); List; Pooled (a random member who hasn't spoken since the last user message). Talkativeness runs 0–100% (default 50%). — [SillyTavern Group Chats](https://docs.sillytavern.app/usage/core-concepts/groupchats/)
- **[doc]** "Swap" (default) puts only the active speaker's card in context while history is shared. "Join" merges all members' description, scenario, personality, examples and depth prompts, and the docs warn it can make characters confuse their traits or themselves. Muting and Force Talk are available, as is Auto-mode, which generates without user input on a 5-second delay. — [SillyTavern Group Chats](https://docs.sillytavern.app/usage/core-concepts/groupchats/)
- **[doc]** In group chats, one alternate greeting is picked at random. — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- **[doc]** The first message most strongly sets reply length and style, which is the main lever for short replies. — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)

### Inferences
- For a Discord bot with many humans, the analogue of "Natural" order is responding to the latest addressed message, and the analogue of "Swap" is keeping one persona in context. Shared history is what drags old topics. A sliding window plus a summary of open threads, with the newest message clearly marked as the one to answer, is the pattern these mechanics suggest. This is unverified as community practice.

### Gaps
- No reliable Discord-bot community guide (oobabot, Mian's Tavern, etc.) with tested advice on multi-user context, short replies or topic drift was retrieved. Search results were product pages only (e.g. [oobabot on PyPI](https://pypi.org/project/oobabot/), [quickchat.ai](https://quickchat.ai/post/discord-ai-chatbot-roleplay)) and were not fetched or verified.

## 7. How card writers evaluate a card

### Takeaway
Evaluation in the community is informal: play a short session (10–15 turns), swipe or regenerate to see variety, push the card emotionally and against its limits, and edit the card toward specificity when it slips. No source documented blind tests or scored checklists.

### Cited Findings
- **[opinion]** Arcanum's check: load the card and play 10–15 turns, checking whether the voice matches, whether it holds under emotional pressure, and whether it respects limits when pushed. When it slips, make the card more specific. Swipe tests are not mentioned. — [Arcanum](https://arcanumrpgs.com/blog/how-to-write-a-character-card/)
- **[anecdotal]** The XTC author's informal metric is how much regenerated (swiped) messages differ from earlier attempts. The DRY author's is hours of chat without loops. — [XTC PR #6335](https://github.com/oobabooga/text-generation-webui/pull/6335); [DRY PR #5677](https://github.com/oobabooga/text-generation-webui/pull/5677)
- **[opinion]** OAI cards: "My best advice for learning how to write better greetings is to RP more." Learning is iterative and play-based. — [rentry.co/oaicards](https://rentry.co/oaicards)
- **[doc]** The token counter turns red when a definition exceeds half the context, a built-in sanity check. — [SillyTavern Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)

### Inferences
- A practical swipe test for repetition: generate N swipes for the same turn, then compare openings, recurring gestures and verbatim overlap with the card and examples. The tooling exists (swipes) but no source formalizes the procedure.

### Gaps
- No blind-test or A/B protocol from the community was found. Reddit (the most likely location) was blocked. Chub.ai, JanitorAI, Risu and Agnai guides were not retrieved in this pass.
