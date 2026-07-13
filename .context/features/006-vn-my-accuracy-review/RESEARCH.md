# Research: VN/MY Accuracy & Code-Correctness Review

`--thorough` was passed, so this research pass ran before task decomposition. Findings below directly
shaped the task list — each section states what was confirmed and how it changed the plan.

## 1. Shape of the two generated report JSONs

Both `data/latest_report_VN_BER.json` (460 lines) and `data/latest_report_MY_GENERAL.json` (270 lines)
share one schema (top-level keys): `executive_summary` (list[str]), `signals_by_sector` (dict of
sector-label → list of signal objects), `opportunities` (list of opportunity objects),
`synthesis` (list[str]), `competition_risks` (list), `data_sources` (list), `_metadata` (dict).

**Signal object:** `{entity, signal, source_name, implication}` — `implication` is Python-generated
(`_generate_implications()` in `pipeline/analyst.py`, zero LLM cost, sector-keyed fallback strings), the
rest come from the `SECTOR_SYNTHESIS_PROMPT` LLM call.

**Opportunity object:** `{title, source_quote, named_entry_point, concrete_action, deadline, source_name,
product_fit, scores{5 dims}, total_score}` — all LLM-generated except `total_score`/`scores`, which are
server-clamped by `_clamp_opportunity_scores()`.

**`data_sources` entry:** `{name, url, sector}` — this is the *only* place a real fetchable URL survives
into the report; it's built in `main.py` from `filtered` scrape results (`report_data["data_sources"] =
[{"name": r["name"], "url": r["url"], "sector": r["sector"]} for r in filtered]`), not by the LLM.

**`_metadata`:** `{country, date, date_display}` — no `domain` key (see §4 below — domain isn't threaded
through `analyse()` at all).

VN report: 4 sectors present (Competitors 7, Partners 22, General News 1, Customers 13 = 43 signals),
3 opportunities, 15 `data_sources`. MY report: 5 sectors (Government & Agencies 3, Industry Associations 1,
Customers 2, Partners 2, Competitors 1 = 9 signals), 3 opportunities, 25 `data_sources`.

## 2. Critical finding: `source_name` is broken for most VN signals — changes the audit's approach

Cross-referencing every signal/opportunity `source_name` against `data_sources` names:

- **VN report:** every signal's `source_name` is one of only 3 values: `"Extracted signals"` (most),
  `"extracted signals"` (a lowercase variant — same underlying defect, inconsistently cased by the LLM),
  or `"Vietnam Investment Review"` (one real source name, for the single General News signal). **None
  of the 43 VN signals' `source_name` values match a real source name except that one.** All 3
  opportunities also carry `source_name: "Extracted signals"`.
- **MY report:** mostly real source names (`National Art Gallery`, `GreenRE`, `TA Global`, etc.), but 4
  signals carry non-source values: `"Extracted signals"`, `"Balai Seni Negara"` (Malay for "National Art
  Gallery" — a real entity but not the *configured* source name, so still a lookup miss), `"source not
  specified"`, `"source text"`. All 3 MY opportunities *do* have real matching `source_name`s.

**Root cause, confirmed by reading `pipeline/analyst.py`:** `_synthesize_sector()` (line 174) builds its
user message as `f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"` — the literal string
`"Extracted signals:"` sits immediately before the actual extraction text. `SECTOR_SYNTHESIS_PROMPT`
asks the model to emit `"source_name": "name of source"` per entry, but the *only* clearly-delimited
source-name markers in `extraction_text` are whatever the extraction-phase model chose to write for
"Format as a flat list grouped by source name" (`SECTOR_EXTRACT_PROMPT` line 44 — no enforced format like
`### {name}`, unlike the extraction call's own *input* construction at line 151, which the synthesis
step never sees). The synthesis-phase model appears to sometimes grab the literal label text
("Extracted signals") instead of parsing out the real per-source heading, especially when a sector's
extraction text mixes multiple sources' signals without a rigid per-signal source tag. This is a real,
live-observed pipeline defect, not a hypothetical — it directly undermines the report's "opportunity
must carry the `source_name` of the specific signal it was extracted from... copy it verbatim" grounding
claim (`SUMMARY_PROMPT` line 75) for the VN report specifically.

**Practical consequence for the audit tasks:** `source_name` cannot be used as the join key to figure out
which live source a VN signal should be checked against. The audit tasks are instructed instead to match
by **`entity` name against `data_sources`** where `source_name` is broken (e.g. the "Becamex IDC" signal's
`entity` is "Becamex IDC", which *is* a real `data_sources` entry) — this works for single-entity
narrative signals but not for signals about a third party mentioned by one of the tracked sources. This
is called out explicitly in Task 003/004 and is itself a CODE-REVIEW.md finding (root cause explanation
lives there; the ACCURACY-AUDIT.md documents the downstream symptom/impact on verifiability).

One dead end ruled out during this research: a sample VN implication string appeared to contain a
replacement character (`�`) when inspected via one ad hoc `py -c` printout — this turned out to be a
Windows console codepage artifact of that inspection method, not a real defect. Verified by reading the
raw bytes directly (`\xe2\x80\x94`, correct UTF-8 em dash) and via `Grep`, which rendered it correctly.
**Not a finding** — noted here so task executors don't waste time re-chasing it.

## 3. Filter gate vs. SUMMARY_PROMPT opportunities gate — confirmed real divergence

`pipeline/filter.py`'s `score_relevance()` uses **per-country** `priority_keywords`/`keywords` lists from
`config/sources.json` (VN: 14 priority + 76 general; MY: 15 priority + 99 general — both include many
entity names and domain-specific terms like `sustainability`, `IoT`, `smart nation`, `CMMS`, etc. that
never appear in the LLM-facing gate).

`SUMMARY_PROMPT`'s OPPORTUNITIES gate (`pipeline/analyst.py` line 75) is a single **hardcoded, global**
keyword list embedded in the prompt string, applied identically regardless of country or domain. Commit
`aea7783` (feature/005-domain-activation) deliberately broadened it by "reusing the same vocabulary
already established in Malaysia's `sources.json` keywords list" — i.e. the intent was explicit alignment
with MY's config list, but the implementation is still one static list shared by every
country/domain combination, not sourced from config. Confirmed divergence: filter.py's VN list has no
retail/healthcare/tourism/manufacturing terms (correctly, since VN's active report is BER-only), but
`SUMMARY_PROMPT`'s gate now includes `retail chain`, `healthcare`, `hospital`, `manufacturing`, `factory`,
`tourism`, `heritage trail`, `smart city` unconditionally — terms that would only make sense for
non-BER domains.

**Practical impact is currently narrow, not zero:** `main.py`'s `run_pipeline()` already domain-filters
which *sources* get scraped before anything reaches `analyse()`
(`sources = [s for s in sources if domain_arg in s.get("domain", ["GENERAL"])]`), so a VN/BER run's raw
material is already BER-scoped in practice — this is why lead 3 (below) speculated the LLM "guesses
right by construction." But VN has 2 sources dual-tagged `["BER","EDU"]`, meaning EDU-relevant signals
from *those* sources can legitimately reach a BER run's `analyse()` call, and the SUMMARY_PROMPT gate
(which already contains EDU terms like `virtual campus`, `STEM lab`, `e-learning`) would let them through
into a report labeled BER. This is a real, if narrow, cross-domain leak. Verdict for the plan: this
doesn't need re-fetching or its own audit task — it's folded into the code-correctness review's existing
file set (`pipeline/analyst.py`, `pipeline/filter.py`, `main.py` all already in scope there).

## 4. Leads 3, 4, 5 — current-code status confirmed

- **Lead 3 (confirmed, unchanged from CONTEXT.md):** `analyse(filtered_results: list, country: dict)`
  (`pipeline/analyst.py` line 339) takes no `domain` parameter. `main.py`'s `run_pipeline()` calls
  `analyse(filtered, country)` (line 71) with `domain_arg` in scope but never passed. The RAG
  `REPORT_HISTORY` write in `analyse()` also only tags `{"date": ..., "country": country["code"]}` — no
  domain — so `_build_rag_context()`'s past-report-themes retrieval (when called) cannot be domain-scoped
  even if it wanted to be. This is architecturally deeper than a one-line fix (touches prompt content,
  RAG metadata schema, and call sites) — flagged in CODE-REVIEW.md, **not** given a fix task.
- **Lead 4 (confirmed):** `pipeline/weekly.py`'s `WEEKLY_PROMPT` (line 10-11) hardcodes
  `"Silversea Media (digital twin & immersive tech company, Singapore)"` verbatim, even though
  `generate_weekly_summary(country_code: str = None)` already accepts and uses `country_code` for
  ChromaDB `where`-filtering and metadata tagging. Unlike lead 3, this **is** a small mechanical fix:
  `main.py`'s call site (`generate_weekly_summary(country_code=country["code"])`, line 105) already has
  the full `country` dict (with `country["name"]`) in scope, and `pipeline/analyst.py`'s `SUMMARY_PROMPT`
  already demonstrates the exact pattern to copy (`{country_name}` placeholder +
  `.replace("{country_name}", country_name)`, added in commit `b10537d` for the identical bug found on
  the daily-report path). Given a fix task (Task 009).
- **Lead 5 (confirmed):** `pipeline/analyst.py` line 341: `Groq(api_key=os.environ["GROQ_API_KEY"])` —
  raises `KeyError` immediately if unset, before any of the three call sites' own `try/except Exception`
  blocks (which already degrade gracefully — `_extract_sector` returns a fallback string,
  `_synthesize_sector` returns `[]`, `_synthesize_summary` returns an empty summary dict) get a chance to
  run. `pipeline/feedback.py` and `pipeline/weekly.py` both use `os.environ.get("GROQ_API_KEY", "")` and
  check `if not client.api_key:` before making a call. Confirmed this is a genuinely small, low-risk,
  one-line fix (`os.environ["GROQ_API_KEY"]` → `os.environ.get("GROQ_API_KEY", "")`) — the existing
  per-call-site exception handling already provides the same graceful-degradation behavior once the
  constructor itself stops raising. Given a fix task (Task 008). Note: this fix does *not* attempt to add
  an explicit "skipped — no GROQ_API_KEY" print like `feedback.py`/`weekly.py` have, because doing so
  would require `main.py` changes too (checking `analyse()`'s return value before proceeding to save a
  report) — that's a judgment call about desired pipeline behavior on missing key, out of scope for a
  mechanical fix task, and is noted as a residual gap in CODE-REVIEW.md instead.
- **Lead 2 (already confirmed in CONTEXT.md, re-verified):** `app.py`'s `report()` fallback check (now at
  line ~108-111 in this worktree) still hardcodes `for d in ("BER", "EDU", "GENERAL")` while
  `_domain_mode()` (line 81-83) validates all 8 (`EDU, BER, GENERAL, RCC, HLS, MFG, CTE, PSS`).
  Confirmed via `git show bb6fbd3` (feature/005-domain-activation, "expand `_domain_mode()` to validate
  all 8 business domains") that this commit updated `_domain_mode()` but never touched the fallback
  tuple three lines away — this is the introducing commit, useful context for CODE-REVIEW.md's git-history
  section. Small, one-line, mechanical fix — given a fix task (Task 007).

## 5. Re-fetch scoping — targeted, not exhaustive

VN has 60 configured sources (43 active), MY has 55 (52 active) — but only sources that actually appear
in each report's `data_sources` array were cited as material the LLM saw for that specific report: **15
for VN, 25 for MY** (both lists, with exact URLs, `sector`, and `fetcher` tier, extracted from
`config/sources.json` and embedded directly in Tasks 001/002 below). Re-fetching the full ~95 active
VN+MY sources would mean auditing content the two existing reports never drew from — not useful for a
grounding check scoped to "does *this* report's content hold up." Targeted re-fetch of only the 40 cited
sources is the sampling strategy used, per CONTEXT.md's Open Questions deferring this call to the
planner.

Caveat baked into Task 003/004: most cited URLs are **homepages**, not the specific press-release/news
URL the original scrape may have captured a signal from (no raw scrape cache survives — see CONTEXT.md).
A live homepage re-fetch that doesn't mention a claimed signal is suggestive but not proof of
hallucination (the page may have simply moved on); a re-fetch that actively contradicts a claim, or where
the entity/domain is entirely unrelated to what's claimed, is much stronger signal. The audit tasks are
written to weight these differently rather than flagging every non-match as a hallucination.

## 6. Git history sampling scope for the code-correctness review

Full commit list across the three shipped features (`feature/003-vietnam-country`,
`feature/004-malaysia-country`, `feature/005-domain-activation`), oldest first:

```
86daa43 docs: add CONTEXT.md and task plan for 003-vietnam-country
b10537d fix: interpolate actual country name into analyst SUMMARY_PROMPT
944d63d feat: add Vietnam subsection to company_context.md prospects/ecosystem
975086a feat: add Vietnam (VN) country block to config/sources.json
8771013 feat: make report/internals/admin routes country-aware
4202de0 feat: working country switcher in base.html, domain tabs preserve country
07638b2 feat: list all countries in admin source-approval dropdown
f0be7e3 feat: country-scope feedback digests and weekly summaries
519c772 fix: tier VN source fetchers and deactivate unreachable sources
61881cb docs: add REVIEW.md for feature/003-vietnam-country (PASS)
585633e chore(context): update project context
060dad9 fix: force UTF-8 stdout/stderr to survive Vietnamese diacritics on Windows
89ce900 feat: add Malaysia (MY) country block to config/sources.json
b3a1bbc feat: real SG/MY/VN country-tab links in base.html
a90f5f2 feat: add Malaysia subsection to company_context.md prospects/ecosystem
4012532 fix: tier MY source fetchers and deactivate unreachable sources
36d2530 docs: add REVIEW.md for feature/004-malaysia-country (PASS)
1f158ff chore(context): update project context after 004-malaysia-country PASS
b1549d6 Merge branch 'feature/004-malaysia-country' into integration/vn-my-review
bb6fbd3 feat: expand _domain_mode() to validate all 8 business domains
e1505c9 feat: add RCC/HLS/MFG/CTE/PSS domain tabs to base.html
4ec3052 docs: activate MFG/HLS/RCC/CTE/PSS product-catalog headings
aea7783 feat: add MFG/HLS/RCC/CTE/PSS product catalogs and broaden opportunities gate
4f174f4 feat: add RCC/HLS/MFG/CTE/PSS checkboxes to admin source-approval form
c9f6464 feat: retag Vietnam sources with real business domains
bcdcfba docs: add REVIEW.md for feature/005-domain-activation (PASS)
efe5125 chore(context): update project context after 005-domain-activation PASS
```

Already-inspected during this research (findings folded into §2-4 above, don't re-review from scratch,
just cite): `b10537d` (the SUMMARY_PROMPT country-name fix that `weekly.py` never received — see lead 4),
`aea7783` (the gate-broadening commit — see §3), `bb6fbd3` (the domain-tuple bug's introducing commit —
see lead 2). The remaining ~24 commits (source-list additions, fetcher tiering, routing/UI changes,
context updates) are genuinely unreviewed and are what Task 006 covers.

## Net effect on decomposition

- Confirmed VN `source_name` breakage is the single most important accuracy finding and reshapes how the
  audit tasks must join signals to sources (entity-name fallback, not source_name).
- Leads 2, 4, 5 are each independent, small, mechanical, low-risk — three separate fix tasks.
- Lead 3 and the gate divergence (§3) are real but architecturally non-trivial — folded into
  CODE-REVIEW.md as flagged findings, no fix task.
- Re-fetch is scoped to exactly the 40 sources actually cited across both reports (15 VN + 25 MY), not
  all ~95 active VN+MY sources — full URL/fetcher lists are embedded directly in Tasks 001/002.
- Accuracy audit and code-correctness review remain two independent tracks (confirming CONTEXT.md's
  Workstream independence decision) but each is internally split into two sequenced sub-tasks purely to
  keep per-task context small and avoid two tasks writing the same markdown file concurrently — not
  because CONTEXT.md's file-ownership analysis was wrong.
