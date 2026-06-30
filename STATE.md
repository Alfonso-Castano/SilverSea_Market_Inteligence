# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🟢 Prototype #3 Complete — Frontend Redesign Done

**Last updated:** 2026-06-30
**Last worked on:** Full frontend redesign of `templates/report.html`, `templates/base.html`, `static/style.css`, `static/animations.js`. Added: collapsible entity grouping, signal spotlight interaction, sector color coding (5 distinct colors), dark/light mode toggle with localStorage persistence, scroll progress bar, source links on signal cards, colored sector header bars with icons, section zone backgrounds, enhanced hover states, reduced motion support.

---

## What's Done
- [x] **Phase 1:** Complete — sector-based pipeline, grounded analyst prompt, daily cadence
- [x] **Phase 2:** Complete — ChromaDB, RAG, feedback loop, weekly summarizer
- [x] **Phase 3:** Complete — structured JSON output, Flask dashboard, two-page split
- [x] **Phase 3.5:** Complete — dark glass hero revamp, sticky scroll nav, Space Grotesk + AOS
- [x] **Real Sources Finalization:** 30 active real sources, branding fix, feedback-loop demo
- [x] **Phase 4 (Efficiency & Coverage):** All 8 steps — keyword filter, source expansion (57 total), company context, metrics glossary, feedback digest consolidation, model research, SYNTHESIS_PROMPT bug fixes
- [x] **Pipeline Optimization:** Scrapling integration, dead code removal (dedup/entities/scoring), filter keyword rebalancing, IMDA URL fix, stage-by-stage verification
- [x] **Information Density Fix:** Per-sector synthesis architecture (6 extraction + 6 sector synthesis + 1 summary = 13 LLM calls). Signal count: 7 → 65.
- [x] **Prototype #2 committed:** `ebd90f6`
- [x] **Frontend Redesign (Prototype #3):** Collapsible entity groups, signal spotlight, sector colors, dark mode, scroll progress, source links, sector headers with icons, enhanced hovers

## What's In Progress
- Nothing active — ready for supervisor demo

## What's Next (Ordered)
1. **Set up README + repo for local testing** — supervisor needs to run `py app.py` locally to review the dashboard
2. **Apply supervisor feedback** — content filtering, design changes based on demo feedback
3. **Switch synthesis to Claude Haiku** — will improve signal quality, description depth, and opportunity scoring
4. **Restore RAG context** — `_build_rag_context()` is dead code; restore once Claude Haiku's 200k context removes the token constraint
5. **Deploy to company servers** — still running locally
6. Remaining deferred items (demo toggle cleanup, ROADMAP phase naming collision)

---

## Current Blockers
- None — ready for supervisor review

## Known Bugs
- **Opportunity scoring out of range:** Model sometimes outputs scores >5 per dimension
- **Customers sector empty:** Only 1 source passed filter, produced 0 signals this run
- **`?demo=feedback` toggle non-functional** — `data/presentation/` directory doesn't exist

## Notes for Next Session
- Need to write a README with setup instructions so supervisor can `git clone` + `pip install` + `py app.py` to test locally.
- The per-sector synthesis architecture is the right approach but signal quality still depends on the 17B model — Claude Haiku upgrade is the next major quality lever.
- `_build_rag_context()` remains dead code in `analyst.py` — restore when switching to Claude Haiku.
