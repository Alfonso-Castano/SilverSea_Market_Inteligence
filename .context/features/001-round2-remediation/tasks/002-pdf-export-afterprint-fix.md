# Task 002: Fix PDF-export afterprint bug (`static/animations.js`)

## Files

- `static/animations.js` (modify only)

## What to do

`initPdfExport()`'s `confirmBtn` click handler (currently lines 199-220) toggles `print-exclude`
on section elements via an untracked `querySelectorAll` loop, then the `afterprint` restore
handler strips `print-exclude` from *every* element carrying that class — including
`#pdf-export-panel`, which carries `print-exclude` permanently in the HTML
(`templates/report.html` line 111) as its own always-on self-hiding mechanism, not something the
export flow itself added. After the first export, the panel permanently loses that class and
starts appearing in print output on every subsequent export.

Fix by mirroring the existing `expandedByUs` pattern: track exactly which elements *this handler*
toggled into `print-exclude`, and restore only those — never touch elements the class was already
on before the handler ran.

Replace:
```javascript
    confirmBtn.addEventListener('click', function () {
      var expandedByUs = [];
      document.querySelectorAll('.entity-group:not(.open)').forEach(function (group) {
        group.classList.add('open');
        expandedByUs.push(group);
      });

      document.querySelectorAll('.pdf-section-checkbox').forEach(function (cb) {
        var section = document.getElementById(cb.dataset.section);
        if (section) section.classList.toggle('print-exclude', !cb.checked);
      });

      window.print();

      window.addEventListener('afterprint', function restoreState() {
        expandedByUs.forEach(function (group) { group.classList.remove('open'); });
        document.querySelectorAll('.print-exclude').forEach(function (el) {
          el.classList.remove('print-exclude');
        });
        window.removeEventListener('afterprint', restoreState);
      });
    });
```
with:
```javascript
    confirmBtn.addEventListener('click', function () {
      var expandedByUs = [];
      document.querySelectorAll('.entity-group:not(.open)').forEach(function (group) {
        group.classList.add('open');
        expandedByUs.push(group);
      });

      var excludedByUs = [];
      document.querySelectorAll('.pdf-section-checkbox').forEach(function (cb) {
        var section = document.getElementById(cb.dataset.section);
        if (section && !cb.checked && !section.classList.contains('print-exclude')) {
          section.classList.add('print-exclude');
          excludedByUs.push(section);
        }
      });

      window.print();

      window.addEventListener('afterprint', function restoreState() {
        expandedByUs.forEach(function (group) { group.classList.remove('open'); });
        excludedByUs.forEach(function (el) { el.classList.remove('print-exclude'); });
        window.removeEventListener('afterprint', restoreState);
      });
    });
```

Note the behavior change is intentional and correct: a section that was *already* excluded before
the click (shouldn't currently be possible since `print-exclude` on sections is only ever added by
this same handler, but the `!section.classList.contains('print-exclude')` guard makes the fix
robust either way) is left alone by the restore step, exactly like `#pdf-export-panel`.

## Interfaces

No public/exported functions change signature. `initPdfExport()` remains a private IIFE-scoped
function with the same DOM element IDs (`pdf-export-toggle`, `pdf-export-options`,
`pdf-export-confirm`, `.pdf-section-checkbox`, `.entity-group`).

## Constraints

- Don't touch any other function in `animations.js` (theme toggle, scroll progress, entity
  groups, spotlight, staggered entrance).
- Don't change `templates/report.html` — the `#pdf-export-panel` `print-exclude` class stays
  exactly as-is; the fix is entirely in the JS restore logic, not the HTML.
- No LLM call involved. Browser print-preview pixel testing is explicitly an Alfonso-owned manual
  checkpoint (per CONTEXT.md) — do not attempt to verify actual print rendering; verify only the
  DOM class-state logic.

## Verification

This is pure DOM logic — verify without a browser using a quick Node or JSDOM-free reasoning
check is not reliable enough; instead verify by code trace plus a manual browser DOM check:

1. Open `templates/report.html` (or the running Flask app's `/` route) in a browser dev console.
2. Confirm `#pdf-export-panel` has class `print-exclude` before doing anything.
3. Click the PDF export toggle, uncheck at least one `.pdf-section-checkbox`, click confirm
   (this will trigger `window.print()` — cancel the print dialog, that's fine, `afterprint` still
   fires on cancel in Chromium-based browsers; if it doesn't fire in the test browser, manually
   invoke `window.dispatchEvent(new Event('afterprint'))` in the console instead).
4. After the (real or simulated) `afterprint` event, re-check `#pdf-export-panel` in the DOM
   inspector — it must **still** have `print-exclude`.
5. Confirm the section whose checkbox was unchecked also had `print-exclude` added during export
   and removed after restore (i.e., its exclusion is transient, only the panel's is permanent).
6. Repeat the export flow a second time to confirm the panel still isn't broken (this is the
   actual regression the bug caused — first export was fine, second export exposed the panel).

## Model tier

mid — the fix requires understanding why the original bug happens (shared class name, blanket
selector) and correctly scoping the tracked-elements pattern, not just pattern-matching a diff.

## Depends on

None.

## Evidence

**Status: DONE**

`git diff static/animations.js` confirms the exact fix: introduces `excludedByUs` array, guards
additions with `!cb.checked && !section.classList.contains('print-exclude')`, restores only
`excludedByUs` elements on `afterprint` instead of a blanket `.print-exclude` query.
`templates/report.html` was not touched (confirmed `#pdf-export-panel`'s permanent `print-exclude`
class at line 111 is untouched by this change since the panel is never a `.pdf-section-checkbox`
target).

No real browser was available in the execution environment, so steps 2/4 of Verification (manual
DOM inspection) were done via code trace instead: the panel's class is never added to
`excludedByUs` (it's not a checkbox-mapped section), so it's never touched by the restore step,
and the `!section.classList.contains('print-exclude')` guard makes this robust even under a
hypothetical overlap. Real browser print-preview QA remains an Alfonso-owned manual checkpoint
per CONTEXT.md.
