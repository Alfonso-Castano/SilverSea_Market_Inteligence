# Visual Design Execution — Handoff Prompt

Copy-paste this into a fresh chat to start the execution session.

---

## Prompt

You are starting an **execution session** for Silversea Media's AI market intelligence system
at `C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence`.

**Model note:** This session is running on Opus. Opus is expensive — use subagents wherever
the plan below identifies independent, parallelizable work (it calls these out explicitly,
e.g. the internals page vs. the report page sessions). If, after reading the plan, you judge
that subagents are *not* worth using for this task (e.g. the work is too interdependent or too
small to benefit), say so to Alfonso **before doing anything else** — state your reasoning and
let him decide whether to switch models — rather than silently proceeding solo on Opus.

### Context files — read these first
1. `CLAUDE.md` — project instructions + auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`,
   `PLAN.md`
2. `.claude/execution/phase3-visual-design.md` — **this is the complete, locked spec for this
   session.** Every visual and structural decision (dark glass hero, sticky nav, opportunity
   restructure, color tokens, fonts, what's explicitly rejected) was already decided in a prior
   discussion session. Treat it as an instruction guide, not a starting point for new design
   decisions — implement exactly what's specified. If something in it conflicts with the
   current codebase or turns out to be genuinely infeasible, stop and flag it rather than
   improvising a substitute.
3. `templates/report.html`, `templates/base.html`, `templates/internals.html`,
   `static/style.css`, `app.py` — current state of the dashboard you're modifying.

### What this session does, in one paragraph

This is a full structural and visual revamp of the report page (`/`), not a style polish: a
continuous dark navy-to-black glassmorphism zone spanning the top nav, country tabs, and a new
hero section with animated glass stat cards, a sticky scroll-spy navigation bar, a restructured
Opportunities section (top 3 by score expanded equally, rest collapsible), and a transition to
a light, soft-shadowed body below. The internals page (`/internals`) gets a lighter pass —
same shadow/hover/animation vocabulary, no dark hero, since it's dev-facing. Architecture stays
unchanged: Flask + Jinja2 server-side rendering, no build step, no JS framework, no new Python
dependencies — the dark hero and glass effects are pure CSS (gradients + `backdrop-filter`).

### How to execute

Follow `.claude/execution/phase3-visual-design.md` session-by-session exactly — it specifies
exact files, exact CSS values, exact Jinja2 logic, and an explicit dependency graph at the
bottom. Key points:
1. Session 1 (shared tokens/config) must complete before anything else.
2. Session 6 (internals page) is fully independent of the report-page sessions (2-5) — good
   subagent candidate, or just run in parallel with your own attention split if not using
   subagents.
3. Sessions 2, 3, 4 all touch `templates/report.html` in different sections (hero, sticky-nav/
   summary, opportunities) — sequence them or give subagents clear section boundaries to avoid
   merge conflicts.
4. Session 5 (shared animation JS) depends on the markup from 2-4 existing.
5. Session 7 (end-to-end verification) is last — actually run `python app.py` and check both
   pages in a browser against the checklist in the plan file. Don't mark this done from
   reading the code alone.

### Hard constraints (do not violate)
- Do not change the JSON schema (`data/latest_report.json` structure), or any Python pipeline
  file (`analyst.py`, `main.py`, `report.py`) — confined to `templates/`, `static/`, and
  `base.html`'s `<head>`/nav markup. `app.py` is untouched (all new stat values are computed in
  Jinja2 from data already passed to the templates).
- Do not change the feedback form's field names or POST behavior (`/feedback` route contract).
- Do not change country-tab *logic* (SG active, MY/VN/ID disabled) — only their visual
  treatment (glass pills).
- No new Python packages, no npm, no build step.
- Do not introduce a gold/champagne accent, a bento-grid sector layout, a single-opportunity
  spotlight card, or a dark internals page — these were considered and explicitly rejected in
  the discussion session. Re-litigating them is out of scope.

### When done
Update `STATE.md` and `PLAN.md` per the normal session-end protocol in `CLAUDE.md` — record
this as a completed visual-revamp sub-phase of Phase 3, and log the new dependencies (AOS,
Google Fonts/Space Grotesk) plus the dark-glass design direction decision in `CONTEXT.md`'s
decision log.
