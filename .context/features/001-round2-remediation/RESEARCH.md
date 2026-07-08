# Research: Round 2 Remediation

`--thorough` mode. This pass verified specific claims in CONTEXT.md against the actual files
(line numbers, exact content) so tasks can be written with zero ambiguity for the executor.
It did not re-run the broader investigation the two prior Fable reviews already did — their
Scope/Decisions/Open-Questions are trusted as-is. Nothing below changes CONTEXT.md's decisions;
this is confirmation + the exact strings/line numbers needed to write precise tasks.

## PDF verification (centerpiece task)

Read `docs/Copy of Business Sector _ed01.pdf` (all 3 pages) directly. Confirmed:

- 7 sectors: EDU, BER, MFG, HLS, RCC, CTE, PSS — matches `company_context.md`'s "Products by
  Business Sector" table exactly, verbatim, for all 7 sectors' solution lists.
- EDU solutions: STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour,
  Metaverse Platform, Customized AR/VR Content.
- BER solutions: Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart
  Virtual Inspection, 3D/VR Virtual Tour, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video
  Analytics Solution.
- **Conclusion: the "Products by Business Sector" section in `company_context.md` needs NO
  changes — it's already a correct, verified transcription.** The remaining work is entirely
  downstream: propagating this real catalog into the sections/prompts/keyword-lists that still
  say "SpatioX Twin/Ops/Audit/Walk" or assume BER is the only active domain.
- SpatioX naming map (used throughout the tasks below), confirmed consistent with the PDF's BER
  list: **Twin → Digital Twin, Ops → Smart Facility Management System, Audit → Smart Virtual
  Inspection, Walk → 3D/VR Virtual Tour.**

## File-by-file verification

**`data/company_context.md`** (152 lines) — SpatioX references remain in exactly 3 sections
(confirms CONTEXT.md's "3 remaining sections" count):
- `## Target Sectors & Use Cases` (lines 49-64) — every bullet ends with `(SpatioX Twin, ...)`.
- `## Key Prospects & Relationships` (lines 91-105) — every prospect entry says "Prospective
  buyer of SpatioX Twin...".
- `## Ecosystem Players` (lines 107-137) — contractor/consultant/integrator/FM-firm bullets
  reference "SpatioX Twin/Ops/Audit" repeatedly.
- `## Competitive Positioning` (lines 65-89) does **not** need changes — already sector-neutral,
  no SpatioX mentions.
- The file also opens with a stale draft banner (line 1: `<!-- DRAFT: rebuilt 2026-07-02 ...
  pending Alfonso review -->`) — out of this task's scope per CONTEXT.md; not touched.

**`pipeline/analyst.py`** (394 lines) — exact locations of the 4 sub-edits CONTEXT.md bundles
into one file-scoped task:
- `SUMMARY_PROMPT` (lines 61-98): line 65-67 hardcodes "Silversea products... SpatioX Twin
  (digital twin platform), SpatioX Ops (smart FM), SpatioX Audit (virtual inspection), SpatioX
  Walk (3D/VR tour)"; line 69 is the opportunities gate keyword list ("digital twin, BIM, 3D
  scanning, XR, smart FM, smart building, building automation, or proptech" — BER-only, no EDU
  terms); line 92 is the `product_fit` field instruction (already generically worded — "see the
  full product catalog in the company context" — so this line likely needs no text change, only
  the line 65-67 catalog block feeding it needs replacing, since the instruction just references
  "the company context" which won't itself have SpatioX text after the fix. Confirm during
  execution whether line 92 needs a small tightening once 65-67 changes shape.)
- `_generate_implications()` (lines 239-272): `SECTOR_IMPLICATIONS` dict (lines 242-248, BER-only
  wording e.g. "digital twin and smart FM solutions"), `SPECIFIC_KEYWORDS` dict (lines 250-261,
  every value string says "Silversea's SpatioX Twin/Ops/Audit/Walk").
- `_derive_competition_risks()` (lines 275-325): `HIGH_KEYWORDS` list (line 289, BER-only terms),
  mitigation string template (lines 301-303: "...differentiate on SpatioX platform integration").
- `_clamp_opportunity_scores()` (lines 194-207) — **not touched by the SpatioX task**; this is
  the function the new unit test (T8) covers. Confirmed it takes a plain list of dicts, no I/O,
  no LLM dependency — safe for pure-Python unit testing with zero mocking needed.
- `RAG_ENABLED` / `_build_rag_context()` (lines 8-12, 101-134) — confirmed dead code (never
  called from `analyse()`), consistent with the 2026-06-29 decision. Out of scope; not touched.

**`app.py`** (235 lines) — confirmed exact bug locations:
- Auth bypass: `login()` (lines 172-185) compares `submitted == os.environ.get("ADMIN_PASSWORD",
  "")` with `==` (not constant-time) and with no guard for an empty/unset `ADMIN_PASSWORD` — an
  empty submitted field paired with an unset env var currently succeeds as admin. Same `==` issue
  for the viewer-password comparison at line 180.
- `/feedback` (lines 126-169): `submitter` sanitization (line 137) only does
  `.strip().replace(" ", "_")` — a value like `../../foo` or `..\\..\\foo` survives untouched and
  is used directly in both the feedback filename (line 150) and the pending-source filename (line
  165), both under `data/`. `relevance_rating` (line 141) does a bare `int(...)` with no
  try/except — a non-numeric value (e.g. `"high"`) raises an uncaught `ValueError`, which Flask
  turns into a 500. CORS (lines 224-229) is a global `@app.after_request` applied to every route,
  not scoped to `/feedback`.
- Admin/source-approval routes (lines 188-221): `approve_source()` (line 206-213) currently reads
  `sector`/`domain` from the form but hardcodes `country_code="SG"` implicitly via
  `source_suggestions.approve()`'s default parameter — no country field is read from the request
  yet, confirming CONTEXT.md's "add a country selector" is a genuine gap, not just UI polish.

**`pipeline/source_suggestions.py`** (56 lines) — confirmed the singleton-mutation bug precisely:
`approve()` (lines 27-49) imports `COUNTRIES` (the module-level list created once at import time
in `config/sources.py` line 24) and mutates it in place (`country["sources"].append(...)`) before
calling `save_sources(countries)`. `config/sources.py`'s `save_sources()` (lines 12-21) already
does its own fresh read-modify-write of the *file* (re-reads `sources.json` to preserve sibling
keys like `_domain_tagging_status`, then overwrites just the `countries` key) — so the on-disk
write itself is already safe. The actual bug is that `approve()`'s in-memory `countries` list
being appended to is the **stale import-time snapshot**, not a fresh read — if `sources.json` on
disk has changed since the process started (e.g. a hand-edit, or a source added via a different
code path), that change is silently lost because `save_sources()` receives (and writes back) the
stale in-memory list, and `save_sources()`'s file-level merge only protects sibling *root* keys,
not the `countries` array's own content. Fix: `config/sources.py` needs a `load_sources()`
function that re-reads the file fresh (i.e., calls the existing private `_load()` again, not the
cached `COUNTRIES` global), and `source_suggestions.approve()` must call that instead of using
the imported `COUNTRIES` name.

**`templates/admin.html`** (107 lines) — confirmed structure: the approve form (lines 33-70) has
a `sector` `<select>` and `domain` checkboxes but no country field at all. Adding a country
`<select name="country">` inside the same `<form>` (before the submit button, alongside the
existing sector/domain fields) is a straightforward, same-pattern addition.

**`static/animations.js`** (243 lines) — confirmed the exact PDF-afterprint bug: `initPdfExport()`
(lines 189-221). The `confirmBtn` click handler builds `expandedByUs` (entity groups it opened)
but toggles `print-exclude` on/off sections via a *separate*, untracked loop (lines 206-209:
`document.querySelectorAll('.pdf-section-checkbox').forEach(...)`). The `afterprint` restore
handler (lines 213-219) then does `document.querySelectorAll('.print-exclude').forEach(el =>
el.classList.remove('print-exclude'))` — this blanket selector also matches
`#pdf-export-panel`, which is confirmed (via `templates/report.html` line 111:
`<div id="pdf-export-panel" class="print-exclude fixed top-3 right-4 z-50">`) to carry
`print-exclude` **permanently in the HTML**, not added by JS. So after the first export, the
panel's self-hiding class is stripped and never restored. Fix direction confirmed as the
"cleaner" option from CONTEXT.md's Implementation Decisions: track a `toggledByUs` array of the
actual elements toggled in the checkbox loop (mirroring the existing `expandedByUs` pattern) and
restore only those, instead of querying `.print-exclude` globally.

**`config/sources.json`** (755 lines) — confirmed structure: one country object (`"code": "SG"`)
containing `sources` (array, each with `name`/`url`/`sector`/`domain`/`type`/`active`),
`priority_keywords` (15 terms, line 662-678, BER-only), `keywords` (73 terms, line 679-751,
BER-only + competitor/prospect names), and a root-level `_domain_tagging_status` string (line
754, unreviewed draft flag — explicitly out of scope, don't touch beyond what T5 requires).
NUS (lines 260-269) and NTU (lines 270-279) are both `"sector": "customers"`, `"domain": ["BER"]`
today — both are genuine dual-tag candidates per CONTEXT.md's EDU stopgap decision, since a
university's own newsroom plausibly carries EDU-relevant campus/virtual-learning signals
alongside BER-relevant campus-facility signals.

**`tests/` directory** — confirmed it does not exist yet; this will be the first test file in the
repo. `pytest` (v9.0.2) and `python3`/Python 3.13.5 are both available in this environment. No
`conftest.py`, no existing test config (`pytest.ini`/`pyproject.toml` `[tool.pytest]` section) —
confirmed absent, so the test task must ensure `pipeline` is importable from wherever pytest is
invoked (repo root), which it is by default since `pipeline/` is a plain package at repo root
with no src-layout indirection.

## Non-findings (confirms CONTEXT.md, nothing new)

- `scripts/seed_vectorstore.py` requires no changes — it already re-chunks and re-embeds whatever
  is currently in `data/company_context.md` on every run; it just needs to be re-run once T3
  (the company_context.md rebuild) lands.
- `templates/report.html` and `templates/report.html`'s scoring glossary (line 311: "How directly
  the opportunity matches a SpatioX product capability") still say "SpatioX" too, and so does a
  dead Jinja fallback branch (lines 209, 215, only reached if `_generate_implications()` failed to
  set `implication`, which it always does). **Flagging, not fixing** — CONTEXT.md's scope
  bullet enumerates `data/company_context.md` and `pipeline/analyst.py` specifically and does not
  list `templates/report.html`; touching it would be scope creep under the "minimal impact" /
  "don't touch adjacent working code beyond what's listed" constraint. Worth a follow-up note in
  Open Questions for a future round, not a task here.
