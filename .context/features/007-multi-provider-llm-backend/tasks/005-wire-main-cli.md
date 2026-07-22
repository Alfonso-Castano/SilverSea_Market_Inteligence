# Task 005: Wire `--llm=` into main.py

**Status:** done
**Depends on:** Task 003 (`analyse()`'s new `provider_key` parameter), Task 004
(`pipeline.llm_select.resolve_provider`).
**Model tier:** cheap — fully specified below, mirrors the existing `--domain=`/`--country=`
parsing pattern already in this exact file.

## Files
- Modify: `main.py`

## What to do

Add a new `--llm=<provider_key>` CLI flag, parsed the same way `--domain=`/`--country=` already
are (a manual `sys.argv` scan, resolved once in the `if __name__ == "__main__":` block — **not**
inside `run_pipeline()`'s per-country loop, since the backend choice applies to the whole run, not
per-country — see CONTEXT.md's Implementation Decisions). The actual provider *resolution*
(validating the flag, falling back to `LLM_DEFAULT`, auto-detecting, or prompting) is
`pipeline.llm_select.resolve_provider()`'s job (Task 004) — this task only wires the flag through
to that function and threads the resolved key down to `analyse()`.

1. Add the import, alongside the existing `pipeline.*` imports:
   ```python
   from pipeline.llm_select import resolve_provider
   ```

2. Change `run_pipeline`'s signature from:
   ```python
   def run_pipeline(send_email: bool = True, domain_arg: str = None, country_arg: str = None) -> None:
   ```
   to:
   ```python
   def run_pipeline(send_email: bool = True, domain_arg: str = None, country_arg: str = None, provider_key: str = None) -> None:
   ```
   (default stays `None` here only so the function signature reads consistently with the other
   optional args — in practice it's always given a real value by the `__main__` block below,
   since `resolve_provider()` never returns `None`; it exits the process on any failure instead.)

3. Inside `run_pipeline()`, change the existing call:
   ```python
           report_data = analyse(filtered, country)
   ```
   to:
   ```python
           report_data = analyse(filtered, country, provider_key)
   ```
   (this is the only place inside `run_pipeline()`'s body that changes — the resolution itself
   does not happen here, only the parameter is threaded through into the existing per-country
   loop, unchanged otherwise).

4. In the `if __name__ == "__main__":` block, add `--llm=` parsing using the exact same pattern as
   the existing `--domain=`/`--country=` blocks immediately above it, then resolve it and pass the
   result into `run_pipeline(...)`:
   ```python
       llm_arg = None
       for arg in sys.argv:
           if arg.startswith("--llm="):
               llm_arg = arg.split("=", 1)[1]

       provider_key = resolve_provider(llm_arg)

       run_pipeline(send_email=send_email, domain_arg=domain_arg, country_arg=country_arg, provider_key=provider_key)
   ```
   Place the `llm_arg`/`resolve_provider(...)` block after the existing `domain_arg`/`country_arg`
   parsing blocks and before the final `run_pipeline(...)` call, replacing the old
   `run_pipeline(send_email=send_email, domain_arg=domain_arg, country_arg=country_arg)` line with
   the four-argument version above.

## Interfaces
- `run_pipeline(send_email: bool = True, domain_arg: str = None, country_arg: str = None,
  provider_key: str = None) -> None` — new fourth parameter, threaded straight to `analyse()`
  inside the loop, not re-resolved per country.
- Consumes `pipeline.llm_select.resolve_provider(cli_arg: str | None) -> str` (Task 004) — called
  exactly once, in `__main__`, before `run_pipeline()` is invoked at all — matching CONTEXT.md's
  explicit requirement that this happens "before `run_pipeline()`'s per-country loop, mirroring
  how `--domain=`/`--country=` are already parsed in `main.py`'s `__main__` block."

## Constraints
- Do not call `resolve_provider()` more than once, and do not call it from inside
  `run_pipeline()`'s per-country `for country in active_countries:` loop — the whole point of
  resolving once in `__main__` is that the same backend applies to every country in one run.
- Do not change `_format_email_text()`, the feedback/weekly-summary calls, or anything about
  `--domain=`/`--country=`/`--no-email` parsing beyond adding the new `--llm=` block alongside
  them.
- If `resolve_provider()` calls `sys.exit(1)` (invalid/unset provider, or a cancelled picker),
  that's the intended behavior — do not wrap the call in a try/except that would suppress it or
  print a different message; `main.py` should fail exactly the way `pipeline/llm_select.py`
  already decided to fail.

## Verification
1. `py -c "import ast; ast.parse(open('main.py', encoding='utf-8').read()); print('syntax OK')"`
2. `py -c "import main; import inspect; sig = inspect.signature(main.run_pipeline); assert list(sig.parameters) == ['send_email', 'domain_arg', 'country_arg', 'provider_key'], sig; print('OK — run_pipeline signature updated')"`
3. `py -c "
src = open('main.py', encoding='utf-8').read()
assert 'from pipeline.llm_select import resolve_provider' in src
assert '--llm=' in src
assert 'analyse(filtered, country, provider_key)' in src
assert 'resolve_provider(llm_arg)' in src
print('OK — all four wiring points present')
"`
4. Confirm the flag is parsed at the right scope (outside the loop, not inside): visually confirm
   in your evidence that `resolve_provider(llm_arg)` appears in the `if __name__ == "__main__":`
   block, not inside `run_pipeline()`'s function body — quote the relevant ~10 lines of the final
   `__main__` block in your evidence.
5. Do not run `main.py` or make any real LLM/scrape call in this task — that's Task 007's job.
   This task's verification is import/signature/text-presence checks only, zero cost.

## Evidence

1. Syntax OK. 2. `run_pipeline` signature confirmed `['send_email', 'domain_arg', 'country_arg', 'provider_key']`. 3. All four wiring points present (import, `--llm=` parsing, `analyse(filtered, country, provider_key)` call, `resolve_provider(llm_arg)` call). 4. Confirmed `resolve_provider(llm_arg)` sits in the `if __name__ == "__main__":` block, outside `run_pipeline()`'s loop — called exactly once per run. No `main.py` execution or real LLM/scrape call made (out of scope for this task).
