# PLAN.md — Current Phase Plan

*Active plan for the phase currently in progress. Overwritten at the start of each new phase.*
*Task status updated by /context-update. Full phase history lives in ROADMAP.md.*

---

## Phase 1 — Foundation

**Goal:** Working daily pipeline for Singapore with sector-based scraper and improved analysis quality.

**Done when:** Pipeline runs daily, pulls from all 5 sector types (website placeholders + LinkedIn),
report quality visibly improved over 12/25 baseline score.

---

## Tasks

### 1. Analyst prompt improvements `[DONE]`
Apply the 3 fixes diagnosed in `quality/reviews/2026-06-16.md`:
- Fix JTC LaunchPad / low-carbon conflation — treat each named programme as a distinct signal
- Rewrite Opportunities section — require named entry point, concrete action, deadline, source citation per score
- Add noise filter — exclude signals with no direct path to Silversea's products or named prospects

File: `pipeline/analyst.py` → `SYSTEM_PROMPT`
Verify: run `py main.py --no-email`, check output quality against rubric

### 2. Sector-based config redesign `[DONE]`
Redesign `config/sources.py` to organise sources by sector rather than a flat list.

Sectors: `gov_agencies`, `associations`, `customers`, `partners`, `competitors`

Each source entry needs: `name`, `sector`, `type` (website/linkedin), `url`, `active` flag.
Use placeholder entries for each sector — real companies appended later.

File: `config/sources.py`

### 3. Scraper multi-sector support `[DONE]`
Update `pipeline/scraper.py` to handle sector-tagged sources.
Output should carry `sector` field through to filtered results and into the analyst.
Analyst prompt should be aware of which sector each signal came from.

Files: `pipeline/scraper.py`, `pipeline/filter.py`, `pipeline/analyst.py`

### 4. LinkedIn scraper `[DONE — DEFERRED]`
Research and implement a scraper for public LinkedIn company pages.
Target: company posts/updates visible without authentication.

Options to evaluate:
- `linkedin-scraper` PyPI package
- Playwright/Selenium with headless browser
- Third-party service (Apify, PhantomBuster) — flag cost to Alfonso before adopting

Constraint: public pages only, no authentication, no paid service without approval.
File: `pipeline/scraper.py` (add linkedin handler) or `pipeline/linkedin_scraper.py`

### 5. Daily cadence `[DONE]`
Update GitHub Actions workflow from weekly to daily.
Preferred time: 9:00 SGT (01:00 UTC).

File: `.github/workflows/weekly.yml` → rename to `daily.yml`, update cron

### 6. Report foundation cleanup `[DONE]`
Light cleanup of `pipeline/report.py` to prepare for Phase 3 dashboard.
No redesign — just ensure HTML structure is clean and section-based
so Phase 3 can slot in tabs and interactive elements without a full rewrite.

File: `pipeline/report.py`

---

## Order of Execution
1 → 2 → 3 → 4 → 5 → 6

Tasks 1 and 2 are independent and can be done in either order.
Tasks 3 depends on 2 (needs sector structure in config first).
Task 4 is independent — can be researched in parallel with 2/3.
Tasks 5 and 6 are independent, do last.

---

## Execution Guide
Session-by-session breakdown with sub-agent strategy, file ownership, and verification steps:
`.claude/execution/phase1.md`

---

## Verify Phase Complete
- [x] `py main.py --no-email` runs without errors
- [x] Report contains signals from multiple sectors (gov_agencies, associations, customers, competitors)
- [x] LinkedIn sources researched and documented as deferred (no viable free approach)
- [x] Opportunities section uses grounded extraction — only cites facts from source text
- [x] No residential property noise in report
- [x] Quality score: 21/25 (target was ≥ 17/25)

## Phase Complete
**Completed:** 2026-06-19
Phase 1 foundation complete. Pipeline runs daily with 25 sector-tagged sources, grounded analyst prompt scoring 21/25.
