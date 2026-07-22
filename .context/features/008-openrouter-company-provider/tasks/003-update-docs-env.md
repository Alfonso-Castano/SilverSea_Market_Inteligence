# Task 003: Document OpenRouter + company Qwen in `.env.example` and `README.md`

**Status:** done
**Depends on:** Task 001 (final provider keys/labels/env-var names come from `config/models.py`'s
`PROVIDERS`)
**Model tier:** mid — content is drafted below in full, but fitting it cleanly into the existing
doc structure (matching surrounding voice, not duplicating Feature 007's existing DeepSeek/Groq/
Qwen/Kimi framing) needs light editorial judgment, same as Feature 007's own Task 006.

## Files
- Modify: `.env.example`
- Modify: `README.md`

## What to do

### 1. `.env.example`

The current file (as of this feature's base) has this block:

```
DASHSCOPE_API_KEY=
# Kimi (Moonshot AI). Sign up at https://platform.moonshot.ai
MOONSHOT_API_KEY=

# Which provider --llm=<key> falls back to when the flag isn't passed. Leave blank to let the
```

Insert a new block **between** `MOONSHOT_API_KEY=` and the `# Which provider --llm=<key>...` line:

```
# OpenRouter (free tier: 50 requests/day, 20/minute; jumps to 1,000/day after a one-time,
# non-expiring $10 credit purchase — Alfonso hasn't decided whether to make that purchase,
# don't assume either number). Registers two free NVIDIA Nemotron models
# (openrouter-nemotron, the default; openrouter-nemotron-nano, an alternative with less
# headroom for high-signal-density sectors) — chosen specifically because NVIDIA is not
# among the providers OpenRouter enforces China-account-blocking for, unlike OpenAI-,
# Anthropic-, and Google-provided models. Sign up free at https://openrouter.ai
OPENROUTER_API_KEY=
# Company-shared Qwen key (Alibaba Cloud DashScope, China-domestic endpoint — distinct
# account/region from DASHSCOPE_API_KEY above). PAID, not free tier — only set this if
# you've been given the company's shared key. Registers company-qwen-flash (qwen3.6-flash)
# and company-qwen-plus (qwen3.7-plus). Ask whoever owns Silversea's shared secrets.
COMPANY_QWEN_API_KEY=
```

Then update the `LLM_DEFAULT` comment block right below it — find:

```
# Which provider --llm=<key> falls back to when the flag isn't passed. Leave blank to let the
# pipeline auto-detect (works with zero setup if exactly one of the keys above is set) or
# prompt interactively — a popup window, falling back to a terminal prompt if no display is
# available — when it can't tell which one you mean. Valid values: deepseek, groq, qwen,
# kimi, local.
LLM_DEFAULT=
```

Replace the "Valid values" line with the full, current list:

```
# Which provider --llm=<key> falls back to when the flag isn't passed. Leave blank to let the
# pipeline auto-detect (works with zero setup if exactly one of the keys above is set) or
# prompt interactively — a popup window, falling back to a terminal prompt if no display is
# available — when it can't tell which one you mean. Valid values: deepseek, groq, qwen,
# kimi, openrouter-nemotron, openrouter-nemotron-nano, company-qwen-flash, company-qwen-plus,
# local.
LLM_DEFAULT=
```

Leave the `# --- Shared company values ...` section below completely untouched.

### 2. `README.md`

Three targeted edits, matching Feature 007's existing edit points — don't rewrite surrounding
prose, extend it:

**a) The key-setup paragraph** (currently ends "...Groq, Qwen (DashScope), and Kimi (Moonshot) are
also supported — see `.env.example` for all four.") — extend to mention the two new options:

> **Set one provider's API key in `.env`.** By default the pipeline uses DeepSeek — sign up free
> at [platform.deepseek.com](https://platform.deepseek.com), no card needed for the initial free
> grant, and reachable from mainland China (unlike Groq). Groq, Qwen (DashScope), Kimi (Moonshot),
> and OpenRouter (free tier, two NVIDIA models, also reachable from mainland China and not subject
> to OpenRouter's OpenAI/Anthropic/Google-specific China restrictions) are also supported — see
> `.env.example` for the full list, including two paid company-shared Qwen options if you've been
> given that key. Nothing else in `.env` is required to run the pipeline itself
> (`GMAIL_*`/`RECIPIENT_EMAILS` only matter if you want the optional email digest, off by default).

**b) The `--llm` bullet** — currently:
> - `--llm` — which LLM provider to use for this run: `deepseek` (default), `groq`, `qwen`,
>   `kimi`, or `local` (Ollama, unverified — see `.context/STATE.md` if you have access to it).
>   Omitting it uses `LLM_DEFAULT` from `.env` if set, auto-detects if exactly one provider's key
>   is configured, or prompts interactively (a popup, falling back to a terminal prompt) if it
>   can't tell which one you mean.

Replace with:
> - `--llm` — which LLM provider to use for this run: `deepseek` (default), `groq`, `qwen`,
>   `kimi`, `openrouter-nemotron`, `openrouter-nemotron-nano`, `company-qwen-flash`,
>   `company-qwen-plus` (the last two are paid, company-key-only — see `.env.example`), or `local`
>   (Ollama, unverified — see `.context/STATE.md` if you have access to it). Omitting it uses
>   `LLM_DEFAULT` from `.env` if set, auto-detects if exactly one provider's key is configured, or
>   prompts interactively (a popup, falling back to a terminal prompt) if it can't tell which one
>   you mean.

**c) Part 2's Stack description** — currently "a configurable LLM backend (DeepSeek by default;
Groq, Qwen, Kimi, or local Ollama — see `--llm`)". Extend to:
> a configurable LLM backend (DeepSeek by default; Groq, Qwen, Kimi, OpenRouter, a paid
> company-shared Qwen key, or local Ollama — see `--llm`)

Do not touch the Troubleshooting table, the Admin access section, or any other content.

## Interfaces
None — documentation only, no code interface.

## Constraints
- Additive documentation update, matching the exact edit points listed — don't restructure
  unrelated sections.
- Env var names in `.env.example` must exactly match Task 001's real `key_env` values
  (`OPENROUTER_API_KEY`, `COMPANY_QWEN_API_KEY`) — if Task 001 landed with different names, use the
  real ones.
- Don't state or imply a decision on the $10 OpenRouter credit purchase — document the free-tier
  50/day number as the safe default assumption (per RESEARCH.md §7, this is explicitly Alfonso's
  call, not something to resolve in docs).
- Don't overstate the China-blocking research as a guarantee — RESEARCH.md §2 found NVIDIA isn't
  *named* as an enforcing provider, which is evidence, not a certainty; keep the doc wording
  consistent with that (the draft above already does — don't strengthen it further).

## Verification
1. `py -c "content = open('.env.example', encoding='utf-8').read(); assert 'OPENROUTER_API_KEY=' in content and 'COMPANY_QWEN_API_KEY=' in content and 'openrouter-nemotron-nano' in content and 'company-qwen-plus' in content; print('OK')"`
2. Confirm every new env var name in `.env.example` matches a real `key_env` value in
   `config/models.py`'s `PROVIDERS` — quote both files' relevant lines side by side in your
   evidence.
3. `py -c "content = open('README.md', encoding='utf-8').read(); assert 'OpenRouter' in content and 'company-qwen-flash' in content; print('OK')"`
4. No LLM/API calls, no pipeline run — text-only task.

## Evidence

1. `.env.example` contains all required vars/entries. 2. Env var names cross-checked line-by-line against `config/models.py`'s `PROVIDERS` — exact match, no discrepancy. 3. README confirmed mentions both `OpenRouter` and `company-qwen-flash`. 4. Text-only diff confirmed (`.env.example`, `README.md` only) — no LLM/API calls, no pipeline run.

Task's draft wording used essentially verbatim — already read naturally in the surrounding context.
