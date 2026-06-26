# PLAN.md — Current Phase Plan

*Active plan for the phase currently in progress. Overwritten at the start of each new phase.*
*Task status updated by /context-update. Full phase history lives in ROADMAP.md.*

---

## Phase 3.5 — Visual Design Revamp

**Goal:** Full structural and visual revamp of the report page (`/`) — dark glass hero, animated stat cards, sticky scroll nav, restructured opportunities — and a lighter matching restyle of the internals page (`/internals`). No architecture changes.

**Done when:**
- Report page has continuous dark gradient zone (nav + country tabs + hero) with glass stat cards, glow orbs, Space Grotesk headings
- Sticky scroll-spy nav appears on scroll past hero, highlights active section
- Opportunities sorted by score: top 3 fully expanded, rest collapsible with chevron toggle
- Internals page restyled with matching shadow/hover/animation vocabulary (no dark hero)
- Feedback form POST contract unchanged, no Python file changes

**Execution file:** `.claude/execution/phase3-visual-design.md`

---

## Tasks

### 1. Tailwind config + shared CSS tokens `[DONE]`
Added `navy-deep`, `font-heading`, `fade-slide-up` keyframes to Tailwind config. Added Google Fonts + AOS CDN links. Added `.glass-card`, `.shadow-soft`, `.shadow-soft-lg`, `.card-hover` to `static/style.css`.

**Files:** `templates/base.html`, `static/style.css`

---

### 2. Continuous dark zone (nav + tabs + hero) `[DONE]`
Restructured `base.html` with dark zone wrapper (`{% block dark_zone_class/style %}`). Glass country tab pills. Report page hero with gradient, glow orbs, glass stat cards, section IDs.

**Files:** `templates/base.html`, `templates/report.html`

---

### 3. Sticky scroll nav + light body sections `[DONE]`
Added fixed scroll nav with section links. Applied `shadow-soft`, `font-heading`, `data-aos="fade-up"` to Executive Summary, Sectors, Synthesis, Feedback sections.

**Files:** `templates/report.html`

---

### 4. Opportunities restructure `[DONE]`
Sorted by `total_score` descending. Top 3 fully expanded with `shadow-soft` + `card-hover`. 4th+ rendered as collapsible rows with chevron toggle.

**Files:** `templates/report.html`

---

### 5. Shared animation JS `[DONE]`
Created `static/animations.js`: count-up animator (`animateCount`), sticky nav IntersectionObserver, scroll-spy active section highlighting.

**Files:** `static/animations.js` (new), referenced from `templates/base.html`

---

### 6. Internals page restyle `[DONE]`
All `shadow-sm` → `shadow-soft`. `card-hover` on stat/timeline cards. Count-up data attributes on numeric cards. Chart.js animation. AOS on timeline/vector store cards. `font-heading` on page title.

**Files:** `templates/internals.html`

---

### 7. End-to-end verification `[DONE]`
- [x] `python app.py` starts without errors
- [x] `http://localhost:5000/` — 200 OK, 34k chars, all key elements present (gradient, glass cards, font-heading, AOS, scroll nav, section IDs, shadow-soft, card-hover, gradient submit button)
- [x] `http://localhost:5000/internals` — 200 OK, 43k chars, all key elements present (shadow-soft, card-hover, count-up targets, chart animation, AOS fade-up, font-heading, no dark hero)
- [x] Feedback POST works — creates JSON in `data/feedback/`
- [x] Country tabs: glass pills on both pages, SG active, MY/VN/ID disabled
- [ ] Visual verification by Alfonso in browser (automated checks passed, human eyes needed)
- [ ] Collapsible opportunities (4th+) not tested — test data only has 2 opportunities

## Phase Complete
**Date:** 2026-06-23
**Summary:** Dark glass hero revamp, sticky scroll nav, restructured opportunities, internals restyle — all implemented per locked spec. Both pages render correctly. Pending: visual verification by Alfonso and testing with a dataset containing >3 opportunities.

---

## Dependencies

```
1 (tokens/config)
   │
   ├─→ 2 (dark zone: nav+tabs+hero)
   │      │
   │      ├─→ 3 (sticky nav + summary/synthesis)
   │      ├─→ 4 (opportunities restructure)
   │      └─→ 5 (shared animation JS — after 2,3,4 markup exists)
   │
   └─→ 6 (internals, independent of 2-5) ← subagent
            │
   7 (verify, after everything)
```
