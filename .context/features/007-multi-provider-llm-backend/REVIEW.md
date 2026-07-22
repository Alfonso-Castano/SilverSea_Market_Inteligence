# Review: Multi-Provider LLM Backend

**Base:** `ad81ca161e35f148eb86bd9313e65d4bc4bda2f9` — diff taken fresh in this pass via
`git diff ad81ca161e35f148eb86bd9313e65d4bc4bda2f9..HEAD`, not from any task file's own
description.

## Task-level check

- **001 (provider registry)** — `config/models.py` matches the task's verbatim spec exactly:
  `PROVIDERS` (deepseek/groq/qwen/kimi), `LLM_DEFAULT`, `GROQ_MODEL`, `LOCAL_MODEL`/`LOCAL_NUM_CTX`
  all present with the right shape. One legitimate post-hoc amendment: `GROQ_MODEL` and
  `PROVIDERS["groq"]["model"]` were both updated from the dead
  `meta-llama/llama-4-scout-17b-16e-instruct` to `llama-3.3-70b-versatile` (commit `496a864`,
  Task 007's amendment) — kept in sync between the two, as required. ✓
- **002 (dependencies)** — `openai==2.46.0` and `ollama==0.6.2` are both present and importable, as
  claimed. **However**, the regenerated `requirements.txt` contains 79 top-level packages that were
  never in the file before and have nothing to do with this project or feature (confirmed by diffing
  the full package-name sets of both file versions — see Evidence). This is a real defect, not
  benign "transitive drift" as the task's own evidence claimed — see Findings below. ✗
- **003 (generalize analyst.py dispatch)** — `_chat_completion()`, `SECTOR_SYNTHESIS_SCHEMA`,
  `SUMMARY_SCHEMA` inserted exactly as specified; `_extract_sector`/`_synthesize_sector`/
  `_synthesize_summary`/`analyse()` signatures all gained `provider_key` exactly as specified;
  `analyse()`'s client construction branches on `"local"` vs. `openai.OpenAI(base_url=..., ...)`
  exactly as specified. Confirmed via fresh `git diff` read: every hunk touches only imports, the
  new dispatch/schema block, the four signatures, the three call-site try-bodies, the two
  local-only hints, and `analyse()`'s client init + call sites — `SECTOR_EXTRACT_PROMPT`/
  `SECTOR_SYNTHESIS_PROMPT`/`SUMMARY_PROMPT`/`_build_rag_context`/`_generate_implications`/
  `_derive_competition_risks`/`_clamp_opportunity_scores`'s body are byte-identical to base. No
  `from groq import Groq` or `GROQ_MODEL` reference remains in the file. ✓
- **004 (`pipeline/llm_select.py`)** — file content is byte-for-byte what the task specified.
  Re-exercised fresh in this pass (not just trusting the task's own evidence): unknown-key path
  exits 1 with the documented stderr message; auto-detect path with exactly one provider key set
  returns that key with no prompt. Matches spec. ✓
- **005 (wire `--llm=` into main.py)** — `run_pipeline()` signature gained `provider_key`;
  `resolve_provider(llm_arg)` is called exactly once in the `if __name__ == "__main__":` block,
  outside `run_pipeline()`'s per-country loop; `analyse(filtered, country, provider_key)` is the
  call site inside the loop. Confirmed via fresh signature introspection. ✓
- **006 (docs)** — `.env.example` has all 7 required vars; README mentions `--llm` and DeepSeek in
  the three targeted spots the task named. One extra, reasonable fix landed same-day but outside
  Task 006's own commit: `e428108` corrected the Qwen signup URL from Alibaba's China-domestic
  console to the international portal (the registry's `base_url` is the `-intl` endpoint, so a
  China-domestic account key wouldn't authenticate) — caught while walking Alfonso through signup
  for Task 007's live verification. Small, factual, in the same file this task already owns; not a
  scope violation. ✓
- **007 (live verification, amended scope)** — Amendment is real and openly documented, not a
  quiet drop (see the Amendment section at the top of the task file and commit `496a864`'s
  message). Groq's live call was re-run after the dead-model fix and passed: 4 signals, 3
  opportunities, clamp invariants held (`total_score == sum(scores.values())`, every dimension in
  `[1,5]`). `py -m pytest tests/test_clamp.py -q` passed. `git status` showed no verification-script
  residue. DeepSeek-native's live call is explicitly reported as **deferred**, not silently skipped
  — see the dedicated judgment-call discussion below. ✓ (with the deferral treated as acceptable,
  not a task-level failure — see below)

## Decision coverage

Checked every Implementation Decision in CONTEXT.md against the code:

- **Default provider DeepSeek, not Groq** — implemented as intended: this is a *documentation-level*
  default (`.env.example`/README recommend `DEEPSEEK_API_KEY` first), not a hardcoded
  code-level fallback — correctly so, since CONTEXT.md's own "silent zero-friction default
  preserved" decision requires whichever single provider's env var is set to win, not a
  hardcoded DeepSeek preference. Verified: `resolve_provider(None)` with exactly one (non-DeepSeek)
  key set returns that key, not `"deepseek"`. ✓
- **Provider registry lives in `config/models.py`, not a new file** — done. ✓
- **One generic OpenAI-compatible dispatch branch covers Groq/DeepSeek/Qwen/Kimi; Ollama keeps its
  own branch** — done, confirmed in `_chat_completion()`: exactly one `if provider_key == "local"`
  branch, one generic `client.chat.completions.create(...)` branch below it, no per-remote-provider
  branching anywhere. ✓
- **`--llm=` resolved once, before the per-country loop** — done, verified by inspection of the
  `__main__` block. ✓
- **`LLM_DEFAULT` env var as the no-prompt-ever switch** — done, `resolve_provider()`'s priority
  order matches exactly (`--llm` > `LLM_DEFAULT` > auto-detect > picker). ✓
- **tkinter popup fallback on any failure, not a `DISPLAY` pre-check** — done: `_pick_via_tkinter`
  is wrapped in a bare `try/except Exception` at the call site in `_interactive_pick`, no
  `DISPLAY` check anywhere in the file. ✓
- **Cancelled/closed picker aborts cleanly, no silent default** — done: `_interactive_pick`'s
  `picker_ran` flag distinguishes "tkinter mechanism failed" (→ terminal fallback) from "tkinter
  ran but returned no choice" (→ `sys.exit(1)`, no terminal fallback attempted). ✓
- **`--llm=<key>` naming an unconfigured provider fails fast before scraping** — done and
  re-verified fresh in this pass (`resolve_provider('deepseek')` with the key unset exits 1 with
  the documented message, before any pipeline stage runs). ✓
- **Admin-page LLM toggle deferred, not built** — confirmed: `app.py`, every file under
  `templates/`, `pipeline/feedback.py`, `pipeline/weekly.py` all show an empty diff against base
  (`git diff ... --stat` for those paths returns nothing). ✓
- **`feature/002`'s Ollama path reused, not re-verified** — `_chat_completion`'s local branch,
  `SECTOR_SYNTHESIS_SCHEMA`/`SUMMARY_SCHEMA`, `LOCAL_MODEL`/`LOCAL_NUM_CTX` are all present and
  structurally consistent with `feature/002`'s shape; Task 007 correctly did not attempt a live
  Ollama call, matching CONTEXT.md's explicit scope exclusion. ✓
- **Anthropic/China-geofencing note** — recorded as a flag for a future `.context/DECISIONS.md`
  entry, not a code change; out of this review's scope to verify beyond confirming CONTEXT.md
  itself documents it (it does, Scope section, final bullet). ✓

No decision was quietly dropped. The one real scope change (DeepSeek-native's live-verification
gate) was explicit, user-authorized, and documented — evaluated on its own below, not silently
passed over.

## Judgment call: is the DeepSeek-native live-verification deferral acceptable for a PASS?

**Yes, on its own — the deferral itself does not sink this review.** Reasoning:

1. **The architecture claim it would have proven is already proven, by the identical code path.**
   CONTEXT.md's core promise — "one generic OpenAI-compatible dispatch branch... no per-provider
   branching" — means DeepSeek and Groq run through the *exact same* `_chat_completion()` code,
   differing only in `base_url`/`api_key`/`model` values pulled from the same `PROVIDERS` dict
   structure. Groq's live call already exercised that shared code path end-to-end (real HTTP call,
   real JSON-mode response, real clamp application) after the transport-layer change. There is no
   DeepSeek-specific branch that could hide a DeepSeek-only defect — if the generic branch works
   for one OpenAI-shaped provider, it works for the shape itself, which is what all four remote
   providers share.
2. **The failure is external and specifically diagnosed, not a mystery.** `402 Insufficient
   Balance` is DeepSeek's own billing-layer response — it means the key authenticated
   successfully and reached the API; the account simply has no usable balance. This is not a
   symptom that could also be explained by a code defect (wrong base_url, wrong model string, or a
   dispatch bug would produce a different error — 401/404/400, not 402).
3. **It's a real, user-made scope decision, not an executor cutting a corner.** Alfonso explicitly
   redirected the practical "default provider" story toward OpenRouter mid-session and chose not
   to fund the DeepSeek-native test account right now. That's a legitimate call for the project
   owner to make, and it's recorded transparently in Task 007's Amendment and in `496a864`'s commit
   message — not something this review had to dig for.
4. **CONTEXT.md's own constraint is honored, not violated.** CONTEXT.md explicitly says "Don't
   claim 'China-verified' in this feature's own REVIEW.md — that status depends on a confirmation
   this feature can't produce itself" and separately says DeepSeek's *correctness* (does it produce
   a sane report) is this feature's job "to verify directly." Task 007 does NOT claim DeepSeek is
   verified — it explicitly reports the gap as deferred. That is the honest state CONTEXT.md asked
   for, not a rounded-up completion claim CLAUDE.md's verification discipline would reject.

**One caveat worth surfacing, not a fail condition on its own:** the `402` result is mild negative
evidence against the "DeepSeek: ...cheapest, most generous free tier..." framing baked into
`config/models.py`'s comments and `.env.example`/README's documentation — RESEARCH.md itself already
flagged the exact free-tier figure as "not independently confirmed against the official pricing
page." A real account hitting `402` on what should be a fresh signup's granted balance is a data
point that this framing may be optimistic. Not something to fail this feature over (verifying
DeepSeek's *billing terms* was explicitly out of this feature's scope per CONTEXT.md's Global
Constraints — that's leo.li's/Alfonso's own out-of-band confirmation), but worth flagging so a
future OpenRouter-integration feature or a DeepSeek-native retry doesn't re-assume the "no card
needed" framing is settled fact.

## Goal alignment

Goal: make `pipeline/analyst.py`'s LLM calls provider-agnostic and switch the default provider to
one reachable from mainland China, while keeping the backend genuinely swappable for testing other
candidates.

**Provider-agnostic dispatch: achieved and proven.** One generic branch now serves four remote
providers plus the existing local branch; Groq's exact prior behavior is preserved end-to-end
(same model output shape, same clamp behavior) through the new transport. **Swappability: achieved
and proven** — `--llm=`, `LLM_DEFAULT`, auto-detect, and the interactive picker all work as
specified and were re-exercised fresh in this pass. **"Switch default to a China-reachable
provider": code-complete but not live-verified this round** — DeepSeek's registry entry, dispatch
path, CLI wiring, and docs are all in place and structurally sound, but the one live call that
would prove "China-based teammates can actually run this against DeepSeek and get a sane report"
was not obtained, for the external/billing reason discussed above, and is honestly reported as such
rather than rounded up. This is a real, acknowledged gap in the feature's headline goal — but not
one this review can hold the executor at fault for, given the judgment-call reasoning above.

The feature as a whole is architecturally sound and does what it says it does at the code level.
It is being held to a FAIL verdict below for an unrelated, independently-discovered reason — see
Findings.

## Findings

### Finding 1 (blocks PASS): `requirements.txt` regeneration introduced 79 unrelated top-level packages

Task 002's own evidence reported this as routine: "other transitive versions shifted as expected,
left as-is per constraint." That is not what actually happened. Comparing the full set of top-level
package names between the base commit's `requirements.txt` and HEAD's:

```
comm -13 <(old package names) <(new package names) | grep -v -E '^(openai|ollama)$'
```

... returns **79 packages** that were never in this file before and have no relationship to this
project's stack: `anthropic`, `fastapi`, `starlette`, `uvicorn`-adjacent (`sse-starlette`,
`python-multipart`), `mcp`, `mcp-server-fetch`, `google-generativeai`, `google-genai`,
`google-api-python-client`, `kubernetes`-adjacent (`pyasn1`, `rsa`, `cachetools`), `pygame`,
`nba_api`, `matplotlib`, `pandas`, `shap`, `scikit-learn`(-adjacent `scipy`/`numba`/`llvmlite`),
`pytest`, `pywin32`, `cryptography`, `openpyxl`, `fpdf2`, and 22 separate `tree-sitter-<language>`
grammar packages (`tree-sitter-go`, `-java`, `-rust`, `-swift`, `-cpp`, `-lua`, `-zig`, etc.).

Root cause: this dev machine has no project-scoped virtual environment (RESEARCH.md §9 already
flagged this), so Task 002's `pip freeze > requirements.txt` captured the *entire global
site-packages* — every package installed for every other tool/project on this machine (visibly,
several look like this Claude Code environment's own MCP/tree-sitter tooling, plus unrelated
personal projects: `pygame`, `nba_api`, `shap`). The file's own header comment says to regenerate
from "a fresh venv under 3.12.3" specifically to avoid this — Task 002's instruction to use "the
global `py` interpreter... matching how this file was generated previously" was itself an
incorrect premise (the prior, clean 127-line version of this file could not have come from a
polluted global environment; it must have used real isolation), and nothing in Task 002's execution
caught the mismatch between that premise and the header comment's own documented process.

**Why this blocks PASS, not just a note:** `requirements.txt` is a load-bearing, shipped artifact —
`README.md`'s own Build & Run section instructs a fresh clone to `pip install -r requirements.txt`.
As currently written, that command would attempt to install PyTorch/transformers-adjacent packages
(already present pre-feature, fine), plus now also FastAPI/Starlette/Uvicorn, a Kubernetes client,
Google Generative AI SDKs, PyGame, an NBA stats client, a SHAP explainability library, and 22
tree-sitter language grammars — multiple unnecessary, sizeable downloads with zero relationship to
this Flask/scraping/RAG pipeline. This directly undoes the "GitLab clone-readiness audit" work
recorded in `.context/STATE.md` (which specifically hardened `requirements.txt` for team
onboarding) and cuts against this exact feature's own spirit — lowering friction for teammates,
some on constrained China-side networks, to get the pipeline running.

A UTF-8 BOM (`EF BB BF`) was also introduced at the start of the file (confirmed via `xxd`), a
further symptom of the regeneration not going through the documented clean process — most `pip`
versions tolerate a BOM'd first comment line, but it's one more sign this file needs a clean
re-generation, not further ad hoc edits.

### Finding 2 (informational, not blocking): `CONTEXT.md`/`RESEARCH.md` were never committed

Both files exist on disk and were read as part of this review, but `git log -- <path>` for either
returns nothing — they're untracked in the working tree, unlike every task file (which are
committed). Doesn't affect runtime behavior; flagging so the dispatching session commits them
alongside this REVIEW.md rather than leaving planning artifacts perpetually untracked.

## Evidence (re-run fresh in this pass)

1. `py -m pytest tests/test_clamp.py -q` → `6 passed in 17.35s`.
2. `py -c "from config.models import PROVIDERS, LLM_DEFAULT, GROQ_MODEL, LOCAL_MODEL, LOCAL_NUM_CTX; ..."` →
   `OK dict_keys(['deepseek', 'groq', 'qwen', 'kimi'])`, `groq model in registry: llama-3.3-70b-versatile`.
3. `py -c "... inspect.signature(analyse) ..."` → `['filtered_results', 'country', 'provider_key']`.
4. `py -c "... inspect.signature(main.run_pipeline) ..."` → `['send_email', 'domain_arg', 'country_arg', 'provider_key']`.
5. `py -c "from pipeline.llm_select import resolve_provider"` → imports cleanly.
6. `py -c "import pipeline.feedback, pipeline.weekly"` → both import cleanly (unaffected by the
   registry change, as CONTEXT.md requires).
7. `resolve_provider('not-a-real-provider')` → stderr `Unknown LLM provider 'not-a-real-provider'.
   Known providers: deepseek, groq, qwen, kimi, local`, exit code **1** (confirmed via `$?`, not
   assumed).
8. `resolve_provider(None)` with a clean environment and only `DEEPSEEK_API_KEY` set (`env -i`,
   not just unset-in-shell) → returns `deepseek`, exit code 0, no prompt shown.
9. `git diff ad81ca161e35f148eb86bd9313e65d4bc4bda2f9..HEAD -- app.py templates/ pipeline/feedback.py pipeline/weekly.py tests/`
   → empty (confirms these files are genuinely untouched, not just claimed to be).
10. `git diff ad81ca161e35f148eb86bd9313e65d4bc4bda2f9..HEAD -- pipeline/analyst.py` read in full —
    confirmed every hunk stays within the scope Task 003 described; prompt constants and the
    post-processing functions listed in Task 003's "does NOT touch" list are byte-identical.
11. `requirements.txt` package-set diff (see Finding 1) — 79 net-new unrelated top-level packages,
    confirmed by set comparison, not by spot-checking a few suspicious lines.
12. `git status --short` → only `.context/features/007-multi-provider-llm-backend/{CONTEXT.md,RESEARCH.md}`
    untracked (Finding 2); no stray verification scripts or other modified files — Task 007's own
    "leave the working tree clean" constraint holds.
13. Did **not** re-run a live Groq or DeepSeek `analyse()` call in this pass — Task 007's own Groq
    evidence (4 signals, 3 opportunities, clamp invariants held, captured this same day) is accepted
    as current, since the only change since that evidence was captured is the unrelated
    `requirements.txt`/Qwen-doc commits, neither of which touches `pipeline/analyst.py` or the Groq
    model string again. Re-spending Groq's shared daily quota to re-confirm unchanged code would
    violate this project's own quota-discipline norm (CLAUDE.md).

## Fix verification (post-FAIL re-check)

Task 008 regenerated `requirements.txt` from a genuinely isolated, throwaway `.venv-regen`
(installed exactly the documented top-level dependency list plus this feature's `openai`/`ollama`
additions, nothing else), then deleted the venv. Independently re-run by the dispatching session,
not just trusting the executor's own report:

```
git show ad81ca161e35f148eb86bd9313e65d4bc4bda2f9:requirements.txt | grep -oE '^[A-Za-z0-9_.\-]+' | sort -u > old_pkgs.txt
grep -oE '^[A-Za-z0-9_.\-]+' requirements.txt | sort -u > new_pkgs.txt
comm -13 old_pkgs.txt new_pkgs.txt | grep -viE '^(openai|ollama)$'
```
→ `jiter` only (a legitimate transitive dependency of `openai`). None of the 79 previously-injected
unrelated packages (`fastapi`, `pygame`, `nba_api`, 22 `tree-sitter-*` grammars, etc.) remain.
BOM check (`open('requirements.txt','rb').read()[:3]`) → `b'# P'`, confirmed clean. File is 131
lines, down from the polluted version. `py -m pytest tests/test_clamp.py -q` → `6 passed`,
confirming the regeneration didn't break the import chain. Finding 2 (untracked `CONTEXT.md`/
`RESEARCH.md`) also resolved — both committed alongside this file.

## Result

**PASS**

Both findings from the original FAIL pass are resolved and independently re-verified in this same
session (task 008, commit `90936cd`). Every task's code deliverable (001, 003, 004, 005, 006, 007,
008) matches its spec, every `CONTEXT.md` Implementation Decision is correctly implemented, the
DeepSeek-native live-verification deferral is judged acceptable on its own merits (external billing
failure, not a code-path ambiguity — the shared dispatch code was already proven end-to-end via
Groq's live call), and `requirements.txt` now installs cleanly with no unrelated packages.

**Carry-forward for the next feature (OpenRouter + company-key work), not a defect in this one:**
DeepSeek-native's live "China-reachable default" claim remains code-complete but not live-proven —
the account's `402 Insufficient Balance` was never resolved, and Alfonso is redirecting the
practical default path to OpenRouter instead. A future feature's own evidence gate should carry
that live verification, against whichever provider ends up being the actual default.
