# Model Research — Silversea Market Intelligence Pipeline

*Research only — zero live API calls made. Published docs and pricing as of 2026-06.*

---

## URGENT: Current Model Deprecated

**`llama-3.3-70b-versatile` was deprecated by Groq on June 17, 2026** (nine days ago).
Groq emailed users and updated its deprecation docs; the model may still respond now but is officially unsupported. The pipeline (`pipeline/analyst.py`) must be updated before the next run or it will fail silently or return errors.

Groq's official recommended replacements: `openai/gpt-oss-120b` or `qwen/qwen3.6-27b`.

---

## Current Setup

- Provider: Groq (free tier)
- Model: `llama-3.3-70b-versatile` (DEPRECATED)
- ~6 LLM calls/run: one extraction call per sector (5) + one synthesis call
- `response_format={"type": "json_object"}` used for structured output
- Estimated tokens/run: 20k–40k input+output
- Known constraint: 25-second delays between calls for TPM compliance

---

## Comparison Table

| Model | Provider | Input / Output (per 1M tokens) | Est. Daily Cost (30k tokens) | JSON Mode | Context Window | Free Tier Limits | Notes |
|---|---|---|---|---|---|---|---|
| `openai/gpt-oss-120b` | Groq | Free tier: $0 | $0 | Yes | 128k | 6k TPM, 30 RPM, 1k RPD, 100k TPD | Groq's recommended replacement for deprecated llama-3.3-70b |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Groq | $0.11 / $0.34 | $0 (free) | Yes | 128k | **30k TPM**, 30 RPM, 1k RPD | Highest free-tier TPM on Groq — eliminates 25s delays |
| `qwen/qwen3.6-27b` | Groq | Free tier: $0 | $0 | Yes | 131k | 6k TPM, 30 RPM, 1k RPD | Second Groq-recommended replacement; largest context on Groq free tier |
| `gemma2-9b-it` | Groq | Free tier: $0 | $0 | Yes | **8k** | 15k TPM, 30 RPM, 1k RPD | Higher TPM but 8k context is a dealbreaker for synthesis calls |
| `claude-haiku-4-5-20251001` | Anthropic | $1.00 / $5.00 | ~$0.07 | Yes | 200k | No free tier; usage-based | Production target per CONTEXT.md; batch API halves cost to ~$0.035/day |
| `llama-3.3-70b` or `llama-3.1-8b` | Cerebras | Free tier: $0 | $0 | Yes | **8k cap (free tier)** | **1M TPD**, 60k–100k TPM, 30 RPM | Generous TPD but 8k context cap rules it out for synthesis; volatile catalog |
| Together AI (various) | Together AI | Varies | ~$0.01–$0.05 | Varies by model | Varies | $25 credits (not permanent) | Credits-only, not a sustained free tier; dynamic rate limits unpublished |

---

## Detailed Analysis

### Groq: `openai/gpt-oss-120b`

OpenAI's open-weight 120B model served on Groq's infrastructure. Groq explicitly names this as the primary replacement for `llama-3.3-70b-versatile`. It supports JSON mode (Groq confirms all 11 current models support JSON structured output). Context window is 128k — well above what any single extraction or synthesis call needs. Free-tier limits are 6k TPM / 30 RPM / 1k RPD / 100k TPD, matching the old llama-3.3-70b limits, so the existing 25-second inter-call delays would still be needed.

**Daily cost at 30k tokens:** $0 (free tier).

**Practical fit:** Drop-in replacement with minimal code change (just the model name string). No TPM improvement over the deprecated model. Quality for JSON extraction is expected to be comparable or better given the larger parameter count and newer architecture.

---

### Groq: `meta-llama/llama-4-scout-17b-16e-instruct`

A 17B-parameter Mixture-of-Experts model from Meta's Llama 4 family. Its standout characteristic on Groq's free tier is **30k TPM** — five times higher than any other free-tier model. This alone eliminates the 25-second delays between sector extraction calls that currently make a pipeline run take ~3 minutes.

Context window is 128k. JSON mode is supported. Paid tier pricing is $0.11/$0.34 per 1M tokens (cheapest on Groq paid tier). Quality trade-off: 17B effective active parameters vs 70B for the old model, but Llama 4 Scout is a newer generation with reported instruction-following quality competitive with Llama 3.3 70B on benchmarks.

**Daily cost at 30k tokens:** $0 (free tier). On paid tier: ~$0.005/day — negligible.

**Practical fit:** Best free-tier upgrade path if the 3-minute runtime is a pain point. Single model-name config change. Worth testing extraction quality before committing.

---

### Groq: `qwen/qwen3.6-27b`

Alibaba's Qwen 3.6 27B model on Groq. Second recommended replacement from Groq alongside gpt-oss-120b. Has the largest context window of any free-tier Groq model at 131k tokens. JSON mode supported. Rate limits match the standard 6k TPM / 100k TPD tier. Quality for structured extraction on multilingual content (relevant for MY/VN/ID expansion in Phase 4) may be stronger than Western models given Alibaba's training data.

**Daily cost:** $0 (free tier).

**Practical fit:** Solid alternative to gpt-oss-120b; larger context gives headroom for Phase 4's expanded source count.

---

### Groq: `gemma2-9b-it`

Google Gemma 2 9B. Has higher TPM (15k vs standard 6k) and a smaller context window of 8k tokens. The 8k limit is a dealbreaker: the synthesis call alone takes 4k–8k input tokens (all five sector extractions concatenated), and there's no safe headroom. **Ruled out for this pipeline.**

---

### Anthropic: `claude-haiku-4-5-20251001` (Claude Haiku 4.5)

The current production candidate per CONTEXT.md (which named "Haiku 3.5" — that model is now retired on Anthropic's direct API; Haiku 4.5 is the successor). Pricing: $1.00/1M input, $5.00/1M output. Batch API (async, 24h SLA) cuts both 50%, to $0.50/$2.50. Prompt caching cuts repeated input tokens up to 90%.

Context window: 200k tokens — by far the largest of any option here, which removes all truncation concerns and could allow a return to the single-call analyst architecture (Phase 1 style) if desired.

JSON mode: fully supported via native tool use and structured output.

Rate limits: Anthropic applies per-tier limits; exact figures depend on usage tier. No free tier.

**Daily cost estimate** (30k tokens/day, roughly 20k input + 10k output):
- Standard: 20k × $1/1M + 10k × $5/1M = $0.020 + $0.050 = **$0.070/day**
- With batch API: ~**$0.035/day**
- Both are well under the $0.10/day budget target.

**Practical fit:** Best structured-output quality. Switching from Groq requires changing base URL + API key in `analyst.py` (minimal code change since the pipeline uses the OpenAI-compatible interface style). No free tier means any test run incurs a small cost.

---

### Cerebras (free tier)

Cerebras offers 1M tokens/day free — ten times Groq's 100k TPD — with 60k–100k TPM. However, the free tier imposes an **8,192-token context cap per request**. With synthesis calls taking 4k–8k input tokens, this is at the absolute limit and will fail for larger runs. Additionally, Cerebras's free model catalog is volatile: it collapsed from ~12 models to 2 models in late May 2026, and the company's own docs warn against hardcoding model names. JSON mode is supported on Llama models when available.

**Practical fit:** Not recommended as a primary provider. The context cap rules it out for synthesis, and catalog volatility makes it unreliable for a daily production pipeline. Possible fallback for extraction-only calls if Groq quotas become a problem, but requires per-call context budgeting.

---

### Together AI

Gives $25 in free credits to new accounts — not a recurring permanent free tier. Rate limits are dynamic and unpublished. No reliable baseline for a daily production pipeline. Structured output support varies by model.

**Practical fit:** Not suitable. One-time credits run out; no predictable free ongoing access.

---

## Recommendation

### Near-term (free tier, immediate action required)

**Switch to `openai/gpt-oss-120b` on Groq.** This is Groq's own recommended replacement for the deprecated `llama-3.3-70b-versatile`, requires only a model-name string change in `analyst.py` (and the config variable wherever it's set), and has equivalent free-tier limits and JSON mode support.

If the 3-minute runtime is a pain point, use **`meta-llama/llama-4-scout-17b-16e-instruct`** instead — the 30k TPM eliminates the 25-second inter-call delays, cutting runtime to under 30 seconds. Trade-off: smaller model (17B vs 120B), so extraction quality should be spot-checked on the first run.

The model config should be a single variable (e.g. `GROQ_MODEL`) so this change is one line.

### Production ($0.10/day budget, once approved)

**Claude Haiku 4.5** (`claude-haiku-4-5-20251001`). Estimated cost $0.035–$0.070/day depending on whether batch API is used. 200k context removes all truncation concerns. Best JSON structured-output reliability of any option here. Aligns with what CONTEXT.md already decided — just note that the target model name has changed from 3.5 to 4.5 since the original decision was made.

---

## Information Gaps

- **gpt-oss-120b quality benchmarks on JSON extraction tasks**: No structured-output benchmark comparisons between gpt-oss-120b and llama-3.3-70b-versatile were findable in published docs. Quality parity is inferred from Groq's own recommendation, not independently verified.
- **Groq TPM discrepancy**: CONTEXT.md records 12k TPM for the deprecated llama-3.3-70b-versatile (as experienced during development). Published docs and third-party sources consistently cite 6k TPM as the current free-tier standard. This may reflect a Groq rate limit reduction since the pipeline was first built, or account-level variation. Actual limit for the replacement model should be confirmed in the Groq console under API keys > Rate Limits.
- **Anthropic API tier rate limits**: Specific RPM/TPM figures for Claude Haiku 4.5 on the lowest paid tier are not published in Anthropic's public docs; they vary by usage tier and require checking the console after account creation.
- **Cerebras context cap source**: The 8k free-tier context cap was cited by multiple third-party sources but not directly verified against Cerebras's own docs in this session.
- **Llama 4 Scout extraction quality vs llama-3.3-70b**: No published head-to-head benchmark on structured JSON extraction from scraped web content found. Runtime improvement is certain (5x TPM); quality parity is not confirmed without a live test run.
