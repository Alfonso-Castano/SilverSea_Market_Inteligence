# Task 001: Fix admin/viewer auth bypass and harden `/feedback` (`app.py`)

## Files

- `app.py` (modify only)

## What to do

Both fixes live in the same file and are bundled per CONTEXT.md's decision ("fold all three
recon findings in as one task alongside the auth-bypass fix"). Do not touch any other route.

**1. Auth bypass fix — `login()` (currently lines 172-185):**

- Add `import hmac` to the top-of-file imports (alongside the existing `import secrets`).
- Refuse admin login outright when `ADMIN_PASSWORD` is unset or empty — check this *before*
  comparing, so an empty/unset env var can never match an empty submitted field.
- Use `hmac.compare_digest` for both the admin and viewer password comparisons instead of `==`.
- Keep the exact same control flow otherwise (admin branch first, then viewer branch, same
  `session["role"]` values, same redirect/render behavior).

Replace:
```python
    if request.method == "POST":
        submitted = request.form.get("password", "")
        if submitted == os.environ.get("ADMIN_PASSWORD", ""):
            session["authenticated"] = True
            session["role"] = "admin"
            return redirect(url_for("report"))
        if submitted == _get_viewer_password():
            session["authenticated"] = True
            session["role"] = "viewer"
            return redirect(url_for("report"))
        return render_template("login.html", error="Incorrect password")
    return render_template("login.html", error=None)
```
with:
```python
    if request.method == "POST":
        submitted = request.form.get("password", "")
        admin_password = os.environ.get("ADMIN_PASSWORD", "")
        if admin_password and hmac.compare_digest(submitted, admin_password):
            session["authenticated"] = True
            session["role"] = "admin"
            return redirect(url_for("report"))
        if hmac.compare_digest(submitted, _get_viewer_password()):
            session["authenticated"] = True
            session["role"] = "viewer"
            return redirect(url_for("report"))
        return render_template("login.html", error="Incorrect password")
    return render_template("login.html", error=None)
```
(`_get_viewer_password()` always returns a real string — it seeds `changeme` on first run — so
no empty-guard is needed on that branch; only `ADMIN_PASSWORD` has an empty-default footgun.)

**2. `/feedback` hardening — `receive_feedback()` (currently lines 126-169):**

(a) Submitter sanitization — replace the current line
```python
    submitter = (data.get("submitter") or "anonymous").strip().replace(" ", "_")
```
with a version that strips path-traversal and filesystem-unsafe characters, not just spaces.
Use a whitelist regex (safer than a blacklist): keep only alphanumerics, underscore, and hyphen,
collapsing everything else (including `.`, `/`, `\`) to `_`, and fall back to `"anonymous"` if the
result is empty. Add `import re` to the top-of-file imports. Example implementation:
```python
    raw_submitter = (data.get("submitter") or "anonymous").strip()
    submitter = re.sub(r"[^A-Za-z0-9_-]", "_", raw_submitter) or "anonymous"
```

(b) `relevance_rating` crash guard — replace
```python
        "relevance_rating": int(data.get("relevance_rating") or data.get("relevance") or 0),
```
with a version that never raises on a non-numeric value. Return a clean 400 JSON error instead of
letting a `ValueError` propagate to a 500. Example:
```python
    raw_rating = data.get("relevance_rating") or data.get("relevance") or 0
    try:
        relevance_rating = int(raw_rating)
    except (TypeError, ValueError):
        return {"error": "relevance_rating must be a number"}, 400
```
Compute this *before* building the `feedback` dict, and use the `relevance_rating` variable in
place of the inline `int(...)` call inside the dict literal.

(c) CORS scoping — the route-blanket `@app.after_request add_cors` (currently lines 224-229)
applies `Access-Control-Allow-Origin: *` to every route including `/`, `/internals`, `/admin`.
Scope it to `/feedback` only. Replace:
```python
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response
```
with:
```python
@app.after_request
def add_cors(response):
    if request.path == "/feedback":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response
```

## Interfaces

No function signatures change. `receive_feedback()` gains one new early-return path (400 on bad
`relevance_rating`); all other response shapes (`"OK", 200`) are unchanged.

## Constraints

- Two shared static passwords (viewer/admin) via Flask sessions remain the auth model — do not
  add per-user accounts or change the session-cookie mechanism.
- Don't touch `require_login()`, `/login` GET rendering, `/admin`, `/admin/sources/...`, or any
  route besides `login()` and `receive_feedback()`/`add_cors()`.
- Don't change the `/feedback` route's existing behavior for valid input (still writes the same
  JSON shape to `data/feedback/` and, when `source_name` is present, to `data/pending_sources/`).
- No LLM calls involved — this task is fully verifiable by code inspection and local `curl`/Flask
  test-client exercise.

## Verification

Run these against the actual code (Flask dev server or `app.test_client()`), not just visual
inspection:

1. Start the app locally (`py app.py` or `flask run`, whichever this repo already uses) or use
   `app.test_client()` in a throwaway script.
2. **Auth bypass is closed:** with `ADMIN_PASSWORD` unset (or set to `""`), POST `/login` with
   `password=""` (empty) — must NOT redirect to `/` as admin; must re-render `login.html` with
   the error. Then POST `/login` with the real `VIEWER_PASSWORD`/`data/viewer_password.txt`
   content — must still succeed as viewer (regression check that the fix didn't break the
   working path).
3. **`/feedback` submitter sanitization:** POST `/feedback` with
   `submitter=..%2F..%2Fescape` (i.e. `../../escape`) and a `report_date` — inspect
   `data/feedback/` afterward and confirm the written filename contains only the sanitized
   `submitter` (no `..` or path separators) and lands inside `data/feedback/`, not outside it.
4. **`relevance_rating` crash guard:** POST `/feedback` with `relevance_rating=not_a_number` —
   must return HTTP 400 with a JSON error body, not a 500.
5. **CORS scoping:** GET `/` (after logging in, or via test client with a mocked session) and
   confirm the response has NO `Access-Control-Allow-Origin` header. POST `/feedback` and confirm
   it DOES have `Access-Control-Allow-Origin: *`.
6. Delete any test artifacts written to `data/feedback/`/`data/pending_sources/` during
   verification.

## Model tier

mid — code is fully specified above, but the executor must correctly wire the guard/regex into
existing control flow and verify the two behavioral edge cases (empty admin password, malformed
rating) actually trigger the new paths, not just eyeball the diff.

## Depends on

None.

## Evidence

**Status: DONE**

Verified live via `app.test_client()` with `ADMIN_PASSWORD` unset:
- Empty admin password: `/login` returns 200 with "Incorrect password" error, no redirect (bypass closed).
- Real viewer password still logs in: 302 redirect to `/` (regression check passed).
- `submitter=../../escape` sanitized to `20260708_053213_______escape.json` — written inside
  `data/feedback/`, no path traversal.
- `relevance_rating=not_a_number` → HTTP 400, `{"error": "relevance_rating must be a number"}`.
- `GET /` has no `Access-Control-Allow-Origin` header; `POST /feedback` has `Access-Control-Allow-Origin: *`.
- Test artifacts written during verification were deleted afterward.
- `git diff -- app.py` re-confirmed by the dispatching session to match the task spec exactly —
  only imports, `receive_feedback()`, `login()`, and `add_cors()` touched.
