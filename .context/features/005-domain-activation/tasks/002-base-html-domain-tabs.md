# Task 002: Expand `templates/base.html` domain tabs from 3 to 8

**Status:** done
**Depends on:** none
**Model tier:** cheap — exact markup for all 5 new tabs is provided below, matching the existing
pattern byte-for-byte except for the domain code/label; the executor's job is transcription plus
verification.

## Files
- Modify: `templates/base.html` (lines 142-165, the "Domain tabs" block only)

## What to do

**1. Add `flex-wrap` to the tabs container** so it wraps to additional rows on narrow viewports
instead of overflowing. Current (line 144):
```html
        <div class="flex gap-3 py-2">
```
New:
```html
        <div class="flex gap-3 py-2 flex-wrap">
```

**2. Insert 5 new tab links** after the existing `General` tab (which ends at line 162 with `</a>`)
and before the closing `</div>` (line 163). Insert exactly this block, matching the existing
EDU/BER/GENERAL tabs' pattern (same classes, same active/inactive conditional styling via
`{% if _domain == '<CODE>' %}`):

```html
          <a href="/?domain=RCC&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'RCC' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'RCC' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'RCC' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Retail & Consumer Goods
          </a>
          <a href="/?domain=HLS&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'HLS' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'HLS' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'HLS' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Healthcare & Life Sciences
          </a>
          <a href="/?domain=MFG&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'MFG' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'MFG' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'MFG' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Manufacturing & Industry 4.0
          </a>
          <a href="/?domain=CTE&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'CTE' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'CTE' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'CTE' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Culture & Tourism
          </a>
          <a href="/?domain=PSS&country={{ _country }}" class="glass-card inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium transition-colors
            {% if _domain == 'PSS' %}text-white{% else %}text-gray-500 hover:text-gray-300{% endif %}"
            style="{% if _domain == 'PSS' %}border-color: rgba(45,106,79,0.6);{% else %}background: rgba(255,255,255,0.03);{% endif %}">
            <span class="w-2 h-2 rounded-full inline-block {% if _domain == 'PSS' %}bg-green-300{% else %}bg-white/20{% endif %}"></span>
            Public Sector & Smart Cities
          </a>
```

Order after this change: EDU, BER, GENERAL, RCC, HLS, MFG, CTE, PSS.

## Interfaces

- Consumes: `_domain` (already set at line 110 via `{% set _domain = current_domain|default('BER') %}`)
  and `_country` (line 109) — both pre-existing template variables, unchanged by this task.
- Consumes the 8-value domain set now validated by `app.py`'s `_domain_mode()` (Task 001) — this
  task does not depend on Task 001 having run first (the markup is self-contained and correct
  regardless of ordering), but both must land before the tabs are meaningfully clickable end-to-end.

## Constraints

- Do not touch the country tabs block (lines ~112-139) above the domain tabs.
- Do not touch anything below line 165 (`{% block hero %}{% endblock %}` and beyond).
- Do not change the existing EDU/BER/GENERAL tabs' markup — only add the container's `flex-wrap`
  class and the 5 new `<a>` blocks.
- No new CSS files, no new color variables — reuse the exact same `rgba(45,106,79,0.6)` accent used
  by every existing tab (this project's convention is a single active-tab color, not per-domain
  colors — do not invent per-domain accent colors here).

## Verification

Run from the repo root:

```
py -c "
from app import app
c = app.test_client()
with c.session_transaction() as sess:
    sess['authenticated'] = True
    sess['role'] = 'viewer'
resp = c.get('/?domain=RCC&country=VN')
assert resp.status_code == 200, resp.status_code
html = resp.get_data(as_text=True)
for code in ['RCC', 'HLS', 'MFG', 'CTE', 'PSS']:
    assert f'domain={code}' in html, code
assert 'flex-wrap' in html
print('OK')
"
```

Must print `OK`. This boots the Flask app in-process (no server needed) and renders the real
template end-to-end with a session pre-authenticated as viewer, confirming all 8 domain codes
appear as tab links and the wrap class is present. No LLM call involved (Groq quota untouched) — VN
may have no report file yet for the `RCC` domain, which is fine; the template must render the tab
bar regardless of whether report data exists (same as the existing EDU/BER/GENERAL behavior for a
domain with no data yet).

## Evidence

Executor report (DONE): `flex-wrap` added, 5 new tab links inserted matching exact existing pattern. Confirmed all 5 domain codes present as links, `flex-wrap` present, `/?domain=RCC&country=VN` renders 200. `templates/base.html` only.
