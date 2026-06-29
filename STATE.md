# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🔴 Information Density Crisis — Report Output Too Sparse

**Last updated:** 2026-06-29
**Last worked on:** Dashboard information density overhaul — expanded signal schema, added competition risks section, data sources table, restructured template layout. Full pipeline run completed but output quality is worse (7 signals, down from 11).

---

## What's Done
- [x] Full pipeline built and running end-to-end locally
- [x] `.claude/` directory configured: settings, custom commands, skills, execution guide
- [x] Context management system set up (CLAUDE.md, /context-update, /phase)
- [x] Full project scope defined: AI market intelligence system with RAG, feedback loop, web dashboard
- [x] All major architectural decisions locked (see CONTEXT.md)
- [x] **Phase 1:** Complete — sector-based pipeline, grounded analyst prompt, daily cadence
- [x] **Phase 2:** Complete — ChromaDB, RAG, feedback loop, weekly summarizer
- [x] **Real Sources Finalization:** Complete — branding fix, 30 active real sources, feedback-loop demo verified
- [x] **Report Density Fix:** Multi-pass analyst architecture (per-sector extraction → synthesis)
- [x] **Phase 3:** Complete — analyst returns structured JSON, Flask dashboard
- [x] **Phase 3.5:** Complete — dark glass hero revamp, sticky scroll nav, Space Grotesk + AOS
- [x] **Presentation Prep (partial):** Real report generated; `?demo=` toggle scaffolding added
- [x] **Phase 4 — All 8 steps:** Complete and independently audited
- [x] **Pipeline Optimization Pass — all 7 steps executed and verified**
- [x] **Stage-by-stage verification — scraper, filter, analyst all tested individually**
- [x] **Dashboard overhaul (template):** Signal cards with source attribution + implication callouts, competition risks section, data sources dropdown, updated stat cards, scroll nav

## What's In Progress
- **Information density diagnosis:** The core problem remains unsolved — the pipeline produces too few signals (7) with too-shallow descriptions. Alfonso wants quantity AND depth comparable to the reference site (oss.silversea-media.net). This is the #1 priority.

## Changes Made This Session (2026-06-29, density overhaul session)
- **Email crash fix:** `main.py` — wrapped `send_digest()` in try/except so email failure doesn't kill the run
- **Data sources capture:** `main.py` — filtered source list (name, url, sector) saved into `report_data["data_sources"]`
- **Signal schema expanded:** `analyst.py` SYNTHESIS_PROMPT — signals now `{entity, signal, source_name, implication}` (was `{entity, signal}`)
- **Competition risks post-processor:** `analyst.py` — `_derive_competition_risks()` classifies competitor signals by threat level (HIGH/MEDIUM/LOW) with mitigation text, runs in Python after LLM call
- **Template restructure:** `report.html` — signals now render as individual full cards per finding (not bullet lists), with "For Silversea Media" callout; competition risks section with threat badges; collapsible data sources table; updated stat cards and scroll nav
- **Signal count regression:** Expanding the schema from 2→4 fields caused the 17B model to produce fewer signals (11→7). The richer-per-signal approach backfired on total quantity.

## Known Bugs
- **Synthesis signal loss (~80%+ now):** 17B `llama-4-scout` drops most extracted signals during synthesis. Was ~60-70% with old 2-field schema, now worse with 4-field schema.
- **Opportunity scoring out of range:** Model outputs scores >5 per dimension and totals >25.
- **Signal descriptions still too shallow:** Even the expanded schema produces generic 1-sentence summaries, not the detailed multi-paragraph findings Alfonso wants.
- **`?demo=feedback` shows identical content to `?demo=clean`** — not in scope.

## What's Next (Ordered)
1. **Diagnose information loss** — test each pipeline stage individually (scraper→filter→extraction→synthesis) to find exactly where information is being lost and how much
2. **Fix information density** — likely requires architectural change to synthesis (per-sector JSON calls instead of one big call, or skip synthesis for signals entirely)
3. **Template layout fix** — change signals from stacked full-width rectangles to a grid of boxes (like reference site's 3-column Discovery cards)
4. **Switch synthesis to Claude Haiku** — will dramatically improve both signal count and description quality
5. Remaining deferred items (demo toggle cleanup, ROADMAP phase naming)

---

## Current Blockers
- **Information density is unacceptable.** Alfonso explicitly rejected the current output as too sparse. The 17B model cannot handle the expanded schema without losing signals. Architectural changes to the synthesis pipeline are required before any further feature work.

## Notes for Next Session
- The extraction step (per-sector LLM calls) likely produces rich output — need to inspect raw extraction text to confirm. If extraction is rich, the bottleneck is the single synthesis call compressing everything.
- Consider: per-sector synthesis calls (one JSON call per sector) instead of one monolithic synthesis call. This would give each sector dedicated attention and avoid the "compress everything" problem.
- Alternative: skip the synthesis LLM call for signals entirely — parse the extraction output directly into structured JSON in Python, and only use the synthesis call for executive_summary, opportunities, and synthesis bullets.
- `_build_rag_context()` is still dead code in `analyst.py` — restore when Claude Haiku is in place.
- Reference site for comparison: https://oss.silversea-media.net/project/meta3d/other/2026-04-30-report.html
