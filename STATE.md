# STATE.md — Current Project State

*Update this at the end of every session via /context-update.*

---

## Status: 🟢 Phase 3 Complete — Pipeline + Dashboard Verified End-to-End

**Last updated:** 2026-06-23
**Last worked on:** Executed full Phase 3 plan (`.claude/execution/phase3-dashboard.md`), Sessions 1-6. Modified `pipeline/analyst.py` (JSON output via Groq `response_format`), rewrote `pipeline/report.py` (thin JSON writer), updated `main.py` (run metadata capture, JSON-based scoring/email). Created `app.py` (Flask, 3 routes), `templates/base.html`, `templates/report.html`, `templates/internals.html`, `static/style.css` — the last two built by parallel subagents. Fixed a feedback-form Content-Type mismatch (JS sent JSON, Flask read form data) by making `/feedback` accept both. Ran the real pipeline twice: first with `llama-3.3-70b-versatile` (hit Groq's 100k TPD free-tier limit mid-run), then temporarily swapped to `llama-3.1-8b-instant` to verify the full scrape→filter→dedup→entities→analyse→score→JSON chain works end-to-end — it does, model restored to 70B afterward.

---

## What's Done
- [x] Full pipeline built and running end-to-end locally
- [x] Groq (Llama 3.3 70B) confirmed working on free tier (subject to 100k TPD limit)
- [x] `.claude/` directory configured: settings, custom commands, skills, execution guide
- [x] Context management system set up (CLAUDE.md, /context-update, /phase)
- [x] Full project scope defined: AI market intelligence system with RAG, feedback loop, web dashboard
- [x] All major architectural decisions locked (see CONTEXT.md)
- [x] **Phase 1:** Complete — sector-based pipeline, grounded analyst prompt, daily cadence
- [x] **Phase 2:** Complete — ChromaDB, RAG, dedup, entities, scoring, feedback loop, weekly summarizer
- [x] **Real Sources Finalization:** Complete — branding fix, 30 active real sources, feedback-loop demo verified
- [x] **Report Density Fix:** Multi-pass analyst architecture (per-sector extraction → synthesis), 8,000+ chars, 17/17 key signals present
- [x] **Phase 3:** Complete — analyst returns structured JSON, Flask dashboard (report + internals + feedback routes), both templates built and verified, full pipeline run confirmed end-to-end

## What's In Progress
- Nothing actively in progress — Phase 3 execution is functionally complete

## What's Next (Ordered)
1. **Get a real, full-quality report**: re-run `python main.py --no-email` with `llama-3.3-70b-versatile` once the Groq daily token quota resets (last hit ~10:00 UTC 2026-06-23)
2. **New session — visual design discussion**: separate "discuss" conversation to scope a visual redesign of the report page (animations, gradients, more "impressive" but not over-engineered) — decide what's possible without architecture changes vs. what requires changes, and which tooling to use (Alfonso is evaluating the `frontend-design` Claude plugin and other tools)
3. Delete `scripts/feedback_server.py` (superseded by `/feedback` route in `app.py`) — deferred, not yet confirmed with Alfonso
4. Fix Construction Plus Asia SSL certificate verification error (minor, anytime)
5. Re-evaluate inactive sources (SGTech, CPG Consultant, FacilityBot) if/when their URLs are fixed
6. Phase 4: weekly summary + Google Drive push + MY/VN/ID source expansion

---

## Current Blockers
- Groq free-tier daily token limit (100k TPD) — blocks getting a real 70B-quality report right now; resolves on its own within hours

## Recent Decisions
- Verified the JSON-output pipeline using a temporary swap to `llama-3.1-8b-instant` (separate rate-limit pool) purely to validate end-to-end wiring after the 70B model hit its daily quota; model reverted to `llama-3.3-70b-versatile` immediately after. That run's report data is real but low quality (8B model hallucinated an opportunity from a residential land tender, which the grounding rules are designed to block) — discard once a clean 70B run is available.
- `/feedback` route in `app.py` accepts both JSON (`request.get_json()`) and form-encoded bodies, and maps both `relevance_rating` and `relevance` field names — needed because the report template's `fetch()` posts JSON with field name `relevance`, while the original feedback server expected form-encoded `relevance_rating`.
- Adopting a two-chat workflow going forward: a "discuss" session to scope/decide architecture and produce a plan, and a separate "execute" session (clean context) that implements from that plan.

## Notes for Next Session
- If continuing pipeline work: just re-run `python main.py --no-email` once the Groq quota window has reset — no code changes needed, model is already back on 70B.
- A new "discuss" session is starting next to scope a visual redesign of the report page — see handoff prompt. It should evaluate the `frontend-design` Claude plugin and other tooling Alfonso brings, decide what's achievable within the current Flask + Jinja2 + Tailwind CDN + Chart.js stack vs. what requires architecture changes, then produce a plan for a future execute session.
- `data/latest_report.json` / `data/run_metadata.json` currently contain real but 8B-model-quality test data — fine for visual design discussions (data shape is correct), but should not be presented as a real report.
