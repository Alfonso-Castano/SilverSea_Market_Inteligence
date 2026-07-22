# Task 003: Generalize pipeline/analyst.py's LLM calls across providers

**Status:** done
**Depends on:** Task 001 (`config/models.py` must export `PROVIDERS`/`LOCAL_MODEL`/`LOCAL_NUM_CTX`
before this file can import them), Task 002 (`openai` package must be installed for this file's
own import-check verification step to succeed, and for the real interpreter this task edits
against to have the package available).
**Model tier:** quality — this is the feature's architectural core: unifying `feature/002`'s
Ollama-specific dispatch shape with four new OpenAI-API-shaped remote providers behind one
generic branch, while preserving Groq's exact existing behavior. Genuine judgment required in
verifying nothing about the three call sites' actual prompts/parsing/error-handling changes.

## Files
- Modify: `pipeline/analyst.py`

## What to do

Read the whole current file first — you need to see exactly how the three call sites
(`_extract_sector`, `_synthesize_sector`, `_synthesize_summary`) and `analyse()` are structured
today before touching anything, since this task's core promise is that Groq's behavior is
byte-for-byte unchanged in outcome, only in *which client sends the request*.

Also read `git show feature/002-local-llm-backend:pipeline/analyst.py` (or
`git diff 168810e feature/002-local-llm-backend -- pipeline/analyst.py`) — that branch already
solved "one dispatch helper covering a schema-constrained local branch and a loose-JSON remote
branch," just for exactly one remote provider (Groq). This task generalizes that remote branch to
cover four remote providers instead of one, reusing the local/Ollama branch and its
`SECTOR_SYNTHESIS_SCHEMA`/`SUMMARY_SCHEMA` verbatim (RESEARCH.md §8 already resolved the
`_chat_completion` shape below — you're implementing a decision already made, not designing from
scratch).

**This task does NOT touch:** `SECTOR_EXTRACT_PROMPT`, `SECTOR_SYNTHESIS_PROMPT`, `SUMMARY_PROMPT`
(content), `_build_rag_context`, `_clamp_opportunity_scores`'s clamping logic,
`_generate_implications`, `_derive_competition_risks`. If your diff touches any of these beyond
moving `_SCORE_DIMENSIONS`'s *location* (see below — content stays identical), you've gone out of
scope.

### 1. Imports

Replace:
```python
import json
import os
import time
import datetime
from groq import Groq
```
with:
```python
import json
import os
import time
import datetime
import openai

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False
```

And replace:
```python
from config.models import GROQ_MODEL
```
with:
```python
from config.models import PROVIDERS, LOCAL_MODEL, LOCAL_NUM_CTX
```

### 2. Add the dispatch helper, local-only JSON schemas, and relocate `_SCORE_DIMENSIONS`

Immediately after `SUMMARY_PROMPT`'s closing `"""` and before `def _build_rag_context(...)`,
insert:

```python
_SCORE_DIMENSIONS = ["strategic_fit", "revenue_potential", "win_probability", "urgency", "intelligence_quality"]

# JSON schemas used ONLY on the local (Ollama) backend, via /api/chat's native `format`
# field for genuine schema-constrained output. Every remote provider (Groq/DeepSeek/Qwen/
# Kimi) never uses these — they keep the loose response_format={"type": "json_object"} mode,
# since Ollama's OpenAI-compatible endpoint doesn't support schema-constrained JSON but its
# native endpoint does (see .context/features/002-local-llm-backend/RESEARCH.md §1).

# Ollama's native `format` schemas must be objects, not bare arrays — so the sector synthesis
# result is wrapped in a top-level `signals` array. This matches the dict-unwrap tolerance
# already in _synthesize_sector (result.get("signals", ...)).
SECTOR_SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "signals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string"},
                    "signal": {"type": "string"},
                    "source_name": {"type": "string"},
                },
                "required": ["entity", "signal", "source_name"],
            },
        }
    },
    "required": ["signals"],
}

# Mirrors SUMMARY_PROMPT's top-level object shape exactly.
SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "array", "items": {"type": "string"}},
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "source_quote": {"type": "string"},
                    "named_entry_point": {"type": "string"},
                    "concrete_action": {"type": "string"},
                    "deadline": {"type": "string"},
                    "source_name": {"type": "string"},
                    "product_fit": {"type": "string"},
                    "scores": {
                        "type": "object",
                        "properties": {dim: {"type": "integer"} for dim in _SCORE_DIMENSIONS},
                        "required": list(_SCORE_DIMENSIONS),
                    },
                    "total_score": {"type": "integer"},
                },
                "required": [
                    "title",
                    "source_quote",
                    "named_entry_point",
                    "concrete_action",
                    "deadline",
                    "source_name",
                    "product_fit",
                    "scores",
                    "total_score",
                ],
            },
        },
        "synthesis": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["executive_summary", "opportunities", "synthesis"],
}


def _chat_completion(client, provider_key: str, system_prompt: str, user_message: str, max_tokens: int, json_schema: dict | None = None) -> str:
    """Dispatch one LLM call to the resolved provider (provider_key: a PROVIDERS key, or "local").

    Returns the raw text content. Every remote provider (Groq/DeepSeek/Qwen/Kimi) is genuinely
    OpenAI-API-shaped, so one branch covers all four: response_format={"type": "json_object"}
    whenever json_schema is given, a plain completion otherwise — the same loose JSON mode the
    Groq-only code already relied on, just parameterized by which client/model is active. The
    local backend uses Ollama's native structured-outputs 'format' field instead, for genuine
    schema enforcement (see the schemas above).
    """
    if provider_key == "local":
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("--llm=local but the 'ollama' package is not installed (see requirements.txt)")
        response = ollama.chat(
            model=LOCAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            format=json_schema,  # None => free-text, matching the extraction call site
            options={"num_ctx": LOCAL_NUM_CTX, "num_predict": max_tokens, "temperature": 0},
        )
        return response["message"]["content"]

    kwargs = {}
    if json_schema is not None:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(
        model=PROVIDERS[provider_key]["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        **kwargs,
    )
    return response.choices[0].message.content
```

Then delete the now-duplicate original `_SCORE_DIMENSIONS = [...]` line that currently sits
between `_synthesize_sector` and `_clamp_opportunity_scores` (it's been relocated above, not
removed — there must be exactly one definition of `_SCORE_DIMENSIONS` in the file afterward).

### 3. `_extract_sector` — add `provider_key`, dispatch through the helper

Change the signature from `def _extract_sector(client, sector_name: str, sources: list) -> str:`
to `def _extract_sector(client, provider_key: str, sector_name: str, sources: list) -> str:`.

Replace the body's `try:` block (currently a direct `client.chat.completions.create(...)` call)
with:
```python
    try:
        return _chat_completion(client, provider_key, SECTOR_EXTRACT_PROMPT, user_message, 2000)
    except Exception as e:
        print(f"    Error extracting {sector_name}: {e}")
        return f"**{label}**: Extraction failed — {e}"
```
(the `except` block's content is unchanged — only the `try` body changes).

### 4. `_synthesize_sector` — add `provider_key`, dispatch through the helper, local-only hint

Change the signature to
`def _synthesize_sector(client, provider_key: str, sector_name: str, extraction_text: str) -> list:`.

After the existing `user_message = f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"`
line, add (matching `feature/002`'s pattern exactly — the local backend needs this hint because
its schema wraps the array in a `signals` key, remote providers don't need it since they already
tolerate the dict-unwrap in the parsing code below):
```python
    if provider_key == "local":
        user_message += '\n\nReturn a JSON object with a top-level "signals" array of the entries.'
```

Replace the `try:` block's call with:
```python
    try:
        content = _chat_completion(
            client,
            provider_key,
            SECTOR_SYNTHESIS_PROMPT,
            user_message,
            2000,
            json_schema=SECTOR_SYNTHESIS_SCHEMA,
        )
        result = json.loads(content)
        if isinstance(result, dict):
            result = result.get("signals", list(result.values())[0] if result else [])
        if not isinstance(result, list):
            result = []
        return [item for item in result if isinstance(item, dict)]
    except Exception as e:
        print(f"    Error synthesizing {sector_name}: {e}")
        return []
```
(the dict-unwrap/list-filter logic is unchanged — only the call itself changes).

### 5. `_synthesize_summary` — add `provider_key`, dispatch through the helper, local-only hint

Change the signature to
`def _synthesize_summary(client, provider_key: str, signals_by_sector: dict, country_name: str) -> dict:`.

After the existing `system_prompt = SUMMARY_PROMPT.replace("{country_name}", country_name)` line,
add:
```python
    if provider_key == "local":
        user_message += (
            '\n\nReturn a single JSON object with the top-level keys '
            '"executive_summary", "opportunities", and "synthesis".'
        )
```

Replace the `try:` block's call with:
```python
    try:
        content = _chat_completion(
            client,
            provider_key,
            system_prompt,
            user_message,
            2000,
            json_schema=SUMMARY_SCHEMA,
        )
        result = json.loads(content)
        result["opportunities"] = _clamp_opportunity_scores(result.get("opportunities", []))
        return result
    except Exception as e:
        print(f"    Error in summary synthesis: {e}")
        return {"executive_summary": [], "opportunities": [], "synthesis": []}
```
(the `_clamp_opportunity_scores` call and its logic are unchanged).

### 6. `analyse()` — resolve the client from `provider_key`, thread it through every call site

Change the signature from `def analyse(filtered_results: list, country: dict) -> dict:` to
`def analyse(filtered_results: list, country: dict, provider_key: str) -> dict:`.

Replace:
```python
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
```
with:
```python
    if provider_key == "local":
        client = None
    else:
        provider = PROVIDERS[provider_key]
        client = openai.OpenAI(base_url=provider["base_url"], api_key=os.environ.get(provider["key_env"], ""))
```

Then update every call site inside `analyse()` to pass `provider_key` as the second positional
argument (matching the new signatures above):
- `sector_extractions[sector_name] = _extract_sector(client, provider_key, sector_name, sources)`
- `signals = _synthesize_sector(client, provider_key, sector_name, extraction_text)`
- `summary = _synthesize_summary(client, provider_key, signals_by_sector, country["name"])`

Nothing else inside `analyse()` changes — `RAG_ENABLED` handling, `_generate_implications`,
`_derive_competition_risks`, the `report_data` assembly, and the `REPORT_HISTORY` write are all
untouched.

## Interfaces
- `analyse(filtered_results: list, country: dict, provider_key: str) -> dict` — new required
  third parameter. `main.py` (Task 005) is the only other file in this repo that calls `analyse()`
  (confirmed via repo-wide grep during planning — `tests/test_clamp.py` imports
  `_clamp_opportunity_scores`/`_SCORE_DIMENSIONS` directly, never `analyse()`, so it's unaffected
  by this signature change).
- `provider_key`: expected to be either a key present in `config.models.PROVIDERS` (currently
  `"deepseek"`, `"groq"`, `"qwen"`, `"kimi"`) or the literal string `"local"`. This function does
  NOT validate `provider_key` itself (e.g. it will raise `KeyError` on `PROVIDERS[provider_key]`
  for an unknown key) — validation and the fail-fast "env var not set" check both happen earlier,
  in `pipeline/llm_select.py` (Task 004), before `analyse()` is ever called. Do not add redundant
  validation here.

## Constraints
- Preserve the exact existing exception-handling shape at all three call sites — each still
  catches its own errors and degrades to a fallback value (never lets an LLM/API error propagate
  out of `analyse()`).
- Do not change `max_tokens` values, `CALL_DELAY`, `MIN_CONTENT_CHARS`, or any prompt string.
- Do not add print statements beyond what already exists.
- Groq's *content* is unaffected by this change (same model string, same
  `response_format={"type": "json_object"}` semantics) — only its transport moves from the `groq`
  package to `openai.OpenAI(base_url="https://api.groq.com/openai/v1", ...)`. If you find yourself
  needing to change Groq's prompts, parsing, or scoring to make this work, stop — that means
  something else is wrong and this task's premise (transport-only change) doesn't hold; report
  BLOCKED rather than improvising a prompt change.

## Verification
1. `py -c "import ast; ast.parse(open('pipeline/analyst.py', encoding='utf-8').read()); print('syntax OK')"`
2. Confirm the `openai` package is installed first (Task 002's job, but re-check here since this
   task depends on it): `py -c "import openai; print('openai', openai.__version__)"`
3. `py -c "from pipeline.analyst import analyse, _chat_completion, SECTOR_SYNTHESIS_SCHEMA, SUMMARY_SCHEMA, _SCORE_DIMENSIONS; import inspect; sig = inspect.signature(analyse); assert list(sig.parameters) == ['filtered_results', 'country', 'provider_key'], sig; print('OK — analyse() signature updated correctly')"`
4. `py -c "
import re
src = open('pipeline/analyst.py', encoding='utf-8').read()
assert 'from groq import Groq' not in src, 'old groq import still present'
assert 'GROQ_MODEL' not in src, 'GROQ_MODEL should no longer be referenced in this file (PROVIDERS[\"groq\"][\"model\"] replaces it)'
assert src.count('_SCORE_DIMENSIONS = [') == 1, 'expected exactly one _SCORE_DIMENSIONS definition after relocation'
assert 'import openai' in src
print('OK — old references removed, no duplicate _SCORE_DIMENSIONS')
"`
5. Confirm `pipeline/analyst.py`'s prompt constants are byte-identical to before your edit —
   `git diff pipeline/analyst.py` and paste, in your evidence, confirmation that the diff hunks
   touching `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT`/`SUMMARY_PROMPT`,
   `_build_rag_context`, `_clamp_opportunity_scores`'s body, `_generate_implications`, and
   `_derive_competition_risks` are all empty (no changes to those regions) — this is the concrete
   check for the "prompts stay untouched" constraint, not just an assertion.
6. Do NOT make a real LLM call in this task — that's Task 007's job, scoped separately and
   deliberately (this task is code-shape verification only, zero token cost).

## Evidence

1. Syntax OK. 2. `openai 2.46.0` importable. 3. `analyse()` signature confirmed `['filtered_results', 'country', 'provider_key']`. 4. No `from groq import Groq`, no `GROQ_MODEL` reference, exactly one `_SCORE_DIMENSIONS = [`, `import openai` present. 5. `git diff` reviewed in full — every hunk touches only imports, the new schema/`_chat_completion` block, the four function signatures, the three call-site try-bodies, the two local-only hints, the relocated `_SCORE_DIMENSIONS`, and `analyse()`'s client init + call sites. Byte-identical region extraction confirmed `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT`/`SUMMARY_PROMPT`/`_build_rag_context`/`_generate_implications`/`_derive_competition_risks`/`_clamp_opportunity_scores` all untouched. 6. No real LLM call made (code-shape verification only, per task scope).

Transport-only premise held with zero improvisation. Groq now flows through `openai.OpenAI(base_url="https://api.groq.com/openai/v1", ...)` using `PROVIDERS["groq"]["model"]` (same model string). `analyse()`'s `provider_key` is a required third positional arg with no internal validation — that's `pipeline/llm_select.py` (task 004)'s job, upstream.
