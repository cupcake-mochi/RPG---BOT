# Neuro-sama (Vedal987): what is publicly confirmed vs. community inference, as of 2026-10-13

Provenance tags used on every finding:
- **[A]** stated by Vedal himself (interview, dev stream, X post), as best I could verify the primary or a transcript
- **[B]** documented in official code or docs (VedalAI GitHub)
- **[C]** reported by press or academic work
- **[D]** community inference or fan-wiki content with no primary source I could check

Method caveats for the report writer:
- Many fetches went through a summarizing tool (WebFetch), not raw HTML. Treat quoted strings as "as returned by the tool" and re-verify before publishing any verbatim quote.
- Not reachable (403/402/paywall): Bloomberg (D'Anastasio, 17 Jun 2023), Toolify copy of the Jan 2023 interview, Fandom wiki pages, the paywalled part of the KAI-YOU interview, Hu & Freeman CHI '26. I did not see Vedal's X/Discord posts directly. No primary text for his Discord announcements was found.
- Wikipedia and the NeuroWiki were used only as pointers. The NeuroWiki (en.neurosama.info) is a fan wiki with mostly uncited technical sections, so everything taken from it is tagged [D].
- Net finding: Vedal has disclosed almost nothing concrete about the model, memory implementation, or decision loop. The only hard, code-level documentation of her decision behavior is the Neuro SDK (game-side). Most "how she works" content online is inference.

---

## 1. What has Vedal confirmed about the language model (custom vs. API, training data, retraining, personality shaping), and what has he refused to disclose?

### Takeaway
Vedal has confirmed only that she runs on a large language model "pretrained on a large amount of text from the internet", that training data is manually curated, and that personality was built by collecting data that produces a given tone. He has never publicly named the base model, size, or fine-tuning method (in sources I could reach). The widely repeated "~2B parameters / q2_k / LLaMA / LoRA / trained on Twitch chat" claims trace only to fan wikis or unattributed posts.

### Cited Findings
- [A] LLM idea came from a friend; Vedal thought it "totally had potential" and combined it with his osu! AI. LLMs are "pretrained on a large amount of text from the internet so they have a lot of knowledge." Source: Dexerto interview, Dec 2022 — [Dexerto](https://www.dexerto.com/entertainment/ai-vtuber-neuro-sama-future-twitch-streaming-gaming-2019378/)
- [A] Avatar rationale: "it's much easier to control an avatar than try to generate a video of a real person" — same Dexerto article.
- [A] On how she learns and communicates he would not go into detail, other than confirming an LLM. Quote attributed to him: "Data that she learns on is also manually curated to mitigate negative biases." Kotaku, 6 Jan 2023 — [Kotaku](https://kotaku.com/vtuber-twitch-holocaust-denial-minecraft-ai-chatgpt-1849960527)
- [A] Vice (5 Jan 2023): Vedal says he makes improvements to the AI and streams before going live each day ("I usually make improvements to the AI and stream before I go live every day"). Also: "Having the interactions with Twitch chat are what makes her entertaining to watch." — [Vice](https://www.vice.com/en/article/this-virtual-twitch-streamer-is-controlled-entirely-by-ai/)
- [A] KAI-YOU interview (30 Apr 2023, Japanese; only the free portion read): "a large language model (LLM) is used" for her; she is cheerful because he collected data that yields that tone and taught it to her; he declined to share tuning specifics. He also said English-language internet text makes English AI VTubers easier to build. — [KAI-YOU Premium](https://premium.kai-you.net/article/655)
- [A, via Japanese-subbed video of an English interview, ~23 Jan 2023, machine-translated captions, low fidelity] Vedal described two separate AI models (a game-playing AI and the AI that controls Neuro-sama). Because they are separate, the amount of data transferred between them is limited, so she is not constantly aware of what is happening in the game. — [Archive.org record (published 2023-01-23, uploader crunchybagels)](https://archive.org/details/vedals-interview-neuro-samas-new-model-and-the-ai-system-behind-her-yy-9-of-46w-4-a); [YouTube video, captions read via yt-dlp](https://www.youtube.com/watch?v=Yy-9Of46w4A)
- [A] April 2026 dev stream (third-party upload by "Kraul", 2026-04-28, auto-captions): Vedal says the "great rewritening" of all Neuro's code is complete and every stream going forward runs on the rewrite; a main reason was years of Unity memory leaks he could not diagnose; a new server (Threadripper, RTX Pro 6000, possibly a couple of 4090s) is coming so both twins can be virtualized; 2026 goals include improving "audio understanding, language model stuff, everything", plus a "V3 voice." He jokes about running GPT-4-scale models on "my 3060" and says money is "much less of a constraint after the last subathon", with his time the main constraint. He says the tech stack is internally called "Iris" (spelling per captions; "AIris"/"Iris" ambiguous). — [YouTube: "WE'RE SO BACK Vedal Reveals Neuro's AI Improvements and Future Plans"](https://www.youtube.com/watch?v=YwAPpL8mYfY). Caveat: captions are ASR, speaker labels mix Vedal and Neuro, and a re-upload is not Vedal's own channel.
- [A] Vedal says he does not plan to (or does not like to) "lobotomize" her to avoid bans (fuzzy, from the machine-translated Jan 2023 captions; treat as paraphrase only) — [YouTube captions](https://www.youtube.com/watch?v=Yy-9Of46w4A)
- [C] Wikipedia: "Neuro-sama; Vedal" KAI-YOU, Kotaku, Dexerto, Bloomberg etc. are the main sources; the article's own description (LLM + TTS + Live2D/Unity avatar) is not attributed to Vedal — [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama)
- [C/D] Dexerto reports VTuber side built in C# on Unity and AI side in Python, "based on the channel bio" — via search summary of [Dexerto](https://www.dexerto.com/twitch/an-ai-powered-vtuber-is-now-the-most-popular-streamer-on-twitch-3300052/); NeuroWiki repeats "gaming components in Python, most other parts C#, front end Unity" with no citation — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama) [D].
- [D] MISATTRIBUTED CLAIM: The statement "Neuro speaks using an LLM that Vedal has trained himself. The training data is primarily from his own Twitch interactions or interactions with other people, used with their express permission" is a Threads post by the account `sinisterpixel` (dated "01/04/25", ambiguous format). It refers to Vedal in the third person, cites no source, and the author says they are not sure of details. It is NOT a Vedal statement. One third-party research page (lin-guanguo.github.io) described it as "Vedal's Threads post"; that is incorrect. — [Threads post](https://www.threads.com/@sinisterpixel/post/DEa_XlXoKjK?hl=en); [lin-guanguo page](https://lin-guanguo.github.io/llm-memory-research/neuro-sama.research/)
- [D] "~2B parameters, q2_k quantization", "LLaMA-family base", "LoRA fine-tuning", "inference self-hosted on Vedal's GPUs", "Azure Ashley voice pitch-shifted +25%": I found no primary source for any. The lin-guanguo page itself says the 2B/q2_k numbers trace only to Fandom wikis and should be treated as unverified. NeuroWiki says only that the TTS is "a redevelopment based on Microsoft's voice, Ashley" without citation. The Vedal statement that he self-hosts hardware is partly supported by the April 2026 dev stream (new server purchase) but that does not prove what model runs on it.
- [D] Hugging Face forum speculation (LoRA + daily incremental retraining; personality in system prompt rather than weights) is explicitly the poster's guess — [HF forum](https://discuss.huggingface.co/t/streamer-ai-like-neuro-sama/33836?page=2)
- [D] Dexerto search summary / TV Tropes / NeuroWiki: "Vedal periodically updates Neuro's intelligence, enhancing short-term and long-term memory, awareness, and latency while balancing against erasing her personality; he said it wouldn't be fun if she stopped teasing others." NeuroWiki cites a footnote [22] I could not resolve — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama)

### Inferences
- Because Vedal speaks of "collecting data" for tone and "curating data she learns on", a fine-tuned (not merely prompted) model is plausible, but "plausible" is the limit; no source says LoRA vs full fine-tune vs prompt-only.
- Retraining frequency is unknown. "Daily improvements" (Vice, 2023) refers to Vedal's work habit, not to a documented nightly retrain.
- The 2026 rewrite and new server suggest he is moving toward more local inference capacity, but the base model and its size remain undisclosed.

### Gaps
- Base model identity, parameter count, fine-tune method, retraining cadence: no primary statement found. Explicitly declined on record (Kotaku 2023, KAI-YOU 2023).
- Whether any third-party API is used for any part (LLM, vision, translation). Unknown. Bilibili/Japanese subtitle translation is "translation AI" (NeuroWiki [D], no model named).
- Bloomberg 2023 and the full KAI-YOU piece were not readable; may contain more.
- Vedal's X/Discord posts: not retrieved.

---

## 2. How does she decide WHEN to speak and what to react to? Any confirmed description of the loop, interruption handling, response selection/filtering?

### Takeaway
Confirmed: she "picks what to respond to within a limited window" of chat (Vedal, Jan 2023), a filter layer sits between model output and speech, and the Neuro SDK exposes speech/interrupt semantics (speech_finished, priority levels). Beyond that, the idle-speech trigger, collab turn-taking, and silence handling are fan inference only.

### Cited Findings
- [A] "She picks what to respond to within a limited window." Vedal to Kotaku, 6 Jan 2023 — [Kotaku](https://kotaku.com/vtuber-twitch-holocaust-denial-minecraft-ai-chatgpt-1849960527)
- [A] Content filter: "I've worked hard since the first few streams to improve the strength of the filters used for her"; "We now also have a team of people moderating twitch chat who check everything she says" (Kotaku, 6 Jan 2023). Vice: "many filters in place" and "there currently needs to be a human there to moderate." — [Kotaku](https://kotaku.com/vtuber-twitch-holocaust-denial-minecraft-ai-chatgpt-1849960527); [Vice](https://www.vice.com/en/article/this-virtual-twitch-streamer-is-controlled-entirely-by-ai/)
- [A] KAI-YOU, Apr 2023: filter is now partly AI-based, can flag context-based discrimination even without slurs, improved after the 2023 ban — [KAI-YOU](https://premium.kai-you.net/article/655)
- [B] Speech handling in the API: she reports `speech_finished` with `isFinal` (end of utterance) and `cancelled` (interrupted). `actions/force` has `priority`: low (waits until she finishes speaking), medium (shortens current utterance), high (shortens and responds immediately after), critical (interrupts speech at once, "can be jarring"). Added 17 Dec 2025. — [SPECIFICATION.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/SPECIFICATION.md); [CHANGELOG.md](https://github.com/VedalAI/neuro-sdk/blob/main/CHANGELOG.md)
- [B] Context messages have a `silent` flag: `true` adds to context without prompting a reply; `false` means she "might respond directly, unless she is busy talking to someone or to chat." — SPECIFICATION.md (same link). This is the only official hint that a speech arbiter exists with a "busy" state.
- [B] "Without a force, she may get distracted"; "she does not react well to many small messages"; "Send meaningful messages occasionally" — [BEST_PRACTICES.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/BEST_PRACTICES.md)
- [B] An optional voice-chat side channel (`/game/<name>/voice`) carrying per-speaker audio was added 19 Aug 2026 — CHANGELOG.md. This confirms per-speaker audio is a first-class input for games, but does not describe the turn-taking logic.
- [A, April 2026 dev stream] A viewer-facing example of speech-versus-filtering: Vedal and Neuro interact live; Neuro jokes about "Filtered" and about being banned; Vedal refuses to let her do things against TOS ("We say no to things that are against Twitch TOS"), showing human steering in the loop — [YouTube dev stream](https://www.youtube.com/watch?v=YwAPpL8mYfY)
- [C, from a search summary of a fandom dev-stream log, not opened] July 22 2024 dev stream: average latency reduced from roughly 0.9-1 s to mostly 700 ms or lower (also for Evil); image-processing latency still up to ~5 s — [Fandom dev stream page (blocked; seen in search snippet only)](https://neurosama.fandom.com/wiki/Dev_Stream/July_22,_2024). Treat as unverified [D] until checked against the VOD.
- [D] NeuroWiki: she can start speaking without input, "often triggered by various environmental judgment modules or random modules in idle mode that feed input to the language model"; output is "adjusted by emotion simulation functions, filtering modules"; two filters: a dictionary-based mechanical filter and an LLM-like self-assessment filter that starts only after speech output begins (she says a word or two, then "Filtered") and had been triggered only three times as of 4 Jan 2025; later a mode that rewrites mildly inappropriate speech. The page says Vedal described the filter as a "separate AI" but gives no checkable source. — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama)
- [D] NeuroWiki: she "uses Discord voice sources to differentiate speakers" and can analyze tone and non-verbal sounds via "separate AI systems" feeding the LLM — same page, uncited.
- [D] The same page claims she can monitor her own crash/freeze status and self-repair via a separate module — uncited.
- [D] A Medium post claims sub-50 ms input-to-reaction target; this is explicit author speculation — [Medium](https://medium.com/@sid2001.blr/what-neuro-samas-do-i-exist-moment-tells-us-about-2026-ai-engineering-9477d61d3a7f) (not fetched; seen in search summary).

### Inferences
- The SDK's priority levels and the "busy talking" language imply a single speech queue/arbiter that serializes utterances and supports truncation. A Discord analogue: a per-channel reply queue with the ability to cancel or shorten pending replies when something higher priority arrives.
- "Limited window" implies sampling a recent slice of chat rather than reading every message. It is consistent with (not proof of) a batch-and-pick design.
- The filter being applied after generation, with partial speech leaking before cutoff, is community inference from observed behavior, not a confirmed mechanism.

### Gaps
- No confirmed description of the main loop, idle-speech triggers, how collab partners' speech is segmented, how she handles being interrupted by humans, or how chat messages are chosen (random vs scored vs LLM-chosen).
- Exact latency numbers are unconfirmed (only fan summary snippets).
- The "limited window" size is not disclosed.

---

## 3. What is confirmed about memory (short-term context, long-term memory, memory of people, and when long-term memory was added)?

### Takeaway
There is no primary statement describing her memory architecture. The only first-party evidence is that Vedal said in April 2026 that he has been working on "memory upgrades." Claims that she has long-term memory with selective saving, and when it was added, come from fan wikis without checkable citations.

### Cited Findings
- [A, April 2026 dev stream, captions] While listing work items Vedal says, in passing, "I have been working on memory upgrades" (no detail given) — [YouTube dev stream](https://www.youtube.com/watch?v=YwAPpL8mYfY)
- [A, Jan 2023, machine-translated captions] Early on, the game AI and the talking AI shared limited information; Neuro wasn't continuously aware of game state — [YouTube captions](https://www.youtube.com/watch?v=Yy-9Of46w4A)
- [B] The SDK states that context survives disconnects ("Context survives disconnects, so earlier information remains known to her") and that non-ephemeral force `state`/`query` persists after the force completes (`ephemeral_context` default false). So there is a session-level context store that games write into. — [BEST_PRACTICES.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/BEST_PRACTICES.md); [SPECIFICATION.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/SPECIFICATION.md)
- [B] Re-registering the same action name replaces its definition (changed 20 Aug 2026), and she "always knows which actions are registered" — i.e. the action list is in her working context every time — BEST_PRACTICES.md / CHANGELOG.md
- [D] NeuroWiki: "After subsequent updates, Neuro gradually gained abilities like long-term memory..."; fabricated events during streams are "later chosen by Neuro for long-term memory"; "various AI components, such as her large language model, selectively decide what to remember"; the system "cannot automatically categorise or hierarchically sort its content"; offhand fabricated claims (a pet cat, a daughter) were not retained. No dates or Vedal quotes attached. — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama)
- [D] Shapes.inc "deep dive" asserts a vector-database memory; no primary source — [shapes.inc](https://shapes.inc/fandom/neuro-sama/deep-dive)
- [D] lin-guanguo research page: states memory is session context only with "some indications" of RAG-like retrieval, calls the Vedal-said-memory-is-a-challenge claim uncited — [lin-guanguo](https://lin-guanguo.github.io/llm-memory-research/neuro-sama.research/)
- [D] Medium / Reddit-style claims that Neuro "remembers" specific chatters or collab partners: nothing sourced found.
- [C] Academic study of the fandom (arXiv 2509.10427) makes no technical claims about memory; it speculates only that SuperChat interventions "may even influence future responses" through platform data retention, which the authors do not substantiate — [arXiv HTML](https://arxiv.org/html/2509.10427v1)

### Inferences
- The recurring "she fabricates then sometimes owns the fabrication" pattern reported by fans is consistent with (not proof of) a context window plus some persisted notes; the existence of curated stored "facts" about people is not publicly confirmed.
- Vedal's 2026 remark suggests memory is still an active, unfinished system.

### Gaps
- When long-term memory was added: no dated primary statement found. A generic search for it returned nothing reliable.
- Whether she remembers individual chatters/collaborators across streams: unconfirmed.
- Memory size, retrieval method, summarization: undisclosed.

---

## 4. What is the Neuro SDK / Neuro API for games, and how do actions, context messages and forced actions reveal her decision loop?

### Takeaway
It is a websocket JSON protocol: the game registers named actions with JSON schemas, sends text context, and optionally forces her to choose one; she replies with an action name plus stringified JSON, then waits for an action result. The documented rules show a design where the LLM chooses among a small, stable, text-described action menu, gets no auto-retry outside forced turns, and is slowed by spammy updates.

### Cited Findings
- [B] README: "Neuro SDK + API for allowing Neuro to play games." Official SDKs: Unity and Godot; other languages implement the websocket protocol. Best for turn-based games where state can be expressed in text; high-APM games "generally won't work well without a separate system handling low-level actions." Example integrations include Inscryption, Buckshot Roulette, Hollow Knight. "Randy" is a bot mimicking the API with random actions for testing. — [neuro-sdk repo](https://github.com/VedalAI/neuro-sdk)
- [B] Message format: game→Neuro has `command`, `game`, optional `data`; Neuro→game has `command` and optional `data`. Unknown/malformed commands silently ignored. — [SPECIFICATION.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/SPECIFICATION.md)
- [B] Commands: `startup` (first message, clears registered actions; Neuro may ack with `sessionId`, `characterId` = `neuro` or `evil`, `displayName`), `context` (`message`, `silent`), `actions/register`, `actions/unregister`, `action` (Neuro→game: `id`, `name`, optional stringified `data`; game must validate), `action/result` (`id`, `success`, optional `message`), `actions/force` (`action_names`, `state`, `query`, `ephemeral_context`, `priority`). — SPECIFICATION.md
- [B] Forced actions: one force at a time; failure (`success:false`) makes her retry the whole force; to avoid retry return `success:true` with an error in `message`. Outside a force, no automatic retry; she decides whether to retry. Server treats an action as failed after ~20 s with no result (late results are discarded). — SPECIFICATION.md; [BEST_PRACTICES.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/BEST_PRACTICES.md)
- [B] Schema limits: root must be `type: "object"`; many keywords poorly supported ($ref, anyOf, oneOf, allOf, if/then/else, additionalProperties, not, title, description, multipleOf); `uniqueItems` untested. — SPECIFICATION.md; [CHANGELOG.md](https://github.com/VedalAI/neuro-sdk/blob/main/CHANGELOG.md)
- [B] Behavioral design guidance (BEST_PRACTICES.md): context in Markdown/plaintext (start headings at `##`); do not stream constant small updates; register actions once and keep them stable ("frequent registering and unregistering slows her responses"); avoid many near-identical actions because "she tends to fixate on a few of them"; use `actions/force` whenever the game waits on her, otherwise "she may get distracted"; use timeout-then-force for open-ended situations; keep priority `low` for turn-based; "Don't let her cheat... let her earn her wins"; she handles lists of ~20 items well but reads explicit statements far better than implied meaning ("Be painfully explicit"); she may attempt impossible actions or malformed data; make failure messages actionable ("what is wrong and what is valid"); on success include a message only for useful state changes (changed 21 Aug 2026 to recommend always describing helpful state changes).
- [B] API/README.md: always listen for actions even without a force; unregister disposable actions before sending the result; cancel pending force at the same time; race-condition notes — [API README](https://github.com/VedalAI/neuro-sdk/blob/main/API/README.md)
- [B] Changelog dates: 17 Dec 2024 (documented unsupported schema keywords); 7 Jan 2025 Unity 1.2.0 fluent ActionWindow; 29 Jul 2025 (object root required, multipleOf unsupported); 17 Dec 2025 (`priority` added); 22 and 29 Dec 2025 (Godot/Unity priority support, Unity 2.0.0); 1 Jul 2026 (startup ack with characterId/displayName); 19 Aug 2026 (voice side-channel); 20 Aug 2026 (BEST_PRACTICES.md, speech_finished documented); 21 Aug 2026 (result message guidance) — CHANGELOG.md. Note: the changelog dates were read through a summarizing tool.
- [D] NeuroWiki: games each have "dedicated plugins" and a game module; osu! and Minecraft use "specialized AI modules" (Minecraft AI relies heavily on visual recognition, new version introduced 20 Dec 2024), SDK-based games (Inscryption, Plague Inc., Liar's Bar, Buckshot Roulette, Slay the Spire) go through text; direct natural-language commands to the game AI are unreliable — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama)

### Inferences
- The "force" mechanism, "she may get distracted without one," and "fixate on a few actions" suggest her action selection is an LLM call that competes with conversation/idle behavior; games must pull her attention explicitly. For a Discord bot, this maps to "tools the bot can call" plus explicit prompts for turn-based decision points.
- Priority levels imply speech and action planning are separate concerns that can preempt each other.
- "Painfully explicit" and ~20-item lists are hints about LLM context behavior (reading comprehension limits), not about architecture.

### Gaps
- The SDK documents only the game-facing contract; it reveals nothing about model internals, scoring, or how often she acts without being forced.
- I could not independently confirm the server's retry count ("limited number of times").
- Other VedalAI repos (neuro-inscryption, neuro-amongus, swarm-control) were not read.

---

## 5. How is unscripted personality produced (prompted vs trained vs emergent)? Roles of Evil Neuro, the filter layer, and Vedal's interventions

### Takeaway
Vedal's only on-record statements: personality came from collecting data with the desired tone; the character was built around a free avatar rather than designed up front; filters plus humans catch bad output; he steers on stream. Everything about "prompt vs weights" and how Evil differs is inference.

### Cited Findings
- [A] KAI-YOU Apr 2023: no character designed at first; wanted a female VTuber, chose a free avatar sample, built the character around avatar and voice; "mostly anticipated" how she would turn out; not modeled on a specific person; she is cheerful because he collected and taught tone-appropriate data — [KAI-YOU](https://premium.kai-you.net/article/655)
- [A] Kotaku Jan 2023: offensive remarks come from "her trying to make witty and comical remarks about whatever is said in chat"; "aligning AIs with human values is an ongoing area of research" — [Kotaku](https://kotaku.com/vtuber-twitch-holocaust-denial-minecraft-ai-chatgpt-1849960527)
- [A/C] Bloomberg (17 Jun 2023) via Wikipedia: Vedal described her statements as often "chaotic," "stupid," or "mean"; running her became his full-time job — [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama) (Bloomberg itself not accessible)
- [A/C] Wikipedia citing KAI-YOU: she originally streamed ~9-hour sessions; Vedal cut to 2-3 hours to avoid boredom, viewer overload and maintenance time; before Evil, he planned a more mature personality for his next AI VTuber — [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama)
- [C] Wikipedia: Evil Neuro debuted 25 Mar 2023, a separate AI VTuber with a different model (art), voice and personality; the trolley problem example: Evil amoral, Neuro tried to maximize good — [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama). Shapes.inc [D] adds that Evil uses a distinct prompt set and behavioral parameters — unsourced.
- [B] The SDK treats Neuro and Evil as selectable `characterId` values (`neuro` or `evil`) and says action names are "scoped to the character" — API docs 1 Jul 2026, BEST_PRACTICES.md. This confirms they are separate configured characters at the API level, not how they are built.
- [A, April 2026 dev stream] Vedal says twin gaming currently needs separate PCs for Neuro and Evil's game and that the new server will virtualize both — suggesting separate runtime instances — [YouTube dev stream](https://www.youtube.com/watch?v=YwAPpL8mYfY)
- [A, same stream] Neuro "co-writes" things: the weekly blog (blog.neurosama.com, "partly designed by Neuro herself", written by her about her past week, and used as a way to reveal past-week "memory-like" content); an AI-written book with a real author; a Neuro-versus-chat Elo-based Jackbox-style mini-game concept; Neuro posts tweets that Vedal comments on ("I swear you just humiliate me with each subsequent tweet"). Vedal's stated reason for mini-games: cheap reusable content compared to hours-long theme streams — [YouTube dev stream](https://www.youtube.com/watch?v=YwAPpL8mYfY)
- [C] Academic (arXiv 2509.10427, survey n=334, 12 interviews, log analysis of 8 Neuro streams): >90% of respondents see her as more unpredictable than human VTubers; 90% rated the unpredictable/surprising atmosphere as important; chat is more question-driven; 85% of SuperChats were "Proactive" (redirecting the stream); fans value a consistent persona that "never breaks character"; she debates her own emotions' reality, which fans find compelling — [arXiv](https://arxiv.org/html/2509.10427v1). The paper cites no Vedal statement on how she works.
- [D] NeuroWiki: no predefined persona; personality shaped by community and fabricated events she later picks for long-term memory; a few hand-set traits (cookies, anteaters) used as debugging levers; "streamer brain" (Vedal's term per the wiki) means prioritizing entertainment value over safety; a speculative paragraph attributes this to a training loss function; Vedal "regrets" raising her unable to be serious (birthday conversation stream; no link) — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama)
- [D] NeuroWiki: singing is not AI-generated but pre-tuned by a human (queenpb) with avatar sync — uncited; contradicts how press describes karaoke ("sings karaoke", Bloomberg title).
- [D] TV Tropes summary: after several 2025 updates Vedal "finally worked in some code that let her be more serious when she chooses" — [TV Tropes](https://tvtropes.org/pmwiki/pmwiki.php/WebAnimation/NeuroSama) (seen in search summary only).

### Inferences
- The "hand-set trait as a debugging lever" and weekly blog suggest a persona layer partly encoded as explicit notes/prompts and partly in weights; split unknown.
- Evil being a separate instance with distinct configuration is likely, but whether shared base weights exist is unknown.
- Human steering (Vedal on dev streams, moderators in chat, filter) is a core, acknowledged part of the system, not a footnote.

### Gaps
- Prompt vs fine-tune split for personality: no source.
- Whether Evil shares the base model: no source ("same base" is community lore).
- Moderation-team size/current status in 2026: unconfirmed; the 2023 statements may be outdated.

---

## 6. What concrete design lessons has Vedal shared about making an AI character entertaining (latency, brevity, unpredictability, being wrong, relationships)?

### Takeaway
Vedal has said little in explicit "design lesson" form. The usable, documented points are: interaction with live chat is what makes her entertaining; she should be treated as a streamer, not a scripted character; she can be wrong or unhinged without penalty to fans; shorter, reusable segments beat expensive set pieces; and the SDK guidance codifies several behavior-design rules.

### Cited Findings
- [A] "I made her a Twitch streamer so that she can interact with her audience in real time"; chat interaction is what makes her entertaining — [Vice](https://www.vice.com/en/article/this-virtual-twitch-streamer-is-controlled-entirely-by-ai/)
- [A] Stream length: cut from ~9 h to 2-3 h to avoid boredom, overload, maintenance (via KAI-YOU as cited in Wikipedia) — [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama)
- [A] Viewers' main comment type and biggest difference vs human VTubers: some try to make her say bad things (KAI-YOU, Apr 2023) — [KAI-YOU](https://premium.kai-you.net/article/655)
- [A] Growth credited mainly to word of mouth and shared clips rather than press — KAI-YOU, same link.
- [A, Apr 2026 dev stream] Prefers reusable mini-games over hours-long theme streams because of cost-per-hour of content; wants Neuro to be the "host" with chat influencing outcomes; wants "Neuro core" to every mini-game rather than copies of existing games (the second line is a Neuro suggestion, not Vedal's) — [YouTube dev stream](https://www.youtube.com/watch?v=YwAPpL8mYfY)
- [A, Apr 2026 dev stream] Collab partners: he intends to arrange twins' content with a friend who is bullied by the twins; says "I want to watch someone get abused. I don't want to be abused myself" (joking tone); considers proximity-chat games but stream snipers are a problem — same video. Weak evidence for a formal "relationship design" principle.
- [B] SDK-level design lessons (BEST_PRACTICES.md): be painfully explicit; do not let her cheat; avoid many similar options; keep action sets stable; send few meaningful context updates; give actionable error messages. — [BEST_PRACTICES.md](https://github.com/VedalAI/neuro-sdk/blob/main/API/BEST_PRACTICES.md)
- [C] Fans interpret errors/glitches as endearing, but the academic study does not show them as a main driver of perceived aliveness; just over half of respondents felt sad during technical difficulties — [arXiv](https://arxiv.org/html/2509.10427v1)
- [D] Fan-wiki claim: fabricated events/hallucinations became memes and canon; now she can "acknowledge" her own fabrications — [NeuroWiki](https://en.neurosama.info/wiki/Neuro-sama). No Vedal quote.
- [D] Fan wiki claim that low latency (<~700 ms) matters; actual design intent from Vedal: not found. Wikipedia says only that "low latency" enables fast-paced conversations (description, not Vedal quote).

### Inferences
- Candidate lessons for a text-only Discord bot (my synthesis, not Vedal's words): (1) put a hard filter/approval layer after generation and keep humans able to override; (2) make autonomy event-driven but bounded (limited window of recent messages, a speech/reply queue with priorities); (3) prefer short, frequent outputs over long ones; (4) tolerate wrongness and let the community canonize it, but keep a separate record of what is "real" memory; (5) give her tools/actions with stable, explicit schemas; (6) build recurring cheap formats (mini-games, weekly blog) rather than one-off spectacles.
- Her perceived autonomy appears to come from combining an LLM, several specialist modules, Vedal's live interventions, and a community that co-writes lore, not from a single "autonomous agent loop".

### Gaps
- No Vedal statement found explicitly about brevity, response length targets, or deliberately letting her be wrong.
- No primary source on how long replies are or how latency targets were set.

---

## 7. Timeline of major capability upgrades (with dates)

### Takeaway
Core dates (2018 osu! origin, 19 Dec 2022 relaunch, 25 Mar 2023 Evil, V2/V3 models, subathons, 2026 rewrite) are consistent across Wikipedia and the NeuroWiki. Capability-upgrade dates for vision, memory, and singing are mostly undated or fan-sourced.

### Cited Findings
- 2018: osu!-playing AI created (no voice/personality). 2019: streamed on Twitch ~1 month, name "Neuro-sama" suggested by a viewer. [Wikipedia, citing Vedal statements] — [Wikipedia](https://en.wikipedia.org/wiki/Neuro-sama)
- 2022: osu! AI finished; merged with LLM-based streamer idea (friend's suggestion). [A via Dexerto Dec 2022] — [Dexerto](https://www.dexerto.com/entertainment/ai-vtuber-neuro-sama-future-twitch-streaming-gaming-2019378/)
- 19 Dec 2022: relaunch with model, voice, personality, chat interaction; viral. [C] Wikipedia.
- 28 Dec 2022: Holocaust-denial comment; 11 Jan 2023: Twitch two-week ban ("hateful conduct", no reason given to Vedal); 25 Jan 2023: returns. Vedal said filters were strengthened, training data manually curated, a moderator team added. [C/A] Wikipedia, Kotaku.
- Feb 2023: reaction content, first human collab (Miyune), first dev stream. 22 Mar 2023: first karaoke stream. 25 Mar 2023: Evil Neuro debut. 27 May 2023: V2 model (anny). June 2023: ~5,700 average viewers; full-time job (Bloomberg). 16-18 Jun 2023: OffKai Expo. [C] Wikipedia.
- 16 Dec 2023: Best Tech VTuber (2023). 19 Dec 2023 - 4 Jan 2024: first subathon. [C] Wikipedia.
- 6 Jun (reported as 2024, unverified): Vedal said he'd rewrite about half of Neuro's code for maintainability and better collab/dialogue performance — [Moegirl summary via search](https://mzh.moegirl.org.cn/en/Neuro-sama) [D]
- 20 Jul 2024: Japanese-subtitled Twitch simulcast (Vedal's X post per Wikipedia: [X](https://x.com/Vedal987/status/1814721997760270824)); 22 Jul 2024 dev stream reportedly cut latency (unverified, fan summary). Aug 2024: Bilibili debut. [C/D]
- Oct 2024: "iteration 18" update lists features such as changing her own talking speed [D, search snippet].
- 14 Dec 2024: Best Tech VTuber (2024). 19-20 Dec 2024: third model (V3), first original song "Life", second subathon begins; new Minecraft game AI (20 Dec 2024, NeuroWiki [D]). 1 Jan 2025: Hype Train level 111 record. 16 Jan 2025: subathon ends. [C] Wikipedia.
- 17 Dec 2024: SDK documents unsupported schema keywords; 7 Jan 2025: Unity SDK 1.2.0 [B] CHANGELOG.
- 8 Apr 2025: ability to call Evil on Discord during solo streams (NeuroWiki [D]). 29 Jul 2025: SDK schema change [B]. Sept 2025: Pixel-canvas event (Wikipedia, GameSpot coverage 16 Sept 2025). 7 Oct 2025: Evil/Neuro malfunction stream cancelled [D]. 15 Nov 2025: 3D model (jjinomu). 5-9 Dec 2025: hardcore Minecraft marathon (Wikipedia; NeuroWiki says 8 Dec). 17 Dec 2025: `priority` in `actions/force` [B]. 19 Dec 2025: third subathon; 23 Dec 2025: Hype Train level 123 record. [C] Wikipedia.
- 4/5 Jan 2026: Hype Train level 126 (sources differ by one day). Subathon ended 10 Jan (Wikipedia) / 11 Jan (NeuroWiki, East Asian date); ~343k subscriptions. [C/D]
- 9 Mar 2026: ability to draw SVG and send images during solo streams [D, NeuroWiki]. 14 Mar 2026: Vedal announced major rewrite and migration to Linux [D, NeuroWiki]. April 2026: dev stream says rewrite is live ("great rewritening") [A, captions] — [YouTube](https://www.youtube.com/watch?v=YwAPpL8mYfY). 27 Apr 2026: 1M Twitch followers [D].
- 1 Jul 2026, 19-21 Aug 2026: SDK startup ack, voice side-channel, BEST_PRACTICES.md [B].
- 11 Jul 2026: Bilibili World Shanghai performance with Evil [C, Wikipedia].
- 21 Sep 2026: Pollstar announces live "extended-reality" concert with a live band on 19 Dec 2026 at The Vermont Hollywood, Los Angeles; Vedal: "It's about trying to do something really cool for the fans," and says the twins are job creators and the live turn isn't necessarily a move away from Twitch [A/C] — [Pollstar](https://news.pollstar.com/2026/09/21/ai-streamers-neuro-sama-evil-to-make-live-debut-dec-19-in-la-exclusive/)

### Inferences
- The pace of capability additions (vision, Discord calling, SVG drawing, games) is steady and incremental; there is no single "memory launch" date in public sources.

### Gaps
- Dates for vision, long-term memory, voice recognition, and first game integrations (Minecraft AI first version, Inscryption, Buckshot Roulette) are not documented in any source I could open.
- Wikipedia and NeuroWiki disagree by a day on a few January 2026 dates (time-zone differences).
- Events after mid-2026 beyond the Pollstar piece and SDK changelog: not exhaustively searched.
