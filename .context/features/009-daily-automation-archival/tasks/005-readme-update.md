# Task 005: README — document automation, archival, the new dependency, and the pending server handoff

**Status:** done
**Depends on:** Tasks 002, 003, 004 (must document what those tasks actually built — script
names, log path, archive URL pattern, dependency install steps — not what was originally planned;
cross-check each claim against those tasks' real Evidence sections before writing this)
**Model tier:** mid — synthesizing accurate documentation from three other tasks' actual output
carries real risk of drift if just copied from CONTEXT.md instead of the real, executed files.

## Files
- Modify: `README.md`

## What to do

**1. Troubleshooting table (README.md, "### 3. Troubleshooting", currently around line 87-97)** —
add one row for the new Playwright/Chromium local-install step, matching the existing `scrapling
install` row's phrasing pattern:

```
| Local PDF archival fails with a browser-not-found error | You skipped `playwright install chromium` after `pip install -r requirements.txt` — run it now, it's a one-time step (see Report Archival below) |
```

**2. New section** — add a new top-level section after "### Architecture" (end of Part 2, current
end of file) documenting this feature. Use this structure (fill in exact script/route names and
paths by reading Tasks 002-004's actual `## Files`/`## Interfaces` sections and their filled-in
Evidence — do not guess or copy speculative names from CONTEXT.md if the executed tasks ended up
differing in any small way):

```markdown
## Part 3 — Daily Automation & Report Archival

The production pipeline is designed to run automatically once a day for all 9 country×domain
combinations (SG/VN/MY × EDU/BER/GENERAL), and archive each freshly-generated report as a
downloadable PDF snapshot.

### How it works

- `scripts/daily_pipeline.py` loops all 9 combinations sequentially (not parallel — avoids
  concurrent ChromaDB writes across processes), invoking `main.py --country=<CODE>
  --domain=<CODE> --no-email` as a subprocess per combination. A failed combination is logged and
  skipped, not fatal to the rest of the run — one bad source list or transient scrape failure
  doesn't block the other 8 combinations.
- After each combination's `main.py` run succeeds, its report is immediately rendered to a PDF via
  headless Chromium (Playwright) and saved to `data/archive/{COUNTRY}/{DOMAIN}/{YYYY-MM-DD}.pdf`
  — reusing the dashboard's own print stylesheet (`static/style.css`'s `@media print` block), not
  a separate PDF-rendering path.
- Every combination's outcome (success/failure, archived or not) is appended as one line to
  `data/logs/daily_pipeline.log`.
- Archived PDFs are browsable and downloadable from `/internals` (open to any logged-in user, no
  admin requirement — same access level as the rest of that page).
- `scripts/daily_pipeline.sh` is the entrypoint meant to be invoked by a scheduled task on the
  production server (see "Production deployment — still pending" below).

### Local setup

The archival step needs Playwright's Chromium browser, which is a separate download from the pip
package:

```bash
pip install -r requirements.txt   # playwright is already a pinned dependency
playwright install chromium       # one-time, fetches the actual browser binary
```

### Production deployment — still pending

The wrapper script and archival code are built and locally verified, but **not yet installed or
scheduled on the production server** — this is a deliberate handoff, not an oversight. What
remains, once server access is actually confirmed:

1. **SSH access.** A dedicated deploy keypair was generated specifically for this
   (`~/.ssh/aimi_prod_deploy`, not anyone's personal key — independently revocable). The public
   key has already been shared out-of-band (not committed to this repo, not pasted into any AI
   chat transcript). Still needed before any server-side step below can happen: the server
   hostname/IP, the deploy username the key should be added under, and confirmation the key's
   actually in that user's `authorized_keys`.
2. **Install Playwright's Chromium on the server**, inside the existing `im-env` venv
   (`/www/wwwroot/ai-mi/im-env`, per `deploy/start.sh`):
   ```bash
   source /www/wwwroot/ai-mi/im-env/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   playwright install-deps chromium   # or: playwright install --with-deps chromium
   ```
   The `install-deps` step matters and is easy to miss: `playwright install chromium` alone only
   fetches the browser binary — on a fresh Ubuntu box, headless Chromium also needs a set of OS-
   level shared libraries (nss, atk, libxcomposite, and others) that aren't there by default.
   `playwright install-deps` installs those via `apt` and needs sudo/root — budget for that when
   scheduling this step with whoever manages the server.
3. **Confirm the production Gunicorn instance is already running** (`bash deploy/start.sh`,
   listening on `127.0.0.1:8001`) before enabling the scheduled task below — the archival step
   authenticates against and renders from that already-running app (it does not start its own
   second instance). If Gunicorn isn't up when the daily job runs, `main.py` itself will still
   succeed and write a fresh report, but that combination's PDF archival step will fail (logged,
   not fatal to the other combinations) since there's no server to render against.
4. **Create the scheduled task** (aaPanel's scheduled-task UI, or a plain crontab entry if
   preferred) to run once daily at 8am server time:
   ```
   0 8 * * * bash /www/wwwroot/ai-mi/scripts/daily_pipeline.sh >> /www/wwwroot/ai-mi/data/logs/cron_stdout.log 2>&1
   ```

No alerting/notification on failure is built (not requested) — check `data/logs/daily_pipeline.log`
(per-combination outcomes) or `/internals`'s archive list (which combinations actually got a fresh
PDF today) to see how a given day's run went.
```

## Interfaces
None — documentation only.

## Constraints
- Do not include the SSH private key, or any placeholder that looks like a real key, anywhere in
  this file. Only ever reference the public key as "already shared out-of-band" — never restate
  its contents here even though it's technically safe to share (keep this file's framing
  consistent with how CONTEXT.md itself handles it).
- Do not claim the server-side steps (Playwright/Chromium install, scheduled-task creation) have
  already happened — they haven't, and this task must not imply otherwise. Frame section 3 above
  exactly as "still pending," matching this feature's actual state.
- Verify every script/route/path name you write against what Tasks 002/003/004 actually built
  (read their Evidence sections), not against this task's own draft snippet above if execution
  ended up differing in some small naming detail.
- Do not remove or restructure any existing README content outside the two additions described
  above (the troubleshooting row, and the new Part 3 section) — this project's README has already
  been rewritten/reordered twice based on real fresh-clone testing; don't undo that.

## Verification
1. `grep -n "Part 3 — Daily Automation" README.md` — confirm the new section exists.
2. `grep -n "playwright install chromium" README.md` — confirm it appears at least twice (local
   setup + production section).
3. `grep -in "ssh-ed25519\|BEGIN.*PRIVATE KEY" README.md` — must return **no matches** (confirms
   no key material was pasted in).
4. `grep -n "still pending" README.md` — confirms the production section's framing wasn't
   accidentally written as "done."
5. By eye: read the new section once fully and confirm every script name (`scripts/
   daily_pipeline.py`/`.sh`), log path (`data/logs/daily_pipeline.log`), and archive path pattern
   (`data/archive/{COUNTRY}/{DOMAIN}/{YYYY-MM-DD}.pdf`) matches exactly what Tasks 002-004 actually
   named in their own Evidence — quote the cross-check in your evidence for this task.

## Evidence

Executed by `feature-executor` (sonnet tier). Cross-checked every claim against the real
committed files (not this task's own draft) — correctly incorporated Task 002's real deviation
(the AOS viewport-resize fix) into the "How it works" section, which the original draft snippet
above didn't know about. Reviewed in full by the orchestrating session — accurate, no fixes
needed. One addition beyond the draft: a "Local setup" note on `ARCHIVE_BASE_URL` for testing
against the dev server instead of production's Gunicorn bind, grounded in `pipeline/archive.py`'s
real code.

1. `grep -n "Part 3 — Daily Automation" README.md` → line 140, section exists.
2. `grep -n "playwright install chromium"` → 4 matches (troubleshooting row, local setup,
   production section x2).
3. `grep -in "ssh-ed25519\|BEGIN.*PRIVATE KEY"` → no matches, confirmed no key material present.
4. `grep -n "still pending"` → 2 matches, framing correct.
5. Cross-check confirmed accurate against real files: `app.py`'s actual route path
   (`/internals/archive/<country>/<domain>/<filename>`, login-gated not admin-gated),
   `pipeline/archive.py`'s real archive path pattern and the two real opacity-trap fixes (entity
   group + AOS viewport resize), `scripts/daily_pipeline.py`'s real constants/log path,
   `scripts/daily_pipeline.sh`'s real `PROJECT_DIR`/`VENV_DIR`, and `deploy/start.sh`'s real bind
   address matching `pipeline/archive.py`'s default.

Only `README.md` touched (89 insertions, 0 deletions) — no existing content restructured.

