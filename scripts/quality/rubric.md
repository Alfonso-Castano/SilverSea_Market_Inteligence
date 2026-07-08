# Report Quality Rubric — Silversea Market Intelligence

Used every week to evaluate the pipeline output before it goes to stakeholders.
Reviews are saved to `quality/reviews/YYYY-MM-DD.md`.

---

## Two-Pass Review Process

### Pass 1: Fact-Check
For every specific claim in the report (company name, project, dollar figure, tender,
policy announcement), the reviewer searches the web to verify it exists and is recent.

Each claim is tagged:
- **VERIFIED** — found a credible source confirming it
- **PLAUSIBLE** — consistent with known facts but no direct confirmation found
- **UNVERIFIED** — searched and found nothing corroborating it
- **HALLUCINATED** — searched and found it to be factually wrong

Only after Pass 1 is complete does Pass 2 run. A report with multiple HALLUCINATED
claims should fail regardless of quality scores.

---

### Pass 2: Quality Scoring

Score each dimension 1–5. Total out of 25.

| Dimension | 1 (Poor) | 3 (Acceptable) | 5 (Excellent) |
|---|---|---|---|
| **Accuracy** | Multiple unverified/wrong claims | Most claims plausible, minor errors | All claims verified against real sources |
| **Specificity** | Vague generalities, no names/numbers | Some specifics, some filler | Named companies, dollar figures, dates throughout |
| **Actionability** | BD team cannot act on anything | 1-2 items are actionable | Clear next steps on 3+ opportunities |
| **Coverage** | Key sectors/signals missing | Most sectors covered, some gaps | All 6 report sections substantive, no obvious gaps |
| **Relevance** | Noise dominates (generic property news) | Mostly relevant, some off-topic | Every item is directly relevant to Silversea |

**Score interpretation:**
- 22–25: Ship it — strong report
- 16–21: Acceptable — minor prompt tuning needed
- 10–15: Weak — significant prompt or source improvements needed
- Below 10: Do not ship — investigate pipeline issues

---

## What "Relevant to Silversea" Means

Content is relevant if it involves:
- Digital twin, BIM, 3D scan, point cloud, XR/AR/VR, spatial computing
- Smart FM, smart buildings, building automation, proptech
- Government tenders/ITQs from BCA, URA, HDB, JTC, MND
- Named competitors: Hiverlab, Gelement, TwinLogic, TwinMatrix, Axomem, DataMesh
- Named prospects: JTC, CapitaLand, Mapletree, Lendlease, SGH, NUH, NUS, NTU, SMU
- Policy signals from Smart Nation, BCA Green Mark, IDD

Content is NOT relevant if it is:
- Generic Singapore property price/volume news with no tech angle
- Retail/F&B/residential market commentary
- Regional macro news unconnected to SG built environment
