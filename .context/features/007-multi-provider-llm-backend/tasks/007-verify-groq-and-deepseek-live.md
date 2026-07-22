# Task 007: Live verification — Groq (regression) and DeepSeek (new default)

**Status:** done (amended scope — Groq verified live; DeepSeek-native explicitly deferred, see Amendment above)
**Depends on:** Task 002 (`openai`/`ollama` installed), Task 003 (`analyse()`'s new dispatch),
Task 005 (main.py wiring — not exercised directly here, but confirms the whole chain is
consistent up to this point).
**Model tier:** mid — executing and correctly interpreting two real LLM calls (does the JSON
parse, are signals/opportunities structurally sane, did clamping still apply) needs judgment, not
just running a fixed command and checking exit code 0.

**Amendment (post-planning, before this re-run):** Two things changed since this task was
written. (1) Groq's `meta-llama/llama-4-scout-17b-16e-instruct` was found dead (removed from
Groq's catalog entirely — confirmed via live `models.list()`, unrelated to this feature) and has
been fixed in `config/models.py` to `llama-3.3-70b-versatile`. (2) DeepSeek-native
(`api.deepseek.com`) hit `402 Insufficient Balance` on the account tied to the key in `.env`;
Alfonso has separately decided to pursue OpenRouter as the practical default path instead of
fixing DeepSeek-native's balance right now (see this session's conversation — DeepSeek-native
stays a valid, already-built registry entry, just not live-verified this round). **This re-run
verifies Groq ONLY.** Ignore the "both keys must be set" prerequisite check below for DeepSeek —
only `GROQ_API_KEY` needs to be present. Run only the `provider_key = "groq"` iteration of the
verification script (drop the `"deepseek"` entry from the loop). Report DeepSeek-native's
verification status as **explicitly deferred**, not blocked and not skipped-silently — a future
feature (OpenRouter integration, not yet scoped) will carry the live "default provider" evidence
gate instead.

## Files
- None modified in the repo. This task creates a throwaway verification script **outside** the
  repo (see below) and must leave the working tree clean afterward — `git status` must show no
  new/modified files when this task finishes.

## What to do

This is the feature's hard evidence gate for its one genuinely risky, unverifiable-by-inspection
claim: that DeepSeek (the new default) actually works end-to-end through the generalized
dispatch, and that Groq (the existing, previously-verified path) still behaves identically now
that its calls go through `openai.OpenAI(base_url=..., ...)` instead of the dedicated `groq`
package. Per CLAUDE.md's verification rule, prefer a scoped `analyse()` call over a full
`py main.py` run — this avoids burning scrape time and keeps the token cost to exactly what's
needed to prove the claim (two small `analyse()` calls, not a real multi-sector pipeline run).

**Prerequisite check before spending any tokens:** confirm `DEEPSEEK_API_KEY` and `GROQ_API_KEY`
are both set in `.env` (or the environment). If either is missing, report BLOCKED with exactly
which key is missing and do not attempt a partial run — both providers need to be verified in
this task, not just one.

1. Write a small verification script to a path **outside this repo** (use the scratchpad
   directory if your environment provides one, or the OS temp directory otherwise — never commit
   this file) with this content:

```python
import os
import sys
sys.path.insert(0, r"<REPO_ROOT>")  # replace with this repo's actual absolute path

from dotenv import load_dotenv
load_dotenv(r"<REPO_ROOT>\.env")

from pipeline.analyst import analyse

country = {"code": "SG", "name": "Singapore"}
filtered = [{
    "sector": "gov_agencies",
    "name": "Test Fixture Source",
    "url": "https://example.com/test-fixture",
    "content": (
        "The Building and Construction Authority (BCA) announced a new S$5 million Smart "
        "Building Grant on 2026-06-01, open to applications from digital twin and BIM "
        "technology vendors until 2026-08-01. XYZ Facilities Corp was named as the first "
        "pilot partner under the programme, which funds smart facility management and "
        "IoT retrofit projects across 12 government buildings. A second S$2 million tranche "
        "for 3D scanning and virtual inspection pilots opens for applications in Q4 2026."
    ),
}]

for provider_key in ["groq", "deepseek"]:
    print(f"\n=== provider: {provider_key} ===")
    try:
        result = analyse(filtered, country, provider_key)
        signal_count = sum(len(v) for v in result.get("signals_by_sector", {}).values())
        print(f"  executive_summary items: {len(result.get('executive_summary', []))}")
        print(f"  signals_by_sector: {list(result.get('signals_by_sector', {}).keys())} ({signal_count} total signals)")
        print(f"  opportunities: {len(result.get('opportunities', []))}")
        for opp in result.get("opportunities", []):
            scores = opp.get("scores", {})
            print(f"    - {opp.get('title')!r} total_score={opp.get('total_score')} scores={scores}")
            assert opp.get("total_score") == sum(scores.values()), "clamp/total_score mismatch"
            assert all(1 <= v <= 5 for v in scores.values()), "score out of 1-5 range"
        print(f"  competition_risks: {len(result.get('competition_risks', []))}")
        print(f"  PASS — {provider_key} produced a well-formed report")
    except Exception as e:
        print(f"  FAIL — {provider_key} raised: {e}")
```

2. Run it once (`py <path-to-script>`), capture the full output.
3. Delete the script immediately after running it — this must never be committed or left in the
   repo working tree.

## Interfaces
- Calls `pipeline.analyst.analyse(filtered_results, country, provider_key)` directly (Task 003's
  new signature) — bypasses `main.py`/scraping/filtering entirely, per CLAUDE.md's
  stage-by-stage-verification preference.

## Constraints
- Run this exactly once per provider — do not loop, retry on transient errors more than once, or
  re-run "just to be sure." Both Groq's daily quota and DeepSeek's free grant are finite and
  shared with any other work happening this session; this task's whole design point is minimizing
  real cost while still proving the claim.
- Do not attempt Qwen or Kimi here — CONTEXT.md's open question on their verification scope was
  resolved during planning (RESEARCH.md §8) as "registered but not live-verified this round,"
  matching how Ollama's entry has sat unverified since `feature/002`. Attempting them here would
  be out of this task's scope and this feature's decided verification budget.
- Do not attempt the local/Ollama path here either, for the same reason — CONTEXT.md explicitly
  says re-verifying `feature/002`'s Ollama path is out of scope for this entire feature.
- The verification script must not be written anywhere inside this git repository — it must not
  appear in `git status` at any point this task is being graded on. If you need to iterate on the
  script, iterate on the copy outside the repo.
- Also run the existing unit test as a fast, zero-LLM-cost regression check that
  `_clamp_opportunity_scores` itself wasn't touched: `py -m pytest tests/test_clamp.py -q`

## Verification
1. Both `analyse()` calls in the script above complete without raising, and each result:
   - has non-empty `signals_by_sector` (at minimum one sector, since the single fixture source
     should produce at least one extracted signal under both providers) — if either provider
     returns zero signals, investigate before concluding PASS: check the printed script output
     for an "Error extracting/synthesizing ..." line (from `analyst.py`'s own except-blocks) that
     would explain it, and report BLOCKED with that detail rather than silently calling it a pass.
   - every opportunity (if any) has `total_score == sum(scores.values())` and every dimension in
     `[1, 5]` — the script's own `assert` statements enforce this; a raised `AssertionError` here
     means the clamp isn't being applied consistently across providers and must be reported as a
     real finding, not swallowed.
2. `py -m pytest tests/test_clamp.py -q` passes (unrelated to the live calls, but confirms this
   feature didn't regress the one existing unit test).
3. `git status` (from the repo root) shows no new or modified files — the verification script
   left no trace in the repo.
4. In your evidence, paste the script's full stdout for both providers (signal counts,
   opportunity counts and scores, PASS/FAIL lines) — a "should work" or "ran successfully" claim
   without the actual output is not sufficient per this project's verification-before-done rule.

## Evidence

Live `analyse(filtered, country, "groq")` call (fixture: single BER government-grant source), against `llama-3.3-70b-versatile` via `openai.OpenAI(base_url="https://api.groq.com/openai/v1", ...)`:
- 4 signals extracted under Government & Agencies, 3 opportunities generated, all with `total_score == sum(scores.values())` and every dimension in `[1,5]` — clamp invariants held.
- `executive_summary`: 3 items. `competition_risks`: 0 (no competitor-sector signals in the single-source fixture, expected).
- `py -m pytest tests/test_clamp.py -q` → `6 passed`.
- Verification script written outside the repo, run exactly once, deleted immediately after — confirmed absent via `test -f`; `git status` showed no trace.

DeepSeek-native explicitly deferred per this task's Amendment (not attempted, not blocked) — Alfonso is pursuing OpenRouter as the practical default path instead; DeepSeek-native's live evidence gate is expected to move to a future OpenRouter-integration feature.
