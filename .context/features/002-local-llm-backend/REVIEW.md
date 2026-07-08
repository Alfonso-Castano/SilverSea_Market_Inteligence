# Review: 002-local-llm-backend

**Base:** 168810eeb12c6e9d5bd257c0b0df9620315d765e
**Reviewed:** 2026-07-08
**Verdict: PASS**

## 1. Task-level check

| Task | Spec match |
|---|---|
| 001 — `ollama` dep + `config/models.py` constants | Matches exactly. `requirements.txt` appends `ollama` as the last line, existing lines untouched. `config/models.py` rewritten verbatim to the spec (`GROQ_MODEL` preserved unchanged, `LLM_BACKEND`/`LOCAL_MODEL`/`LOCAL_NUM_CTX` added with identical env var names/defaults). One inaccuracy surfaced in the task file's own stated research, not in the implementation: the task claimed "no other file currently imports from `config/models.py` besides `pipeline/analyst.py`," but `pipeline/feedback.py` and `pipeline/weekly.py` both do (`from config.models import GROQ_MODEL`). This didn't cause a wrong implementation — the constraint ("don't add anything speculative for other call sites") was correctly honored regardless — but it means those two files still hardcode the Groq path with no `LLM_BACKEND` awareness. That's consistent with CONTEXT.md's explicit scope ("this feature's local backend option applies to `pipeline/analyst.py`'s LLM call sites" only), so not a scope violation, just a research-accuracy note worth flagging. |
| 002 — local backend dispatch in `analyst.py` | Matches. `_chat_completion` helper, two JSON schemas, conditional `ollama` import, conditional Groq client construction, and all 3 call sites rewired exactly as specified. The task's own logged "deliberate deviation" (schema passed unconditionally to `_chat_completion` at both synthesis sites, gated on presence not value) was independently re-verified against the real diff in this pass — confirmed correct: `_chat_completion`'s Groq branch only sets `response_format` based on `json_schema is not None`, so Groq's `response_format={"type":"json_object"}` on both synthesis calls is byte-for-byte preserved regardless of the schema's *content*, while the local branch consumes the schema's *content* via `format=`. The `user_message` local-only hints remain correctly gated on `LLM_BACKEND == "local"` literally (not unconditionally), so no user-visible prompt change reaches Groq. |
| 003 — smoke test | Matches. Test skips cleanly on missing package/server/model, runs two real calls otherwise, doesn't touch `test_clamp.py`. |
| 004 — README docs | Matches. Env var table rows added after `GROQ_API_KEY` without reordering; new `## Local LLM Setup (Optional)` section with the full 7-step runbook, correct GGUF source/tag/Modelfile content. |

## 2. Decision coverage (CONTEXT.md Implementation Decisions)

- Config-switchable via `LLM_BACKEND` env var, default `groq` — confirmed (`config/models.py`, verified live).
- Ollama + Qwen3-32B Q6_K as the chosen stack — confirmed in `config/models.py` defaults, README runbook, and task 001/004 evidence.
- Native `ollama` package (not OpenAI-SDK shim) — confirmed: `import ollama`, `ollama.chat(...)` used directly in `_chat_completion`, no `openai` package or `base_url` shim added anywhere in the diff.
- Groq path stays byte-for-byte unchanged — confirmed by direct code inspection (see task 002 row above) and by the unchanged `model=GROQ_MODEL`/`max_tokens`/`response_format` construction in the non-local branch of `_chat_completion`.
- No changes to the 3-phase extract→synthesize→summary architecture — confirmed; `analyse()`'s control flow, `_extract_sector`/`_synthesize_sector`/`_synthesize_summary`'s call order, and `_clamp_opportunity_scores`/`_generate_implications`/`_derive_competition_risks` are untouched apart from the dispatch-site rewiring.
- No filter AI changes — confirmed; `pipeline/filter.py` does not appear in the diff at all.
- No scheduling/automation work — confirmed; nothing touches Task Scheduler, cron, or `main.py`'s invocation surface.
- GPU correction (RTX 5090, not 5070) — grepped repo-wide for "5070"; zero hits outside this feature's own CONTEXT.md discussion history (which correctly documents the correction), confirming no stray wrong-GPU reference leaked into code or other docs.

## 3. Goal alignment

The feature's one-sentence goal — give `pipeline/analyst.py` a config-switchable local-LLM backend as an opt-in alternative to Groq, without changing default behavior for existing runs — is satisfied as a whole. All three LLM call sites route through one dispatch point (`_chat_completion`) keyed on `LLM_BACKEND`; the default (unset or `"groq"`) path is provably unchanged; the local path is real (native `ollama.chat`, genuine JSON-schema enforcement via `format=`, not just prompt-level hinting) and is independently verifiable via the smoke test once Ollama is actually provisioned. The primary risk named in CONTEXT.md (real schema-compliant JSON from the local model) is correctly left as an open, explicitly-labeled Alfonso-owned manual checkpoint rather than fabricated as verified — task 003's evidence is honest about a clean skip, not a false pass.

## 4. Evidence gate — fresh evidence gathered this pass

```
$ py -c "import ast; ast.parse(open('pipeline/analyst.py').read()); print('SYNTAX OK')"
SYNTAX OK

$ py -c "from pipeline import analyst; print(analyst.LLM_BACKEND, analyst.SECTOR_SYNTHESIS_SCHEMA is not None, analyst.SUMMARY_SCHEMA is not None)"
groq True True

$ py -c "from config.models import GROQ_MODEL, LLM_BACKEND, LOCAL_MODEL, LOCAL_NUM_CTX; print(GROQ_MODEL, LLM_BACKEND, LOCAL_MODEL, LOCAL_NUM_CTX)"
meta-llama/llama-4-scout-17b-16e-instruct groq qwen3-32b-q6k 32768

$ py -m pytest tests/test_local_backend_smoke.py -v -rs
tests/test_local_backend_smoke.py::test_local_backend_free_text_call_returns_nonempty_string SKIPPED [ 50%]
tests/test_local_backend_smoke.py::test_local_backend_schema_call_returns_valid_synthesis_json SKIPPED [100%]
SKIPPED [1] tests\test_local_backend_smoke.py:93: local Ollama server is not reachable (Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible. https://ollama.com/download)
SKIPPED [1] tests\test_local_backend_smoke.py:109: local Ollama server is not reachable (Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible. https://ollama.com/download)
2 skipped in 12.66s
Exit code: 0

$ py -m pytest tests/test_clamp.py -v
6 passed in 10.78s
Exit code: 0

$ py -c "content = open('README.md').read(); print(all(s in content for s in ['LLM_BACKEND', 'LOCAL_LLM_MODEL', 'LOCAL_LLM_NUM_CTX', 'Local LLM Setup', 'bartowski/Qwen3-32B-GGUF', 'ollama create', 'test_local_backend_smoke']))"
True
```

No Groq quota was spent — the Groq path was verified by code inspection only, per CONTEXT.md's explicit constraint. The clean skip on `test_local_backend_smoke.py` is the expected, acceptable outcome on this dev machine (no live Ollama server) and matches this feature's own design — not treated as a failure.

## 5. Discrepancies

None blocking. One non-blocking note carried forward (not a fix task, just worth flagging to Alfonso): task 001's evidence claimed no file besides `pipeline/analyst.py` imports from `config/models.py`; in fact `pipeline/feedback.py` and `pipeline/weekly.py` also import `GROQ_MODEL` from it. This didn't affect correctness of what was built (both files remain Groq-only, which is in-scope and expected — `LLM_BACKEND=local` only affects the three `analyst.py` call sites per CONTEXT.md's stated scope), but it does mean `feedback.py`/`weekly.py` will keep requiring `GROQ_API_KEY` even on a `LLM_BACKEND=local` run — worth noting as a known limitation, not something this feature was scoped to fix.

## Overall: PASS

All 4 tasks match spec, all CONTEXT.md decisions are reflected in code, the feature achieves its stated goal, and the evidence gate was run fresh in this pass with all commands exiting 0 and producing the expected output.
