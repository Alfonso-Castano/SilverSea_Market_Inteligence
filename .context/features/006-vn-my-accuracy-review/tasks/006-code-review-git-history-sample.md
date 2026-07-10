# Task 006: Code-correctness review — rapid-dispatch git history sample (appends to CODE-REVIEW.md)

**Status:** pending
**Depends on:** Task 005 (`005-code-review-data-flow-and-gates.md`) — must run strictly after Task 005
lands, since both write to the same `CODE-REVIEW.md` file (Task 005 creates it with a `## 2.` placeholder
section this task fills in; running concurrently would race on the same file).
**Model tier:** quality — same rationale as Task 005: reviewing rapidly cheap/mid-tier-dispatched commits
for quality issues is exactly the kind of judgment CONTEXT.md's Global Constraints call for a
higher-capability tier on.

## Files
- Modify: `.context/features/006-vn-my-accuracy-review/CODE-REVIEW.md` (fill in the `## 2. Rapid-dispatch
  git history sample` section Task 005 left as a placeholder — do not touch section 1 above it)

## What to do

CONTEXT.md explicitly requires sampling `git log`/`git show` across `feature/003-vietnam-country`,
`feature/004-malaysia-country`, and `feature/005-domain-activation` — not just the current merged code
state (which Task 005 already reviewed) — because this session's development happened via many rapid
cheap/mid-tier executor subagent dispatches, and Alfonso wants the actual work product sampled.

`.context/features/006-vn-my-accuracy-review/RESEARCH.md` §6 already has the full ordered commit list
(27 commits) and has already inspected 3 of them in detail (`b10537d`, `aea7783`, `bb6fbd3` — findings
folded into RESEARCH.md §3-4 and Task 005's section 1; don't re-review these from scratch, just cite
them here with a one-line pointer back to where the finding already lives).

Review the **remaining ~24 commits** from RESEARCH.md §6's list. For each, run `git show <hash>` (or
`git show <hash> --stat` first if the diff looks large) and look specifically for:

- **Correctness bugs introduced silently** — a rapid-dispatch commit that looks mechanical
  (e.g. "tier VN source fetchers") but actually changed something else too, or got a detail wrong (e.g.
  wrong sector/domain value, a copy-paste error from the SG/VN pattern applied incorrectly to MY, an
  off-by-one in a country-scoping filter).
- **Inconsistent application of a pattern across near-identical commits** — e.g. compare
  `519c772` (VN fetcher tiering) against `4012532` (MY fetcher tiering), or `975086a` (VN sources.json
  block) against `89ce900` (MY sources.json block) — same task type, done by (likely) different
  dispatches; check they applied the same conventions (field names, `inactive_reason` phrasing style,
  `fetcher` tier decisions) and flag any drift.
- **Scope creep or scope gaps** — a commit whose message claims one thing but whose diff does more or
  less than that (e.g. does `8771013` "make report/internals/admin routes country-aware" actually cover
  all three routes, or does it miss one that a later commit had to patch?).
- **Anything that corroborates or contradicts an ACCURACY-AUDIT.md or CODE-REVIEW.md section 1 finding**
  — e.g. if you find the commit that introduced the `SECTOR_SYNTHESIS_PROMPT`/`_synthesize_sector()`
  code path used by the `source_name` breakage (RESEARCH.md §2), note whether it predates this session's
  three features entirely (likely, since RESEARCH.md's own reading of `analyst.py` suggests this is
  older code, not new to VN/MY) — this matters because it changes whether the bug is "newly introduced by
  rapid dispatch" (a rapid-dispatch quality problem) vs. "a pre-existing latent bug VN/MY's real content
  happened to newly expose" (a scope/testing-coverage problem, arguably worse since 3 `/feature-verify`
  PASSes over 3 features never caught it). Check `git log -p --follow pipeline/analyst.py` or
  `git blame` around the relevant lines if useful, but don't spend excessive time here — a clear
  one-paragraph conclusion either way is enough.

You do not need one row per commit — group commits that raise no issues (most of them, likely) into a
single "reviewed, no issues found" summary line per feature branch, and give full detail rows only to
commits where you found something worth flagging.

Open `.context/features/006-vn-my-accuracy-review/CODE-REVIEW.md`, find the `## 2. Rapid-dispatch git
history sample` section (currently a placeholder left by Task 005), and replace it with your findings:

```markdown
## 2. Rapid-dispatch git history sample

Sampled all 27 commits across `feature/003-vietnam-country`, `feature/004-malaysia-country`, and
`feature/005-domain-activation` (full list: `RESEARCH.md` §6). 3 already reviewed during planning
research (`b10537d`, `aea7783`, `bb6fbd3` — see RESEARCH.md §3-4 and section 1 above); this section
covers the remaining 24.

**feature/003-vietnam-country:** [one-line summary of commits reviewed, "no issues" or pointer to a
finding row below]

**feature/004-malaysia-country:** [same]

**feature/005-domain-activation:** [same]

| # | Commit | Finding | Severity |
|---|--------|---------|----------|
| ... |

**`source_name` breakage provenance:** [your one-paragraph conclusion on whether the
`_synthesize_sector()` bug (RESEARCH.md §2) predates this session's 3 features or was introduced/newly
exposed by them]
```

Do not modify section 1 (Task 005's content) above the `## 2.` heading.

## Interfaces
- Consumes: `RESEARCH.md` §6 (commit list), `git log`/`git show` history, the `CODE-REVIEW.md` file
  structure Task 005 already created.
- Produces: the completed `CODE-REVIEW.md` (both sections filled in) — this is the feature's final
  code-correctness deliverable, nothing downstream depends on this task within the plan.

## Constraints
- Read-only with respect to git history and all code files — `git show`/`git log` only, no `git checkout`
  of another branch's state, no edits to any `.py`/`.json`/`.html` file. Only edit `CODE-REVIEW.md`.
- No `py main.py` run, no Groq/LLM API calls of any kind.
- Do not touch section 1 or the file's shared header — only fill in section 2.

## Verification
1. Confirm the file now has real content (not a placeholder) under section 2:
   `py -c "content = open('.context/features/006-vn-my-accuracy-review/CODE-REVIEW.md', encoding='utf-8').read(); s2 = content.split('## 2.')[1]; assert len(s2.strip()) > 200; print('OK', len(s2))"`
2. In your final report to the dispatching session, state how many of the 24 newly-reviewed commits
   raised a finding, list them with severity, and state your `source_name`-breakage-provenance conclusion
   explicitly (not just "see the file").

## Evidence
[Filled in at completion]
