# pipeline/scoring.py — Passive source quality scoring based on report citations
import json
import os

SCORES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "source_scores.json")

BASELINE_SCORE = 5.0
CITED_BONUS = 2.0
UNCITED_DECAY = 0.5


def _load_scores() -> dict:
    if not os.path.exists(SCORES_PATH):
        return {}
    try:
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_scores(scores: dict) -> None:
    os.makedirs(os.path.dirname(SCORES_PATH), exist_ok=True)
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)


def _source_names(result: dict) -> list:
    if "names" in result:
        return result["names"]
    if "name" in result:
        return [result["name"]]
    return []


def _source_urls(result: dict) -> list:
    if "urls" in result:
        return result["urls"]
    if "url" in result:
        return [result["url"]]
    return []


def update_scores(filtered_results: list, report_text: str) -> dict:
    """
    Update source quality scores based on which sources were cited in the report.

    Args:
        filtered_results: list of dicts with 'url'/'name' (or 'urls'/'names') fields
        report_text: the LLM-generated report text

    Returns: dict of source_name -> score
    """
    scores = _load_scores()
    report_lower = report_text.lower()

    cited_count = 0
    uncited_count = 0

    for result in filtered_results:
        names = _source_names(result)
        urls = _source_urls(result)

        for name in names:
            if name not in scores:
                scores[name] = BASELINE_SCORE

            url = urls[names.index(name)] if name in names and len(urls) == len(names) else (urls[0] if urls else "")
            is_cited = (name.lower() in report_lower) or (url and url.lower() in report_lower)

            if is_cited:
                scores[name] += CITED_BONUS
                cited_count += 1
            else:
                scores[name] = max(0.0, scores[name] - UNCITED_DECAY)
                uncited_count += 1

    _save_scores(scores)

    top_sources = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:2]
    top_str = ", ".join(f"{name} ({score:.1f})" for name, score in top_sources)
    print(f"  Source scores: {cited_count} cited, {uncited_count} uncited. Top: {top_str}")

    return scores
