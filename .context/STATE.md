# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## Current Position

Status: Supervisor Feedback Round 2 fully implemented (8/8 topics, Phases A-F); this session is migrating the project's context/workflow system itself — old `CONTEXT.md`/`STATE.md`/`ROADMAP.md`/`PLAN.md`/`PROJECT_REQUIREMENTS.md` files are being replaced by this `.context/` structure and a new CLAUDE.md built around `/feature-*` commands.

Last activity: 2026-07-08 — Workflow migration (this session). Prior activity: 2026-07-02 — executed all 8 Supervisor Feedback Round 2 topics in one session (Opus lead + 7 Sonnet subagents across 4 dependency waves). Files touched that session: `app.py`, `main.py`, `config/sources.py`, `pipeline/analyst.py`, `pipeline/report.py`, `pipeline/vectorstore.py`, `static/animations.js`, `static/style.css`, `templates/base.html`, `templates/report.html`, `data/company_context.md`. Files created: `config/sources.json`, `data/.flask_secret_key`, `data/viewer_password.txt`, `pipeline/source_suggestions.py`, `templates/admin.html`, `templates/login.html`. One inline mid-session fix: `save_sources()` now preserves root-level sibling keys.

**No commits were made in the 2026-07-02 session** — Alfonso has not yet reviewed/committed that 17-file diff. Verify `git status` before assuming it's landed.

## What's Done

- **Phase 1 (Foundation):** Sector-based pipeline, grounded analyst prompt, daily cadence
- **Phase 2 (AI Brain):** ChromaDB, RAG, feedback loop, weekly summarizer
- **Phase 3 (Web Dashboard):** Structured JSON output, Flask dashboard, two-page split (deploy step still outstanding)
- **Phase 3.5:** Dark glass hero revamp, sticky scroll nav, Space Grotesk + AOS
- **Real Sources Finalization:** 30 active real sources (later expanded to 62), branding fix, feedback-loop demo
- **"Phase 4" (Efficiency & Coverage, 2026-06-26):** All 8 steps — see naming-collision note in ROADMAP.md
- **Pipeline Optimization:** Scrapling integration, dead code removal, filter rebalancing, stage-by-stage verification
- **Information Density Fix:** Per-sector synthesis architecture. Signal count 7 → 65.
- **Frontend Redesign (Prototype #3):** Collapsible entity groups, spotlight, sector colors, dark mode, source links
- **Country Source Template:** `docs/source_submission_template.xlsx`
- **Supervisor Feedback Round 2 — all 8 topics (A1-A3, B1-B3, C1-C2, D1-D6, E1-E4, F1-F4):** scoring rubric + clamp, opportunity source links, PDF export, `sources.py`→`sources.json` + domain field, viewer/admin auth, source-suggestion queue + admin approval UI, company-context 7-sector rebuild, domain switcher (`--domain` flag), `--country` flag + ChromaDB `where` plumbing
- **Workflow migration (this session, 2026-07-08):** New CLAUDE.md (foundational template, customized), `.context/OVERVIEW.md`, `.context/DECISIONS.md`, `.context/ROADMAP.md`, `.context/STATE.md` written from the old context files + codebase scan + `PROJECT_REQUIREMENTS.md`. Old files pending subagent-verified deletion.

## What's In Progress

- Workflow migration: new `.context/` files written; a verification subagent still needs to confirm nothing from the old files was lost before the old files are deleted.

## Next Action

Confirm `git status` reflects exactly the 17 files touched in the 2026-07-02 Supervisor Feedback Round 2 session, since that diff was never committed. Then, the first real pipeline exercise of the new scaffolding: `py main.py --no-email --domain=BER --country=SG` — produces `data/latest_report_SG_BER.json`, exercising the domain-scoped file loading fallback end-to-end for the first time. **Only run this when Groq's daily quota is fresh** — a full run consumes real TPD budget.

## Known Bugs / Open Items

- **Feedback digest and weekly-summary country-scoping** — both still global/unscoped; open question for Alfonso (see `.context/ROADMAP.md`).
- **A3 PDF export afterprint edge case** — `initPdfExport()`'s restore-state handler strips `.print-exclude` from all elements including `#pdf-export-panel` itself, which needs the class permanently. After the first PDF export, the panel loses its self-hiding class. Low-priority polish, not a first-run bug.
- **`sentence-transformers` still pulled transitively** — importing `pipeline.vectorstore` triggers a HuggingFace weight download at import time, despite the 2026-06-29 decision to drop this dependency. ChromaDB's default embedding function appears to still require it transitively.
- **`ADMIN_PASSWORD` empty-string default** — flagged to Alfonso to set the env var.
- **Widened opportunities relevance gate is not actually active** — described as applied/verified in the 2026-06-26 decision entries, but lost during the 2026-06-29/06-30 prompt restructuring. `SUMMARY_PROMPT` currently uses a keyword-only gate. Not part of the Round 2 scope; flagged for a future session.
- **Customers sector historically thin** — only 1 source passed filter, 0 signals, in at least one past real run. Worth re-checking after the full source expansion.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — unreviewed by Alfonso; see ROADMAP.md open questions.
