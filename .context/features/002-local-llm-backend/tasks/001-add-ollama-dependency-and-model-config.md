# Task 001: Add `ollama` dependency and backend config constants

**Status:** pending
**Depends on:** none
**Model tier:** cheap — the exact code is specified below; the executor's job is transcription plus verification.

## Files
- Modify: `requirements.txt`
- Modify: `config/models.py`

## What to do

1. In `requirements.txt`, add a new line `ollama` (the native Ollama Python package — NOT the `openai` package; see `.context/features/002-local-llm-backend/RESEARCH.md` §1 for why). Keep the existing lines and their order unchanged; just append.

2. Rewrite `config/models.py` to:

```python
# config/models.py — Single source of truth for LLM model selection
import os

GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# LLM_BACKEND selects which backend pipeline/analyst.py calls: "groq" (default,
# unchanged production/dev path) or "local" (Ollama running Qwen3-32B on
# Alfonso's own hardware — free, but requires local Ollama setup; see
# .context/features/002-local-llm-backend/RESEARCH.md).
LLM_BACKEND = os.environ.get("LLM_BACKEND", "groq").strip().lower()

# Local tag name the model was registered under via `ollama create` (Q6_K GGUF
# import — see RESEARCH.md §2). Configurable in case Alfonso names it differently.
LOCAL_MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen3-32b-q6k")

# Context window for the local model. 32768 covers the worst-case per-sector
# extraction input (see RESEARCH.md §3) with headroom; override if VRAM
# headroom proves tighter than expected.
LOCAL_NUM_CTX = int(os.environ.get("LOCAL_LLM_NUM_CTX", "32768"))
```

## Interfaces
- Produces: `LLM_BACKEND`, `LOCAL_MODEL`, `LOCAL_NUM_CTX` constants in `config/models.py`, importable by `pipeline/analyst.py` (task 002) alongside the existing `GROQ_MODEL`.

## Constraints
- Do not change the existing `GROQ_MODEL` value or remove it.
- No other file currently imports from `config/models.py` besides `pipeline/analyst.py` (confirmed via repo-wide grep during research) — don't add anything speculative for other call sites.

## Verification
Run `py -c "from config.models import GROQ_MODEL, LLM_BACKEND, LOCAL_MODEL, LOCAL_NUM_CTX; print(GROQ_MODEL, LLM_BACKEND, LOCAL_MODEL, LOCAL_NUM_CTX)"` — must exit 0 and print `meta-llama/llama-4-scout-17b-16e-instruct groq qwen3-32b-q6k 32768` (defaults, since no env vars are set in this shell). Then run `pip show ollama` (or `py -m pip show ollama` if `pip` isn't on PATH) — must exit 0 confirming the package installed from `requirements.txt` (install it first with `pip install -r requirements.txt` if not already present).

## Evidence
