# Task 005: Code-correctness review — domain/country data flow and gate consistency (creates CODE-REVIEW.md)

**Status:** pending
**Depends on:** none
**Model tier:** quality — pin to Opus (`opus`). Per Alfonso's 2026-07-10 directive (CONTEXT.md Global
Constraints), the code-correctness/technical-review half of this feature is explicitly assigned Opus —
this is the area Alfonso trusts least (rapid cheap/mid-tier dispatches produced the code under review)
and wants the deepest available analysis applied. Note: this environment's `opus` tier resolves to
Opus 4.8, the same model the main dispatching session runs as — there is no mechanism to pin this
subagent to an older Opus point-release (see CONTEXT.md's feasibility note).

## Files
- Create: `.context/features/006-vn-my-accuracy-review/CODE-REVIEW.md` (this task creates the file with
  a shared header + sections 1-2; Task 006 appends a section 3 afterward — do not let Task 006 run
  concurrently with this one, they write the same file)

## What to do

Review whether the codebase actually wires VN/MY source data through to report output correctly. This
task covers the **current merged code state** (not git history — that's Task 006). Read
`.context/features/006-vn-my-accuracy-review/RESEARCH.md` in full first — §2-4 already confirmed several
findings with exact file/line evidence; your job is to verify those still hold (quick re-check, code may
have shifted slightly), write them up properly, and extend the review to anything RESEARCH.md didn't
already nail down. Do not silently fix anything — this task produces a findings document only (see
CONTEXT.md's "no silent fixes" decision; three of these findings already have separate, optional fix
tasks — 007, 008, 009 — cross-reference them by task number in your writeup, don't duplicate their
content).

**Areas to cover, each with a findings entry (even if "no issue found"):**

1. **Domain filtering correctness** (`main.py`, `app.py`'s `_domain_mode()`) — confirm
   `run_pipeline()`'s `sources = [s for s in sources if domain_arg in s.get("domain", ["GENERAL"])]`
   (main.py ~line 57-58) correctly handles both single-string and list-valued `domain` fields in
   `config/sources.json` (check a few real VN entries with list-valued `domain`, e.g. the 2
   `["BER","EDU"]`-dual-tagged ones). Confirm `app.py`'s `_domain_mode()` (line ~81-83) and the
   `report()`/`internals()` fallback logic around it are internally consistent — RESEARCH.md §4 (lead 2)
   already confirmed the `("BER", "EDU", "GENERAL")` hardcoded fallback tuple doesn't match
   `_domain_mode()`'s full 8-domain list; verify this is still true in this worktree's `app.py` and write
   it up (reference that it has an optional fix at Task 007 — don't fix it yourself here).

2. **Sector mapping** — confirm `pipeline/analyst.py`'s `SECTOR_LABELS` dict covers every `sector` value
   actually used in VN/MY's `config/sources.json` entries (`gov_agencies`, `associations`, `customers`,
   `partners`, `competitors`, `general_news`) with no silent fallback to a raw/ugly label for a typo'd
   sector value anywhere in the VN/MY source blocks.

3. **Keyword relevance gate vs. opportunities gate** — RESEARCH.md §3 already confirmed a real divergence
   between `pipeline/filter.py`'s per-country `config/sources.json`-driven keyword lists and
   `SUMMARY_PROMPT`'s hardcoded, global, gate keyword list in `pipeline/analyst.py`. Verify this is still
   accurate in the current code, and add anything RESEARCH.md's pass didn't fully cover — e.g. check
   whether MY's broader keyword list (99 keywords, includes retail/healthcare/tourism/manufacturing
   terms since MY has more active non-BER domains than VN) creates asymmetric behavior between the two
   countries' reports that's worth calling out explicitly.

4. **RAG retrieval scoping** (`pipeline/vectorstore.py`, `pipeline/analyst.py`'s `_build_rag_context()`
   and the `REPORT_HISTORY` write in `analyse()`) — RESEARCH.md §4 (lead 3) already confirmed `analyse()`
   never receives a `domain` parameter and `REPORT_HISTORY` writes are only country-tagged, not
   domain-tagged. Verify this still holds, and check what this concretely means for VN/MY: does
   `_build_rag_context()` get called at all in the current `analyse()` flow (check — RESEARCH.md notes it
   may be dead code, confirm one way or the other for this worktree), and if it is called, could a VN/BER
   run's RAG query pull in cross-domain "past report themes" now that 8 domains are active? Write up what
   you find — this is architecturally non-trivial (see RESEARCH.md's "Net effect" section), so it's a
   flagged finding, not a fix task.

5. **The `source_name` breakage's code-level root cause** — RESEARCH.md §2 already root-caused this to
   `_synthesize_sector()`'s user-message construction (`pipeline/analyst.py` line ~174, the literal
   `"Extracted signals:"` label text immediately preceding unstructured extraction text with no enforced
   per-source delimiter). Write this up here as the CODE-REVIEW.md counterpart to
   ACCURACY-AUDIT.md's symptom-level finding (Tasks 003/004) — this file should explain *why* it happens
   in the code, the other file documents its *impact* on report trustworthiness. Do not propose a fix
   task for this (CONTEXT.md's rule: needs prompt-engineering judgment, not mechanical) — just flag it
   clearly, e.g. as a candidate for a future `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT` rework
   that enforces a stricter machine-parseable per-source format.

Write your findings to `.context/features/006-vn-my-accuracy-review/CODE-REVIEW.md` using this structure:

```markdown
# Code-Correctness Review: VN/MY + Domain-Activation Wiring

Findings table format, severity-ranked, per CLAUDE.md's `REVIEW.md` convention. Covers
`feature/003-vietnam-country`, `feature/004-malaysia-country`, and `feature/005-domain-activation`'s
current merged state (this section) and sampled git history (Task 006's section below).

## 1. Current-code data flow and gate consistency

| # | Area | File(s) | Finding | Severity | Optional fix task |
|---|------|---------|---------|----------|--------------------|
| ... |

[One row minimum per numbered area above (1-5), more if an area surfaces multiple distinct issues.
Severity: use High/Medium/Low/Informational. "Optional fix task" column: task number (007/008/009) or
"none — needs judgment, see writeup".]

## 2. Rapid-dispatch git history sample

[Left for Task 006 to fill in — do not write anything here.]
```

## Interfaces
- Consumes: `main.py`, `app.py`, `pipeline/analyst.py`, `pipeline/filter.py`, `pipeline/vectorstore.py`,
  `config/sources.json`, `RESEARCH.md`.
- Produces: `CODE-REVIEW.md` (created here with header + section 1) — Task 006 depends on this file
  existing and appends section 2.

## Constraints
- Read-only with respect to all pipeline/config/app code — this task produces a findings document, it
  never edits `app.py`, `pipeline/*.py`, `main.py`, or `config/sources.json`.
- Do not duplicate Tasks 007/008/009's fix content here — reference them by task number for findings that
  already have an optional fix task; write full detail only for findings that don't (items 3, 4, 5 above).
- Do not delete or restructure the `## 2. Rapid-dispatch git history sample` placeholder — Task 006
  depends on it being present so it can append cleanly.

## Verification
1. Confirm the file exists with both section headers:
   `py -c "content = open('.context/features/006-vn-my-accuracy-review/CODE-REVIEW.md', encoding='utf-8').read(); assert '## 1.' in content and '## 2.' in content; print('OK')"`
2. In your final report to the dispatching session, list all findings by number/area with their severity,
   so the dispatching session can sanity-check without re-opening the file.

## Evidence
[Filled in at completion]
