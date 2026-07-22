# Task 001: Provider registry in config/models.py

**Status:** done
**Depends on:** none
**Model tier:** cheap — the exact registry content is fully specified below (transcription plus
verification); no design judgment left for the executor.

## Files
- Modify: `config/models.py`

## What to do

Replace the current 1-line file with the content below verbatim (adjust only if the file has
drifted from what's shown — it was a 2-line file as of this feature's base commit `ad81ca1`, so
drift is unlikely):

```python
# config/models.py — Single source of truth for LLM model selection and provider registry
import os

# GROQ_MODEL stays a standalone constant (not folded into PROVIDERS below) because
# pipeline/feedback.py and pipeline/weekly.py import it directly for their own,
# independent Groq-only LLM calls — out of this feature's scope (see
# .context/features/007-multi-provider-llm-backend/RESEARCH.md §7). Do not remove it.
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# LLM_DEFAULT: set to a PROVIDERS (or "local") key to silently pick a backend with no
# prompt, regardless of how many providers have a configured API key — the
# engineer-accessible switch for wherever this pipeline is hosted (dev machine, company
# server, cloud host). Overridden by --llm=<key> on the command line. See
# pipeline/llm_select.py for the full resolution order.
LLM_DEFAULT = os.environ.get("LLM_DEFAULT", "").strip().lower()

# Every entry here is genuinely OpenAI-API-shaped (chat.completions.create,
# response_format={"type": "json_object"}) — pipeline/analyst.py dispatches all of them
# through one generic openai.OpenAI(base_url=..., api_key=...) branch, no per-provider
# code. DeepSeek is the default (see LLM_DEFAULT's fallback in llm_select.py): confirmed
# reachable from mainland China without a proxy (unlike Groq, whose console 403s from
# China), cheapest, most generous free grant, lowest signup friction of the candidates
# researched — see RESEARCH.md §1.
PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "key_env": "DEEPSEEK_API_KEY",
        # deepseek-chat/deepseek-reasoner deprecate 2026-07-24 15:59 UTC; deepseek-v4-flash
        # is their current non-thinking-mode default model — see RESEARCH.md §1.
        "model": "deepseek-v4-flash",
    },
    "groq": {
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    },
    "qwen": {
        "label": "Qwen (DashScope)",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "key_env": "DASHSCOPE_API_KEY",
        "model": "qwen-plus",
    },
    "kimi": {
        "label": "Kimi (Moonshot)",
        "base_url": "https://api.moonshot.ai/v1",
        "key_env": "MOONSHOT_API_KEY",
        # Model naming is unsettled across Moonshot's own docs as of this writing (kimi-k3,
        # kimi-k2.6, kimi-k2.5 all appear) — kimi-k3 is the most-recent name found on the
        # official docs domain. Confirm against platform.kimi.ai before relying on this in
        # production; this entry is registered but not live-verified this round (see
        # RESEARCH.md §4, §8).
        "model": "kimi-k3",
    },
}

# Local backend (Ollama) — reused from feature/002-local-llm-backend, never verified
# against a real model on any machine; kept exactly as unverified (see
# .context/STATE.md's Known Bugs section). Not part of PROVIDERS above since it has no
# base_url/api_key shape — pipeline/analyst.py and pipeline/llm_select.py both special-case
# the string "local" instead.
LOCAL_MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen3-32b-q6k")
LOCAL_NUM_CTX = int(os.environ.get("LOCAL_LLM_NUM_CTX", "32768"))
```

## Interfaces
- `PROVIDERS`: `dict[str, dict]` — each value has keys `label` (str), `base_url` (str),
  `key_env` (str, the env var name holding that provider's API key), `model` (str, the model
  name string to send in `chat.completions.create(model=...)`). Consumed by
  `pipeline/analyst.py` (Task 003) and `pipeline/llm_select.py` (Task 004).
- `LLM_DEFAULT`: `str`, already lowercased/stripped, empty string if unset. Consumed by
  `pipeline/llm_select.py` (Task 004).
- `GROQ_MODEL`: unchanged, still consumed by `pipeline/feedback.py` and `pipeline/weekly.py` —
  do not remove or rename it.
- `LOCAL_MODEL`, `LOCAL_NUM_CTX`: unchanged from `feature/002-local-llm-backend`'s shape
  (`git show feature/002-local-llm-backend:config/models.py` to compare) — consumed by
  `pipeline/analyst.py`'s local/Ollama branch (Task 003).

## Constraints
- Do not add a `"local"` entry into the `PROVIDERS` dict — it has a structurally different shape
  (no `base_url`/`api_key`, uses `LOCAL_MODEL`/`LOCAL_NUM_CTX` instead) and both consumers treat
  `"local"` as a special-cased string, not a `PROVIDERS` lookup. Mixing it in would force
  Task 003/004 to special-case around a dict entry that doesn't match the others' shape.
  Do not build any dynamic provider-loading/plugin mechanism — this is a static dict, per
  CONTEXT.md's "no new abstraction beyond what's needed" constraint.
- Do not touch any other file in this task.

## Verification
1. `py -c "import ast; ast.parse(open('config/models.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "from config.models import PROVIDERS, LLM_DEFAULT, GROQ_MODEL, LOCAL_MODEL, LOCAL_NUM_CTX; assert set(PROVIDERS) == {'deepseek','groq','qwen','kimi'}; assert all({'label','base_url','key_env','model'} <= set(v) for v in PROVIDERS.values()); assert GROQ_MODEL == 'meta-llama/llama-4-scout-17b-16e-instruct'; print('OK', PROVIDERS.keys())"`
3. Confirm `pipeline/feedback.py`'s and `pipeline/weekly.py`'s existing `from config.models import
   GROQ_MODEL` still import cleanly (proves this change didn't break the two files this feature
   deliberately doesn't touch): `py -c "import pipeline.feedback, pipeline.weekly; print('OK, both still import')"`

## Evidence

1. `py -c "import ast; ast.parse(open('config/models.py', encoding='utf-8').read()); print('syntax OK')"` → `syntax OK`
2. `py -c "from config.models import PROVIDERS, LLM_DEFAULT, GROQ_MODEL, LOCAL_MODEL, LOCAL_NUM_CTX; assert set(PROVIDERS) == {'deepseek','groq','qwen','kimi'}; assert all({'label','base_url','key_env','model'} <= set(v) for v in PROVIDERS.values()); assert GROQ_MODEL == 'meta-llama/llama-4-scout-17b-16e-instruct'; print('OK', PROVIDERS.keys())"` → `OK dict_keys(['deepseek', 'groq', 'qwen', 'kimi'])`
3. `py -c "import pipeline.feedback, pipeline.weekly; print('OK, both still import')"` → `OK, both still import` (exit 0)

File replaced exactly as specified (82 lines replacing the prior 2-line file). No `"local"` entry added to `PROVIDERS`. No other files touched.
