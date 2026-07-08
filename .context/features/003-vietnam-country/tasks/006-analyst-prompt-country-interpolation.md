# Task 006: Interpolate the actual country name into `pipeline/analyst.py`'s `SUMMARY_PROMPT`

**Status:** pending

## Files

- `pipeline/analyst.py` (modify — `SUMMARY_PROMPT` constant, `_synthesize_summary()`, and the one
  call site inside `analyse()`)

## What to do

`SUMMARY_PROMPT` (current lines 61-99) currently opens with a hardcoded sentence: *"You are
writing an executive summary for a market intelligence report for Silversea Media, a digital
twin / smart FM company in Singapore."* This runs for every country, including VN — the LLM is
being told it's analyzing Singapore even when the actual `country` dict passed into `analyse()`
is Vietnam's.

**Do not use `str.format()` on the whole prompt** — `SUMMARY_PROMPT` contains many literal JSON
`{...}` blocks later in the string (the `scores` object, the final output schema) that `.format()`
would try to interpret as format fields and raise a `KeyError`/`IndexError` on, or require
escaping every single one as `{{`/`}}` (error-prone, easy to miss one). Use a plain, targeted
`str.replace()` on one unique placeholder token instead — simpler and can't collide with the JSON
braces elsewhere in the string.

**1. Change the opening sentence** (line 61) from:
```python
SUMMARY_PROMPT = """You are writing an executive summary for a market intelligence report for Silversea Media, a digital twin / smart FM company in Singapore.
```
to:
```python
SUMMARY_PROMPT = """You are writing an executive summary for a market intelligence report for Silversea Media, a digital twin / smart FM company operating in {country_name}.
```
Everything else in the constant (lines 62-99) stays byte-for-byte unchanged — do not touch the
rubric, the schema, or any other prose.

**2. Update `_synthesize_summary()`** (current lines 211-237) to accept a `country_name` parameter
and substitute it before sending the system message:
```python
def _synthesize_summary(client, signals_by_sector: dict, country_name: str) -> dict:
    """Produce executive_summary, opportunities, and synthesis from structured signals."""
    sections = []
    for sector_name, signals in signals_by_sector.items():
        lines = []
        for s in signals:
            lines.append(f"- {s.get('entity', '?')} [source: {s.get('source_name', '')}]: {s.get('signal', '')}")
        sections.append(f"=== {sector_name} ===\n" + "\n".join(lines))

    user_message = "Structured signals by sector:\n\n" + "\n\n".join(sections)
    system_prompt = SUMMARY_PROMPT.replace("{country_name}", country_name)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        result["opportunities"] = _clamp_opportunity_scores(result.get("opportunities", []))
        return result
    except Exception as e:
        print(f"    Error in summary synthesis: {e}")
        return {"executive_summary": [], "opportunities": [], "synthesis": []}
```
(Only the new `country_name` parameter, the new `system_prompt` line, and using `system_prompt`
instead of `SUMMARY_PROMPT` directly in the `messages` list are new — everything else in the
function body is unchanged.)

**3. Update the call site inside `analyse()`** (current line 369):
```python
    summary = _synthesize_summary(client, signals_by_sector)
```
to:
```python
    summary = _synthesize_summary(client, signals_by_sector, country["name"])
```
`analyse(filtered_results: list, country: dict)` already receives the full `country` dict (used
elsewhere in the same function for the `REPORT_HISTORY` metadata tag, `country["code"]`) — this
just reads its existing `"name"` key (e.g. `"Singapore"` or `"Vietnam"`), no new data plumbing
needed anywhere upstream.

## Interfaces

- `_synthesize_summary(client, signals_by_sector: dict, country_name: str) -> dict` — signature
  gains one required positional parameter. This is a private (`_`-prefixed) function only called
  from within this module, so no other file needs updating.

## Constraints

- Do not touch the scoring rubric, the JSON schema, `_clamp_opportunity_scores()`,
  `_generate_implications()`, `_derive_competition_risks()`, `_extract_sector()`,
  `_synthesize_sector()`, or any other prompt (`SECTOR_EXTRACT_PROMPT`, `SECTOR_SYNTHESIS_PROMPT`)
  — this task is scoped exactly to the one hardcoded country reference in `SUMMARY_PROMPT` and its
  call chain.
- No second hardcoded country string may be introduced anywhere as a substitute (e.g. do not
  default `country_name` to `"Singapore"` if unset) — per CONTEXT.md's explicit constraint, the
  actual country dict passed into `analyse()` is always available, so there's no legitimate case
  needing a fallback default.
- Do not use `str.format()`/f-string formatting on the full `SUMMARY_PROMPT` constant — see the
  brace-collision explanation above; the `str.replace()` approach is required, not a style
  preference.

## Verification

No LLM call needed — this is a pure string-construction change, verifiable without any Groq API
call:

1. `py -c "import ast; ast.parse(open('pipeline/analyst.py', encoding='utf-8').read())"` — must
   parse without a `SyntaxError`.
2. ```
   py -c "
   from pipeline.analyst import SUMMARY_PROMPT
   assert 'Singapore' not in SUMMARY_PROMPT, 'hardcoded Singapore still present'
   assert '{country_name}' in SUMMARY_PROMPT, 'placeholder token missing'
   vn_prompt = SUMMARY_PROMPT.replace('{country_name}', 'Vietnam')
   assert 'Vietnam' in vn_prompt
   assert '{country_name}' not in vn_prompt
   assert '\"strategic_fit\": 0' in vn_prompt, 'JSON schema block corrupted by the substitution'
   print('OK')
   "
   ```
   must print `OK` with no `AssertionError`.
3. `py -c "import inspect; from pipeline.analyst import _synthesize_summary; print(inspect.signature(_synthesize_summary))"`
   — must show a `country_name` parameter.
4. Grep/read `analyse()` to confirm the call site now reads
   `_synthesize_summary(client, signals_by_sector, country["name"])` — exact string match.

## Model tier

cheap — the exact code changes are fully specified above; the executor's job is precise
transcription plus running the verification commands (particularly confirming the `.replace()`
approach doesn't corrupt the JSON schema portion of the prompt, which the assertion in step 2
directly checks).

## Depends on

None. Isolated to `pipeline/analyst.py`, touched by no other task in this feature.

## Evidence

