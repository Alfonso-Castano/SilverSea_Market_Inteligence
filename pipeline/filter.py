# pipeline/filter.py — Keyword filtering to drop irrelevant scraped content


def score_relevance(text: str, keywords: list) -> int:
    """Count how many distinct keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def filter_results(scraped: list, keywords: list, min_score: int = 1) -> list:
    """
    Keep only results that contain at least min_score keyword hits.
    Attaches a relevance_score to each result for downstream use.
    """
    filtered = []
    for result in scraped:
        if result["error"] or not result["content"]:
            continue
        score = score_relevance(result["content"], keywords)
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
