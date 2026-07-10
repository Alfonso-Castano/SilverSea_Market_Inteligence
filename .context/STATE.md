# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## ⚠️ Branch-local note — read before trusting this file

This STATE.md reflects **only** the git history of `feature/004-malaysia-country` (cut from `main` at `168810e`). A sibling branch, `feature/003-vietnam-country` (also cut from `168810e`, also PASSed `/feature-verify`), has its own independent `.context/` updates in its own worktree (`C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence-vietnam`) that do **not** appear here, because neither branch has merged to `main` yet. Do not treat this file as reflecting Vietnam's completion — it doesn't, by construction of the parallel-worktree pattern used this round. **Reconciling STATE.md/DECISIONS.md/ROADMAP.md content across both branches is an outstanding manual step for whoever merges second** — see Known Bugs / Open Items below.

## Current Position

**This is a temporary integration/review branch (`integration/vn-my-review`), not a feature branch — it exists solely so Alfonso can review Vietnam and Malaysia together in one working dashboard before deciding on real merge order into `main`.** It merges `feature/003-vietnam-country` and `feature/004-malaysia-country` (both independently PASSed `/feature-verify`, both still unmerged to `main`) into one combined branch. Neither original feature branch was altered by this merge — this STATE.md exists only on `integration/vn-my-review`.

Both features are complete and PASSed on their own branches:

- **Vietnam (`feature/003-vietnam-country`, PASSed 2026-07-08, `REVIEW.md` at `61881cb`):** VN added as a second, fully independent country — 60 sources in `config/sources.json` (43 active after live scraper verification), country-aware Flask routing (`_country_mode()` mirroring `_domain_mode()`, wired into `/`, `/internals`, `/admin`), a working country switcher in `base.html`, dynamic admin country dropdown, `SUMMARY_PROMPT` no longer hardcodes "Singapore", a Vietnam subsection in `company_context.md` (BER/EDU-flavored, matching VN's own domain-scope decision), and — the one item explicitly not deferred again — `pipeline/feedback.py`/`pipeline/weekly.py` now country-scoped (previously global/unscoped), plus per-country `run_metadata.json`.
- **Malaysia (`feature/004-malaysia-country`, PASSed 2026-07-10, `REVIEW.md` at `36d2530`):** MY added as a third country — 55 sources (52 active after live scraper verification), sector-mapped 1:1 via the submission's own Relationship Type column (customers 26, partners 10, competitors 8, gov_agencies 7, associations 3 — the first source list to populate `associations` with real non-SG entries, general_news 1). Every MY source tagged with both `"GENERAL"` and its real submitted business domain (BER/RCC/HLS/MFG/CTE/PSS/EDU) for forward-compatibility, even though only BER/EDU/GENERAL are active pipeline domains this round. MY's own keyword lists (15 priority + 99 general, the latter including 18 new cross-sector terms, since only 31% of MY's sources are BER-tagged). A Malaysia subsection in `company_context.md` covering the *full* real business breadth (not just BER/EDU, unlike Vietnam's). **This feature touched zero Python files** — entirely JSON/Markdown/HTML data — which is why, on Malaysia's own branch alone, the dashboard couldn't actually switch countries (no `app.py` routing existed there).

**Merging the two branches together on this integration branch is what makes the combined dashboard actually work**: Vietnam's `app.py`/`_country_mode()` routing now serves Malaysia's data too, and Malaysia's `company_context.md`/`base.html` content was reconciled with Vietnam's (both had independently touched the same insertion points — see the git history's merge commit for how the conflicts were resolved: `sources.json` and `company_context.md` combined by keeping both countries' additions in full; `base.html` resolved by keeping Malaysia's already-reproduced superset, since it independently contained SG+VN+MY all as real links).

**Two open manual checkpoints carried forward from Vietnam, plus one new one from Malaysia, none blocking:** (1) a live `py main.py --country=VN --domain=BER` run already happened once, successfully, during Alfonso's review session (two real bugs surfaced and fixed live: a Windows console UTF-8 crash on Vietnamese diacritics, and a missing `.env` in the VN worktree — see DECISIONS.md); (2) a live `py main.py --country=MY` run has NOT yet happened — new Alfonso-owned Groq-quota-gated checkpoint, and the only way to confirm whether MY's cross-sector keyword additions actually surface a reasonable signal count from its non-BER sources; (3) real-browser visual QA of the country-tab styling — code-level correctness verified for both VN's and MY's versions, pixels need eyes.

Last activity: 2026-07-10 — created `integration/vn-my-review`, merged both feature branches, resolved conflicts in `config/sources.json`/`data/company_context.md`/`templates/base.html`/`.context/*`, for Alfonso's combined dashboard review.

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
- **Feature 003 — Vietnam Country Expansion (2026-07-08, PASSED):** Vietnam wired end-to-end — 60 VN sources (43 active), country-aware Flask routing (`_country_mode()`), working country switcher UI, dynamic admin country dropdown, country-scoped feedback/weekly-summary ChromaDB access (previously global/unscoped — real gap closed, not deferred), country-scoped `run_metadata.json`, VN subsection in `company_context.md` + vectorstore reseed, `SUMMARY_PROMPT` no longer hardcodes "Singapore". First real exercise of the `--country` scaffolding against a second country's live data. Not yet merged to `main`.
- **Feature 004 — Malaysia Country Expansion (2026-07-10, PASSED):** MY country block (55 sources, 52 active), sector mapping, dual GENERAL+real-domain tagging, MY-specific keyword lists, `company_context.md` Malaysia subsection (full business breadth, unlike Vietnam's BER/EDU-only one), `COMPANY_CONTEXT` reseed. Touched zero Python files — needed Vietnam's `app.py` routing (merged in on this integration branch) to actually become usable end-to-end. Not yet merged to `main`.

## What's In Progress

Nothing actively in flight. Both Vietnam and Malaysia feature branches are complete and PASSed; this integration branch exists solely for Alfonso's combined dashboard review before a real merge decision.

## Next Action

Alfonso reviews both Vietnam's and Malaysia's reports side by side via this integration branch's dashboard, then decides real merge order/strategy for `feature/003-vietnam-country` and `feature/004-malaysia-country` into `main` (this integration branch itself is not intended to be the thing that merges — it's a review scaffold). After that review and any resulting fixes, the confirmed next step is **full activation of the remaining 5 business domains (RCC, HLS, MFG, CTE, PSS)** as first-class, active pipeline domains alongside the currently-active BER/EDU/GENERAL — this is Alfonso's own explicit instruction, not to be lost or treated as a vague someday-item.

## Known Bugs / Open Items

- **Full 7-domain activation (RCC/HLS/MFG/CTE/PSS) is the confirmed next step, explicitly requested by Alfonso to be tracked and not lost.** Currently only BER/EDU/GENERAL are active, validated pipeline domains (`_domain_mode()`, domain tabs/checkboxes, and — critically — `pipeline/analyst.py`'s `SUMMARY_PROMPT` product catalog and opportunities-gate keywords are all BER/EDU-only). Malaysia's source list (55 sources, only 31% BER-tagged; the rest RCC/PSS/HLS/CTE/MFG) is what surfaced this gap concretely, but it applies **retroactively to Vietnam's sources too** — both country features independently made the same "stay scoped to current active domains" call, deferring full activation as a separate feature since it changes domain routing/UI/the analyst's opportunity-gate keywords for **all** countries (SG included), not just the newly-added one. The underlying product-catalog content for RCC/HLS/MFG/CTE/PSS already exists in `company_context.md` (written during Feature 001, marked reference-only) — the gap is entirely in routing/prompt wiring, not missing content.
- **Malaysia's signals-visible-but-opportunities-gated asymmetry** — MY's broadened filter keywords (18 cross-sector additions) let non-BER sources pass the relevance filter and surface raw signals, but `SUMMARY_PROMPT`'s opportunities gate stays BER/EDU-keyword-only, so most of MY's sources will show signals but rarely generate `opportunities` entries until domain activation lands. Must be visible to Alfonso during dashboard review, not silently absorbed.
- **`pipeline/weekly.py`'s `WEEKLY_PROMPT` hardcodes "Singapore"** — same bug class as the `SUMMARY_PROMPT` fix in Feature 003's Task 006, but out of that feature's declared scope. Data-layer scoping is already correct (a VN weekly run only compresses VN-tagged reports); this is a prompt-content quality bug, not a data-independence bug. Small, well-understood follow-up — mirror Task 006's `str.replace()` pattern.
- **Reconciling this integration branch's `.context/` files back into `feature/003-vietnam-country`, `feature/004-malaysia-country`, and eventually `main`** — this branch's STATE.md/DECISIONS.md/ROADMAP.md were manually reconciled from both branches' independently-diverged updates for review purposes; whoever performs the real merge to `main` should treat this branch's `.context/` as a reference, not assume it's automatically correct post-merge.
- **Live pipeline runs:** Vietnam's `py main.py --country=VN --domain=BER` already ran successfully once (surfaced and fixed two real bugs live — a Windows UTF-8 console crash on Vietnamese diacritics, and a missing `.env` in a fresh worktree). Malaysia's equivalent run has NOT happened yet — new Groq-quota-gated Alfonso-owned checkpoint, also the only way to confirm whether MY's broadened keywords actually surface a reasonable signal count. SG's own `py main.py --domain=BER --country=SG` run from Feature 001 is also still outstanding.
- **Real-browser visual QA** of the country-tab styling in `base.html` — code-level correctness verified for both VN's and MY's versions (and their merged combination on this branch), pixels need eyes. Same open item as `login.html`/`admin.html`/PDF-print from Feature 001.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16`).
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `run_metadata.json` isn't domain-scoped (only country-scoped) — no longer fully harmless now that multiple countries/domains coexist.
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc.
  - `pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset, unlike the graceful-skip pattern in `feedback.py`/`weekly.py`.
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **`ADMIN_PASSWORD` empty-string default** — safe (refuses login when unset) but not functional; Alfonso still needs to set the env var to actually use admin login.
- **Widened opportunities relevance gate is not active** — gate stays keyword-only by design; reinstating the previously-lost "ecosystem entity action" second path remains a separate, deferred decision, now overlapping with the domain-activation next step above.
- **Customers sector historically thin (SG)** — only 1 source passed filter, 0 signals, in at least one past real run.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; untouched by either Feature 003 or Feature 004.
- **VN sources may under-perform the keyword filter** — VN keywords are English-only (no Vietnamese-language matching); not yet empirically checked against a live run.
- **ID country expansion** — still fully unbuilt; VN/MY establish a reusable pattern but don't extend to it.
- **Bookkeeping correction (carried from Feature 001)** — ROADMAP.md previously recorded 54 active SG sources; Feature 001's evidence gate confirmed 62 total / 57 active.
