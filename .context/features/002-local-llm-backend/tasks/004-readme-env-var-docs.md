# Task 004: Document the local-backend env vars and a full setup runbook in README.md

**Status:** pending
**Depends on:** 001
**Model tier:** cheap — the exact wording/steps are specified below; transcription plus verification.

## Files
- Modify: `README.md`

## What to do

This task's audience is Alfonso following these steps by hand on a different physical machine (a work computer, freshly cloned) — write it as a literal runbook, not just a reference table. Pull every concrete detail (model source, filenames, commands, tag name) from `.context/features/002-local-llm-backend/RESEARCH.md` §2-§3 rather than re-deriving or approximating them.

1. In the `Environment Variables` table (currently lines ~61-67), add three rows after the `GROQ_API_KEY` row:

   ```markdown
   | `LLM_BACKEND` | Pipeline only | `groq` (default) or `local` — selects which LLM backend `pipeline/analyst.py` calls. `local` requires a locally-running Ollama server serving Qwen3-32B at Q6_K quantization (see "Local LLM Setup" below) |
   | `LOCAL_LLM_MODEL` | Local backend only | Ollama tag the Q6_K model was registered under (default `qwen3-32b-q6k`) |
   | `LOCAL_LLM_NUM_CTX` | Local backend only | Context window size passed to Ollama (default `32768`) |
   ```

2. Just above the `Environment Variables` section (after the existing `.env` code block at line ~48), no change is needed to that example block — `LLM_BACKEND` is optional and defaults to `groq`, so it shouldn't be added to the required-looking `.env` example; the table entry alone is sufficient. (This keeps the example minimal and matches the "zero behavior change unless explicitly opted in" framing from CONTEXT.md — don't add local-backend vars to the example block.)

3. Add a new `## Local LLM Setup (Optional)` section, placed after the existing `## Environment Variables` section, containing a numbered runbook covering, in order:
   - **Prerequisite hardware/software note**: this path needs a GPU with real VRAM headroom (developed against a 32GB RTX 5090; Q6_K weights are ~23GB) and Windows with Ollama installed.
   - **Step 1 — Install Ollama**: download/install from ollama.com for Windows; confirm with `ollama --version`.
   - **Step 2 — Get the Q6_K GGUF**: download `Qwen3-32B-Q6_K.gguf` from `bartowski/Qwen3-32B-GGUF` on Hugging Face (~23GB; note this is a large manual download, not something to script/automate here).
   - **Step 3 — Register it with Ollama**: create a one-line `Modelfile` (`FROM ./Qwen3-32B-Q6_K.gguf`) in the same folder as the downloaded GGUF, then run `ollama create qwen3-32b-q6k -f Modelfile`. Confirm with `ollama list` (should show `qwen3-32b-q6k`).
   - **Step 4 — Clone this repo and install Python deps**: `git clone`, `cd`, `pip install -r requirements.txt` (this pulls in the `ollama` package from task 001).
   - **Step 5 — Set `LLM_BACKEND=local`** in `.env` (alongside any other needed vars; `GROQ_API_KEY` is not required when running local-only).
   - **Step 6 — Verify the backend actually works**: run `py -m pytest tests/test_local_backend_smoke.py -v` (task 003's smoke test) and confirm it passes with real schema-compliant JSON output, not a skip — a skip means step 2 or 3 wasn't completed correctly.
   - **Step 7 — Run the real pipeline**: `py main.py --domain=BER --country=SG` (or whichever domain/country) with `LLM_BACKEND=local` set, to exercise the full pipeline end-to-end against the local model.
   - Note explicitly that quantization tag name / context window are overridable via `LOCAL_LLM_MODEL` / `LOCAL_LLM_NUM_CTX` if the exact setup differs (e.g. a different quant chosen, or VRAM headroom proves tighter than expected).

## Interfaces
- Consumes: the exact env var names `LLM_BACKEND`, `LOCAL_LLM_MODEL`, `LOCAL_LLM_NUM_CTX` as defined in `config/models.py` by task 001, and the exact model tag name (`qwen3-32b-q6k`) and GGUF source (`bartowski/Qwen3-32B-GGUF`) from RESEARCH.md §2 — if task 001 named the env vars differently, use those names instead, not the ones written here.

## Constraints
- Don't reorder or reword the existing table rows.
- Don't touch anything outside the `Environment Variables` section and the new `Local LLM Setup` section.
- Do not attempt to actually perform any of these steps (no downloading the GGUF, no running `ollama` commands) — this task only writes the documentation.

## Verification
Run `py -c "import re; content = open('README.md').read(); assert all(s in content for s in ['LLM_BACKEND', 'LOCAL_LLM_MODEL', 'LOCAL_LLM_NUM_CTX', 'Local LLM Setup', 'bartowski/Qwen3-32B-GGUF', 'ollama create', 'test_local_backend_smoke']); print('OK')"` — must exit 0 and print `OK`.

## Evidence
