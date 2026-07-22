# Task 002: Add `openai` and `ollama` to requirements.txt

**Status:** done
**Depends on:** none — different file from every other task in this feature, safe to run in
parallel with Task 001.
**Model tier:** cheap — mechanical dependency addition, fully specified below.

## Files
- Modify: `requirements.txt`

## What to do

This repo's `requirements.txt` is a full `pip freeze` output, regenerated from a documented
top-level install list (see the file's own header comment). Two new top-level packages are
needed: `openai` (the generic OpenAI-compatible client used for Groq/DeepSeek/Qwen/Kimi — see
Task 003) and `ollama` (the local backend's native client, reused from
`feature/002-local-llm-backend`, already installed on this dev machine per RESEARCH.md §9 but not
yet in this file).

1. Update the header comment's documented top-level list to add `openai` and `ollama` alongside
   the existing ones (`groq, requests, beautifulsoup4, python-dotenv, chromadb,
   sentence-transformers, scrapling[fetchers], flask, Jinja2`) and update the regeneration
   instructions to include them in the `pip install` line.
2. In an actual Python 3.12.3-equivalent environment (this dev machine has no project `.venv` —
   use the global `py` interpreter, matching how this file was generated previously per its own
   header comment; `ollama` is already installed globally here, `openai` is not — see
   RESEARCH.md §9), run:
   ```
   py -m pip install openai ollama
   py -m pip freeze > requirements.txt
   ```
   This regenerates the entire pinned list from what's actually installed — expect other
   transitive-dependency version lines to shift slightly beyond just the two new entries; that's
   expected and correct (matches how this file has always been regenerated, per its own header
   comment's instructions), not a mistake to avoid.
3. Confirm `openai` and `ollama` both appear as top-level pinned entries in the resulting file.

## Interfaces
None — this is a dependency manifest only, no code interface.

## Constraints
- Do not hand-edit individual version pin lines to "fix" something that looks different from
  before — a full regenerated `pip freeze` is the correct, established process for this file (see
  its own header comment); resist the urge to selectively edit.
- Do not add any package beyond `openai` and `ollama` — if `pip freeze` picks up unrelated drift
  from packages already in the file (e.g. a transitive dependency bump unrelated to this feature),
  that's expected and fine; don't manually prune it back to the old pins.

## Verification
1. `py -c "content = open('requirements.txt', encoding='utf-8').read(); assert 'openai==' in content or 'openai ' in content; assert 'ollama==' in content or 'ollama ' in content; print('OK — both present')"`
2. `py -c "import openai; print('openai', openai.__version__)"` and
   `py -c "import ollama; print('ollama import OK')"` — both must succeed after step 2 above.
3. Paste the actual `git diff requirements.txt` line count (insertions/deletions) into your
   evidence — this file changes substantially on every regeneration, so a "looks about right" 
   claim isn't sufficient; show the real diff stat.

## Evidence

1. `py -c "content = open('requirements.txt', encoding='utf-8').read(); assert 'openai==' in content or 'openai ' in content; assert 'ollama==' in content or 'ollama ' in content; print('OK — both present')"` → `OK — both present`
2. `py -c "import openai; print('openai', openai.__version__)"` → `openai 2.46.0`; `py -c "import ollama; print('ollama import OK')"` → `ollama import OK`
3. `git diff --stat requirements.txt` → `requirements.txt | 192 +++++++++++++++++++++++++++++++++++++++----------------` / `1 file changed, 136 insertions(+), 56 deletions(-)`

Full `pip freeze` regeneration completed as specified (`openai==2.46.0`, `ollama==0.6.2` pinned); other transitive versions shifted as expected, left as-is per constraint.
