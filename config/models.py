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
