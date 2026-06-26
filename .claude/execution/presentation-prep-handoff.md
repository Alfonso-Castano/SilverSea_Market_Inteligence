# Presentation Prep — Execution Handoff

Copy-paste everything below the line into a fresh Claude Code session.

---

## Context

You are working at `C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence` — an AI market
intelligence pipeline for Silversea Media. It scrapes ~30 Singapore built-environment sources,
filters/deduplicates them, runs them through an LLM analyst (Groq Llama 3.3 70B), and produces
a structured JSON report served by a Flask dashboard at `localhost:5000`. The system has a
RAG-based feedback loop: user feedback → LLM-summarised digest → stored in ChromaDB vector
store → retrieved as context on the next pipeline run, shaping what the analyst emphasizes.

**Alfonso is presenting this to his supervisor today.** He needs two versions of the report
ready to demo side-by-side:
1. A **clean report** — no feedback influence, no prior report history in the vector store.
   Shows the baseline intelligence output.
2. A **feedback-influenced report** — after realistic feedback is submitted and aggregated,
   showing the system learned and adjusted priorities. Proves the feedback loop works.

Both must be accessible at `localhost:5000` without re-running the pipeline during the demo.

Read `CLAUDE.md` first — it auto-imports `STATE.md`, `CONTEXT.md`, `ROADMAP.md`, `PLAN.md`.

## The Problem

The current `data/latest_report.json` contains low-quality test data from an 8B model run —
it's unusable for a demo. We need two fresh, full-quality 70B reports and a way to toggle
between them in the browser.

## Files Involved

- `main.py` — pipeline orchestrator. Run with `py main.py --no-email`. Calls
  `aggregate_feedback()` at the top (processes any JSON in `data/feedback/`), then scrapes →
  filters → deduplicates → extracts entities → analyses → saves `data/latest_report.json`
  and `data/run_metadata.json`.
- `app.py` — Flask server. `GET /` reads `data/latest_report.json`, `GET /internals` reads
  metadata + ChromaDB, `POST /feedback` saves JSON to `data/feedback/`.
- `pipeline/vectorstore.py` — ChromaDB wrapper. Collections: `company_context` (seed doc —
  **DO NOT DELETE**), `report_history`, `feedback_digests`. Persistent at `data/chromadb/`.
  Key functions: `get_collection(name)`, `add_documents(...)`, `delete_documents(...)`.
- `pipeline/feedback.py` — `aggregate_feedback()`: reads `data/feedback/*.json`, LLM-
  summarises them, stores digest in `feedback_digests` collection, moves originals to
  `data/feedback/processed/`.
- `data/feedback/` — unprocessed feedback JSON files (consumed by `aggregate_feedback()`).
- `data/feedback/processed/` — already-aggregated feedback files.
- `templates/report.html`, `templates/base.html`, `templates/internals.html` — Jinja2
  templates. Recently revamped with dark glass hero, sticky nav, animations. Do not change
  the visual design — only add the demo toggle mechanism.
- `static/style.css`, `static/animations.js` — CSS/JS assets. Do not change.

## What to Do

### Phase 1: Clean Slate

1. **Delete all feedback files:**
   - Remove everything in `data/feedback/` (both raw and `processed/` subfolder).
2. **Clear ChromaDB collections** (keep `company_context` intact):
   - Write and run a small Python script that uses `pipeline/vectorstore` to clear
     `report_history` and `feedback_digests`. Approach: get the collection, call
     `col.get()` to get all IDs, then `col.delete(ids=...)`. Or delete and recreate the
     collection via `get_client().delete_collection(name)` then
     `get_client().get_or_create_collection(name, embedding_function=...)` — but be
     careful to re-import the embedding function from `pipeline/vectorstore`.
   - **CRITICAL: Do NOT touch `company_context`.** It contains the Silversea product/company
     seed document the analyst needs.
3. **Discard current test data:** Delete `data/latest_report.json` and
   `data/run_metadata.json` — they're from an 8B model test run.

### Phase 2: Clean Pipeline Run (no feedback)

4. **Run the pipeline:** `py main.py --no-email`
   - This will call `aggregate_feedback()` first — since you cleared `data/feedback/`, it
     will find nothing and skip. Good.
   - Uses Groq Llama 3.3 70B (`llama-3.3-70b-versatile`). Groq free tier has a 100k
     tokens/day limit — the last quota hit was ~10:00 UTC on 2026-06-23, it should be
     fully reset by now. If you get a rate limit error, wait and retry.
   - Runtime: ~3 minutes (multi-pass analyst makes ~6 Groq calls with 25s delays between
     them for TPM compliance).

5. **Verify the clean report:**
   - Read `data/latest_report.json`. Check:
     - `executive_summary`: are bullet points grounded in real Singapore built-environment
       news? No fabricated events.
     - `signals_by_sector`: do sectors (Gov Agencies, Associations, Customers, Partners,
       Competitors) contain signals referencing real companies from the source list?
     - `opportunities`: each must have `title`, `total_score` (1-25), `source_quote`
       (verbatim from a real source), `concrete_action`, `product_fit`. Product names MUST
       be one of: **SpatioX Twin, SpatioX Ops, SpatioX Audit, SpatioX Walk**. NOT
       "MetaTwin" anything. Scores should have sub-scores (strategic_fit, revenue_potential,
       win_probability, urgency, intelligence_quality — each 1-5).
     - `synthesis`: grounded strategic takeaways, not generic filler.
   - If anything looks hallucinated or references wrong product names, flag it — do NOT
     silently proceed.

6. **Save the clean report:**
   ```
   mkdir data\presentation
   copy data\latest_report.json data\presentation\clean_report.json
   copy data\run_metadata.json data\presentation\clean_metadata.json
   ```

7. **Start Flask and verify rendering:**
   - `py app.py` (run in background)
   - Fetch `http://localhost:5000/` — should render the dark gradient hero, glass stat cards
     with real numbers (count-up animation), sector cards, opportunity cards sorted by score
     (top 3 expanded if >3 exist), executive summary, synthesis, feedback form.
   - Fetch `http://localhost:5000/internals` — should show real run metadata numbers, source
     scores chart, vector store browser (company_context populated, report_history and
     feedback_digests empty).
   - Confirm no console/template errors.

### Phase 3: Feedback-Influenced Pipeline Run

8. **Submit realistic example feedback:**
   Post 2-3 feedback submissions via the `/feedback` endpoint that reference real content
   from the clean report. Make them sound like a BD team member who read the report:
   - One submission rating relevance 4-5, highlighting a specific opportunity as most useful,
     asking for more coverage of a specific sector or topic.
   - One submission rating relevance 3, noting a missed topic (e.g., "We're also tracking
     [specific competitor] — would like to see their moves covered" or "Missing coverage of
     upcoming government tender deadlines").
   - One submission requesting a priority shift (e.g., "Weight the Partners sector higher —
     we have active conversations with [partner from the report]").
   
   Use real names/signals/opportunities from the clean report you just verified — don't
   invent feedback about things that weren't in the report.

   POST to `http://localhost:5000/feedback` with `Content-Type: application/json`:
   ```json
   {
     "relevance": "4",
     "most_useful": "...",
     "missed_topics": "...",
     "priority_changes": "...",
     "submitter": "BD Team Member",
     "report_date": "2026-06-24"
   }
   ```

9. **Stop the Flask server** (it will be restarted after the second run).

10. **Run the pipeline again:** `py main.py --no-email`
    - This time, `aggregate_feedback()` WILL find the JSON files you just submitted, LLM-
      summarise them into a digest, and store that digest in ChromaDB's `feedback_digests`
      collection. The analyst will then retrieve this digest as RAG context, which should
      influence the report.

11. **Verify the feedback-influenced report:**
    - Read `data/latest_report.json`. Compare against the clean report:
      - The feedback should have measurably changed something — different emphasis in the
        executive summary, adjusted opportunity scoring or new opportunities surfaced, the
        sector/topic the feedback asked about getting more prominence.
      - If the two reports are identical or nearly so, investigate why the feedback didn't
        influence the output (check if the digest was actually stored in ChromaDB, check if
        the analyst's RAG retrieval is working).

12. **Save the feedback report:**
    ```
    copy data\latest_report.json data\presentation\feedback_report.json
    copy data\run_metadata.json data\presentation\feedback_metadata.json
    ```

### Phase 4: Presentation Toggle

13. **Modify `app.py`** to support a `?demo=` query parameter on the report route:
    - `localhost:5000/` (no param, or `?demo=clean`) → reads
      `data/presentation/clean_report.json` and `data/presentation/clean_metadata.json`
    - `localhost:5000/?demo=feedback` → reads `data/presentation/feedback_report.json` and
      `data/presentation/feedback_metadata.json`
    - The internals page should also respect this toggle for run metadata display.
    - Add a small visual indicator so Alfonso knows which version he's viewing — e.g., a
      subtle pill/badge in the hero section showing "Clean Run" or "With Feedback" in
      `text-gray-400` text. Keep it minimal — this is a demo aid, not a feature.
    - **Do NOT change:** the `/feedback` POST route behavior, the template visual design
      (dark hero, glass cards, animations, opportunity structure), or any pipeline file.

14. **Restart Flask** and verify both versions render correctly at their respective URLs.

### Phase 5: Final Verification

15. Check the full verification list:
    - [ ] `localhost:5000/` shows clean report with real, accurate, grounded data
    - [ ] `localhost:5000/?demo=feedback` shows feedback-influenced report with visible
          differences from the clean version
    - [ ] Both versions: dark gradient hero, glass stat cards animate, sticky nav works,
          sector cards render, opportunities render with score badges and breakdowns
    - [ ] Both versions: no hallucinated companies, no wrong product names, no invented
          deadlines, scores are reasonable (not all 25s, not all 5s)
    - [ ] Internals page (`/internals`) renders with real data — source scores chart, vector
          store browser shows company_context + feedback_digests content
    - [ ] The demo toggle indicator is visible so Alfonso knows which version he's showing
    - [ ] No console errors, no template errors, pages load quickly

## Constraints

- **Use `py` not `python`** as the command — Windows py launcher.
- **Do NOT change any pipeline Python files:** `analyst.py`, `report.py`, `filter.py`,
  `scraper.py`, `dedup.py`, `entities.py`, `scoring.py`, `feedback.py`, `vectorstore.py`,
  `emailer.py`.
- **Do NOT change templates' visual design** — the dark hero, glass cards, animations, sticky
  nav, opportunity structure were just revamped in Phase 3.5. Only add the demo toggle
  indicator.
- **Do NOT change the feedback form's field names or POST behavior.**
- **Keep `company_context` collection intact** — only clear `report_history` and
  `feedback_digests`.
- Groq rate limits: 12k tokens/minute, 100k tokens/day on free tier. If you hit a limit,
  wait and retry — don't switch models.
- Silversea's products: **SpatioX Twin, SpatioX Ops, SpatioX Audit, SpatioX Walk**. If the
  report says "MetaTwin" anything, that's a bug in the analyst prompt — flag it.

## Verification

The presentation is ready when Alfonso can:
1. Open `localhost:5000/` → see a polished, accurate, real-data market intelligence report
2. Open `localhost:5000/?demo=feedback` → see a visibly different report shaped by team
   feedback
3. Switch between them live during the demo to show "before feedback" vs "after feedback"
4. Open `localhost:5000/internals` → show the AI system internals (source scores, vector
   store contents, feedback digests) as proof the system is real and working
