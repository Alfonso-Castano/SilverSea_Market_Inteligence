# Phase 3 Dashboard — Handoff Prompt

Copy-paste this into a fresh Opus session to start execution.

---

## Prompt

You are executing Phase 3 (Web Dashboard) of Silversea Media's AI market intelligence system
at `C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence`.

### Context files — read these first, in order:
1. `CLAUDE.md` — project instructions + auto-imports STATE.md, CONTEXT.md, ROADMAP.md, PLAN.md
2. `.claude/execution/phase3-dashboard.md` — **the complete execution plan** with 6 sessions of
   detailed implementation instructions, exact code snippets, file paths, and verify steps

### What you're building
Two dashboard surfaces from one Flask app:
- **Surface 1 (`/`)** — Polished market intelligence report for BD/sales team + CEO. Score badges,
  sector cards, visual hierarchy. Must look professional.
- **Surface 2 (`/internals`)** — AI system observability page for the developer/maintainer. Source
  quality scores chart, vector store browser, feedback digest timeline, run metadata.

### Current state
- Phase 1 (scraping pipeline) and Phase 2 (AI Brain: ChromaDB, RAG, feedback loop) are complete
- `pipeline/analyst.py` currently returns freeform text — Session 1 switches it to structured JSON
- `pipeline/report.py` currently generates static HTML — Session 2 strips it to a JSON writer
- `scripts/feedback_server.py` is a standalone Flask app on port 5050 — Session 3 consolidates it
  into the main `app.py`
- No code has been written for Phase 3 yet — you're starting from the execution plan

### Execution order
The plan has 6 sessions. Sessions 1→2→3 are sequential (pipeline code changes with tight
dependencies). Sessions 4 and 5 are parallel (independent template work). Session 6 is final
verification.

### Subagent strategy
You are an Opus model — you're expensive. **Use subagents to parallelize where possible.**
Sessions 4 (report template) and 5 (internals template) are ideal subagent candidates: each is
self-contained HTML/Jinja2/CSS/JS work with well-defined inputs (the JSON schema from Session 1,
the design spec from the execution file, and the `templates/base.html` you create in Session 3).

Recommended approach:
- Execute Sessions 1-3 yourself (core pipeline changes, tight interdependencies)
- Spawn two subagents in parallel for Sessions 4 and 5 (template building)
- Execute Session 6 yourself (end-to-end verification needs the full picture)

If you assess that the scope is NOT big enough to justify subagents (e.g., the templates are
simple enough to do inline), STOP and tell me before proceeding — I'll switch to a cheaper model
for sequential execution. But given the detail in the execution plan (report page has score badges
with sub-score bars, sector card grids, feedback form restyling; internals page has Chart.js
integration, tabbed vector store browser), subagents should be justified.

### Key constraints
- Token efficiency matters — read specific files, don't dump full contents
- Must be free — no paid services, no premium templates
- Flask is already a dependency — don't introduce unnecessary complexity
- The execution plan at `.claude/execution/phase3-dashboard.md` has exact code snippets and
  file paths for each session — follow it, don't re-derive
