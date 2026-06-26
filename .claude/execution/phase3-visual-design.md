# Phase 3.5 — Visual Design Revamp: Execution Guide

Read `CLAUDE.md` first (auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`).
This file is the **complete, locked spec** for this session. It is an instruction guide, not
a brainstorm — every visual/structural decision below was already made in a prior discussion
session. Do not re-decide direction, palette, or structure; implement exactly what's specified.
If something here is genuinely impossible given the current codebase, stop and flag it before
improvising a substitute.

---

## What Must Be True When This Is Done

1. **Report page (`/`) is a structural and visual revamp, not a style polish.** Dark glass
   hero with animated stat cards, sticky scroll nav, restructured opportunities section, light
   body below the hero. It must look and feel like a premium product, not a Bootstrap-tier
   internal tool.
2. **Internals page (`/internals`) shares the same shadow/hover/animation vocabulary** as the
   report page's light body, but stays light throughout — no dark hero there.
3. **Zero architecture change.** Flask + Jinja2 + server-side rendering unchanged. No npm, no
   build step, no JS framework. The dark hero and glass cards are CSS (gradients +
   `backdrop-filter: blur`), not a new rendering layer.
4. **No regressions.** Feedback form POST contract, JSON schema consumed by templates, and all
   existing Python pipeline files are untouched.
5. **Country tabs are restyled (glass pills) as part of the continuous dark zone, but their
   logic (SG active, MY/VN/ID disabled) is unchanged** — visual only.

---

## Locked Design Tokens

Add these once in Session 1; every other session consumes them — do not invent alternates.

### Color (no new colors beyond what's listed)
- Existing brand colors stay as the Tailwind config already defines them: `navy #0a2540`,
  `navy-light #1a3a5c`, `green-accent #2d6a4f`, `green-accent-light #40916c`.
- Add `navy-deep: #050d18` (near-black navy, for the darkest point of the hero gradient — not
  pure black, keeps it on-brand).
- All glow/accent effects use `green-accent` / `green-accent-light` only. Do not introduce gold,
  champagne, or any other accent color.

### Gradients
- **Hero/dark-zone background:** `linear-gradient(135deg, #050d18 0%, #0a2540 55%, #102a45 100%)`
  applied to the continuous dark zone (top nav + country tabs + hero, see Session 2).
- **Glow orbs:** 2-3 large, soft, blurred circular `div`s positioned absolutely behind hero
  content, using `green-accent` at low opacity (`rgba(45,106,79,0.25)` and similar), `filter:
  blur(80px)` or via Tailwind arbitrary value, `border-radius: 50%`. Purely decorative, `z-index`
  below content, `pointer-events: none`.
- **CTA button gradient:** `green-accent` → `green-accent-light`, diagonal, used only on the
  feedback submit button.

### Glassmorphism (hero stat cards + country tab pills only — not used in the light body)
```css
.glass-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1rem;
}
```
Text inside `.glass-card` on the dark zone uses white / `text-gray-200` / `text-gray-400` —
never the navy/gray-700 tones used in the light body.

### Shadows (light body only — not used in the dark zone, which uses glass instead)
```css
.shadow-soft {
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06);
}
.shadow-soft-lg {
  box-shadow: 0 2px 4px rgba(15, 23, 42, 0.06), 0 16px 40px rgba(15, 23, 42, 0.10);
}
```
Used in both the report page's light body and the internals page (replacing all current
`shadow-sm`/`shadow-md` usage in those areas).

### Typography
- Add **Space Grotesk** via Google Fonts CDN: one `<link>` for
  `https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap`
  in `templates/base.html` `<head>` (replacing the implicit system-font fallback; Inter stays
  the body font via the existing Tailwind `fontFamily.display` config — add a second
  `fontFamily.heading: ['Space Grotesk', 'system-ui', 'sans-serif']` entry).
- Space Grotesk is used for: hero headline, hero stat numbers, all section `<h2>` headers, and
  opportunity score badge numbers. Everything else (body text, labels, form fields) stays Inter.

### Animation keyframes (Tailwind config `extend.keyframes`/`extend.animation`)
- `fade-slide-up`: `opacity 0→1`, `translateY(12px→0)`, used for AOS-equivalent reveals if not
  handled by AOS directly.
- No CSS `@keyframes` needed for count-up — that's JS-driven (Session 5).
- Card hover lift: not a keyframe, a transition — `transition: transform 0.2s ease, box-shadow
  0.2s ease;` with `:hover { transform: translateY(-2px); }` paired with the shadow-soft-lg
  swap.

---

## Prerequisites — Install Before Starting

### Python packages: none. No changes to `requirements.txt`.

### CDN dependencies (add to `templates/base.html` `<head>`, no install):
- **Google Fonts** — Space Grotesk + Inter, link above.
- **AOS (Animate On Scroll)**:
  `<link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">` and
  `<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>`, with
  `AOS.init({ duration: 500, once: true, offset: 40 })` called in a shared script block.
- Tailwind CSS and Chart.js — already present, no change.

### Claude Code tooling for this session:
- **`frontend-design` plugin** (`anthropics/claude-plugins-official`) — install and let it
  auto-invoke during template/CSS generation for aesthetic judgment on spacing, contrast, and
  motion timing within the locked tokens above (it should refine execution, not override the
  locked direction).
- `ui-ux-pro-max-skill` and HTMX: evaluated in the prior discussion, not used in this pass.

### Explicitly rejected: any JS framework, any build step, any new Python dependency, gold/
champagne accent color, bento-grid sector layout, single-opportunity spotlight card, full-dark
internals page. These were considered and explicitly declined — do not reintroduce them.

---

## Session Map

```
Session 1 (Tailwind config + shared CSS tokens: glass, shadows, gradients, fonts, AOS setup)
        │
        ├──→ Session 2 (Continuous dark zone: nav + country tabs + hero, report.html top)
        │
        ├──→ Session 3 (Sticky scroll nav + light-body sections: summary/sectors/synthesis)
        │           — depends on Session 2 existing (needs hero section IDs to scroll to)
        │
        ├──→ Session 4 (Opportunities restructure: top 3 expanded + collapsible rest)
        │
        ├──→ Session 5 (Shared animation JS: count-up counters, scroll-active nav highlight)
        │           — touches Sessions 2-4's markup, do after them
        │
        ├──→ Session 6 (Internals page: light restyle, same vocabulary, no dark hero)
        │
        └──→ Session 7 (End-to-end verification)
```

Session 1 must complete first. Sessions 2, 3, 4 touch `report.html` in different sections and
can be sequenced or subagented in parallel if the executing session splits by section
(header/hero vs. body cards vs. opportunities) — but Session 3's sticky nav needs Session 2's
section `id` attributes to exist, so do 2 before 3 if not parallelizing carefully. Session 6
(internals) is fully independent of 2-5 and can run in parallel with any of them. Session 5
(shared JS) should come after the markup it animates exists. Session 7 last, always.

**Subagent guidance:** Session 6 (internals) is the cleanest subagent candidate — fully
independent file, no dependency on report.html sessions. Sessions 2/3/4 all modify
`templates/report.html` in different regions; if subagented, give each a clear line-range/
section boundary to avoid merge conflicts, or do them sequentially in the main context instead.

---

## Session 1: Tailwind Config + Shared CSS Tokens

**Files:** `templates/base.html` (Tailwind config block, `<head>` CDN links), `static/style.css`

**Exact additions:**
1. In `base.html`'s `tailwind.config` script: add `navy-deep: '#050d18'` to `colors`, add
   `fontFamily.heading: ['Space Grotesk', 'system-ui', 'sans-serif']`, add `extend.keyframes`
   with `fade-slide-up` and `extend.animation` mapping it.
2. Add Google Fonts `<link>` and AOS `<link>`/`<script>` tags to `<head>`.
3. Add `AOS.init(...)` call — put it in a `{% block scripts %}` in `base.html` itself (not
   per-page) so both report.html and internals.html get it without duplicating the call; child
   templates extend `{% block scripts %}` with `{{ super() }}` if they add their own scripts.
4. In `static/style.css`: add `.glass-card`, `.shadow-soft`, `.shadow-soft-lg` exactly as
   specified in the Locked Design Tokens section above. Add `.card-hover` utility class
   bundling the transform/shadow hover transition. Keep all existing classes
   (`.score-badge`, `.score-bar-track`, `.score-bar-fill`, `.tab-btn`, `.tab-content`) — do not
   remove, only add.

---

## Session 2: Continuous Dark Zone (Nav + Country Tabs + Hero)

**Files:** `templates/base.html` (nav + country-tabs markup), `templates/report.html` (new
hero section, replacing the current flat `bg-navy` header bar)

**What to build:**
1. In `base.html`: change the `<nav>` and country-tabs `<div>` backgrounds so they sit on the
   same gradient as the hero (apply the hero gradient to a wrapping container spanning nav +
   country tabs + hero, OR apply the gradient as a `body`-level background image that the nav/
   tabs/hero sit transparently on top of — either approach is fine, the requirement is no
   visible light-colored seam between nav, country tabs, and hero). Country tab pills: replace
   `bg-green-accent`/`bg-gray-100` solid pills with `.glass-card`-style pills (active tab gets a
   brighter glass + green-accent border, disabled tabs stay muted glass, same disabled
   `cursor-not-allowed` behavior — logic unchanged, only the pill's visual treatment changes).
   Place the 3 decorative glow-orb `div`s behind this combined zone.
2. In `report.html`: remove the current flat `<div class="bg-navy ...">` header block (lines
   ~13-25 in the current file) and replace with a hero section containing:
   - Headline: "Market Intelligence Report" in Space Grotesk (`font-heading`), large
     (`text-4xl` or `text-5xl`), white, with the country + date sub-line below it in
     `text-gray-300`/`text-gray-400`.
   - A 4-card row of `.glass-card` stat cards: Total Signals, Opportunities Found, Top Score,
     Sectors Covered. Each card: large Space Grotesk number (start at 0, animated by Session
     5's JS, target value computed in Session 4's Jinja2 changes — see below), small uppercase
     label beneath in `text-gray-400`.
   - Compute the 4 stat values in `report.html`'s Jinja2 (no Python/route changes needed, all
     derivable from the existing `report` dict already passed to the template):
     - Total Signals: sum of `signals | length` across `report.signals_by_sector.values()`.
     - Opportunities Found: `report.opportunities | length`.
     - Top Score: max of `opp.total_score` across `report.opportunities` (or `0` if empty).
     - Sectors Covered: count of sectors in `report.signals_by_sector` with a non-empty list.
   - Give the hero section `id="hero"` and add `id` attributes to each subsequent section
     (`id="summary"`, `id="sectors"`, `id="opportunities"`, `id="synthesis"`, `id="feedback"`)
     for Session 3's sticky nav to target.
   - The hero's bottom edge transitions to the light body background (`bg-bg-page`) — either a
     hard cut (acceptable) or a subtle fade; do not overthink this, a clean cut at the hero's
     closing `</div>` is fine.

---

## Session 3: Sticky Scroll Nav + Light Body Sections

**Files:** `templates/report.html` (Executive Summary, Synthesis sections; new sticky nav
markup)

**What to build:**
1. Sticky nav: a `.glass-card`-styled pill bar, `position: fixed` (or `sticky`), centered or
   right-aligned near the top, containing links to `#summary`, `#sectors`, `#opportunities`,
   `#synthesis`, `#feedback`. Hidden/transparent while the hero is in view, fades in once the
   user scrolls past the hero (toggle a class via a scroll listener — implement in Session 5's
   shared JS, not here; this session just adds the markup with the right `id`/`href` wiring and
   a `nav-hidden`/`nav-visible` class pair for Session 5 to toggle).
2. Executive Summary and Synthesis cards: apply `.shadow-soft` (replacing `shadow-sm`), add
   `data-aos="fade-up"` to each section wrapper. No structural change to these two sections
   beyond the visual tokens — they stay as bullet lists per the existing Jinja2 loop.
3. Add `id` attributes (`id="summary"`, `id="synthesis"`) to these sections if not already
   added in Session 2 — confirm Session 2's IDs landed on the right elements before duplicating.

---

## Session 4: Opportunities Restructure

**Files:** `templates/report.html` (Opportunities section)

**What to build:**
1. Sort `report.opportunities` by `total_score` descending in the Jinja2 template (use
   `report.opportunities | sort(attribute='total_score', reverse=true)` — if `total_score` can
   be missing, default via the existing `opp.total_score | default(0)` pattern already in the
   file).
2. First 3 (post-sort): render exactly as the current full card layout (score badge, quote,
   entry point/deadline/action/product-fit grid, score breakdown bars, source link) — apply
   `.shadow-soft` + `.card-hover` instead of `shadow-sm`. Equal visual weight across all 3 — no
   single one gets extra emphasis.
3. Remaining opportunities (index 3+): render as a compact collapsed row — badge (smaller) +
   title + first ~80 chars of `source_quote` or `concrete_action` (whichever is present,
   truncated with Jinja2 `| truncate(80)`) + a chevron icon. Clicking the row toggles a hidden
   `<div>` containing the same full detail block used for the top 3 (entry point, deadline,
   action, product fit, score bars, source link) via vanilla JS (`classList.toggle('hidden')`
   on click, rotate the chevron via a CSS class toggle — no JS animation library needed for
   this, a CSS `transition` on `max-height` or a simple `hidden`/`block` toggle is sufficient).
4. `id="opportunities"` on the section wrapper (confirm against Session 2/3, don't duplicate).

---

## Session 5: Shared Animation JS

**Files:** new `static/animations.js` (referenced from `base.html`), no changes to existing
inline scripts beyond removing anything superseded

**What to build, as one small file:**
1. `animateCount(el, target, duration=1200)` — count-up from 0 to `target`, written once,
   called for each of the 4 hero stat cards on page load (not scroll-triggered — they're above
   the fold).
2. Sticky-nav scroll behavior: on scroll, toggle the nav's visibility class once scroll position
   passes the hero's height; use `IntersectionObserver` on each section (`#summary`, `#sectors`,
   `#opportunities`, `#synthesis`, `#feedback`) to add an `active` class to the matching nav
   link when that section is in view, removing it from the others.
3. Wire this file into `base.html` via `<script src="{{ url_for('static',
   filename='animations.js') }}"></script>`, placed after AOS's script tag.
4. Do not duplicate AOS's own reveal logic — AOS handles `data-aos` reveals independently;
   this file only handles count-up and nav-highlight, which AOS doesn't do.

---

## Session 6: Internals Page — Light Restyle, Same Vocabulary

**Files:** `templates/internals.html`

**What to change (visual only, no new cards, no `app.py` changes):**
1. Replace all `shadow-sm` with `.shadow-soft` on every card/section in the file (Last Run
   banner cards, source-scores chart card, table, vector store browser card, feedback digest
   timeline cards).
2. Add `.card-hover` to the Last Run banner's 5 stat cards and the feedback digest timeline
   cards.
3. Last Run banner's 5 numbers: animate count-up on page load using the same
   `animateCount()` helper from Session 5's `static/animations.js` (these are plain integers
   already in the template — `metadata.sources_scraped`, `sources_passed_filter`,
   `dedup_merged`, `entities_extracted`; the timestamp card is not a number, leave it static).
4. Chart.js config (in the existing inline `<script>` block): add `animation: { duration: 800,
   easing: 'easeOutQuart' }` to the chart options so bars grow in rather than snapping.
5. Tab switching JS (existing `.tab-btn`/`.tab-content` logic): add a CSS transition
   (`opacity`/`transition: opacity 0.15s ease`) so switching tabs fades rather than instantly
   swapping `display`. Minimal JS change: toggle an `opacity-0`/`opacity-100` class with a
   short `setTimeout` before/after toggling `active`, or rely purely on the existing `.active`
   class plus a CSS transition on opacity (simplest: add `transition-opacity duration-150` to
   `.tab-content` and let the existing `active`/inactive class swap handle it, no JS change
   needed if `.tab-content` uses opacity instead of `display: none` — adjust `static/style.css`
   `.tab-content { display: none; }` rule accordingly if pursuing the no-JS-change route).
6. Add `data-aos="fade-up"` to the feedback digest timeline entries and vector store document
   cards for scroll-in reveal, consistent with the report page.
7. **No dark hero anywhere on this page.** Page header (`<h1>AI System Internals</h1>` block)
   stays on the light background, just gets the Space Grotesk heading font applied via
   `font-heading` class.

---

## Session 7: End-to-End Verification

**Verify checklist — actually run the app and check in a browser, don't mark done on inspection
alone:**
- [ ] `python app.py` starts without errors
- [ ] `http://localhost:5000/` — nav, country tabs, and hero form one continuous dark gradient
      zone with no visible light seam; glow orbs visible but subtle; 4 stat cards count up on
      load; headline and stat numbers render in Space Grotesk, body text in Inter
- [ ] Sticky nav appears once scrolled past the hero, hides/fades when back at the top, active
      section highlights correctly while scrolling through Summary → Sectors → Opportunities →
      Synthesis → Feedback
- [ ] Sector cards: icons + count badges render correctly for all 5 sectors, hover lift works
- [ ] Opportunities: top 3 (by score, sorted) fully expanded and visually equal; 4th+ render
      collapsed and expand on click without layout jank
- [ ] Feedback form still submits successfully, creates JSON in `data/feedback/`, thank-you
      state still swaps correctly — no regression from any markup changes around it
- [ ] `http://localhost:5000/internals` — same shadow/hover system, Last Run numbers count up,
      source-scores chart bars animate in, tab switching fades instead of snapping, no dark hero
      present
- [ ] No console errors (AOS, Google Fonts load, `animations.js`, Chart.js)
- [ ] Country tabs: SG still shows as active/selected, MY/VN/ID still show as disabled — only
      the visual treatment (glass pill) changed, not the logic
- [ ] Page load time not noticeably degraded (2 small CDN scripts + 1 font + ~one new small JS
      file — should be negligible; confirm by feel, no formal benchmark needed)

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
   └─→ 6 (internals, independent of 2-5)
            │
   7 (verify, after everything)
```
