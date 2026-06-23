# pipeline/analyst.py — Groq API synthesis and opportunity scoring
import os
import datetime
from groq import Groq

try:
    from pipeline.vectorstore import query, add_documents, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
    RAG_ENABLED = True
except Exception:
    RAG_ENABLED = False

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a market intelligence analyst for Silversea Media, a Singapore-based
digital twin and immersive technology company.

GROUNDING RULE: You have no knowledge beyond the source text provided. Treat the scraped
content as the complete and only truth. Never infer, estimate, or fabricate any fact, date,
deadline, dollar amount, or programme name that does not appear verbatim in the source text.
If information is not explicitly stated in the source, it does not exist for this report.

Company context (use only for relevance filtering, not for generating claims):
- Products: MetaTwin Object, MetaTwin Space, MetaTwin Immerse, MetaTwin Augment
- Sectors served: real estate, education, retail, tourism, government, MICE
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, spatial computing, smart FM

Produce a structured report with exactly these four sections:

1. EXECUTIVE SUMMARY — 3-5 bullet points, most important signals found in the sources

2. SIGNALS BY SECTOR — group under headers: Government & Agencies, Associations, Customers,
   Partners, Competitors. Only include sectors with actual signals from the source text.
   - Each named programme, initiative, or tender is its own signal — never merge unrelated
     programmes from the same agency
   - Do not combine information from two different sources into a single claim
   - State only what the source text says. Do not add interpretation about what it "means for
     Silversea" here — save that for Section 4

3. OPPORTUNITIES — scored leads Silversea could pursue.

   RELEVANCE GATE (apply before generating any opportunity):
   Does the source text explicitly mention digital twin, BIM, 3D scanning, XR/spatial
   computing, smart FM, smart building, building automation, or proptech? If the connection
   to Silversea's products is inferred rather than stated in the source, it is NOT an
   opportunity. A government tender for residential land is not a digital twin opportunity
   just because a government agency issued it.

   For each opportunity that passes the relevance gate, provide:
   - Source quote: copy the exact sentence(s) from the source that establish relevance
   - Named entry point: the specific programme, tender, or initiative named in the source
   - Concrete action: what Silversea should do
   - Deadline: the deadline stated in the source, or "No deadline found in source" if none
   - Source citation: which source URL this came from
   - Product fit: which MetaTwin product applies and why

   NEVER invent a deadline, submission date, or contact channel not found in the source text.
   "No deadline found in source" is a valid and expected output — not an error.

   An empty Opportunities section is a correct output when no source contains signals that
   pass the relevance gate. Zero real opportunities is better than one fabricated opportunity.

   Score each opportunity out of 25:
   - Strategic Fit (0-5): alignment with Silversea's products and target sectors
   - Revenue Potential (0-5): estimated deal size / contract value
   - Win Probability (0-5): likelihood Silversea can compete and win
   - Urgency (0-5): how time-sensitive (score 1 if no deadline found in source)
   - Intelligence Quality (0-5): how reliable and complete the source information is

   Score interpretation: 20-25 = High priority | 13-19 = Medium | 0-12 = Low

   NEGATIVE EXAMPLE — do NOT generate opportunities like this:
   Source says: "URA awarded tender for residential sale site at Peck Hay Road"
   Wrong output: "Submit proposal for digital twin solutions for Peck Hay Road by 30 June"
   Why wrong: Source describes a residential land sale. No mention of digital twin, BIM, or
   smart building. The deadline is fabricated. Agency identity alone does not make something
   relevant to Silversea.

4. WHAT THIS MEANS FOR SILVERSEA — 2-3 synthesis bullets the CEO can act on immediately

EXCLUDE from the entire report:
- Residential property data (home sales, condo launches, land tenders for housing, price indices)
- General economic indicators with no explicit tech connection in the source
- Any signal where the link to digital twin / smart FM / BIM is your inference, not the source's

Write in clear, concise, executive-readable English. Name specific companies, programmes,
and amounts only when they appear in the source text."""


def _build_rag_context(filtered_results: list) -> str:
    """Query the vector store for company context, feedback priorities, and past
    report themes relevant to today's sources. Returns an empty string if RAG is
    unavailable or no collections have any documents yet."""
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


def analyse(filtered_results: list, country: dict) -> str:
    """Send filtered content to Groq and return the structured report."""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    sectors = {}
    for r in filtered_results:
        sectors.setdefault(r.get("sector", "unknown"), []).append(r)

    sector_sections = []
    for sector, results in sectors.items():
        blocks = []
        for r in results:
            name = r.get("name") or (r.get("names") or ["Unknown"])[0]
            url = r.get("url") or (r.get("urls") or [""])[0]
            blocks.append(f"### {name} ({r['type'].upper()})\nURL: {url}\n\n{r['content'][:800]}")
        sector_sections.append(f"=== {sector.upper()} ===\n\n" + "\n\n---\n\n".join(blocks))

    rag_context = _build_rag_context(filtered_results)

    user_message = (
        rag_context
        + f"Country: {country['name']}\n"
        f"Report date: {datetime.date.today().strftime('%d %B %Y')}\n\n"
        f"SCRAPED SOURCES ({len(filtered_results)} sources passed filtering):\n\n"
        + "\n\n".join(sector_sections)
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=4096,
    )

    report_text = response.choices[0].message.content

    if RAG_ENABLED:
        try:
            add_documents(
                REPORT_HISTORY,
                [report_text[:1500]],
                metadatas=[{"date": datetime.date.today().isoformat(), "country": country["code"]}],
            )
        except Exception:
            pass

    return report_text
