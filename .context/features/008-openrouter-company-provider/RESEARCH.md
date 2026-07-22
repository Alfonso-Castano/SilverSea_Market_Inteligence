# Research: Feature 008 — OpenRouter + Company Qwen Provider

All research below was performed live during `/feature-plan --thorough`, 2026-07-22. Every item
CONTEXT.md's Open Questions section asked to be re-verified (not trusted from the prior session's
snapshot) was actually re-verified against a live source. Six real OpenRouter API calls were made
against the free tier during this session's testing (2 initial JSON-mode probes + 2 reasoning-
disabled probes + 2 wrapper-hint + reasoning-disabled probes) — well under the 50/day budget, and
in line with the "2-3 shortlisted candidates, few calls each" instruction.

## §1. OpenRouter free-model catalog — re-verified live

`curl -s https://openrouter.ai/api/v1/models` (no auth needed for listing), fetched fresh this
session: **342 total models, 14 free (`:free` suffix)**. The free-tier roster itself has visibly
churned since CONTEXT.md's snapshot (several different model families now appear — Poolside,
Cohere North, more NVIDIA Nemotron variants), confirming CONTEXT.md's warning that the catalog
changes week to week and must not be trusted from memory.

**However, the JSON-mode-capable subset is, by coincidence, identical to CONTEXT.md's snapshot** —
checking each free model's `supported_parameters` field for `response_format`/`structured_outputs`
gives exactly the same 5 models:

| Model ID | Context | `response_format`/`structured_outputs`? |
|---|---|---|
| `openai/gpt-oss-20b:free` | 131,072 | Yes |
| `google/gemma-4-26b-a4b-it:free` | 262,144 | Yes |
| `google/gemma-4-31b-it:free` | 262,144 | Yes |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262,144 | Yes |
| `nvidia/nemotron-nano-9b-v2:free` | 128,000 | Yes |

The other 9 free models (all reasoning-only chat/agentic models without JSON mode) are irrelevant
to this pipeline's `_synthesize_sector()`/`_synthesize_summary()` calls, which both depend on
`response_format={"type": "json_object"}`.

## §2. China-account-blocking risk — re-confirmed, with an important nuance

Re-searched this live (HN thread, OpenRouter's own guardrails doc, and general web search).
Confirmed: **OpenRouter enforces account-level regional restrictions specifically for OpenAI-,
Anthropic-, and Google-provided models** — accounts that look China-based get blocked from those
three providers' models, based on signals like billing address (not just IP), independent of
OpenRouter itself staying reachable. This is described as "out of OpenRouter's control" — it's the
underlying providers' own restriction, which OpenRouter is contractually enforcing.

OpenRouter's own `guardrails` doc page does **not** itself document this (it's scoped to
org-level spend/access-control guardrails, unrelated) — the actual source is a Hacker News
discussion plus general tech coverage of the broader 2026 US AI-export-control environment
(Anthropic was separately ordered by the US government to block non-US nationals from its
strongest models entirely, and made public distillation allegations against DeepSeek/Moonshot/
MiniMax — context for why the enforcement exists, not itself about OpenRouter specifically).

**NVIDIA is not named anywhere as an enforcing provider**, in either this session's research or the
prior session's. Attempts to check whether `openai/gpt-oss-20b`'s or `google/gemma-4-*`'s free-tier
serving on OpenRouter routes through those companies' own infrastructure (which would trigger the
block) vs. a third-party inference host (which might not) were inconclusive — OpenRouter's public
provider-routing pages didn't yield a clear answer via automated fetch. Given that inconclusiveness,
and given the explicit instruction to treat NVIDIA as the safer default absent contrary evidence,
**the two NVIDIA free models are the only candidates carried forward** as real registry entries.
`openai/gpt-oss-20b:free` and the two Gemma models are not registered this feature, consistent with
CONTEXT.md's stated priority order (China-safety first, above raw capability).

## §3. Context window / capability vs. real workload

Per-sector extraction input can run ~15,000 tokens (per CONTEXT.md's own estimate: ~10-11 sources
× 6,000-char `smart_truncate()` cap ≈ 60,000 chars). Both NVIDIA candidates' context windows
comfortably clear this (262,144 and 128,000 tokens respectively) — context length was never the
binding constraint for either. The real constraint turned out to be **output budget under
`max_tokens=2000`, not input context** — see §4.

Between the two: `nvidia/nemotron-3-super-120b-a12b:free` (120B total / ~12B active params, MoE) is
the substantially larger, more capable model; `nvidia/nemotron-nano-9b-v2:free` is a small 9B model.
Live-testing (§4) confirmed the larger model is also the more *token-efficient* one for this
pipeline's actual per-signal JSON output shape — directly relevant given this project's own history
of rewriting its architecture specifically to maximize signal density per response (see
`.context/DECISIONS.md`'s 2026-06-29 per-sector-synthesis rewrite, which took signal count from 7 to
65 specifically by giving each sector's synthesis call more effective output budget).

## §4. Reasoning-token JSON-truncation risk — tested against the pipeline's REAL call shape

This is the most consequential finding of this feature's research, and it **required a real code
change**, not just registry data — contradicting CONTEXT.md's stated hope that this feature would
be "almost entirely registry data plus docs." CONTEXT.md itself flagged this exact possibility
("a real risk to research, not assume... that's a planning-relevant finding, not something to route
around silently") and asked for it to be tested against the actual call shape. It was, and the
finding is real.

**Test 1 — default settings, `_synthesize_sector()`'s real system prompt (`SECTOR_SYNTHESIS_PROMPT`
verbatim), a representative 3-source fixture extraction block, `response_format={"type":
"json_object"}`, `max_tokens=2000`, no `reasoning` parameter passed (provider default):**

| Model | `finish_reason` | completion tokens | `reasoning_tokens` | Result |
|---|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | `stop` | 1304 | 1415 | Parsed OK, but returned a bare single object (not an array), and dropped one of the two real signals in the fixture |
| `nvidia/nemotron-nano-9b-v2:free` | `stop` | 1331 | 1331 | Same failure mode — bare object, one signal dropped |

Neither model returned a `content: None` truncation (the failure mode CONTEXT.md's own prior-session
test found at `max_tokens=50`) — at `max_tokens=2000` there's enough headroom to avoid that specific
symptom. But both models spent the overwhelming majority of their output budget on an internal
reasoning trace (not visible in `content`, only in usage accounting) and, likely as a *consequence*
of budget pressure, both also failed to comply with the "respond with a JSON array" instruction,
instead emitting a single bare JSON object — silently dropping one of two real signals. Fed through
`_synthesize_sector()`'s actual unwrap logic (`result.get("signals", list(result.values())[0] if
result else [])`, then `if not isinstance(result, list): result = []`), this specific failure shape
would in some cases parse to garbage and get discarded entirely (zero signals surfaced) — precisely
the "information density" regression this project has fought hard against before.

**Test 2 — same call, `extra_body={"reasoning": {"enabled": False}}` added (OpenRouter's unified
reasoning-control parameter):**

- `nvidia/nemotron-3-super-120b-a12b:free`: `reasoning_tokens` dropped to 0, completion dropped to
  141 tokens, **but still returned a bare object, not an array** — reasoning wasn't the (only) cause
  of the shape problem; the model just doesn't reliably follow "respond with a JSON array" under
  loose `json_object` mode without more explicit structural guidance.
- `openai/gpt-oss-20b:free`: rejected the request outright — `400 Reasoning is mandatory for this
  endpoint and cannot be disabled`. This model cannot have its reasoning overhead removed at all,
  which (combined with the China-blocking risk in §2) is a second, independent reason it isn't
  registered this feature.

**Test 3 — same call, reasoning disabled AND the exact same "wrap in a top-level `signals` array"
hint `pipeline/analyst.py` already appends to `user_message` for `provider_key == "local"` (Ollama)
— reused verbatim, not reinvented:**

- `nvidia/nemotron-3-super-120b-a12b:free`: `finish_reason=stop`, 231 completion tokens, **valid
  JSON array, 2 correctly-shaped entries, both real signals present** (BCA's grant announcement
  merged into one entity entry — not perfectly granular per the prompt's "don't merge" rule, but
  consistent with normal free-tier-model behavior elsewhere in this pipeline, not a new problem).
- `nvidia/nemotron-nano-9b-v2:free`: `finish_reason=stop`, 1617 completion tokens (well under 2000,
  but 7× more verbose per entry than the larger model), **valid JSON array, 4 entries** — arguably
  *more* rule-compliant (BCA's 3 distinct signals kept separate rather than merged) but at
  substantially higher token cost per signal (~404 completion tokens/entry vs. ~115 for the larger
  model). Extrapolated to a real production sector with many more genuine signals than this toy
  3-source fixture, the nano model's verbosity leaves far less headroom before hitting
  `max_tokens=2000` and re-triggering the exact truncation failure this fix is meant to prevent.

**Conclusion — this is a real, necessary code change, not registry-only:**
`pipeline/analyst.py`'s `_chat_completion()` must pass `extra_body={"reasoning": {"enabled":
False}}` whenever `provider_key` is one of the new `openrouter-*` keys (applies uniformly to all
three call sites — extraction, sector synthesis, summary synthesis — since all three share
`max_tokens=2000` and the same reasoning-overhead risk), and `_synthesize_sector()`'s existing
`provider_key == "local"` wrapper-hint condition must be widened to also match `openrouter-*` keys,
reusing the exact same hint string already written for Ollama. `_synthesize_summary()`'s existing
local-only hint was *not* extended the same way — its target shape is already a top-level object
(matching `SUMMARY_SCHEMA`), which is what loose `json_object` mode naturally biases toward; the
array-vs-object confusion that broke sector synthesis doesn't apply there. This wasn't live-tested
independently (budget discipline — see below), so Task 004's live-verification run, which exercises
`analyse()` end-to-end (all three call sites), is the actual proof point for this half of the claim,
not an assumption to ship silently.

**Budget spent:** 6 real OpenRouter API calls total this session (2 default-settings probes, 1
reasoning-disabled probe against gpt-oss-20b that failed fast on a 400 before consuming much, 1
reasoning-disabled probe against nemotron-3-super, 2 combined reasoning-disabled + wrapper-hint
probes). Well within the "2-3 shortlisted candidates, small number of calls each" instruction and
the 50/day shared limit — confirmed via `openrouter.zendesk.com`'s rate-limit doc and general web
sources that 50/day (free) / 1,000/day (after a one-time non-expiring $10 credit purchase) / 20/min
(unaffected by the credit purchase) are all still accurate as of this session. Also newly learned:
**failed requests still count against the daily quota** — worth calling out in the live-verification
task's caution language, since a naive retry-on-error loop would burn quota faster than expected.

## §5. Final model recommendation

**Default: `nvidia/nemotron-3-super-120b-a12b:free`** (registry key: `openrouter-nemotron`).
Reasoning: not named among China-blocking-enforcing providers (§2); large context window (§3); by
far the most token-efficient of the two viable candidates for this pipeline's real JSON output
shape, giving the most headroom against `max_tokens=2000` under real (higher-signal-density)
production sectors, not just this session's small test fixture (§4).

**Secondary, non-default entry: `nvidia/nemotron-nano-9b-v2:free`** (registry key:
`openrouter-nemotron-nano`). Also China-safe and confirmed working with the same reasoning-disable +
wrapper-hint fix, but registered as an explicitly non-default alternative — its ~7× higher
token-per-signal verbosity means it has meaningfully less safety margin under `max_tokens=2000` at
real production signal density, flagged directly in its registry comment so nobody promotes it to
default without re-testing against a real, large multi-source sector.

`openai/gpt-oss-20b:free` and both `google/gemma-4-*:free` models are **not registered** this
feature — excluded on China-blocking risk (§2) grounds, which CONTEXT.md named as the top-priority
elimination criterion, ahead of raw capability.

## §6. Company Qwen model ID strings — DashScope catalog research

Fetched `https://www.alibabacloud.com/help/en/model-studio/models` directly (the official Alibaba
Cloud Model Studio docs) and cross-checked with general web search. The current, confirmed DashScope
text-generation lineup for the newest Qwen generation contains exactly three flagship model ID
strings: **`qwen3.7-max`, `qwen3.7-plus`, `qwen3.6-flash`**. No `qwen3.6-plus` and no `qwen3.7-flash`
were found anywhere on the official docs page (explicitly re-checked by asking for every
`qwen3.*`-prefixed string on the page) or via general web search.

This means, of CONTEXT.md's four guessed strings:
- **`qwen3.6-flash`** — independently confirmed twice over (matches official docs, and was already
  live-smoke-tested successfully in the prior session against the real company key/endpoint). Ships
  as a confident registry entry.
- **`qwen3.7-plus`** — matches the official docs (appears as a current, real flagship model), but was
  **not live-tested against the real company key** this session, per the explicit instruction not to
  discover model strings by trial-and-error against a shared paid credential. Registered, but flagged
  in its registry comment as "documentation-confirmed, not live-verified against the company account
  — confirm before relying on this in production," mirroring the exact precedent Feature 007 already
  set for `kimi-k3`.
- **`qwen3.6-plus`** — no evidence found that this model exists in DashScope's current catalog.
  **Not registered.** If Alfonso/the teammate confirms it's real (e.g. a legacy 3.6-generation tier
  still live on the company's account even though 3.7 is now DashScope's recommended "plus" tier),
  adding it is a trivial one-line follow-up to `config/models.py`, not a new feature.
- **`qwen3.7-flash`** — same: no evidence found anywhere. **Not registered**, same follow-up path if
  later confirmed.

This is a deliberate scope reduction from CONTEXT.md's stated "four company-Qwen entries" — shipping
two confidently-sourced entries and clearly flagging why the other two aren't included is judged
better than shipping two guessed model ID strings that live documentation research found no evidence
for and that would produce a live `400 model not found` for anyone who selects them.

## §7. The $10 OpenRouter credit question

Not resolved here — this is explicitly Alfonso's decision per CONTEXT.md, not the planner's or
executor's to make. No task in this feature assumes either the 50/day or 1,000/day ceiling; the
live-verification task budgets itself to a small, fixed number of calls regardless of which limit is
actually in effect, and the docs task documents the free-tier number (50/day) as the safe assumption
without asserting whether the credit purchase has happened or will happen.
