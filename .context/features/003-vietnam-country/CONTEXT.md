# Feature: Vietnam Country Expansion

**Base:** 168810eeb12c6e9d5bd257c0b0df9620315d765e

## Goal

Add Vietnam (`VN`) as a second, fully independent country in the market intelligence pipeline, using the real source list Alfonso received from the Vietnam branch — exercising and completing the `--country` scaffolding that has existed since Supervisor Feedback Round 2 but was never run against real second-country data.

## Scope

**In scope:**
- New `"Vietnam"` / `"VN"` country block in `config/sources.json`: ~55 sources from the supplied source list (`Silversea_Vietnam_Market_07072026.pdf`), mapped into the existing 6-sector taxonomy, with their own `priority_keywords`/`keywords` lists (country-level, not shared with SG).
- Fix `app.py`'s `/` and `/internals` routes to be country-aware (`?country=SG|VN` query param, mirroring the existing `_domain_mode()` pattern) instead of hardcoding `"SG"` into the report filename lookup.
- Add a country switcher to the dashboard UI (`templates/base.html`/`report.html`), alongside the existing domain tabs.
- Fix `admin.html`'s country `<select>` to list all countries from `config/sources.json` instead of a hardcoded single `SG` option.
- Fix `pipeline/analyst.py`'s `SUMMARY_PROMPT`, which currently hardcodes "Singapore" in its system framing — must reflect whichever country is actually being analysed.
- Add a parallel Vietnam subsection to `data/company_context.md`'s "Key Prospects & Relationships" and "Ecosystem Players" sections, using entities from the supplied source list (Vingroup, Sun Group, VSIP, FPT, Viettel, Becamex, etc.). Product catalog, BD Priorities, and Regulatory sections stay untouched (already country-agnostic).
- Country-scope `pipeline/feedback.py` and `pipeline/weekly.py` — both currently write to/query global, un-scoped ChromaDB collections. Add `country` metadata tagging and filtering, matching the pattern `pipeline/analyst.py` already uses for `REPORT_HISTORY` writes.
- Country-scope `run_metadata.json` (known bug, STATE.md) — write `run_metadata_{country_code}.json` per run, mirroring `report.py`'s existing domain-scoping filename pattern, so `/internals` can show the right country's metadata.
- Verify newly-added VN sources are actually scrapeable (dry-run each, mark `fetcher: default|stealth|dynamic` and `active: true|false` per source) — same iterative process used to onboard the original ~57 SG sources.

**Explicitly out of scope:**
- Any change to the analysis architecture (multi-pass extract→synthesize→summary), the opportunity scoring rubric, or the RAG mechanism itself. Vietnam runs through the identical pipeline logic as Singapore — only source list, keywords, and the fixes above are country-specific.
- Vietnamese-language keyword matching. The filter does plain English substring matching; VN keywords are English-only for this round (see Decisions below). Sources that score consistently low due to Vietnamese-only content are a known, accepted limitation — not a blocker for this feature.
- MY/ID country expansion. This feature is Vietnam-only; the pattern it establishes should make MY/ID additive later, but they are not being built now.
- A live `main.py --country=VN` end-to-end run burning Groq quota. Per CLAUDE.md's verification protocol, this is an Alfonso-owned manual checkpoint, same as Feature 001's still-open SG checkpoint.
- Resolving the pre-existing `_domain_tagging_status` draft-flag review (STATE.md open item) — unrelated to this feature, not reopened here.

## Implementation Decisions

- **Feedback/weekly country-scoping**: Fix now, not deferred again. *(User decision.)* Rationale given: without this, VN feedback digests and SG feedback digests blend into one global collection, directly undermining the requirement that "the country runs separately."
- **company_context.md**: Add a parallel Vietnam subsection to "Key Prospects & Relationships" and "Ecosystem Players," rather than leaving those sections Singapore-only. *(User decision.)* Rationale: RAG retrieval against `COMPANY_CONTEXT` is not country-filtered by design (correct for the product catalog), so leaving these two sections SG-only would surface irrelevant SG prospect framing into every VN report.
- **Sector mapping** for the VN source list's categories, which don't map 1:1 onto the pipeline's 6-sector taxonomy (no "associations" category in the VN list): *(User-confirmed.)*
  - `Government Authority` → `gov_agencies`
  - `Target Customer`, `Existing Customer`, `Potential Customer`, `Customer` → `customers`
  - `Competitor`, `Competitor / partner` (Siemens) → `competitors`
  - `Dealer / Supplier` → `partners`
  - `Facility Management` (Savills Vietnam, CBRE Vietnam) → `partners`
  - `News / Research` → `general_news`
- **VN keyword list**: Reuse SG's `priority_keywords`/`keywords` as the starting point, stripped of SG-specific procurement terms (`GeBIZ`, `BCA Green Mark`) and SG-only competitor names (`Hiverlab`, `Gelement`, `TwinLogic`, `TwinMatrix`). English-only for this round — no Vietnamese-language equivalents. *(User decision.)* Rationale: keeps effort proportional; empirically verify keyword-hit rate during the source dry-run pass rather than upfront translation work, matching how SG's source list was iteratively tuned (see DECISIONS.md 2026-06-29 entries).
- **Domain tagging for VN sources**: Default `["GENERAL", "BER"]` per source, matching SG's default. Dual-tag `["BER", "EDU"]` for sources with a clear education angle — Ministry of Education & Training (MOET), Văn Lang University, HUIT — following the NUS/NTU dual-tagging precedent from Feature 001. *(Claude's default judgment — not explicitly asked, flagged here for visibility.)*
- **VN source `active` status**: All newly-added sources start `active: true`; the scraper-verification task (dry-run + fetcher tiering) may flip individual sources to `active: false` per the established pattern, same as SGTech/CPG Consultant/FacilityBot/CCCC were in prior rounds. *(Claude's default judgment.)*
- **`app.py` country routing**: Add a `_country_mode()` helper mirroring `_domain_mode()` (`request.args.get("country", "SG")`, validated against known country codes read from `config/sources.py`), used by both `/` and `/internals`. *(Claude's default judgment — only one sensible approach given the existing domain-mode precedent.)*
- **Branching**: This feature branches from `main` (168810e), not from `feature/002-local-llm-backend` (the branch this session started on). That branch has an unrelated, uncommitted CONTEXT.md for a different, not-yet-executed feature (local Ollama LLM backend) — left untouched. *(User decision.)*

## Global Constraints

- Every task must preserve `main.py --country=SG` (and `--domain=` filtering) behaving exactly as it does today — this feature is additive, not a rework of existing country/domain handling.
- `config/sources.json` writes must go through `config/sources.py`'s `load_sources()`/`save_sources()` (disk-reread, sibling-key-preserving) — never hand-roll a separate read/write path.
- Follow the existing per-country nesting convention: no redundant per-source `"country"` field (per the 2026-07-02 decision — country is fully determined by which country block a source lives under).
- Match existing Jinja2/Tailwind patterns for any new UI (country tabs should visually follow the existing domain-tab implementation in `base.html`, not introduce a new component style).
- No new Python dependencies. No architecture change to the LLM call pattern, ChromaDB collection structure (metadata-filter additions are fine; new collections are not), or Flask routing style.
- `SUMMARY_PROMPT` and any other country-specific prompt text must interpolate the actual country name from the `country` dict already passed into `analyse()` — no second hardcoded country string introduced anywhere.

## Open Questions

- Exact `fetcher` tier (`default`/`stealth`/`dynamic`) per VN source is unknown until dry-run verification during execution — expect some VN sources (government ministry sites, large corporates) to need `stealth`/`dynamic`, matching the SG onboarding experience with IMDA/Scrapling.
- Some VN government/local sources may be Vietnamese-language-only with no English version, which the current keyword filter may consistently score low. Accepted as a known limitation this round (see Decisions above); worth revisiting if it turns out to exclude a large fraction of the government-agency sector.
- Whether MY/ID expansion (still fully unbuilt) should reuse this feature's country-scoping fixes as a template is a future question, not decided here.
