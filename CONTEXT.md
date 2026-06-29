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

### [2026-06-23] Phase 3 dashboard architecture decisions

**Decision:** Analyst output changes from freeform markdown text to structured JSON (dict with keys: executive_summary, signals_by_sector, opportunities, synthesis)
**Reason:** The dashboard needs to render score badges, sector cards, and score-breakdown bars — all impossible when the only data source is a prose string that requires regex parsing. JSON output makes the report machine-readable. Grounding rules and scoring rubric in SYNTHESIS_PROMPT stay untouched; only an additive OUTPUT FORMAT instruction block is appended.

**Decision:** Flask + Jinja2 with live per-request rendering (no SPA, no React, no FastAPI)
**Reason:** The pipeline is batch-driven (runs once daily). Pages are server-rendered from JSON files + ChromaDB reads. Flask is already a dependency (feedback server). Adding a JS frontend framework would introduce npm/build tooling for no capability gain. Live rendering (vs pre-baked static HTML) is simpler — Flask reads `data/latest_report.json` fresh on each request, always current, no generation step to keep in sync.

**Decision:** Tailwind CSS via CDN for styling; Chart.js via CDN for internals charts
**Reason:** No build step (no npm, no webpack). CDN is fine for an internal low-traffic dashboard. Tailwind gives utility-class control for cards/badges/grids without custom CSS overhead. Chart.js is the lightest free charting library that covers bar/line/doughnut for the ops dashboard.

**Decision:** Two-page split: report page built from scratch, internals page adapts free Volt Dashboard template
**Reason:** The CEO-facing report page must not look generic — custom Tailwind + CSS variables gives control over visual identity. The maintainer-facing internals page has no such constraint — adapting a free admin template saves build time on a page no one judges aesthetically.

**Decision:** Feedback endpoint consolidated from separate `scripts/feedback_server.py` (port 5050) into the main Flask app (`app.py`, port 5000)
**Reason:** One server instead of two. Same CORS headers, same JSON-to-file logic. The feedback form's action URL changes from `http://localhost:5050/feedback` to `/feedback` (relative, same origin).

---

### [2026-06-23] Phase 3.5 — Visual design revamp direction locked

**Decision:** Report page (`/`) gets a dark navy-to-black glassmorphism revamp — continuous dark zone spanning top nav, country tabs, and a new hero section with animated glass stat cards, a sticky scroll-spy nav, and a restructured Opportunities section (top 3 by score expanded equally, rest collapsible) — transitioning to a light, soft-shadowed body below. Internals page (`/internals`) gets the same shadow/hover/animation vocabulary but stays light throughout, no dark hero.
**Reason:** An initial "Notion-style restrained polish" framing was explicitly rejected by Alfonso as underselling the ambition — he wants a genuine structural/visual revamp ("luxurious," "visually impressive"), not incremental styling. Internals stays lighter because it's dev-facing and lower priority, not because the revamp direction was scaled back generally.

**Decision:** Glow/accent color stays brand green (`#2d6a4f`) only — no new accent (e.g. gold/champagne) introduced. Sector cards keep a uniform grid (no bento layout). Opportunities keep equal visual weight across the top 3 (no single spotlight card for #1).
**Reason:** Considered and explicitly declined in discussion — these were live options Alfonso chose not to take, recorded here so a future session doesn't reintroduce them as if undecided.

**Decision:** Space Grotesk (Google Fonts CDN) added for headlines/section headers/stat numbers; Inter remains the body font. AOS (Animate On Scroll, CDN) added for scroll-reveal animations.
**Reason:** Both are zero-build-step CDN additions that fit the "no architecture change" constraint — Flask + Jinja2 server-side rendering is preserved; the dark hero and glass effects are pure CSS (`backdrop-filter`), not a new rendering layer.

### [2026-06-23] Phase 3.5 — Visual design revamp executed

**Decision:** All visual revamp changes implemented exactly per locked spec in `.claude/execution/phase3-visual-design.md`. New CDN dependencies: Google Fonts (Space Grotesk + Inter), AOS 2.3.1. New file: `static/animations.js` (count-up, scroll-spy, sticky nav). No Python packages added, no architecture change.
**Reason:** Execution session; all decisions were made in the prior discussion session.

---

### [2026-06-24] Presentation prep — demo toggle kept, two analyst quality bugs surfaced

**Decision:** `app.py`'s `?demo=clean|feedback` query-param toggle (reads `data/presentation/{mode}_*.json`, falls back to `latest_report.json`) and the small "Clean Run"/"With Feedback" badge in `report.html`/`internals.html` are kept as working state, not reverted — even though the feedback-influenced report was never generated (`data/presentation/` directory doesn't exist) and the supervisor demo already happened.
**Reason:** Alfonso confirmed the supervisor saw this in-progress state and it's fine as historical/working state. Reverting would discard real, harmless scaffolding for no benefit.

**Decision:** Two analyst-output quality issues found during this run are logged as known bugs, not fixed yet: (1) `opportunities: []` — the relevance gate in `SYNTHESIS_PROMPT` let zero signals through, which is a documented "correct" behavior per the prompt but unhelpful for a BD demo; (2) `G Element`/`DataMesh` (configured under `competitors` sector) had their signals duplicated into the "Partners" bucket in `signals_by_sector`. The LLM appears to bucket by semantic content of the sentence rather than each source's configured sector.
**Reason:** Both require a `SYNTHESIS_PROMPT` change in `analyst.py`, which was out of scope for the presentation-prep task (constrained to not touch pipeline files) and burns Groq tokens to test. Deferred to the next planning session once supervisor feedback is incorporated.

**Decision:** Groq's free-tier daily token quota (100k TPD) is now fully exhausted for 2026-06-24 (~99,481/100,000 used) after two clean-run attempts. No further `main.py` runs until the quota resets at UTC midnight — confirmed with Alfonso to hold off intentionally to conserve tokens for future runs.
**Reason:** Two failed retry attempts showed Groq's 429 error message ("try again in Xm") understates the real wait — it's a daily quota tied to UTC midnight, not a short rolling window. Burning more tokens chasing a same-day fix wasn't viable.

### [2026-06-26] Phase 4 scope locked: efficiency, coverage, and bug-fix pass

**Decision:** The next phase (Phase 4, executed via `.claude/execution/phase4-efficiency-coverage-handoff.md`) bundles eight items into one sequential pass: (1) expand `company_context.md` with ecosystem-player detail, (2) build a no-AI rule-based keyword filter with tiered (priority vs. general) weighting in `filter.py`/`config/sources.py`, (3) replace `scraper.py`'s blind character-cut truncation with keyword-anchored "smart truncation," (4) add the supervisor's full ~50-source ecosystem list (deduplicated against existing sources) and fix already-known broken scrapers, (5) add a metrics/scores glossary to `report.html`/`internals.html`, (6) add a feedback-digest consolidation mechanism (modeled on the existing weekly-summary pattern) to stop unbounded growth of the `feedback_digests` ChromaDB collection, (7) produce a written LLM model-research comparison (Groq alternatives vs. Claude Haiku vs. others) with zero live API calls, and (8) fix the two known `SYNTHESIS_PROMPT` bugs (empty-opportunities gate, sector mis-categorization) — sequenced last and shipped marked "unverified."
**Reason:** Alfonso's supervisor-demo feedback plus his own ideas spanned token-efficiency (both the scrape-filter side and the RAG/feedback-context side), full source coverage, model choice, and report clarity — all interrelated enough that splitting them into separate phases risked losing the shared context (e.g. the filter's keyword criteria depend on the expanded company context; the glossary's copy depends on knowing the bug-fix status). Alfonso explicitly chose "everything in the feedback, one big phase" over splitting it, since there's no fixed deadline. Two rounds of plan review (a code-grounded subagent reading the actual pipeline files, then a pure-logic subagent reviewing the plan's own sequencing) found and corrected real issues before lock-in: the original single "filter + truncation" step was actually two separate tasks touching two different files; the original "fix RAG digest growth" step was retargeted from the wrong function (`feedback.py`'s already-correct per-batch summarizer) to the actual growth point; and Step 8 was moved to run last, explicitly unverified, because editing 70B-model grounding-rule prompt logic with no live-run verification path was identified as the single highest-risk item in the plan.

**Decision:** Chinese state contractors (CSCEC, CCCC, CHEC) are now included as `partners`-sector sources, superseding the 2026-06-23 decision that left them out of scope.
**Reason:** The 2026-06-23 exclusion was scoped to a prioritized subset for a near-term demo, not a permanent architectural call. The supervisor's full ecosystem-list PDF re-listed them under "Main contractors," and Alfonso confirmed this round's source expansion should include the full list rather than re-applying the older prioritization filter.

**Decision:** TwinMatrix is re-added as a `competitors`-sector source, superseding the 2026-06-23 decision that dropped it.
**Reason:** Same as above — the 2026-06-23 drop was specific to that round's prioritized subset. The supervisor's full list re-included TwinMatrix under "Key competitors," and Alfonso confirmed re-adding it this round.

**Decision:** Main contractors, consultants, M&E/BMS system integrators, and facility-management firms from the supervisor's ecosystem list all map onto the existing `partners` sector — no new sector introduced.
**Reason:** Consistent with the existing convention already established for AECOM, CPG Consultant, Honeywell, and Cushman & Wakefield (all currently classified as `partners`), and consistent with the 2026-06-23 decision that the five-sector taxonomy (gov_agencies, associations, customers, partners, competitors) plus `general_news` stays fixed. The PDF's own "Owner" vs. everything-else distinction supports this: owners are buyers (→ `customers`), every other ecosystem role is a potential service/channel partner (→ `partners`).

### [2026-06-26] Phase 4 execution — SYNTHESIS_PROMPT bug fixes applied (unverified)

**Decision:** Widened the RELEVANCE GATE in `SYNTHESIS_PROMPT` (`pipeline/analyst.py`) to accept a second path for opportunities: a tracked ecosystem entity (customer, partner, competitor, or government agency from the company context) taking a built-environment-relevant action (tender, partnership, project announcement, facility initiative). The anti-fabrication rule ("if inferred, NOT an opportunity") is preserved — only the gate's scope was widened, not its strictness.
**Before:** `"Does the signal explicitly mention digital twin, BIM, 3D scanning, XR/spatial computing, smart FM, smart building, building automation, or proptech? If the connection to Silversea's products is inferred, it is NOT an opportunity."`
**After:** `"Does the signal explicitly mention digital twin, BIM, 3D scanning, XR/spatial computing, smart FM, smart building, building automation, proptech, OR involve a named entity from Silversea's tracked ecosystem (a customer, partner, competitor, or government agency listed in the company context) taking an action relevant to the built environment sector (a tender, partnership, project announcement, or facility initiative)? If the connection to Silversea's products is inferred rather than stated or reasonably implied by a tracked entity's documented action, it is NOT an opportunity."`
**Reason:** The strict keyword-only gate produced zero opportunities on the last real run — technically correct per the prompt's own design, but a BD-facing report with zero opportunities every run is not useful. The wider gate still enforces anti-fabrication (no inferred connections) but adds a second, narrower path: a tracked entity doing something built-environment-relevant.
**Status:** Fix applied 2026-06-26 — **unverified**, requires a live Groq run to confirm. See Phase 4 handoff Step 8.

**Decision:** Added a sector mis-categorization prevention instruction to `SYNTHESIS_PROMPT` (`pipeline/analyst.py`), in the SIGNALS BY SECTOR section: `"CRITICAL: Each signal belongs ONLY to the sector section its source content was extracted under (the === SECTOR NAME === headers in the intelligence below) — never duplicate a signal into a different sector bucket because its content sounds like it belongs elsewhere."`
**Reason:** Sources configured under `competitors` (e.g. G Element, DataMesh) had their signals duplicated into the `Partners` bucket. The LLM was bucketing by semantic content ("partnership" → Partners) rather than by the source's configured sector. The new instruction forces sector-faithful categorization.
**Status:** Fix applied 2026-06-26 — **unverified**, requires a live Groq run to confirm. See Phase 4 handoff Step 8.

**Decision:** Model research (Step 7) revealed that `llama-3.3-70b-versatile` was deprecated by Groq on 2026-06-17. Recommended replacement: `openai/gpt-oss-120b` (drop-in, same limits) or `meta-llama/llama-4-scout-17b-16e-instruct` (30k TPM, eliminates inter-call delays). See `data/model_research.md` for full comparison.
**Reason:** The pipeline will fail or behave unpredictably on the next run if the model string isn't updated. This was not a planned change — it surfaced during Step 7 research.

### [2026-06-26] Split-model architecture for extraction vs synthesis

**Decision:** The multi-pass analyst pipeline (`analyst.py`) will use two different Groq models: `meta-llama/llama-4-scout-17b-16e-instruct` (17B, 30k TPM) for per-sector extraction calls, and `openai/gpt-oss-120b` (120B, 8k TPM) for the single synthesis call.
**Reason:** Functional verification proved that no single free-tier Groq model works for both stages. `gpt-oss-120b` has strong instruction-following but only 8k TPM — too small for extraction calls where raw scraped content from 9-11 sources per sector can reach 9-10k tokens in a single request. `llama-4-scout` has 30k TPM (extraction never hits it) but only 17B parameters — too weak to follow the dense SYNTHESIS_PROMPT, causing it to aggressively summarize instead of preserving every extracted signal (report went from ~25 signals to ~10). The synthesis call's input is only ~5.7k tokens (extraction summaries, not raw content), so it fits under `gpt-oss-120b`'s 8k TPM. This gives extraction the TPM headroom it needs and synthesis the instruction-following quality it needs.

**Decision:** Both SYNTHESIS_PROMPT bug fixes (widened relevance gate, sector categorization) confirmed working on `llama-4-scout` run — opportunities gate correctly identified BCA Construction Startup Competition (score 18/25), correctly excluded URA residential tenders; no cross-sector signal duplication observed.
**Reason:** Verification run 2026-06-26 with all 6 sectors extracting. Status upgraded from "unverified" to "verified."

**Decision:** `CALL_DELAY` reduced from 25s to 2s in `analyst.py`.
**Reason:** `llama-4-scout` has 30k TPM — the 25s inter-call delays were designed for the old 6-12k TPM models. Even the synthesis call using `gpt-oss-120b` (8k TPM) fits in a single request, so long delays between calls are unnecessary. Pipeline run time dropped from ~3 min to ~30s.

### [2026-06-29] Split-model approach failed — simplified prompt instead

**Decision:** `gpt-oss-120b` rejected entirely for synthesis. The model returns empty output (empty string, not truncation) on the SYNTHESIS_PROMPT — tested both with `response_format={"type": "json_object"}` (Groq JSON validation error, `failed_generation: ''`) and without (raw empty string). This supersedes the 2026-06-26 split-model decision above.
**Reason:** Three failure modes discovered: (1) Groq counts `max_tokens` against TPM, so input 5.4k + max_tokens 6k = 11.4k >> 8k limit; (2) reducing max_tokens to 2.5k (total 7.9k < 8k) still produced empty output with response_format; (3) without response_format, still empty. The model simply cannot handle this task.

**Decision:** SYNTHESIS_PROMPT simplified from ~117 lines to ~30 lines, keeping `llama-4-scout` for both extraction and synthesis.
**Reason:** The dense multi-rule prompt was designed for when the LLM saw raw content directly. In the multi-pass architecture, extraction already handles grounding — the synthesis prompt was carrying unnecessary instructional weight the 17B model couldn't process. Simplified prompt preserves core rules (signal preservation, sector fidelity, opportunity relevance gate, no fabrication) but removes redundant grounding instructions, negative examples, and verbose formatting requirements.
**Result:** Opportunities improved from 0 to 3 identified (BCA Construction Startup Competition, G Element Digital Twin, DataMesh AI Agent). Signal count still ~9 vs ~30+ in extraction — ~60-70% loss, improved from ~80% with the old dense prompt but still unacceptable. Known issues: scoring ignores 0-5 scale, G Element duplicated across sectors.

**Decision:** RAG context (`_build_rag_context()`) removed from synthesis call.
**Reason:** Token budget constraint — RAG context added ~1-2k tokens of redundant company context (already hardcoded in SYNTHESIS_PROMPT) plus feedback priorities and past report themes. Must be restored when switching to Claude Haiku (200k context window removes the constraint). The function is currently dead code.

**Decision:** Claude Haiku upgrade deferred until pipeline optimization is complete.
**Reason:** Alfonso wants scraper, filter, RAG, and feedback systems hardened and verified before switching the synthesis model. No point feeding a better model through a leaky pipeline. Optimization pass covers: scraper quality (evaluating Scrapling library), filter tuning, feedback loop efficiency, dead code removal.

### [2026-06-29] Pipeline optimization pass — Scrapling integration and dead code removal

**Decision:** Scrapling library integrated into `pipeline/scraper.py` with tiered fetcher strategy: `_fetch_default()` (plain requests), `_fetch_stealth()` (Scrapling StealthyFetcher — Cloudflare/bot bypass), `_fetch_dynamic()` (Scrapling DynamicFetcher — full browser rendering for JS SPAs). Per-source `"fetcher"` config field dispatches. Imports are lazy so the pipeline still works without Scrapling installed (default sources use requests only).
**Reason:** 5+ sources were INACTIVE due to 403 errors or JS-only rendering that requests+BeautifulSoup can't handle. Scrapling's StealthyFetcher and DynamicFetcher can unblock them. API verified against official docs: class methods (`StealthyFetcher.fetch(url)`), response HTML via `page.body` (bytes), imported from `scrapling.fetchers`.

**Decision:** `pipeline/dedup.py`, `pipeline/entities.py`, `pipeline/scoring.py` deleted; `sentence-transformers` dependency dropped.
**Reason:** All three modules produced no useful output in practice. Dedup loaded a 90MB model and consistently merged 0 results. Entities attached data nothing downstream read. Scoring tracked unreliable citation-based scores that decayed to 0. Removing them simplifies the pipeline and drops ~500MB of dependencies.

**Decision:** Filter keyword rebalancing — entity names (competitors, customers, ecosystem players) moved from `priority_keywords` (3x weight) to `keywords` (1x weight).
**Reason:** Sources were auto-passing the relevance filter just by mentioning their own name (e.g. CapitaLand's newsroom scored 3+ because "CapitaLand" was a priority keyword). Now a source must mention a technology/domain term (digital twin, BIM, smart FM, etc.) to score high enough to pass.

### [2026-06-29] Pipeline verification — bugs found and fixed

**Decision:** Fixed `analyst.py:185` which used `MODEL` instead of `GROQ_MODEL`, causing a `NameError` at synthesis time. This was a leftover from the split-model refactor that renamed the variable.
**Reason:** Stage-by-stage verification caught it before a full pipeline run. Without this fix, `main.py` would crash after completing all extraction calls but before producing the final report.

**Decision:** IMDA URL corrected from `/resources/press-releases` to `/resources/press-releases-factsheets-and-speeches`, fetcher set to `"dynamic"`.
**Reason:** The old URL returned a 404 redirect ("Page Not Found"). The correct path was found via the IMDA homepage. The page is JS-rendered, so it also needs the dynamic fetcher. Content went from 25 chars (useless) to 5,545 chars (real press releases).

**Decision:** CCCC set to `active: False`.
**Reason:** Consistently times out (15s timeout exceeded) — Chinese state contractor site is unreachable from Singapore. CSCEC (same category) still works and is kept active.

**Decision:** Scrapling installed and all stealth/dynamic fetchers verified working. Active source count: 57 (was 58 before CCCC disabled, but 5 stealth/dynamic sources that were previously failing due to missing Scrapling are now functional).
**Reason:** Verification run confirmed: SJ Group (3,589 chars), Schneider Electric (2,860), Alstern Technologies (2,982), Aperio (3,364), MCC (1,815), IMDA (5,545) — all returning real content.

### [2026-06-29] Dashboard density overhaul — schema expansion backfired

**Decision:** Expanded SYNTHESIS_PROMPT signal schema from `{entity, signal}` to `{entity, signal, source_name, implication}` and added a Python-based competition risks post-processor that classifies competitor signals by threat level.
**Reason:** Alfonso reviewed the dashboard against a reference site (oss.silversea-media.net) and found per-signal information far too sparse. The expanded schema was intended to produce richer per-signal output. Competition risks were derived in pure Python (zero token cost) to avoid overloading the LLM.

**Decision:** The schema expansion caused a signal count regression from 11 to 7. The approach of adding fields to the synthesis prompt is confirmed as counterproductive with the 17B model — it trades count for (marginal) depth, and Alfonso wants BOTH.
**Reason:** The 17B `llama-4-scout` model has limited instruction-following capacity. Adding more output fields per signal means it produces fewer signals total. The fundamental bottleneck is the single monolithic synthesis call that tries to compress all sector extractions into one JSON response. This architectural issue cannot be solved by prompt engineering alone on a 17B model.

**Decision:** Template restructured from bullet lists to individual cards per signal, with "For Silversea Media" implication callouts (LLM-generated with sector-based fallback heuristics). Competition risks section added with threat-level badges. Data sources collapsible table added. Layout uses full-width stacked cards.
**Reason:** Alfonso confirmed the card-per-finding approach is correct but wants a 3-column grid layout (like the reference site) instead of full-width stacked rectangles. Template change is correct in direction but needs layout adjustment.

## Open Questions
*(Remove entries when resolved, note the resolution)*

- What email address(es) should receive the production report? → TBD, confirm with Ms. Mok
- Should past reports be archived/browsable? → Not required for MVP
- Any sources behind login/paywall that need special handling? → Assume no for MVP
- Hosting: Vercel for prototype → company servers for production (confirmed)
- Feedback form exact field types → resolved: relevance rating (1-5), most useful signal, missed topics, priority changes, optional submitter name
- Full customer/partner/association source lists → resolved 2026-06-26: full ~50-source ecosystem PDF received, mapped onto the existing sector taxonomy, and executed in Phase 4 Step 4 — 62 total sources (54 active, 8 inactive with documented reasons)
