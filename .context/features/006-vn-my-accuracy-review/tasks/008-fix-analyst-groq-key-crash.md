# Task 008 (FIX, optional): analyst.py crashes with KeyError on unset GROQ_API_KEY

**Status:** done
**Depends on:** none — standalone, optional fix, fully specified below. Does not require the audit tasks
to run first (finding already confirmed in `RESEARCH.md` §4, lead 5). Per CONTEXT.md's "fix tasks are
separate and optional" decision, Alfonso may execute this alone or skip it.
**Model tier:** cheap — one-line, fully-specified change; transcription plus verification.

## Files
- Modify: `pipeline/analyst.py` (line 341, inside `analyse()`)

## What to do

`pipeline/analyst.py`'s `analyse()` constructs its Groq client as:

```python
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
```

This raises `KeyError` immediately if `GROQ_API_KEY` is unset — before any of the graceful `try/except`
degradation already built into `_extract_sector()`, `_synthesize_sector()`, and `_synthesize_summary()`
gets a chance to run. `pipeline/feedback.py` (lines 60, 121) and `pipeline/weekly.py` (line 63) both use
the safer pattern:

```python
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
```

Fix: change `analyst.py` line 341 to match that pattern exactly:

```python
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
```

That's the entire change. Do not add an explicit `if not client.api_key: print(...); return` early-exit
the way `feedback.py`/`weekly.py` do — `analyse()`'s call sites already have their own per-site
`try/except Exception` blocks (`_extract_sector` returns a fallback string, `_synthesize_sector` returns
`[]`, `_synthesize_summary` returns an empty summary dict) that will catch the resulting Groq
authentication error on the first real `.create()` call and degrade the same way they already handle any
other API failure. Adding an early-exit here would also require `main.py` to check `analyse()`'s return
value before calling `save_report_json()` (it currently doesn't), which is a larger behavioral decision
about desired pipeline behavior on a missing key — out of scope for this one-line mechanical fix (flagged
as a residual gap in `CODE-REVIEW.md` if that task has already run; not this task's job to resolve).

## Interfaces
None — `analyse()`'s signature and return shape are unchanged; this only changes how the API key is read.

## Constraints
- Change only that one line. Do not touch the surrounding function, the three call sites' existing
  `try/except` blocks, or `main.py`.
- Do not add new print/logging statements — keep the fix minimal, matching exactly what
  `feedback.py`/`weekly.py` already do for the client-construction line itself (they add a separate
  early-exit check that this task deliberately does not replicate — see rationale above).

## Verification
1. `py -c "import ast; ast.parse(open('pipeline/analyst.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "
import re
src = open('pipeline/analyst.py', encoding='utf-8').read()
assert 'os.environ[\"GROQ_API_KEY\"]' not in src, 'old KeyError-raising pattern still present'
assert 'os.environ.get(\"GROQ_API_KEY\", \"\")' in src, 'new safe pattern not found'
print('OK — pattern replaced')
"`
3. Confirm the module still imports cleanly with no `GROQ_API_KEY` set (simulating the exact crash
   scenario this fixes) — this is a real, cheap, zero-LLM-cost verification since it only exercises
   Python import machinery, not an actual API call:
   PowerShell: `powershell -Command "$env:GROQ_API_KEY=$null; py -c \"import os; os.environ.pop('GROQ_API_KEY', None); from pipeline.analyst import analyse; print('import OK, no KeyError at import time')\""`
   — note this only proves the *import* doesn't crash; `analyse()` itself is not invoked (that would need
   real filtered results and would attempt a real Groq call once inside the function, hitting the
   existing per-call-site exception handling) — describe in your evidence that you verified the specific
   line changed and the import-time behavior, not a full `analyse()` invocation (which is out of scope
   per the no-LLM-calls constraint).

## Evidence
DONE (haiku executor). Single-line change at `pipeline/analyst.py:341`: `os.environ["GROQ_API_KEY"]` → `os.environ.get("GROQ_API_KEY", "")`; `git diff` confirms 1 insertion / 1 deletion, that line only. Verified: (1) AST parse → syntax OK; (2) regex → old pattern gone, new present; (3) module imports cleanly with GROQ_API_KEY unset → "import OK, no KeyError at import time" (import-time behavior only, not a full analyse() call — no LLM invoked). No early-exit/print added (out of scope). No other file touched.
