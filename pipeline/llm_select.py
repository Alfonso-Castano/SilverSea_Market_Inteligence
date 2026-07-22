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
