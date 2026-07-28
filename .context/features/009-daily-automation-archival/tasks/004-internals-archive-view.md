# Task 004: `/internals` archive browsing section + download route

**Status:** done
**Depends on:** none (independent of Tasks 001–003 — this task only needs the
`data/archive/{country}/{domain}/{YYYY-MM-DD}.pdf` layout, which is already locked in CONTEXT.md's
Implementation Decisions, not code from `pipeline/archive.py`; it can be built and verified with
hand-created dummy PDF files, before or in parallel with Tasks 001–003)
**Model tier:** mid — real design judgment on route security (this project has a documented
history of exactly this class of path-traversal bug — see `.context/DECISIONS.md`'s 2026-07-08
Feature 001 entry) and Jinja template integration into an existing multi-section page.

## Files
- Modify: `app.py`
- Modify: `templates/internals.html`

## What to do

**1. In `app.py`**, add archive listing + a download route. Placement: near the other module-level
constants/helpers (after `DATA_DIR`/`FEEDBACK_DIR`/`PRESENTATION_DIR` and before `_load_json`, or
wherever fits cleanly next to the existing helpers — your call, keep it readable).

Add `send_from_directory` to the existing Flask import line:
```python
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
```

Add:
```python
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
_ARCHIVE_FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.pdf$")
# Same 8-code whitelist used by _domain_mode() below — kept as its own literal here rather than
# factored into a shared constant, matching this file's existing pattern (the same tuple already
# appears twice, in _domain_mode() and report()'s any_domain_file_exists check).
_VALID_ARCHIVE_DOMAINS = ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS")


def _list_archives():
    """Scan data/archive/{country}/{domain}/{date}.pdf and return a flat list of dicts (newest
    first) for the /internals archive browsing section. Returns [] if the archive dir doesn't
    exist yet (e.g. before the wrapper script has ever run) — not an error state."""
    archives = []
    if not os.path.isdir(ARCHIVE_DIR):
        return archives
    for country in sorted(os.listdir(ARCHIVE_DIR)):
        country_dir = os.path.join(ARCHIVE_DIR, country)
        if not os.path.isdir(country_dir):
            continue
        for domain in sorted(os.listdir(country_dir)):
            domain_dir = os.path.join(country_dir, domain)
            if not os.path.isdir(domain_dir):
                continue
            for filename in os.listdir(domain_dir):
                if not _ARCHIVE_FILENAME_RE.match(filename):
                    continue
                archives.append({
                    "country": country,
                    "domain": domain,
                    "date": filename[:-4],
                    "filename": filename,
                })
    archives.sort(key=lambda a: a["date"], reverse=True)
    return archives
```

In the existing `internals()` view function, call `_list_archives()` and pass it into
`render_template("internals.html", ...)` as `archives=archives` (add it alongside the existing
`scores`/`metadata`/`collections`/`demo_mode`/`current_country` kwargs — don't reorder or remove
any of the existing ones).

Add a new route (anywhere among the other `@app.route` definitions, e.g. right after `internals()`):
```python
@app.route("/internals/archive/<country>/<domain>/<filename>")
def download_archive(country, domain, filename):
    valid_codes = {c["code"] for c in load_sources()}
    if country not in valid_codes or domain not in _VALID_ARCHIVE_DOMAINS or not _ARCHIVE_FILENAME_RE.match(filename):
        return "Not found", 404
    directory = os.path.join(ARCHIVE_DIR, country, domain)
    return send_from_directory(directory, filename, as_attachment=True)
```

No change needed to `require_login()` (the `@app.before_request` hook) — `/internals/archive/...`
isn't `login`, isn't `static`, and isn't `/feedback`, so it's already gated behind login exactly
like `/internals` itself, with no role check, matching CONTEXT.md's placement decision.

**2. In `templates/internals.html`**, add a 5th section after the existing "4. Feedback Digest
Timeline" section (before `{% endblock %}` at line 190), matching the existing section markup
style (same card/table classes as the "Source Quality Scores" table above it):

```html
  <!-- 5. Report Archive -->
  <section class="mb-10">
    <h2 class="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Report Archive</h2>
    {% if archives %}
    <div class="bg-bg-card dark:bg-dark-card border border-border-card dark:border-dark-border rounded-xl shadow-soft overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 dark:bg-dark-card-hover text-left text-xs uppercase tracking-wider text-gray-400">
            <th class="px-6 py-3 font-semibold">Date</th>
            <th class="px-6 py-3 font-semibold">Country</th>
            <th class="px-6 py-3 font-semibold">Domain</th>
            <th class="px-6 py-3 font-semibold text-right">Download</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border-card dark:divide-dark-border">
          {% for a in archives %}
          <tr class="hover:bg-gray-50 dark:hover:bg-dark-card-hover">
            <td class="px-6 py-3 text-gray-700 dark:text-gray-300">{{ a.date }}</td>
            <td class="px-6 py-3 text-gray-700 dark:text-gray-300">{{ a.country }}</td>
            <td class="px-6 py-3 text-gray-700 dark:text-gray-300">{{ a.domain }}</td>
            <td class="px-6 py-3 text-right">
              <a href="{{ url_for('download_archive', country=a.country, domain=a.domain, filename=a.filename) }}" class="text-green-accent hover:underline font-medium">Download PDF</a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="bg-bg-card dark:bg-dark-card border border-border-card dark:border-dark-border rounded-xl shadow-soft p-6 text-center text-gray-400">
      No archived reports yet.
    </div>
    {% endif %}
  </section>
```

## Interfaces
- `_list_archives() -> list[dict]` — new, `app.py`-local helper, keys `country`/`domain`/`date`/
  `filename`.
- `download_archive(country, domain, filename)` — new Flask view, route
  `/internals/archive/<country>/<domain>/<filename>`, GET only (no method specified = GET-only
  default, matching `/internals`'s own route).
- `internals()` — existing view function, gains one new template kwarg (`archives`), no other
  signature/behavior change.
- Template expects `archives` to always be defined (an empty list is fine — `_list_archives()`
  never returns `None`).

## Constraints
- The download route must validate all three URL segments before touching the filesystem:
  `country` against `{c["code"] for c in load_sources()}` (the same set `_country_mode()` and
  `/feedback` already validate against elsewhere in this file), `domain` against the 8-code
  whitelist, and `filename` against the `^\d{4}-\d{2}-\d{2}\.pdf$` regex. Reject (404) if any
  check fails, before calling `send_from_directory`. This project has a documented history of
  exactly this class of bug (Feature 001's `/feedback` filename path-traversal fix, 2026-07-08) —
  don't skip the explicit whitelist just because `send_from_directory` has its own internal
  traversal guard.
- No role check on either the listing or the download route — `/internals` is open to any
  logged-in user (viewer or admin) per its existing, unchanged behavior; do not add
  `session.get("role") != "admin"` anywhere in this task.
- Do not change `require_login()`'s exclusion list.
- Do not reorder or remove any existing `render_template("internals.html", ...)` kwargs.
- Do not touch `pipeline/archive.py`, `scripts/daily_pipeline.py`, or any other template.

## Verification

No Playwright needed for this task — just Flask, `curl`, and hand-created dummy files.

1. Create two dummy archive files (contents don't matter for this task — this task tests listing
   and serving, not PDF rendering, which Task 002 already covers separately):
   ```
   mkdir -p data/archive/SG/BER data/archive/VN/GENERAL
   echo "dummy" > data/archive/SG/BER/2026-07-20.pdf
   echo "dummy" > data/archive/VN/GENERAL/2026-07-21.pdf
   ```
2. Install a minimal working set if not already available (`pip install flask python-dotenv`) and
   boot the dev server: `python app.py` (background), confirm it's listening.
3. Log in and capture a session cookie (viewer password is `Silversea` unless
   `data/viewer_password.txt` already holds something else on this machine — check that file
   first if the login step below returns "Incorrect password"):
   ```
   curl -s -c cookies.txt -d "password=Silversea" http://localhost:5000/login > /dev/null
   ```
4. Confirm the archive section renders with both dummy entries:
   ```
   curl -s -b cookies.txt http://localhost:5000/internals | grep -c "2026-07-20\|2026-07-21"
   ```
   should report matches for both dates (or grep for each individually and show both hits).
5. Confirm the download route actually serves the file:
   ```
   curl -s -b cookies.txt -o downloaded.pdf http://localhost:5000/internals/archive/SG/BER/2026-07-20.pdf
   diff downloaded.pdf data/archive/SG/BER/2026-07-20.pdf
   ```
   `diff` should report no difference.
6. **Security check — do not skip.** Confirm path-traversal and invalid-segment attempts are
   rejected with 404, not served:
   ```
   curl -s -b cookies.txt -o /dev/null -w "%{http_code}\n" "http://localhost:5000/internals/archive/SG/BER/..%2f..%2f..%2fapp.py"
   curl -s -b cookies.txt -o /dev/null -w "%{http_code}\n" "http://localhost:5000/internals/archive/XX/BER/2026-07-20.pdf"
   curl -s -b cookies.txt -o /dev/null -w "%{http_code}\n" "http://localhost:5000/internals/archive/SG/BER/notadate.pdf"
   ```
   All three must report `404`, not `200` and not the contents of `app.py`.
7. Confirm the download route is still login-gated (no cookie): 
   ```
   curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/internals/archive/SG/BER/2026-07-20.pdf
   ```
   should report `302` (redirect to `/login`), not `200`.
8. Clean up the dummy files (`data/archive/SG/BER/2026-07-20.pdf`,
   `data/archive/VN/GENERAL/2026-07-21.pdf`, and the now-empty `data/archive/` tree they created)
   and `cookies.txt`/`downloaded.pdf` before finishing, so this task doesn't leave test fixtures
   behind for Task 002/003's own archive output to collide with. Stop the dev server.

## Evidence

Executed by `feature-executor` (sonnet tier). `app.py`/`templates/internals.html` diffs reviewed
by the orchestrating session and confirmed to match spec exactly, no changes needed.

1. Dummy fixtures created (`data/archive/SG/BER/2026-07-20.pdf`, `data/archive/VN/GENERAL/2026-07-21.pdf`).
2. `python -c "import app"` — clean import, no errors.
3. Dev server booted; `curl` against `/login` → `200`.
4. Login via `curl -c cookies.txt -d "password=Silversea" .../login` → valid session cookie
   (`data/viewer_password.txt` held `Silversea`, the documented default).
5. Archive listing renders both dummy dates (`grep -c` → 2 matches each: date cell + href).
6. Download correctness: fetched file `diff`s identical to the source dummy file.
7. **Security checks — all four required outcomes confirmed:**
   - URL-encoded traversal (`..%2f..%2f..%2fapp.py`) → `404` (rejected at Flask's route-converter
     layer, before reaching the view).
   - Unencoded traversal (`../../../app.py`) → `404` (same layer).
   - Invalid country code (`XX`) → `404`, body `Not found` (caught by the explicit whitelist check
     inside `download_archive()`).
   - Invalid filename (`notadate.pdf`) → `404`, body `Not found` (caught by the explicit regex
     check).
   Both defensive layers (Flask's own route-converter rejection, and this view's own explicit
   whitelist/regex checks) confirmed independently functional — matches the task's "both layers
   required" constraint, not just one incidentally covering for the other.
8. Unauthenticated request to the download route (no cookie) → `302` redirect to `/login` —
   `require_login()` gates it correctly with zero changes to that function.
9. Cleanup confirmed: dev server processes killed, `data/archive/` (dummy tree),
   `cookies.txt`/`downloaded.pdf` all removed. Final `git status --porcelain` showed only
   `app.py`/`templates/internals.html` modified from this task, no leftover fixtures.

