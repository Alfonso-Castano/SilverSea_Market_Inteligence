# Silversea Market Intelligence System — Deployment Guide

## Table of Contents

- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Quick Start: Dashboard Only](#quick-start-dashboard-only)
- [Running the Full Pipeline](#running-the-full-pipeline)
- [Production Deployment](#production-deployment)
- [Environment Variables Reference](#environment-variables-reference)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## System Overview

The Silversea Market Intelligence System is a stateful AI market intelligence platform built for Silversea Media's BD/sales team. It scrapes sector- and business-domain-tagged sources across three countries (Singapore, Vietnam, Malaysia), filters and synthesizes findings through a multi-pass LLM pipeline, and serves the result as a daily internal web dashboard with a feedback loop that measurably shapes future reports.

**Tech Stack:** Python 3.12.3, Flask + Jinja2, Tailwind CSS (CDN, no build step), Groq API (Llama 4 Scout 17B), ChromaDB (via `sentence-transformers` embeddings), Scrapling + Playwright (dynamic page scraping).

**Authentication:** Two shared passwords (viewer, admin) — no per-user accounts.

---

## Prerequisites

| Component | Version / Notes |
|-----------|----------------|
| OS | **Ubuntu 24.04 LTS** (this guide targets it; macOS / Windows also work) |
| Python | **3.12.3** (exact, per `.python-version`), minimum 3.11+ |
| pip | Latest (bundled with Python 3.12.3) |
| Network | Outbound HTTPS access (source scraping + Groq API calls) |
| Disk Space | ~2 GB (Python packages + ChromaDB + Playwright browsers) |

> **Ubuntu 24.04 note:** The default `python3` on Ubuntu 24.04 is **3.12.3** — an exact match for the project requirement. No separate Python installation is needed.

### Install System Dependencies (Ubuntu 24.04)

Before starting, install the required Ubuntu system packages:

```bash
sudo apt update
sudo apt install -y python3.12-venv python3-pip python3-dev nginx git
```

| Package | Purpose |
|---------|---------|
| `python3.12-venv` | Create Python virtual environments (Ubuntu 24.04 requires the version-specific package) |
| `python3-pip` | Python package manager |
| `python3-dev` | C extension headers for Python (`chromadb` dependency) |
| `nginx` | Production reverse proxy (skip for dashboard-only mode) |
| `git` | Clone the repository |

---

## Quick Start: Dashboard Only

This mode requires **no API keys** — it reads pre-generated report data already committed in the repository.

### 1. Clone the Repository

```bash
git clone https://git.silversea-media.net/silversea-media/marketintelligent/ai-mi.git
cd ai-mi
```

### 2. Create a Virtual Environment and Install Dependencies

```bash
python3 -m venv im-env
source im-env/bin/activate          # Windows: im-env\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)

```bash
cp .env.example .env
```

**No `.env` values are required for dashboard-only mode** — leave everything blank and it still works.

### 4. Start the Dashboard

```bash
python3 app.py
```

Open your browser and navigate to **http://localhost:5000**.

### 5. Log In

You will be redirected to a login page on first access. Log in with the default password **`Silversea`**.

- This is the built-in shared default — no `.env` setup needed.
- If an admin has rotated the password via `/admin`, or if `VIEWER_PASSWORD` is set in `.env`, use that value instead.

---

## Running the Full Pipeline

The full pipeline scrapes real sources, makes real LLM calls, and overwrites `data/latest_report_{COUNTRY}_{DOMAIN}.json`.

### Prerequisites

Complete all steps in [Quick Start](#quick-start-dashboard-only) above first, then continue.

### 1. Install Scrapling Browser Binaries

```bash
scrapling install
```

> ⚠️ **This is an easy-to-miss step.** `pip install` only installs the Scrapling and Playwright *Python packages* — the actual browser binaries needed by some sources to bypass anti-bot pages or render JS-heavy sites are a separate download via `scrapling install`. Skip this and you'll see errors like `Executable doesn't exist at ...\chrome-win64\chrome.exe` the first time the pipeline hits a source tagged `"fetcher": "stealth"` or `"fetcher": "dynamic"`.

### 2. Set Your Groq API Key

Set `GROQ_API_KEY` in `.env`:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

Sign up free at [console.groq.com](https://console.groq.com) — no payment info needed for the free tier.

### 3. Run the Pipeline

**Run scoped to one country and one domain:**

```bash
python3 main.py --country=SG --domain=BER --no-email
```

**Parameter Reference:**

| Parameter | Description | Values |
|-----------|-------------|--------|
| `--country` | Which country's source list to run | `SG` (Singapore), `VN` (Vietnam), `MY` (Malaysia) |
| `--domain` | Business-domain-tagged subset of sources | `BER` (Built Environment), `GENERAL`, `EDU`, `RCC`, `HLS`, `MFG`, `CTE`, `PSS` |
| `--no-email` | Skip the optional email digest step | Recommended unless `GMAIL_*` vars are configured |

> ⚠️ **Mind the quota:** Groq's free tier has a 100,000-token daily limit. A single scoped run costs roughly 15,000–30,000 tokens. Don't loop over combinations speculatively.

Omitting `--country`/`--domain` runs every active combination — this is slow and burns through your quota quickly. Not recommended for testing.

### 4. View Results

Output overwrites `data/latest_report_{COUNTRY}_{DOMAIN}.json`, which the dashboard reads fresh on every request — **no restart needed** to see new results.

---

## Production Deployment (Ubuntu 24.04)

The following are recommended approaches for production deployment. The built-in Flask development server (`app.py`) is **not suitable for production use**.

### 1. Deploy Code to `/www/wwwroot/ai-mi`

```bash
mkdir -p /www/wwwroot
git clone https://git.silversea-media.net/silversea-media/marketintelligent/ai-mi.git /www/wwwroot/ai-mi
```

### 2. Create Virtual Environment and Install Dependencies

```bash
cd /www/wwwroot/ai-mi
python3 -m venv im-env
source im-env/bin/activate
pip install -r requirements.txt
pip install gunicorn
scrapling install
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with actual values (at minimum set GROQ_API_KEY and ADMIN_PASSWORD)
```

### 4. Start / Restart Gunicorn

Use the provided `deploy/start.sh` script, which handles "stop if running, then start" automatically:

```bash
bash /www/wwwroot/ai-mi/deploy/start.sh
```

Script behavior:
- If a Gunicorn process is already running, sends `SIGTERM` for graceful shutdown (force-kills with `SIGKILL` after 2s timeout)
- Starts a new process in `--daemon` mode, writing the PID to `gunicorn.pid`
- Verifies the new process is alive after startup

> Manual stop: `kill $(cat /www/wwwroot/ai-mi/gunicorn.pid)`

### 5. Configure Nginx Reverse Proxy

`/etc/nginx/sites-available/silversea-mi`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout config (LLM calls can be slow)
        proxy_read_timeout 180s;
        proxy_connect_timeout 10s;
    }

    location /static {
        alias /www/wwwroot/ai-mi/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6. Enable the Site and Reload Nginx

```bash
# Remove the default site first (avoids port conflicts)
sudo rm -f /etc/nginx/sites-enabled/default

# Enable the Silversea MI site
sudo ln -s /etc/nginx/sites-available/silversea-mi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Configure Firewall (UFW)

Ubuntu 24.04 uses `ufw` by default:

```bash
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS (if using SSL)
sudo ufw allow 22/tcp       # SSH (don't lock yourself out!)
sudo ufw enable
sudo ufw status             # Verify rules
```

### 8. Configure SSL/HTTPS (Recommended)

Use Certbot to obtain a free Let's Encrypt certificate:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run   # Verify auto-renewal
```

Certbot will automatically modify the Nginx config to add SSL and set up HTTP→HTTPS redirection.

---

### Scheduled Pipeline Runs (Cron)

In production, you'll likely want to run the pipeline daily:

```bash
crontab -e
```

```bash
# Run Singapore BER pipeline every day at 7:00 AM
0 7 * * * cd /www/wwwroot/ai-mi && /www/wwwroot/ai-mi/im-env/bin/python main.py --country=SG --domain=BER --no-email >> /www/wwwroot/ai-mi/cron.log 2>&1

# Run Vietnam BER pipeline every day at 7:30 AM
30 7 * * * cd /www/wwwroot/ai-mi && /www/wwwroot/ai-mi/im-env/bin/python main.py --country=VN --domain=BER --no-email >> /www/wwwroot/ai-mi/cron.log 2>&1

# Weekly summary every Sunday at 3:00 AM (auto-triggered by main.py when run on Sunday)
0 3 * * 0 cd /www/wwwroot/ai-mi && /www/wwwroot/ai-mi/im-env/bin/python main.py --country=SG --domain=GENERAL --no-email >> /www/wwwroot/ai-mi/cron.log 2>&1
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Pipeline only | Groq API key for LLM calls. Sign up free at [console.groq.com](https://console.groq.com) |
| `VIEWER_PASSWORD` | No | Dashboard viewer password. Defaults to `Silversea` if unset, auto-seeded into `data/viewer_password.txt` on first run |
| `ADMIN_PASSWORD` | Admin only | Password for the `/admin` page. **No default** — admin login is refused if unset |
| `GMAIL_USER` | Email only | Gmail sender address for the email digest |
| `GMAIL_APP_PASSWORD` | Email only | Gmail app-specific password (not your regular password — generate at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)) |
| `RECIPIENT_EMAILS` | Email only | Comma-separated list of recipient email addresses for the digest |

> ⚠️ **Security note:** `.env` is per-machine and gitignored — never commit it to the repository. `ADMIN_PASSWORD` has no built-in default on purpose; get the real value from whoever owns Silversea's shared secrets.

---

## Troubleshooting

| Symptom | Solution |
|---------|----------|
| Redirected to `/login` immediately, don't know the password | Log in with `Silversea` — the built-in shared default |
| Pipeline fails with `Executable doesn't exist at ...chrome-win64\chrome.exe` | Run `scrapling install` (a one-time step after `pip install -r requirements.txt`) |
| `pip install -r requirements.txt` fails, or things behave oddly | Check `python3 --version` against `.python-version` (`3.12.3`). Dependencies (`numpy`/`onnxruntime` via `chromadb`) have a hard floor of Python 3.11+ |
| `/admin` always redirects away, even after logging in | `ADMIN_PASSWORD` isn't set in `.env` — there's no default for it |
| Pipeline runs but dashboard shows no new data | Check that `data/latest_report_{COUNTRY}_{DOMAIN}.json` was generated. The dashboard reads files fresh on every request, but ensure your URL params `?country=` and `?domain=` match the pipeline run |
| ChromaDB errors | Ensure the `data/` directory is writable. ChromaDB stores data in a persistent directory under `data/` |

---

## Project Structure

```
ai-mi/
├── app.py                  # Flask dashboard entry point (viewer/admin auth)
├── main.py                 # Pipeline entry point (scrape → filter → analyze → report)
├── requirements.txt        # Python dependencies (exact pinned versions)
├── .python-version         # Python version constraint (3.12.3)
├── .env.example            # Environment variable template
├── config/
│   ├── sources.json        # Per-country source list (177 total, 152 active)
│   ├── sources.py          # Source loading/saving utilities
│   └── models.py           # Data models
├── pipeline/
│   ├── scraper.py          # Tiered scraper (plain requests / Scrapling stealth / dynamic-JS)
│   ├── filter.py           # Keyword filtering (priority + general tiered weighting)
│   ├── analyst.py          # LLM analysis (extract → synthesize → summary, three calls)
│   ├── report.py           # Report JSON persistence
│   ├── emailer.py          # Gmail digest sender (optional)
│   ├── feedback.py         # Feedback aggregation + ChromaDB RAG loop
│   ├── vectorstore.py      # ChromaDB vector store wrapper
│   ├── weekly.py           # Weekly summary compression
│   └── source_suggestions.py # Source suggestion approval workflow
├── data/
│   ├── latest_report*.json # Pre-generated report files + per-country/domain reports
│   ├── company_context.md  # Company context knowledge document
│   ├── viewer_password.txt # Viewer password persistence file
│   └── feedback/           # User feedback JSON files
├── static/
│   ├── style.css           # Custom styles
│   └── animations.js       # Frontend animations
├── templates/
│   ├── base.html           # Jinja2 base template (nav, layout)
│   ├── report.html         # Dashboard main page (signals, opportunities, risks)
│   ├── login.html          # Login page
│   ├── admin.html          # Admin page (source approval, password rotation)
│   └── internals.html      # System internals page
├── deploy/                 # Deployment guides
│   ├── deployment-zh.md    # Chinese deployment guide
│   └── deployment-en.md    # English deployment guide (this file)
├── docs/                   # Reference materials (PDFs, Excel templates, etc.)
├── tests/                  # Tests
├── scripts/                # Utility scripts
└── output/                 # Output directory
```

---

## Architecture Overview

```
config/sources.json (per-country source list, sector + domain tags)
  → Scraper (tiered: plain requests / Scrapling stealth / Scrapling dynamic-JS)
  → Keyword Filter (priority + general tiered weighting, per-country keyword lists)
  → Per-Sector Extraction (one LLM call per sector — lists every concrete signal, no interpretation)
  → Per-Sector Synthesis (extraction text → structured JSON: entity/signal/source)
  → Summary Call (executive summary + scored opportunities, one call)
  → data/latest_report_{COUNTRY}_{DOMAIN}.json
  → Flask dashboard (viewer/admin auth-gated)
```

**Key Design Decision:** The extract-then-synthesize split exists because feeding a single large synthesis call too much raw content at once caused the model to silently drop most of the signal — splitting per-sector fixed this (signal count went from single digits to 65+ in testing).

**Feedback Loop:** The dashboard's feedback form aggregates submissions, summarizes them via LLM into a digest, and stores that digest in ChromaDB — future pipeline runs retrieve it as context, so team feedback measurably changes what gets surfaced later.

**Opportunity Scoring:** Each identified opportunity is scored on 5 dimensions (Strategic Fit, Revenue Potential, Win Probability, Urgency, Intelligence Quality; 1–5 each, 25 max). Score bands: 20–25 = escalate to BD immediately, 13–19 = monitor, 0–12 = log only.
