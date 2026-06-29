# Execution Plan — Pipeline Optimization Pass

**Created:** 2026-06-29
**Purpose:** Pre-Claude-Haiku hardening. Optimize everything upstream of the LLM so the
model upgrade feeds on the best possible data.
**Constraint:** Do NOT touch `templates/`, `static/`, `app.py`, the LLM model constant
in `analyst.py`, or `SYNTHESIS_PROMPT`. Pipeline-only changes.

---

## Step 1: Create `config/models.py` — Shared Model Constant

**What:** Create a new file `config/models.py` that exports a single constant.
**Why:** Three files hardcode the model string. One source of truth.

**Create `config/models.py`:**
```python
# config/models.py — Single source of truth for LLM model selection
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
```

**Then update these three files to import from it:**

1. `pipeline/analyst.py` line 14:
   - Remove: `MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"`
   - Add: `from config.models import GROQ_MODEL`
   - Replace all references to `MODEL` with `GROQ_MODEL` (lines 135, 188)

2. `pipeline/feedback.py` lines 57 and 118:
   - Add at top: `from config.models import GROQ_MODEL`
   - Line 57: change `model="meta-llama/llama-4-scout-17b-16e-instruct"` to `model=GROQ_MODEL`
   - Line 118: same change

3. `pipeline/weekly.py` line 69:
   - Add at top: `from config.models import GROQ_MODEL`
   - Line 69: change `model="meta-llama/llama-4-scout-17b-16e-instruct"` to `model=GROQ_MODEL`

**Verify:** `grep -r "llama-4-scout" pipeline/ config/` should return only `config/models.py`.

---

## Step 2: Remove Dead Code — `dedup.py`, `entities.py`, `scoring.py`

**What:** Remove three pipeline steps that produce no useful output.
**Why:**
- `dedup.py` loads a 90MB sentence-transformers model, compares first 300 chars, consistently
  merges 0 results. The LLM handles cross-source synthesis anyway.
- `entities.py` attaches an `entities` dict to each result. Nothing downstream reads it —
  not the analyst, not the report template, not the dashboard.
- `scoring.py` tracks citation-based source scores. The citation check is unreliable (LLM
  doesn't preserve source names), scores decay toward 0, and scores aren't used in filtering,
  extraction, or synthesis.

### 2a. Remove from `main.py`

Current `main.py` imports (lines 11-17):
```python
from pipeline.dedup import deduplicate
from pipeline.entities import extract_entities
from pipeline.scoring import update_scores
```
**Delete these three import lines.**

Current pipeline body (lines 60-72):
```python
print("Deduplicating signals...")
deduped = deduplicate(filtered)

print("Extracting entities...")
enriched = extract_entities(deduped)

print("Analysing with Claude...")
report_data = analyse(enriched, country)

print("Scoring sources...")
report_text_for_scoring = json.dumps(report_data, ensure_ascii=False)
update_scores(filtered, report_text_for_scoring)
```

**Replace with:**
```python
print("Analysing with LLM...")
report_data = analyse(filtered, country)
```

This simultaneously:
- Removes dedup call
- Removes entities call
- Removes scoring call
- Fixes the "Analysing with Claude..." print (finding #10)
- Passes `filtered` directly to `analyse()` instead of through dedup→entities chain

**Also update `run_metadata` dict (lines 77-87).** Remove these keys:
- `"dedup_input"` (line 84)
- `"dedup_output"` (line 85)
- `"dedup_merged"` (line 86)
- `"entities_extracted"` (line 87)

The metadata dict should become:
```python
run_metadata = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "country": country["name"],
    "country_code": country["code"],
    "sources_scraped": len(scraped),
    "sources_passed_filter": len(filtered),
}
```

### 2b. Delete the files

Delete these three files entirely:
- `pipeline/dedup.py`
- `pipeline/entities.py`
- `pipeline/scoring.py`

Also delete `data/source_scores.json` if it exists.

### 2c. Remove stale `entities` dict from `config/sources.py`

Delete lines 113-120 of `config/sources.py`:
```python
        "entities": {
            "government": ["BCA", "MND", "URA", "HDB", "SGBC", "JTC", "Smart Nation", "IMDA"],
            "prospects": ["JTC Corporation", "CapitaLand", "Mapletree", "Lendlease",
                          "SGH", "NUH", "TTSH", "Alexandra Hospital",
                          "NUS", "NTU", "SMU", "Keppel"],
            "partners": ["AECOM", "CPG Consultant", "Honeywell", "Cushman & Wakefield"],
            "competitors": ["Hiverlab", "Gelement", "TwinLogic", "Axomem", "DataMesh", "FacilityBot", "Cryotos"],
        },
```

This dict is never referenced in code (grep for `["entities"]` or `.entities` on
country dicts — nothing reads it). It was a Phase 1 artifact superseded by the source
list itself.

Also remove the matching `"entities": {}` from the commented-out future country templates
(lines 123-125) if present.

**Verify after Step 2:**
- `python -c "from main import run_pipeline; print('imports OK')"` should succeed
- `grep -r "dedup\|entities\|scoring" main.py pipeline/` should return nothing
  (except `pipeline/vectorstore.py` if "entities" appears in a collection name — it doesn't)
- No import errors

---

## Step 3: Filter Optimization — Keyword Rebalancing

**What:** Restructure the keyword lists so that entity names (companies, orgs) don't
auto-pass the filter. Require at least one topic/technology keyword for relevance.
**Why:** Currently, CapitaLand's newsroom scores >= 3 just because the page says
"CapitaLand" (a priority keyword at 3x). It passes the filter even when the content is
about residential condo sales with zero relevance to digital twin / proptech.

### 3a. Restructure `priority_keywords` in `config/sources.py`

**Current `priority_keywords` (lines 79-90):**
```python
"priority_keywords": [
    # Tender/RFP language
    "tender", "RFP", "ITQ", "ITT", "GeBIZ",
    # Product-category terms
    "digital twin", "BIM", "smart FM", "smart building", "proptech", "building automation",
    # Tracked competitor names
    "Hiverlab", "Gelement", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh",
    "FacilityBot", "Cryotos", "Minuscule Technologies", "Alstern Technologies",
    "Aperio", "Nuvola Media", "SSI Corporate", "NeuronCloud",
    # Tracked customer names
    "CapitaLand", "Mapletree", "Lendlease", "JTC", "HDB estate",
],
```

**New `priority_keywords`:**
```python
"priority_keywords": [
    # Tender/RFP language — highest BD priority
    "tender", "RFP", "ITQ", "ITT", "GeBIZ",
    # Core product-category terms — direct Silversea relevance
    "digital twin", "BIM", "smart FM", "smart building", "proptech",
    "building automation", "3D scanning", "point cloud",
    "facility management", "smart facility",
],
```

Changes:
- All competitor names REMOVED from priority_keywords
- All customer names REMOVED from priority_keywords
- Added "3D scanning", "point cloud", "facility management", "smart facility" (core SpatioX capabilities that were missing from priority tier)

### 3b. Restructure `keywords` in `config/sources.py`

**Current `keywords` (lines 91-111):**
```python
"keywords": [
    # Digital twin & immersive tech
    "virtual tour", "3D scan", "point cloud",
    "immersive", "XR", "extended reality", "virtual reality", "augmented reality",
    "metaverse", "spatial computing",
    # Smart FM & buildings
    "facilities management", "building management",
    "smart estate", "intelligent building",
    # Construction & development
    "construction technology", "contech", "greenfield", "smart construction",
    "BCA Green Mark", "IDD", "integrated digital delivery",
    # Government & tenders
    "public sector", "smart nation", "government digital", "built environment",
    # Partners vocabulary
    "M&E integration", "BMS", "building automation system", "asset management system",
    "consultancy", "facilities consultancy",
    # Ecosystem player names (new)
    "MCC", "CSCEC", "CCCC", "CHEC", "Sembcorp", "SJ Group",
    "Meinhardt", "BECA", "Ramboll", "Azbil",
    "Johnson Controls", "Schneider", "Quantum Automation",
    "ST Synthesis", "Savills",
],
```

**New `keywords`:**
```python
"keywords": [
    # Digital twin & immersive tech
    "virtual tour", "3D scan", "3D visualization",
    "immersive", "XR", "extended reality", "virtual reality", "augmented reality",
    "metaverse", "spatial computing",
    # Smart FM & buildings
    "building management", "smart estate", "intelligent building",
    "IoT", "CMMS", "predictive maintenance",
    # Construction & development
    "construction technology", "contech", "greenfield", "smart construction",
    "BCA Green Mark", "IDD", "integrated digital delivery",
    "TOP inspection", "defect inspection", "virtual inspection",
    "sustainability", "green building", "net zero",
    # Government & tenders
    "public sector", "smart nation", "government digital", "built environment",
    # Partners vocabulary
    "M&E integration", "BMS", "building automation system", "asset management system",
    # Tracked entity names — 1x weight, not auto-pass
    # Competitors
    "Hiverlab", "Gelement", "TwinLogic", "TwinMatrix", "Axomem", "DataMesh",
    "FacilityBot", "Cryotos", "Minuscule Technologies", "Alstern Technologies",
    "Aperio", "Nuvola Media", "SSI Corporate", "NeuronCloud",
    # Customers
    "CapitaLand", "Mapletree", "Lendlease", "JTC", "HDB estate",
    # Ecosystem players
    "MCC", "CSCEC", "CCCC", "CHEC", "Sembcorp", "SJ Group",
    "Meinhardt", "BECA", "Ramboll", "Azbil",
    "Johnson Controls", "Schneider", "Quantum Automation",
    "ST Synthesis", "Savills",
],
```

Changes made:
- Entity names (competitor, customer, ecosystem) moved here from priority_keywords — now 1x weight instead of 3x
- Removed "point cloud" (promoted to priority_keywords)
- Removed "facilities management" (promoted to priority_keywords as "facility management")
- Removed "consultancy", "facilities consultancy" (too generic, matches any consulting firm's page)
- Added "3D visualization" — core SpatioX Twin capability
- Added "IoT" — SpatioX Ops integrates IoT sensors
- Added "CMMS" — what competitor products (Cryotos, FacilityBot) are; relevant for competitive intel
- Added "predictive maintenance" — SpatioX Ops use case
- Added "TOP inspection", "defect inspection", "virtual inspection" — direct SpatioX Audit terms
- Added "sustainability", "green building", "net zero" — adjacent to BCA Green Mark, growing policy driver

### 3c. No changes to `filter.py` logic

The `score_relevance()` function and `min_score=3` threshold stay the same. The keyword
rebalancing alone fixes the problem:
- Before: CapitaLand newsroom → "CapitaLand" priority hit (3×1 = 3) → passes
- After: CapitaLand newsroom about condos → "CapitaLand" general hit (1×1 = 1) → fails
- After: CapitaLand newsroom about smart building → "CapitaLand" (1) + "smart building" priority (3) = 4 → passes

The `smart_truncate()` function in `scraper.py` also uses these keyword lists (passed
from `main.py`), so it will automatically benefit from the rebalanced lists — truncation
will now anchor on technology terms rather than entity names.

**Verify after Step 3:**
- Count keywords: priority should have ~10 terms, general should have ~45-50 terms
- No source name should appear in `priority_keywords`
- All competitor, customer, and ecosystem player names should be in `keywords`

---

## Step 4: Set Aperio `active: False`

**What:** In `config/sources.py`, line 70, change Aperio's `active` field.

**Current:**
```python
{"name": "Aperio", "url": "https://aperio.ai/", "sector": "competitors", "type": "website", "active": True},
```

**Change to:**
```python
{"name": "Aperio", "url": "https://aperio.ai/", "sector": "competitors", "type": "website", "active": False},  # returns 403 Forbidden every run
```

---

## Step 5: Scrapling Integration — Tiered Fetcher Strategy

**What:** Add Scrapling as the scraping engine with a per-source `fetcher` config field.
Sources that work with plain HTTP keep using it. Sources that need JS rendering or anti-bot
bypass get Scrapling's specialized fetchers.

**Why:** 5+ sources are currently INACTIVE because the basic requests+BeautifulSoup scraper
can't handle them (403s, JS-required). Scrapling's StealthyFetcher and DynamicFetcher can
unblock them.

### 5a. Add Scrapling dependency

Add to `requirements.txt` (or create if not exists):
```
scrapling[fetchers]
```

Note: After installing, run `scrapling install` to download browser binaries. This is
needed for StealthyFetcher and DynamicFetcher. For GitHub Actions, add this as a setup
step.

### 5b. Add `fetcher` field to source configs

In `config/sources.py`, add a `"fetcher"` key to sources that need non-default fetching.
Sources without the key (or with `"fetcher": "default"`) use the standard HTTP fetcher.

**Sources to update:**

Currently INACTIVE — re-enable with appropriate fetcher:
```python
{"name": "MCC", ..., "active": True, "fetcher": "dynamic"},           # JS-only SPA
{"name": "SJ Group", ..., "active": True, "fetcher": "stealth"},      # 403 bot protection
{"name": "Schneider Electric", ..., "active": True, "fetcher": "stealth"},  # 403 bot protection
{"name": "Alstern Technologies", ..., "active": True, "fetcher": "stealth"},  # 403 bot protection
```

Currently ACTIVE but known to return 403 intermittently — add stealth fetcher:
```python
{"name": "Aperio", ..., "active": True, "fetcher": "stealth"},  # override Step 4 — try stealth first
```

**IMPORTANT:** If Aperio works with stealth fetcher during testing, keep it active with
`"fetcher": "stealth"`. If it still fails, set `active: False` as in Step 4. The execution
agent should try stealth first and fall back to inactive.

All other sources keep `"fetcher": "default"` (or omit the key entirely — default behavior).

**Full list of source lines to modify in `config/sources.py`:**

Line 44 (MCC):
```python
{"name": "MCC", "url": "https://www.mcc.sg/", "sector": "partners", "type": "website", "active": True, "fetcher": "dynamic"},  # JS-only SPA — needs browser rendering
```

Line 49 (SJ Group):
```python
{"name": "SJ Group", "url": "https://www.sjgroup.com/", "sector": "partners", "type": "website", "active": True, "fetcher": "stealth"},  # 403 bot protection — needs stealth
```

Line 55 (Schneider Electric):
```python
{"name": "Schneider Electric", "url": "https://www.se.com/ww/en/", "sector": "partners", "type": "website", "active": True, "fetcher": "stealth"},  # 403 bot protection — needs stealth
```

Line 69 (Alstern Technologies):
```python
{"name": "Alstern Technologies", "url": "https://alstern-technologies.com/", "sector": "competitors", "type": "website", "active": True, "fetcher": "stealth"},  # 403 bot protection — needs stealth
```

Line 70 (Aperio):
```python
{"name": "Aperio", "url": "https://aperio.ai/", "sector": "competitors", "type": "website", "active": True, "fetcher": "stealth"},  # 403 Forbidden with default fetcher — try stealth
```

### 5c. Rewrite `pipeline/scraper.py`

Replace the entire file with the following. The key changes are:
- Three fetcher functions: `_fetch_default()`, `_fetch_stealth()`, `_fetch_dynamic()`
- `scrape_source()` dispatches based on the source's `fetcher` field
- `smart_truncate()` is unchanged
- `scrape_all()` is unchanged except it passes the full source dict

**New `pipeline/scraper.py`:**
```python
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


def _extract_text(html: str) -> str:
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
    from scrapling import StealthyFetcher
    fetcher = StealthyFetcher()
    response = fetcher.fetch(url)
    return _extract_text(response.html)


def _fetch_dynamic(url: str) -> str:
    """Scrapling DynamicFetcher — full browser rendering for JS-heavy SPAs."""
    from scrapling import DynamicFetcher
    fetcher = DynamicFetcher()
    response = fetcher.fetch(url)
    return _extract_text(response.html)


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
```

**IMPORTANT implementation notes for the execution agent:**

1. The Scrapling import is **lazy** (inside each `_fetch_*` function) so it doesn't break
   if scrapling isn't installed — default sources still work with just `requests`.

2. `_extract_text()` is factored out so all three fetchers use the same BeautifulSoup
   cleanup. Scrapling returns raw HTML in `response.html`, not pre-parsed text.

3. **Verify the Scrapling API** before writing: the `response.html` property and
   `StealthyFetcher`/`DynamicFetcher` class names should be confirmed against the actual
   library. Read the Scrapling README or source if needed. The API shown above is based
   on the README as of 2026-06-29 — if the actual API differs, adapt accordingly. The
   key contract is: fetch URL → get HTML string → pass to `_extract_text()`.

4. If Scrapling's API returns a parsed object instead of raw HTML, adapt `_extract_text()`
   or use the object's text extraction method directly.

---

## Step 6: Wire Weekly Summarizer into `main.py`

**What:** Call `generate_weekly_summary()` from `main.py` once per week (Sundays).
**Why:** Currently only callable via `python -m pipeline.weekly` manually.

**In `main.py`**, add this import at the top:
```python
from pipeline.weekly import generate_weekly_summary
```

**After the `for country in active_countries:` loop ends (after line 98's print), add:**
```python
    if datetime.date.today().weekday() == 6:  # Sunday
        print("Running weekly summary (Sunday)...")
        generate_weekly_summary()
```

This goes inside `run_pipeline()` but outside the country loop — at the same indentation
level as the `for country in active_countries:` line.

---

## Step 7: Expand Report History Storage

**What:** Store more than just executive_summary in the report_history ChromaDB collection.
**Why:** The weekly summarizer retrieves these documents to compress into a weekly digest.
Currently it only sees 3-5 headline bullets per day, losing all signal detail.

**In `pipeline/analyst.py`, lines 207-216**, change:

```python
if RAG_ENABLED:
    try:
        summary_for_rag = json.dumps(report_data.get("executive_summary", []))[:1500]
        add_documents(
            REPORT_HISTORY,
            [summary_for_rag],
            metadatas=[{"date": datetime.date.today().isoformat(), "country": country["code"]}],
        )
    except Exception:
        pass
```

**To:**
```python
if RAG_ENABLED:
    try:
        rag_content = {
            "executive_summary": report_data.get("executive_summary", []),
            "signals_by_sector": report_data.get("signals_by_sector", {}),
            "opportunities": report_data.get("opportunities", []),
        }
        summary_for_rag = json.dumps(rag_content, ensure_ascii=False)[:4000]
        add_documents(
            REPORT_HISTORY,
            [summary_for_rag],
            metadatas=[{"date": datetime.date.today().isoformat(), "country": country["code"]}],
        )
    except Exception:
        pass
```

Changes:
- Stores executive_summary + signals_by_sector + opportunities (not just executive_summary)
- Truncation limit raised from 1500 to 4000 chars (still safe for ChromaDB, gives the
  weekly summarizer much more to work with)
- Added `ensure_ascii=False` for proper Unicode handling

---

## Execution Order

Steps MUST be executed in this order due to dependencies:

```
Step 1 (config/models.py)     — no dependencies, do first
Step 2 (remove dead code)     — depends on Step 1 (analyst.py MODEL → GROQ_MODEL)
Step 3 (filter keywords)      — independent of Steps 1-2, but do after to avoid merge conflicts in sources.py
Step 4 (Aperio inactive)      — do with Step 3 (same file), BUT see Step 5 note about trying stealth first
Step 5 (Scrapling)            — depends on Step 3 (sources.py changes already applied)
Step 6 (weekly summarizer)    — independent, do anytime after Step 2 (main.py is modified in Step 2)
Step 7 (report history)       — depends on Step 1 (analyst.py already modified)
```

Recommended batching:
- **Batch A (config + cleanup):** Steps 1, 2
- **Batch B (filter + sources):** Steps 3, 4
- **Batch C (scraper):** Step 5
- **Batch D (RAG prep):** Steps 6, 7

---

## Post-Execution Verification Checklist

After all steps are complete, verify:

1. **Import check:** `python -c "from main import run_pipeline; print('OK')"` — no import errors
2. **No stale references:** `grep -r "dedup\|entities\|scoring" main.py pipeline/` — should return nothing
3. **Model constant consolidated:** `grep -r "llama-4-scout" pipeline/ config/` — only in `config/models.py`
4. **No entity names in priority_keywords:** visually confirm `config/sources.py` priority_keywords has only technology/domain terms
5. **Scrapling lazy imports work:** `python -c "from pipeline.scraper import scrape_source; print('OK')"` — should work even without scrapling installed (lazy import)
6. **Weekly summarizer wired:** `grep "weekly" main.py` — should show import and Sunday check

Do NOT run the full pipeline (`python main.py`) — that requires Groq API tokens and is
deferred to the testing phase.

---

## Files Modified (Summary)

| File | Action |
|------|--------|
| `config/models.py` | **CREATE** — shared GROQ_MODEL constant |
| `config/sources.py` | EDIT — restructure keywords, add fetcher fields, remove entities dict, Aperio inactive |
| `pipeline/scraper.py` | REWRITE — add Scrapling fetcher dispatch |
| `pipeline/analyst.py` | EDIT — import GROQ_MODEL, expand report history storage |
| `pipeline/feedback.py` | EDIT — import GROQ_MODEL |
| `pipeline/weekly.py` | EDIT — import GROQ_MODEL |
| `main.py` | EDIT — remove dead imports/calls, wire weekly summarizer, fix print |
| `pipeline/dedup.py` | **DELETE** |
| `pipeline/entities.py` | **DELETE** |
| `pipeline/scoring.py` | **DELETE** |
| `data/source_scores.json` | **DELETE** (if exists) |
