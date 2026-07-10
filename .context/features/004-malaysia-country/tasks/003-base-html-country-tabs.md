# Task 003: Malaysia (and Vietnam) real country-tab links in `templates/base.html`

**Status:** done

## Files

- `templates/base.html` (modify only — the country-tabs block and the domain-tabs block, current
  lines 109-155)

## What to do

**Background — important, read before editing.** This feature's branch (`feature/004-malaysia-
country`) was cut from `main` at commit `168810e`, which predates `feature/003-vietnam-country`'s
own fix to this exact block. As a result, on *this* branch, `base.html` still has the *old*
structure: Singapore is a static highlighted `<span>` (not a link), and Malaysia/Vietnam/Indonesia
are all inert, grayed-out `cursor-not-allowed` `<span>`s. The domain tabs below them link to
`/?domain=EDU` etc. with no `country` param at all.

Vietnam's own branch already fixed this (turning SG and VN into real links, adding `&country=` to
the domain tabs) — but since that fix hasn't merged to `main` yet, it doesn't exist on this
branch. **This task must reproduce Vietnam's already-decided final state exactly (not just bolt
Malaysia on top of the current broken state)** — i.e. fix SG, VN, *and* MY together — so this
branch is internally correct on its own regardless of which branch merges to `main` first. When
Vietnam's and Malaysia's branches eventually both merge, expect a small, easily-resolved textual
merge conflict on this block (both branches converge on the same final content for SG/VN/MY, so
resolution is trivial, not a real design conflict — this is expected and already noted in
CONTEXT.md).

**Replace the whole country-tabs + domain-tabs block (current lines 109-155) with:**

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
          <a href="/?country=MY&domain={{ _domain }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _country == 'MY' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _country == 'MY' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _country == 'MY' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Malaysia
          </a>
          <a href="/?country=VN&domain={{ _domain }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _country == 'VN' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _country == 'VN' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _country == 'VN' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Vietnam
          </a>
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

**Known, accepted limitation — read before writing verification steps.** On this branch, `app.py`
does not read a `?country=` query param anywhere (confirmed: `report()`'s `domain_filename` is
hardcoded to `f"latest_report_SG_{domain}.json"`, and no route passes `current_country` into
`render_template`) — that wiring is Vietnam's own `app.py` change (`feature/003-vietnam-country`'s
Task 003), and per CONTEXT.md's Global Constraints, `app.py` is explicitly out of scope for this
Malaysia feature. This means `_country` will always render as `'SG'` (the `|default('SG')`
fallback) on this branch alone, even when the `MY` or `VN` link is clicked — the new links will be
present and structurally correct, but won't actually change which country's report is displayed
until this branch merges with Vietnam's `app.py` changes. This is intentional and expected (see
CONTEXT.md's "Branching" decision and this feature's dispatch notes) — verify the template change
itself, not end-to-end country-switching behavior, which is out of this task's reach on this
branch.

## Interfaces

- Introduces template-level reads of a `current_country` context variable (with `|default('SG')`
  fallback, matching the existing `current_domain|default('BER')` pattern already used by routes
  that don't pass it, e.g. `login.html`/`admin.html`). No route on this branch currently passes
  `current_country` — that remains true after this task, per the scope note above.

## Constraints

- Match the existing Tailwind/glass-card visual pattern exactly — same classes, same
  `border-color`/`background` inline-style convention already used by the domain tabs, per
  CLAUDE.md's "match existing patterns" constraint. Do not introduce a new tab component style.
- Indonesia stays an inert `<span>` placeholder — do not turn it into a link or add
  `?country=ID` handling; Indonesia has no data and is out of this feature's scope.
- Do not change the dark-zone wrapper, nav bar, or hero block — only the two tab `<div>`s described
  above.
- Do not touch `app.py`, `main.py`, or any other template — this task is scoped to
  `templates/base.html` only, per CONTEXT.md's Global Constraints.
- Real-browser visual QA (pixel-level check that the tabs render correctly) is an Alfonso-owned
  manual checkpoint per this project's established pattern (see STATE.md's open items) — this
  task's job is correct Jinja logic and matching Tailwind class usage, not pixel verification.

## Verification

No LLM call needed — Flask-side template change, verify by booting the app and curling routes:

1. Start the Flask app, then fetch `/` (default route, `current_country` unset anywhere) and
   confirm the returned HTML contains `href="/?country=SG&domain=`, `href="/?country=MY&domain=`,
   and `href="/?country=VN&domain=` links (not `<span>`s for any of the three).
2. Confirm the domain tab links now include `&country=` — check the HTML for
   `href="/?domain=EDU&country=SG"` (since `_country` defaults to `SG` on this branch, per the
   scope note above — do not expect `?country=MY` to appear here even after fetching `/?country=MY`,
   since `app.py` never reads that param on this branch).
3. Confirm the default active-tab highlighting: on the `/` response, Singapore's `<a>` tag shows
   the "active" branch (`text-white`, the green border-color), since `_country` defaults to `'SG'`
   with no route passing anything else. Malaysia's and Vietnam's `<a>` tags should show the
   "inactive" branch (`text-gray-500`) in this same response.
4. Confirm Indonesia is still a plain `<span>` (not `<a href=`) in the response — it must not have
   become clickable.
5. Confirm the app boots without a `TemplateSyntaxError` when hitting `/`, `/internals`, `/login`
   (steps 1-4 already exercise `/`; also hit `/internals` and `/login` once each to confirm no
   syntax error on routes that don't pass `current_domain`/`current_country` at all).

## Model tier

mid — the `{% set %}` reordering and the domain-tabs `&country=` addition require understanding
why the existing structure needs restructuring (not just appending new markup), but the target
HTML is fully specified above.

## Depends on

None — isolated to `templates/base.html`, no data dependency on Task 001/002 (`config/sources.json`)
or Task 004 (`data/company_context.md`). Can run in parallel with those.

## Evidence

Executor report (DONE):
- `/` renders (200) with real `<a>` links for SG/MY/VN, Indonesia still plain `<span>`.
- Domain tab links carry `&country=SG` (correctly defaults, since `app.py` doesn't read `?country=` on this branch — known, documented limitation, not a bug).
- Singapore shows "active" styling by default; MY/VN show "inactive" styling.
- `/`, `/internals`, `/login` all boot without `TemplateSyntaxError`.

Files changed: `templates/base.html` only.
