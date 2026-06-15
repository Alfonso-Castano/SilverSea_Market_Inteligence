# CONTEXT.md — Architectural Decisions Log

*This file records key decisions and their rationale. Append new decisions as they're made.
Never delete entries — this is a permanent record. Read this at the start of every session.*

---

## Decision Log

### [2026-06] Initial Architecture

**Decision:** Plain Python pipeline (requests + BeautifulSoup) over n8n or Firecrawl
**Reason:** Free, zero external dependencies for MVP, sufficient for the ~15 target sources.
Firecrawl can be added later if JavaScript-heavy sites prove unscrapable with plain requests.

**Decision:** GitHub Actions for scheduling over a hosted server or n8n cloud
**Reason:** Completely free, no server to maintain, integrates naturally with GitHub repo,
cron syntax is straightforward for a weekly run.

**Decision:** Vercel for report hosting over GitHub Pages
**Reason:** Cleaner URL, easier custom domain migration later, same auto-deploy-from-GitHub
workflow, still free. When supervisor approves, can migrate to Alibaba Cloud OSS or their
own servers with minimal config change.

**Decision:** Claude Haiku (not Sonnet/Opus) for analyst.py
**Reason:** Cost. At ~15-30 articles per week, Haiku costs ~$0.10-0.30/run vs $1-3 for Sonnet.
Upgrade to Sonnet if report quality is insufficient.

**Decision:** Country-config structure from day one even though only SG is active
**Reason:** Supervisor's original brief mentioned SG, MY, ID, VN. Restructuring later is
expensive. One `active: True/False` flag per country costs nothing now.

**Decision:** No database — GitHub repo as storage
**Reason:** MVP only. HTML output is ephemeral (regenerated weekly). No historical querying
needed for MVP. Add SQLite or similar if archiving past reports becomes a requirement.

**Decision:** Gmail SMTP for email delivery
**Reason:** Free, no new service to sign up for. Alfonso's personal Gmail used for testing;
company email swapped in for production.

---

## Open Questions
*(Remove entries when resolved, note the resolution)*

- What email address(es) should receive the production report? → TBD, confirm with Ms. Mok
- Should past reports be archived/browsable? → Not required for MVP
- Any sources behind login/paywall that need special handling? → Assume no for MVP
- Final approval on Vercel vs Alibaba Cloud OSS for hosting? → Vercel for prototype,
  OSS when supervisor greenlight received
