# Task 007 (FIX, optional): app.py's report() fallback still hardcodes 3 domains, not 8

**Status:** pending
**Depends on:** none — this is a standalone, optional fix. It is fully specified below and does not
require Task 005/006's CODE-REVIEW.md to exist first (the finding is already confirmed in
`RESEARCH.md` §4, lead 2). Alfonso may execute this task alone, alongside the audit tasks, or skip it
entirely — per CONTEXT.md's "fix tasks are separate and optional" decision, it makes no code changes on
its own; nothing else in this plan depends on it running.
**Model tier:** cheap — one-line, fully-specified change; transcription plus verification.

## Files
- Modify: `app.py` (~line 108-111, inside the `report()` route)

## What to do

`app.py`'s `_domain_mode()` (line ~81-83) validates all 8 active business domains:

```python
def _domain_mode():
    domain = request.args.get("domain", "BER")
    return domain if domain in ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS") else "BER"
```

But `report()`'s fallback check (which decides whether to fall back to the legacy, pre-domain-scoping
`latest_report.json` when no domain-scoped report exists for the current country) still only checks the
original 3:

```python
            any_domain_file_exists = any(
                os.path.exists(os.path.join(DATA_DIR, f"latest_report_{country}_{d}.json"))
                for d in ("BER", "EDU", "GENERAL")
            )
```

This means: for a country that has a report file for, say, `RCC` or `PSS` only (no `BER`/`EDU`/`GENERAL`
report), this check would incorrectly conclude "no domain-scoped report exists for this country" and
fall back to the stale legacy `latest_report.json` — silently showing wrong content instead of an
accurate "no report yet for this domain" state. Currently masked for VN/MY since both already have
`BER`/`GENERAL` reports, but real once any country's *only* report is a domain outside the original 3.

Fix: change the tuple to cover all 8 domains, matching `_domain_mode()`'s validation list exactly:

```python
            any_domain_file_exists = any(
                os.path.exists(os.path.join(DATA_DIR, f"latest_report_{country}_{d}.json"))
                for d in ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS")
            )
```

That's the entire change — replace the 3-element tuple with the 8-element tuple, copied verbatim from
`_domain_mode()`'s own tuple so the two lists can never drift again by construction (consider adding a
one-line comment noting they must stay in sync, e.g. `# keep in sync with _domain_mode()`'s tuple above`,
if you judge it clarifies intent — optional, not required).

## Interfaces
None — this is an internal fallback-check detail; no function signature changes.

## Constraints
- Change only the one tuple literal (and optionally add a one-line sync comment). Do not touch
  `_domain_mode()`, the surrounding `if`/`else` structure, or any other route.
- Do not touch `internals()`'s analogous country-metadata fallback check (a similar-looking but distinct
  block a few lines below) — out of scope for this fix.

## Verification
1. `py -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "
import re
src = open('app.py', encoding='utf-8').read()
domain_mode_tuple = re.search(r'def _domain_mode.*?\((.*?)\)', src, re.S).group(1)
fallback_tuple = re.search(r'any_domain_file_exists = any\(.*?for d in \((.*?)\)', src, re.S).group(1)
assert 'RCC' in fallback_tuple and 'PSS' in fallback_tuple and 'MFG' in fallback_tuple, fallback_tuple
print('fallback tuple now includes all 8 domains')
"` — confirms the fallback tuple was actually widened (a looser check than exact string equality since
   `_domain_mode()`'s tuple has a slightly different literal shape; the important thing is the fallback
   check now includes the 5 domains it was missing).
3. Boot the app and curl the report route to confirm no regression (per CLAUDE.md's Verification Before
   Done: Flask-side changes are verified by booting the app and curling the route, no LLM call needed):
   `py -c "import app" ` (import-time sanity check — confirms no syntax/import error) then start the
   Flask dev server briefly and `curl` `/?country=VN&domain=BER` (an existing report) to confirm it still
   renders, and `/?country=VN&domain=PSS` (a domain VN has no report file for yet) to confirm it now
   falls through correctly rather than silently mis-serving legacy content — describe what each returned
   in your evidence.

## Evidence
[Filled in at completion]
