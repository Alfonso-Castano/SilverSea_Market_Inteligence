# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## ⚠️ Branch stack note — read before trusting this file

This worktree is `feature/006-vn-my-accuracy-review`, branched from `feature/005-domain-activation`'s tip (`16db787`), which itself sits on `integration/vn-my-review` (which merges `feature/003-vietnam-country` + `feature/004-malaysia-country`). So this is a 4-deep unmerged stack: `feature/003` + `feature/004` → `integration/vn-my-review` → `feature/005-domain-activation` → `feature/006-vn-my-accuracy-review` (this branch). None of it is in `main` yet.

## Current Position

**Feature `006-vn-my-accuracy-review` PASSed `/feature-verify`** (`REVIEW.md` at `4fb9dc3`, all 9 tasks done, evidence gate green). This was a deliberately read-mostly audit — no live pipeline run, no Groq/LLM calls — checking the VN/MY/domain-activation work shipped in Features 003-005 for (1) report-content accuracy against live-refetched source pages, and (2) code-correctness (domain filtering, sector mapping, gates, RAG). Deliverables: `.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md` and `CODE-REVIEW.md`.

**Headline finding — `source_name` attribution is broken, and it predates this session:** 42 of 43 VN signals + all 3 VN opportunities carry the literal placeholder string `"Extracted signals"` (or lowercase variant) as `source_name` instead of a real, joinable source name; MY is milder (5 of 9 signals + all opportunities affected). Root cause is in `pipeline/analyst.py:174`'s `_synthesize_sector()` — the synthesis user-message wraps extraction text under the literal label `"Extracted signals:\n{extraction_text}"` with no enforced per-source delimiter, so the model grabs that label itself as `source_name`. Git-dated to 2026-06-29 (commits `ebd90f6`/`59e4f52`) — this **predates** Features 003/004/005 entirely. It's a testing-coverage gap (three separate green `/feature-verify` gates checked code-matches-spec, not report-content fidelity, and none caught it), not a regression introduced by this session's rapid dispatches. Left flagged, not fixed — needs prompt-engineering judgment on `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT`, not a mechanical patch.

**Other findings, all flagged and NOT fixed this feature** (see DECISIONS.md for full detail): fabricated Silversea product names in several opportunities' `product_fit` fields (e.g. "Building Automation", "Smart Building", "E-learning solutions" — none are real catalog products); one VN signal (Becamex IDC) contains text copy-pasted near-verbatim from a different cited source (Viettel Group) — cross-source content contamination; `filter.py`'s per-country relevance gate and `SUMMARY_PROMPT`'s hardcoded-global opportunities gate diverge, widest for VN (4 dual-tagged BER+EDU sources create an EDU→BER leak path); `_build_rag_context()` is confirmed dead code (never called), and `REPORT_HISTORY` writes are country-scoped but domain-blind — a dormant cross-domain contamination trap if RAG is ever restored; `analyse()` still receives no explicit `domain` parameter, so every `product_fit` judgment reasons across all 7 sector catalogs regardless of which domain the report is actually for. A sample of the session's 24 rapid-dispatch commits (Features 003/004/005) turned up only Low/Informational findings — no new correctness bug was introduced by the dispatches themselves.

**Three low-risk mechanical fixes were applied, each its own commit, Alfonso-approved:**
- `14adeb3` — `app.py`'s `report()` domain-fallback tuple widened from 3 to all 8 domains (matches `_domain_mode()`). Fixes a latent bug, currently masked for VN/MY, where a country whose only report is e.g. RCC/PSS would wrongly fall back to legacy `latest_report.json`.
- `106ca9b` — `pipeline/analyst.py`'s `analyse()` now uses `os.environ.get("GROQ_API_KEY", "")` instead of `os.environ["GROQ_API_KEY"]`, degrading gracefully instead of `KeyError` on an unset key. **Resolves** a previously-tracked known-bug (see Known Bugs below).
- `0a3f907` — `pipeline/weekly.py`'s `WEEKLY_PROMPT` now threads real `country_name` (was hardcoded `"Singapore"` for every country); `main.py`'s call site passes `country["name"]`. **Resolves** another previously-tracked known-bug.

`feature/006-vn-my-accuracy-review` is PASSed but **not yet merged to `main`** — same pending-merge state as every prior feature branch in this stack (002 through 005).

Last activity: 2026-07-13 — `/feature-verify` PASS for `006-vn-my-accuracy-review` (commits `e0bb371`..`4fb9dc3` on `feature/006-vn-my-accuracy-review`, branched from `feature/005-domain-activation` tip `16db787`).

## What's Done

- **Phase 1 (Foundation):** Sector-based pipeline, grounded analyst prompt, daily cadence
- **Phase 2 (AI Brain):** ChromaDB, RAG, feedback loop, weekly summarizer
- **Phase 3 (Web Dashboard):** Structured JSON output, Flask dashboard, two-page split (deploy step still outstanding)
- **Phase 3.5:** Dark glass hero revamp, sticky scroll nav, Space Grotesk + AOS
- **Real Sources Finalization:** 62 total SG sources (57 active per Feature 001's evidence gate), branding fix, feedback-loop demo
- **"Phase 4" (Efficiency & Coverage, 2026-06-26):** All 8 steps — see naming-collision note in ROADMAP.md
- **Pipeline Optimization:** Scrapling integration, dead code removal, filter rebalancing, stage-by-stage verification
- **Information Density Fix:** Per-sector synthesis architecture. Signal count 7 → 65.
- **Frontend Redesign (Prototype #3):** Collapsible entity groups, spotlight, sector colors, dark mode, source links
- **Country Source Template:** `docs/source_submission_template.xlsx`
- **Supervisor Feedback Round 2 — all 8 topics (A1-A3, B1-B3, C1-C2, D1-D6, E1-E4, F1-F4):** scoring rubric + clamp, opportunity source links, PDF export, `sources.py`→`sources.json` + domain field, viewer/admin auth, source-suggestion queue + admin approval UI, company-context 7-sector rebuild, domain switcher (`--domain` flag), `--country` flag + ChromaDB `where` plumbing
- **Workflow migration (2026-07-08):** New CLAUDE.md, `.context/OVERVIEW.md`, `.context/DECISIONS.md`, `.context/ROADMAP.md`, `.context/STATE.md` replacing the old ad hoc context files.
- **Feature 001 — Round 2 Remediation (2026-07-08, PASSED):** Auth bypass fix + `/feedback` hardening, PDF afterprint fix, SpatioX→real-catalog rebuild across `company_context.md` and `analyst.py`, EDU keywords + NUS/NTU dual-tagging, `COMPANY_CONTEXT` vectorstore reseed, admin country selector + `approve()` disk-reread fix, first unit test (`tests/test_clamp.py`). Merged to base as of `168810e`.
- **Feature 003 — Vietnam Country Expansion (2026-07-08, PASSED):** Vietnam wired end-to-end — 60 VN sources (43 active), country-aware Flask routing (`_country_mode()`), working country switcher UI, dynamic admin country dropdown, country-scoped feedback/weekly-summary ChromaDB access, country-scoped `run_metadata.json`, VN subsection in `company_context.md` + vectorstore reseed, `SUMMARY_PROMPT` no longer hardcodes "Singapore". Not yet merged to `main`.
- **Feature 004 — Malaysia Country Expansion (2026-07-10, PASSED):** MY country block (55 sources, 52 active), sector mapping, dual GENERAL+real-domain tagging, MY-specific keyword lists, `company_context.md` Malaysia subsection, `COMPANY_CONTEXT` reseed. Touched zero Python files. Not yet merged to `main`.
- **Integration review branch (2026-07-10, `integration/vn-my-review`):** Merged Vietnam + Malaysia together for Alfonso's combined dashboard review; later became the real base for Feature 005 rather than staying a throwaway scaffold.
- **Feature 005 — Full Domain Activation (2026-07-10, PASSED):** All 8 business domains (BER/EDU/GENERAL + RCC/HLS/MFG/CTE/PSS) now first-class, routable, analyzed pipeline domains — `_domain_mode()`, `base.html`/`admin.html` UI, `SUMMARY_PROMPT` product catalogs + broadened opportunities gate, `company_context.md` caveat removal. Vietnam's sources retroactively retagged with real business domains (30 sources, mirroring Malaysia's pattern). Malaysia and Singapore needed zero source changes. Not yet merged to `main`.
- **Source-document archival (2026-07-10, commit `851853b`):** Original ground-truth source submissions behind Features 003/004 archived to `docs/`.
- **Feature 006 — VN/MY Accuracy & Code-Correctness Review (2026-07-13, PASSED, not yet merged):** Two-part audit (report-content accuracy vs. live-refetched sources; code-correctness of domain/sector/gate wiring) of everything shipped in Features 003-005, deliberately with no live pipeline run and no Groq/LLM calls. Found the `source_name` attribution breakage (pre-existing, predates this session), fabricated product names in opportunity `product_fit` fields, one cross-source contamination instance, filter/opportunities-gate divergence, dead `_build_rag_context()` + domain-blind `REPORT_HISTORY`. Applied 3 low-risk mechanical fixes (`app.py` domain fallback, `analyst.py` graceful `GROQ_API_KEY` degradation, `weekly.py` country-name threading); left the deeper findings flagged for a future prompt-engineering pass. See `.context/DECISIONS.md` for full detail.

## What's In Progress

Nothing actively in flight. Feature 006 is complete and PASSed. `feature/006-vn-my-accuracy-review` sits atop a 4-deep unmerged stack (`feature/003-vietnam-country` + `feature/004-malaysia-country` → `integration/vn-my-review` → `feature/005-domain-activation` → `feature/006-vn-my-accuracy-review`) — none merged to `main`.

## Next Action

Alfonso to decide how to handle the flagged `source_name` attribution breakage — the headline finding, affecting nearly every VN signal/opportunity's source citation — likely as its own future `/feature-discuss` scoping a prompt-engineering rework of `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT` (e.g. forcing extraction output into a rigid per-source structure) rather than a mechanical patch. In parallel, and lower urgency, Alfonso can decide real merge order/strategy for the now-4-deep branch stack into `main`, and whether to schedule the other flagged-not-fixed findings (fabricated product names, filter/gate divergence, dead RAG scoping, `analyse()`'s missing `domain` parameter) into that same future pass or a separate one.

## Known Bugs / Open Items

- **NEW headline finding (2026-07-13, Feature 006): `source_name` attribution broken, pre-dates this session.** 42/43 VN signals + all 3 VN opportunities, 5/9 MY signals, carry a literal placeholder (`"Extracted signals"`/`"extracted signals"`) instead of a real source name. Root cause: `pipeline/analyst.py:174`'s `_synthesize_sector()` user-message has no enforced per-source delimiter around extraction text. Git-dated to 2026-06-29 (`ebd90f6`/`59e4f52`) — predates Features 003/004/005; a testing-coverage gap (3 prior green `/feature-verify` gates checked spec-conformance, not content fidelity), not a rapid-dispatch regression. Flagged, not fixed — needs prompt-engineering judgment, not a mechanical patch.
- **NEW (2026-07-13, Feature 006): fabricated product names in opportunity `product_fit` fields** — both VN and MY reports emit product names not in Silversea's real catalog (e.g. "Building Automation", "Smart Building", "E-learning solutions"). A consistent weak spot across both countries. Flagged, not fixed.
- **NEW (2026-07-13, Feature 006): one confirmed cross-source content contamination instance** — a VN Becamex IDC signal contains text copy-pasted near-verbatim from a different cited source (Viettel Group) in the same report. Isolated finding, not systemically checked beyond this one instance.
- **NEW (2026-07-13, Feature 006): `filter.py` relevance gate vs. `SUMMARY_PROMPT` opportunities gate diverge** — `filter.py` uses per-country config keywords; `SUMMARY_PROMPT`'s opportunities gate uses one hardcoded global keyword list. Aligned for MY, looser than `filter.py` for VN, where 4 (not 2 as earlier research suggested) BER+EDU dual-tagged sources create an EDU→BER leak path. Flagged, not fixed.
- **NEW (2026-07-13, Feature 006): dead `_build_rag_context()` confirmed + domain-blind `REPORT_HISTORY`** — the function is never called; `REPORT_HISTORY` writes are country-scoped but not domain-scoped, a dormant cross-domain contamination trap if RAG context is ever restored. Flagged, not fixed.
- **NEW (2026-07-13, Feature 006): `analyse()` never receives an explicit `domain` parameter** — every `product_fit` judgment reasons across all 7 sector product catalogs regardless of which domain the report is actually being generated for. Architecturally non-trivial; flagged as a lead, not fixed.
- **RESOLVED (2026-07-13, Feature 006): `pipeline/analyst.py` crashing on unset `GROQ_API_KEY`.** Now degrades gracefully via `os.environ.get(..., "")`, matching `feedback.py`/`weekly.py`'s existing pattern. Do not reopen.
- **RESOLVED (2026-07-13, Feature 006): `pipeline/weekly.py`'s `WEEKLY_PROMPT` hardcoding "Singapore".** Now threads real `country_name` per-run. Do not reopen.
- **RESOLVED (2026-07-10, Feature 005): Full 7-domain activation.** All 8 domains (BER/EDU/GENERAL/RCC/HLS/MFG/CTE/PSS) are active, routable, and analyzed. Do not reopen.
- **SG's own domain coverage for RCC/HLS/MFG/CTE/PSS remains fully unstarted** — no real SG sources tagged for these 5 verticals; SG will show empty results under those domain tabs until/unless real SG sources are added.
- **4-deep unmerged branch stack** — `feature/003-vietnam-country` + `feature/004-malaysia-country` → `integration/vn-my-review` → `feature/005-domain-activation` → `feature/006-vn-my-accuracy-review`, none merged to `main`. `integration/vn-my-review` is load-bearing, not a throwaway scaffold.
- **`admin.html`'s domain checkboxes only render when `data/pending_sources/` is non-empty** — pre-existing wrapper, predates Feature 005/006, not a defect either introduced.
- **Live pipeline runs, all still open, all Groq-quota-gated, all Alfonso-owned:** VN's `py main.py --country=VN --domain=BER` ran once (Feature 003 review); MY's equivalent has not happened yet; a fresh VN/MY run under the broadened Feature 005 opportunities gate would confirm whether non-BER/EDU signals now actually generate `opportunities` entries; SG's own `py main.py --domain=BER --country=SG` run from Feature 001 is also still outstanding. Note: given the `source_name` breakage finding, a fresh run alone won't fix report quality — the prompt-engineering rework needs to land first for a re-run to be diagnostically useful.
- **Malaysia's signals-visible-but-opportunities-gated asymmetry** — narrowed by Feature 005's broadened gate, but not confirmed without a live run.
- **Real-browser visual QA** of the domain-tab and country-tab styling in `base.html`, `login.html`/`admin.html`, and PDF print-preview — all still open, pixels-need-eyes items from Features 001/005.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16`).
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `run_metadata.json` isn't domain-scoped (only country-scoped).
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc.
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **`ADMIN_PASSWORD` empty-string default** — safe (refuses login when unset) but not functional; Alfonso still needs to set the env var to actually use admin login.
- **Customers sector historically thin (SG)** — only 1 source passed filter, 0 signals, in at least one past real run.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; untouched by Features 003, 004, 005, or 006.
- **VN sources may under-perform the keyword filter** — VN keywords are English-only (no Vietnamese-language matching); not yet empirically checked against a live run.
- **ID country expansion** — still fully unbuilt; VN/MY establish a reusable pattern but don't extend to it.
- **Bookkeeping correction (carried from Feature 001)** — ROADMAP.md previously recorded 54 active SG sources; Feature 001's evidence gate confirmed 62 total / 57 active.
