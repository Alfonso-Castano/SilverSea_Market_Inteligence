# Task 004: pipeline/llm_select.py — provider resolution (CLI flag / env / auto-detect / picker)

**Status:** done
**Depends on:** Task 001 (`config/models.py` must export `PROVIDERS`/`LLM_DEFAULT`).
**Model tier:** mid — the resolution policy and the tkinter/terminal fallback behavior are both
fully specified below (including the two judgment calls CONTEXT.md left implicit); the executor
applies that prose spec faithfully rather than designing the policy itself.

## Files
- Create: `pipeline/llm_select.py`

## What to do

Create a new module implementing `resolve_provider(cli_arg)`, the CLI-only (not Flask) provider
resolution logic `main.py` calls exactly once, before its per-country loop (Task 005 wires the
call site — this task only builds the function). CONTEXT.md's exact requirement is: no `--llm`, no
`LLM_DEFAULT` env var, exactly one provider's env var configured → use it silently, no prompt
(unchanged zero-friction default for today's single-provider `.env`); otherwise, in priority
order: `--llm=<key>` wins if given; else `LLM_DEFAULT` wins if set; else, if provider
auto-detection is ambiguous (zero or 2+ remote providers have their API key env var set), show an
interactive picker (a real `tkinter` popup, falling back automatically to a terminal prompt on
*any* failure — not a `DISPLAY`-env-var pre-check, see RESEARCH.md §6 for why).

Write the file with this exact content:

```python
# pipeline/llm_select.py — Resolves which LLM provider a CLI run uses. CLI-only: never imported
# by app.py/the Flask dashboard — see .context/features/007-multi-provider-llm-backend/CONTEXT.md's
# explicit deferral of any dashboard-facing provider picker.
import os
import sys

from config.models import PROVIDERS, LLM_DEFAULT

_ALL_KEYS = list(PROVIDERS.keys()) + ["local"]


def resolve_provider(cli_arg: str | None) -> str:
    """Resolve which provider key this run uses. Priority order:
    1. --llm=<key> (cli_arg, already stripped of the '--llm=' prefix by main.py)
    2. LLM_DEFAULT env var
    3. auto-detect: exactly one PROVIDERS entry has its key_env set in the environment -> use it
    4. interactive picker (tkinter popup, falling back to a terminal prompt on any failure)

    Exits the process (sys.exit(1), printing a clear message to stderr) on any failure mode:
    an unknown provider key, an explicitly-named provider whose required API key env var isn't
    set, or a picker that ends with no selection made. Never returns a key that hasn't been
    validated as usable.
    """
    if cli_arg:
        key = cli_arg.strip().lower()
        _validate_or_exit(key)
        return key

    if LLM_DEFAULT:
        _validate_or_exit(LLM_DEFAULT)
        return LLM_DEFAULT

    configured = [k for k, p in PROVIDERS.items() if os.environ.get(p["key_env"], "").strip()]
    if len(configured) == 1:
        return configured[0]

    return _interactive_pick(configured)


def _validate_or_exit(key: str) -> None:
    if key not in _ALL_KEYS:
        print(f"Unknown LLM provider '{key}'. Known providers: {', '.join(_ALL_KEYS)}", file=sys.stderr)
        sys.exit(1)
    if key != "local":
        env_name = PROVIDERS[key]["key_env"]
        if not os.environ.get(env_name, "").strip():
            print(f"--llm={key} (or LLM_DEFAULT={key}) requires {env_name} to be set in .env — refusing to start scraping without it.", file=sys.stderr)
            sys.exit(1)


def _interactive_pick(configured: list) -> str:
    """Fires only when neither --llm nor LLM_DEFAULT resolved a provider and auto-detection was
    ambiguous (zero or 2+ remote providers configured). Candidates are the remote providers that
    currently have an API key set, plus "local" always offered (Ollama needs no env var to be a
    legitimate choice — its actual availability is a runtime fact surfaced as a clear error from
    pipeline/analyst.py if missing, not something resolvable here). If zero remote providers are
    configured, candidates is just ["local"] — this function does NOT silently auto-select it;
    the user must still actively choose it, matching the "no silent fallback to a default" rule.
    """
    candidates = configured + ["local"]

    try:
        choice = _pick_via_tkinter(candidates)
        picker_ran = True
    except Exception:
        choice = ""
        picker_ran = False

    if not picker_ran:
        choice = _pick_via_terminal(candidates)

    if not choice:
        print("No LLM provider selected — aborting.", file=sys.stderr)
        sys.exit(1)

    _validate_or_exit(choice)
    return choice


def _pick_via_tkinter(candidates: list) -> str:
    """Raises on ANY failure (missing tkinter module, no display, anything) so the caller falls
    back to a terminal prompt — this is deliberately a broad try/except at the call site, not a
    narrow catch here, since a missing display raises tkinter.TclError at Tk() construction time
    while a missing tkinter build raises ModuleNotFoundError at the import above, and both must
    trigger the same fallback (see RESEARCH.md §6 — a DISPLAY env var pre-check would miss the
    Windows/Mac headless case entirely, which is why this wraps the real attempt instead)."""
    import tkinter as tk

    result = {"choice": ""}
    root = tk.Tk()
    root.title("Select LLM provider")
    tk.Label(
        root,
        text="No --llm flag or LLM_DEFAULT set, and provider auto-detection was\nambiguous. Pick which LLM backend this run uses:",
        justify="left",
    ).pack(padx=16, pady=(16, 8))

    def _select(key):
        result["choice"] = key
        root.destroy()

    for key in candidates:
        label = PROVIDERS[key]["label"] if key in PROVIDERS else "Local (Ollama)"
        tk.Button(root, text=label, width=30, command=lambda k=key: _select(k)).pack(padx=16, pady=4)

    tk.Button(root, text="Cancel", width=30, command=root.destroy).pack(padx=16, pady=(4, 16))
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
    return result["choice"]


def _pick_via_terminal(candidates: list) -> str:
    print("\nSelect LLM provider for this run:")
    for i, key in enumerate(candidates, 1):
        label = PROVIDERS[key]["label"] if key in PROVIDERS else "Local (Ollama)"
        print(f"  {i}. {label} ({key})")
    try:
        raw = input(f"Enter a number [1-{len(candidates)}], or press Enter to cancel: ").strip()
    except EOFError:
        return ""
    if raw.isdigit() and 1 <= int(raw) <= len(candidates):
        return candidates[int(raw) - 1]
    return ""
```

## Interfaces
- `resolve_provider(cli_arg: str | None) -> str` — the only function `main.py` (Task 005) calls.
  Returns a validated provider key (`PROVIDERS` key or `"local"`); never returns an unvalidated or
  unusable key — it calls `sys.exit(1)` itself on every failure mode rather than raising, so
  `main.py`'s call site needs no try/except around it.
- Depends on `config.models.PROVIDERS` and `config.models.LLM_DEFAULT` (Task 001).

## Constraints
- CLI-only — do not import this module from `app.py` or any template; CONTEXT.md explicitly
  defers any Flask/dashboard-facing provider picker (see its "Explicitly out of scope" section) —
  don't reopen that here even structurally.
- Do not pre-check the `DISPLAY` environment variable as a substitute for the try/except around
  the actual tkinter attempt — RESEARCH.md §6 confirms this would misfire on headless Windows/Mac
  (no `DISPLAY` var exists there even when a real display is present).
- Do not fall back to the terminal prompt after a *successful* tkinter session that the user
  explicitly cancelled — only fall back when the tkinter mechanism itself failed to run at all
  (see `_interactive_pick`'s `picker_ran` flag, which distinguishes these two cases exactly).
- Do not add a numeric or timed retry loop, or any other UX embellishment beyond what's specified
  above — keep this proportional to a small CLI utility.

## Verification
1. `py -c "import ast; ast.parse(open('pipeline/llm_select.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "from pipeline.llm_select import resolve_provider; print('import OK')"`
3. Exercise the explicit-flag path with a known-bad key (should exit 1 with a clear stderr
   message, zero LLM cost): PowerShell —
   `powershell -Command "py -c \"from pipeline.llm_select import resolve_provider; resolve_provider('not-a-real-provider')\""`
   — confirm this exits non-zero and prints the "Unknown LLM provider" message.
4. Exercise the explicit-flag path with a real key whose env var is deliberately unset (should
   exit 1 with the "requires ... to be set" message, zero LLM cost):
   `powershell -Command "$env:DEEPSEEK_API_KEY=$null; py -c \"import os; os.environ.pop('DEEPSEEK_API_KEY', None); from pipeline.llm_select import resolve_provider; resolve_provider('deepseek')\""`
5. Exercise the auto-detect success path (zero LLM cost — this only tests resolution, not a real
   API call): set exactly one provider's env var and confirm `resolve_provider(None)` returns that
   key without prompting:
   `powershell -Command "$env:DEEPSEEK_API_KEY='test-value-not-real'; py -c \"import os; os.environ['DEEPSEEK_API_KEY']='test-value-not-real'; from pipeline.llm_select import resolve_provider; print(resolve_provider(None))\""`
   — must print `deepseek` with no popup/prompt shown (only one provider env var was set).
6. Do not exercise the interactive-picker path against a real popup/terminal session in this
   task's automated verification (it blocks waiting for GUI/stdin input) — instead, in your
   evidence, walk through the `_interactive_pick`/`_pick_via_tkinter`/`_pick_via_terminal` code by
   hand against the two scenarios in the Constraints section above (tkinter unavailable →
   terminal fallback; tkinter available but cancelled → abort, no terminal fallback) and confirm
   by inspection that the logic matches.

## Evidence

1-2. Syntax OK, `resolve_provider` importable. 3. Unknown-key path: `resolve_provider('not-a-real-provider')` → stderr `Unknown LLM provider 'not-a-real-provider'. Known providers: deepseek, groq, qwen, kimi, local`, exit 1. 4. Missing-env-var path: `resolve_provider('deepseek')` with `DEEPSEEK_API_KEY` unset → stderr `--llm=deepseek (or LLM_DEFAULT=deepseek) requires DEEPSEEK_API_KEY to be set in .env`, exit 1. 5. Auto-detect path: exactly one provider env var set → `resolve_provider(None)` returns `deepseek`, no prompt shown, exit 0. 6. Interactive-picker path verified by code walkthrough (not executed, per task instruction — would block on GUI/stdin): confirmed the `picker_ran` flag correctly distinguishes "tkinter mechanism failed" (falls back to terminal) from "tkinter succeeded but user cancelled" (aborts, no fallback).

File content is byte-for-byte what the task specified. Not imported anywhere yet — task 005 wires the `main.py` call site.
