# Task 002: Wire a local (Ollama) backend into `pipeline/analyst.py`'s three LLM call sites

**Status:** done
**Depends on:** 001
**Model tier:** quality — first local-model integration in this repo; the primary risk being tested (genuine schema-constrained JSON on a real local model) lives here, and the Groq path must stay byte-for-byte unchanged.

## Files
- Modify: `pipeline/analyst.py`

## What to do

Read `.context/features/002-local-llm-backend/RESEARCH.md` first (§1, §4) — it explains why this uses the native `ollama` package's `/api/chat` + `format` (JSON-schema) mechanism for the local branch rather than an OpenAI-SDK/base_url shim, and exactly which 3 call sites and line ranges are affected.

1. **Imports.** Add, near the existing `from groq import Groq` import:
   ```python
   try:
       import ollama
       OLLAMA_AVAILABLE = True
   except Exception:
       OLLAMA_AVAILABLE = False
   ```
   Update the `from config.models import GROQ_MODEL` line to also import `LLM_BACKEND, LOCAL_MODEL, LOCAL_NUM_CTX`.

2. **Add one dispatch helper**, placed above `_extract_sector` (which is the first function that will call it):
   ```python
   def _chat_completion(client, system_prompt: str, user_message: str, max_tokens: int, json_schema: dict | None = None) -> str:
       """Dispatch one LLM call to the configured backend (LLM_BACKEND: 'groq' | 'local').
       Returns the raw text content. json_schema, when given, is a JSON-schema dict describing
       the exact expected structured output — enforced via Ollama's native structured-outputs
       'format' field on the local backend. The Groq path is unchanged: it keeps using its
       existing loose response_format={"type": "json_object"} whenever json_schema is given,
       and a plain completion otherwise. This must not change Groq's behavior at all when
       LLM_BACKEND is unset or "groq"."""
       if LLM_BACKEND == "local":
           if not OLLAMA_AVAILABLE:
               raise RuntimeError("LLM_BACKEND=local but the 'ollama' package is not installed (see requirements.txt)")
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
           model=GROQ_MODEL,
           messages=[
               {"role": "system", "content": system_prompt},
               {"role": "user", "content": user_message},
           ],
           max_tokens=max_tokens,
           **kwargs,
       )
       return response.choices[0].message.content
   ```

3. **Two JSON schemas**, defined as module-level dicts near the existing `SECTOR_SYNTHESIS_PROMPT`/`SUMMARY_PROMPT` constants, used only on the local branch:
   - `SECTOR_SYNTHESIS_SCHEMA`: an **object** schema (not a bare array — Ollama's native `format` schemas are objects) with one required property `signals`, an array of objects each with required string properties `entity`, `signal`, `source_name`. This intentionally matches the dict-wrapped shape `_synthesize_sector`'s parsing already tolerates (`result.get("signals", ...)`) — confirm this by re-reading that function before writing the schema, don't just trust this task's description.
   - `SUMMARY_SCHEMA`: an object schema matching `SUMMARY_PROMPT`'s existing top-level shape (`executive_summary`: array of strings, `opportunities`: array of objects with `title`, `source_quote`, `named_entry_point`, `concrete_action`, `deadline`, `source_name`, `product_fit`, `scores` (object with the 5 `_SCORE_DIMENSIONS` as integer properties), `total_score`; `synthesis`: array of strings).
   - When calling `_chat_completion` for these two call sites with `LLM_BACKEND == "local"`, append one short line to the *user message* (not the shared prompt constant used by both backends) instructing the model to return an object with a top-level `signals` field (sector synthesis) — do this by building the user_message string conditionally, e.g. only add the hint when `LLM_BACKEND == "local"`. Do NOT modify `SECTOR_SYNTHESIS_PROMPT`, `SUMMARY_PROMPT`, or `SECTOR_EXTRACT_PROMPT` themselves — those are shared system prompts and must stay identical for the Groq path.

4. **Wire the 3 call sites** to use `_chat_completion` instead of calling `client.chat.completions.create(...)` directly:
   - `_extract_sector`: `_chat_completion(client, SECTOR_EXTRACT_PROMPT, user_message, 2000)` (no `json_schema` — free text, same as today for both backends).
   - `_synthesize_sector`: `_chat_completion(client, SECTOR_SYNTHESIS_PROMPT, user_message, 2000, json_schema=SECTOR_SYNTHESIS_SCHEMA if LLM_BACKEND == "local" else None)`, then `json.loads(...)` the returned string exactly as today — the existing dict-unwrap logic (`result.get("signals", ...)`) already handles both shapes, leave it unchanged.
   - `_synthesize_summary`: same pattern with `SUMMARY_SCHEMA`.

5. **Make the Groq client conditional** in `analyse()`. Currently:
   ```python
   client = Groq(api_key=os.environ["GROQ_API_KEY"])
   ```
   This must not run when `LLM_BACKEND == "local"` — a local-only run must not require `GROQ_API_KEY` to be set at all (this is load-bearing for the feature, not a bonus fix). Change to something like:
   ```python
   client = Groq(api_key=os.environ["GROQ_API_KEY"]) if LLM_BACKEND != "local" else None
   ```
   `client` is passed through unchanged to `_extract_sector`/`_synthesize_sector`/`_synthesize_summary`, which ignore it entirely on the local branch (see `_chat_completion` above — it only touches `client` in the non-local branch).

## Interfaces
- Consumes: `LLM_BACKEND`, `LOCAL_MODEL`, `LOCAL_NUM_CTX` from `config/models.py` (task 001).
- Produces: `_chat_completion(...)` as the single LLM-dispatch point in `pipeline/analyst.py`; `SECTOR_SYNTHESIS_SCHEMA`/`SUMMARY_SCHEMA` as the local-only JSON schemas — task 003's smoke test imports these two schemas directly to validate against real Ollama output.

## Constraints
- The Groq path (`LLM_BACKEND` unset or `"groq"`) must behave byte-for-byte identically to before this change — same prompts, same `max_tokens`, same `response_format` usage, same parsing. Verify this by diffing the Groq branch of `_chat_completion` against the original 3 call sites.
- Do not touch `SECTOR_EXTRACT_PROMPT`, `SECTOR_SYNTHESIS_PROMPT`, `SUMMARY_PROMPT`, `_clamp_opportunity_scores`, `_generate_implications`, `_derive_competition_risks`, or anything in `main.py` / `pipeline/vectorstore.py` — none of that is in scope for this feature.
- Do not attempt to install Ollama, pull/import the Q6_K model, or run any `ollama` CLI command as part of this task — that's an Alfonso-owned manual prerequisite (RESEARCH.md §2). This task only needs the `ollama` Python package importable (from task 001) to write correct code; it does not need a live Ollama server to complete.

## Verification
Stage-by-stage per CLAUDE.md — no Groq quota spent here:
1. `py -c "import ast; ast.parse(open('pipeline/analyst.py').read())"` — must exit 0 (syntax-valid).
2. `py -c "from pipeline import analyst; print(analyst.LLM_BACKEND, analyst.SECTOR_SYNTHESIS_SCHEMA is not None, analyst.SUMMARY_SCHEMA is not None)"` — must exit 0 and print `groq True True` (default backend, both schemas defined).
3. With `LLM_BACKEND` still unset/`groq`, confirm `analyst._chat_completion`'s non-local branch is unchanged by inspection — diff the constructed `client.chat.completions.create(...)` call against the original 3 call sites' arguments (same `model=GROQ_MODEL`, same `max_tokens`, same `response_format` conditions). Note in Evidence that this was checked, since there's no live Groq call to run without spending quota.

## Evidence

**Check 1+2:**
```
$ py -c "import ast; ast.parse(open('pipeline/analyst.py').read()); print('SYNTAX OK')"
SYNTAX OK
$ py -c "from pipeline import analyst; print(analyst.LLM_BACKEND, analyst.SECTOR_SYNTHESIS_SCHEMA is not None, analyst.SUMMARY_SCHEMA is not None)"
groq True True
```

**Check 3 — Groq-branch inspection vs. original 3 call sites (no live call, no quota spent):**
- `_extract_sector`: identical (`_chat_completion(..., 2000)`, no schema → no `response_format`, matches original).
- `_synthesize_sector` / `_synthesize_summary`: identical `model`/`max_tokens`/`response_format={"type":"json_object"}` — confirmed via direct diff read by the dispatching session.
- `analyse()`'s Groq client now conditional on `LLM_BACKEND != "local"` — required so a local-only run never needs `GROQ_API_KEY`.

**Deliberate deviation from this task file's literal point-4 wording (flagged by the executor, verified by the dispatching session via `git diff pipeline/analyst.py`):** the task text said to pass `json_schema=SCHEMA if LLM_BACKEND == "local" else None` at the two synthesis call sites. Taken literally this sets `json_schema=None` on the Groq path, which — given `_chat_completion` only sets `response_format` when `json_schema is not None` — would silently drop Groq's `response_format={"type":"json_object"}`, violating this same task's overriding "Groq path byte-for-byte identical" constraint. Resolved by passing the schema **unconditionally** to `_chat_completion` at both synthesis sites: the Groq branch only checks the schema's *presence* (preserving old behavior exactly), while the local branch consumes its *content* via `format=`. The `user_message` local-only hints remain correctly gated on `LLM_BACKEND == "local"`. Verified correct and intentional — approved.
