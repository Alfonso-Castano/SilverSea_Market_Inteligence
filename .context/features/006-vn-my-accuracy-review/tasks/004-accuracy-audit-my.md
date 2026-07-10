# Task 004: Accuracy audit — Malaysia GENERAL report (appends to ACCURACY-AUDIT.md)

**Status:** pending
**Depends on:** Task 002 (`002-refetch-my-sources.md`) — needs `refetched/my_sources.json` to exist.
Task 003 (`003-accuracy-audit-vn.md`) — must run strictly after Task 003 lands, since both write to the
same `ACCURACY-AUDIT.md` file (Task 003 creates it with a `## Malaysia` placeholder section this task
fills in; running concurrently would race on the same file).
**Model tier:** quality — same rationale as Task 003: this is core audit-content judgment work, not
mechanical, and CONTEXT.md's Global Constraints call for a higher-capability tier here specifically.

## Files
- Modify: `.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md` (append/fill in the
  `## Malaysia` section Task 003 left as a placeholder — do not touch the `## Vietnam` section above it)

## What to do

Audit `data/latest_report_MY_GENERAL.json` for factual accuracy against real source material, using the
same method Task 003 used for Vietnam. Your three sources of ground truth, in priority order:

1. **`.context/features/006-vn-my-accuracy-review/refetched/my_sources.json`** (from Task 002) — live
   content re-fetched today from the 25 sources the report's `data_sources` array cites.
2. **`docs/Source_submission_Malaysia_Sources.pdf`** — the original MY source-list document (use the
   `Read` tool's `pages` parameter, up to 20 pages per call; check total page count first with a small
   read before deciding how many calls you need).
3. **`config/sources.json`**'s MY block — for cross-checking source names/URLs/sectors/domains against
   what's actually configured (do not modify this file — read-only).

Read `.context/features/006-vn-my-accuracy-review/RESEARCH.md` §2 first for context: the MY report's
`source_name` field is **mostly correct** (unlike VN's near-total breakage), but 4 of its 9 signals still
carry non-matching values: `"Extracted signals"` (same defect as VN), `"Balai Seni Negara"` (the Malay
name for "National Art Gallery" — a real entity, but not the exact configured `source_name`, so it's
still a lookup miss against `data_sources`), `"source not specified"`, and `"source text"`. For these 4,
fall back to matching by `entity` name against `data_sources`, same as Task 003 did for VN. All 3 MY
opportunities already have real, matching `source_name`s — no fallback needed for those.

For every signal in `signals_by_sector` (9 total) and every opportunity (3 total):
1. Identify which real source it should be checked against (`source_name` match first, entity-name
   fallback for the 4 broken ones).
2. Compare the claim against that source's re-fetched live content (`my_sources.json`) and, where useful,
   the PDF's original one-line description of that source.
3. Classify as one of: **Grounded**, **Unverifiable**, or **Contradicted/Suspect** — same definitions as
   Task 003 (re-read its "What to do" section 3 if you weren't given it — the classification criteria are
   identical, only the report differs). Be conservative on Contradicted/Suspect; a live homepage not
   mentioning a claim isn't itself proof of hallucination.
4. Pay particular attention to specific, checkable claims: the two National Art Gallery tender claims
   (exact Malay procurement titles — check these are plausible, not garbled/invented), the TA Global
   CloutHaus Residences opportunity, and the GreenRE and Malaysia Airport Holding Berhad opportunities.

Also check the 3 opportunities' `product_fit` reasoning against Silversea's actual product catalog
(`data/company_context.md`'s Products by Business Sector section, or `pipeline/analyst.py`'s
`SUMMARY_PROMPT` catalog block) — flag if a `product_fit` claims a solution that doesn't plausibly match
the opportunity's actual subject matter. Since this report is domain `GENERAL` (not `BER`), also sanity
-check whether any signal/opportunity is actually specific to a non-BER sub-domain (e.g. healthcare,
retail, tourism — MY's active domains per RESEARCH.md §3 include HLS, RCC, CTE) and whether `product_fit`
reasoning reflects that correctly, given lead 3's confirmed finding that `analyse()` never receives an
explicit domain parameter.

Open `.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md`, find the `## Malaysia` section
(currently just a placeholder comment left by Task 003), and replace it with your findings using the same
structure Task 003 used for Vietnam:

```markdown
## Malaysia (`latest_report_MY_GENERAL.json`)

**Coverage:** 9 signals across 5 sectors, 3 opportunities, checked against 25 re-fetched sources +
`docs/Source_submission_Malaysia_Sources.pdf`.

**Summary:** [N Grounded / N Unverifiable / N Contradicted-Suspect out of 9 signals; same breakdown for
the 3 opportunities]

| # | Type | Entity | Claim (short) | Classification | Evidence / Reasoning |
|---|------|--------|----------------|-----------------|----------------------|
| ... |
```

Do not modify anything above the `## Malaysia` heading (Task 003's Vietnam section and the shared file
header).

## Interfaces
- Consumes: `refetched/my_sources.json` (Task 002), `data/latest_report_MY_GENERAL.json`,
  `docs/Source_submission_Malaysia_Sources.pdf`, `config/sources.json`, and the `ACCURACY-AUDIT.md` file
  structure Task 003 already created.
- Produces: the completed `ACCURACY-AUDIT.md` (both country sections filled in) — this is the feature's
  final accuracy-review deliverable, nothing downstream depends on this task within the plan.

## Constraints
- Read-only with respect to all pipeline/config/data files — this task only edits
  `ACCURACY-AUDIT.md`.
- No `py main.py` run, no Groq/LLM API calls of any kind.
- Do not touch the `## Vietnam` section or the file's shared header — only fill in `## Malaysia`.

## Verification
1. Confirm the file now has real content (not a placeholder) under `## Malaysia`:
   `py -c "content = open('.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md', encoding='utf-8').read(); my_section = content.split('## Malaysia')[1]; assert len(my_section.strip()) > 200; print('OK', len(my_section))"`
2. In your final report to the dispatching session, state the exact Grounded/Unverifiable/
   Contradicted-Suspect counts for MY signals and opportunities, and list every Contradicted/Suspect
   finding by name.

## Evidence
[Filled in at completion]
