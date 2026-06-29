# pipeline/scraper.py — Fetches raw content from source URLs
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 15  # seconds


def smart_truncate(text: str, priority_keywords: list, keywords: list, max_chars: int = 6000) -> str:
    """Keep sentences near keyword matches instead of blindly cutting at a char limit.
    Falls back to a blind cut if no keyword hits are found anywhere in the text."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    all_keywords = [kw.lower() for kw in priority_keywords + keywords]

    hit_indices = set()
    for i, sentence in enumerate(sentences):
        s_lower = sentence.lower()
        if any(kw in s_lower for kw in all_keywords):
            hit_indices.add(i)

    if not hit_indices:
        return text[:max_chars]

    WINDOW = 2  # sentences kept on each side of a keyword hit
    keep_indices = set()
    for i in hit_indices:
        for j in range(max(0, i - WINDOW), min(len(sentences), i + WINDOW + 1)):
            keep_indices.add(j)

    kept = [sentences[i] for i in sorted(keep_indices)]
    result = " ".join(kept)
    return result[:max_chars]


def _extract_text(html) -> str:
    """Parse HTML and extract clean text, removing nav/footer/script/style noise."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def _fetch_default(url: str) -> str:
    """Standard HTTP fetch with requests — fast, no JS support."""
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return _extract_text(response.text)


def _fetch_stealth(url: str) -> str:
    """Scrapling StealthyFetcher — bypasses Cloudflare/bot protection."""
    from scrapling.fetchers import StealthyFetcher
    page = StealthyFetcher.fetch(url)
    return _extract_text(page.body)


def _fetch_dynamic(url: str) -> str:
    """Scrapling DynamicFetcher — full browser rendering for JS-heavy SPAs."""
    from scrapling.fetchers import DynamicFetcher
    page = DynamicFetcher.fetch(url)
    return _extract_text(page.body)


FETCHERS = {
    "default": _fetch_default,
    "stealth": _fetch_stealth,
    "dynamic": _fetch_dynamic,
}


def scrape_source(source: dict, priority_keywords: list, keywords: list) -> dict:
    """Fetch and parse text content from a single source."""
    url = source["url"]
    fetcher_type = source.get("fetcher", "default")
    try:
        fetch_fn = FETCHERS.get(fetcher_type, _fetch_default)
        text = fetch_fn(url)
        text = smart_truncate(text, priority_keywords, keywords)

        return {
            "name": source["name"],
            "url": url,
            "type": source.get("type", "unknown"),
            "sector": source.get("sector", "unknown"),
            "content": text,
            "error": None,
        }
    except Exception as e:
        return {
            "name": source["name"],
            "url": url,
            "type": source.get("type", "unknown"),
            "sector": source.get("sector", "unknown"),
            "content": "",
            "error": str(e),
        }


def scrape_all(sources: list, priority_keywords: list, keywords: list) -> list:
    """Scrape all sources, return list of result dicts (including failures)."""
    results = []
    for source in sources:
        if not source.get("active", True):
            print(f"  [{source['name']} | {source.get('sector', 'unknown')}] INACTIVE")
            continue
        result = scrape_source(source, priority_keywords, keywords)
        status = "OK" if not result["error"] else f"FAILED: {result['error']}"
        print(f"  [{result['name']} | {result['sector']}] {status}")
        results.append(result)
    return results
