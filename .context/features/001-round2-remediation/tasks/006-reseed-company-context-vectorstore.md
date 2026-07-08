# Task 006: Re-seed ChromaDB's `COMPANY_CONTEXT` collection

## Files

- None modified. This task runs the existing `scripts/seed_vectorstore.py` unchanged.

## What to do

`data/company_context.md` was rebuilt by task 003 (SpatioX→real-catalog terminology fix in the
three remaining sections). ChromaDB does not re-read the source file on its own — per
`OVERVIEW.md`'s Global Constraints, any content change there requires re-running
`scripts/seed_vectorstore.py` to actually take effect.

Run the existing script exactly as-is — no code changes:
```
py scripts/seed_vectorstore.py
```
(or `python3 scripts/seed_vectorstore.py`, whichever this environment's working Python
invocation is — confirm which one is on PATH before running; both `python3` and a Windows `py`
launcher are known to be usable in this repo's dev environment).

This deletes and rebuilds the `COMPANY_CONTEXT` collection (see `scripts/seed_vectorstore.py`'s
`seed()` function: `client.delete_collection(COMPANY_CONTEXT)` then `add_documents(...)`). It uses
ChromaDB's local embedding function only — **no Groq/LLM API call is made by this script**, so it
does not touch the Groq daily quota and is safe to run as an executor task.

## Interfaces

None — no code interfaces change. This task's "interface" is the script's existing CLI entry
point (`if __name__ == "__main__": seed()`), unchanged.

## Constraints

- Do not modify `scripts/seed_vectorstore.py` itself — this task is a run-and-verify task, not a
  code change.
- Must run *after* task 003 lands (the company-context content it seeds must be the corrected
  version, not the pre-fix SpatioX-laden version) — see Depends on below.
- This does write to the local ChromaDB persistent store on disk (whatever path
  `pipeline/vectorstore.py`'s `get_client()` points at) — that's expected and desired, it's the
  entire point of this task.

## Verification

1. Run `py scripts/seed_vectorstore.py` (or `python3 scripts/seed_vectorstore.py`) and capture
   stdout — must print `Seeded N chunks into 'company_context' collection.` (or whatever the
   actual `COMPANY_CONTEXT` constant's value is — check `pipeline/vectorstore.py` for the exact
   collection name string) with `N > 0` and exit code 0, no traceback.
2. Confirm the rebuild actually happened by querying the collection directly afterward:
   ```python
   from pipeline.vectorstore import get_collection, COMPANY_CONTEXT
   col = get_collection(COMPANY_CONTEXT)
   result = col.get(limit=200, include=["documents"])
   docs = result.get("documents", [])
   assert not any("SpatioX" in d for d in docs), "stale SpatioX chunks still present after re-seed"
   print(f"{len(docs)} chunks confirmed, zero contain 'SpatioX'")
   ```
3. If step 1 or 2 fails with an import error related to `sentence-transformers` or a model
   download timeout, that's a pre-existing environment condition (see STATE.md's known-bugs
   section on `sentence-transformers`), not something this task should attempt to fix — report it
   as a blocker rather than patching `pipeline/vectorstore.py`, which is out of this task's scope.

## Model tier

cheap — mechanical script execution plus a verification query; no code to write.

## Depends on

Task 003 (`003-company-context-catalog-rebuild.md`) — must run after the content fix lands, not
before, since re-seeding before the fix would just re-embed the stale SpatioX content.

## Evidence

**Status: DONE**

- `py scripts/seed_vectorstore.py` → `Seeded 34 chunks into 'company_context' collection.` exit 0.
- Verification query: `34 chunks confirmed, zero contain "SpatioX"`.
- No git-tracked files changed — this task only writes to the local ChromaDB persistent store
  (untracked, as expected).
