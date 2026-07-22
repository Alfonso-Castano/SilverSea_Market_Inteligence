# config/models.py — Single source of truth for LLM model selection and provider registry
import os

# GROQ_MODEL stays a standalone constant (not folded into PROVIDERS below) because
# pipeline/feedback.py and pipeline/weekly.py import it directly for their own,
# independent Groq-only LLM calls — out of this feature's scope (see
# .context/features/007-multi-provider-llm-backend/RESEARCH.md §7). Do not remove it.
#
# meta-llama/llama-4-scout-17b-16e-instruct was removed from Groq's catalog entirely
# (confirmed via a live models.list() call, 2026-07-22 — 404 model_not_found, independent
# of any client library). Reverted to llama-3.3-70b-versatile, this project's original,
# historically-validated model (21/25 quality score, see .context/DECISIONS.md's 2026-06-19
# entry) before Groq deprecated *that* model and llama-4-scout replaced it for TPM headroom.
# Confirmed live on this account's model list as of this fix.
GROQ_MODEL = "llama-3.3-70b-versatile"

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
        # Kept in sync with GROQ_MODEL above — see its comment for why this changed.
        "model": "llama-3.3-70b-versatile",
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
    "openrouter-nemotron": {
        "label": "OpenRouter (NVIDIA Nemotron Super, free)",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        # Default OpenRouter entry — see RESEARCH.md §5. NVIDIA is not named among the
        # providers OpenRouter enforces China-account-blocking for (unlike OpenAI/
        # Anthropic/Google-provided models — see RESEARCH.md §2), and this is the more
        # token-efficient of the two NVIDIA free JSON-capable candidates under this
        # pipeline's real per-signal output shape (see RESEARCH.md §4). Requires the
        # dispatch-side reasoning-disable + JSON-array wrapper-hint fix in
        # pipeline/analyst.py (see feature 008's task 002) — without it, this model
        # (like its sibling below) burns most of its output budget on an internal
        # reasoning trace and returns malformed/incomplete JSON.
    },
    "openrouter-nemotron-nano": {
        "label": "OpenRouter (NVIDIA Nemotron Nano, free)",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "model": "nvidia/nemotron-nano-9b-v2:free",
        # Non-default alternative — also China-safe (see RESEARCH.md §2) and confirmed
        # working with the same reasoning-disable + wrapper-hint fix as the entry above,
        # but ~7x more verbose per extracted signal in live testing (RESEARCH.md §4),
        # leaving meaningfully less headroom under max_tokens=2000 for sectors with many
        # real signals. Do not promote this to LLM_DEFAULT without re-testing against a
        # large, real multi-source sector first.
    },
    "company-qwen-flash": {
        "label": "Company Qwen (paid) — 3.6 Flash",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_env": "COMPANY_QWEN_API_KEY",
        "model": "qwen3.6-flash",
        # China-domestic DashScope endpoint, genuinely distinct from the existing "qwen"
        # entry above (dashscope-intl.aliyuncs.com, a different account/region) — not a
        # duplicate. Model string independently confirmed twice: matches Alibaba Cloud's
        # official Model Studio docs AND was live-smoke-tested successfully against the
        # real company key in the prior planning session (see RESEARCH.md §6). Paid —
        # label says so on purpose; do not make this LLM_DEFAULT.
    },
    "company-qwen-plus": {
        "label": "Company Qwen (paid) — 3.7 Plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_env": "COMPANY_QWEN_API_KEY",
        "model": "qwen3.7-plus",
        # Same key/endpoint as company-qwen-flash above. Model string matches Alibaba
        # Cloud's official Model Studio docs (a current, real flagship model) but has NOT
        # been live-tested against the real company account/key — confirm it actually
        # authenticates before relying on this in production (see RESEARCH.md §6, same
        # caveat this registry already carries for kimi-k3 above). Two other guessed
        # strings from this feature's original scope (qwen3.6-plus, qwen3.7-flash) were
        # deliberately NOT added here — documentation research found no evidence either
        # exists in DashScope's current catalog. If a human confirms one is real, adding
        # it is a one-entry follow-up to this dict, not a new feature.
    },
}

# Local backend (Ollama) — reused from feature/002-local-llm-backend, never verified
# against a real model on any machine; kept exactly as unverified (see
# .context/STATE.md's Known Bugs section). Not part of PROVIDERS above since it has no
# base_url/api_key shape — pipeline/analyst.py and pipeline/llm_select.py both special-case
# the string "local" instead.
LOCAL_MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen3-32b-q6k")
LOCAL_NUM_CTX = int(os.environ.get("LOCAL_LLM_NUM_CTX", "32768"))
