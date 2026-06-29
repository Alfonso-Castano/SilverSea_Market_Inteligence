# Handoff: Split-Model Fix + Holistic Pipeline Review

## Context

You are working at `C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence` — an AI market
intelligence pipeline for Silversea Media. Read CLAUDE.md first (it auto-imports STATE.md,
CONTEXT.md, ROADMAP.md, and PLAN.md). Then read PLAN.md carefully — it describes this exact
task as the active phase.

## The Situation

A functional verification session just completed. The pipeline's multi-pass analyst
(`pipeline/analyst.py`) works in two phases:
- **Phase 1 (extraction):** One LLM call per sector, extracting named signals from raw scraped
  content. Currently uses `meta-llama/llama-4-scout-17b-16e-instruct` (17B params, 30k TPM).
- **Phase 2 (synthesis):** One LLM call that takes all extraction outputs and produces the
  final structured JSON report. Also currently uses `llama-4-scout`.

The problem: **Phase 1 extraction works great** — it produces ~13,000 characters of rich,
detailed signals across 6 sectors (Gov & Agencies: 4,226 chars, Partners: 3,480 chars,
Competitors: 2,621 chars with G Element's 5 partnerships, DataMesh's 3 product launches, etc.).
**Phase 2 synthesis throws away ~80% of it.** The `SYNTHESIS_PROMPT` explicitly says "every
extracted signal that names a specific company, partnership, product, event, or metric MUST
appear" but the 17B model ignores this and aggressively summarizes, producing only ~10 signals
in the final report.

There is **temporary debug logging** in `analyst.py`'s `analyse()` function that prints the raw
extraction output between Phase 1 and Phase 2. It was added to diagnose this problem. Remove it
once the fix is verified.

## What to Do — In This Order

### Step 1: Apply the split-model fix

In `pipeline/analyst.py`, make the synthesis call use `openai/gpt-oss-120b` (120B params, 8k
TPM on Groq free tier) while keeping `llama-4-scout` for extraction. The synthesis call's input
is only ~5,700 tokens (extraction summaries + SYNTHESIS_PROMPT + RAG context), well under the
8k TPM limit. The extraction calls must stay on `llama-4-scout` because individual sector
extraction requests can reach 9-10k tokens (raw scraped content), exceeding `gpt-oss-120b`'s
8k TPM.

Practically: add a second model constant (e.g. `SYNTHESIS_MODEL`) and use it in the
`client.chat.completions.create()` call at line ~269 where `SYNTHESIS_PROMPT` is used. Keep the
existing `MODEL` constant for `_extract_sector()`.

### Step 2: Run `py main.py --no-email` and verify

One run. Check:
1. All 6 sector extractions succeed (no TPM errors — `llama-4-scout` handles these).
2. The synthesis call succeeds (no TPM error — input should be ~5.7k tokens under 8k limit).
3. The final `data/latest_report.json` preserves the extracted signals — compare the debug
   extraction dump (printed to console) against what appears in `signals_by_sector`. The report
   should have significantly more signals than the ~10 from the 17B-only run. Specifically
   check that G Element's 5 partnerships, DataMesh's 3 product launches, AECOM's framework
   wins, and BCA's startup competition all appear.
4. `opportunities` array — check if any signals pass the widened relevance gate (G Element's
   digital twin partnerships, DataMesh's digital twin products should qualify).
5. No cross-sector signal duplication (sector categorization fix still holds).

### Step 3: Remove debug logging

Delete the temporary extraction dump block in `analyst.py`'s `analyse()` function (the
`for sector_name, report in sector_reports.items(): print(f"\n--- RAW EXTRACTION...")` block
between Phase 1 and Phase 2).

### Step 4: Holistic pipeline review

Alfonso wants a comprehensive review of the entire pipeline — not just the synthesis issue.
Look at everything with fresh eyes and identify any flaws, inefficiencies, or issues that
could affect report quality or reliability. This is an open-ended review, not a checklist.
Areas to consider (not exhaustive):
- Scraper reliability and content quality
- Filter effectiveness (is min_score=3 the right threshold? are the keyword lists complete?)
- Deduplication and entity extraction — are they doing useful work?
- RAG context injection — is it actually helping the analyst or just adding noise?
- Source quality scoring — is it being used downstream or just logged?
- The SYNTHESIS_PROMPT itself — now that a stronger model is running it, are there prompt
  issues that were masked by the weak model?
- Any other pipeline stages that might be lossy or broken

Report your findings to Alfonso — he wants to understand what's happening before more changes
pile up. Lean toward reporting issues rather than silently fixing them, unless a fix is trivial
and obviously safe.

## Constraints

- Don't change `templates/`, `static/`, or `app.py` — this is pipeline-only.
- One authorized `py main.py --no-email` run for verifying the split-model fix. Additional
  runs only if the first one reveals something that needs a code fix and re-test.
- Report findings, don't silently rewrite things. Alfonso wants visibility.

## Key Files

- `pipeline/analyst.py` — MODEL constant, SYNTHESIS_PROMPT, `_extract_sector()`, `analyse()`
- `pipeline/filter.py` — `score_relevance()`, `filter_results()`
- `pipeline/scraper.py` — `smart_truncate()`, `scrape_source()`
- `pipeline/feedback.py` — `aggregate_feedback()`, `consolidate_feedback_digests()`
- `pipeline/dedup.py` — semantic deduplication
- `pipeline/entities.py` — named entity extraction
- `pipeline/scoring.py` — source quality scoring
- `pipeline/vectorstore.py` — ChromaDB wrapper
- `config/sources.py` — source URLs, keyword lists, country config
- `main.py` — pipeline entrypoint, orchestration order
- `data/latest_report.json` — output from last run
- `data/model_research.md` — model comparison (stale — still recommends gpt-oss-120b as
  drop-in; actual situation requires split-model)
