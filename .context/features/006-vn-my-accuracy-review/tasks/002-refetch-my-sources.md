# Task 002: Re-fetch the 25 live source pages cited in the MY GENERAL report

**Status:** done
**Depends on:** none
**Model tier:** cheap — the exact source list, fetcher tiers, and the function to call are all specified
below; this is mechanical execution (call an existing function per source, dump the results), not
judgment.

## Files
- Create: `.context/features/006-vn-my-accuracy-review/refetched/my_sources.json`

## What to do

`data/latest_report_MY_GENERAL.json`'s `data_sources` array lists 25 sources the pipeline actually
scraped for that report. No raw scrape content survives from the original run (see CONTEXT.md) — this
task re-fetches those same 25 URLs live, right now, using the pipeline's own existing tiered fetchers
(`pipeline/scraper.py`'s `scrape_source()` — zero LLM cost, plain HTTP / Scrapling only), so a later task
can compare today's live content against the report's claims.

Run a short Python script (inline via `py -c` or a throwaway `.py` file) that:

1. Builds this exact list of 25 source dicts (name, url, sector — taken directly from
   `config/sources.json`'s MY block; all 25 use `fetcher: "default"`, so the field can be omitted or set
   explicitly to `"default"`; `type` can be omitted, `scrape_source()` defaults it):

```python
MY_SOURCES = [
    {"name": "National Art Gallery", "url": "https://www.artgallery.gov.my/", "sector": "gov_agencies"},
    {"name": "GreenRE", "url": "https://www.greenre.org/#", "sector": "associations"},
    {"name": "REDHA Institute", "url": "https://rehdainstitute.com/#", "sector": "associations"},
    {"name": "PKNS FM Integrated Sdn Bhd", "url": "https://pknsfmi.com/", "sector": "customers"},
    {"name": "Avisena Women's & Children Specialist Hospital", "url": "https://ash2.avisena.com.my/", "sector": "customers"},
    {"name": "Capri by Fraser", "url": "https://www.frasershospitality.com/en/malaysia/kualalumpur/capri-by-fraser-bukit-bintang/", "sector": "customers"},
    {"name": "City Motor Group", "url": "https://citymotorsgroup.com.my/", "sector": "customers"},
    {"name": "NCT Borneo Sdn Bhd", "url": "https://nct.net.my/", "sector": "customers"},
    {"name": "IHH Healthcare", "url": "https://www.ihhhealthcare.com/", "sector": "customers"},
    {"name": "UCSI Hospital", "url": "https://www.ucsiuniversity.edu.my/", "sector": "customers"},
    {"name": "UOA Development Berhad", "url": "https://uoa.com.my/", "sector": "customers"},
    {"name": "Sunway Group", "url": "https://www.sunway.com.my/", "sector": "customers"},
    {"name": "Sunway Medical Centre", "url": "https://www.sunwaymedical.com/en/", "sector": "customers"},
    {"name": "Sunway Property", "url": "https://sunwayproperty.com/", "sector": "customers"},
    {"name": "TA Global", "url": "https://taglobal.com.my/", "sector": "customers"},
    {"name": "Bandar Utama City Center Sdn Bhd", "url": "https://www.1utama.com.my/", "sector": "customers"},
    {"name": "Malaysia Airlines", "url": "https://www.malaysiaairlines.com/my/en/home.html", "sector": "customers"},
    {"name": "Malaysia Airport Holding Berhad", "url": "https://corporate.malaysiaairports.com.my/en", "sector": "customers"},
    {"name": "ITMAX System Berhad", "url": "https://itmax.com.my/", "sector": "partners"},
    {"name": "Redtone", "url": "https://www.redtone.com/", "sector": "partners"},
    {"name": "Serve Deck Innovation Sdn Bhd", "url": "https://www.servedeck.com/", "sector": "competitors"},
    {"name": "Accenture", "url": "https://www.accenture.com/my-en", "sector": "competitors"},
    {"name": "Virtualtech Frontier", "url": "https://www.virtualtechfrontier.com/", "sector": "competitors"},
    {"name": "3 Particles", "url": "https://www.3particle.com/", "sector": "competitors"},
    {"name": "Dreamory", "url": "https://dreamorygroup.com/", "sector": "general_news"},
]
```

2. For each source, call `pipeline.scraper.scrape_source(source, priority_keywords, keywords)` — pass
   MY's real `priority_keywords`/`keywords` from `config/sources.json` (via
   `config.sources.load_sources()`, find the `"MY"` country dict) so `smart_truncate()` behaves exactly
   as it would in a real pipeline run. This returns a dict with `{name, url, type, sector, content,
   error}` per source — do not hand-roll a different fetch path.

3. Write the full list of 25 result dicts (in the same order as `MY_SOURCES` above) as a JSON array to
   `.context/features/006-vn-my-accuracy-review/refetched/my_sources.json` (create the `refetched/`
   directory if it doesn't exist — Task 001 may or may not have created it already, either is fine).
   Use `json.dump(..., indent=2, ensure_ascii=False)` and `encoding="utf-8"` on the file handle, matching
   `pipeline/report.py`'s convention.

Expect some failures (dead links, redesigned sites, bot-blocking) — that's fine and itself useful
information for the downstream accuracy audit; don't retry indefinitely or escalate a source's fetcher
tier beyond `"default"` (none of these 25 are configured with `stealth`/`dynamic` — if a fetch fails,
just record the error, don't promote the tier yourself).

## Interfaces
- Consumes: `pipeline.scraper.scrape_source()` (unmodified, read-only use), `config.sources.load_sources()`
  for MY's keyword lists.
- Produces: `refetched/my_sources.json` — a JSON array of 25 `{name, url, type, sector, content, error}`
  dicts, consumed by Task 004 (MY accuracy audit).

## Constraints
- Zero LLM/Groq API calls — this task only does live HTTP fetches via `scrape_source()`.
- Do not modify `pipeline/scraper.py`, `config/sources.json`, or any pipeline file — this task only
  writes the one new cache file listed above.
- Do not fetch any URL other than the 25 listed above — this is a targeted, scoped re-fetch, not a full
  MY source-list crawl.
- This task is independent of Task 001 (different file, different country) — do not wait for it.

## Verification
1. `py -c "import json; d = json.load(open('.context/features/006-vn-my-accuracy-review/refetched/my_sources.json', encoding='utf-8')); print(len(d)); print(sum(1 for r in d if not r['error']))"`
   — must print `25` on the first line (all 25 sources present) and the count of successful fetches on
   the second line (some failures are acceptable; zero non-error results would indicate something is
   broken, e.g. no network access from this environment — investigate rather than silently accepting an
   all-empty file).
2. Spot-check in your final report: paste the `content` length (in chars) and `error` value for at least
   3 of the 25 sources, so the dispatching session can see real output was captured, not stub data.

## Evidence
DONE (haiku executor). Verification output: `25` / `25` — all 25 MY sources present, all fetched with zero errors, zero LLM/Groq calls (pure HTTP/Scrapling via `scrape_source()`). Spot-check content lengths: National Art Gallery 1361, Capri by Fraser 6000, Sunway Medical Centre 6000 chars (all error=None). MY keywords loaded correctly (15 priority + 99 regular). Output written to `refetched/my_sources.json` (UTF-8, ensure_ascii=False, indent=2). No pipeline files modified.
