# Task 008: First unit test — `tests/test_clamp.py` for the opportunity-scoring clamp

## Files

- `tests/test_clamp.py` (create — new file)
- `tests/__init__.py` (create — empty file, only if pytest's rootdir/discovery requires it in
  this repo's layout; check first, see Verification step 1)

## What to do

`pipeline/analyst.py`'s `_clamp_opportunity_scores(opportunities: list) -> list` (currently lines
194-207) is the Python-side safety net documented in `.context/DECISIONS.md`'s A1 decision: it
clamps each of the 5 score dimensions to the 1-5 range and recomputes `total_score` as their sum,
regardless of what the LLM returned. This has never had a test — this task adds the repo's first
one. It is pure-Python, takes a plain list of dicts, does no I/O, and needs no mocking — safe to
test directly with zero LLM cost.

Write `tests/test_clamp.py` covering these cases (per CONTEXT.md's decision, matching the Fable
review's proposed cases):

```python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.analyst import _clamp_opportunity_scores, _SCORE_DIMENSIONS


def _make_opp(scores=None):
    return {"title": "Test opportunity", "scores": scores or {}}


def test_out_of_range_dimensions_are_clamped():
    opp = _make_opp({
        "strategic_fit": 9,
        "revenue_potential": -3,
        "win_probability": 3,
        "urgency": 100,
        "intelligence_quality": 5,
    })
    result = _clamp_opportunity_scores([opp])[0]
    assert result["scores"]["strategic_fit"] == 5
    assert result["scores"]["revenue_potential"] == 1
    assert result["scores"]["win_probability"] == 3
    assert result["scores"]["urgency"] == 5
    assert result["scores"]["intelligence_quality"] == 5
    assert result["total_score"] == 19  # 5 + 1 + 3 + 5 + 5


def test_negative_and_non_numeric_values_default_to_one():
    opp = _make_opp({
        "strategic_fit": -5,
        "revenue_potential": "high",
        "win_probability": None,
        "urgency": 3,
        "intelligence_quality": 4,
    })
    result = _clamp_opportunity_scores([opp])[0]
    assert result["scores"]["strategic_fit"] == 1
    assert result["scores"]["revenue_potential"] == 1
    assert result["scores"]["win_probability"] == 1
    assert result["scores"]["urgency"] == 3
    assert result["scores"]["intelligence_quality"] == 4
    assert result["total_score"] == 10


def test_missing_dimensions_default_to_one():
    opp = _make_opp({"strategic_fit": 4})  # other four dims absent entirely
    result = _clamp_opportunity_scores([opp])[0]
    for dim in _SCORE_DIMENSIONS:
        assert dim in result["scores"]
    assert result["scores"]["strategic_fit"] == 4
    assert result["scores"]["revenue_potential"] == 1
    assert result["scores"]["win_probability"] == 1
    assert result["scores"]["urgency"] == 1
    assert result["scores"]["intelligence_quality"] == 1
    assert result["total_score"] == 8


def test_missing_scores_key_entirely_defaults_all_to_one():
    opp = {"title": "No scores field at all"}
    result = _clamp_opportunity_scores([opp])[0]
    assert result["total_score"] == 5  # 1 * 5 dimensions
    assert all(v == 1 for v in result["scores"].values())


def test_llm_supplied_bogus_total_score_is_overridden():
    opp = _make_opp({
        "strategic_fit": 5,
        "revenue_potential": 5,
        "win_probability": 5,
        "urgency": 5,
        "intelligence_quality": 5,
    })
    opp["total_score"] = 999  # LLM hallucinated an out-of-range total
    result = _clamp_opportunity_scores([opp])[0]
    assert result["total_score"] == 25  # recomputed from clamped dims, not trusted from input


def test_multiple_opportunities_are_each_clamped_independently():
    opps = [
        _make_opp({"strategic_fit": 10, "revenue_potential": 1, "win_probability": 1, "urgency": 1, "intelligence_quality": 1}),
        _make_opp({"strategic_fit": 1, "revenue_potential": 1, "win_probability": 1, "urgency": 1, "intelligence_quality": 1}),
    ]
    result = _clamp_opportunity_scores(opps)
    assert result[0]["total_score"] == 9   # 5+1+1+1+1
    assert result[1]["total_score"] == 5   # 1+1+1+1+1
```

Adjust the `sys.path.insert` boilerplate only if step 1 of Verification below shows pytest can
already resolve `pipeline` from the repo root without it (in which case simplify the import to a
plain `from pipeline.analyst import ...` and drop the `sys`/`os` lines) — the boilerplate above is
a safe default given this repo has no existing `conftest.py`/`pyproject.toml` pytest config.

## Interfaces

No production code changes — this task only adds a test file. It imports
`pipeline.analyst._clamp_opportunity_scores` and `pipeline.analyst._SCORE_DIMENSIONS`, both of
which already exist and are untouched by this feature's other tasks.

## Constraints

- Do not modify `pipeline/analyst.py` in this task — if `_clamp_opportunity_scores` needs a
  behavior change to make a test pass, that's a signal the test is wrong, not the function (its
  current behavior is the documented, correct spec per `.context/DECISIONS.md`'s A1 entry).
- Plain `pytest` only — no new test framework, no fixtures library beyond what pytest ships with.
- This is the first test file in the repo — don't add a `pytest.ini`/`pyproject.toml` config
  unless Verification step 1 shows test discovery genuinely fails without one; prefer the
  in-file `sys.path` shim over introducing new config files if either approach works.

## Verification

1. First, check whether `pipeline` is importable from repo root without the path shim: run
   `py -m pytest tests/test_clamp.py -v` (or `python3 -m pytest tests/test_clamp.py -v`) from the
   repo root. If it passes without the `sys.path.insert` lines, you may simplify the import (see
   note above) — but leaving the shim in is also acceptable and safer against future working-
   directory changes.
2. Run `py -m pytest tests/test_clamp.py -v` and confirm all 6 test functions pass (exit code 0).
3. Confirm no Groq API key or network access was needed — the test run should succeed even if
   `GROQ_API_KEY` is unset in the environment (since `_clamp_opportunity_scores` never touches the
   Groq client).
4. Run `py -m pytest tests/ -v` (whole `tests/` directory, not just this file) to confirm nothing
   else in the directory is broken by this file's presence — trivial today since it's the only
   test file, but establishes the pattern for future test files.

## Model tier

cheap — the full test file content is given verbatim above; the executor's job is to create the
file, run the verification commands, and adjust only the import-shim detail based on what step 1
of Verification shows.

## Depends on

None. Does not touch `pipeline/analyst.py`, so it has no file-ownership conflict with task 004
(which edits `analyst.py`'s prompts and post-processing functions but explicitly does not touch
`_clamp_opportunity_scores`) — safe to execute in parallel with task 004.

## Evidence

**Status: DONE**

`py -m pytest tests/ -v` → 6 passed in 10.81s, independently re-run by the dispatching session.
`GROQ_API_KEY` unset in the environment throughout — zero LLM/network dependency confirmed.
`tests/__init__.py` was added alongside `tests/test_clamp.py` for pytest discovery; the
`sys.path.insert` shim from the task file was kept as-is.
