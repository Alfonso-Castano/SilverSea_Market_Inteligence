# Task 004: Add a Malaysia subsection to `data/company_context.md` + re-seed the vectorstore

**Status:** done

## Files

- `data/company_context.md` (modify — additions only, inside two existing sections)
- No other file changes. This task also *runs* (does not modify) `scripts/seed_vectorstore.py`.

## What to do

**Background:** `pipeline/analyst.py`'s RAG retrieval against the `COMPANY_CONTEXT` ChromaDB
collection is not country-filtered by design (correct for the product catalog, which is
country-agnostic) — this means the "Key Prospects & Relationships" and "Ecosystem Players"
sections need their own Malaysia content, or every MY report run risks pulling in irrelevant
Singapore prospect framing. The "Products by Business Sector," "Target Sectors & Use Cases,"
"Competitive Positioning," "BD Priorities," and "Regulatory & Certification Note" sections are
already country-agnostic and must NOT be touched by this task.

Unlike Vietnam's subsection (which stayed BER/EDU-flavored, matching VN's own domain-scope
decision), **Malaysia's subsection must cover the full real business breadth of the MY source
list** (BER, RCC, HLS, MFG, CTE, PSS, EDU) — per CONTEXT.md's forward-compatibility decision, the
same reasoning as tagging every MY source with its real (non-BER) domain in `config/sources.json`.
Use the RCC/HLS/MFG/CTE/PSS product names already in this file's "Products by Business Sector"
section (written during Feature 001, currently marked "reference only, not active this round") —
do not invent new product names.

**1. Add a Malaysia subsection to "Key Prospects & Relationships"** (current section spans lines
91-105, ending right before "## Ecosystem Players" at line 107). Insert a new `###` subheading and
content immediately after the existing SG content (after the "Government agencies tracked..."
paragraph, before the `## Ecosystem Players` heading):

```markdown
### Malaysia

**Sunway Group** — Major Malaysian conglomerate spanning property, retail, hospitality, and
healthcare. Prospective buyer of Digital Twin and Smart Facility Management System across its
property portfolio, AR way-finding for its Umrah/Hajj travel operations (Culture, Tourism &
Events), and AR way-finding for Sunway Medical Centre (Healthcare & Life Sciences).

**PKNS FM Integrated Sdn Bhd** — Existing client for the metaverse-integrated operation centre and
smart facilities platform (Smart Facility Management System).

**TOGL Technology Sdn Bhd** — Existing client for a metaverse solution built for their annual
gathering event (Metaverse Platform), delivered across two versions.

**Property developers (4D Virtual Tour rendering prospects):** BDB Land, UOA Development Berhad,
TA Global, Sunsuria Berhad, Skyworld Development Berhad, and Sunway Property — all prospective
buyers of 3D/VR Virtual Tour rendering services for property marketing; UOA additionally a
prospect for AR way-finding at its Bangsar South car park.

**Healthcare prospects:** Avisena Women's & Children Specialist Hospital (existing client, VR
safety courseware rental, potential Deepmoo scanning upsell for a new hospital launch), IHH
Healthcare and UCSI Hospital (AR way-finding prospects), and Sunway Medical Centre (AR
way-finding) — all Healthcare & Life Sciences prospects (Smart Facility Management System,
Customized AR/VR Content).

**Manufacturing prospects:** Perodua and Daikin Malaysia — automotive and appliance manufacturers,
prospective buyers of Smart Facility Management System and IoT & AI Solutions for smart-factory
initiatives, with Perodua also a prospect for immersive roadshow content and Digital Twin.

**Retail/hospitality prospects:** Ricoh (Malaysia), Panasonic Appliances Marketing Asia Pacific,
and Sharp — prospective buyers of Virtual Showroom and AI-enabled Digital Twin with Smart Facility
Management System; Capri by Fraser (existing client, 4D Virtual Tour scanning) and City Motor
Group (existing client, virtual showroom/facilities landing page embed) round out the Retail,
Commerce & Consumer Goods relationship base.

**Telecom/media prospects:** U Mobile — Digital Twin aligned with its Ultra 5G rollout, plus AR
way-finding for a BERJAYA-group shopping mall; YTL Info Screen — AR solution for marketing
campaigns.

**Aviation prospects:** Malaysia Airlines (VR training courseware for cabin crew) and Malaysia
Airport Holding Berhad (AR way-finding and Digital Twin) — both Public Sector & Smart Cities
prospects.

**Education-adjacent partners:** Inkube Edu Sdn Bhd (existing partner, Vrealab solution to
government schools and metaverse solution to a government university) and U Learning (potential
partner, Vrealab solutions) — same education-technology-adjacent profile as NUS/NTU in Singapore.

**Government agencies tracked for tender and policy signals:** MDEC (Malaysia Digital Economy
Corporation — grants, tech-industry business opportunities), Air Selangor (water utilities, tender
pipeline), JPJ (Jabatan Pengangkutan Jalan — Road Transport Department, VR safety driving
simulation potential), Think City (Kuala Lumpur Council-appointed agency, Digital Twin/Smart
Facility Management System for KL city area), SEDIA (Sabah Economic Development and Investment
Authority — metaverse career and VR training prospects), National Art Gallery (immersive
experience centre prospect), and PR1MA Corporation Berhad (4D Virtual Tour prospect).
```

**2. Add a Malaysia subsection to "Ecosystem Players"** (current section spans lines 107-136).
Insert a new subsection at the end of that section, after the existing "Facility management firms"
subsection (before `## BD Priorities` at line 138):

```markdown
**Malaysia — main partners and channel prospects** — Potential collaboration/JV or channel
partners, not direct BD targets:
- Ezytap Sdn Bhd — Existing partner delivering the Sabah Tourism Metaverse to KePKAS; potential
  collaboration on AR gamification for the Sandakan Heritage Trail (Culture, Tourism & Events)
- ITMAX System Berhad — Potential partner for AI-enabled Digital Twin with Smart Facility
  Management System; NDA pending
- SAINS — Potential partner for AI-enabled Digital Twin with Smart Facility Management System
- TRB Ventures Sdn Bhd (Mhub) — Existing partner for 4D Virtual Tour rendering; potential upsell to
  a digital-twin property booking platform
- Huawei Cloud — Potential technology/referral partner across multiple solution lines
- CelcomDigi — Potential partner for AI-enabled Digital Twin and Vrealab solutions; NDA pending
- Redtone — Dormant existing partner (4D Virtual Tour rendering and scanning); relationship needs
  re-establishing with the right point of contact
- Art Network Events — Potential partner for creative-tech event content (AR launch gimmicks, AR
  gamification)

**Malaysia — government/association ecosystem:**
- GreenRE — Potential collaborator on AI-enabled Digital Twin with Smart Facility Management
  System (green-building certification body)
- REDHA Institute — Potential association membership for developer-industry connections
- Malaysia Retail Chain Association (MRCA) — Potential association membership for retail-industry
  connections

**Malaysia — competitors to watch:**
- Esri Malaysia — GIS technology including digital twin solutions
- Serve Deck Innovation Sdn Bhd — Smart facilities management platform
- Accenture — Metaverse and AI solutions; also a potential partnership-collaboration angle
- Virtualtech Frontier, EDT, THEXRA, 3 Particles — Metaverse/VR/AR/immersive and creative-tech
  content solution providers
- Unbound Malaysia — AI, AR, and education-related solutions
```

Do not add a Malaysia competitor list to the existing "Competitive Positioning" section — CONTEXT.md's
scope for this task is explicitly limited to "Key Prospects & Relationships" and "Ecosystem
Players" only (the "Malaysia — competitors to watch" list above goes inside "Ecosystem Players",
mirroring where Vietnam's technology-dealer and FM-firm ecosystem lists live, not into the
country-agnostic "Competitive Positioning" section).

**3. Re-seed the `COMPANY_CONTEXT` ChromaDB collection.** ChromaDB does not re-read
`company_context.md` on its own — any content change requires re-running the existing seeding
script, unchanged:
```
py scripts/seed_vectorstore.py
```
This deletes and rebuilds the `COMPANY_CONTEXT` collection (see `scripts/seed_vectorstore.py`'s
`seed()` function). It uses ChromaDB's local embedding function only — **no Groq/LLM API call is
made**, so it does not touch the Groq daily quota.

## Interfaces

None — pure Markdown content addition plus running an existing, unmodified script. No code
interfaces change.

## Constraints

- Do not touch "Products by Business Sector," "Target Sectors & Use Cases," "Competitive
  Positioning," "BD Priorities," or "Regulatory & Certification Note" — all explicitly
  country-agnostic and out of scope per CONTEXT.md.
- Do not modify `scripts/seed_vectorstore.py` itself — run it as-is.
- Ground every entity mentioned in the new subsections in the MY source list (already transcribed
  into `config/sources.json` by Task 001) — do not invent prospects, product pairings, or facts
  not present there. The product names used (Digital Twin, Smart Facility Management System,
  3D/VR Virtual Tour, Metaverse Platform, Customized AR/VR Content, IoT & AI Solutions, Virtual
  Showroom) must come from the existing "Products by Business Sector" catalog already in this
  file (including its RCC/HLS/MFG/CTE/PSS rows, currently marked "reference only") — do not invent
  new product names.
- Keep the same prose style/format as the existing SG/VN entries (bold entity name, em-dash,
  one-to-two sentence description referencing a specific Silversea product) — this is additive
  content matching an established pattern, not a redesign.

## Verification

No LLM call needed for the Markdown edit; the re-seed step makes no LLM call either:

1. `grep -c "^### Malaysia" data/company_context.md` (or equivalent read/search) — must find
   exactly one occurrence, inside "Key Prospects & Relationships."
2. Confirm the file still has exactly one `## Ecosystem Players` heading and the new Malaysia
   subsections were appended inside it, not as a new top-level `##` section.
3. `py -c "import re; text=open('data/company_context.md',encoding='utf-8').read(); assert 'SpatioX' not in text, 'do not reintroduce SpatioX naming'; print('OK')"`
   — must print `OK` (guards against accidentally reintroducing already-cleaned-up terminology).
4. Run `py scripts/seed_vectorstore.py` — must print `Seeded N chunks into 'company_context'
   collection.` with `N > 0` and exit code 0, no traceback (this number will be higher than
   Feature 001's recorded 34, since this task adds new content).
5. Confirm the re-seed picked up the new content:
   ```python
   from pipeline.vectorstore import get_collection, COMPANY_CONTEXT
   col = get_collection(COMPANY_CONTEXT)
   result = col.get(limit=200, include=["documents"])
   docs = result.get("documents", [])
   assert any("Sunway" in d for d in docs), "Malaysia content not found in re-seeded collection"
   print(f"{len(docs)} chunks confirmed, Malaysia content present")
   ```

## Model tier

mid — the exact Malaysia-subsection text is provided above and can largely be transcribed, but the
executor must correctly place it within the existing document structure (right section, right
subsection boundary) and verify it doesn't disturb the untouched sections around it.

## Depends on

None. Isolated to `data/company_context.md` (and running the unmodified seeding script) — no other
task touches this file. Can run in parallel with Tasks 001/002/003.

## Evidence

Executor report (DONE):
1. `grep -c "^### Malaysia"` → `1`.
2. Single `## Ecosystem Players` heading confirmed; Malaysia subsections appended inside it before `## BD Priorities`.
3. SpatioX-absence check → `OK`.
4. `py scripts/seed_vectorstore.py` → `Seeded 46 chunks into 'company_context' collection.` (up from 34 baseline), exit 0.
5. Re-seed content check → `46 chunks confirmed, Malaysia content present`.

Files changed: `data/company_context.md` only (85 pure insertions). "Competitive Positioning" untouched, per constraint.
