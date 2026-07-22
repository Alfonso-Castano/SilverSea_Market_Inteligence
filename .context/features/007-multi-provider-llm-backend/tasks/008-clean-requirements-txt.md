# Task 008: Regenerate requirements.txt in real isolation — remove 79 unrelated packages

**Status:** done
**Depends on:** none (independent of every other task in this feature — `requirements.txt` only).
**Model tier:** cheap — mechanical, fully specified below; no design judgment required.

## Files
- Modify: `requirements.txt`

## Why this task exists

`/feature-verify`'s review of this feature (`REVIEW.md`, Finding 1) found that Task 002's
`py -m pip freeze > requirements.txt` was run against this dev machine's **global** Python
environment (no project `.venv` exists here), which captured every package installed for every
other tool/project on the machine — not just this project's dependencies. Comparing the full
top-level package-name set before and after Task 002 shows **79 net-new unrelated packages**:
`anthropic`, `fastapi`, `starlette`, `sse-starlette`, `python-multipart`, `mcp`,
`mcp-server-fetch`, `google-generativeai`, `google-genai`, `google-api-python-client`, `pyasn1`,
`rsa`, `cachetools`, `pygame`, `nba_api`, `matplotlib`, `pandas`, `shap`, `scipy`, `numba`,
`llvmlite`, `pytest`, `pywin32`, `cryptography`, `openpyxl`, `fpdf2`, and 22 separate
`tree-sitter-<language>` grammar packages, among others — none of which this Flask/scraping/RAG
pipeline needs. A UTF-8 BOM was also introduced at the start of the file. This directly undoes the
prior "GitLab clone-readiness audit" hardening of this exact file (see `.context/STATE.md`) and
means a fresh `git clone` + `pip install -r requirements.txt` (this project's own documented
onboarding path, per `README.md`) now pulls down dozens of unnecessary, sometimes large packages.

## What to do

1. Create a genuinely isolated virtual environment scoped to just this project — do not reuse the
   machine's global site-packages:
   ```
   py -m venv .venv-regen
   .venv-regen\Scripts\pip install --upgrade pip
   ```
2. Install exactly the documented top-level dependency list plus this feature's two additions
   (`openai`, `ollama`) — nothing else, no left-over packages from any other tool:
   ```
   .venv-regen\Scripts\pip install groq requests beautifulsoup4 python-dotenv chromadb sentence-transformers "scrapling[fetchers]" flask Jinja2 openai ollama
   ```
3. Regenerate the file from that clean environment only:
   ```
   .venv-regen\Scripts\pip freeze > requirements.txt
   ```
   Write the file as UTF-8 **without a BOM** (confirm with
   `py -c "print(open('requirements.txt','rb').read()[:3])"` — must NOT print `b'\xef\xbb\xbf'`).
4. Restore the file's existing header comment (the one already in the file), updating only the
   documented top-level list and the regeneration `pip install` line to include `openai` and
   `ollama` — same content Task 002 already wrote for this part, don't rewrite it:
   ```
   # Pinned to exact versions from a clean install under Python 3.12.3 (see .python-version).
   # Direct top-level dependencies: groq, requests, beautifulsoup4, python-dotenv,
   # chromadb, sentence-transformers, scrapling[fetchers], flask, Jinja2, openai, ollama — everything
   # else below is a transitive dependency pinned via `pip freeze` for reproducibility.
   # To regenerate: create a fresh venv under 3.12.3, `pip install groq requests
   # beautifulsoup4 python-dotenv chromadb sentence-transformers "scrapling[fetchers]"
   # flask Jinja2 openai ollama`, then `pip freeze > requirements.txt`.
   ```
5. Delete the throwaway `.venv-regen` directory once `requirements.txt` is written — it must not
   be committed or left in the working tree (add a one-line `.venv-regen` ignore rule only if you
   find yourself needing to re-run this more than once in the same session; otherwise just delete
   it and confirm `git status` shows nothing extra).
6. Confirm the result contains `openai` and `ollama` (this feature's actual additions) and does
   **not** contain any of the 79 packages listed in the "Why this task exists" section above, nor
   any other package unrelated to this project's documented top-level list and its normal
   transitive dependencies.

## Interfaces
None — dependency manifest only, no code interface. `openai`/`ollama` import checks (already
proven working in Task 002/003) are unaffected by this task; only the *file contents* change.

## Constraints
- Do not hand-pick which of the 79 packages to keep or drop — the point is a clean regeneration
  from real isolation, not manual curation of a polluted list. If the clean venv genuinely needs a
  package not in the documented top-level list (shouldn't happen, but if `scrapling[fetchers]` or
  `chromadb` pulls in something unexpected), that's fine to keep — the test is "does this trace
  back to an actual dependency of the documented top-level list," not "is the file short."
- Do not touch any other file in this task.
- Do not skip the BOM check — confirmed root-caused as part of the same regeneration problem, not
  a separate issue to defer.
- Do not commit the throwaway `.venv-regen` directory.

## Verification
1. `py -c "content = open('requirements.txt', encoding='utf-8').read(); assert 'openai==' in content and 'ollama==' in content; print('OK — both present')"`
2. `py -c "print(open('requirements.txt','rb').read()[:3])"` → must print `b'# P'` or similar
   (plain ASCII `#`), NOT `b'\xef\xbb\xbf'`.
3. Re-run the same package-set comparison the review used, against this task's own regenerated
   file, and confirm the result is empty (or contains only packages you can trace to the
   documented top-level list's real transitive dependencies):
   ```
   git show ad81ca161e35f148eb86bd9313e65d4bc4bda2f9:requirements.txt | grep -oE '^[A-Za-z0-9_.\-]+' | sort -u > old_pkgs.txt
   grep -oE '^[A-Za-z0-9_.\-]+' requirements.txt | sort -u > new_pkgs.txt
   comm -13 old_pkgs.txt new_pkgs.txt | grep -viE '^(openai|ollama)$'
   ```
   Paste the actual output in your evidence — if anything beyond a small number of genuinely
   explainable transitive additions appears, investigate before reporting done, do not just note
   it and move on.
4. `git status --short` — confirm no `.venv-regen` directory or other stray files remain.
5. Confirm `py -m pytest tests/test_clamp.py -q` still passes (proves the regenerated file didn't
   somehow break an already-working import chain — this test needs no LLM call).

## Evidence

Regenerated from a genuinely isolated throwaway `.venv-regen` (installed exactly the documented top-level list plus `openai`/`ollama`, nothing else), then deleted.

1. `openai==` and `ollama==` both present. 2. `open('requirements.txt','rb').read()[:3]` → `b'# P'` — no BOM. 3. Package-set comparison against base (`comm -13 old new`, excluding openai/ollama) → `jiter` only (a legitimate transitive dependency of `openai`) — independently re-confirmed by the dispatching session, not just the executor's own report. 4. `git status --short` → only `requirements.txt` modified, no `.venv-regen` residue. 5. `py -m pytest tests/test_clamp.py -q` → `6 passed`.

79 previously-injected unrelated packages (fastapi, pygame, nba_api, tree-sitter-* grammars, etc.) all confirmed absent. File is 131 lines, down from the polluted version.
