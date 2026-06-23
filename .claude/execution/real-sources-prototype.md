# Real Sources + AI System Finalization — Execution Guide

Read `CLAUDE.md` first (auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`).
This file is the complete plan — almost no re-derivation should be needed. If something here
conflicts with the current codebase, trust the codebase and flag the conflict before proceeding.

**Deadline context:** This is being finalized for a manager presentation. Work top-to-bottom;
each session has a hard verify step before moving on. Do not skip verification to save time —
an unverified change is worse than no change at this point.

---

## The Two Things That Must Be True When This Is Done

1. **Sources scrape correctly and relevant info gets reported.** The pipeline pulls real content
   from real Silversea ecosystem companies (not placeholders), filters it sensibly, and the
   generated report contains accurate, sector-organized signals — no fabricated facts, no
   wrong product names.
2. **The RAG/feedback loop demonstrably changes the output.** Not just "the code runs" — a
   specific, named difference must exist between a report generated with no feedback context
   and one generated after a real feedback digest is in the vector store.

---

## Session Map

```
Session 1 (branding fix)  ──────────────┐
                                          ├──→ Session 4 (dry-run scrape verify)
Session 2 (URL research — subagent) ────┤
                                          │
Session 3 (config + keyword update) ─────┘
                                          │
                                          ▼
                              Session 5 (clear test ChromaDB/feedback data)
                                          │
                                          ▼
                              Session 6 (baseline run, no feedback)
                                          │
                                          ▼
                              Session 7 (inject real feedback → aggregate)
                                          │
                                          ▼
                              Session 8 (second run → diff against baseline)
```

Sessions 1, 2, 3 can happen in any order but all must finish before Session 4.
Sessions 5–8 are strictly sequential — each depends on the previous step's output.

---

## Session 1: Fix Product Branding Bug

**Goal:** `pipeline/analyst.py`'s SYSTEM_PROMPT currently describes Silversea's products as
"MetaTwin Object/Space/Immerse/Augment" — this is wrong and will show up directly in the
report. The real products (per supervisor's company profile doc) are:

- **SpatioX Twin** — Digital Twin platform, live dashboard, high-fidelity 3D visualization
- **SpatioX Ops** — Smart Facility Management: workflow/asset management, IoT/CCTV/access
  control integration
- **SpatioX Audit** — Smart virtual inspection (property TOP inspection)
- **SpatioX Walk** — 3D/VR virtual tour, WebGL virtual walkthrough

**File:** `pipeline/analyst.py` — SYSTEM_PROMPT only.

**Changes:**
- Replace the "Company context" bullet list (products line) with the four SpatioX products
  above, each with a one-line description so the LLM can match opportunities to the right
  product.
- Update the RELEVANCE GATE section — it currently lists "digital twin, BIM, 3D scanning,
  XR/spatial computing, smart FM, smart building, building automation, proptech" — this list
  is still accurate, just make sure "Product fit" instructions reference SpatioX names, not
  MetaTwin.
- Update the NEGATIVE EXAMPLE section if it references MetaTwin by name (check first).

**Do NOT change:** grounding rules, quote-before-extract requirement, scoring rubric (Strategic
Fit / Revenue Potential / Win Probability / Urgency / Intelligence Quality), report section
structure, abstain-token behavior. Those are locked decisions from Phase 1 (see CONTEXT.md).

**Verify:** `grep -i metatwin pipeline/analyst.py` returns nothing. `grep -i spatiox
pipeline/analyst.py` returns the four product names.

---

## Session 2: Research Real Newsroom URLs (sub-agent candidate)

**Goal:** Find the actual press/news/media page for each of the 10 new sources below — not
their homepage. This is the same kind of work Phase 1 already did for the current 20 sources.

**New sources to research** (homepage URLs are known from the supervisor's source doc; find
the actual newsroom/press/blog path for each):

| Name | Sector | Homepage (starting point) |
|---|---|---|
| IMDA | gov_agencies | https://www.imda.gov.sg/ |
| SGTech | associations | https://www.sgtech.org.sg/ |
| REDAS | associations | https://redas.com/ |
| Keppel | customers | https://www.keppel.com/ |
| AECOM | partners | https://aecom.com/ |
| CPG Consultant | partners | https://cpgcorp.com.sg/ |
| Honeywell | partners | https://www.honeywell.com/us/en |
| Cushman & Wakefield | partners | https://www.cushmanwakefield.com/en/singapore/services/facilities-services |
| FacilityBot | competitors | https://facilitybot.co/ |
| Cryotos | competitors | https://www.cryotos.com/ |

**Why a sub-agent:** 10 sources × web research each would flood the main session's context
with search results and intermediate page fetches that aren't needed afterward — only the
final URL list matters downstream. Use the **orchestrator skill** (`/orchestrate`) to confirm
this is worth delegating (it almost certainly is, given Phase 1 made the same call for a
similar task), then **prompt-engineer skill** (`/prompt-engineer`) to draft the sub-agent
prompt. Spawn with `subagent_type: general-purpose` (needs WebFetch/WebSearch).

**Sub-agent deliverable:** A structured list, one line per source:
`name | sector | newsroom_url | notes (anti-bot risk, JS-rendered, language, etc.)`

If a clean newsroom/press path can't be found for a source, the sub-agent should return the
homepage anyway with a note — don't block on it. Mark such sources `active: False` in Session 3
rather than guessing a URL that doesn't exist.

**Do NOT** have the sub-agent edit any files — research only, returns text.

---

## Session 3: Update Source Config

**Goal:** Add the 10 new sources (using Session 2's URLs) into `config/sources.py`, plus
verify the existing 14 already-active sources are still correctly mapped. Final active set
should be ~24 sources across the 5 existing sectors (`gov_agencies`, `associations`,
`customers`, `partners`, `competitors` — no new sectors).

**Sector assignments (already decided, don't re-litigate):**
- **gov_agencies**: BCA, URA, HDB, JTC, MND (existing) + IMDA (new)
- **associations**: SGBC (existing) + SGTech, REDAS (new)
- **customers**: CapitaLand, Mapletree, Lendlease (existing) + Keppel (new)
- **partners**: currently empty/placeholder — replace with AECOM, CPG Consultant, Honeywell,
  Cushman & Wakefield (all new). Remove the `"Partners TBD"` placeholder entry entirely.
- **competitors**: Hiverlab, G Element, TwinLogic, Axomem, DataMesh (existing, keep) +
  FacilityBot, Cryotos (new). **Drop TwinMatrix** — lower BD priority than the two new entries.

**Explicitly out of scope for this round** (do not add): GeBIZ, Smart Nation/GovTech, BCI Asia,
Construction Plus Asia, NUS/NTU/SGH, CSCEC/CCCC/CHEC, any LinkedIn/Facebook source. These stay
candidates for the post-presentation full rollout — leave existing ones as-is if already in
the file, just don't expand them.

**Format for each new entry** (matches existing convention):
```python
{"name": "IMDA", "url": "<from session 2>", "sector": "gov_agencies", "type": "website", "active": True},
```
If Session 2 couldn't find a clean newsroom URL for a source, set `"active": False` and add a
trailing comment noting why.

**Keyword review:** The `keywords` list in `config/sources.py` is digital-twin/smart-FM/contech
focused. The new `partners` sector sources (AECOM, CPG, Honeywell, C&W) publish in different
vocabulary — project delivery, BMS, asset management. Add these terms to the keyword list so
their relevant content isn't filtered out before reaching the analyst:
`"M&E integration", "BMS", "building automation system", "asset management system",
"consultancy", "facilities consultancy"`. Keep all existing keywords — this is additive only.

**File:** `config/sources.py` only.

**Verify:**
```
python -c "from config.sources import COUNTRIES; c = COUNTRIES[0]; print(len([s for s in c['sources'] if s['active']]))"
```
Should print approximately 24. Then:
```
python -c "from config.sources import COUNTRIES; c = COUNTRIES[0]; print(set(s['sector'] for s in c['sources'] if s['active']))"
```
Should print exactly the 5 sectors — no new sector names introduced.

---

## Session 4: Dry-Run Scrape Verification (no LLM calls)

**Goal:** Confirm every active source actually returns usable content before spending LLM
calls on it. This catches anti-bot blocks, dead URLs, and JS-rendered pages that return empty
HTML — the same failure mode that hit Construction Plus Asia (SSL error) in Phase 1.

**How:** Write a small throwaway check (don't commit a permanent script unless useful) that
calls `pipeline.scraper.scrape_all()` on the active SG source list and `pipeline.filter.filter_results()`,
then prints per-source: name, sector, content length, error (if any), and whether it passed
the keyword filter. Something like:
```python
from config.sources import COUNTRIES
from pipeline.scraper import scrape_all
from pipeline.filter import filter_results

country = COUNTRIES[0]
scraped = scrape_all(country["sources"])
filtered = filter_results(scraped, country["keywords"])
for r in scraped:
    print(r["name"], r["sector"], len(r["content"]), r["error"])
```

**What to look for:**
- Any source returning 0 content length with no error → likely JS-rendered or blocked, mark
  `active: False` in `config/sources.py` and note why.
- Any source returning content but 0 keyword matches → check manually whether the page is
  just not a news/press page (wrong URL found in Session 2) vs. genuinely no current news.
- At minimum, gov_agencies and customers sectors should have multiple sources passing filter
  — these are the highest-confidence categories. If they're empty, something's wrong upstream
  (wrong URL or keyword list too narrow), not just "no news this week."

**Fix loop:** If 2+ sources fail, go back to Session 2/3 and fix URLs or keywords before
proceeding — don't carry broken sources into the full pipeline run.

**Verify (done when):** Console output shows every active source attempted, most returning
non-trivial content (a few hundred+ chars), and the filter breakdown shows hits across at
least 3 of the 5 sectors.

---

## Session 5: Clear Experimental ChromaDB / Feedback Data

**Goal:** All existing data in `feedback_digests` and `report_history` ChromaDB collections is
from Phase 2 testing — not real team feedback. Clear it so Session 8's feedback-loop demo
starts from a clean baseline and the diff is attributable to the real feedback you inject in
Session 7, not leftover test data.

**Do NOT clear `company_context`** — that's the real seeded company profile document and
should stay.

**How:** There's no bulk-clear helper in `pipeline/vectorstore.py` yet — add one if needed, or
delete and recreate the two collections directly via the ChromaDB client:
```python
from pipeline.vectorstore import get_client, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
client = get_client()
client.delete_collection(REPORT_HISTORY)
client.delete_collection(FEEDBACK_DIGESTS)
```
(`get_or_create_collection` in `get_collection()` will recreate them empty on next use.)

Also clear `data/feedback/processed/*.json` (old test submissions) — leave the directory
structure intact. Do not touch `data/source_scores.json` unless it's also full of test-only
data from sources no longer in the active list (use judgment — stale entries for removed
sources are harmless, just noise).

**Verify:**
```python
from pipeline.vectorstore import query, REPORT_HISTORY, FEEDBACK_DIGESTS
print(query(REPORT_HISTORY, "test", n_results=5))
print(query(FEEDBACK_DIGESTS, "test", n_results=5))
```
Both should return empty document lists.

---

## Session 6: Baseline Pipeline Run (No Feedback)

**Goal:** Run the full pipeline once with the new real sources and a clean feedback/report
history, producing a baseline report with no accumulated feedback context — system prompt +
RAG company-context only.

**Run:** `py main.py --no-email`

**Capture:** Copy the resulting `output/index.html` (or the raw `report_text`) to a clearly
labeled location, e.g. `output/baseline_no_feedback.html`, so Session 8 can diff against it.
Don't overwrite this file in later sessions.

**Verify:** Pipeline completes without errors. Report has signals from multiple sectors,
correctly cites SpatioX products (not MetaTwin), and the Opportunities section follows the
grounding rules (quoted source text, no fabricated deadlines).

---

## Session 7: Inject Real Feedback Signal

**Goal:** Submit one deliberate, falsifiable feedback signal via the existing feedback
mechanism, then run aggregation so it lands in the `feedback_digests` collection.

**How to submit:** Either run `scripts/feedback_server.py` and POST to it, or write the JSON
submission file directly into `data/feedback/` matching the schema `pipeline/feedback.py`
expects (`relevance_rating`, `most_useful`, `missed_topics`, `priority_changes`, optional name).

**Suggested feedback content** (pick one specific, checkable instruction — don't soften it):
> "We care more about smart facility management (SpatioX Ops) opportunities than digital twin
> visualization ones. Deprioritize competitor-only updates that don't include a concrete
> opportunity for Silversea."

**Run aggregation:** `python -c "from pipeline.feedback import aggregate_feedback; aggregate_feedback()"`

**Verify:**
```python
from pipeline.vectorstore import query, FEEDBACK_DIGESTS
print(query(FEEDBACK_DIGESTS, "facility management", n_results=3))
```
Should return the digest text summarizing the injected feedback. Confirm
`data/feedback/processed/` now contains the moved submission file.

---

## Session 8: Second Run + Diff Against Baseline

**Goal:** Prove the feedback loop measurably changes output — this is the deliverable for
priority #2.

**Run:** `py main.py --no-email` again (same or refreshed source content is fine — the point
is the feedback context, not new scraped content).

**Diff against Session 6's baseline:**
- Does the new report visibly weight FM/SpatioX Ops opportunities higher (more detail, higher
  scores, or appears first) than digital-twin-only signals?
- Are competitor-only mentions without a concrete opportunity trimmed or deprioritized compared
  to the baseline?
- This diff is the actual demo artifact for tomorrow — keep both HTML files
  (`baseline_no_feedback.html` and the new run) side by side, don't discard the baseline.

**If the diff is weak or absent:** Don't fabricate a stronger demo. Instead check:
1. Is `RAG_ENABLED` true in `pipeline/analyst.py` (i.e. did `pipeline/vectorstore` import
   cleanly)?
2. Did `_build_rag_context()` actually retrieve the feedback digest (check via the query in
   Session 7 — was anything findable)?
3. Is the digest content specific enough for the embedding query to surface it, given the
   scraped content's actual keywords?

A real "the effect is subtle, here's why" is a more honest and more defensible presentation
artifact than a faked-looking dramatic before/after — note this explicitly if it's the case.

---

## Sub-Agent / Orchestrator Note

Only Session 2 (URL research) is a clear sub-agent candidate in this plan — it's the one task
that's research-heavy and would otherwise flood the main session with intermediate search
results that don't matter once the final URL list is in hand.

If, once underway, the next agent judges the overall scope here to be larger than expected
(e.g. many sources turn out to need deeper research, or Session 4's dry-run reveals widespread
failures requiring iteration), it should re-evaluate using the **orchestrator skill**
(`/orchestrate`) before defaulting to doing everything inline. Don't spawn sub-agents
reflexively — each one costs context/tokens to brief and re-synthesize. The bar is: would a
sub-agent's output be small and self-contained relative to the research/exploration it would
take to produce it? Session 2 clears that bar; most other sessions here (file edits, pipeline
runs, verification) don't.

---

## Phase Complete Checklist

- [ ] `pipeline/analyst.py` references SpatioX products, zero MetaTwin references
- [ ] `config/sources.py` has ~24 active sources across exactly 5 sectors, no placeholder URLs
- [ ] Dry-run scrape shows most active sources returning real content, failures documented
- [ ] `feedback_digests` and `report_history` collections cleared of test data; `company_context` untouched
- [ ] Baseline report generated and saved (`output/baseline_no_feedback.html` or equivalent)
- [ ] Real feedback submitted, aggregated, confirmed present in `feedback_digests`
- [ ] Second report generated and diffed against baseline — specific, named difference identified (or honestly documented as weak/absent with root cause)
- [ ] `py main.py --no-email` runs clean end-to-end with no errors

When all boxes are checked, run `/context-update` to refresh `STATE.md`, `CONTEXT.md`, and
`ROADMAP.md` with what was actually done (not just what was planned).
