import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "sources.json")


def _load():
    with open(_PATH, encoding="utf-8") as f:
        return json.load(f)["countries"]


def load_sources():
    """Fresh read of sources.json from disk — use this instead of the cached COUNTRIES
    singleton anywhere a read-modify-write needs to see the current on-disk state."""
    return _load()


def save_sources(countries):
    """Atomic write-back — used by the admin source-approval flow (Phase D).
    Preserves sibling root-level keys (e.g. _domain_tagging_status)."""
    with open(_PATH, encoding="utf-8") as f:
        data = json.load(f)
    data["countries"] = countries
    tmp_path = _PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, _PATH)


COUNTRIES = _load()
