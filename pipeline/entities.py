# pipeline/entities.py — Regex-based named entity extraction (no LLM calls)
import re

KNOWN_COMPANIES = [
    "CapitaLand", "Mapletree", "Lendlease", "Keppel", "CDL", "City Developments",
    "Frasers", "UOL", "GuocoLand", "Surbana Jurong", "Boustead", "Woh Hup",
    "Shimizu", "Obayashi", "Kajima", "Samsung C&T", "Hyundai E&C",
    "NUS", "NTU", "SMU", "SIT", "SGH", "NUHS", "Changi Airport Group",
]

# Multi-word capitalized names, e.g. "Sentosa Development Corporation"
_CAPITALIZED_NAME_RE = re.compile(
    r"\b(?:[A-Z][a-zA-Z&]+\s){1,4}(?:Pte Ltd|Ltd|Group|Corporation|Authority|Board|Agency)\b"
)

_AMOUNT_RE = re.compile(
    r"\b(?:S\$|SGD\s?|\$)\s?\d[\d,]*(?:\.\d+)?\s?(?:million|billion|m|bn|M|B)?\b"
)

_DATE_PATTERNS = [
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
    r"\bQ[1-4]\s+\d{4}\b",
    r"\bby\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\b",
    r"\bdeadline:?\s*[^.,;\n]{3,40}",
]
_DATE_RE = re.compile("|".join(_DATE_PATTERNS), re.IGNORECASE)

_REFERENCE_RE = re.compile(
    r"\b(?:GeBIZ\s+ref(?:erence)?[:.]?\s*[A-Za-z0-9-]+|"
    r"tender\s+no\.?\s*[:.]?\s*[A-Za-z0-9-]+|"
    r"(?:ref(?:erence)?|project)\s*(?:no\.?|#)?\s*[:.]?\s*[A-Z]{1,4}-\d{2,}(?:-[A-Za-z0-9]+)?)\b",
    re.IGNORECASE,
)


def _extract_companies(text: str) -> list:
    found = set()
    for company in KNOWN_COMPANIES:
        if re.search(rf"\b{re.escape(company)}\b", text, re.IGNORECASE):
            found.add(company)
    for match in _CAPITALIZED_NAME_RE.findall(text):
        found.add(match.strip())
    return sorted(found)


def _extract_amounts(text: str) -> list:
    return sorted(set(m.strip() for m in _AMOUNT_RE.findall(text)))


def _extract_dates(text: str) -> list:
    return sorted(set(m.strip() for m in _DATE_RE.findall(text)))


def _extract_references(text: str) -> list:
    return sorted(set(m.strip() for m in _REFERENCE_RE.findall(text)))


def extract_entities(filtered_results: list) -> list:
    """
    Add an 'entities' dict (companies, amounts, dates, references) to each result.
    """
    for result in filtered_results:
        text = result.get("content", "")
        result["entities"] = {
            "companies": _extract_companies(text),
            "amounts": _extract_amounts(text),
            "dates": _extract_dates(text),
            "references": _extract_references(text),
        }
    return filtered_results
