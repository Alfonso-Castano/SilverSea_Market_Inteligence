# Task 002: `pipeline/archive.py` — headless Playwright PDF archival of a report page

**Status:** done
**Depends on:** Task 001 (needs Playwright + Chromium installed to write and test this)
**Model tier:** mid — the core logic is fully specified below (this is largely transcription), but
the executor needs to correctly reason about the login flow and the entity-group-expansion step
from RESEARCH.md §3/§6, and design the local verification (there's a real risk of writing a
verification that "passes" against a blank or login-page PDF if the content check is skipped).

## Files
- Create: `pipeline/archive.py`

## What to do

Create a new module with one public function, `archive_report_pdf(country_code, domain,
base_url=None)`, that renders the given country/domain report page to a PDF using headless
Chromium via Playwright, and saves it to `data/archive/{country_code}/{domain}/{YYYY-MM-DD}.pdf`
(the file layout CONTEXT.md already locked in).

```python
# pipeline/archive.py — Headless PDF archival of a report page via Playwright + Chromium.
#
# Reuses the *existing* browser print CSS (static/style.css's `@media print` block) rather than
# building a second rendering path. `@media print` alone isn't enough to reveal collapsed entity
# groups (they default to opacity:0, which the print media query doesn't override — see
# .context/features/009-daily-automation-archival/RESEARCH.md §3), so this module also replicates
# the one-line group-expansion step that `static/animations.js`'s "Export PDF" button already does
# before printing.
import os
import datetime

from playwright.sync_api import sync_playwright

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
VIEWER_PASSWORD_PATH = os.path.join(DATA_DIR, "viewer_password.txt")

# Mirrors app.py's _get_viewer_password() fallback. Duplicated deliberately, not imported from
# app.py — importing app.py here would construct the Flask app, create the secret-key file, etc.
# as side effects of what should be a plain text-file read.
_DEFAULT_VIEWER_PASSWORD = "Silversea"

# Matches deploy/start.sh's BIND for the production Gunicorn instance — in production, the wrapper
# script archives against the already-running live app, not a second instance it spins up itself.
# Override via the ARCHIVE_BASE_URL env var (or the base_url parameter) for local testing against
# `py app.py`'s dev server (http://localhost:5000).
_DEFAULT_BASE_URL = "http://127.0.0.1:8001"


def _get_viewer_password() -> str:
    if os.path.exists(VIEWER_PASSWORD_PATH):
        with open(VIEWER_PASSWORD_PATH, "r", encoding="utf-8") as f:
            value = f.read().strip()
            return value or _DEFAULT_VIEWER_PASSWORD
    return _DEFAULT_VIEWER_PASSWORD


def archive_report_pdf(country_code: str, domain: str, base_url: str = None) -> str:
    """Render the report page for `country_code`/`domain` to a PDF and save it under
    data/archive/{country_code}/{domain}/{YYYY-MM-DD}.pdf. Returns the saved file's absolute path.
    Raises RuntimeError if login fails (e.g. viewer password file missing/wrong) or if Playwright
    itself raises during navigation/render — callers (the wrapper script) are expected to catch
    this per-combination, not let it abort the whole run.
    """
    base_url = base_url or os.environ.get("ARCHIVE_BASE_URL", _DEFAULT_BASE_URL)
    password = _get_viewer_password()
    date_str = datetime.date.today().isoformat()

    out_dir = os.path.join(ARCHIVE_DIR, country_code, domain)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{date_str}.pdf")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            page.goto(f"{base_url}/login")
            page.fill("#password", password)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            page.goto(f"{base_url}/?country={country_code}&domain={domain}")
            page.wait_for_load_state("networkidle")

            if "/login" in page.url:
                raise RuntimeError(
                    f"Archive login failed for {base_url} (country={country_code}, "
                    f"domain={domain}) — check data/viewer_password.txt"
                )

            # Replicate animations.js's confirmBtn handler: expand every collapsed entity group
            # so its content isn't opacity:0 in the printed output. See RESEARCH.md §3.
            page.evaluate(
                "document.querySelectorAll('.entity-group').forEach(el => el.classList.add('open'))"
            )

            # Second, previously-undocumented opacity trap found during this task's own
            # verification (distinct from the entity-group one above): every major report
            # section (base.html loads AOS 2.3.1; report.html tags each section
            # data-aos="fade-up") sits at opacity:0 until AOS's IntersectionObserver marks it
            # .aos-animate on scroll-into-view. A single-viewport headless render never scrolls,
            # so every section below the fold (sectors, opportunities, competition-risks,
            # data-sources) printed blank even with the entity-group fix in place. Resizing the
            # viewport to the page's full scroll height (measured after the groups above are
            # expanded, since that changes page height) brings every section into AOS's observed
            # viewport at once, without touching report.html/animations.js/style.css.
            full_height = page.evaluate("document.body.scrollHeight")
            page.set_viewport_size({"width": 1280, "height": full_height})
            page.wait_for_timeout(300)

            # page.pdf() already defaults to `print` CSS media (RESEARCH.md §1) — set it
            # explicitly anyway so this doesn't silently break on a future Playwright version.
            page.emulate_media(media="print")
            page.pdf(path=out_path, format="A4", print_background=True)
        finally:
            browser.close()

    return out_path
```

Write the file exactly as above (the comments are part of the spec, not optional — they record
*why* each non-obvious step exists, for the next person who reads this file without this task's
context).

## Interfaces
- `archive_report_pdf(country_code: str, domain: str, base_url: str = None) -> str` — the only
  public function. The wrapper script (Task 003) imports and calls this once per successful
  `main.py` combination.
- Depends on `playwright.sync_api.sync_playwright` (Task 001) and on `app.py`'s existing `/login`
  and `/` routes being served at `base_url` — does not depend on any other project module (no
  import from `app.py`, `pipeline/report.py`, etc.).

## Constraints
- Must use `p.chromium.launch(...)` — `page.pdf()` only works in headless Chromium, not
  Firefox/WebKit (RESEARCH.md §2). Do not use `p.firefox` or `p.webkit`.
- Do not drive the existing `#pdf-export-toggle`/`#pdf-export-confirm` buttons or call
  `page.evaluate("window.print()")` — see RESEARCH.md §4 for why. Use `page.pdf()` directly.
- Do not add the checkbox-exclusion logic (`.pdf-section-checkbox` → `.print-exclude`) — every
  checkbox defaults to checked in `templates/report.html`, so the default DOM state already
  includes every section; there is nothing to reproduce here for a full archival snapshot.
- Do not import `app.py` from this module.
- Always call `browser.close()` even if rendering fails partway (the `try`/`finally` above handles
  this — keep it).
- Do not touch any other file in this task.

## Verification

This must be tested against real, already-existing local report data — no pipeline run, no LLM
call. Use the `SG`/`BER` combination (`data/latest_report_SG_BER.json` already exists).

1. Install a minimal working set into whatever environment you're using (not the full
   `requirements.txt` — that pulls in `chromadb`/`torch`/`sentence-transformers`/`scrapling`
   unnecessarily for this check): `pip install flask python-dotenv playwright==1.61.0`, then
   `playwright install chromium` if not already done in Task 001's environment.
2. Boot the Flask dev server in the background from the repo root: `python app.py` (listens on
   `http://localhost:5000` per `app.py`'s own `__main__` block). Confirm it's actually listening
   (e.g. `curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/login` returns `200`).
3. Run:
   ```
   python -c "from pipeline.archive import archive_report_pdf; p = archive_report_pdf('SG', 'BER', base_url='http://localhost:5000'); print('SAVED:', p)"
   ```
4. Confirm the printed path is `data/archive/SG/BER/{today's date}.pdf` and the file exists on
   disk (`ls -la` or equivalent) with a non-trivial size — a blank/login-page render would be
   small (well under 20 KB); the real report page is content-rich and should be substantially
   larger.
5. **Content check — do not skip this, a passing file-exists check alone does not prove the
   group-expansion step worked.** `data/latest_report_SG_BER.json`'s first Government & Agencies
   signal (entity `BCA`) contains the text `"Built Environment Innovation Hub (BEIH)"` — this
   signal lives inside a collapsed-by-default entity group, so it will only appear in the rendered
   PDF if `.entity-group` expansion actually happened. Install `pypdf` ad hoc for this check only
   (do **not** add it to `requirements.txt` — it's a one-time verification tool, not a shipped
   dependency): `pip install pypdf`, then:
   ```
   python -c "import re; from pypdf import PdfReader; r = PdfReader('data/archive/SG/BER/<today's date>.pdf'); text = ''.join((p.extract_text() or '') for p in r.pages); normalized = re.sub(r'\s+', ' ', text); assert 'Built Environment Innovation Hub' in normalized, 'collapsed entity-group content missing from PDF — expansion step failed'; print('CONTENT CHECK OK,', len(r.pages), 'pages,', len(text), 'chars extracted')"
   ```
   (Whitespace-normalized before the substring check — Chromium's A4 text layout wraps this exact
   phrase across a line, and `pypdf`'s `extract_text()` inserts a literal newline at that wrap
   point instead of a space, which made the original un-normalized assertion false-fail during
   this task's own execution despite the content being genuinely present. See Evidence below.)
   Report the actual assertion result, not just that the command ran.
6. Stop the dev server after verification.

## Evidence

Executed by `feature-executor` (sonnet tier). First attempt reported **FAILED** — a genuinely new
finding, not an execution mistake — triaged and resolved by the orchestrating session in the same
turn (root cause was fully diagnosed by the executor itself; the fix it had already applied was
independently re-verified rather than redispatched from scratch, since re-running the corrected
content check against the executor's own already-generated PDF was sufficient evidence).

**What the first attempt found:** the code as originally specified (entity-group expansion only)
rendered a PDF with only ~1,400 characters of extractable text — the executive summary and footer
only. Root cause: `templates/report.html`'s major sections (`#sectors`, `#opportunities`,
`#competition-risks`, `#data-sources`) carry `data-aos="fade-up"` (AOS 2.3.1, loaded in
`base.html`), which sets `opacity:0` until an `IntersectionObserver` marks the element
`.aos-animate` on scroll-into-view — never triggered by a single-shot headless render with no
scrolling. `static/style.css`'s `@media print` block has no override for this. **This is a
real, pre-existing defect in the report page's print path, not something introduced by this
task** — it would affect a human clicking the existing "Export PDF" button too, if they hadn't
first scrolled through the full page. Worth flagging for `/update-context` as a newly-discovered
known issue, separate from this feature's own scope.

**Fix applied** (now the actual content of `pipeline/archive.py`, code block above updated to
match): after entity-group expansion, resize the Playwright viewport to
`document.body.scrollHeight` (measured after expansion, since that changes page height) plus a
300ms settle wait, before calling `page.pdf()` — brings every AOS-tagged section into the
observed viewport at once. Confirmed effective: extracted text length went from ~1,400 to ~25,801
characters, with real signal-card content present (e.g. "BCA has waived space rental fees...").

**Second, smaller finding:** the task's original content-check assertion (`'Built Environment
Innovation Hub' in text`, unnormalized) still failed even after the above fix — not because
content was missing, but because Chromium's A4 layout wraps that exact phrase across a line, and
`pypdf` inserts a literal `\n` at the wrap point instead of a space. Confirmed via manual
inspection that the full sentence is present verbatim (matches `data/latest_report_SG_BER.json`
exactly, just line-wrapped in the rendered PDF). Fixed by whitespace-normalizing extracted text
before the substring check (task's Verification section above updated to match).

**Final verification, re-run directly by the orchestrating session against the executor's
already-generated PDF (no regeneration needed — same file, corrected assertion only):**
```
python -c "import re; from pypdf import PdfReader; r = PdfReader('data/archive/SG/BER/2026-07-28.pdf'); text = ''.join((p.extract_text() or '') for p in r.pages); normalized = re.sub(r'\s+', ' ', text); assert 'Built Environment Innovation Hub' in normalized, '...'; print('CONTENT CHECK OK,', len(r.pages), 'pages,', len(text), 'chars extracted')"
→ CONTENT CHECK OK, 41 pages, 25801 chars extracted
```
File confirmed on disk: `data/archive/SG/BER/2026-07-28.pdf`, 767,752 bytes, 41 pages.

All other verification steps (pip install, chromium install, dev server boot, `SAVED:` path,
file-size threshold) passed on the executor's first pass — only the content-check assertion
needed the fix above.

