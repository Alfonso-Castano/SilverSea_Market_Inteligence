# PROJECT_REQUIREMENTS.md
## Market Intelligence Pipeline — Silversea Media

---

## Background

**Company:** Silversea Media — Singapore HQ, digital twin & immersive technology company (~2017).
**Products:** MetaTwin Object, MetaTwin Space, MetaTwin Immerse, MetaTwin Augment
**Industries served:** Real estate, education, retail, tourism, government, MICE
**Offices:** Singapore, Malaysia, Indonesia, Vietnam; partnerships in China, Europe, LatAm
**CRM:** Bitrix24

**The ask from the supervisor:**
> "Can build AI agent for the daily/weekly market report for each country and relevant business sectors?"

---

## What We're Building

An automated pipeline that:
1. Scrapes Singapore's built environment / construction / smart FM web sources weekly
2. Filters and scores the content for relevance to Silversea
3. Synthesizes findings into a structured intelligence report using Claude API
4. Delivers the report as a live HTML page (Vercel) and an email digest

**Who reads it:** The entire company — the CEO definitely reads it. Output must be
executive-readable: clear, concise, and actionable.

**What "actionable" means here:** Not just a news dump. The report should tell the team
*what it means for Silversea* — e.g. "JTC announced a $40M smart FM tender. This is
directly in Silversea's wheelhouse. Here's why." Sales signals, competitor moves,
and policy changes that the BD team can act on.

---

## Scope

**Phase 1 (this internship):** Singapore only
**Future phases:** Malaysia, Indonesia, Vietnam — the codebase must be structured to
support this from day one (see Country Scalability below)

**Cadence:** Weekly — runs every Monday morning SGT via GitHub Actions cron

**Does NOT need to:** feed into Bitrix24 CRM, require login/authentication anywhere,
handle real-time monitoring

---

## Tech Stack

| Layer | Tool | Reason |
|---|---|---|
| Scraping | Plain Python (`requests` + `BeautifulSoup`) | Free, no API dependency, sufficient for target sites |
| Scheduling | GitHub Actions (cron) | Free, zero server required |
| LLM processing | Claude API (Haiku model) | ~$0.10–0.30/run, nearly free at this scale |
| Report hosting | Vercel (free tier) | Clean URL, auto-deploys from GitHub push |
| Email delivery | Gmail SMTP (free) | Zero cost, sufficient for MVP |
| Storage | GitHub repo | Free, version-controlled, no DB needed |

**If scraping proves insufficient:** Firecrawl (free tier: 500 credits/month) can be
added later. Start without it.

**Cost target:** $0/month for MVP. Max $5–10/month if the system scales.

---

## Repo Structure

```
market-intel/
├── CLAUDE.md                    # AI agent instructions
├── PROJECT_REQUIREMENTS.md      # This file
├── CONTEXT.md                   # Architectural decisions log
├── STATE.md                     # Current session state / progress
├── main.py                      # Runs the full pipeline end-to-end
├── config/
│   └── sources.py               # URLs, keywords, country configs (see below)
├── pipeline/
│   ├── scraper.py               # Fetches raw content from URLs
│   ├── filter.py                # Keyword filtering
│   ├── analyst.py               # Claude API synthesis and scoring
│   ├── report.py                # HTML report generation
│   └── emailer.py               # Email digest sender
├── output/
│   └── index.html               # What Vercel serves (auto-generated)
├── .github/
│   └── workflows/
│       └── weekly.yml           # GitHub Actions cron job
└── README.md
```

---

## Country Scalability

`config/sources.py` must be structured as a list of country configs from day one:

```python
COUNTRIES = [
    {
        "name": "Singapore",
        "code": "SG",
        "active": True,
        "sources": [...],
        "keywords": [...],
        "entities": {...}
    },
    # Future:
    # { "name": "Malaysia", "code": "MY", "active": False, ... },
    # { "name": "Indonesia", "code": "ID", "active": False, ... },
]
```

The pipeline loops over `active` countries. Adding Malaysia later = adding one entry
and flipping `active` to True.

---

## Report Structure

Each weekly report should contain these sections:

1. **Executive Summary** — 3–5 bullet points, what matters most this week
2. **Market Signals** — what's happening in SG's built environment sector
3. **Government & Policy** — BCA, MND, URA, HDB tenders and announcements
4. **Competitor Activity** — what Hiverlab, Gelement, and others are doing
5. **Opportunities** — scored leads or projects Silversea could pursue
6. **What This Means for Silversea** — 2–3 synthesis bullets the CEO can act on

The last two sections are the most important — they're what makes the report
actionable rather than just informational.

---

## Scoring Model (from existing prototype)

Opportunities are scored on 5 dimensions (5 points each, 25 points total):

| Dimension | What it measures |
|---|---|
| **Strategic Fit** | How well it aligns with Silversea's products and target sectors |
| **Revenue Potential** | Estimated deal size / contract value |
| **Win Probability** | Likelihood Silversea can compete and win |
| **Urgency** | How time-sensitive the opportunity is |
| **Intelligence Quality** | How reliable and complete the source information is |

Score interpretation:
- 20–25: High priority — escalate to BD team immediately
- 13–19: Medium priority — monitor and prepare
- 0–12: Low priority — log and revisit

This scoring model should be embedded in the analyst.py system prompt for Claude.

---

## Sources to Monitor (Singapore)

Seeded from the existing prototype's source-monitoring-plan. These are the priority sources:

### Government & Regulatory
- BCA (Building and Construction Authority): https://www.bca.gov.sg
- MND (Ministry of National Development): https://www.mnd.gov.sg
- URA (Urban Redevelopment Authority): https://www.ura.gov.sg
- HDB (Housing Development Board): https://www.hdb.gov.sg
- GeBIZ (Government procurement portal): https://www.gebiz.gov.sg
- Smart Nation initiatives: https://www.smartnation.gov.sg

### Industry News
- BCI Asia: https://www.bciasia.com
- Construction Plus Asia: https://www.construction-plus.com
- PropertyGuru: https://www.propertyguru.com.sg
- EdgeProp Singapore: https://www.edgeprop.sg
- The Business Times (property/construction): https://www.businesstimes.com.sg

### Competitor Monitoring
Track these companies for news, job postings, tenders, and announcements:
- **Hiverlab** — https://www.hiverlab.com (direct XR/digital twin competitor)
- **Gelement** — https://www.gelement.com (digital twin competitor)
- **TwinLogic** — monitor via news search
- **TwinMatrix** — monitor via news search
- **Axomem** — monitor via news search
- **DataMesh** — monitor via news search

### Key Customer / Prospect Monitoring
Track for project announcements, tenders, and digital transformation signals:
- JTC Corporation: https://www.jtc.gov.sg
- CapitaLand: https://www.capitaland.com
- Hospitals (SGH, NUH, Tan Tock Seng) — monitor for smart FM / digital twin tenders
- Universities (NUS, NTU, SMU) — monitor for campus tech projects

---

## Key Entities (Seed Data from Wiki)

### Government Bodies
- **BCA** — Building and Construction Authority. Regulates construction, sets green building standards (BCA Green Mark). Key source of tenders and policy signals.
- **MND** — Ministry of National Development. Parent ministry for BCA, HDB, URA. Sets long-term land use and built environment policy.
- **URA** — Urban Redevelopment Authority. Master plan, zoning, development approvals.
- **HDB** — Housing Development Board. Public housing — smart home and smart estate digital twin opportunities.
- **SGBC** — Singapore Green Building Council. Green certification, sustainability policy signals.

### Priority Customers / Prospects
- **JTC Corporation** — industrial estates, science parks. Active in smart FM and digital twin.
- **CapitaLand** — largest real estate developer in SG. Strong sustainability push = digital twin opportunity.
- **Mapletree** — large commercial/industrial REIT. Smart building initiatives.
- **Lendlease** — commercial developments, sustainability focus.
- **Hospitals** — SGH, NUH, TTSH, Alexandra. Smart FM / maintenance digital twin potential.
- **Universities** — NUS, NTU, SMU. Campus digital twin and immersive learning.

### Competitors
- **Hiverlab** — SG-based XR company. Direct competitor in immersive/virtual tours. Strong in tourism and events.
- **Gelement** — SG-based digital twin company. Closest architectural competitor to Silversea.
- **TwinLogic / TwinMatrix** — smaller SG digital twin players. Monitor for partnership or acquisition signals.
- **Axomem / DataMesh** — regional players. Monitor for market entry signals.

---

## Key Keywords for Filtering

```python
SINGAPORE_KEYWORDS = [
    # Digital twin & immersive tech
    "digital twin", "virtual tour", "3D scan", "BIM", "point cloud",
    "immersive", "XR", "extended reality", "virtual reality", "augmented reality",
    "metaverse", "spatial computing",

    # Smart FM & buildings
    "smart building", "smart FM", "facilities management", "building management",
    "proptech", "smart estate", "intelligent building", "building automation",

    # Construction & development
    "construction technology", "contech", "greenfield", "smart construction",
    "BCA Green Mark", "IDD", "integrated digital delivery",

    # Government & tenders
    "GeBIZ", "ITQ", "ITT", "RFP", "tender", "public sector",
    "smart nation", "government digital", "built environment",

    # Competitor names
    "Hiverlab", "Gelement", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh",

    # Customer names
    "JTC", "CapitaLand", "Mapletree", "Lendlease", "HDB estate",
]
```

---

## Environment Variables Required

```
ANTHROPIC_API_KEY=        # Claude API for analyst.py
GMAIL_USER=               # Sender email for emailer.py
GMAIL_APP_PASSWORD=        # Gmail app password (not account password)
RECIPIENT_EMAILS=          # Comma-separated list of report recipients
```

These go in GitHub Actions secrets (never committed to repo).

---

## MVP Definition

The MVP is complete when:
- [ ] `main.py` runs end-to-end without errors
- [ ] At least 5 sources are scraped successfully
- [ ] Filtering removes clearly irrelevant content
- [ ] Claude API produces a structured report with all 6 sections
- [ ] HTML report is generated and served on Vercel
- [ ] Email digest is sent to test recipient (Alfonso's email)
- [ ] GitHub Actions cron triggers the pipeline successfully

**Not required for MVP:**
- Perfect scraping of every source
- Polished HTML design
- Competitor deep-dive pages
- Multi-country support (structure for it, don't build it)
