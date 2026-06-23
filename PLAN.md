# PLAN.md — Current Phase Plan

*Active plan for the phase currently in progress. Overwritten at the start of each new phase.*
*Task status updated by /context-update. Full phase history lives in ROADMAP.md.*

---

## Phase 3 — Web Dashboard

**Goal:** Replace static HTML output with a professional Flask-served dashboard. Two surfaces: a polished market intelligence report for BD/sales team, and an AI system internals page for the developer/maintainer.

**Done when:**
- `app.py` serves both pages from one Flask app on port 5000
- Report page renders structured JSON data with score badges, sector cards, visual hierarchy
- Internals page shows vector store contents, source scores chart, feedback digests, run metadata
- Feedback form submits to `/feedback` on the same app (replacing `scripts/feedback_server.py`)
- Country tabs: SG active, MY/VN/ID slots greyed out

**Execution file:** `.claude/execution/phase3-dashboard.md` — full implementation details for each session.

---

## Tasks

### 1. Analyst JSON output `[DONE]`
Modify `pipeline/analyst.py` to return structured JSON dict instead of freeform text string.

**Files:** `pipeline/analyst.py`
**Details:** Append JSON output format instruction to SYNTHESIS_PROMPT (after locked grounding rules). Parse response with `json.loads`, fallback to wrapped raw text on parse failure. Return dict.

---

### 2. Pipeline + report refactor `[DONE]`
Refactor `main.py` to write `data/latest_report.json` + `data/run_metadata.json`. Rewrite `pipeline/report.py` to a thin JSON writer (strip all HTML generation).

**Files:** `main.py`, `pipeline/report.py`
**Details:** Capture run metadata (source counts, dedup stats, timestamp). Replace `generate_html()` with `save_report_json()`. Adapt scoring and email calls for dict input.

---

### 3. Flask app + routes `[DONE]`
Create `app.py` with three routes: `/` (report), `/internals`, `POST /feedback`.

**Files:** `app.py` (new), `templates/` directory (new), `static/` directory (new)
**Details:** Migrate feedback endpoint from `scripts/feedback_server.py`. Read JSON files + ChromaDB for live rendering. Delete `scripts/feedback_server.py` when done.
**Note:** `/feedback` accepts both JSON and form-encoded bodies (template posts JSON). `scripts/feedback_server.py` not yet deleted — deferred pending Alfonso's confirmation.

---

### 4. Report template — Surface 1 `[DONE]`
Build `templates/base.html` + `templates/report.html` — polished market intelligence report page.

**Files:** `templates/base.html` (new), `templates/report.html` (new), `static/style.css` (new)
**Details:** Tailwind CDN, brand colors (#0a2540 navy, #2d6a4f green), score badges (color-coded 0-25), sector card grid, feedback form, country tabs. Must look professional — not a Bootstrap tutorial, not a text dump.

---

### 5. Internals template — Surface 2 `[DONE]`
Build `templates/internals.html` — AI system observability page.

**Files:** `templates/internals.html` (new)
**Details:** Chart.js horizontal bar chart for source scores, tabbed vector store browser (3 collections), feedback digest timeline, run metadata stat cards. Can adapt Volt Dashboard template shell.

---

### 6. End-to-end verification `[DONE]`
Run full pipeline → start Flask → verify both surfaces render real data → test feedback submission.

**Verify checklist:**
- [x] `python main.py --no-email` produces `data/latest_report.json` + `data/run_metadata.json`
- [x] `python app.py` starts without errors
- [x] `http://localhost:5000/` renders report with score badges and sector cards
- [x] `http://localhost:5000/internals` renders source scores chart and vector store browser
- [x] Feedback form submits and creates JSON in `data/feedback/`
- [x] No regressions in scoring, feedback aggregation, or weekly summarizer

**Note:** Verified using a temporary `llama-3.1-8b-instant` swap after the 70B model hit Groq's 100k TPD free-tier limit mid-run. Model reverted to `llama-3.3-70b-versatile`. A clean full-quality 70B run is still needed once the quota resets.

## Phase Complete
**Date:** 2026-06-23
**Summary:** Flask dashboard live at `/` (report) and `/internals`, structured JSON pipeline output, feedback loop consolidated into one app — full chain verified end-to-end.

---

## Dependencies

```
1 (analyst JSON) → 2 (pipeline refactor) → 3 (Flask app + routes)
                                                    ↓
                                            4 (report template)  ← parallel
                                            5 (internals template) ← parallel
                                                    ↓
                                            6 (end-to-end verify)
```

## Subagent Strategy

Sessions 4 and 5 are independent template-building work (HTML/Jinja2/CSS/JS). Each can be delegated to a subagent with the JSON schema and design spec as input. Sessions 1-3 modify core pipeline code with tight interdependencies — execute in main context.
