# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🟡 Presentation Prep Partial — Supervisor Demo Done, Feedback Pending Discussion

**Last updated:** 2026-06-24
**Last worked on:** Ran `.claude/execution/presentation-prep-handoff.md` to prep a clean-vs-feedback demo toggle for Alfonso's supervisor presentation. Cleared `data/feedback/` + `data/feedback/processed/` and wiped ChromaDB's `report_history`/`feedback_digests` collections (kept `company_context`). Got one successful real 70B Groq run into `data/latest_report.json` (real sources, real signals — no longer 8B test data) but it has two known quality issues (see below). A second run to produce the feedback-influenced version failed twice on Groq's daily token quota (100k TPD), which is now fully exhausted (~99,481/100,000 used) — real reset is at UTC midnight, not the short window Groq's error message implied. Added a `?demo=clean|feedback` query-param toggle to `app.py` (reads `data/presentation/{mode}_*.json`, falls back to `latest_report.json`) plus a small "Clean Run"/"With Feedback" badge in `report.html`/`internals.html`. **`data/presentation/` was never created**, so both `?demo=` values currently resolve to the same fallback file — the toggle exists in code but the feedback-version content does not yet exist. Alfonso confirmed the supervisor demo already happened using this in-progress state, and supervisor feedback has been received — next step is a discussion session to turn that feedback into a plan.

---

## What's Done
- [x] Full pipeline built and running end-to-end locally
- [x] Groq (Llama 3.3 70B) confirmed working on free tier (subject to 100k TPD limit)
- [x] `.claude/` directory configured: settings, custom commands, skills, execution guide
- [x] Context management system set up (CLAUDE.md, /context-update, /phase)
- [x] Full project scope defined: AI market intelligence system with RAG, feedback loop, web dashboard
- [x] All major architectural decisions locked (see CONTEXT.md)
- [x] **Phase 1:** Complete — sector-based pipeline, grounded analyst prompt, daily cadence
- [x] **Phase 2:** Complete — ChromaDB, RAG, dedup, entities, scoring, feedback loop, weekly summarizer
- [x] **Real Sources Finalization:** Complete — branding fix, 30 active real sources, feedback-loop demo verified
- [x] **Report Density Fix:** Multi-pass analyst architecture (per-sector extraction → synthesis), 8,000+ chars, 17/17 key signals present
- [x] **Phase 3:** Complete — analyst returns structured JSON, Flask dashboard (report + internals + feedback routes), both templates built and verified, full pipeline run confirmed end-to-end
- [x] **Phase 3.5:** Complete — dark glass hero revamp on report page, sticky scroll nav, restructured opportunities (top 3 by score expanded, rest collapsible), Space Grotesk + AOS + glass stat cards + glow orbs, internals page light restyle with matching animation vocabulary
- [x] **Presentation Prep (partial):** Real 70B clean report generated and live at `/`; `?demo=` toggle scaffolding added to `app.py` + templates; supervisor demo happened on this state

## What's In Progress
- Supervisor feedback has been received (raw, not yet structured) — next session is a discussion to turn it into a concrete plan, then a new `.claude/execution/` handoff for an execution agent.

## Known Bugs (found during presentation prep, unresolved)
- **`opportunities` array is empty** in the current `data/latest_report.json` — the strict relevance gate in `SYNTHESIS_PROMPT` (analyst.py) let zero signals through on this run. Empty is a documented "correct" output per the prompt's own rule ("Zero opportunities is a correct output when nothing passes the gate"), but it's a bad look for a BD-facing demo — the Opportunities section rendered with a "No opportunities passed the relevance gate this cycle" placeholder instead of real opportunity cards.
- **Sector mis-categorization**: `G Element` and `DataMesh` are configured under the `competitors` sector in `config/sources.py`, but in the synthesis output their signals appear duplicated into both "Partners" and "Competitors" buckets in `signals_by_sector`. Likely cause: the LLM is bucketing by semantic content ("G Element partners with X" reads like a Partners-shaped sentence) rather than by each source's actual configured sector. Facts themselves are accurate — this is a categorization/grounding issue in the synthesis prompt, not a hallucination.
- **`?demo=feedback` currently shows identical content to `?demo=clean`** — `data/presentation/clean_report.json` and `feedback_report.json` were never created (Groq quota ran out before the second run could complete), so both query values fall back to the same `data/latest_report.json`.

## What's Next (Ordered)
1. Discuss supervisor feedback with Alfonso, turn it into a plan, write a new `.claude/execution/` handoff doc for the next phase.
2. Decide whether to fix the empty-opportunities / sector-mixing issues as part of that next phase (likely a `SYNTHESIS_PROMPT` change in `analyst.py`).
3. Once Groq's daily quota resets (UTC midnight), generate the actual feedback-influenced report into `data/presentation/feedback_report.json` + `feedback_metadata.json` if the demo toggle is still wanted going forward.
4. Delete `scripts/feedback_server.py` (superseded by `/feedback` route in `app.py`) — deferred, not yet confirmed with Alfonso
5. Fix Construction Plus Asia SSL certificate verification error (minor, anytime)
6. Re-evaluate inactive sources (SGTech, CPG Consultant, FacilityBot) if/when their URLs are fixed
7. Phase 4: weekly summary + Google Drive push + MY/VN/ID source expansion

---

## Current Blockers
- **Groq free-tier daily token limit (100k TPD) is fully exhausted** (~99,481/100,000 used as of 2026-06-24 ~09:30 SGT). Real reset is UTC midnight (~22+ hours from exhaustion), not the short window Groq's 429 error message implies. **No more pipeline runs until quota resets** — confirmed with Alfonso to hold off intentionally.

## Recent Decisions
- Phase 3.5 visual revamp executed exactly per locked spec: dark gradient hero (navy-deep → navy → #102a45), glassmorphism stat cards, Space Grotesk display font, AOS scroll animations, sticky scroll-spy nav, opportunities sorted by score with top 3 expanded and rest collapsible.
- New CDN dependencies added: Google Fonts (Space Grotesk + Inter), AOS 2.3.1. No new Python packages.
- Internals page kept light (no dark hero) — matching shadow/hover/animation vocabulary only.
- `app.py` `?demo=clean|feedback` toggle added per `.claude/execution/presentation-prep-handoff.md`; kept in place (not reverted) per Alfonso's confirmation that the supervisor demo used this in-progress state.

## Notes for Next Session
- `data/latest_report.json` now holds a real 70B-quality run (not 8B test data) — but see Known Bugs above before treating it as fully clean.
- `.claude/execution/presentation-prep-handoff.md` is now historical/superseded — the demo it was written for already happened.
- Do not run `main.py` again until Groq's daily quota resets — confirmed with Alfonso.
- The collapsible opportunities feature (chevron expand/collapse for items 4+) still hasn't been visually exercised with >3 real opportunities — current real run has 0.
