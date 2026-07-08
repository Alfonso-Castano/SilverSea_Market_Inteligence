# Task 003: Finish SpatioX→real-catalog rebuild in `data/company_context.md`

**Status:** done

## Files

- `data/company_context.md` (modify only)

## What to do

The "Products by Business Sector" section (lines 12-47) is already a verified-correct
transcription of the real ~14-solution catalog from `docs/Copy of Business Sector _ed01.pdf` —
confirmed against the source PDF this planning session, do not re-derive or edit it.

Three other sections still reference the old placeholder "SpatioX Twin/Ops/Audit/Walk" framing
and need rewriting to reference the real catalog instead, using this naming map (confirmed
against the PDF's BER solution list):

| Old SpatioX name | Real catalog name |
|---|---|
| SpatioX Twin | Digital Twin |
| SpatioX Ops | Smart Facility Management System |
| SpatioX Audit | Smart Virtual Inspection |
| SpatioX Walk | 3D/VR Virtual Tour |

**Section 1 — `## Target Sectors & Use Cases` (lines 49-64):** Every bullet currently ends with a
parenthetical like `(SpatioX Twin, Walk)`. Replace each SpatioX reference with the real catalog
name(s) per the map above. For the "Education" bullet specifically, also draw on the EDU solution
list (STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour, Metaverse
Platform, Customized AR/VR Content) rather than only BER-mapped names, since Education is its own
active domain this round, not a BER sub-case. Example transformation:
- Before: `**Real estate** — ... (SpatioX Twin, Walk).`
- After: `**Real estate** — ... (Digital Twin, 3D/VR Virtual Tour).`
- Before: `**Education** — Campus digital twins for facilities planning, virtual orientation, and
  remote learning environments at universities and institutions (SpatioX Twin, Walk).`
- After: `**Education** — Campus digital twins for facilities planning (Digital Twin), and virtual
  orientation, remote learning, and STEM lab environments at universities and institutions
  (Virtual Campus, STEM 3D Virtual Lab, 3D/VR Virtual Tour).`
Apply the same pattern (map to the real name, and for Education prefer EDU-sector solution names)
to every bullet in this section: Smart FM, Government/smart-city, Retail, Tourism, MICE.

**Section 2 — `## Key Prospects & Relationships` (lines 91-105):** Every prospect entry says
"Prospective buyer of SpatioX Twin...". Replace with "Digital Twin" (or the more specific real
solution name where the sentence's context calls for it — e.g. NUS/NTU's "immersive
orientation/training experiences (SpatioX Walk)" becomes "immersive orientation/training
experiences (3D/VR Virtual Tour)"). Keep every other fact (company names, business rationale)
unchanged — this is a terminology substitution, not a content rewrite.

**Section 3 — `## Ecosystem Players` (lines 107-137):** Every contractor/consultant/M&E-integrator
/FM-firm bullet references "SpatioX Twin/Ops/Audit" (e.g. "digital twin collaboration potential",
"potential partner for construction-phase SpatioX Audit integration", "SpatioX Ops integration
opportunity"). Replace each SpatioX product mention with its real-catalog equivalent per the map
above. Where the existing text says just "digital twin" (lowercase, generic, not "SpatioX Twin")
— e.g. "digital twin collaboration potential on large construction projects" for MCC — that's
already fine as-is, no change needed; only the explicit "SpatioX <Product>" strings need
substitution.

## Interfaces

None — this is a prose/markdown content edit, no code interfaces involved.

## Constraints

- Do NOT touch the "Products by Business Sector" section (lines 12-47) — already verified
  correct.
- Do NOT touch `## Company Overview`, `## Competitive Positioning` (no SpatioX references found
  there), `## BD Priorities`, or `## Regulatory & Certification Note`.
- Do NOT touch the draft banner comment on line 1 (`<!-- DRAFT: rebuilt 2026-07-02... -->`) — out
  of this round's scope.
- Preserve every factual claim (company names, relationship type, rationale) — only the
  product-name terminology changes.
- This file is the RAG seed doc — changes here only take effect once
  `scripts/seed_vectorstore.py` is re-run (see the dependent re-seed task).

## Verification

Code-inspection-level, no LLM call needed:

1. `grep -n -i spatiox data/company_context.md` — must return zero matches after the edit (down
   from the current 3-section set of matches).
2. Re-read the three edited sections in full and confirm every real-catalog name used actually
   appears in the "Products by Business Sector" table (i.e. no invented product names).
3. Confirm the "Products by Business Sector" section (lines 12-47) is byte-identical to before
   the edit (diff should show zero changes there).

## Model tier

mid — requires judgment to reword each bullet naturally while staying strictly within the real
catalog's vocabulary and not altering any factual claims.

## Depends on

None.

## Evidence

**Status: DONE**

- `grep -n -i spatiox data/company_context.md` → exit code 1, zero matches.
- `git diff --stat data/company_context.md` → 24 insertions / 24 deletions, confined to the three
  target sections (no lines before line 48 touched).
- Line-range diff of lines 12-47 ("Products by Business Sector") between HEAD and working copy →
  byte-identical, confirmed independently by the dispatching session.
- All real-catalog names substituted (Digital Twin, Smart Facility Management System, Smart
  Virtual Inspection, 3D/VR Virtual Tour, Virtual Campus, STEM 3D Virtual Lab) verify against the
  "Products by Business Sector" table.
- One judgment call within the task's own instructions: generic bare "SpatioX" mentions not tied
  to a specific product (e.g. "co-bid SpatioX on projects") were reworded to "co-bid Silversea's
  solutions on projects" since no single real-catalog product maps to a generic reference — this
  satisfies the zero-spatiox-matches requirement while preserving the original meaning.
