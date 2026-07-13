# Task 006: Retag Vietnam sources in `config/sources.json` with real business domains

**Status:** done
**Depends on:** none
**Model tier:** cheap — every edit is fully specified with exact current line numbers and exact
target values below; the executor's job is precise mechanical transcription plus verification, not
judgment. (This is a large task by edit count, not by difficulty — do not re-derive any domain
assignment, the table below is authoritative per `CONTEXT.md`.)

## Files
- Modify: `config/sources.json` (Vietnam country block only, `"code": "VN"` at line 769 through the
  end of that country's `sources` array at line 1463 — do not touch the SG block above it or the
  MY block below it)

## What to do

Edit the `"domain"` array of each of the 36 named sources below, changing it from its current value
to the target value shown. Every one of these sources currently has `"domain": ["GENERAL", "BER"]`
(a 2-line array) **except** the 3 already-dual-tagged ones noted inline below. Use the Edit tool
with enough surrounding context (the `"name"` field on the preceding lines) to uniquely target each
one — do not use a blind find-and-replace-all on `"BER"` since that string appears dozens of times
in this file for sources that must NOT change.

| # | Source name (`"name"` field, exact) | Current line (as of this planning pass) | Target `"domain"` array |
|---|---|---|---|
| 1 | `ITPC` | 773-781 | `["GENERAL", "PSS"]` |
| 2 | `Ministry of Industry & Trade (MOIT)` | 796-804 | `["GENERAL", "MFG"]` |
| 3 | `Ministry of Science & Technology (MOST)` | 807-816 (array has trailing comma; `inactive_reason` follows) | `["GENERAL", "PSS"]` |
| 4 | `Ministry of Health (MOH)` | 819-828 (trailing comma; `inactive_reason` follows) | `["GENERAL", "HLS"]` |
| 5 | `National Innovation Center (NIC)` | 844-853 (trailing comma; `inactive_reason` follows) | `["GENERAL", "PSS"]` |
| 6 | `VNPT` | 891-900 | `["GENERAL", "PSS"]` |
| 7 | `Panasonic Vietnam` | 903-912 | `["GENERAL", "MFG"]` |
| 8 | `Samsung Vietnam` | 915-923 | `["GENERAL", "MFG"]` |
| 9 | `FPT Corporation` | 926-935 (trailing comma; `inactive_reason` follows) | `["GENERAL", "PSS"]` |
| 10 | `Viettel Group` | 938-947 | `["GENERAL", "PSS"]` |
| 11 | `NVIDIA` | 1041-1049 | `["GENERAL", "PSS"]` |
| 12 | `Microsoft Azure` | 1052-1060 | `["GENERAL", "PSS"]` |
| 13 | `Amazon Web Services` | 1063-1071 | `["GENERAL", "PSS"]` |
| 14 | `Dell Technologies` | 1074-1083 | `["GENERAL", "PSS"]` |
| 15 | `Cisco` | 1086-1095 | `["GENERAL", "PSS"]` |
| 16 | `Vietnam Investment Review` | 1120-1128 | `["GENERAL", "PSS"]` |
| 17 | `VnExpress Business` | 1131-1139 | `["GENERAL", "PSS"]` |
| 18 | `Vietnam Briefing` | 1142-1150 | `["GENERAL", "PSS"]` |
| 19 | `World Bank Vietnam` | 1153-1161 | `["GENERAL", "BER"]` **— already this value; no byte change results. See Open Note below.** |
| 20 | `VIFA Liên Minh` | 1164-1172 | `["GENERAL", "CTE"]` |
| 21 | `TTDecor` | 1175-1183 | `["GENERAL", "RCC"]` |
| 22 | `BambuUP` | 1186-1194 | `["GENERAL", "PSS"]` |
| 23 | `GIZ` | 1197-1205 | `["GENERAL", "EDU"]` |
| 24 | `Vietsoft Pro` | 1208-1216 | `["GENERAL", "PSS"]` |
| 25 | `ATZ` | 1219-1228 (trailing comma; `inactive_reason` follows) | `["GENERAL", "BER"]` **— already this value; no byte change results. See Open Note below.** |
| 26 | `Coca-Cola Vietnam` | 1231-1239 | `["GENERAL", "RCC"]` |
| 27 | `Biz Eyes` | 1242-1251 | `["GENERAL", "RCC"]` |
| 28 | `MIK Group` | 1266-1274 | `["GENERAL", "BER"]` **— already this value; no byte change results. See Open Note below.** |
| 29 | `BM Windows` | 1277-1285 | `["GENERAL", "BER"]` **— already this value; no byte change results. See Open Note below.** |
| 30 | `Arobid` | 1288-1296 | `["GENERAL", "RCC"]` |
| 31 | `QMS` | 1299-1307 | `["GENERAL", "BER"]` **— already this value; no byte change results. See Open Note below.** |
| 32 | `Sao Mai Group` | 1310-1318 | `["GENERAL", "EDU"]` |
| 33 | `CMC` | 1333-1342 (trailing comma; `inactive_reason` follows) | `["GENERAL", "PSS"]` |
| 34 | `Lạc Việt` | 1345-1354 (trailing comma; `inactive_reason` follows) | `["GENERAL", "HLS"]` |
| 35 | `Newtecons` | 1357-1365 | `["GENERAL", "BER"]` **— already this value; no byte change results. See Open Note below.** |
| 36 | `Đa Minh Education - Gia Đình Education` | 1452-1461 (trailing comma; `inactive_reason` follows) | `["GENERAL", "BER", "EDU"]` — **this one is a genuine dual-tag addition, not a value swap** (current is `["GENERAL", "BER"]`, target adds `"EDU"` as a 3rd element) |

**Open note on rows 19, 25, 28, 29, 31, 35 (World Bank Vietnam, ATZ, MIK Group, BM Windows, QMS,
Newtecons):** `CONTEXT.md`'s retag table assigns these a target domain of `BER`, which is identical
to their current value. Editing them is a verified no-op, not a mistake — leave them exactly as
`["GENERAL", "BER"]`. Do not skip verifying these 6 (confirm the value is what it should be), but do
not expect or force a diff on them.

**Sources NOT in the table above keep their current `"domain"` value completely unchanged.** This
includes the 3 sources already correctly dual-tagged before this task (do not touch these, they are
not in the 36-row table): `Ministry of Education & Training (MOET)` (stays
`["GENERAL", "BER", "EDU"]`), `HUIT` (stays `["GENERAL", "BER", "EDU"]`), `Văn Lang University`
(stays `["GENERAL", "BER", "EDU"]`). It also includes the 7 no-URL stub sources explicitly excluded
from retagging (no source notes ever existed for these): `VNDC Technology Media`, `BPRO`,
`Digital World`, `CTO Group`, `Exporum`, `Steamzone`, `Delta` — all stay `["GENERAL", "BER"]`. And it
includes every other VN source not named above (Ministry of Construction (MOC), Vingroup, Sun Group,
VSIP, Becamex IDC, Siemens, Schneider Electric, Honeywell, Johnson Controls, Autodesk, Bentley
Systems, Matterport, Savills Vietnam, CBRE Vietnam) — all stay `["GENERAL", "BER"]`.

**Nothing else about any VN source may change** — `name`, `url`, `sector`, `type`, `active`,
`fetcher` (where present), and `inactive_reason` (where present) must stay byte-identical for every
source in the VN block, whether or not its `domain` array changed.

## Interfaces

None — this is a static config file read by `config/sources.py`'s `load_sources()` at pipeline/app
startup. No other task in this feature touches `config/sources.json`.

## Constraints

- Manual Edit-tool edits are fine for this one-time retagging pass (established precedent for
  planned data changes, per `CONTEXT.md`'s Global Constraints) — do not write a script to
  mechanically rewrite the file, and do not touch `config/sources.py`.
- Do not touch the SG country block (starts line 5) or the MY country block (starts line 1561) —
  this task is scoped exclusively to the VN block (lines 769-1463 as of this planning pass; line
  numbers will shift slightly as edits land, re-locate by `"name"` field, not by line number, for
  edits after the first few).
- Do not touch VN's own `priority_keywords` (line ~1464) or `keywords` (line ~1480) lists — those
  are out of scope for this task (a separate task, Task 004, touches the *Malaysia* keywords list
  only as a read-only reference, not VN's).
- Line numbers in the table above are a navigation aid captured during planning; re-verify each by
  the source's unique `"name"` string before editing, since earlier edits in this same task will
  shift line numbers for entries further down the file.

## Verification

Run from the repo root. This script only prints `OK` plus a count — it deliberately never prints
any Vietnamese source name or file prose, to avoid the Windows console `cp1252` encode crash already
hit twice this session with Vietnamese diacritics. Non-ASCII names below are written as `\uXXXX`
escapes inside the Python source (not printed), which sidesteps the console-encoding problem
entirely since nothing gets written to stdout except `OK` and a number:

```
py -c "
import json
data = json.load(open('config/sources.json', encoding='utf-8'))
vn = next(c for c in data['countries'] if c['code'] == 'VN')
by_name = {s['name']: s['domain'] for s in vn['sources']}

expected = {
    'ITPC': ['GENERAL', 'PSS'],
    'Ministry of Industry & Trade (MOIT)': ['GENERAL', 'MFG'],
    'Ministry of Science & Technology (MOST)': ['GENERAL', 'PSS'],
    'Ministry of Health (MOH)': ['GENERAL', 'HLS'],
    'National Innovation Center (NIC)': ['GENERAL', 'PSS'],
    'VNPT': ['GENERAL', 'PSS'],
    'Panasonic Vietnam': ['GENERAL', 'MFG'],
    'Samsung Vietnam': ['GENERAL', 'MFG'],
    'FPT Corporation': ['GENERAL', 'PSS'],
    'Viettel Group': ['GENERAL', 'PSS'],
    'NVIDIA': ['GENERAL', 'PSS'],
    'Microsoft Azure': ['GENERAL', 'PSS'],
    'Amazon Web Services': ['GENERAL', 'PSS'],
    'Dell Technologies': ['GENERAL', 'PSS'],
    'Cisco': ['GENERAL', 'PSS'],
    'Vietnam Investment Review': ['GENERAL', 'PSS'],
    'VnExpress Business': ['GENERAL', 'PSS'],
    'Vietnam Briefing': ['GENERAL', 'PSS'],
    'World Bank Vietnam': ['GENERAL', 'BER'],
    'VIFA Liên Minh': ['GENERAL', 'CTE'],
    'TTDecor': ['GENERAL', 'RCC'],
    'BambuUP': ['GENERAL', 'PSS'],
    'GIZ': ['GENERAL', 'EDU'],
    'Vietsoft Pro': ['GENERAL', 'PSS'],
    'ATZ': ['GENERAL', 'BER'],
    'Coca-Cola Vietnam': ['GENERAL', 'RCC'],
    'Biz Eyes': ['GENERAL', 'RCC'],
    'MIK Group': ['GENERAL', 'BER'],
    'BM Windows': ['GENERAL', 'BER'],
    'Arobid': ['GENERAL', 'RCC'],
    'QMS': ['GENERAL', 'BER'],
    'Sao Mai Group': ['GENERAL', 'EDU'],
    'CMC': ['GENERAL', 'PSS'],
    'Lạc Việt': ['GENERAL', 'HLS'],
    'Newtecons': ['GENERAL', 'BER'],
    'Đa Minh Education - Gia Đình Education': ['GENERAL', 'BER', 'EDU'],
}

missing = [n for n in expected if n not in by_name]
mismatched = [n for n in expected if n in by_name and by_name[n] != expected[n]]
assert not missing, ('missing count', len(missing))
assert not mismatched, ('mismatched count', len(mismatched))

unchanged = {
    'Ministry of Construction (MOC)': ['GENERAL', 'BER'],
    'Ministry of Education & Training (MOET)': ['GENERAL', 'BER', 'EDU'],
    'Vingroup': ['GENERAL', 'BER'],
    'Sun Group': ['GENERAL', 'BER'],
    'VSIP': ['GENERAL', 'BER'],
    'HUIT': ['GENERAL', 'BER', 'EDU'],
    'Văn Lang University': ['GENERAL', 'BER', 'EDU'],
    'VNDC Technology Media': ['GENERAL', 'BER'],
    'BPRO': ['GENERAL', 'BER'],
    'Delta': ['GENERAL', 'BER'],
}
un_mismatched = [n for n in unchanged if by_name.get(n) != unchanged[n]]
assert not un_mismatched, ('unchanged-source mismatch count', len(un_mismatched))

assert len(vn['sources']) == 60, ('source count changed', len(vn['sources']))
print('OK', len(by_name), len(vn['sources']))
"
```

Must print `OK 36 60` with no `AssertionError`.

Then confirm no unrelated fields drifted:
```
git diff --stat config/sources.json
```
Should show exactly one file changed. Then:
```
git diff config/sources.json
```
Read the diff and confirm every changed/added line is one of: a domain-code string (`"PSS"`,
`"MFG"`, `"HLS"`, `"RCC"`, `"CTE"`, `"BER"`, `"EDU"`, `"GENERAL"`) or a comma on an otherwise
unchanged bracket line. No `"name"`, `"url"`, `"sector"`, `"type"`, `"active"`, `"fetcher"`, or
`"inactive_reason"` line should appear in the diff anywhere. Do not run this diff command in a way
that prints the full file — `git diff` output for this file is a few dozen lines, safe to read
directly.

## Evidence

Executor report (DONE). Verification script's missing/mismatched/unchanged assertions all passed; total VN source count still 60. Note: script printed `OK 60 60`, not the task's predicted `OK 36 60` — this is a task-file documentation artifact (the script's `by_name` dict is built from all 60 VN sources, not just the 36-row target table; the number of names actually checked against `expected` is still 36, just not what gets printed), not a data defect. Independently confirmed via `git diff --stat` (31 insertions/30 deletions — exactly 30 single-value swaps + 1 three-element addition for Đa Minh) and full diff read: only `domain` array lines changed anywhere in the file; all 6 no-op sources (World Bank Vietnam, ATZ, MIK Group, BM Windows, QMS, Newtecons) correctly show zero diff; no `name`/`url`/`sector`/`type`/`active`/`fetcher`/`inactive_reason` line appears in the diff. SG and MY blocks untouched.

Files changed: `config/sources.json` (VN block only).
