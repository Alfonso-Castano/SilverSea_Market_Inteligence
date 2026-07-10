# Code-Correctness Review: VN/MY + Domain-Activation Wiring

Findings table format, severity-ranked, per CLAUDE.md's `REVIEW.md` convention. Covers
`feature/003-vietnam-country`, `feature/004-malaysia-country`, and `feature/005-domain-activation`'s
current merged state (this section) and sampled git history (Task 006's section below).

**Scope & method.** Read-only code review of the *current merged worktree state* on
`feature/006-vn-my-accuracy-review`. Verified each RESEARCH.md §2–4 finding against the live files
(exact line numbers below reflect this worktree), extended them with structural evidence pulled from
`config/sources.json` and the two generated report JSONs, and re-derived severities. No code, config,
or template was modified — findings only. Three findings map to pre-scoped optional fix tasks
(007/008/009); the rest are flagged as needing prompt-engineering / architectural judgment and are
written up in full here. Fix tasks 008 (`GROQ_API_KEY` `KeyError`) and 009 (`weekly.py` hardcoded
company/country string) are mechanical, already-scoped, and cross-referenced where they touch the same
files, but are out of this section's five review areas and are not re-detailed here.

Evidence commands run this pass (all read-only, zero LLM/Groq calls):
- Parsed `config/sources.json`: VN = 60 sources / 14 priority + 76 general keywords; MY = 55 sources /
  15 priority + 99 general keywords. **All 60 VN and all 55 MY (and all 62 SG) sources carry
  list-valued `domain`; zero string-valued or missing `domain` fields anywhere in the file.**
- Sector-value audit: VN sectors = {gov_agencies 7, customers 32, competitors 10, partners 7,
  general_news 4} (no `associations`); MY sectors = {gov_agencies 7, associations 3, customers 26,
  partners 10, competitors 8, general_news 1}. **No typo'd / out-of-vocabulary sector value in either
  block.**
- Report JSON join-key audit: `data/latest_report_VN_BER.json` — 43 signals, only **1** carries a
  `source_name` that matches a real `data_sources` name; 42 are `"Extracted signals"` (20) /
  `"extracted signals"` (22); all 3 opportunities carry `"Extracted signals"`.
  `data/latest_report_MY_GENERAL.json` — 9 signals, 3 match; junk values `"source not specified"`,
  `"source text"`, `"Extracted signals"`, `"Balai Seni Negara"` present; all 3 MY opportunities *do*
  carry real matching source names.
- Call-graph check (`grep`): `analyse(` is called once (`main.py:71`, `analyse(filtered, country)` — no
  domain); `_build_rag_context(` is **never called** anywhere in the repo (only its own definition +
  historical docs reference it).

## 1. Current-code data flow and gate consistency

| # | Area | File(s) | Finding | Severity | Optional fix task |
|---|------|---------|---------|----------|--------------------|
| 5 | `source_name` breakage root cause | `pipeline/analyst.py:174` (`_synthesize_sector`), context: `SECTOR_EXTRACT_PROMPT:44`, `SECTOR_SYNTHESIS_PROMPT:57`, `SUMMARY_PROMPT:75` | Synthesis user-message wraps unstructured extraction text under the literal label `"Extracted signals:"` with no enforced per-source delimiter; the model grabs that label as `source_name`. **42/43 VN signals + all 3 VN opportunities are unattributable to a real source.** Breaks the report's own "copy source_name verbatim" grounding claim. | **High** | none — needs judgment (prompt-engineering rework of `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT`), see 5. below |
| 3 | Keyword filter gate vs. opportunities gate | `pipeline/filter.py:4-10` (per-country config keywords) vs. `pipeline/analyst.py:75` (hardcoded global gate) | Real divergence, confirmed. Filter uses per-country lists; the opportunities gate is one static list applied to every country/domain. **Asymmetric by country:** VN's config keyword list contains *none* of the gate's cross-domain terms (retail/healthcare/hospital/manufacturing/factory/tourism/heritage), so filter.py is stricter than the gate for VN; MY's list contains all of them, so MY is broadly aligned. Enables a narrow EDU/non-BER leak into VN/BER reports. | **Medium** | none — needs judgment (sourcing gate from per-country config is a design change), see 3. below |
| 4 | RAG retrieval scoping | `pipeline/analyst.py:107` (`_build_rag_context`, dead), `:339` (`analyse` — no domain param), `:394-398` (`REPORT_HISTORY` write), `pipeline/vectorstore.py:42-47` (`query` `where`) | `analyse()` never receives `domain`; `REPORT_HISTORY` writes tag `{date, country}` only (no domain); `_build_rag_context()` is **dead code (never called)** and even its own query passes no `where` at all. **No active RAG leak today**, but the schema + query gaps are baked in and will bleed cross-country *and* cross-domain themes into every report the moment RAG is restored (planned at the Haiku switch), now that 8 domains + 3 countries share one collection. | **Medium** | none — needs judgment (architectural: prompt + RAG metadata schema + call sites), see 4. below |
| 1b | Domain fallback tuple inconsistency | `app.py:81-83` (`_domain_mode`, 8 domains) vs. `app.py:108-111` (`report()` fallback tuple, 3 domains) | `_domain_mode()` validates all 8 domains but the `any_domain_file_exists` guard only scans `("BER","EDU","GENERAL")`. A country whose only report(s) live in RCC/HLS/MFG/CTE/PSS would compute `any_domain_file_exists == False` and fall back to the legacy cross-country `latest_report.json`, mislabeling it. Dormant for *current* VN_BER / MY_GENERAL reports but a live correctness gap. | **Medium** | **Task 007** |
| 1a | Domain filtering operator fragility | `main.py:57-58` | `sources = [s for s in sources if domain_arg in s.get("domain", ["GENERAL"])]` is **correct for all current data** — every VN/MY/SG source has a list `domain`, so `in` is list-membership; the 4 VN BER+EDU dual-tagged sources correctly appear in both BER and EDU runs. Latent only: if a bare string `domain` ever appeared, `in` silently degrades to substring matching (safe today only because the 8 full domain codes have no substring collisions). | **Low / Informational** | none — latent, no current-data defect |
| 2 | Sector→label mapping | `pipeline/analyst.py:18-25` (`SECTOR_LABELS`), used at `:145,172,352,361` | **No issue found.** `SECTOR_LABELS` covers all 6 canonical sectors; every VN and MY source uses a canonical `sector` value (no typos), so the `.get(...)` fallback to a raw/title-cased label never fires for VN/MY. One cosmetic asymmetry: `analyse()`'s *print* fallback is `SECTOR_LABELS.get(sector_name, sector_name)` (no `.title()`) vs. `.replace("_"," ").title()` in the two call helpers — log-only, no data-flow impact. | **Informational** | none |

---

### Detailed writeups (items without a fix task)

#### 5. `source_name` breakage — code-level root cause (High)

This is the CODE-REVIEW.md counterpart to the symptom/impact finding documented in ACCURACY-AUDIT.md
(Tasks 003/004). ACCURACY-AUDIT.md records *that* VN signals cannot be traced to a source; this records
*why*, in the code.

**Mechanism.** The synthesis phase builds its user message at `pipeline/analyst.py:174`:

```python
user_message = f"Sector: {label}\n\nExtracted signals:\n{extraction_text}"
```

`SECTOR_SYNTHESIS_PROMPT` (`:48-59`) instructs the model to emit `"source_name": "name of source"` per
entry. But the only text the synthesis model sees is `extraction_text` — the free-form output of the
*extraction* phase — introduced by the literal words `"Extracted signals:"`. The extraction prompt
(`SECTOR_EXTRACT_PROMPT:44`) only says *"Format as a flat list grouped by source name"* with **no
machine-parseable delimiter** the synthesis step can rely on. Critically, the extraction phase's own
*input* is rigidly delimited — `_extract_sector()` builds `### {name}\nURL: {url}\n\n{content}` blocks
(`:151`) — but that structured input is consumed inside the extraction call and **never reaches the
synthesis call**; only the model's prose summary of it does. With no reliable per-source heading in that
prose, the synthesis model frequently latches onto the nearest salient label — the literal
`"Extracted signals"` header itself — and emits it as `source_name`.

**Live evidence (this worktree).** VN report: 42 of 43 signals carry `"Extracted signals"` /
`"extracted signals"`; the lone real value (`"Vietnam Investment Review"`) is the single General News
signal. All 3 VN opportunities carry `"Extracted signals"`. MY (a shorter, cleaner report) degrades less
but still emits `"source not specified"`, `"source text"`, `"Extracted signals"`, and `"Balai Seni
Negara"` (the Malay name for a real entity, but not the *configured* source name — still a lookup miss).

**Why the summary step is not the culprit.** `_synthesize_summary()` faithfully forwards each signal's
`source_name` into its input (`:222`, `f"- {entity} [source: {source_name}]: {signal}"`) and
`SUMMARY_PROMPT:75/97` tells opportunities to copy it verbatim. So opportunities are *correctly copying
an already-broken value*. The defect originates entirely in the extract→synthesize handoff, not in the
summary call — a fix must target the per-source format contract between `SECTOR_EXTRACT_PROMPT` and
`SECTOR_SYNTHESIS_PROMPT`.

**Flag, not a fix task.** Per CONTEXT.md's "no silent fixes" rule and the task brief, this needs
prompt-engineering judgment (e.g. force extraction output into a rigid `### {source_name}` structure and
have synthesis parse per-heading, or carry source identity structurally rather than in free text) — it
is not a one-line mechanical change. Candidate for a future `SECTOR_EXTRACT_PROMPT` /
`SECTOR_SYNTHESIS_PROMPT` rework that enforces a machine-parseable per-source format.

#### 3. Filter gate vs. opportunities gate — confirmed divergence + VN/MY asymmetry (Medium)

`pipeline/filter.py`'s `score_relevance()` (`:4-10`) scores scraped content against the **per-country**
`priority_keywords`/`keywords` lists loaded from `config/sources.json` (VN: 14+76, 90 unique lowercased;
MY: 15+99, 114 unique). `SUMMARY_PROMPT`'s OPPORTUNITIES gate (`pipeline/analyst.py:75`) is a single
**hardcoded, global** keyword list embedded in the prompt string, applied identically regardless of
country or domain. Commit `aea7783` (feature/005-domain-activation) broadened this gate to mirror MY's
`sources.json` vocabulary, but the implementation remains one static list, not sourced from config.

**Concrete asymmetry (measured this pass).** The global gate's cross-domain terms — `retail chain`,
`healthcare`, `hospital`, `manufacturing`, `factory`, `tourism`, `heritage trail` — are:
- **absent from VN's config keyword list** (VN is correctly BER-narrow: its active BER-only report has
  no retail/health/tourism/manufacturing vocabulary), yet the gate admits those terms unconditionally;
- **present in MY's config keyword list** (MY has active RCC 13 / HLS 4 / CTE 3 / MFG 2 domains, so its
  list legitimately carries retail/healthcare/tourism/manufacturing terms), so the same global gate is
  broadly aligned with MY.

Net: for **MY**, filter.py and the opportunities gate agree on scope; for **VN**, filter.py is *stricter*
than the opportunities gate. The two gates disagree about what is in-scope for a VN/BER report.

**Practical leak — narrow but real.** `main.py:57-58` domain-filters *sources* before scraping, so a
VN/BER run's raw material is already BER-scoped. However VN has **4** sources dual-tagged with EDU
(MOET, HUIT, Văn Lang University, Đa Minh Education — RESEARCH.md §3 said "2"; this worktree has 4, two
of them universities highly likely to emit EDU signals). Those sources are legitimately included in a
BER run (they carry `BER`), and any EDU-flavoured signal they surface can pass the global gate — which
already contains `edtech`, `virtual campus`, `STEM lab`, `e-learning` — into a report *labeled BER*.
More broadly, any non-BER signal riding in on a source that passed the BER keyword filter can clear the
looser global gate. This is a genuine cross-domain mislabel path, bounded today by how few dual-tagged
sources exist.

**Flag, not a fix task.** Aligning the opportunities gate with per-country/per-domain config (rather than
a global string) is a design decision, not a mechanical edit — deferred to judgment per RESEARCH.md §3.

#### 4. RAG retrieval scoping — dead today, latent cross-domain trap on restore (Medium)

Three facts, all verified in this worktree:

1. **`analyse()` takes no `domain`.** Signature is `analyse(filtered_results: list, country: dict)`
   (`:339`); `main.py:71` calls `analyse(filtered, country)` with `domain_arg` in scope but never passed.
   So nothing downstream of the pipeline entry point knows which domain it is producing a report for.
2. **`REPORT_HISTORY` writes are country-tagged only.** `:394-398` writes
   `metadatas=[{"date": ..., "country": country["code"]}]` — **no domain key**. VN, MY, and SG all write
   into the one shared `REPORT_HISTORY` collection, distinguishable by country but never by domain.
3. **`_build_rag_context()` is dead code.** Defined at `:107`, it is **not called** anywhere in
   `analyse()` or the repo (grep confirms only the definition + historical docs mention it). Moreover it
   would query with **no `where` filter at all** (`:123`, `query(collection_name, query_text,
   n_results=3)`) — not even country-scoped — even though `vectorstore.query()` supports `where`
   (`:42-47`).

**What this means for VN/MY, concretely.** *Today there is no RAG cross-domain leak*: no accumulated
context is prepended to any LLM call — `_synthesize_summary()`'s user message (`:225`) is purely the
structured signals. The "cross-domain past report themes" risk is therefore **dormant**, not active.

But the gap is structural and pre-loaded. DECISIONS.md records RAG restoration as planned for the Claude
Haiku production switch. If `_build_rag_context()` is switched back on *as written*, it will retrieve
"Past report themes" across **all countries and all 8 domains** into every report — a VN/BER run would
pull MY/RCC or SG/GENERAL themes — because (a) the query passes no `where` and (b) the stored documents
carry no `domain` to filter on even if one were added. With 8 domains now active and 3 countries sharing
one collection, this dormant blast radius is materially larger than when the function was cut
(SG-only, BER-only). The internals view (`app.py:138-147`) already reads `REPORT_HISTORY` unscoped, so
the mixed-provenance store is observable today, display-only.

**Flag, not a fix task.** RESEARCH.md lead 3 explicitly withholds a fix task: closing this touches prompt
content, the RAG metadata schema (add `domain`), *and* the `analyse()`/`main.py` call sites (thread
`domain` through) simultaneously — an architectural change requiring judgment, not a mechanical one-liner.

### Notes on items 1a / 1b / 2

- **1b (Task 007).** The `app.py` fallback-tuple inconsistency is real and confirmed against
  RESEARCH.md §4 lead 2 (introduced by commit `bb6fbd3`, which expanded `_domain_mode()` to 8 domains but
  left the tuple three lines away at 3). Fix is one-line/mechanical — do **not** apply it here; it is
  owned by **Task 007**. Worth recording that it is currently *masked* for the two generated reports
  (VN_BER, MY_GENERAL both fall inside the 3-domain tuple), so the bug does not corrupt today's output —
  it bites the first time a country's only report is in RCC/HLS/MFG/CTE/PSS.
- **1a.** No current-data defect (all `domain` fields are lists; no substring collisions among the 8
  codes). Recorded as latent fragility only, not given a fix task.
- **2.** No issue found — recorded per the task's "one entry per area even if clean" instruction.

## 2. Rapid-dispatch git history sample

Sampled all 27 commits across `feature/003-vietnam-country`, `feature/004-malaysia-country`, and
`feature/005-domain-activation` (full list: `RESEARCH.md` §6). 3 were already reviewed during planning
research (`b10537d`, `aea7783`, `bb6fbd3` — see RESEARCH.md §3-4 and section 1 above: `b10537d` is the
SUMMARY_PROMPT country-name fix `weekly.py` never got (Task 009 / finding 4); `aea7783` broadened the
global opportunities gate (finding 3); `bb6fbd3` is the introducing commit for the `app.py` domain-tuple
mismatch (finding 1b / Task 007)). This section covers the remaining **24**, all read-only via
`git show`/`git log`/`git blame`, zero LLM/Groq calls.

**feature/003-vietnam-country (11 commits):** `8771013` (country-aware routes) verified — all **3** routes
covered (report/internals/admin), fallback discipline mirrors `_domain_mode`, and it confirms the 3-domain
fallback tuple *predates* it (it only swapped `SG`→`{country}`; the tuple-vs-`_domain_mode` mismatch was
introduced later by `bb6fbd3`, consistent with RESEARCH.md §4). `f0be7e3` (feedback/weekly
country-scoping) is clean — the removed `count==0` guard was relocated to a correct `if not documents:`
check (`weekly.py:37`), `matched_files` move logic is right, and it **corroborates lead 4 / Task 009**:
it country-scoped retrieval + metadata but left `WEEKLY_PROMPT`'s hardcoded "Silversea Media (… Singapore)"
untouched. `060dad9` (UTF-8 stdout) minimal and correct. `07638b2`, `4202de0` reviewed (see finding rows
for `4202de0`; `975086a`/`519c772` also below). `86daa43`, `61881cb`, `585633e` are docs/`.context`-only,
no code impact. **Findings: `975086a`, `519c772`, `4202de0` (all Low/Informational).**

**feature/004-malaysia-country (7 commits):** near-mechanical mirrors of the VN work; the value here is
the VN-vs-MY consistency check. `89ce900` (MY sources.json) and `4012532` (MY fetcher tiering) each drift
from their VN counterparts (finding rows below). `b3a1bbc` (base.html) reworked the same block VN already
rewrote (finding row). `a90f5f2` (company_context MY subsection) is additive RAG-seed prose — content
accuracy is the ACCURACY-AUDIT track's concern, not code-correctness; diff shape is clean. `36d2530`,
`1f158ff` docs-only. `b1549d6` (merge) conflict-resolved `base.html`, `config/sources.json`,
`company_context.md` et al.; merged `sources.json` re-parses valid with all 3 country blocks intact (SG 62
/ VN 60 / MY 55 — section 1), so the conflict resolution was sound. **Findings: `89ce900`, `4012532`,
`b3a1bbc` (all Low/Informational).**

**feature/005-domain-activation (6 commits):** `e1505c9` (5 new domain tabs) correctly carry
`&country={{ _country }}`, preserving the country-preservation pattern. `4f174f4` (admin RCC/HLS/MFG/CTE/PSS
checkboxes) use the consistent `name="domain"` multi-checkbox convention. `4ec3052` de-flags 5
company_context headings, product text unchanged — the correct docs partner to `aea7783`'s prompt wiring.
`c9f6464` (retag 30 VN sources to real domains) is internally consistent (GENERAL preserved on every
source, dual-tag pattern followed); **context note, not a code bug:** it moves 30 VN sources off `BER`,
so the audited `latest_report_VN_BER.json` (generated pre-retag under blanket-BER tagging) is now stale
relative to config — a fresh VN/BER run would scrape far fewer sources. `bcdcfba`, `efe5125` docs-only.
**No code-correctness findings.**

| # | Commit(s) | Finding | Severity |
|---|-----------|---------|----------|
| G1 | `975086a` (VN sources.json) | **Message-vs-diff drift.** Message: VN keywords = "SG's lists minus SG-specific terms," naming 6 removals (GeBIZ, BCA Green Mark, Hiverlab, Gelement, TwinLogic, TwinMatrix). Diff removes exactly those 6 but the VN `keywords` list still carries many SG-specific entities — `smart nation`, `HDB estate`, `JTC`, `CapitaLand`, `Mapletree`, `Lendlease`, `Sembcorp`, `SJ Group`, and the full SG competitor roster. The "minus SG-specific terms" cleanup is only partial. Runtime harm is low (filter keywords can only *add* score when matched, and these SG terms rarely appear in VN content), but the VN filter carries irrelevant SG vocabulary. | Low |
| G2 | `89ce900` vs `975086a` (MY vs VN keyword derivation) | **Inconsistent pattern across the two country blocks.** VN stripped 6 SG-specific terms; MY reused SG's lists **verbatim** (message is accurate: "reuse SG's verbatim plus 18") — so MY retains `GeBIZ` **as a `priority_keyword` (3× weight)**, plus `BCA Green Mark`, `TwinMatrix`, etc. Two different philosophies applied to the identical task type by different dispatches. Concrete artifact: a Malaysian source mentioning Singapore's `GeBIZ` procurement portal gets 3× priority credit it shouldn't. Low real-world impact (GeBIZ ≈ absent from MY content), but the two blocks should have agreed on whether SG-specific terms belong. | Low |
| G3 | `4012532` vs `519c772` (MY vs VN fetcher tiering) | **Cosmetic convention drift, no functional effect.** VN places `inactive_reason` *after* the `domain` array and phrases reasons with an em-dash and "on all three fetcher tiers"; MY places `inactive_reason` *immediately after `active`* (before `domain`) and phrases with a hyphen and "across default, stealth, and dynamic fetchers." JSON key order is semantically irrelevant, so no bug — recorded only as evidence the two near-identical dispatches used different house styles. Both commits' active/stealth/inactive counts reconcile with their messages. | Informational |
| G4 | `4202de0` vs `b3a1bbc` (base.html country tabs) | **Parallel edits to identical lines → real merge conflict, resolved correctly.** Both commits rewrote the same country-tab block from the same base (`7eaaba4`), producing **different tab orderings** (VN branch: SG/**VN/MY**; MY branch: SG/**MY/VN**). `b3a1bbc`'s message claims it "reproduces Vietnam's already-decided final state exactly," but the ordering differs — a small message inaccuracy. Merge `b1549d6` conflict-resolved `base.html` to the MY ordering (SG/MY/VN, current state); functionally correct — all three are real `?country=` links with the right codes, ID inert. No functional defect; flagged as message-vs-actual drift + a merge-surface worth noting. | Informational |

**Net:** of the 24 newly-reviewed commits, **6 raised a finding** across 4 rows (G1 `975086a`, G2 `89ce900`
+`975086a`, G3 `519c772`+`4012532`, G4 `4202de0`+`b3a1bbc`) — all **Low or Informational**, none High/Medium.
No silently-introduced correctness bug was found in the sampled history: every commit's diff matched its
stated intent modulo the keyword-cleanup overstatement (G1) and the tab-ordering claim (G4), and the two
higher-risk pipeline commits (`8771013` routing, `f0be7e3` feedback/weekly scoping) are correct. The three
Medium/High findings in section 1 (`source_name` breakage, gate divergence, RAG scoping) all live in code
that **predates** this session's three features (see provenance below) — the rapid-dispatch work itself was
mechanically sound.

**`source_name` breakage provenance — it predates this session's 3 features (pre-existing latent bug,
newly exposed).** Hard git evidence: `_synthesize_sector()` and its `f"Sector: {label}\n\nExtracted
signals:\n{extraction_text}"` user-message construction (the root cause in section 1 finding 5) were
introduced in **`ebd90f6` (2026-06-29, "prototype #2 — per-sector synthesis")**; `SECTOR_EXTRACT_PROMPT`'s
loose "Format as a flat list grouped by source name" contract dates to **`59e4f52` (2026-06-23,
"multi-pass analyst")**. Both are **9-15 days older** than `feature/003-vietnam-country`'s first commit
(`86daa43`, 2026-07-08). Within this session's 27-commit range only `b10537d` and `aea7783` touched
`pipeline/analyst.py`, and **neither went near** the extract→synthesize handoff (`b10537d` = SUMMARY_PROMPT
country-name interpolation; `aea7783` = opportunities-gate broadening + product catalogs). Conclusion: this
is **not** a rapid-dispatch quality defect — it is a pre-existing SG-era latent bug that VN's larger, real,
multi-source content newly *exposed* (SG's smaller earlier reports masked it). That makes it a
**scope/testing-coverage failure**, arguably worse than a fresh dispatch bug: three `/feature-verify`
PASSes across features 003/004/005 all generated VN/MY reports without any step re-checking that signal
`source_name`s actually join back to real `data_sources` — so a report-breaking attribution defect shipped
through three consecutive green gates. Fixing it requires prompt-engineering judgment on the
`SECTOR_EXTRACT_PROMPT`↔`SECTOR_SYNTHESIS_PROMPT` per-source format contract (section 1 finding 5), not a
mechanical one-liner.
