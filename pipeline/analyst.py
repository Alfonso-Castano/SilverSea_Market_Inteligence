# pipeline/analyst.py — Multi-pass Groq API: extract → per-sector synthesis → summary
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

from config.models import GROQ_MODEL
CALL_DELAY = 2
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

SECTOR_SYNTHESIS_PROMPT = """Convert the extracted signals below into a JSON array. Each signal becomes one entry.

RULES:
1. Every named signal (partnership, launch, tender, event, metric, strategic move) MUST become its own entry. Do NOT merge or summarize multiple signals into one.
2. Write each "signal" field as 2-3 complete sentences preserving specific names, dates, numbers, and details from the source.
3. Only use facts from the text below. Never invent facts.
4. EXCLUDE: residential property sales, general economic data with no tech/construction link.

Respond with ONLY valid JSON, no other text:
[{"entity": "Company Name", "signal": "2-3 sentence description with specific details", "source_name": "name of source"}]

If there are no actionable signals, respond with: []"""

SUMMARY_PROMPT = """You are writing an executive summary for a market intelligence report for Silversea Media, a digital twin / smart FM company in Singapore.

You will receive structured signals already organized by sector. Your job is to produce ONLY the summary fields — the signals themselves are already finalized.

Silversea products (for opportunity identification):
- SpatioX Twin (digital twin platform), SpatioX Ops (smart FM), SpatioX Audit (virtual inspection), SpatioX Walk (3D/VR tour)
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, smart FM

OPPORTUNITIES: Only include signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building, building automation, or proptech. Zero opportunities is correct when nothing qualifies.

Respond with ONLY valid JSON:
{
  "executive_summary": ["3-5 most important signals across all sectors — be specific with names and facts"],
  "opportunities": [
    {
      "title": "short title",
      "source_quote": "the signal text",
      "named_entry_point": "programme/tender name",
      "concrete_action": "what Silversea should do",
      "deadline": "as stated or 'No deadline found in source'",
      "source_url": "",
      "product_fit": "which SpatioX product and why",
      "scores": {"strategic_fit": 0, "revenue_potential": 0, "win_probability": 0, "urgency": 0, "intelligence_quality": 0},
      "total_score": 0
    }
  ],
  "synthesis": ["2-3 bullets: cross-sector themes and what they mean for Silversea"]
}"""


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
            model=GROQ_MODEL,
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


def _synthesize_sector(client, sector_name: str, extraction_text: str) -> list:
    """Convert one sector's extraction text into structured JSON signals."""
    label = SECTOR_LABELS.get(sector_name, sector_name.replace("_", " ").title())

    user_message = f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SECTOR_SYNTHESIS_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        if isinstance(result, dict):
            result = result.get("signals", list(result.values())[0] if result else [])
        if not isinstance(result, list):
            result = []
        return result
    except Exception as e:
        print(f"    Error synthesizing {sector_name}: {e}")
        return []


def _synthesize_summary(client, signals_by_sector: dict) -> dict:
    """Produce executive_summary, opportunities, and synthesis from structured signals."""
    sections = []
    for sector_name, signals in signals_by_sector.items():
        lines = []
        for s in signals:
            lines.append(f"- {s.get('entity', '?')}: {s.get('signal', '')}")
        sections.append(f"=== {sector_name} ===\n" + "\n".join(lines))

    user_message = "Structured signals by sector:\n\n" + "\n\n".join(sections)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"    Error in summary synthesis: {e}")
        return {"executive_summary": [], "opportunities": [], "synthesis": []}


def _generate_implications(signals_by_sector: dict) -> None:
    """Add implication field to each signal based on sector and keyword matching. Zero LLM cost."""
    SECTOR_IMPLICATIONS = {
        "Government & Agencies": "Government initiative that could create procurement opportunities or regulatory tailwinds for Silversea's digital twin and smart FM solutions.",
        "Industry Associations": "Industry body activity that could provide networking, certification, or partnership channels for Silversea Media.",
        "Customers": "Activity from a potential or existing customer that may signal demand for digital twin, BIM, or smart FM solutions.",
        "Partners": "Partner ecosystem development that could strengthen Silversea's go-to-market or delivery capabilities.",
        "Competitors": "Competitive activity to monitor — may indicate market trends or areas where Silversea needs to differentiate.",
        "General News": "Market development in Singapore's built environment sector relevant to Silversea's positioning.",
    }

    SPECIFIC_KEYWORDS = {
        "digital twin": "Directly relevant to Silversea's core SpatioX Twin platform.",
        "smart fm": "Aligns with Silversea's SpatioX Ops smart facility management solution.",
        "smart building": "Aligns with Silversea's SpatioX Ops smart building management capabilities.",
        "bim": "Relevant to Silversea's BIM-to-digital-twin workflow in SpatioX Twin.",
        "3d scan": "Relevant to Silversea's 3D scanning and point cloud capabilities.",
        "virtual tour": "Directly relevant to Silversea's SpatioX Walk 3D/VR tour product.",
        "xr": "Relevant to Silversea's XR/spatial computing capabilities.",
        "inspection": "Relevant to Silversea's SpatioX Audit virtual inspection solution.",
        "facility management": "Core market for Silversea's SpatioX Ops platform.",
        "iot": "Complementary technology to Silversea's smart building sensor integration.",
    }

    for sector_name, signals in signals_by_sector.items():
        default_impl = SECTOR_IMPLICATIONS.get(sector_name, "Relevant market development for Silversea Media.")
        for s in signals:
            signal_lower = s.get("signal", "").lower()
            matched = None
            for kw, impl in SPECIFIC_KEYWORDS.items():
                if kw in signal_lower:
                    matched = impl
                    break
            s["implication"] = matched if matched else default_impl


def _derive_competition_risks(report_data: dict) -> None:
    """Post-process LLM output to derive competition risk assessments (pure Python, zero token cost)."""
    signals_by_sector = report_data.get("signals_by_sector", {})

    competitor_key = None
    for key in signals_by_sector:
        if "competitor" in key.lower():
            competitor_key = key
            break

    if not competitor_key:
        report_data["competition_risks"] = []
        return

    HIGH_KEYWORDS = ["digital twin", "smart fm", "bim", "3d scan", "iot", "smart building", "facility management"]
    MEDIUM_KEYWORDS = ["partnership", "expansion", "funding", "launch", "acquisition"]
    THREAT_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

    risks = []
    for signal_entry in signals_by_sector[competitor_key]:
        entity = signal_entry.get("entity", "Unknown")
        signal_text = signal_entry.get("signal", "")
        signal_lower = signal_text.lower()

        if any(kw in signal_lower for kw in HIGH_KEYWORDS):
            threat_level = "HIGH"
            mitigation = (
                f"Direct competitor in Silversea's core domain. Monitor {entity}'s "
                f"product development closely and differentiate on SpatioX platform integration."
            )
        elif any(kw in signal_lower for kw in MEDIUM_KEYWORDS):
            threat_level = "MEDIUM"
            mitigation = (
                f"Growing capability that could overlap with Silversea's market. Track {entity}'s "
                f"strategic direction and partnership outcomes."
            )
        else:
            threat_level = "LOW"
            mitigation = (
                f"Tangential activity with limited immediate impact. Continue routine monitoring of {entity}."
            )

        risks.append({
            "entity": entity,
            "signal": signal_text,
            "threat_level": threat_level,
            "mitigation": mitigation,
        })

    risks.sort(key=lambda r: THREAT_ORDER.get(r["threat_level"], 3))
    report_data["competition_risks"] = risks


def analyse(filtered_results: list, country: dict) -> dict:
    """Multi-pass analysis: extract per sector, synthesize per sector, then summarize."""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    substantive = [r for r in filtered_results if len(r.get("content", "")) >= MIN_CONTENT_CHARS]

    sectors = {}
    for r in substantive:
        sectors.setdefault(r.get("sector", "unknown"), []).append(r)

    # Phase 1: per-sector signal extraction (unchanged)
    sector_extractions = {}
    for i, (sector_name, sources) in enumerate(sectors.items()):
        label = SECTOR_LABELS.get(sector_name, sector_name)
        print(f"    Extracting {label} ({len(sources)} sources)...")
        sector_extractions[sector_name] = _extract_sector(client, sector_name, sources)
        if i < len(sectors) - 1:
            time.sleep(CALL_DELAY)

    # Phase 2: per-sector JSON synthesis
    signals_by_sector = {}
    for i, (sector_name, extraction_text) in enumerate(sector_extractions.items()):
        label = SECTOR_LABELS.get(sector_name, sector_name)
        print(f"    Structuring {label}...")
        time.sleep(CALL_DELAY)
        signals = _synthesize_sector(client, sector_name, extraction_text)
        if signals:
            signals_by_sector[label] = signals
            print(f"      -> {len(signals)} signals")

    # Phase 3: add implications via Python (zero LLM cost)
    _generate_implications(signals_by_sector)

    # Phase 4: summary synthesis (executive_summary + opportunities + synthesis)
    print("    Generating summary...")
    time.sleep(CALL_DELAY)
    summary = _synthesize_summary(client, signals_by_sector)

    # Assemble final report
    report_data = {
        "executive_summary": summary.get("executive_summary", []),
        "signals_by_sector": signals_by_sector,
        "opportunities": summary.get("opportunities", []),
        "synthesis": summary.get("synthesis", []),
    }

    # Store in RAG
    if RAG_ENABLED:
        try:
            rag_content = {
                "executive_summary": report_data.get("executive_summary", []),
                "signals_by_sector": report_data.get("signals_by_sector", {}),
                "opportunities": report_data.get("opportunities", []),
            }
            summary_for_rag = json.dumps(rag_content, ensure_ascii=False)[:4000]
            add_documents(
                REPORT_HISTORY,
                [summary_for_rag],
                metadatas=[{"date": datetime.date.today().isoformat(), "country": country["code"]}],
            )
        except Exception:
            pass

    _derive_competition_risks(report_data)

    return report_data
