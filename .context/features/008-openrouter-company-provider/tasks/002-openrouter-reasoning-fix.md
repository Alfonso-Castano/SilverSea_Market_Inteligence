# Task 002: Fix OpenRouter reasoning-token overhead and JSON-array shape in `_chat_completion()`

**Status:** done
**Depends on:** Task 001 (the `openrouter-*` provider keys this task's `provider_key.startswith(...)`
checks are keyed against must exist in `PROVIDERS` first, so an executor can cross-check naming)
**Model tier:** cheap — the exact code change is fully specified below, discovered and confirmed
via live testing during planning (see RESEARCH.md §4), not something requiring new design judgment
from the executor. Correctness is proven by Task 004's live-verification run, not by re-deriving
the reasoning here.

## Files
- Modify: `pipeline/analyst.py`

## What to do

This is a real, necessary code change — not registry-only — found during this feature's research.
Live-testing the pipeline's actual `_synthesize_sector()` call shape (its real system prompt,
`response_format={"type": "json_object"}`, `max_tokens=2000`) against both new NVIDIA free models
found that OpenRouter's default behavior spends the overwhelming majority of the output budget on
an internal reasoning trace, and — likely as a related side effect — the model then fails to follow
the "respond with a JSON array" instruction, instead emitting a bare JSON object and silently
dropping real signals. Disabling reasoning via OpenRouter's unified `reasoning` request parameter,
**combined with** reusing the exact JSON-array-wrapper hint this file already sends for the `local`
(Ollama) provider, was confirmed live to fix both problems together — see RESEARCH.md §4 for the
full before/after evidence from this session's live calls.

**1. In `_chat_completion()`**, add a reasoning-disable branch for OpenRouter provider keys. Find
this existing block:

```python
    kwargs = {}
    if json_schema is not None:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(
```

Replace with:

```python
    kwargs = {}
    if json_schema is not None:
        kwargs["response_format"] = {"type": "json_object"}
    if provider_key.startswith("openrouter"):
        # OpenRouter's free NVIDIA Nemotron models default to emitting an internal
        # reasoning trace that can consume the large majority of max_tokens before any
        # real content is produced, truncating/malforming JSON output — confirmed live
        # during feature 008's planning (1300+ reasoning tokens observed against a
        # max_tokens=2000 sector-synthesis call; see
        # .context/features/008-openrouter-company-provider/RESEARCH.md §4). Disabling
        # reasoning via OpenRouter's unified `reasoning` request parameter frees that
        # budget for real content. Applied to every call site (extraction, sector
        # synthesis, summary synthesis), not just the JSON-mode ones, since all three
        # share the same max_tokens=2000 ceiling and the same overhead risk.
        kwargs["extra_body"] = {"reasoning": {"enabled": False}}
    response = client.chat.completions.create(
```

**2. In `_synthesize_sector()`**, widen the existing local-only JSON-array-shape hint to also cover
OpenRouter. Find:

```python
    user_message = f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"
    if provider_key == "local":
        user_message += '\n\nReturn a JSON object with a top-level "signals" array of the entries.'
```

Replace with:

```python
    user_message = f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"
    if provider_key == "local" or provider_key.startswith("openrouter"):
        # Loose response_format={"type": "json_object"} mode nudges free-tier OpenRouter
        # models toward a bare JSON *object*, not the array SECTOR_SYNTHESIS_PROMPT asks
        # for — confirmed live (RESEARCH.md §4). The same object-wrapper phrasing already
        # used for Ollama's native schema mode fixes it here too, since
        # _synthesize_sector()'s own unwrap logic below already handles a
        # {"signals": [...]} shape.
        user_message += '\n\nReturn a JSON object with a top-level "signals" array of the entries.'
```

**Do NOT** make the analogous change to `_synthesize_summary()`'s existing `provider_key ==
"local"` hint block — leave that one exactly as-is. `SUMMARY_SCHEMA`'s target shape is already a
top-level object (`executive_summary`/`opportunities`/`synthesis` keys), which is what loose
`json_object` mode naturally produces without needing a wrapper hint — the array-vs-object
confusion that broke sector synthesis doesn't apply there. This wasn't independently live-tested
during planning (budget discipline); Task 004's live-verification run, which exercises `analyse()`
end-to-end, is where this assumption actually gets proven or disproven — if it's proven wrong,
report that finding in Task 004's evidence rather than silently patching around it there.

## Interfaces
- `_chat_completion(client, provider_key, system_prompt, user_message, max_tokens, json_schema=None)`
  — signature unchanged, only its internal `kwargs` construction gains the conditional `extra_body`
  key. Every existing caller (`_extract_sector`, `_synthesize_sector`, `_synthesize_summary`) is
  unaffected for non-`openrouter-*` provider keys.
- `openai.OpenAI.chat.completions.create(..., extra_body={...})` — a standard pass-through kwarg on
  the `openai` Python SDK (confirmed working during planning's live tests, same SDK version this
  repo already depends on) that forwards extra fields into the raw HTTP request body; OpenRouter
  reads `reasoning.enabled` from there. Not a new dependency.

## Constraints
- The `provider_key.startswith("openrouter")` check must not match `"deepseek"`, `"groq"`, `"qwen"`,
  `"kimi"`, `"company-qwen-flash"`, `"company-qwen-plus"`, or `"local"` — verify by eye that none of
  those strings start with `"openrouter"`.
- Do not change `max_tokens=2000` at any of the three call sites — RESEARCH.md §4's live tests
  confirmed this is sufficient once reasoning is disabled (231-1617 completion tokens observed,
  comfortably under 2000, for both new NVIDIA models against the test fixture).
- Do not add the wrapper hint to `_synthesize_summary()` — see the explicit "Do NOT" instruction
  above. If Task 004's live run finds `_synthesize_summary()` also needs it, that's a finding to
  report, not something to fix silently inside this task (this task is already merged/done by then).
- This function is shared by every provider (Groq, DeepSeek, Qwen-direct, Kimi, the two company-Qwen
  entries, and both new OpenRouter entries) — do not regress any of them. Task 004's live
  verification only re-exercises the OpenRouter path directly, so double-check by inspection that
  the `if provider_key.startswith("openrouter")` branch is strictly additive and unreachable for
  every other provider key.
- Do not touch any other file in this task.

## Verification
1. `py -c "import ast; ast.parse(open('pipeline/analyst.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "import pipeline.analyst; print('OK, imports cleanly')"`
3. `py -c "content = open('pipeline/analyst.py', encoding='utf-8').read(); assert 'provider_key.startswith(\"openrouter\")' in content; assert content.count('provider_key.startswith(\"openrouter\")') == 2, 'expected exactly 2 occurrences (one in _chat_completion, one in _synthesize_sector)'; print('OK — both sites present')"`
4. By eye: confirm `_synthesize_summary()`'s existing `if provider_key == "local":` block is
   byte-for-byte unchanged (quote the relevant lines in your evidence).
5. `py -m pytest tests/test_clamp.py -q` — unrelated to this change, but confirms no accidental
   regression to the one existing unit test.
6. No live LLM calls in this task — Task 004 owns that evidence. This task's verification is purely
   static (syntax, import, string-presence, byte-diff-by-eye).

## Evidence

1. Syntax OK. 2. `pipeline.analyst` imports cleanly. 3. `provider_key.startswith("openrouter")` appears exactly 2 times (one in `_chat_completion()`, one in `_synthesize_sector()`). 4. `_synthesize_summary()`'s `if provider_key == "local":` block confirmed byte-for-byte unchanged (quoted in executor's report). 5. `py -m pytest tests/test_clamp.py -q` → `6 passed`. 6. All three `_chat_completion()` call sites confirmed still at `max_tokens=2000`.

No live LLM calls made — static verification only, per task scope.
