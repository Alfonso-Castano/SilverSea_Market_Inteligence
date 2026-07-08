import datetime
import json
import os
import re
import shutil

from config.sources import load_sources, save_sources

PENDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pending_sources")
PROCESSED_DIR = os.path.join(PENDING_DIR, "processed")
REJECTED_DIR = os.path.join(PENDING_DIR, "rejected")
INTEREST_SIGNALS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "source_interest_signals.json"
)


def _normalize_url(url):
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u.rstrip("/")


def find_duplicate_source(source_name, source_url):
    """Check a suggested source's name/URL against every source already in
    sources.json (all countries). Returns the matching existing source dict,
    or None if it's genuinely new."""
    name_norm = (source_name or "").strip().lower()
    url_norm = _normalize_url(source_url)
    for country in load_sources():
        for src in country.get("sources", []):
            if name_norm and src.get("name", "").strip().lower() == name_norm:
                return src
            if url_norm and _normalize_url(src.get("url", "")) == url_norm:
                return src
    return None


def record_interest_signal(source_name, source_url, matched_source_name, submitter):
    """Log a duplicate suggestion as a source-interest signal for admin visibility.
    This does not touch sources.json — it's informational only."""
    signals = []
    if os.path.exists(INTEREST_SIGNALS_PATH):
        with open(INTEREST_SIGNALS_PATH, "r", encoding="utf-8") as f:
            signals = json.load(f)
    signals.append({
        "source_name": source_name,
        "source_url": source_url,
        "matched_existing_source": matched_source_name,
        "submitted_by": submitter,
        "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    with open(INTEREST_SIGNALS_PATH, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)


def list_interest_signals():
    if not os.path.exists(INTEREST_SIGNALS_PATH):
        return []
    with open(INTEREST_SIGNALS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def list_pending():
    if not os.path.isdir(PENDING_DIR):
        return []
    entries = []
    for filename in sorted(os.listdir(PENDING_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(PENDING_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
        entry["_filename"] = filename
        entries.append(entry)
    return entries


def approve(filename, sector, domain, country_code="SG"):
    src_path = os.path.join(PENDING_DIR, filename)
    with open(src_path, "r", encoding="utf-8") as f:
        suggestion = json.load(f)

    new_source = {
        "name": suggestion["source_name"],
        "url": suggestion["source_url"],
        "sector": sector,
        "domain": domain if isinstance(domain, list) else [domain],
        "type": "website",
        "active": True,
    }

    countries = load_sources()
    for country in countries:
        if country["code"] == country_code:
            country["sources"].append(new_source)
            break
    save_sources(countries)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    shutil.move(src_path, os.path.join(PROCESSED_DIR, filename))


def reject(filename):
    src_path = os.path.join(PENDING_DIR, filename)
    os.makedirs(REJECTED_DIR, exist_ok=True)
    shutil.move(src_path, os.path.join(REJECTED_DIR, filename))
