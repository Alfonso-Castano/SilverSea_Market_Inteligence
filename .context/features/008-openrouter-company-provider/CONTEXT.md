# Feature: OpenRouter + Company Qwen Provider

**Base:** 0b7e302ddc20b262b668630b1f60ac9e42fb86be

**Branch note (deviation from the standard context-contract):** this feature does **not** get its
own `feature/008-slug` branch. Alfonso explicitly asked to keep building on
`feature/007-multi-provider-llm-backend` (still unmerged) since this feature is a direct, close
continuation of 007's registry pattern, and he wants one combined merge to `main` rather than two.
All work for this feature lands as further commits on `feature/007-multi-provider-llm-backend`.
The Base SHA above is `feature/007`'s tip at the moment this feature started — `feature-reviewer`
should diff `<base>..HEAD` on that same branch, exactly as it would for a dedicated branch.

## Goal

Add OpenRouter (a third-party aggregator, confirmed reachable from mainland China by Alfonso's
own China-based teammates) and a company-shared Qwen API key as additional selectable providers in
the registry `feature/007` already built, without changing that feature's dispatch or selection
*logic* — this is expected to be almost entirely registry data plus docs.

## Scope

**In scope:**
- `config/models.py`'s `PROVIDERS` dict gains new flat entries (no nested/two-level picker menu —
  matches 007's established pattern and this session's own prior decision on the company-key UX):
  - One or more `openrouter-*` entries, `base_url: "https://openrouter.ai/api/v1"`, `key_env:
    "OPENROUTER_API_KEY"` — **exact model ID(s) and which one becomes default are deliberately not
    locked here; see Open Questions.** What CONTEXT.md's own earlier research assumed
    (`deepseek/deepseek-v4-flash:free`, `deepseek/deepseek-r1:free`) was **confirmed wrong** by a
    live query against OpenRouter's own `GET /api/v1/models` during this discussion — DeepSeek is
    not currently in OpenRouter's free tier at all. The real free catalog (verified live, 14
    models) and which of them actually support `response_format` JSON mode is recorded in Open
    Questions below; `/feature-plan` must re-verify this live again (the catalog churns weekly)
    rather than trusting this document's snapshot.
  - Four company-Qwen entries sharing one key and one base_url: `key_env: "COMPANY_QWEN_API_KEY"`,
    `base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"` (China-domestic DashScope
    endpoint — confirmed distinct from the existing `qwen` entry's `-intl` endpoint, so this is
    genuinely a different account/region, not a duplicate). Model strings: `qwen3.6-flash`
    (confirmed by Alfonso directly), plus `qwen3.7-flash`/`qwen3.6-plus`/`qwen3.7-plus` (naming
    pattern inferred from the confirmed one — **not independently confirmed**, flagged as an open
    question for `/feature-plan`'s research to verify against DashScope's actual model catalog
    before locking in). Picker labels must clearly mark these as paid (e.g. "Company Qwen (paid) —
    3.7 Plus") so nobody mistakes them for a free option.
- `.env.example`/`README.md` updated for the two new env vars (`OPENROUTER_API_KEY`,
  `COMPANY_QWEN_API_KEY`) and the new default.
- A live-verification task (matching 007's Task 007 discipline) proving at minimum the OpenRouter
  free route works end-to-end through the existing dispatch — real API cost, run once, not looped.
  Whether the company key also gets a live call this round is a planner judgment call (it's paid,
  so minimizing real spend matters even more than usual — see Global Constraints).
- Existing registry entries (Groq, DeepSeek-native, Qwen-direct, Kimi-direct) stay exactly as they
  are — this feature only adds entries, doesn't remove or restructure any.

**Expected to require zero changes (confirm during `/feature-plan`, don't assume without
checking):** `pipeline/analyst.py`'s `_chat_completion()` dispatch and `pipeline/llm_select.py`'s
resolution logic are already fully generic (keyed off `PROVIDERS` dict contents, not per-provider
code) — adding registry entries should not require touching either file's logic. **One real risk
to research, not assume:** whether OpenRouter's free-tier routed models honor
`response_format={"type": "json_object"}` the same way Groq/DeepSeek/Qwen/Kimi do — `_synthesize_
sector()`/`_synthesize_summary()` depend on this. If they don't, that's a planning-relevant finding,
not something to route around silently.

**Explicitly out of scope:**
- Any Flask/dashboard-facing picker — same standing deferral from `feature/007`'s `CONTEXT.md`,
  not reopened here.
- A true nested/two-level picker menu for the company key's sub-models — explicitly decided
  against this session in favor of the flat-list pattern.
- A hardcoded guard preventing the company-tier entries from ever being the sole auto-detected
  provider — explicitly decided against this session (see Implementation Decisions). The existing
  `LLM_DEFAULT` env var is the tool for anyone who wants an ironclad guarantee.
- Re-litigating DeepSeek-native's `402 Insufficient Balance` status — unchanged, still deferred,
  not this feature's problem to fix (see `feature/007`'s `REVIEW.md`).
- Rotating the company Qwen key because it was shared via group chat — flagged to Alfonso as a
  credential-hygiene parallel to the 2026-07-17 GitLab PAT incident, but rotation (if it happens)
  is Alfonso's/the key owner's action, not a task this feature builds.

## Implementation Decisions

- **New registry entries only, no logic changes to `pipeline/analyst.py`/`pipeline/llm_select.py`
  unless research proves otherwise.** [Claude's default judgment, confirmed by user via silence/
  deferral to technical judgment] — both files are already provider-agnostic by construction;
  the burden of proof is on finding a reason this needs code changes, not assuming it does.
- **Which OpenRouter model(s) to register and which becomes default is an open research question,
  not a locked decision** — see Open Questions. Superseded the earlier (wrong) assumption that
  DeepSeek was free on OpenRouter.
- **Company Qwen entries: flat list, one per model, not a nested two-level popup.** [User,
  confirmed this session] — consistent with the flat-list pattern already decided for this exact
  scenario in the prior session's discussion, avoids new picker-UI complexity for a 4-item choice.
- **No hardcoded guard against the company key auto-becoming the sole-configured default.** [User,
  explicit choice among two presented options] — reasoning: in practice a `.env` will have at
  least one free key configured too, making auto-detect ambiguous (→ prompts, never silently picks
  company); `LLM_DEFAULT` already exists as the tool for anyone wanting a stronger guarantee. Don't
  revisit this as an oversight if it comes up later — it was a considered choice.
- **`COMPANY_QWEN_API_KEY` as the company key's env var name, not `DASHSCOPE_API_KEY`.** [Claude's
  default judgment] — `DASHSCOPE_API_KEY` is already claimed by the existing `qwen` entry (the
  `-intl` endpoint, a different Alibaba Cloud account/region); reusing it for a second, different
  endpoint would create real ambiguity for anyone with both a personal international account and
  access to the company's China-domestic key.
- **`base_url` values are hardcoded in the registry, not read from a `DASHSCOPE_BASE_URL`-style env
  var**, even though that's the env var name pattern the teammate's own instructions used.
  [Claude's default judgment] — every other `PROVIDERS` entry hardcodes its `base_url` directly in
  `config/models.py`; introducing env-configurable base URLs for just this one provider would be a
  new, inconsistent mechanism for no benefit anyone has asked for (CONTEXT.md's "no new
  abstraction beyond what's needed" constraint, inherited from `feature/007`).
- **This feature builds directly onto `feature/007-multi-provider-llm-backend`'s branch, no new
  branch of its own.** [User, explicit] — see the Branch note above.
- **Feature number: 008.** [Claude's default judgment] — next after 007; unambiguous despite 007
  also having an internally-numbered fix task called "008" in its own `tasks/` dir (fix-task
  numbering and feature numbering are separate sequences per the context-contract).

## Global Constraints

- Everything `feature/007`'s own `CONTEXT.md` Global Constraints section said still applies here
  (Groq's behavior preservation, comment style, no plugin/dynamic-loading mechanism, static dict
  registry) — this feature extends that registry, it doesn't change its shape or philosophy.
- The company Qwen key is a real, paid, shared credential — minimize live-call spend against it
  more carefully than the free-tier providers warrant. Never loop, retry-for-luck, or exercise it
  more than the minimum needed to prove correctness.
- Keep picker labels for paid entries unambiguous about cost — this was a direct, explicit user
  requirement ("I don't want the company model to be the default"), not a nice-to-have.
- Follow this project's verification-before-done discipline: a live-evidence gate is expected for
  at least the new OpenRouter default, matching `feature/007`'s Task 007 precedent (fresh
  `analyse()` call, real output pasted as evidence, not "should work").

## Open Questions

**OpenRouter model choice — the core research task for `/feature-plan`, deliberately not decided
in discussion.** Re-query `GET https://openrouter.ai/api/v1/models` live (don't trust this
snapshot — the free catalog visibly churns week to week, per multiple sources found during this
discussion) and select from scratch against these constraints, in priority order:
1. **Must actually support `response_format`/`structured_outputs`** (confirmed via the model's own
   `supported_parameters` field, not assumed) — required for `_synthesize_sector()`/
   `_synthesize_summary()`. As of this discussion, only 5 of OpenRouter's 14 free models did:
   `openai/gpt-oss-20b:free`, `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free`,
   `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-nano-9b-v2:free`. Re-verify this list
   is still current, don't assume it's unchanged by the time `/feature-plan` runs.
2. **China-account-blocking risk.** OpenRouter has begun enforcing account-level regional
   restrictions specifically for OpenAI-, Anthropic-, and Google-provided models — accounts that
   look China-based get blocked from those providers' models specifically, even though OpenRouter
   itself stays reachable. NVIDIA was not named among the enforcing providers as of this
   discussion's research. This means `gpt-oss-20b`/the two Gemma models carry real risk of being
   unusable for China-based teammates specifically — verify current status, don't just inherit this
   session's snapshot, and treat NVIDIA's models as the safer starting assumption for the
   China-relevant default until proven otherwise.
3. **Context window and general capability sufficient for this pipeline's actual workload**
   (per-sector extraction sees up to ~10-11 sources of largely-untruncated scraped content per
   `.context/DECISIONS.md`'s 2026-06-19 entry; synthesis calls reason over structured JSON with a
   locked 5-dimension scoring rubric) — Alfonso wants this weighed explicitly, not just "whichever
   is free and JSON-capable, pick the smallest."
4. **Reasoning-token overhead must not silently truncate JSON output.** Live-tested this session:
   `nvidia/nemotron-nano-9b-v2:free` returned `content: None` at `max_tokens=50` because it spent
   the entire budget on an internal chain-of-thought trace before any real content — worked fine at
   `max_tokens=300`. This was tested with a plain-text prompt, not an actual `response_format`
   JSON-mode call — `/feature-plan` must test the *actual* call shape
   (`_synthesize_sector`/`_synthesize_summary`'s real system prompts, at the pipeline's existing
   `max_tokens=2000`) against whichever model(s) get shortlisted, and confirm JSON isn't truncated
   mid-object by reasoning overhead before locking in a default. If it is, `max_tokens` may need
   raising for OpenRouter specifically — a real, planner-decidable code change, not silently
   assumed safe.
5. Likely outcome: multiple `openrouter-*` entries registered (not just one), similar to the
   existing multi-entry pattern — final count and which one is default is the planner's call, backed
   by the research above, not pre-decided here.

**Other open items:**
- **Company Qwen model ID strings for 3.7 Flash / 3.6 Plus / 3.7 Plus are inferred, not confirmed**
  (only `qwen3.6-flash` was given directly, and live-smoke-tested successfully this session — real
  content returned, confirming the key and endpoint both work). `/feature-plan`'s research should
  verify the other three real strings against DashScope's model catalog (or ask Alfonso to get them
  from the same teammate) before they're locked into `config/models.py` — do not ship guessed model
  ID strings silently.
- **OpenRouter free-tier rate limits are tight: 50 requests/day, 20/minute, unattended by any
  purchase; jumps to 1,000/day after a one-time $10 credit purchase (never expires).** At ~13 LLM
  calls per pipeline run, the free tier caps out around 3-4 full runs/day, shared across everyone
  using the key. Alfonso has not yet decided whether to make the $10 purchase — flag this cost
  tradeoff explicitly during planning rather than silently assuming either answer; it materially
  affects how conservative the live-verification task needs to be.
- **Should the company Qwen key get a live-verification call this round, given it's paid?** Partially
  resolved this session — a manual smoke test (plain-text prompt, not through the pipeline) already
  confirmed the key/endpoint/model work end-to-end. Whether `/feature-execute` still runs a second,
  in-pipeline live call as this feature's formal evidence gate (matching `feature/007`'s Task 007
  precedent) is the planner's call — weigh proving the actual dispatch path against minimizing
  further spend on a shared company resource.
