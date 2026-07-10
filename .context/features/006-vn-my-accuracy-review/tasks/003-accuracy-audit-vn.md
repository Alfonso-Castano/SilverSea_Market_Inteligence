# Task 003: Accuracy audit — Vietnam BER report (creates ACCURACY-AUDIT.md)

**Status:** done
**Depends on:** Task 001 (`001-refetch-vn-sources.md`) — needs `refetched/vn_sources.json` to exist.
**Model tier:** mid — pin to Sonnet 5 (`sonnet`). Per Alfonso's 2026-07-10 directive (CONTEXT.md Global
Constraints), the knowledge/accuracy-audit half of this feature is explicitly assigned Sonnet 5, not
Opus — the top tier is reserved for the code-correctness review (Tasks 005/006) instead. This supersedes
this task's earlier `quality` assignment from the initial planning pass; the underlying judgment-heavy
nature of the task (assessing whether LLM-generated content is grounded or hallucinated) is unchanged,
only the tier pinning is.

## Files
- Create: `.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md` (this task creates the file
  with a shared header + the VN section; Task 004 appends a MY section afterward — do not let Task 004
  run concurrently with this one, they write the same file)

## What to do

Audit `data/latest_report_VN_BER.json` for factual accuracy against real source material. You have three
sources of ground truth, in priority order:

1. **`.context/features/006-vn-my-accuracy-review/refetched/vn_sources.json`** (from Task 001) — live
   content re-fetched today from the 15 sources the report's `data_sources` array cites.
2. **`docs/Silversea_Vietnam_Market_07072026.pdf`** — the original VN source-list document (use the
   `Read` tool's `pages` parameter, up to 20 pages per call; check total page count first with a small
   read before deciding how many calls you need).
3. **`config/sources.json`**'s VN block — for cross-checking source names/URLs/sectors/domains against
   what's actually configured (do not modify this file — read-only).

**Read `.context/features/006-vn-my-accuracy-review/RESEARCH.md` §2 first** — it documents a confirmed,
already-diagnosed defect that changes how you must approach this audit: **43 of the VN report's 43
signals and all 3 opportunities carry a broken `source_name`** (`"Extracted signals"` /
`"extracted signals"`, a literal label string that leaked into the LLM's output — not a real source name
— except one signal correctly attributed to "Vietnam Investment Review"). Do not treat every one of these
as "no source, therefore hallucinated" — instead, **match by `entity` name against `data_sources`** where
possible (e.g. a signal with `entity: "Becamex IDC"` should be checked against the `data_sources` entry
named "Becamex IDC" / its re-fetched content in `vn_sources.json`). Where a signal's `entity` doesn't
correspond to any of the 15 `data_sources` (e.g. it names a third party the tracked source merely
mentions), note that you cannot verify it against a re-fetch and check it against the PDF source
descriptions instead, or mark it "unverifiable — third-party entity, no direct source."

For every signal in `signals_by_sector` (43 total) and every opportunity (3 total):
1. Identify which real source it should be checked against (entity-name match to `data_sources`, per
   above).
2. Compare the claim against that source's re-fetched live content (`vn_sources.json`) and, where useful,
   the PDF's original one-line description of that source.
3. Classify as one of: **Grounded** (claim plausibly matches what the source discusses — note live
   content may have moved on since the original scrape, so absence of an exact match on a homepage is
   not itself proof of hallucination — see RESEARCH.md §5's caveat), **Unverifiable** (source broken/
   unreachable on re-fetch, or entity has no traceable source at all), or **Contradicted/Suspect**
   (the claim states something specific — a partnership, a figure, a named programme — that the source's
   actual content, PDF description, or general knowledge of the entity makes implausible or is nowhere
   supported; be conservative here, this is the category that matters most).
4. Pay particular attention to specific, checkable claims: named partnerships (e.g. the Becamex IDC /
   World Bank / Sembcorp / NUS claims in the sample signal), tender/deadline claims, and any numeric
   figures — these are the highest-stakes claims for a BD-facing report and the ones grounding failures
   are most damaging on.

Also check the 3 opportunities' `product_fit` reasoning against Silversea's actual product catalog
(`data/company_context.md`'s Products by Business Sector section, or `pipeline/analyst.py`'s
`SUMMARY_PROMPT` catalog block) — flag if a `product_fit` claims a solution that doesn't plausibly match
the opportunity's actual subject matter.

Write your findings to `.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md` using this
structure (create the file — Task 004 will append a Malaysia section below yours, so leave your VN
section clearly closed off):

```markdown
# Accuracy Audit: VN/MY Report Content vs. Real Sources

Findings table format, severity-ranked, per CLAUDE.md's `REVIEW.md` convention (structured findings, not
prose narrative). No `py main.py` run, no LLM calls were used to produce this audit — all comparisons are
against live re-fetched source pages and the original source-list PDFs.

## Vietnam (`latest_report_VN_BER.json`)

**Coverage:** 43 signals across 4 sectors, 3 opportunities, checked against 15 re-fetched sources +
`docs/Silversea_Vietnam_Market_07072026.pdf`.

**Summary:** [N Grounded / N Unverifiable / N Contradicted-Suspect out of 43 signals; same breakdown for
the 3 opportunities]

| # | Type | Entity | Claim (short) | Classification | Evidence / Reasoning |
|---|------|--------|----------------|-----------------|----------------------|
| ... |

[Include every Contradicted/Suspect finding as its own table row, no matter how minor. Grounded and
Unverifiable findings can be summarized/grouped rather than one row each if there are many similar
ones — but the `source_name` breakage itself (RESEARCH.md §2) must be called out explicitly here as
context for why so many rows are "Unverifiable via source_name, verified via entity-name fallback
instead."]

## Malaysia (`latest_report_MY_GENERAL.json`)

[Left for Task 004 to fill in — do not write anything here.]
```

## Interfaces
- Consumes: `refetched/vn_sources.json` (Task 001), `data/latest_report_VN_BER.json`,
  `docs/Silversea_Vietnam_Market_07072026.pdf`, `config/sources.json`.
- Produces: `ACCURACY-AUDIT.md` (created here with header + VN section) — Task 004 depends on this file
  existing and appends to it.

## Constraints
- Read-only with respect to all pipeline/config/data files — this task produces a findings document, it
  never edits report JSON, `config/sources.json`, or any pipeline code.
- No `py main.py` run, no Groq/LLM API calls of any kind (re-fetching source *pages* via
  `pipeline/scraper.py` is not an LLM call and is fine — that already happened in Task 001; this task
  only reads its output).
- Do not delete or restructure the `## Malaysia` placeholder section — Task 004 depends on it being
  present so it can append cleanly.

## Verification
1. `py -c "import json; ... "` is not applicable here (this task produces markdown, not code) — instead:
   confirm the file exists and both `## Vietnam` and `## Malaysia` headers are present:
   `py -c "content = open('.context/features/006-vn-my-accuracy-review/ACCURACY-AUDIT.md', encoding='utf-8').read(); assert '## Vietnam' in content and '## Malaysia' in content; print('OK')"`
2. In your final report to the dispatching session, state the exact Grounded/Unverifiable/
   Contradicted-Suspect counts for VN signals and opportunities, and list every Contradicted/Suspect
   finding by name (not just "see the file") so the dispatching session can sanity-check severity without
   re-opening the file.

## Evidence
DONE (sonnet executor). Created `ACCURACY-AUDIT.md` header + `## Vietnam` section + intact `## Malaysia` placeholder; verification `assert '## Vietnam' and '## Malaysia'` → OK. Read-only, no LLM/Groq calls. Counts: **38 Grounded / 0 Unverifiable / 5 Contradicted-Suspect** of 43 signals; **1 Grounded / 0 Unverifiable / 2 Contradicted-Suspect** of 3 opportunities. All 43 signals' `entity` matched a `data_sources` entry, so the source_name-breakage entity-fallback fully substituted (no third-party unverifiables). Contradicted/Suspect findings:
1. **Becamex IDC signal — HIGH:** "data storage centers and virtual servers" is a near-verbatim lift from **Viettel's** homepage, not Becamex — cross-source contamination (260 MWp solar figure itself is grounded).
2. **Opp 3 BM Windows — HIGH:** product_fit "Smart Building, Building Automation" — not real Silversea product names; fabrication repeated in concrete_action.
3. **Opp 2 Vietsoftpro — MEDIUM:** product_fit "E-learning solutions" not a named Silversea product.
4. **Ninh Thuan 2 nuclear (General News) — MEDIUM:** report says VN/S.Korea "are collaborating"; source says VN "will select the official partner... Q3 2026" (prospective, not active).
5. **NVIDIA DiffusionGemma — LOW:** report says NVIDIA "released" it; it's Google DeepMind's model NVIDIA merely accelerates.
6. **Becamex "VSIC" — LOW:** report expands as "Vietnam-Singapore Industrial Corporation"; source says "Innovation Centre".
7. **TTDecor implication — LOW:** Python post-processing collided "BIM Corporation" (a developer) with Building Information Modeling — pipeline artifact, not LLM. (5 of 15 sources produced zero signals — noted as unused capacity, not a finding.)
