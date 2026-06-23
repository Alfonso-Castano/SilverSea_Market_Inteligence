# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🟡 Report Density Improvement — Testing Complete, Pending Review

**Last updated:** 2026-06-23
**Last worked on:** Rewrote `pipeline/analyst.py` from single-call to multi-pass architecture (per-sector extraction → synthesis). Also ran info-gap analysis comparing raw scraped data vs report output, identifying that ~75% of actionable signals were being dropped. The multi-pass rewrite plus improved synthesis prompt increased report size from ~4,600 chars → ~8,000 chars (73% increase) and signal coverage from ~25% to near-complete (17/17 key signals now present). Committed prototype 1 earlier in session. Multi-pass changes not yet committed.

---

## What's Done
- [x] Full pipeline built and running end-to-end locally
- [x] Groq (Llama 3.3 70B) confirmed working on free tier
- [x] `.claude/` directory configured: settings, custom commands, skills, execution guide
- [x] Context management system set up (CLAUDE.md, /context-update, /phase)
- [x] Full project scope defined: AI market intelligence system with RAG, feedback loop, web dashboard
- [x] All major architectural decisions locked (see CONTEXT.md)
- [x] **Phase 1:** Complete — sector-based pipeline, grounded analyst prompt, daily cadence
- [x] **Phase 2:** Complete — ChromaDB, RAG, dedup, entities, scoring, feedback loop, weekly summarizer
- [x] **Real Sources Finalization:** Complete — branding fix, 30 active real sources, feedback-loop demo verified
- [x] **Report Density — Info Gap Analysis:** Sub-agent analysed raw scraped data vs report output; found ~75% signal loss concentrated in LLM dropping entire sectors (competitors, partners) plus 800-char truncation
- [x] **Report Density — Multi-Pass Analyst:** Rewrote `pipeline/analyst.py` — Phase 1 extracts signals per sector (full content, no truncation), Phase 2 synthesizes into final report. 25s delay between calls for Groq TPM compliance.
- [x] **Report Density — Verification:** Report now 8,019 chars with all key signals present: G Element (5 MOUs: CLIXLogic, Daikin, Savills FM, SUTD, RoviSys), DataMesh (Yokogawa, NVIDIA, FactVerse AI Agent, Gartner), AECOM, JTC Punggol, SGBC

## What's In Progress
- Alfonso reviewing report quality to decide if density is sufficient or needs more work

## What's Next (Ordered)
1. Alfonso reviews `output/index.html` — confirm report density is good enough or identify remaining gaps
2. If approved: commit multi-pass analyst changes, update context files
3. Phase 3 planning (web dashboard) — two surfaces: polished report view + AI-system internals/observability page
4. Full source rollout (remaining ~25 sources) — Phase 4
5. MY/VN/ID country expansion — Phase 4

---

## Current Blockers
- None — awaiting Alfonso's review of report quality

## Recent Decisions
- Multi-pass analyst architecture: per-sector LLM extraction (no truncation, full content) → synthesis call. ~3 min runtime due to Groq rate limiting (25s between calls). Trade-off accepted for dramatically better information density.
- Raised synthesis max_tokens from 4096 → 6000 since extraction outputs are compact (~1000 chars/sector), leaving TPM budget for longer output
- TwinLogic and Axomem return page shells (JS-rendered) — their content can't be scraped without Firecrawl. Known limitation, not fixable in current architecture.

## Notes for Next Session
- Read the handoff prompt Alfonso was given: review `output/index.html`, confirm density, commit if approved, then Phase 3.
- `pipeline/analyst.py` changes are NOT committed yet — only prototype 1 was pushed. Need to commit the multi-pass rewrite.
- The `output/baseline_no_feedback.html` from the earlier session is still available for comparison if needed.
