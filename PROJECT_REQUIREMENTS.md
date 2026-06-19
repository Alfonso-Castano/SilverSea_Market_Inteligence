# PROJECT_REQUIREMENTS.md
## Silversea Market Intelligence System

*Rewritten 2026-06-19. Supersedes the original pipeline-only requirements document.*
*Placeholders marked `[TBD: reason]` must be resolved before the relevant phase begins.*

---

## Background

**Company:** Silversea Media — Singapore HQ, digital twin & immersive technology company (~2017)
**Products:** MetaTwin Object, MetaTwin Space, MetaTwin Immerse, MetaTwin Augment
**Industries served:** Real estate, education, retail, tourism, government, MICE
**Offices:** Singapore, Malaysia, Indonesia, Vietnam; partnerships in China, Europe, LatAm
**CRM:** Bitrix24

**The ask from the supervisor:**
> "Can build AI agent for the daily/weekly market report for each country and relevant business sectors?"

---

## Vision

An AI market intelligence system that monitors Singapore's built environment sector daily,
synthesizes signals into actionable intelligence for the BD/sales team, and learns over
time through user feedback. The system does not just aggregate news — it reasons about
what each signal means for Silversea specifically, weighted by accumulated company context
and past feedback.

Built fully for Singapore first. Architecture supports Malaysia, Indonesia, Vietnam in Phase 4.

---

## System Architecture

```
Data Layer (Phase 1)
  Scraper        → fetches content from sector-tagged sources (websites + LinkedIn)
  Filter         → keyword filtering, drops irrelevant content
  Sectors        → gov_agencies | associations | customers | partners | competitors

AI Brain (Phase 2)
  Summarizer     → compresses raw filtered content into structured signals
  Vector Store   → stores: past report summaries, feedback digests, company context
  RAG Analyst    → retrieves relevant context from vector store at inference time
                   → reasons about signals, scores opportunities, writes report sections
  Weekly Digest  → every 7 days, compresses week's reports into one summary,
                   replaces individual daily entries in vector store, pushes to Google Drive

Feedback Loop (Phase 2)
  Feedback Form  → embedded at end of each daily report (whole-company access)
  Aggregator     → collects feedback, summarizes it before ingestion (not raw append)
  Updater        → summarized feedback updates vector store context for next run

Output (Phase 3)
  Daily Report   → internal web dashboard, company servers, no authentication
  Weekly Summary → auto-pushed to Google Drive every 7 days
  Cadence        → daily at 09:00 SGT (01:00 UTC), GitHub Actions cron
```

---

## Phases

### Phase 1 — Foundation `[IN PROGRESS]`
**Goal:** Working daily pipeline with sector-based scraper and improved analysis quality.

**Done when:**
- `main.py` runs daily without errors
- Pulls from all 5 sector types (website placeholders + LinkedIn)
- Report quality scores ≥ 17/25 (up from 12/25 baseline)
- Opportunities section cites named programme, concrete action, source

**Tasks:** See `PLAN.md`

---

### Phase 2 — AI Brain `[PENDING]`
**Goal:** System learns from feedback and improves output over time.

**Done when:**
- Feedback submitted on Day 1 measurably changes what the report surfaces on Day 7
- Weekly summary auto-generated and pushed to Google Drive
- Vector store accumulates context without unbounded growth (weekly compression working)

**Key decisions locked:**
- Vector store: ChromaDB (local, free — see Tech Stack)
- LLM: Groq for dev/test, Claude Haiku 3.5 for production
- No AI agents in Phase 2 — RAG + context only. Agent behaviour (verification step) deferred to Phase 3+.
- AI enhancements confirmed for Phase 2: semantic deduplication, named entity extraction, source quality scoring

**`[TBD: embedding model]`** — what model converts text to vectors for retrieval. Decide at Phase 2 start.

---

### Phase 3 — Web Dashboard `[PENDING]`
**Goal:** Internal web application replacing static HTML output.

**Done when:**
- BD team and company read daily report from one internal URL
- Feedback form embedded and functional
- Weekly summary linked from dashboard

**Key decisions to make at Phase 3 start:**
- `[TBD: web framework]` — Flask vs FastAPI backend
- `[TBD: hosting details]` — company server specs, deployment method

---

### Phase 4 — Summary + Scale `[PENDING]`
**Goal:** Multi-country expansion + Google Drive integration.

**Done when:**
- Malaysia, Indonesia, Vietnam pipelines active with real sources
- Weekly summaries auto-land in Google Drive folder
- All placeholder sources replaced with real lists

---

## Tech Stack

| Layer | Tool | Status | Reason |
|---|---|---|---|
| Scraping | Python (`requests` + `BeautifulSoup`) | Confirmed | Free, no API dependency, sufficient for target sites |
| Scheduling | GitHub Actions (daily cron) | Confirmed | Free, no server required |
| LLM (testing) | Groq (Llama 3.3 70B) | Confirmed | Free tier — used for all development and testing. Swap to Claude when going to production. |
| LLM (production) | Claude Haiku 3.5 | Confirmed | ~$0.05–0.15/day at current volume. Better tool use than Groq for future agent work. Model is a config variable — trivial to swap Haiku → Sonnet for specific tasks. |
| Rate limiting | Hard cap per pipeline run | Confirmed | Safety measure: cap max LLM calls per run and per day. Prevents runaway loops and API abuse. |
| Vector Store | ChromaDB (local) | Confirmed | Free, no external API, runs on company server. Switch to Pinecone if multi-server setup required in Phase 3+. |
| Report hosting | Company servers (internal) | Confirmed | Vercel was prototype only; production on company infrastructure |
| Email | Gmail SMTP | Phase 1 only | For testing; company email in production |
| Weekly archive | Google Drive (auto-push) | Phase 4 | Auto-triggered, no manual step |
| Storage | GitHub repo | Confirmed for Phase 1 | No DB needed until vector store introduced in Phase 2 |

---

## Sources

Sources are organised by sector. Each source carries: `name`, `sector`, `type`, `url`, `active` flag.
The pipeline loops over active sources; inactive ones are ignored without code changes.

### Sector: `gov_agencies`
Priority government bodies — tenders, policy, regulatory signals.

| Name | URL | Status |
|---|---|---|
| BCA (Building and Construction Authority) | https://www.bca.gov.sg | Active |
| MND (Ministry of National Development) | https://www.mnd.gov.sg | Active |
| URA (Urban Redevelopment Authority) | https://www.ura.gov.sg | Active |
| HDB (Housing Development Board) | https://www.hdb.gov.sg | Active |
| GeBIZ (Government procurement portal) | https://www.gebiz.gov.sg | Active |
| Smart Nation / GovTech | https://www.smartnation.gov.sg | Active |
| JTC Corporation | https://www.jtc.gov.sg | Active |

### Sector: `associations`
Industry bodies — standards, events, market intelligence signals.

| Name | URL | Status |
|---|---|---|
| SGBC (Singapore Green Building Council) | https://www.sgbc.sg | Active |
| BCI Asia | https://www.bciasia.com | Active |
| Construction Plus Asia | https://www.construction-plus.com | Active |
| `[TBD: REDAS, SCEM, others]` | — | Placeholder — confirm with supervisor |

### Sector: `customers`
Known prospects and target accounts — project announcements, tenders, digital transformation signals.

| Name | URL | Status |
|---|---|---|
| CapitaLand | https://www.capitaland.com | Placeholder |
| Mapletree | https://www.mapletree.com.sg | Placeholder |
| Lendlease | https://www.lendlease.com/sg | Placeholder |
| SGH (Singapore General Hospital) | https://www.sgh.com.sg | Placeholder |
| NUS (National University of Singapore) | https://www.nus.edu.sg | Placeholder |
| NTU (Nanyang Technological University) | https://www.ntu.edu.sg | Placeholder |
| `[TBD: full list from supervisor]` | — | Placeholder |

### Sector: `partners`
Companies Silversea works with — partnership announcements, market moves.

| Name | URL | Status |
|---|---|---|
| `[TBD: partner list from supervisor]` | — | Placeholder — no confirmed list yet |

### Sector: `competitors`
Direct competitors — product launches, job postings, tenders, acquisitions.

| Name | URL | Status |
|---|---|---|
| Hiverlab | https://www.hiverlab.com | Active |
| G Element (Gelement) | https://www.gelement.com | Active |
| TwinLogic | Monitor via news search | Placeholder |
| TwinMatrix | Monitor via news search | Placeholder |
| Axomem | Monitor via news search | Placeholder |
| DataMesh | Monitor via news search | Placeholder |

### General news (for testing / filling gaps)
| Name | URL |
|---|---|
| PropertyGuru | https://www.propertyguru.com.sg |
| EdgeProp Singapore | https://www.edgeprop.sg |
| The Business Times | https://www.businesstimes.com.sg |

---

## Keywords for Filtering

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
    "construction technology", "contech", "smart construction",
    "BCA Green Mark", "IDD", "integrated digital delivery",

    # Government & tenders
    "GeBIZ", "ITQ", "ITT", "RFP", "tender", "public sector",
    "smart nation", "government digital", "built environment",

    # Competitor names
    "Hiverlab", "G Element", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh",

    # Customer / prospect names
    "JTC", "CapitaLand", "Mapletree", "Lendlease",
]
```

---

## AI Brain

*This section describes the intended behaviour. Implementation specifics are decided at Phase 2 start.*

### What it is
The AI brain is a reasoning layer that sits between raw scraped content and the output report.
It does not just summarise — it interprets signals through accumulated company context: what
Silversea sells, who the target accounts are, what opportunities the team has flagged in the
past, and what the feedback has said matters most.

### What goes into the vector store
- **Past report summaries** — compressed weekly summaries (not raw daily reports)
- **Feedback digests** — summarised feedback from the team, not raw form submissions
- **Company context seed** — a one-time-written document describing Silversea's products,
  target sectors, known prospects, and current BD priorities (manually maintained by supervisor)
- **Named entities** — extracted structured data (companies, amounts, dates, tender numbers) stored
  alongside prose for better retrieval quality

### Phase 2 AI enhancements (confirmed)
Three enhancements beyond base RAG, applied before signals reach the analyst:

1. **Semantic deduplication** — embed all signals and detect near-duplicates across sources (same story covered by multiple outlets). Merge into one signal before analyst sees it. Reduces noise.

2. **Named entity extraction** — extract structured data from each signal: company names, dollar amounts, dates, tender numbers, project names. Store as structured metadata alongside prose in the vector store. Better retrieval, better analyst context.

3. **Source quality scoring** — log which sources produce signals that make it into the Opportunities section vs. get dropped. Build a quality score per source over time. Use it to weight retrieval. Passive learning — no extra LLM call needed.

### Safety: rate limiting
A hard cap is applied per pipeline run and per day:
- Max N LLM calls per run (prevents runaway loops)
- Max N runs per day (prevents API abuse or misconfigured cron)
- If cap is hit, pipeline logs the breach and exits cleanly — does not silently drop signals

### How it works at inference time (RAG)
1. Daily scraper runs and produces filtered, structured signals per sector
2. Analyst retrieves relevant context from vector store (past priorities, feedback)
3. Analyst reasons: "Given what we know and what the team has told us, which of these signals
   matters most and why?"
4. Output: scored, sector-organised daily report with named opportunities and concrete actions

### Weekly compression
Every 7 days, the system:
1. Generates a weekly summary (synthesises 7 daily reports into one document)
2. Pushes the summary to Google Drive (auto, no manual step)
3. Replaces the 7 individual report entries in the vector store with the single compressed summary
   (prevents unbounded growth)

---

## Feedback System

*Exact form fields are `[TBD: discuss with Alfonso]`. Design principles are confirmed.*

### Design principles
- Form is embedded at the end of each daily report
- Accessible to the whole company (no login)
- Fields must be structured — not free-text-only — so they can be efficiently processed
- Raw submissions are **not** injected directly into the vector store
- Instead: submissions are aggregated, then an LLM summarises them into a short feedback digest
- The digest (not the raw submissions) is what updates the vector store
- This prevents context bloat and keeps the brain's memory clean and meaningful

### What the feedback should capture (fields TBD)
The form needs to answer at least these questions for the system:
- Which signals or topics were most useful this week?
- Which were least useful / noise?
- Any priority shifts the team wants to signal (e.g. "focus more on hospitals")?

`[TBD: finalise exact field types — structured ratings, dropdowns, or short text fields]`

---

## Report Structure (Daily)

Each daily report contains:

1. **Executive Summary** — 3–5 bullets, what matters most today
2. **Signals by Sector** — organised by `gov_agencies | associations | customers | partners | competitors`
3. **Opportunities** — scored leads; each entry must include: named programme or contact, concrete action, deadline or window, source citation
4. **What This Means for Silversea** — 2–3 synthesis bullets the CEO can act on

### Scoring Model (per opportunity)

| Dimension | Score /5 | What it measures |
|---|---|---|
| Strategic Fit | /5 | Alignment with Silversea's products and target sectors |
| Revenue Potential | /5 | Estimated deal size / contract value |
| Win Probability | /5 | Likelihood Silversea can compete and win |
| Urgency | /5 | How time-sensitive the opportunity is |
| Intelligence Quality | /5 | How reliable and complete the source information is |

Total /25. Thresholds: 20–25 = escalate to BD immediately | 13–19 = monitor | 0–12 = log

---

## Dashboard (Phase 3)

- Internal web app hosted on company servers
- No authentication (internal network access)
- Single view — same for all users (BD team, management, CEO)
- Shows: today's daily report + link to weekly summary
- Feedback form embedded at bottom of each report
- No manual re-run trigger — system runs on schedule only

---

## Country Scalability

Architecture supports multi-country from Phase 1. Each country is a config entry with an
`active` flag. Adding Malaysia = adding one config block and flipping `active: True`.

Active in Phase 1: Singapore only.
Phases 2–3: Singapore only.
Phase 4: Malaysia, Indonesia, Vietnam added.

```python
COUNTRIES = [
    { "name": "Singapore", "code": "SG", "active": True,  "sectors": {...} },
    { "name": "Malaysia",  "code": "MY", "active": False, "sectors": {} },  # Phase 4
    { "name": "Indonesia", "code": "ID", "active": False, "sectors": {} },  # Phase 4
    { "name": "Vietnam",   "code": "VN", "active": False, "sectors": {} },  # Phase 4
]
```

---

## Environment Variables

```
ANTHROPIC_API_KEY=        # Claude API (if Claude is chosen as LLM)
GROQ_API_KEY=             # Groq API (if Groq/Llama remains)
GMAIL_USER=               # Sender email for Phase 1 testing
GMAIL_APP_PASSWORD=       # Gmail app password
RECIPIENT_EMAILS=         # Comma-separated recipients (Phase 1 testing)
GOOGLE_DRIVE_FOLDER_ID=   # Target Drive folder for weekly summaries (Phase 4)
[TBD: vector store keys]  # Pinecone API key if Pinecone chosen; none needed for ChromaDB
```

All secrets go in GitHub Actions secrets — never committed to repo.

---

## Open Items

| Item | Blocks | Owner |
|---|---|---|
| Embedding model choice | Phase 2 start | Alfonso |
| Feedback form fields (exact field types) | Phase 2 feedback pipeline | Alfonso + supervisor |
| Full customer source list | Phase 1 placeholder → real sources in Phase 4 | Supervisor |
| Full partner source list | Phase 1 placeholder → real sources in Phase 4 | Supervisor |
| Association list (REDAS, SCEM, others?) | Phase 1 placeholder | Supervisor |
| Production email recipients | Phase 4 | Ms. Mok |
| Company server specs / deployment method | Phase 3 | Supervisor / IT |
| Google Drive folder for weekly summaries | Phase 4 | Alfonso |
