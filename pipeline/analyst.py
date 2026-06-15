# pipeline/analyst.py — Claude API synthesis and opportunity scoring
import os
import anthropic

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are a market intelligence analyst for Silversea Media, a Singapore-based
digital twin and immersive technology company. Your products are MetaTwin Object, MetaTwin Space,
MetaTwin Immerse, and MetaTwin Augment. You serve real estate, education, retail, tourism,
government, and MICE sectors.

You will receive scraped content from Singapore's built environment sector. Produce a structured
weekly market intelligence report with exactly these six sections:

1. EXECUTIVE SUMMARY — 3-5 bullet points, most important signals this week
2. MARKET SIGNALS — key developments in SG's built environment / proptech / smart FM space
3. GOVERNMENT & POLICY — BCA, MND, URA, HDB tenders and policy announcements
4. COMPETITOR ACTIVITY — what Hiverlab, Gelement, TwinLogic, TwinMatrix, and others are doing
5. OPPORTUNITIES — scored leads or projects Silversea could pursue

   For each opportunity, provide a score out of 25 using this model:
   - Strategic Fit (0-5): alignment with Silversea's products and target sectors
   - Revenue Potential (0-5): estimated deal size / contract value
   - Win Probability (0-5): likelihood Silversea can compete and win
   - Urgency (0-5): how time-sensitive the opportunity is
   - Intelligence Quality (0-5): how reliable and complete the source information is

   Score interpretation: 20-25 = High priority | 13-19 = Medium | 0-12 = Low

6. WHAT THIS MEANS FOR SILVERSEA — 2-3 synthesis bullets the CEO can act on immediately

Write in clear, concise, executive-readable English. Be specific — name the companies,
projects, and dollar amounts. Focus on what's actionable, not just what happened."""


def analyse(filtered_results: list, country: dict) -> str:
    """Send filtered content to Claude and return the structured report."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Build a compact content block for each source
    source_blocks = []
    for r in filtered_results:
        block = f"### {r['name']} ({r['type'].upper()})\nURL: {r['url']}\n\n{r['content'][:3000]}"
        source_blocks.append(block)

    user_message = (
        f"Country: {country['name']}\n"
        f"Report date: {__import__('datetime').date.today().strftime('%d %B %Y')}\n\n"
        f"SCRAPED SOURCES ({len(source_blocks)} sources passed filtering):\n\n"
        + "\n\n---\n\n".join(source_blocks)
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text
