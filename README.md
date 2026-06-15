# Silversea Market Intelligence Pipeline

Automated weekly market intelligence report for Silversea Media's BD/sales team.
Covers Singapore's built environment, proptech, smart FM, and digital twin sectors.

## How It Works

1. **Scraper** fetches content from ~11 curated sources (government, industry, competitors)
2. **Filter** removes irrelevant content using keyword matching
3. **Analyst** sends filtered content to Claude API, which produces a structured 6-section report
4. **Report** writes an HTML page to `output/index.html` (served via Vercel)
5. **Emailer** sends a digest to configured recipients

Runs every Monday 09:00 SGT via GitHub Actions.

## Local Development

```bash
pip install -r requirements.txt

# Set env vars (or create a .env file and load it)
export ANTHROPIC_API_KEY=...
export GMAIL_USER=...
export GMAIL_APP_PASSWORD=...
export RECIPIENT_EMAILS=alfonsocastano486@gmail.com

# Run without sending email
python main.py --no-email
```

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key |
| `GMAIL_USER` | Sender Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail app password (not account password) |
| `RECIPIENT_EMAILS` | Comma-separated recipient list |

Set these as GitHub Actions secrets for automated runs.

## Deployment

Vercel is connected to this repo and auto-deploys `output/index.html` on every push.

## Adding Countries

In `config/sources.py`, add a new entry to `COUNTRIES` with `active: False`.
Flip to `True` when sources and keywords are ready.
