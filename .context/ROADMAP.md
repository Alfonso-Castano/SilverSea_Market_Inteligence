# Roadmap: Silversea Market Intelligence System

## Overview

The journey from a placeholder weekly scraper to a daily, multi-domain, feedback-driven AI intelligence system for Singapore's built-environment sector, with an internal web dashboard. Phases 1-3 (below) are the original roadmap and are complete. Several unplanned "rounds" (Phase 3.5, the informally-named "Phase 4 — Efficiency & Coverage," pipeline optimization, dashboard/frontend redesigns, and "Supervisor Feedback Round 2") were inserted between and after them, driven by live supervisor review rather than pre-planned scope — these are recorded as completed work below, not as roadmap phases with their own success criteria, since they were reactive rather than planned. The original **Phase 4 — Summary + Scale** (multi-country real sources + Google Drive push) remains genuinely pending and is the only open phase.

**⚠️ Naming collision, unresolved:** two different bodies of work have both been called "Phase 4" in this project's history — (1) the original roadmap's "Phase 4 — Summary + Scale" below (still pending), and (2) a separately-scoped "Phase 4 — Efficiency, Coverage & Bug-Fix Pass" from 2026-06-26 (completed, see `.context/DECISIONS.md`). Don't assume which one "Phase 4" means without checking dates — flag to Alfonso before renumbering.

## Phases

- [x] **Phase 1: Foundation** — Sector-based scraper, grounded analyst prompt, daily-cadence pipeline for Singapore
- [x] **Phase 2: AI Brain** — ChromaDB RAG, feedback loop, weekly summarizer
- [x] **Phase 3: Web Dashboard** — Flask + Jinja2 two-surface dashboard (report + internals), though production deployment was never completed
- [ ] **Phase 4: Summary + Scale** — Weekly Google Drive push, real MY/VN/ID sources — genuinely pending, not yet started with real data

## Phase Details

### Phase 1: Foundation `[DONE — completed 2026-06-19]`
**Goal:** Working daily pipeline for Singapore with sector-based scraper and improved analysis quality.
**Depends on:** Nothing (first phase)
**Success Criteria:**
1. `main.py` runs daily without errors ✓
2. Pulls from all 5 sector types ✓
3. Report quality score ≥17/25 — achieved 21/25 (up from 12/25 baseline) ✓
4. Opportunities section cites named programme, concrete action, source ✓

### Phase 2: AI Brain `[DONE — completed 2026-06-22]`
**Goal:** System learns and improves from user feedback over time.
**Depends on:** Phase 1
**Success Criteria:**
1. Feedback submitted on Day 1 measurably changes what the report surfaces on Day 7 — verified end-to-end with test data ✓
2. Weekly summary auto-generated and pushed to Google Drive — summary generation done; Drive push explicitly deferred to Phase 4 ✓ (partial)
3. Vector store accumulates context without unbounded growth (weekly compression working) ✓

### Phase 3: Web Dashboard `[DONE — completed 2026-06-23, deploy step still outstanding]`
**Goal:** Proper internal web application replacing static HTML output, split into a BD/sales-facing report view and a maintainer-facing internals/observability view.
**Depends on:** Phase 2
**Success Criteria:**
1. Company can read a polished daily report and submit feedback from one internal URL ✓
2. Developer can view AI-system internals (vector store, source scores, feedback digests, run metadata) on a separate page ✓
3. Deploy to company servers, no authentication — **not done**, app still runs locally. (Authentication was later added anyway in Supervisor Feedback Round 2, ahead of and independent from the deploy step.)

### Phase 4: Summary + Scale `[PENDING — not started with real data]`
**Goal:** Weekly synthesis pushed externally + multi-country expansion with real sources.
**Depends on:** Phase 3
**Success Criteria:**
1. Four-country daily pipeline running (scaffolding exists via `--country`; no real MY/VN/ID sources populated)
2. Weekly summaries landing in Google Drive (never built — summary generation exists, external push does not)
3. All placeholder sources replaced with real company/agency lists (done for SG only — 62 total sources, 57 active; corrected 2026-07-08 from a previously recorded 54)

---

## Completed Work Outside the Original Roadmap

These rounds were driven by live supervisor/Alfonso feedback rather than pre-planned phases. Full rationale for each in `.context/DECISIONS.md`.

- **Real Sources Finalization (2026-06-23)** — 30 active real SG sources wired in, MetaTwin→SpatioX branding fix, feedback-loop demo.
- **Phase 3.5 — Visual Design Revamp (2026-06-23)** — Dark glass hero, sticky scroll nav, Space Grotesk + AOS animations on the report page.
- **"Phase 4" — Efficiency, Coverage & Bug-Fix Pass (2026-06-26)** — 8-item bundle: expanded company context, rule-based keyword filter, smart truncation, full ~50-source ecosystem list, metrics glossary, feedback-digest consolidation, LLM model research, two analyst bug fixes. (This is the "Phase 4" naming-collision entry flagged above.)
- **Pipeline Optimization Pass (2026-06-29)** — Scrapling tiered-fetcher integration, dead-code removal (dedup/entities/scoring modules), filter keyword rebalancing.
- **Information Density Fix / Per-Sector Synthesis Rewrite (2026-06-29)** — Replaced monolithic synthesis call with per-sector extraction → per-sector synthesis → summary. Signal count 7 → 65.
- **Frontend Redesign, Prototype #3 (2026-06-30)** — Collapsible entity groups, signal spotlight, sector color coding, dark mode toggle, source-link mapping.
- **Country Source Template (2026-07)** — `docs/source_submission_template.xlsx` for other-country teams to submit source lists.
- **Supervisor Feedback Round 2 (2026-07-02)** — 8-topic bundle across Phases A-F: scoring rubric fix, opportunity source links, PDF export, `sources.py`→`sources.json` migration, viewer/admin auth, source-suggestion admin-approval queue, multi-domain (BER/EDU/GENERAL) restructure with 7-sector product catalog rebuild, `--country` scaffolding + ChromaDB metadata scoping.
- **Workflow Migration to `.context/` (2026-07-08)** — This session: replaced the ad hoc `CONTEXT.md`/`STATE.md`/`ROADMAP.md`/`PLAN.md` file set and the foundational CLAUDE.md with the structured `.context/` + `/feature-*` workflow.
- **Feature 001 — Round 2 Remediation (2026-07-08, `feature/001-round2-remediation`, PASSED)** — Fixed the admin/viewer auth bypass and `/feedback` route hardening (path-traversal sanitization, crash guard, CORS scoping); finished the SpatioX→real-catalog rebuild consistently across `company_context.md` and `pipeline/analyst.py`; added EDU filter keywords + NUS/NTU dual-tagging; re-seeded the `COMPANY_CONTEXT` vectorstore; added an admin country selector and fixed a stale-singleton bug in `source_suggestions.approve()`; added the repo's first unit test. See `.context/DECISIONS.md` for full rationale. Branch not yet merged to `main`.

## Open Questions Carried Forward

- **Feedback-digest and weekly-summary country-scoping** — both currently global/unscoped. `REPORT_HISTORY` now accumulates a mix of country-tagged (analyst.py) and untagged (weekly.py, feedback.py) documents; a future `where={"country":"SG"}` query would silently exclude weekly-summary docs. Explicitly re-deferred in Feature 001. Alfonso to decide whether these should be country-scoped.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — mechanical BER/EDU/GENERAL domain assignments from Supervisor Feedback Round 2 (B2) remain unreviewed. Feature 001 added a stopgap (EDU keywords + NUS/NTU dual-tagged `["BER","EDU"]`) but did not resolve the underlying draft-flag review; the admin country-selector change touched the same file so watch for drift.
- **`ADMIN_PASSWORD` env var** — Feature 001 closed the security hole (unset/empty now refuses login rather than matching), but the var still must be set by Alfonso for admin login to actually work.
- **A3 PDF export browser polish** — the afterprint class-strip bug itself was fixed in Feature 001 (`static/animations.js` now tracks only elements it toggled); real-browser print-preview visual QA across signal cards and entity groups is still an open Alfonso-owned manual checkpoint.
- **SpatioX naming cleanup** — **resolved by Feature 001** (2026-07-08). All remaining SpatioX references in `company_context.md` (Target Sectors, Key Prospects, Ecosystem Players) and `pipeline/analyst.py` were rebuilt around the real 7-sector catalog per an explicit naming map (Ops→Smart Facility Management System, Audit→Smart Virtual Inspection, Twin→Digital Twin, Walk→3D/VR Virtual Tour). Zero SpatioX references remain in either file.
- **Claude Haiku production switch** — still deliberately deferred; pipeline hardening was the stated blocker, not yet explicitly re-confirmed as done.
- **Production deployment** — company-server hosting was scoped in Phase 3 and never completed; app runs locally only.
- **Future pipeline-polish round (new, from Feature 001's recon pass)** — no LLM rate limiter despite a 2026-06-19 decision recording one; `sentence-transformers` is a direct (not transitive) dependency; email digest likely renders blank; `run_metadata.json` not domain/country-scoped; `weekly.py` retrieval order-unstable with no dedup guard; `pipeline/analyst.py` crashes on unset `GROQ_API_KEY`; dead file `scripts/feedback_server.py` still on disk. See `.context/DECISIONS.md` (2026-07-08 entry) for detail. Not yet scoped as a feature.
