# Review: 004-malaysia-country

**Result: PASS**

**Base:** 168810eeb12c6e9d5bd257c0b0df9620315d765e
**Reviewed:** branch `feature/004-malaysia-country`, diff `168810e..HEAD` (3 code/config files + 4 task files + CONTEXT.md)

## 1. Task-level check

All 4 task files' specs were compared against `git diff 168810e..HEAD`. Every task's actual diff matches its spec — no undeclared files touched, no interface drift, no constraint violations found:

- **001 (MY sources.json block)** — `config/sources.json` gained a second `countries` entry, `"MY"`, 55 sources, `priority_keywords` (15) and `keywords` (99). Verified fresh: JSON valid, `load_sources()` returns `['SG', 'MY']`, SG's 62 sources untouched (numstat confirms `config/sources.json` is 735 insertions / 0 deletions relative to base — a pure append, nothing in the pre-existing SG block or `_domain_tagging_status` was touched).
- **002 (MY scraper dry-run verification)** — field-level-only changes on top of Task 001's 55 objects: 50 default-active, 2 `fetcher: "stealth"` (Air Selangor, Panasonic Appliances Marketing Asia Pacific), 0 dynamic, 3 newly `active: false` with descriptive `inactive_reason`s (U Learning, Art Network Events, Unbound Malaysia — all JS-SPA-shell failures, not URL/mapping errors). Source count stayed 55; SG untouched. (The task's own recorded "8 insertions/3 deletions" evidence is a diff against Task 001's commit, not against base — consistent with the cumulative base→HEAD diff showing 735 pure insertions, since none of Task 001's originally-inserted lines survive as a separate "delete" once diffed straight from base.)
- **003 (base.html country tabs)** — diff shows SG flipped from static `<span>` to `<a href="/?country=SG&domain={{ _domain }}">`, MY and VN added as real links with identical structure, Indonesia left as an inert `<span>`. The `{% set _country %}`/`{% set _domain %}` pair was correctly hoisted above both tab blocks (previously `_domain` was set only above the domain-tabs block). Domain tabs gained `&country={{ _country }}`. This reproduces Vietnam's not-yet-merged fix from scratch on this pre-VN-fix branch, exactly as instructed — confirmed live (see Evidence gate §7).
- **004 (company_context.md Malaysia subsection + reseed)** — new `### Malaysia` subsection under "Key Prospects & Relationships" (one occurrence, correctly positioned before `## Ecosystem Players`), and a Malaysia block appended inside "Ecosystem Players" before `## BD Priorities`. "Competitive Positioning," "Products by Business Sector," "Target Sectors & Use Cases," "BD Priorities," and "Regulatory & Certification Note" are untouched (diff shows exactly two hunks, both inside "Key Prospects & Relationships" and "Ecosystem Players"). `scripts/seed_vectorstore.py` was run, not modified.

## 2. Decision coverage

Every Implementation Decision in CONTEXT.md is reflected in the code, with the domain-scope boundary checked with extra care per the dispatch brief:

- **Domain-scope decision (the one genuinely blocking call)** — `_domain_mode()` (lives in `app.py`), `pipeline/analyst.py`'s `SUMMARY_PROMPT`, `app.py`, `main.py`, `templates/admin.html`, `pipeline/feedback.py`, `pipeline/weekly.py` all show **zero diff** from base — confirmed individually via `git diff 168810e..HEAD --stat -- <file>` for each, all empty. Zero Python files were touched anywhere in this feature's diff (confirmed via `--stat -- '*.py'`, empty output) — the entire feature is JSON/Markdown/HTML.
- **Every MY source tagged `GENERAL` + real domain** — confirmed programmatically for all 55 (not sampled): `all('GENERAL' in s['domain'] for s in my['sources'])` → `True`, zero missing. Non-GENERAL domain breakdown: BER 17, RCC 13, PSS 13, HLS 4, CTE 3, EDU 3, MFG 2 (sums to 55), matching CONTEXT.md's stated breakdown exactly.
- **Sector mapping** — fresh `Counter` over all 55 MY sources: `gov_agencies: 7, associations: 3, customers: 26, partners: 10, competitors: 8, general_news: 1` — exact match.
- **`templates/base.html` shows SG, MY, AND VN as real links** — live-rendered `/` response (authenticated test-client session) contains `href="/?country=SG&domain=`, `href="/?country=MY&domain=`, and `href="/?country=VN&domain=` — all three are `<a>` tags, not `<span>`s. Indonesia confirmed still a plain `<span class="...cursor-not-allowed">` with no `country=ID` anywhere in the response. This correctly reproduces Vietnam's not-yet-merged fix on this pre-VN-fix branch rather than only adding Malaysia.
- **MY `priority_keywords`/`keywords`** — `priority_keywords` is byte-identical to SG's 15-item list (`sg['priority_keywords'] == my['priority_keywords']` → `True`) — MY does NOT strip anything, unlike Vietnam. `keywords`: MY's first 81 entries are identical to SG's full 81-item list (`my_kw[:81] == sg_kw` → `True`), followed by exactly 18 new cross-sector terms (`virtual showroom` … `water utilities`), for 99 total. Matches CONTEXT.md's decision precisely.
- **`company_context.md`'s Malaysia subsection covers full business breadth** — confirmed both in the Markdown (RCC entities like Ricoh/Panasonic/Sharp, HLS entities like Avisena/IHH Healthcare, MFG entities like Perodua/Daikin, CTE entities like Ezytap/Sunway's Umrah-Hajj AR, PSS entities like MDEC/Think City/JPJ) and independently in the **re-seeded live ChromaDB collection** — spot-checked "Ricoh" (RCC), "Avisena" (HLS), "Perodua" (MFG), "Ezytap" (CTE), "Think City" (PSS) all present in the 46 retrieved chunks, not just BER/EDU-flavored content.
- **Source count 55** — confirmed, not 61 (the submission's blank rows 56-61 correctly excluded).

## 3. Goal alignment

The feature's stated goal — add Malaysia as a third, fully independent country, reusing Vietnam's now-generic country-scoping infrastructure, while preserving MY's full real business-domain breadth in the data even though only BER/EDU/GENERAL are active pipeline domains this round — is satisfied. All in-scope items from CONTEXT.md's Scope section are present: the 55-source MY country block with correct sector/domain tagging, the base.html tab flip (reproducing Vietnam's fix on this branch), the company_context.md Malaysia subsections with full business breadth, and the scraper dry-run verification. Nothing in the explicitly-out-of-scope list was touched: RCC/HLS/MFG/CTE/PSS were not activated as first-class pipeline domains, no analysis-architecture/scoring/RAG changes were made, `app.py`/`main.py`/`admin.html`/`feedback.py`/`weekly.py` are all confirmed untouched, and no `py main.py` end-to-end run was performed (correctly deferred as Alfonso's manual checkpoint).

The known, deliberate limitation — `app.py` does not read `?country=` on this branch, so `current_country` always defaults to `'SG'` even after clicking the MY/VN tab — is real (confirmed: `report()` in `app.py` calls `render_template("report.html", ...)` with no `current_country` argument anywhere, and `domain_filename` is hardcoded to `f"latest_report_SG_{domain}.json"`). Task 003 correctly worked around this by verifying template correctness (links present, `&country=SG` on domain tabs, correct active-tab styling) rather than claiming end-to-end country-switching, which is genuinely untestable on this branch alone. This is documented in Task 003 and is not silently glossed over.

## 4. Evidence gate — fresh commands run this pass

**1-2. JSON validity + MY/SG source counts:**
```
$ py -c "import json; json.load(open('config/sources.json', encoding='utf-8')); print('VALID JSON')"
VALID JSON

$ py -c "from config.sources import load_sources; ..."
countries: ['SG', 'MY']
SG sources: 62
MY sources: 55 priority_keywords: 15 keywords: 99
```

**3. Sector counts + GENERAL tagging, all 55 (not sampled):**
```
Sector counts: Counter({'customers': 26, 'partners': 10, 'competitors': 8, 'gov_agencies': 7, 'associations': 3, 'general_news': 1})
All GENERAL tagged: True
Missing GENERAL: []
Domain breakdown (non-GENERAL): Counter({'BER': 17, 'PSS': 13, 'RCC': 13, 'HLS': 4, 'CTE': 3, 'EDU': 3, 'MFG': 2})
```

**4. Keyword lengths + reuse-verbatim check:**
```
SG priority_keywords == MY priority_keywords: True (15 items)
SG keywords all present in MY (prefix match): True (81 items)
Extra appended count: 18
```

**5. Zero Python files touched:**
```
$ git diff 168810e..HEAD --stat -- '*.py'
(no output)
$ for f in app.py main.py templates/admin.html pipeline/feedback.py pipeline/weekly.py pipeline/analyst.py; do git diff 168810e..HEAD --stat -- "$f"; done
(all empty)
```

**6. Full file-list check:**
```
$ git diff 168810e..HEAD --stat -- . ':!.context'
 config/sources.json     | 735 +++++++++...
 data/company_context.md |  85 +++...
 templates/base.html     |  32 +-
 3 files changed, 841 insertions(+), 11 deletions(-)
```
Exactly the three expected files (plus `.context/features/004-malaysia-country/` task files and CONTEXT.md, not code).

**7. Flask test client, authenticated session, live-rendered `/`, `/internals`, `/login`:**
```
/ status: 200
has SG link: True
has MY link: True
has VN link: True
Indonesia as link (should be False): False
domain tabs have &country=SG: True
SG block active (text-white): True
MY block inactive (text-gray-500): True
Indonesia surrounding: ...<span ... cursor-not-allowed...>Indonesia</span>
/internals status: 200
/login status: 200
```
(First unauthenticated attempt correctly 302-redirected to `/login` per Feature 001's auth gate — expected behavior, not a bug; re-ran with an authenticated session.)

**8. company_context.md structure + live ChromaDB reseed content:**
```
### Malaysia count: 1
## Ecosystem Players count: 1
SpatioX present: False
Malaysia — main partners position: inside Ecosystem Players (True)
Malaysia — competitors to watch position: inside Ecosystem Players (True)

$ py -c "from pipeline.vectorstore import get_collection, COMPANY_CONTEXT; ..."
total chunks: 46
Sunway present: True
MDEC present: True (PSS)
Ricoh present: True (RCC)
Avisena present: True (HLS)
Perodua present: True (MFG)
Ezytap present: True (CTE)
Think City present: True (PSS)
```

**Repo test suite (unaffected by this feature, run to confirm nothing broke):**
```
$ py -m pytest tests/ -v
============================= test session starts =============================
collected 6 items
tests/test_clamp.py::test_out_of_range_dimensions_are_clamped PASSED     [ 16%]
tests/test_clamp.py::test_negative_and_non_numeric_values_default_to_one PASSED [ 33%]
tests/test_clamp.py::test_missing_dimensions_default_to_one PASSED       [ 50%]
tests/test_clamp.py::test_missing_scores_key_entirely_defaults_all_to_one PASSED [ 66%]
tests/test_clamp.py::test_llm_supplied_bogus_total_score_is_overridden PASSED [ 83%]
tests/test_clamp.py::test_multiple_opportunities_are_each_clamped_independently PASSED [100%]
============================= 6 passed in 11.38s ==============================
```

**9. No `py main.py` run was performed** — per CLAUDE.md's LLM-quota policy and CONTEXT.md's explicit scope exclusion, a live `main.py --country=MY --domain=BER`/`--domain=GENERAL` end-to-end run stays an Alfonso-owned manual checkpoint, same treatment as SG's and VN's still-open checkpoints. Not run in this review pass.

All evidence gates pass.

## Findings

None. No discrepancies found between task specs, CONTEXT.md decisions, and the actual code. No scope creep in either direction — the domain-scope boundary (the feature's one genuinely sensitive constraint) held exactly as specified, verified both by empty diffs on every named file and by zero Python files touched anywhere in the feature.

## Carry-forward note for `/feature-verify`'s post-PASS context refresh

CONTEXT.md's Open Questions section explicitly asks that the following be carried into `.context/STATE.md`'s Known Bugs/Next Action and `.context/DECISIONS.md` once this feature passes review (not this reviewer's job to edit those files, but flagging so the refresh step doesn't drop it):

- **Full 7-domain activation (RCC/HLS/MFG/CTE/PSS) is the confirmed next step**, applying retroactively to Vietnam's sources too (also currently BER/EDU/GENERAL-tagged only).
- MY's cross-sector keyword additions are unverified against a live pipeline run — whether they surface a reasonable signal count from MY's non-BER sources is an open question for Alfonso's eventual manual checkpoint.
- The signals-visible-but-opportunities-gated asymmetry (broadened filter keywords surface MY's non-BER signals, but `SUMMARY_PROMPT`'s opportunities gate stays BER/EDU-only) should be visible to Alfonso during dashboard review, not silently absorbed.
