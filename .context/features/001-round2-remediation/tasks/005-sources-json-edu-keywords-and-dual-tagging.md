# Task 005: Add EDU keywords and dual-tag NUS/NTU in `config/sources.json`

**Status:** done

## Files

- `config/sources.json` (modify only)

## What to do

**1. Add EDU-relevant terms to the shared `keywords` list** (currently lines 679-751, inside the
SG country object). This is the existing single shared per-country keyword list — no new schema,
no per-domain keyword split (per CONTEXT.md's decision). Append these terms to the end of the
existing `keywords` array (before its closing `]`), keeping the existing BER terms and
competitor/prospect names untouched:
```json
        "edtech",
        "e-learning",
        "LMS",
        "learning management system",
        "campus digital",
        "STEM lab",
        "virtual lab",
        "virtual campus",
        "online learning",
        "blended learning"
```
(Comma-join correctly with the preceding entry `"Savills"` — that line currently has no trailing
comma since it's the last item; add one before inserting these new entries, and make sure the
final new entry has no trailing comma since it's now the new last item before `]`.)

**2. Dual-tag NUS and NTU as `["BER", "EDU"]`.** Both are currently `"domain": ["BER"]` (NUS at
current lines 260-269, NTU at current lines 270-279, both under `"sector": "customers"`). Change
each source's `"domain"` array from `["BER"]` to `["BER", "EDU"]`. Do not change any other field
on these two source objects (name, url, sector, type, active all stay the same).

Do not dual-tag any other source — CONTEXT.md scopes this to "NUS/NTU (or any other currently-BER
source with genuinely EDU-relevant content) as `["BER","EDU"]` where it's not complex to do." NUS
and NTU (university newsrooms) are the clear, low-risk case; scan the rest of the `sources` array
briefly for any other source whose `name`/`url` is unambiguously a university or education
institution and apply the same dual-tag if found, but do not force a domain change onto anything
that isn't obviously an education institution (e.g. don't touch SGH, government agencies,
contractors, or general news sources even if they occasionally cover education topics).

## Interfaces

None — pure JSON data edit, no code changes. `config/sources.py`'s `_load()`/`COUNTRIES` and
`pipeline/filter.py`'s keyword consumption are unaffected in structure, only in the data they
read.

## Constraints

- `config/sources.json` is the source of truth; do not touch `config/sources.py`'s logic in this
  task (a separate task modifies it for the admin-approval fix — no overlap, this task only edits
  the JSON data file).
- Do not touch `priority_keywords` (lines 662-678) — CONTEXT.md's decision is to add EDU terms to
  the shared `keywords` list only, not to `priority_keywords`.
- Do not touch `_domain_tagging_status` (last line) — unreviewed draft flag, explicitly out of
  scope; don't resolve or alter its value or wording as part of this task.
- Must remain valid JSON — verify with a JSON parser after editing, not just visual inspection.
- Sector (`customers`/etc.) and domain (`BER`/`EDU`/`GENERAL`) are orthogonal — dual-tagging NUS/
  NTU's domain does not touch their `sector` field.

## Verification

No LLM call needed — pure JSON/config verification:

1. `python -c "import json; json.load(open('config/sources.json', encoding='utf-8'))"` (or
   `py -c "..."`) — must succeed with no exception, confirming the file is still valid JSON.
2. `python -c "import json; d=json.load(open('config/sources.json',encoding='utf-8')); kw=d['countries'][0]['keywords']; print([k for k in ['edtech','e-learning','LMS','virtual campus'] if k in kw])"`
   — must print all four new terms as present.
3. `python -c "import json; d=json.load(open('config/sources.json',encoding='utf-8')); srcs={s['name']: s['domain'] for s in d['countries'][0]['sources']}; print(srcs.get('NUS'), srcs.get('NTU'))"`
   — must print `['BER', 'EDU'] ['BER', 'EDU']`.
4. Confirm `config.sources.COUNTRIES` still imports cleanly:
   `python -c "from config.sources import COUNTRIES; print(len(COUNTRIES[0]['sources']))"` — must
   match the source count from before this edit (no sources added/removed, only fields changed).

## Model tier

cheap — exact strings and exact field changes are fully specified above; the executor's job is
correct JSON editing plus running the verification commands.

## Depends on

None.

## Evidence

**Status: DONE**

- `py -c "import json; json.load(open('config/sources.json', encoding='utf-8'))"` → succeeds, valid JSON.
- Keyword check: `['edtech', 'e-learning', 'LMS', 'virtual campus']` — all present.
- Domain check: `NUS -> ['BER', 'EDU']`, `NTU -> ['BER', 'EDU']`.
- Source count unchanged at 62 (`config.sources.COUNTRIES` imports cleanly).
- No other source was dual-tagged; only NUS/NTU met the "unambiguously an education institution"
  bar per the task's guidance.
