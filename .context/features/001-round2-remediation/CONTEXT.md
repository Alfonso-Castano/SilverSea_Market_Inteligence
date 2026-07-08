# Feature: Round 2 Remediation

**Base:** 3dc471a831f05cb7955be8b22c205895976e0f84

## Goal

Finish and correct the "Supervisor Feedback Round 2" work committed as WIP in `3dc471a` — an independent Fable-model review (re-verifying, not trusting, both the executor's self-report and a prior independent handoff review) found the auth gate has a bypass, the live dashboard is currently serving stale pre-fix data, and the SpatioX→real-catalog rebuild is only partially done (the transcription is correct but everything downstream of it — prompts, gate keywords, Python post-processing, filter keywords — still runs on the old 4-product SpatioX/BER-only worldview).

## Scope

**In scope:**
- Fix the admin/viewer auth bypass (`app.py`) — empty `ADMIN_PASSWORD` + blank submit currently grants admin access; comparisons aren't constant-time.
- Fix the PDF-export afterprint bug (`static/animations.js`) — `#pdf-export-panel` loses its own `.print-exclude` class after first export.
- Finish the SpatioX→real-catalog rebuild consistently across `data/company_context.md` (3 remaining sections), `pipeline/analyst.py`'s `SUMMARY_PROMPT` system message, the opportunities gate keyword list, the `product_fit` instruction, and the two Python post-processing functions (`_generate_implications`, `_derive_competition_risks`). Real catalog = the 7-sector solution list in `docs/Copy of Business Sector _ed01.pdf` (verified accurate transcription already exists in `company_context.md`'s "Products by Business Sector" section — reuse it, don't re-derive it).
- Add EDU-relevant keywords to `config/sources.json`'s shared filter keyword list (merged list, not a schema change).
- Dual-tag NUS/NTU (or any other currently-BER source with genuinely EDU-relevant content) as `["BER","EDU"]` where it's not complex to do — a stopgap until the supervisor's real EDU source list arrives, not a full EDU source-list build-out.
- Re-seed ChromaDB's `COMPANY_CONTEXT` collection via the existing `scripts/seed_vectorstore.py` after the context rebuild lands.
- Add a country selector to the admin source-approval UI (`templates/admin.html`, `app.py`), and fix `source_suggestions.approve()` to re-read `sources.json` from disk instead of mutating the import-time `COUNTRIES` singleton.
- Add a first unit test (`tests/test_clamp.py`) for the opportunity-scoring clamp logic — zero LLM cost, closes the "unit-tested" gap the executor falsely claimed.
- Harden the unauthenticated `/feedback` route in `app.py` (surfaced by a broader pipeline recon pass, folded in since it's the same file as the auth-bypass fix and security-adjacent): (a) sanitize the `submitter` field before it's used in a filename — currently only spaces are replaced, so a value like `..\..\foo` can write JSON outside `data/feedback/`/`data/pending_sources/`; (b) wrap the `relevance_rating` int conversion so a non-numeric value returns a clean error instead of a 500; (c) scope CORS (`Access-Control-Allow-Origin: *`) to the `/feedback` route only, not every route in the app.

**Explicitly out of scope for this round:**
- Country-scoping `pipeline/weekly.py` and `pipeline/feedback.py` ChromaDB writes — deferred; no second country has real data yet to make the gap observable.
- Reinstating the lost "ecosystem entity taking a relevant action" second path on the opportunities gate — separate, previously-deferred decision; this round's gate fix is keyword-only (adds EDU terms alongside existing BER terms).
- A full real EDU source list — dual-tagging existing sources is a stopgap; the actual list is expected from the supervisor separately.
- Restoring `_build_rag_context()` / full RAG context in the summary call — deferred to the planned Claude Haiku production switch (200k context removes the current token-budget reason it was cut). This round's `product_fit` fix inlines a compact catalog directly into the prompt instead, as an interim fix.
- Running `py main.py` end-to-end — Groq daily-quota constraint means this is an **Alfonso-owned manual checkpoint**, not an executor task. Run only after all code-level tasks land, so the run reflects the fixes rather than reproducing the current stale/broken output.
- Visual QA of `login.html`/`admin.html` styling and actual browser print-preview testing — **Alfonso-owned manual checkpoint**; structural/Tailwind-class consistency can be checked in code, but pixels need eyes.
- Reviewing/resolving `config/sources.json`'s `_domain_tagging_status` draft flag (mechanical BER-default tagging) — unreviewed, pre-existing open item, not blocking this round's tasks, though T6 (country selector) touches the same file so drift should be watched.

## Implementation Decisions

- **Auth bypass fix** — refuse admin login when `ADMIN_PASSWORD` is unset/empty (check before comparing), use `hmac.compare_digest` for both admin and viewer password comparisons. Decided by: Claude's default judgment (security-correctness fix, not a design choice).
- **PDF afterprint fix** — either exclude `#pdf-export-panel` explicitly from the class-strip, or (cleaner) track only the elements the export flow itself toggled, mirroring the existing `expandedByUs` pattern. Decided by: Claude's default judgment; executor should pick whichever is less code.
- **SpatioX naming map** for the rebuild: Ops→Smart Facility Management System, Audit→Smart Virtual Inspection, Twin→Digital Twin, Walk→3D/VR Virtual Tour — per the Fable review's mapping. Decided by: Fable review's analysis, confirmed by user via this discussion.
- **EDU stopgap sourcing** — dual-tag existing sources (e.g. NUS/NTU) as `["BER","EDU"]` now where genuinely applicable and not complex; full EDU source list is a separate future delivery from the supervisor, not part of this round's scope. Decided by: user.
- **Filter keywords** — add EDU terms (edtech, e-learning, LMS, campus, STEM, virtual lab, etc.) directly into the existing shared per-country keyword list in `config/sources.json`; no per-domain keyword schema this round. Decided by: user.
- **Country-scoping of weekly/feedback writes (T8)** — deferred, not part of this round. Decided by: user.
- **Opportunities gate scope** — keyword-only widening (add EDU terms alongside existing BER terms); do NOT reinstate the separate lost "ecosystem entity action" path this round. Decided by: user.
- **Admin approval fixes** — bundle the country-selector UI addition and the `approve()` disk-reread fix together since both touch `pipeline/source_suggestions.py` in the same area. Decided by: Claude's default judgment (small, same-file, low-risk).
- **Test scope** — first-ever test file in the repo (`tests/test_clamp.py`, plain pytest), covering the scoring clamp only: out-of-range dims, negative/non-numeric values, missing dims, LLM-supplied bogus `total_score` overridden. Decided by: Claude's default judgment, matches Fable review's proposed cases.
- **`/feedback` hardening** — fold all three recon findings (submitter sanitization, relevance_rating crash guard, CORS scoping) in as one task alongside the auth-bypass fix rather than deferring any of them. Decided by: user.

## Global Constraints

- No `py main.py` runs during execution — Groq's 100k TPD free-tier quota must not be burned speculatively. Any task that would require an LLM call to verify must instead be verified via code inspection, unit-level exercise of pure-Python functions, or explicitly flagged as an Alfonso-owned manual checkpoint.
- `config/sources.json` is the source of truth for sources/keywords; `config/sources.py` is a thin loader only — don't reintroduce logic into `sources.py`.
- Two shared static passwords (viewer/admin) via Flask sessions remain the auth model — do not introduce per-user accounts while fixing the bypass.
- Flask + Jinja2 + Tailwind/Chart.js via CDN, no SPA, no build step — any UI change (admin country selector, etc.) must stay within this stack.
- `data/company_context.md` is the RAG seed doc — any content change there requires a `scripts/seed_vectorstore.py` re-run to actually take effect (ChromaDB doesn't re-read the file on its own).
- Sector (`gov_agencies`/`associations`/`customers`/`partners`/`competitors`/`general_news`) and domain (`BER`/`EDU`/`GENERAL`) are orthogonal per-source fields — don't conflate them when dual-tagging sources for EDU.
- Minimal impact / no drive-by refactors — this is a remediation pass on a specific, enumerated set of gaps; don't touch adjacent working code (e.g. the confirmed-working auth route-gating logic, the sources.json migration mechanics, the domain/country CLI plumbing) beyond what's listed above.

## Open Questions

- `config/sources.json`'s `_domain_tagging_status` draft flag (mechanical BER-default domain tagging) remains unreviewed by Alfonso — flagged, not part of this round, but the admin-approval changes (T6) touch the same file, so watch for drift.
- Minor bookkeeping mismatch: live active source count is 57, not the 54 recorded in ROADMAP.md — worth a one-line ROADMAP correction whenever `/update-context` next runs, not a task in this feature.
- `ADMIN_PASSWORD` still needs to actually be set in Alfonso's local `.env` even after the bypass fix — the fix makes the unset case *safe* (refuses login), not *functional* (admin still won't be able to log in until the var is set).

## Deferred — Future Pipeline-Polish Round (not part of 001, logged from a broader recon pass)

None of these block or belong in this feature. Surfaced by a pipeline-wide health scan run alongside this discussion, explicitly out of scope here per user decision — revisit via a future `/feature-discuss` on general pipeline polish:

- **No LLM rate limiter exists**, despite a 2026-06-19 decision recording "hard rate limit on LLM calls per run and per day... logs a breach and exits cleanly" — no such mechanism found in `pipeline/analyst.py`, `pipeline/feedback.py`, or `pipeline/weekly.py`. Likely lost during the dead-code removal pass (`scoring.py` etc.) or never actually built. Docs-vs-code inconsistency worth a DECISIONS.md correction too.
- **`sentence-transformers` is a direct, explicit dependency, not transitive** — `pipeline/vectorstore.py:14-16` explicitly instantiates `SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")`. STATE.md's current wording ("appears to still require it transitively") is factually wrong and should be corrected at the next `/update-context`.
- **Email digest likely renders blank** — `main.py`'s `send_digest(email_text, "", ...)` call puts an empty HTML part last in a `multipart/alternative` message; most mail clients prefer the last alternative. Non-fatal, legacy Phase-1 feature.
- **`run_metadata.json` isn't domain/country-scoped** — in a multi-country run, only the last country's metadata survives, unlike report files. Harmless today (SG-only), becomes relevant once Phase 4 multi-country is real.
- **`weekly.py`'s ChromaDB retrieval is order-unstable and doesn't guard against re-compressing an already-weekly-summarized doc** — `collection.get(limit=...)` has no ordering guarantee, so recent dailies could be silently missed once `REPORT_HISTORY` exceeds ~14 docs. Related to the already-deferred country-scoping gap (T8) — worth revisiting together.
- **`pipeline/analyst.py` crashes with `KeyError` if `GROQ_API_KEY` is unset**, unlike the graceful-skip pattern used in `feedback.py`/`weekly.py`. Low real-world risk since the key is always set in practice, but inconsistent with the rest of the codebase's pattern.
- **Dead code**: `scripts/feedback_server.py` still on disk despite DECISIONS.md recording its consolidation into `app.py` back in 2026-06-23. Trivial to delete, just out of this round's minimal-impact scope.
