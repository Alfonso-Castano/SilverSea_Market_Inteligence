# Supervisor Feedback Round 2 — Planning Document

Read `CLAUDE.md` first (auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`).

This document is the **locked output of a planning-only session** with Alfonso (2026-07-02,
continued). No code was touched during that session. Every decision below — scope, sequencing,
auth model, scoring rubric, source-storage migration — was explicitly discussed and confirmed
with Alfonso; do not re-litigate them. This document's job is to hand a fully-scoped set of
decisions to an **implementation-planning session**, which should code-ground each item against
the actual current state of the repo (file contents, existing helper functions, existing data
shapes) before writing an execution-level spec like `.claude/execution/phase4-efficiency-coverage-handoff.md`.

Several items below reference code by file/line as observed on 2026-07-02. **Re-verify against
current code before planning implementation** — do not assume these line numbers or shapes are
still accurate by the time this is picked up.

---

## Source of Truth for This Round

This round bundles supervisor demo feedback plus Alfonso's own ideas, collected via a structured
brain-dump session, organized into 8 topics, each with implementation approach discussed and
locked. Also incorporates `docs/Copy of Business Sector _ed01.pdf` (Silversea's 7 business
sectors — EDU, BER, MFG, HLS, RCC, CTE, PSS — with sector descriptions and mapped product
catalog), supplied mid-session. Only EDU and BER are in scope for active build-out this round;
the other 5 sectors are documented for future reference only.

---

## What Must Be True When This Round Is Done

1. **The report is password-gated.** A shared viewer password protects the report; a separate
   admin password (held by CEO + technical roles) can change the viewer password without a
   redeploy.
2. **Every opportunity card links to its source article**, using the same `source_name` →
   `data_sources` URL-lookup pattern already used for signal cards (per the 2026-06-30 decision
   in CONTEXT.md) — not a homepage link, not an LLM-fabricated URL.
3. **Opportunity scores are bounded and mean something.** Five dimensions (strategic fit,
   revenue potential, win probability, urgency, intelligence quality), each 1-5, defined by the
   rubric in this document. `total_score` is capped at 25 and computed/verified in Python, not
   trusted blindly from the LLM.
4. **Anyone can suggest a new source from the feedback form**, and an admin (gated by the admin
   password from #1) can review and approve it into the live source list without editing code.
5. **The report can be exported as a PDF** with user-controlled section inclusion, using a
   browser-print approach (no new PDF-generation dependency).
6. **The report has three domain sections — EDU, BER, and General** — each backed by
   domain-tagged sources, with company context and prompts reflecting Silversea's real product
   catalog (not the SpatioX 4-product placeholder) mapped to sector.
7. **Company context regulatory content is stripped to universal-only statements** —
   country-specific regulation is removed; local users are trusted to judge regulatory
   relevance themselves.
8. **The pipeline has country-aware scaffolding** (`country` field, `--country` flag, scoped
   output files) ready to accept non-SG sources, even though no non-SG sources exist yet.
9. **No regressions**: dark-glass visual design (Phase 3.5), existing feedback form POST
   contract, `?demo=clean|feedback` toggle, and any file not named in a step are untouched.

---

## Hard Constraints (apply to every step)

- Use `py`, not `python`, for any Windows command.
- Do not touch `templates/base.html`'s dark-zone gradient/glass tokens, `static/style.css`'s
  `.glass-card`/`.shadow-soft`/`.card-hover` classes, or `static/animations.js`'s existing
  functionality (collapse/expand, spotlight, scroll-spy, dark mode toggle) — extend, don't
  rewrite.
- No `py main.py` run / live Groq call without Alfonso's explicit go-ahead and confirmation the
  daily quota is fresh (recurring constraint from prior phases — Groq free tier is 100k TPD).
- No new Python packages unless a step explicitly requires one. The `sources.py` → `sources.json`
  migration (Phase B) and the auth/PDF-export work (Phases A/C/D) should be achievable with
  stdlib + Flask only. Flag it to Alfonso before adding a dependency.
- Only touch files relevant to the step being executed.

---

## Locked Decisions Per Topic

### 1. Authentication
- **Two secrets, no user accounts:** `VIEWER_PASSWORD` (shared company-wide, gates the report)
  and `ADMIN_PASSWORD` (CEO + technical roles only, gates a `/admin` area).
- Flask session-based gate (`before_request` checks a signed session cookie; unauthenticated →
  redirect to `/login`).
- Viewer password must be changeable without a redeploy — store it in a small local file the
  app reads per-request (not just an env var), with an admin-only endpoint to rewrite it. Env
  var becomes the initial default/seed value only.
- `/admin` area also gates the source-approval queue (Topic 4) — same `ADMIN_PASSWORD`, one
  auth mechanism serving two features.
- **Verify before implementing:** current `app.py` route structure, whether Flask sessions are
  already configured (`SECRET_KEY` set), and how/where the feedback form's existing POST
  route works, since `/admin` should follow the same conventions.

### 2. Opportunity source links
- Drop the LLM-fabricated `"source_url": ""` field from `SUMMARY_PROMPT` (currently
  `pipeline/analyst.py`, in the `scores` block region — re-verify line numbers).
- Have the LLM emit `source_name` on each opportunity instead (mirroring the signal schema).
- Template-side: reuse the existing `source_urls` dict lookup (from `data_sources`) already
  built for signal cards in `report.html`, applied to the opportunities section too.
- **Verify before implementing:** exact current opportunity JSON schema in `analyst.py`, and
  the exact Jinja2 lookup pattern used for signal source links in `report.html` so this stays
  consistent rather than inventing a second lookup mechanism.

### 3. Opportunity scoring rubric (fixes the >20/25 bug)
**Root cause (confirmed in code, 2026-07-02):** `SUMMARY_PROMPT`'s `scores` JSON shape has no
scale/range instructions or total-score calculation guidance at all — the LLM invents its own
scale. This is not a clamping bug, it's a missing-instruction bug.

**Locked rubric** — five dimensions, each an integer 1-5, `total_score` = sum (max 25):

| Dimension | 1 (low) | 3 (mid) | 5 (high) |
|---|---|---|---|
| Strategic Fit | Barely touches Silversea's product categories | Plausible fit with one product line | Direct fit — explicitly matches a named solution |
| Revenue Potential | No budget/scale indication | Mid-size project, no figure stated | Named budget/tender value, or large-scale (nationwide/multi-site) |
| Win Probability | No visible relationship; competitor already engaged | Neutral — open opportunity, no known blockers | Existing Silversea relationship, or entity actively seeking vendors |
| Urgency | No deadline / long-term exploratory | Deadline stated but >3 months out | Deadline imminent (<1 month) or "now accepting proposals" |
| Intelligence Quality | Vague, secondhand, or inferred | Direct quote, some detail | Direct quote + named entity + specific numbers/dates |

- Prompt must state this rubric explicitly (table or equivalent prose), including that each
  dimension is an integer 1-5.
- **Add a Python-side safety net**: after parsing the LLM's JSON, clamp each dimension to
  [1,5] and recompute `total_score` as their sum server-side — don't trust the LLM's own sum.
  This prevents a future prompt regression from silently reproducing the >25 bug.

### 4. Source suggestion via feedback form
- New feedback form fields: Source Name, Source URL, Description.
- Submissions land in a pending queue (JSON file, modeled on the existing feedback-submission
  storage pattern — **verify exact current mechanism in the feedback aggregation code before
  implementing**, don't assume a shape).
- `/admin` page (gated per Topic 1) lists pending sources; admin assigns sector + domain
  (+ country, once Topic 8 lands) and approves or rejects.
- Approval writes the new source into `config/sources.json` (see Topic-B migration below) as
  `active: True`.
- **No auto-activation without review** — a bad/irrelevant/paywalled URL should never reach the
  scraper without a human look first.

### 5. PDF export
- Browser-print approach: no new PDF library.
- Checkboxes per report section (sector groups) control a `print-hidden` CSS class.
- "Export" action: (a) force-expand any collapsed entity groups the user included (collapsed
  content renders empty when printed), (b) apply `@media print` overrides — force light-mode
  colors even if dark mode is toggled on (dark backgrounds print badly / waste ink), hide nav,
  buttons, feedback form, dark-mode toggle, (c) call `window.print()`.
- **Verify before implementing:** current collapse/expand implementation in `animations.js` to
  hook the "force expand" step correctly, and current dark-mode CSS variable structure to know
  what needs print-time overriding.

### 6 & 7. Multi-domain restructure + company context rework (bundled — same files)
- `domain` field on each source becomes 3-valued in practice for this round: `BER`, `EDU`,
  `GENERAL` (a source may carry more than one domain tag if genuinely cross-cutting).
- Dashboard domain switcher (already decided in prior session, not yet built) ships with these
  3 tabs.
- `company_context.md` and the analyst prompts (`analyst.py`) get rebuilt around the real
  product catalog from `docs/Copy of Business Sector _ed01.pdf`, replacing the SpatioX
  4-product-only framing:
  - STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour, Metaverse
    Platform, Customized AR/VR Content (EDU)
  - Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart Virtual
    Inspection, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video Analytics Solution (BER,
    and shared with several other sectors per the PDF's product-mapping table)
  - Full 7-sector table (with the 5 out-of-scope sectors — MFG, HLS, RCC, CTE, PSS — included
    for reference/future use) should be preserved in `company_context.md` even though only
    EDU/BER/GENERAL are active domains this round, so the multi-domain groundwork already
    covers eventual expansion.
- Product-fit reasoning in prompts becomes sector-aware (matches product to the domain the
  signal came from) rather than assuming BER/digital-twin framing for everything.
- Regulatory content in `company_context.md`: strip anything specific to a single country's
  regulatory regime; keep only statements that hold across all target countries. Note in the
  file (or a report disclaimer) that regulatory fit is the local team's responsibility to
  assess.
- **Verify before implementing:** current full contents of `company_context.md` and the exact
  current SYNTHESIS/SUMMARY prompt structure in `analyst.py`, since this is a rewrite of
  existing content, not a green-field addition.

### 8. Multi-country architecture scaffolding
- Add a `country` field to source config, mirroring the `domain` field pattern (default `"SG"`
  on all existing entries).
- `main.py` gains a `--country` flag alongside the planned `--domain` flag.
- Output artifacts become country+domain scoped, e.g. `data/latest_report_SG_BER.json`.
- ChromaDB context (company context, feedback digests, report history) needs country-scoping
  too, or a future MY run could retrieve SG-specific feedback as if it were relevant — decide
  the exact mechanism (separate collections vs. metadata filter) during implementation
  planning; not yet decided which of these two approaches to use.
- This is pure plumbing for this round — no real non-SG source data exists yet (still waiting
  on submissions via `docs/source_submission_template.xlsx`), so no visible report output
  changes as a result of this step alone.

---

## Structural Prerequisite: `sources.py` → `sources.json` Migration

**Decision:** Migrate source data out of `config/sources.py` (currently a Python literal) into
`config/sources.json`, with `sources.py` reduced to a thin loader function. This is a
prerequisite for Topic 4 (admin-approval writes) and is being done in the same pass as Topics 6/7/8
(domain + country fields) since all of them need the source config file touched anyway — better
to touch it once.

**Reason:** Programmatically appending a new source to a Python source file from a web request
(via text templating or AST manipulation) is fragile and hard to review/rollback. A JSON file
can be safely read, appended to, and written back with the standard library, and diffs cleanly
in git.

**Migration scope:** every place that currently does `from config.sources import SOURCES` (or
equivalent) needs to be found and updated to use the new loader. This is mechanical but must be
exhaustive — **grep the whole pipeline (`scraper.py`, `filter.py`, `main.py`, any others) for
`sources` imports before starting**, don't assume only one or two call sites exist.

---

## Sequencing: Phase A → F

```
Phase A (independent, quick wins — can run in parallel with each other)
  A1. Scoring rubric fix (Topic 3) — analyst.py prompt + Python-side clamp
  A2. Opportunity source links (Topic 2) — analyst.py schema change + report.html template
  A3. PDF export (Topic 5) — report.html + animations.js + new print CSS

Phase B (foundational — touches config/sources.py/.json once)
  B1. sources.py → sources.json migration
  B2. Add `domain` field (BER/EDU/GENERAL) to every source
  B3. Add `country` field (default "SG") to every source
  → unlocks C, D, E, F

Phase C (depends on B for admin gate to protect something meaningful, though technically
          auth itself doesn't require B — sequenced here because D needs both)
  C1. Viewer password gate (Topic 1)
  C2. Admin password + /admin area scaffold (Topic 1)

Phase D (depends on B + C)
  D1. Feedback form: new source-suggestion fields (Topic 4)
  D2. Pending-source queue storage
  D3. /admin approval UI, writes to sources.json

Phase E (depends on B for domain field to exist)
  E1. company_context.md rebuild around real product catalog (Topics 6/7)
  E2. analyst.py prompt updates — sector-aware product fit, regulatory content strip
  E3. Dashboard domain switcher — EDU/BER/GENERAL tabs (Topic 6)
  E4. main.py --domain flag, domain-scoped output files

Phase F (depends on B; lowest urgency — no visible effect until real country data arrives)
  F1. main.py --country flag, country-scoped output files
  F2. ChromaDB country-scoping mechanism (decide + implement collection-vs-metadata approach)
```

Phase A has no dependency on anything else and should ship first regardless of when the rest
starts. Phase F can trail behind everything else with no urgency, since Alfonso is still waiting
on country source submissions.

---

## Open Items for the Implementation-Planning Session

These were explicitly left undecided in the planning session and need a decision (or a
default + flag-to-Alfonso) before or during implementation planning:

1. **ChromaDB country-scoping mechanism** (Phase F2) — separate collections per country vs. a
   metadata filter on shared collections. Not decided.
2. **Exact current shape of the feedback-submission storage mechanism** (Topic 4) — this
   document assumes a JSON-file pattern analogous to what's used elsewhere, but the actual
   current feedback aggregation code should be read before assuming the pending-source queue
   should look the same way.
3. **Whether `/admin` is a distinct route prefix or folded into `/internals`** — not discussed;
   default to a distinct `/admin` route since `/internals` is currently unauthenticated and
   developer-facing, while `/admin` needs to be privileged.
4. **PDF export page-break behavior** — browser print's pagination is not fully controllable;
   if card-splitting-across-pages looks bad in testing, may need `page-break-inside: avoid`
   CSS tuning, flagged as a possible follow-up polish item rather than a blocker.

---

## Not In Scope This Round

- The other 5 business sectors from the PDF (MFG, HLS, RCC, CTE, PSS) — documented in
  `company_context.md` for future reference only, no active sources or domain tags this round.
- Real non-SG country sources — waiting on submissions via the Excel template.
- Claude Haiku migration / `_build_rag_context()` restoration — still deferred per STATE.md,
  unrelated to this round's scope.
- Deployment to company servers — still running locally; auth (Topic 1) makes this more
  reasonable to eventually deploy but doesn't itself constitute deployment work.
