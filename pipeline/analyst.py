# pipeline/analyst.py — Multi-pass Groq API: extract → per-sector synthesis → summary
import json
import os
import time
import datetime
import openai

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

try:
    from pipeline.vectorstore import query, add_documents, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
    RAG_ENABLED = True
except Exception:
    RAG_ENABLED = False

from config.models import PROVIDERS, LOCAL_MODEL, LOCAL_NUM_CTX
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
5. If a source's extraction says "No actionable signals" (or similar), OMIT that source entirely — do not create an entry for it.

Respond with ONLY valid JSON, no other text:
[{"entity": "Company Name", "signal": "2-3 sentence description with specific details", "source_name": "name of source"}]

If there are no actionable signals, respond with: []"""

SUMMARY_PROMPT = """You are writing an executive summary for a market intelligence report for Silversea Media, a digital twin / smart FM company operating in {country_name}.

You will receive structured signals already organized by sector. Your job is to produce ONLY the summary fields — the signals themselves are already finalized.

Silversea products (for opportunity identification):
- Built Environment & Real Estate (BER): Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart Virtual Inspection, 3D/VR Virtual Tour, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video Analytics Solution.
- Education & EdTech (EDU): STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour, Metaverse Platform, Customized AR/VR Content.
- Manufacturing & Industry 4.0 (MFG): Digital Twin, Smart Virtual Inspection, IoT & AI Solutions, Smart Facility Management System, Customized AR/VR Content, 3D Scanning to 3D Model.
- Healthcare & Life Sciences (HLS): Smart Facility Management System, 3D/VR Virtual Tour, Customized AR/VR Content, Digital Twin, IoT Solution, CCTV Video Analytics Solution.
- Retail, Commerce & Consumer Goods (RCC): Virtual Showroom, Smart Virtual Mockup, Interactive Digital Content, Metaverse Platform, 3D Scanning to 3D Model, Customized AR/VR Content.
- Culture, Tourism & Events (CTE): Virtual Event Platform, 3D/VR Virtual Tour, Interactive Digital Content, Metaverse Platform, 3D Scanning to 3D Model.
- Public Sector & Smart Cities (PSS): Digital Twin, Smart Facility Management System, Smart Virtual Inspection, IoT & AI Solutions, Customized AR/VR Content.
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, smart FM, IoT, virtual/immersive content.

OPPORTUNITIES: Only include signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building, building automation, proptech, edtech, virtual campus, STEM lab, e-learning, virtual/immersive learning, virtual showroom, retail chain, healthcare, hospital, manufacturing, factory, tourism, heritage trail, smart city, or government digitalization. Zero opportunities is correct when nothing qualifies. Every opportunity must carry the source_name of the specific signal it was extracted from — copy it verbatim from the structured signals input, do not invent a new value.

SCORING RUBRIC — each dimension is an integer from 1 to 5. total_score is the sum of all five (max 25).

- Strategic Fit: 1 = barely touches Silversea's product categories, 3 = plausible fit with one product line, 5 = direct fit explicitly matching a named solution.
- Revenue Potential: 1 = no budget/scale indication, 3 = mid-size project with no figure stated, 5 = named budget/tender value or large-scale (nationwide/multi-site).
- Win Probability: 1 = no visible relationship or a competitor is already engaged, 3 = neutral/open opportunity with no known blockers, 5 = existing Silversea relationship or the entity is actively seeking vendors.
- Urgency: 1 = no deadline / long-term exploratory, 3 = deadline stated but more than 3 months out, 5 = deadline imminent (under 1 month) or "now accepting proposals".
- Intelligence Quality: 1 = vague/secondhand/inferred, 3 = direct quote with some detail, 5 = direct quote plus named entity plus specific numbers/dates.

Every dimension must be an integer 1-5, never 0 and never above 5.

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
      "source_name": "must exactly match a source_name value from the structured signals above",
      "product_fit": "which Silversea solution (see the product catalog listed above, organized by business sector) best fits this opportunity, and why — reason from the domain the signal's sector belongs to, not just built-environment framing",
      "scores": {"strategic_fit": 0, "revenue_potential": 0, "win_probability": 0, "urgency": 0, "intelligence_quality": 0},
      "total_score": 0
    }
  ],
  "synthesis": ["2-3 bullets: cross-sector themes and what they mean for Silversea"]
}"""


_SCORE_DIMENSIONS = ["strategic_fit", "revenue_potential", "win_probability", "urgency", "intelligence_quality"]

# JSON schemas used ONLY on the local (Ollama) backend, via /api/chat's native `format`
# field for genuine schema-constrained output. Every remote provider (Groq/DeepSeek/Qwen/
# Kimi) never uses these — they keep the loose response_format={"type": "json_object"} mode,
# since Ollama's OpenAI-compatible endpoint doesn't support schema-constrained JSON but its
# native endpoint does (see .context/features/002-local-llm-backend/RESEARCH.md §1).

# Ollama's native `format` schemas must be objects, not bare arrays — so the sector synthesis
# result is wrapped in a top-level `signals` array. This matches the dict-unwrap tolerance
# already in _synthesize_sector (result.get("signals", ...)).
SECTOR_SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "signals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string"},
                    "signal": {"type": "string"},
                    "source_name": {"type": "string"},
                },
                "required": ["entity", "signal", "source_name"],
            },
        }
    },
    "required": ["signals"],
}

# Mirrors SUMMARY_PROMPT's top-level object shape exactly.
SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "array", "items": {"type": "string"}},
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "source_quote": {"type": "string"},
                    "named_entry_point": {"type": "string"},
                    "concrete_action": {"type": "string"},
                    "deadline": {"type": "string"},
                    "source_name": {"type": "string"},
                    "product_fit": {"type": "string"},
                    "scores": {
                        "type": "object",
                        "properties": {dim: {"type": "integer"} for dim in _SCORE_DIMENSIONS},
                        "required": list(_SCORE_DIMENSIONS),
                    },
                    "total_score": {"type": "integer"},
                },
                "required": [
                    "title",
                    "source_quote",
                    "named_entry_point",
                    "concrete_action",
                    "deadline",
                    "source_name",
                    "product_fit",
                    "scores",
                    "total_score",
                ],
            },
        },
        "synthesis": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["executive_summary", "opportunities", "synthesis"],
}


def _chat_completion(client, provider_key: str, system_prompt: str, user_message: str, max_tokens: int, json_schema: dict | None = None) -> str:
    """Dispatch one LLM call to the resolved provider (provider_key: a PROVIDERS key, or "local").

    Returns the raw text content. Every remote provider (Groq/DeepSeek/Qwen/Kimi) is genuinely
    OpenAI-API-shaped, so one branch covers all four: response_format={"type": "json_object"}
    whenever json_schema is given, a plain completion otherwise — the same loose JSON mode the
    Groq-only code already relied on, just parameterized by which client/model is active. The
    local backend uses Ollama's native structured-outputs 'format' field instead, for genuine
    schema enforcement (see the schemas above).
    """
    if provider_key == "local":
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("--llm=local but the 'ollama' package is not installed (see requirements.txt)")
        response = ollama.chat(
            model=LOCAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            format=json_schema,  # None => free-text, matching the extraction call site
            options={"num_ctx": LOCAL_NUM_CTX, "num_predict": max_tokens, "temperature": 0},
        )
        return response["message"]["content"]

    kwargs = {}
    if json_schema is not None:
        kwargs["response_format"] = {"type": "json_object"}
    if provider_key.startswith("openrouter"):
        # OpenRouter's free NVIDIA Nemotron models default to emitting an internal
        # reasoning trace that can consume the large majority of max_tokens before any
        # real content is produced, truncating/malforming JSON output — confirmed live
        # during feature 008's planning (1300+ reasoning tokens observed against a
        # max_tokens=2000 sector-synthesis call; see
        # .context/features/008-openrouter-company-provider/RESEARCH.md §4). Disabling
        # reasoning via OpenRouter's unified `reasoning` request parameter frees that
        # budget for real content. Applied to every call site (extraction, sector
        # synthesis, summary synthesis), not just the JSON-mode ones, since all three
        # share the same max_tokens=2000 ceiling and the same overhead risk.
        kwargs["extra_body"] = {"reasoning": {"enabled": False}}
    response = client.chat.completions.create(
        model=PROVIDERS[provider_key]["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
        **kwargs,
    )
    return response.choices[0].message.content


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


def _extract_sector(client, provider_key: str, sector_name: str, sources: list) -> str:
    """Phase 1: Extract signals from one sector's sources via a focused LLM call."""
    label = SECTOR_LABELS.get(sector_name, sector_name.replace("_", " ").title())

    source_blocks = []
    for r in sources:
        name = r.get("name") or (r.get("names") or ["Unknown"])[0]
        url = r.get("url") or (r.get("urls") or [""])[0]
        source_blocks.append(f"### {name}\nURL: {url}\n\n{r['content']}")

    user_message = f"Sector: {label}\n\n" + "\n\n---\n\n".join(source_blocks)

    try:
        return _chat_completion(client, provider_key, SECTOR_EXTRACT_PROMPT, user_message, 2000)
    except Exception as e:
        print(f"    Error extracting {sector_name}: {e}")
        return f"**{label}**: Extraction failed — {e}"


def _synthesize_sector(client, provider_key: str, sector_name: str, extraction_text: str) -> list:
    """Convert one sector's extraction text into structured JSON signals."""
    label = SECTOR_LABELS.get(sector_name, sector_name.replace("_", " ").title())

    user_message = f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"
    if provider_key == "local" or provider_key.startswith("openrouter"):
        # Loose response_format={"type": "json_object"} mode nudges free-tier OpenRouter
        # models toward a bare JSON *object*, not the array SECTOR_SYNTHESIS_PROMPT asks
        # for — confirmed live (RESEARCH.md §4). The same object-wrapper phrasing already
        # used for Ollama's native schema mode fixes it here too, since
        # _synthesize_sector()'s own unwrap logic below already handles a
        # {"signals": [...]} shape.
        user_message += '\n\nReturn a JSON object with a top-level "signals" array of the entries.'

    try:
        content = _chat_completion(
            client,
            provider_key,
            SECTOR_SYNTHESIS_PROMPT,
            user_message,
            2000,
            json_schema=SECTOR_SYNTHESIS_SCHEMA,
        )
        result = json.loads(content)
        if isinstance(result, dict):
            result = result.get("signals", list(result.values())[0] if result else [])
        if not isinstance(result, list):
            result = []
        return [item for item in result if isinstance(item, dict)]
    except Exception as e:
        print(f"    Error synthesizing {sector_name}: {e}")
        return []


def _clamp_opportunity_scores(opportunities: list) -> list:
    """Server-side safety net: never trust the LLM's own total_score or dimension range."""
    for opp in opportunities:
        raw_scores = opp.get("scores", {}) or {}
        clamped = {}
        for dim in _SCORE_DIMENSIONS:
            try:
                value = int(raw_scores.get(dim, 1))
            except (TypeError, ValueError):
                value = 1
            clamped[dim] = max(1, min(5, value))
        opp["scores"] = clamped
        opp["total_score"] = sum(clamped.values())
    return opportunities


def _synthesize_summary(client, provider_key: str, signals_by_sector: dict, country_name: str) -> dict:
    """Produce executive_summary, opportunities, and synthesis from structured signals."""
    sections = []
    for sector_name, signals in signals_by_sector.items():
        lines = []
        for s in signals:
            lines.append(f"- {s.get('entity', '?')} [source: {s.get('source_name', '')}]: {s.get('signal', '')}")
        sections.append(f"=== {sector_name} ===\n" + "\n".join(lines))

    user_message = "Structured signals by sector:\n\n" + "\n\n".join(sections)
    system_prompt = SUMMARY_PROMPT.replace("{country_name}", country_name)
    if provider_key == "local":
        user_message += (
            '\n\nReturn a single JSON object with the top-level keys '
            '"executive_summary", "opportunities", and "synthesis".'
        )

    try:
        content = _chat_completion(
            client,
            provider_key,
            system_prompt,
            user_message,
            2000,
            json_schema=SUMMARY_SCHEMA,
        )
        result = json.loads(content)
        result["opportunities"] = _clamp_opportunity_scores(result.get("opportunities", []))
        return result
    except Exception as e:
        print(f"    Error in summary synthesis: {e}")
        return {"executive_summary": [], "opportunities": [], "synthesis": []}


def _generate_implications(signals_by_sector: dict) -> None:
    """Add implication field to each signal based on sector and keyword matching. Zero LLM cost."""
    SECTOR_IMPLICATIONS = {
        "Government & Agencies": "Government initiative that could create procurement opportunities or regulatory tailwinds for Silversea's digital twin, smart FM, or education-technology solutions.",
        "Industry Associations": "Industry body activity that could provide networking, certification, or partnership channels for Silversea Media.",
        "Customers": "Activity from a potential or existing customer that may signal demand for digital twin, smart FM, or campus/education technology solutions.",
        "Partners": "Partner ecosystem development that could strengthen Silversea's go-to-market or delivery capabilities.",
        "Competitors": "Competitive activity to monitor — may indicate market trends or areas where Silversea needs to differentiate.",
        "General News": "Market development relevant to Silversea's positioning across the built environment and education sectors.",
    }

    SPECIFIC_KEYWORDS = {
        "digital twin": "Directly relevant to Silversea's Digital Twin solution.",
        "smart fm": "Aligns with Silversea's Smart Facility Management System solution.",
        "smart building": "Aligns with Silversea's Smart Facility Management System building management capabilities.",
        "bim": "Relevant to Silversea's BIM-to-digital-twin workflow.",
        "3d scan": "Relevant to Silversea's 3D Scanning to 3D Model capabilities.",
        "virtual tour": "Directly relevant to Silversea's 3D/VR Virtual Tour product.",
        "xr": "Relevant to Silversea's XR/spatial computing capabilities.",
        "inspection": "Relevant to Silversea's Smart Virtual Inspection solution.",
        "facility management": "Core market for Silversea's Smart Facility Management System.",
        "iot": "Complementary technology to Silversea's IoT & AI Solutions.",
        "stem lab": "Directly relevant to Silversea's STEM 3D Virtual Lab solution.",
        "virtual campus": "Directly relevant to Silversea's Virtual Campus solution.",
        "edtech": "Relevant to Silversea's education-sector product line (Virtual Campus, STEM 3D Virtual Lab).",
        "e-learning": "Relevant to Silversea's education-sector immersive/virtual learning solutions.",
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

    HIGH_KEYWORDS = ["digital twin", "smart fm", "bim", "3d scan", "iot", "smart building", "facility management", "virtual campus", "stem lab", "edtech"]
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
                f"product development closely and differentiate on Silversea's product suite integration."
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


def analyse(filtered_results: list, country: dict, provider_key: str) -> dict:
    """Multi-pass analysis: extract per sector, synthesize per sector, then summarize."""
    if provider_key == "local":
        client = None
    else:
        provider = PROVIDERS[provider_key]
        client = openai.OpenAI(base_url=provider["base_url"], api_key=os.environ.get(provider["key_env"], ""))

    substantive = [r for r in filtered_results if len(r.get("content", "")) >= MIN_CONTENT_CHARS]

    sectors = {}
    for r in substantive:
        sectors.setdefault(r.get("sector", "unknown"), []).append(r)

    # Phase 1: per-sector signal extraction (unchanged)
    sector_extractions = {}
    for i, (sector_name, sources) in enumerate(sectors.items()):
        label = SECTOR_LABELS.get(sector_name, sector_name)
        print(f"    Extracting {label} ({len(sources)} sources)...")
        sector_extractions[sector_name] = _extract_sector(client, provider_key, sector_name, sources)
        if i < len(sectors) - 1:
            time.sleep(CALL_DELAY)

    # Phase 2: per-sector JSON synthesis
    signals_by_sector = {}
    for i, (sector_name, extraction_text) in enumerate(sector_extractions.items()):
        label = SECTOR_LABELS.get(sector_name, sector_name)
        print(f"    Structuring {label}...")
        time.sleep(CALL_DELAY)
        signals = _synthesize_sector(client, provider_key, sector_name, extraction_text)
        if signals:
            signals_by_sector[label] = signals
            print(f"      -> {len(signals)} signals")

    # Phase 3: add implications via Python (zero LLM cost)
    _generate_implications(signals_by_sector)

    # Phase 4: summary synthesis (executive_summary + opportunities + synthesis)
    print("    Generating summary...")
    time.sleep(CALL_DELAY)
    summary = _synthesize_summary(client, provider_key, signals_by_sector, country["name"])

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
