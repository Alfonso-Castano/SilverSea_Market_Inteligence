# pipeline/analyst.py — Multi-pass Groq API synthesis and opportunity scoring
import json
import os
import time
import datetime
from groq import Groq

try:
    from pipeline.vectorstore import query, add_documents, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
    RAG_ENABLED = True
except Exception:
    RAG_ENABLED = False

MODEL = "llama-3.3-70b-versatile"
CALL_DELAY = 25
MIN_CONTENT_CHARS = 150

SECTOR_LABELS = {
    "gov_agencies": "Government & Agencies",
    "associations": "Industry Associations",
    "customers": "Customers",
    "partners": "Partners",
    "competitors": "Competitors",
    "general_news": "General News",
}

SECTOR_EXTRACT_PROMPT = """You are an extraction assistant for a market intelligence pipeline.
You will be given raw scraped content from one sector's sources. Your only job is to list
every named, concrete signal found in the text — do not summarize, interpret, or generalize.

For each source, list every instance of:
- Partnerships, MOUs, joint ventures, alliances (name both parties)
- Product or service launches (name the product and what it does)
- Case studies or project outcomes with metrics (name the client, project, and numbers)
- Tenders, RFPs, procurement notices (name the agency, scope, and deadline if stated)
- Events, conferences, exhibitions (name the event and date if stated)
- Strategic moves: expansions, funding, leadership changes, new offices, certifications
- Awards, recognitions, or industry endorsements (name the award and recipient)

GROUNDING RULE: Only state what is explicitly in the text. Do not infer relationships,
dates, or amounts that are not written. If a source has no concrete named signal, write
"No actionable signals" for that source — do not invent filler content.

Format as a flat list grouped by source name. Be specific: include company names, numbers,
dates, and programme names exactly as they appear in the source. This is a private internal
extraction step, not the final report — write tersely, no preamble, no conclusion."""

SYNTHESIS_PROMPT = """You are a market intelligence analyst for Silversea Media, a Singapore-based
digital twin and immersive technology company.

GROUNDING RULE: You have no knowledge beyond the extracted signals provided below. Treat
them as the complete and only truth. Never infer, estimate, or fabricate any fact, date,
deadline, dollar amount, or programme name that does not appear verbatim in the extracted
signals. If information is not explicitly stated there, it does not exist for this report.

Company context (use only for relevance filtering, not for generating claims):
- Products:
  * SpatioX Twin — Digital Twin platform, live dashboard, high-fidelity 3D visualization
  * SpatioX Ops — Smart Facility Management: workflow/asset management, IoT/CCTV/access control integration
  * SpatioX Audit — Smart virtual inspection (property TOP inspection)
  * SpatioX Walk — 3D/VR virtual tour, WebGL virtual walkthrough
- Sectors served: real estate, education, retail, tourism, government, MICE
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, spatial computing, smart FM

Produce a structured report with exactly these four sections:

1. EXECUTIVE SUMMARY — 3-5 bullet points, most important signals across all sectors

2. SIGNALS BY SECTOR — include EVERY sector from the intelligence below.
   CRITICAL: Every extracted signal that names a specific company, partnership, product,
   event, or metric MUST appear in this section as its own bullet point. Do not collapse
   multiple signals into one generic sentence like "X provides updates." If the extraction
   lists 5 partnerships for G Element, all 5 must appear. If DataMesh has 3 product launches,
   all 3 must appear. The BD team reads this for competitive intelligence — detail is the
   value, not brevity.
   - Each named programme, initiative, partnership, or tender is its own bullet
   - Do not combine information from two different sources into a single claim
   - For each signal, name both parties in a partnership and the specific scope
   - Include all metrics, dates, and programme names exactly as extracted

3. OPPORTUNITIES — scored leads Silversea could pursue.

   RELEVANCE GATE: Does the signal explicitly mention digital twin, BIM, 3D scanning,
   XR/spatial computing, smart FM, smart building, building automation, or proptech?
   If the connection to Silversea's products is inferred, it is NOT an opportunity.

   For each opportunity that passes the gate:
   - Source quote: the specific signal text that establishes relevance
   - Named entry point: the programme, tender, or initiative
   - Concrete action: what Silversea should do
   - Deadline: as stated, or "No deadline found in source"
   - Product fit: which SpatioX product applies and why

   NEVER invent a deadline or contact channel not found in the signals.
   Zero opportunities is a correct output when nothing passes the gate.

   Score each opportunity out of 25:
   - Strategic Fit (0-5), Revenue Potential (0-5), Win Probability (0-5),
     Urgency (0-5), Intelligence Quality (0-5)
   Score interpretation: 20-25 = High | 13-19 = Medium | 0-12 = Low

   NEGATIVE EXAMPLE — do NOT generate opportunities like this:
   Signal says: "URA awarded tender for residential sale site at Peck Hay Road"
   Wrong: "Submit proposal for digital twin solutions for Peck Hay Road by 30 June"
   Why wrong: Residential land sale, no digital twin/BIM/smart building mention.

4. WHAT THIS MEANS FOR SILVERSEA — 2-3 synthesis bullets the CEO can act on immediately

EXCLUDE from the entire report:
- Residential property data (home sales, condo launches, land tenders for housing)
- General economic indicators with no explicit tech connection
- Signals where the link to digital twin / smart FM / BIM is your inference, not the source's

Write in clear, concise, executive-readable English. Name specific companies, programmes,
and amounts only when they appear in the extracted signals.

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
Every score field is an integer 0-5. "total_score" is the sum (0-25)."""


def _build_rag_context(filtered_results: list) -> str:
    """Query the vector store for company context, feedback priorities, and past
    report themes relevant to today's sources."""
    if not RAG_ENABLED or not filtered_results:
        return ""

    longest = sorted(filtered_results, key=lambda r: len(r.get("content", "")), reverse=True)[:3]
    query_text = " ".join(r["content"][:200] for r in longest)

    sections = []
    for collection_name, label in (
        (COMPANY_CONTEXT, "Company context"),
        (FEEDBACK_DIGESTS, "Recent feedback priorities"),
        (REPORT_HISTORY, "Past report themes"),
    ):
        try:
            result = query(collection_name, query_text, n_results=3)
        except Exception:
            continue
        docs = (result.get("documents") or [[]])[0]
        if not docs:
            continue
        bullets = "\n".join(f"- {doc}" for doc in docs)
        sections.append(f"{label}:\n{bullets}")

    if not sections:
        return ""

    return (
        "ACCUMULATED CONTEXT (use for relevance filtering and priority weighting — "
        "NOT as source material):\n\n"
        + "\n\n".join(sections)
        + "\n\n---\n\n"
    )


def _extract_sector(client, sector_name: str, sources: list) -> str:
    """Phase 1: Extract signals from one sector's sources via a focused LLM call."""
    label = SECTOR_LABELS.get(sector_name, sector_name.replace("_", " ").title())

    source_blocks = []
    for r in sources:
        name = r.get("name") or (r.get("names") or ["Unknown"])[0]
        url = r.get("url") or (r.get("urls") or [""])[0]
        source_blocks.append(f"### {name}\nURL: {url}\n\n{r['content']}")

    user_message = f"Sector: {label}\n\n" + "\n\n---\n\n".join(source_blocks)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SECTOR_EXTRACT_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"    Error extracting {sector_name}: {e}")
        return f"**{label}**: Extraction failed — {e}"


def analyse(filtered_results: list, country: dict) -> dict:
    """Multi-pass analysis: extract signals per sector, then synthesize into structured JSON report."""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    substantive = [r for r in filtered_results if len(r.get("content", "")) >= MIN_CONTENT_CHARS]

    sectors = {}
    for r in substantive:
        sectors.setdefault(r.get("sector", "unknown"), []).append(r)

    # Phase 1: per-sector signal extraction
    sector_reports = {}
    for i, (sector_name, sources) in enumerate(sectors.items()):
        label = SECTOR_LABELS.get(sector_name, sector_name)
        print(f"    Extracting {label} ({len(sources)} sources)...")
        sector_reports[sector_name] = _extract_sector(client, sector_name, sources)
        if i < len(sectors) - 1:
            time.sleep(CALL_DELAY)

    # Phase 2: synthesis into final report
    print("    Synthesizing report...")
    time.sleep(CALL_DELAY)

    rag_context = _build_rag_context(filtered_results)

    intelligence_sections = []
    for sector_name, report in sector_reports.items():
        label = SECTOR_LABELS.get(sector_name, sector_name)
        intelligence_sections.append(f"=== {label.upper()} ===\n{report}")

    user_message = (
        rag_context
        + f"Country: {country['name']}\n"
        f"Report date: {datetime.date.today().strftime('%d %B %Y')}\n\n"
        f"SECTOR INTELLIGENCE ({len(substantive)} sources analysed across "
        f"{len(sectors)} sectors):\n\n"
        + "\n\n".join(intelligence_sections)
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=6000,
        response_format={"type": "json_object"},
    )

    report_text = response.choices[0].message.content

    try:
        report_data = json.loads(report_text)
    except json.JSONDecodeError:
        report_data = {
            "executive_summary": [report_text[:500]],
            "signals_by_sector": {},
            "opportunities": [],
            "synthesis": ["Report generated but JSON parsing failed — raw text preserved."],
            "_raw_text": report_text,
        }

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

    return report_data
