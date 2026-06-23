# PLAN.md — Current Phase Plan

*Active plan for the phase currently in progress. Overwritten at the start of each new phase.*
*Task status updated by /context-update. Full phase history lives in ROADMAP.md.*

---

## Phase 2 — AI Brain

**Goal:** System learns and improves from user feedback over time. RAG-enhanced analyst retrieves accumulated context. Feedback submitted on Day 1 measurably changes what the report surfaces on Day 7.

**Done when:**
- ChromaDB seeded with company context, pipeline retrieves relevant context at inference time
- Semantic deduplication reduces noise, named entities extracted as metadata
- Feedback form in report → aggregation → digest in vector store → influences next run
- Weekly summarizer compresses 7 daily reports into one summary

---

## Tasks

### 1. Embedding model + ChromaDB setup `[DONE]`
Choose embedding model and initialize ChromaDB infrastructure.

**Decision:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim, fast, free, local, no API key).
Rationale: runs on CPU, ~80MB model, good retrieval quality for short documents, widely used.

**Implementation:**
- `requirements.txt` — add `chromadb`, `sentence-transformers`
- `pipeline/vectorstore.py` — new module: init ChromaDB client (persistent storage in `data/chromadb/`), collection management, add/query helpers
- Collections: `company_context`, `report_history`, `feedback_digests`

**Verify:** `python -c "from pipeline.vectorstore import get_collection; print(get_collection('company_context'))"` runs without error.

Files: `pipeline/vectorstore.py` (new), `requirements.txt`

---

### 2. Seed vector store with company context `[DONE]`
Create Silversea company context document and ingest into ChromaDB.

**Implementation:**
- `data/company_context.md` — structured document: products, target sectors, key prospects, competitive positioning, priorities
- `scripts/seed_vectorstore.py` — reads company context, chunks it, embeds, stores in `company_context` collection
- Chunking: split by section headers, ~300-500 chars per chunk

**Verify:** Query "digital twin smart building" returns relevant company context chunks.

Files: `data/company_context.md` (new), `scripts/seed_vectorstore.py` (new)

---

### 3. Semantic deduplication `[DONE]`
Pre-analyst step: merge same-story signals that appear across multiple sources.

**Implementation:**
- `pipeline/dedup.py` — new module
- Embed each filtered result's content (title + first 300 chars)
- Cosine similarity > 0.85 threshold → merge into one entry, note all source URLs
- Runs after `filter.py`, before `analyst.py`
- Merged entries carry `sources: [url1, url2, ...]` instead of single `url`

**Verify:** Run pipeline with known duplicate content across sources → dedup reduces count.

Files: `pipeline/dedup.py` (new), `main.py` (insert dedup step)

---

### 4. Named entity extraction `[DONE]`
Pre-analyst step: extract structured metadata from each signal.

**Implementation:**
- `pipeline/entities.py` — new module
- Extract: company names, dollar amounts, dates/deadlines, tender/reference numbers
- Regex-based + simple heuristics (not LLM — saves tokens)
- Output: adds `entities` dict to each filtered result
- Entities stored alongside report in ChromaDB for future retrieval

**Verify:** Run pipeline → filtered results contain `entities` field with extracted values.

Files: `pipeline/entities.py` (new), `main.py` (insert entity step)

---

### 5. RAG-enhanced analyst `[DONE]`
Modify analyst to retrieve relevant context from vector store at inference time.

**Implementation:**
- Before LLM call: query `company_context` + `feedback_digests` + `report_history` collections
- Use top signal keywords as query → retrieve top 3-5 relevant chunks
- Inject retrieved context into the USER message (not system prompt) as a new section:
  ```
  ACCUMULATED CONTEXT (from past reports and feedback):
  - [chunk 1]
  - [chunk 2]
  ```
- Do NOT modify SYSTEM_PROMPT grounding constraints
- After LLM call: store today's report summary in `report_history` collection

**Verify:** Run pipeline → report references context that only exists in vector store (not in scraped sources).

Files: `pipeline/analyst.py` (modify `analyse` function), `pipeline/vectorstore.py`

---

### 6. Source quality scoring `[DONE]`
Passive scoring: track which sources produce signals that end up in the report.

**Implementation:**
- `pipeline/scoring.py` — new module
- After analyst runs: compare which source URLs are cited in the report
- Increment score for cited sources, decay score for sources that pass filter but aren't cited
- Store scores in `data/source_scores.json` (simple JSON, not ChromaDB)
- Log scores per run to stdout

**Verify:** Run pipeline twice → `data/source_scores.json` exists with per-source scores.

Files: `pipeline/scoring.py` (new), `main.py` (insert scoring step), `data/source_scores.json` (generated)

---

### 7. Feedback form `[DONE]`
Embed a feedback form at the bottom of the HTML report.

**Implementation:**
- Add HTML form to `report.py` output (after report content)
- Fields: relevance rating (1-5), most useful signal (text), missed topic (text), priority change (text), submitter name (optional)
- Form submits to a simple endpoint (Phase 3 will host properly; for now, write to `data/feedback/` as JSON files via a minimal local Flask endpoint OR use a free form backend like Formspree)
- No authentication required

**Decision:** Use `scripts/feedback_server.py` — minimal Flask app that accepts POST and writes JSON to `data/feedback/`. Runs alongside pipeline on company server.

**Verify:** Submit form in browser → JSON file appears in `data/feedback/`.

Files: `pipeline/report.py` (modify), `scripts/feedback_server.py` (new), `data/feedback/` (directory)

---

### 8. Feedback aggregation pipeline `[DONE]`
Collect feedback submissions, LLM-summarize, store digest in vector store.

**Implementation:**
- `pipeline/feedback.py` — new module
- Reads all JSON files in `data/feedback/` since last aggregation
- Sends batch to LLM with prompt: "Summarize this team feedback into a concise priority digest"
- Stores resulting digest in `feedback_digests` collection in ChromaDB
- Marks processed files (move to `data/feedback/processed/`)
- Triggered: daily, before main pipeline run (so today's context includes yesterday's feedback)

**Verify:** Add test feedback files → run aggregation → query `feedback_digests` → digest returned.

Files: `pipeline/feedback.py` (new), `main.py` (add feedback aggregation step before analysis)

---

### 9. Weekly summarizer `[DONE — Google Drive export deferred]`
Compress 7 daily reports into one weekly summary. Store in vector store, push to Google Drive.

**Note:** Compression + vector store replacement implemented and verified (`pipeline/weekly.py`, `.github/workflows/weekly_summary.yml`). Google Drive export deliberately deferred until all real sources are in and the pipeline is finalized — revisit alongside Phase 4.

**Implementation:**
- `pipeline/weekly.py` — new module
- Reads last 7 daily reports from `report_history` collection
- Sends to LLM: "Compress these 7 daily reports into a weekly intelligence summary"
- Stores weekly summary in `report_history` (replaces the 7 daily entries to prevent bloat)
- Exports to Google Drive via API (service account)
- Triggered: separate GitHub Actions workflow on Sunday

**Google Drive integration:** service account with Drive API scope, writes to shared folder.

**Verify:** After 7 daily runs, trigger weekly → summary appears in vector store and Google Drive.

Files: `pipeline/weekly.py` (new), `.github/workflows/weekly_summary.yml` (new), `scripts/setup_google_drive.py` (new)

---

## Dependencies

```
1 (ChromaDB setup)
├── 2 (seed context) → 5 (RAG analyst)
├── 3 (dedup) — independent after 1
├── 4 (entities) — independent after 1
└── 5 (RAG) → 8 (feedback aggregation) → 9 (weekly summarizer)

6 (scoring) — independent, needs analyst output only
7 (feedback form) — independent, needs report.py only
8 (aggregation) — needs 1 + 7
9 (weekly) — needs 5 + 8
```

## Execution Order (session-safe chunks)

**Session A:** Tasks 1 + 2 (ChromaDB infra + seed)
**Session B:** Tasks 3 + 4 (dedup + entities — parallel, independent)
**Session C:** Task 5 (RAG analyst — core integration, needs focus)
**Session D:** Tasks 6 + 7 (scoring + feedback form — parallel, independent)
**Session E:** Task 8 (feedback aggregation)
**Session F:** Task 9 (weekly summarizer + Google Drive)
**Session G:** End-to-end verification + /context-update

---

## Verify Phase Complete
- [x] ChromaDB vector store initialized and seeded with company context (23 chunks)
- [x] `py main.py --no-email` runs without errors (regression check)
- [x] Analyst retrieves relevant context from vector store — visibly influences report
- [x] Semantic deduplication reduces duplicate signals across sources
- [x] Named entities extracted and stored as structured metadata
- [x] Source quality scores logged per run
- [x] Feedback form renders at bottom of HTML report
- [x] Feedback → aggregation → digest in vector store works end-to-end
- [x] Weekly summarizer compresses 7 daily reports into one summary
- [x] Feedback on Day 1 measurably changes report on Day 7 (verified via test feedback)

## Phase Complete
**Date:** 2026-06-22
**Summary:** Phase 2 (AI Brain) fully implemented and verified end-to-end. ChromaDB vector store with 3 collections (company_context, report_history, feedback_digests), RAG-enhanced analyst, semantic dedup, entity extraction, source scoring, feedback form + aggregation + weekly summarization all working. Full feedback loop demonstrated: test feedback → aggregated digest → stored in vector store → retrieved as context on next run. Google Drive export deferred to Phase 4.
