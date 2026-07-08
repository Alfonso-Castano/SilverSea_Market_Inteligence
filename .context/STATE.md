# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## Current Position

Feature `001-round2-remediation` (branch `feature/001-round2-remediation`) passed `/feature-verify` — all 8 tasks done, evidence gate green. This feature fixed the admin/viewer auth bypass and moved both password comparisons to `hmac.compare_digest` in `app.py`; closed three `/feedback` hardening gaps found by a broader recon pass (submitter path-traversal sanitization, `relevance_rating` crash guard returning a clean 400 instead of a 500, CORS scoped to `/feedback` only instead of every route); finished the SpatioX→real-catalog rebuild consistently across `data/company_context.md` (Target Sectors, Key Prospects, Ecosystem Players sections) and `pipeline/analyst.py` (`SUMMARY_PROMPT`, opportunities gate keywords, `product_fit` instruction, `_generate_implications`, `_derive_competition_risks`) — zero `SpatioX` references remain in either file; added EDU filter keywords to `config/sources.json`'s shared keyword list and dual-tagged NUS/NTU as `["BER","EDU"]`; re-seeded ChromaDB's `COMPANY_CONTEXT` collection (live-verified: 34 chunks, no SpatioX residue); added an admin country selector (`templates/admin.html`) and fixed `source_suggestions.approve()`'s stale-`COUNTRIES`-singleton bug via a new `config/sources.py` `load_sources()` that re-reads disk; and added the repo's first unit test (`tests/test_clamp.py`, 6 cases, all passing) for the opportunity-scoring clamp. The PDF-export afterprint bug (`static/animations.js`) was also fixed on this branch.

**Two manual checkpoints remain open and un-actioned** (Alfonso-owned, not blocking the PASS): (1) a fresh `py main.py --domain=BER --country=SG` run to exercise the fixes end-to-end — quota-gated, only run on a fresh Groq daily quota; (2) visual QA of `login.html`/`admin.html` styling and real-browser PDF print-preview — code-level structure was checked, pixels need eyes.

Last activity: 2026-07-08 — `/feature-verify` PASS for `001-round2-remediation` (commits `9c64642`..`4545563` on `feature/001-round2-remediation`, plus the `d638077` vectorstore reseed and the feature's `CONTEXT.md`/`RESEARCH.md`/task files/`REVIEW.md`). Branch not yet merged to `main` as of this update.

## What's Done

- **Phase 1 (Foundation):** Sector-based pipeline, grounded analyst prompt, daily cadence
- **Phase 2 (AI Brain):** ChromaDB, RAG, feedback loop, weekly summarizer
- **Phase 3 (Web Dashboard):** Structured JSON output, Flask dashboard, two-page split (deploy step still outstanding)
- **Phase 3.5:** Dark glass hero revamp, sticky scroll nav, Space Grotesk + AOS
- **Real Sources Finalization:** 62 total sources (57 active per Feature 001's evidence gate), branding fix, feedback-loop demo
- **"Phase 4" (Efficiency & Coverage, 2026-06-26):** All 8 steps — see naming-collision note in ROADMAP.md
- **Pipeline Optimization:** Scrapling integration, dead code removal, filter rebalancing, stage-by-stage verification
- **Information Density Fix:** Per-sector synthesis architecture. Signal count 7 → 65.
- **Frontend Redesign (Prototype #3):** Collapsible entity groups, spotlight, sector colors, dark mode, source links
- **Country Source Template:** `docs/source_submission_template.xlsx`
- **Supervisor Feedback Round 2 — all 8 topics (A1-A3, B1-B3, C1-C2, D1-D6, E1-E4, F1-F4):** scoring rubric + clamp, opportunity source links, PDF export, `sources.py`→`sources.json` + domain field, viewer/admin auth, source-suggestion queue + admin approval UI, company-context 7-sector rebuild, domain switcher (`--domain` flag), `--country` flag + ChromaDB `where` plumbing
- **Workflow migration (2026-07-08):** New CLAUDE.md, `.context/OVERVIEW.md`, `.context/DECISIONS.md`, `.context/ROADMAP.md`, `.context/STATE.md` replacing the old ad hoc context files.
- **Feature 001 — Round 2 Remediation (2026-07-08, PASSED):** Auth bypass fix + `/feedback` hardening, PDF afterprint fix, SpatioX→real-catalog rebuild across `company_context.md` and `analyst.py`, EDU keywords + NUS/NTU dual-tagging, `COMPANY_CONTEXT` vectorstore reseed, admin country selector + `approve()` disk-reread fix, first unit test (`tests/test_clamp.py`).

## What's In Progress

Nothing actively in flight. `001-round2-remediation` is complete and PASSed but its branch (`feature/001-round2-remediation`) is not yet merged to `main`.

## Next Action

Merge `feature/001-round2-remediation` to `main` (confirm with Alfonso first — no prior feature branch in this project has gone through a merge step). Then work through the two open manual checkpoints in either order: a fresh `py main.py --domain=BER --country=SG` run (only once Groq's daily quota is fresh — first real end-to-end exercise of the remediated pipeline), and visual QA of `login.html`/`admin.html` + real-browser PDF print-preview.

## Known Bugs / Open Items

- **Two manual checkpoints from Feature 001, still open:** (1) fresh `py main.py --domain=BER --country=SG` run — quota-gated; (2) visual QA of `login.html`/`admin.html` + real-browser PDF print-preview.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, explicitly out of scope there, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one — likely lost during the dead-code removal pass or never actually built. Worth a DECISIONS.md correction note when addressed.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16` instantiates `SentenceTransformerEmbeddingFunction` directly) — corrects the prior framing below, which called it transitive; that was factually wrong.
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `run_metadata.json` isn't domain/country-scoped — only the last country's metadata survives a multi-country run. Harmless today (SG-only).
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc — related to the country-scoping gap below.
  - `pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset, unlike the graceful-skip pattern in `feedback.py`/`weekly.py`.
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **Feedback digest and weekly-summary country-scoping** — both still global/unscoped; explicitly re-deferred in Feature 001 (out of scope). Open question for Alfonso.
- **`ADMIN_PASSWORD` empty-string default** — the bypass fix makes this *safe* (refuses login when unset) but not *functional*; Alfonso still needs to set the env var to actually use admin login.
- **Widened opportunities relevance gate is not active** — Feature 001 confirmed the gate stays keyword-only by design (EDU terms added alongside BER terms); reinstating the previously-lost "ecosystem entity action" second path remains a separate, deferred decision.
- **Customers sector historically thin** — only 1 source passed filter, 0 signals, in at least one past real run. Worth re-checking after the full source expansion.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; Feature 001's admin country-selector change touched the same file but did not resolve this flag.
- **Bookkeeping correction** — ROADMAP.md previously recorded 54 active sources; Feature 001's evidence gate confirmed 62 total / 57 active. Corrected in ROADMAP.md this pass.
