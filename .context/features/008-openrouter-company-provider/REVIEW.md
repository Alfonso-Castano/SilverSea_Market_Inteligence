# Review: OpenRouter + Company Qwen Provider

**Base:** `0b7e302ddc20b262b668630b1f60ac9e42fb86be` — diff taken fresh in this pass via
`git diff 0b7e302ddc20b262b668630b1f60ac9e42fb86be..HEAD` on `feature/007-multi-provider-llm-backend`
(this feature's continuation branch, per its own documented deviation from the standard
context-contract — see CONTEXT.md's Branch note), not from any task file's own description.

## Task-level check

- **001 (provider registry, `config/models.py`)** — diff read in full: purely additive, 54 lines
  added, zero lines touched inside the pre-existing `deepseek`/`groq`/`qwen`/`kimi` entries or
  elsewhere in the file (`GROQ_MODEL`, `LLM_DEFAULT`, `LOCAL_MODEL`, `LOCAL_NUM_CTX` all confirmed
  byte-identical to base). Four new entries land exactly as specified: `openrouter-nemotron`,
  `openrouter-nemotron-nano` (both `base_url: https://openrouter.ai/api/v1`, `key_env:
  OPENROUTER_API_KEY`), `company-qwen-flash`, `company-qwen-plus` (both `base_url:
  https://dashscope.aliyuncs.com/compatible-mode/v1`, `key_env: COMPANY_QWEN_API_KEY`). Model
  strings match exactly (`nvidia/nemotron-3-super-120b-a12b:free`,
  `nvidia/nemotron-nano-9b-v2:free`, `qwen3.6-flash`, `qwen3.7-plus`). Confirmed `qwen3.6-plus` and
  `qwen3.7-flash` are genuinely absent from the diff — the deliberate omission is real, not just
  claimed. Both company labels contain "paid". ✓
- **002 (`pipeline/analyst.py` reasoning fix)** — diff read in full, matches the task's exact
  specified hunks: `_chat_completion()` gains `if provider_key.startswith("openrouter"):
  kwargs["extra_body"] = {"reasoning": {"enabled": False}}` right after the existing
  `response_format` block; `_synthesize_sector()`'s hint condition widens from
  `provider_key == "local"` to `provider_key == "local" or provider_key.startswith("openrouter")`.
  `_synthesize_summary()`'s own `if provider_key == "local":` hint block (line 354) is confirmed
  byte-for-byte unchanged — grepped all four `provider_key == "local"` occurrences in the file and
  read each in context; only the one in `_synthesize_sector()` was touched, exactly as the task's
  "Do NOT" instruction required. `max_tokens=2000` unchanged everywhere (grepped, still three call
  sites, no site touched). `extra_body` confirmed to be a real, existing parameter of the installed
  `openai==2.46.0` SDK's `chat.completions.create` (`inspect.signature` check, not assumed) — not a
  new dependency. ✓
- **003 (`.env.example`/`README.md` docs)** — both diffs read in full, match the task's drafted
  wording essentially verbatim at all three README edit points (key-setup paragraph, `--llm` bullet,
  Stack line) and the `.env.example` insertion point (between `MOONSHOT_API_KEY=` and the
  `LLM_DEFAULT` comment block, `LLM_DEFAULT`'s "Valid values" list extended correctly). The
  `# --- Shared company values ---` section below is confirmed untouched. Env var names
  (`OPENROUTER_API_KEY`, `COMPANY_QWEN_API_KEY`) match Task 001's real `key_env` values exactly. No
  overstatement of the China-blocking research as a guarantee ("not among the providers... enforces
  ... for" — evidence-worded, not asserted as certain). ✓
- **004 (live verification)** — evidence reports a real `analyse(filtered, country,
  "openrouter-nemotron")` call: 4 signals under Government & Agencies, 2 opportunities, clamp
  invariants held (`total_score == sum(scores.values())`, every dimension in `[1,5]`), real
  `source_name` (not the pre-existing placeholder-bug string), `pytest tests/test_clamp.py` passed,
  run exactly once, script written outside the repo and confirmed deleted (`git status` clean at
  the time). Per this project's quota-discipline norm and this task's own explicit instruction, this
  was **not** re-run in this review pass. Instead, validity was confirmed by inspection: `git log
  --oneline 0b7e302..HEAD -- pipeline/analyst.py` shows exactly one commit touching that file
  (`e25fa25`, Task 002's fix), and it predates the commit that carries Task 004's evidence
  (`4d3c86c`, the last commit on the branch) — no later change to `pipeline/analyst.py` could have
  invalidated what Task 004 proved. ✓

## Decision coverage

Checked every Implementation Decision in CONTEXT.md against the code:

- **New registry entries only, no logic changes unless research proves otherwise** — research (
  RESEARCH.md §4) did prove a logic change necessary, and CONTEXT.md's own decision text explicitly
  carved out that exception ("unless research proves otherwise"). Task 002's change is real,
  documented, and traced directly to the live-tested finding, not a quiet scope violation. ✓
- **Which OpenRouter model(s) — left as open research, not pre-decided** — resolved via
  RESEARCH.md §1-§5 to two NVIDIA entries, `openrouter-nemotron` as default; both registered
  exactly as the research concluded. ✓
- **Company Qwen entries: flat list, not nested** — confirmed: two flat top-level `PROVIDERS`
  entries (`company-qwen-flash`, `company-qwen-plus`), no picker/menu abstraction introduced. ✓
- **No hardcoded guard against the company key auto-becoming the sole-configured default** —
  confirmed by grep: no `company-qwen` special-casing exists anywhere outside `config/models.py`'s
  registry data itself; `pipeline/llm_select.py` (untouched) still treats every `PROVIDERS` entry
  uniformly for auto-detect. `LLM_DEFAULT` remains the only guard mechanism, as decided. ✓
- **`COMPANY_QWEN_API_KEY`, not `DASHSCOPE_API_KEY`** — confirmed both company entries use
  `key_env: "COMPANY_QWEN_API_KEY"`, distinct from the pre-existing `qwen` entry's
  `DASHSCOPE_API_KEY`. ✓
- **`base_url` hardcoded in the registry, not env-configurable** — confirmed: both new `base_url`
  values are literal strings in `config/models.py`, no new `os.environ.get(...)`-style
  base-URL-from-env mechanism introduced anywhere. ✓
- **Feature builds directly onto `feature/007-multi-provider-llm-backend`, no new branch** —
  confirmed: `git branch --show-current` → `feature/007-multi-provider-llm-backend`; this review's
  diff base (`0b7e302`) is that branch's tip at feature-008-start, exactly as CONTEXT.md specifies. ✓
- **Feature number 008** — used consistently throughout (`.context/features/008-...`, commit
  message prefixes `(008)`). ✓

No decision was quietly dropped or silently overridden.

## Interaction with Feature 007 — confirmed coherent, not just assumed

`pipeline/llm_select.py` was not touched by this feature (confirmed: absent from the diff's file
list). Verified by inspection and a fresh import test that it still correctly enumerates all four
new provider keys with zero code change needed: `_ALL_KEYS = list(PROVIDERS.keys()) + ["local"]`
and `_validate_or_exit()`/the auto-detect `configured = [k for k, p in PROVIDERS.items() if
os.environ.get(p["key_env"], "")...]` comprehension are both fully generic over dict contents.
Fresh check this pass:

```
py -c "import pipeline.llm_select; from config.models import PROVIDERS; print([k for k in PROVIDERS if k.startswith('openrouter')])"
# -> ['openrouter-nemotron', 'openrouter-nemotron-nano']
```

Both new OpenRouter keys and both new company-Qwen keys are live in `PROVIDERS` and reachable
through `--llm=<key>`, `LLM_DEFAULT`, auto-detect, and the interactive picker with zero
`llm_select.py` changes — the plan's assumption holds, confirmed rather than trusted.

## Goal alignment

Goal: "Add OpenRouter ... and a company-shared Qwen API key as additional selectable providers ...
without changing that feature's dispatch or selection logic beyond what research proves necessary."

**Achieved.** Four new providers are genuinely selectable through every existing mechanism
(`--llm=`, `LLM_DEFAULT`, auto-detect, interactive picker) with no changes to `llm_select.py` at
all. The one dispatch-logic change that did land (`_chat_completion()`'s OpenRouter reasoning-
disable branch, `_synthesize_sector()`'s widened wrapper hint) is exactly the "beyond what research
proves necessary" exception the goal statement itself anticipates — it's narrowly scoped
(`provider_key.startswith("openrouter")`, confirmed unreachable for any other provider key),
traced directly to a live-tested failure mode (RESEARCH.md §4), and proven to fix it end-to-end
through the real dispatch path (Task 004's live evidence). `_synthesize_summary()` was correctly
left untouched per the task's explicit scope boundary. The registry-only entries
(`company-qwen-flash`, `company-qwen-plus`, and `openrouter-nemotron-nano`) required, and received,
zero code changes beyond the shared reasoning-disable branch (which also correctly applies to them,
since they share `_chat_completion()`). The feature holds together as a coherent whole: docs,
registry, and code fix are all mutually consistent and cross-referenced correctly.

## Findings

None that block PASS. Two minor observations, neither a defect:

1. `company-qwen-plus`'s model string (`qwen3.7-plus`) is documentation-confirmed but not
   live-verified against the real company account — this is disclosed accurately in the registry
   comment itself and in RESEARCH.md §6, not silently shipped as if verified. Consistent with the
   same precedent Feature 007 set for `kimi-k3`. Not a defect in this feature; a known,
   transparently-flagged gap for a future session to close if that entry is ever selected.
2. `requirements.txt` is untouched by this feature (confirmed via diff) — the `extra_body` kwarg
   used in Task 002's fix is already supported by the `openai==2.46.0` version Feature 007 pinned,
   so no new dependency was needed and none was added. Feature 007's own `requirements.txt`
   pollution defect (its Finding 1) does not recur here.

## Evidence (re-run fresh in this pass)

1. `git diff 0b7e302ddc20b262b668630b1f60ac9e42fb86be..HEAD --stat` → 10 files changed (6 feature-doc
   files, `.env.example`, `README.md`, `config/models.py`, `pipeline/analyst.py`); `requirements.txt`
   absent from the list, confirmed via a direct diff on that path (empty).
2. `py -c "import ast; ast.parse(open('config/models.py', encoding='utf-8').read()); print('syntax OK')"`
   → `syntax OK`.
3. `py -c "from config.models import PROVIDERS; assert set(PROVIDERS) == {...8 keys...}; ..."` →
   `OK ['company-qwen-flash', 'company-qwen-plus', 'deepseek', 'groq', 'kimi', 'openrouter-nemotron', 'openrouter-nemotron-nano', 'qwen']`.
4. `py -c "import pipeline.analyst; print('analyst OK')"` → imports cleanly.
5. `py -c "import pipeline.llm_select; from config.models import PROVIDERS; print([k for k in PROVIDERS if k.startswith('openrouter')])"`
   → `['openrouter-nemotron', 'openrouter-nemotron-nano']` (llm_select needs zero code change to see
   the new keys — confirmed, not assumed).
6. `py -m pytest tests/test_clamp.py -q` → `6 passed in 16.89s`.
7. `grep -n 'provider_key == "local"' pipeline/analyst.py` → 4 occurrences read in context; confirmed
   only the `_synthesize_sector()` one (line 298) was widened to also match `openrouter*`; the
   `_chat_completion()` dispatch branch (line 197), `_synthesize_summary()`'s hint (line 354), and
   `analyse()`'s client-construction branch (line 472) are all unchanged.
8. `grep -n "company-qwen\|openrouter" pipeline/*.py config/*.py main.py` → confirms no
   `company-qwen`-specific branching exists anywhere outside the registry data itself, and the only
   `openrouter`-specific code is the two sites Task 002 specified.
9. `py -c "import openai; print(openai.__version__)"` → `2.46.0`;
   `inspect.signature(Completions.create)` → confirms `extra_body` is a real parameter of the
   installed SDK, not a new/unverified dependency surface.
10. `git status --short` → clean (nothing untracked, nothing modified) — all feature-doc files
    (CONTEXT.md, RESEARCH.md, task files) are committed, unlike Feature 007's first-pass Finding 2.
11. `git log --oneline 0b7e302..HEAD -- pipeline/analyst.py` → exactly one commit (`e25fa25`),
    which predates the commit carrying Task 004's live-verification evidence (`4d3c86c`) —
    confirms that evidence is still valid for the current code state; no re-run performed, per this
    project's quota-discipline norm and this task's explicit instruction not to re-spend OpenRouter's
    shared free-tier quota.
12. Did **not** make any new live OpenRouter or company-Qwen API calls in this review pass — per
    explicit instruction, both are quota/cost-sensitive shared resources already exercised
    appropriately during planning (RESEARCH.md's 6 calls) and execution (Task 004's 1 call).

## Result

**PASS**

Every task's code deliverable (001-004) matches its spec exactly, confirmed via fresh `git diff`
reads rather than trusting task files' own self-reported evidence. Every CONTEXT.md Implementation
Decision is correctly implemented, including the one legitimate, disclosed exception (the
reasoning-disable code change, explicitly permitted by CONTEXT.md's own "unless research proves
otherwise" wording and fully traced to live-tested evidence). The interaction with Feature 007's
already-reviewed dispatch/selection logic is coherent: `pipeline/llm_select.py` required, and
received, zero changes, confirmed by inspection and a fresh import/enumeration check rather than
assumed. The feature satisfies its stated goal — four new providers genuinely selectable through
the existing generic mechanisms, with the one necessary logic change narrowly scoped, justified, and
proven end-to-end by Task 004's live-verification evidence, which remains valid since no later
commit touched `pipeline/analyst.py` again.
