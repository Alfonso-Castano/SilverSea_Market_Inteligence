# Project State

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## ⚠️ Branch stack note — read before trusting this file

This worktree is `feature/005-domain-activation`, built directly on top of `integration/vn-my-review` (base `b1549d6`) — **not** on `main`. `integration/vn-my-review` itself already merges `feature/003-vietnam-country` and `feature/004-malaysia-country`. So this is a 3-deep unmerged stack: `feature/003` + `feature/004` → `integration/vn-my-review` → `feature/005-domain-activation` (this branch). None of it is in `main` yet. This STATE.md reflects the full combined picture as of this branch's tip — Vietnam, Malaysia, and now full 8-domain activation all together.

## Current Position

**Feature `005-domain-activation` PASSed `/feature-verify`** (`REVIEW.md` at `bcdcfba`, all 6 tasks done, evidence gate green). This is the feature that finally resolves the "confirmed next step" both Feature 003 (Vietnam) and Feature 004 (Malaysia) explicitly flagged and deferred: full activation of the remaining 5 business domains.

What shipped:
- **All 8 business domains are now first-class, active, routable pipeline domains** — BER/EDU/GENERAL (previously active) plus RCC, HLS, MFG, CTE, PSS (newly activated). `app.py`'s `_domain_mode()` validates all 8 with `BER` as the invalid-input fallback. `templates/base.html`'s domain-tabs row expanded from 3 to 8 real links (`flex-wrap` added so they wrap on narrow viewports). `templates/admin.html`'s source-approval checkboxes expanded from 3 to 8 (only `GENERAL` pre-checked, matching the prior default).
- **`pipeline/analyst.py`'s `SUMMARY_PROMPT`** now carries all 7 sector product catalogs (added the 5 new ones, transcribed verbatim from `company_context.md`'s "Products by Business Sector" section — byte-for-byte verified) and a broadened `OPPORTUNITIES:` gate keyword list (10 new cross-sector terms, reused from Malaysia's existing keyword vocabulary rather than inventing a new list).
- **`data/company_context.md`** — the "— reference only, not active this round" caveat removed from the 5 previously-dormant sector headings (MFG/HLS/RCC/CTE/PSS); the product-list text itself was untouched, since it was already correct from Feature 001.
- **Vietnam's sources retagged with real business domains** — 30 of VN's 60 sources (mirroring Malaysia's existing dual-tag pattern) got a genuine non-BER domain added alongside `GENERAL`, derived entirely from each source's own existing description in the original VN source list (no new research). 1 additional source (Đa Minh Education) got a name-based `EDU` dual-tag. 6 sources' real domain happened to already equal `BER` (verified explicit no-ops). The remaining sources (3 pre-existing EDU dual-tags, 7 blank no-URL stubs, everything else) were left untouched. VN's total source count stays 60; no source's name/url/sector/type/active/fetcher fields changed, only `domain` arrays.
- **Malaysia's and Singapore's `sources.json` blocks needed zero changes** — Malaysia was already correctly domain-tagged from Feature 004; Singapore has no non-BER sources to retag. Both independently confirmed byte-identical to their pre-feature state via a full structural diff (not just `git diff --stat`) in the reviewer's evidence gate.

**New, explicitly-flagged-by-Alfonso open item, not yet scoped as a feature:** an accuracy and value review of the reports already generated for Vietnam and Malaysia is needed. In Alfonso's own words: accuracy is checkable, but "value" (how useful a given piece of information is to the company for a specific country) is inherently subjective, and he expects it will be genuinely hard to automate or score cleanly. See Next Action and Known Bugs below — this is now the item at risk of being lost the way domain-activation almost was, so it's logged with the same prominence.

**One process note, not a defect:** `admin.html`'s domain checkboxes are nested inside a pre-existing `{% if pending %}` block (present before this feature too) — they don't render when `data/pending_sources/` is empty. Anyone visually verifying the admin page's new checkboxes needs a seeded pending-source fixture first, or they'll get a false negative.

Last activity: 2026-07-10 — `/feature-verify` PASS for `005-domain-activation` (commits `bb6fbd3`..`c9f6464` on `feature/005-domain-activation`, plus `bcdcfba` REVIEW.md). Branch not yet merged anywhere — sits on `integration/vn-my-review`, which itself sits on `feature/003-vietnam-country` + `feature/004-malaysia-country`, none merged to `main`.

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
- **Feature 005 — Full Domain Activation (2026-07-10, PASSED):** All 8 business domains (BER/EDU/GENERAL + RCC/HLS/MFG/CTE/PSS) now first-class, routable, analyzed pipeline domains — `_domain_mode()`, `base.html`/`admin.html` UI, `SUMMARY_PROMPT` product catalogs + broadened opportunities gate, `company_context.md` caveat removal. Vietnam's sources retroactively retagged with real business domains (30 sources, mirroring Malaysia's pattern). Malaysia and Singapore needed zero source changes. Resolves the next-step item both Feature 003 and Feature 004 flagged. Not yet merged to `main`.

## What's In Progress

Nothing actively in flight. Feature 005 is complete and PASSed. `feature/005-domain-activation` sits atop a 3-deep unmerged stack (`feature/003-vietnam-country` + `feature/004-malaysia-country` → `integration/vn-my-review` → `feature/005-domain-activation`) — none merged to `main`.

## Next Action

Two things are now open, roughly equal priority — pick based on what Alfonso wants to look at first:

1. **Decide real merge order/strategy** for the 3-deep branch stack into `main` (`feature/003` + `feature/004` → `integration/vn-my-review` → `feature/005-domain-activation`). This has been an open decision since the integration branch was created and is now more pressing since Feature 005 built directly on top of it, making `integration/vn-my-review` load-bearing rather than a throwaway review scaffold.
2. **Accuracy and value review of Vietnam's and Malaysia's already-generated live reports** — explicitly requested by Alfonso, not yet scoped as a feature. His own framing: accuracy is checkable, but "value" (how useful a piece of information is to the company for a specific country) is inherently subjective and will likely be hard to automate or score cleanly. Needs a `/feature-discuss` to even figure out what "done" looks like here, given the subjectivity.

Separately, whenever Groq's daily quota is fresh, a live `py main.py --country=VN` and/or `--country=MY` run (any domain) would confirm whether the broadened opportunities gate from Feature 005 actually surfaces new non-BER/EDU opportunities — quota-gated, Alfonso-owned, not blocking either item above.

## Known Bugs / Open Items

- **RESOLVED (2026-07-10, Feature 005): Full 7-domain activation.** Previously the most prominently-tracked open item across Features 003 and 004 — now done. All 8 domains (BER/EDU/GENERAL/RCC/HLS/MFG/CTE/PSS) are active, routable, and analyzed. Do not reopen this as a pending item in future sessions.
- **NEW, prominently flagged (2026-07-10, from Feature 005's Open Questions, explicitly requested by Alfonso): accuracy and value review of Vietnam's and Malaysia's already-generated live reports.** Not yet scoped as a feature. Alfonso's own framing: accuracy is checkable, but "value" (how useful a piece of information is to the company for a specific country) is inherently subjective and expected to be genuinely hard to automate or score cleanly. This is the next item at risk of being lost across sessions — treat with the same "do not lose this" weight the domain-activation item got in the two prior features' context updates.
- **SG's own domain coverage for RCC/HLS/MFG/CTE/PSS remains fully unstarted** — no real SG sources tagged for these 5 verticals; SG will show empty results under those domain tabs until/unless real SG sources are added. Separate, unaddressed question from the VN retag — not part of Feature 005's scope.
- **3-deep unmerged branch stack** — `feature/003-vietnam-country` + `feature/004-malaysia-country` → `integration/vn-my-review` → `feature/005-domain-activation`, none merged to `main`. `integration/vn-my-review` is no longer a throwaway review scaffold — Feature 005 built directly on it, so it's now load-bearing for any real merge to `main`.
- **`admin.html`'s domain checkboxes only render when `data/pending_sources/` is non-empty** — pre-existing `{% if pending %}` wrapper, predates Feature 005, not a defect it introduced. Anyone visually verifying the 8 new checkboxes needs a seeded pending-source fixture first (the reviewer used a temporary one and removed it after).
- **Live pipeline runs, all still open, all Groq-quota-gated, all Alfonso-owned:** (1) VN's `py main.py --country=VN --domain=BER` already ran successfully once (Feature 003 review); (2) MY's equivalent run has NOT happened yet; (3) **new from Feature 005** — a fresh VN/MY run under the broadened opportunities gate would confirm whether non-BER/EDU signals now actually generate `opportunities` entries, not just pass the relevance filter; (4) SG's own `py main.py --domain=BER --country=SG` run from Feature 001 is also still outstanding.
- **Malaysia's signals-visible-but-opportunities-gated asymmetry — now substantially narrowed by Feature 005**, but not fully confirmed without a live run (see above). Prior to Feature 005, MY's non-BER sources could pass the relevance filter but rarely generated `opportunities` entries since the gate was BER/EDU-keyword-only; the gate is now broadened, but whether it actually produces opportunities for those sectors in practice is unverified without a live run.
- **`pipeline/weekly.py`'s `WEEKLY_PROMPT` hardcodes "Singapore"** — same bug class as the `SUMMARY_PROMPT` fix in Feature 003's Task 006, still out of scope for every feature since. Data-layer scoping is already correct; this is a prompt-content quality bug only. Small, well-understood follow-up.
- **Real-browser visual QA** of the domain-tab and country-tab styling in `base.html` — code-level correctness verified (including the new 8-tab `flex-wrap` layout), pixels need eyes. Same open item as `login.html`/`admin.html`/PDF-print from Feature 001.
- **Deferred — Future Pipeline-Polish Round** (surfaced by Feature 001's recon pass, not yet a scheduled feature):
  - No LLM rate limiter exists, despite a 2026-06-19 decision recording one.
  - `sentence-transformers` is a **direct, explicit** dependency (`pipeline/vectorstore.py:14-16`).
  - Email digest likely renders blank — `main.py`'s `send_digest(email_text, "", ...)` puts an empty HTML part last in a `multipart/alternative` message.
  - `run_metadata.json` isn't domain-scoped (only country-scoped).
  - `weekly.py`'s ChromaDB retrieval (`collection.get(limit=...)`) is order-unstable with no guard against re-compressing an already-summarized doc.
  - `pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset, unlike the graceful-skip pattern in `feedback.py`/`weekly.py`.
  - Dead file: `scripts/feedback_server.py` still on disk despite its 2026-06-23 consolidation into `app.py`.
- **`ADMIN_PASSWORD` empty-string default** — safe (refuses login when unset) but not functional; Alfonso still needs to set the env var to actually use admin login.
- **Customers sector historically thin (SG)** — only 1 source passed filter, 0 signals, in at least one past real run.
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist.
- **`config/sources.json`'s `_domain_tagging_status` draft flag** — still unreviewed by Alfonso; untouched by Features 003, 004, or 005.
- **VN sources may under-perform the keyword filter** — VN keywords are English-only (no Vietnamese-language matching); not yet empirically checked against a live run.
- **ID country expansion** — still fully unbuilt; VN/MY establish a reusable pattern but don't extend to it.
- **Bookkeeping correction (carried from Feature 001)** — ROADMAP.md previously recorded 54 active SG sources; Feature 001's evidence gate confirmed 62 total / 57 active.
