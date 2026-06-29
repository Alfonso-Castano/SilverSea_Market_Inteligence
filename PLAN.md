# PLAN.md — Current Phase Plan

*Active plan for the phase currently in progress. Overwritten at the start of each new phase.*
*Task status updated by /context-update. Full phase history lives in ROADMAP.md.*

---

## Information Density Fix — Pipeline Diagnosis & Architectural Change

**Goal:** Dramatically increase the quantity and depth of signals in the report.
Currently producing 7 shallow signals from 33 filtered sources — unacceptable.
Target: 20+ detailed signals with multi-sentence descriptions, statistics, and specifics.

---

## Tasks

### 1. Dashboard template + schema changes `[x]`
Signal schema expanded to 4 fields, competition risks section added, data sources table added,
template restructured to card-per-finding layout. **But signal count regressed from 11→7.**

### 2. Diagnose information loss per pipeline stage `[ ]`
Test each stage individually: scraper output volume → filter pass-through → extraction output
→ synthesis output. Find exactly where information is being dropped and how much.

### 3. Fix synthesis architecture `[ ]`
The single monolithic synthesis call is the bottleneck. Likely solution: per-sector JSON
synthesis calls instead of one big call, or skip synthesis for signals entirely and parse
extraction output in Python.

### 4. Fix template layout `[ ]`
Change signal cards from full-width stacked rectangles to a 3-column grid of boxes
(matching reference site's Discovery card layout).

### 5. Verify end-to-end `[ ]`
Run full pipeline, confirm 20+ signals with rich descriptions render correctly.

---

## Dependencies

```
2 (diagnose) → 3 (fix architecture) → 5 (verify)
4 (layout fix) is independent, can run in parallel with 2-3
```
