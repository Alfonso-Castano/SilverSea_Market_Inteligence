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

**Coverage:** 9 signals across 5 sectors (Government & Agencies 3, Industry Associations 1, Customers 2,
Partners 2, Competitors 1), 3 opportunities, checked against 25 re-fetched sources
(`refetched/my_sources.json`) and `config/sources.json`'s MY block. `docs/Source_submission_Malaysia_
Sources.pdf` could not be read in this environment (the `Read` tool's PDF renderer requires
`poppler-utils`, not installed here — a tooling limitation, not a data gap) — per the task's stated
priority order, `refetched/my_sources.json` is priority #1 and was sufficient ground truth for every
claim below; all 7 entity names checked below were independently cross-verified against
`config/sources.json`'s MY source list (priority #3) and matched exactly.

**`source_name` cross-check (RESEARCH.md §2):** confirmed 4 of 9 signals carry non-matching `source_name`
values — `"source not specified"` (TA Global, Malaysia Airport Holding Berhad — 2 signals),
`"source text"` (ITMAX System Berhad, Redtone — 2 signals), and `"Extracted signals"` (Accenture — 1
signal); plus `"Balai Seni Negara"` on a third National Art Gallery signal, a real entity name (the Malay
name for National Art Gallery) but not the exact configured `source_name`, so still a lookup miss. All 4
were resolved via entity-name fallback against the 25 `data_sources` entries and matched cleanly — the
"Balai Seni Negara" fallback is further confirmed by National Art Gallery's own re-fetched homepage, which
literally carries "Balai Seni Negara" as its own Malay-language masthead label. The remaining 5 signals
and all 3 opportunities already carry correct, matching `source_name`s — no fallback needed.

**Summary:** 8 Grounded / 0 Unverifiable / 1 Contradicted-Suspect out of 9 signals; 1 Grounded / 0
Unverifiable / 2 Contradicted-Suspect out of 3 opportunities.

| # | Type | Entity | Claim (short) | Classification | Evidence / Reasoning |
|---|------|--------|----------------|-----------------|----------------------|
| 1 | Signal (Government & Agencies) | National Art Gallery | Two named tenders — "Sebut Harga Bagi Kerja-Kerja Baik Pulih Dan Penggantian Paip Bekalan Air Serta Kerja-Kerja Berkaitan" and "Sebut Harga Bagi Perkhidmatan Penyeggaraan Secara Komprehensif Sistem Penyahlembapan (Dehumidifier)" — no deadline stated | **Grounded** | Both exact Malay procurement titles appear verbatim in `artgallery.gov.my`'s re-fetched "PENGUMUMAN" (Announcements) section — not garbled or invented. No deadline is stated on the live page either, matching the report's "no deadline found." |
| 2 | Signal (Government & Agencies) | National Art Gallery | Exhibition list (Cinta Buatan Malaysia, KePulauan: Refleksi BIMP-EAGA, Orang Timur, Asal Tanah, Bakat Muda Sezaman) + Festival Budaya Malaysia Perak 2026 + Pesta Buku Antarabangsa 2026; `implication`: "Relevant to Silversea's **BIM**-to-digital-twin workflow" | **Contradicted/Suspect — LOW** | The signal's factual content is fully grounded — every exhibition/event title matches `artgallery.gov.my`'s re-fetched "PAMERAN" and "SIARAN MEDIA" lists verbatim. But the Python-generated `implication` field ("BIM-to-digital-twin workflow") is a keyword-collision artifact: the only "BIM" substring anywhere near this signal is inside "**BIM**P-EAGA" (Brunei-Indonesia-Malaysia-Philippines East ASEAN Growth Area — a real regional economic bloc name, nothing to do with Building Information Modeling). Same defect pattern as the VN audit's TTDecor/"BIM Corporation" finding (`implication` is zero-LLM-cost, keyword-matched Python post-processing per RESEARCH.md §1) — a pipeline artifact, not an LLM synthesis hallucination, but it still ships in the live report. |
| 3 | Signal (Government & Agencies) | Balai Seni Negara | "...strengthened its partnership with media as a strategic partner for 'Hawana 2026'." | **Grounded** | Matches `artgallery.gov.my`'s re-fetched "SIARAN MEDIA" heading verbatim: "Balai Seni Negara Perkukuh Kerjasama Dengan Media Sebagai Rakan Strategik Hawana 2026." "Balai Seni Negara" is confirmed as National Art Gallery's own Malay-language masthead label — the `source_name` mismatch (RESEARCH.md §2) is a lookup-key defect, not a factual error in the claim itself. |
| 4 | Signal (Industry Associations) | GreenRE | Partnered with CamTech University (Cambodia) to advance sustainable practices through education/training | **Grounded** | Matches `greenre.org`'s re-fetched News list near-verbatim: "GreenRE and CamTech University (Cambodia) Sign MOU to Advance Green Building Training and Education." |
| 5 | Signal (Customers) | TA Global | Launched CloutHaus Residences (mixed-use); launched The Arden office tower, planned for 1Q2026 | **Grounded** | `taglobal.com.my`'s re-fetched content confirms both named projects and the 1Q2026 timing for The Arden ("TA Global to launch The Arden office tower in 1Q2026"). The source (dated Oct 13, 2025) uses future tense ("will launch...in the fourth quarter of this year") for CloutHaus rather than the report's past tense "launched" — a minor tense mismatch, but Q4 2025 has since passed relative to the report's July 2026 date, and CloutHaus Residences is listed as a current live "Property Highlight" elsewhere on the same re-fetched page — not treated as a fabrication. |
| 6 | Signal (Customers) | Malaysia Airport Holding Berhad | Groundbreaking ceremony for Subang MRO Logistics Complex Project, a partnership with Mitsui Fudosan | **Grounded** | Near-verbatim match to `corporate.malaysiaairports.com.my`'s re-fetched "MITSUI FUDOSAN AND MALAYSIA AIRPORTS BREAK GROUND ON SUBANG MRO LOGISTICS COMPLEX PROJECT" (dated 09 Jul 26), including the JV structure (MFMA Industrial Sdn Bhd, a joint venture of Mitsui Fudosan (Asia) Malaysia and Malaysia Airports (Subang) Sdn Bhd). |
| 7 | Signal (Partners) | ITMAX System Berhad | "No actionable signals found for ITMAX System Berhad." | **Grounded** | `itmax.com.my`'s re-fetched content is generic evergreen product marketing (smart-city solutions) with no dated announcement to extract — an honest abstain that correctly reflects the source, not a fabrication. |
| 8 | Signal (Partners) | Redtone | "No actionable signals found for Redtone." | **Grounded** | `redtone.com`'s re-fetched content is likewise generic product/company marketing with no specific dated news item in the extracted text — honest abstain. |
| 9 | Signal (Competitors) | Accenture | Partnered with UNICEF (GenU) for youth development; partnered with ServiceNow for AI-powered services; teamed with Siemens Digital Industries on software/automation | **Grounded** | All three sub-claims match `accenture.com/my-en`'s re-fetched news list near-verbatim: "How UNICEF's GenU is closing the youth skills gap," "ServiceNow and Accenture launch AI-powered services...," and "Accenture to Strengthen Capabilities for Software and Automation Solutions from Siemens Digital Industries." `source_name` was the broken "Extracted signals" value; resolved via entity-name fallback to the `Accenture` `data_sources` entry. |
| — | Opportunity | TA Global's CloutHaus Residences | `source_quote` + `product_fit`: "Smart Facility Management System, Digital Twin" | **Grounded** | Source quote matches signal 5's grounded content. Both product names are real BER-catalog items (`data/company_context.md`'s Products by Business Sector) and a plausible fit for a mixed-use residential/commercial development, consistent with the catalog's general Real Estate framing (Digital Twin, 3D/VR Virtual Tour) plus Smart FM for the operational phase. |
| — | Opportunity | Malaysia Airport Holding Berhad's Subang MRO Logistics Complex Project | `product_fit`: "Smart Facility Management System, Building Automation" | **Contradicted/Suspect — MEDIUM** | "Building Automation" is not a real Silversea product — the catalog (`data/company_context.md`'s Products by Business Sector) lists only Smart Facility Management System, Digital Twin, Smart Virtual Mockup, Smart Virtual Inspection, 3D/VR Virtual Tour, 3D Scanning to 3D Model, IoT & AI Solutions, CCTV Video Analytics Solution among BER products; "building automation" appears in the file only as a description of third-party BMS vendors' own products (Honeywell, Schneider Electric, Azbil), never as a Silversea offering. Also diverges from `company_context.md`'s own pre-established fit for this exact prospect ("Malaysia Airport Holding Berhad (AR way-finding and Digital Twin) — both Public Sector & Smart Cities prospects") — neither "Smart Facility Management System" nor "Building Automation" matches that established framing. |
| — | Opportunity | GreenRE's partnership with CamTech University | `product_fit`: "Digital Twin, Smart Building" | **Contradicted/Suspect — MEDIUM** | "Smart Building" is not a real Silversea product name (same catalog check as above); "Digital Twin" is real and plausible. Diverges from `company_context.md`'s own pre-established GreenRE fit, listed under "Malaysia — government/association ecosystem": "Potential collaborator on AI-enabled Digital Twin with **Smart Facility Management System** (green-building certification body)" — the correct second product should be "Smart Facility Management System," not the invented "Smart Building." |

**Note on category totals:** row 2 above is the one signal-level finding (1 of 9); the two Opportunity rows
above are the 2 of 3 opportunity-level findings. Combined with the 8 Grounded signal rows (1, 3-9) and the
1 Grounded opportunity, this fully accounts for all 3 opportunities and all 9 signals.

**Domain note (GENERAL vs. sub-domain specificity):** consistent with RESEARCH.md §4 (lead 3 —
`analyse()` receives no explicit `domain` parameter), every `product_fit` in this report reasons in
generic BER-style terms (Smart Facility Management System, Digital Twin) regardless of the report being
labeled `GENERAL`. None of the 9 signals or 3 opportunities is substantively about a non-BER sub-domain
(healthcare, retail, tourism) even though 4 of the 25 cited `data_sources` are healthcare entities
(Avisena Women's & Children Specialist Hospital, IHH Healthcare, UCSI Hospital, Sunway Medical Centre) —
none of the four produced an extracted signal in this run, so no HLS-specific `product_fit` mismatch was
observable to check.
