# Review: 003-vietnam-country

**Result: PASS**

**Base:** 168810eeb12c6e9d5bd257c0b0df9620315d765e
**Reviewed:** branch `feature/003-vietnam-country`, diff `168810e..HEAD` (9 code/config/template files + 8 task files + CONTEXT.md, 2,674 insertions / 83 deletions across 19 files)

## 1. Task-level check

All 8 task files' specs were compared against `git diff 168810e..HEAD` directly (not against the tasks' own Evidence sections). Every task's actual diff matches its spec:

- **001 (VN sources.json)** — new `"Vietnam"/"VN"` country object appended after SG's, with `active`, `sources`, `priority_keywords`, `keywords`. 60 source entries (52 URL-bearing + 8 no-URL `active:false` stubs with `inactive_reason`), matching the spec's 7+6+10+5+2+4+18+8=60 arithmetic. SG block byte-identical (`git diff` shows zero changes inside the SG object; `_domain_tagging_status` untouched).
- **002 (VN scraper verification)** — field-only changes (`active`/`fetcher`/`inactive_reason`) on the 60 entries added by 001; no structural changes, source count unchanged at 60.
- **003 (app.py/main.py country routing)** — `_country_mode()` added mirroring `_domain_mode()`; `report()`/`internals()`/`admin()` updated exactly per spec; `main.py`'s `run_metadata_{country['code']}.json` filename change present. Diff matches the task's prescribed code blocks verbatim.
- **004 (base.html country switcher)** — country-tabs block replaced with real `<a href="/?country=SG&domain=...">`/`<a href="/?country=VN&domain=...">` links; Malaysia/Indonesia remain inert `<span>`s; domain tabs now carry `&country={{ _country }}`; both `{% set %}` lines moved above both blocks. Matches spec's HTML block exactly.
- **005 (admin.html dynamic country select)** — hardcoded single `<option value="SG">` replaced with `{% for c in countries %}` loop, `SG` still default-selected. 4-line diff, nothing else in the form touched.
- **006 (analyst.py SUMMARY_PROMPT interpolation)** — opening sentence changed to `operating in {country_name}`; `_synthesize_summary()` gained `country_name` parameter and does `SUMMARY_PROMPT.replace("{country_name}", country_name)` (not `.format()`, avoiding the JSON-brace collision the task explicitly warned about); call site passes `country["name"]`. Matches spec.
- **007 (company_context.md Vietnam subsection)** — Vietnam content added inside "Key Prospects & Relationships" (before `## Ecosystem Players`) and inside "Ecosystem Players" (before `## BD Priorities`) — confirmed by diff hunks, not just task claim. No other section touched. Vectorstore re-seeded (41 chunks, up from 34).
- **008 (feedback.py/weekly.py country-scoping)** — `aggregate_feedback(country_code=None)`, `consolidate_feedback_digests(max_digests=10, country_code=None)`, `generate_weekly_summary(country_code=None)` all gained the additive parameter with `None`-default backward compatibility; `main.py` moved the feedback calls inside the per-country loop and looped the Sunday weekly-summary call; `app.py`'s `receive_feedback()` reads/validates `country`; `report.html` gained the hidden `country` input. `consolidate_feedback_digests` correctly counts the *filtered* result (`len(ids)`) rather than `collection.count()`, matching the task's explicit correctness requirement. `SUMMARIZE_PROMPT`/`CONSOLIDATION_PROMPT`/`WEEKLY_PROMPT` string constants left untouched per constraint.

No undeclared files touched in any task; no interface drift; no constraint violations found.

## 2. Decision coverage

Every Implementation Decision in CONTEXT.md is reflected in the code, independently re-verified (not trusted from task Evidence sections alone):

- **(a) Feedback/weekly country-scoping fixed now** — confirmed live: `collection.get(where={"country": "VN"})` against `REPORT_HISTORY` returns only VN-tagged throwaway docs (fresh test this pass, cleanup verified). `main.py` calls both functions inside the per-country loop, not once globally.
- **(b) company_context.md Vietnam subsection placement** — confirmed via diff: exactly one `### Vietnam` heading inside "Key Prospects & Relationships," Vietnam bullets appended inside the existing single `## Ecosystem Players` section (not a new top-level heading). "Products by Business Sector," "BD Priorities," "Regulatory" sections show zero diff.
- **(c) Sector-mapping rules applied to all ~60 VN sources** — fresh count this pass: `customers: 32, competitors: 10, gov_agencies: 7, partners: 7, general_news: 4` = 60, matching the category tables in Task 001 exactly (Government Authority→gov_agencies 7, Target Customer→customers 6, Competitor→competitors 10, Dealer/Supplier→partners 5, Facility Management→partners 2, News/Research→general_news 4, generic/existing/potential Customer + no-URL stubs→customers 18+8=26; 6+26=32 customers total).
- **(d) VN keyword lists = SG minus exactly the named terms** — fresh check this pass: `GeBIZ` absent from VN `priority_keywords` (present in SG's 15-item list, VN has 14); `BCA Green Mark`, `Hiverlab`, `Gelement`, `TwinLogic`, `TwinMatrix` all absent from VN `keywords` (all present in SG's 81-item list, VN has 76). No other term added or removed.
- **(e) EDU dual-tagging applied to exactly MOET, Văn Lang University, HUIT** — fresh check this pass: `['Ministry of Education & Training (MOET)', 'HUIT', 'Văn Lang University']` are the only three VN sources with `'EDU'` in their `domain` array; every other VN source has exactly `['GENERAL', 'BER']`. (Note: MOET was separately flipped `active:false` by Task 002 due to a network timeout — its EDU domain tag is untouched and correct; Task 002's scope was explicitly `active`/`fetcher`/`inactive_reason` only, not `domain`.)
- **(f) Branching decision** — fresh check this pass: `git merge-base feature/003-vietnam-country main` == `168810eeb12c6e9d5bd257c0b0df9620315d765e` == `main`'s current HEAD, confirming this feature branches directly from `main`, not from `feature/002-local-llm-backend` (which remains a separate, untouched branch).

## 3. Goal alignment

CONTEXT.md's goal — "Add Vietnam (VN) as a second, fully independent country in the market intelligence pipeline... exercising and completing the `--country` scaffolding" — is satisfied end-to-end, not just at the backend-plumbing level. Live-verified this pass via `app.test_client()`:

- `GET /?country=VN` renders (200) and the response HTML contains a working `href="/?country=VN&domain=..."` link (a real `<a>`, not the old inert `<span>`) — a user can actually click from the dashboard into the Vietnam view.
- The domain tabs on the VN page carry `&country=VN`, so switching domain (BER/EDU/GENERAL) while viewing Vietnam does not silently reset back to SG.
- `GET /internals?country=VN` renders (200), reading the country-scoped `run_metadata_VN.json` path (falls back correctly with no report/metadata yet, without mislabeling SG data as VN's).
- `GET /admin`'s template (rendered with a non-empty `pending` list to exercise the country `<select>`, since it's gated behind `{% if pending %}`) lists both `<option value="SG"` and `<option value="VN"`, SG default-selected.
- `POST /feedback` with `country: "VN"` is written to disk with `"country": "VN"`; an invalid code falls back to `"SG"`.
- The analyst's `SUMMARY_PROMPT` no longer says "Singapore" anywhere and interpolates cleanly for any country name without corrupting the JSON schema block that follows it in the same prompt string.
- The `COMPANY_CONTEXT` ChromaDB collection (41 chunks) contains real Vietnam content ("Vingroup" confirmed present, "SpatioX" confirmed absent).

**Scope check against CONTEXT.md:** every in-scope item is present (VN sources.json block, country-aware routes, country switcher UI, dynamic admin country select, SUMMARY_PROMPT fix, company_context.md VN subsection + reseed, feedback/weekly country-scoping, run_metadata country-scoping, scraper dry-run/fetcher-tiering). Nothing out-of-scope was touched: no analysis-architecture change, no Vietnamese-language keywords added, no MY/ID data introduced, no live `py main.py --country=VN` run performed, `_domain_tagging_status` left untouched.

**`WEEKLY_PROMPT` hardcoded-Singapore flag — verdict: not FAIL-worthy, logged as a follow-up, not a gap in this feature's scope.** Fresh-checked this pass: `pipeline/weekly.py`'s `WEEKLY_PROMPT` (line 11) still reads `"...Silversea Media (digital twin & immersive tech company, Singapore)."` CONTEXT.md's Scope section names only `pipeline/analyst.py`'s `SUMMARY_PROMPT` for the country-hardcoding fix; it never lists `WEEKLY_PROMPT`, `SUMMARIZE_PROMPT`, or `CONSOLIDATION_PROMPT`. Task 008's own Constraints section explicitly required these three constants stay unchanged ("this task is about metadata/filtering plumbing, not prompt content"), and Task 008 correctly complied — this was a deliberate, spec-compliant scope boundary, not an oversight. The functional impact is real but narrow and already country-scoped correctly at the data layer: `generate_weekly_summary(country_code="VN")` now correctly retrieves and compresses only VN-tagged `REPORT_HISTORY` documents (verified fresh this pass), so a VN weekly run would only ever summarize genuine VN daily reports — the LLM's opening self-description would just be factually wrong about which country it's summarizing, a prompt-content quality bug, not a data-scoping/independence bug. This is the same class of issue Task 006 fixed in `SUMMARY_PROMPT`, and should be scoped as a small follow-up task, but treating it as a blocking gap in *this* feature would mean re-litigating a scope boundary CONTEXT.md set deliberately and narrowly. Recommend adding it to `.context/STATE.md`'s Known Bugs list (parallel to the existing "pipeline-polish round" items) for a future feature.

## 4. Evidence gate

**Fresh commands run this pass (not reused from any task's own Evidence section):**

```
$ py -c "import json; json.load(open('config/sources.json', encoding='utf-8')); print('JSON valid')"
JSON valid

$ py -c "from config.sources import load_sources, COUNTRIES; ..."
['SG', 'VN']
sources 60
priority_keywords 14
keywords 76
active 43 inactive 17
```

**AST parse — all 5 touched Python files, fresh this pass:**
```
app.py OK
main.py OK
pipeline/analyst.py OK
pipeline/feedback.py OK
pipeline/weekly.py OK
```

**Flask test-client, live session auth (`session_transaction()` with `authenticated=True`, matching Task 004's precedent for sandboxed password-file access):**
```
GET /?country=VN status: 200
has href country=VN link: True
has href country=SG link: True
GET /internals?country=VN status: 200
GET /?country=SG status: 200
GET /?country=XX status: 200  (falls back to SG active-tab styling, confirmed)
Malaysia/Indonesia: still inert <span>, not <a>
```

**admin.html — rendered directly via `render_template()` with a non-empty `pending` list** (the country `<select>` lives inside `{% if pending %}`, so an empty list, as literally suggested by the review brief, renders zero HTML for it — used a one-entry fake `pending` list instead to actually exercise the block):
```
has value="SG" option: True
has value="VN" option: True
selected options: ['SG']
```

**SUMMARY_PROMPT interpolation — re-run fresh, not reused from Task 006's Evidence:**
```
$ py -c "from pipeline.analyst import SUMMARY_PROMPT; assert 'Singapore' not in SUMMARY_PROMPT; ...; assert '\"strategic_fit\": 0' in vn_prompt; print('OK')"
OK
```

**ChromaDB COMPANY_CONTEXT collection — checked directly, fresh this pass:**
```
total chunks: 41
Vingroup present: True
SpatioX present (should be False): False
```

**ChromaDB `where`-filter mechanics — fresh live test against REPORT_HISTORY, throwaway docs cleaned up after:**
```
add_documents(REPORT_HISTORY, ['throwaway SG doc','throwaway VN doc'], metadatas=[{country:SG},{country:VN}], ids=[...])
col.get(where={'country':'VN'}) -> ['throwaway VN doc']  # only the VN doc returned
delete_documents(...) -> cleanup confirmed, 0 remaining
```

**`/feedback` country field — fresh POST via test client, cleaned up after:**
```
POST /feedback {report_date, country: "VN", relevance_rating: 3} -> 200
written file's "country" field: "VN"
test artifact deleted
```

**Branching — fresh check:**
```
$ git merge-base feature/003-vietnam-country main
168810eeb12c6e9d5bd257c0b0df9620315d765e   # == main's HEAD == CONTEXT.md's Base
```

**Working tree left clean** (`git status --short` empty) after all verification — no stray files, no leftover ChromaDB throwaway docs, no leftover feedback/report_metadata test artifacts.

All evidence gates pass. Per CLAUDE.md's LLM-quota policy and CONTEXT.md's explicit out-of-scope item, **no `py main.py --country=VN` end-to-end run was performed** — this remains an open, Alfonso-owned manual checkpoint (same treatment as Feature 001's still-open SG checkpoint), not a review-blocking gate.

## Findings

No discrepancies found between task specs, CONTEXT.md's Implementation Decisions, and the actual code. No scope creep in either direction (nothing in-scope silently skipped, nothing out-of-scope accidentally touched).

One item logged as an open follow-up, not a defect in this feature: `pipeline/weekly.py`'s `WEEKLY_PROMPT` constant still hardcodes "Singapore" in its system framing. This was correctly out of Task 008's scope (its constraints explicitly preserved all three prompt constants verbatim) and was never listed in CONTEXT.md's Scope section for this feature — CONTEXT.md named only `SUMMARY_PROMPT`. The data-layer country-scoping fix (Task 008) means a VN weekly summary would still only ever compress genuine VN daily reports; the gap is that the LLM's self-description of what it's summarizing would say "Singapore" regardless of which country's reports it's actually compressing. Recommend a small follow-up feature/task (mirroring Task 006's `str.replace()` pattern) rather than reopening this feature's scope.

## Open manual checkpoints (not blocking, Alfonso-owned)

1. Fresh `py main.py --country=VN --domain=BER` run — quota-gated, first real end-to-end exercise of the VN pipeline against live Groq calls and live VN source scraping in combination.
2. Real-browser visual QA of the new country-tab styling (`templates/base.html`) — code-level Jinja/Tailwind-class correctness was verified this pass; pixel rendering needs eyes (same category as Feature 001's still-open `login.html`/`admin.html`/PDF-print checkpoints).
3. `pipeline/weekly.py`'s `WEEKLY_PROMPT` Singapore-hardcoding (see Findings above) — small, well-understood follow-up, not blocking this feature's PASS.
