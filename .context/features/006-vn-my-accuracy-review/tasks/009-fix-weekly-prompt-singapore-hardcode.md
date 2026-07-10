# Task 009 (FIX, optional): weekly.py's WEEKLY_PROMPT hardcodes "Singapore" for every country

**Status:** pending
**Depends on:** none — standalone, optional fix, fully specified below. Does not require the audit tasks
to run first (finding already confirmed in `RESEARCH.md` §4, lead 4). Per CONTEXT.md's "fix tasks are
separate and optional" decision, Alfonso may execute this alone or skip it.
**Model tier:** cheap — the exact pattern to copy already exists in the codebase (commit `b10537d` fixed
the identical bug on the daily-report path); this is transcription of that established pattern to a
second file, plus verification.

## Files
- Modify: `pipeline/weekly.py` (`WEEKLY_PROMPT` string, `generate_weekly_summary()` signature and its
  `.format()` call)
- Modify: `main.py` (the `generate_weekly_summary(country_code=country["code"])` call site, ~line 105)

## What to do

`pipeline/weekly.py`'s `WEEKLY_PROMPT` hardcodes "Singapore" regardless of which country's reports are
being compressed:

```python
WEEKLY_PROMPT = """You are summarizing a week of daily market intelligence reports for Silversea Media
(digital twin & immersive tech company, Singapore).
```

This is the exact same bug commit `b10537d` already fixed on `pipeline/analyst.py`'s `SUMMARY_PROMPT`
(feature/003-vietnam-country, Task 006) — that commit's message: *"SUMMARY_PROMPT hardcoded 'Singapore'
regardless of which country's data was being analysed, so a Vietnam run would misdescribe itself as
Singapore."* `weekly.py` never received the same treatment. `generate_weekly_summary(country_code: str =
None)` already threads `country_code` through for ChromaDB `where`-filtering and metadata tagging, but
never uses it in the actual prompt text sent to the LLM.

Apply the identical fix pattern `b10537d` used (str.replace on a placeholder token, not `.format()`,
since `WEEKLY_PROMPT` contains no literal braces currently but keeping the same mechanism as
`SUMMARY_PROMPT` is the established, deliberate convention in this codebase — see that commit's own
rationale for choosing `.replace()` over `.format()`):

1. In `pipeline/weekly.py`, change the `WEEKLY_PROMPT` string's first line to use a placeholder:

```python
WEEKLY_PROMPT = """You are summarizing a week of daily market intelligence reports for Silversea Media
(digital twin & immersive tech company, {country_name}).
```

2. Change `generate_weekly_summary`'s signature to accept a `country_name` parameter, defaulting to
   `"Singapore"` to preserve today's exact behavior for any caller that doesn't pass it (matches
   `country_code`'s existing `= None` default-preserves-old-behavior convention, but `"Singapore"` here
   since that's the literal string being replaced, not `None`):

```python
def generate_weekly_summary(country_code: str = None, country_name: str = "Singapore") -> str:
```

3. Where the prompt is currently formatted (line ~70), replace the placeholder before use, mirroring
   `_synthesize_summary()`'s exact pattern in `pipeline/analyst.py`:

```python
    system_prompt = WEEKLY_PROMPT.replace("{country_name}", country_name)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": system_prompt.format(count=len(weekly_docs), reports=reports_text)}],
        max_tokens=2048,
    )
```

   (Note: `WEEKLY_PROMPT` already uses real `.format()` placeholders `{count}` and `{reports}` — those
   stay exactly as-is; only the new `{country_name}` token is replaced via `.replace()` *before* the
   `.format()` call, so `.format()` never sees an unresolved `{country_name}` token. Do this in the order
   shown: `.replace()` first, then `.format()` on the result.)

4. In `main.py`, update the one call site (~line 105, inside the Sunday weekly-summary loop) to pass the
   country name, which is already in scope as `country["name"]`:

```python
            generate_weekly_summary(country_code=country["code"], country_name=country["name"])
```

That's the entire change — 4 small edits across the two files, no new files, no schema changes.

## Interfaces
- `generate_weekly_summary()`'s signature gains one new optional parameter (`country_name`) with a
  backward-compatible default — any other caller (there are none currently besides `main.py` and
  `weekly.py`'s own `if __name__ == "__main__":` block) keeps working unchanged.
- `weekly.py`'s standalone `if __name__ == "__main__":` block (bottom of the file) calls
  `generate_weekly_summary()` with no arguments — leave this call site untouched; it will correctly fall
  back to the new `country_name="Singapore"` default, matching its pre-existing `country_code=None`
  (global, all-countries) behavior.

## Constraints
- Do not change `country_code`'s existing behavior or the `where`-filter/metadata-tagging logic that uses
  it — this fix only touches the prompt text's country *name* string, not the ChromaDB scoping logic.
- Do not touch `pipeline/analyst.py` — the reference pattern lives there, but this task only copies the
  pattern to `weekly.py`, it doesn't modify the original.
- Keep the `.replace()`-before-`.format()` ordering exactly as shown — reversing it would leave an
  unresolved `{country_name}` token if `.format()` runs first (since `.format()` doesn't know about that
  key and would raise `KeyError`).

## Verification
1. `py -c "import ast; ast.parse(open('pipeline/weekly.py', encoding='utf-8').read()); ast.parse(open('main.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "
import re
src = open('pipeline/weekly.py', encoding='utf-8').read()
assert '{country_name}' in src, 'placeholder not added to WEEKLY_PROMPT'
assert 'country_name: str = \"Singapore\"' in src, 'signature default not added'
assert '.replace(\"{country_name}\", country_name)' in src, 'replace() call not added'
main_src = open('main.py', encoding='utf-8').read()
assert 'country_name=country[\"name\"]' in main_src, 'main.py call site not updated'
print('OK — all 4 edits present')
"`
3. Exercise the actual string substitution with zero LLM cost (this is pure string formatting, no API
   call — safe to run directly):
   `py -c "
from pipeline.weekly import WEEKLY_PROMPT
result = WEEKLY_PROMPT.replace('{country_name}', 'Vietnam').format(count=3, reports='(sample)')
assert 'Vietnam' in result and 'Singapore' not in result, result[:200]
print('Substitution verified — Vietnam appears, Singapore does not')
"`
4. Confirm `generate_weekly_summary()` still degrades gracefully with no `GROQ_API_KEY` set (matching
   existing behavior, no new crash introduced by the signature change):
   `powershell -Command "$env:GROQ_API_KEY=$null; py -c \"import os; os.environ.pop('GROQ_API_KEY', None); from pipeline.weekly import generate_weekly_summary; r = generate_weekly_summary(country_code='VN', country_name='Vietnam'); print('returned:', repr(r))\""`
   — should print an empty-string return and a "skipped — no GROQ_API_KEY" message (or "No daily reports
   found" if that check fires first — either graceful-skip path is fine), not a crash.

## Evidence
[Filled in at completion]
