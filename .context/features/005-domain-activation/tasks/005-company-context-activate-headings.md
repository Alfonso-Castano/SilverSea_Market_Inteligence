# Task 005: Remove the "reference only" caveat from 5 product-catalog headings

**Status:** done
**Depends on:** none
**Model tier:** cheap — 5 mechanical string removals, exact text given below.

## Files
- Modify: `data/company_context.md` (5 headings inside the "Products by Business Sector" section,
  currently lines 29, 33, 37, 41, 45)

## What to do

Remove the ` — reference only, not active this round` suffix from exactly these 5 headings (leave
the product-list text under each heading completely untouched):

| Current | New |
|---|---|
| `### Manufacturing & Industry 4.0 (MFG) — reference only, not active this round` | `### Manufacturing & Industry 4.0 (MFG)` |
| `### Healthcare & Life Sciences (HLS) — reference only, not active this round` | `### Healthcare & Life Sciences (HLS)` |
| `### Retail, Commerce & Consumer Goods (RCC) — reference only, not active this round` | `### Retail, Commerce & Consumer Goods (RCC)` |
| `### Culture, Tourism & Events (CTE) — reference only, not active this round` | `### Culture, Tourism & Events (CTE)` |
| `### Public Sector & Smart Cities (PSS) — reference only, not active this round` | `### Public Sector & Smart Cities (PSS)` |

Do 5 separate exact-match edits (each heading line is already unique in the file, so no extra
surrounding context is needed to disambiguate).

## Interfaces

None — this is a documentation/reference file read by `pipeline/vectorstore.py`'s seeding process
and by Task 004's executor (already completed its own read of this content independently — Task
004 does not need to wait for this task, and this task does not need to wait for Task 004).

## Constraints

- **No other change to this section.** Do not touch:
  - The `### Education & EdTech (EDU) — active this round` or
    `### Built Environment & Real Estate (BER) — active this round` headings (they already read
    correctly and are out of scope).
  - The intro paragraph above the headings (lines 14-18), which currently reads *"Only EDU and BER
    are active scraping/analysis domains this round — the other five sectors are preserved here for
    reference so a future expansion round doesn't need to re-transcribe the catalog."* This sentence
    becomes slightly stale after this task, but CONTEXT.md explicitly scopes this task to the 5
    heading suffixes only — do not rewrite this paragraph even though it would read more accurately
    if updated. (If genuinely bothered by this, note it in your report rather than editing it.)
  - The product-list text under any of the 5 headings (the actual solution names) — those stay
    byte-identical; only the heading line itself changes.
  - The `<!-- DRAFT: ... -->` HTML comment at the top of the file, or any other section
    (`## Target Sectors & Use Cases` and beyond).

## Verification

Run from the repo root:

```
py -c "
text = open('data/company_context.md', encoding='utf-8').read()
assert 'reference only, not active this round' not in text, 'caveat suffix still present'
for heading in [
    '### Manufacturing & Industry 4.0 (MFG)',
    '### Healthcare & Life Sciences (HLS)',
    '### Retail, Commerce & Consumer Goods (RCC)',
    '### Culture, Tourism & Events (CTE)',
    '### Public Sector & Smart Cities (PSS)',
]:
    assert heading in text, heading
    assert heading + ' —' not in text, heading + ' still has a suffix'
assert '### Education & EdTech (EDU) — active this round' in text
assert '### Built Environment & Real Estate (BER) — active this round' in text
print('OK')
"
```

Must print `OK` with no `AssertionError`. The assertion strings above deliberately avoid containing
the file's em-dash character (matched only via the ASCII text after it, e.g. `'reference only, not
active this round'`) — do not add a `print()` of any file prose containing non-ASCII characters
(em dashes, diacritics) in your own verification, to avoid the Windows console `cp1252` encode
crash already hit twice this session.

## Evidence

Executor report (DONE): all 5 caveat suffixes removed, product-list text untouched, EDU/BER headings untouched. Verification script printed OK. Intro paragraph (lines 14-18, "Only EDU and BER are active...") is now slightly stale — flagged, left unchanged per explicit task scope.
