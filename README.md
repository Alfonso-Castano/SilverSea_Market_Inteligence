# Silversea Market Intelligence System

## Part 1 — Build & Run

Everything below has been run and verified against this exact repo state (not just written from memory of what should work). Two independent paths, pick the one you need:

- **[View the dashboard only](#1-view-the-dashboard-only)** — no API keys, reads pre-generated report data already in the repo.
- **[Run the full pipeline](#2-run-the-full-pipeline)** — scrapes real sources, calls an LLM, regenerates the report. Needs a Groq API key.

Both need **Python 3.12.3** (pinned in [`.python-version`](.python-version) — check it matches what you have: `python3 --version`).

### 1. View the dashboard only

```bash
git clone https://git.silversea-media.net/silversea-media/marketintelligent/ai-mi.git
cd ai-mi
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python3 app.py                     # Windows: py app.py (or python app.py)
```

Open **http://localhost:5000**.

**No `.env` values are required for this path** — leave everything in `.env` blank and it still works. The dashboard renders from whatever's already committed in `data/latest_report_*.json`; nothing here calls an LLM or needs a key.

**You will immediately hit a login screen — this is expected, not a bug.** Every route redirects to `/login` until you authenticate:

- Log in with `Silversea` — this is the built-in shared default, no `.env` setup required.
- If an admin has since rotated it via `/admin`, or if `VIEWER_PASSWORD` is set in `.env`, use that value instead — either one overrides the built-in default the first time anyone submits the login form (after that, whatever's in `data/viewer_password.txt` is the real password until an admin rotates it again).

That's the whole dashboard-only path. `ADMIN_PASSWORD`, `GROQ_API_KEY`, and the email vars are irrelevant here — see [Run the full pipeline](#2-run-the-full-pipeline) and [Admin access](#admin-access) below if you need those.

### 2. Run the full pipeline

This scrapes real sources, makes real LLM calls, and overwrites `data/latest_report_{COUNTRY}_{DOMAIN}.json`.

**Same setup as above, plus:**

```bash
# after `pip install -r requirements.txt`:
scrapling install
```

This is a separate, easy-to-miss step. `pip install` only installs the Scrapling and Playwright *Python packages* — the actual browser binaries some sources need (to get past anti-bot pages or render JS-heavy sites) are a separate download that `scrapling install` fetches. Skip this and you'll see errors like `Executable doesn't exist at ...\chrome-win64\chrome.exe` the first time the pipeline hits a source tagged `"fetcher": "stealth"` or `"fetcher": "dynamic"` in `config/sources.json` (sources on the default fetcher are unaffected either way).

**Set `GROQ_API_KEY` in `.env`.** Sign up free at [console.groq.com](https://console.groq.com) — no payment info needed for the free tier. Nothing else in `.env` is required to run the pipeline itself (`GMAIL_*`/`RECIPIENT_EMAILS` only matter if you want the optional email digest, off by default).

**Run it scoped to one country and one domain:**

```bash
python3 main.py --country=SG --domain=BER --no-email
```

- `--country` — which country's source list to run: `SG` (Singapore), `VN` (Vietnam), or `MY` (Malaysia).
- `--domain` — which business-domain-tagged subset of that country's sources to run: `BER` (Built Environment) and `GENERAL` have the most source coverage today; `EDU` exists but is thin for most countries; `RCC`/`HLS`/`MFG`/`CTE`/`PSS` exist as source tags but don't have dedicated UI tabs yet (see Part 2).
- `--no-email` — skip the optional email digest step entirely (recommended unless you've set up the `GMAIL_*` vars).
- Omitting `--country`/`--domain` runs every active combination — this is slow and burns much more quota than scoping to one. Don't do this while just testing.

**Real caveat, not a hypothetical one:** Groq's free tier is a 100,000-token daily quota, shared across every run you make that day. A single scoped `--country`/`--domain` run costs roughly 15,000-30,000 tokens depending on how many sources are tagged for that domain. Don't loop over combinations speculatively — pick the one you actually need to test.

Output overwrites `data/latest_report_{COUNTRY}_{DOMAIN}.json` (e.g. `data/latest_report_SG_BER.json`), which `app.py` reads fresh on every dashboard request — no restart needed to see new results.

#### Admin access

`/admin` (source-approval queue, viewer-password rotation) is gated by a separate `ADMIN_PASSWORD` in `.env`. Unlike the viewer password, **there is no default** — if it's unset, admin login is refused outright regardless of what you type. This is intentional (a previous version of this app had an auth bypass here), not a bug to work around. Ask whoever owns Silversea's shared secrets for the real value.

#### A note on `.env` and shared passwords

`.env` is per-machine and gitignored — it is never committed to either repo. `VIEWER_PASSWORD` has a working built-in default (`Silversea`, hardcoded in `app.py`) precisely because it's meant to be known company-wide — nobody needs to touch `.env` for it unless an admin has rotated it to something else. `ADMIN_PASSWORD` is the opposite: it has **no** built-in default on purpose (see [Admin access](#admin-access) above), because baking an admin credential into a git-committed file would give every clone of this repo admin rights. Get the real `ADMIN_PASSWORD` value from whoever owns Silversea's shared secrets for this project and paste it into your own local `.env` — not into a chat with an AI assistant or any other logged channel (secrets pasted into a chat transcript should be treated as compromised, the same way an exposed API token would be).

### 3. Troubleshooting

The fast-path fixes for what's most likely to trip you up, even though each is explained in full above:

| Symptom | Fix |
|---|---|
| Redirected to `/login` immediately, don't know the password | Log in with `Silversea` — the built-in shared default (auto-seeded into `data/viewer_password.txt` on first login attempt, unless an admin has since rotated it) |
| Pipeline fails with `Executable doesn't exist at ...chrome-win64\chrome.exe` | You skipped `scrapling install` after `pip install -r requirements.txt` — run it now, it's a one-time step |
| `pip install -r requirements.txt` fails, or things behave oddly after installing | Check `python3 --version` against [`.python-version`](.python-version) (`3.12.3`) — this repo's dependencies (`numpy`/`onnxruntime` via `chromadb`) have a real floor of Python 3.11+, and the pinned versions were only tested against 3.12.3 specifically |
| `/admin` always redirects you away, even after logging in | `ADMIN_PASSWORD` isn't set in `.env` — there's no default for it, unlike the viewer password |

---

## Part 2 — What This Is

A stateful AI market intelligence system for Silversea Media's BD/sales team. It scrapes sector- and business-domain-tagged sources across three countries, filters and synthesizes findings through a multi-pass LLM pipeline, and serves the result as a daily internal web dashboard with a feedback loop that measurably shapes future reports — all without fabricating connections that aren't actually in the source material.

**Countries:** Singapore, Vietnam, and Malaysia are all active today (152 active sources total, out of 177 configured — some are deliberately deactivated after failing scrape verification). Each has its own independent source list in `config/sources.json`, and the pipeline runs one country at a time via `--country`.

**Sectors vs. domains — two orthogonal tags, easy to conflate:** every source in `config/sources.json` carries both a **sector** (`gov_agencies`, `associations`, `customers`, `partners`, `competitors`, `general_news` — describes the source's *relationship* to Silversea) and one or more **business domains** (`BER` Built Environment, `EDU` Education, `GENERAL`, plus `RCC`/`HLS`/`MFG`/`CTE`/`PSS` for the wider Vietnam/Malaysia catalog — describes the *industry* the source covers). A pipeline run is scoped to one domain via `--domain`; within that run, results are still organized and reported by sector. The dashboard's nav currently surfaces three domain tabs (Education, Built Environment, General) per country — the five newer domains (`RCC`/`HLS`/`MFG`/`CTE`/`PSS`) are tagged in the source config and reachable via the pipeline, but their content is folded into the General tab (tagged with a small badge showing its real domain) rather than getting dedicated tabs of their own yet.

### Architecture

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

The extract-then-synthesize split exists because feeding a single large synthesis call too much raw content at once caused the model to silently drop most of the signal — splitting per-sector fixed that (signal count went from single digits to 65+ in testing).

**Stack:** Python, Flask + Jinja2, Tailwind CSS (CDN, no build step), Groq API (Llama 4 Scout 17B) for LLM calls, ChromaDB (via `sentence-transformers` embeddings) for the RAG feedback loop and report history.

**Auth:** two shared passwords (viewer, admin), not per-user accounts — matches the actual requirement (company-wide gated access, admin-only password rotation) without building account infrastructure nobody asked for.

**Feedback loop:** the dashboard's feedback form aggregates submissions, summarizes them via LLM into a digest, and stores that digest in ChromaDB — future pipeline runs retrieve it as context, so team feedback measurably changes what gets surfaced later, not just cosmetically. A weekly job compresses that week's daily reports into one summary to keep the vector store from growing unbounded.

**Opportunity scoring:** each identified opportunity is scored on 5 dimensions (Strategic Fit, Revenue Potential, Win Probability, Urgency, Intelligence Quality; 1-5 each, 25 max), with a Python-side clamp as a safety net against the LLM drifting outside that scale. Score bands: 20-25 = escalate to BD immediately, 13-19 = monitor, 0-12 = log only.

**Source suggestions:** the feedback form also accepts new source suggestions. An admin reviews them on `/admin` and approves or rejects; approving appends the source directly into `config/sources.json` as active — no separate registration step, it's picked up automatically by the next matching pipeline run.

**A local-LLM backend exists but isn't part of `main`.** `feature/002-local-llm-backend` adds a config-switchable Ollama-based backend as a free alternative to the Groq API. It's unmerged and its own smoke test has never produced a verified pass against a real model — treat it as experimental and check that branch's own notes before relying on it.

Full architectural decision history and current known issues are tracked internally (`.context/DECISIONS.md` / `.context/STATE.md`) — those files are intentionally excluded from this repo's tree; ask Alfonso if you need that history.
