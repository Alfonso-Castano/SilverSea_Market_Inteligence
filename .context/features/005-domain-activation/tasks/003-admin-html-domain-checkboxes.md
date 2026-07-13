# Task 003: Expand `templates/admin.html` domain checkboxes from 3 to 8

**Status:** done
**Depends on:** none
**Model tier:** cheap — exact markup for all 5 new checkboxes is provided below, matching the
existing pattern byte-for-byte except for the domain code; the executor's job is transcription plus
verification.

## Files
- Modify: `templates/admin.html` (lines 48-63, the source-approval form's "Domain" checkbox group
  only)

## What to do

Current block (lines 48-63):
```html
            <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Domain</label>
            <div class="flex gap-3 pt-1.5">
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="BER" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                BER
              </label>
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="EDU" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                EDU
              </label>
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="GENERAL" checked class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                GENERAL
              </label>
            </div>
```

Insert 5 new `<label>` blocks after the `GENERAL` one and before the closing `</div>` (line 62),
matching the same pattern exactly (no `checked` attribute — only `GENERAL` is pre-checked by
existing design, leave that alone):

```html
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="RCC" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                RCC
              </label>
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="HLS" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                HLS
              </label>
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="MFG" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                MFG
              </label>
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="CTE" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                CTE
              </label>
              <label class="inline-flex items-center gap-1.5 text-sm text-gray-600 dark:text-gray-300 cursor-pointer">
                <input type="checkbox" name="domain" value="PSS" class="rounded border-border-card text-green-accent focus:ring-green-accent/40" />
                PSS
              </label>
```

## Interfaces

- Consumes: nothing new — `approve_source()` in `app.py` (line ~273) already reads
  `request.form.getlist("domain") or ["GENERAL"]`, which works unchanged for any number of checkbox
  values. No `app.py` change needed for this task.

## Constraints

- Do not add `flex-wrap` to this checkbox row's container — CONTEXT.md scopes the `flex-wrap`
  addition specifically to `templates/base.html`'s domain tabs, not this form. Leave
  `<div class="flex gap-3 pt-1.5">` exactly as-is.
- Do not touch the `checked` attribute on the `GENERAL` checkbox, or any other part of the
  source-approval form (sector dropdown, name/url fields, submit button) above or below this block.

## Verification

Run from the repo root:

```
py -c "
from app import app
c = app.test_client()
with c.session_transaction() as sess:
    sess['authenticated'] = True
    sess['role'] = 'admin'
resp = c.get('/admin')
assert resp.status_code == 200, resp.status_code
html = resp.get_data(as_text=True)
for code in ['RCC', 'HLS', 'MFG', 'CTE', 'PSS']:
    assert f'value=\"{code}\"' in html, code
print('OK')
"
```

Must print `OK`. This boots the Flask app in-process with a session pre-authenticated as admin and
renders `/admin` end-to-end, confirming all 5 new checkbox values are present in the rendered HTML.
No LLM call involved.

## Evidence

Executor report (DONE): 5 new checkboxes inserted, no `checked` attribute on any, GENERAL's checked state untouched, container's `flex-wrap`-free class untouched. Confirmed all 5 values render on `/admin`. `templates/admin.html` only.
