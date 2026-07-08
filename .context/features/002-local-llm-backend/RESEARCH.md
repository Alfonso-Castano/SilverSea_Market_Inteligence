# Research — Local LLM Backend (Ollama + Qwen3-32B)

`--thorough` was passed; this is genuinely first-in-repo territory (no prior Ollama/local-model integration exists anywhere in this codebase), so a dedicated research pass ran before decomposition. Findings below directly shaped the task breakdown.

## 1. OpenAI-compatible endpoint vs. native `/api/chat` — resolved in favor of the native `ollama` Python library

CONTEXT.md's constraint says to "reuse/mirror the `groq` SDK's OpenAI-compatible interface against Ollama's OpenAI-compatible endpoint rather than introducing a second, differently-shaped LLM client abstraction," but CONTEXT.md *also* requires genuine schema-constrained structured outputs (not loose `json_object` mode) as "the primary risk being tested." These two constraints turned out to be in tension:

- Ollama does expose `/v1/chat/completions` (OpenAI-compatible), and the `openai` Python SDK can point at it via `base_url="http://localhost:11434/v1"`, `api_key="ollama"` (placeholder, ignored).
- However, per Ollama's own docs (`docs.ollama.com/api/openai-compatibility`), **`response_format={"type": "json_schema", "json_schema": {...}}` is explicitly NOT supported on `/v1/chat/completions`** — only loose JSON mode is. Some third-party writeups show `client.beta.chat.completions.parse()` "working" against Ollama, but that's the OpenAI SDK client-side helper constructing a `json_schema`-typed `response_format` under the hood — the same unsupported field, so it's unreliable to depend on.
- Genuine schema-constrained structured output **is** confirmed, documented, and stable via Ollama's **native** `/api/chat` endpoint's `format` parameter, called through the native `ollama` Python package (`ollama.chat(model=..., messages=..., format=<json-schema-dict>, options={...})`). This is what Ollama's own structured-outputs docs and blog post demonstrate, and it's been supported since Ollama 0.5.0+.

**Resolution:** the local backend uses the native `ollama` Python package (a new, small dependency), not an `openai`-SDK-against-Ollama shim. This is the smallest deviation from CONTEXT.md's "no second client abstraction" intent that still satisfies the (higher-priority, explicitly-flagged-as-primary-risk) genuine-schema-enforcement requirement — the two Groq and local branches are unified behind one dispatch helper in `analyst.py` (see task 002) rather than becoming two parallel LLM-calling code paths scattered across the file. Both branches keep exactly the same call signature (system prompt, user message, max tokens, optional JSON schema in/JSON string out), so call sites don't need to know which backend is live.

## 2. Qwen3-32B at Q6_K — not available as a standard Ollama library tag; needs a manual GGUF import

Checked the official Ollama library (`ollama.com/library/qwen3`) tag list directly. The `32b` size only ships as:
- `qwen3:32b` (= `qwen3:32b-q4_K_M`, ~20GB, the default)
- `qwen3:32b-q8_0`
- `qwen3:32b-fp16`

**No `q6_K` tag exists in the official library.** CONTEXT.md's open question #2 ("standard Ollama quantization or custom GGUF import") is resolved: it needs a custom import. The standard path is:
1. Download a Q6_K GGUF of Qwen3-32B from a reputable third-party quantizer on Hugging Face (e.g. `bartowski/Qwen3-32B-GGUF`, which publishes the full quant ladder including Q6_K) — this is a ~23GB file download, not something a coding agent should attempt.
2. Write a one-line `Modelfile`: `FROM ./Qwen3-32B-Q6_K.gguf`
3. `ollama create qwen3-32b-q6k -f Modelfile` to register it under a local tag name.
4. `ollama run qwen3-32b-q6k` / `ollama list` to confirm.

This whole sequence (multi-GB download, GGUF import, local tag naming) is a one-time, host-machine setup action outside the repo, matching CONTEXT.md's own guess on its open question #3. **It is treated as an Alfonso-owned manual prerequisite, not a task file** — no task in this feature attempts to install Ollama, download the GGUF, or run `ollama create`. Task 003 (verification) assumes this is already done and checks for it explicitly (`ollama list` must show the configured tag) rather than attempting to provision it — if missing, the executor reports BLOCKED with these exact steps rather than guessing a substitute.

**Local model tag name used throughout the code:** `qwen3-32b-q6k` (configurable via env var, see task 001), matching the convention above.

## 3. Context window sizing

`pipeline/scraper.py`'s `smart_truncate()` caps each source at 6000 chars. A sector can have up to ~10 sources passing the filter (real runs have gone as high as 9-11 sources/sector per `.context/DECISIONS.md`'s 2026-06-19 entry), so the worst-case per-sector extraction input is roughly 10 × 6000 = 60,000 chars ≈ 15,000 tokens (English averages ~4 chars/token), plus the ~300-token system prompt and up to 2000 output tokens reserved (`max_tokens=2000` at every call site). That's comfortably under 20k tokens total, but with real margin needed for variance (multi-byte content, longer sources, the object-wrapper overhead described below).

Qwen3-32B supports native context up to 32,768 tokens (larger via YaRN scaling, not needed here). **Recommendation: `num_ctx=32768`**, configurable via an env var so it can be tuned down if VRAM headroom (Q6_K weights ≈23GB on a 32GB card) proves tighter than expected once a real per-sector call is exercised. This resolves CONTEXT.md's open question on context sizing.

## 4. `pipeline/analyst.py` — exact call sites confirmed by full read

Three Groq call sites, all via `client.chat.completions.create(model=GROQ_MODEL, ...)`:
- `_extract_sector()` (line ~150): free-text output, no `response_format`, `max_tokens=2000`.
- `_synthesize_sector()` (line ~172): `response_format={"type": "json_object"}`, `max_tokens=2000`. Expects a JSON array `[{"entity":..., "signal":..., "source_name":...}]`, but the parsing code (`if isinstance(result, dict): result = result.get("signals", list(result.values())[0] ...)`) already tolerates a dict-wrapped result — this existing tolerance is exactly what lets the local backend emit an object-wrapped `{"signals": [...]}` shape (needed because Ollama's native `format` schemas are objects, not bare arrays — see below) without touching the Groq-path parsing logic at all.
- `_synthesize_summary()` (line ~223): `response_format={"type": "json_object"}`, `max_tokens=2000`. Expects a top-level object `{"executive_summary": [...], "opportunities": [...], "synthesis": [...]}` — already object-shaped, no wrapping change needed for the local schema.

`analyse()` (line ~333) currently does `client = Groq(api_key=os.environ["GROQ_API_KEY"])` unconditionally — this must become conditional on `LLM_BACKEND`, both because a local-only run shouldn't require a Groq key at all, and because that's the only way `LLM_BACKEND=local` can function standalone (not just as a bonus fix — it's load-bearing for this feature).

## 5. `config/models.py` and other Groq-model references

`config/models.py` is a 2-line file: `GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"`. It's the single source of truth imported only by `pipeline/analyst.py` (confirmed via repo-wide grep — `pipeline/weekly.py`, `pipeline/feedback.py`, the GitHub Actions workflows, and various `.context/` docs reference `GROQ_MODEL`/`GROQ_API_KEY` only in passing text/docs, not as a second import site). No other file needs a mirrored model constant — `config/models.py` is the correct (and only) place to add `LLM_BACKEND`, `LOCAL_MODEL`, and `LOCAL_NUM_CTX`, resolving CONTEXT.md's open question #4.

## Judgment calls made here (flagged, not silently assumed)

- Local backend implemented via the native `ollama` package rather than an OpenAI-SDK/base_url shim, for the schema-reliability reason in §1. This is a real deviation worth Alfonso's awareness even though it doesn't reopen CONTEXT.md's decision (env-var switch, Groq stays default) — only the "what the local branch is built from" detail.
- Ollama installation, GGUF download, and `ollama create` are explicitly NOT task files — treated as Alfonso's manual prerequisite, confirmed against CONTEXT.md's own stated guess.
- `num_ctx=32768` is a recommendation with headroom, not a measured hard requirement — task 003's real local test is what actually validates it.
