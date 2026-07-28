# Task 001: Confirm Playwright in `requirements.txt` as a direct dependency + local browser install

**Status:** done
**Depends on:** none
**Model tier:** cheap — the change is a header-comment edit only (the version-pinned dependency
line itself already exists), plus running two install commands and confirming their output. No
design judgment required; see RESEARCH.md §5 for why this is smaller than it first looks.

## Files
- Modify: `requirements.txt`

## What to do

1. Open `requirements.txt` and confirm the line `playwright==1.61.0` is already present (it is —
   confirmed during planning; do **not** re-add it or change its version). It's currently an
   undeclared transitive dependency (almost certainly pulled in by `scrapling[fetchers]`, whose
   dynamic fetcher is Playwright-based) — not listed in the file's own header comment as a "direct
   top-level dependency."

2. Update the header comment block at the top of the file (the `# Direct top-level dependencies:
   groq, requests, beautifulsoup4, ...` line) to add `playwright` to that list, since starting with
   this feature, `pipeline/archive.py` imports `playwright.sync_api` directly — it's no longer
   merely an indirect consequence of installing Scrapling. Keep the rest of the comment block's
   wording and structure intact; this is a one-item addition to an existing comma-separated list,
   not a rewrite.

3. Do **not** run a full `pip freeze` regeneration of this file. This dev machine still has no
   project-scoped `.venv` (a real, standing risk — see `.context/STATE.md`'s Known Bugs list, item
   10, and Feature 007's original FAIL for exactly this mistake happening once already). The pinned
   version line for `playwright` doesn't need to change, so there is no reason to regenerate the
   whole file and risk recapturing unrelated global packages.

## Interfaces
None — this task changes a comment and confirms an existing pinned version line; no code changes.

## Constraints
- Do not change the pinned version number on the existing `playwright==1.61.0` line.
- Do not touch any other dependency line, including `patchright==1.61.2` (a separate package, also
  already pinned, not directly used by this feature).
- Do not attempt a full `pip freeze > requirements.txt` regeneration.
- Do not modify any file other than `requirements.txt`.

## Verification

Run these against whatever Python environment you're using for this task (this sandbox's default
`python`/`pip` currently has *nothing* installed, not even `flask` — confirmed during planning; you
will need to `pip install` into it, a venv, or whatever working environment you use):

1. `pip install playwright==1.61.0` — confirm it installs cleanly (exact version match to the
   pinned line).
2. `playwright install chromium` — this fetches the actual Chromium browser binary (not part of the
   pip package). Confirm it completes without error. This step is needed once per machine/environment
   and is separate from the pip install.
3. `python -c "from playwright.sync_api import sync_playwright; print('playwright import OK')"` —
   confirm it prints `playwright import OK` with no traceback.
4. `python -c "content = open('requirements.txt', encoding='utf-8').read(); assert 'playwright==1.61.0' in content; assert content.count('playwright==1.61.0') == 1; print('OK — exactly one playwright line, version unchanged')"`
5. By eye: confirm the header comment's "Direct top-level dependencies" list now includes
   `playwright`, and quote the updated line in your evidence.

## Evidence

Executed by `feature-executor` (haiku tier), reviewed and one cosmetic fix applied by the
orchestrating session (a comment line-wrap split "everything" onto its own line; merged back).

1. `pip install playwright==1.61.0` — clean install at the pinned version.
2. `playwright install chromium` — completed without error.
3. `python -c "from playwright.sync_api import sync_playwright; print('playwright import OK')"` →
   `playwright import OK`.
4. `python -c "..."` assertion script → `OK — exactly one playwright line, version unchanged`.
5. Header comment now reads (requirements.txt lines 2-4):
   ```
   # Direct top-level dependencies: groq, requests, beautifulsoup4, python-dotenv,
   # chromadb, sentence-transformers, scrapling[fetchers], flask, Jinja2, openai, ollama, playwright —
   # everything else below is a transitive dependency pinned via `pip freeze` for reproducibility.
   ```
6. Confirmed via `git diff requirements.txt`: only the header comment changed, the pinned
   `playwright==1.61.0` line itself (line 81) is untouched, no other dependency line touched, no
   full `pip freeze` regeneration occurred.

