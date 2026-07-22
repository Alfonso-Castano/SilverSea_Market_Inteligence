# Research — Multi-Provider LLM Backend

`--thorough` was passed; this is genuinely first-in-repo territory (no prior multi-remote-provider
LLM client work exists anywhere in this codebase — `feature/002-local-llm-backend` only ever
touched Groq vs. one local Ollama backend). Findings below directly shaped the task breakdown.
Everything in this file is checked against official provider docs (`api-docs.deepseek.com`,
`console.groq.com/docs`, `alibabacloud.com/help`, `platform.kimi.ai`) via live fetch on
2026-07-22, not general model knowledge — several first-pass search results came from
AI-generated SEO content farms (`chat-deep.ai`, `deepseek.day`, `qwen-3.com`, `deepseekv4pro.com`,
`mydeepseekapi.com`, etc.) impersonating "2026 guides" and were discarded in favor of the actual
vendor docs once cross-checked.

## 1. DeepSeek — time-sensitive finding: `deepseek-chat`/`deepseek-reasoner` deprecate in 2 days

Confirmed directly against `api-docs.deepseek.com` (two independent fetches, official domain):

- Current model names are **`deepseek-v4-flash`** (fast/cheap, non-thinking) and
  **`deepseek-v4-pro`** (more capable). The legacy names `deepseek-chat` and `deepseek-reasoner`
  **deprecate on 2026-07-24 15:59 UTC** — two days from this feature's planning date
  (2026-07-22) — and until then map onto `deepseek-v4-flash`'s non-thinking/thinking modes.
- **Registry uses `deepseek-v4-flash` as the default model, not `deepseek-chat`.** CONTEXT.md's
  "5M tokens, no card" framing was based on an earlier session's research into `deepseek-chat`-era
  pricing; using that literal model string today would work for about 48 hours and then break.
- Base URL for the OpenAI SDK: `https://api.deepseek.com` (no `/v1` suffix — this is what
  DeepSeek's own docs use; a `/v1`-suffixed variant is also reported to work but the unsuffixed
  form is the documented canonical one).
- JSON mode: `response_format={"type": "json_object"}` is supported and documented, with one
  real requirement — **the word "json" must appear in the system or user prompt** or the API may
  return empty content. Confirmed already satisfied by the existing prompts unmodified —
  `SECTOR_SYNTHESIS_PROMPT` and `SUMMARY_PROMPT` both already contain the literal string
  "JSON" ("Respond with ONLY valid JSON..."). No prompt change needed, consistent with
  CONTEXT.md's constraint that prompts stay untouched.
- **Free tier exact figure not independently confirmed against the official pricing page.**
  The pricing page describes cost as "deducted from your topped-up balance or granted balance"
  — confirming a free "granted balance" mechanism exists, distinct from paid top-up — but does
  not state the exact token figure or whether a card is required at signup. Treat CONTEXT.md's
  "5M tokens, no card" as directionally plausible but unconfirmed precisely; not this feature's
  job to re-verify (per CONTEXT.md's constraint, China-reachability and exact free-tier terms are
  leo.li's/Alfonso's own out-of-band confirmation, not something this session can verify).

## 2. Groq — confirmed, matches existing behavior exactly

`base_url="https://api.groq.com/openai/v1"`, existing `GROQ_API_KEY`, existing model string
(`meta-llama/llama-4-scout-17b-16e-instruct`), `response_format={"type": "json_object"}` already
proven working (it's what the current `groq` SDK-based code already relies on). Switching Groq's
call site from the dedicated `groq` package to the generic `openai.OpenAI(base_url=..., ...)`
client is a transport-layer change only — the Groq API itself doesn't change, and the `groq`
Python package is itself documented as a thin wrapper around the same OpenAI-compatible REST
surface. This is the regression case Task 007's verification must prove behaves identically to
today.

## 3. Qwen / DashScope — simple international endpoint exists; a workspace-scoped variant does not fit a static registry

Two different DashScope OpenAI-compatible surfaces exist and it matters which one the registry
uses:
- A newer "Model Studio" regional surface with workspace-ID-embedded URLs, e.g.
  `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` — **not usable** in
  a static per-provider registry entry (CONTEXT.md explicitly rules out any dynamic
  provider-loading mechanism), since the URL itself would need runtime interpolation per account.
- The classic, simpler DashScope compatible-mode endpoint, confirmed via cross-search and
  consistent across multiple independent sources: **`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`**
  (international) — no workspace ID needed, works with a plain `DASHSCOPE_API_KEY`. This is what
  the registry uses.
- Model name: `qwen-plus` (confirmed both via the official Alibaba Cloud doc's own example and
  independent sources).
- `response_format={"type": "json_object"}` support: **not independently confirmed** against
  DashScope's authoritative "OpenAI-compatible parameters" table (it wasn't listed in the section
  fetched) — secondary sources claim JSON mode is supported once configured, but this is not
  proven to official-doc confidence. Left flagged, not blocking — Qwen is registered structurally
  but not live-verified this round (see judgment call below).

## 4. Kimi / Moonshot — confirmed base URL and auth; model name and JSON-mode support less certain

`base_url="https://api.moonshot.ai/v1"`, API key env var `MOONSHOT_API_KEY` (confirmed via the
official `platform.kimi.ai` migration guide, which also documents the `/v1/chat/completions`,
`/v1/files`, and related endpoints as OpenAI-compatible). Model naming is genuinely unsettled
across sources — the official docs page referenced `kimi-k3`, `kimi-k2.6`, and `kimi-k2.5` without
stating a single canonical "current default"; the registry uses `kimi-k3` as the most-recent name
that appeared directly on the official docs domain, flagged for confirmation before any real
reliance. `response_format={"type": "json_object"}` support wasn't explicitly confirmed in the
fetched docs either (OpenAI-compatible generally implies it, but that's an inference, not a
citation).

## 5. One `openai.OpenAI(...)` client per provider — no real gotcha

A client instance is bound to one `base_url`/`api_key` pair at construction time, so switching
providers means constructing a new client, not reusing one across providers — this matches the
existing pattern exactly (`analyse()` already constructs exactly one client per pipeline run,
once, before any of the three call sites fire — see `feature/002`'s
`client = Groq(...) if LLM_BACKEND != "local" else None`). No special handling needed: build one
`openai.OpenAI(base_url=provider["base_url"], api_key=os.environ.get(provider["key_env"], ""))`
in `analyse()`, exactly where the `Groq(...)` construction happens today.

## 6. tkinter popup fallback — confirmed platform behavior

- **Windows (this dev machine):** `import tkinter` succeeds, `tkinter.TkVersion` reports `8.6` —
  genuinely stdlib here, confirmed via direct `py -c "import tkinter"` execution, not assumed.
- **Headless Ubuntu server (CONTEXT.md's fallback target):** two independent failure modes are
  both real and must both be caught by the same broad `except`: (1) on many minimal/server Ubuntu
  installs, the Tk bindings are a *separate* apt package (`python3-tk`) not installed by default
  — `import tkinter` itself raises `ModuleNotFoundError`, before any display is even touched; (2)
  even where tkinter *is* installed, constructing the actual window (`tkinter.Tk()`) with no X
  server / no `$DISPLAY` raises `_tkinter.TclError: no display name and no $DISPLAY environment
  variable`. These are two different exception types at two different points (import time vs.
  window-construction time) — confirming CONTEXT.md's already-locked decision to wrap the *entire*
  tkinter attempt (import + window construction) in one broad `try/except Exception`, not to
  narrowly catch only `TclError` (which would miss the `ModuleNotFoundError` case entirely) and
  not to pre-check a `DISPLAY` env var (Windows/Mac headless cases have no `DISPLAY` variable at
  all even when a real display exists, so that check would misfire there). No design change from
  CONTEXT.md's decision — this section exists to confirm it against real platform behavior rather
  than leaving it asserted-but-unverified.

## 7. Scope gap found, deliberately NOT pulled into this feature: `pipeline/feedback.py` and `pipeline/weekly.py` have their own independent Groq-only call sites

Both files construct their own `Groq(api_key=os.environ.get("GROQ_API_KEY", ""))` client and
import `GROQ_MODEL` directly (`pipeline/feedback.py` lines 60, 121; `pipeline/weekly.py` line 63)
— entirely separate from the three `pipeline/analyst.py` call sites CONTEXT.md's Scope section
names. **CONTEXT.md's Goal and Scope sections both name only `pipeline/analyst.py`** — this
feature does not touch `feedback.py`/`weekly.py`. Practical consequence: a China-based user
running with only `DEEPSEEK_API_KEY` set (no `GROQ_API_KEY`) gets a fully working core pipeline
(scrape → filter → analyse → report) via DeepSeek, but feedback-digest aggregation and weekly
summarization will keep silently printing "skipped — no GROQ_API_KEY" and doing nothing — a
real, pre-existing degrade-gracefully behavior (not a crash, per the 2026-07-13 fix logged in
`.context/DECISIONS.md`), just one that stays Groq-only after this feature ships. **Not built into
this feature's task list** — CONTEXT.md didn't authorize touching those files, and expanding scope
unilaterally would violate the "respect scope boundaries exactly" instruction this planning pass
was given. Flagged here, and in the final report back, as a real follow-up candidate for a future
small feature, not something this feature silently left broken without noting it.

## 8. Judgment calls made here (flagged, not silently assumed)

- **Only Groq (regression) and DeepSeek (new default) get a live-verified call this round.**
  CONTEXT.md left this as "planner's call, informed by budget." Qwen and Kimi are registered
  structurally (so `--llm=qwen`/`--llm=kimi` are real, wired code paths) but not exercised against
  a real account this round — this mirrors exactly how Ollama's entry has sat unverified-but-real
  since `feature/002`, which CONTEXT.md explicitly says to leave as-is. Neither this session nor
  Alfonso has a Qwen/DashScope or Kimi/Moonshot account/key on hand; obtaining one is out of scope
  for a planning pass.
- **Interactive-picker candidate list, where CONTEXT.md leaves the exact behavior implicit:**
  when the picker fires (no `--llm`, no `LLM_DEFAULT`, and not exactly one remote provider's env
  var is configured), it offers the remote providers whose env var *is* currently set, plus
  `local` always offered (since Ollama needs no env var to be a legitimate choice — its
  availability is a runtime fact the existing `_chat_completion`-style dispatch already surfaces
  as a clear error if missing, matching `feature/002`'s `RuntimeError` pattern). If zero remote
  providers have a key configured, the picker still offers `local` alongside a clear on-screen
  note that no remote provider is configured — it does not auto-select `local` silently, matching
  CONTEXT.md's "no silent fallback to a default" rule. This exact behavior is written into Task
  004 so the executor isn't left to guess.
- **`pipeline/llm_select.py` as a new, dedicated module** rather than inlining the resolution
  logic into `main.py`'s `__main__` block. CONTEXT.md's "CLI-only surface, off `main.py`" reads
  most naturally as "not part of the Flask dashboard" (contrasting with `app.py`), not literally
  "must live inside `main.py`'s file" — a dedicated module keeps `main.py`'s `__main__` block
  a thin call site (mirroring how `--domain=`/`--country=` parsing stays inline there because it's
  truly trivial, while this resolution logic — CLI/env/auto-detect/popup/terminal/fail-fast — is
  substantial enough to warrant its own file per this project's "smaller, focused files" bias).

## 9. Environment already checked on this dev machine (informs Task 002/003/007's verification steps)

- No project `.venv` exists; `py` (3.13.5) is the global interpreter used for ad hoc checks (repo
  is pinned to 3.12.3 in `.python-version` — a pre-existing, unrelated mismatch).
- `ollama` package: **already installed** globally (residue from the `feature/002`
  investigation noted in `.context/STATE.md`).
- `openai` package: **not installed** — Task 002/003's verification steps must `pip install
  openai` first or their import checks will fail for a real reason unrelated to the code change.
- `groq` package: installed at `1.4.0` (repo's pinned `requirements.txt` says `1.5.0` — a minor,
  pre-existing version drift on this machine, not something this feature needs to reconcile).
