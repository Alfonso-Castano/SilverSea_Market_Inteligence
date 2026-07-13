# Task 003: Country-aware `/` and `/internals` routing, admin country list, run_metadata scoping

**Status:** done

## Files

- `app.py` (modify — add `_country_mode()` helper; edit `report()`, `internals()`, `admin()`
  route functions; add one top-level import)
- `main.py` (modify — `run_pipeline()`'s run_metadata write block only)

## What to do

**Background:** `app.py` hardcodes `"SG"` into the report-filename lookup in `report()`
(`f"latest_report_SG_{domain}.json"`), and `internals()` reads a single global
`data/run_metadata.json` with no country awareness at all. Meanwhile `_domain_mode()` already
establishes the pattern this task should mirror for country. Separately, `admin()`'s template
needs a live list of countries to populate a dropdown (used by Task 005).

**1. Add a top-level import** near the existing `from pipeline import source_suggestions` line:
```python
from config.sources import load_sources
```

**2. Add `_country_mode()`**, directly after the existing `_domain_mode()` function (current lines
80-82):
```python
def _country_mode():
    valid_codes = {c["code"] for c in load_sources()}
    country = request.args.get("country", "SG")
    return country if country in valid_codes else "SG"
```

**3. Update `report()`** (current lines 85-105) to use it instead of the hardcoded `"SG"`:
```python
@app.route("/")
def report():
    demo_mode = _demo_mode()
    domain = _domain_mode()
    country = _country_mode()
    domain_filename = f"latest_report_{country}_{domain}.json"
    report_data = _load_json(os.path.join("presentation", f"{demo_mode}_report.json"), {})
    if not report_data:
        if os.path.exists(os.path.join(DATA_DIR, domain_filename)):
            report_data = _load_json(domain_filename, {})
        else:
            # Only fall back to the pre-domain-scoping legacy report if NO domain-scoped
            # file exists yet anywhere for THIS country — never substitute a different
            # domain's or country's content for one that simply has no report yet, which
            # would silently mislabel stale cross-domain/cross-country data as belonging
            # to this one.
            any_domain_file_exists = any(
                os.path.exists(os.path.join(DATA_DIR, f"latest_report_{country}_{d}.json"))
                for d in ("BER", "EDU", "GENERAL")
            )
            if not any_domain_file_exists:
                report_data = _load_json("latest_report.json", {})
    return render_template("report.html", report=report_data, demo_mode=demo_mode,
                            current_domain=domain, current_country=country)
```
(Only the `domain_filename`/`any_domain_file_exists` variable content changes to use `country`
instead of the literal `"SG"`; the fallback structure and comment intent are preserved and
extended — update the comment as shown.)

**4. Update `internals()`** (current lines 108-136) to be country-aware and read the
country-scoped metadata file (written by main.py, see step 5 below), with the same
never-mislabel-as-another-country fallback discipline as `report()`:
```python
@app.route("/internals")
def internals():
    demo_mode = _demo_mode()
    country = _country_mode()
    scores = _load_json("source_scores.json", {})
    metadata = _load_json(os.path.join("presentation", f"{demo_mode}_metadata.json"), {})
    if not metadata:
        country_metadata_filename = f"run_metadata_{country}.json"
        if os.path.exists(os.path.join(DATA_DIR, country_metadata_filename)):
            metadata = _load_json(country_metadata_filename, {})
        else:
            any_country_metadata_exists = any(
                os.path.exists(os.path.join(DATA_DIR, f"run_metadata_{c['code']}.json"))
                for c in load_sources()
            )
            if not any_country_metadata_exists:
                metadata = _load_json("run_metadata.json", {})

    collections_data = {}
    try:
        from pipeline.vectorstore import get_collection, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
        for name in [COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS]:
            col = get_collection(name)
            result = col.get(limit=20, include=["documents", "metadatas"])
            collections_data[name] = {
                "documents": result.get("documents", []),
                "metadatas": result.get("metadatas", []),
                "ids": result.get("ids", []),
                "count": col.count(),
            }
    except Exception as e:
        collections_data = {"error": str(e)}

    return render_template("internals.html",
        scores=scores,
        metadata=metadata,
        collections=collections_data,
        demo_mode=demo_mode,
        current_country=country,
    )
```
(Only the metadata-loading block and the two new `country`/`current_country` lines are new; the
`collections_data` block is unchanged — copy it verbatim, do not modify the collection-viewer
logic, that's out of this task's scope.)

**5. Update `admin()`** (current lines 222-228) to pass the live country list for Task 005's
template dropdown:
```python
@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    pending = source_suggestions.list_pending()
    interest_signals = source_suggestions.list_interest_signals()
    countries = load_sources()
    return render_template("admin.html", pending=pending, interest_signals=interest_signals,
                            countries=countries)
```

**6. `main.py` — country-scope the run_metadata write.** In `run_pipeline()`, current lines 76-86:
```python
        run_metadata = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "country": country["name"],
            "country_code": country["code"],
            "sources_scraped": len(scraped),
            "sources_passed_filter": len(filtered),
        }
        metadata_path = os.path.join("data", "run_metadata.json")
        os.makedirs("data", exist_ok=True)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(run_metadata, f, indent=2)
```
Change only the `metadata_path` line:
```python
        metadata_path = os.path.join("data", f"run_metadata_{country['code']}.json")
```
Everything else in that block (the `run_metadata` dict contents, `os.makedirs`, the `open`/`json.dump`
call) stays exactly as-is — this mirrors `pipeline/report.py`'s existing domain-scoping filename
pattern (`latest_report_{country_code}_{domain}.json`), applied here to `run_metadata`.

## Interfaces

- New function `app._country_mode() -> str` — returns a validated country code, `"SG"` default,
  mirrors `_domain_mode()`'s signature/contract exactly.
- `render_template("report.html", ...)` and `render_template("internals.html", ...)` now both
  receive a `current_country` kwarg (string, e.g. `"SG"` or `"VN"`).
- `render_template("admin.html", ...)` now receives a `countries` kwarg (list of country dicts,
  same shape as `config.sources.load_sources()`'s return value).
- No change to any existing route's URL pattern or HTTP method.

## Constraints

- Do not touch `_demo_mode()`, `_domain_mode()`, `login()`, `receive_feedback()`,
  `change_viewer_password()`, `approve_source()`, `reject_source()`, or `add_cors()` — those are
  out of this task's scope (Task 008 touches `receive_feedback()` separately, after this task
  lands).
- Do not touch `pipeline/report.py`'s domain-scoping logic — only `main.py`'s run_metadata write
  path changes.
- Preserve the existing "never substitute a different domain's/country's content for one that
  simply has no report yet" fallback discipline exactly — this is a deliberate anti-mislabeling
  rule from the original domain-scoping work, not incidental code.
- `main.py --country=SG` (and `--domain=`) must keep behaving exactly as today — this is additive
  scoping (a filename now includes the country code), not a behavior change for SG.

## Verification

No LLM call needed — Flask-side changes only, verify by booting the app and curling routes per
CLAUDE.md's verification protocol:

1. `py -c "import ast; ast.parse(open('app.py', encoding='utf-8').read())"` and same for
   `main.py` — both must parse without a `SyntaxError`.
2. Start the Flask app locally (`py app.py` or via `app.test_client()`), then:
   - `GET /?country=SG` — must render (whatever report data exists or the empty-state, no
     traceback).
   - `GET /?country=VN` — must render without a traceback, even with no VN report file yet
     (exercises the "no report yet" fallback path — should NOT show SG's report data mislabeled
     as VN).
   - `GET /?country=XX` (an invalid/unknown code) — must fall back to `"SG"` behavior, not crash.
   - `GET /internals?country=VN` — must render without a traceback.
   - `GET /admin` (as an authenticated admin session, or via direct `render_template("admin.html",
     pending=[], interest_signals=[], countries=load_sources())` if `ADMIN_PASSWORD` isn't set in
     this environment) — confirm the response/rendered HTML contains no Jinja error.
3. `python -c "from app import _country_mode"` style check isn't meaningful outside a request
   context — instead confirm via `grep`/read that `_country_mode()` exists and matches the
   `_domain_mode()` contract (default `"SG"`, validated against `load_sources()`'s codes).
4. Confirm `main.py`'s `metadata_path` line now builds `run_metadata_{code}.json` — grep the file
   to confirm the exact f-string, then (optionally, since this doesn't call the LLM) run
   `py main.py --no-email --country=SG` only if you want to also exercise scraping/filtering live
   — **do not** do this if it would proceed to the `analyse()` LLM call; if you want to verify the
   metadata-write path specifically without burning Groq quota, simplest is to grep-confirm the
   f-string and trust `pipeline/report.py`'s already-proven identical pattern, rather than running
   the full pipeline.

## Model tier

mid — several small, well-specified edits across two files, but requires correctly threading a
new parameter through multiple call sites without breaking the existing SG/domain behavior.

## Depends on

None. This task does not touch `config/sources.json` (Tasks 001/002) or any template (Tasks
004/005/008's report.html changes) — it can run in parallel with those. Tasks 004, 005, and 008
each depend on this task instead, since they consume `current_country`/`countries` template
context this task introduces.

## Evidence

Executor report (DONE):
1. `ast.parse` on both files — clean.
2. Flask test-client: `GET /?country=SG`, `/?country=VN`, `/?country=XX`, `/internals?country=VN` all → 200, no tracebacks.
3. Mocked `load_sources()` to include VN (since 001 hadn't landed yet at dispatch time) and confirmed the "no VN report yet" fallback does NOT mislabel SG's report as VN's.
4. `render_template("admin.html", ..., countries=load_sources())` renders cleanly (no Jinja error).
5. Grep-confirmed `_country_mode()`, its call sites in `report()`/`internals()`, `admin()`'s `countries=load_sources()`, and `main.py`'s `run_metadata_{country['code']}.json` f-string.

Files changed: `app.py`, `main.py`. Did not run `py main.py` (would trigger Groq LLM call) — metadata path verified via grep only, per instructions.
