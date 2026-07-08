# Task 004: Finish SpatioX→real-catalog rebuild in `pipeline/analyst.py`

## Files

- `pipeline/analyst.py` (modify only)

## What to do

Four sub-edits in this file all stem from the same problem: the pipeline still reasons about
opportunities/implications/competition using the old 4-product SpatioX/BER-only worldview, even
though `data/company_context.md`'s real catalog (7 sectors, EDU+BER active this round) has been
separately rebuilt (see the sibling company-context task — no dependency either direction; this
task inlines its own compact catalog rather than relying on the RAG context, which is disabled).

Naming map (same as the company-context task, confirmed against
`docs/Copy of Business Sector _ed01.pdf`): **Twin → Digital Twin, Ops → Smart Facility Management
System, Audit → Smart Virtual Inspection, Walk → 3D/VR Virtual Tour.**

**1. `SUMMARY_PROMPT`'s hardcoded product catalog (currently lines 65-67):**

Replace:
```python
Silversea products (for opportunity identification):
- SpatioX Twin (digital twin platform), SpatioX Ops (smart FM), SpatioX Audit (virtual inspection), SpatioX Walk (3D/VR tour)
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, smart FM
```
with a compact inline catalog covering both active domains (BER and EDU) instead of BER-only
SpatioX naming:
```python
Silversea products (for opportunity identification):
- Built Environment & Real Estate (BER): Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart Virtual Inspection, 3D/VR Virtual Tour, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video Analytics Solution.
- Education & EdTech (EDU): STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour, Metaverse Platform, Customized AR/VR Content.
- Core tech: digital twin, BIM, 3D scanning, XR/AR/VR, smart FM, IoT, virtual/immersive content.
```

**2. Opportunities gate keyword list (currently line 69):**

Replace:
```python
OPPORTUNITIES: Only include signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building, building automation, or proptech. Zero opportunities is correct when nothing qualifies. Every opportunity must carry the source_name of the specific signal it was extracted from — copy it verbatim from the structured signals input, do not invent a new value.
```
with a version that keeps the keyword-only gate mechanism (per CONTEXT.md — do NOT reinstate the
separate "ecosystem entity action" path this round) but adds EDU terms alongside the existing BER
terms:
```python
OPPORTUNITIES: Only include signals that explicitly mention digital twin, BIM, 3D scanning, XR, smart FM, smart building, building automation, proptech, edtech, virtual campus, STEM lab, e-learning, or virtual/immersive learning. Zero opportunities is correct when nothing qualifies. Every opportunity must carry the source_name of the specific signal it was extracted from — copy it verbatim from the structured signals input, do not invent a new value.
```

**3. `product_fit` field instruction (currently line 92):**

Current text: `"product_fit": "which Silversea solution (see the full product catalog in the
company context, organized by business sector) best fits this opportunity, and why — reason from
the domain the signal's sector belongs to, not just built-environment framing"`. This line
already avoids naming SpatioX directly and already tells the model to reason across domains — but
it references "the company context" for the catalog, and RAG context injection is disabled (see
`_build_rag_context()`, dead code, not restored this round — deferred to the Claude Haiku
switch). Since the model has no actual access to "the company context" at inference time, point it
at the catalog block you just inlined in step 1 instead:
```python
"product_fit": "which Silversea solution (see the product catalog listed above, organized by business sector) best fits this opportunity, and why — reason from the domain the signal's sector belongs to, not just built-environment framing"
```

**4. `_generate_implications()` (currently lines 239-272):**

`SECTOR_IMPLICATIONS` dict (lines 242-248) — every value string is BER-only worded (e.g. "digital
twin and smart FM solutions", "Singapore's built environment sector"). Reword each to be
domain-neutral so it reads correctly for an EDU-sector signal too. Example:
- Before: `"Customers": "Activity from a potential or existing customer that may signal demand for
  digital twin, BIM, or smart FM solutions."`
- After: `"Customers": "Activity from a potential or existing customer that may signal demand for
  digital twin, smart FM, or campus/education technology solutions."`
Apply the same domain-neutral rewording to all six dict values (Government & Agencies, Industry
Associations, Customers, Partners, Competitors, General News).

`SPECIFIC_KEYWORDS` dict (lines 250-261) — every value says "Silversea's SpatioX
Twin/Ops/Audit/Walk". Replace with the real catalog names per the map above, and add EDU-relevant
keyword entries. Example transformation:
- Before: `"digital twin": "Directly relevant to Silversea's core SpatioX Twin platform."`
- After: `"digital twin": "Directly relevant to Silversea's Digital Twin solution."`
- Before: `"smart fm": "Aligns with Silversea's SpatioX Ops smart facility management solution."`
- After: `"smart fm": "Aligns with Silversea's Smart Facility Management System solution."`
- Before: `"virtual tour": "Directly relevant to Silversea's SpatioX Walk 3D/VR tour product."`
- After: `"virtual tour": "Directly relevant to Silversea's 3D/VR Virtual Tour product."`
- Before: `"inspection": "Relevant to Silversea's SpatioX Audit virtual inspection solution."`
- After: `"inspection": "Relevant to Silversea's Smart Virtual Inspection solution."`
Add these new EDU-relevant keys to the same dict (append, don't reorder existing keys):
```python
        "stem lab": "Directly relevant to Silversea's STEM 3D Virtual Lab solution.",
        "virtual campus": "Directly relevant to Silversea's Virtual Campus solution.",
        "edtech": "Relevant to Silversea's education-sector product line (Virtual Campus, STEM 3D Virtual Lab).",
        "e-learning": "Relevant to Silversea's education-sector immersive/virtual learning solutions.",
```

**5. `_derive_competition_risks()` (currently lines 275-325):**

`HIGH_KEYWORDS` list (line 289) is BER-only. Add EDU-relevant terms:
```python
    HIGH_KEYWORDS = ["digital twin", "smart fm", "bim", "3d scan", "iot", "smart building", "facility management", "virtual campus", "stem lab", "edtech"]
```
Mitigation string template (lines 301-303) says `"...differentiate on SpatioX platform
integration."` — replace `"SpatioX platform"` with `"Silversea's product suite"` (domain-neutral,
since this function runs for any competitor signal regardless of domain):
```python
            mitigation = (
                f"Direct competitor in Silversea's core domain. Monitor {entity}'s "
                f"product development closely and differentiate on Silversea's product suite integration."
            )
```

**Do NOT touch** `_clamp_opportunity_scores()` (lines 194-207) — that function is covered by a
separate unit-test task and must not change behavior.

## Interfaces

No function signatures change. `analyse()`'s call graph, return shape (`executive_summary`,
`signals_by_sector`, `opportunities`, `synthesis`, `competition_risks`), and RAG write-back are
all unchanged — only prompt text and Python dict/list literal contents change.

## Constraints

- Keyword-only opportunities gate — do not add back the "ecosystem entity taking a relevant
  action" second path (explicitly deferred, separate decision).
- Don't touch `_build_rag_context()`, `RAG_ENABLED`, `_extract_sector()`, `_synthesize_sector()`,
  `_clamp_opportunity_scores()`, or `analyse()`'s structure — only the specific strings/dict
  literals enumerated above.
- No LLM call needed to verify this task — all five edits are static prompt text and Python
  literals, checkable by direct inspection and (where relevant) importing the module and calling
  the pure-Python functions (`_generate_implications`, `_derive_competition_risks`) with synthetic
  input.

## Verification

1. `grep -n -i spatiox pipeline/analyst.py` — must return zero matches after the edit.
2. Import the module and exercise the two pure-Python functions with synthetic data (no Groq
   call, no network):
   ```python
   from pipeline.analyst import _generate_implications, _derive_competition_risks
   sectors = {"Customers": [{"entity": "NUS", "signal": "NUS launches a virtual campus edtech initiative."}]}
   _generate_implications(sectors)
   print(sectors["Customers"][0]["implication"])  # should mention "Virtual Campus" or "education", not "SpatioX"
   report = {"signals_by_sector": {"Competitors": [{"entity": "G Element", "signal": "G Element wins a digital twin tender."}]}}
   _derive_competition_risks(report)
   print(report["competition_risks"][0]["mitigation"])  # should say "Silversea's product suite", not "SpatioX platform"
   ```
3. Read the final `SUMMARY_PROMPT` string in full and confirm it's valid Python (no syntax
   errors) and every product name mentioned appears in the real catalog transcribed in
   `data/company_context.md`'s "Products by Business Sector" section.
4. Confirm `python -c "import pipeline.analyst"` (or `py -c "import pipeline.analyst"`) succeeds
   with no import errors (this alone doesn't need `GROQ_API_KEY` — that's only read inside
   `analyse()`, not at import time).

## Model tier

mid — the exact replacement text is given above for every edit, but the executor must apply it
correctly across five distinct locations in one file without disturbing surrounding logic, and
verify via the pure-Python function calls above rather than assuming the text edit is sufficient.

## Depends on

None (inlines its own catalog rather than depending on the company-context rebuild or RAG).

## Evidence

**Status: DONE**

- `grep -n -i spatiox pipeline/analyst.py` → exit code 1, zero matches (re-confirmed independently
  by the dispatching session).
- `_generate_implications` on synthetic NUS/virtual-campus signal → `"Directly relevant to
  Silversea's Virtual Campus solution."` (re-run independently, matches).
- `_derive_competition_risks` on synthetic G Element/digital-twin signal → `"...differentiate on
  Silversea's product suite integration."`, no "SpatioX" (re-run independently, matches).
- `git diff pipeline/analyst.py` confirms `_clamp_opportunity_scores` is absent from the diff —
  untouched, as required.
- `py -c "import pipeline.analyst"` succeeds (only the pre-existing, documented
  sentence-transformers HF-weight-loading warning appears, not a new issue).
- Every product name in the rebuilt `SUMMARY_PROMPT` catalog block verified present in
  `data/company_context.md`'s "Products by Business Sector" section.
