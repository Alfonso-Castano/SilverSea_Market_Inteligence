# Review: 001-round2-remediation

**Result: PASS**

**Base:** 3dc471a831f05cb7955be8b22c205895976e0f84
**Reviewed:** branch `feature/001-round2-remediation`, diff `3dc471a..HEAD` (10 code/config files + 8 task files + CONTEXT.md/RESEARCH.md)

## 1. Task-level check

All 8 task files' specs were compared line-by-line against `git diff 3dc471a..HEAD`. Every task's actual diff matches its spec exactly — no undeclared files touched, no interface drift, no constraint violations found:

- **001 (auth bypass + /feedback hardening)** — `app.py`: `hmac.compare_digest` used for both admin/viewer login comparisons, empty `ADMIN_PASSWORD` checked before comparison; submitter sanitized via whitelist regex; `relevance_rating` wrapped in try/except returning 400 JSON; CORS scoped to `request.path == "/feedback"`. Matches spec verbatim.
- **002 (PDF afterprint fix)** — `static/animations.js`: switched to an `excludedByUs` tracking array (the "track only what we toggled" option CONTEXT.md offered as the cleaner alternative), restore handler now only un-excludes those elements. `#pdf-export-panel` no longer loses its own exclusion class.
- **003 (company_context.md rebuild)** — all three named sections (Target Sectors, Key Prospects, Ecosystem Players) rewritten per the naming map; "Products by Business Sector" section untouched; zero `spatiox` matches remain (verified independently below).
- **004 (analyst.py prompt/post-processing rebuild)** — `SUMMARY_PROMPT`'s product list, opportunities gate keywords, `product_fit` instruction, `_generate_implications`, and `_derive_competition_risks` all rebuilt around the real catalog with EDU terms added alongside BER terms. Gate stayed keyword-only (no ecosystem-entity path reinstated, per the out-of-scope list).
- **005 (EDU keywords + dual-tagging)** — 10 EDU terms appended to the shared `keywords` list (not `priority_keywords`); NUS/NTU domain changed to `["BER","EDU"]`; no other source touched; JSON still valid, source count unchanged at 62.
- **006 (vectorstore reseed)** — no code changed (run-only task); independently re-verified below that the live ChromaDB `COMPANY_CONTEXT` collection actually reflects the post-rebuild content.
- **007 (admin country selector + approve() disk-reread)** — `config/sources.py` gained `load_sources()`; `pipeline/source_suggestions.py`'s `approve()` now calls it instead of the stale `COUNTRIES` singleton; `templates/admin.html` has a hardcoded SG `<select>`; `app.py`'s `approve_source()` reads `country` from the form. Scoped exactly to `admin()`/`approve_source()` — `login()`/`receive_feedback()`/`add_cors()` untouched (task 001's territory respected).
- **008 (test_clamp.py)** — `tests/test_clamp.py` + `tests/__init__.py` added, covering out-of-range, negative/non-numeric, missing-dims, missing-scores-key, bogus-total-score-override, and multi-opportunity-independence cases against `_clamp_opportunity_scores`/`_SCORE_DIMENSIONS`, both of which pre-existed in `pipeline/analyst.py`.

## 2. Decision coverage

Every Implementation Decision in CONTEXT.md is reflected in the code:

- Auth bypass fix (refuse-before-compare + `hmac.compare_digest`) — present, live-verified.
- PDF afterprint fix — present, using the "track only what we toggled" variant.
- SpatioX naming map (Ops→Smart Facility Management System, Audit→Smart Virtual Inspection, Twin→Digital Twin, Walk→3D/VR Virtual Tour) — applied consistently across `company_context.md` and `analyst.py`.
- EDU stopgap sourcing (dual-tag NUS/NTU only) — present, no over-tagging.
- Filter keywords added to shared list, not a per-domain schema — present.
- Country-scoping of weekly/feedback writes — correctly left untouched (deferred).
- Opportunities gate — keyword-only widening confirmed; no ecosystem-entity path reinstated.
- Admin approval fixes bundled (country selector + disk-reread) in one task, same file area — present.
- Test scope — matches exactly (clamp-only, the 6 specified cases).
- `/feedback` hardening folded into task 001 alongside the auth fix — present.

## 3. Goal alignment

The feature's stated goal — fix the auth bypass, un-break the dashboard's root causes, and finish the SpatioX→real-catalog rebuild consistently — is satisfied as a whole. The auth bypass is closed and live-verified. The SpatioX rebuild is now consistent end-to-end: `company_context.md` (all 4 sections), `pipeline/analyst.py`'s prompt/gate/product_fit/post-processing, and the re-seeded ChromaDB collection all agree on the real catalog with zero `SpatioX` references left in either file this feature touched. `/feedback` hardening and the admin approve() staleness bug are both fixed. Nothing in the "explicitly out of scope" list was touched: `pipeline/weekly.py`, `pipeline/feedback.py`, `main.py`, `templates/report.html`, `templates/login.html`, and `scripts/` all show zero diff from base.

## 4. Evidence gate

**Test suite — run fresh this pass:**

```
$ py -m pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0
collected 6 items

tests/test_clamp.py::test_out_of_range_dimensions_are_clamped PASSED     [ 16%]
tests/test_clamp.py::test_negative_and_non_numeric_values_default_to_one PASSED [ 33%]
tests/test_clamp.py::test_missing_dimensions_default_to_one PASSED       [ 50%]
tests/test_clamp.py::test_missing_scores_key_entirely_defaults_all_to_one PASSED [ 66%]
tests/test_clamp.py::test_llm_supplied_bogus_total_score_is_overridden PASSED [ 83%]
tests/test_clamp.py::test_multiple_opportunities_are_each_clamped_independently PASSED [100%]

============================= 6 passed in 11.02s ==============================
```
Exit code 0.

**Spot-check — SpatioX residue:**
```
$ grep -rn -i spatiox pipeline/ data/company_context.md
(no output — zero matches)
```

**Spot-check — clean imports:**
```
$ py -c "import app; print('app OK')"
app OK

$ py -c "import pipeline.analyst; print('analyst OK')"
(HF Hub warning + weight-loading progress bar — pre-existing sentence-transformers behavior, not introduced by this feature)
analyst OK
```

**Independent live re-verification (not just trusting task 001's Evidence section)** — via `app.test_client()` with `ADMIN_PASSWORD` unset:
- Empty admin password POST to `/login` → HTTP 200, no redirect (`Location` header absent) — bypass closed.
- `/feedback` with `relevance_rating=not_a_number` → HTTP 400, `{"error": "relevance_rating must be a number"}`.
- `GET /` → no `Access-Control-Allow-Origin` header. `POST /feedback` → `Access-Control-Allow-Origin: *`.
- `/feedback` with `submitter=../../escape` → written as `..._______escape.json` inside `data/feedback/`, no path traversal. Test artifacts deleted after verification.

**Independent live re-verification of task 006's reseed claim** (this data isn't in the git diff since ChromaDB's store is untracked):
```
$ py -c "
from pipeline.vectorstore import get_collection, COMPANY_CONTEXT
col = get_collection(COMPANY_CONTEXT)
docs = col.get(limit=200, include=['documents']).get('documents', [])
print(len(docs), 'chunks'); print('any SpatioX:', any('SpatioX' in d for d in docs))
"
34 chunks
any SpatioX: False
```

**Spot-check — sources.json integrity:**
```
$ py -c "... edtech/e-learning/LMS/virtual campus present, NUS/NTU -> ['BER','EDU'], source count 62"
['edtech', 'e-learning', 'LMS', 'virtual campus']
['BER', 'EDU'] ['BER', 'EDU']
62
```

All evidence gates pass. No `py main.py` run was performed (correctly out of scope — Alfonso-owned manual checkpoint per CONTEXT.md).

## Findings

None. No discrepancies found between task specs, CONTEXT.md decisions, and the actual code. No scope creep in either direction.
