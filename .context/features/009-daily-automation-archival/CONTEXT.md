# Feature: Daily Automated Pipeline Runs + Report Archival

**Base:** 90b9d7dbce78a26a1bc7001d4ac9b5242ccf295f

## Goal

The production pipeline runs automatically every day at 8am for all 3 countries × 3 visible domains, and each completed report is permanently archived as a downloadable PDF snapshot, browsable from within the app.

## Scope

**In scope:**
- A wrapper script that runs `main.py` sequentially for all 9 (country × domain) combinations: SG/VN/MY × EDU/BER/GENERAL.
- A single crontab entry on the production Ubuntu server (`/www/wwwroot/ai-mi`, per `deploy/start.sh`) invoking that wrapper at 8am server time.
- Headless PDF generation (via Playwright + Chromium) of each freshly-generated report, immediately after that report's `main.py` run completes — reusing the *existing* browser print CSS/JS (`templates/report.html`'s PDF panel, `static/animations.js`'s `initPdfExport()`) rather than building a second rendering path.
- Archive storage on the server filesystem, organized per country/domain/date.
- A simple list+download view for browsing past archived reports (exact placement: `/internals`, see Implementation Decisions).
- SSH deploy-key access set up so this session (or a future one) can install and verify the cron job directly.

**Out of scope (deliberately deferred to a separate feature):**
- Bulk source submission (replacing the "suggest a source" feedback flow) — unrelated files, no dependency on this feature, will get its own `/feature-discuss` pass after this one ships.
- Any change to which providers/models the pipeline uses — already resolved; production already runs on a paid company-shared Qwen key (`company-qwen-flash`), no quota concern for 9 runs/day (~117 LLM calls/day total).
- Alerting/notification on cron failure (e.g. email/Slack on a bad run) — not requested, not assumed. Logging only.
- Archive retention/pruning policy — not requested. Default is keep-forever (see Implementation Decisions); revisit only if disk usage becomes a real problem.

## Implementation Decisions

- **Feature split**: this feature covers automation + archival only, split from bulk-source-upload per Alfonso's explicit confirmation — two independent features, two branches, two review passes.
- **Server access**: SSH key-based, scoped deploy user, public-key-only handoff — Alfonso's explicit choice, over both "human installs it" and "decide later." A dedicated ed25519 keypair (`~/.ssh/aimi_prod_deploy`, *not* Alfonso's personal key) was generated this session specifically for this purpose, so it's independently revocable. **Public key** (safe to share, already generated):
  `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINvOWFHbskXceIv8zi4r4k5mXT+ZGzUM3slMp1Ge+sZA aimi-deploy-claude-code`
  **Still needed from Alfonso before any server work can start**: the server hostname/IP, the deploy username the public key should be added under (recommend a low-privilege, non-root user scoped to `/www/wwwroot/ai-mi` if the server supports creating one — Alfonso/leo.li's call, not assumed here), and confirmation the key's been added to that user's `authorized_keys`. This is a hard blocker for the cron-install task specifically, not for building/testing the wrapper script and PDF logic locally first.
- **PDF generation approach**: Playwright + headless Chromium — Alfonso's explicit choice over a server-side HTML-to-PDF library, specifically to reuse the real print CSS/JS with zero duplicated rendering logic, accepting the added dependency weight (Chromium binary, `playwright install chromium` needed on the server, meaningful RAM/disk during each render). The headless render will need to hit the real Flask app (either the live server locally on `localhost` server-side, or a local `app.run()` instance during the wrapper's execution) with a session cookie/auth bypass mechanism for the archival process specifically — **left to the planner/executor**, since it depends on `app.py`'s actual login/session implementation (grounded from code, not guessed here).
- **Archive browsing UI**: a simple list+download view — Alfonso's explicit choice over filesystem-only. **Default judgment (Claude's, not confirmed with Alfonso): placed on `/internals`**, not `/admin` — `/internals` is already the maintainer-facing observability page (run metadata, vector store contents, source scores) open to any logged-in user (viewer or admin; confirmed via `app.py`, no role check on that route), and archived reports are a natural extension of "what's happened with this system," not an admin-only action like source approval. Flag this placement to Alfonso for confirmation at plan review if it matters to him.
- **Archive timing**: archive **immediately after each combination's own `main.py` run completes successfully** (not "before next run overwrites it") — Claude's default judgment, not explicitly discussed. This means the archive accumulates one dated snapshot per country/domain per day going forward automatically, which is what "store the report after it refreshes" describes, and avoids ever archiving a stale/replaced report instead of the fresh one.
- **Archive file layout**: Claude's default judgment, not explicitly discussed — `data/archive/{country}/{domain}/{YYYY-MM-DD}.pdf`, mirroring the existing `latest_report_{country}_{domain}.json` naming convention already used by `pipeline/report.py`.
- **Wrapper execution model**: Claude's default judgment — one Python script (not 9 separate crontab lines) that loops the 9 combinations sequentially, subprocess-invoking `main.py` per combination (matching how it's already invoked from the CLI, not importing it as a library), continuing to the next combination if one fails rather than aborting the whole run, and logging per-combination success/failure to a file the internals page (or just the server) can inspect. Sequential (not parallel) specifically to avoid concurrent ChromaDB writes across different `main.py` processes — `.context/STATE.md`'s known-bugs list already documents a transient ChromaDB concurrent-access issue from running `main.py` and the Flask dev server against the same store at once; parallelizing 9 runs would risk the same class of problem multiplied by 9.
- **Domain/country set for the daily run**: exactly the 3 visible tabs (EDU/BER/GENERAL) × 3 countries (SG/VN/MY) = 9 runs, matching Alfonso's "all three sectors" and the current UI, not all 8 underlying domain codes.
- **`--no-email` flag**: each `main.py` invocation should keep using `--no-email`, matching how the pipeline is already run in practice per `.context/STATE.md` (email digest is a known-broken, deprioritized path, not something this feature should accidentally start relying on).

## Global Constraints

- This is a solo internship project; token/effort efficiency matters (see root `CLAUDE.md`).
- No speculative full `py main.py` runs against Groq — moot for production (company Qwen key, no free-tier quota concern per Alfonso), but still applies to any *local* dev-side testing of the wrapper script during planning/execution — use `--no-email` and prefer dry-run/mocked combinations where a real LLM call isn't the thing being tested.
- Never put a credential, token, or private key in chat or in a committed file. The SSH deploy key's private half stays local to this dev machine only (`~/.ssh/aimi_prod_deploy`, outside the repo, never committed) — only the public key is shared, and only through Alfonso/leo.li's own channel, not pasted back into this conversation as something to relay further.
- Match the project's existing "boring stack" bias: no new frameworks beyond what's already decided here (Playwright is the one deliberate, discussed exception for this feature).
- Flask + Jinja2, server-rendered, no SPA — archive browsing UI should follow the same pattern as `/internals`'s existing rendering, not introduce client-side JS framework machinery.

## Open Questions

- Server hostname/IP, deploy username, and confirmation the public key above has been added to `authorized_keys` — blocks the cron-install task only, not the rest of the build. Alfonso to provide (from leo.li or his own access).
- Whether a low-privilege dedicated deploy user is actually creatable on the server, vs. using an existing account — Alfonso/leo.li's call once server details are known.
- Archive retention policy (keep-forever vs. prune after N days/months) — not raised, defaulting to keep-forever; revisit only if disk usage on the server becomes a real concern.
- `/internals` vs `/admin` placement for the archive browsing view — Claude's default judgment (see above), not explicitly confirmed with Alfonso.
- Exact mechanism for the headless Playwright render to authenticate against the app's session-gated report page — left to the planner/executor to ground against `app.py`'s real login implementation.
