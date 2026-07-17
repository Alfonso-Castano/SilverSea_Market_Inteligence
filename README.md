# Silversea Market Intelligence System

A stateful AI market intelligence system for Silversea Media's BD/sales team. It scrapes sector-tagged sources across multiple countries (Singapore, Vietnam, Malaysia) and business domains (Built Environment, Education, and more), filters and synthesizes findings through a multi-pass LLM pipeline, and serves the result as a daily internal web dashboard with a feedback loop that shapes future reports. 152 active sources across 3 countries as of this writing.

## Requirements

- **Python 3.12.3** (pinned in `.python-version` — see below for why)
- A Groq API key (free tier) if you want to run the full pipeline, not just view the dashboard

## Quick Start — View the Dashboard

```bash
git clone <this repo's URL>
cd SilverSea_Market_Inteligence
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python3 app.py                     # Windows: py app.py, or python app.py
```

Open **http://localhost:5000** in your browser.

**The dashboard is behind a login wall** — every route redirects to `/login` until you authenticate. There's a viewer role (read-only) and an admin role (source-approval queue, viewer-password rotation), gated by two separate passwords:

- **Viewer password**: set `VIEWER_PASSWORD` in `.env`. If you leave it unset, the app silently seeds `data/viewer_password.txt` with the literal string `changeme` on first run and uses that — so if you skip setting it, log in with `changeme`.
- **Admin password**: set `ADMIN_PASSWORD` in `.env`. Unlike the viewer password, there is **no default** — if it's unset, admin login is refused outright (by design, not a bug). Ask whoever owns Silversea's shared secrets for the real value.

The dashboard renders from whatever's already in `data/latest_report_*.json` (pre-generated, committed to the repo) — no API keys or pipeline run needed just to look at it.

**Note (Windows):** the example above uses `python3`; on Windows you may need `py` or `python` instead depending on how Python was installed. All three are equivalent here.

## Dashboard

**Report page** (`/`) — Market intelligence signals grouped by entity within sectors (Government & Agencies, Industry Associations, Customers, Partners, Competitors, General News). Switch between countries (Singapore/Vietnam/Malaysia) and business domains (Built Environment/Education/General) via the tabs at the top. Features: collapsible entity groups, signal spotlight (click any card), dark/light mode toggle, PDF export, source links on every signal card.

**Internals page** (`/internals`) — AI system observability: vector store contents, feedback digests, run metadata. Admin-only sections require the admin role.

**Admin page** (`/admin`, admin role only) — Review and approve/reject sources suggested via the feedback form. Approving appends an active source to `config/sources.json`; it's picked up automatically by the next matching pipeline run — no separate registration step.

**Feedback form** — Embedded at the bottom of the report page. Submissions are aggregated and fed back into the AI system to shape future reports.

## Architecture

```
config/sources.json (per-country, per-source: sector + business-domain tags)
  → Scraper (tiered: plain requests / Scrapling stealth / Scrapling dynamic-JS)
  → Keyword Filter (priority + general tiered weighting, per-country keyword lists)
  → Per-Sector Extraction (one LLM call per sector with content)
  → Per-Sector Synthesis (extraction text → structured JSON)
  → Summary Call (executive summary + scored opportunities)
  → data/latest_report_{COUNTRY}_{DOMAIN}.json
  → Flask app serves dashboard (viewer/admin auth-gated)
```

**Stack:** Python, Flask + Jinja2, Tailwind CSS (CDN), Groq API (Llama 4 Scout 17B) by default, ChromaDB (RAG feedback loop + report history)

**Countries:** Singapore (SG), Vietnam (VN), Malaysia (MY) — each with its own source list in `config/sources.json`, run independently via `--country=<CODE>`.

**Business domains:** Built Environment (BER), Education (EDU), General (GENERAL), plus Retail & Commerce, Healthcare, Manufacturing, Culture & Tourism, and Public Sector for Vietnam/Malaysia — each source is tagged with the domain(s) it's relevant to; a pipeline run is scoped to one domain at a time via `--domain=<CODE>`.

**Auth:** two shared passwords (viewer/admin), not per-user accounts — see the Quick Start section above.

## Running the Full Pipeline

Requires a `.env` file (copy `.env.example` and fill in at least `GROQ_API_KEY`):

```bash
pip install -r requirements.txt
python3 main.py --country=SG --domain=BER --no-email
```

`--country` and `--domain` are both optional; omitting them runs every active country/domain combination, which is slow and burns a lot more Groq quota — scope to one country/domain while testing. `--no-email` skips the (optional) email digest, which needs `GMAIL_USER`/`GMAIL_APP_PASSWORD`/`RECIPIENT_EMAILS` set to work at all.

A single country/domain run takes roughly 30 seconds to a few minutes and uses on the order of 15-30k Groq tokens, depending on how many sources are tagged for that domain — Groq's free tier is 100k tokens/day, so don't loop over every country/domain combination speculatively. Output overwrites `data/latest_report_{COUNTRY}_{DOMAIN}.json`, which the Flask app reads fresh on every request.

**One-time setup step for scraping (not covered by `pip install`):** some sources need Scrapling's stealth/dynamic fetchers to get past anti-bot protection or render JS-heavy pages. `pip install -r requirements.txt` installs the Scrapling and Playwright *Python packages*, but not the actual browser binaries they drive — those are a separate download. Run this once after installing dependencies:

```bash
scrapling install
```

Without this step, any source tagged `"fetcher": "stealth"` or `"fetcher": "dynamic"` in `config/sources.json` will fail when the pipeline reaches it (sources using the default `requests`-based fetcher are unaffected).

## Choosing an LLM Backend

By default, the pipeline uses the Groq API (`GROQ_API_KEY`, free tier) for all LLM calls. A local-model backend (`LLM_BACKEND=local`) also exists, running against a self-hosted Ollama server instead — see `feature/002-local-llm-backend` for status; as of this writing it has **not** been merged to `main` and should be treated as experimental. Check that branch's own notes before relying on it.

## Environment Variables

See `.env.example` for the full list with inline comments on which values you get yourself (free tier) versus which are shared team secrets. Summary:

| Variable | Required For | Get it from |
|---|---|---|
| `GROQ_API_KEY` | Running the pipeline | Your own free account at [console.groq.com](https://console.groq.com) |
| `VIEWER_PASSWORD` | Dashboard login | Shared team value (defaults to `changeme` if unset) |
| `ADMIN_PASSWORD` | Admin login (`/admin`) | Shared team value — no default, admin login is refused if unset |
| `GMAIL_USER` | Email digest (optional) | Shared team value |
| `GMAIL_APP_PASSWORD` | Email digest (optional) | Shared team value |
| `RECIPIENT_EMAILS` | Email digest (optional) | Shared team value |

None of these are needed just to view the dashboard with existing report data — only `VIEWER_PASSWORD` (or the `changeme` default) matters for that.
