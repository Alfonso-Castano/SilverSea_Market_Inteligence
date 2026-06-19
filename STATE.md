# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🟢 Phase 1 Complete — Phase 2 Planning Next

**Last updated:** 2026-06-19
**Last worked on:** Phase 1 full execution — rewrote analyst prompt (3 iterations, 12→13→21/25), restructured sources.py (25 sector-tagged sources with researched URLs), wired sector through scraper→filter→analyst, renamed workflow to daily, added semantic IDs and list wrapping to report HTML, researched LinkedIn scraping (deferred), ran quality reviews

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

## What's In Progress
- Nothing — Phase 1 complete, Phase 2 not yet started

## What's Next (Ordered)
1. **Phase 2 planning** — run `/phase` to create Phase 2 plan (AI Brain: ChromaDB, RAG, feedback loop)
2. Decide embedding model for vector store
3. Seed vector store with Silversea company context document
4. Build semantic deduplication step
5. Build feedback form + aggregation pipeline
6. Fix Construction Plus Asia SSL error (minor — can be done anytime)

---

## Current Blockers
- Real source lists (per sector) not yet received from supervisor — placeholders in use
- Partner source list entirely unknown — supervisor to provide
- Embedding model for Phase 2 vector store — decide at Phase 2 start

## Recent Decisions
- Analyst prompt uses grounding techniques: closed-book framing, quote-before-extract for opportunities, negative few-shot example, per-field abstain tokens (`NOT_FOUND_IN_SOURCE`)
- Content per source truncated to 800 chars in analyst (Groq free tier has 12k TPM limit with 18+ sources)
- LinkedIn scraping deferred — all free approaches blocked by LinkedIn's anti-bot measures or require auth
- 3 gov source URLs fixed after testing (HDB→root domain, Smart Nation→/initiatives, JTC→/about-jtc/news-and-stories)
- BCA domain migrated from www.bca.gov.sg to www1.bca.gov.sg

## Notes for Next Session
- Phase 1 is committed and verified. Start Phase 2 planning.
- The 800 char content limit is a Groq free tier constraint — will be lifted when switching to Claude Haiku in production (200k context)
- Quality review suggested adding a "Signals to Watch" subsection for near-miss items — consider for Phase 2 prompt refinement
