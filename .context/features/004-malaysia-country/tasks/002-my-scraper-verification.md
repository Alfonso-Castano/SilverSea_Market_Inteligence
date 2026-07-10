# Task 002: Dry-run and verify all 55 MY sources (fetcher tiering + active flags)

**Status:** done

## Files

- `config/sources.json` (modify only — flip `active`/add `fetcher`/add `inactive_reason` on
  individual MY source objects added by Task 001; no structural changes, no new/removed/renamed
  source objects)

## What to do

Task 001 added 55 MY source objects to `config/sources.json`, all defaulting to `"active": true`
with no `"fetcher"` field (implicit `"default"` — plain `requests` fetch, see
`pipeline/scraper.py`'s `FETCHERS` dict). This task repeats the same live-verification process
used to onboard SG's and Vietnam's source lists (see DECISIONS.md's 2026-06-29 entries and
Vietnam's own Task 002 for precedent: IMDA needed `fetcher: "dynamic"`, CCCC was set
`active: False` after consistent timeouts, several VN sources needed `fetcher: "stealth"` for
Cloudflare/bot protection, and a few were caught serving a Cloudflare challenge page that a naive
status/length check would have missed).

**This is a live-HTTP task, not an LLM task** — it makes real requests to the 55 MY source URLs,
but makes zero Groq API calls, so it does not touch the daily LLM quota and can be fully executed
and verified in this task, unlike a full pipeline run.

All 55 MY sources have a URL (unlike Vietnam, which had 8 no-URL stubs already `active: false` and
out of scope) — so all 55 need to be dry-run tested here.

For each of the 55 MY sources added by Task 001:

1. Fetch the URL with `pipeline.scraper`'s default fetcher first (plain `requests` — you can call
   `pipeline.scraper.scrape_source(source, priority_keywords, keywords)` directly, or just
   `requests.get(url, headers=pipeline.scraper.HEADERS, timeout=15)` for a quicker probe).
2. If the default fetch succeeds (200 status, non-trivial extracted text — use
   `MIN_CONTENT_CHARS = 150` from `pipeline/analyst.py` as a rough usefulness bar, though this
   task is about scrapability, not filter-passing) — leave the source as-is (no `fetcher` field,
   `active: true`).
3. If the default fetch fails with a 403 or a bot-challenge page (common for Cloudflare-protected
   sites — corporate sites like Accenture, Huawei Cloud, CelcomDigi, Sharp are plausible
   candidates), retry with `_fetch_stealth()` (Scrapling `StealthyFetcher`). If that succeeds, set
   `"fetcher": "stealth"` on that source.
4. If stealth also fails, or the page is a JS-rendered SPA returning near-empty text via plain
   `requests`/stealth (empty `<div id="app">`-style shells are the usual tell — several MY sources
   use `#/i18n`-style hash routing, e.g. U Learning, which is a plausible SPA candidate), try
   `_fetch_dynamic()` (Scrapling `DynamicFetcher`). If that succeeds, set `"fetcher": "dynamic"`.
5. If all three tiers fail (timeout, persistent 403, 404, DNS failure, or consistently unusable
   content), set `"active": false` and add an `"inactive_reason"` string describing *why*
   (mirroring the SG/VN precedent — e.g. `"Consistently times out from this network"`, `"404 —
   URL structure changed"`, `"Cloudflare-protected, stealth and dynamic fetchers both failed"`).
   Do not guess at a corrected URL — if a source's newsroom/press page structure isn't obvious
   from the homepage, mark it inactive with a reason noting that, rather than spending excessive
   time hunting for the "real" URL (a reasonable future admin/Alfonso follow-up, not blocking this
   task). Several MY URLs point at a homepage rather than a dedicated newsroom/press page (e.g.
   `https://www.mdec.my/`, `https://www.perodua.com.my/`) — that alone is not a reason to mark a
   source inactive; only mark inactive if the fetch itself genuinely fails or returns unusable
   content, matching the SG/VN precedent of accepting homepage URLs when no better page was
   supplied.

Watch specifically for the Cloudflare-challenge-page failure mode VN's Task 002 caught (FPT, ATZ):
a fetch that returns 200 status and >150 chars can still be a "Just a moment..." challenge page,
not real content — inspect actual body text, not just status/length, before accepting a tier as
successful.

Do not modify `priority_keywords`/`keywords` in this task even if you notice low keyword-hit rates
on a specific source — that's explicitly out of this task's scope (flag it in your evidence report
if you think it's severe enough to matter, but don't act on it).

Track your per-source results (URL tested, tier that worked or failure reason) — you'll need this
list for the Verification section and for your final report to the dispatching session.

## Interfaces

None — no code changes, only per-source `active`/`fetcher`/`inactive_reason` field values in
`config/sources.json`.

## Constraints

- Do not add, remove, or rename any source objects — only modify `active`, `fetcher`, and
  `inactive_reason` on the existing 55 MY entries from Task 001.
- Do not touch the SG country block.
- Do not touch MY's `priority_keywords`/`keywords` (see note above).
- Direct manual edits via the Edit tool are fine as long as the file stays valid JSON afterward —
  no need to script through `config.sources.save_sources()` for this one-time verification pass.
- Respect `pipeline/scraper.py`'s existing `REQUEST_TIMEOUT = 15` — don't invent a longer timeout
  to force a marginal source to "succeed"; if it needs more than 15s on a plain fetch, that's
  itself useful information (though Scrapling's fetchers may have their own internal timeouts —
  use their defaults).

## Verification

No LLM call needed — this task's own execution *is* the verification (live HTTP fetches), plus:

1. `py -c "import json; json.load(open('config/sources.json', encoding='utf-8'))"` — must succeed,
   confirming the file is still valid JSON after your edits.
2. `py -c "from config.sources import load_sources; c=[x for x in load_sources() if x['code']=='MY'][0]; print(len(c['sources']))"`
   — must print `55` (same total as after Task 001; you may only change field values, never the
   count).
3. Produce a summary table (in your final report to the dispatching session, not necessarily a
   file) of: how many MY sources ended up `active: true` with no `fetcher` (default), how many
   with `fetcher: "stealth"`, how many with `fetcher: "dynamic"`, and how many `active: false`
   (with their `inactive_reason`s) — same shape of evidence as SG's/VN's onboarding record.
4. Spot-check at least 3 sources end-to-end via `pipeline.scraper.scrape_source(source,
   priority_keywords, keywords)` using the actual MY `priority_keywords`/`keywords` from
   `config/sources.json`, confirming real extracted text comes back (not an empty string or an
   error dict) for whichever fetcher tier you assigned each one.

## Model tier

mid — mechanical field updates, but each source's fetcher-tier decision requires judgment based on
live HTTP behavior (mirrors the SG/VN onboarding process, which was also mid/manual judgment, not
a scripted classifier).

## Depends on

Task 001 (`001-my-sources-json.md`) — the MY sources must exist in `config/sources.json` before
they can be dry-run tested. Both tasks modify `config/sources.json`; this task must run strictly
after Task 001 lands, not in parallel with it.

## Evidence

Executor report (DONE). Live dry-run of all 55 MY sources:

| Tier | Count |
|---|---|
| `active: true`, no fetcher (default) | 50 |
| `active: true`, `fetcher: "stealth"` | 2 |
| `active: true`, `fetcher: "dynamic"` | 0 |
| Newly `active: false` | 3 |
| **Total** | **55** |

Stealth-tier: Panasonic Appliances Marketing Asia Pacific (default 403 → stealth 200), Air Selangor (default 200 but 19-char SPA shell → stealth 200, real content).

Newly inactive (all 3 tiers failed): U Learning (hash-routing SPA, all tiers return only a Chinese-language cookie-consent banner), Art Network Events (SPA shell, ~30 chars across all tiers), Unbound Malaysia (SPA shell, ~116 chars across all tiers).

No Cloudflare challenge pages found masquerading as 200s (checked systematically, not just spot-checked). Corporate sites flagged as plausible Cloudflare candidates (Accenture, Huawei Cloud, CelcomDigi, Sharp) all succeeded on the plain default fetcher — no escalation needed.

Spot-checked 4 sources end-to-end via `pipeline.scraper.scrape_source()` with real MY keyword lists — all returned real extracted text.

Files changed: `config/sources.json` only (8 insertions / 3 deletions across exactly 5 source objects — field-level only, source count unchanged at 55).
