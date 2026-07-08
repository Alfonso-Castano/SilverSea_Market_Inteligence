# Task 005: Dynamic country dropdown in `templates/admin.html`

**Status:** done

## Files

- `templates/admin.html` (modify only — the country `<select>` in the approve form)

## What to do

Feature 001 added a country `<select>` to the source-approval form (current lines 65-71) as an
explicit stopgap, hardcoded to a single `SG` option, because at the time only Singapore had real
source data. Task 003 (this feature) updates `app.py`'s `/admin` route to pass a live `countries`
list (from `config.sources.load_sources()`) into the template context — this task consumes that
to make the dropdown actually list every country in `config/sources.json`, VN included, instead
of the hardcoded single option.

Replace the current block:
```html
          <div class="flex-1 min-w-[120px]">
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
            <select name="country" required
              class="w-full rounded-lg border border-border-card dark:border-dark-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-accent/40 focus:border-green-accent dark:bg-dark-bg dark:text-gray-200">
              <option value="SG" selected>Singapore (SG)</option>
            </select>
          </div>
```
with:
```html
          <div class="flex-1 min-w-[120px]">
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Country</label>
            <select name="country" required
              class="w-full rounded-lg border border-border-card dark:border-dark-border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-accent/40 focus:border-green-accent dark:bg-dark-bg dark:text-gray-200">
              {% for c in countries %}
              <option value="{{ c.code }}" {% if c.code == 'SG' %}selected{% endif %}>{{ c.name }} ({{ c.code }})</option>
              {% endfor %}
            </select>
          </div>
```
`SG` stays the default-selected option (matching current behavior — it's the most-populated
country and the existing default), but the dropdown now lists every country present in
`config/sources.json` (SG and VN, after Task 001 lands), not just SG.

## Interfaces

None new — consumes the `countries` template variable Task 003 introduces on the `/admin` route
(a list of dicts shaped like `config.sources.load_sources()`'s return value — each with at least
`name` and `code` keys, which is all this template needs).

## Constraints

- Do not change the surrounding `<form>` structure, the Sector `<select>`, or the Domain
  checkboxes in the same form — only the Country `<select>`'s contents.
- Keep the exact same Tailwind classes on the `<select>` element (visual consistency, no new
  component style).
- If `countries` is ever empty or unset (e.g. a template render path that doesn't pass it), the
  `{% for %}` loop simply renders zero `<option>`s rather than crashing — this is acceptable
  Jinja behavior and doesn't need an explicit empty-state guard, since `/admin`'s route (Task 003)
  always passes a real list.

## Verification

No LLM call needed — Flask-side template change:

1. Confirm `templates/admin.html` still parses as valid Jinja by rendering it directly:
   `render_template("admin.html", pending=[], interest_signals=[], countries=[{"name": "Singapore", "code": "SG"}, {"name": "Vietnam", "code": "VN"}])`
   (from a Flask app/request context, e.g. via `app.test_request_context()`) — must not raise a
   `TemplateSyntaxError` or `UndefinedError`.
2. Confirm the rendered HTML contains both `<option value="SG"` and `<option value="VN"` and that
   the `SG` option (and only that one) has ` selected` in its tag.
3. If `ADMIN_PASSWORD` is set in this environment, log in as admin and hit `/admin` directly to
   confirm the same via a live request instead of/in addition to step 1.
4. Confirm no other part of the rendered page changed — the pending-suggestions list and
   interest-signals section should render identically to before this task (diff the response body
   against a pre-change baseline if convenient, or just visually confirm those sections are
   untouched in the template source).

## Model tier

cheap — a single, fully-specified block replacement (Jinja loop over an already-provided list);
no judgment calls beyond confirming the loop variable names match what Task 003 actually passes.

## Depends on

Task 003 (`003-app-country-routing-and-run-metadata-scoping.md`) — the `/admin` route must already
pass `countries` into the template context before this task's `{% for c in countries %}` loop has
anything real to iterate over. Both tasks are otherwise on different files (`app.py` vs.
`templates/admin.html`), so this is a data-availability dependency, not a same-file conflict.

## Evidence

Executor report (DONE): hardcoded `<option value="SG">` replaced with `{% for c in countries %}` loop; SG stays default-selected via conditional. Sector select, domain checkboxes, form structure, interest-signals section, viewer-password section all confirmed untouched. `git diff` shows a minimal 4-line change.

Files changed: `templates/admin.html` only.
