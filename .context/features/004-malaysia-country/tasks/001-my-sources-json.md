# Task 001: Add Malaysia (MY) country block to `config/sources.json`

**Status:** done

## Files

- `config/sources.json` (modify only — append one new object to the `countries` array; no other
  edits)

## What to do

`config/sources.json`'s `countries` array currently has exactly one entry (`"SG"`, 62 sources).
This task appends a second entry, `"MY"` (Malaysia), with 55 real sources transcribed from the
Malaysia branch's source submission (`Source_submission_Malaysia.xlsx`, via Suex Ching — the raw
list and every source's business domain/description was already given to the planning session and
is fully reflected in the JSON below; you do not need to re-derive any mapping).

**Insert the following object into the `countries` array, immediately after the SG object's
closing `}` and before the `],` that closes the `countries` array** (i.e. add a comma after SG's
closing `}`, then this object, keeping `_domain_tagging_status` as the last top-level key
untouched):

```json
    {
      "name": "Malaysia",
      "code": "MY",
      "active": true,
      "sources": [
        {
          "name": "MDEC",
          "url": "https://www.mdec.my/",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Air Selangor",
          "url": "https://www.airselangor.com/?lang=en",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Jabatan Pengangkutan Jalan (JPJ)",
          "url": "https://www.jpj.gov.my/",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Think City",
          "url": "https://thinkcity.com.my/",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Sabah Economic Development and Investment Authority (SEDIA)",
          "url": "https://sedia.com.my/",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "National Art Gallery",
          "url": "https://www.artgallery.gov.my/",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "CTE"
          ]
        },
        {
          "name": "PR1MA Corporation Berhad",
          "url": "https://www.pr1ma.my/",
          "sector": "gov_agencies",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "GreenRE",
          "url": "https://www.greenre.org/#",
          "sector": "associations",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "REDHA Institute",
          "url": "https://rehdainstitute.com/#",
          "sector": "associations",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Malaysia Retail Chain Association (MRCA)",
          "url": "https://www.mrca.org.my/",
          "sector": "associations",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "PKNS FM Integrated Sdn Bhd",
          "url": "https://pknsfmi.com/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "TOGL Technology Sdn Bhd",
          "url": "https://www.togltechnology.com/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "Avisena Women's & Children Specialist Hospital",
          "url": "https://ash2.avisena.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "HLS"
          ]
        },
        {
          "name": "BDB Land Sdn Bhd",
          "url": "https://bdb.com.my/property/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Capri by Fraser",
          "url": "https://www.frasershospitality.com/en/malaysia/kualalumpur/capri-by-fraser-bukit-bintang/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "Ricoh (Malaysia) Sdn Bhd",
          "url": "https://www.ricoh.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "Panasonic Appliances Marketing Asia Pacific",
          "url": "https://www.panasonic.com/my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "City Motor Group",
          "url": "https://citymotorsgroup.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "NCT Borneo Sdn Bhd",
          "url": "https://nct.net.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Perodua",
          "url": "https://www.perodua.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "MFG"
          ]
        },
        {
          "name": "Daikin Malaysia",
          "url": "https://www.daikin.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "MFG"
          ]
        },
        {
          "name": "U Mobile",
          "url": "https://www.u.com.my/en/personal/home",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "YTL Info Screen",
          "url": "https://www.infoscreen.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "IHH Healthcare",
          "url": "https://www.ihhhealthcare.com/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "HLS"
          ]
        },
        {
          "name": "UCSI Hospital",
          "url": "https://www.ucsiuniversity.edu.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "HLS"
          ]
        },
        {
          "name": "UOA Development Berhad",
          "url": "https://uoa.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Sunway Group",
          "url": "https://www.sunway.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "CTE"
          ]
        },
        {
          "name": "Sunway Medical Centre",
          "url": "https://www.sunwaymedical.com/en/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "HLS"
          ]
        },
        {
          "name": "Sunway Property",
          "url": "https://sunwayproperty.com/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "TA Global",
          "url": "https://taglobal.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Sunsuria Berhad",
          "url": "https://www.sunsuria.com/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Skyworld Development Berhad",
          "url": "https://skyworldgroup.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Bandar Utama City Center Sdn Bhd",
          "url": "https://www.1utama.com.my/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "Sharp",
          "url": "https://my.sharp/",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "Malaysia Airlines",
          "url": "https://www.malaysiaairlines.com/my/en/home.html",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Malaysia Airport Holding Berhad",
          "url": "https://corporate.malaysiaairports.com.my/en",
          "sector": "customers",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Inkube Edu Sdn Bhd",
          "url": "https://bestaritsb.com/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "EDU"
          ]
        },
        {
          "name": "TRB Ventures Sdn Bhd (Mhub)",
          "url": "https://www.mhub.my/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Ezytap Sdn Bhd",
          "url": "https://ezytap.my/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "CTE"
          ]
        },
        {
          "name": "ITMAX System Berhad",
          "url": "https://itmax.com.my/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "SAINS",
          "url": "https://www.sains.com.my/web/home/index",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "U Learning",
          "url": "https://www.ulearning.asia/ulearning/index.html#/i18n",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "EDU"
          ]
        },
        {
          "name": "Huawei Cloud",
          "url": "https://www.huaweicloud.com/intl/en-us/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "CelcomDigi",
          "url": "https://www.celcomdigi.com/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Redtone",
          "url": "https://www.redtone.com/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Art Network Events",
          "url": "https://artnetwork.com.my/",
          "sector": "partners",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Esri Malaysia",
          "url": "https://esrimalaysia.com.my/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Serve Deck Innovation Sdn Bhd",
          "url": "https://www.servedeck.com/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "BER"
          ]
        },
        {
          "name": "Accenture",
          "url": "https://www.accenture.com/my-en",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        },
        {
          "name": "Virtualtech Frontier",
          "url": "https://www.virtualtechfrontier.com/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "EDT",
          "url": "https://www.weareedt.com/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "THEXRA",
          "url": "https://thexra.com/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "3 Particles",
          "url": "https://www.3particle.com/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "RCC"
          ]
        },
        {
          "name": "Unbound Malaysia",
          "url": "https://www.unboundmalaysia.com/",
          "sector": "competitors",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "EDU"
          ]
        },
        {
          "name": "Dreamory",
          "url": "https://dreamorygroup.com/",
          "sector": "general_news",
          "type": "website",
          "active": true,
          "domain": [
            "GENERAL",
            "PSS"
          ]
        }
      ],
      "priority_keywords": [
        "tender",
        "RFP",
        "ITQ",
        "ITT",
        "GeBIZ",
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
      ],
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
        "BCA Green Mark",
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
        "Hiverlab",
        "Gelement",
        "TwinLogic",
        "TwinMatrix",
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
        "blended learning",
        "virtual showroom",
        "shopping mall",
        "retail chain",
        "hospitality",
        "hospital",
        "healthcare",
        "safety courseware",
        "medical centre",
        "factory",
        "manufacturing",
        "industrial",
        "heritage trail",
        "tourism",
        "immersive experience centre",
        "smart city",
        "government grant",
        "driving simulation",
        "water utilities"
      ]
    }
```

Notes on where the content above came from (context only, not something to re-derive):

- **`priority_keywords` and `keywords` (through `"blended learning"`) are copied verbatim from
  SG's existing lists** — per CONTEXT.md's explicit decision, MY reuses SG's full lists as-is
  (including `GeBIZ` and the SG-specific competitor names like Hiverlab/Gelement/TwinLogic/
  TwinMatrix), unlike Vietnam's list which stripped those SG-specific terms. Do not strip anything
  from this base — that stripping decision was VN-specific and does not apply here.
- **The 18 terms appended after `"blended learning"`** (`virtual showroom` through
  `water utilities`) are new MY cross-sector additions, added to the 1x-weight `keywords` list
  only (never `priority_keywords`), covering the non-BER majority of MY's source list: retail/
  showroom terms for RCC, healthcare/hospital/safety-training terms for HLS, factory/manufacturing
  terms for MFG, tourism/heritage/event terms for CTE, and government/smart-city/grant terms for
  PSS. Each was drawn directly from the MY source descriptions (e.g. "virtual showroom" from
  Ricoh/Panasonic/Sharp, "shopping mall" from U Mobile/Bandar Utama, "hospital"/"healthcare" from
  Avisena/IHH Healthcare/Sunway Medical Centre, "safety courseware" from Avisena's VR safety
  courseware, "heritage trail"/"tourism" from Ezytap's Sabah Tourism Metaverse and Sandakan
  Heritage Trail work, "smart city" from Think City, "government grant" from MDEC).
- **Sector mapping** (`Customer→customers`, `Partner→partners`, `Government→gov_agencies`,
  `Association→associations`, `Competitor→competitors`, `General News→general_news`) and each
  source's real business `domain` tag (`BER`/`RCC`/`HLS`/`MFG`/`CTE`/`PSS`/`EDU`, always paired
  with `"GENERAL"`) come directly from the source submission and are already correctly applied in
  the JSON above — final counts: `gov_agencies` 7, `associations` 3, `customers` 26, `partners` 10,
  `competitors` 8, `general_news` 1 (55 total); domain breakdown BER 17, RCC 13, PSS 13, HLS 4,
  CTE 3, EDU 3, MFG 2.
- All 55 sources default to `"active": true` with no `"fetcher"` field (implicit default/plain-
  `requests` fetcher) — Task 002 dry-run-tests each one and flips `active`/adds `fetcher` as
  needed. Do not hand-guess fetcher tiers or activity status in this task, even where a source's
  business description mentions it being an "inactive" *partner relationship* (e.g. Redtone,
  described as "Inactive existing partner" in the business sense) — that is unrelated to whether
  its website is scrapeable, which Task 002 determines empirically.

## Interfaces

- Produces: the `"MY"` entry in `config.sources.load_sources()` / `config.sources.COUNTRIES`,
  consumed by `main.py --country=MY` (already-generic filtering, confirmed unchanged) and by
  Task 002 (scraper verification, same file) and Task 003 (`templates/base.html`'s new MY tab
  link, different file, no data dependency).

## Constraints

- Only append the new `"MY"` object to the `countries` array. Do not modify the existing `"SG"`
  object, and do not touch the trailing `_domain_tagging_status` key (keep it as the last
  top-level key, unchanged in value).
- Do not add a per-source `"country"` field — country is determined by nesting in the `countries`
  array, per the existing repo-wide convention (see CONTEXT.md's Global Constraints).
- Must remain valid JSON — verify with a JSON parser after editing, not just visual inspection.
- Direct manual edit via the Edit tool is fine, same as Feature 001's Task 005 precedent for this
  same file — no need to script through `config.sources.save_sources()` for this one-time data
  load (that function exists for the *runtime* admin-approval write path, not for this kind of
  planned data addition).

## Verification

No LLM call needed — pure JSON/config verification:

1. `py -c "import json; json.load(open('config/sources.json', encoding='utf-8'))"` — must succeed
   with no exception, confirming the file is still valid JSON.
2. `py -c "from config.sources import load_sources; cs=load_sources(); print([c['code'] for c in cs])"`
   — must print `['SG', 'MY']`.
3. `py -c "from config.sources import load_sources; my=[c for c in load_sources() if c['code']=='MY'][0]; print(len(my['sources']), len(my['priority_keywords']), len(my['keywords']))"`
   — must print `55 15 99`.
4. `py -c "from config.sources import load_sources; from collections import Counter; my=[c for c in load_sources() if c['code']=='MY'][0]; print(Counter(s['sector'] for s in my['sources']))"`
   — must print counts matching `gov_agencies: 7, associations: 3, customers: 26, partners: 10,
   competitors: 8, general_news: 1`.
5. `py -c "from config.sources import load_sources; my=[c for c in load_sources() if c['code']=='MY'][0]; assert all('GENERAL' in s['domain'] for s in my['sources']); print('OK')"`
   — must print `OK`, confirming every MY source is tagged `GENERAL` (and therefore reachable via
   `--domain=GENERAL` even before RCC/HLS/MFG/CTE/PSS become first-class active domains).
6. Confirm the SG block is untouched: `py -c "from config.sources import load_sources; sg=[c for c in load_sources() if c['code']=='SG'][0]; print(len(sg['sources']))"` — must still print `62`.

## Model tier

cheap — every source's sector/domain mapping and every keyword addition is fully specified above;
the executor's job is precise JSON transcription plus running the verification commands, no
judgment calls required.

## Depends on

None.

## Evidence

Executor report (DONE):
1. JSON valid.
2. `['SG', 'MY']`.
3. `55 15 99` — matches exactly.
4. `Counter({'customers': 26, 'partners': 10, 'competitors': 8, 'gov_agencies': 7, 'associations': 3, 'general_news': 1})` — exact match.
5. All MY sources tagged `GENERAL` — `OK`.
6. SG unchanged — still `62` sources.
7. `git diff --stat` — 730 pure insertions, 0 deletions.

Files changed: `config/sources.json` only.
