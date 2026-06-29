# Phase 4 — Efficiency, Coverage & Bug-Fix Pass: Execution Guide

Read `CLAUDE.md` first (auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`).

This file is the **complete, locked spec** for this phase. Every decision below — scope,
sequencing, sector mappings, file targets, even the resolution of two source-list conflicts —
was already made in a prior discussion + two rounds of plan review (one code-grounded, one
pure-logic). Do not re-derive scope or re-litigate sequencing. If something here turns out to
be genuinely impossible given the current codebase, stop and flag it to Alfonso before
improvising a substitute — do not silently deviate.

This phase resolves supervisor feedback from the 2026-06-24 demo (full feedback transcript
already absorbed into the steps below — you do not need the original conversation) plus two
known bugs logged in `STATE.md`'s "Known Bugs" section.

---

## Execution Model

This phase is intended to be run by an Opus-based orchestrator session that delegates each
numbered step below to subagents (Sonnet/Haiku-tier, sized to task complexity) rather than
doing all the work in the main context. The orchestrator's job is sequencing, dependency
enforcement, and verification — not writing every line of code itself. See the companion
handoff prompt for how this session should be kicked off; this document is the spec each
subagent (or the orchestrator itself, if a step is done inline) must follow exactly.

---

## What Must Be True When This Phase Is Done

1. **The pre-LLM filter pipeline is measurably stricter and cheaper** — content reaching the
   Groq analyst is keyword-relevant (rule-based, zero AI cost) and truncated by keyword
   proximity instead of a blind character cut, so fewer tokens are wasted on irrelevant text
   without losing genuinely relevant content.
2. **`config/sources.py` reflects the full ~50-source ecosystem list** Alfonso's supervisor
   provided (see Step 4's exact source table), correctly mapped onto the existing 5-sector +
   general_news taxonomy — no new sectors introduced.
3. **No source that's expected to be active is silently returning null content** — every newly
   added or previously-broken source is either verified scrapable or explicitly marked
   `active: False` with a one-line reason comment, exactly like the existing
   SGTech/CPG Consultant/FacilityBot pattern.
4. **The report's metrics are self-explanatory** — a glossary/legend exists for every score
   and metric shown in `report.html` and `internals.html`, with an explicit caveat where a
   metric's *current output* may not yet reflect its *intended* behavior (see Step 5).
5. **Feedback digests don't accumulate unbounded in ChromaDB** — a consolidation mechanism
   exists, modeled on the existing weekly-summary pattern, so `feedback_digests` doesn't grow
   forever with stale, increasingly-redundant entries.
6. **A written model-research recommendation exists**, comparing Groq alternatives, Claude
   Haiku, and other realistic candidates on cost/quality/token-efficiency for this specific
   summarization+structured-extraction task — research only, no live/paid API calls made.
7. **`company_context.md` is expanded** with clearer BD priorities and the newly-provided
   ecosystem detail, explicitly flagged for Alfonso's review (not silently treated as final).
8. **The two known `SYNTHESIS_PROMPT` bugs are fixed in code** (empty-opportunities gate,
   sector mis-categorization) but explicitly marked **unverified** in `STATE.md** until a live
   Groq run confirms the fix — this is not optional paperwork, see Step 8's exact requirement.
9. **No regressions**: the dark-glass visual design (Phase 3.5), the feedback form's POST
   contract, the `?demo=clean|feedback` toggle, and any pipeline file not named in a step below
   are untouched.

---

## Hard Constraints (apply to every step)

- **No `py main.py` run, no Groq API call, no call to any paid LLM API, anywhere in this
  phase.** Groq's free-tier daily quota (100k TPD) was exhausted as of 2026-06-24 and resets at
  UTC midnight — that reset may or may not have happened by the time this phase runs; treat
  `main.py` as off-limits regardless unless Alfonso explicitly says the quota is confirmed
  fresh AND asks for a verification run himself. Steps that would normally be verified by a
  live run (Step 8, parts of Step 2/3) must be verified by code review and reasoning instead,
  and explicitly flagged as unverified where a live run is the only real test.
- **Use `py`, not `python`**, for any Windows command shown to Alfonso or run by an agent with
  shell access — Windows `py` launcher convention already established in this repo.
- **Do not touch**: `templates/base.html`'s dark-zone gradient/glass tokens, `static/style.css`'s
  `.glass-card`/`.shadow-soft`/`.card-hover` classes, `static/animations.js`, the `/feedback`
  POST route's field names, the `?demo=` toggle logic in `app.py`. These were locked in prior
  phases (3.5 and Presentation Prep) and are explicitly out of scope here.
- **Only touch files named in the step you're executing.** Don't refactor adjacent code "while
  you're in there."
- **No new Python packages** unless a step explicitly says so (none do — Steps 2/3's filtering
  logic uses only the standard library `re` module, no new NLP dependency).
- Company products are **SpatioX Twin, SpatioX Ops, SpatioX Audit, SpatioX Walk** — never
  "MetaTwin" anything, in any file you touch.

---

## Step Map & Dependencies

```
1 (expand company_context.md)
   │
   ├─→ 2 (rule-based filter criteria: filter.py + config/sources.py keyword tiers)
   │      │
   │      └─→ 3 (smart truncation: scraper.py) — uses same keyword infra as 2, do after 2
   │             │
   │             └─→ 4 (source expansion + scraper fixes, merged) — verifies new/fixed
   │                    sources against 2+3's filter/truncation behavior, not the old behavior
   │
   ├─→ 5 (metrics glossary, report.html/internals.html) — independent of 2/3/4, but its copy
   │      must carry the caveat described in Step 5 about Step 8's bug fix
   │
   ├─→ 6 (feedback digest consolidation, new logic modeled on pipeline/weekly.py) — independent
   │
   ├─→ 7 (model research, subagent-driven comparison, no live calls) — independent, can run
   │      in parallel with anything
   │
   └─→ 8 (SYNTHESIS_PROMPT bug fixes) — run LAST, after 1-6 are committed and stable. Marked
          unverified. Must also note in STATE.md that the next live run must check per-sector
          Groq TPM budget against Step 4's larger source count (see Step 8.4).
```

Steps 5, 6, 7 have no file overlap with 1-4 or each other and can be subagented in parallel.
Step 8 must be sequenced last regardless of parallelization elsewhere, per the explicit risk
finding from plan review: editing grounding-rule prompt logic with zero verification path is
the single highest-risk item in this phase, and should not be entangled with five other
in-flight changes.

---

## Step 1: Expand `company_context.md`

**File:** `data/company_context.md`

**Current state:** Already has 6 sections (Company Overview, Products, Target Sectors & Use
Cases, Competitive Positioning, Key Prospects & Relationships, BD Priorities) — this is
reasonably thorough, not a blank slate. Do not rewrite it from scratch; extend it.

**What to add:**

1. A new section **"Ecosystem Players"** (insert after "Key Prospects & Relationships", before
   "BD Priorities") covering the categories from the supervisor's source-list document that
   aren't yet represented: main contractors, consultants, M&E/BMS system integrators, and
   facility management firms. Use this structure:
   - **Main contractors** (potential collaboration/JV partners on construction-phase digital
     twin and TOP-audit work): MCC, CSCEC, CCCC, CHEC, Sembcorp, SJ Group.
   - **Consultants** (potential channel partners — BIM/engineering firms that could
     recommend or co-bid SpatioX on projects): AECOM, Meinhardt Group, CPG Consultant, BECA,
     Ramboll, Azbil.
   - **M&E system integrators / BMS** (potential integration partners — SpatioX Ops competes
     and complements building management system vendors): Honeywell, Johnson Controls,
     Schneider Electric, Quantum Automation.
   - **Facility management firms** (potential customers for SpatioX Ops, or channel partners
     reselling FM services on top of it): Cushman & Wakefield, ST Synthesis (ST Engineering),
     Savills.
   - One line per category explaining the BD angle (why this category matters to Silversea,
     not just a name list) — follow the existing prose style used in "Key Prospects &
     Relationships" (each entry has a one-line rationale, not just a name).
2. Expand the existing **"Known competitors in Singapore"** list under "Competitive
   Positioning" to include the additional competitors from the new source list not already
   present: TwinMatrix, Minuscule Technologies, Alstern Technologies, Aperio, Nuvola Media,
   SSI Corporate, NeuronCloud, FacilityBot, Cryotos. (Hiverlab, G Element, TwinLogic, Axomem,
   DataMesh are already listed — don't duplicate.)
3. Add a short note at the end of **"BD Priorities"**: *"Ecosystem players (contractors,
   consultants, M&E integrators, FM firms) are channel/partnership signals, not direct BD
   targets like tracked prospects — a contractor announcing a new project is lower priority
   than a tracked prospect (CapitaLand, Mapletree, etc.) announcing the same project."* This
   gives Step 2's filter criteria a concrete priority signal to encode.

**This draft must be flagged for Alfonso's review before being treated as ground truth** — add
an HTML comment at the top of the file: `<!-- DRAFT: expanded 2026-XX-XX by execution agent,
pending Alfonso review — see Phase 4 handoff Step 1 -->`. Do not remove this comment yourself;
Alfonso removes it once he's reviewed the content.

**Success criterion:** the file has the new "Ecosystem Players" section, the expanded
competitor list, the BD-priority note, and the pending-review comment. No other section
content is altered.

---

## Step 2: Rule-Based Filter Criteria (no AI, code-only)

**Files:** `pipeline/filter.py`, `config/sources.py`

**Current state (read this before changing anything):**
- `pipeline/filter.py` is 32 lines: `score_relevance(text, keywords)` counts how many distinct
  keywords (case-insensitive substring match) appear in `text`; `filter_results(scraped,
  keywords, min_score=1)` keeps any result with `score >= min_score` (currently just 1 — i.e.
  a single keyword hit anywhere in 8000 characters of scraped text passes).
- `config/sources.py`'s `COUNTRIES[0]["keywords"]` is one flat list of ~45 terms (no tiering,
  no weighting) used for both relevance filtering and (currently) Step 3's truncation target.

**What's wrong with this today:** a single weak keyword hit (e.g. "tender" appearing once in
an 8000-character page about something unrelated) passes the gate just as easily as a page
dense with five high-value terms. This is why the relevance gate downstream in the analyst
prompt has to do so much of the filtering work itself, burning LLM tokens on content that a
cheap, free, rule-based pass could have already screened out.

**What to build:**

1. In `config/sources.py`, split the flat `keywords` list into two tiers, both still under
   `COUNTRIES[0]`:
   - `"priority_keywords"`: terms that strongly indicate BD relevance per Step 1's "BD
     Priorities" — tender/RFP language (`"tender"`, `"RFP"`, `"ITQ"`, `"ITT"`, `"GeBIZ"`),
     explicit product-category terms (`"digital twin"`, `"BIM"`, `"smart FM"`, `"smart
     building"`, `"proptech"`, `"building automation"`), and all tracked
     prospect/competitor/partner names already in the existing list's "Competitor names" /
     "Customer names" groups.
   - `"keywords"`: everything else from the current list (general industry vocabulary —
     `"construction technology"`, `"metaverse"`, `"consultancy"`, etc.) stays as the lower-tier
     list. Keep the existing list's grouping comments (`# Digital twin & immersive tech`,
     etc.) — just split the file's single list into these two named lists, don't lose the
     organization.
   - Add the new ecosystem-player names from Step 1 (MCC, CSCEC, CCCC, CHEC, Sembcorp, SJ
     Group, Meinhardt, BECA, Ramboll, Azbil, Johnson Controls, Schneider, Quantum Automation,
     ST Synthesis, Savills, TwinMatrix, Minuscule Technologies, Alstern Technologies, Aperio,
     Nuvola Media, SSI Corporate, NeuronCloud) to the lower-tier `"keywords"` list so Step 4's
     new sources have a baseline relevance signal even before any sector-specific content
     match.
2. In `pipeline/filter.py`, change `score_relevance` to accept both tiers and weight them:
   ```python
   def score_relevance(text: str, priority_keywords: list, keywords: list) -> int:
       text_lower = text.lower()
       priority_hits = sum(1 for kw in priority_keywords if kw.lower() in text_lower)
       general_hits = sum(1 for kw in keywords if kw.lower() in text_lower)
       return priority_hits * 3 + general_hits
   ```
   (Weight of 3 for priority hits is a deliberate, simple constant — not tuned against real
   data, since no live run is available this round. Document this in a one-line comment:
   `# weight is a placeholder constant — revisit once a live run can be scored against it`.)
3. Change `filter_results`'s default `min_score` from `1` to `3` — this means either one
   priority-tier hit, or three general-tier hits, are required to pass. Thread the two keyword
   lists through: `filter_results(scraped, priority_keywords, keywords, min_score=3)`.
4. Update the one call site in `main.py` (`filtered = filter_results(scraped,
   country["keywords"])` at line 54) to `filtered = filter_results(scraped,
   country["priority_keywords"], country["keywords"])`.
5. Keep the existing per-sector breakdown print statement in `filter_results` working — it
   already iterates `filtered`, no change needed there beyond the new parameters.

**Explicitly NOT in scope for this step:** no semantic/embedding-based relevance scoring, no
LLM call of any kind. This step must be implementable and testable with zero API calls — verify
it by running `filter_results` against a few hand-written test strings in a throwaway Python
shell (not a unit test file unless one already exists for `filter.py` — check before adding
one) to confirm the weighting and threshold behave as expected on obvious pass/fail examples.

**Success criterion:** `filter.py`'s functions accept the two-tier keyword lists and the new
weighting/threshold; `config/sources.py` has both lists populated; `main.py`'s call site is
updated; a quick manual check (3-4 example strings: one with a clear tender mention, one with
only generic industry vocabulary, one irrelevant) confirms the new threshold behaves as
intended before moving to Step 3.

---

## Step 3: Keyword-Anchored Smart Truncation

**File:** `pipeline/scraper.py`

**Current state:** `scrape_source()` does `text = text[:8000]` (line 30) — a blind character
cut applied to every source regardless of where the relevant content actually sits in the
page. For a long page, this can cut off entirely before reaching the one paragraph that
mentions a tender or partnership.

**What to build:**

1. Add a new function in `pipeline/scraper.py`:
   ```python
   import re

   def smart_truncate(text: str, priority_keywords: list, keywords: list, max_chars: int = 6000) -> str:
       """Keep sentences near keyword matches instead of blindly cutting at a char limit.
       Falls back to a blind cut if no keyword hits are found anywhere in the text."""
       sentences = re.split(r'(?<=[.!?])\s+', text)
       all_keywords = [kw.lower() for kw in priority_keywords + keywords]

       hit_indices = set()
       for i, sentence in enumerate(sentences):
           s_lower = sentence.lower()
           if any(kw in s_lower for kw in all_keywords):
               hit_indices.add(i)

       if not hit_indices:
           return text[:max_chars]

       WINDOW = 2  # sentences kept on each side of a keyword hit
       keep_indices = set()
       for i in hit_indices:
           for j in range(max(0, i - WINDOW), min(len(sentences), i + WINDOW + 1)):
               keep_indices.add(j)

       kept = [sentences[i] for i in sorted(keep_indices)]
       result = " ".join(kept)
       return result[:max_chars]
   ```
2. Change `scrape_source()`'s signature to accept the two keyword lists:
   `def scrape_source(source: dict, priority_keywords: list, keywords: list) -> dict:` and
   replace line 30 (`text = text[:8000]`) with
   `text = smart_truncate(text, priority_keywords, keywords)`.
3. Change `scrape_all()`'s signature to `def scrape_all(sources: list, priority_keywords:
   list, keywords: list) -> list:` and pass both through to each `scrape_source(source,
   priority_keywords, keywords)` call.
4. Update the one call site in `main.py` (`scraped = scrape_all(country["sources"])` at line
   51) to `scraped = scrape_all(country["sources"], country["priority_keywords"],
   country["keywords"])`.
5. The `max_chars=6000` default (down from the old blind 8000) is intentional — smart
   truncation should already be denser/more relevant per character, so a slightly smaller
   budget keeps token cost down without losing signal. Do not tune this number further without
   a live run to measure against; leave it at 6000 and note in a comment why
   (`# lower than the old 8000 — content is now keyword-dense, not blindly cut`).

**Why this depends on Step 2, not just shares its keyword lists:** Step 2 is what defines
`priority_keywords`/`keywords` as two distinct, tiered lists in `config/sources.py` in the
first place. Do Step 2 first so Step 3 has the right lists to import, not the old flat one.

**Success criterion:** `scrape_source`/`scrape_all` take and use the keyword lists;
`smart_truncate` exists and falls back gracefully to a blind cut when no keywords match (so it
never returns an empty string for a source that genuinely has no relevant content — that's
correct behavior, the filter step downstream will drop it); `main.py`'s call site updated.
Verify by manually testing `smart_truncate` against 2-3 sample strings (a single long
paragraph with one keyword early and one late, confirming both surrounding windows are kept;
a string with zero keyword hits, confirming the blind-cut fallback fires).

---

## Step 4: Source Expansion + Scraper Fixes (merged pass)

**File:** `config/sources.py`

**This step depends on Steps 2 and 3 being complete** — new and previously-broken sources must
be dry-run-scraped using the *new* filter/truncation logic, not the old blind-cut behavior,
otherwise the verification done here would need to be redone once Steps 2/3 land.

### 4a. Fix already-known null-returning sources

Three sources are currently `active: False` with documented reasons (lines 21, 35, 44 of
`config/sources.py`):
- **SGTech** (`https://www.sgtech.org.sg/`) — ASP.NET site, news pages return 404.
- **CPG Consultant** (`https://cpgcorp.com.sg/`) — no dedicated newsroom page found.
- **FacilityBot** (`https://facilitybot.co/`) — `/blog` path returns 404, homepage only.

Also fix the **Construction Plus Asia SSL certificate verification error** mentioned in
`STATE.md`'s "What's Next" list (item 5) — investigate why `requests.get()` fails SSL
verification for `https://www.constructionplusasia.com/sg/category/news-and-events/` and
either find a working URL/fix the verification issue, or document why it can't be fixed and
leave it `active: False` with a reason comment matching the existing pattern.

For each of these four: attempt to find a working press/newsroom URL (search the site's
structure, try `/news`, `/press`, `/media`, `/insights` paths, or a sitemap if one exists). If
a working URL is found, flip `active: True` and update the `url` field. If still no working
URL exists after a genuine attempt, leave `active: False` and update the reason comment to
reflect what was tried (don't leave the old comment if it's now inaccurate).

### 4b. Add new sources from the supervisor's full ecosystem list

The supervisor's source-list PDF was cross-referenced against the current `config/sources.py`
to remove duplicates. The table below is the **final, deduplicated, sector-mapped list of new
sources to add** — no further judgment calls needed on sector placement; that decision is
already made:

**New `gov_agencies` sources:**
| Name | URL (from PDF — verify/find real press page before activating) |
|---|---|
| Enterprise Singapore | `https://www.enterprisesg.gov.sg/` |
| SLA (Singapore Land Authority) | `https://www.sla.gov.sg/` |
| GovTech | `https://www.tech.gov.sg/` |

**New `associations` sources:**
| Name | URL |
|---|---|
| BCA Academy | `https://www.bcai.com.sg/` |
| SIFMA Singapore | `https://sifma.org.sg/` |
| NTUC | `https://www.ntuc.org.sg/` |

**New `partners` sources** (main contractors, consultants, M&E/BMS integrators, facility
management — per Step 1's "Ecosystem Players" section, all four categories map to the existing
`partners` sector, consistent with how AECOM/Honeywell/Cushman & Wakefield are already
classified):
| Name | URL |
|---|---|
| MCC | `https://www.mcc.sg/` |
| CSCEC | `https://en.chinaconstruction.cscec.com/` (or `https://cscecsingapore.cscec.com/` if the Singapore-specific site has a better newsroom — check both) |
| CCCC | `https://www.ccccltd.cn/` |
| CHEC | `https://www.chec.bj.cn/` |
| Sembcorp | `https://www.sembcorp.com/` |
| SJ Group | `https://www.sjgroup.com/` |
| Meinhardt Group | `https://meinhardtgroup.com/` |
| BECA | `https://www.beca.com/en-sg` |
| Ramboll | `https://www.ramboll.com/` |
| Azbil | `https://www.azbil.com` |
| Johnson Controls | `https://www.johnsoncontrols.com/` |
| Schneider Electric | `https://www.se.com/ww/en/` |
| Quantum Automation | `https://qa.com.sg/` |
| ST Synthesis (ST Engineering) | `https://www.stengg.com/` |
| Savills | `https://www.savills.com.sg/` |

**New `competitors` sources** (TwinMatrix re-added per Alfonso's explicit 2026-06-26
decision, superseding the 2026-06-23 "dropped" call — note this supersession in the commit/
`CONTEXT.md` entry per the "Ending a Session" instructions):
| Name | URL |
|---|---|
| TwinMatrix | `https://www.twinmatrix.net/` |
| Minuscule Technologies | `https://www.minusculetechnologies.com/` |
| Alstern Technologies | `https://alstern-technologies.com/` |
| Aperio | `https://aperio.ai/` |
| Nuvola Media | `https://www.nuvolamedia.com/` |
| SSI Corporate | `https://www.ssi-corporate.com/` |
| NeuronCloud | `https://www.neuroncloud.ai/` |

**New `general_news` source:**
| Name | URL |
|---|---|
| Straits Times Property | `https://www.straitstimes.com/property` |

**Explicitly NOT added this round** (deferred, do not add): CNA Singapore, Business Times
general site (the Property section is already present as a source), Zaobao. These were
researched and judged too noisy or low-priority for the added token cost relative to the
already-present Business Times Property and EdgeProp sources. LinkedIn and Facebook URLs for
any source (re-requested in the supervisor's PDF) remain out of scope — no free, no-auth
scraping method exists, per the Phase 1 decision already logged in `CONTEXT.md`.

### What "verified" means for every new/fixed source in this step

For each source in the tables above:
1. Add it to `config/sources.py` with `active: True` and the URL from the table (or a better
   URL you found while checking for a real news/press page — homepages are a last resort).
2. Dry-run scrape it: call `scrape_source()` directly (with Step 2/3's keyword lists) in a
   throwaway script or Python shell — do not run the full `main.py` pipeline to do this, that
   would burn quota on the Groq analyst step too. Confirm `result["error"]` is `None` and
   `result["content"]` is non-empty and looks like actual news/press content, not a generic
   homepage shell or a 404 page rendered as 200.
3. If it fails (error, empty, or junk content), try 1-2 alternate URL paths (`/news`,
   `/press-releases`, `/media`, `/insights`, `/about/news`) before giving up.
4. If still failing after a genuine attempt, set `active: False` and add a one-line comment
   explaining what was tried and why it failed — matching the existing pattern exactly
   (`# ASP.NET site, news pages return 404` style).

**Success criterion:** every source from the tables above exists in `config/sources.py` under
the correct sector, each either verified scrapable (`active: True`, confirmed non-empty
real content) or explicitly marked broken with a reason (`active: False` + comment). No
duplicate URLs across the file. `CONTEXT.md` gets a new dated entry recording the TwinMatrix
and Chinese-contractor supersessions (see "Ending a Session" section at the bottom of this
doc).

---

## Step 5: Metrics & Scores Glossary

**Files:** `templates/report.html`, `templates/internals.html`

**Current state:** Both pages already render real computed metrics with no explanation
anywhere:
- `report.html` lines 144-191 (and the duplicated collapsed-row block, lines ~202-244): each
  opportunity's `total_score` (0-25) and its five sub-scores (`scores.strategic_fit`,
  `revenue_potential`, `win_probability`, `urgency`, `intelligence_quality`, each 0-5),
  rendered as colored bars (green ≥4, amber ≥2, gray below).
- `report.html` hero stat cards (lines 47-64): Total Signals, Opportunities Found, Top Score,
  Sectors Covered — these are simple counts/maxes, self-explanatory, do not need glossary
  entries.
- `internals.html`: source quality scores from `pipeline/scoring.py` — `BASELINE_SCORE = 5.0`,
  `+2.0` per citation in a report, `-0.5` decay per run a source goes uncited. Confirm the
  exact rendering location in `internals.html` before writing copy (read the file; the prior
  code-review pass confirmed these scores are rendered there but did not give exact line
  numbers — find them yourself, do not guess the markup structure).

**What to build:**

1. A small glossary/legend component — a `.glass-card`-styled (on the dark hero, if placed
   there) or `.shadow-soft`-styled (if placed in the light body) collapsible panel, consistent
   with the existing design system from Phase 3.5. Reuse existing CSS classes
   (`.shadow-soft`, `.card-hover`) — do not invent new styling, per the hard constraint above.
2. Content for the opportunity scoring legend (place near the Opportunities section in
   `report.html`, e.g. a small "What do these scores mean?" expandable note above or below the
   section heading):
   - **Strategic Fit (0-5):** how directly the opportunity matches a SpatioX product capability.
   - **Revenue Potential (0-5):** estimated deal size / business value if pursued.
   - **Win Probability (0-5):** how likely Silversea is to win this specific opportunity given
     known relationships/competition.
   - **Urgency (0-5):** how time-sensitive the opportunity is (deadline proximity, competitive
     pressure).
   - **Intelligence Quality (0-5):** how well-grounded/specific the underlying signal is (named
     entities, dates, amounts vs. vague mentions).
   - **Total Score (0-25):** sum of the five sub-scores. 20-25 = High, 13-19 = Medium, 0-12 =
     Low (this banding already exists in the prompt's `SYNTHESIS_PROMPT`, lines 100 of
     `pipeline/analyst.py` — reuse the exact thresholds, don't invent new ones).
3. Content for the source quality score legend (place near wherever `internals.html` renders
   per-source scores):
   - **Source Quality Score:** starts at 5.0 for every new source. +2.0 each time a report
     cites that source; -0.5 each run it's scraped but not cited. Higher scores indicate
     sources that consistently produce report-worthy signal.
4. **Required caveat, verbatim or close to it, near the opportunity scoring legend**: *"Note:
   the relevance gate and sector-categorization logic that produces these scores had two known
   issues as of 2026-06-24 (see STATE.md) — a fix has been applied but not yet verified with a
   live run. Scores reflect the analyst's intended scoring rubric; treat current live output
   as provisional until the next verified run."* This caveat must be removed (by Alfonso or a
   future session) once Step 8's fix is confirmed working on a live run — do not remove it
   yourself in this phase, since you cannot run the verification.

**Success criterion:** every score/metric visible on both pages has an accessible explanation
reachable from the page itself (not just in this doc); the opportunity-scoring legend carries
the required provisional-output caveat; no existing visual design tokens were modified to
build this, only reused.

---

## Step 6: Feedback Digest Consolidation

**Files:** new logic, modeled on `pipeline/weekly.py` — decide whether to add this as a new
function in `pipeline/feedback.py` or a new small module `pipeline/feedback_consolidation.py`
(prefer extending `pipeline/feedback.py` unless the function count there gets unwieldy — use
your judgment, this is a minor structural call, not a locked decision).

**Why this step exists, precisely:** `pipeline/feedback.py`'s existing `aggregate_feedback()`
already does correct single-batch condensing (reads pending feedback JSON files, makes one
LLM call, stores one digest, moves files to `processed/`) — this is NOT broken and should not
be changed. The actual problem is one level up: every time `aggregate_feedback()` runs, it
adds **one more permanent entry** to the `feedback_digests` ChromaDB collection via
`add_documents()` (line 63-70 of `feedback.py`) — there is no mechanism that ever merges,
expires, or prunes old digests. Over weeks/months, this collection grows without bound. The
per-call token cost to the analyst stays capped (`pipeline/analyst.py`'s `_build_rag_context`,
line 174, always queries with `n_results=3`), but retrieval quality degrades as the collection
fills with old, increasingly redundant digests that may rank similarly to fresher ones in
semantic search.

**What to build**, directly modeled on `pipeline/weekly.py`'s `generate_weekly_summary()`
pattern (read that file in full before writing this — it already solves an equivalent problem
for `REPORT_HISTORY`):

1. A new function, e.g. `consolidate_feedback_digests(max_digests: int = 10) -> None` in
   `pipeline/feedback.py`:
   - Get the `FEEDBACK_DIGESTS` collection via `get_collection()`.
   - If `collection.count() <= max_digests`, return immediately — nothing to consolidate.
   - Otherwise, retrieve all digests (`collection.get(include=["documents", "metadatas"])`),
     sort by date metadata (oldest first — reuse the `date` metadata field already written by
     `aggregate_feedback()`).
   - Take the oldest `(count - max_digests + 1)` digests (i.e., consolidate just enough to get
     back under the cap, keeping the most recent `max_digests - 1` digests untouched).
   - Make **one** Groq call (model `"llama-3.3-70b-versatile"`, same as the rest of the
     codebase) with a new prompt — call it `CONSOLIDATION_PROMPT` — that compresses those N
     old digests into a single consolidated digest, in the same spirit as
     `pipeline/weekly.py`'s `WEEKLY_PROMPT`: *"Compress these {count} feedback digests into ONE
     consolidated priority summary. Preserve any recurring themes, drop one-off or
     superseded requests. Output 4-6 bullets, no preamble."*
   - `delete_documents(FEEDBACK_DIGESTS, old_ids)` for the consolidated-away digests, then
     `add_documents(FEEDBACK_DIGESTS, [consolidated_text], metadatas=[{"date":
     today.isoformat(), "type": "consolidated", "source_count": str(len(old_ids))}])` — mirror
     `weekly.py`'s delete-then-replace pattern exactly.
2. Call this function from `main.py`, right after the existing `aggregate_feedback()` call at
   line 45 (`aggregate_feedback()` then `consolidate_feedback_digests()` on the next line) —
   so consolidation is checked every pipeline run, but only actually does work (and burns a
   Groq call) once the cap is exceeded.
3. `max_digests=10` is a placeholder constant, same caveat as Step 2/3's tuning constants —
   comment it as such (`# placeholder cap, untuned — revisit with real usage data`).

**This cannot be tested with a live run this phase** (no Groq calls allowed) — verify by
reading the logic against `pipeline/weekly.py`'s proven pattern and confirming the function is
correctly wired into `main.py`. Do not mark this "verified," mark it "implemented, mirrors the
proven weekly-summary pattern, untested against live data."

**Success criterion:** the function exists, is called from `main.py` after
`aggregate_feedback()`, never fires unless the digest count actually exceeds the cap, and
follows the exact delete-then-replace pattern already proven in `pipeline/weekly.py`.

---

## Step 7: Model Research (subagent-driven, no live calls)

**Output:** a new file, `data/model_research.md` (or similar — this is new content, no
existing file to extend).

**Hard rule, repeated because it's the one most likely to be silently violated:** this step
makes **zero** live API calls to any LLM provider, paid or free, during this research. If you
find published benchmark/pricing documentation insufficient to compare models, **stop and
report that gap in the output document** — do not "just check with one quick call" to fill the
gap. There is no quota available to spend on this, and a $0.10/day cap is explicitly described
as tentative, not currently approved for active spend.

**What to research and report**, comparing at minimum: Groq's other available models (e.g.
any Llama variants, Mixtral, or other models Groq's free tier offers beyond
`llama-3.3-70b-versatile`), Claude Haiku 3.5 (already the production candidate per
`CONTEXT.md`'s prior decision), and any other realistic candidate (e.g. another free-tier
provider) — using only published pricing pages, documentation, and benchmark results:

1. **Cost** — per-token pricing (input/output separately if it differs), and a rough estimate
   of daily cost at this pipeline's current scale (multi-pass analyst: ~6 calls/run, one run/
   day, growing source count per Step 4 — estimate token volume from the existing
   `MIN_CONTENT_CHARS`/`max_tokens` constants already in `pipeline/analyst.py` rather than
   guessing from scratch).
2. **Quality for this specific task** — structured JSON extraction + summarization +
   relevance-gating reasoning (not generic chatbot quality). Cite published benchmarks where
   available (e.g. instruction-following, JSON-mode reliability) rather than general
   leaderboard rank.
3. **Token efficiency** — context window size, whether the model supports a native JSON-mode
   response format (Groq's `llama-3.3-70b-versatile` already uses
   `response_format={"type": "json_object"}` per `pipeline/analyst.py` line 267 — confirm
   whether each candidate supports an equivalent mode).
4. **Practical constraints** — rate limits (TPM/TPD) on the free tier of each candidate, since
   the current Groq 12k TPM / 100k TPD limit is the proximate cause of this entire planning
   exercise.

**Format the output as a comparison table plus a short written recommendation** — which model
to use as a near-term free-tier choice (if different from current Groq), and which to use once
the tentative $0.10/day budget is actually approved. Explicitly flag any place where published
information was insufficient and a real test would be needed (without recommending that test
happen without Alfonso's go-ahead and a confirmed budget).

**Success criterion:** `data/model_research.md` exists with the comparison and recommendation;
zero API calls were made to produce it; any information gaps are explicitly flagged rather than
filled by guessing or testing.

---

## Step 8: Fix the Two Known `SYNTHESIS_PROMPT` Bugs — LAST, UNVERIFIED

**File:** `pipeline/analyst.py` (the `SYNTHESIS_PROMPT` string, lines 48-155)

**Run this step only after Steps 1-6 are committed and stable.** This is the single
highest-risk item in this phase per two rounds of plan review: editing a ~150-line prose
prompt that controls a 70B model's behavior, with zero ability to test it against a live call
this phase, carries real risk of either not fixing the bug or overcorrecting into a worse
regression (e.g. reintroducing the kind of fabricated opportunities the grounding rules were
written to prevent — see `CONTEXT.md`'s 2026-06-19 entry: it took 3 iterations to get this
prompt from 13/25 to 21/25 quality).

### 8.1 — Bug 1: Empty opportunities (overly strict relevance gate)

Current text, `SYNTHESIS_PROMPT` lines 83-85:
```
RELEVANCE GATE: Does the signal explicitly mention digital twin, BIM, 3D scanning,
XR/spatial computing, smart FM, smart building, building automation, or proptech?
If the connection to Silversea's products is inferred, it is NOT an opportunity.
```
This produced zero opportunities on the last real run — the gate is correctly strict per its
own design intent ("Zero opportunities is a correct output when nothing passes the gate," line
95), but a BD-facing report with zero opportunities every run is not useful even when
technically correct. The fix is to widen the gate slightly without removing the
anti-fabrication grounding rule it's paired with:

Change the gate text to:
```
RELEVANCE GATE: Does the signal explicitly mention digital twin, BIM, 3D scanning,
XR/spatial computing, smart FM, smart building, building automation, proptech, OR involve
a named entity from Silversea's tracked ecosystem (a customer, partner, competitor, or
government agency listed in the company context) taking an action relevant to the built
environment sector (a tender, partnership, project announcement, or facility initiative)?
If the connection to Silversea's products is inferred rather than stated or reasonably implied
by a tracked entity's documented action, it is NOT an opportunity.
```
This keeps the anti-fabrication rule (no inferred connections) but adds a second, narrower
path to passing the gate — a tracked entity doing something built-environment-relevant, even
if the text doesn't use one of the exact technical keywords. Do not weaken the gate further
than this; do not remove the "if inferred, NOT an opportunity" sentence.

### 8.2 — Bug 2: Sector mis-categorization

Current behavior: sources configured under `competitors` in `config/sources.py` (e.g. G
Element, DataMesh) had their signals duplicated into the `Partners` bucket of
`signals_by_sector` in the synthesis output. Root cause per `STATE.md`: the LLM appears to
bucket by semantic content of the sentence (a sentence describing a partnership reads as
"Partners-shaped") rather than by the source's actual configured sector.

The synthesis prompt currently has no instruction tying sector buckets to the *input* sector
labels at all — `SECTOR_LABELS` (lines 18-25 of `analyst.py`) are used to *label* the
extraction sections (`=== {label.upper()} ===` in `_extract_sector`, line 249), but the
synthesis prompt's SIGNALS BY SECTOR instructions (lines 69-79) never tell the model to keep a
signal in the sector section it was extracted under, regardless of what the signal's *content*
sounds like.

Add this sentence to the SIGNALS BY SECTOR section (insert after the existing line 69, "include
EVERY sector from the intelligence below"):
```
CRITICAL: Each signal belongs ONLY to the sector section its source content was extracted
under (the === SECTOR NAME === headers in the intelligence below) — never duplicate a signal
into a different sector bucket because its content sounds like it belongs elsewhere. A
signal from a source extracted under "Competitors" stays under "Competitors" even if it
describes that competitor's partnership with someone else.
```

### 8.3 — Mark as unverified, not done

After making both edits, you must do all of the following — skipping any of these is not
acceptable:
1. Add a dated entry to `CONTEXT.md`'s decision log describing both prompt changes exactly as
   made (quote the before/after text, same level of detail as this doc).
2. Update `STATE.md`'s "Known Bugs" section: change both bug entries from "unresolved" to
   "fix applied 2026-XX-XX in `analyst.py`'s `SYNTHESIS_PROMPT` — **unverified**, requires a
   live Groq run to confirm. See Phase 4 handoff Step 8." Do not delete the bug descriptions —
   downgrade their status, keep the detail.
3. Update `STATE.md`'s "What's Next" list: the **first** item must become "Run `py main.py
   --no-email` once Groq quota is confirmed fresh, to verify Step 8's two prompt fixes AND
   check whether the larger source count from Step 4 has pushed any per-sector extraction call
   (`_extract_sector` in `analyst.py`) over Groq's 12k TPM limit — Step 4 added roughly 29 new
   sources across `gov_agencies`, `associations`, `partners`, `competitors`, and
   `general_news`, several of which now have meaningfully more sources per sector than when
   the multi-pass architecture was last tuned (see `CONTEXT.md`'s 2026-06-23 multi-pass
   architecture entry)." This is a real, plan-review-identified risk, not boilerplate —
   the per-sector batching that keeps each Groq call under budget was sized against the old
   source count, and Step 4 changed that count materially.

**Success criterion:** both prompt edits are made exactly as specified; `CONTEXT.md` and
`STATE.md` are updated per 8.3; nothing in this step is described as "done" or "fixed" without
the "unverified, pending live run" qualifier attached everywhere it's mentioned.

---

## Verification Checklist (run through this before considering the phase complete)

- [ ] `data/company_context.md` has the new "Ecosystem Players" section, expanded competitor
      list, BD-priority note, and the pending-review HTML comment at the top.
- [ ] `pipeline/filter.py` and `config/sources.py` implement the two-tier weighted keyword
      scoring; `main.py`'s `filter_results` call site updated; manually verified against 3-4
      example strings.
- [ ] `pipeline/scraper.py` has `smart_truncate()`, both `scrape_source`/`scrape_all` signatures
      updated, `main.py`'s `scrape_all` call site updated; manually verified fallback behavior.
- [ ] `config/sources.py` contains every new source from Step 4's tables, correctly sectored,
      each either `active: True` with confirmed-working content or `active: False` with an
      accurate reason comment. No duplicate URLs.
- [ ] `CONTEXT.md` has a dated entry recording the TwinMatrix re-add and Chinese-contractor
      inclusion, superseding the 2026-06-23 decisions.
- [ ] Glossary/legend exists and renders on both `report.html` and `internals.html`, using only
      existing design tokens, with the required provisional-output caveat near the opportunity
      scoring legend.
- [ ] `consolidate_feedback_digests()` exists, is wired into `main.py` after
      `aggregate_feedback()`, follows the `weekly.py` delete-then-replace pattern, and is
      documented as implemented-but-untested.
- [ ] `data/model_research.md` exists, contains a comparison table and recommendation, and
      made zero live API calls.
- [ ] Both `SYNTHESIS_PROMPT` edits are made exactly as specified in Step 8; `CONTEXT.md` and
      `STATE.md` both reflect the unverified status and the required first-action-next-session
      note about per-sector token budget risk.
- [ ] `python`/`py app.py` still starts without errors and `localhost:5000/` and
      `/internals` still render correctly with no console errors — this confirms none of the
      template/glossary changes broke anything, even though the underlying report data is
      unchanged (still the old `latest_report.json` from before this phase, since no pipeline
      run happened).
- [ ] No file outside this phase's named targets was modified. No `py main.py` run occurred at
      any point in this phase.

## Ending This Phase (per `CLAUDE.md`'s session protocol)

When this phase's work is complete:
1. Update `STATE.md` with what was completed, the unverified status of Step 8, and the
   next-session-first-action note from Step 8.3.
2. `CONTEXT.md` gets the Step 8 prompt-change entry and the Step 4 source-list-supersession
   entry (both described above) — these are real architectural/scope decisions, not noise.
3. `PLAN.md` gets overwritten for whatever phase comes next (likely: the live verification run
   once Groq quota resets, plus Alfonso's review of Step 1's draft company context).
