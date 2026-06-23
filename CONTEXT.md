# CONTEXT.md — Architectural Decisions Log

*This file records key decisions and their rationale. Append new decisions as they're made.
Never delete entries — this is a permanent record. Read this at the start of every session.*

---

## Decision Log

### [2026-06] Initial Architecture

**Decision:** Plain Python pipeline (requests + BeautifulSoup) over n8n or Firecrawl
**Reason:** Free, zero external dependencies for MVP, sufficient for the ~15 target sources.
Firecrawl can be added later if JavaScript-heavy sites prove unscrapable with plain requests.

**Decision:** GitHub Actions for scheduling over a hosted server or n8n cloud
**Reason:** Completely free, no server to maintain, integrates naturally with GitHub repo,
cron syntax is straightforward for a weekly run.

**Decision:** Vercel for report hosting over GitHub Pages
**Reason:** Cleaner URL, easier custom domain migration later, same auto-deploy-from-GitHub
workflow, still free. When supervisor approves, can migrate to Alibaba Cloud OSS or their
own servers with minimal config change.

**Decision:** Claude Haiku (not Sonnet/Opus) for analyst.py
**Reason:** Cost. At ~15-30 articles per week, Haiku costs ~$0.10-0.30/run vs $1-3 for Sonnet.
Upgrade to Sonnet if report quality is insufficient.

**Decision:** Country-config structure from day one even though only SG is active
**Reason:** Supervisor's original brief mentioned SG, MY, ID, VN. Restructuring later is
expensive. One `active: True/False` flag per country costs nothing now.

**Decision:** No database — GitHub repo as storage
**Reason:** MVP only. HTML output is ephemeral (regenerated weekly). No historical querying
needed for MVP. Add SQLite or similar if archiving past reports becomes a requirement.

**Decision:** Gmail SMTP for email delivery
**Reason:** Free, no new service to sign up for. Alfonso's personal Gmail used for testing;
company email swapped in for production.

---

### [2026-06] Project scope expanded: pipeline → AI system

**Decision:** The system is no longer a reporting pipeline. It is a stateful AI market intelligence system with a RAG-based feedback loop that learns and improves over time.
**Reason:** Supervisor requirements expanded to include: sector-based scraping (gov agencies, associations, customers, partners, competitors), AI brain with persistent context, feedback form that reweights priorities, weekly summary, and a proper internal web dashboard.

**Decision:** Sector-based scraper architecture — five sectors: gov_agencies, associations, customers, partners, competitors
**Reason:** Supervisor wants intelligence organised by who the signal comes from, not just what topic it covers. Each sector has distinct BD relevance.

**Decision:** Daily pipeline cadence, not weekly
**Reason:** Supervisor confirmed daily reports are the target cadence. GitHub Actions cron to run at 09:00 SGT.

**Decision:** Production hosting on company servers, not Vercel
**Reason:** Supervisor confirmed internal web dashboard on company infrastructure. Vercel was prototype-only.

**Decision:** Build fully for Singapore first, then expand to MY, VN, ID
**Reason:** Avoids premature generalisation. SG system becomes the template; other countries just add their sector sources. Phase 4 handles expansion.

**Decision:** RAG-based feedback loop using a vector store
**Reason:** User feedback (submitted via form at end of each daily report) must update what the AI prioritises. Vector store accumulates context; weekly summarisation prevents bloat. No fine-tuning — prompt-time retrieval only.

**Decision:** Lightweight context management (CLAUDE.md + 4 files + /phase + /context-update) over GSD framework
**Reason:** Solo project, token efficiency is a constraint. GSD overhead not justified yet. Revisit if project grows to a team.

---

---

### [2026-06-19] AI system design decisions locked

**Decision:** Groq (Llama 3.3 70B) for development/testing; Claude Haiku 3.5 for production
**Reason:** Groq free tier eliminates cost during development. Claude Haiku has better tool use support for future agent work. Model is a config variable — trivial to swap. Cost at production volume: ~$0.05–0.15/day.

**Decision:** ChromaDB as vector store (local, free)
**Reason:** No external API or cost. Runs on company server. Switch to Pinecone only if multi-server architecture is required in Phase 3+. Simpler to start.

**Decision:** RAG + context only for Phase 2; no AI agents
**Reason:** Agents add per-run cost (multiple LLM calls) and complexity without proportional gain at current scale. Agentic verification step (high-scoring opportunities trigger web search) deferred to Phase 3+ when base system is proven.

**Decision:** Three Phase 2 AI enhancements confirmed: semantic deduplication, named entity extraction, source quality scoring
**Reason:** All three add measurable signal quality improvement with low complexity. Deduplication reduces noise across sources. Named entity extraction improves RAG retrieval quality. Source quality scoring enables passive learning over time without extra LLM calls.

**Decision:** Hard rate limit on LLM calls per run and per day
**Reason:** Safety measure. Prevents runaway loops and API abuse from misconfigured cron or feedback pipeline. Pipeline logs breach and exits cleanly.

**Decision:** Feedback form submissions are aggregated and LLM-summarised before vector store ingestion
**Reason:** Raw submissions are too verbose and varied for clean retrieval. A short digest of consensus feedback is more useful context for the analyst than many individual paragraphs. Prevents context bloat.

**Decision:** Pre-run context injection removed from scope
**Reason:** Alfonso confirmed the feedback form covers this purpose. Team feedback submitted after reading a report becomes context for the next day's run. No separate injection mechanism needed.

### [2026-06-19] Phase 1 prompt engineering decisions

**Decision:** Grounded prompting pattern for analyst — closed-book framing, quote-before-extract for opportunities, negative few-shot examples, per-field abstain tokens
**Reason:** Llama 3.3 70B fabricates causal links and invents deadlines when given a structured template to fill. Three iterations proved that explicit grounding constraints (not just "be accurate") are required. Quality jumped from 13/25 to 21/25 after applying these techniques.

**Decision:** Content truncated to 800 chars per source in analyst prompt (down from 2000)
**Reason:** Groq free tier has 12k TPM limit. With 18+ sources passing filter, 2000 chars/source exceeds the limit. 800 chars fits within budget. This constraint is lifted when switching to Claude Haiku in production (200k context).

**Decision:** LinkedIn scraping deferred from Phase 1
**Reason:** All free no-auth approaches are blocked by LinkedIn's anti-bot measures (login walls, CDP detection, IP reputation). Paid options (Apify, PhantomBuster) require budget approval. Not a Phase 1 blocker — revisit when budget is available.

---

### [2026-06-22] Phase 2 completion decisions

**Decision:** Google Drive export deferred from the weekly summarizer to Phase 4
**Reason:** Supervisor's real source lists (customers, partners, associations, MY/VN/ID) aren't finalized yet. Building Drive export now would mean reworking it once the pipeline scope is locked. The weekly summarizer's core function — compressing daily reports and replacing them in the vector store to prevent bloat — is built and verified; only the external push is deferred.

**Decision:** Phase 3 scope expanded to two separate dashboard surfaces
**Reason:** Alfonso wants a polished, professional market-intelligence report view for the BD/sales team, plus a separate developer-facing page showing AI-system internals (vector store contents, source scores, feedback digests, run metadata) so anyone maintaining the system can see what's driving its output without reading code.

---

### [2026-06-23] Real source list received — prioritized subset locked for prototype

**Decision:** Of the ~50 ecosystem sources in the supervisor's Built Environment doc, only a ~24-source prioritized subset will be wired in for tomorrow's presentation: gov_agencies +IMDA, associations +SGTech/REDAS, customers +Keppel, partners (newly populated) = AECOM/CPG Consultant/Honeywell/Cushman & Wakefield, competitors +FacilityBot/Cryotos (TwinMatrix dropped). Chinese state contractors (CSCEC/CCCC/CHEC), NUS/NTU/SGH, GeBIZ, Smart Nation/GovTech, BCI Asia, and Construction Plus Asia are left as-is/out of scope for this round.
**Reason:** Finding a real newsroom/press URL per source (not just the homepage given in the PDF) is the slow part — same research cost Phase 1 already paid for the current 20 sources. Attempting all ~50 in one session risked discovering scraping failures only at demo time. A smaller, fully-verified set is more defensible than a larger, partially-broken one. Sector taxonomy stays exactly as Phase 1/2 built it (gov_agencies, associations, customers, partners, competitors) — no new sectors introduced.

**Decision:** LinkedIn and Facebook source URLs (requested again by supervisor's doc) remain out of scope for this round.
**Reason:** LinkedIn scraping was already ruled out in Phase 1 (anti-bot, no free no-auth method). Facebook carries the same risk profile and wasn't worth re-researching under the deadline. Still a Phase 4+ candidate if budget allows a paid scraping API.

### [2026-06-23] Branding bug found: analyst prompt referenced wrong product names

**Decision:** `pipeline/analyst.py`'s SYSTEM_PROMPT will be corrected to reference Silversea's real products (SpatioX Twin, SpatioX Ops, SpatioX Audit, SpatioX Walk) instead of the placeholder names it currently has ("MetaTwin Object/Space/Immerse/Augment").
**Reason:** The placeholder names were never updated after the company profile was confirmed. Since this string drives the Product Fit field in every Opportunity the LLM generates, it would surface as a visible factual error in any report shown to the manager. Locked grounding-rule structure (closed-book framing, quote-before-extract, abstain tokens, scoring rubric) from Phase 1 is preserved — only the product-name content changes.

### [2026-06-23] Real sources finalization executed — branding + sources + feedback-loop demo

**Decision:** `data/company_context.md` (vector store seed document) updated alongside `analyst.py` to replace all MetaTwin→SpatioX references, then re-seeded into ChromaDB.
**Reason:** The RAG pipeline retrieves company context chunks at inference time. If the seed document still said "MetaTwin," the LLM could echo wrong product names even with the SYSTEM_PROMPT fixed. Both files must be consistent.

**Decision:** SGTech, CPG Consultant, and FacilityBot marked `active: False` in `config/sources.py` after dry-run scrape verification.
**Reason:** SGTech's ASP.NET news URLs return 404 (non-standard URL routing). CPG Consultant has no dedicated newsroom page. FacilityBot's /blog path returns 404. All three kept in config for future re-evaluation but excluded from daily pipeline to avoid error noise.

**Decision:** Final active source count is 30 (not the ~24 originally estimated) because pre-existing sources were kept as-is per execution plan instructions.
**Reason:** The execution plan explicitly said "leave existing ones as-is if already in the file" for sources like GeBIZ, Smart Nation, NUS/NTU/SGH. The ~24 estimate counted only the new + key existing sources but the file already had more active entries from Phase 1.

### [2026-06-23] Multi-pass analyst architecture for information density

**Decision:** Rewrote `pipeline/analyst.py` from a single monolithic LLM call to a two-phase multi-pass approach: Phase 1 makes one Groq call per sector with full untruncated source content, extracting every named signal; Phase 2 synthesizes all sector extractions into the final structured report.
**Reason:** Info-gap analysis showed the single-call approach was losing ~75% of actionable signals. Root causes: (1) the LLM silently dropped entire sectors (Competitors, Partners) when given 21 sources at once, (2) 800-char truncation cut rich sources (DataMesh 8000 chars → 800). Multi-pass eliminates truncation (each sector has 2-6 sources, fits under 12k TPM) and forces per-sector attention. Result: report size 4,600 → 8,000 chars, 17/17 key signals now present. Trade-off: ~3 min runtime (25s delay between calls for Groq TPM compliance) vs ~30s for single call.

---

## Open Questions
*(Remove entries when resolved, note the resolution)*

- What email address(es) should receive the production report? → TBD, confirm with Ms. Mok
- Should past reports be archived/browsable? → Not required for MVP
- Any sources behind login/paywall that need special handling? → Assume no for MVP
- Hosting: Vercel for prototype → company servers for production (confirmed)
- Feedback form exact field types → resolved: relevance rating (1-5), most useful signal, missed topics, priority changes, optional submitter name
- Full customer/partner/association source lists → resolved: supervisor provided full ecosystem list 2026-06-23; prioritized ~24-source subset locked for the prototype, remaining sources deferred to Phase 4 full rollout
