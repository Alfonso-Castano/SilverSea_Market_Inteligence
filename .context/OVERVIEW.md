# Silversea Market Intelligence System

## What This Is

A stateful AI market intelligence system for Silversea Media's BD/sales team. It scrapes sector-tagged sources (government agencies, industry associations, customers, partners, competitors, general news), filters and synthesizes findings through a multi-pass LLM pipeline, and serves the result as a daily internal web dashboard (Flask) with a RAG-based feedback loop — user feedback measurably changes what future reports surface. Built fully for Singapore first; `--domain` and `--country` scaffolding exists for future expansion (BER/EDU/GENERAL industry domains now; MY/VN/ID countries later).

This started as a simpler weekly scrape-and-email pipeline (see `PROJECT_REQUIREMENTS.md`, superseded 2026-06) and grew into the current architecture through several rounds of supervisor feedback — see `.context/DECISIONS.md` for the full history of pivots.

## Core Value

A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

## Scope

### In Scope
- Singapore built-environment (BER) sector coverage across 6 relationship-sectors (`gov_agencies`, `associations`, `customers`, `partners`, `competitors`, `general_news`)
- Daily pipeline cadence (was weekly originally; changed to daily per supervisor direction)
- Multi-pass LLM analysis (per-sector extraction → per-sector synthesis → summary) to avoid signal loss under small-model context limits
- RAG feedback loop: team feedback → LLM-summarized digest → ChromaDB → shapes next report
- Weekly summarization: compresses 7 daily reports into one, replaces individual entries in the vector store (prevents unbounded growth)
- Two-surface Flask dashboard: polished report view (BD/sales-facing) + internals/observability view (maintainer-facing: vector store contents, source scores, feedback digests, run metadata)
- Viewer + admin password-gated access (shared static passwords, not per-user accounts)
- Source-suggestion flow: team can propose new sources via the feedback form; admin approves/rejects into `config/sources.json`
- Multi-domain tagging (`BER`/`EDU`/`GENERAL`) per source, and `--country` pipeline scaffolding, both additive and not yet exercised with real non-SG data
- Opportunity scoring on a locked 5-dimension rubric (strategic fit, revenue potential, win probability, urgency, intelligence quality; each /5, total /25) with a Python-side clamp as a safety net against LLM scale drift
- PDF export of the report view

### Explicitly Out of Scope
- **LinkedIn / Facebook scraping** — no free, no-auth method survives anti-bot measures; revisit only if a paid scraping API (Apify, PhantomBuster) gets budget approval.
- **Fine-tuning** — prompt-time RAG retrieval only, no model fine-tuning, to keep the system simple and swappable.
- **AI agents / agentic verification steps** — considered for Phase 3+ but never built; adds per-run cost and complexity without proportional gain at current scale.
- **Per-user authentication / accounts** — two shared static passwords (viewer, admin) satisfy the actual requirement (company-wide access, password-rotation restricted to CEO/technical roles) without building real user-account infrastructure.
- **Real MY/VN/ID source lists** — country scaffolding (`--country` flag, ChromaDB metadata filter) exists, but no real sources are populated for any country besides SG.
- **Google Drive auto-push for weekly summaries** — deferred repeatedly; source lists for the feature weren't finalized when it would have been built, and it's been superseded in priority by other requests each round.
- **Production deployment to company servers** — the app currently runs locally only; production hosting/deployment was never completed.

## Context

**Company:** Silversea Media — Singapore HQ, digital twin & immersive technology company (est. ~2017). Industries served: real estate, education, retail, tourism, government, MICE. Offices in Singapore, Malaysia, Indonesia, Vietnam; partnerships in China, Europe, LatAm. CRM: Bitrix24.

**The original ask (from Alfonso's supervisor):** *"Can build AI agent for the daily/weekly market report for each country and relevant business sectors?"*

**Product framing has changed twice.** The system originally referenced a placeholder 4-product "MetaTwin" suite (Object/Space/Immerse/Augment), corrected in 2026-06-23 to Silversea's real "SpatioX" suite (Twin/Ops/Audit/Walk), then rebuilt again in 2026-07 around Silversea's actual ~14-solution catalog spanning all 7 of the supervisor's business sectors (EDU, BER, MFG, HLS, RCC, CTE, PSS) — see `docs/Copy of Business Sector _ed01.pdf`. Some legacy SpatioX references may still linger in `data/company_context.md` outside the rebuilt "Products by Business Sector" section — flagged as an open cleanup item, not yet resolved.

**The pipeline's relationship-sector taxonomy (`gov_agencies`/`associations`/`customers`/`partners`/`competitors`/`general_news`) is intentionally distinct from industry `domain` tagging (`BER`/`EDU`/`GENERAL`).** Sector describes who the signal comes from relative to Silversea; domain describes what industry it covers. Both are orthogonal, per-source fields in `config/sources.json`.

**This is a solo internship project** (Alfonso), reviewed periodically by a supervisor whose feedback has driven most major pivots (weekly→daily cadence, Vercel→company-server hosting direction, sector reorganization, source-list expansion, the "Supervisor Feedback Round 2" 8-topic round covering auth/scoring/domains/countries). Sessions have historically ended by updating context files by hand; this project has just adopted a structured `.context/` + `/feature-*` workflow to replace that.

## Constraints

- **Budget**: Alfonso is on a personal Claude Code plan — token efficiency matters in every session, not just this migration.
- **LLM quota (dev)**: Groq free tier — 100k tokens/day (TPD), tiered TPM limits depending on model. The pipeline has been redesigned more than once specifically to fit under these limits (multi-pass extraction/synthesis split, `llama-4-scout-17b` for both stages after `gpt-oss-120b` proved unusable at the synthesis token budget). A full `py main.py` run burns real daily quota — don't run it speculatively.
- **LLM strategy**: Groq (free) for all development/testing; Claude Haiku 3.5 planned for production once the pipeline (scraper, filter, RAG, feedback) is hardened and verified. This switch has been deliberately deferred multiple times, not forgotten.
- **No paid scraping infra**: Apify/PhantomBuster-class tools are out of reach without supervisor budget approval — shapes the LinkedIn/Facebook exclusion above.
- **No dedicated server yet**: production hosting was scoped for "company servers" from Phase 3 onward but never actually provisioned; the app still runs locally.
- **Tech stack is deliberately boring**: Flask + Jinja2 + Tailwind/Chart.js via CDN — no SPA, no npm/build step, no FastAPI — chosen because the app is batch-driven (one pipeline run/day) and a JS framework would add build tooling for no capability gain.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Plain Python (`requests`/BeautifulSoup) + Scrapling (stealth/dynamic fetchers) over Firecrawl/paid scraping | Free; Scrapling added later specifically to unblock 403/JS-only sources without introducing a paid dependency |
| ChromaDB (local, free) as the vector store | No external API/cost; runs on whatever host the app runs on; revisit only if multi-server architecture is required |
| No database beyond ChromaDB — JSON files + git as storage | MVP scope never needed historical querying beyond what the vector store already provides |
| Flask + Jinja2 server-rendered dashboard, no SPA | Pipeline is batch-driven (once/day); a JS framework buys nothing here and adds build tooling |
| Multi-pass analyst architecture (per-sector extract → per-sector synthesize → summary) | A single monolithic synthesis call on a 17B model dropped ~80-90% of extracted signals; splitting the call per sector fixed information density (signal count went 7 → 65 over several iterations) |
| Two shared static passwords (viewer, admin) instead of real accounts | Matches the actual requirement (company-wide gated access, admin-only password rotation) without building unneeded account infrastructure |
| `config/sources.json` (not `.py`) as the source-of-truth | The admin source-approval flow needs safe programmatic read-modify-write; templating/AST-editing Python source from a request handler was judged too fragile |

Full, dated rationale for every architectural pivot — including several that were tried and reverted (e.g. the `gpt-oss-120b` split-model attempt) — lives in `.context/DECISIONS.md`.

## Environment Variables

All secrets go in GitHub Actions secrets / a local `.env` — never committed to the repo.

```
GROQ_API_KEY=             # Groq API — current dev/test LLM
ANTHROPIC_API_KEY=        # Claude API — for the planned Claude Haiku production switch (not yet made)
GMAIL_USER=                # Sender email, Phase 1 testing only
GMAIL_APP_PASSWORD=        # Gmail app password
RECIPIENT_EMAILS=          # Comma-separated recipients, Phase 1 testing only
GOOGLE_DRIVE_FOLDER_ID=    # Target Drive folder for weekly summaries — feature never built, var unused
VIEWER_PASSWORD=           # Seeds data/viewer_password.txt on first run; defaults to "changeme" if unset
ADMIN_PASSWORD=            # Gates /admin; defaults to empty string if unset — see known-bug note in STATE.md
```

## Opportunity Scoring Model

Each opportunity is scored on 5 dimensions (1-5 each, `total_score` capped at 25 by a Python-side clamp — see the A1 decision in `.context/DECISIONS.md`): Strategic Fit, Revenue Potential, Win Probability, Urgency, Intelligence Quality.

**Score-band interpretation:** 20-25 = escalate to BD immediately | 13-19 = monitor | 0-12 = log only. (This banding is original guidance from `PROJECT_REQUIREMENTS.md`; the rubric and clamp were rebuilt in Supervisor Feedback Round 2, but the interpretation thresholds were never revisited and presumably still apply.)

---
*Migrated to `.context/` structure: 2026-07-08. Originally initiated 2026-06.*
