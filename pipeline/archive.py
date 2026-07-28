# pipeline/archive.py — Headless PDF archival of a report page via Playwright + Chromium.
#
# Reuses the *existing* browser print CSS (static/style.css's `@media print` block) rather than
# building a second rendering path. `@media print` alone isn't enough to reveal collapsed entity
# groups (they default to opacity:0, which the print media query doesn't override), so this module
# also replicates the one-line group-expansion step that static/animations.js's "Export PDF" button
# already does before printing.
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
            # so its content isn't opacity:0 in the printed output.
            page.evaluate(
                "document.querySelectorAll('.entity-group').forEach(el => el.classList.add('open'))"
            )

            # Second, previously-undocumented opacity trap found during this task's own
            # verification (distinct from the entity-group one above): every major report
            # section (`base.html` loads AOS 2.3.1; report.html tags each section
            # `data-aos="fade-up"`) sits at opacity:0 until AOS's IntersectionObserver marks it
            # `.aos-animate` on scroll-into-view. A single-viewport headless render never scrolls,
            # so every section below the fold (sectors, opportunities, competition-risks,
            # data-sources) printed blank even with the entity-group fix in place — confirmed via
            # a failing content-check assertion during this task's own verification. Resizing the
            # viewport to the page's full scroll height (measured after the groups above are
            # expanded, since that changes page height) brings every section into AOS's observed
            # viewport at once, without touching report.html/animations.js/style.css.
            full_height = page.evaluate("document.body.scrollHeight")
            page.set_viewport_size({"width": 1280, "height": full_height})
            page.wait_for_timeout(300)

            # page.pdf() already defaults to `print` CSS media — set it explicitly anyway so this
            # doesn't silently break on a future Playwright version.
            page.emulate_media(media="print")
            page.pdf(path=out_path, format="A4", print_background=True)
        finally:
            browser.close()

    return out_path
