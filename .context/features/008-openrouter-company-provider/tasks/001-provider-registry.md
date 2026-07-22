# Task 001: Extend PROVIDERS registry with OpenRouter + company Qwen entries

**Status:** done
**Depends on:** none (base is `feature/007-multi-provider-llm-backend`'s current tip on this
branch — `config/models.py` as it exists right now, with `deepseek`/`groq`/`qwen`/`kimi`)
**Model tier:** cheap — the exact registry content is fully specified below (transcription plus
verification); no design judgment left for the executor. The model-choice research behind these
exact entries is already done — see `.context/features/008-openrouter-company-provider/RESEARCH.md`
§1-§6 if you want the reasoning, but you don't need to re-derive anything here.

## Files
- Modify: `config/models.py`

## What to do

Add four new entries to the existing `PROVIDERS` dict (do not touch `deepseek`, `groq`, `qwen`,
`kimi`, `GROQ_MODEL`, `LLM_DEFAULT`, `LOCAL_MODEL`, `LOCAL_NUM_CTX` — this task is additive only).
Insert the new entries after the existing `"kimi"` entry, before the dict's closing `}`:

```python
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
```

## Interfaces
- Same `PROVIDERS` shape as every existing entry: `label` (str), `base_url` (str), `key_env` (str),
  `model` (str). No new keys, no new shape — `pipeline/analyst.py`'s `analyse()` already builds
  `openai.OpenAI(base_url=provider["base_url"], api_key=os.environ.get(provider["key_env"], ""))`
  generically off this dict; adding entries here requires no changes there (confirmed by inspection
  during planning — see CONTEXT.md's "Expected to require zero changes" note, which held for the
  registry itself, just not for `_chat_completion()`'s reasoning/JSON-shape handling — that's task
  002, a separate file).
- Consumed by `pipeline/llm_select.py`'s `resolve_provider()` with zero changes needed there either
  — it already iterates `PROVIDERS.items()` generically for auto-detect and the interactive picker.

## Constraints
- Do not add a `"local"`-shaped entry mixed into this dict (unchanged constraint from Feature 007's
  Task 001 — `"local"` stays a special-cased string, not a `PROVIDERS` lookup).
- Do not change `LLM_DEFAULT`'s default value or add any hardcoded provider-selection logic — this
  task is registry data only. Whether OpenRouter becomes the practical default in practice is a
  `LLM_DEFAULT`/`.env` configuration choice for whoever runs the pipeline, not something baked into
  this file (matches Feature 007's `feature/007`-inherited "no hardcoded guard" decision, extended
  to these new entries too).
- Do not add `qwen3.6-plus` or `qwen3.7-flash` entries — research found no evidence either model
  string exists (see RESEARCH.md §6). Shipping a guessed model ID that 400s at runtime is worse than
  not offering the option.
- Do not touch any other file in this task.

## Verification
1. `py -c "import ast; ast.parse(open('config/models.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "from config.models import PROVIDERS; assert set(PROVIDERS) == {'deepseek','groq','qwen','kimi','openrouter-nemotron','openrouter-nemotron-nano','company-qwen-flash','company-qwen-plus'}; assert all({'label','base_url','key_env','model'} <= set(v) for v in PROVIDERS.values()); print('OK', sorted(PROVIDERS.keys()))"`
3. `py -c "from config.models import PROVIDERS; assert PROVIDERS['openrouter-nemotron']['base_url'] == PROVIDERS['openrouter-nemotron-nano']['base_url'] == 'https://openrouter.ai/api/v1'; assert PROVIDERS['company-qwen-flash']['base_url'] == PROVIDERS['company-qwen-plus']['base_url'] == 'https://dashscope.aliyuncs.com/compatible-mode/v1'; assert PROVIDERS['openrouter-nemotron']['key_env'] == PROVIDERS['openrouter-nemotron-nano']['key_env'] == 'OPENROUTER_API_KEY'; assert PROVIDERS['company-qwen-flash']['key_env'] == PROVIDERS['company-qwen-plus']['key_env'] == 'COMPANY_QWEN_API_KEY'; assert PROVIDERS['company-qwen-flash']['model'] == 'qwen3.6-flash'; assert PROVIDERS['company-qwen-plus']['model'] == 'qwen3.7-plus'; assert PROVIDERS['openrouter-nemotron']['model'] == 'nvidia/nemotron-3-super-120b-a12b:free'; assert PROVIDERS['openrouter-nemotron-nano']['model'] == 'nvidia/nemotron-nano-9b-v2:free'; assert 'paid' in PROVIDERS['company-qwen-flash']['label'].lower() and 'paid' in PROVIDERS['company-qwen-plus']['label'].lower(); print('OK — all values correct')"`
4. Confirm existing consumers still import cleanly: `py -c "import pipeline.feedback, pipeline.weekly, pipeline.llm_select; print('OK, all still import')"`
5. `git diff config/models.py` — confirm the diff is purely additive (no lines removed/changed inside the pre-existing `deepseek`/`groq`/`qwen`/`kimi` entries or elsewhere in the file).

## Evidence

1. Syntax OK. 2. `PROVIDERS` keys confirmed: `['company-qwen-flash', 'company-qwen-plus', 'deepseek', 'groq', 'kimi', 'openrouter-nemotron', 'openrouter-nemotron-nano', 'qwen']`. 3. All value assertions passed (base_urls, key_envs, model strings, "paid" in both company labels). 4. `pipeline.feedback`, `pipeline.weekly`, `pipeline.llm_select` all still import cleanly. 5. `git diff` confirmed purely additive — 54 lines added, zero removed from existing entries or elsewhere in the file.
