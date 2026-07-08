# Task 008: Country-scope `pipeline/feedback.py` and `pipeline/weekly.py`

**Status:** done

## Files

- `pipeline/feedback.py` (modify — `aggregate_feedback()`, `consolidate_feedback_digests()`)
- `pipeline/weekly.py` (modify — `generate_weekly_summary()`)
- `app.py` (modify — `receive_feedback()` route only)
- `templates/report.html` (modify — one new hidden form field)
- `main.py` (modify — `run_pipeline()`'s feedback-processing and weekly-summary call sites)

## What to do

**Background:** `pipeline/feedback.py` and `pipeline/weekly.py` currently read/write fully global,
unscoped ChromaDB collections (`FEEDBACK_DIGESTS`, `REPORT_HISTORY`). `pipeline/analyst.py`
already tags its `REPORT_HISTORY` writes with `"country": country["code"]` (see `analyse()`'s
`add_documents(REPORT_HISTORY, ..., metadatas=[{"date": ..., "country": country["code"]}])`) —
this task extends that same tagging pattern to feedback digests and threads country filtering
through both modules' reads. Per CONTEXT.md's explicit decision, this is being fixed now, not
deferred again — without it, VN and SG feedback/weekly summaries blend into one global stream.

There is a real gap to close first: **feedback submissions currently capture no country context
at all** — the `/feedback` route's hidden form only carries `report_date`. Steps 1-3 below close
that gap; steps 4-6 make `feedback.py`/`weekly.py` actually use it.

**1. `templates/report.html` — capture which country's report a feedback submission is about.**
Immediately after the existing hidden field (current line 526):
```html
      <input type="hidden" name="report_date" value="{{ report._metadata.date }}" />
```
add:
```html
      <input type="hidden" name="country" value="{{ current_country|default('SG') }}" />
```
The feedback form's existing JS (`new FormData(form).entries()`, later in the same file) already
serializes every named form field automatically — no JS change is needed for this new field to
reach `/feedback`.

**2. `app.py`'s `receive_feedback()` — read and validate the country field.** Add, right after the
existing `submitter` sanitization block:
```python
    from config.sources import load_sources
    raw_country = (data.get("country") or "SG").strip()
    valid_codes = {c["code"] for c in load_sources()}
    country_code = raw_country if raw_country in valid_codes else "SG"
```
(If Task 003 already added a top-level `from config.sources import load_sources` import to
`app.py`, use that instead of a local import inside this function — check the top of the file
first and don't duplicate the import.)

Then add `"country": country_code` to the `feedback` dict being written to disk:
```python
    feedback = {
        "report_date": data.get("report_date", ""),
        "country": country_code,
        "relevance_rating": relevance_rating,
        "most_useful": data.get("most_useful", ""),
        "missed_topics": data.get("missed_topics", ""),
        "priority_changes": priority_changes,
        "submitter": submitter,
        "submitted_at": now.isoformat(),
    }
```
Do not touch anything else in `receive_feedback()` (the duplicate-source-suggestion logic, the
pending-source-suggestion write) — those are unrelated to country-scoping.

**3. `pipeline/feedback.py` — `aggregate_feedback(country_code: str = None)`.** Filter submissions
by their (now-present) `country` field, defaulting missing/legacy submissions (written before this
feature) to `"SG"` — historically all feedback was implicitly Singapore-only, so that's the
correct backward-compatible default, not an arbitrary choice. Only move to `processed/` the files
actually consumed for the requested country, leaving other countries' pending files untouched for
their own next run:
```python
def aggregate_feedback(country_code: str = None) -> None:
    """Read unprocessed feedback for one country, summarize via LLM, store digest in vector store.
    country_code=None processes ALL pending feedback regardless of country (legacy/manual-run
    behavior); pass an explicit code to scope to one country's submissions."""
    if not os.path.isdir(FEEDBACK_DIR):
        return

    json_files = [f for f in os.listdir(FEEDBACK_DIR) if f.endswith(".json")]
    if not json_files:
        return

    matched_files = []
    submissions = []
    for filename in json_files:
        filepath = os.path.join(FEEDBACK_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                sub = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        sub_country = sub.get("country", "SG")
        if country_code and sub_country != country_code:
            continue
        submissions.append(sub)
        matched_files.append(filename)

    if not submissions:
        return

    feedback_text = "\n\n".join(
        f"Rating: {s.get('relevance_rating', '?')}/5\n"
        f"Most useful: {s.get('most_useful', 'N/A')}\n"
        f"Missed topics: {s.get('missed_topics', 'N/A')}\n"
        f"Priority changes: {s.get('priority_changes', 'N/A')}"
        for s in submissions
    )

    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    if not client.api_key:
        print("  Feedback aggregation skipped — no GROQ_API_KEY")
        return

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": SUMMARIZE_PROMPT.format(feedback_text=feedback_text)}],
        max_tokens=512,
    )

    digest = response.choices[0].message.content
    metadata = {
        "date": datetime.date.today().isoformat(),
        "submissions_count": str(len(submissions)),
    }
    if country_code:
        metadata["country"] = country_code
    add_documents(FEEDBACK_DIGESTS, [digest], metadatas=[metadata])

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    for filename in matched_files:
        shutil.move(os.path.join(FEEDBACK_DIR, filename), os.path.join(PROCESSED_DIR, filename))

    scope_note = f" [{country_code}]" if country_code else ""
    print(f"  Feedback: aggregated {len(submissions)} submission(s) into vector store digest{scope_note}")
```

**4. `pipeline/feedback.py` — `consolidate_feedback_digests(max_digests=10, country_code=None)`.**
Filter the `FEEDBACK_DIGESTS` read via `where`, and use the *filtered* result count (not
`collection.count()`, which counts the whole unfiltered collection) to decide whether
consolidation is needed — this matters: with country filtering active, consolidating based on the
global count would trigger prematurely/incorrectly relative to one country's actual digest count.
```python
def consolidate_feedback_digests(max_digests: int = 10, country_code: str = None) -> None:
    """Merge oldest feedback digests when one country's digest count exceeds cap.
    Mirrors pipeline/weekly.py's delete-then-replace pattern."""
    collection = get_collection(FEEDBACK_DIGESTS)
    get_kwargs = {"include": ["documents", "metadatas"]}
    if country_code:
        get_kwargs["where"] = {"country": country_code}
    results = collection.get(**get_kwargs)
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    ids = results.get("ids", [])
    count = len(ids)
    if count <= max_digests:
        return

    # Sort by date, oldest first
    paired = list(zip(ids, documents, metadatas))
    paired.sort(key=lambda x: (x[2] or {}).get("date", ""))

    n_to_consolidate = count - max_digests + 1
    old_ids = [p[0] for p in paired[:n_to_consolidate]]
    old_docs = [p[1] for p in paired[:n_to_consolidate]]

    digests_text = "\n\n---\n\n".join(old_docs)

    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    if not client.api_key:
        print("  Feedback consolidation skipped — no GROQ_API_KEY")
        return

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": CONSOLIDATION_PROMPT.format(
            count=len(old_docs), digests_text=digests_text
        )}],
        max_tokens=512,
    )

    consolidated = response.choices[0].message.content

    delete_documents(FEEDBACK_DIGESTS, old_ids)
    metadata = {
        "date": datetime.date.today().isoformat(),
        "type": "consolidated",
        "source_count": str(len(old_ids)),
    }
    if country_code:
        metadata["country"] = country_code
    add_documents(FEEDBACK_DIGESTS, [consolidated], metadatas=[metadata])

    scope_note = f" [{country_code}]" if country_code else ""
    print(f"  Feedback: consolidated {len(old_ids)} old digests into 1 summary{scope_note}")
```

**5. `pipeline/weekly.py` — `generate_weekly_summary(country_code: str = None)`.** Filter the
`REPORT_HISTORY` read via `where` when a country is given (accepting that pre-existing untagged
docs are excluded when filtering — a known, accepted limitation per DECISIONS.md, not something
this task backfills), and tag the new weekly-summary write with country:
```python
def generate_weekly_summary(country_code: str = None) -> str:
    """Retrieve recent daily reports for one country, compress into weekly summary, update vector
    store. country_code=None retains the old global (all-countries) behavior."""
    collection = get_collection(REPORT_HISTORY)
    get_kwargs = {"limit": 14, "include": ["documents", "metadatas"]}
    if country_code:
        get_kwargs["where"] = {"country": country_code}
    results = collection.get(**get_kwargs)
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    ids = results.get("ids", [])

    if not documents:
        print("No daily reports found — skipping weekly summary.")
        return ""

    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)

    weekly_docs = []
    weekly_ids = []
    for doc, meta, doc_id in zip(documents, metadatas, ids):
        date_str = (meta or {}).get("date", "")
        try:
            doc_date = datetime.date.fromisoformat(date_str)
            if doc_date >= week_ago:
                weekly_docs.append(doc)
                weekly_ids.append(doc_id)
        except (ValueError, TypeError):
            weekly_docs.append(doc)
            weekly_ids.append(doc_id)

    if not weekly_docs:
        print("No reports from the last 7 days — skipping.")
        return ""

    reports_text = "\n\n---\n\n".join(weekly_docs)

    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    if not client.api_key:
        print("Weekly summary skipped — no GROQ_API_KEY")
        return ""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": WEEKLY_PROMPT.format(count=len(weekly_docs), reports=reports_text)}],
        max_tokens=2048,
    )

    summary = response.choices[0].message.content

    delete_documents(REPORT_HISTORY, weekly_ids)

    metadata = {
        "date": today.isoformat(),
        "type": "weekly_summary",
        "covers_from": week_ago.isoformat(),
        "covers_to": today.isoformat(),
        "daily_count": str(len(weekly_docs)),
    }
    if country_code:
        metadata["country"] = country_code
    add_documents(REPORT_HISTORY, [summary], metadatas=[metadata])

    scope_note = f" [{country_code}]" if country_code else ""
    print(f"  Weekly summary: compressed {len(weekly_docs)} daily reports into 1 summary{scope_note}")
    return summary
```
Note: the original used `collection.count()` up front purely as an early-exit ("no reports at
all") and then `collection.get(limit=min(count, 14), ...)`. Since `get_kwargs["where"]` changes
what "all documents" means, the rewrite above drops the separate `count()` early-exit and instead
checks `if not documents:` after the (possibly filtered) `get()` call — simpler and correct under
filtering. Also note `limit=14` no longer needs `min(count, 14)` since Chroma's `get()` already
caps at however many documents actually exist/match — verify this is still true when you run the
verification steps below; if Chroma errors on a `limit` larger than the available/filtered count,
add back a `min()` guard against the *filtered* result size instead.

**6. `main.py` — thread country through both call sites.** Currently `aggregate_feedback()` and
`consolidate_feedback_digests()` are called once, globally, before the per-country loop (current
lines 44-46):
```python
    print("Processing feedback from previous run...")
    aggregate_feedback()
    consolidate_feedback_digests()

    for country in active_countries:
        print(f"=== {country['name']} ({country['code']}) ===")
```
Move both calls inside the loop, scoped per-country, and remove the old global pre-loop calls:
```python
    for country in active_countries:
        print(f"=== {country['name']} ({country['code']}) ===")

        print("Processing feedback from previous run...")
        aggregate_feedback(country_code=country["code"])
        consolidate_feedback_digests(country_code=country["code"])

        sources = country["sources"]
```
And the Sunday weekly-summary block (current lines 98-100):
```python
    if datetime.date.today().weekday() == 6:  # Sunday
        print("Running weekly summary (Sunday)...")
        generate_weekly_summary()
```
becomes:
```python
    if datetime.date.today().weekday() == 6:  # Sunday
        print("Running weekly summary (Sunday)...")
        for country in active_countries:
            generate_weekly_summary(country_code=country["code"])
```

## Interfaces

- `pipeline.feedback.aggregate_feedback(country_code: str = None) -> None` — new optional
  parameter, default `None` preserves the old (all-countries) behavior for any other caller.
- `pipeline.feedback.consolidate_feedback_digests(max_digests: int = 10, country_code: str = None) -> None`
  — same additive-default pattern.
- `pipeline.weekly.generate_weekly_summary(country_code: str = None) -> str` — same pattern.
- `app.receive_feedback()` — now reads one additional form/JSON field (`country`), still no route
  signature change.

## Constraints

- Backward compatibility: every new parameter defaults to `None`/preserves old behavior when
  omitted — `main.py` is the only caller in this codebase, and this task updates it to always pass
  an explicit `country_code`, but the default-`None` signature must still exist so no other
  hypothetical caller breaks.
- Do not attempt to backfill `country` metadata onto pre-existing ChromaDB documents or
  pre-existing feedback JSON files on disk — that's explicitly the "known, accepted limitation"
  DECISIONS.md already documents (older docs simply won't match a country-filtered `where` query
  going forward); this task fixes things prospectively, not retroactively.
- Do not touch `app.py`'s `login()`, `report()`, `internals()`, `admin()`, `change_viewer_password()`,
  `approve_source()`, `reject_source()`, or `add_cors()` — `receive_feedback()` only.
- Do not touch the duplicate-source-suggestion detection logic or the pending-source-suggestion
  write inside `receive_feedback()` — unrelated to this task, already working correctly.
- Keep `SUMMARIZE_PROMPT`, `CONSOLIDATION_PROMPT`, and `WEEKLY_PROMPT` string constants unchanged
  — this task is about metadata/filtering plumbing, not prompt content.

## Verification

No LLM call needed for the plumbing/structure — verify the ChromaDB `where`-filtering mechanics
and file-routing logic directly, without calling Groq:

1. `py -c "import ast; ast.parse(open('pipeline/feedback.py', encoding='utf-8').read())"`,
   same for `pipeline/weekly.py`, `app.py`, `main.py` — all four must parse without a
   `SyntaxError`.
2. Confirm `collection.get(where=...)` actually filters as expected — this is the load-bearing
   ChromaDB behavior this whole task depends on, so verify it directly against the local
   persistent store (no LLM call): add two throwaway documents to `REPORT_HISTORY` with different
   `country` metadata values, call `get_collection(REPORT_HISTORY).get(where={"country": "VN"},
   include=["documents"])`, confirm only the VN-tagged one comes back, then delete both throwaway
   documents (via `delete_documents`) so the store is left clean.
3. Exercise `aggregate_feedback(country_code=...)`'s filtering logic without a live Groq call by
   creating two throwaway files in `data/feedback/` (one with `"country": "SG"`, one with
   `"country": "VN"`), monkeypatching or temporarily unsetting `GROQ_API_KEY` so the function
   exits early at the "no GROQ_API_KEY" guard *after* the filtering step — instead, to actually
   verify the filter logic itself without relying on the API-key guard's placement, write a small
   standalone script that duplicates just the filtering loop (read `data/feedback/*.json`, filter
   by `sub.get("country","SG") == "VN"`) and confirm it selects only the VN file. Clean up both
   throwaway files afterward (delete, don't move to `processed/`, since this is a verification
   script, not a real run).
4. Confirm `templates/report.html` now renders the new hidden `country` input — render the
   template with `current_country="VN"` and check `name="country"` and `value="VN"` both appear in
   the output.
5. Confirm `app.py`'s `receive_feedback()` now reads and validates `country` — grep the file to
   confirm the exact block from step 2 above is present, and exercise it with
   `app.test_client().post("/feedback", json={"report_date": "2026-07-08", "country": "VN", "relevance_rating": 3})`
   (or `"country": "XX"` to confirm it falls back to `"SG"`) — check the resulting file written to
   `data/feedback/` contains the expected `"country"` value, then delete that test file.
6. Confirm `main.py`'s feedback/weekly call sites now pass `country_code=country["code"]` — grep
   to confirm the exact call signatures at both sites (per-country loop and the Sunday block).

## Model tier

quality — this is the one task in the feature with genuine architectural weight: it closes a real
structural gap (feedback submissions previously carried no country context at all), changes a
call site from "run once globally" to "run per-country in a loop" (a real behavior change, not
just a parameter default), and requires correctly reasoning about ChromaDB `where`-filtering
semantics (count-before-filter vs. count-after-filter, as called out explicitly in step 4's
`consolidate_feedback_digests` rewrite) rather than mechanically transcribing a fully-specified
diff.

## Depends on

Task 003 (`003-app-country-routing-and-run-metadata-scoping.md`) — this task's `app.py` edit
(`receive_feedback()`) and `main.py` edit (feedback/weekly call sites) must land after Task 003's
edits to those same two files (`report()`/`internals()`/`admin()` in `app.py`; the run_metadata
write block in `main.py`) to avoid one task's diff stepping on the other's line ranges. Also
reuses the `from config.sources import load_sources` import Task 003 adds to `app.py` — check for
it before adding a duplicate.

## Evidence

Executor report (DONE):
1. AST parse — all 4 files clean.
2. Load-bearing `collection.get(where=...)` filter verified directly against live ChromaDB: SG+VN throwaway docs added to REPORT_HISTORY, `where={"country":"VN"}` returned only the VN doc; cleaned up after.
3. `aggregate_feedback`'s country-filter logic verified against two throwaway feedback files — selected only the VN one.
4. `report.html` hidden field renders `value="VN"` / `value="SG"` correctly.
5. `POST /feedback` with `country:"VN"` writes `country: VN`; `country:"XX"` falls back to `SG`. Test files cleaned up.
6. Grep-confirmed all three call sites in `main.py` now pass `country_code=country["code"]`.
7. Confirmed `limit=14` + `where` filter with 1 match does not error — no `min()` guard needed.

Files changed: `templates/report.html`, `app.py` (receive_feedback only), `pipeline/feedback.py`, `pipeline/weekly.py`, `main.py`.

Flagged (not a defect, out of this task's scope): `pipeline/weekly.py`'s `WEEKLY_PROMPT` constant still hardcodes "Singapore" in its system framing — task constraints explicitly said not to touch prompt constants, so correctly left as-is, but it's the same class of bug Task 006 fixed in `SUMMARY_PROMPT`. Worth a follow-up. Also flagged: `receive_feedback()`'s filename scheme (`%Y%m%d_%H%M%S_{submitter}`) can collide if the same submitter posts twice within one second — pre-existing behavior, unrelated to country-scoping, not fixed here.
