# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🟡 Real Sources Finalization — Planned, Execution Pending

**Last updated:** 2026-06-23
**Last worked on:** Supervisor provided the real Built Environment ecosystem source list (PDF: government agencies, owners, main contractors, consultants, M&E/BMS integrators, facility management firms, competitors). Reviewed it against `config/sources.py` and `pipeline/analyst.py`, discovered a branding bug — the analyst SYSTEM_PROMPT describes Silversea's products as "MetaTwin Object/Space/Immerse/Augment," which is wrong; the real products are SpatioX Twin/Ops/Audit/Walk. Locked a prioritized ~24-source subset (mapped into the existing 5 sectors, no new sectors) for a presentation-ready prototype, and wrote a full execution guide at `.claude/execution/real-sources-prototype.md` covering: branding fix, source URL research + config update, dry-run scrape verification, clearing Phase 2 test-only ChromaDB/feedback data, and a baseline-vs-feedback report diff to prove the RAG/feedback loop has a measurable effect. **No code changes made this session — planning only.**

---

## What's Done
- [x] Full pipeline built and running end-to-end locally (scraper, filter, analyst, report, emailer, main.py)
- [x] 24/25 sources attempted (23 OK, 1 SSL failure: Construction Plus Asia), 18 pass keyword filtering
- [x] Groq (Llama 3.3 70B) confirmed working on free tier
- [x] Quality reviews: 12/25 (2026-06-16) → 13/25 (2026-06-19 v1) → 21/25 (2026-06-19 v2)
- [x] `.claude/` directory configured: settings, custom commands, skills, execution guide
- [x] Context management system set up (CLAUDE.md, /context-update, /phase)
- [x] Full project scope defined: AI market intelligence system with RAG, feedback loop, web dashboard
- [x] ROADMAP.md created: 4-phase plan mapped
- [x] PROJECT_REQUIREMENTS.md fully rewritten to reflect new scope (2026-06-19)
- [x] All major architectural decisions locked (see CONTEXT.md)
- [x] **Phase 1 Task 1:** Analyst SYSTEM_PROMPT rewritten with grounding constraints (closed-book framing, quote-before-extract, negative few-shot, explicit abstain tokens)
- [x] **Phase 1 Task 2:** config/sources.py restructured — 25 sources across 6 sectors with researched newsroom URLs
- [x] **Phase 1 Task 3:** Sector field wired end-to-end through scraper → filter → analyst (grouped by sector in LLM prompt)
- [x] **Phase 1 Task 4:** LinkedIn scraping researched and deferred — no free no-auth method viable
- [x] **Phase 1 Task 5:** GitHub Actions workflow renamed weekly→daily, cron set to `0 1 * * *`
- [x] **Phase 1 Task 6:** Report HTML cleanup — semantic IDs on headings, list items wrapped in `<ul>` tags
- [x] **Phase 2 Task 1:** ChromaDB vector store set up (`pipeline/vectorstore.py`), 3 collections: company_context, report_history, feedback_digests
- [x] **Phase 2 Task 2:** Company context seeded — `data/company_context.md` + `scripts/seed_vectorstore.py`, 23 chunks
- [x] **Phase 2 Task 3:** Semantic deduplication (`pipeline/dedup.py`) — embedding cosine similarity >0.85 merge
- [x] **Phase 2 Task 4:** Named entity extraction (`pipeline/entities.py`) — regex-based, no LLM calls
- [x] **Phase 2 Task 5:** RAG-enhanced analyst (`pipeline/analyst.py`) — retrieves context into user message, SYSTEM_PROMPT untouched
- [x] **Phase 2 Task 6:** Source quality scoring (`pipeline/scoring.py`) — JSON-persisted, cited/uncited tracking
- [x] **Phase 2 Task 7:** Feedback form embedded in report HTML + `scripts/feedback_server.py` (Flask, port 5050)
- [x] **Phase 2 Task 8:** Feedback aggregation (`pipeline/feedback.py`) — LLM-summarized digest into vector store
- [x] **Phase 2 Task 9:** Weekly summarizer (`pipeline/weekly.py`) + `.github/workflows/weekly_summary.yml` — Google Drive export deferred

## What's In Progress
- Nothing actively being coded — execution guide is written and ready; next session executes it end-to-end (target: manager presentation 2026-06-24)

## What's Next (Ordered)
1. Execute `.claude/execution/real-sources-prototype.md` Session 1 — fix MetaTwin→SpatioX branding bug in `pipeline/analyst.py`
2. Session 2 — research real newsroom/press URLs for 10 new sources (sub-agent candidate)
3. Session 3 — update `config/sources.py` with ~24 real sources across existing 5 sectors
4. Sessions 4–8 — dry-run scrape verify, clear test ChromaDB/feedback data, baseline run, inject real feedback, second run + diff to prove RAG loop works
5. After execution: `/context-update` again to record what was actually done
6. Phase 3 (web dashboard) planning — picked up in a separate chat, after backend/sources are finalized

---

## Current Blockers
- None — supervisor's real source list received and reviewed; full rollout (remaining ~25 sources, MY/VN/ID) still deferred to Phase 4 but that's expected, not a blocker for tomorrow's prototype

## Recent Decisions
- Prioritized ~24-source subset locked for tomorrow's presentation rather than attempting all ~50 PDF sources — newsroom URL discovery is the slow part, not code; full list deferred to Phase 4 (see CONTEXT.md)
- `partners` sector (previously an inactive placeholder) now gets real sources: AECOM, CPG Consultant, Honeywell, Cushman & Wakefield — consultants/M&E integrators/FM firms treated as channel partners
- Dropped TwinMatrix from competitors in favor of FacilityBot and Cryotos — more directly competitive on smart FM
- LinkedIn/Facebook source URLs requested by supervisor explicitly skipped again for this round (LinkedIn scraping already ruled out infeasible; Facebook has the same risk profile) — noted as future work
- Test-only ChromaDB feedback/report-history data (from Phase 2 verification) will be cleared before the real feedback-loop demo so the before/after diff is attributable to real injected feedback, not stale test data

## Notes for Next Session
- Read `.claude/execution/real-sources-prototype.md` in full before starting — it is the complete plan, sessions are sequential where noted, don't re-derive decisions already locked there.
- `pipeline/analyst.py`'s MetaTwin branding bug must be fixed regardless of anything else — it's currently factually wrong in every generated report.
- `data/chromadb/`, `data/feedback/`, and `data/source_scores.json` are gitignored (local/runtime state, not committed) — clearing them is safe and won't affect git history.
