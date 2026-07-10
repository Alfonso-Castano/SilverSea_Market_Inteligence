# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## ⚠️ Branch-local note — read before trusting this file

This STATE.md reflects **only** the git history of `feature/004-malaysia-country` (cut from `main` at `168810e`). A sibling branch, `feature/003-vietnam-country` (also cut from `168810e`, also PASSed `/feature-verify`), has its own independent `.context/` updates in its own worktree (`C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence-vietnam`) that do **not** appear here, because neither branch has merged to `main` yet. Do not treat this file as reflecting Vietnam's completion — it doesn't, by construction of the parallel-worktree pattern used this round. **Reconciling STATE.md/DECISIONS.md/ROADMAP.md content across both branches is an outstanding manual step for whoever merges second** — see Known Bugs / Open Items below.

## Current Position

Feature `004-malaysia-country` (branch `feature/004-malaysia-country`, this worktree) passed `/feature-verify` — all 4 tasks done, evidence gate green, `REVIEW.md` committed at `36d2530`. This feature added Malaysia (`MY`) as a third country in `config/sources.json`: 55 sources (the submission's header claimed 61; rows 56-61 were blank) mapped 1:1 onto the existing 6-sector taxonomy (`customers` 26, `partners` 10, `competitors` 8, `gov_agencies` 7, `associations` 3, `general_news` 1 — the first source list to populate `associations` with real non-SG entries), verified live: 52/55 active after scraper dry-run (50 default fetcher, 2 stealth — Air Selangor, Panasonic Appliances Marketing Asia Pacific; 3 inactive — U Learning, Art Network Events, Unbound Malaysia — all JS-SPA shells with no real content reachable behind any fetcher tier). Every MY source is tagged with both `"GENERAL"` and its real submitted business domain (`BER` 17, `PSS` 13, `RCC` 13, `HLS` 4, `CTE` 3, `EDU` 3, `MFG` 2) for forward-compatibility, even though only BER/EDU/GENERAL are active pipeline domains this round. MY got its own keyword lists: `priority_keywords` (15, byte-identical to SG's) and `keywords` (99 = SG's 81 verbatim + 18 new cross-sector terms drawn from the submission's Description column, needed because only 31% of MY's sources are BER-tagged). `data/company_context.md` gained a Malaysia subsection under Key Prospects/Ecosystem Players covering the *full* real business breadth (RCC/HLS/MFG/CTE/PSS entities like Ricoh, Avisena, Perodua, Ezytap, Think City — not just BER/EDU, unlike Vietnam's narrower subsection), and `COMPANY_CONTEXT` was re-seeded and live-verified (46 chunks, all new entities present). `templates/base.html`'s country tabs were fixed to show SG/MY/VN as real links, Indonesia still inert — this branch had to independently reproduce Vietnam's own base.html fix from scratch, since MY's branch was cut from a pre-VN-fix `main` and the two branches are still unmerged siblings.

**This feature is unusual: it touched zero Python files.** `app.py`, `main.py`, `templates/admin.html`, `pipeline/feedback.py`, `pipeline/weekly.py`, `pipeline/analyst.py`, and `_domain_mode()` are all confirmed untouched (empty diffs verified individually) — the entire feature is JSON/Markdown/HTML data. Consequence: **Malaysia's dashboard is not yet actually usable end-to-end on this branch alone.** `app.py`'s `report()` route never reads `?country=` here (that wiring is Vietnam's own `app.py` change, which doesn't exist on this branch) — `current_country` always defaults to `'SG'`, so clicking the MY tab today still displays Singapore's report. This resolves automatically once this branch merges with Vietnam's `app.py` routing work.

Two unmerged sibling feature branches now exist off the same base (`168810e`): `feature/003-vietnam-country` (PASSed, own STATE.md lives only on that branch) and `feature/004-malaysia-country` (PASSed, this update). **Neither is merged to `main` yet.**

Last activity: 2026-07-10 — `/feature-verify` PASS for `004-malaysia-country` (commits `89ce900`..`4012532` on `feature/004-malaysia-country`, plus `36d2530` REVIEW.md). Branch not yet merged to `main`.

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
- **Feature 004 — Malaysia Country Expansion (2026-07-10, `feature/004-malaysia-country`, PASSED, this branch):** MY country block (55 sources, 52 active), sector mapping, dual GENERAL+real-domain tagging, MY-specific keyword lists, `company_context.md` Malaysia subsection (full business breadth), `COMPANY_CONTEXT` reseed, base.html SG/MY/VN tab links (independently reproducing Vietnam's fix). Branch not yet merged to `main`. Note: `feature/003-vietnam-country` also PASSed independently on its own sibling branch/worktree — not detailed here since its history isn't on this branch; see that branch's own STATE.md.

## What's In Progress

Nothing actively in flight on this branch. `004-malaysia-country` is complete and PASSed but not yet merged to `main`, and not yet reconciled with the sibling `feature/003-vietnam-country` branch.

## Next Action

Alfonso to review both the Malaysia and Vietnam dashboards (once merged, or via each branch's own worktree) and decide on merge order/conflict resolution — `templates/base.html`'s country-tabs block will produce a small, easily-resolved textual merge conflict between the two branches (both converge on the same final content: SG/MY/VN as links, ID inert). After that dashboard review and any resulting fixes, the confirmed next step is **full activation of the remaining 5 business domains (RCC, HLS, MFG, CTE, PSS)** as first-class, active pipeline domains alongside the currently-active BER/EDU/GENERAL — see Known Bugs / Open Items below; this is Alfonso's own explicit instruction, not to be lost or treated as a vague someday-item.

## Known Bugs / Open Items

- **Full 7-domain activation (RCC/HLS/MFG/CTE/PSS) is the confirmed next step, explicitly requested by Alfonso to be tracked and not lost.** Currently only BER/EDU/GENERAL are active, validated pipeline domains (`_domain_mode()`, domain tabs/checkboxes, and — critically — `pipeline/analyst.py`'s `SUMMARY_PROMPT` product catalog and opportunities-gate keywords are all BER/EDU-only). Malaysia's source list (55 sources, only 31% BER-tagged; the rest RCC/PSS/HLS/CTE/MFG) is what surfaced this gap concretely, but it applies **retroactively to Vietnam's sources too** — both country features independently made the same "stay scoped to current active domains" call, deferring full activation as a separate feature since it changes domain routing/UI/the analyst's opportunity-gate keywords for **all** countries (SG included), not just the newly-added one. The underlying product-catalog content for RCC/HLS/MFG/CTE/PSS already exists in `company_context.md` (written during Feature 001, marked reference-only) — the gap is entirely in routing/prompt wiring, not missing content.
- **Malaysia's signals-visible-but-opportunities-gated asymmetry** — MY's broadened filter keywords (18 cross-sector additions) let non-BER sources pass the relevance filter and surface raw signals, but `SUMMARY_PROMPT`'s opportunities gate stays BER/EDU-keyword-only, so most of MY's sources will show signals but rarely generate `opportunities` entries until domain activation lands. Must be visible to Alfonso during dashboard review, not silently absorbed.
- **Reconciling STATE.md/DECISIONS.md/ROADMAP.md across `feature/003-vietnam-country` and `feature/004-malaysia-country`** — both branches independently ran their own `/update-context` pass off the same base (`168810e`), so their `.context/` files have diverged and don't know about each other. This is a manual step for whoever merges second (or for Alfonso directly): fold the other branch's STATE.md narrative and DECISIONS.md entries in rather than letting one silently overwrite the other. Not attempted in this pass — explicitly out of scope per this update's instructions.
- **Malaysia's dashboard is not yet end-to-end usable on this branch alone** — `app.py` doesn't read `?country=` here (that's Vietnam's own `app.py` change), so `current_country` defaults to `'SG'` regardless of which country tab is clicked. Resolves once this branch merges with Vietnam's routing work.
- **New manual checkpoint (Alfonso-owned, Groq quota-gated):** a fresh `py main.py --country=MY --domain=BER` (or `--domain=GENERAL`) run — first real end-to-end exercise of the Malaysia pipeline, alongside the existing open SG and VN checkpoints below. Also the only way to confirm whether MY's cross-sector keyword additions actually surface a reasonable signal count from its non-BER sources.
- **Two manual checkpoints from Feature 001, still open:** (1) fresh `py main.py --domain=BER --country=SG` run — quota-gated; (2) visual QA of `login.html`/`admin.html` styling and real-browser PDF print-preview — code-level structure was checked, pixels need eyes.
- **Vietnam's own manual checkpoints** (live pipeline run, country-tab visual QA) — tracked on `feature/003-vietnam-country`'s own STATE.md, not duplicated here; Malaysia's base.html changes are visually identical in structure to Vietnam's, so this is the same carry-forward item, not a new one.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, explicitly out of scope there, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one — likely lost during the dead-code removal pass or never actually built.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16` instantiates `SentenceTransformerEmbeddingFunction` directly).
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `run_metadata.json` isn't domain/country-scoped — only the last country's metadata survives a multi-country run. No longer harmless-by-default now that MY/VN both exist alongside SG.
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc — related to the country-scoping gap below.
  - `pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset, unlike the graceful-skip pattern in `feedback.py`/`weekly.py`.
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **Feedback digest and weekly-summary country-scoping** — both still global/unscoped; explicitly re-deferred in Feature 001 (out of scope). Open question for Alfonso, now more pressing with 3 countries in play.
- **`ADMIN_PASSWORD` empty-string default** — the bypass fix makes this *safe* (refuses login when unset) but not *functional*; Alfonso still needs to set the env var to actually use admin login.
- **Widened opportunities relevance gate is not active** — Feature 001 confirmed the gate stays keyword-only by design (EDU terms added alongside BER terms); reinstating the previously-lost "ecosystem entity action" second path remains a separate, deferred decision, now overlapping with the domain-activation next step above.
- **Customers sector historically thin (SG)** — only 1 source passed filter, 0 signals, in at least one past real run. Worth re-checking after the full source expansion.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; Feature 001's admin country-selector change and Feature 004's MY block both touched this file but neither resolved this flag.
- **Bookkeeping correction (carried from Feature 001)** — ROADMAP.md previously recorded 54 active SG sources; Feature 001's evidence gate confirmed 62 total / 57 active.
