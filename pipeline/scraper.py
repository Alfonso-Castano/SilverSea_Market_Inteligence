# pipeline/scraper.py — Fetches raw content from source URLs
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


def scrape_source(source: dict) -> dict:
    """Fetch and parse text content from a single source."""
    url = source["url"]
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove nav, footer, script, style noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Truncate to avoid blowing out the context window downstream
        text = text[:8000]

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


def scrape_all(sources: list) -> list:
    """Scrape all sources, return list of result dicts (including failures)."""
    results = []
    for source in sources:
        if not source.get("active", True):
            print(f"  [{source['name']} | {source.get('sector', 'unknown')}] INACTIVE")
            continue
        result = scrape_source(source)
        status = "OK" if not result["error"] else f"FAILED: {result['error']}"
        print(f"  [{result['name']} | {result['sector']}] {status}")
        results.append(result)
    return results
