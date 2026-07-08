# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## Current Position

`feature/001-round2-remediation` was merged to `main` (18 commits, clean, no conflicts) earlier this session. `feature/002-local-llm-backend` was then branched from the resulting `main` (`168810e`) and just passed `/feature-verify` — all 4 tasks done, evidence gate green (`.context/features/002-local-llm-backend/REVIEW.md`, PASS). This feature added a config-switchable local LLM backend to `pipeline/analyst.py`: a new `LLM_BACKEND` env var (`groq`|`local`, default `groq`, in `config/models.py`) routes all 3 of `analyst.py`'s LLM call sites through one `_chat_completion` dispatch helper. The local path uses Ollama's native `/api/chat` structured-outputs mechanism (real `ollama.chat()`, `format=` JSON-schema enforcement) — not an OpenAI-SDK/`base_url` shim, since Ollama's OpenAI-compatible endpoint doesn't support genuine JSON-schema enforcement. Target model is Qwen3-32B at Q6_K quantization on Alfonso's own hardware (RTX 5090, 32GB VRAM — corrects an earlier in-session "RTX 5070" assumption that never landed in any committed file). Qwen3-32B Q6_K isn't a standard Ollama library tag; it requires a manual GGUF import (`bartowski/Qwen3-32B-GGUF` via a one-line Modelfile, done outside the repo) — `config/models.py`'s `LOCAL_MODEL` defaults to the tag `qwen3-32b-q6k`. `README.md` gained a full 7-step "Local LLM Setup (Optional)" runbook. `tests/test_local_backend_smoke.py` is the feature's evidence gate; it skips cleanly on this dev machine (no Ollama server running here) — an accepted by-design PASS state, not a gap. The Groq path is confirmed byte-for-byte unchanged (default/unset `LLM_BACKEND` behavior untouched); `pipeline/feedback.py`/`pipeline/weekly.py` still hardcode Groq (out of this feature's scope, noted as a known limitation).

`feature/002-local-llm-backend` is done and PASSed but **not yet merged to `main`** — same pending-merge pattern Feature 001 was in before this session's merge.

A third, sibling branch — `feature/003-vietnam-country` (Vietnam country expansion: ~55 new sources, country-scoping fixes to `feedback.py`/`weekly.py`/`run_metadata.json`, a `company_context.md` Vietnam subsection) — was developed concurrently in a separate git worktree (`C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence-vietnam`, same `.git`) by a separate Claude Code session, specifically to avoid two sessions colliding on one working-directory checkout. Its task execution just finished per Alfonso, but it has **not been tested or verified** — no `/feature-verify` has run against it yet. This is a sibling in-flight feature, not part of `002-local-llm-backend`'s scope, and is not marked complete here.

Last activity: 2026-07-08 — `/feature-verify` PASS for `002-local-llm-backend` (commits `bdc95af`..`d9ec0c5` on `feature/002-local-llm-backend`, branched from `main` at `168810e` post-Feature-001-merge).

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
- **Feature 001 — Round 2 Remediation (2026-07-08, PASSED, MERGED to `main`):** Auth bypass fix + `/feedback` hardening, PDF afterprint fix, SpatioX→real-catalog rebuild across `company_context.md` and `analyst.py`, EDU keywords + NUS/NTU dual-tagging, `COMPANY_CONTEXT` vectorstore reseed, admin country selector + `approve()` disk-reread fix, first unit test (`tests/test_clamp.py`).
- **Feature 002 — Local LLM Backend (2026-07-08, PASSED, not yet merged):** `LLM_BACKEND` config switch (`groq`|`local`, default `groq`) in `config/models.py`; `pipeline/analyst.py`'s 3 LLM call sites routed through a single `_chat_completion` dispatch helper; native Ollama `/api/chat` structured-output path for Qwen3-32B Q6_K (RTX 5090, 32GB VRAM); README 7-step local setup runbook; `tests/test_local_backend_smoke.py` smoke test (skips cleanly without a live Ollama server).

## What's In Progress

- `feature/002-local-llm-backend` — PASSed, awaiting merge to `main` (Alfonso decision, same as Feature 001's pre-merge state).
- `feature/003-vietnam-country` (separate worktree at `..\SilverSea_Market_Inteligence-vietnam`) — task execution finished per Alfonso, but **not yet tested or `/feature-verify`'d**. Sibling feature, developed by a separate session, not evaluated in this update.

## Next Action

Alfonso to decide real-world verification of the local Ollama/Qwen3-32B backend at a separate office computer with GPU access (clone this repo there, follow the README's "Local LLM Setup" runbook, confirm `tests/test_local_backend_smoke.py` actually exercises live calls rather than skipping) — this is a new, third open Alfonso-owned manual checkpoint alongside the two carried over from Feature 001. In parallel, Alfonso is deciding whether to test `feature/003-vietnam-country` before merging it. Merging `feature/002-local-llm-backend` to `main` is a separate open decision, not yet made.

## Known Bugs / Open Items

- **Three manual checkpoints now open, Alfonso-owned:** (1) fresh `py main.py --domain=BER --country=SG` run — quota-gated (from Feature 001); (2) visual QA of `login.html`/`admin.html` + real-browser PDF print-preview (from Feature 001); (3) live verification of the local Ollama/Qwen3-32B backend on GPU hardware (from Feature 002) — smoke test currently skips cleanly on this dev machine, which is by design but means the local backend has never actually run against a real model yet.
- **`feature/003-vietnam-country` untested** — developed in a separate worktree by a separate session; task execution finished but no verification has run. Not part of this update's scope.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, explicitly out of scope there, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one — likely lost during the dead-code removal pass or never actually built. Worth a DECISIONS.md correction note when addressed.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16` instantiates `SentenceTransformerEmbeddingFunction` directly) — corrects the prior framing below, which called it transitive; that was factually wrong.
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `run_metadata.json` isn't domain/country-scoped — only the last country's metadata survives a multi-country run. Harmless today (SG-only) but newly relevant once `feature/003-vietnam-country` lands.
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc — related to the country-scoping gap below.
  - `pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset, unlike the graceful-skip pattern in `feedback.py`/`weekly.py` — worth revisiting given Feature 002 now makes a Groq-free `LLM_BACKEND=local` run a real possibility for `analyst.py` itself (though `feedback.py`/`weekly.py` still hardcode Groq regardless).
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **`pipeline/feedback.py`/`pipeline/weekly.py` remain Groq-only** — Feature 002's `LLM_BACKEND=local` switch applies only to `pipeline/analyst.py`'s 3 call sites, by explicit scope; these two files still require `GROQ_API_KEY` even on a local-backend run.
- **Feedback digest and weekly-summary country-scoping** — both still global/unscoped; explicitly re-deferred in Feature 001 (out of scope). Open question for Alfonso, and now also touched by `feature/003-vietnam-country`'s in-progress country-scoping fixes (unverified).
- **`ADMIN_PASSWORD` empty-string default** — the bypass fix makes this *safe* (refuses login when unset) but not *functional*; Alfonso still needs to set the env var to actually use admin login.
- **Widened opportunities relevance gate is not active** — Feature 001 confirmed the gate stays keyword-only by design (EDU terms added alongside BER terms); reinstating the previously-lost "ecosystem entity action" second path remains a separate, deferred decision.
- **Customers sector historically thin** — only 1 source passed filter, 0 signals, in at least one past real run. Worth re-checking after the full source expansion.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; Feature 001's admin country-selector change touched the same file but did not resolve this flag.
- **Bookkeeping correction** — ROADMAP.md previously recorded 54 active sources; Feature 001's evidence gate confirmed 62 total / 57 active. Corrected in ROADMAP.md this pass.
- **AI-assisted relevance filtering and 3-phase pipeline architecture revisit** — both named as candidate future features during Feature 002's discussion, deliberately not built there: (1) evaluate `pipeline/filter.py`'s existing keyword-weighted scoring before deciding whether local-model judgment should append or replace it; (2) reconsider the extract→synthesize→summary 3-phase split now that local compute removes the Groq token-budget constraint that originally forced it — deferred until the local backend itself is proven stable.
