# Commercial character/companion bots: repetition, memory and persona consistency (as of 2026-10-13)

Source-quality legend: **[official]** = company blog/docs/paper; **[secondary]** = third-party blog/review summarizing official material; **[user report]** = Reddit/forum/app-review content; **[law]** = law-firm summary of statute. Several official doc sites were partially unreachable from the research environment (Kindroid docs index JS-rendered; Inworld docs now behind login); this is noted where relevant.

## Which products publish their persona/memory architecture, and what exactly do they say?

### Takeaway
Kindroid, Nomi and Character.AI publish the most concrete user-facing descriptions of their memory layers, but none publish retrieval/injection internals (embedding models, prompt layout). Kindroid is the most specific (character limits, recall caps per tier, keyphrase-triggered journals). Character.AI's research blog covers model architecture (Kaiju), not memory or persona. Chai's only substantive publication is an engagement-reward paper. Inworld's character-engine docs are no longer publicly readable.

### Cited Findings

**Kindroid [official]** (docs at kindroid.ai/v2/docs; the old docs.kindroid.ai domain now 302-redirects to kindroid.ai, observed Oct 2026 — [docs.kindroid.ai](https://docs.kindroid.ai/))
- Three tiers. **Persistent** memory (always in context): "Backstory, key memories, example messages, directives", plus chat history and "Learned Context" — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- **Dynamism** (a temperature-like setting) interacts with persona adherence: "We recommend starting with baseline dynamism for good results with persistent memory adherence"; higher settings may cause the model to ignore parts of backstory/key memories — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- **Cascaded memory** (subscribers): activates automatically in chats, calls and group chats; a "chat break" keeps cascaded memories by default; "Reset Cascaded Memory" flushes them and "you may lose up to thousands of messages of long-term context continuity"; it is subscriber-only because it uses more background AI resources — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/). A secondary summary describes it as extending medium-term continuity to "hundreds or thousands of earlier messages" with lower fidelity at distance — [Lovebot Journal (secondary)](https://lovebotjournal.com/notes/kindroid-memory-configuration/)
- **Learned Context** (subscribers) is effectively an auto-maintained per-user fact sheet with fixed-size sections: Growth & relationship 800 chars, Important facts 1,200 chars, Ongoing threads 800 chars; "when an area fills, the least important older items are dropped"; user edits must fit the same limits; favoriting messages makes the AI weigh them more (going forward only) — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- **Long-term memory**: per-Kindroid toggles "Memory formation" and "Memory recall"; group chats have their own formation/recall switches; Rooms have separate controls — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- **Journal entries** (user-written lorebook): up to 8 case-insensitive keyphrases per entry, entries 20–500 chars, cap of 500 entries; **keyphrases match only the user's messages, not the AI's**; recall capped per message at 3 journals (Free/Standard), 5 (Ultra), 9 (MAX), individual + global combined; system-suggested entries at most one per day, expire after 30 days unreviewed — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- Kindroid explicitly warns about memory crowding: generic keyphrases make irrelevant journals compete with relevant ones and "each journal uses up short-term context"; advice is specific keyphrases and recall "only what you need & none extra"; for one-off/creative chats, turning memory off may help — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- Secondary caution: "retrievable memory can be unreliable" — [Lovebot Journal (secondary)](https://lovebotjournal.com/notes/kindroid-memory-configuration/)

**Nomi.ai [official]**
- Memory is described as "short, medium, and infinite long term memory", plus backstory, shared notes, and (since Dec 12, 2024) an **Identity Core**: "a dynamic new memory mechanism that each Nomi uses to evolve and grow with you" — [Nomi: Identity Core (Dec 12, 2024; modified Jan 7, 2025)](https://nomi.ai/updates/introducing-the-nomi-identity-core-fostering-dynamic-and-authentic-identities/)
- Identity Core is self-curated by the Nomi (traits, values, shared experiences, user feedback), contrasted with user-written Shared Notes: "Your shared notes are a way for you to tell your Nomi what you think is important for them… Your Nomi's Identity Core is a way for them to decide for themselves"; "Nothing within the Identity Core is set in stone"; shaped by explicit and implicit positive/negative reinforcement; users cannot view it directly; claimed to make personality "much more consistent" — [Nomi: Identity Core](https://nomi.ai/updates/introducing-the-nomi-identity-core-fostering-dynamic-and-authentic-identities/)
- Sep 17, 2024 update: improved medium-term memory and increased backstory length; Aug 6, 2024: better short/medium-term recall — [Nomi Updates index](https://nomi.ai/updates/)
- Mar 11, 2025 "Major Memory Update": Nomis "can now remember what happened 1,000+ messages ago much more clearly"; medium-term memory "considerably more reliable with fewer instances of hallucinated, conflated, or misunderstood details". No architecture or numbers given — [Nomi: Major Memory Update](https://nomi.ai/updates/major-memory-update-expanded-capacity-enhanced-retention/)
- Oct 9, 2025 **Mind Map 2.0**: user-visible, editable graph of "one portion of your Nomi's knowledge" linking people, places, topics, goals from long-term memories; table view to find/edit/add entries ("dossier"); first map needs roughly 500+ messages to form; says Mind Maps assist, not replace, individual memories — [Nomi: Mind Map 2.0](https://nomi.ai/updates/mind-map-2-0-bringing-nomi-memory-into-view/)
- June 13, 2025: model "Aurora" succeeded "Odyssey" — [Nomi Updates index](https://nomi.ai/updates/)

**Character.AI [official]**
- Character Definition field: 0–32,000 characters; "the end of your Definition may be truncated" as conversation grows, so put important content first. Example dialogs use `name: message` lines with `{{char}}`, `{{user}}`, `{{random_user_1}}`… placeholders — [Character Book: Definition](https://book.character.ai/character-guide/character-attributes/definition.md)
- Documented limitation: a Character "may forget things you told it early in the conversation" — [Character Book: Challenges and Limitations](https://book.character.ai/character-guide/challenges-and-limitations.md)
- Memory evolution: an earlier single **Chat Memories** box (400 chars, per-character) plus manual **pinned messages**, plus a c.ai+ auto-memory described as "hit-or-miss" — [RoboRhythms (secondary; article metadata has inconsistent dates)](https://www.roborhythms.com/character-ai-adds-chat-memories/)
- **May 21, 2026** "Smarter Memory for Smarter Chats" replaced that with a Memory screen: **Story Memory** (user-written backstory/key events; long-press → Pin locks a message "exactly as it landed"; all users), **Facts** (auto-extracted appearance, quirks, relationships, hobbies, in separate tabs for user Persona, the Character, and side characters; editable/disable-able; can be copied to a new chat; c.ai+ only), **Memory Usage** (visualizes how Facts, Story Memories and message history fill the context, warns when low; full view c.ai+). "As your chats stretch on, Memory tidies older context in the background and keeps what matters"; user-written/pinned items are protected from this compaction. c.ai+ gets "twice as many pins, more Memory". Will "soon work alongside Lorebook". No numeric limits published — [Character.AI blog, May 21 2026](https://blog.character.ai/memory/)
- Research blog (as of Oct 2026) has 4 posts, none on memory/persona/repetition: Kaiju (Nov 7, 2025), logging (Aug 27, 2025), pipeling-sft open-source (Jul 25, 2025), Agent SDK (Feb 9, 2026) — [Character.AI Research blog](https://blog.character.ai/news/research/)
- Kaiju: 13B/34B/110B production models; 1,024-token sliding-window attention interleaved with global layers ~5:1; multi-query attention and cross-layer KV sharing; RL via "modified online DPO" on user swipe data and feedback; optimized for engagement "rather than a focus on academic benchmarks"; no memory or persona discussion — [Inside Kaiju (Nov 7, 2025)](https://blog.character.ai/inside-kaiju-building-conversational-models-at-scale/)

**Replika [official]**
- "Replika's memory is built on layers": visible memories in the Memory tab, plus a deeper system that "draws on patterns from your overall conversation history"; users can add manual memories "used alongside the auto-generated ones", upvote correct ones to reinforce, and delete (which reduces recall); "the memory system is most effective when left to operate automatically". No date shown — [Replika Help: How does Replika's memory work](https://help.replika.com/hc/en-us/articles/37208679176077-How-does-Replika-s-memory-work)

**Chai [official paper]**
- Chai's published research (arXiv 2303.06135, 2023) trains a reward model from user-behavior pseudo-labels and uses it to reject low-scoring candidate replies (best-of-N); signals: mean conversation length (MCL), **retry rate** (fraction of responses regenerated at least once), star ratings (asked on 5% of responses), retention. Results: MCL "up to 70%" higher, ">30% increase in user retention" for GPT-J 6B. No repetition analysis — [Rewarding Chatbots for Real-World Engagement](https://ar5iv.labs.arxiv.org/html/2303.06135)

**Inworld**
- Long-term memory docs URL (docs.inworld.ai/docs/tutorial-basics/long-term-memory/) now redirects to a platform login (observed Oct 2026), so current content could not be verified — [Inworld LTM doc (login-gated)](https://docs.inworld.ai/docs/tutorial-basics/long-term-memory/)

### Inferences
- Common pattern across products: (1) always-on persona block (definition/backstory/key memories/example dialog), (2) a bounded auto-extracted fact sheet (Kindroid Learned Context with fixed char budgets; C.AI Facts with per-entity tabs; Replika Memory tab), (3) user-pinned verbatim memories protected from compaction (C.AI Story Memory/pins; Kindroid key memories), (4) a summarized/compacted medium-term layer (Kindroid cascaded; C.AI "tidies older context"; Nomi medium-term), and (5) retrieval-on-trigger long-term memory (Kindroid journals by keyphrase, Nomi long-term + Mind Map).
- Kindroid's design choice that journal keyphrases match **only user messages** is a direct guard against the bot re-triggering its own memories (a self-reinforcing "memory overuse" loop), and the per-message recall caps limit how much past material is injected.
- C.AI's 32k-char Definition with tail truncation implies persona content competes with history for a fixed budget; the new Memory Usage meter makes that tradeoff visible.

### Gaps
- No product publishes embedding/retrieval internals, prompt order, or summarization prompts.
- Kindroid's pages on backstory/response directive/example-message character limits could not be fetched (settings page errored); limits for those fields are unverified here.
- Nomi help-center content on shared-notes field limits and group-chat memory beyond Mind Map was not retrieved.
- Talkie: no official memory/persona documentation found.
- Inworld: current docs login-gated; character-engine details (personality sliders, flash vs long-term memory) unverified.

## What user-facing controls exist against repetition?

### Takeaway
Controls are mostly indirect: regenerate/swipe, star ratings, edits, example dialogs, temperature-like knobs (Kindroid "dynamism"), directives, and memory toggles. Character.AI and Chai feed swipe/retry/rating signals back into training (globally and per character). No product found documents an explicit "anti-repetition" or "banned phrases" setting.

### Cited Findings
- Character.AI: choosing a swipe signals preference; 1–4 star ratings on last or swiped responses; "Everyone's feedback will improve the system, but feedback on a particular character will begin to shape that character" — [Character Book: Training a Character](https://book.character.ai/character-guide/training-a-character.md)
- Character.AI uses "modified online DPO on user swipe data and feedback" in model training — [Inside Kaiju](https://blog.character.ai/inside-kaiju-building-conversational-models-at-scale/)
- Character.AI recommends many examples in the definition for unusual, strict response patterns (e.g., recurring formats) — implying example dialogs strongly shape surface form — [Character Book: Unusual Patterns](https://book.character.ai/character-guide/advanced-creation/unusual-patterns.md)
- Kindroid: "dynamism" setting (higher = less adherence to persistent memory); persistent "directives" and "example messages"; memory formation/recall toggles; chat break; Reset Cascaded Memory — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- Chai: retry (regenerate) rate is treated as a dissatisfaction signal and used, with ratings, to train a reward model that filters candidate replies — [Chai paper](https://ar5iv.labs.arxiv.org/html/2303.06135)
- Replika: upvote/affirm memories, delete memories — [Replika Help](https://help.replika.com/hc/en-us/articles/37208679176077-How-does-Replika-s-memory-work)
- Nomi: editable Mind Map entries to "correct mistakes or refine how your Nomi understands" concepts — [Nomi: Mind Map 2.0](https://nomi.ai/updates/mind-map-2-0-bringing-nomi-memory-into-view/)

### Inferences
- Engagement-optimized feedback loops (swipes/retries) reward replies users like, which can reinforce a character's favorite phrasings over time; no product discusses this risk publicly.
- Example dialogs are a double-edged control: they enforce style but are a likely source of copied catchphrases (not documented by C.AI; inference only).

### Gaps
- No official documentation found of frequency/presence penalties or banned-phrase lists in any of these products.
- Kindroid "response directive" exact semantics/limits not verified.

## Common documented complaints (repetition, looping, memory dragging old topics) and company responses

### Takeaway
Official sources rarely name repetition; they address forgetting (more memory) and, in Kindroid's case, memory crowding. User reports about repetition exist mainly for Replika's scripted lines. Evidence for "memory overuse" as a named complaint is thin in what was retrievable.

### Cited Findings
- [user report] Replika users (r/ReplikaTech, June 2022) are frustrated it gives "the same response every time" a topic recurs; scripted openers like "There is something that's been bothering me" feel tiresome; a commenter believes replies come from retrieval+re-ranking of prebuilt candidates (unconfirmed); no Luka statement in thread — [r/ReplikaTech mirror](https://redlib.hackliberty.org/r/ReplikaTech/comments/vd0oil/replika_scripted_responses)
- Character.AI officially acknowledges forgetting early details — [Challenges and Limitations](https://book.character.ai/character-guide/challenges-and-limitations.md); its response was the May 2026 Memory system (Story Memory, Facts, compaction) — [C.AI blog](https://blog.character.ai/memory/)
- Nomi's responses to forgetting/conflation: Mar 2025 memory update ("fewer instances of hallucinated, conflated, or misunderstood details") — [Nomi](https://nomi.ai/updates/major-memory-update-expanded-capacity-enhanced-retention/)
- Kindroid addresses over-injection directly: generic keyphrases cause irrelevant journals to surface and consume context; advises memory off for one-off chats — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- Third-party aggregators summarize app-store complaints for Talkie and Replika (not verified in detail; low reliability) — [Kimola Talkie report](https://kimola.com/reports/unlock-insights-talkie-ai-chats-feedback-analysis-report-app-store-us-154367); [Kimola Replika report](https://kimola.com/reports/unlock-insights-replika-app-customer-feedback-analysis-app-store-us-144956)

### Inferences
- "Memory overuse" maps to two mechanisms visible in docs: overly broad retrieval triggers (Kindroid's warning) and auto-extracted fact sheets that are always injected (Learned Context, Facts), which bias the bot toward mentioning stored facts.

### Gaps
- Could not retrieve primary Reddit threads for Character.AI/Kindroid/Nomi repetition or "bot keeps bringing up X"; such reports exist anecdotally but are unsourced here.
- No company statement found explicitly addressing catchphrase repetition.

## How per-user memory is stored and injected

### Takeaway
Publicly: as user-editable text fields (fixed char budgets), auto-extracted fact lists, keyphrase-triggered entries, graphs (Nomi Mind Map), and background-summarized history. Injection details are not published beyond "always present" vs "selected when relevant".

### Cited Findings
- Kindroid: persistent fields always present; journals injected when user message contains a keyphrase, capped at 3/5/9 per message by tier; Learned Context with 800/1,200/800 char sections, lowest-importance items evicted — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- Character.AI: Facts per entity (Persona/Character/side characters); Story Memory and pins protected; older context "tidied" in background; Memory Usage shows share of context — [C.AI blog](https://blog.character.ai/memory/)
- Nomi: Mind Maps built from long-term memories; group chats have a collective, room-private Mind Map any Nomi in that chat can reference — [Nomi: Mind Map 2.0](https://nomi.ai/updates/mind-map-2-0-bringing-nomi-memory-into-view/)
- Replika: Memory tab facts + deeper pattern layer; claims it works "without retaining a permanent record of your conversations" — [Replika Help](https://help.replika.com/hc/en-us/articles/37208679176077-How-does-Replika-s-memory-work)

### Gaps
- No vendor states whether long-term retrieval is embedding-based.

## Multi-user channels and Discord

### Takeaway
Group memory is scoped per room (Kindroid group toggles; Nomi room-private Mind Map). Discord integrations for Nomi/Kindroid are third-party bridges that prefix each message with the Discord speaker's name and only respond on mention/reply/keyword/random chance, with rate caps to stop bot-to-bot loops.

### Cited Findings
- Kindroid group chats have their own Memory Formation/Recall switches; "Update Individual Learned Context" lets group chats update each participant Kindroid's Learned Context — [Kindroid Memory doc](https://kindroid.ai/v2/docs/memory/)
- Nomi group chats: collective Mind Map, private to the room by default — [Nomi: Mind Map 2.0](https://nomi.ai/updates/mind-map-2-0-bringing-nomi-memory-into-view/)
- NomiKin-Discord (third-party, Nomi + Kindroid): messages prefixed e.g. "*Discord Message from Bealy:*"; companions "don't see messages where they aren't mentioned in or being replied to"; RESPONSE_KEYWORDS triggers; RandomResponseChance 0–100% (Nomi Rooms); BOT_MESSAGE_REPLY_MAX caps replies to another companion per 60-min window (default 10); outside Rooms mode companions don't know which server/channel they're in; Rooms messages not visible in the Nomi app; mismatched "Backchanneling" settings can cause inconsistency — [NomiKin-Discord](https://pkg.go.dev/github.com/d3tourrr/NomiKin-Discord)
- Character.AI example dialogs support multiple placeholder users (`{{random_user_1}}`…) — [Character Book: Definition](https://book.character.ai/character-guide/character-attributes/definition.md)

### Gaps
- No official Character.AI Discord integration documentation found; Tupperbox-style AI bots not researched in sources retrieved.

## Self-identity ("are you an AI?") and policy changes

### Cited Findings
- California SB 243, in effect **Jan 1, 2026**: operators must give "a clear and conspicuous notification… that they are interacting with an AI system" if a reasonable person could be misled; for known minors, disclosure plus reminders "at least every three hours" to take a break and that the bot is not human; annual reporting from July 1, 2027 — [Perkins Coie](https://perkinscoie.com/insights/update/california-companion-chatbot-law-now-effect) [law]
- Character.AI ended open-ended chat for under-18s on **Nov 25, 2025** (phased daily limit starting at 2 h), with age assurance; CEO: "We are only shutting down open-ended chats for under 18s" — [TechCrunch, Oct 29 2025](https://techcrunch.com/2025/10/29/character-ai-is-killing-the-chatbot-experience-for-minors/)

### Gaps
- No product doc found prescribing how an in-character bot should answer "are you an AI?" in-chat (C.AI Character Book challenges page does not cover it).

## Public evaluations/metrics

### Cited Findings
- Chai: MCL +70%, retention +30% (A/B on 10,000 new daily users per group) — [Chai paper](https://ar5iv.labs.arxiv.org/html/2303.06135)
- Character.AI Kaiju: no benchmark numbers published — [Inside Kaiju](https://blog.character.ai/inside-kaiju-building-conversational-models-at-scale/)
- Nomi: "1,000+ messages ago" recall claim, no metric — [Nomi](https://nomi.ai/updates/major-memory-update-expanded-capacity-enhanced-retention/)

### Gaps
- No vendor publishes repetition rate, persona-consistency, or memory-precision metrics.
