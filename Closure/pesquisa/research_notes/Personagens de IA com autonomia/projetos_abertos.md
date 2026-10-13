# Open-source AI VTuber / companion / autonomous-character projects: how they actually work

Read on 2026-10-13. Tags on each claim: [code] = read from source file; [docs] = official docs or README; [third-party] = auto-generated or unofficial doc of unknown date; [community] = Reddit/blog/forum practice, not documented behavior. Note: pages were read through a fetch tool that summarizes, so quotes are as returned by the tool, not byte-verified. Repo state snapshot (GitHub API, 2026-10-13): AIRI 50.3k stars, pushed 2026-10-13; elizaOS/eliza 19.6k stars, pushed 2026-10-13; Open-LLM-VTuber 14.1k stars, last push 2026-05-15, latest release v1.2.1 (2025-08-26); kimjammer/Neuro 2.1k stars, last push 2025-01-17 (dormant); z-waif (SugarcaneDefender) 602 stars (under the 1k bar, included because it was requested), pushed 2026-06-19.

Scope note: SillyTavern, Letta, elizaOS, OpenClaw are included as "other notable". I found nothing citable for "Timelines" memory add-on, Soulkyn/Kindroid clones, TavernAI group chat, or AI-Waifu-Vtuber (ardha27); those are in Gaps. Park et al. "Generative Agents" is included because Neuro's memory is a direct implementation of it.

---

## 1. Architecture and main loop of each project

### Takeaway
Three different shapes: (a) Neuro and Open-LLM-VTuber are request/response pipelines with a thin "should I prompt now" gate (a polling timer in Neuro; a frontend-sent signal in OLV); (b) AIRI's core-agent is a generic tool-round runtime and its autonomy lives in per-integration services; (c) elizaOS, Letta and OpenClaw are agent frameworks where "persona" is data fed into a generic loop. For a Discord text bot, the transferable core is: one shared state object, one gate function that says "may I speak now", and one prompt builder that assembles persona + memory injections + recent history.

### Cited Findings

**kimjammer/Neuro (Neuro-sama recreation)**
- `main.py` creates all class instances and threads; a single `signals` object is shared by every class (read/write common state; `signals.terminate` stops everything). Modules in `modules/` extend `Module`, run in their own thread/event loop, implement `run()` and optionally `get_prompt_injection()` returning an `Injection` (text + priority); injections are sorted lowest to highest so highest priority lands at the end of the prompt. [docs] — [README](https://github.com/kimjammer/Neuro) / [raw README](https://raw.githubusercontent.com/kimjammer/Neuro/master/README.md)
- `prompter.py` runs `prompt_loop`, a 0.1 s polling loop. Each tick it computes `timeSinceLastMessage = time.time() - signals.last_message_time` and pushes a `patience_update` event to the UI. [code] — [prompter.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/prompter.py)
- `prompt_now` is: return False unless `stt_ready` and `tts_ready`; return False if `human_speaking`, `AI_thinking` or `AI_speaking` (this is the only "interruption" handling: nobody is ever talked over, no cancellation); then triggers in order: `signals.new_message` (human spoke), `len(signals.recentTwitchMessages) > 0` (unprocessed chat), `timeSinceLastMessage > PATIENCE` (silence timeout). After prompting, `last_message_time = time.time()` resets the timer. [code] — [prompter.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/prompter.py)
- Model chosen per call by `chooseLLM()`: the `image` LLM if a multimodal module exists and `multimodal_now()`, else the `text` LLM. [code] — same file.
- Twitch chat is read by `twitchClient.py`; messages longer than `TWITCH_MAX_MESSAGE_LENGTH = 300` are ignored. [code] — [constants.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/constants.py)
- Dormant: last push 2025-01-17; tested only with Llama 3 8B Instruct via text-generation-webui; README says the author can "make no guarantee" outputs will not be vile and the only built-in filter word is "turkey" (debug) plus `blacklist.txt`. [docs/API] — [README](https://raw.githubusercontent.com/kimjammer/Neuro/master/README.md), [API](https://api.github.com/repos/kimjammer/Neuro)

**Open-LLM-VTuber (OLV)**
- Modular LLM/ASR/TTS via `conf.yaml`; web + desktop frontend (separate Open-LLM-VTuber-Web repo); `src/open_llm_vtuber`, `prompts/`, `characters/`, `mcp_servers.json`. [docs] — [README](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)
- All inputs go through `handle_conversation_trigger` in `src/open_llm_vtuber/conversations/conversation_handler.py`, which selects input by `msg_type` (`ai-speak-signal`, `text-input`, `mic-audio-end`) and routes to `process_single_conversation` or `process_group_conversation`; a new task starts only if the previous one for that client/group is done (group path); interrupts cancel the task and store the partial reply plus a `"[Interrupted by user]"` marker. [code] — [conversation_handler.py](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/src/open_llm_vtuber/conversations/conversation_handler.py)
- Agent types in `conf.yaml`: `basic_memory_agent` ("Nothing fancy", `llm_provider`, `faster_first_response`, `segment_method`, `use_mcpp`, `mcp_enabled_servers`), `letta_agent` (`host`, `port`, `id`; "the LLM that runs in practice is configured on Letta"), `hume_ai_agent` (`idle_timeout: 15` there is a disconnect timer, not proactivity); "MemGPT is temporarily removed". [docs] — [conf.default.yaml](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/config_templates/conf.default.yaml)
- Release cadence: latest release v1.2.1 on 2025-08-26; repo push 2026-05-15; license is NOASSERTION ("Other"). [API] — [releases](https://api.github.com/repos/Open-LLM-VTuber/Open-LLM-VTuber/releases/latest), [repo](https://api.github.com/repos/Open-LLM-VTuber/Open-LLM-VTuber)

**Project AIRI (moeru-ai/airi)**
- Monorepo ("Self hosted, you-owned Grok Companion"): stage apps (`stage-web`, `stage-tamagotchi`, `stage-pocket`), packages including `core-agent`, `core-character`, `memory-pgvector`, `server-runtime`, `server-sdk`; integrations listed in README: Discord bot, Minecraft bot, "Telegram, Factorio, MCP". [docs] — [README](https://github.com/moeru-ai/airi); package list via [GitHub API packages](https://api.github.com/repos/moeru-ai/airi/contents/packages)
- `@proj-airi/core-agent` README: handles "scheduling, context composition, tool rounds, and generation events"; one assistant turn = ordered rounds, each round = one model call plus all tool executions it requested; retries 408/429/5xx up to 3 times only before any output/tool call (so side effects never repeat); Responses adapter caps local function tools at 10 steps; turns are stored only after all steps settle; memory search is described only as an example of an external/trusted plugin task, not a built-in. [docs] — [core-agent README](https://raw.githubusercontent.com/moeru-ai/airi/main/packages/core-agent/README.md)
- As of 2026-10-13 `services/` in main contains only `computer-use-mcp` (no `telegram-bot`, `discord-bot`, `minecraft` directory there), and `packages/core-character/src` listed no files. [API] — [services](https://api.github.com/repos/moeru-ai/airi/contents/services), [core-character](https://api.github.com/repos/moeru-ai/airi/contents/packages/core-character). I could not locate where the Discord/Telegram/Minecraft bots now live.

**z-waif (SugarcaneDefender/z-waif)**
- Front end that glues Oobabooga (or LMStudio/Ollama since v1.15), RVC, Whisper; features: "Enhanced Memory" (lorebook entries + custom RAG over older conversations), rolling summaries every 10 message pairs, backups on boot and every 8 messages; modules for Discord, Vision, Alarm, Minecraft; autochat skips blank messages. Mood/emotion is not implemented ("Emotional / Tone understanding" is an unchecked To-Do). [docs] — [README](https://github.com/SugarcaneDefender/z-waif)

**Other notable**
- **elizaOS (elizaOS/eliza, MIT, 19.6k stars)**: message pipeline = bypass rules, then an LLM "shouldRespond" step, then response generation, then evaluators (see Q2). Docs index at [docs.elizaos.ai/llms.txt](https://docs.elizaos.ai/llms.txt). [docs] — [message-flow](https://docs.elizaos.ai/plugin-registry/bootstrap/message-flow.md)
- **Letta (MemGPT successor)**: agent state = always-in-context "memory blocks" (`label`, `description`, `value`, `limit` in characters; common labels `persona` and `human`; blocks prepended to prompt in an XML-like format; `read_only` flag; blocks can be shared across agents) edited by the agent through built-in memory tools. [docs] — [memory blocks](https://docs.letta.com/guides/core-concepts/memory/memory-blocks)
- **OpenClaw** (general autonomous agent, not a VTuber): "Heartbeat" runs periodic agent turns in the main session (see Q2). [docs] — [heartbeat](https://docs.openclaw.ai/gateway/heartbeat)
- **Generative Agents** (Park et al., arXiv 2304.03442, Apr 2023, rev. Aug 2023): experiences recorded in natural language, consolidated into reflections, retrieved to plan behavior; ablations show observation, planning and reflection each contribute to believability. [paper abstract] — [arXiv](https://arxiv.org/abs/2304.03442)

### Inferences
- The simplest shape that works in production-ish form is Neuro's: shared state + one polling gate + injections list. It maps almost 1:1 to a Discord bot with an asyncio loop.
- Several "autonomous" repos are less autonomous than their READMEs imply: OLV's proactive speaking is a frontend-sent signal plus a canned prompt (Q2), AIRI's core-agent explicitly delegates memory to adapters.

### Gaps
- AIRI's actual Discord/Telegram/Minecraft agent code was not found in main as of this read; the only description I found of the Telegram bot's loop is third-party (Q2).
- AI-Waifu-Vtuber, TavernAI, Soulkyn, Kindroid-style clones: not researched or no citable source found.

---

## 2. Proactive behavior (speaking without being addressed)

### Takeaway
Documented proactive mechanisms are simple: a silence timer (Neuro `PATIENCE = 60` s), a frontend idle signal plus a fixed "say something" prompt (OLV), an LLM-chosen action loop with a `sleep` action on a 60 s tick (AIRI Telegram, third-party doc), and periodic heartbeat turns where the default answer is silence (OpenClaw). None of the projects I could read implements an explicit boredom/interest score; "alive" feeling comes from the timer plus a prompt that tells the model what to do with silence.

### Cited Findings
- Neuro: `PATIENCE = 60` ("seconds to wait before prompting the AI") in constants; silence trigger `timeSinceLastMessage > PATIENCE` in `prompter.py`; the timer is reset on every prompt, so the character speaks at most once per 60 s of silence. [code] — [constants.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/constants.py), [prompter.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/prompter.py)
- Neuro: what the character says on silence is steered by the system prompt: it tells the character to change topics if someone doesn't respond and to occasionally share fun facts, with short (about one sentence) replies. [code] — constants.py `SYSTEM_PROMPT`
- Neuro blocks on `human_speaking`/`AI_thinking`/`AI_speaking`, so it cannot run away with consecutive prompts; there is no per-user rate limit in `prompter.py`. [code] — prompter.py
- OLV: proactive speaking is "Basic AI proactive speaking (experimental)" in v1.0.1; no trigger or idle-seconds is documented in the release post. [docs] — [v1.0.1 release](https://docs.llmvtuber.com/blog/v1.0.1-release)
- OLV code path: a client message of type `ai-speak-signal` loads `system_config.tool_prompts.proactive_speak_prompt` (default file text: "Please say something that would be engaging and appropriate for the current context."); if unset it falls back to "Please say something."; it sets metadata `proactive_speak`, `skip_memory`, `skip_history`, i.e. the synthetic prompt is not written to history/memory; client gets `"AI wants to speak something..."`. So the idle decision lives in the frontend, not the Python backend. [code] — [conversation_handler.py](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/src/open_llm_vtuber/conversations/conversation_handler.py), [prompt file](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/prompts/utils/proactive_speak_prompt.txt)
- OLV `basic_memory_agent.py`: `skip_memory` is honored in `_to_messages` (user turn sent to LLM but not saved). The tool did not find `proactive_speak`/`skip_history` handling in that file. [code] — [basic_memory_agent.py](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/src/open_llm_vtuber/agent/agents/basic_memory_agent.py)
- AIRI Telegram bot (third-party generated doc, date unknown; code not found in current main): LLM-driven action selection among `read_unread_messages`, `send_message`, `send_sticker`, `list_chats`, and flow actions `continue` / `break` / `sleep` (sleep = wait 30 s; break = stop and clear context); `loopPeriodic` in `services/telegram-bot/src/bots/telegram/index.ts` runs on a 60 s `setTimeout`, first over existing chats then "new opportunities"; per-chat limits: 20 context messages, 50 action-history entries, 100 unread messages. [third-party] — [mintlify.wiki AIRI Telegram page](https://mintlify.wiki/moeru-ai/airi/integrations/telegram)
- OpenClaw heartbeat: `agents.defaults.heartbeat.every` (default `30m`, `"0m"` disables), `activeHours` (`start`, `end`, `timezone`), quiet reply `NO_REPLY` (legacy `HEARTBEAT_OK` accepted when remaining content <= 300 chars), `heartbeat_respond` tool with `notify: true/false`; default prompt is "intentionally narrow" and tells the agent not to infer or repeat old tasks; each heartbeat is a full agent turn; cost mitigations `isolatedSession: true` (est. ~100K tokens down to 2-5K), `lightContext: true`, cheaper `model` for heartbeat only. [docs] — [heartbeat](https://docs.openclaw.ai/gateway/heartbeat)
- SillyTavern group auto-mode: while enabled, the group generates without user input; "The next auto-mode turn is triggered after a 5-second delay when the last drafted character sends its message"; typing in the send box disables it. Code: `DEFAULT_AUTO_MODE_DELAY = 5`, worker on `setInterval(groupChatAutoModeWorker, autoModeDelay * 1000)` skips the turn if a send or group generation is in progress. [docs + code] — [groupchats docs](https://docs.sillytavern.app/usage/core-concepts/groupchats/), [group-chats.js](https://raw.githubusercontent.com/SillyTavern/SillyTavern/release/public/scripts/group-chats.js)
- Generative Agents-style "importance/recency/relevance" scoring: secondary summaries say retrieval ranks by recency (exponential decay since last access), relevance (embedding similarity), importance (LLM-assigned ~1-10), and reflection triggers when summed importance of recent memories passes a threshold; weights differ across write-ups (all 1 in one LangChain write-up; 0.5/3.0/2.0 in another), so check the paper before using. [secondary] — [search summary of agentpatterns.ai / W&B](https://agentpatterns.ai/agent-design/generative-agents-memory-stream/)
- No "inner monologue" loop, boredom score, or interest score was found in any of: Neuro, OLV, z-waif README, AIRI core-agent README, or the third-party Telegram doc.

### Inferences
- Neuro's design (single timer, reset on any speech, blocked while busy) is the minimum viable proactive loop; its main weakness is that the topic comes only from a generic "change topic / fun fact" instruction, so proactive lines can feel random rather than self-directed.
- OLV keeps the synthetic "say something" turn out of history (`skip_history`, `skip_memory`); this is a useful pattern to stop proactive nudges polluting context and being mimicked.
- OpenClaw's inversion (default output is silence, with explicit token and `notify` flag) is the cleanest documented way to let a model decline to speak; AIRI's Telegram `sleep` action is the same idea inside an action list.
- A Discord bot could combine: Neuro-style idle timer as the wake-up, an OpenClaw/AIRI-style structured "speak or stay quiet" decision, and OLV-style exclusion of the synthetic prompt from history.

### Gaps
- Where OLV's frontend decides to send `ai-speak-signal` (idle seconds, toggle) not found (Open-LLM-VTuber-Web code search required auth).
- AIRI Telegram prompt text for choosing actions not found; current main no longer lists the service.
- No source for "mood/boredom" scalars in any project read.

---

## 3. Long-term and short-term memory

### Takeaway
Real implementations are: Neuro's ChromaDB store seeded with manual "long-term" facts and auto-generated Q&A reflections every 20 messages; SillyTavern's rolling Summarize + Chat Vectorization (both documented with caveats); Letta's always-in-context editable blocks; z-waif's rolling summaries + RAG; AIRI's pgvector message embeddings. OLV deliberately removed long-term memory. Maintainers uniformly warn that none of this is guaranteed to improve chats.

### Cited Findings
- Neuro memory: ChromaDB at `./memories/chroma.db`, collection `neuro_collection`, default embedding function; `run()` checks every 5 s and when `len(history) - processed_count >= 20` sends the 20 messages with `MEMORY_PROMPT` ("three high-level question-and-answer pairs", split on `{qa}`), upserts each as `{"type": "short-term"}` — explicitly following the Generative Agents paper; manually added memories are `long-term`; seed file `memoryinit.json` loaded only when DB is empty; import/export JSON; frontend controls both types separately. [code + docs] — [modules/memory.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/modules/memory.py), [memories/readme.md](https://raw.githubusercontent.com/kimjammer/Neuro/master/memories/readme.md)
- Neuro retrieval: query = recent Twitch messages + last `MEMORY_QUERY_MESSAGE_COUNT = 5` history entries; `MEMORY_RECALL_COUNT = 5` results; injected as `"{AI_NAME} knows these things:\n" ... "End of knowledge section\n"` with `priority = 60`. No importance score, no decay, no deletion beyond manual. [code] — memory.py, constants.py
- Neuro code issues noticed by the reader: `STOP_STRINGS.remove("\n")` returns None so `"stop"` is sent as null; `API.wipe()` doesn't refresh `self.collection`; `create_memory` passes non-list args to `upsert`. [code] — memory.py
- Neuro context management: `CONTEXT_SIZE = 8192`, "program targets up to 90% of this" (README/constants); the trimming code itself was not readable via the tool. [docs] — constants.py
- OLV: "long-term memory is temporarily removed (coming back soon)" (README); chat log persistence remains. `basic_memory_agent` keeps `_memory` as an unbounded plain list of `{role, content}` with no trimming/summarization in that file; duplicates of the immediately preceding message are skipped. Letta agent option delegates memory to a Letta server. [docs + code] — [README](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber), [basic_memory_agent.py](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/src/open_llm_vtuber/agent/agents/basic_memory_agent.py)
- OLV group chat shares one `conversation_history` list of `"Name: text"` strings with a per-member `memory_index` pointer; each member sees only the unseen part, and a member does not get its own line back. [code] — [group_conversation.py](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/src/open_llm_vtuber/conversations/group_conversation.py)
- SillyTavern Summarize extension: model-generated rolling summary saved in chat metadata on the last in-context message; Prompt supports `{{words}}`; triggers "every X messages" and/or "every X words" (whichever first; 0 disables); "Set the interval so the first summary appears just as older messages begin dropping out of the prompt"; Raw vs Classic prompt builders; blocking vs non-blocking; "Restore Previous". Docs warn summaries "can omit details or hallucinate" and should be checked. [docs] — [Summarize](https://docs.sillytavern.app/extensions/summarize/)
- SillyTavern Chat Vectorization: per-message vectors, chunk 400 chars, Query messages default 2, score threshold 25%, Insert# default 3, Retain# default 5, injection templated as "past events" ordered most relevant last with sender names; docs warn it "does not guarantee better chats or memory", and that changing prefix invalidates prompt caching ("choose either vectorization or caching, not both"); optional experimental vector summarization "may sometimes make search less effective". [docs] — [Chat Vectorization](https://docs.sillytavern.app/extensions/chat-vectorization/)
- SillyTavern Smart Context (legacy): ChromaDB via Extras, inactive until 10 messages; docs now say it is "no longer maintained and not recommended"; memories can be inaccurate after message edits/deletes; World Info recommended for a single shared database. [docs] — [Smart Context](https://docs.sillytavern.app/extensions/smart-context/)
- Letta: `persona` and `human` blocks always in context, character-limited, agent-editable via memory tools; the block `description` is "the main signal" for how the agent reads/writes it; setting `value` replaces the whole block so concurrent writers can overwrite each other. Newer "Dreaming" (`/sleeptime`): background subagents "review recent conversations, consolidate useful lessons, and update memory without interrupting your active work"; memory lives in MemFS, a git-backed filesystem; optional "Agent reviews before applying"; triggered after N completed steps or on context compaction. [docs] — [memory blocks](https://docs.letta.com/guides/core-concepts/memory/memory-blocks), [sleeptime/dreaming](https://docs.letta.com/guides/agents/architectures/sleeptime)
- elizaOS: after reply, evaluators run via `runtime.evaluate(...)`; the reflection evaluator extracts new facts, updates relationships and self-reviews; per the docs' decision points reflection runs when message count exceeds conversation length divided by four. [docs] — [message-flow](https://docs.elizaos.ai/plugin-registry/bootstrap/message-flow.md)
- AIRI (third-party doc): PostgreSQL + pgvector `chat_messages` table with `embedding vector(768)` for semantic search; README lists "Memory Alaya (WIP)" and a `packages/memory-pgvector` package exists. [third-party + docs] — [mintlify.wiki](https://mintlify.wiki/moeru-ai/airi/integrations/telegram), [README](https://github.com/moeru-ai/airi)
- z-waif: lorebook + custom RAG over older conversations; rolling summaries every 10 message pairs ("SEARCH_POINT_SIZE", "SUMMARY_TOKENS_MAX_COUNT" settings); changelog warns "RAG should probably be on, might break if not!". [docs] — [README](https://github.com/SugarcaneDefender/z-waif)
- Community (not documented behavior): common advice is summarizing every ~50 messages into a lorebook and hiding summarized messages, or using the Qvink extension; one commenter describes an "8-16k context rot cliff"; a vendor blog (Meganova, sells a character product) argues memory is for plot continuity and does not fix personality drift. [community] — [techtactician repetition guide](https://techtactician.com/sillytavern-repetition-fixes-best-settings/), [Meganova blog](https://blog.meganova.ai/why-your-ai-character-breaks-after-10-messages) (as summarized by search; not fetched in full)

### Inferences
- No project reviewed implements forgetting/decay in shipped code; Neuro's memory only grows and relies on a top-5 similarity cut. The Generative Agents scoring (recency/importance/relevance) exists only in the paper's lineage, not in Neuro.
- Neuro's trick of storing Q&A pairs ("three high-level questions + answers") rather than free summaries yields retrieval-friendly units and is cheap (one call per 20 messages).
- Letta's two-tier idea (small always-in-context blocks for persona/per-user facts + retrieval for everything else + a background consolidation job) is the best-documented pattern for per-user profiles; none of the VTuber projects keep per-user profiles in code I could read.

### Gaps
- Retrieval/trim code in Neuro `llmWrappers/` (90% context trimming, how history is formatted with Twitch author names) could not be read (tool returned only constructors).
- No per-user profile mechanism was found in Neuro, OLV or z-waif.
- Maintainer statements on what "fails" are limited to the SillyTavern docs caveats above; I found no maintainer post-mortems in issues/discussions.

---

## 4. Personality definition and keeping it non-generic

### Takeaway
Persona is almost always a static text block (Neuro `SYSTEM_PROMPT` with an example chat; OLV `persona_prompt` in `conf.yaml` / `characters/`; SillyTavern V2/V3 card fields; elizaOS `bio`/`messageExamples`/`style`). Maintainers' consistent guidance: put identity in always-sent fields, teach voice via the first message and example dialogue, and re-inject a short reminder near the end of the prompt. Nobody in this set uses fine-tuning/LoRA in the shipped repos I read.

### Cited Findings
- Neuro `SYSTEM_PROMPT` (constants.py): one reply only, no quotes; playful, sarcastic, curious AI VTuber with a backstory; short replies (about one sentence); change topic when ignored; includes a short example transcript; must fit under `CONTEXT_SIZE`. Injections are appended with priority so higher-priority text sits at the prompt end. [code] — [constants.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/constants.py), [README](https://raw.githubusercontent.com/kimjammer/Neuro/master/README.md)
- Neuro sampler/stop settings: `STOP_STRINGS = ["\n", "<|eot_id|>"]` (forces single-line replies), `max_tokens: 200`, `BANNED_TOKENS` (comment: banning token 422 stopped Mistral 7B v0.2 spamming hashtags). [code] — constants.py, [textLLMWrapper.py](https://raw.githubusercontent.com/kimjammer/Neuro/master/llmWrappers/textLLMWrapper.py)
- OLV: `character_config.persona_prompt` (block scalar) and `character_name` ("Will be used in the group conversation"); README: "Shape your AI companion's persona by modifying the Prompt". `basic_memory_agent` default system text is just "You are a helpful assistant." unless overridden; `set_system` appends an interrupt note, and the MCP prompt is appended when tool mode is "prompt". [docs + code] — [conf.default.yaml](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/config_templates/conf.default.yaml), basic_memory_agent.py
- Character Card V3 spec (kwaroran): inherits V2 fields `name`, `description`, `personality`, `scenario`, `first_mes`, `mes_example`, `system_prompt`, `post_history_instructions`, `alternate_greetings`, `character_book`; new: `group_only_greetings` (required, "only for group chats"), `nickname` (replaces `{{char}}` if set), `creator_notes_multilingual`, `assets` (types icon/background/user_icon/emotion/other); lorebook entry fields `keys`, `secondary_keys`+`selective`, `constant`, `insertion_order` (lower added earlier), `priority` (lower-priority entries dropped first when `token_budget` reached), `use_regex`; `depth`/position are set by `@@depth` / `@@position` decorators in content; a lorebook can disable the UI prompt with `@@disable_ui_prompt`. [spec] — [SPEC_V3.md](https://github.com/kwaroran/character-card-spec-v3/blob/main/SPEC_V3.md)
- SillyTavern Character Design: description/personality/scenario are "permanent" (always sent); example messages (`<START>` marker, `{{char}}:`/`{{user}}:` prefixes) are inserted only if context space remains and are dropped block by block; the first message sets style and length expectations "more than anything else"; token counter turns red above half the model context; points to community formats (Trappu's PList + Ali:Chat, AliCat's Ali:Chat, kingbri's minimalist guide); Main Prompt and Post-History Instructions overrides only apply if "Prefer Char. Prompt/Instructions" are enabled, `{{original}}` keeps the default; Character's Note injected at a depth with role User/System/Assistant. [docs] — [Character Design](https://docs.sillytavern.app/usage/core-concepts/characterdesign/)
- SillyTavern Author's Note: in-chat at a depth (0 = very end of history; 4 = before the most recent three messages) or after scenario; frequency N inserts every Nth user input; "The closer the Author's Note is to the bottom of the prompt, the more impact it has on the next AI response"; suggested for style/format reminders. [docs] — [Author's Note](https://docs.sillytavern.app/usage/core-concepts/authors-note/)
- elizaOS character file: `bio` (string or array), `messageExamples` ("the most powerful tool for shaping conversational behavior"), `style` with `all`/`chat`/`post`, `topics` in tiers, `adjectives` (avoid contradictory sets), `knowledge`; guidance "Consistency Over Complexity", base examples on real user interactions, avoid stereotypes/clichés; how fields are sampled into the prompt is not explained in that page. [docs] — [personality-and-behavior](https://docs.elizaos.ai/agents/personality-and-behavior.md)
- Letta: persona lives in an editable `persona` block (can be `read_only`). [docs] — memory-blocks page above.
- Community (not documented behavior): lorebooks are the usual recommendation for keeping character facts stable; one user reports "night and day" continuity improvements. [community] — via [techtactician](https://techtactician.com/sillytavern-repetition-fixes-best-settings/) search summary.

### Inferences
- Both Neuro and ST docs converge on "short replies + one-line stop sequence + example dialogue in the prompt" as the cheapest anti-genericness lever; ST says example blocks are the first thing trimmed, so the persistent voice must live in description/Author's Note-style bottom injections.
- A text Discord bot with two characters can use V3-style fields (including `group_only_greetings` and `nickname`) as a schema even without a card parser.

### Gaps
- No project reviewed documents fine-tuning/LoRA for persona (Neuro-sama's real model is not open); sampler recommendations beyond Neuro's constants were not found in maintainer docs.
- No maintainer guidance on sycophancy found.

---

## 5. Group chat: which character replies, and turn-taking

### Takeaway
SillyTavern has the only richly documented activation system (manual / natural / list / pooled, with mention detection and per-character talkativeness); OLV uses a plain round-robin queue where AIs just keep talking until interrupted; Neuro and AIRI have no multi-character logic in what I could read.

### Cited Findings
- SillyTavern reply-order strategies: Manual (`/trigger`); Natural Order ("Tries to simulate the flow of a real human conversation"; mentions first, then talkativeness, then random); List Order (members in list order); Pooled Order ("Activates one random character who hasn't spoken yet since the last user message"). Generation modes: Swap character cards (default: only active speaker's card in context) vs Join character cards (all cards combined; docs warn it can cause characters to become confused about themselves or merge personalities; Include/Exclude muted). [docs] — [groupchats](https://docs.sillytavern.app/usage/core-concepts/groupchats/)
- Talkativeness: "how often the character speaks if they were not mentioned"; 0% = speaks only when mentioned; 100% = always replies; default 50%. Mentions match whole words of the name (e.g. "Misaka Mikoto" activates on "Misaka" or "Mikoto"); characters won't reply to their own name in their own message unless "Allow Self Responses". [docs] — same page.
- Natural-order algorithm (code): `bannedUser` = last speaker when trigger is not user input (cleared if `allowSelfResponses`); each word of the input is compared with each member's name words (mentioned members activate without a roll); remaining members shuffled and each activates if `talkativeness >= Math.random()` (missing -> `talkativeness_default`); if nobody activated, picks randomly among members with talkativeness > 0 (or all members) — and that fallback is not filtered by `bannedUser`. List order returns all enabled members. Pooled order: activates exactly one from those who haven't spoken since the last user message; if all have, excludes the last speaker. [code] — [group-chats.js](https://raw.githubusercontent.com/SillyTavern/SillyTavern/release/public/scripts/group-chats.js) (as summarized by the fetch tool).
- OLV round-robin: `group_queue=list(group_members)`, loop pops front, runs the turn, re-appends to the back (`state.group_queue.append(current_member_uid)`); human input only seeds the history at the start; no relevance-based speaker choice; loop only ends on cancellation or fatal error; errors in one turn are caught and broadcast; reader flagged bugs: `is_first_responder` never set True, hardcoded "Human" name inconsistency. [code] — [group_conversation.py](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/src/open_llm_vtuber/conversations/group_conversation.py)
- OLV group prompt (`group_conversation_prompt`, added to each AI participant's memory) per tool summary: respond conversationally without a "Name:" colon label, feel free to address the other AIs, alternate short and long responses so others can take part, and actively suggest interesting topics. [code/prompt file] — [group_conversation_prompt.txt](https://raw.githubusercontent.com/Open-LLM-VTuber/Open-LLM-VTuber/main/prompts/utils/group_conversation_prompt.txt) (summary only; text not returned verbatim)
- elizaOS: no multi-character turn-taking logic found, but per-agent `shouldRespond` with bypass for DMs/API rooms, mute state overridable by name mention, and an LLM evaluation that treats any action other than IGNORE/NONE as "respond". [docs] — [message-flow](https://docs.elizaos.ai/plugin-registry/bootstrap/message-flow.md)

### Inferences
- For two characters on Discord, SillyTavern's "mention first, then talkativeness roll, then fallback" is directly portable and cheap (no LLM call); the code shows its failure points: the fallback can re-pick the last speaker, and without a ban two characters can ping-pong forever (OLV's queue has exactly that shape and relies on user interrupts).
- ST "Swap" mode (only speaker's card in context) is the documented way to avoid persona bleed; "Join" is documented as risky.

### Gaps
- No documented mechanism where one character decides to *interject* in the other's conversation based on content, other than ST talkativeness dice and name mentions.
- Neuro/AIRI multi-character behavior: none found.

---

## 6. Tool use and multi-user handling

### Takeaway
Tool use is mostly via MCP (OLV `use_mcpp`, AIRI core-agent tool rounds, Letta memory tools). Multi-user handling is thin in the VTuber projects: Neuro treats Twitch chat as one anonymous stream; AIRI Telegram keeps a per-chat context; SillyTavern is single-user by design.

### Cited Findings
- OLV: `use_mcpp: True` ("MCP Plus to let the LLM have the ability to use tools"), `mcp_enabled_servers`, `mcp_prompt` ("Please note that Agent will decide whether to use this prompt or not"); Claude and OpenAI-compatible tool loops; if the API reports no tool support (`__API_NOT_SUPPORT_TOOLS__`) it falls back to prompt mode and parses JSON with `StreamJSONDetector`. [code] — conf.default.yaml, basic_memory_agent.py
- AIRI core-agent: tool rounds, parallel tool calls, max 10 local tool steps, provider-side web search with sources. [docs] — core-agent README.
- Neuro Twitch handling: `recentTwitchMessages` non-empty triggers a prompt; messages are fed to the memory query; per-user distinction/prioritization not documented in README. [code + docs] — prompter.py, memory.py, README
- AIRI Telegram (third-party): per-chat `ChatContext` (`chatId`, `messages`, `actions`, `currentAbortController`), messages deduplicated by `chatId-messageId`, queued, processed sequentially per chat; `ADMIN_USER_IDS` config. [third-party] — [mintlify.wiki](https://mintlify.wiki/moeru-ai/airi/integrations/telegram)
- Discord voice input to Neuro "was attempted but is unsupported by Discord". [docs] — Neuro README.

### Inferences
- A Discord text bot can reuse the per-channel context + dedupe-by-message-id + sequential processing pattern; per-user profile blocks (Letta `human`-style) are the missing piece none of the VTuber repos provide in readable code.

### Gaps
- No documentation of per-user memory isolation or abuse limits in Neuro/OLV/AIRI.

---

## 7. Documented failure modes and mitigations

### Takeaway
Documented mitigations are mostly structural (busy flags, stop strings, token bans, short replies, skip-history for synthetic prompts, quiet-reply tokens, cost-cutting settings). Most failure-mode discussion available is community practice, not maintainer docs. Persona drift, sycophancy and prompt injection by chat users are essentially undocumented in the repos read.

### Cited Findings
- Runaway chatter / overlap: Neuro never prompts while human speaking, AI thinking or AI speaking, and resets the patience timer after each prompt. [code] — prompter.py. SillyTavern auto-mode skips turns while a generation is in flight and typing disables auto-mode. [docs/code]
- OLV group chat has no natural end: the queue re-queues each speaker so conversation continues until cancelled. [code] — group_conversation.py
- Repetition / formatting loops: Neuro bans specific tokens (hashtag spam on Mistral 7B v0.2) and uses stop strings; SillyTavern docs name no repetition fix beyond samplers. Community checklist: wrong instruct template, duplicated/conflicting instructions in history, context pushed past what the model handles, over-tight repetition penalty breaking grammar; try DRY and XTC samplers; if a few similar replies accumulate, delete them or restart because repeated content carries forward on smaller models. [community] — [techtactician](https://techtactician.com/sillytavern-repetition-fixes-best-settings/) (via search summary; not fetched in full)
- Persona drift in long chats: community claims drift appears around an "8-16k context rot cliff" and recommends periodic summaries + lorebooks; unverified numbers. [community] — same sources.
- Memory staleness: Chat Vectorization and Smart Context can return inaccurate memories after edits/deletes; summaries can hallucinate; prompt-cache invalidation by vectorization. [docs] — SillyTavern pages above.
- Persona bleed in groups: ST docs warn "Join character cards" can produce confused or merged personalities. [docs] — groupchats page.
- Cost/latency: OpenClaw heartbeat is a full agent turn each interval (est. ~100K tokens, 2-5K with `isolatedSession`); OLV `faster_first_response` starts speech at the first comma; Neuro keeps replies ~1 sentence/`max_tokens: 200` and a tiny local STT model to keep latency low. [docs/code] — heartbeat page, conf.default.yaml, constants.py, README
- Safety / prompt injection by chat users: Neuro README says no guarantee outputs won't be vile and the filter is minimal (`is_filtered()` with a debug word, `blacklist.txt`); AIRI core-agent retries only before any side effect, avoiding duplicate tool actions. No documented defense against chat-borne prompt injection was found in Neuro, OLV or AIRI docs. [docs/code]
- Interruption bookkeeping: OLV stores the partial AI reply plus `"[Interrupted by user]"` in history so the model knows what was actually heard. [code] — basic_memory_agent.py

### Inferences
- Failure modes the target bot should assume and test for are exactly the ones not covered by upstream docs: ping-pong between the two characters (no natural end condition in OLV's queue), drift despite memory, and injection via other users' messages.
- Cheap structural guards (busy flag, per-channel cooldown, quiet-reply token, synthetic prompts kept out of history, short-reply stop sequences) are proven in the code read.

### Gaps
- No maintainer-authored documentation on sycophancy, persona drift measurement, or injection defense. The community figures above come from search-result summaries, not fully read threads; Reddit threads were not opened directly.
- No numbers on cost per day for any VTuber project.
