# Task 004: Live verification — OpenRouter default (`openrouter-nemotron`) through the real pipeline dispatch

**Status:** done
**Depends on:** Task 001 (registry entry must exist), Task 002 (the reasoning-disable +
JSON-array-wrapper fix this task's whole point is to prove actually works end-to-end, not just in
planning-time isolated probes)
**Model tier:** mid — executing and correctly interpreting three real LLM calls chained through
`analyse()` (does extraction produce real text, does sector synthesis produce a well-shaped
non-empty signal list, does the summary call produce valid opportunities with clamp invariants
holding) needs judgment, not just checking exit code 0.

## Files
- None modified in the repo. This task creates a throwaway verification script **outside** the
  repo (scratchpad directory, or OS temp dir) and must leave the working tree clean afterward —
  `git status` must show no new/modified files when this task finishes.

## What to do

This is this feature's hard evidence gate. Planning-time research (see
`.context/features/008-openrouter-company-provider/RESEARCH.md` §4) already proved, via isolated
probe calls, that `nvidia/nemotron-3-super-120b-a12b:free` produces correct, complete JSON when
called with reasoning disabled and the JSON-array wrapper hint — but those probes called the raw
OpenRouter API directly with a hand-copied prompt, not through `pipeline/analyst.py`'s actual
`analyse()` function with Task 002's real code changes applied. This task closes that gap: prove
the *real* dispatch path (`analyse()` → `_extract_sector()` → `_synthesize_sector()` →
`_synthesize_summary()`, all through Task 002's new `provider_key.startswith("openrouter")`
branches) works end-to-end for the new default.

**Prerequisite check before spending any tokens:** confirm `OPENROUTER_API_KEY` is set in `.env` or
the environment. If missing, report BLOCKED with that detail — do not attempt a partial run.

1. Write a small verification script to a path **outside this repo** (scratchpad directory if
   available, OS temp dir otherwise — never commit this file):

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

print(f"=== provider: openrouter-nemotron ===")
try:
    result = analyse(filtered, country, "openrouter-nemotron")
    signal_count = sum(len(v) for v in result.get("signals_by_sector", {}).values())
    print(f"  executive_summary items: {len(result.get('executive_summary', []))}")
    print(f"  signals_by_sector: {list(result.get('signals_by_sector', {}).keys())} ({signal_count} total signals)")
    print(f"  opportunities: {len(result.get('opportunities', []))}")
    for opp in result.get("opportunities", []):
        scores = opp.get("scores", {})
        print(f"    - {opp.get('title')!r} total_score={opp.get('total_score')} scores={scores} source_name={opp.get('source_name')!r}")
        assert opp.get("total_score") == sum(scores.values()), "clamp/total_score mismatch"
        assert all(1 <= v <= 5 for v in scores.values()), "score out of 1-5 range"
    print(f"  competition_risks: {len(result.get('competition_risks', []))}")
    print(f"  PASS — openrouter-nemotron produced a well-formed report" if signal_count > 0 else "  FAIL — zero signals extracted")
except Exception as e:
    print(f"  FAIL — openrouter-nemotron raised: {e}")
```

2. Run it once (`py <path-to-script>`), capture the full output.
3. Delete the script immediately after running it.

## Interfaces
- Calls `pipeline.analyst.analyse(filtered_results, country, provider_key)` directly (the same
  entry point Feature 007's Task 007 used) — bypasses `main.py`/scraping/filtering entirely, per
  CLAUDE.md's stage-by-stage-verification preference.

## Constraints
- Run this exactly once for `openrouter-nemotron` — do not loop, retry on transient errors, or
  re-run "just to be sure." **OpenRouter's free tier counts failed requests against the daily quota
  too** (confirmed during this feature's research) — a naive retry-on-failure loop burns quota
  faster than a normal call pattern would suggest. If it fails once, read the error, understand it,
  and report BLOCKED or FAILED with the real reason rather than retrying blind.
- Do **not** also live-test `openrouter-nemotron-nano` in this task — it shares the identical code
  path Task 002 fixed, and planning-time research (RESEARCH.md §4) already confirmed the same
  reasoning-disable + wrapper-hint fix works for it in isolation. Verifying only the default through
  the real dispatch path, and leaving `openrouter-nemotron-nano` "registered but not live-verified
  through the full pipeline this round," matches the exact precedent this project already set for
  `kimi-k3` (Feature 007) and DeepSeek-native (Feature 007, deferred). Testing both would double
  this task's real spend for no new information about whether Task 002's *code* works.
- Do **not** attempt either `company-qwen-*` entry here — CONTEXT.md's own open question on this was
  resolved by explicit instruction: the company key already got a successful plain-text smoke test
  in a prior session, and re-testing it (through the pipeline or otherwise) would spend real paid
  company credit for no new information. Out of this task's scope.
- Do not attempt Groq/DeepSeek/Qwen-direct/Kimi/local here — unaffected by this feature's changes,
  already covered by Feature 007's own verification task.
- The verification script must not be written anywhere inside this git repository at any point —
  must not appear in `git status`.
- Also run the existing unit test as a fast, zero-LLM-cost regression check:
  `py -m pytest tests/test_clamp.py -q`

## Verification
1. The `analyse()` call in the script completes without raising, and the result:
   - has non-empty `signals_by_sector` (the single fixture source has clear concrete signals — a
     zero-signal result means Task 002's fix didn't actually work end-to-end; investigate the
     printed script output for an "Error extracting/synthesizing..." line before concluding
     anything, and report BLOCKED with that detail rather than silently calling it a pass).
   - every opportunity (if any) has `total_score == sum(scores.values())` and every dimension in
     `[1, 5]` — the script's own `assert` statements enforce this.
   - `opportunities`' `source_name` fields (if any) are real, non-placeholder values, not the
     literal string "Extracted signals" — this project has a known, separate, pre-existing bug of
     that exact shape (see `.context/STATE.md`'s Known Bugs section); if you observe it here, note
     it in your evidence as an observation, not something this task is scoped to fix.
2. `py -m pytest tests/test_clamp.py -q` passes.
3. `git status` (from repo root) shows no new or modified files.
4. In your evidence, paste the script's full stdout (signal counts, opportunity counts/scores,
   PASS/FAIL line) — a "should work" or "ran successfully" claim without the actual output is not
   sufficient per this project's verification-before-done rule.
5. If the call fails, report FAILED (not a silent retry) with the exact error text, and flag
   whether it looks like a Task 002 code defect (e.g. still-malformed JSON) vs. an external issue
   (e.g. OpenRouter rate-limited, model temporarily unavailable) — this distinction determines
   whether Task 002 needs rework or this is a transient, report-and-move-on condition.

## Evidence

Live `analyse(filtered, country, "openrouter-nemotron")` call (fixture: single BER government-grant source), through the real dispatch path (`analyse()` → `_extract_sector()` → `_synthesize_sector()` → `_synthesize_summary()`, exercising Task 002's actual code changes, not an isolated probe):
- 4 signals extracted under Government & Agencies, 2 opportunities generated. Clamp invariants held for both: `total_score == sum(scores.values())` (23 = 5+5+3+5+5, 20 = 5+4+3+3+5), every dimension in `[1,5]`.
- `source_name` on both opportunities correctly resolved to the real fixture source name (`'Test Fixture Source'`) — the pre-existing, separately-tracked `source_name` placeholder bug (`.context/STATE.md` Known Bugs) was not observed in this single-source run.
- `py -m pytest tests/test_clamp.py -q` → `6 passed`.
- Ran exactly once, per the OpenRouter-quota constraint (failed requests count against the daily limit too) — passed on the first attempt, no retry needed.
- Verification script written outside the repo, deleted immediately after; `git status` confirmed clean (only pre-existing untracked feature-doc files).

`openrouter-nemotron-nano`, both `company-qwen-*` entries, and Groq/DeepSeek/Qwen-direct/Kimi/local were deliberately not touched, per this task's scope.
