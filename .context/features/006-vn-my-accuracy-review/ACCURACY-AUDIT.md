# Accuracy Audit: VN/MY Report Content vs. Real Sources

Findings table format, severity-ranked, per CLAUDE.md's `REVIEW.md` convention (structured findings, not
prose narrative). No `py main.py` run, no LLM calls were used to produce this audit — all comparisons are
against live re-fetched source pages (`refetched/vn_sources.json`) and the original source-list PDF
(`docs/Silversea_Vietnam_Market_07072026.pdf`).

## Vietnam (`latest_report_VN_BER.json`)

**Coverage:** 43 signals across 4 sectors (Competitors 7, Partners 22, General News 1, Customers 13), 3
opportunities, checked against 15 re-fetched sources + `docs/Silversea_Vietnam_Market_07072026.pdf`.

**`source_name` breakage (RESEARCH.md §2):** 42 of the 43 signals and all 3 opportunities carry the
broken literal label `"Extracted signals"` / `"extracted signals"` as `source_name`, not a real source
name — confirmed here independently. Only the single General News signal (`source_name:
"Vietnam Investment Review"`) has a correct, usable `source_name`. This audit therefore joined every
other signal/opportunity to its real source by matching `entity` against the 15 `data_sources` entries
instead. This worked cleanly for all 43 signals — every `entity` in the report corresponds to exactly one
of the 15 cited `data_sources` (Becamex IDC, Siemens, Honeywell, Johnson Controls, NVIDIA, Cisco,
TTDecor, Vietsoft Pro, BM Windows, or Vietnam Investment Review) — so no signal had to fall back to
"unverifiable — third-party entity, no direct source." 5 of the 15 re-fetched sources (Viettel Group,
Bentley Systems, Matterport, Dell Technologies, CBRE Vietnam) produced **zero** attributed signals in the
report despite being successfully scraped — not a finding, just unused source material.

**Summary:** 38 Grounded / 0 Unverifiable / 5 Contradicted-Suspect out of 43 signals; 1 Grounded / 0
Unverifiable / 2 Contradicted-Suspect out of 3 opportunities.

| # | Type | Entity | Claim (short) | Classification | Evidence / Reasoning |
|---|------|--------|----------------|-----------------|----------------------|
| 1 | Signal (Competitors) | Becamex IDC | "...launched Trang Trai Nang Luong Mat Troi, a Solar Energy Farm with a 260 MWp capacity. **They also introduced digital solutions for businesses, including data storage centers and virtual servers.**" | **Contradicted/Suspect — HIGH** | The 260 MWp solar-farm figure is confirmed verbatim on `becamex.com.vn` ("260 MWP Điện Xanh"). But "digital solutions for businesses, including data storage centers and virtual servers" is a **near-verbatim match to Viettel Group's homepage content** ("Digital solutions for businesses (Data storage center; Virtual server...)") — a *different* cited source in the same report. This text does not appear anywhere in Becamex IDC's re-fetched content. This is cross-source content contamination: a claim about one competitor (Viettel Group) misattributed to another (Becamex IDC) in the same signal. |
| 2 | Opportunity | BM Windows | `product_fit`: "Smart Building, Building Automation" | **Contradicted/Suspect — HIGH** | Neither "Smart Building" nor "Building Automation" is a real Silversea product name. `data/company_context.md`'s BER catalog lists only: Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart Virtual Inspection, 3D/VR Virtual Tour, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video Analytics Solution. The opportunity's `concrete_action` ("Propose Silversea's smart building and building automation solutions...") repeats the same non-existent product names, so this is a BD-facing recommendation built on fabricated product names, not a paraphrase of a real one. |
| 3 | Opportunity | Vietsoftpro | `product_fit`: "STEM 3D Virtual Lab, Virtual Campus, E-learning solutions" | **Contradicted/Suspect — MEDIUM** | "STEM 3D Virtual Lab" and "Virtual Campus" are real EDU-catalog products. "E-learning solutions" is not — it does not appear as a named Silversea product anywhere in `company_context.md`'s EDU list (STEM 3D Virtual Lab, Virtual Campus, Virtual Event Platform, 3D/VR Virtual Tour). A plausible-sounding but invented third product name was appended alongside two genuine ones. |
| 4 | Signal (General News) | Vietnam and South Korea | "Vietnam and South Korea **are collaborating** on the Ninh Thuan 2 nuclear power plant project." | **Contradicted/Suspect — MEDIUM** | `vir.com.vn`'s re-fetched homepage headline reads "**Vietnam eyes partnership** with South Korea for Ninh Thuan 2 nuclear power plant / Vietnam **will select** the official partner... in the third quarter of 2026." The source describes a prospective partner-selection process, not an active, already-established collaboration. The signal overstates certainty/timeline on what is explicitly a tender/deadline-relevant claim — exactly the highest-stakes category the audit was asked to scrutinize. |
| 5 | Signal (Partners) | NVIDIA | "NVIDIA **released** DiffusionGemma, an open model for text generation." | **Contradicted/Suspect — LOW** | Source headline: "RTX AI Garage: NVIDIA Accelerates **Google DeepMind's** DiffusionGemma for Local AI." DiffusionGemma is Google DeepMind's model; NVIDIA optimizes/accelerates it for its RTX hardware platform, it did not "release" it. Minor misattribution of authorship. |
| 6 | Signal (Competitors) | Becamex IDC | "...partnered with Sembcorp to co-found the **Vietnam-Singapore Industrial Corporation, VSIC**." | **Contradicted/Suspect — LOW** | Source names the entity "Trung Tâm Đổi Mới Sáng Tạo Việt Nam – Singapore (VSIC)" = **Vietnam-Singapore Innovation Centre**, not "Industrial Corporation." The underlying Becamex/Sembcorp partnership fact is fully confirmed by the source; only the acronym's English expansion is wrong — a translation/expansion error, not a fabricated partnership. (Same signal also renders "National University of Singapore" backwards as "University of National Singapore" — a minor name-order garble, not counted separately.) |
| 7 | Signal (Customers) | TTDecor | `implication`: "Relevant to Silversea's **BIM**-to-digital-twin workflow" | **Contradicted/Suspect — LOW** | The signal's "BIM" refers to **BIM Corporation**, a Vietnamese property-developer group (client on TTDecor's "The Lotus Ha Long" villa project) — not Building Information Modeling. `implication` is Python-generated (`_generate_implications()`, keyword-matched, zero LLM cost per RESEARCH.md §1), so this is a pipeline post-processing artifact (keyword collision on "BIM"), not an LLM synthesis hallucination — flagged for completeness since it still ships in the report. |
| 8+ | Signals (Competitors, Partners, General News, Customers) | Siemens, Honeywell, Johnson Controls, Becamex IDC (remaining 2 signals), all 18 remaining NVIDIA signals, all 4 Cisco signals, TTDecor (remaining 2 signals), Vietsoft Pro (all 4 signals), BM Windows (all 6 signals) | Various — see `data/latest_report_VN_BER.json` | **Grounded** (38 signals total) | Each independently checked against its re-fetched source content in `vn_sources.json` via entity-name match; every named product, partnership, figure, date, or event (e.g. Siemens "Vectron X"/"Building X"/"Electrification X"/Amazon-rainforest digital twin; Honeywell's MIT partnership and NOTIFIER INSPIRE launch; Johnson Controls' Metasys 16.0 and Alliance for Climate Transition listing; TTDecor's Him Lam 2014 / Nam Long 2020 / IHG Intercontinental Phú Quốc partnerships; Vietsoft Pro's Jan 25 / Dec 30 2025 / Sep 12 2025 event dates and Hue IoT Hub opening; BM Windows' BMU launch, Chau Duc groundbreaking, and New York award, all with matching dates) is directly present in the corresponding source's re-fetched content, in most cases near-verbatim. No further hallucinations found in this group. |
| — | Opportunity | Becamex IDC Eco-Industrial Park | `source_quote` + `product_fit`: "Smart Facility Management System, Digital Twin" | **Grounded** (1 opportunity) | Source quote matches Becamex's re-fetched content; both named products are real BER-catalog items and a plausible fit for an industrial-park facility-management opportunity. |

**Note on category totals:** rows 1, 4, 5, 6, 7 above are signal-level findings (5 of 43); rows 2 and 3
are opportunity-level findings (2 of 3). Combined with the one Grounded opportunity, this fully accounts
for all 3 opportunities and, via the grouped row, all 43 signals.

## Malaysia (`latest_report_MY_GENERAL.json`)

[Left for Task 004 to fill in — do not write anything here.]
