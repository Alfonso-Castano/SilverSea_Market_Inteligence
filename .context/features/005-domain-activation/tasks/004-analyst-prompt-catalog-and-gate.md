# Task 004: Add RCC/HLS/MFG/CTE/PSS to `SUMMARY_PROMPT`'s product catalog and broaden the opportunities gate

**Status:** done
**Depends on:** none
**Model tier:** cheap — both edits are fully specified below, transcribed verbatim from
`data/company_context.md`'s existing product catalog (already read for this planning pass) and
`config/sources.json`'s Malaysia `keywords` list; the executor's job is transcription plus running
the verification commands, not judgment.

## Files
- Modify: `pipeline/analyst.py` (lines 65-70, inside the `SUMMARY_PROMPT` constant only)

## What to do

Use the Edit tool with exact string matches (`old_string`/`new_string`) — do NOT rewrite
`SUMMARY_PROMPT` with `.format()` or touch any other part of the constant. This mirrors the
precedent set by Feature 003 Task 006 (`.context/features/003-vietnam-country/tasks/006-analyst-prompt-country-interpolation.md`):
the string contains a literal JSON schema block with curly braces later on, so only targeted
`str.replace()`-style edits on unique substrings are safe.

**Edit 1 — add the 5 new product catalogs.** Current text (lines 67-68):
```
- Education & EdTech (EDU): STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour, Metaverse Platform, Customized AR/VR Content.
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, smart FM, IoT, virtual/immersive content.
```
Replace with (insert 5 new bullet lines between the EDU line and the "Core tech" line — text
transcribed verbatim from `data/company_context.md`'s "Products by Business Sector" section):
```
- Education & EdTech (EDU): STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour, Metaverse Platform, Customized AR/VR Content.
- Manufacturing & Industry 4.0 (MFG): Digital Twin, Smart Virtual Inspection, IoT & AI Solutions, Smart Facility Management System, Customized AR/VR Content, 3D Scanning to 3D Model.
- Healthcare & Life Sciences (HLS): Smart Facility Management System, 3D/VR Virtual Tour, Customized AR/VR Content, Digital Twin, IoT Solution, CCTV Video Analytics Solution.
- Retail, Commerce & Consumer Goods (RCC): Virtual Showroom, Smart Virtual Mockup, Interactive Digital Content, Metaverse Platform, 3D Scanning to 3D Model, Customized AR/VR Content.
- Culture, Tourism & Events (CTE): Virtual Event Platform, 3D/VR Virtual Tour, Interactive Digital Content, Metaverse Platform, 3D Scanning to 3D Model.
- Public Sector & Smart Cities (PSS): Digital Twin, Smart Facility Management System, Smart Virtual Inspection, IoT & AI Solutions, Customized AR/VR Content.
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, smart FM, IoT, virtual/immersive content.
```

**Edit 2 — broaden the OPPORTUNITIES gate keyword list.** Current text (line 70):
```
OPPORTUNITIES: Only include signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building, building automation, proptech, edtech, virtual campus, STEM lab, e-learning, or virtual/immersive learning. Zero opportunities is correct when nothing qualifies. Every opportunity must carry the source_name of the specific signal it was extracted from — copy it verbatim from the structured signals input, do not invent a new value.
```
Replace with (adds cross-sector terms reusing Malaysia's already-established `config/sources.json`
`keywords` vocabulary — the 18 terms appended after `"blended learning"` in that country's block —
covering retail/showroom, healthcare/hospital, manufacturing/factory, tourism/heritage, and
government/smart-city signals):
```
OPPORTUNITIES: Only include signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building, building automation, proptech, edtech, virtual campus, STEM lab, e-learning, virtual/immersive learning, virtual showroom, retail chain, healthcare, hospital, manufacturing, factory, tourism, heritage trail, smart city, or government digitalization. Zero opportunities is correct when nothing qualifies. Every opportunity must carry the source_name of the specific signal it was extracted from — copy it verbatim from the structured signals input, do not invent a new value.
```

## Interfaces

- `SUMMARY_PROMPT` remains a module-level string constant with the same `{country_name}` placeholder
  and the same trailing JSON schema block — no signature or call-site changes anywhere. Nothing else
  in this feature depends on this task's output at the code level (the company_context.md task,
  Task 005, is edited independently and does not need this task to run first or vice versa — this
  task already has the verbatim product text it needs).

## Constraints

- Do not touch the scoring rubric, the JSON schema block, `_clamp_opportunity_scores()`,
  `_generate_implications()`, `_derive_competition_risks()`, `_synthesize_summary()`, or any other
  prompt (`SECTOR_EXTRACT_PROMPT`, `SECTOR_SYNTHESIS_PROMPT`) in this file.
- Do not use `.format()` on the full `SUMMARY_PROMPT` string — it contains literal `{...}` JSON
  blocks later in the same string that `.format()` would misinterpret.
- Do not add a 6th "GENERAL" bullet to the product list — `GENERAL` is not a business-sector product
  catalog, it's the existing "relevant to Silversea overall" fallback domain; nothing in
  `company_context.md`'s product catalog corresponds to it and CONTEXT.md does not ask for one.
- Product text must match `data/company_context.md`'s "Products by Business Sector" section
  verbatim (not reworded) — that file is the source of truth for these 5 catalogs.

## Verification

Run from the repo root — pure string/syntax checks, no LLM call, no Groq quota used:

```
py -c "import ast; ast.parse(open('pipeline/analyst.py', encoding='utf-8').read())"
```
Must produce no output (no `SyntaxError`).

```
py -c "
from pipeline.analyst import SUMMARY_PROMPT
for code, name in [
    ('MFG', 'Manufacturing & Industry 4.0'),
    ('HLS', 'Healthcare & Life Sciences'),
    ('RCC', 'Retail, Commerce & Consumer Goods'),
    ('CTE', 'Culture, Tourism & Events'),
    ('PSS', 'Public Sector & Smart Cities'),
]:
    assert f'({code})' in SUMMARY_PROMPT, code
    assert name in SUMMARY_PROMPT, name
for term in ['virtual showroom', 'retail chain', 'healthcare', 'hospital', 'manufacturing', 'factory', 'tourism', 'heritage trail', 'smart city', 'government digitalization']:
    assert term in SUMMARY_PROMPT, term
assert '\"strategic_fit\": 0' in SUMMARY_PROMPT, 'JSON schema block corrupted'
assert '{country_name}' in SUMMARY_PROMPT, 'country placeholder lost'
print('OK')
"
```
Must print `OK` with no `AssertionError`.

## Evidence

Executor report (DONE): syntax check clean, all 5 sector codes/names present, all 10 new opportunity keywords present, JSON schema block intact, country placeholder intact. `pipeline/analyst.py` only.
