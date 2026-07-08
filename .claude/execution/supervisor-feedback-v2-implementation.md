# Supervisor Feedback Round 2 — Implementation Guide

Read `CLAUDE.md` first (auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`).

This file is the **code-grounded, execution-level spec** for the round previously scoped in
`.claude/execution/supervisor-feedback-v2-handoff.md`. That document is still the source of
truth for *scope and decisions* (auth model, scoring rubric, PDF export approach, phase
sequencing) — do not re-litigate anything it locked. This document's job is different: every
file, function, and line reference below was re-verified against the actual repo on
2026-07-02 by four parallel read-only research passes, so an execution agent can implement each
step with **zero further research or judgment calls**, except where explicitly flagged as an
open call for Alfonso.

**Read the "Corrections to the Handoff Doc's Assumptions" section below before starting —
one topic's target file structure changed underneath the handoff doc between when it was
written and when this spec was written.**

---

## Corrections to the Handoff Doc's Assumptions

The handoff doc assumed `pipeline/analyst.py` still had a single ~150-line `SYNTHESIS_PROMPT`
(lines 48-155) with an explicit `RELEVANCE GATE` block (lines 83-85) and a sector-categorization
instruction (lines 69-79), per the 2026-06-26 CONTEXT.md entries. **This is no longer the file's
structure.** The 2026-06-29 "split-model failed, simplified prompt" decision and the 2026-06-30
per-sector synthesis rewrite replaced that single prompt with three separate prompts:

- `SECTOR_EXTRACT_PROMPT` (lines 27-46) — Phase 1, per-sector raw-content extraction
- `SECTOR_SYNTHESIS_PROMPT` (lines 48-59) — Phase 2, one call per sector, converts extraction
  text into structured `[{entity, signal, source_name}]` JSON
- `SUMMARY_PROMPT` (lines 61-88) — Phase 4, single call, produces `executive_summary`,
  `opportunities`, `synthesis` from the already-structured signals

Topics 2 (opportunity source links) and 3 (scoring rubric) both still target the right *prompt*
(`SUMMARY_PROMPT`, which still contains the opportunity schema, the empty `source_url` field,
and the un-scaled `scores` block) — the handoff doc's *intent* was correct, only its line
numbers and "SYNTHESIS_PROMPT" name were stale. This spec below uses the correct current names
and lines throughout.

**Also note, for Alfonso's awareness, not as a task in this round:** the widened relevance gate
("tracked entity taking a BER-relevant action") that CONTEXT.md's 2026-06-26 entry describes as
applied and verified working is **no longer present** in the current `SUMMARY_PROMPT`. The
current opportunities instruction (line 69) is back to a keyword-only gate: *"Only include
signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building,
building automation, or proptech. Zero opportunities is correct when nothing qualifies."* It
appears to have been dropped, not deliberately reverted, during the 2026-06-29/06-30 prompt
rewrites. This is not one of the 8 topics in scope this round and is **not** to be fixed as part
of this spec — flagging it here only so a future session doesn't mistake CONTEXT.md's old "fixed
and verified" entry for current reality.

---

## What Must Be True When This Round Is Done

Unchanged from the handoff doc — see that file's "What Must Be True" section (9 items: password
gate, opportunity source links, bounded scores, source-suggestion admin queue, PDF export,
three domain sections with real product catalog, universal-only regulatory content,
country-aware scaffolding, no regressions).

---

## Hard Constraints (apply to every step — unchanged from handoff doc)

- Use `py`, not `python`, for any Windows command.
- Do not touch `templates/base.html`'s dark-zone gradient/glass Tailwind color tokens
  (`base.html:15-37`), `static/style.css`'s `.glass-card` (`style.css:85-91`), `.shadow-soft`/
  `.shadow-soft-lg` (`style.css:96-107`), `.card-hover` (`style.css:112-124`) classes, or
  `static/animations.js`'s existing functionality (dark mode toggle `animations.js:24-52`,
  entity collapse/expand `animations.js:117-124`) — **extend, don't rewrite.**
- No `py main.py` run / live Groq call without Alfonso's explicit go-ahead and confirmation the
  daily quota is fresh.
- No new Python packages. Every step in this document is achievable with the stdlib + Flask +
  the already-installed `chromadb`/`groq` packages. If an execution agent believes a step
  genuinely needs a new dependency, stop and flag it to Alfonso — do not add one silently.
- Only touch files named in the step being executed.

---

## Open Items — Resolved

The handoff doc left four items undecided. Each is resolved below with reasoning; none required
guessing on something expensive to unwind.

### 1. ChromaDB country-scoping mechanism → **metadata filter, not separate collections**

**Resolved: metadata filter.** `pipeline/vectorstore.py` (50 lines total) is a thin global
singleton today — three fixed collection-name constants (`COMPANY_CONTEXT`, `REPORT_HISTORY`,
`FEEDBACK_DIGESTS`), one `PersistentClient`, and four functions (`get_collection`,
`add_documents`, `query`, `delete_documents`) that all take `collection_name` as a plain string
and pass `metadatas`/`ids` straight to ChromaDB's native `.add()`/`.query()`/`.delete()`.

A metadata filter (add `"country": "SG"` to every `metadatas` dict already being passed into
`add_documents`, and thread an optional `where` dict through `query()`) is a same-file, additive
change: three call sites in `pipeline/feedback.py`, one in `pipeline/weekly.py`, and one in
`pipeline/analyst.py`'s `analyse()` RAG-write block (lines 344-358) each gain one extra key in a
dict literal they already build. Separate collections would instead require generating
collection names dynamically per country everywhere `get_collection()` is called, multiplying
the number of ChromaDB collections and requiring every caller to know the current country —
a bigger surface change for a feature with **zero real non-SG data to test against yet** (per
the handoff doc: "no visible report output changes as a result of this step alone"). Metadata
filtering is fully backward-compatible: every existing document either gets no `country` key
(old data) or `"country": "SG"` (new writes), and `query()`'s new `where` parameter defaults to
`None` (no filter) everywhere it's not explicitly passed, so today's single-country behavior is
unchanged until MY/VN/ID sources actually exist.

### 2. Feedback-submission storage shape → **confirmed by research: flat JSON files, no `pending/` subdirectory**

`pipeline/feedback.py`'s `FEEDBACK_DIR` is `data/feedback/` (not `data/feedback/pending/` as the
handoff doc assumed) — `aggregate_feedback()` globs `*.json` directly in that directory
(`feedback.py:28`) and moves consumed files to `data/feedback/processed/` on success
(`feedback.py:73-75`). `app.py`'s `/feedback` POST route (`app.py:71-99`) writes one file per
submission there, named `{timestamp}_{submitter}.json`.

**Decision:** the new pending-source queue mirrors this exact pattern in a sibling directory,
`data/pending_sources/` (flat JSON files, one per suggestion, `processed/` and `rejected/`
subdirectories for admin decisions) — see Phase D2 below. This is not a new storage
abstraction; it is the same convention already proven for feedback.

### 3. `/admin` route placement → **confirmed: distinct `/admin` prefix**

Confirmed via research: `app.py` currently has exactly three routes (`/`, `/internals`,
`/feedback`), no `before_request` hook, no `SECRET_KEY`/`app.secret_key` anywhere, and no
login/auth template exists in `templates/` (only `base.html`, `report.html`, `internals.html`).
`/internals` is and remains unauthenticated/developer-facing. A distinct `/admin` prefix (new
route, new template) is confirmed as the right default — there is no existing admin-adjacent
code to fold into.

### 4. PDF export page-break behavior → **still an open follow-up, not resolved here**

No `@media print` rule exists anywhere in the repo today (confirmed absent via grep across all
`.css` files). Page-break behavior under real browser print rendering cannot be determined by
static code reading — it requires opening the page in a browser and testing actual pagination.
**This remains flagged as a possible post-implementation polish pass**, not a blocker for
shipping Phase A3. Implement the `@media print` rule per A3 below; if card-splitting-across-
pages looks bad when Alfonso actually tests it, `page-break-inside: avoid` tuning is a fast
follow-up, not a redo.

---

## Structural Prerequisite: `sources.py` → `sources.json` Migration

**Confirmed via research:** `main.py:8` (`from config.sources import COUNTRIES`) is the **only**
call site in the entire codebase importing from `config/sources.py` — grepped exhaustively
across all `.py` files. The migration is genuinely single-call-site.

**Confirmed current structure** of `config/sources.py` (first ~60 lines read):
```python
COUNTRIES = [
    {
        "name": "Singapore",
        "code": "SG",
        "active": True,
        "priority_keywords": [...],   # confirmed present via main.py:50,53 usage
        "keywords": [...],
        "sources": [
            {"name": "BCA", "url": "...", "sector": "gov_agencies", "type": "website", "active": True},
            # some entries also carry "fetcher": "dynamic" | "stealth" (e.g. IMDA, MCC, SJ Group, Schneider Electric)
            # active:False entries carry inline # comments explaining why (SGTech, Construction Plus Asia, CCCC, CHEC)
        ],
    },
]
```

### B1: Migrate to JSON

**New file:** `config/sources.json` — holds the exact same structure as the Python literal
above, as valid JSON. Since JSON has no comments, every existing `# reason` comment on an
`active: False` source becomes a new string field on that source dict:
`"inactive_reason": "ASP.NET site, news pages return 404"` (etc., one per currently-documented
inactive source — SGTech, CPG Consultant, FacilityBot, CCCC, CHEC, Construction Plus Asia if
still inactive).

**Rewrite `config/sources.py`** to a thin loader (this preserves `main.py:8`'s
`from config.sources import COUNTRIES` unchanged — zero other files need touching):
```python
import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "sources.json")


def _load():
    with open(_PATH, encoding="utf-8") as f:
        return json.load(f)["countries"]


def save_sources(countries):
    """Atomic write-back — used by the admin source-approval flow (Phase D)."""
    tmp_path = _PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({"countries": countries}, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, _PATH)


COUNTRIES = _load()
```
Note the JSON's top-level key is `"countries"` (a dict wrapper), not a bare list — this avoids
a bare top-level JSON array (harder to extend with future top-level keys like a schema version)
and matches the pattern already used by `data/model_research.md`-adjacent JSON artifacts in this
repo (e.g. `data/latest_report.json`'s wrapper-object convention). `COUNTRIES` itself, once
loaded, is still the same list of country dicts every existing consumer expects.

`save_sources()` is added now (Phase B) even though it's only consumed in Phase D, because it's
a one-line addition to the same file being touched anyway — consistent with the original
Phase 4 handoff's "touch a file once" rationale that motivated bundling this migration with the
domain/country field additions in the first place.

**Success criterion:** `main.py` runs unmodified (still `from config.sources import COUNTRIES`)
and produces byte-for-byte the same `COUNTRIES` structure as before the migration, verified by
loading both old and new versions in a throwaway script and comparing.

### B2: Add `domain` field

Add `"domain": [...]` (a list, since a source may be cross-cutting per the handoff doc) to every
source entry in `config/sources.json`. Values: `"BER"`, `"EDU"`, `"GENERAL"`.

**Default-assignment rule** (apply mechanically, then flag the whole file for Alfonso's review —
same pattern as Phase 4 Step 1's `company_context.md` draft marker):
- `gov_agencies`, `associations`, `general_news` sector sources → `["GENERAL", "BER"]` (they
  cover built-environment policy/industry news but aren't BER-exclusive)
- `customers`, `partners`, `competitors` sector sources → `["BER"]` (the current source list is
  entirely built-environment-flavored; there are no EDU-sector customers/partners/competitors in
  the source list today — confirmed no NUS/NTU/education-sector entries appear as `customers` in
  the reviewed portion of `config/sources.py`)
- If, during implementation, a specific source is obviously EDU-flavored (e.g. an education
  ministry or ed-tech association, if any exist in the full source list beyond what was
  reviewed), tag it `["EDU"]` instead of the sector default — use judgment per-source, but do
  not invent EDU sources that aren't already in the list. Real EDU sources are out of scope this
  round (no EDU source list has been submitted yet).

Add an HTML-comment-equivalent flag since JSON has no comments — add a top-level key in
`sources.json`: `"_domain_tagging_status": "draft — mechanical sector-based defaults applied 2026-XX-XX, pending Alfonso review, see supervisor-feedback-v2-implementation.md Phase B2"`. Remove this key only when Alfonso confirms the tagging (mirrors the `company_context.md` DRAFT-comment convention already established).

### B3: Country field — deliberate deviation from the handoff doc

**The handoff doc's plan (Topic 8) asks for a `"country": "SG"` field on every individual
source.** Research confirms this would be redundant: sources are already nested inside each
country's dict (`COUNTRIES = [{"code": "SG", "sources": [...]}]`), so a source's country is
already fully determined by which country dict it lives under. Duplicating `"country": "SG"` on
every one of ~60 source dicts adds no information and creates a consistency-drift risk (a future
edit could move a source between country dicts without updating its redundant field).

**Deviation:** do not add a per-source `"country"` field. Instead:
- `--country` filtering (Phase F1) operates on the existing `COUNTRIES[i]["code"]` field, exactly
  the way `--domain` filtering (Phase E4) operates on the new per-source `domain` field — the
  distinction is intentional: `country` is a property of *which list a source lives in*, `domain`
  is a property of *the source itself* (a single SG source can be BER and GENERAL at once; a
  source cannot live in two countries' lists at once without being two separate entries, which is
  correct — a source physically served from one country's market).
- When Phase D's admin-approval flow adds a new source, the admin picks which country's dict in
  `COUNTRIES` to append it to (defaulting to `"SG"`, the only country with real data) — this
  achieves the same practical outcome the handoff doc wanted (an admin can assign a country to a
  new source) without a redundant field on every existing source.

This is a concrete, reasoned deviation from the handoff doc, recorded here per this document's
own instructions to flag any sequencing/scope change with a reason.

---

## Sequencing: Phase A → F (unchanged structure from handoff doc, now grounded)

```
Phase A (independent, quick wins — no shared files, can run in parallel with each other)
  A1. Scoring rubric fix — pipeline/analyst.py SUMMARY_PROMPT + Python-side clamp
  A2. Opportunity source links — pipeline/analyst.py SUMMARY_PROMPT + templates/report.html
  A3. PDF export — templates/report.html + static/animations.js + static/style.css

Phase B (foundational — touches config/sources.py/.json once)
  B1. sources.py → sources.json migration
  B2. Add `domain` field (BER/EDU/GENERAL) to every source
  B3. Country field — deliberately NOT added per-source (see above); country stays
      nesting-implicit
  → unlocks C, D, E, F

Phase C (auth)
  C1. Viewer password gate
  C2. Admin password + /admin area scaffold

Phase D (depends on B for sources.json write-back, C for the admin gate)
  D1. Feedback form: new source-suggestion fields
  D2. Pending-source queue storage
  D3. /admin approval UI, writes to sources.json via save_sources()

Phase E (depends on B for domain field to exist)
  E1. company_context.md rebuild around real product catalog
  E2. analyst.py prompt updates — product-fit reasoning becomes catalog-aware
  E3. Dashboard domain switcher — EDU/BER/GENERAL tabs
  E4. main.py --domain flag, domain-scoped output files

Phase F (depends on B; lowest urgency)
  F1. main.py --country flag, country-scoped output files (bundled with E4's naming change)
  F2. ChromaDB country-scoping via metadata filter (see Open Item #1 resolution)
```

---

## Phase A — Quick Wins

### A1: Scoring Rubric Fix

**File:** `pipeline/analyst.py`

**Current state (confirmed):** `SUMMARY_PROMPT` (lines 61-88) contains this schema fragment at
lines 82-84:
```
"scores": {"strategic_fit": 0, "revenue_potential": 0, "win_probability": 0, "urgency": 0, "intelligence_quality": 0},
"total_score": 0
```
No scale, range, or calculation instruction exists anywhere in the prompt for these fields — the
`0`s are just JSON placeholder syntax, not instructions. `_synthesize_summary()` (lines 181-205)
parses the LLM's JSON via `json.loads(...)` at line 202 with zero validation; `analyse()` (line
339) copies `opportunities` into the report dict verbatim.

**Change 1 — prompt text.** Insert the locked rubric immediately before the JSON schema block in
`SUMMARY_PROMPT` (i.e., before whatever line currently introduces the `"opportunities"` array
schema, roughly line 70-71 based on the schema starting at line 71):
```
SCORING RUBRIC — each dimension is an integer from 1 to 5. total_score is the sum of all five (max 25).

- Strategic Fit: 1 = barely touches Silversea's product categories, 3 = plausible fit with one product line, 5 = direct fit explicitly matching a named solution.
- Revenue Potential: 1 = no budget/scale indication, 3 = mid-size project with no figure stated, 5 = named budget/tender value or large-scale (nationwide/multi-site).
- Win Probability: 1 = no visible relationship or a competitor is already engaged, 3 = neutral/open opportunity with no known blockers, 5 = existing Silversea relationship or the entity is actively seeking vendors.
- Urgency: 1 = no deadline / long-term exploratory, 3 = deadline stated but more than 3 months out, 5 = deadline imminent (under 1 month) or "now accepting proposals".
- Intelligence Quality: 1 = vague/secondhand/inferred, 3 = direct quote with some detail, 5 = direct quote plus named entity plus specific numbers/dates.

Every dimension must be an integer 1-5, never 0 and never above 5.
```

**Change 2 — Python-side safety net.** Add a new function in `pipeline/analyst.py` (near the
top, after imports, or directly above `_synthesize_summary`):
```python
_SCORE_DIMENSIONS = ["strategic_fit", "revenue_potential", "win_probability", "urgency", "intelligence_quality"]


def _clamp_opportunity_scores(opportunities: list) -> list:
    """Server-side safety net: never trust the LLM's own total_score or dimension range."""
    for opp in opportunities:
        raw_scores = opp.get("scores", {}) or {}
        clamped = {}
        for dim in _SCORE_DIMENSIONS:
            try:
                value = int(raw_scores.get(dim, 1))
            except (TypeError, ValueError):
                value = 1
            clamped[dim] = max(1, min(5, value))
        opp["scores"] = clamped
        opp["total_score"] = sum(clamped.values())
    return opportunities
```
Call it inside `_synthesize_summary()`, right after the `json.loads(...)` at line 202, before the
function returns:
```python
result = json.loads(response.choices[0].message.content)
result["opportunities"] = _clamp_opportunity_scores(result.get("opportunities", []))
return result
```
(Exact insertion point: wherever the parsed `result` dict is returned — apply the clamp to
`result["opportunities"]` before that return statement, whatever line number it lands on after
Change 1's prompt-text insertion shifts line numbers.)

**Success criterion:** every opportunity in a report's JSON has five integer scores each in
[1,5] and a `total_score` in [5,25] that is the literal sum of its five dimensions, regardless of
what the LLM returns — verifiable by unit-testing `_clamp_opportunity_scores()` directly against
hand-written inputs (a dict with a score of 9, a dict missing a dimension entirely, a dict with a
string `"5"` instead of an int) without any live Groq call.

---

### A2: Opportunity Source Links

**Files:** `pipeline/analyst.py` (`SUMMARY_PROMPT`), `templates/report.html`

**Current state (confirmed):** `SUMMARY_PROMPT` line 81 hardcodes `"source_url": ""` in the
opportunity JSON schema shown to the LLM — the user message built for this call
(`"Structured signals by sector:\n\n" + sections"`, per `analyse()`'s call site) only ever
contains `entity`/`signal` text, never a URL, so the LLM has no real URL to fill this field with
even if it wanted to (it either leaves it blank or fabricates one).

Signal cards already solve exactly this problem correctly: `templates/report.html:74-80` builds
a `source_urls` dict **inline in Jinja2** (not in Python) from `report.data_sources`:
```jinja2
{% set source_urls = {} %}
{% if report.data_sources is defined %}
  {% for src in report.data_sources %}
    {% if source_urls.update({src.name: src.url}) %}{% endif %}
  {% endfor %}
{% endif %}
```
and looks it up per-signal at `report.html:174-180` via
`source_urls.get(signal.source_name | default(''), '')`.

Opportunities currently render at two near-duplicate blocks — top-3 expanded
(`report.html:305-354`) and collapsed rows 4+ (`report.html:356-412`) — and both use
`opp.source_url` **directly** (`report.html:332-337` and `:388-393`), which is why the link is
always empty today.

**Change 1 — prompt schema.** In `SUMMARY_PROMPT`, replace the `"source_url": ""` field (line 81)
with `"source_name": "must exactly match a source_name value from the structured signals above"`.
Add one sentence to the prompt's opportunity instructions (near wherever `source_url` was
mentioned): *"Every opportunity must carry the `source_name` of the specific signal it was
extracted from — copy it verbatim from the structured signals input, do not invent a new
value."*

**Verify at implementation time** (this one detail genuinely needs a live code read, not just
this doc, since the exact user-message-building code for the summary call wasn't in this pass's
research scope): confirm that the structured per-sector signal JSON fed into `SUMMARY_PROMPT`'s
user message (built somewhere in `analyse()`, likely where `signals_by_sector` is assembled
before the `_synthesize_summary()` call) actually includes each signal's `source_name` field in
the text the LLM sees — `SECTOR_SYNTHESIS_PROMPT`'s output schema is confirmed to be
`{entity, signal, source_name}` per this document's research, so the field almost certainly is
present in the per-sector JSON already; just confirm the summary call's input text doesn't strip
it out before it reaches the LLM.

**Change 2 — template.** In `templates/report.html`, at both opportunity blocks
(`:332-337` and `:388-393`), replace:
```jinja2
{% if opp.source_url %}
<a href="{{ opp.source_url }}" ...>View source ...</a>
{% endif %}
```
with the same `source_urls` dict lookup already used for signals:
```jinja2
{% set opp_src_url = source_urls.get(opp.source_name | default(''), '') %}
{% if opp_src_url %}
<a href="{{ opp_src_url }}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-sm text-green-accent hover:opacity-70 font-medium mb-5 break-all transition-opacity">
  View source
  <svg class="w-3.5 h-3.5" ...>...</svg>
</a>
{% endif %}
```
(Keep the existing SVG icon and class list exactly as currently rendered — only the URL source
changes, from `opp.source_url` to the dict lookup. `source_urls` is already in scope at this
point in the template since it's built once near the top, lines 74-80, before both the signals
and opportunities sections render.)

**Success criterion:** every opportunity whose `source_name` matches an entry in
`report.data_sources` renders a working "View source" link; opportunities whose `source_name`
doesn't match anything render no link (same graceful-absence behavior signal cards already have)
— verifiable by hand-constructing a test `latest_report.json` with one matching and one
non-matching `source_name` and loading `/` in a browser, no live Groq call needed.

---

### A3: PDF Export

**Files:** `templates/report.html`, `static/animations.js`, `static/style.css`

**Current state (confirmed):**
- No `@media print` rule exists anywhere in the repo (grepped across all `.css` files).
- Entity collapse/expand (`animations.js:117-124`) is a simple class toggle — clicking
  `.entity-group-toggle` toggles `.open` on the closest `.entity-group`; the actual
  height-animation lives in CSS (a `grid-template-rows` transition keyed off `.open`), not in JS.
  This means "force-expand" for print is just: add `.open` to every `.entity-group` that doesn't
  already have it.
- Elements that must be hidden when printing (confirmed locations): nav bar
  (`templates/base.html:73-101`, includes the dark-mode toggle button `#theme-toggle` at
  `base.html:92-97`), scroll progress bar (`#scroll-progress`, `base.html:68`), sticky scroll-spy
  nav (`#scroll-nav`, `report.html:96-108`), spotlight overlay (`#spotlight-overlay`,
  `base.html:138`), and the feedback form section (`section#feedback`, `report.html:478-547`).
- The dark-zone gradient (`report.html:5-6` overriding `base.html:71`'s `dark_zone_class`/
  `dark_zone_style` blocks) and dark-mode Tailwind classes throughout must be overridden to
  force light colors on print — dark backgrounds waste ink/print badly.

**Change 1 — CSS.** Append a new `@media print` block to the end of `static/style.css` (do not
touch any existing rule, including the `prefers-reduced-motion` block at lines 401-411 — append
after it):
```css
@media print {
  #scroll-nav,
  #scroll-progress,
  #spotlight-overlay,
  #theme-toggle,
  section#feedback,
  nav {
    display: none !important;
  }

  html, body {
    background: #ffffff !important;
    color: #111827 !important;
  }

  .dark, [class*="dark:"] {
    background: transparent !important;
    color: inherit !important;
  }

  .print-exclude {
    display: none !important;
  }

  .glass-card, .shadow-soft, .shadow-soft-lg {
    box-shadow: none !important;
    backdrop-filter: none !important;
    border: 1px solid #e5e7eb !important;
  }

  .entity-group-content {
    display: block !important;
    grid-template-rows: 1fr !important;
  }

  .signal-card, .entity-group {
    page-break-inside: avoid;
  }
}
```
(The `nav` in the hide-list targets `base.html`'s nav bar element directly by tag — confirm
during implementation whether it needs a more specific selector if `nav` is used elsewhere for a
non-chrome purpose; based on research, `base.html:73-101`'s nav bar is the only `<nav>` in
`base.html`, and `report.html:96-108`'s sticky nav is `#scroll-nav`, already covered by ID.)

**Change 2 — export controls in `report.html`.** Add a small export panel (placement: near the
top of the report, e.g. inside the existing sticky nav area or as a new collapsible panel) with
one checkbox per sector section plus one for Opportunities, defaulting all checked, and an
"Export PDF" button:
```html
<div id="pdf-export-panel" class="print-exclude ...">
  <button id="pdf-export-toggle" type="button">Export PDF</button>
  <div id="pdf-export-options" hidden>
    {% for sector_key, label in sector_labels.items() %}
    <label><input type="checkbox" class="pdf-section-checkbox" data-section="sector-{{ sector_key }}" checked> {{ label }}</label>
    {% endfor %}
    <label><input type="checkbox" class="pdf-section-checkbox" data-section="opportunities" checked> Opportunities</label>
    <button id="pdf-export-confirm" type="button">Generate PDF</button>
  </div>
</div>
```
Give each sector's top-level wrapper element and the opportunities section wrapper a matching
`id="sector-{{ sector_key }}"` / `id="opportunities"` if they don't already have one (verify
existing IDs during implementation — the opportunities section wrapper is confirmed to start at
`report.html:270`, check if it already carries an ID).

**Change 3 — JS.** Add to `static/animations.js` (new function, do not modify existing
functions — call it from the same `DOMContentLoaded` init block that calls the other `init*`
functions):
```javascript
function initPdfExport() {
  var toggleBtn = document.getElementById('pdf-export-toggle');
  var optionsPanel = document.getElementById('pdf-export-options');
  var confirmBtn = document.getElementById('pdf-export-confirm');
  if (!toggleBtn || !confirmBtn) return;

  toggleBtn.addEventListener('click', function () {
    optionsPanel.hidden = !optionsPanel.hidden;
  });

  confirmBtn.addEventListener('click', function () {
    var expandedByUs = [];
    document.querySelectorAll('.entity-group:not(.open)').forEach(function (group) {
      group.classList.add('open');
      expandedByUs.push(group);
    });

    document.querySelectorAll('.pdf-section-checkbox').forEach(function (cb) {
      var section = document.getElementById(cb.dataset.section);
      if (section) section.classList.toggle('print-exclude', !cb.checked);
    });

    window.print();

    window.addEventListener('afterprint', function restoreState() {
      expandedByUs.forEach(function (group) { group.classList.remove('open'); });
      document.querySelectorAll('.print-exclude').forEach(function (el) {
        el.classList.remove('print-exclude');
      });
      window.removeEventListener('afterprint', restoreState);
    });
  });
}
```

**Success criterion:** clicking "Export PDF" → checking/unchecking sections → "Generate PDF"
opens the browser print dialog with (a) all `.entity-group`s force-expanded, (b) unchecked
sections hidden, (c) dark-mode colors overridden to light regardless of the user's current theme
toggle state, (d) nav/progress-bar/feedback-form/spotlight hidden — verifiable by manually
testing print-preview in a browser after implementation (per Open Item #4, exact page-break
polish is a follow-up if it looks bad, not a blocker).

---

## Phase B — `sources.py` → `sources.json` Migration + Domain Field

See the "Structural Prerequisite" section above for B1 (migration + `save_sources()`) and B2
(domain field, mechanical defaults + review flag). B3 is a deliberate no-op — see the reasoning
above; do not add a per-source country field.

**Success criterion (whole phase):** `config/sources.json` exists with every source from the old
`config/sources.py` present, each carrying a new `domain` list; `config/sources.py` is reduced to
the loader + `save_sources()`; `main.py` runs completely unmodified and produces the same
`COUNTRIES` list as before; `config/sources.json` carries the `_domain_tagging_status` draft flag
pending Alfonso's review.

---

## Phase C — Authentication

**Files:** `app.py`, new `templates/login.html`, new `data/viewer_password.txt`, new
`data/.flask_secret_key`

**Current state (confirmed):** `app.py` (107 lines) has exactly three routes — `/` (`report()`,
lines 31-37), `/internals` (lines 40-68), `/feedback` (POST/OPTIONS, lines 71-99) — plus one
`after_request` CORS hook (lines 102-107, not auth-related). No `app.secret_key` /
`app.config['SECRET_KEY']` is set anywhere. No `before_request` hook exists. Imports are minimal:
`json`, `os`, `datetime`, `from flask import Flask, render_template, request` (plus one inline
lazy import of `pipeline.vectorstore` inside `internals()`). No login/auth template exists.

### C1: Viewer password gate

**Secret key.** Add near the top of `app.py`, after `app = Flask(__name__)`:
```python
import secrets

_SECRET_KEY_PATH = os.path.join(DATA_DIR, ".flask_secret_key")


def _load_or_create_secret_key():
    if os.path.exists(_SECRET_KEY_PATH):
        with open(_SECRET_KEY_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(_SECRET_KEY_PATH, "w", encoding="utf-8") as f:
        f.write(key)
    return key


app.secret_key = _load_or_create_secret_key()
```
(Persisted to a local file, same pattern as the viewer password below, so sessions survive app
restarts — a purely random in-memory key would log everyone out on every restart, which is
disruptive for an internal tool.)

**Viewer password file + seed.** New file `data/viewer_password.txt` (plain text, single line,
the current password). Seed logic — add near the secret-key logic:
```python
_VIEWER_PASSWORD_PATH = os.path.join(DATA_DIR, "viewer_password.txt")


def _get_viewer_password():
    if not os.path.exists(_VIEWER_PASSWORD_PATH):
        seed = os.environ.get("VIEWER_PASSWORD", "changeme")
        with open(_VIEWER_PASSWORD_PATH, "w", encoding="utf-8") as f:
            f.write(seed)
        return seed
    with open(_VIEWER_PASSWORD_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _set_viewer_password(new_password):
    with open(_VIEWER_PASSWORD_PATH, "w", encoding="utf-8") as f:
        f.write(new_password)
```

**`before_request` gate.** Add:
```python
@app.before_request
def require_login():
    if request.endpoint in ("login", "static") or request.path == "/feedback":
        return None
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return None
```
(`/feedback` stays unauthenticated deliberately — it's the existing whole-company, no-login
feedback POST contract from Phase 2, explicitly protected as a no-regression item. The report and
internals pages become gated; the feedback submission itself does not, matching the handoff
doc's "no login" language for the feedback mechanism.)

Add `from flask import session, redirect, url_for` to the existing Flask import line.

**`/login` route:**
```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        submitted = request.form.get("password", "")
        if submitted == os.environ.get("ADMIN_PASSWORD", ""):
            session["authenticated"] = True
            session["role"] = "admin"
            return redirect(url_for("report"))
        if submitted == _get_viewer_password():
            session["authenticated"] = True
            session["role"] = "viewer"
            return redirect(url_for("report"))
        return render_template("login.html", error="Incorrect password")
    return render_template("login.html", error=None)
```

**New `templates/login.html`** — simple standalone page (not extending `base.html`, since
`base.html`'s nav/tabs assume an authenticated report context): a centered password form, styled
with the same `.shadow-soft` / brand-green (`#2d6a4f`) tokens already used elsewhere, no new
design tokens invented.

### C2: Admin password + `/admin` area scaffold

`ADMIN_PASSWORD` stays an env-var-only secret (no file, no UI to change it — per the handoff
doc, it's "held by CEO + technical roles," and a simpler env-var-only secret avoids building a
credential-rotation UI for a secret only a couple of people ever touch).

```python
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")  # populated fully in Phase D


@app.route("/admin/change-viewer-password", methods=["POST"])
def change_viewer_password():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    new_password = request.form.get("new_password", "").strip()
    if new_password:
        _set_viewer_password(new_password)
    return redirect(url_for("admin"))
```

**Success criterion:** visiting `/` or `/internals` unauthenticated redirects to `/login`;
submitting the viewer password grants `session["role"] = "viewer"` and access to `/` and
`/internals` but a 302-redirect-to-login on `/admin`; submitting `ADMIN_PASSWORD` grants
`/admin` access too; `/feedback` still accepts unauthenticated POSTs (regression check);
restarting the Flask process does not log existing sessions out (secret key persisted) and does
not reset the viewer password (file persisted).

---

## Phase D — Source Suggestion via Feedback Form

**Files:** `templates/report.html` (feedback form section), `app.py` (`/feedback` route,
`/admin` route), new `pipeline/source_suggestions.py`, new `templates/admin.html`

### D1: New feedback form fields

**Current state (confirmed):** the feedback form section lives at `report.html:478-547`
(`section#feedback`, containing `#feedback-form` and `#feedback-thanks`). `app.py`'s
`receive_feedback()` (lines 71-99) currently reads exactly these fields: `submitter`,
`report_date`, `relevance_rating`/`relevance`, `most_useful`, `missed_topics`,
`priority_changes` — no source-suggestion fields exist today.

Add three new **optional** fields to the form markup in `report.html`'s `#feedback-form`:
`source_name`, `source_url`, `source_description` (plain text inputs, clearly labeled "Suggest a
new source (optional)").

### D2: Pending-source queue storage

**In `app.py`'s `receive_feedback()`**, after the existing feedback-file-write logic (do not
modify the existing write — this is additive), add:
```python
source_name = (data.get("source_name") or "").strip()
if source_name:
    pending_dir = os.path.join(DATA_DIR, "pending_sources")
    os.makedirs(pending_dir, exist_ok=True)
    suggestion = {
        "source_name": source_name,
        "source_url": (data.get("source_url") or "").strip(),
        "description": (data.get("source_description") or "").strip(),
        "submitted_by": submitter,
        "submitted_at": now.isoformat(),
    }
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{submitter}.json"
    with open(os.path.join(pending_dir, filename), "w", encoding="utf-8") as f:
        json.dump(suggestion, f, indent=2, ensure_ascii=False)
```
This mirrors the exact existing `FEEDBACK_DIR` pattern (`data/pending_sources/` sibling to
`data/feedback/`, same timestamp+submitter naming) — confirmed as the right model per Open
Item #2's resolution above.

**New file `pipeline/source_suggestions.py`:**
```python
import json
import os
import shutil

from config.sources import COUNTRIES, save_sources

PENDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pending_sources")
PROCESSED_DIR = os.path.join(PENDING_DIR, "processed")
REJECTED_DIR = os.path.join(PENDING_DIR, "rejected")


def list_pending():
    if not os.path.isdir(PENDING_DIR):
        return []
    entries = []
    for filename in sorted(os.listdir(PENDING_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(PENDING_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        entry["_filename"] = filename
        entries.append(entry)
    return entries


def approve(filename, sector, domain, country_code="SG"):
    src_path = os.path.join(PENDING_DIR, filename)
    with open(src_path, "r", encoding="utf-8") as f:
        suggestion = json.load(f)

    new_source = {
        "name": suggestion["source_name"],
        "url": suggestion["source_url"],
        "sector": sector,
        "domain": domain if isinstance(domain, list) else [domain],
        "type": "website",
        "active": True,
    }

    countries = COUNTRIES
    for country in countries:
        if country["code"] == country_code:
            country["sources"].append(new_source)
            break
    save_sources(countries)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    shutil.move(src_path, os.path.join(PROCESSED_DIR, filename))


def reject(filename):
    src_path = os.path.join(PENDING_DIR, filename)
    os.makedirs(REJECTED_DIR, exist_ok=True)
    shutil.move(src_path, os.path.join(REJECTED_DIR, filename))
```

### D3: `/admin` approval UI

Fill in `templates/admin.html` (scaffolded empty in Phase C2) with a list of
`source_suggestions.list_pending()` entries, each with a form: sector `<select>` (the six
existing sector values — `gov_agencies`, `associations`, `customers`, `partners`, `competitors`,
`general_news`), domain `<select multiple>` or checkboxes (`BER`, `EDU`, `GENERAL`), and
Approve/Reject buttons posting to:
```python
@app.route("/admin/sources/<filename>/approve", methods=["POST"])
def approve_source(filename):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    sector = request.form.get("sector")
    domain = request.form.getlist("domain") or ["GENERAL"]
    source_suggestions.approve(filename, sector, domain)
    return redirect(url_for("admin"))


@app.route("/admin/sources/<filename>/reject", methods=["POST"])
def reject_source(filename):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    source_suggestions.reject(filename)
    return redirect(url_for("admin"))
```

**Success criterion:** submitting the feedback form with a `source_name` filled in creates a file
in `data/pending_sources/`; visiting `/admin` (as admin) lists it; approving with a chosen
sector/domain appends a new `active: True` entry to `config/sources.json` (via `save_sources()`)
and moves the file to `processed/`; rejecting moves it to `rejected/` without touching
`sources.json`; no source ever reaches `sources.json` without going through this approval step
(no auto-activation).

---

## Phase E — Multi-Domain Restructure + Company Context Rework

**Files:** `data/company_context.md`, `pipeline/analyst.py`, `templates/report.html`,
`templates/base.html`, `main.py`, `pipeline/report.py`

### E1: `company_context.md` rebuild

**Current state (confirmed, full 124-line file read):** line 1 still carries a stale
`<!-- DRAFT: expanded 2026-06-26 ... -->` marker from the Phase 4 pass. The file is still framed
entirely around the 4-product "SpatioX" catalog (Twin/Ops/Audit/Walk) at lines 14-20, referenced
again at line 42 ("four-product suite") and line 121 ("Silversea's four products"). It already
has a "Key Prospects & Relationships" section (lines 64-78) and an "Ecosystem Players" section
(lines 80-109, added by the Phase 4 pass). Regulatory mentions are SG-specific but sparse (BCA
Green Mark, IDD, GeBIZ, Smart Nation — lines 28, 78, 115, 117); there's no multi-country
regulatory content to strip, just SG-specific language to genericize.

**Changes:**
1. Replace the stale line-1 comment with a new dated draft marker:
   `<!-- DRAFT: rebuilt 2026-XX-XX for multi-domain/product-catalog overhaul, pending Alfonso review — see supervisor-feedback-v2-implementation.md Phase E1 -->`
2. Replace the Products section (lines 14-20) with the full product catalog from
   `docs/Copy of Business Sector _ed01.pdf`, organized by business sector, EDU and BER called out
   as active this round, the other five preserved for reference:
   ```markdown
   ## Products by Business Sector

   ### Education & EdTech (EDU) — active this round
   STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour,
   Metaverse Platform, Customized AR/VR Content.

   ### Built Environment & Real Estate (BER) — active this round
   Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart Virtual
   Inspection, 3D/VR Virtual Tour, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video
   Analytics Solution.

   ### Manufacturing & Industry 4.0 (MFG) — reference only, not active this round
   Digital Twin, Smart Virtual Inspection, IoT & AI Solutions, Smart Facility Management
   System, Customized AR/VR Content, 3D Scanning to 3D Model.

   ### Healthcare & Life Sciences (HLS) — reference only, not active this round
   Smart Facility Management System, 3D/VR Virtual Tour, Customized AR/VR Content, Digital
   Twin, IoT Solution, CCTV Video Analytics Solution.

   ### Retail, Commerce & Consumer Goods (RCC) — reference only, not active this round
   Virtual Showroom, Smart Virtual Mockup, Interactive Digital Content, Metaverse Platform,
   3D Scanning to 3D Model, Customized AR/VR Content.

   ### Culture, Tourism & Events (CTE) — reference only, not active this round
   Virtual Event Platform, 3D/VR Virtual Tour, Interactive Digital Content, Metaverse
   Platform, 3D Scanning to 3D Model.

   ### Public Sector & Smart Cities (PSS) — reference only, not active this round
   Digital Twin, Smart Facility Management System, Smart Virtual Inspection, IoT & AI
   Solutions, Customized AR/VR Content.
   ```
   This is the exact table transcribed from `docs/Copy of Business Sector _ed01.pdf` pages 1-3.
3. Update line 42's "four-product suite" and line 121's "Silversea's four products" references
   to reflect the multi-domain catalog (e.g. "Silversea's product catalog spans multiple
   solutions across seven business sectors — see Products by Business Sector above").
4. Genericize the regulatory mentions (lines 28, 78, 115, 117): replace named SG-specific
   schemes (BCA Green Mark, IDD, GeBIZ, Smart Nation) used as blanket qualifiers with a universal
   statement, and add one new short subsection: *"Regulatory & Certification Note: certification
   and procurement schemes vary by market (e.g. green-building certifications, government
   e-procurement portals). Assessing local regulatory fit is the responsibility of each local
   team — this document intentionally does not maintain country-specific regulatory detail."*
   Keep the named SG examples only as illustrative examples inside that note, not as
   authoritative blanket statements elsewhere in the file.

### E2: `analyst.py` prompt updates

`SUMMARY_PROMPT`'s `product_fit` field description (part of the opportunity schema, inside the
lines 61-88 range) currently assumes BER/digital-twin framing. Update its instruction text from
implying a fixed 4-product set to: *"which Silversea solution (see the full product catalog in
the company context, organized by business sector) best fits this opportunity, and why — reason
from the domain the signal's sector belongs to, not just built-environment framing."* No
structural change to the JSON schema itself is needed — `product_fit` stays a free-text field;
only the instructional wording pointing the LLM at the (now much larger) catalog changes.

Domain-aware source filtering happens upstream in `main.py` (E4), not inside `analyst.py` itself
— `analyse()` receives already domain-filtered sources, so no domain parameter needs to be
threaded through `analyst.py`'s functions.

### E3: Dashboard domain switcher

Mirror the existing country-tab pattern (`templates/base.html:104-122`, `.glass-card` inline
tabs) with a parallel domain-tab row: `EDU`, `BER`, `GENERAL`. `app.py`'s `/` route gains a
`?domain=` query param (default `"BER"`, since that's the only domain with real report data
today) and loads `data/latest_report_{country_code}_{domain}.json` with a fallback to the
existing `data/latest_report.json` for any report that predates domain-scoping (preserves the
`?demo=` toggle and existing presentation-mode JSON files untouched — those stay domain-agnostic
during this transition).

### E4: `main.py --domain` flag + domain-scoped output

**Current state (confirmed):** `main.py` has no `argparse`, only a manual
`"--no-email" not in sys.argv` check (line 98). Keep that lightweight style rather than
introducing `argparse` — consistent with the existing minimal convention:
```python
domain_arg = None
for arg in sys.argv:
    if arg.startswith("--domain="):
        domain_arg = arg.split("=", 1)[1]
```
When `domain_arg` is set, filter each country's sources before scraping:
```python
sources = country["sources"]
if domain_arg:
    sources = [s for s in sources if domain_arg in s.get("domain", ["GENERAL"])]
```
Pass `sources` (not `country["sources"]`) into `scrape_all(...)` at the existing call site
(`main.py:50`). When `domain_arg` is `None` (the default, no flag passed), behavior is completely
unchanged from today — every source runs, exactly as now, preserving backward compatibility.

**Output naming:** `pipeline/report.py`'s `save_report_json(report_data, country["name"])` call
site (`main.py:68`) needs a domain suffix. Update `save_report_json`'s signature to accept an
optional `domain` parameter and build the filename as
`latest_report_{country_code}_{domain}.json` when a domain is specified, falling back to the
existing `latest_report.json` (no country/domain suffix) when none is — this keeps the current
no-flag pipeline run producing exactly the same file it does today.

**Success criterion:** `py main.py --no-email --domain=BER` (not run live this session — verify
the argument-parsing and filtering logic by code review and a dry-run of the filtering function
against a small in-memory source list, not a live Groq call) filters sources to only
BER-domain-tagged ones before scraping; running with no `--domain` flag produces byte-identical
behavior to the current pipeline.

---

## Phase F — Multi-Country Scaffolding

### F1: `main.py --country` flag

Same pattern as E4, filtering `COUNTRIES` itself rather than a single country's sources:
```python
country_arg = None
for arg in sys.argv:
    if arg.startswith("--country="):
        country_arg = arg.split("=", 1)[1]

active_countries = [c for c in COUNTRIES if c["active"]]
if country_arg:
    active_countries = [c for c in active_countries if c["code"] == country_arg]
```
Bundle with E4's output-naming change — a run can specify both `--domain=` and `--country=`
independently; `save_report_json` already takes the country, so no further change needed beyond
E4's domain-suffix addition.

### F2: ChromaDB country-scoping via metadata filter

Per Open Item #1's resolution: add `"country": country["code"]` to the `metadatas` dict already
built at each of these confirmed write sites:
- `pipeline/feedback.py`'s `aggregate_feedback()` `add_documents` call (lines 64-71) — note this
  function currently runs once per pipeline invocation, not per-country (`main.py:42-44`, before
  the country loop); if feedback needs to become country-scoped, `aggregate_feedback()` would
  need to accept a country parameter — **flag this as a genuine open question for Alfonso**:
  feedback is currently a single whole-company stream regardless of country, and whether
  feedback should even be country-scoped (vs. staying a single global stream that just happens to
  currently be 100% SG-sourced) is a product decision, not a code-grounding question. Default
  recommendation: leave `aggregate_feedback()` global/unscoped for now (matches "pure plumbing,
  no visible effect" framing of this whole phase) and revisit only once real multi-country
  feedback volume exists.
- `pipeline/weekly.py`'s `generate_weekly_summary()` `add_documents` call (lines 77-89) — same
  question applies; same default (leave global for now).
- `pipeline/analyst.py`'s `analyse()` RAG-write block (lines 344-358, writing to
  `REPORT_HISTORY`) — this one is unambiguous: it runs inside the per-country loop
  (`main.py:46-90`), so `country["code"]` is already in scope at the call site. Add
  `"country": country["code"]` to its `metadatas` dict.

Add an optional `where` parameter to `pipeline/vectorstore.py`'s `query()`:
```python
def query(collection_name, query_text, n_results=5, where=None):
    collection = get_collection(collection_name)
    kwargs = {"query_texts": [query_text], "n_results": n_results}
    if where:
        kwargs["where"] = where
    return collection.query(**kwargs)
```
Since `_build_rag_context()` in `analyst.py` is confirmed dead code (never called, per this
document's research), no caller needs updating to pass `where` yet — this is pure plumbing ready
for when `_build_rag_context()` (or its Claude-Haiku-era replacement) is eventually restored.

**Success criterion:** `REPORT_HISTORY` documents written during a pipeline run carry a
`"country": "SG"` metadata key going forward; `query()` accepts but does not require a `where`
filter; no existing query call site breaks (all current call sites, if any beyond the dead
`_build_rag_context()`, keep working since `where` defaults to `None`). The open
feedback/weekly-scoping question is explicitly handed to Alfonso, not silently resolved.

---

## Verification Checklist

- [ ] A1: `_clamp_opportunity_scores()` exists in `analyst.py`, is called from
      `_synthesize_summary()`, and the rubric text is in `SUMMARY_PROMPT`. Verified via
      hand-written unit inputs, no live Groq call.
- [ ] A2: `SUMMARY_PROMPT`'s opportunity schema uses `source_name` not `source_url`;
      `report.html`'s two opportunity blocks use the `source_urls` dict lookup. Verified via a
      hand-constructed test JSON report loaded in a browser.
- [ ] A3: `@media print` block exists in `style.css`; export panel + JS exist in
      `report.html`/`animations.js`; force-expand and section-hide logic verified manually in
      browser print preview.
- [ ] B1: `config/sources.json` exists; `config/sources.py` is a thin loader + `save_sources()`;
      `main.py` runs unmodified and `COUNTRIES` is unchanged in shape.
- [ ] B2: every source in `sources.json` has a `domain` list; `_domain_tagging_status` draft flag
      present pending Alfonso review.
- [ ] B3: confirmed no per-source `country` field was added (deliberate deviation, documented).
- [ ] C1/C2: `/`, `/internals`, `/admin` all redirect to `/login` when unauthenticated;
      `/feedback` still accepts unauthenticated POSTs (regression check); viewer password
      survives app restart (file-based); sessions survive app restart (persisted secret key).
- [ ] D1/D2/D3: submitting a source suggestion creates a file in `data/pending_sources/`;
      `/admin` lists it; approve/reject move it correctly; approved sources appear in
      `config/sources.json` with `active: True` and admin-chosen sector/domain.
- [ ] E1: `company_context.md` has the full 7-sector product catalog, updated draft marker,
      genericized regulatory language.
- [ ] E2: `SUMMARY_PROMPT`'s `product_fit` instruction references the full catalog, not a fixed
      4-product set.
- [ ] E3: domain tab UI exists in `base.html`/`report.html`, mirroring the country-tab pattern.
- [ ] E4: `main.py --domain=X` filters sources correctly; no-flag behavior unchanged
      (byte-identical to pre-change pipeline behavior).
- [ ] F1: `main.py --country=X` filters `COUNTRIES` correctly.
- [ ] F2: `analyse()`'s RAG-write carries `country` metadata; `query()` accepts optional `where`;
      the feedback/weekly country-scoping question is flagged to Alfonso, not silently decided.
- [ ] No regressions: dark-glass visual tokens untouched, `?demo=clean|feedback` toggle still
      works, `/feedback`'s existing field contract (`submitter`, `report_date`,
      `relevance_rating`, `most_useful`, `missed_topics`, `priority_changes`) unchanged.
- [ ] No `py main.py` run occurred without Alfonso's explicit go-ahead.
- [ ] No new Python packages were added without flagging Alfonso first.

## Ending This Round (per `CLAUDE.md`'s session protocol)

1. Update `STATE.md` with what was completed per phase, and the two open questions flagged in
   this document (feedback/weekly ChromaDB country-scoping decision, PDF page-break polish).
2. `CONTEXT.md` gets dated entries for: the `sources.json` migration, the B3 deviation (no
   per-source country field, nesting-implicit instead), and the company-context product-catalog
   rebuild.
3. `PLAN.md` gets overwritten for whichever phase is executed first (per the sequencing above,
   Phase A has no dependencies and should be planned/executed first).
