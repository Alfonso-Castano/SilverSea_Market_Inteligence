# Task 006: Document the new providers in .env.example and README.md

**Status:** done
**Depends on:** Task 001 (final env var names come from `config/models.py`'s `PROVIDERS`), Task
004 (`LLM_DEFAULT`/picker behavior), Task 005 (`--llm=` flag exists and is wired).
**Model tier:** mid — content is drafted below in full, but CONTEXT.md explicitly leaves "precise
wording/placement of the `LLM_DEFAULT` documentation" to this task; apply light judgment fitting
it into the existing doc structure rather than treating the draft as untouchable verbatim text.

## Files
- Modify: `.env.example`
- Modify: `README.md`

## What to do

### 1. `.env.example`

Replace the current `# --- Get your own (free tier) ---` section (currently just
`GROQ_API_KEY=` with its comment) with:

```
# --- LLM backend: pick which provider(s) you want available (free tier, get your own) ---
# The pipeline's core analysis (pipeline/analyst.py) runs on any ONE of the providers below
# per run, selected via --llm=<key> or LLM_DEFAULT below. (pipeline/feedback.py and
# pipeline/weekly.py still call Groq directly regardless of this setting — a known, narrower
# gap; set GROQ_API_KEY too if you want feedback-digest/weekly-summary generation working.)
#
# DeepSeek is the default provider when nothing else is configured: reachable from mainland
# China without a proxy (unlike Groq's own console, which 403s there), cheapest, and the
# most generous free grant of the providers below. Sign up free at
# https://platform.deepseek.com — no card required for the initial free token grant.
DEEPSEEK_API_KEY=
# Groq API key — the original dev/test provider, still fully supported, just no longer the
# default. Not reachable from mainland China. Sign up free at https://console.groq.com
GROQ_API_KEY=
# Qwen (Alibaba Cloud DashScope). Sign up at https://dashscope.console.aliyun.com
DASHSCOPE_API_KEY=
# Kimi (Moonshot AI). Sign up at https://platform.moonshot.ai
MOONSHOT_API_KEY=

# Which provider --llm=<key> falls back to when the flag isn't passed. Leave blank to let the
# pipeline auto-detect (works with zero setup if exactly one of the keys above is set) or
# prompt interactively — a popup window, falling back to a terminal prompt if no display is
# available — when it can't tell which one you mean. Valid values: deepseek, groq, qwen,
# kimi, local.
LLM_DEFAULT=

# Local backend (Ollama) — only read when LLM_DEFAULT=local or --llm=local is used. Requires
# Ollama installed and running locally with a model already pulled/imported; this path has
# never been verified against a real model on any machine (see .context/STATE.md if you have
# access to it). Safe to leave both blank otherwise.
LOCAL_LLM_MODEL=
LOCAL_LLM_NUM_CTX=
```

Leave the `# --- Shared company values ...` section below it completely untouched.

### 2. `README.md`

Three targeted edits, not a rewrite:

**a) The two-path intro bullet** ("Run the full pipeline... Needs a Groq API key.") — update to
say "Needs an LLM provider API key (DeepSeek by default; Groq and others also supported)."

**b) The "Run the full pipeline" section's key-setup paragraph** — currently:
> **Set `GROQ_API_KEY` in `.env`.** Sign up free at [console.groq.com](https://console.groq.com)
> — no payment info needed for the free tier. Nothing else in `.env` is required to run the
> pipeline itself...

Replace with something in this shape (adjust wording to fit the surrounding paragraph's voice,
don't just paste this verbatim if it reads awkwardly in context):
> **Set one provider's API key in `.env`.** By default the pipeline uses DeepSeek — sign up free
> at [platform.deepseek.com](https://platform.deepseek.com), no card needed for the initial free
> grant, and reachable from mainland China (unlike Groq). Groq, Qwen (DashScope), and Kimi
> (Moonshot) are also supported — see `.env.example` for all four. Nothing else in `.env` is
> required to run the pipeline itself (`GMAIL_*`/`RECIPIENT_EMAILS` only matter for the optional
> email digest, off by default).

**c) The `--country`/`--domain`/`--no-email` bullet list** (right after the
`python3 main.py --country=SG --domain=BER --no-email` example) — add a new bullet documenting
`--llm=`:
> - `--llm` — which LLM provider to use for this run: `deepseek` (default), `groq`, `qwen`,
>   `kimi`, or `local` (Ollama, unverified — see `.context/STATE.md` if you have access to it).
>   Omitting it uses `LLM_DEFAULT` from `.env` if set, auto-detects if exactly one provider's key
>   is configured, or prompts interactively (a popup, falling back to a terminal prompt) if it
>   can't tell which one you mean.

Do not touch the Troubleshooting table, the Admin access section, or any content below "Part 1 —
Build & Run" unless you find an existing Groq-only reference there that would now read as
factually wrong given the default changed — if you find one, fix it minimally and note exactly
what you changed and why in your evidence; don't go looking for unrelated wording to improve.

## Interfaces
None — documentation only, no code interface.

## Constraints
- Don't remove or restructure any section unrelated to LLM provider selection — this is an
  additive documentation update, not a README rewrite.
- Keep the existing "Real caveat, not a hypothetical one" paragraph about Groq's specific
  100k-token daily quota as-is (it's still accurate for anyone using Groq) — don't try to
  generalize it into a provider-agnostic quota statement, since each provider's actual limits
  differ and this feature's research didn't pin down all of them to production-ready precision
  (see RESEARCH.md §1, §8).
- `.env.example` changes must exactly match the real env var names Task 001 put in
  `config/models.py`'s `PROVIDERS` (`DEEPSEEK_API_KEY`, `GROQ_API_KEY`, `DASHSCOPE_API_KEY`,
  `MOONSHOT_API_KEY`) — if Task 001 landed with different names than shown here, use the real
  ones, don't leave a mismatch between the registry and the example file.

## Verification
1. `py -c "content = open('.env.example', encoding='utf-8').read(); assert 'DEEPSEEK_API_KEY=' in content and 'GROQ_API_KEY=' in content and 'DASHSCOPE_API_KEY=' in content and 'MOONSHOT_API_KEY=' in content and 'LLM_DEFAULT=' in content and 'LOCAL_LLM_MODEL=' in content and 'LOCAL_LLM_NUM_CTX=' in content; print('OK — all vars present')"`
2. Confirm every env var name in `.env.example` matches a real `key_env` value in
   `config/models.py`'s `PROVIDERS` dict (or is one of `LLM_DEFAULT`/`LOCAL_LLM_MODEL`/
   `LOCAL_LLM_NUM_CTX`, which `config/models.py` also reads) — do this by eye, quote both files'
   relevant lines side by side in your evidence.
3. `py -c "content = open('README.md', encoding='utf-8').read(); assert '--llm' in content and 'DeepSeek' in content; print('OK — README mentions both')"`
4. No LLM/API calls, no pipeline run — this is a text-only task.

## Evidence

1. `.env.example` contains all 7 required vars. 2. By-eye cross-check confirmed every env var name matches `config/models.py`'s `PROVIDERS`/`LLM_DEFAULT`/`LOCAL_LLM_MODEL`/`LOCAL_LLM_NUM_CTX` exactly — no mismatches. 3. README confirmed mentions both `--llm` and `DeepSeek`. 4. Text-only diff: `.env.example` +34/-3, `README.md` +7/-3.

One additional minimal fix beyond the three named edits, per the Constraints clause allowing a factually-wrong Groq-only reference to be corrected: Part 2's Stack description ("Groq API ... for LLM calls") updated to reflect the configurable backend. Nothing else below Part 1 touched.
