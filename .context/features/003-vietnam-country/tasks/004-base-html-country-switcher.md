# Task 004: Working country switcher in `templates/base.html`

**Status:** done

## Files

- `templates/base.html` (modify only — the country-tabs block and the domain-tabs block)

## What to do

**Background:** `base.html` currently renders four static country "tabs" (lines 109-128) —
Singapore shown as the only active/highlighted one (a plain `<span>`, not a link), Malaysia/
Vietnam/Indonesia shown as grayed-out, `cursor-not-allowed` placeholder `<span>`s. Now that
Task 003 wires `_country_mode()` into `/` and `/internals` and passes `current_country` into the
template context, Singapore and Vietnam should become real, working links — Malaysia and
Indonesia stay as inert placeholders (no MY/ID data exists yet; this feature is VN-only per
CONTEXT.md's explicit scope).

Separately, the existing domain tabs (lines 130-155) link to `/?domain=EDU` etc. with no
`country` param at all — meaning clicking a domain tab while viewing `?country=VN` would silently
reset the view back to the default `SG` country. This task also fixes that, since a country
switcher that gets clobbered by every domain-tab click isn't actually usable.

**Replace the whole country-tabs + domain-tabs block (current lines 109-155)** with:

```html
    {% set _country = current_country|default('SG') %}
    {% set _domain = current_domain|default('BER') %}

    <!-- Country tabs -->
    <div class="border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex gap-3 py-2">
          <a href="/?country=SG&domain={{ _domain }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _country == 'SG' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _country == 'SG' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _country == 'SG' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Singapore
          </a>
          <a href="/?country=VN&domain={{ _domain }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _country == 'VN' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _country == 'VN' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _country == 'VN' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Vietnam
          </a>
          <span class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium text-gray-500 cursor-not-allowed" style="background: rgba(255,255,255,0.03);">
            Malaysia
          </span>
          <span class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium text-gray-500 cursor-not-allowed" style="background: rgba(255,255,255,0.03);">
            Indonesia
          </span>
        </div>
      </div>
    </div>

    <!-- Domain tabs -->
    <div class="border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex gap-3 py-2">
          <a href="/?domain=EDU&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'EDU' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'EDU' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'EDU' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Education &amp; EdTech
          </a>
          <a href="/?domain=BER&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'BER' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'BER' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'BER' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Built Environment
          </a>
          <a href="/?domain=GENERAL&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'GENERAL' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'GENERAL' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'GENERAL' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            General
          </a>
        </div>
      </div>
    </div>
```

Note the key structural change: both `{% set %}` lines now sit *above* both tab blocks (previously
`_domain` was set only immediately before the domain-tabs block) so both blocks can reference both
variables. `templates/report.html` and `templates/internals.html` need no changes — they extend
`base.html` and inherit this block automatically; do not touch either of those files in this task.

## Interfaces

None new — this task consumes the `current_country` template variable Task 003 introduces
(`|default('SG')` handles any page/route that doesn't pass it, exactly like the existing
`current_domain|default('BER')` pattern already does for `login.html`/`admin.html`, which don't
pass either variable).

## Constraints

- Match the existing Tailwind/glass-card visual pattern exactly — same classes, same
  `border-color`/`background` inline-style convention already used by the domain tabs, per
  CLAUDE.md's "match existing patterns" constraint. Do not introduce a new tab component style.
- Malaysia and Indonesia stay as inert `<span>` placeholders — do not turn them into links or
  add `?country=MY`/`?country=ID` handling; those countries have no data and are out of this
  feature's scope.
- Do not change the dark-zone wrapper, nav bar, or hero block — only the two tab `<div>`s described
  above.
- Real-browser visual QA (pixel-level check that the tabs render correctly) is an Alfonso-owned
  manual checkpoint per this project's established pattern (see STATE.md's open items) — this
  task's job is correct Jinja logic and matching Tailwind class usage, not pixel verification.

## Verification

No LLM call needed — Flask-side template change, verify by booting the app and curling routes:

1. Start the Flask app, then fetch `/?country=SG` and `/?country=VN` (e.g. via
   `requests.get` or `app.test_client()`), and confirm the returned HTML contains both
   `href="/?country=SG&domain=` and `href="/?country=VN&domain=` links (not `<span>`s) — a
   simple substring check on the response body is sufficient.
2. Confirm the domain tab links now include `&country=` — check the HTML for
   `href="/?domain=EDU&country=` etc.
3. Confirm the active-tab highlighting logic: fetch `/?country=VN` and check the Vietnam link's
   `class`/`style` attributes match the "active" branch (`text-white`, the green border-color) —
   e.g. `'href="/?country=VN&domain=BER" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors\n            text-white"' in response.text` (adjust
   whitespace matching to however Jinja actually renders it — check the real output rather than
   assuming exact whitespace).
4. Confirm Malaysia/Indonesia are still plain `<span>` (not `<a href=`) in the response — they
   must not have become clickable.
5. `py -c "import ast"`-style syntax check doesn't apply to Jinja — instead confirm the app boots
   without a `TemplateSyntaxError` when hitting any route that renders `base.html` (steps 1-4
   already exercise this).

## Model tier

mid — the `{% set %}` reordering and the domain-tabs `&country=` addition require understanding
why the existing structure needs restructuring (not just appending new markup), but the target
HTML is fully specified above.

## Depends on

Task 003 (`003-app-country-routing-and-run-metadata-scoping.md`) — needs `current_country` to
actually be passed into the template context by `/` and `/internals` for the switcher to be
functionally correct end-to-end (the template itself would still render with the
`|default('SG')` fallback even without Task 003, but verification steps 1-3 need the real
`?country=VN` query param to actually reach the template, which only happens once Task 003 lands).

## Evidence

Executor report (DONE):
- `GET /?country=SG`, `/?country=VN`, `/internals?country=VN` all → 200.
- SG/VN links confirmed as real `<a href="/?country=...&domain=...">` (not `<span>`), Malaysia/Indonesia confirmed still inert `<span>` (no link).
- Domain tab links confirmed carrying `&country=` (EDU/BER/GENERAL all checked).
- Active-tab styling on `/?country=VN` confirmed (`text-white`, green border-color) via actual rendered snippet.
- No `TemplateSyntaxError` on any route.

Note: verified via `session_transaction()` direct session auth rather than reading `viewer_password.txt` through the real login form (sandbox blocked reading the password file as a credential-materialization guard) — same end-to-end template behavior confirmed either way.

Files changed: `templates/base.html` only.
