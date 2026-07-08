# Task 002: Dry-run and verify all new VN sources (fetcher tiering + active flags)

**Status:** pending

## Files

- `config/sources.json` (modify only — flip `active`/add `fetcher` on individual VN source
  objects added by Task 001; no structural changes)

## What to do

Task 001 added ~60 VN source objects to `config/sources.json`, all defaulting to `"active": true`
with no `"fetcher"` field (implicit `"default"` — plain `requests` fetch, see
`pipeline/scraper.py`'s `FETCHERS` dict). This task repeats the same live-verification process
used to originally onboard the SG source list (see DECISIONS.md's 2026-06-29 entries: IMDA needed
`fetcher: "dynamic"`, CCCC was set `active: False` after consistent timeouts, etc.).

**This is a live-HTTP task, not an LLM task** — it makes real requests to the VN source URLs, but
makes zero Groq API calls, so it does not touch the daily LLM quota and can be fully executed and
verified in this task, unlike a full pipeline run.

For each of the ~52 active, URL-bearing VN sources added by Task 001 (skip the 8 no-URL entries —
they're already `active: false` and out of scope here):

1. Fetch the URL with `pipeline.scraper`'s default fetcher first (plain `requests` — you can call
   `pipeline.scraper.scrape_source(source, priority_keywords, keywords)` directly, or just
   `requests.get(url, headers=pipeline.scraper.HEADERS, timeout=15)` for a quicker probe).
2. If the default fetch succeeds (200 status, non-trivial extracted text — use
   `MIN_CONTENT_CHARS = 150` from `pipeline/analyst.py` as a rough usefulness bar, though this
   task is about scrapability, not filter-passing) — leave the source as-is (no `fetcher` field,
   `active: true`).
3. If the default fetch fails with a 403 or a bot-challenge page (common for Cloudflare-protected
   sites — several VN government/large-corporate sites are plausible candidates per CONTEXT.md's
   Open Questions), retry with `_fetch_stealth()` (Scrapling `StealthyFetcher`). If that succeeds,
   set `"fetcher": "stealth"` on that source.
4. If stealth also fails, or the page is a JS-rendered SPA returning near-empty text via plain
   `requests`/stealth (empty `<div id="app">`-style shells are the usual tell), try
   `_fetch_dynamic()` (Scrapling `DynamicFetcher`). If that succeeds, set `"fetcher": "dynamic"`.
5. If all three tiers fail (timeout, persistent 403, 404, DNS failure, or consistently unusable
   content), set `"active": false` and add an `"inactive_reason"` string describing *why*
   (mirroring the SG precedent — e.g. `"Consistently times out from this network"`,
   `"404 — URL structure changed"`, `"Cloudflare-protected, stealth and dynamic fetchers both
   failed"`). Do not guess at a corrected URL — if a source's newsroom/press page structure isn't
   obvious from the homepage, mark it inactive with a reason noting that, rather than spending
   excessive time hunting for the "real" URL (that's a reasonable future admin/Alfonso follow-up,
   not blocking this task).

Expect some Vietnamese-language-only sources to return real content but score low against the
English-only VN keyword list from Task 001 — that is explicitly a known, accepted limitation this
round (CONTEXT.md's Open Questions) and is **not** a reason to mark a source inactive here; this
task is purely about whether content can be *fetched*, not whether it will pass the relevance
filter. Do not modify `priority_keywords`/`keywords` in this task even if you notice low
keyword-hit rates — that's explicitly out of this task's scope (flag it in your evidence report
if you think it's severe enough to matter, but don't act on it).

Track your per-source results (URL tested, tier that worked or failure reason) — you'll need this
list for the Verification section and for your final report to the dispatching session.

## Interfaces

None — no code changes, only per-source `active`/`fetcher`/`inactive_reason` field values in
`config/sources.json`.

## Constraints

- Do not add, remove, or rename any source objects — only modify `active`, `fetcher`, and
  `inactive_reason` on the existing ~60 VN entries from Task 001.
- Do not touch the SG country block.
- Do not touch VN's `priority_keywords`/`keywords` (see note above).
- All writes must go through `config.sources.save_sources()` (disk-reread, sibling-key-preserving)
  if you script the edits — do not hand-roll a separate read/write path. Direct manual edits via
  the Edit tool are also fine as long as the file stays valid JSON afterward.
- Respect `pipeline/scraper.py`'s existing `REQUEST_TIMEOUT = 15` — don't invent a longer timeout
  to force a marginal source to "succeed"; if it needs more than 15s on a plain fetch, that's
  itself useful information (though Scrapling's fetchers may have their own internal timeouts —
  use their defaults).

## Verification

No LLM call needed — this task's own execution *is* the verification (live HTTP fetches), plus:

1. `py -c "import json; json.load(open('config/sources.json', encoding='utf-8'))"` — must succeed,
   confirming the file is still valid JSON after your edits.
2. `py -c "from config.sources import load_sources; c=[x for x in load_sources() if x['code']=='VN'][0]; print(len(c['sources']))"`
   — must print the same total source count as after Task 001 (you may only change field values,
   never the count).
3. Produce a summary table (in your final report to the dispatching session, not necessarily a
   file) of: how many VN sources ended up `active: true` with no `fetcher` (default), how many
   with `fetcher: "stealth"`, how many with `fetcher: "dynamic"`, and how many `active: false`
   (with their `inactive_reason`s). This is the same shape of evidence DECISIONS.md records for
   the SG onboarding (e.g. "Active source count: 57").
4. Spot-check at least 3 sources end-to-end via `pipeline.scraper.scrape_source(source,
   priority_keywords, keywords)` using the actual VN `priority_keywords`/`keywords` from
   `config/sources.json`, confirming real extracted text comes back (not an empty string or an
   error dict) for whichever fetcher tier you assigned each one.

## Model tier

mid — mechanical field updates, but each source's fetcher-tier decision requires judgment based on
live HTTP behavior (mirrors the SG onboarding process, which was also mid/manual judgment, not a
scripted classifier).

## Depends on

Task 001 (`001-vn-sources-json.md`) — the VN sources must exist in `config/sources.json` before
they can be dry-run tested. Both tasks modify `config/sources.json`; this task must run strictly
after Task 001 lands, not in parallel with it.

## Evidence

