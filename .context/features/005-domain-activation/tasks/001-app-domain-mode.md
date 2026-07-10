# Task 001: Expand `app.py`'s `_domain_mode()` to 8 valid domains

**Status:** done
**Depends on:** none
**Model tier:** cheap — the exact code change is fully specified below; the executor's job is transcription plus running the verification commands.

## Files
- Modify: `app.py` (lines 81-83, `_domain_mode()` only)

## What to do

Current code (lines 81-83):
```python
def _domain_mode():
    domain = request.args.get("domain", "BER")
    return domain if domain in ("EDU", "BER", "GENERAL") else "BER"
```

Change the validated tuple to include the 5 new domains:
```python
def _domain_mode():
    domain = request.args.get("domain", "BER")
    return domain if domain in ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS") else "BER"
```

That is the entire change — one line. Do not touch `_demo_mode()`, `_country_mode()`, or the `report()` route body below it.

## Interfaces

- `_domain_mode()` return contract unchanged (still returns a string, still defaults to `"BER"` on
  any invalid/missing value) — only the accepted set grows. No caller signature changes, so
  `templates/base.html`'s tab links (Task 002) and `templates/admin.html`'s checkboxes (Task 003)
  need no coordination with this task beyond using the same 8 domain codes.

## Constraints

- Do not change the default value (`"BER"`) or the fallback behavior for invalid domains.
- Do not touch any other function in `app.py`.

## Verification

Run from the repo root (`c:\Users\alfon\SilverSea\SilverSea_Market_Inteligence-domains`):

```
py -c "
from app import app, _domain_mode
with app.test_request_context('/?domain=RCC'):
    assert _domain_mode() == 'RCC'
with app.test_request_context('/?domain=PSS'):
    assert _domain_mode() == 'PSS'
with app.test_request_context('/?domain=MFG'):
    assert _domain_mode() == 'MFG'
with app.test_request_context('/?domain=HLS'):
    assert _domain_mode() == 'HLS'
with app.test_request_context('/?domain=CTE'):
    assert _domain_mode() == 'CTE'
with app.test_request_context('/?domain=BER'):
    assert _domain_mode() == 'BER'
with app.test_request_context('/?domain=BOGUS'):
    assert _domain_mode() == 'BER'
print('OK')
"
```

Must print `OK` with no `AssertionError` and no import error. Importing `app` is safe here — no LLM
calls happen at import time (only Flask app construction and local file reads).

## Evidence

Executor report (DONE): `_domain_mode()` now validates 8 codes, default/fallback unchanged. All 7 assertions passed (RCC/PSS/MFG/HLS/CTE/BER + invalid→BER fallback). One-line diff, `app.py` only.
