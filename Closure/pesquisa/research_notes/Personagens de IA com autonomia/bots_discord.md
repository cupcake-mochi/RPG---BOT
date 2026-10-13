# Discord character bots in multi-user servers: reply gating, proactivity, memory, personas, policy, cost and failure modes

Research date: 2026-10-13. Method note: the WebFetch/WebSearch tools returned page summaries produced by a small model, not raw text. The Discord Developer Policy and Developer Terms pages returned HTTP 403 on every attempt, so their text was NOT read directly (see Gaps in section 5). Anything tagged (anecdotal) comes from forums, listings or vendor blogs and is not independent evidence.

## 1. Reply gating in group channels (when to answer when not mentioned)

### Takeaway
Real bots use a layered gate. Hard triggers (mention, reply to the bot, wake word or name) always answer. Everything else goes through a cheap probabilistic or classifier stage, with per-channel caps and bot-to-bot filters. The most detailed open-source example is oobabot, which uses a time-since-last-summon probability table. A published 2026 group-chat write-up recommends a small LLM classifier with three outputs (respond/react/ignore).

### Cited Findings
- oobabot has three trigger types: @-mentions, DMs, and wakewords (CLI default `['oobabot']`). It also does "unsolicited" replies: random chance of posting in a channel where others write within a window after its last post (README says parameters "are in flux"). — [oobabot README](https://github.com/chrisrude/oobabot)
- oobabot `docs/config.sample.yml` defaults: `disable_unsolicited_replies: False`, `unsolicited_channel_cap: 3` (only the N most recently summoned channels get unsolicited replies; 0 = no limit; mentions and wakewords still work anywhere), `reply_in_thread: False`, `history_lines: 7`, `stream_responses_speed_limit: 0.7` (seconds between streamed edits, to avoid Discord rate limits), `stop_markers: ['### End of Transcript ###<|endoftext|>', '<|endoftext|>']`. — [config.sample.yml](https://raw.githubusercontent.com/chrisrude/oobabot/main/docs/config.sample.yml)
- oobabot `settings.py` (not user-configurable constants): the chance of an unsolicited reply is 90% within 60 s of being pinged in that channel, 70% within 120 s, 50% within 300 s, otherwise 0; an "interrobang bonus" of 0.3 is added when the message ends with `?` or `!`. — [settings.py](https://raw.githubusercontent.com/chrisrude/oobabot/main/src/oobabot/settings.py) (summary of a model-read file; verify numbers in the repo)
- oobabot `decide_to_respond.py` order of checks: ignore messages from other bots (loop prevention) and from itself; mentions/DMs/wakewords always reply; for channel messages, skip if someone else is mentioned and the bot is not, skip empty messages, skip if unsolicited disabled, look up base chance by time since last mention, add interrobang bonus, roll a uniform random number. State is kept per channel in `LastReplyTimes`, using message timestamps, purged by the longest window. — [decide_to_respond.py](https://raw.githubusercontent.com/chrisrude/oobabot/main/src/oobabot/decide_to_respond.py)
- oobabot known issue: the model sometimes continues the conversation on behalf of other chat members, and the author truncates this with hacks that can make replies terse. — [oobabot README](https://github.com/chrisrude/oobabot)
- llmcord does no ambient gating. It answers only when @-mentioned (in a reply, in a thread, or in DMs). The reply chain is the conversation history, stored in Discord with no database. Config: `max_messages: 25` (oldest dropped first), `max_text: 100000`, `max_images: 5`, `allow_dms: true`, `permissions` with `users`/`roles`/`channels` and `allowed_ids`/`blocked_ids`, system prompt with `{date}`/`{time}`, and a recommendation to tell the model that user messages are prefixed with `<@ID>`. — [llmcord README](https://github.com/jakobdylanc/llmcord)
- SillyTavern group chats offer four reply-order strategies. Manual (only a chosen member answers, `/trigger`), Natural Order (mention detection, then talkativeness-based activation, then random pick among the activated), List Order, Pooled Order (random among characters who have not spoken since the last user message). Mentions are whole-word matches. Per-character "talkativeness" runs 0% (answers only when named) to 100%, default 50%; if nobody activates, one speaker is chosen at random. Auto-mode starts the next turn 5 s after the last character message. — [SillyTavern docs: group chats](https://docs.sillytavern.app/usage/core-concepts/groupchats/)
- evil-bot (Ollama persona bot, tiny repo, anecdotal for quality) ships random replies on by default: `DEFAULT_RANDOM_ENABLED=True`, `DEFAULT_RANDOM_CHANCE=10` (percent), `DEFAULT_TRIGGER_WORDS="evil,evil bot,good,good bot"`, `MAX_CONTEXT_MESSAGES=5`, storage in SQLite (`bot_settings.db`), commands `!set`, `!get`, `!default`, `!trigger`, `!random`. — [sistav/evil-bot](https://github.com/sistav/evil-bot)
- AutoResponse (discord.js, preset phrases not LLM): per-channel reply probability starts at 6% and rises 1% per message up to 100%, resets to 6% after a reply, then a channel cooldown (duration not stated) stored in `replyCooldowns.db`; opt-in channels via `/addreplychannel`. — [AutoResponse docs mirror](https://mintlify.wiki/notdylandover/AutoResponse/introduction)
- discord-gpt (PHP) has `app.slowModeTime` (minimum seconds before answering the same user again) and `app.reactionWords` (keyword triggers). — via search snippet, [ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fkarhal%2Fdiscord-gpt) (not verified in repo)
- AktivaAI (archived 20 Jun 2025, successor viel-ai): characters answer when their name is said or one of their messages is replied to; per-channel character whitelists via `/set_whitelist` and `/clear_whitelist`; `//` prefix keeps a message out of the AI's context; per-channel/thread memory. No cooldown option documented. — [AktivaAI](https://github.com/Iteranya/AktivaAI)
- LLM classifier gate (iMessage/SMS group chats, not Discord; Linq blog, 25 Jun 2026): a cheap model (Claude Haiku 4.5) classifies each group message as `respond`, `react` or `ignore` with `max_tokens: 20`, seeing only the last 4 messages with sender handles; bias toward `respond` when unsure; `react` reserved for acknowledgements; the main model (Sonnet) runs only after the gate passes; if recent context already contains reactions, favor `respond` to avoid reaction spirals. Claimed benefits: consistency, lower cost, chattiness tunable by editing only the classifier, unit-testable with labeled messages. — [Linq: building AI agents that work in group chats](https://linqapp.com/blog/building-ai-agents-that-work-in-group-chats) (vendor blog; self-reported)
- A Discourse AI forum thread (anecdotal) reports that telling a persona in its system prompt to stay quiet failed because the model had already been triggered; the lesson drawn was that trigger logic must be in code, not in the prompt. — [meta.discourse.org thread](https://meta.discourse.org/t/allow-ai-persona-agent-to-respond-only-to-mentions-not-to-replies-to-its-posts/399221?tl=he)
- Discord slowmode (`rate_limit_per_user`, 0 to 21600 s) does not apply to bots, so a bot must self-limit. — [Discord docs: Channel resource](https://docs.discord.com/developers/resources/channel)

### Inferences
- The oobabot pattern (open follow window right after being addressed, decaying chance, bonus for questions, hard cap on how many channels are "live") is directly reusable for a small server: the window keeps the bot from interjecting in unrelated channels.
- For two alternating characters, the SillyTavern "talkativeness + whole-word name mention + pick one" logic maps well: name detection chooses the speaker, and the classifier or probability only decides whether to speak at all.
- No verified Discord-specific open-source bot using an LLM "should I respond" classifier was found; the only documented classifier design is the Linq group-chat one.

### Gaps
- Character.AI, Kindroid and Nomi group-chat speaker-selection logic: no official or technical documentation found (searches returned only marketing and general multi-agent material).
- Shapes' internal reply-gating: not found.
- oobabot numbers come from a model-read raw file; not independently re-checked against the repo.

## 2. Spontaneous / proactive messages

### Takeaway
Documented proactive behavior in Discord bots is mostly the probability-after-activity pattern above (reactive-ish interjection). Companion apps (Replika, Nomi, Kindroid) market "proactive" outreach after the user has been away, but the mechanism and frequency controls are not documented. I found no reliable community data on annoyance thresholds.

### Cited Findings
- Interjection in oobabot is confined to recent summon channels (cap 3) and decays over 5 minutes, which is a built-in annoyance control. — [oobabot settings.py](https://raw.githubusercontent.com/chrisrude/oobabot/main/src/oobabot/settings.py), [config.sample.yml](https://raw.githubusercontent.com/chrisrude/oobabot/main/docs/config.sample.yml)
- The Linq write-up lists "react instead of text" as a first-class action and warns that over-talking leads people to mute the agent; its group prompt says "react less often." — [Linq](https://linqapp.com/blog/building-ai-agents-that-work-in-group-chats)
- Replika markets proactive check-ins that follow up days later; Nomi and Kindroid list proactive messaging when the user is away. Frequency/quiet-hour settings were not found. — [Replika App Store listing](https://apps.apple.com/app/replika/id1158555867); [aicompanionpick comparison](https://aicompanionpick.com/replika-vs-kindroid-vs-character-ai-2026) (marketing/comparison sites, anecdotal)
- Discord community complaints about unsolicited bot activity found only concern spam DMs from self-bots, not channel chatbots. — [Discord support community post](https://support.discord.com/hc/en-us/community/posts/360050056414-Automated-direct-messages-from-Self-Bots-accounts)
- Webhook/bot execution can send without a user trigger, with `SUPPRESS_NOTIFICATIONS` flag available to avoid pinging. — [Discord docs: Webhook resource](https://docs.discord.com/developers/resources/webhook)

### Inferences
- Idle timers, "daily life" posts and session-start events: no concrete open-source Discord implementation with config names was found. A design for the target server can reuse the oobabot window logic plus a scheduled task and a hard daily cap per channel, but that is design, not reported practice.
- Using emoji reactions as a low-cost presence signal is supported by the Linq `react` action, not by a Discord bot source.

### Gaps
- Community-reported annoyance thresholds (messages per hour, idle times): not found; the search for Reddit/forum threads returned nothing usable.
- No source found for "scheduled daily-life posts" in Discord character bots.

## 3. Per-user memory and relationships

### Takeaway
Simple bots keep a per-user or per-channel rolling history; richer ones use SQLite with full-text and vector search. No verified Discord character bot with an affinity score or documented opt-out/forget flow was found, so privacy practices have to be designed, not copied.

### Cited Findings
- Sora (OpenRouter bot): per-user conversation history with `/clear_context`; channel scope via `/set_channel <id|all>`. — [mintsuku/sora](https://github.com/mintsuku/sora)
- AktivaAI: memory per channel and thread, isolated between threads, with slash commands to modify or clear segments. — [AktivaAI](https://github.com/Iteranya/AktivaAI)
- Buzzkeeper (Rust Discord bot) moved from a notes list to a SQLite retrieval layer with FTS5 keyword search and sqlite-vec vector search, preferring SQLite over a separate vector DB for single-file simplicity and backups; memories are added with `/remember` (deletion not mentioned). — via search summary of [Hive post](https://hive.blog/hivedevs/@beggars/buzzkeeper-update-persistent-intelligent-classifiable-memory) (page itself returned 403; unverified)
- VexAI uses SQLite by default with FTS5 and keeps revision history of message edits and deletions. — via search summary, [VexAI mirror](https://gitblind.noratr.app/mrelmida/VexAI) (unverified; revision history of deleted messages is a privacy concern)
- Agno ships a Discord example agent with per-user memory in SQLite. — [Agno docs](https://docs.agno.com/examples/applications/discord/agent_with_user_memory) (snippet only)
- llmcord stores nothing: history is the Discord reply chain and users are identified by `<@ID>` prefixes. — [llmcord README](https://github.com/jakobdylanc/llmcord)
- Discord's policy side: Shapes was alleged to have ignored user requests to delete stored data (see section 5), so honoring deletion is an enforcement-relevant practice. — [GamingHQ, 16 May 2025](https://gaminghq.eu/2025/05/16/discord-bans-100000-ai-bots-from-shapes-inc-after-major-policy-violations/) (secondary source)

### Inferences
- For a private community of dozens, SQLite with a table of (user_id, fact, source_message_id, created_at) plus periodic summaries is sufficient; a vector DB is unnecessary at this size. Reasoned from the Buzzkeeper choice and the scale, not reported by a bot at this scale.
- A `/esquecer` (forget) and `/memoria` (show) command, deletion of memory when a member leaves, and not logging raw message text are low-cost privacy practices consistent with the deletion allegation against Shapes; none were verified in an existing bot.

### Gaps
- Affinity/relationship-score implementations in Discord bots: none found.
- Documented opt-out commands in character bots: none verified.
- Mem0/Letta Discord integrations were not examined.

## 4. Multiple personas on one bot account (webhooks)

### Takeaway
Webhooks let one bot post under different names and avatars per message, and character bots like AktivaAI and Mian's Tavern do exactly this. Limits: webhook messages are not from the bot user, cannot be replied-to via @ in the PluralKit experience, and the docs set no rules or numbers beyond per-resource rate limiting and a 2000-character cap.

### Cited Findings
- Execute Webhook accepts per-message `username` and `avatar_url` overrides; `thread_id` posts into an existing thread (auto-unarchives); forum channels need `thread_id` or `thread_name`; `content` max 2000 chars; `allowed_mentions` is recommended for user-generated content; `wait=true` returns the message object; non-application-owned webhooks cannot send interactive components. The webhook's own name cannot contain "clyde" or "discord". The page does not document username rules for the override and does not mention message references (replies). — [Discord docs: Webhook](https://docs.discord.com/developers/resources/webhook)
- Webhooks are a top-level rate-limit resource; global limit for bots is 50 requests/second; no webhook-specific numbers are given in the docs; if a webhook returns 404 stop using it; 10,000 invalid (401/403/429) requests per 10 minutes triggers a Cloudflare ban. — [Discord docs: Rate limits](https://docs.discord.com/developers/topics/rate-limits)
- Community figures for webhooks: about 5 requests per 2 seconds per webhook, but one source says about 30 messages per minute, and both say to read the rate-limit headers instead of hardcoding. — [Hookdeck guide](https://hookdeck.com/guides/platforms/post/how-to-get-started-with-discord-webhooks), [Cybrancee](https://cybrancee.com/blog/discord-webhooks-explained-what-they-can-and-cant-do/) (third-party, conflicting)
- Typing indicator endpoint lasts 10 seconds; the docs advise bots to generally avoid it and list no rate-limit numbers. A webhook cannot trigger a typing indicator (inference: the endpoint is a bot-authenticated channel route). — [Discord docs: Channel](https://docs.discord.com/developers/resources/channel)
- PluralKit proxy: it deletes the user's message and reposts it through a webhook with member name/avatar; requires per-channel Manage Messages and Manage Webhooks, plus Send Messages in Threads; combined name max 80 characters; webhook messages cannot be edited like normal ones (use `pk;edit`); "You cannot reply-@ a proxied message" because they are webhooks, with a 🔔 reaction workaround; webhook users cannot be blocked. — [PluralKit guide](https://pluralkit.me/guide/), [PluralKit FAQ](https://pluralkit.me/faq/)
- Tupperbox: same webhook model, proxy reactions (delete, who-sent-it, edit), autoproxy, optional log channel copying proxied messages for moderators. — [Tupperbox](https://tupperbox.app/)
- AktivaAI: each character has a webhook for its avatar, triggered by name or by replying to its message. — [AktivaAI](https://github.com/Iteranya/AktivaAI)
- Mian's Tavern (hosted roleplay bot, listing text only): uses webhooks for character name/avatar, requires Manage Webhooks, runs roleplay in threads, characters reply when mentioned or named. — via search summary of [top.gg listing](https://top.gg/bot/1287923107604205630) (page 403; unverified, anecdotal)

### Inferences
- Because a webhook message has no bot-user identity, a member cannot use Discord's native reply to a character and trigger the bot on it the way llmcord does; reply detection has to compare the replied-to message's webhook ID/username with the persona list. This is reasoned from the PluralKit FAQ and the Execute Webhook docs, not tested.
- Two alternating characters on one webhook per channel (or one webhook per persona) avoids overwriting the webhook's default identity; sequencing messages with a small delay keeps well under any documented limit at this scale.
- Slash commands will always appear as the bot application, not as a character.

### Gaps
- Whether webhook messages can set `message_reference` (reply): the docs page does not say; unverified.
- Official webhook per-route numbers: not published on the rate-limit page.
- Thread-specific webhook quirks beyond `thread_id`: not found.

## 5. Platform constraints as of 2026 (policy, Clyde, Shapes)

### Takeaway
Message content is a privileged intent (needed unless the bot is mentioned, in DMs, or reading its own messages), with verification and approval at 100+ servers. The Developer Policy/Terms texts could not be read; secondary sources conflict on whether an explicit ML-training ban exists, while Discord's own August 2025 FAQ says AI companies may not train on user messages. Shapes was removed on about 1 May 2025 with alleged reasons (training, token collection, ignored deletions, child safety); Shapes denies the training claim.

### Cited Findings
- Message Content intent: privileged; enable in the Developer Portal; apps in 100+ guilds must be verified and approved; apps under 10,000 unique users can enable directly per this page; unapproved use closes the gateway with code 4014. Without it, content fields are empty except for messages the bot sends, DMs, messages that mention the bot, and message context-menu targets. The docs do not mention AI specifically. — [Discord docs: Gateway](https://docs.discord.com/developers/events/gateway) (page read in 2026; no date shown)
- The Developer Policy URL redirects to support-dev.discord.com article 8563934450327; a search result titles it "Effective date: July 8, 2024". One search summary says "Handle Data with Care" bars using API message content to train ML/AI models including LLMs without permission; another found only a clause limiting API Data use to the app's stated functionality and no explicit AI language. — [search result for the policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy) (403 on fetch; conflicting secondary readings, unverified)
- Discord policy FAQ, update dated 29 Aug 2025: "No, we do not allow AI companies to train their models using your messages." — [Discord: Important Policy Updates](https://discord.com/safety/important-policy-updates)
- Clyde: launched March 2023 using OpenAI, limited servers. In April 2023 users jailbroke it with a "grandma" roleplay (napalm) and a "DAN" prompt (meth); Discord called it experimental, added reporting, noted OpenAI moderation filters, and reportedly patched the grandma exploit. — [TechCrunch, 20 Apr 2023](https://techcrunch.com/2023/04/20/jailbreak-tricks-discords-new-chatbot-into-sharing-napalm-and-meth-instructions/)
- Clyde shutdown: Discord's support note said it would be deactivated at the end of the month, no invocation in DMs, group DMs or servers after 1 Dec 2023; Discord called it "an experiment shared with a small percentage of servers" and gave no specific reason. — [Gizmodo, 17 Nov 2023](https://gizmodo.com/discord-chat-ai-clyde-shutdown-1851030659); [AlternativeTo](https://alternativeto.net/news/2023/11/discord-is-discontinuing-clyde-its-experimental-ai-chatbot-effective-december-1st). Whether the jailbreaks caused it: not stated by any source.
- Shapes Inc (Circle Labs): Discord removed its bots on about 1 May 2025. Alleged reasons per third-party reporting: collecting users' bot tokens, using Discord message content to train models, not honoring deletion requests, age-restricted/child-safety lapses. More than 100,000 user-hosted bots reportedly banned. Shapes denies training on Discord data, says it used only opt-in non-Discord data, calls the enforcement selective, and says token collection is common practice. No official Discord statement was found; details come from emails relayed by others. — [GamingHQ, 16 May 2025](https://gaminghq.eu/2025/05/16/discord-bans-100000-ai-bots-from-shapes-inc-after-major-policy-violations/); [Alon Alush blog, updated 3 May 2025](https://alon-alush.github.io/ai%20world/shapesinctermination/); [Manifold market](https://manifold.markets/bohaska/will-shapesinc-be-reinstated-by-dis)
- Rate limits relevant to a chatty bot: 50 requests/s global; 10,000 invalid requests per 10 minutes before a Cloudflare ban; no documented limit for typing indicator. — [Discord docs: Rate limits](https://docs.discord.com/developers/topics/rate-limits)

### Inferences
- A private server with under 100 guilds can enable Message Content without verification, but should still not store or reuse message content beyond what the bot's stated function needs, and never use it for training or fine-tuning.
- Shapes' lessons for a hobby bot: do not collect other people's tokens, honor deletion requests, keep minors/age-restricted rules in the persona prompt. These follow from the alleged violations; the allegations are partly disputed.
- Collapse of the "bot speaks as two characters" design into webhooks remains within documented features, but no source addresses whether Discord requires bots to disclose AI use; none found.

### Gaps
- Primary text of the Developer Policy and Developer Terms (403): effective date, any AI/ML clause, deletion duty, and 2026 updates remain unverified. Needs a manual read at support-dev.discord.com.
- Any 2026 Discord announcement on AI bots: none found.
- Discord's own statement on Shapes: none found.

## 6. Cost and abuse control

### Takeaway
Hobby-scale costs reported by blogs are a few dollars to about $20 a month on cheap models, with history length as the main cost driver. Prompt injection is real (Clyde jailbreaks) and was handled by patching and provider moderation. Gating before the main model call is the main saving.

### Cited Findings
- TokenMix (13 Apr 2026): small-server scenario of 100 active users and 500 AI messages/day listed at about $1.35/month for DeepSeek V4, $0.90 for GPT-4.1 Nano, $4.50 for GPT-4.1 mini; $5-50/month for 1,000 active users. — [TokenMix](https://tokenmix.ai/blog/ai-api-for-discord-bots) (via search summary; vendor blog)
- GetAPIPulse (2026, undated): at 5,000 messages/day, 500 input and 200 output tokens each, "cheapest models" under $21/month; premium models $100-525/month; routing simple messages to cheap models claimed to cut a 1,000-user bot from $225 to $45; tips: cap output, shorten system prompt, cache repeated answers, monitor usage. The page's own monthly figures are inconsistent with its stated assumptions (my recomputation gives about $25-29 for the cheapest). — [GetAPIPulse](https://getapipulse.com/blog-ai-discord-bot-cost-2026.html) (low reliability)
- Quickchat (via search summary): context of about 10 previous turns raises input from about 500 to about 5,000 tokens, roughly ten times the cost. — [Quickchat](https://quickchat.ai/post/free-ai-discord-bots) (vendor blog, anecdotal)
- Gate-before-generate saves cost: most group traffic stops at the cheap classifier and the large model is not invoked. — [Linq](https://linqapp.com/blog/building-ai-agents-that-work-in-group-chats)
- Hard caps in open-source bots: llmcord `max_messages`/`max_text`/`max_images` and per-user/role/channel allow and block lists; oobabot `history_lines: 7`. — [llmcord](https://github.com/jakobdylanc/llmcord), [oobabot config](https://raw.githubusercontent.com/chrisrude/oobabot/main/docs/config.sample.yml)
- Jailbreak examples against a Discord bot with provider-side moderation: grandma roleplay and DAN. — [TechCrunch](https://techcrunch.com/2023/04/20/jailbreak-tricks-discords-new-chatbot-into-sharing-napalm-and-meth-instructions/)
- Use `allowed_mentions` on bot/webhook output to stop injected @everyone or role pings. — [Discord docs: Webhook](https://docs.discord.com/developers/resources/webhook)

### Inferences
- With roughly 100-200 model calls a day on a small model and a 4-message gate, the main cost is the final in-character generation; prompt caching of the character sheet and rolling summaries rather than long raw history would be the main lever. This is an estimate from the sources above, not an operator report.
- No operator-reported monthly bill for a small private character-bot server was found.

### Gaps
- Real operator post-mortems with receipts: none found; cost figures come from vendor or listicle pages with inconsistent math.
- Prompt-injection defenses used by character bots (output filters, per-user quotas) beyond the allow/block lists above: not documented in the sources read.
- Provider prompt-caching discounts: not covered in these sources.

## 7. Documented failure modes and community lessons

### Takeaway
The recurring failures are over-talking, bot-to-bot loops, the model speaking for other users, inconsistent decisions when the same call both judges and writes, and prompt-level instructions failing to prevent triggered replies. Fixes found are code-level gates, bot-message filters, caps and split judge/writer calls.

### Cited Findings
- Bot-to-bot loops: oobabot ignores all messages from other bots and from itself by design. — [decide_to_respond.py](https://raw.githubusercontent.com/chrisrude/oobabot/main/src/oobabot/decide_to_respond.py)
- A hobby Python bot looped by reading its own replies; the poster's fix was a flag to skip its own output (anecdotal, forum). — [OutSystems forum](https://www.outsystems.com/forums/discussion/65984/python-based-discord-bot-reply-errors-infinite-loop/)
- Over-talking and reaction spirals, plus judge-and-writer inconsistency, are listed as failure modes with the classifier gate as fix. — [Linq](https://linqapp.com/blog/building-ai-agents-that-work-in-group-chats)
- Model speaks for others: oobabot's author acknowledges this and truncates, causing terse replies. — [oobabot README](https://github.com/chrisrude/oobabot)
- Persona answers every reply to its own posts despite prompt instructions (anecdotal, Discourse). — [meta.discourse.org](https://meta.discourse.org/t/allow-ai-persona-agent-to-respond-only-to-mentions-not-to-replies-to-its-posts/399221?tl=he)
- Developer write-up (secondary, via search summary) that early multi-character attempts had everyone reply to every message, causing redundant output and doubled cost, and random speaker selection broke coherence when the wrong character answered a direct question. — [linqapp / dev.to results](https://learn.traeai.com/t/ai-engineering/phases/16-multi-agent-and-swarms/10-group-chat-speaker-selection) (unverified summary)
- SillyTavern's fallback of picking one random speaker when nobody activates exists so group chats never stall. — [SillyTavern docs](https://docs.sillytavern.app/usage/core-concepts/groupchats/)

### Inferences
- With two alternating characters, the biggest risk is the pair feeding each other: a rule that webhook messages produced by the bot itself never count as a trigger, plus a cap on consecutive character turns per human message, addresses this (consistent with oobabot's bot-ignore rule; not tested).
- "Feels fake" complaints: no cited community source was found; avoid claiming a documented fix.

### Gaps
- Primary community post-mortems (Reddit, Discord forums) for AI character bots: search returned none; the only support is anecdotal forum posts from non-character bots.
- Kindroid/Nomi/Character.AI failure reports: not found.
