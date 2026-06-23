# Phase 3 — Web Dashboard: Execution Guide

Read `CLAUDE.md` first (auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`).
This file is the complete plan. If something here conflicts with the current codebase,
trust the codebase and flag the conflict before proceeding.

---

## What Must Be True When This Is Done

1. **Two dashboard surfaces live from one Flask app.** Route `/` renders the polished market
   intelligence report from structured JSON data. Route `/internals` renders the AI system
   internals page. Route `POST /feedback` accepts feedback form submissions (replacing the
   separate `scripts/feedback_server.py`).
2. **The pipeline produces structured JSON, not freeform text.** `analyst.py`'s `analyse()`
   returns a Python dict (not a string). `main.py` writes `data/latest_report.json` and
   `data/run_metadata.json` per run. The Flask app reads these JSON files + ChromaDB + source
   scores to render the dashboard live per request.
3. **The report page looks professional enough for a CEO.** Score badges, sector cards, visual
   hierarchy. Not a Bootstrap tutorial, not generic AI text dump.
4. **The internals page shows the AI system's state at a glance.** Source quality scores (bar
   chart), vector store contents (browsable), feedback digest timeline, last-run metadata.

---

## Prerequisites — Install Before Starting

### Python packages (add to requirements.txt):
```
Jinja2
```
Flask already depends on Jinja2, but make it explicit. No other new packages needed —
Tailwind CSS and Chart.js load via CDN `<script>` tags (no npm/node/build step).

### CDN dependencies (loaded in HTML templates, no install):
- **Tailwind CSS** — `<script src="https://cdn.tailwindcss.com"></script>` in `<head>`
- **Chart.js** — `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>` (internals page only)

### No build tools needed. No npm. No React. No webpack. Pure Python + Jinja2 + CDN.

---

## Session Map

```
Session 1 (analyst JSON output)  ──────────┐
                                            │
Session 2 (main.py + report.py refactor)  ──┤
                                            │
Session 3 (Flask app + routes)  ────────────┤
                                            │
Session 4 (report template — Surface 1)  ───┤  ← can subagent this (HTML/CSS only)
                                            │
Session 5 (internals template — Surface 2) ─┤  ← can subagent this (HTML/CSS only)
                                            │
Session 6 (end-to-end verify)  ─────────────┘
```

Session 1 must complete before Session 2.
Session 2 must complete before Session 3.
Sessions 4 and 5 can run in parallel after Session 3 (both are pure template work).
Session 6 goes last.

**Subagent guidance:** Sessions 4 and 5 are independent template-building work. Each is
self-contained (write HTML/Jinja2 templates, CSS, client-side JS). These are ideal subagent
candidates — give each the JSON schema, the design spec, and the target file path. Sessions
1-3 modify core pipeline code with tight interdependencies — do these in the main context.

---

## Session 1: Analyst JSON Output

**Goal:** Change `analyst.py` so `analyse()` returns a Python dict, not a plain text string.

**File:** `pipeline/analyst.py`

### What to change

The synthesis call (Phase 2 of the multi-pass architecture, line 199-228) currently returns
`response.choices[0].message.content` as a plain string with markdown headers. Change it to
produce structured JSON.

**Step 1:** Append the following output format instruction to the end of `SYNTHESIS_PROMPT`
(after the current text, before the closing `"""`). Do NOT modify any of the existing grounding
rules, scoring rubric, negative examples, or section specifications — those are locked decisions.
Only ADD this block at the end:

```
OUTPUT FORMAT: Respond with valid JSON matching this exact schema. No markdown, no preamble,
no explanation outside the JSON object.

{
  "executive_summary": ["bullet 1", "bullet 2", ...],
  "signals_by_sector": {
    "Government & Agencies": [
      {"entity": "BCA", "signal": "description of the signal"}
    ],
    "Industry Associations": [...],
    "Customers": [...],
    "Partners": [...],
    "Competitors": [...],
    "General News": [...]
  },
  "opportunities": [
    {
      "title": "Short descriptive title",
      "source_quote": "Exact quote from signals",
      "named_entry_point": "Programme/tender/initiative name",
      "concrete_action": "What Silversea should do",
      "deadline": "As stated, or 'No deadline found in source'",
      "source_url": "URL if available",
      "product_fit": "Which SpatioX product and why",
      "scores": {
        "strategic_fit": 0,
        "revenue_potential": 0,
        "win_probability": 0,
        "urgency": 0,
        "intelligence_quality": 0
      },
      "total_score": 0
    }
  ],
  "synthesis": ["bullet 1", "bullet 2", ...]
}

Only include sectors that have actual signals. "opportunities" may be an empty array.
Every score field is an integer 0-5. "total_score" is the sum (0-25).
```

**Step 2:** In the `analyse()` function, after `response.choices[0].message.content` (line 228):

```python
import json

report_text = response.choices[0].message.content

# Parse JSON — fall back to wrapping raw text if LLM didn't comply
try:
    report_data = json.loads(report_text)
except json.JSONDecodeError:
    # Graceful fallback: wrap raw text so pipeline doesn't crash
    report_data = {
        "executive_summary": [report_text[:500]],
        "signals_by_sector": {},
        "opportunities": [],
        "synthesis": ["Report generated but JSON parsing failed — raw text preserved."],
        "_raw_text": report_text,
    }
```

**Step 3:** Change the return: `return report_data` (dict, not string).

**Step 4:** Update the RAG storage call (lines 230-238). Currently stores `report_text[:1500]`.
Change to store a text summary for vector search:

```python
if RAG_ENABLED:
    try:
        summary_for_rag = json.dumps(report_data.get("executive_summary", []))[:1500]
        add_documents(
            REPORT_HISTORY,
            [summary_for_rag],
            metadatas=[{"date": datetime.date.today().isoformat(), "country": country["code"]}],
        )
    except Exception:
        pass
```

**Step 5:** Check if Groq's API supports `response_format={"type": "json_object"}` for the
Llama 3.3 model. If it does, add it to the `client.chat.completions.create()` call on line 219.
If it doesn't, rely on the prompt instruction alone — the JSON fallback in Step 2 handles failures.

### Do NOT change
- `SECTOR_EXTRACT_PROMPT` — Phase 1 extraction stays as plain text (it's intermediate, not rendered)
- `_build_rag_context()` — reads from vector store, doesn't depend on output format
- `_extract_sector()` — Phase 1 extraction, independent of synthesis output format
- The grounding rules, scoring rubric, negative examples, or section specifications in `SYNTHESIS_PROMPT`
- The `SECTOR_LABELS` dict
- The `CALL_DELAY`, `MIN_CONTENT_CHARS` constants

### Verify
```bash
python -c "
from pipeline.analyst import SYNTHESIS_PROMPT
assert 'OUTPUT FORMAT' in SYNTHESIS_PROMPT
assert 'executive_summary' in SYNTHESIS_PROMPT
print('Prompt updated correctly')
"
```

Full end-to-end verify deferred to Session 6 (requires API call + live sources).

---

## Session 2: Main Pipeline + Report Refactor

**Goal:** `main.py` captures run metadata, writes JSON artifacts. `report.py` becomes a thin
JSON writer (HTML generation removed — Flask handles rendering now).

### File: `main.py`

**Changes:**

1. Replace `from pipeline.report import generate_html` with `from pipeline.report import save_report_json`

2. After the `analyse()` call (line 44), capture run metadata:

```python
import json
import datetime

# After analyse() returns report_data (now a dict):
run_metadata = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "country": country["name"],
    "country_code": country["code"],
    "sources_scraped": len(scraped),
    "sources_passed_filter": len(filtered),
    "dedup_input": len(filtered),
    "dedup_output": len(deduped),
    "dedup_merged": len(filtered) - len(deduped),
    "entities_extracted": sum(1 for r in enriched if r.get("entities")),
}
```

3. Write run metadata:
```python
metadata_path = os.path.join("data", "run_metadata.json")
os.makedirs("data", exist_ok=True)
with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(run_metadata, f, indent=2)
```

4. Replace the `generate_html()` call (line 50) with:
```python
save_report_json(report_data, country["name"])
```

5. Update `update_scores()` call — it currently takes `report_text` (string). It needs the
   full report text for citation matching. Extract it from the dict:
```python
report_text_for_scoring = json.dumps(report_data, ensure_ascii=False)
update_scores(filtered, report_text_for_scoring)
```

6. Update `send_digest()` call — it currently takes `(report_text, report_html, country_name)`.
   For email, generate a plain-text summary from the dict:
```python
if send_email:
    email_text = _format_email_text(report_data)
    send_digest(email_text, "", country["name"])  # HTML email deferred
```

   Add a helper `_format_email_text(report_data)` that concatenates exec summary + opportunities
   into plain text. Keep it simple — email formatting is not Phase 3 scope.

### File: `pipeline/report.py`

**Rewrite entirely** (currently 170 lines of HTML string concatenation + feedback form template).
Replace with:

```python
# pipeline/report.py — Writes the structured report JSON to data/latest_report.json
import json
import os
import datetime

REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "latest_report.json")


def save_report_json(report_data: dict, country_name: str) -> None:
    """Save structured report data as JSON for the Flask dashboard to render."""
    report_data["_metadata"] = {
        "country": country_name,
        "date": datetime.date.today().isoformat(),
        "date_display": datetime.date.today().strftime("%d %B %Y"),
    }

    os.makedirs(os.path.dirname(os.path.abspath(REPORT_PATH)), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"  Report JSON written to {os.path.abspath(REPORT_PATH)}")
```

The `FEEDBACK_FORM_TEMPLATE` and `generate_html()` function are deleted — feedback form
moves to the Jinja2 template (Session 4), HTML rendering moves to Flask (Session 3).

### Verify
```bash
python -c "
from pipeline.report import save_report_json
test = {'executive_summary': ['test'], 'signals_by_sector': {}, 'opportunities': [], 'synthesis': ['test']}
save_report_json(test, 'Singapore')
import json, os
data = json.load(open('data/latest_report.json'))
assert '_metadata' in data
assert data['_metadata']['country'] == 'Singapore'
print('report.py refactor works')
os.remove('data/latest_report.json')
"
```

---

## Session 3: Flask App + Routes

**Goal:** Single Flask app serving both dashboards + feedback endpoint.

### New file: `app.py` (project root)

```python
# app.py — Flask dashboard serving market intelligence report and AI system internals
import json
import os
import datetime

from flask import Flask, render_template, request

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEEDBACK_DIR = os.path.join(DATA_DIR, "feedback")


def _load_json(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default or {}


@app.route("/")
def report():
    report_data = _load_json("latest_report.json", {})
    return render_template("report.html", report=report_data)


@app.route("/internals")
def internals():
    scores = _load_json("source_scores.json", {})
    metadata = _load_json("run_metadata.json", {})

    # Query ChromaDB collections for display
    collections_data = {}
    try:
        from pipeline.vectorstore import get_collection, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
        for name in [COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS]:
            col = get_collection(name)
            result = col.get(limit=20, include=["documents", "metadatas"])
            collections_data[name] = {
                "documents": result.get("documents", []),
                "metadatas": result.get("metadatas", []),
                "ids": result.get("ids", []),
                "count": col.count(),
            }
    except Exception as e:
        collections_data = {"error": str(e)}

    return render_template("internals.html",
        scores=scores,
        metadata=metadata,
        collections=collections_data,
    )


@app.route("/feedback", methods=["POST", "OPTIONS"])
def receive_feedback():
    """Feedback endpoint — migrated from scripts/feedback_server.py."""
    if request.method == "OPTIONS":
        return "", 204

    now = datetime.datetime.now(datetime.timezone.utc)
    submitter = (request.form.get("submitter") or "anonymous").strip().replace(" ", "_")

    feedback = {
        "report_date": request.form.get("report_date", ""),
        "relevance_rating": int(request.form.get("relevance_rating", 0)),
        "most_useful": request.form.get("most_useful", ""),
        "missed_topics": request.form.get("missed_topics", ""),
        "priority_changes": request.form.get("priority_changes", ""),
        "submitter": submitter,
        "submitted_at": now.isoformat(),
    }

    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{submitter}.json"
    with open(os.path.join(FEEDBACK_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)

    return "OK", 200


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


if __name__ == "__main__":
    print("Dashboard running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
```

### Directory structure to create
```
templates/
  base.html        (shared layout — Tailwind CDN, nav, brand colors)
  report.html      (Surface 1 — extends base.html)
  internals.html   (Surface 2 — extends base.html)
static/
  style.css        (custom CSS variables + overrides beyond Tailwind)
```

### CORS note
The feedback form now POSTs to the same origin (port 5000 instead of 5050). Update the
form action in `templates/report.html` to `/feedback` (relative URL). CORS headers kept
for any cross-origin testing but no longer strictly needed.

### Verify
```bash
python -c "from app import app; print('Flask app imports OK')"
```

Full render verification in Session 6.

---

## Session 4: Report Template (Surface 1)

**Goal:** Professional market intelligence report page. This is what the CEO and BD team see.

### File: `templates/base.html`

Shared layout for both pages:
- `<script src="https://cdn.tailwindcss.com"></script>` in head
- Tailwind config block: custom brand colors (dark navy `#0a2540`, green accent `#2d6a4f`,
  score colors: green `#16a34a` for 20-25, amber `#d97706` for 13-19, gray `#6b7280` for 0-12)
- Nav bar: "Silversea Media" wordmark left, "Report" / "Internals" tabs right
- Country tab row below nav: SG (active, green dot), MY/VN/ID (greyed out, disabled)
- Footer: "Auto-generated by Silversea Market Intelligence System"
- `{% block content %}{% endblock %}`

### File: `templates/report.html`

Extends `base.html`. Reads from `{{ report }}` dict (the JSON from `data/latest_report.json`).

**Layout (top to bottom):**

1. **Header bar** — "Market Intelligence Report" + date from `report._metadata.date_display`

2. **Executive Summary card** — light background, left green border accent, bullet list from
   `report.executive_summary[]`

3. **Signals by Sector grid** — iterate `report.signals_by_sector` dict:
   - One card per sector (2-column grid on desktop, 1-column mobile)
   - Card header = sector name with icon/emoji indicator
   - Each signal is a list item: `signal.entity` in bold, `signal.signal` as text
   - Sectors with no signals don't render (the dict only contains sectors with data)

4. **Opportunities section** — iterate `report.opportunities[]`:
   - One card per opportunity
   - **Score badge** — large, color-coded (green/amber/gray based on total_score)
     positioned top-right of card
   - Title as card heading
   - Source quote in italics with quotation marks
   - Fields displayed: Named entry point, Concrete action, Deadline, Product fit
   - **Score breakdown** — 5 mini horizontal bars (one per sub-score, 0-5 scale),
     labeled: Strategic Fit, Revenue, Win Probability, Urgency, Intel Quality
   - If `report.opportunities` is empty: "No opportunities passed the relevance gate this
     cycle." in a muted callout

5. **What This Means for Silversea** — callout box, bullet list from `report.synthesis[]`

6. **Feedback form** — same fields as current (relevance 1-5 radio, most useful signal,
   missed topics, priority changes, submitter name). Form action = `/feedback`. Include
   hidden `report_date` field. JavaScript: fetch() POST on submit, show thank-you message,
   hide form. Style to match the dashboard design.

### Design tokens (CSS variables in `static/style.css` or Tailwind config):
```
--color-navy: #0a2540
--color-green-accent: #2d6a4f
--color-score-high: #16a34a    (20-25)
--color-score-medium: #d97706  (13-19)
--color-score-low: #6b7280     (0-12)
--color-bg-card: #ffffff
--color-bg-page: #f8fafc
--color-border: #e2e8f0
--font-display: 'Inter', system-ui, sans-serif
```

### Key visual requirements
- Score badges must be immediately visible — the 0-25 score is the most important visual
  element on the page, not buried in text
- Sector cards should feel like a dashboard, not a document — use background colors, spacing,
  and card shadows to create visual separation
- The overall feel should be "executive briefing tool" not "LLM output page"
- Mobile-responsive (Tailwind handles this via responsive prefixes)

---

## Session 5: Internals Template (Surface 2)

**Goal:** AI system observability page for the developer/maintainer.

### File: `templates/internals.html`

Extends `base.html`. This page can look more utilitarian — it's a developer tool, not a
CEO-facing surface. Adapt the visual shell from a free admin template (Volt Dashboard or
similar) if it saves time, or just use Tailwind utility classes directly.

**Layout (top to bottom):**

1. **Last-Run Metadata banner** — read from `{{ metadata }}` dict:
   - Last run timestamp
   - Sources scraped: `metadata.sources_scraped`
   - Passed filter: `metadata.sources_passed_filter`
   - Dedup: `metadata.dedup_merged` signals merged
   - Entities extracted: `metadata.entities_extracted`
   - Display as a row of stat cards (number + label)

2. **Source Quality Scores** — read from `{{ scores }}` dict (source_name → float):
   - **Bar chart** (Chart.js horizontal bar) — sources sorted by score descending
   - **Table** below chart — columns: Source Name, Score, visual bar indicator
   - Color-code: green > 10, amber 5-10, red < 5

3. **Vector Store Browser** — read from `{{ collections }}` dict:
   - Three tabs: `company_context` / `report_history` / `feedback_digests`
   - Each tab shows:
     - Collection count (e.g. "23 documents")
     - Scrollable list of documents with metadata
     - Each entry: truncated document text (first 200 chars) + metadata badges (date, type, etc.)
   - Tab switching: pure CSS/JS (no framework needed)

4. **Feedback Digest Timeline** — from the `feedback_digests` collection data:
   - Chronological list of digests
   - Each entry: date, submission count, digest text
   - Most recent at top

### Chart.js integration
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  // Data injected from Jinja2:
  const sourceLabels = {{ scores.keys() | list | tojson }};
  const sourceValues = {{ scores.values() | list | tojson }};

  new Chart(document.getElementById('scoresChart'), {
    type: 'bar',
    data: {
      labels: sourceLabels,
      datasets: [{
        label: 'Quality Score',
        data: sourceValues,
        backgroundColor: sourceValues.map(v => v > 10 ? '#16a34a' : v > 5 ? '#d97706' : '#ef4444'),
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: { legend: { display: false } }
    }
  });
</script>
```

---

## Session 6: End-to-End Verification

**Goal:** Prove both surfaces work with real pipeline data.

### Step 1: Run the pipeline
```bash
python main.py --no-email
```
Confirm:
- `data/latest_report.json` exists and contains valid JSON with all 4 top-level keys
- `data/run_metadata.json` exists with source counts
- `data/source_scores.json` exists (may already be there from prior runs)
- No Python tracebacks

### Step 2: Start the Flask app
```bash
python app.py
```

### Step 3: Check Surface 1 (Report)
Open `http://localhost:5000/` in a browser. Verify:
- [ ] Executive summary renders as bullet points
- [ ] Each sector with signals has its own card
- [ ] Opportunities show score badges (color-coded)
- [ ] Score breakdown bars render for each opportunity
- [ ] Empty opportunities shows the "no opportunities" callout
- [ ] Feedback form renders and submits (check `data/feedback/` for new JSON file)
- [ ] Country tabs show SG active, others greyed out
- [ ] Page looks professional — not a text dump, not generic Bootstrap

### Step 4: Check Surface 2 (Internals)
Open `http://localhost:5000/internals`. Verify:
- [ ] Run metadata stats display (sources scraped, filter count, etc.)
- [ ] Source scores bar chart renders (Chart.js)
- [ ] Vector store tabs work — can see company_context, report_history, feedback_digests
- [ ] Feedback digest timeline shows entries (if any exist in ChromaDB)

### Step 5: Regression check
- [ ] `pipeline/analyst.py` still produces valid JSON output (not broken by prompt changes)
- [ ] `pipeline/scoring.py` still works (citation matching against JSON-stringified report)
- [ ] `pipeline/feedback.py` still aggregates (reads from `data/feedback/`, writes to ChromaDB)
- [ ] `pipeline/weekly.py` still compresses (reads from report_history, writes summary)

### Step 6: Clean up
- Delete `scripts/feedback_server.py` (replaced by route in `app.py`)
- Update `output/index.html` — either delete it or have the pipeline write a redirect to
  `http://localhost:5000/` for anyone who still opens it directly

---

## Files Changed Summary

| File | Action | Description |
|------|--------|-------------|
| `pipeline/analyst.py` | Modify | Add JSON output format to SYNTHESIS_PROMPT, parse JSON response, return dict |
| `pipeline/report.py` | Rewrite | Strip HTML generation, replace with `save_report_json()` |
| `main.py` | Modify | Write `run_metadata.json`, call `save_report_json()`, adapt scoring/email calls |
| `app.py` | **New** | Flask app — 3 routes: `/`, `/internals`, `POST /feedback` |
| `templates/base.html` | **New** | Shared layout: Tailwind CDN, nav, brand colors, country tabs |
| `templates/report.html` | **New** | Surface 1: market intelligence report |
| `templates/internals.html` | **New** | Surface 2: AI system internals |
| `static/style.css` | **New** | Custom CSS variables, score badge colors, card styles |
| `requirements.txt` | Modify | Add `Jinja2` (explicit) |
| `scripts/feedback_server.py` | Delete | Replaced by route in `app.py` |

---

## Risk Notes

- **Groq JSON mode**: If `response_format={"type": "json_object"}` is not supported for
  Llama 3.3 70B on Groq, the prompt-only approach may occasionally produce malformed JSON.
  The fallback parser in Session 1 handles this gracefully. If it happens too often in
  practice, consider: (a) switching to Claude Haiku which has native JSON mode, or (b) adding
  a simple `json.loads` retry with a "please fix the JSON" follow-up call.

- **Tailwind CDN**: The CDN version is not recommended for production at scale, but this is
  an internal low-traffic dashboard — no performance concern. If it ever matters, switch to
  a Tailwind build step later.

- **ChromaDB import in app.py**: The first request to `/internals` will load the
  sentence-transformer model (~80MB). This is a one-time cost per app restart. If startup
  time matters, lazy-load it.
