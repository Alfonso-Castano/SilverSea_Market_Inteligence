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
