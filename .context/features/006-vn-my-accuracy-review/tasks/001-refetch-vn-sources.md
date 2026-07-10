# Task 001: Re-fetch the 15 live source pages cited in the VN BER report

**Status:** pending
**Depends on:** none
**Model tier:** cheap — the exact source list, fetcher tiers, and the function to call are all specified
below; this is mechanical execution (call an existing function per source, dump the results), not
judgment.

## Files
- Create: `.context/features/006-vn-my-accuracy-review/refetched/vn_sources.json`

## What to do

`data/latest_report_VN_BER.json`'s `data_sources` array lists 15 sources the pipeline actually scraped
for that report. No raw scrape content survives from the original run (see CONTEXT.md) — this task
re-fetches those same 15 URLs live, right now, using the pipeline's own existing tiered fetchers
(`pipeline/scraper.py`'s `scrape_source()` — zero LLM cost, plain HTTP / Scrapling only), so a later task
can compare today's live content against the report's claims.

Run a short Python script (inline via `py -c` or a throwaway `.py` file) that:

1. Builds this exact list of 15 source dicts (name, url, sector, fetcher — taken directly from
   `config/sources.json`'s VN block; `type` can be omitted, `scrape_source()` defaults it):

```python
VN_SOURCES = [
    {"name": "Viettel Group", "url": "https://viettel.com.vn/en/", "sector": "competitors", "fetcher": "stealth"},
    {"name": "Becamex IDC", "url": "https://becamex.com.vn", "sector": "competitors", "fetcher": "stealth"},
    {"name": "Siemens", "url": "https://www.siemens.com", "sector": "competitors", "fetcher": "default"},
    {"name": "Honeywell", "url": "https://www.honeywell.com", "sector": "competitors", "fetcher": "default"},
    {"name": "Johnson Controls", "url": "https://www.johnsoncontrols.com", "sector": "competitors", "fetcher": "default"},
    {"name": "Bentley Systems", "url": "https://www.bentley.com", "sector": "competitors", "fetcher": "stealth"},
    {"name": "Matterport", "url": "https://matterport.com", "sector": "competitors", "fetcher": "default"},
    {"name": "NVIDIA", "url": "https://www.nvidia.com", "sector": "partners", "fetcher": "default"},
    {"name": "Dell Technologies", "url": "https://www.dell.com", "sector": "partners", "fetcher": "stealth"},
    {"name": "Cisco", "url": "https://www.cisco.com", "sector": "partners", "fetcher": "stealth"},
    {"name": "CBRE Vietnam", "url": "https://www.cbrevietnam.com", "sector": "partners", "fetcher": "default"},
    {"name": "Vietnam Investment Review", "url": "https://vir.com.vn", "sector": "general_news", "fetcher": "default"},
    {"name": "TTDecor", "url": "https://ttdecor.net/gioi-thieu-art", "sector": "customers", "fetcher": "default"},
    {"name": "Vietsoft Pro", "url": "https://vietsoftpro.com/", "sector": "customers", "fetcher": "default"},
    {"name": "BM Windows", "url": "https://bmwindows.vn/vi", "sector": "customers", "fetcher": "default"},
]
```

2. For each source, call `pipeline.scraper.scrape_source(source, priority_keywords, keywords)` — pass
   VN's real `priority_keywords`/`keywords` from `config/sources.json` (via
   `config.sources.load_sources()`, find the `"VN"` country dict) so `smart_truncate()` behaves exactly
   as it would in a real pipeline run. This returns a dict with `{name, url, type, sector, content,
   error}` per source — do not hand-roll a different fetch path.

3. Write the full list of 15 result dicts (in the same order as `VN_SOURCES` above) as a JSON array to
   `.context/features/006-vn-my-accuracy-review/refetched/vn_sources.json` (create the `refetched/`
   directory if it doesn't exist). Use `json.dump(..., indent=2, ensure_ascii=False)` and
   `encoding="utf-8"` on the file handle, matching `pipeline/report.py`'s convention.

Expect some failures (dead links, redesigned sites, bot-blocking beyond what `stealth` handles) — that's
fine and itself useful information for the downstream accuracy audit; don't retry indefinitely or
escalate a source's fetcher tier beyond what's specified above (e.g. don't promote a failing `"default"`
source to `"dynamic"` — that's out of scope here; just record the error and move on).

## Interfaces
- Consumes: `pipeline.scraper.scrape_source()` (unmodified, read-only use), `config.sources.load_sources()`
  for VN's keyword lists.
- Produces: `refetched/vn_sources.json` — a JSON array of 15 `{name, url, type, sector, content, error}`
  dicts, consumed by Task 003 (VN accuracy audit).

## Constraints
- Zero LLM/Groq API calls — this task only does live HTTP/Scrapling fetches via `scrape_source()`.
- Do not modify `pipeline/scraper.py`, `config/sources.json`, or any pipeline file — this task only
  writes the one new cache file listed above.
- Do not fetch any URL other than the 15 listed above — this is a targeted, scoped re-fetch, not a full
  VN source-list crawl.

## Verification
1. `py -c "import json; d = json.load(open('.context/features/006-vn-my-accuracy-review/refetched/vn_sources.json', encoding='utf-8')); print(len(d)); print(sum(1 for r in d if not r['error']))"`
   — must print `15` on the first line (all 15 sources present) and the count of successful fetches on
   the second line (some failures are acceptable; zero non-error results would indicate something is
   broken, e.g. no network access from this environment — investigate rather than silently accepting an
   all-empty file).
2. Spot-check in your final report: paste the `content` length (in chars) and `error` value for at least
   3 of the 15 sources, so the dispatching session can see real output was captured, not stub data.

## Evidence
[Filled in at completion]
