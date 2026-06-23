# ROADMAP.md — Silversea Market Intelligence System

*Phase-level plan. Update phase status via /context-update when a phase completes or changes.*

---

## Vision

A stateful AI market intelligence system for Silversea Media's BD/sales team covering
Singapore's built environment sector. The system learns and improves over time through a
RAG-based feedback loop. Built fully for Singapore first, then expanded to MY, VN, ID.

---

## Full System Architecture

```
Data Layer
  Scraper: websites + LinkedIn
  Sectors: gov_agencies | associations | customers | partners | competitors
  Content: events, policies, releases, tenders, competitor moves
  Sources: placeholder structure in Phase 1 → real companies in Phase 4

AI Brain (Phase 2)
  Semantic deduplication: merge same-story signals across sources before analysis
  Named entity extraction: company names, amounts, dates, tender numbers → structured metadata
  Source quality scoring: passive learning — tracks which sources produce actionable signals
  Vector store (ChromaDB): past weekly summaries, feedback digests, company context seed
  RAG analyst: retrieves relevant context at inference time → shapes report output
  Weekly summarizer: every 7 days, compresses week's daily reports → one summary in vector store

Feedback Loop (Phase 2)
  Feedback form: embedded at end of each daily report, whole-company access, no login
  Aggregator: collects submissions, LLM-summarises into digest before storage
  Digest stored in vector store → retrieved as context on next run

Output
  Daily report → internal web dashboard on company servers (Phase 3)
  Weekly summary → auto-pushed to Google Drive (Phase 4)
  Cadence: daily at 09:00 SGT / 01:00 UTC

LLM Strategy
  Testing/dev: Groq Llama 3.3 70B (free)
  Production: Claude Haiku 3.5 (~$0.05–0.15/day)
  Model is a config variable — swap without code changes
  No agents in Phase 2; agentic verification step considered for Phase 3+

Scope
  Phase 1–3: Singapore only
  Phase 4: Malaysia, Indonesia, Vietnam added
```

---

## Phases

### Phase 1 — Foundation `[DONE]` *(completed 2026-06-19)*
**Goal:** Working daily pipeline for Singapore with sector-based scraper and improved analysis quality.

- [x] Apply 3 analyst.py prompt improvements from quality review (2026-06-16)
- [x] Redesign config/sources.py for sector-based organisation (gov, associations, customers, partners, competitors)
- [x] Rebuild scraper for multi-sector placeholder structure (websites)
- [x] LinkedIn scraper — researched, deferred (no free no-auth method viable)
- [x] Update GitHub Actions workflow for daily cadence
- [x] Update report.py — semantic IDs, proper list wrapping for Phase 3 dashboard

**Result:** Pipeline runs daily, 25 sector-tagged sources, quality score 21/25 (up from 12/25 baseline).

---

### Phase 2 — AI Brain `[DONE]` *(completed 2026-06-22)*
**Goal:** System learns and improves from user feedback over time.

- [x] Integrate ChromaDB vector store
- [x] Seed vector store with company context document (Silversea products, prospects, priorities)
- [x] Add semantic deduplication step (pre-analyst, uses embeddings)
- [x] Add named entity extraction step (pre-analyst, produces structured metadata)
- [x] Implement source quality scoring (passive, logged per run)
- [x] Modify analyst to retrieve relevant context from vector store at inference time (RAG)
- [x] Build feedback form — embedded at end of daily report (structured fields, whole-company)
- [x] Build feedback aggregation pipeline: submissions → LLM summarises → digest stored in vector store
- [x] Weekly summarizer: compress 7 daily reports → one summary, replace in vector store *(Google Drive push deferred to Phase 4)*

**Result:** Full feedback loop verified end-to-end — feedback submitted measurably changes what the next report surfaces, demonstrated live with test data.

---

### Phase 3 — Web Dashboard `[DONE]` *(completed 2026-06-23)*
**Goal:** Proper internal web application replacing static HTML output, split into two surfaces: a polished market-intelligence report view for the BD/sales team, and a separate AI-system internals/observability page for the developer/maintainer (vector store contents, source scores, feedback digests, last-run metadata).

- [x] Choose web framework / front-end approach — Flask + Jinja2, Tailwind CSS CDN, Chart.js CDN
- [x] Switch analyst.py output from freeform text to structured JSON
- [x] Refactor main.py + report.py for JSON artifacts + run metadata
- [x] Build Flask app (app.py) with routes: /, /internals, POST /feedback
- [x] Design + build polished market-intelligence report template (Surface 1)
- [x] Design + build AI-system internals template (Surface 2)
- [x] Country-tab architecture — SG active, MY/VN/ID slots ready
- [x] End-to-end verification
- [ ] Deploy to company servers (no authentication, internal access) — deferred, still running locally

**Result:** Company can read a polished daily report and submit feedback from one internal URL; developer can view AI-system internals on a separate page. Verified end-to-end locally; production server deployment not yet done.

---

### Phase 4 — Summary + Scale `[PENDING]`
**Goal:** Weekly synthesis + multi-country expansion.

- [ ] Weekly summary generation (synthesises 7 daily reports)
- [ ] Google Drive integration — weekly summary stored automatically
- [ ] Country expansion: MY, VN, ID — real sources added per sector
- [ ] Replace all placeholder sources with real company/agency lists

**Done when:** Four-country daily pipeline running, weekly summaries landing in Google Drive, real sources active.

---

## Open Questions
- Web framework for Phase 3 — resolved 2026-06-23: Flask + Jinja2, Tailwind CSS via CDN, Chart.js via CDN. No SPA/React/FastAPI.
- Feedback form exact field types — resolved: relevance rating (1-5), most useful signal, missed topics, priority changes, optional submitter name
- Real source lists (SG) — resolved 2026-06-23: 30 active sources across 6 sectors wired in and verified; remaining ~20 Singapore sources + MY/VN/ID deferred to Phase 4
- Production email recipients — confirm with Ms. Mok before Phase 4
