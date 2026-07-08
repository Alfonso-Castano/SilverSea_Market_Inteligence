import json
import os
import shutil

from config.sources import COUNTRIES, save_sources

PENDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pending_sources")
PROCESSED_DIR = os.path.join(PENDING_DIR, "processed")
REJECTED_DIR = os.path.join(PENDING_DIR, "rejected")


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

    countries = COUNTRIES
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
