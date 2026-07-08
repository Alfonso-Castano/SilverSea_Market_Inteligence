# Task 007: Admin country selector + `approve()` disk-reread fix

**Status:** done

## Files

- `config/sources.py` (modify — add one function)
- `pipeline/source_suggestions.py` (modify)
- `templates/admin.html` (modify)
- `app.py` (modify — `admin()` and `approve_source()` routes only)

## What to do

**Background:** `pipeline/source_suggestions.py`'s `approve()` currently imports the module-level
`COUNTRIES` singleton (created once when `config/sources.py` is first imported) and mutates that
same in-memory list in place before calling `save_sources()`. If `sources.json` on disk has
changed since the process started, that change is silently lost, because `approve()` is writing
back a stale in-memory snapshot, not a fresh read. Separately, the admin UI has no way to pick
which country's source list a suggestion gets appended to — `approve()` defaults to `"SG"`
unconditionally.

**1. `config/sources.py` — add a fresh-read function.** Add a new public function that re-reads
the file from disk on every call (reusing the existing private `_load()`):
```python
def load_sources():
    """Fresh read of sources.json from disk — use this instead of the cached COUNTRIES
    singleton anywhere a read-modify-write needs to see the current on-disk state."""
    return _load()
```
Add this directly after the existing `_load()` function definition, before `save_sources()`.
Leave `_load()`, `save_sources()`, and the module-level `COUNTRIES = _load()` line completely
unchanged — `COUNTRIES` remains valid for `main.py`'s existing use (a one-shot read at pipeline
start), this is purely an additive function for the admin-approval code path.

**2. `pipeline/source_suggestions.py` — use the fresh read in `approve()`.** Change the import
and the function body:
```python
from config.sources import load_sources, save_sources
```
(remove `COUNTRIES` from this import — nothing else in this file uses it). In `approve()`,
replace:
```python
    countries = COUNTRIES
    for country in countries:
        if country["code"] == country_code:
            country["sources"].append(new_source)
            break
    save_sources(countries)
```
with:
```python
    countries = load_sources()
    for country in countries:
        if country["code"] == country_code:
            country["sources"].append(new_source)
            break
    save_sources(countries)
```
The `country_code="SG"` default parameter on `approve()` stays as a fallback, but the admin route
(step 4 below) will now pass an explicit value from the form.

**3. `templates/admin.html` — add a country `<select>` to the approve form.** Inside the existing
approve `<form>` (currently lines 33-70), add a country field alongside the existing sector/domain
fields, before the submit button. Since only SG is currently populated with real sources, hardcode
the one option for now (this is a stopgap the same way the EDU dual-tagging is a stopgap — not a
full multi-country UI build-out):
```html
          <div class="flex-1 min-w-[120px]">
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
            <select name="country" required
              class="w-full rounded-lg border border-border-card dark:border-dark-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-accent/40 focus:border-green-accent dark:bg-dark-bg dark:text-gray-200">
              <option value="SG" selected>Singapore (SG)</option>
            </select>
          </div>
```
Place this new `<div>` between the existing "Sector" `<div>` and "Domain" `<div>` (or immediately
after "Domain", before the submit `<button>`) — either position is fine, just keep it inside the
same `<form>` so it submits together with sector/domain.

**4. `app.py` — read the country field and pass it through.** `approve_source()` (currently lines
206-213) currently doesn't read a `country` field at all. Update it:
```python
@app.route("/admin/sources/<filename>/approve", methods=["POST"])
def approve_source(filename):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    sector = request.form.get("sector")
    domain = request.form.getlist("domain") or ["GENERAL"]
    country = request.form.get("country", "SG")
    source_suggestions.approve(filename, sector, domain, country_code=country)
    return redirect(url_for("admin"))
```

## Interfaces

- New public function `config.sources.load_sources() -> list` (returns the same shape as the
  existing `COUNTRIES` list — a list of country dicts).
- `pipeline.source_suggestions.approve(filename, sector, domain, country_code="SG")` — signature
  unchanged, only its internal implementation changes (now calls `load_sources()` instead of
  using the imported `COUNTRIES` name).
- `app.approve_source(filename)` — now reads one additional form field (`country`), no route
  signature change (still takes `filename` from the URL).

## Constraints

- Flask + Jinja2 + Tailwind CDN, no build step — the new `<select>` must use the same Tailwind
  utility classes as the existing sector `<select>` in the same form, for visual consistency
  (visual QA is an Alfonso-owned manual checkpoint, but the class list should already match the
  existing pattern so there's nothing left for him to flag structurally).
- Do not add a general multi-country admin UI (e.g. dynamically listing all `COUNTRIES` codes) —
  CONTEXT.md scopes this to a country selector stopgap, and only SG has real data; hardcoding the
  one option is intentional, not a shortcut to fix later in this round.
- Do not change `config/sources.py`'s `_load()` or `save_sources()` internals — only add the new
  `load_sources()` function.
- This task's `app.py` edits are confined to `admin()`/`approve_source()` — do not touch
  `login()`, `receive_feedback()`, or `add_cors()` (those are owned by task 001).

## Verification

No LLM call needed:

1. `python -c "from config.sources import load_sources; print(len(load_sources()[0]['sources']))"`
   (or `py -c "..."`) — must succeed and print a source count matching the current
   `config/sources.json` state.
2. Confirm `load_sources()` actually re-reads from disk (not cached): run the above, then
   externally modify `config/sources.json` (e.g. touch a harmless field via a throwaway script),
   call `load_sources()` again in a fresh Python process, and confirm it reflects the change —
   demonstrating it isn't returning a stale import-time singleton. Revert any test modification
   afterward.
3. Exercise `pipeline.source_suggestions.approve()` end-to-end against a throwaway pending-source
   JSON file (don't use a real pending suggestion): create a temp file in `data/pending_sources/`
   matching the expected suggestion schema, call `approve(filename, "customers", ["GENERAL"],
   country_code="SG")`, and confirm (a) it appends to `config/sources.json`'s SG country's
   `sources` array, (b) the file moves to `data/pending_sources/processed/`. Then manually remove
   the test source you just added from `config/sources.json` and confirm the file is still valid
   JSON afterward.
4. Start the Flask app (or use `app.test_client()`), log in as admin (requires `ADMIN_PASSWORD`
   to be set — if it isn't set in this environment, verify via direct template rendering instead:
   `render_template("admin.html", pending=[])` and confirm no Jinja error, then check the
   rendered HTML string contains `name="country"` and `value="SG"`).
5. Confirm `app.py`'s `approve_source()` route now reads `request.form.get("country", "SG")` and
   passes it as `country_code` — grep the file to confirm the exact call signature.

## Model tier

mid — multi-file coordination (4 files) with one new function signature; well-specified but
requires correctly wiring the new parameter end-to-end (template → route → suggestions module →
sources loader) without breaking the existing sector/domain flow.

## Depends on

Task 001 (`001-auth-bypass-and-feedback-hardening.md`) — both tasks modify `app.py`; task 001 must
land first so this task edits the post-fix version of the file and there is no risk of one task's
diff silently overwriting the other's.

## Evidence

**Status: DONE**

- `load_sources()` added to `config/sources.py`, unchanged `_load()`/`save_sources()`/`COUNTRIES`.
- `pipeline/source_suggestions.py`'s `approve()` now calls `load_sources()` instead of the
  `COUNTRIES` singleton — proven via a live disk-mutation test: `COUNTRIES` stayed stale after an
  external write, `load_sources()` reflected it immediately (re-verified independently, count
  clean at 62 with no leftover test artifacts).
- `approve()` exercised end-to-end against a throwaway pending-source file: source appended to
  SG's array, file moved to `processed/`, both cleaned up afterward.
- `templates/admin.html` renders with `name="country"` present (re-confirmed via grep).
- `git diff app.py` confined exactly to `approve_source()` — `login()`, `receive_feedback()`,
  `add_cors()` (task 001's territory) untouched, re-confirmed independently.
