# Research: Feature 009 — Daily Automation + Report Archival

Not a `--thorough` run. Most of this feature is mechanical (wrapper script, a list+download view)
and didn't need research. Three things were genuinely uncertain enough to check inline before
decomposing, since getting any of them wrong would silently produce a broken or blank archived PDF
with no error — exactly the failure mode a cron job with no alerting (explicitly out of scope) would
never surface. All three were resolved with concrete evidence, not guessed.

## §1. Does `page.pdf()` respect `@media print` CSS by default?

Confirmed via a live web search against Playwright's own docs (Playwright Python API reference,
`Page.pdf()`) plus corroborating third-party guides: **`page.pdf()` uses `print` CSS media by
default** — you only need `page.emulate_media(media="screen")` if you want to *override* it to
screen styles. Nothing needs to be done to get `@media print` applied; it's the default state.

Task 002 still has the executor call `page.emulate_media(media="print")` explicitly before
`page.pdf()` anyway — defensive/explicit, not because it's required, so a future Playwright version
change to the default can't silently break this feature.

## §2. Is `page.pdf()` Chromium-only?

Confirmed, same search: **`page.pdf()` only works in headless Chromium** — Firefox and WebKit
Playwright contexts don't support it at all (this is a documented, permanent API limitation, not a
config flag). Task 002 explicitly instructs `playwright.chromium.launch()` — not `firefox` or
`webkit` — for exactly this reason.

## §3. The real gap: `@media print` alone is NOT enough to reveal collapsed entity groups

This is the one finding that materially changed Task 002's design, and is worth flagging loudly —
CONTEXT.md's framing ("reuse the print CSS/JS") turns out to require a little more precision than
"just call page.pdf()."

Read `static/style.css` directly (lines 249–258 and 421–459):

```css
.entity-group-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.35s ..., opacity 0.25s ease;
  opacity: 0;                              /* ← collapsed by default, ALL entity groups */
}
.entity-group.open .entity-group-content {
  grid-template-rows: 1fr;
  opacity: 1;                              /* ← only reachable via the `.open` class */
}

@media print {
  ...
  .entity-group-content {
    display: block !important;
    grid-template-rows: 1fr !important;    /* ← overrides display/grid-template-rows... */
  }
  /* ...but does NOT override opacity. */
}
```

Every signal on the report page starts inside a collapsed `.entity-group` (no `.open` class) until a
user clicks it. The `@media print` block forces `display: block` and `grid-template-rows: 1fr`, but
never touches `opacity` — so a naive `page.emulate_media(media="print"); page.pdf(...)` with no
other steps would produce a PDF where **every collapsed section is present in the DOM but invisible**
(`opacity: 0`), because the only rule that sets `opacity: 1` is `.entity-group.open
.entity-group-content`, which isn't media-query-gated and is never reached without the `.open` class.

The existing "Export PDF" button's own JS (`static/animations.js`'s `initPdfExport()`, lines
199–222) already knows this — its `confirmBtn` click handler explicitly adds `.open` to every
`.entity-group` before calling `window.print()` (lines 201–204). That's the real behavior this
feature needs to reuse — not the button/`window.print()` mechanics themselves, which don't translate
cleanly to headless automation (see §4), but the underlying class-toggle logic.

**Resolution, applied in Task 002:** before calling `page.pdf()`, run one `page.evaluate()` call
replicating exactly what `confirmBtn`'s handler does for group-expansion (not its checkbox-exclusion
loop, which is irrelevant here — see below):

```js
document.querySelectorAll('.entity-group').forEach(el => el.classList.add('open'));
```

The checkbox-exclusion half of that same handler (`.pdf-section-checkbox` → `.print-exclude`) does
**not** need reproducing: every checkbox in `templates/report.html` defaults to `checked` (confirmed
by reading the template, lines 120/126), and nothing in an unattended archival run ever unchecks one
— so the default DOM state already includes every section, matching what a full archival snapshot
should contain.

## §4. Why not just drive the existing "Export PDF" button and call it done?

Two reasons this feature's PDF generation calls `page.pdf()` directly instead of clicking
`#pdf-export-toggle` → `#pdf-export-confirm` (which itself calls `window.print()`):

1. `window.print()` opens the browser's native print dialog — in a headless, display-less Chromium
   process there's nothing to interact with it, and relying on it to somehow also produce the file
   Playwright wants is not how Playwright's PDF generation works. `page.pdf()` is a separate,
   dedicated CDP (Chrome DevTools Protocol) command; `window.print()` and `page.pdf()` are unrelated
   mechanisms that happen to both key off the same `@media print` CSS.
2. Driving the button also reopens the (already-hidden, `print-exclude`-tagged) options panel and
   toggles checkbox-derived `print-exclude` classes — all no-ops here since nothing is unchecked, but
   unnecessary surface area for an unattended script to depend on (e.g. if the button's `id`s or
   click-handler wiring ever change for the interactive feature, this archival path shouldn't break
   with it).

Calling `page.evaluate()` for the one-line group-expansion, then `page.pdf()` directly, is both
simpler and decoupled from the interactive button's own implementation details.

## §5. Playwright is already a pinned (transitive) dependency — not a fresh addition

Reading `requirements.txt` directly: `playwright==1.61.0` (and `patchright==1.61.2`) are **already
present** in the pinned dependency list. Neither is listed in the file's own header comment as a
"direct top-level dependency" — both are almost certainly transitive, pulled in by
`scrapling[fetchers]` (Scrapling's dynamic/stealth fetchers are themselves Playwright/Patchright-
based, which is consistent with `.context/DECISIONS.md`'s 2026-06-29 entry describing Scrapling's
tiered fetcher integration).

This means Task 001 is **not** "add a new dependency line" — it's "confirm the pinned version is
already there (it is, no edit needed to the version line itself) and update the header comment to
also list `playwright` as a direct dependency now that `pipeline/archive.py` imports it explicitly,
not just relies on it transitively through Scrapling." This is a smaller, lower-risk change than
CONTEXT.md's framing implied, and specifically avoids repeating Feature 007's original
`requirements.txt`-regeneration mistake (this dev machine still has no project-scoped `.venv` — see
`.context/STATE.md` item 10 — so a full `pip freeze` regeneration here remains a real risk; this
task deliberately does a targeted comment edit instead of a full regeneration).

Separately confirmed live on this machine: neither `playwright` nor any other project dependency
(not even `flask`) is currently importable from the bare `python`/`pip` this session's shell
resolves to (`ModuleNotFoundError` for both) — there is no active project environment here at all,
consistent with the standing "no `.venv` on this machine" note. Every task below that needs to boot
`app.py` or import `pipeline.archive` locally must install its own minimal working set first
(`flask`, `python-dotenv`, `playwright` — not a full `pip install -r requirements.txt`, which would
also pull in `chromadb`/`torch`/`sentence-transformers`/`scrapling` unnecessarily for these narrow
checks) — this is spelled out explicitly in each task's Verification section rather than assumed.

## §6. Login mechanism for the headless render

Read `app.py` and `templates/login.html` directly rather than guessing. There's no API-token or
cookie-injection path — auth is a plain session cookie set by `POST /login` with a `password` form
field (`<input id="password" name="password">`, submit via `<button type="submit">`, no CSRF
token). The simplest, most robust approach — and the one Task 002 uses — is to drive this exact
flow with Playwright (`page.goto("/login")` → `page.fill("#password", ...)` → `page.click("button
[type=submit]")`), same as a real user, rather than trying to construct or replay a signed Flask
session cookie by hand. The viewer password (not admin — read-only archival needs no admin rights)
is read directly from `data/viewer_password.txt`, falling back to the same hardcoded default
(`"Silversea"`) `app.py`'s own `_get_viewer_password()` uses if the file doesn't exist yet — Task
002 duplicates this constant deliberately rather than importing `app.py` (importing it would trigger
Flask app construction, secret-key-file creation, etc. as a side effect of a simple password read).
