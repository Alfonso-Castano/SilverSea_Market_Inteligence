# Task 003: Wrapper script — loop 9 country×domain combinations, archive, log outcomes

**Status:** done
**Depends on:** Task 002 (`pipeline.archive.archive_report_pdf` must exist to import)
**Model tier:** mid — control-flow and logging-format design against CONTEXT.md's locked
decisions, plus writing a mocked test that proves the continue-on-failure behavior without any
real `main.py`/LLM invocation.

## Files
- Create: `scripts/daily_pipeline.py`
- Create: `scripts/daily_pipeline.sh`

## What to do

**1. `scripts/daily_pipeline.py`** — loops the 9 SG/VN/MY × EDU/BER/GENERAL combinations,
subprocess-invoking `main.py` per combination (matching how it's already invoked from the CLI —
not importing `main.run_pipeline` as a library, per CONTEXT.md's locked decision), continuing past
a failed combination rather than aborting, archiving via `pipeline.archive.archive_report_pdf`
immediately after each combination's own successful run, and logging a one-line outcome per
combination to `data/logs/daily_pipeline.log`.

Structure it like this (fill in per the constraints below — this is a specification of shape and
behavior, write real working code from it, don't leave placeholders):

```python
# scripts/daily_pipeline.py — Loops all 9 SG/VN/MY x EDU/BER/GENERAL combinations sequentially,
# invoking main.py as a subprocess per combination (matching its existing CLI invocation shape),
# archiving each successful combination's report to PDF, and logging per-combination outcomes.
# Sequential, not parallel, by design — avoids concurrent ChromaDB writes across processes (see
# .context/STATE.md's known-bugs entry on transient ChromaDB concurrent-access issues).
import datetime
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "logs")
LOG_PATH = os.path.join(LOG_DIR, "daily_pipeline.log")

COUNTRIES = ("SG", "VN", "MY")
DOMAINS = ("EDU", "BER", "GENERAL")
COMBINATIONS = [(c, d) for c in COUNTRIES for d in DOMAINS]


def _log(line: str) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {line}\n")
    print(line)


def run_all() -> None:
    for country, domain in COMBINATIONS:
        try:
            result = subprocess.run(
                [sys.executable, "main.py", f"--country={country}", f"--domain={domain}", "--no-email"],
                cwd=PROJECT_ROOT,
                check=False,
            )
        except Exception as e:
            _log(f"{country} {domain} FAILED (subprocess error: {e})")
            continue

        if result.returncode != 0:
            _log(f"{country} {domain} FAILED (main.py exit code {result.returncode})")
            continue

        try:
            from pipeline.archive import archive_report_pdf
            archive_path = archive_report_pdf(country, domain)
            _log(f"{country} {domain} SUCCESS archived={archive_path}")
        except Exception as e:
            _log(f"{country} {domain} SUCCESS archive_failed=({e})")


if __name__ == "__main__":
    run_all()
```

**2. `scripts/daily_pipeline.sh`** — the aaPanel/crontab entrypoint, mirroring `deploy/start.sh`'s
own conventions (same `PROJECT_DIR`, same venv name/path — reuse `im-env`, do not invent a new
venv name):

```bash
#!/bin/bash
# Silversea Market Intelligence — daily pipeline + archival entrypoint (aaPanel scheduled task)
# 用法: bash scripts/daily_pipeline.sh

set -e

PROJECT_DIR="/www/wwwroot/ai-mi"
VENV_DIR="$PROJECT_DIR/im-env"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在 — $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "错误: 虚拟环境不存在 — $VENV_DIR"
    exit 1
fi
source "$VENV_DIR/bin/activate"

python scripts/daily_pipeline.py
```

## Interfaces
- `run_all() -> None` in `scripts/daily_pipeline.py` — the sole entry point the `.sh` script calls
  (via `if __name__ == "__main__"`).
- Imports `pipeline.archive.archive_report_pdf(country_code, domain)` (Task 002) — imported lazily
  inside the loop (as shown above), not at module top-level, so a missing/broken `pipeline.archive`
  import doesn't crash the whole script before any combination has a chance to run.
- Invokes `main.py` exactly as documented elsewhere in this repo: `python main.py
  --country=<CODE> --domain=<CODE> --no-email` (no `--llm=` flag — CONTEXT.md's locked decision is
  to rely on `resolve_provider(None)`'s existing env-var auto-detect, unchanged).

## Constraints
- Exactly 9 combinations: `{SG, VN, MY} × {EDU, BER, GENERAL}` — not all 8 underlying domain codes
  (CONTEXT.md's locked decision).
- Sequential, not parallel/threaded/async — one `subprocess.run(...)` completes before the next
  combination starts. Do not add concurrency.
- A failed combination (non-zero `main.py` exit code, a subprocess-launch exception, or an
  archival exception) must not stop the loop — every one of the 9 combinations must still be
  attempted even if an earlier one fails. Verify this is true for all three failure types shown
  above (subprocess launch failure, non-zero exit, archive failure after a successful run).
- Every combination gets exactly one log line in `data/logs/daily_pipeline.log`, appended (not
  overwritten) — so a full day's history of daily runs accumulates in one file, not one file per
  day. (Archive retention/pruning is explicitly out of scope for this feature per CONTEXT.md; the
  same applies to this log file — don't add rotation logic.)
- `archive_report_pdf` is only called for combinations where `main.py` itself exited 0 — never for
  a failed combination (there'd be no fresh report to archive).
- Do not import `main.py`'s `run_pipeline` as a library function — subprocess only, matching
  CONTEXT.md's explicit decision (keeps this script's own failures isolated from a single Python
  process; a crash inside one `main.py` run can't take down the wrapper's process).
- `scripts/daily_pipeline.sh` must reuse `deploy/start.sh`'s existing `PROJECT_DIR`
  (`/www/wwwroot/ai-mi`) and venv path (`im-env`) — do not invent different values.
- Do not touch `deploy/start.sh` itself, `app.py`, or any template in this task.

## Verification

No real `main.py` invocation and no LLM calls in this task's verification (per the project's
standing constraint on speculative pipeline runs) — test the wrapper's own control flow with
`subprocess.run` and `archive_report_pdf` both mocked, proving the looping/continue-on-
failure/logging behavior in isolation.

1. `python -c "import ast; ast.parse(open('scripts/daily_pipeline.py', encoding='utf-8').read()); print('syntax OK')"`
2. Write and run a short mocked test proving the required behavior — either as an inline
   `python -c` script or a throwaway file you delete afterward (your choice), but it must actually
   execute and you must report its real output. It needs to:
   - Monkeypatch `scripts.daily_pipeline.COMBINATIONS` down to 3 entries, e.g.
     `[("SG", "BER"), ("VN", "BER"), ("MY", "BER")]`.
   - Patch `subprocess.run` (via `unittest.mock.patch`) to return a fake object with
     `.returncode = 0` for the first two calls and `.returncode = 1` for the third.
   - Patch `pipeline.archive.archive_report_pdf` (or however it's imported in your implementation)
     to a no-op that records its call args and returns a fake path, without touching
     `sys.modules` in a way that breaks the lazy import shown above.
   - Call `run_all()`.
   - Assert: `subprocess.run` was called exactly 3 times, once per combination, with `main.py` and
     the correct `--country=`/`--domain=`/`--no-email` args each time.
   - Assert: the archive mock was called exactly 2 times (for the two combinations whose fake
     `subprocess.run` returned exit code 0) — never for the third.
   - Assert: `run_all()` completed and returned normally (didn't raise), proving the third
     combination's simulated failure didn't abort the loop.
   - Assert: `data/logs/daily_pipeline.log` gained exactly 3 new lines matching the pattern
     `SUCCESS`/`SUCCESS`/`FAILED` in that order (or read the file and show the 3 lines in your
     evidence).
3. Report the exact commands run and their real output/assertions in your evidence — "should work"
   is not acceptable per this project's verification standard.
4. `bash -n scripts/daily_pipeline.sh` (or equivalent shell syntax check, e.g. `sh -n` if `bash` is
   unavailable in this environment) — confirms the `.sh` file has valid syntax. This cannot be
   executed end-to-end locally (no `/www/wwwroot/ai-mi`, no server) — a syntax check is the correct
   and sufficient local evidence gate for this file; do not attempt to fake a server directory
   structure to "fully" test it.

## Evidence

Executed by `feature-executor` (sonnet tier). Both files written verbatim per spec, confirmed by
the orchestrating session via direct file review — no deviations.

1. `python -c "import ast; ast.parse(...); print('syntax OK')"` → `syntax OK`.
2. Mocked control-flow test (3 combos, exit codes 0/0/1): all assertions passed —
   `subprocess.run` called exactly 3 times with correct `main.py --country=/--domain=/--no-email`
   args; `archive_report_pdf` called exactly 2 times (only for the two successful combos, never
   for the failed one); `run_all()` returned normally despite the simulated failure (loop wasn't
   aborted); `data/logs/daily_pipeline.log` gained exactly 3 lines in order
   SUCCESS/SUCCESS/FAILED, shown verbatim in the executor's report.
3. `bash -n scripts/daily_pipeline.sh` → `SHELL SYNTAX OK`.

`scripts/` has no `__init__.py` (namespace package, same pattern as `pipeline/`) — noted, not an
issue.

