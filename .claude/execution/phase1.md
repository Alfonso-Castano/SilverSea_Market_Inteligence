# Phase 1 Execution Guide

Read CLAUDE.md before starting any session (it auto-imports STATE.md, CONTEXT.md, ROADMAP.md, PLAN.md).
Read PROJECT_REQUIREMENTS.md for source lists, keywords, and system architecture.

---

## Session Map

```
Session 1 (analyst prompt)  ───────────────────┐
                                                ├──→ Session 3 (multi-sector scraper)
Session 2 (sector config + URL research)  ─────┘         │
                                                          ├──→ Session 3b (quality re-score)
Session 4 (LinkedIn research + impl)  ── independent      │
                                                          ▼
                                              Session 5 (daily cadence + report cleanup)
```

Sessions 1 and 2 can run in either order. Session 3 requires Session 2 complete.
Session 4 is independent — best after Session 2 so config has linkedin-type sources.
Session 5 goes last. Quality re-score runs after Session 3 (or after Session 4 if LinkedIn adds content).

---

## Session 1: Analyst Prompt Fix

**Orchestrator verdict:** Single session. One file, sequential edits, no research needed.

**Goal:** Fix the 3 quality issues diagnosed in `quality/reviews/2026-06-16.md`.

**File:** `pipeline/analyst.py` — only the `SYSTEM_PROMPT` string.

**Changes to SYSTEM_PROMPT:**
1. Add instruction: treat each named government programme as a distinct signal. Do not conflate
   programmes from the same agency (e.g. JTC LaunchPad vs JTC low-carbon are separate signals).
2. Rewrite the Opportunities section spec: every opportunity MUST include a named entry point
   (person, programme, or tender), a concrete action Silversea should take, a deadline or window,
   and a source citation. Scores without these are not acceptable.
3. Add noise filter: exclude signals with no direct path to Silversea's products or named
   prospects. Specifically exclude residential property market data, general economic indicators,
   and sector news that doesn't connect to digital twin / immersive tech / smart FM.

**Do NOT change:**
- The function `analyse()` — only the prompt text
- The model, API client setup, or message structure
- The scoring model dimensions (Strategic Fit, Revenue Potential, etc.) — those stay

**Verify:** `py main.py --no-email` — inspect the generated report in `output/index.html`.
Check: (a) opportunities cite specific programmes/actions, (b) no residential property noise,
(c) distinct programmes from the same agency are separate signals.

---

## Session 2: Sector-Based Config Redesign

**Orchestrator verdict:** Subagent for URL research, main session for config restructure.

The config restructure itself is straightforward. But finding correct newsroom/press-release
URLs for ~20 sources is web-search-heavy and would flood the main context with search results.

### Step 1: Spawn URL research sub-agent

Use `/orchestrate` to confirm the sub-agent strategy, then `/prompt-engineer` to craft the prompt.

The sub-agent's job:
- Take the source list from PROJECT_REQUIREMENTS.md (all sectors)
- For each source with a top-level URL (e.g. `https://www.capitaland.com`), web-search for
  the correct newsroom, press releases, or media page URL
- For sources marked "Monitor via news search" (some competitors), find their website and
  any news/blog page
- Return a structured list: `name | sector | url | notes`
- Do NOT edit any files — research only, return results as text

Sub-agent type: `general-purpose` (needs WebSearch).

### Step 2: Apply results to config/sources.py

After the sub-agent returns URLs, restructure `config/sources.py`:

**Current structure:**
```python
"sources": [
    {"name": "BCA", "url": "...", "type": "government"},
    ...
]
```

**Target structure:**
```python
"sources": [
    {"name": "BCA", "url": "...", "sector": "gov_agencies", "type": "website", "active": True},
    {"name": "CapitaLand", "url": "...", "sector": "customers", "type": "website", "active": True},
    {"name": "Hiverlab", "url": "...", "sector": "competitors", "type": "linkedin", "active": True},
    ...
]
```

Key changes:
- Replace `type` values (government/industry/competitor/prospect) with `sector` field
  using the 5 canonical sectors: `gov_agencies`, `associations`, `customers`, `partners`, `competitors`
- Add `type` field for source type: `website` or `linkedin`
- Add `active` flag on every source (True for confirmed, True for placeholders too — we want
  the scraper to attempt them so we can see which ones work)
- Add ALL sources from PROJECT_REQUIREMENTS.md, including placeholders
- Keep the `entities` and `keywords` dicts — they still work
- Keep the commented-out future country blocks

**File:** `config/sources.py` — this is the only file this session touches.

**Verify:** `python -c "from config.sources import COUNTRIES; c = COUNTRIES[0]; print(set(s['sector'] for s in c['sources']))"`
Should print: `{'gov_agencies', 'associations', 'customers', 'partners', 'competitors'}`

---

## Session 3: Scraper Multi-Sector Support

**Orchestrator verdict:** Single session. Three files, but tightly coupled — changes flow
through the pipeline sequentially (scraper → filter → analyst). No parallelism possible.

**Goal:** Make the `sector` field flow end-to-end from config through to the LLM prompt and report.

**Files:** `pipeline/scraper.py`, `pipeline/filter.py`, `pipeline/analyst.py`

### scraper.py
- In `scrape_source()`: copy `source["sector"]` into the result dict alongside name/url/type
- In `scrape_all()`: include sector in console output (e.g. `[BCA | gov_agencies] OK`)
- No other changes needed — the scraper already passes through the source dict fields

### filter.py
- No structural changes needed — `sector` is already preserved because filter passes the
  full result dict through. But verify this is true after reading the code.
- Optional: include sector in the filter summary print line

### analyst.py
- Group source blocks by sector in the user message. Instead of a flat list of sources,
  organize them under sector headers:
  ```
  === GOV_AGENCIES ===
  ### BCA (WEBSITE)
  ...

  === CUSTOMERS ===
  ### CapitaLand (WEBSITE)
  ...
  ```
- Update SYSTEM_PROMPT to reference the sector-based structure. The prompt was already
  improved in Session 1 — this adds sector awareness on top. Specifically:
  - Tell the LLM that sources are grouped by sector
  - Tell it to organize the "Signals by Sector" section using these sector groupings
  - Tell it that `customers` sector signals are highest priority for opportunity scoring

**Important:** Session 1 already modified SYSTEM_PROMPT. Read the current version of
`pipeline/analyst.py` before editing — do not assume the original prompt text.

**Do NOT change:**
- The scoring model
- The API client or model config
- The function signatures

**Verify:** `py main.py --no-email` — check that:
1. Console output shows sector labels per source
2. Report organizes signals by sector
3. Pipeline completes without errors

### After Session 3: Quality Re-Score

Run `/quality-review` to generate a new quality score. This uses a web-search-enabled sub-agent
(the command handles orchestration internally). Compare the new score against the 12/25 baseline.
Target: >= 17/25.

If the score is below 17, read the review findings and determine whether another prompt
iteration is needed before proceeding.

---

## Session 4: LinkedIn Scraper

**Orchestrator verdict:** Subagent for research, main session for implementation.

LinkedIn scraping is research-heavy and uncertain. The research phase (testing approaches,
reading docs, checking what's possible) would flood the main context. Delegate it.

### Step 1: Spawn LinkedIn research sub-agent

Use `/orchestrate` then `/prompt-engineer` to craft the research prompt.

The sub-agent's job:
- Research free, no-auth approaches to scraping public LinkedIn company pages
- Specifically investigate:
  - Direct requests + BeautifulSoup (does LinkedIn block? what do you get?)
  - `linkedin-scraper` or `linkedin-api` PyPI packages — do they work without login?
  - Playwright/Selenium headless browser approach
  - Any free API or RSS feed for LinkedIn company posts
  - Google cache or other indirect approaches
- For each approach: does it work? what content do you get? what are the risks (rate limiting, IP ban)?
- Return a recommendation ranked by reliability and simplicity
- Do NOT write any code or edit files — research only

Sub-agent type: `general-purpose` (needs WebSearch + Bash for testing packages).

### Step 2: Implement the chosen approach

Based on research results, implement in `pipeline/scraper.py`:
- Add a handler for `type: "linkedin"` sources (if scraping is viable)
- Or create `pipeline/linkedin_scraper.py` if the implementation is complex enough to warrant
  a separate module
- The handler should return the same dict structure as `scrape_source()`:
  `{name, url, sector, type, content, error}`
- If LinkedIn blocks everything: document findings in a short note, mark LinkedIn sources
  as `active: False` in config, and move on. "Attempted but deferred" is acceptable.

**Do NOT change:**
- `scrape_all()` contract — it should just call the right handler based on source type
- Any non-LinkedIn scraping logic

**Verify:** Run scraper with one LinkedIn source URL, check whether content is returned.
If content is returned, run `py main.py --no-email` to verify end-to-end.

---

## Session 5: Daily Cadence + Report Cleanup

**Orchestrator verdict:** Single session. Two small independent tasks, no research, no sub-agents.

### Task 5: Daily cadence

**File:** `.github/workflows/weekly.yml` → rename to `.github/workflows/daily.yml`

Changes:
- Rename the file
- Change `name:` from "Weekly" to "Daily"
- Change cron from `0 1 * * 1` (Monday only) to `0 1 * * *` (every day)
- Update commit message from "weekly report" to "daily report"

### Task 6: Report HTML cleanup

**File:** `pipeline/report.py`

Changes:
- Add semantic `id` attributes to section headers so Phase 3 dashboard can target them
  (e.g. `id="executive-summary"`, `id="signals-gov-agencies"`, `id="opportunities"`)
- Ensure list items are wrapped in `<ul>` or `<ol>` tags (currently bare `<li>` elements)
- No visual redesign — keep the existing CSS

**Do NOT change:**
- The function signature of `generate_html()`
- The output path logic
- The basic visual design (fonts, colors, layout)

**Verify:** Run `py main.py --no-email`, open `output/index.html` in a browser, inspect
that sections have IDs and lists are properly wrapped.

---

## Sub-Agent Strategy Summary

| Session | Sub-agents? | What the sub-agent does | Why not inline? |
|---|---|---|---|
| 1 | No | — | Single file, sequential edits |
| 2 | Yes (1) | Web-search for correct source URLs | ~20 searches would flood main context |
| 3 | No | — | Tightly coupled pipeline changes |
| 3b | Yes (1) | Quality re-score via /quality-review | Web-search fact-checking, self-contained |
| 4 | Yes (1) | LinkedIn scraping research | Uncertain research with many dead ends |
| 5 | No | — | Two small tasks, no research |

When spawning sub-agents, always:
1. Use `/orchestrate` to confirm the strategy (even if this guide says "subagent" — verify)
2. Use `/prompt-engineer` to craft the prompt (don't write ad-hoc prompts)
3. Specify the sub-agent type (`general-purpose` for WebSearch, `Explore` for code search)
4. Be explicit about the deliverable format in the prompt
5. Tell the sub-agent what files it does NOT own

---

## Phase Complete Checklist

- [ ] `py main.py --no-email` runs without errors
- [ ] Report contains signals from multiple sectors (not just gov/news)
- [ ] LinkedIn sources attempted in scraper output (or documented as deferred with findings)
- [ ] Opportunities section cites named programmes, concrete actions, deadlines, sources
- [ ] No residential property noise in report
- [ ] Quality re-score >= 17/25
- [ ] GitHub Actions workflow is daily (cron: `0 1 * * *`)
- [ ] Report HTML has semantic section IDs

When all boxes are checked, run `/context-update` to update STATE.md, CONTEXT.md, and ROADMAP.md.
Phase 1 status changes to COMPLETE. Phase 2 planning begins.
