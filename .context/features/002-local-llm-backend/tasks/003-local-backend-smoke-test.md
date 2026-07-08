# Task 003: Local-backend smoke test — real Ollama call, schema-compliant JSON verified

**Status:** pending
**Depends on:** 002
**Model tier:** mid — judgment needed to write a meaningful real-call test and interpret its output, but no new architecture.

## Files
- Create: `tests/test_local_backend_smoke.py`

## What to do

This is the feature's actual evidence gate for its stated primary risk ("verify the local backend actually produces valid, schema-compliant JSON on real pipeline prompts") — CONTEXT.md and CLAUDE.md both say this must be checked stage-by-stage against the real local model, not mocked, and must not spend Groq quota.

Write a pytest file that:

1. Skips cleanly (via `pytest.mark.skipif` or an early `pytest.skip(...)`) if either:
   - `ollama` isn't importable, or
   - the configured local model (`config.models.LOCAL_MODEL`) doesn't appear in `ollama.list()`'s model names.

   When skipping for the second reason, the skip message must include the exact setup steps from `.context/features/002-local-llm-backend/RESEARCH.md` §2 (download a Q6_K GGUF, write a `Modelfile`, `ollama create <tag> -f Modelfile`) so a future run tells whoever sees the skip exactly what to do — don't just say "model not found."

2. If the model is present, run **two real calls** against it (this is the actual verification — no mocking):
   - One call through `pipeline.analyst._chat_completion` mirroring `_extract_sector`'s free-text usage (`json_schema=None`) with a short, realistic sample sector content block (a couple of sentences naming a fake but plausible partnership/tender, similar shape to what `_extract_sector` would receive) — just assert it returns a non-empty string.
   - One call through `_chat_completion` mirroring `_synthesize_sector`'s usage, passing `SECTOR_SYNTHESIS_SCHEMA` and a short extraction-shaped input, then `json.loads(...)` the result and assert: it parses without raising, and (matching `_synthesize_sector`'s own dict-unwrap logic) the unwrapped result is a list where every item has `entity`, `signal`, and `source_name` keys.

   Set `LLM_BACKEND=local` for the duration of the test (e.g. via `monkeypatch.setenv` reloading `config.models`/`pipeline.analyst`, or by directly calling `pipeline.analyst._chat_completion` with the local branch forced — pick whichever is less invasive given how task 002 actually wired the module-level `LLM_BACKEND` constant; check that file before deciding).

3. Do not touch `tests/test_clamp.py` or any other existing test file.

## Interfaces
- Consumes: `_chat_completion`, `SECTOR_SYNTHESIS_SCHEMA` from `pipeline/analyst.py` (task 002); `LOCAL_MODEL` from `config/models.py` (task 001).
- Produces: a repeatable smoke test any future session can re-run to re-confirm the local backend still works, without needing to re-derive verification steps from scratch.

## Constraints
- No Groq API calls anywhere in this test — it exercises the local backend only.
- If the local Ollama server isn't reachable at all (connection refused, not just missing model), the test should skip with a clear message too, not fail/error — this is a smoke test gated on real local infrastructure being present, not a hard CI requirement.
- Don't attempt to start Ollama, pull models, or run `ollama create` from within the test — it only checks/exercises what's already there.

## Verification
Run `py -m pytest tests/test_local_backend_smoke.py -v`. Two acceptable passing outcomes, both are valid evidence:
- **If Ollama + the Q6_K model are already set up on this machine:** the test must actually run both real calls and pass, with the JSON-schema assertion genuinely exercised — this is the real evidence CONTEXT.md asks for. Paste the actual pytest output (not just exit code) into Evidence.
- **If they are not yet set up:** the test must skip (not error) with the exact setup-instructions message from RESEARCH.md §2 visible in the pytest output — paste that skip message into Evidence, and note explicitly that the primary-risk verification remains an open Alfonso-owned manual checkpoint until Ollama + the Q6_K model are actually provisioned on his machine (mirror the phrasing style of the two existing open checkpoints already tracked in `.context/STATE.md`).

Either outcome is acceptable for this task's own completion (the test correctly reports its own state); do not fabricate a pass if the model genuinely isn't available.

## Evidence
