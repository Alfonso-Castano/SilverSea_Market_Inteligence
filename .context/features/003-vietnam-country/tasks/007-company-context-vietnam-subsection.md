# Task 007: Add a Vietnam subsection to `data/company_context.md` + re-seed the vectorstore

**Status:** done

## Files

- `data/company_context.md` (modify — additions only, inside two existing sections)
- No other file changes. This task also *runs* (does not modify) `scripts/seed_vectorstore.py`.

## What to do

**Background:** `pipeline/analyst.py`'s RAG retrieval against the `COMPANY_CONTEXT` ChromaDB
collection is not country-filtered by design (correct for the product catalog, which is
country-agnostic) — per CONTEXT.md's decision, this means the two prospect/ecosystem sections
need their own Vietnam content, or every VN report run risks pulling in irrelevant Singapore
prospect framing. The "Products by Business Sector," "BD Priorities," and "Regulatory &
Certification Note" sections are already country-agnostic and must NOT be touched by this task.

**1. Add a Vietnam subsection to "Key Prospects & Relationships"** (current section spans lines
91-105, ending right before "## Ecosystem Players" at line 107). Insert a new `###` subheading
and content immediately after the existing SG content (after the "Government agencies tracked..."
paragraph, before the `## Ecosystem Players` heading):

```markdown
### Vietnam

**Vingroup** — Vietnam's largest private conglomerate, real estate/smart city developer.
Prospective buyer of Digital Twin for smart-city and large-scale development projects.

**Sun Group** — Major Vietnamese developer (resorts, urban, entertainment). Prospective buyer of
Digital Twin and 3D/VR Virtual Tour for new development marketing and facilities planning.

**VSIP (Vietnam Singapore Industrial Park)** — Industrial park developer/operator. Prospective
buyer of Smart Facility Management System and Digital Twin for industrial park asset management.

**VNPT** — State-owned telecom group active in smart city initiatives. Prospective partner/buyer
for Digital Twin and IoT & AI Solutions in smart city programmes.

**Panasonic Vietnam** — Manufacturing operations. Prospective buyer of Smart Facility Management
System and IoT & AI Solutions for smart factory initiatives.

**Samsung Vietnam** — Large-scale manufacturing operations. Prospective buyer of Smart Facility
Management System and Digital Twin for factory digitalization.

**Education prospects:** Văn Lang University and HUIT (Ho Chi Minh City University of Industry
and Trade) — campus digital twin (Digital Twin) and virtual event/orientation use cases (3D/VR
Virtual Tour, Virtual Event Platform), same profile as NUS/NTU in Singapore. Sao Mai Group
(Vrealab platform) and Lạc Việt (VR training for medical/education) are additional
education-technology-adjacent prospects worth tracking for partnership or competitive signals.

**Government agencies tracked for tender and policy signals:** ITPC (Ho Chi Minh City Investment
& Trade Promotion Centre — IT solution focus), Ministry of Construction (MOC — BIM policy, smart
buildings, digital twin), Ministry of Industry & Trade (MOIT — Industry 4.0, energy), Ministry of
Science & Technology (MOST — AI, innovation), Ministry of Health (MOH — smart hospital), Ministry
of Education & Training (MOET — smart campus), National Innovation Center (NIC — innovation
funding).
```

**2. Add a Vietnam subsection to "Ecosystem Players"** (current section spans lines 107-136).
Insert a new `###` subsection at the end of that section, after the existing "Facility management
firms" subsection (before `## BD Priorities` at line 138):

```markdown
**Vietnam — technology dealers/suppliers** — Infrastructure and platform partners whose products
complement Silversea's delivery stack, not direct BD targets:
- NVIDIA — AI GPUs, Omniverse; potential technology partner for Digital Twin/3D rendering
  infrastructure
- Microsoft Azure — Cloud AI; potential cloud infrastructure partner
- Amazon Web Services — Cloud; potential cloud infrastructure partner
- Dell Technologies — Workstations; potential hardware supplier for 3D scanning/rendering
  workloads
- Cisco — Networking; potential infrastructure partner for large-scale smart building deployments

**Vietnam — facility management firms** — Potential customers for Smart Facility Management
System, or channel partners reselling FM services on top of it:
- Savills Vietnam — Global property consultancy's Vietnam arm; potential Smart Facility
  Management System / Digital Twin customer for portfolio-wide FM contracts
- CBRE Vietnam — Global real estate services' Vietnam arm; potential Smart Facility Management
  System customer for FM portfolio management
```

Do not add a Vietnam competitor list to "Competitive Positioning" — CONTEXT.md's scope for this
task is explicitly limited to "Key Prospects & Relationships" and "Ecosystem Players" only.

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
- Ground every entity mentioned in the new subsections in the source list above (or in the source
  list Task 001 transcribed into `config/sources.json`) — do not invent prospects, product
  pairings, or facts not present in either source. The product names used (Digital Twin, Smart
  Facility Management System, 3D/VR Virtual Tour, IoT & AI Solutions, Virtual Event Platform) must
  come from the existing "Products by Business Sector" catalog already in this file — do not
  invent new product names.
- Keep the same prose style/format as the existing SG entries (bold entity name, em-dash,
  one-to-two sentence description referencing a specific Silversea product) — this is additive
  content matching an established pattern, not a redesign.

## Verification

No LLM call needed for the Markdown edit; the re-seed step makes no LLM call either:

1. `grep -c "^### Vietnam" data/company_context.md` (or equivalent read/search) — must find
   exactly one occurrence, inside "Key Prospects & Relationships."
2. Confirm the file still has exactly one `## Ecosystem Players` heading and the new Vietnam
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
   assert any("Vingroup" in d for d in docs), "Vietnam content not found in re-seeded collection"
   print(f"{len(docs)} chunks confirmed, Vietnam content present")
   ```

## Model tier

mid — the exact Vietnam-subsection text is provided above and can largely be transcribed, but the
executor must correctly place it within the existing document structure (right section, right
subsection boundary) and verify it doesn't disturb the untouched sections around it.

## Depends on

None. Isolated to `data/company_context.md` (and running the unmodified seeding script) — no
other task touches this file.

## Evidence

Executor report (DONE):
1. `grep -c "^### Vietnam"` → `1`.
2. Single `## Ecosystem Players` heading confirmed; Vietnam subsections appended inside it before `## BD Priorities`.
3. SpatioX-absence check — printed `OK`.
4. `py scripts/seed_vectorstore.py` → `Seeded 41 chunks into 'company_context' collection.` (up from 34), exit 0.
5. Re-seed content check → `41 chunks confirmed, Vietnam content present`.

Files changed: `data/company_context.md` only. `git diff` confirmed purely additive to the two named sections.
