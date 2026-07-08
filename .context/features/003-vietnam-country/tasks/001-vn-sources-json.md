# Task 001: Add Vietnam (`VN`) country block to `config/sources.json`

**Status:** done

## Files

- `config/sources.json` (modify only — add one new element to the `countries` array)

## What to do

Add a new country object to the `countries` array in `config/sources.json`, immediately after
the existing Singapore object (which currently ends at line 766 with `}`, followed by line 767's
`]` closing the array). Insert `,` after the SG object's closing `}`, then the new VN object,
before the array's closing `]`. Do not touch anything inside the existing SG object.

The new object's shape:

```json
{
  "name": "Vietnam",
  "code": "VN",
  "active": true,
  "sources": [ ... see below ... ],
  "priority_keywords": [ ... see below ... ],
  "keywords": [ ... see below ... ]
}
```

### Source list (from `Silversea_Vietnam_Market_07072026.pdf`, transcribed below — this is the
authoritative data for this task; no other document needs to be consulted)

Every source object needs: `name`, `url`, `sector`, `type` (always `"website"`), `active`,
`domain` (array). Do **not** set `fetcher` on any of these — that field is added per-source by
Task 002 (scraper verification) only after a live dry-run; defaulting to the implicit `"default"`
fetcher (plain `requests`) here is correct and matches how new SG sources were originally onboarded.

**Sector mapping (per CONTEXT.md, user-confirmed — apply exactly, do not improvise a different
mapping):**
- `Government Authority` → `sector: "gov_agencies"`
- `Target Customer` / `Existing Customer` / `Potential Customer` / generic `Customer` → `sector: "customers"`
- `Competitor` / `Competitor / partner` (Siemens) → `sector: "competitors"`
- `Dealer / Supplier` → `sector: "partners"`
- `Facility Management` → `sector: "partners"`
- `News / Research` → `sector: "general_news"`

**Domain tagging:** default `"domain": ["GENERAL", "BER"]` for every source (matches SG's
default). Dual-tag `"domain": ["GENERAL", "BER", "EDU"]` for exactly these three, which have a
clear education angle (per CONTEXT.md's decision, following the NUS/NTU precedent from Feature
001): **Ministry of Education & Training (MOET)**, **Văn Lang University**, **HUIT**. No other
source gets the EDU tag.

Now the full list, grouped by category (map each to the sector above):

**Government Authority → `gov_agencies`:**
| name | url | notes (context only, not a field) |
|---|---|---|
| ITPC | https://itpc.hochiminhcity.gov.vn/home | IT Solution |
| Ministry of Construction (MOC) | https://moc.gov.vn | BIM policy, Smart Buildings, Digital Twin |
| Ministry of Industry & Trade (MOIT) | https://moit.gov.vn | Industry 4.0, Energy |
| Ministry of Science & Technology (MOST) | https://most.gov.vn | AI, Innovation |
| Ministry of Health (MOH) | https://moh.gov.vn | Smart Hospital |
| Ministry of Education & Training (MOET) | https://moet.gov.vn | Smart Campus — **dual-tag EDU** |
| National Innovation Center (NIC) | https://nic.gov.vn | Innovation funding |

**Target Customer → `customers`:**
| name | url | notes |
|---|---|---|
| Vingroup | https://vingroup.net | Smart City, Real Estate |
| Sun Group | https://sungroup.com.vn | New developments |
| VSIP | https://vsip.com.vn | Industrial Parks |
| VNPT | https://vnpt.com.vn | Smart City |
| Panasonic Vietnam | https://www.panasonic.com/vn | Smart Factory |
| Samsung Vietnam | https://www.samsung.com/vn | Manufacturing |

**Competitor / Competitor-partner → `competitors`:**
| name | url | notes |
|---|---|---|
| FPT Corporation | https://fpt.com | Enterprise DX |
| Viettel Group | https://viettel.com.vn/en/ | AI, IoT, Smart City |
| Becamex IDC | https://becamex.com.vn | Industrial Parks |
| Siemens | https://www.siemens.com | Building X, Digital Twin (listed as "Competitor/partner") |
| Schneider Electric | https://www.se.com/vn | EcoStruxure |
| Honeywell | https://www.honeywell.com | BMS |
| Johnson Controls | https://www.johnsoncontrols.com | OpenBlue |
| Autodesk | https://www.autodesk.com | Construction Cloud, Tandem |
| Bentley Systems | https://www.bentley.com | Infrastructure Digital Twin |
| Matterport | https://matterport.com | 3D Capture |

**Dealer / Supplier → `partners`:**
| name | url | notes |
|---|---|---|
| NVIDIA | https://www.nvidia.com | AI GPUs, Omniverse |
| Microsoft Azure | https://azure.microsoft.com | Cloud AI |
| Amazon Web Services | https://aws.amazon.com | Cloud |
| Dell Technologies | https://www.dell.com | Workstations |
| Cisco | https://www.cisco.com | Networking |

**Facility Management → `partners`:**
| name | url | notes |
|---|---|---|
| Savills Vietnam | https://www.savills.com.vn | FM contracts |
| CBRE Vietnam | https://www.cbrevietnam.com | FM contracts |

**News / Research → `general_news`:**
| name | url | notes |
|---|---|---|
| Vietnam Investment Review | https://vir.com.vn | Investment & FDI |
| VnExpress Business | https://vnexpress.net/kinh-doanh | Business news |
| Vietnam Briefing | https://www.vietnam-briefing.com | Regulations |
| World Bank Vietnam | https://www.worldbank.org/en/country/vietnam | Infrastructure reports |

**Existing / Potential / Generic Customer → `customers`:**
| name | url | notes |
|---|---|---|
| VIFA Liên Minh | https://vifafair.com/ | Virtual event |
| TTDecor | https://ttdecor.net/gioi-thieu-art | — |
| BambuUP | https://bambuup.com/ | — |
| GIZ | https://www.giz.de/en/vi/viet-nam | VR Training |
| Vietsoft Pro | https://vietsoftpro.com/ | VR headset Pico |
| ATZ | https://atz.com.vn/en | AR Solution, Digital Twin |
| Coca-Cola Vietnam | https://www.coca-cola.com/vn/vi | AR Solution |
| Biz Eyes | https://biz-eyes.com.vn/ | AR Solution |
| HUIT | https://huit.edu.vn/ | Virtual event — **dual-tag EDU** |
| MIK Group | https://www.mikgroup.vn/ | Virtual Showroom, Virtual event |
| BM Windows | https://bmwindows.vn/vi | Digital Twin |
| Arobid | https://arobid.com/vi | Virtual Showroom, Virtual event |
| QMS | https://qms.vn/bat-dong-san | Virtual Showroom |
| Sao Mai Group | https://saomaiedu.com/ | Vrealab |
| Văn Lang University | https://www.vlu.edu.vn/ | Digital Twin - virtual event — **dual-tag EDU** |
| CMC | https://www.cmc.com.vn/ | Digital Twin |
| Lạc Việt | https://lacviet.vn/ | VR training for Medical, Vrealab PC |
| Newtecons | https://newtecons.vn/ | Digital Twin |

**Entries with NO URL supplied in the source PDF** — 8 total: VNDC Technology Media, BPRO,
Digital World, CTO Group, Exporum, Steamzone, Delta, Đa Minh Education - Gia Đình Education.
**Explicit decision (planner's call, not to be re-litigated by the executor):** include all 8 as
source objects with `"url": ""`, `"active": false`, `"sector": "customers"`,
`"inactive_reason": "no URL supplied in source list — needs Alfonso to provide"`. This mirrors the
existing precedent of keeping known-but-currently-unusable sources in the config with an
`inactive_reason` (see SGTech/CPG Consultant/FacilityBot in the SG block) rather than silently
dropping them — they stay visible for a future admin/Alfonso pass to supply URLs. Do not attempt
to guess or web-search for URLs for these 8 — leave `"url": ""` exactly.

This gives 7 + 6 + 10 + 5 + 2 + 4 + 18 + 8 = **60 total source entries** (52 active, 8 inactive).
If your count differs, recount against the tables above before proceeding — do not silently drop
or duplicate an entry.

### Keyword lists

**`priority_keywords`** — copy of SG's `priority_keywords` (`config/sources.json` current lines
666-682) with `"GeBIZ"` removed (the only SG-specific term in that list per CONTEXT.md's decision):
```json
"priority_keywords": [
  "tender",
  "RFP",
  "ITQ",
  "ITT",
  "digital twin",
  "BIM",
  "smart FM",
  "smart building",
  "proptech",
  "building automation",
  "3D scanning",
  "point cloud",
  "facility management",
  "smart facility"
]
```

**`keywords`** — copy of SG's `keywords` (current lines 683-765) with exactly these 4 terms
removed: `"BCA Green Mark"`, `"Hiverlab"`, `"Gelement"`, `"TwinLogic"`, `"TwinMatrix"` (5 terms —
count carefully). Do not remove or add anything else — CONTEXT.md's decision names only these
plus GeBIZ (already excluded from priority_keywords above) as SG-specific; every other term
(including other SG entity names like "CapitaLand", "JTC", "Savills", policy terms like "IDD" and
"smart nation") stays, verbatim, per the literal scope of that decision. Do not add any new
Vietnam-specific terms (e.g. entity names from the source list above) — CONTEXT.md's rationale is
to empirically verify keyword-hit rate during Task 002's dry-run pass rather than guess upfront;
if Task 002 finds VN sources are failing the filter for lack of relevant keywords, that is Task
002's problem to solve, not this task's.
```json
"keywords": [
  "virtual tour",
  "3D scan",
  "3D visualization",
  "immersive",
  "XR",
  "extended reality",
  "virtual reality",
  "augmented reality",
  "metaverse",
  "spatial computing",
  "building management",
  "smart estate",
  "intelligent building",
  "IoT",
  "CMMS",
  "predictive maintenance",
  "construction technology",
  "contech",
  "greenfield",
  "smart construction",
  "IDD",
  "integrated digital delivery",
  "TOP inspection",
  "defect inspection",
  "virtual inspection",
  "sustainability",
  "green building",
  "net zero",
  "public sector",
  "smart nation",
  "government digital",
  "built environment",
  "M&E integration",
  "BMS",
  "building automation system",
  "asset management system",
  "Axomem",
  "DataMesh",
  "FacilityBot",
  "Cryotos",
  "Minuscule Technologies",
  "Alstern Technologies",
  "Aperio",
  "Nuvola Media",
  "SSI Corporate",
  "NeuronCloud",
  "CapitaLand",
  "Mapletree",
  "Lendlease",
  "JTC",
  "HDB estate",
  "MCC",
  "CSCEC",
  "CCCC",
  "CHEC",
  "Sembcorp",
  "SJ Group",
  "Meinhardt",
  "BECA",
  "Ramboll",
  "Azbil",
  "Johnson Controls",
  "Schneider",
  "Quantum Automation",
  "ST Synthesis",
  "Savills",
  "edtech",
  "e-learning",
  "LMS",
  "learning management system",
  "campus digital",
  "STEM lab",
  "virtual lab",
  "virtual campus",
  "online learning",
  "blended learning"
]
```
(81 SG terms minus the 5 named above = 76 terms. Verify your final array's length before saving.)

## Interfaces

None — pure JSON data edit. `config/sources.py`'s `_load()`/`COUNTRIES`/`load_sources()` are
unaffected in structure, only in the data they now return (one more country in the list).

## Constraints

- Do not touch the existing SG country object in any way.
- Do not touch `_domain_tagging_status` (last line of the file) — out of scope.
- Must remain valid JSON — verify with a JSON parser after editing, not just visual inspection.
- Do not set a `"country"` field on individual source objects — country is determined entirely by
  which country object a source lives under (existing repo-wide convention, see DECISIONS.md's
  2026-07-02 entry).
- Do not add a `fetcher` field to any new source in this task — that's Task 002's job, after a
  live dry-run per source.

## Verification

No LLM call needed:

1. `py -c "import json; json.load(open('config/sources.json', encoding='utf-8'))"` — must succeed,
   confirming valid JSON.
2. `py -c "from config.sources import load_sources; c=[x for x in load_sources() if x['code']=='VN'][0]; print(len(c['sources']), len(c['priority_keywords']), len(c['keywords']))"`
   — must print the VN source count (60, per the count above — recount if your total differs) and
   the two keyword-list lengths (14 and 76 respectively, or your recounted values if they differ
   from this task's arithmetic).
3. `py -c "from config.sources import load_sources; c=[x for x in load_sources() if x['code']=='VN'][0]; print([s['domain'] for s in c['sources'] if s['name'] in ('Ministry of Education & Training (MOET)', 'Văn Lang University', 'HUIT')])"`
   — must print three `['GENERAL', 'BER', 'EDU']` lists.
4. `py -c "from config.sources import load_sources; c=[x for x in load_sources() if x['code']=='VN'][0]; print([s['name'] for s in c['sources'] if not s['active']])"`
   — must print exactly the 8 no-URL entries and nothing else.
5. `py -c "from config.sources import COUNTRIES; print([c['code'] for c in COUNTRIES])"` — must
   print `['SG', 'VN']`, confirming the SG entry is untouched and VN was appended correctly.
6. `py -c "import json; d=json.load(open('config/sources.json',encoding='utf-8')); print('GeBIZ' not in d['countries'][1]['priority_keywords'], 'BCA Green Mark' not in d['countries'][1]['keywords'], 'Hiverlab' not in d['countries'][1]['keywords'])"`
   — must print `True True True`.

## Model tier

mid — large, mostly-mechanical transcription task, but requires correct judgment on the
missing-URL entries, the dual-tag exceptions, and the keyword-list diffing (removing exactly the
named terms, not more or fewer).

## Depends on

None.

## Evidence

Executor report (DONE):
1. JSON valid — parses cleanly.
2. `60 14 76` — matches expected source/priority_keywords/keywords counts exactly.
3. Dual-tag check (MOET, Văn Lang University, HUIT) → three `['GENERAL', 'BER', 'EDU']` lists.
4. Inactive-list check → exactly the 8 no-URL entries.
5. `COUNTRIES` codes → `['SG', 'VN']`.
6. SG-specific-term exclusion check → `True True True`.
7. `git diff --stat` → 772 insertions, 0 deletions — SG block and `_domain_tagging_status` untouched.

Note: hit a Windows console `cp1252` UnicodeEncodeError printing Vietnamese diacritics in one verification command; resolved with `PYTHONIOENCODING=utf-8`, no data issue.

Files changed: `config/sources.json` only.
