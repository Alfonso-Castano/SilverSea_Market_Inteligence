# pipeline/filter.py — Keyword filtering to drop irrelevant scraped content


def score_relevance(text: str, priority_keywords: list, keywords: list) -> int:
    """Score relevance with priority keywords weighted 3x."""
    # weight is a placeholder constant — revisit once a live run can be scored against it
    text_lower = text.lower()
    priority_hits = sum(1 for kw in priority_keywords if kw.lower() in text_lower)
    general_hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    return priority_hits * 3 + general_hits


def filter_results(scraped: list, priority_keywords: list, keywords: list, min_score: int = 3) -> list:
    """
    Keep only results that contain at least min_score weighted keyword hits.
    Attaches a relevance_score to each result for downstream use.
    """
    filtered = []
    for result in scraped:
        if result["error"] or not result["content"]:
            continue
        score = score_relevance(result["content"], priority_keywords, keywords)
        if score >= min_score:
            result["relevance_score"] = score
            filtered.append(result)

    sector_counts = {}
    for result in filtered:
        sector = result.get("sector", "unknown")
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    breakdown = ", ".join(f"{sector}: {count}" for sector, count in sector_counts.items())

    print(f"  Filter: {len(filtered)}/{len(scraped)} sources passed ({breakdown})")
    return filtered
