# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## Current Position

Feature `003-vietnam-country` (branch `feature/003-vietnam-country`, this worktree) passed `/feature-verify` — all 8 tasks done, evidence gate green (`REVIEW.md` committed at `61881cb`). This feature adds Vietnam (`VN`) as a second, fully independent country in the pipeline, exercising the `--country` scaffolding for the first time against real second-country data. Concretely: a new `"Vietnam"/"VN"` block in `config/sources.json` with 60 sources (customers 32, competitors 10, gov_agencies 7, partners 7, general_news 4) and its own `priority_keywords`(14)/`keywords`(76) lists, mapped from the supplied VN source-list categories per an explicit sector-mapping rule; live scraper verification against all 60 (32 default fetcher, 11 stealth, 43 active / 17 inactive with recorded `inactive_reason`s, 8 of those pre-existing no-URL stubs); country-aware Flask routing via a new `_country_mode()` helper mirroring the existing `_domain_mode()` pattern (`/`, `/internals`, `/admin` all `?country=SG|VN`-aware); a working country switcher in `templates/base.html` (real `<a href="/?country=VN&domain=...">` links; MY/ID remain inert placeholder `<span>`s) with domain tabs now preserving the selected country; `admin.html`'s country `<select>` now loops all countries from `config/sources.json` instead of a hardcoded single `SG` option; `pipeline/analyst.py`'s `SUMMARY_PROMPT` no longer hardcodes "Singapore" — interpolates `country["name"]` via `str.replace()` (not `.format()`, to avoid colliding with the prompt's JSON-brace schema block); a parallel Vietnam subsection added to `data/company_context.md`'s Key Prospects & Relationships and Ecosystem Players sections (Vingroup, Sun Group, VSIP, FPT, Viettel, Becamex, etc.), with the `COMPANY_CONTEXT` vectorstore re-seeded (41 chunks, up from 34, live-verified "Vingroup" present / "SpatioX" absent); and — the one item explicitly *not* deferred again — `pipeline/feedback.py` and `pipeline/weekly.py` are now country-scoped (`country_code` parameter, `where={"country": ...}` filtering on ChromaDB reads/writes), closing a previously-recorded global/unscoped gap, plus `run_metadata.json` is now written per-country as `run_metadata_{code}.json`.

This feature branched cleanly from `main` (`168810e`), not from the sibling `feature/002-local-llm-backend` branch also present in this repo — the two features were worked concurrently in separate git worktrees this session (`SilverSea_Market_Inteligence-vietnam` for this one), a new pattern for this project letting two Claude Code sessions work the same repo without colliding on branch checkouts. `feature/003-vietnam-country` is not yet merged to `main` as of this update — same open-merge pattern as Feature 001.

**Three open items carried forward, none blocking the PASS:** (1) a fresh `py main.py --country=VN --domain=BER` run is still an Alfonso-owned manual checkpoint (Groq quota) — there are now *two* such outstanding checkpoints, this one and Feature 001's still-open `--country=SG` run; (2) real-browser visual QA of the new country-tab styling in `base.html` — code-level Jinja/Tailwind correctness was verified, pixels need eyes, same category as Feature 001's still-open `login.html`/`admin.html`/PDF-print checkpoints; (3) `pipeline/weekly.py`'s `WEEKLY_PROMPT` still hardcodes "Singapore" in its system framing — same bug class Task 006 fixed in `SUMMARY_PROMPT`, explicitly out of this feature's declared scope (Task 008's constraints preserved all three weekly/feedback prompt constants verbatim), logged as a small future follow-up, not blocking. The data-layer country-scoping fix (feedback.py/weekly.py) means a VN weekly summary would still only ever compress genuine VN daily reports — this is a prompt-content quality bug, not a data-independence bug.

Last activity: 2026-07-08 — `/feature-verify` PASS for `003-vietnam-country` (commits `86daa43`..`519c772` on `feature/003-vietnam-country`, plus `61881cb` for `REVIEW.md`). Branch not yet merged to `main`.

## What's Done

- **Phase 1 (Foundation):** Sector-based pipeline, grounded analyst prompt, daily cadence
- **Phase 2 (AI Brain):** ChromaDB, RAG, feedback loop, weekly summarizer
- **Phase 3 (Web Dashboard):** Structured JSON output, Flask dashboard, two-page split (deploy step still outstanding)
- **Phase 3.5:** Dark glass hero revamp, sticky scroll nav, Space Grotesk + AOS
- **Real Sources Finalization:** 62 total SG sources (57 active), branding fix, feedback-loop demo
- **"Phase 4" (Efficiency & Coverage, 2026-06-26):** All 8 steps — see naming-collision note in ROADMAP.md
- **Pipeline Optimization:** Scrapling integration, dead code removal, filter rebalancing, stage-by-stage verification
- **Information Density Fix:** Per-sector synthesis architecture. Signal count 7 → 65.
- **Frontend Redesign (Prototype #3):** Collapsible entity groups, spotlight, sector colors, dark mode, source links
- **Country Source Template:** `docs/source_submission_template.xlsx`
- **Supervisor Feedback Round 2 — all 8 topics (A1-A3, B1-B3, C1-C2, D1-D6, E1-E4, F1-F4):** scoring rubric + clamp, opportunity source links, PDF export, `sources.py`→`sources.json` + domain field, viewer/admin auth, source-suggestion queue + admin approval UI, company-context 7-sector rebuild, domain switcher (`--domain` flag), `--country` flag + ChromaDB `where` plumbing
- **Workflow migration (2026-07-08):** New CLAUDE.md, `.context/OVERVIEW.md`, `.context/DECISIONS.md`, `.context/ROADMAP.md`, `.context/STATE.md` replacing the old ad hoc context files.
- **Feature 001 — Round 2 Remediation (2026-07-08, PASSED):** Auth bypass fix + `/feedback` hardening, PDF afterprint fix, SpatioX→real-catalog rebuild across `company_context.md` and `analyst.py`, EDU keywords + NUS/NTU dual-tagging, `COMPANY_CONTEXT` vectorstore reseed, admin country selector + `approve()` disk-reread fix, first unit test (`tests/test_clamp.py`).
- **Feature 003 — Vietnam Country Expansion (2026-07-08, PASSED, this worktree):** Vietnam wired end-to-end — 60 VN sources (43 active) in `config/sources.json`, country-aware Flask routing (`_country_mode()`), working country switcher UI, dynamic admin country dropdown, country-scoped feedback/weekly-summary ChromaDB access (previously global/unscoped — real gap closed, not deferred), country-scoped `run_metadata.json`, VN subsection in `company_context.md` + vectorstore reseed (41 chunks), `SUMMARY_PROMPT` no longer hardcodes "Singapore". First real exercise of the `--country` scaffolding against a second country's live data.

## What's In Progress

Nothing actively in flight in this worktree. `003-vietnam-country` is complete and PASSed but its branch (`feature/003-vietnam-country`) is not yet merged to `main`. (Note: a separate `feature/002-local-llm-backend` branch/worktree exists in this repo with its own in-progress work — not covered by this update, which is scoped to this worktree only.)

## Next Action

Merge `feature/003-vietnam-country` to `main` (confirm with Alfonso first, and coordinate with whatever state `feature/002-local-llm-backend` is in, since both branch from/near the same `main` and were worked concurrently). Then work through the three open items in whatever order Alfonso prefers: a fresh `py main.py --country=VN --domain=BER` run (Groq-quota-gated), real-browser visual QA of the `base.html` country-tab styling, and the small `WEEKLY_PROMPT` Singapore-hardcoding follow-up.

## Known Bugs / Open Items

- **Two Groq-quota-gated manual checkpoints now outstanding** (Alfonso-owned): (1) Feature 001's `py main.py --domain=BER --country=SG` run; (2) Feature 003's `py main.py --country=VN --domain=BER` run — first-ever live combination of VN scraping + Groq analysis.
- **Two real-browser visual QA checkpoints now outstanding** (Alfonso-owned, code-level correctness already verified for both): (1) Feature 001's `login.html`/`admin.html` styling + PDF print-preview; (2) Feature 003's `base.html` country-tab styling.
- **`pipeline/weekly.py`'s `WEEKLY_PROMPT` hardcodes "Singapore"** — same bug class as the `SUMMARY_PROMPT` fix in Feature 003's Task 006, but out of that feature's declared scope (Task 008 deliberately preserved `WEEKLY_PROMPT`/`SUMMARIZE_PROMPT`/`CONSOLIDATION_PROMPT` verbatim). Data-layer scoping is already correct (a VN weekly run only compresses VN-tagged reports); this is a prompt-content quality bug, not a data-independence bug. Small, well-understood follow-up — mirror Task 006's `str.replace()` pattern.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one — likely lost during the dead-code removal pass or never actually built.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16` instantiates `SentenceTransformerEmbeddingFunction` directly).
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc.
  - `pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset, unlike the graceful-skip pattern in `feedback.py`/`weekly.py`.
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **`ADMIN_PASSWORD` empty-string default** — safe (refuses login when unset) but not functional; Alfonso still needs to set the env var to actually use admin login.
- **Widened opportunities relevance gate is not active** — gate stays keyword-only by design; reinstating the previously-lost "ecosystem entity action" second path remains a separate, deferred decision.
- **Customers sector historically thin (SG)** — only 1 source passed filter, 0 signals, in at least one past real run. Worth re-checking after the full source expansion.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; untouched by Feature 003 (VN sources added alongside it, not resolving it).
- **VN sources may under-perform the keyword filter** — VN keywords are English-only this round (no Vietnamese-language matching); Vietnamese-only government/local sources are an accepted, known limitation, not yet empirically checked against a live run (blocked on the VN quota-gated checkpoint above).
- **MY/ID country expansion** — still fully unbuilt; Feature 003 establishes a reusable pattern (country-scoping, `_country_mode()`, sector-mapping approach) but doesn't extend to them.
