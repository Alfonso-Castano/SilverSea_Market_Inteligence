# PLAN.md — Current Phase Plan

*Active plan for the phase currently in progress. Overwritten at the start of each new phase.*
*Task status updated by /context-update. Full phase history lives in ROADMAP.md.*

---

## Frontend Redesign — Dashboard Visual & Interaction Overhaul

**Goal:** Transform the report page from a flat card grid into an interactive, color-coded, visually rich dashboard with collapsible entity grouping, signal spotlight, dark mode, and sector-specific styling.

---

## Tasks

### 1. Color system + dark mode foundation `[x]`
Tailwind config updated with 6 sector colors (gov=blue, assoc=teal, customer=amber, partner=purple, competitor=rose, news=slate) + dark mode palette. Dark mode class-based toggle with localStorage persistence. `base.html` updated.

### 2. CSS overhaul `[x]`
Complete rewrite of `style.css`: sector color coding via CSS custom properties and `data-sector` attribute selectors, entity group collapse/expand with `grid-template-rows` animation, signal spotlight with backdrop blur, section zone backgrounds (rose tint for risks, green for opportunities), enhanced card hover states, full dark mode overrides, `prefers-reduced-motion` support.

### 3. JavaScript interactions `[x]`
`animations.js` rewritten: dark mode toggle with icon swap, scroll progress bar, entity group collapse/expand, signal spotlight (click card → expand + dim siblings + overlay, dismiss via click/Escape), staggered AOS delays on card grids. All original functionality (count-up, scroll nav, scroll spy) preserved.

### 4. Report template restructure `[x]`
`report.html` restructured: signals grouped by entity within each sector (Jinja2 dict grouping), collapsible entity bars with dot + name + count + chevron, sector header bars with gradient color + icon + count badge, source URL links on every signal card (mapped from `data_sources`), dark mode classes throughout, section zone wrappers for Risks and Opportunities.

### 5. Verify in browser `[x]`
Flask app running at localhost:5000. All elements verified: 5 sector headers, 27 entity groups, 82 signal cards, 65 source links, dark mode toggle, scroll progress bar, spotlight overlay.

---

## Phase Complete
**Completed:** 2026-06-30
**Summary:** Full frontend redesign executed — collapsible entity grouping, signal spotlight, 5-color sector coding, dark/light mode, scroll progress bar, source links, enhanced hovers. Ready for supervisor demo.
