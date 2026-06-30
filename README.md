# Silversea Market Intelligence System

Automated daily market intelligence for Silversea Media's BD/sales team. Scrapes ~57 sources across Singapore's built environment sector, runs AI-powered extraction and synthesis, and serves an interactive dashboard with 65+ signals per run.

## Quick Start — View the Dashboard

You only need Flask installed to see the report:

```bash
git clone https://github.com/Alfonso-Castano/SilverSea_Market_Inteligence.git
cd SilverSea_Market_Inteligence
pip install flask
py app.py
```

Open **http://localhost:5000** in your browser. The dashboard renders from pre-generated report data — no API keys or pipeline run needed.

## Dashboard

**Report page** (`/`) — Market intelligence signals grouped by entity within 5 color-coded sectors. Features: collapsible entity groups, signal spotlight (click any card), dark/light mode toggle, scroll progress bar, source links on every signal card.

**Internals page** (`/internals`) — AI system observability: vector store contents, source quality scores, feedback digests, run metadata.

**Feedback form** — Embedded at the bottom of the report page. Submissions are aggregated and fed back into the AI system to shape future reports.

## Architecture

```
Scraper (57 sources, 5 sectors)
  → Keyword Filter (priority + general tiered weighting)
  → Per-Sector Extraction (6 LLM calls — one per sector)
  → Per-Sector Synthesis (6 LLM calls — extraction text → structured JSON)
  → Summary Call (1 LLM call — executive summary + opportunities)
  → data/latest_report.json
  → Flask app serves dashboard
```

**Stack:** Python, Flask + Jinja2, Tailwind CSS (CDN), Groq API (Llama 4 Scout 17B), ChromaDB

**Sectors:** Government & Agencies, Industry Associations, Customers, Partners, Competitors

## Running the Full Pipeline

Requires a `.env` file:

```
GROQ_API_KEY=your_groq_api_key
```

Then:

```bash
pip install -r requirements.txt
py main.py
```

Takes ~30 seconds, uses ~15-20k Groq tokens per run. Output overwrites `data/latest_report.json`, which the Flask app reads on each request.

## Environment Variables

| Variable | Required For | Description |
|---|---|---|
| `GROQ_API_KEY` | Pipeline only | Groq API key ([free tier](https://console.groq.com)) |
| `GMAIL_USER` | Email only | Sender Gmail address |
| `GMAIL_APP_PASSWORD` | Email only | Gmail app password |
| `RECIPIENT_EMAILS` | Email only | Comma-separated recipient list |

None of these are needed to view the dashboard.
