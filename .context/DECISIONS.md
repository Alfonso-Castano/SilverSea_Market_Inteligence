# Decisions Log

Running record of decisions that constrain future work. Newest first. Check here before re-deciding something already settled. Migrated verbatim from the project's original `CONTEXT.md` (2026-06 through 2026-07-02) on 2026-07-08 — every entry below existed in that file; none were invented during migration. Any future session or `/feature-*` run should append new entries above this note, newest-first.

---

## [2026-07-13] — Feature 006 (VN/MY Accuracy & Code-Correctness Review): findings locked, three mechanical fixes applied

**Decision:** The review was executed as planned — nine tasks across four waves, deliberately with no live `py main.py` run and no Groq/LLM calls anywhere in the feature. Accuracy audits (VN, MY) compared already-generated report JSON against live-refetched source pages (`refetched/vn_sources.json`, `refetched/my_sources.json`) plus `config/sources.json`; code-correctness reviews inspected data-flow and gate logic directly. Model tiers were pinned per Alfonso's 2026-07-10 directive: accuracy audits on Sonnet 5 (`mid` tier), code reviews on Opus 4.8 (`quality` tier), refetch/mechanical-fix tasks on Haiku, all orchestrated by an Opus 4.8 main session.
**Rationale:** Matches the sequencing decision locked before this feature started (see the entry below) — the point was to catch hallucination/wiring defects in already-shipped work without spending Groq quota or risking a live run re-confirming a bug that could be found by inspection alone.

**Decision — headline finding, left flagged, not fixed:** `source_name` attribution is broken across VN and MY reports. VN: 42 of 43 signals and all 3 opportunities carry the literal placeholder string `"Extracted signals"`/`"extracted signals"` as `source_name`, not a real, joinable source name — only 1 signal (General News, "Vietnam Investment Review") is correctly attributed. MY is milder: 5 of 9 signals plus all opportunities affected, with some further variants (`"source not specified"`, `"source text"`, `"Balai Seni Negara"` — a real but non-matching label). Root cause, confirmed at the code level: `pipeline/analyst.py:174`'s `_synthesize_sector()` builds its synthesis-phase user message as `f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"` with no enforced per-source delimiter inside `extraction_text` — the model latches onto the literal label `"Extracted signals"` itself and emits it back as `source_name`, rather than any of the real source names embedded further down in the extraction text. **Critically, this bug is git-dated to 2026-06-29 (commits `ebd90f6`/`59e4f52`) — it predates Features 003, 004, and 005 entirely.** It is a testing-coverage gap, not a regression introduced by this session's rapid feature dispatches: three separate `/feature-verify` passes (Features 003, 004, 005) each returned PASS on this exact code path, because each verified code-matches-spec and evidence-gate conformance, not report-content fidelity against real source data — a gap this feature was specifically created to close, and did. Left flagged rather than fixed, since the fix requires prompt-engineering judgment (e.g. forcing extraction output into a rigid `### {source_name}` structure per source, not a one-line patch), which is out of scope for a review-only feature.
**Rationale:** Fixing this correctly requires redesigning `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT`'s structure, which risks the same kind of signal-count regression the 2026-06-29 per-sector-synthesis rewrite was originally built to avoid (see that entry further down this log) — not something to attempt inside a review feature whose explicit constraint was "surface findings, don't silently fix while reviewing."

**Decision — other findings, all left flagged, not fixed:** (1) Fabricated Silversea product names appear in several opportunities' `product_fit` fields in both VN and MY reports — e.g. "Building Automation", "Smart Building" (BER), "E-learning solutions" (EDU) — none of which exist in `data/company_context.md`'s real product catalog; a consistent weak spot, distinct from the `source_name` bug. (2) One confirmed instance of cross-source content contamination: a VN Becamex IDC competitor signal contains a sentence ("digital solutions for businesses, including data storage centers and virtual servers") that is a near-verbatim match to a *different* cited source in the same report, Viettel Group's homepage — the 260 MWp solar-farm claim in the same signal is independently confirmed accurate, so this is a partial contamination within one signal, not a wholesale fabrication. (3) `pipeline/filter.py`'s relevance gate (per-country config keywords) and `SUMMARY_PROMPT`'s opportunities gate (one hardcoded global keyword list) diverge — aligned for MY, looser than `filter.py` for VN, where 4 BER+EDU dual-tagged sources (corrects RESEARCH.md's earlier estimate of 2) create an EDU→BER leak path into opportunities. (4) `_build_rag_context()` is confirmed dead code (never called anywhere in the pipeline); separately, `REPORT_HISTORY` vectorstore writes are country-scoped but not domain-scoped — a dormant cross-domain contamination trap that would only manifest if RAG context retrieval is ever restored. (5) `analyse()` still receives no explicit `domain` parameter, meaning every `product_fit` judgment reasons across all 7 sector product catalogs simultaneously regardless of which domain a given report is actually for — flagged as an architecturally non-trivial lead, not attempted.
**Rationale:** All five are genuine defects or design gaps worth fixing, but each requires either prompt-engineering judgment, a scope decision (e.g. whether/how to thread `domain` through `analyse()`), or is a one-off content-quality issue not amenable to a mechanical patch — consistent with this feature's explicit constraint against silently fixing anything found during a review pass.

**Decision:** Three low-risk, purely mechanical fixes were applied on Alfonso's explicit approval, each its own independently-revertible commit: `app.py`'s `report()` route's domain-fallback tuple widened from 3 to all 8 domains to match `_domain_mode()` (`14adeb3`) — fixes a latent bug, currently masked for VN/MY since neither yet has a report in the previously-missing 5 domains, where a country whose only report exists under e.g. RCC would wrongly fall back to the legacy undifferentiated `latest_report.json`; `pipeline/analyst.py`'s `analyse()` switched from `os.environ["GROQ_API_KEY"]` to `os.environ.get("GROQ_API_KEY", "")` (`106ca9b`), resolving a previously-tracked known-bug (crash on unset key) by matching the graceful-degradation pattern `feedback.py`/`weekly.py` already used; `pipeline/weekly.py`'s `WEEKLY_PROMPT` now threads real `country_name` instead of hardcoding `"Singapore"` for every country, with `main.py`'s call site updated to pass `country["name"]` (`0a3f907`), resolving the second previously-tracked known-bug of this exact class.
**Rationale:** All three are mechanical, single-purpose, low-risk, and each independently resolves a defect this project's own `.context/` files had already been tracking as an open item for one or more prior features — a rare case where a review-only feature's optional-fix allowance was worth using rather than purely flagging.

**Decision:** Git-history sampling of the 24 rapid-dispatch commits across Features 003 (Vietnam), 004 (Malaysia), and 005 (domain activation) turned up only Low/Informational findings — keyword-list message drift, VN reusing SG's keyword list inconsistently (e.g. MY's own `GeBIZ` mention in its priority-keywords list is a leftover SG artifact), cosmetic JSON key-order differences. No new correctness bug was introduced by the session's rapid subagent dispatches themselves; the headline `source_name` finding predates all three features.
**Rationale:** This distinction matters for how future sessions read this review — it validates that the rapid-dispatch subagent workflow used for Features 003-005 did not itself introduce defects, and redirects attention toward the actual root cause (a 2026-06-29 prompt-structure bug) rather than toward the dispatch process.

---

## [2026-07-10] — Pre-review sequencing: two-part VN/MY review scoped as its own feature before any live pipeline run or dashboard polish

**Decision:** Before running a fresh live pipeline for Vietnam or Malaysia, and before finalizing either country's dashboard pages further, a thorough two-part review of everything built across Features 003 (Vietnam), 004 (Malaysia), and 005 (domain activation) will happen first, scoped as its own feature (likely numbered `006`). Part 1, knowledge/accuracy: does the analyst's LLM-generated report content actually reflect real information from the scraped sources, with no hallucinated facts, connections, or figures — i.e. do `pipeline/analyst.py`'s grounding rules (closed-book framing, quote-before-extract, abstain tokens) actually hold up in practice, not just on paper. Part 2, code-correctness: does the codebase actually wire source data through to report output correctly — domain filtering, sector mapping, keyword relevance gating, RAG retrieval, the Vietnam domain retag from Feature 005, and the `SUMMARY_PROMPT` catalog/gate expansion from Feature 005.
**Rationale:** A large amount of surface area (three features) was built quickly via subagent execution this session, on top of each other, without a live pipeline run to exercise most of it end-to-end. Alfonso wants to catch hallucinations or wiring bugs now, before investing further effort in dashboard polish or burning Groq quota on a live run that might just be re-confirming pre-existing bugs.

**Decision:** This review will be run as its own feature in a fresh chat/session, using the standard `/feature-discuss` → `/feature-plan` sequence — explicitly **not** the `/feature-quick` fast path, despite Alfonso initially describing it in terms that sounded like a quick-path request. Given the review's stated thoroughness and genuinely two-part scope (accuracy *and* code-correctness, spanning three prior features), the full discuss→plan sequence was judged the better fit; Alfonso was informed of this distinction and agreed. Discussion and planning will run on a Sonnet 5 agent; execution will run on a separate Opus 4.8 agent.
**Rationale:** This mirrors the project's existing tier-based subagent dispatch pattern (see CLAUDE.md's Subagent Strategy section) but applies it to the discuss/plan-vs-execute split of an entire feature, not just individual tasks within one feature — a genuinely new application of the pattern, recorded here since it's a process decision that will shape how Feature 006 gets dispatched.

**Decision:** A live pipeline re-run for VN and/or MY (to observe the Feature 005 broadened opportunities gate in action) and any further VN/MY dashboard polish both remain explicitly deferred until after this review completes.
**Rationale:** Direct consequence of the above — no point spending Groq's daily quota or polish effort on output that this review might reveal to be wrong or wired incorrectly.

**Decision:** The original ground-truth source documents behind Features 003 and 004 were located and archived into `docs/`: `Silversea_Vietnam_Market_07072026.pdf`, `Source_submission_Malaysia_Sources.pdf`, and `Source_submission_Malaysia.xlsx` (commit `851853b`).
**Rationale:** These are the ground-truth documents the upcoming accuracy review needs to check report content against, alongside `config/sources.json`'s data (which was derived from them in Features 003/004). Archiving them now, ahead of the review, means Feature 006 doesn't need a separate step to go find them.

---

## [2026-07-10] — Feature 005 (Full Business-Domain Activation): all 8 domains wired, Vietnam retagged

**Decision:** All 5 remaining business domains (RCC, HLS, MFG, CTE, PSS) activated as first-class, routable, analyzed pipeline domains alongside the already-active BER/EDU/GENERAL — `app.py`'s `_domain_mode()` now validates 8 codes (invalid input still falls back to `BER`); `templates/base.html`'s domain-tabs row expanded from 3 to 8 real links with `flex-wrap` added so they wrap on narrow viewports instead of overflowing; `templates/admin.html`'s source-approval checkboxes expanded from 3 to 8, matching the same set, only `GENERAL` pre-checked.
**Rationale:** This is the confirmed next step both Feature 003 (Vietnam) and Feature 004 (Malaysia) independently deferred and explicitly asked to be tracked — see the 2026-07-10 Feature 004 entry below. The underlying product-catalog content for all 5 domains already existed in `company_context.md` (written during Feature 001, marked reference-only); the actual gap was entirely routing/prompt wiring, not missing content.

**Decision:** `pipeline/analyst.py`'s `SUMMARY_PROMPT` extended with the 5 new sector product catalogs, transcribed verbatim (byte-for-byte verified in review) from `company_context.md`'s "Products by Business Sector" section — no new product-name invention. The `OPPORTUNITIES:` gate keyword list broadened with 10 cross-sector terms, reused directly from the cross-sector vocabulary Malaysia's `keywords` list already established (Feature 004, Task 001) rather than inventing a second, slightly-different term list. Edited via the same `str.replace()`-safe pattern established in Feature 003's Task 006 (never `.format()` on the full prompt string, since it contains a literal JSON schema block with curly braces later in the same string).
**Rationale:** Keeps cross-sector vocabulary consistent across the codebase and avoids re-deriving product names from scratch when an already-accurate source (`company_context.md`) exists.

**Decision:** `data/company_context.md`'s 5 previously-dormant sector headings (MFG/HLS/RCC/CTE/PSS) had their "— reference only, not active this round" caveat suffix removed. No other change to that section — the product-list text itself was already correct and untouched.
**Rationale:** Mechanical follow-through now that the domains are genuinely active — the caveat existed specifically to flag that the content wasn't wired up yet, and it now is.

**Decision — Vietnam retagging pulled into this feature's scope, reversing Claude's own initial recommendation to defer it (explicit user decision):** 30 of Vietnam's 60 sources retagged with a real, genuine business domain (RCC/HLS/MFG/CTE/PSS) dual-tagged alongside `GENERAL`, mirroring Malaysia's existing pattern — plus 1 more (Đa Minh Education) getting a name-based `EDU` dual-tag as a deliberately low-confidence but justifiable exception, plus 6 sources confirmed as explicit no-ops (their real domain already equalled `BER`). Every assignment was derived solely from each source's own existing description in the original VN source list (already used once for Feature 003's Task 001 sector mapping) — no new research, no re-reading external sources. The 7 fully-blank no-URL/no-description stub sources kept their default `["GENERAL", "BER"]` tag rather than receiving an invented domain.
**Rationale (Alfonso's own framing):** Alfonso wants the full source lists genuinely usable now, not just stored, and accepted the extra scope even though it's closer to research than Malaysia's mechanical case — Malaysia's source list came with an explicit business-domain column from the submitter; Vietnam's did not. The "reuse existing descriptions only, no new research" constraint kept effort proportional and avoided fabricating domain assignments with no textual basis.

**Decision:** This feature branches directly from `integration/vn-my-review` (`b1549d6`), not from `main` — a deliberate change from an earlier "branch off main" plan, forced by the Vietnam-retagging scope decision above, since VN's `sources.json` (which this feature must modify) only exists merged with Malaysia's on that integration branch.
**Rationale:** Direct consequence: `integration/vn-my-review` is no longer just a throwaway review scaffold for Alfonso's side-by-side dashboard comparison — it's now the real, load-bearing path toward eventually merging Vietnam + Malaysia + this feature into `main` together. Whoever handles the eventual merge to `main` needs to treat the 3-deep stack (`feature/003` + `feature/004` → `integration/vn-my-review` → `feature/005-domain-activation`) as one unit, not three independent branches.

**Decision — explicitly logged, not attempted this feature, prominently flagged by Alfonso to survive into `.context/STATE.md`:** an accuracy and value review of Vietnam's and Malaysia's already-generated live reports is needed. Alfonso's own framing: accuracy is checkable, but "value" (how useful a given piece of information is to the company for a specific country) is inherently subjective and he expects it will be genuinely hard to automate or score cleanly.
**Rationale:** Not yet scoped as a feature — there's no clear definition of "done" yet given the acknowledged subjectivity of the "value" half. Logged now, with the same prominence the domain-activation item got in Features 003/004, specifically so it isn't lost the way that item almost was before Feature 004 called it out explicitly.

---

## [2026-07-10] — Feature 004 (Malaysia Country Expansion): scope locked, full domain activation explicitly deferred

**Decision:** Malaysia (`MY`) added as a third country in `config/sources.json` — 55 sources (the submission header claimed 61; rows 56-61 were blank), mapped 1:1 onto the existing 6-sector taxonomy with no ambiguity (`Customer`→`customers` 26, `Partner`→`partners` 10, `Government`→`gov_agencies` 7, `Association`→`associations` 3, `Competitor`→`competitors` 8, `General News`→`general_news` 1). MY got its own `priority_keywords` (15, byte-identical to SG's) and `keywords` (99 = SG's 81 verbatim + 18 new cross-sector terms).
**Rationale:** Only 31% of MY's source list is BER-tagged (the rest spans RCC/PSS/HLS/CTE/MFG); reusing SG's pure-BER keyword list as-is would have filtered out the majority of MY's real, submitted sources at the relevance-filter stage even though they're domain-tagged and meant to be reachable. This is the first source list to populate the `associations` sector with real non-SG entries (GreenRE, REDHA Institute, Malaysia Retail Chain Association).

**Decision:** Every MY source is tagged with both `"GENERAL"` and its real submitted business domain (`BER`/`RCC`/`HLS`/`MFG`/`CTE`/`PSS`/`EDU`) in its `domain` array, rather than being restricted to just BER/EDU/GENERAL tags. `data/company_context.md`'s new Malaysia subsection likewise covers the full real business breadth, not just BER/EDU.
**Rationale:** Since `main.py`'s domain filter checks `domain_arg in source["domain"]`, dual-tagging with `GENERAL` makes every source reachable today via `--domain=GENERAL` regardless of its real domain, while the real tag sits ready for a future domain-activation feature to pick up with zero data migration needed. Preserves the full submitted source list without inventing scope that isn't active yet.

**Decision — the one genuinely blocking call this round, made explicitly by Alfonso:** Malaysia (and, retroactively, Vietnam) stays scoped to the currently-active BER/EDU/GENERAL pipeline domains this round. Full activation of RCC/HLS/MFG/CTE/PSS as first-class, validated pipeline domains (`_domain_mode()`'s validated set, dedicated domain tabs/checkboxes, and — most importantly — `pipeline/analyst.py`'s `SUMMARY_PROMPT` product catalog and opportunities-gate keywords) was explicitly **not** done in this feature.
**Rationale (Alfonso's own framing, to be preserved verbatim in intent):** Full 7-domain activation is materially bigger than "add a country" — it changes domain routing/UI/prompt behavior for **all** countries (SG and Vietnam included), not just Malaysia, since `domain` is orthogonal to `country`. Malaysia's source list (only 31% BER-tagged) is simply what surfaced the gap concretely; it isn't a Malaysia-specific problem. Alfonso explicitly asked that this be tracked clearly and not lost — it is the confirmed next step after his dashboard review of both the Vietnam and Malaysia country expansions and any resulting fixes, not a vague someday-item. The underlying product-catalog content for all 5 remaining domains already exists in `company_context.md` (written during Feature 001, marked reference-only) — the actual gap is entirely in routing/prompt wiring. **This decision applies retroactively to Vietnam's sources too** — Vietnam's own feature (`003-vietnam-country`) independently made the identical "stay scoped to current active domains" call in its own, earlier, separate scope discussion; both country features converged on the same boundary without coordinating.

**Decision:** This feature branches from `main` at `168810e`, independently of the still-unmerged `feature/003-vietnam-country` (cut from the same base). Task 003 (`templates/base.html` country tabs) independently reproduces Vietnam's own not-yet-merged tab-link fix (SG/MY/VN as real links, Indonesia inert) from scratch on this branch, rather than only adding a Malaysia tab onto the old inert-span state.
**Rationale:** Since MY's branch was cut before Vietnam's fix landed on its own branch, and the two branches won't see each other's commits until one merges to `main`, MY's branch needed to be internally correct on its own. Both branches converge on the same final `base.html` content, so the eventual merge conflict between them is expected to be small and mechanically trivial to resolve, not a real design conflict.

**Decision:** This feature touched zero Python files — `app.py`, `main.py`, `templates/admin.html`, `pipeline/feedback.py`, `pipeline/weekly.py`, and `pipeline/analyst.py` are all confirmed untouched (verified via empty per-file diffs against base, not just claimed).
**Rationale:** All of this was already made country-agnostic by the Vietnam feature's own earlier work, and needs zero further changes to add a country — this is the one significant way Malaysia's scope is smaller than Vietnam's. Direct consequence: Malaysia's dashboard is not yet end-to-end usable on this branch alone, since `app.py`'s `report()` route doesn't read `?country=` here (that wiring only exists on Vietnam's branch) — clicking the MY tab still displays SG's report until the two branches merge.

**Note (not a new decision, a process observation):** Two sibling feature branches — `feature/003-vietnam-country` and `feature/004-malaysia-country` — both cut from `168810e` and both independently PASSed `/feature-verify`, each ran its own `/update-context` pass in its own isolated worktree. Neither branch's `.context/` updates are visible to the other since neither has merged to `main`. Reconciling STATE.md/DECISIONS.md/ROADMAP.md content across both branches is an outstanding manual step for whoever merges second — not resolved as part of either feature's context refresh.

---

## [2026-07-10] — Integration review branch: Vietnam + Malaysia merged for combined dashboard review

**Decision:** Created `integration/vn-my-review`, a temporary branch (not intended to itself be merged to `main`) merging `feature/003-vietnam-country` and `feature/004-malaysia-country` together, so Alfonso could review both countries' dashboards side by side before deciding on real merge order/strategy. Neither original feature branch was modified by this merge.
**Rationale:** Alfonso explicitly wanted to review Vietnam and Malaysia together but did not want to merge either branch to `main` yet ("I'd rather remain in this in-progress branch and then merge once we have all the changes finished"). Malaysia's own branch alone can't demonstrate working country-switching (it has zero `app.py` changes), so a combined branch was the only way to give Alfonso a genuinely working combined dashboard without touching `main`.

**Decision:** Merge conflicts resolved as follows — `templates/base.html`: took Malaysia's version verbatim (already a superset containing SG/VN/MY all as real links, since Malaysia's branch had independently reproduced Vietnam's fix). `config/sources.json`: git's line-level diff3 algorithm produced 20+ confusingly interleaved conflict hunks (both branches append a same-shaped JSON object at the same insertion point); resolved by programmatically reconstructing the file from each branch's own known-good JSON (confirmed SG blocks were byte-identical between both branches first) rather than hand-editing conflict markers — final `countries` array is `[SG, VN, MY]`. `data/company_context.md`: both branches' Key Prospects/Ecosystem Players additions kept in full (Vietnam's subsection followed by Malaysia's, no content lost). `.context/STATE.md`/`DECISIONS.md`/`ROADMAP.md`: manually reconciled to reflect both features' completion, framed explicitly as an integration/review branch rather than either original feature's own state.
**Rationale:** The `sources.json` diff3 confusion was a genuine git limitation worth recording — future multi-branch JSON-array-append merges in this repo should expect the same interleaved-conflict pattern and should default to programmatic reconstruction over manual conflict-marker editing, which would be highly error-prone at that scale (20+ hunks across ~1500 lines).

---

## [2026-07-08] — Feature 003 (Vietnam Country Expansion): scope, sector mapping, and country-scoping fixes locked

**Decision:** Vietnam (`VN`) added as a second, fully independent country, using the real ~60-source list Alfonso received (`Silversea_Vietnam_Market_07072026.pdf`), branching this feature from `main` (`168810e`) rather than from the concurrently-in-flight `feature/002-local-llm-backend` branch.
**Rationale:** This is the first real exercise of the `--country` scaffolding built in Supervisor Feedback Round 2 against genuine second-country data. `feature/002-local-llm-backend` was a separate, unrelated, not-yet-executed feature being worked in a sibling git worktree this session — branching from `main` instead keeps the two features fully independent, avoiding any dependency between them. This is the first time this project has used sibling git worktrees to let two Claude Code sessions work the repo concurrently without colliding on branch checkouts.

**Decision:** The VN source list's categories (which don't map 1:1 onto the pipeline's existing 6-sector taxonomy — notably no "associations" category) were mapped as: `Government Authority`→`gov_agencies`; `Target/Existing/Potential/generic Customer`→`customers`; `Competitor`/`Competitor-partner`→`competitors`; `Dealer/Supplier` and `Facility Management`→`partners`; `News/Research`→`general_news`.
**Rationale:** User-confirmed mapping. Kept the taxonomy unchanged (per the standing "sector = relationship to Silversea, not industry" decision) rather than inventing a new category for the one non-matching case.

**Decision:** VN's `priority_keywords`/`keywords` lists reuse SG's as a starting point, stripped of SG-specific terms (`GeBIZ`, `BCA Green Mark`, and SG-only competitor names `Hiverlab`/`Gelement`/`TwinLogic`/`TwinMatrix`) — English-only, no Vietnamese-language equivalents this round.
**Rationale:** Keeps effort proportional; empirically tune keyword-hit rate during a future live run rather than upfront translation work, matching how SG's list was iteratively tuned. Accepted risk: Vietnamese-only sources may score consistently low under this filter — logged as a known limitation, not a blocker.

**Decision:** `pipeline/feedback.py` and `pipeline/weekly.py` country-scoped now, not deferred again — both gained a `country_code` parameter and `where={"country": ...}` ChromaDB filtering, mirroring the pattern `pipeline/analyst.py` already used for `REPORT_HISTORY` writes. `run_metadata.json` also country-scoped to `run_metadata_{code}.json`, mirroring `report.py`'s existing domain-scoping filename pattern.
**Rationale:** User decision, explicitly reversing the "declined for this round" deferral recorded in Feature 001's 2026-07-08 entry above ("No second country has real data yet to make the country-scoping gap observable"). With VN now real data, leaving feedback/weekly global would blend VN and SG feedback digests into one collection, directly undermining the requirement that each country run independently.

**Decision:** A parallel Vietnam subsection was added to `data/company_context.md`'s "Key Prospects & Relationships" and "Ecosystem Players" sections (Vingroup, Sun Group, VSIP, FPT, Viettel, Becamex, etc.); the "Products by Business Sector," "BD Priorities," and "Regulatory" sections were left untouched as already country-agnostic. `COMPANY_CONTEXT` vectorstore re-seeded (41 chunks, up from 34).
**Rationale:** `COMPANY_CONTEXT` RAG retrieval is not country-filtered by design (correct for the shared product catalog), so leaving prospects/ecosystem sections SG-only would surface irrelevant SG framing into every VN report.

**Decision:** `pipeline/analyst.py`'s `SUMMARY_PROMPT` fixed to interpolate the actual country name (`country["name"]`) via `str.replace()`, not `.format()`.
**Rationale:** The prompt string contains a JSON schema block with literal curly braces later in the same string; `.format()` would collide with those braces. `str.replace()` on a single named placeholder avoids the collision entirely. This closes the "Singapore" hardcoding that Feature 001's recon pass had flagged as a known gap outside its own scope.

**Decision explicitly out of scope this round (recorded so it isn't re-raised as undecided):** `pipeline/weekly.py`'s `WEEKLY_PROMPT`, `SUMMARIZE_PROMPT`, and `CONSOLIDATION_PROMPT` constants were deliberately left untouched — still hardcode "Singapore" in their framing — because Task 008's declared scope was ChromaDB metadata/filtering plumbing only, not prompt content, and CONTEXT.md's Scope section named only `SUMMARY_PROMPT` for the country-hardcoding fix. Data-layer country-scoping (which documents get retrieved/compressed) is correct regardless; only the LLM's self-description text is wrong. Logged as a small follow-up feature/task, not a defect in this feature.
**Rationale:** Reviewed and confirmed not-FAIL-worthy in `/feature-verify` — re-litigating a scope boundary CONTEXT.md set deliberately and narrowly would have meant scope creep in the review step itself.

---

## [2026-07-08] — Feature 001 (Round 2 Remediation): remediation scope and fixes locked

**Decision:** A full remediation feature (`.context/features/001-round2-remediation/`) was scoped against the "Supervisor Feedback Round 2" WIP commit (`3dc471a`) after an independent Fable-model review found the admin/viewer auth gate had a bypass, the SpatioX→real-catalog rebuild was only partially applied (accurate transcription in `company_context.md`'s catalog section, but prompts/gate keywords/post-processing/filter keywords downstream still ran on the old 4-product SpatioX worldview), and a broader recon pass surfaced three additional `/feedback`-route hardening gaps.
**Rationale:** Both the executor's self-report and a prior independent handoff review had been trusted without re-verification; re-verifying from scratch found real, live-exploitable gaps (auth bypass, unsanitized filename input) that a shallower review missed. Bundling all findings into one remediation feature, sequenced by shared-file dependency, matches the project's established pattern (see the 2026-07 Round 2 scope-lock entry) for avoiding repeated touches to the same files across sessions.

**Decision:** Admin/viewer auth bypass fixed by refusing login when `ADMIN_PASSWORD`/`VIEWER_PASSWORD` is unset or empty (checked before any comparison), and switching both password comparisons to `hmac.compare_digest`.
**Rationale:** The prior implementation allowed an empty `ADMIN_PASSWORD` env var plus a blank form submission to satisfy a `==` comparison and grant admin access; plain `==` on secrets is also timing-attack-prone. This makes the unset-password case *safe* (login refused) but not *functional* — Alfonso must still set `ADMIN_PASSWORD` to actually use admin login.

**Decision:** `/feedback` route hardened on three fronts, folded into the same task as the auth fix since both are security-adjacent and touch `app.py`: (1) `submitter` is sanitized via a whitelist regex before being used in a filename (previously only spaces were replaced, allowing `..\..\foo`-style path traversal outside `data/feedback/`/`data/pending_sources/`); (2) `relevance_rating`'s int conversion is wrapped in try/except returning a clean 400 JSON error instead of crashing with a 500; (3) `Access-Control-Allow-Origin: *` scoped to the `/feedback` route only, not applied globally via `add_cors()` to every route in the app.
**Rationale:** All three were found during a pipeline-wide recon pass run alongside the Feature 001 discussion, not part of the original auth-bypass report. Since they land in the same file and same security surface as the auth fix, deferring them to a separate future round was judged to add re-review cost for no benefit — user decided to fold them in now.

**Decision:** SpatioX→real-catalog rebuild finished consistently, using an explicit naming map: Ops→Smart Facility Management System, Audit→Smart Virtual Inspection, Twin→Digital Twin, Walk→3D/VR Virtual Tour. Applied across `data/company_context.md`'s three remaining sections (Target Sectors, Key Prospects, Ecosystem Players — the "Products by Business Sector" section was already correct and left untouched) and `pipeline/analyst.py`'s `SUMMARY_PROMPT` system message, opportunities gate keywords, `product_fit` instruction, `_generate_implications`, and `_derive_competition_risks`.
**Rationale:** The 2026-07 catalog transcription (from `docs/Copy of Business Sector _ed01.pdf`) was accurate in isolation but nothing downstream had been updated to actually use it — the analyst's live prompts, gate, and post-processing were still reasoning in terms of the old 4-product SpatioX suite. The naming map came from the Fable review's analysis and was confirmed by the user rather than re-derived from scratch.

**Decision:** EDU expansion stays a stopgap this round — EDU-relevant terms (edtech, e-learning, LMS, campus, STEM, virtual lab, etc.) added directly to `config/sources.json`'s existing shared `keywords` list (not `priority_keywords`, no new per-domain keyword schema), and NUS/NTU dual-tagged `["BER","EDU"]` where genuinely applicable. A full real EDU source list remains a separate, expected future delivery from the supervisor.
**Rationale:** Building a full EDU source list wasn't available data at this point; a lightweight stopgap (shared keywords + dual-tagging two already-tracked sources) closes the most visible gap without inventing sources that don't have supervisor sign-off.

**Decision:** `pipeline/source_suggestions.py`'s `approve()` fixed to call a new `config/sources.py` `load_sources()` (re-reads `sources.json` from disk) instead of mutating the import-time `COUNTRIES` module-level singleton; an admin country selector (`templates/admin.html`, plain hardcoded SG `<select>` for now) added in the same task since both touch the same file area.
**Rationale:** The stale-singleton bug meant an admin approval action could silently operate on an out-of-date in-memory copy of the source list in a long-running Flask process. Bundling with the country-selector UI addition avoided a second pass through the same code region.

**Decision:** First-ever test file added to the repo: `tests/test_clamp.py` (plain pytest, no new test framework dependency), covering only the opportunity-scoring clamp (`_clamp_opportunity_scores`/`_SCORE_DIMENSIONS` in `pipeline/analyst.py`) — out-of-range dimensions, negative/non-numeric values, missing dimensions, a missing `scores` key entirely, an LLM-supplied bogus `total_score` being overridden, and independence across multiple opportunities in one response.
**Rationale:** The clamp is pure Python with zero LLM cost to exercise, closing a real "unit-tested" gap a prior review had falsely claimed was already closed. Scope stayed narrow (clamp only) rather than attempting broader pipeline test coverage in the same pass.

**Decision explicitly declined for this round (recorded so it isn't re-raised as undecided):** Country-scoping `pipeline/weekly.py` and `pipeline/feedback.py` ChromaDB writes, and reinstating the previously-lost "ecosystem entity taking a relevant action" second path on the opportunities gate (the gate stays keyword-only, EDU terms added alongside BER terms) — both left untouched, matching prior deferrals.
**Rationale:** No second country has real data yet to make the country-scoping gap observable; the ecosystem-entity gate path is a separate, previously-deferred decision this round didn't reopen. Also confirmed out of scope: `py main.py` end-to-end execution (Groq quota — Alfonso-owned manual checkpoint) and visual/print-preview QA of `login.html`/`admin.html` (pixels need eyes, not code review).

**Decision:** A pipeline-wide health-scan recon pass (run alongside this feature's discussion, not part of its scope) surfaced six additional issues, explicitly deferred to a future pipeline-polish round rather than folded into Feature 001: no LLM rate limiter exists despite a 2026-06-19 decision recording one; `sentence-transformers` is a direct explicit dependency in `pipeline/vectorstore.py` (correcting the prior STATE.md framing that called it transitive); the email digest likely renders blank due to HTML/plaintext MIME-part ordering in `main.py`; `run_metadata.json` isn't domain/country-scoped; `weekly.py`'s ChromaDB retrieval is order-unstable with no dedup guard; `pipeline/analyst.py` crashes on unset `GROQ_API_KEY` instead of degrading gracefully; and `scripts/feedback_server.py` is dead code left over from its 2026-06-23 consolidation into `app.py`.
**Rationale:** None of these block or belong in the auth/catalog/hardening remediation scope of Feature 001 — logged now so they aren't lost, to be picked up via a future `/feature-discuss` on general pipeline polish.

---

## [2026-07-02] — Supervisor Feedback Round 2: execution deviations and inline fixes

**Decision:** `save_sources()` in `config/sources.py` reads the existing `sources.json` before writing back, preserving all sibling root-level keys (`_domain_tagging_status` and any future ones) — not just the `countries` list.
**Rationale:** The original Phase B1 implementation wrote `{"countries": countries}` fresh on every call, silently dropping `_domain_tagging_status` on the first real admin approval. Surfaced by a post-implementation review. Fixed inline (read-modify-write) since it's two lines in the same file, fully backward-compatible, and prevents the source-suggestion approval flow from erasing the pending-review flag.

**Decision:** `_synthesize_summary()`'s LLM input f-string in `pipeline/analyst.py` now includes each signal's `source_name` — extending the original A2 spec scope by one line.
**Rationale:** Code-grounding during execution confirmed the pre-existing `f"- {entity}: {signal}"` string dropped `source_name` entirely, which would have made A2's schema change (LLM emitting `source_name` in opportunities) fail silently. Smallest possible fix; redesigning the message format was disproportionate.

**Decision:** Phase A parallelization was reduced from three concurrent subagents to one sequential subagent doing A1+A2+A3 back-to-back.
**Rationale:** A1+A2 both edit `SUMMARY_PROMPT`; A2+A3 both edit `templates/report.html`. Concurrent edits would silently overwrite each other. The consolidated agent still ran in parallel with disjoint Phase B1 and Phase C agents, so wall-clock impact was minimal.

**Decision:** Phase F's `analyse()` REPORT_HISTORY writes already carried `"country": country["code"]` metadata before this session — no F3 code change was made.
**Rationale:** Confirmed via `git show HEAD:pipeline/analyst.py` that the country key predated the session. `pipeline/feedback.py` and `pipeline/weekly.py` were deliberately left un-tagged per spec default, meaning `REPORT_HISTORY` accumulates a mix of country-tagged and untagged documents going forward — `where={"country":"SG"}` queries would silently exclude weekly-summary docs. Flagged to Alfonso, unresolved.

---

## [2026-07-02] — Supervisor Feedback Round 2: implementation planning, open items resolved

**Decision:** ChromaDB country-scoping uses a metadata filter (`"country": "SG"` added to existing `metadatas` dicts, plus an optional `where` parameter on `pipeline/vectorstore.py`'s `query()`), not separate collections per country.
**Rationale:** `pipeline/vectorstore.py` is a thin ~50-line global singleton (three fixed collection-name constants, one `PersistentClient`, four passthrough functions). A metadata filter is additive and backward-compatible everywhere `where` isn't passed. Separate collections would require dynamic collection-name generation at every call site for a feature with zero real non-SG data to test against yet.

**Decision:** The `config/sources.py` → `config/sources.json` migration does NOT add a per-source `"country"` field.
**Rationale:** Sources already nest inside each country's dict (`COUNTRIES = [{"code": "SG", "sources": [...]}]`) — country is already fully determined by nesting. A redundant field risks consistency drift for zero new information. `--country` filtering operates on `COUNTRIES[i]["code"]`; `--domain` filtering is genuinely per-source (one SG source can be both BER and GENERAL) and uses its own field. The admin-approval flow achieves the practical goal (picking which country's list to append to) without the redundant field.

**Decision:** `company_context.md`'s product catalog was rebuilt around the full 7-sector table (EDU, BER, MFG, HLS, RCC, CTE, PSS) transcribed directly from `docs/Copy of Business Sector _ed01.pdf` pages 1-3, replacing the "four-product SpatioX suite" framing that still persisted at several lines despite the earlier 2026-07 decision to move away from it.
**Rationale:** Code-grounding found the file was never actually updated past the SpatioX 4-product framing even though the architectural decision to change it had already been made. The PDF was now on disk and its per-sector product lists transcribed verbatim.

**Correction (not a new decision):** The 2026-06-26 entries below describing a fixed `SYNTHESIS_PROMPT` at specific line numbers, with an explicit widened `RELEVANCE GATE` and a sector-categorization instruction, no longer describe the current file. Code-grounding this session found `pipeline/analyst.py` was restructured into three separate prompts (`SECTOR_EXTRACT_PROMPT`, `SECTOR_SYNTHESIS_PROMPT`, `SUMMARY_PROMPT`) during the 2026-06-29/06-30 rewrites, and the widened relevance gate is no longer present — `SUMMARY_PROMPT` reverted to a keyword-only gate. Not a deliberate revert; appears lost when the prompt was restructured. Trust this correction over the 2026-06-26 entries' line numbers.

---

## [2026-07] — Supervisor Feedback Round 2: scope and architecture locked

**Decision:** Eight supervisor/Alfonso feedback topics (report auth, opportunity source links, opportunity scoring fix, feedback-driven source suggestion, PDF export, multi-domain EDU/BER/General restructure, company context rework, multi-country scaffolding) were bundled into one planning document, sequenced Phase A→F by dependency rather than executed ad hoc.
**Rationale:** Several topics share files or ordering constraints (source-suggestion approval needs the auth work; multi-domain, multi-country, and source-suggestion all touch `config/sources.py`). Bundling with an explicit dependency-aware sequence avoids touching shared files multiple times across sessions — same rationale as the original Phase 4 bundling decision (2026-06-26).

**Decision:** Report authentication uses two static shared passwords (`VIEWER_PASSWORD`, `ADMIN_PASSWORD`) with Flask session cookies — no user accounts, no per-person login.
**Rationale:** Requirement is company-wide shared access gated by a password, with password-rotation privilege restricted to CEO/technical roles. A second admin-only secret satisfies the role restriction without building real per-user authentication the project doesn't otherwise need. The viewer password is stored in a local file (not just an env var) so an admin can change it without a redeploy.

**Decision:** `config/sources.py` (a Python literal) migrated to `config/sources.json`, with `sources.py` reduced to a thin loader.
**Rationale:** The source-suggestion feature needs an admin-approval action to safely append a new source to the live config from a web request. Writing to Python source from a request handler (text templating or AST manipulation) is fragile and hard to review/rollback; JSON supports safe read-modify-write and diffs cleanly in git.

**Decision:** Opportunity source links reuse the existing `source_name` → `data_sources` URL-lookup pattern already built for signal cards (2026-06-30), rather than having the LLM generate a URL directly.
**Rationale:** `SUMMARY_PROMPT` had the LLM fill in `"source_url": ""` itself with no real URL to draw from — the actual cause of empty opportunity links. The signal-card mechanism already solves this; reusing it needs only a schema change (opportunities emit `source_name` instead of a fabricated URL).

**Decision:** Opportunity scoring bug root cause: `SUMMARY_PROMPT`'s `scores` JSON block specified no scale, range, or total-score calculation method — the LLM had always been inventing its own scale. Fix: a locked 5-dimension rubric (strategic fit, revenue potential, win probability, urgency, intelligence quality; each 1-5, `total_score` capped at 25), stated explicitly in the prompt, plus a Python-side clamp-and-recompute safety net after parsing the LLM's JSON.
**Rationale:** Supersedes the earlier "model sometimes outputs scores >5 per dimension" framing — the actual defect was a missing instruction, not inconsistent model behavior. The Python-side net guards against a future prompt regression silently reproducing out-of-range totals.

**Decision:** The `domain` field (from the earlier "Multi-domain pipeline architecture" decision below) becomes 3-valued for this round — `BER`, `EDU`, `GENERAL` — rather than just BER/EDU. Company context and analyst prompts rebuilt around Silversea's real ~14-solution product catalog (from `Copy of Business Sector _ed01.pdf`) instead of the SpatioX 4-product framing, even though only EDU/BER/GENERAL are active domains this round.
**Rationale:** `GENERAL` fills the role of "relevant to Silversea overall, not sector-specific" as a first-class domain rather than a fallback bucket. The product-catalog rebuild was prompted by the sector sheet revealing the current framing doesn't reflect Silversea's actual catalog; fixing it now avoids a second rework pass when MFG/HLS/RCC/CTE/PSS eventually get built out.

**Decision:** Company context regulatory content stripped to universal-only statements — no country-specific regulatory detail — leaving regulatory-fit judgment to each local team.
**Rationale:** Maintaining per-country regulatory detail in one shared file is unsustainable as country expansion proceeds.

---

## [2026-07] — Multi-domain pipeline architecture chosen for BER + EDU expansion

**Decision:** The pipeline supports multiple industry domains (starting BER — Built Environment & Real Estate, and EDU — Education & EdTech) on one shared pipeline, not two separate pipelines. Each source in `config/sources.py` gains a `domain` field (`"BER"`, `"EDU"`, or a list for shared sources). `main.py` accepts `--domain` to filter sources and produce a domain-specific report. The Flask dashboard gets a domain switcher tab.
**Rationale:** BER and EDU have significant source overlap (e.g. GovTech, Smart Nation publish signals relevant to both). Two fully separate pipelines would scrape the same sources twice with no cross-domain signal surfacing. Implementation deferred until the EDU source list was received.

**Decision:** The existing pipeline sectors (`gov_agencies`, `associations`, `customers`, `partners`, `competitors`, `general_news`) describe each source's *relationship to Silversea*, not the *industry domain* it covers — this stays fixed. The new `domain` field is additive and orthogonal.
**Rationale:** The supervisor's 7-sector business document (EDU, BER, MFG, HLS, RCC, CTE, PSS) clarified that the current pipeline covers almost exclusively BER + PSS by content, with EDU appearing only incidentally. The relationship taxonomy stays unchanged; domain tagging is the mechanism for multi-sector expansion.

**Decision:** Other-country teams submit source lists via `docs/source_submission_template.xlsx`, generated by `scripts/generate_source_sheet.py`. Required fields: Source Name, Source URL, Description. Optional: Relationship Type (dropdown), Business Domain (dropdown). 100 pre-formatted rows with conditional formatting graying out unused rows.
**Rationale:** PDF fillable forms require Adobe Acrobat Pro to author. Google Sheets required MCP tooling that added friction. Excel via openpyxl generates locally in seconds, opens natively anywhere, and converts to Google Sheets if needed. Grayed rows (vs. Apps-Script dynamic row spawning) avoids the Google authorization prompt that macro-bearing sheets trigger.

---

## [2026-06-30] — Frontend redesign: interaction and visual architecture

**Decision:** Collapsible entity-based grouping within each sector — signals grouped by entity (e.g. BCA, URA) via Jinja2 dict aggregation, collapsed by default. Applies to Competition Risks too.
**Rationale:** With 65 signals, a flat grid is overwhelming; grouping by entity lets users scan entity names and expand only what's relevant. Collapse animation uses CSS `grid-template-rows: 0fr → 1fr` for smooth height transitions.

**Decision:** Signal spotlight interaction — inline expansion with backdrop dim/blur, not a modal.
**Rationale:** Alfonso chose inline over modal to preserve spatial context. Clicking adds a `spotlight-active` class (scale + border glow + larger text), applies `spotlight-mode` to body (dims/blurs other cards), shows a backdrop overlay. Dismissed via click, Escape, or overlay click.

**Decision:** Sector color coding — 5 accent colors via CSS custom properties and `data-sector` selectors: Government=#3b82f6 (blue), Associations=#0d9488 (teal), Partners=#8b5cf6 (purple), Competitors=#e11d48 (rose), General News=#64748b (slate).
**Rationale:** Alfonso wanted "heavier color scheming" for instant sector scannability without reading text. Colors carry through sector header bars, card left borders, implication boxes, entity group badges.

**Decision:** Dark mode via Tailwind `darkMode: 'class'` with a nav-bar toggle switch, state persisted in `localStorage`, falling back to system preference if unset.
**Rationale:** Alfonso wanted a user-controlled toggle, not just system preference. `localStorage` persistence prevents the toggle resetting on reload with minimal added complexity.

**Decision:** Source URLs mapped from the `data_sources` array to signal cards via a Jinja2 dict lookup (`source_urls[signal.source_name]`) — no pipeline code changes.
**Rationale:** Signal objects have `source_name` but empty `source_url`; the URLs already exist in `data_sources` in the same JSON. Template-level mapping avoids touching pipeline code.

---

## [2026-06-29] — Per-sector synthesis architecture: information density fix

**Decision:** Replaced the single monolithic synthesis LLM call with a three-phase approach: (1) 6x per-sector extraction calls (unchanged), (2) 6x per-sector JSON synthesis calls via `SECTOR_SYNTHESIS_PROMPT` — each converts one sector's extraction text into structured `[{entity, signal, source_name}]` JSON, (3) 1x summary-only call via `SUMMARY_PROMPT` producing only `executive_summary`, `opportunities`, `synthesis` from the already-structured signals. The old monolithic `SYNTHESIS_PROMPT` was deleted. Implications (`implication` field) generated in Python post-processing (`_generate_implications()`) with keyword-specific overrides — zero LLM cost.
**Rationale:** The single synthesis call was the proven bottleneck, dropping ~90% of extracted signals (60-80 → 7). The 17B `llama-4-scout` model handles small, focused tasks well but can't compress all sectors into one large JSON response. Splitting synthesis per-sector gave each sector dedicated attention. Signal count: 7 → 65. Total LLM calls/run: 7 → 13. Token budget: ~15-20k/run, well within 100k TPD and 30k TPM limits.

**Decision:** Signal grid layout in `templates/report.html` changed from stacked full-width cards to responsive 3-column grid (`grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4`).
**Rationale:** Alfonso requested a grid layout matching a reference site's Discovery card layout instead of full-width stacked rectangles.

---

## [2026-06-29] — Dashboard density overhaul: schema expansion backfired

**Decision:** Expanded `SYNTHESIS_PROMPT` signal schema from `{entity, signal}` to `{entity, signal, source_name, implication}` and added a Python-based competition-risks post-processor classifying competitor signals by threat level.
**Rationale:** Alfonso reviewed the dashboard against a reference site and found per-signal information far too sparse. Competition risks were derived in pure Python (zero token cost) to avoid overloading the LLM.

**Decision (reverted):** The schema expansion caused a signal-count regression from 11 to 7. Adding fields to the synthesis prompt was confirmed counterproductive on the 17B model — it trades count for marginal depth, and Alfonso wants both. This directly motivated the per-sector synthesis rewrite above.
**Rationale:** `llama-4-scout` has limited instruction-following capacity; more output fields per signal means fewer signals total. The fundamental bottleneck (one monolithic call compressing all sectors) can't be solved by prompt engineering alone on a 17B model.

**Decision:** Template restructured from bullet lists to individual cards per signal, with "For Silversea Media" implication callouts (LLM-generated with sector-based fallback heuristics). Competition risks section added with threat-level badges. Data sources collapsible table added.
**Rationale:** Alfonso confirmed the card-per-finding approach was correct but wanted a 3-column grid (like the reference site) instead of full-width stacked rectangles — direction correct, layout needed adjustment (resolved by the per-sector rewrite's grid change above).

---

## [2026-06-29] — Pipeline verification: bugs found and fixed

**Decision:** Fixed `analyst.py` which used `MODEL` instead of `GROQ_MODEL`, causing a `NameError` at synthesis time — a leftover from the split-model refactor's variable rename.
**Rationale:** Stage-by-stage verification caught it before a full pipeline run; without the fix, `main.py` would crash after all extraction calls completed but before producing the final report.

**Decision:** IMDA URL corrected from `/resources/press-releases` to `/resources/press-releases-factsheets-and-speeches`, fetcher set to `"dynamic"`.
**Rationale:** The old URL 404-redirected ("Page Not Found"); the correct path was found via the IMDA homepage. The page is JS-rendered, requiring the dynamic fetcher. Content went from 25 chars (useless) to 5,545 chars (real press releases).

**Decision:** CCCC set to `active: False`.
**Rationale:** Consistently times out (15s exceeded) — site unreachable from Singapore. CSCEC (same category) still works and stays active.

**Decision:** Scrapling installed and all stealth/dynamic fetchers verified working. Active source count: 57.
**Rationale:** Verification run confirmed real content returned for SJ Group, Schneider Electric, Alstern Technologies, Aperio, MCC, IMDA — all previously failing due to missing Scrapling.

---

## [2026-06-29] — Pipeline optimization pass: Scrapling integration and dead code removal

**Decision:** Scrapling library integrated into `pipeline/scraper.py` with tiered fetcher strategy: `_fetch_default()` (plain requests), `_fetch_stealth()` (Scrapling StealthyFetcher — Cloudflare/bot bypass), `_fetch_dynamic()` (Scrapling DynamicFetcher — full browser rendering for JS SPAs). Per-source `"fetcher"` config field dispatches. Imports are lazy so the pipeline still works without Scrapling installed.
**Rationale:** 5+ sources were inactive due to 403 errors or JS-only rendering that requests+BeautifulSoup can't handle. API verified against official docs before integration.

**Decision:** `pipeline/dedup.py`, `pipeline/entities.py`, `pipeline/scoring.py` deleted; `sentence-transformers` dependency dropped.
**Rationale:** All three produced no useful output in practice — dedup loaded a 90MB model and consistently merged 0 results; entities attached data nothing downstream read; scoring tracked unreliable citation-based scores that decayed to 0. Removing them simplifies the pipeline and drops ~500MB of dependencies.

**Decision:** Filter keyword rebalancing — entity names (competitors, customers, ecosystem players) moved from `priority_keywords` (3x weight) to `keywords` (1x weight).
**Rationale:** Sources were auto-passing the relevance filter just by mentioning their own name (e.g. CapitaLand's newsroom scoring 3+ just because "CapitaLand" was a priority keyword). Now a source must mention a technology/domain term to score high enough to pass.

---

## [2026-06-29] — Split-model approach failed — simplified prompt instead

**Decision (reverted the 2026-06-26 split-model decision below):** `gpt-oss-120b` rejected entirely for synthesis. It returns empty output on `SYNTHESIS_PROMPT` — tested both with and without `response_format={"type": "json_object"}`.
**Rationale:** Three failure modes discovered: (1) Groq counts `max_tokens` against TPM, so input 5.4k + max_tokens 6k = 11.4k >> 8k limit; (2) reducing max_tokens to 2.5k (total 7.9k < 8k) still produced empty output with response_format; (3) without response_format, still empty. The model simply couldn't handle this task.

**Decision:** `SYNTHESIS_PROMPT` simplified from ~117 lines to ~30 lines, keeping `llama-4-scout` for both extraction and synthesis.
**Rationale:** The dense multi-rule prompt was designed for when the LLM saw raw content directly; in the multi-pass architecture extraction already handles grounding, so the synthesis prompt carried unnecessary weight the 17B model couldn't process. Opportunities improved 0 → 3. Signal count still ~9 vs ~30+ in extraction (~60-70% loss, improved from ~80% but still unacceptable — resolved later by the per-sector synthesis rewrite). Known issues at this point: scoring ignored the 0-5 scale, G Element duplicated across sectors.

**Decision:** RAG context (`_build_rag_context()`) removed from the synthesis call — became dead code at this point.
**Rationale:** Token budget constraint — RAG context added ~1-2k redundant tokens (company context already hardcoded in the prompt) plus feedback priorities and past themes. Must be restored when switching to Claude Haiku (200k context removes the constraint).

**Decision:** Claude Haiku upgrade deferred until pipeline optimization is complete.
**Rationale:** Alfonso wants scraper, filter, RAG, and feedback systems hardened and verified before switching the synthesis model — no point feeding a better model through a leaky pipeline.

---

## [2026-06-26] — Split-model architecture for extraction vs synthesis (superseded 2026-06-29 above)

**Decision:** Multi-pass analyst pipeline used two different Groq models: `meta-llama/llama-4-scout-17b-16e-instruct` (17B, 30k TPM) for per-sector extraction, `openai/gpt-oss-120b` (120B, 8k TPM) for the single synthesis call.
**Rationale:** No single free-tier Groq model worked for both stages. `gpt-oss-120b` had strong instruction-following but only 8k TPM — too small for extraction where raw content across 9-11 sources/sector reaches 9-10k tokens. `llama-4-scout` had 30k TPM (extraction never hit it) but was too weak to follow the dense synthesis prompt, over-summarizing (report went ~25 → ~10 signals). Synthesis input was only ~5.7k tokens, fitting under `gpt-oss-120b`'s 8k TPM.

**Decision:** Both `SYNTHESIS_PROMPT` bug fixes (widened relevance gate, sector categorization — see 2026-06-26 execution entry below) confirmed working on a `llama-4-scout` run.
**Rationale:** Verification run with all 6 sectors extracting: opportunities gate correctly identified BCA Construction Startup Competition (18/25), correctly excluded URA residential tenders; no cross-sector signal duplication. Status upgraded "unverified" → "verified" (later superseded when `gpt-oss-120b` was abandoned entirely).

**Decision:** `CALL_DELAY` reduced from 25s to 2s.
**Rationale:** `llama-4-scout`'s 30k TPM made the old 25s inter-call delays (designed for 6-12k TPM models) unnecessary. Even the `gpt-oss-120b` synthesis call fit in a single request. Pipeline run time dropped ~3 min → ~30s.

---

## [2026-06-26] — Phase 4 execution: SYNTHESIS_PROMPT bug fixes applied (later reverted/lost, see 2026-07-02 correction above)

**Decision:** Widened the RELEVANCE GATE in `SYNTHESIS_PROMPT` to accept a second path for opportunities: a tracked ecosystem entity (customer, partner, competitor, government agency) taking a built-environment-relevant action, alongside the original keyword-mention path. Anti-fabrication rule preserved.
**Rationale:** The strict keyword-only gate produced zero opportunities on the last real run — technically correct per design, but useless for a BD-facing report every run.
**Status note:** Per the 2026-07-02 correction above, this fix no longer exists in the current file — it appears to have been lost during the 2026-06-29/06-30 prompt restructuring, not deliberately reverted.

**Decision:** Added a sector mis-categorization prevention instruction to `SYNTHESIS_PROMPT`.
**Rationale:** Sources configured under `competitors` (e.g. G Element, DataMesh) had signals duplicated into the `Partners` bucket — the LLM was bucketing by semantic content rather than configured sector.
**Status note:** Same as above — no longer present in the current prompt structure.

**Decision:** Model research revealed `llama-3.3-70b-versatile` was deprecated by Groq on 2026-06-17. Recommended replacement: `openai/gpt-oss-120b` (drop-in) or `meta-llama/llama-4-scout-17b-16e-instruct` (30k TPM, eliminates inter-call delays). See `data/model_research.md`.
**Rationale:** The pipeline would fail or behave unpredictably on the next run if the model string wasn't updated — this surfaced unexpectedly during research, not as a planned change.

---

## [2026-06-26] — Phase 4 scope locked: efficiency, coverage, and bug-fix pass

**Decision:** Eight items bundled into one sequential pass: (1) expand `company_context.md` with ecosystem-player detail, (2) build a no-AI rule-based keyword filter with tiered weighting, (3) replace `scraper.py`'s blind character-cut truncation with keyword-anchored smart truncation, (4) add the supervisor's full ~50-source ecosystem list (deduplicated) and fix known broken scrapers, (5) add a metrics/scores glossary to the dashboard, (6) add feedback-digest consolidation to stop unbounded ChromaDB growth, (7) produce a written LLM model-research comparison with zero live API calls, (8) fix two known `SYNTHESIS_PROMPT` bugs — sequenced last, shipped "unverified."
**Rationale:** These items spanned token-efficiency, source coverage, model choice, and report clarity, all interrelated enough that splitting into separate phases risked losing shared context (e.g. the filter's keywords depend on the expanded company context). Alfonso explicitly chose one big phase over splitting, since there was no fixed deadline. Two rounds of plan review (code-grounded, then pure-logic) found and corrected real sequencing issues before lock-in.

**Decision:** Chinese state contractors (CSCEC, CCCC, CHEC) included as `partners`-sector sources, superseding the 2026-06-23 exclusion below.
**Rationale:** The 2026-06-23 exclusion was scoped to a prioritized demo subset, not a permanent call. The supervisor's full ecosystem-list PDF re-listed them under "Main contractors."

**Decision:** TwinMatrix re-added as a `competitors`-sector source, superseding the 2026-06-23 drop below.
**Rationale:** Same as above — the 2026-06-23 drop was specific to that round's prioritized subset; the supervisor's full list re-included it under "Key competitors."

**Decision:** Main contractors, consultants, M&E/BMS system integrators, and facility-management firms all map onto the existing `partners` sector — no new sector introduced.
**Rationale:** Consistent with the existing convention (AECOM, CPG Consultant, Honeywell, Cushman & Wakefield already classified as `partners`) and the fixed five-sector-plus-general_news taxonomy. Owners are buyers (→ `customers`); every other ecosystem role is a potential service/channel partner (→ `partners`).

---

## [2026-06-24] — Presentation prep: demo toggle kept, two analyst quality bugs surfaced

**Decision:** `app.py`'s `?demo=clean|feedback` query-param toggle and the "Clean Run"/"With Feedback" badge were kept as working state, not reverted — even though the feedback-influenced report was never generated (`data/presentation/` doesn't exist) and the supervisor demo already happened.
**Rationale:** Alfonso confirmed the supervisor saw this in-progress state and it's fine as historical/working state; reverting would discard harmless scaffolding for no benefit. (Still non-functional as of the last check — `data/presentation/` still doesn't exist.)

**Decision:** Two analyst-output quality issues logged as known bugs, not fixed immediately: (1) `opportunities: []` — the relevance gate let zero signals through, "correct" per the prompt's design but unhelpful for a demo; (2) sources configured under `competitors` (G Element, DataMesh) had signals duplicated into the "Partners" bucket.
**Rationale:** Both required a `SYNTHESIS_PROMPT` change, out of scope for presentation-prep and costly to test against Groq tokens. Deferred to Phase 4 (addressed 2026-06-26 above, later lost per the 2026-07-02 correction).

**Decision:** Groq's free-tier daily quota (100k TPD) was fully exhausted for 2026-06-24 (~99,481/100,000). No further `main.py` runs until UTC midnight reset — confirmed with Alfonso to hold off intentionally.
**Rationale:** Groq's 429 message ("try again in Xm") understates the real wait — it's a daily quota tied to UTC midnight, not a short rolling window.

---

## [2026-06-23] — Multi-pass analyst architecture for information density

**Decision:** Rewrote the analyst from a single monolithic LLM call to a two-phase multi-pass approach: Phase 1 makes one Groq call per sector with full untruncated source content, extracting every named signal; Phase 2 synthesizes all sector extractions into the final structured report.
**Rationale:** Info-gap analysis showed the single-call approach lost ~75% of actionable signals. Root causes: the LLM silently dropped entire sectors (Competitors, Partners) when given 21 sources at once, and 800-char truncation cut rich sources (e.g. DataMesh 8000 chars → 800). Multi-pass eliminated truncation (each sector has 2-6 sources, fits under 12k TPM) and forced per-sector attention. Report size 4,600 → 8,000 chars, 17/17 key signals present. Trade-off: ~3 min runtime (25s inter-call delay for Groq TPM compliance) vs ~30s for single call.

---

## [2026-06-23] — Phase 3.5: visual design revamp direction locked, then executed

**Decision:** Report page (`/`) gets a dark navy-to-black glassmorphism revamp — continuous dark zone spanning top nav, country tabs, and a new hero section with animated glass stat cards, a sticky scroll-spy nav, and a restructured Opportunities section (top 3 by score expanded equally, rest collapsible) — transitioning to a light, soft-shadowed body below. Internals page (`/internals`) gets the same shadow/hover/animation vocabulary but stays light throughout, no dark hero.
**Rationale:** An initial "Notion-style restrained polish" framing was explicitly rejected by Alfonso as underselling the ambition — he wanted a genuine structural/visual revamp ("luxurious," "visually impressive"), not incremental styling. Internals stays lighter because it's dev-facing and lower priority, not because the revamp direction was scaled back generally.

**Decision (explicitly declined alternatives, recorded so they aren't reintroduced as undecided):** Glow/accent color stays brand green (`#2d6a4f`) only — no new accent (e.g. gold/champagne) introduced. Sector cards keep a uniform grid (no bento layout). Opportunities keep equal visual weight across the top 3 (no single spotlight card for #1).
**Rationale:** These were live options Alfonso considered and chose not to take in discussion.

**Decision:** Space Grotesk (Google Fonts CDN) added for headlines/section headers/stat numbers; Inter remains the body font. AOS (Animate On Scroll, CDN) added for scroll-reveal animations.
**Rationale:** Both are zero-build-step CDN additions fitting the "no architecture change" constraint — Flask + Jinja2 server-side rendering is preserved; the dark hero and glass effects are pure CSS (`backdrop-filter`), not a new rendering layer.

**Decision:** All visual revamp changes were implemented exactly per the locked spec. New CDN dependencies: Google Fonts (Space Grotesk + Inter), AOS 2.3.1. New file: `static/animations.js` (count-up, scroll-spy, sticky nav). No Python packages added, no architecture change.
**Rationale:** Execution session; all decisions were made in the prior discussion session.

---

## [2026-06-23] — Phase 3 dashboard architecture decisions

**Decision:** Analyst output changed from freeform markdown to structured JSON (`executive_summary`, `signals_by_sector`, `opportunities`, `synthesis`).
**Rationale:** The dashboard needs to render score badges, sector cards, score-breakdown bars — impossible from a prose string requiring regex parsing. Grounding rules and scoring rubric stayed untouched; only an additive OUTPUT FORMAT block was appended.

**Decision:** Flask + Jinja2 with live per-request rendering (no SPA, no React, no FastAPI).
**Rationale:** The pipeline is batch-driven (once/day). Pages are server-rendered from JSON files + ChromaDB reads. Flask was already a dependency (feedback server). A JS framework would add npm/build tooling for no capability gain. Live rendering (vs. pre-baked HTML) is simpler — always current, no generation step to keep in sync.

**Decision:** Tailwind CSS via CDN for styling; Chart.js via CDN for internals charts.
**Rationale:** No build step. CDN is fine for an internal low-traffic dashboard. Tailwind gives utility-class control without custom CSS overhead; Chart.js is the lightest free option covering bar/line/doughnut.

**Decision:** Two-page split — report page built from scratch, internals page adapts a free Volt Dashboard template.
**Rationale:** The CEO-facing report page must not look generic — custom Tailwind + CSS variables gives visual-identity control. The maintainer-facing internals page has no such constraint, so adapting a free admin template saves build time on a page no one judges aesthetically.

**Decision:** Feedback endpoint consolidated from a separate `scripts/feedback_server.py` (port 5050) into the main Flask app (`app.py`, port 5000).
**Rationale:** One server instead of two, same CORS/JSON logic. The feedback form's action URL changed to `/feedback` (relative, same origin).

---

## [2026-06-23] — Real sources finalization executed: branding + sources + feedback-loop demo

**Decision:** `data/company_context.md` (vector-store seed doc) updated alongside `analyst.py` to replace all MetaTwin→SpatioX references, then re-seeded into ChromaDB.
**Rationale:** The RAG pipeline retrieves company-context chunks at inference time; if the seed doc still said "MetaTwin," the LLM could echo wrong product names even with the system prompt fixed. Both files must stay consistent.

**Decision:** SGTech, CPG Consultant, and FacilityBot marked `active: False` after dry-run scrape verification.
**Rationale:** SGTech's ASP.NET news URLs return 404. CPG Consultant has no dedicated newsroom page. FacilityBot's `/blog` returns 404. All three kept in config for future re-evaluation, excluded from the daily pipeline to avoid error noise.

**Decision:** Final active source count was 30 (not the ~24 originally estimated) because pre-existing sources were kept as-is per the execution plan.
**Rationale:** The plan said "leave existing ones as-is" for sources like GeBIZ, Smart Nation, NUS/NTU/SGH. The ~24 estimate counted only new + key existing sources, but the file already had more active entries from Phase 1.

---

## [2026-06-23] — Branding bug found: analyst prompt referenced wrong product names

**Decision:** `pipeline/analyst.py`'s SYSTEM_PROMPT corrected to reference Silversea's real products (SpatioX Twin/Ops/Audit/Walk) instead of the placeholder "MetaTwin Object/Space/Immerse/Augment."
**Rationale:** The placeholder names were never updated after the company profile was confirmed. Since this string drives the Product Fit field in every generated Opportunity, it would surface as a visible factual error in any manager-facing report. The locked grounding-rule structure (closed-book framing, quote-before-extract, abstain tokens, scoring rubric) was preserved — only product-name content changed.

---

## [2026-06-23] — Real source list received: prioritized subset locked for prototype

**Decision:** Of the ~50 ecosystem sources in the supervisor's Built Environment doc, only a ~24-source prioritized subset was wired in for a presentation: gov_agencies +IMDA, associations +SGTech/REDAS, customers +Keppel, partners (newly populated) = AECOM/CPG Consultant/Honeywell/Cushman & Wakefield, competitors +FacilityBot/Cryotos (TwinMatrix dropped). Chinese state contractors, NUS/NTU/SGH, GeBIZ, Smart Nation/GovTech, BCI Asia, and Construction Plus Asia left as-is/out of scope for this round.
**Rationale:** Finding a real newsroom/press URL per source (not just the PDF's homepage) is the slow part — same cost Phase 1 already paid. Attempting all ~50 in one session risked discovering scraping failures only at demo time; a smaller fully-verified set is more defensible than a larger, partially-broken one. Sector taxonomy stayed exactly as Phase 1/2 built it. **Both the Chinese-state-contractor exclusion and the TwinMatrix drop were later reversed** — see the 2026-06-26 Phase 4 entry above.

**Decision:** LinkedIn and Facebook source URLs remained out of scope for this round.
**Rationale:** LinkedIn scraping was already ruled out in Phase 1 (anti-bot, no free no-auth method). Facebook carries the same risk profile and wasn't worth researching under the deadline. Still a Phase 4+ candidate if a paid scraping API gets budget.

---

## [2026-06-22] — Phase 2 completion decisions

**Decision:** Google Drive export deferred from the weekly summarizer to Phase 4.
**Rationale:** The supervisor's real source lists (customers, partners, associations, MY/VN/ID) weren't finalized yet; building Drive export before that would mean reworking it once scope locked. The weekly summarizer's core function (compressing daily reports, replacing them in the vector store) was built and verified — only the external push was deferred.

**Decision:** Phase 3 scope expanded to two separate dashboard surfaces.
**Rationale:** Alfonso wants a polished, professional report view for BD/sales plus a separate developer-facing internals page (vector store contents, source scores, feedback digests, run metadata) so anyone maintaining the system can see what's driving output without reading code.

---

## [2026-06-19] — Phase 1 prompt engineering decisions

**Decision:** Grounded prompting pattern for the analyst — closed-book framing, quote-before-extract for opportunities, negative few-shot examples, per-field abstain tokens.
**Rationale:** Llama 3.3 70B fabricated causal links and invented deadlines when given a structured template to fill. Three iterations proved explicit grounding constraints (not just "be accurate") were required. Quality jumped from 13/25 to 21/25.

**Decision:** Content truncated to 800 chars/source in the analyst prompt (down from 2000).
**Rationale:** Groq free tier has a 12k TPM limit; with 18+ sources passing the filter, 2000 chars/source exceeded it. This constraint was lifted once the pipeline switches to Claude Haiku in production (200k context).

**Decision:** LinkedIn scraping deferred from Phase 1.
**Rationale:** All free no-auth approaches were blocked by LinkedIn's anti-bot measures. Not a Phase 1 blocker — revisit when budget for paid options (Apify, PhantomBuster) is available.

---

## [2026-06-19] — AI system design decisions locked

**Decision:** Groq (Llama 3.3 70B) for development/testing; Claude Haiku 3.5 for production.
**Rationale:** Groq's free tier eliminates dev cost. Claude Haiku has better tool-use support for future agent work. Model is a config variable — trivial to swap. Production cost estimate: ~$0.05–0.15/day.

**Decision:** ChromaDB as vector store (local, free).
**Rationale:** No external API/cost; runs on the company server. Switch to Pinecone only if a multi-server architecture is required in Phase 3+.

**Decision:** RAG + context only for Phase 2; no AI agents.
**Rationale:** Agents add per-run cost (multiple LLM calls) and complexity without proportional gain at this scale. Agentic verification (high-scoring opportunities trigger web search) deferred to Phase 3+ once the base system is proven.

**Decision:** Three Phase 2 AI enhancements confirmed: semantic deduplication, named entity extraction, source quality scoring.
**Rationale:** All three add measurable signal-quality improvement with low complexity — dedup reduces cross-source noise, entity extraction improves RAG retrieval, source scoring enables passive learning without extra LLM calls. (Note: all three were later deleted — see the 2026-06-29 "Pipeline optimization pass" entry above — as producing no useful output in practice.)

**Decision:** Hard rate limit on LLM calls per run and per day.
**Rationale:** Safety measure to prevent runaway loops and API abuse from misconfigured cron or feedback pipelines. Pipeline logs a breach and exits cleanly.

**Decision:** Feedback form submissions are aggregated and LLM-summarized before vector-store ingestion.
**Rationale:** Raw submissions are too verbose and varied for clean retrieval. A short consensus digest is more useful analyst context than many individual paragraphs, and prevents context bloat.

**Decision:** Pre-run context injection removed from scope.
**Rationale:** Alfonso confirmed the feedback form already covers this purpose — team feedback on one report becomes context for the next run. No separate injection mechanism needed.

---

## [2026-06] — Project scope expanded: pipeline → AI system

**Decision:** The system is no longer a reporting pipeline — it's a stateful AI market intelligence system with a RAG-based feedback loop that learns and improves over time.
**Rationale:** Supervisor requirements expanded to include sector-based scraping (gov agencies, associations, customers, partners, competitors), an AI brain with persistent context, a feedback form that reweights priorities, weekly summaries, and a proper internal web dashboard.

**Decision:** Sector-based scraper architecture — five sectors: gov_agencies, associations, customers, partners, competitors.
**Rationale:** The supervisor wants intelligence organized by who the signal comes from, not just what topic it covers — each sector has distinct BD relevance.

**Decision:** Daily pipeline cadence, not weekly.
**Rationale:** Supervisor confirmed daily reports are the target cadence (GitHub Actions cron at 09:00 SGT — cron itself never actually configured for daily prod use; app runs locally).

**Decision:** Production hosting on company servers, not Vercel.
**Rationale:** Supervisor confirmed an internal web dashboard on company infrastructure; Vercel was prototype-only. (Never actually provisioned — still runs locally as of the last session.)

**Decision:** Build fully for Singapore first, then expand to MY, VN, ID.
**Rationale:** Avoids premature generalization — the SG system becomes the template; other countries just add sector sources.

**Decision:** RAG-based feedback loop using a vector store.
**Rationale:** User feedback submitted via a form at the end of each daily report must update what the AI prioritizes. Vector store accumulates context; weekly summarization prevents bloat. No fine-tuning — prompt-time retrieval only.

**Decision:** Lightweight context management (CLAUDE.md + a handful of files + `/phase` + `/context-update`) over the GSD framework.
**Rationale:** Solo project, token efficiency is a constraint; GSD overhead wasn't justified at that scale. **Superseded 2026-07-08** by the `.context/` + `/feature-*` workflow this migration establishes — see `.context/OVERVIEW.md`.

---

## [2026-06] — Initial Architecture

**Decision:** Plain Python pipeline (`requests` + BeautifulSoup) over n8n or Firecrawl.
**Rationale:** Free, zero external dependencies for MVP, sufficient for the ~15 target sources. Firecrawl could be added later if JS-heavy sites proved unscrapable with plain requests (later partially superseded — Scrapling was added in 2026-06-29 for exactly this reason, though still not Firecrawl).

**Decision:** GitHub Actions for scheduling over a hosted server or n8n cloud.
**Rationale:** Free, no server to maintain, integrates naturally with the GitHub repo, straightforward cron syntax for a weekly run. (Cadence later changed to daily; GitHub Actions cron never actually finished being wired for production.)

**Decision:** Vercel for report hosting over GitHub Pages.
**Rationale:** Cleaner URL, easier custom-domain migration later, same auto-deploy-from-GitHub workflow, still free. Migration to Alibaba Cloud OSS or company servers planned once the supervisor approved. **Superseded** — production hosting direction changed to company servers (see the 2026-06 "Project scope expanded" entry above), Vercel was prototype-only.

**Decision:** Claude Haiku (not Sonnet/Opus) for `analyst.py`.
**Rationale:** Cost — at ~15-30 articles/week, Haiku costs ~$0.10-0.30/run vs. $1-3 for Sonnet. Upgrade to Sonnet only if report quality proves insufficient. **Superseded for the dev phase** — Groq became the dev/test LLM (see 2026-06-19 above); Claude Haiku remains the intended production model, not yet switched to.

**Decision:** Country-config structure from day one even though only SG is active.
**Rationale:** The supervisor's original brief mentioned SG, MY, ID, VN. Restructuring later would be expensive; one `active: True/False` flag per country costs nothing now.

**Decision:** No database — GitHub repo as storage.
**Rationale:** MVP only; HTML output is ephemeral (regenerated weekly, later daily). No historical querying needed for MVP. Add SQLite or similar if archiving past reports becomes a requirement. (ChromaDB later added for the vector store, but no relational/document DB was ever introduced.)

**Decision:** Gmail SMTP for email delivery.
**Rationale:** Free, no new service sign-up. Alfonso's personal Gmail used for testing; company email to be swapped in for production (never completed — email delivery appears to have been superseded in priority by the web dashboard).
