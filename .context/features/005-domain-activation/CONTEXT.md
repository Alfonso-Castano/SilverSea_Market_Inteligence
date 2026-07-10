# Feature: Full Business-Domain Activation (RCC/HLS/MFG/CTE/PSS)

**Base:** b1549d65ef033eba357bd0d51c8a78474c4a564b (`integration/vn-my-review`, the merged Vietnam+Malaysia branch — see Branching decision below for why this feature builds here rather than off `main`)

## Goal

Activate the remaining 5 business domains (Retail/Commerce/Consumer Goods, Healthcare & Life Sciences, Manufacturing & Industry 4.0, Culture/Tourism & Events, Public Sector & Smart Cities) as first-class, routable, analyzed pipeline domains alongside the currently-active BER/EDU/GENERAL — and retroactively re-tag Vietnam's sources with their real business domains (mirroring Malaysia's existing pattern), so the full breadth of both countries' submitted source lists becomes genuinely visible and analyzed, not just stored.

## Scope

**In scope:**
- `app.py`'s `_domain_mode()` — expand the validated domain set from `("EDU", "BER", "GENERAL")` to include `RCC`, `HLS`, `MFG`, `CTE`, `PSS` (8 total).
- `templates/base.html` — expand the domain-tabs row from 3 to 8 tabs. Add `flex-wrap` to the tabs container so it wraps to additional rows on narrow viewports rather than overflowing.
- `templates/admin.html` — expand the domain checkboxes in the source-approval form from 3 to 8, matching the same domain set.
- `pipeline/analyst.py`'s `SUMMARY_PROMPT` — add the RCC/HLS/MFG/CTE/PSS product catalogs (transcribed verbatim from `data/company_context.md`'s existing "Products by Business Sector" section — this content already exists, written during Feature 001, currently marked "reference only, not active this round") to the "Silversea products" list, alongside the existing BER/EDU entries. Broaden the `OPPORTUNITIES:` gate keyword list with cross-sector terms.
- `data/company_context.md` — remove the "— reference only, not active this round" caveat suffix from the 5 now-active sector headings (`### Manufacturing & Industry 4.0 (MFG)`, `### Healthcare & Life Sciences (HLS)`, `### Retail, Commerce & Consumer Goods (RCC)`, `### Culture, Tourism & Events (CTE)`, `### Public Sector & Smart Cities (PSS)`). No other change to that section — the product lists themselves stay as-is.
- `config/sources.json`'s Vietnam block — retag all 52 VN sources that have real descriptions (from the original source PDF, already used once for Task 001's sector mapping in Feature 003) with their real business domain, dual-tagged alongside `GENERAL` exactly like Malaysia's pattern. See the full retag table below — this is the authoritative, complete source of truth for this task, no re-derivation needed.
- Branching: this feature builds directly on `integration/vn-my-review` (not `main`), because VN's `sources.json` — which this feature must modify — only exists there, merged with Malaysia's. This is a deliberate change from an earlier "branch off main" plan; the VN-retagging scope decision (below) is what forced it. Consequence: `integration/vn-my-review` is no longer just a throwaway review scaffold — it's now the real path toward eventually merging Vietnam + Malaysia + this feature into `main` together.

**Explicitly out of scope:**
- Malaysia's `sources.json` — already correctly domain-tagged from Feature 004, zero changes needed.
- Singapore's `sources.json` — no non-BER sources exist to retag. SG will show empty results under the 5 new domain tabs until/unless real SG sources are added for those verticals in the future. This is an expected consequence, not a bug to fix here.
- Indonesia — still no data, still out of scope.
- A fresh live pipeline run (VN and/or MY) to confirm opportunities now actually surface for non-BER/EDU signals under the broadened gate — Alfonso-owned, Groq-quota-gated manual checkpoint, same treatment as every prior country pipeline run this project.
- Accuracy/value review of already-generated report content (Vietnam's and Malaysia's live reports) — Alfonso explicitly flagged this as needed, and explicitly acknowledged it's hard since "value" is subjective. Not attempted in this feature; logged under Open Questions so it survives into `.context/STATE.md` via this feature's own `/feature-verify` context refresh.
- Any change to the multi-pass analysis architecture (extract→synthesize→summary), the opportunity scoring rubric/clamp, or the RAG mechanism.

## Implementation Decisions

- **Vietnam retagging is in scope this round.** *(User decision — reverses Claude's own initial recommendation to defer it.)* Rationale given: Alfonso wants the full source lists genuinely usable now, and accepted the extra scope even though it's closer to research than the mechanical Malaysia case, since Malaysia's source list came with an explicit business-domain column and Vietnam's did not.
- **Vietnam retagging method: reuse the original VN source list's own descriptions only — no new research, no re-reading external sources.** *(Claude's default judgment, directly implementing the user's stated preference to trim rather than research.)* Every domain assignment below is derived from the same source notes already used once for Feature 003's Task 001 sector mapping. The 7 fully-blank no-URL/no-description stub sources (no notes ever existed for these — `VNDC Technology Media`, `BPRO`, `Digital World`, `CTO Group`, `Exporum`, `Steamzone`, `Delta`) keep their default `["GENERAL", "BER"]` tag rather than receiving an invented domain. The 8th no-URL stub, `Đa Minh Education - Gia Đình Education`, gets a name-based `EDU` dual-tag as the one justifiable low-confidence exception (the word "Education" appears twice in its own name — a much lower inference bar than fabricating a domain from nothing).
- **The full VN retag table** (name → new real domain, dual-tagged alongside `GENERAL`; sources not listed here keep their current tag unchanged):

| Source | New real domain |
|---|---|
| ITPC | PSS |
| Ministry of Construction (MOC) | BER *(unchanged — stays BER)* |
| Ministry of Industry & Trade (MOIT) | MFG |
| Ministry of Science & Technology (MOST) | PSS |
| Ministry of Health (MOH) | HLS |
| Ministry of Education & Training (MOET) | EDU *(unchanged — already dual-tagged EDU)* |
| National Innovation Center (NIC) | PSS |
| Vingroup | BER *(unchanged)* |
| Sun Group | BER *(unchanged)* |
| VSIP | BER *(unchanged — industrial park development, treated like a property developer per Malaysia's precedent, not MFG)* |
| VNPT | PSS |
| Panasonic Vietnam | MFG |
| Samsung Vietnam | MFG |
| FPT Corporation | PSS |
| Viettel Group | PSS |
| Becamex IDC | BER *(unchanged — industrial park development)* |
| Siemens | BER *(unchanged)* |
| Schneider Electric | BER *(unchanged)* |
| Honeywell | BER *(unchanged)* |
| Johnson Controls | BER *(unchanged)* |
| Autodesk | BER *(unchanged)* |
| Bentley Systems | BER *(unchanged)* |
| Matterport | BER *(unchanged)* |
| NVIDIA | PSS |
| Microsoft Azure | PSS |
| Amazon Web Services | PSS |
| Dell Technologies | PSS |
| Cisco | PSS |
| Savills Vietnam | BER *(unchanged)* |
| CBRE Vietnam | BER *(unchanged)* |
| Vietnam Investment Review | PSS |
| VnExpress Business | PSS |
| Vietnam Briefing | PSS |
| World Bank Vietnam | BER *(explicit "Infrastructure reports" note)* |
| VIFA Liên Minh | CTE *(furniture/trade fair, "Virtual event" note)* |
| TTDecor | RCC *(decor/furniture retail)* |
| BambuUP | PSS *(Vietnamese innovation/startup ecosystem platform, broad tech)* |
| GIZ | EDU *("VR Training" note)* |
| Vietsoft Pro | PSS *(hardware/tech vendor, no vertical signal)* |
| ATZ | BER *("Digital Twin" note)* |
| Coca-Cola Vietnam | RCC *(consumer goods)* |
| Biz Eyes | RCC |
| HUIT | EDU *(unchanged — already dual-tagged EDU)* |
| MIK Group | BER *(Vietnamese real estate developer)* |
| BM Windows | BER *(construction materials/windows manufacturer, treated as construction-adjacent)* |
| Arobid | RCC *(showroom/marketplace platform)* |
| QMS | BER *(real estate — "bat-dong-san" in its URL means "real estate")* |
| Sao Mai Group | EDU *(Vrealab education-tech platform)* |
| Văn Lang University | EDU *(unchanged — already dual-tagged EDU)* |
| CMC | PSS *(broad IT conglomerate, no single vertical)* |
| Lạc Việt | HLS *("VR training for Medical" note)* |
| Newtecons | BER *(Vietnamese construction contractor)* |
| Đa Minh Education - Gia Đình Education | EDU *(name-based inference, the one exception among the 8 no-URL stubs — see rationale above)* |
| *(7 remaining no-URL stubs: VNDC Technology Media, BPRO, Digital World, CTO Group, Exporum, Steamzone, Delta)* | *No change — stay `["GENERAL", "BER"]` default, no basis to assign anything else* |

- **Domain tab UI**: add `flex-wrap` to the domain-tabs container rather than redesigning into a dropdown. *(Claude's default judgment.)* Minimal change, matches the existing Tailwind utility-class pattern already used throughout `base.html`; a dropdown would be a bigger, unrequested redesign.
- **Opportunities-gate keyword source**: reuse the cross-sector vocabulary already established in Malaysia's `keywords` list (Task 001 of Feature 004 — retail/showroom, healthcare/hospital, manufacturing/factory, tourism/heritage, government/smart-city terms) rather than inventing new terms. *(Claude's default judgment.)* Keeps the vocabulary consistent across the codebase instead of introducing a second, slightly-different cross-sector term list.
- **Product catalog source**: transcribe verbatim from `company_context.md`'s existing "Products by Business Sector" RCC/HLS/MFG/CTE/PSS entries — no new product-name invention. The executor must read that section directly rather than trust a paraphrase.

## Global Constraints

- No new Python dependencies.
- Match existing Tailwind/Jinja2 patterns for all UI changes — same pill-tab styling already used for BER/EDU/GENERAL, same checkbox styling in `admin.html`.
- Preserve `main.py --domain=BER|EDU|GENERAL` and all existing SG/VN/MY country filtering behaving exactly as today — this feature is additive (more domain values become valid), not a rework of existing filtering logic.
- `pipeline/analyst.py`'s `SUMMARY_PROMPT` edits must use the same `str.replace()`-safe pattern already established (Feature 003's Task 006) — never `.format()` on the full prompt string, since it contains a literal JSON schema block with curly braces later in the same string.
- `config/sources.json` edits: manual Edit-tool edits are fine for this one-time retagging pass (matching the established precedent for planned data changes, not runtime writes) — do not touch anything about VN sources other than the `domain` array (name, url, sector, type, active, fetcher, inactive_reason all stay exactly as they are).
- Do not touch `pipeline/feedback.py`, `pipeline/weekly.py`, `main.py`, or the multi-pass extract→synthesize→summary architecture.

## Open Questions

- **Accuracy and value review of Vietnam's and Malaysia's already-generated live reports is explicitly needed, per Alfonso, but not attempted here.** Alfonso's own framing: accuracy is checkable, but "value" (how useful a piece of information is to the company for a specific country) is inherently subjective and will be genuinely hard to automate or score cleanly. Not yet scoped as a feature — flag this prominently in `.context/STATE.md`'s Known Bugs/Next Action via this feature's own context refresh, so it isn't lost the way the domain-activation item almost was.
- Whether a live pipeline re-run (VN and/or MY) after this feature ships is needed to confirm the broadened opportunities gate actually surfaces non-BER/EDU opportunities — Alfonso-owned, Groq-quota-gated, deferred.
- SG's own domain coverage for RCC/HLS/MFG/CTE/PSS is a fully separate, unstarted question — no real SG sources exist for these verticals yet.
- `pipeline/weekly.py`'s `WEEKLY_PROMPT` still hardcodes "Singapore" — carried forward from Feature 003, still not addressed, still a small, well-understood follow-up.
