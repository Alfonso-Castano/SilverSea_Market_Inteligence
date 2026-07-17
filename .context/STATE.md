# Project State

🟢 Working prototype, presented to supervisor; now split across two remotes with a documented publish workflow.

## Reference

See: .context/OVERVIEW.md
See: .context/ROADMAP.md
See: .context/DECISIONS.md

**Core value:** A daily report that surfaces actionable, source-cited BD signals and opportunities the sales team wouldn't otherwise catch — and gets measurably better over time from team feedback, without fabricating connections that aren't actually in the source material.

**Last updated:** 2026-07-17

## Repository Setup — read this first

This repo now pushes to **two remotes**, each seeing a different tree:

- **`origin`** — Alfonso's personal GitHub. `main` pushes here as always, full history, `.claude/`, `.context/`, `CLAUDE.md` all included. **This stays the working branch for every session** — nothing about day-to-day work changes.
- **`gitlab`** — the company-wide repo at `git.silversea-media.net/silversea-media/marketintelligent/ai-mi`, what the rest of the Silversea team actually clones and runs. A dedicated branch, **`gitlab-main`**, is what gets pushed there — it's `main` with `.claude/`, `.context/`, and `CLAUDE.md` untracked (still on disk, still tracked on `main`; just not part of what GitLab sees).

**Publish workflow, every time there's something ready for the team:**
```
git checkout gitlab-main
git merge main                          # will conflict on .gitignore — keep gitlab-main's version
git push gitlab gitlab-main:main
git checkout main                       # back to normal work
```
Full rationale in `.context/DECISIONS.md` (2026-07-17 entry). A GitLab personal access token was pasted into an earlier chat and had to be treated as compromised — revoked and replaced. The new token is never embedded in the remote URL or typed into a chat; it's cached by Git Credential Manager (Windows Credential Manager) after one manual authenticated `git fetch gitlab` in a real terminal. If push/fetch against `gitlab` ever fails with an auth error, that's a stale-credential problem to solve outside the chat, not something to fix by putting a token anywhere in a command or message.

Current state: `gitlab-main` has been pushed three times now — most recently commit `9654272` (GitHub `main` at `ab71597`), confirmed live on GitLab via `git ls-tree` after each push (`.claude`/`.context`/`CLAUDE.md` verified absent every time). **The GitLab repo has now been announced to the team as ready for testing** (message sent 2026-07-17) — this is the first time this repo has been handed to anyone outside Alfonso.

## What's Done

- **Phases 1-3** (Foundation, AI Brain, Web Dashboard) — see `.context/ROADMAP.md` for detail.
- **Supervisor Feedback Round 2** — auth, scoring rubric, PDF export, `sources.json` migration, domain/country scaffolding.
- **Feature 001 — Round 2 Remediation** — auth bypass fix, `/feedback` hardening, SpatioX→real-catalog rebuild, first unit test.
- **Features 003-006 — Vietnam + Malaysia + full domain activation + accuracy review** — all merged to `main` (commit `9e09c8f`). Vietnam (60 sources, 43 active) and Malaysia (55 sources, 52 active) are both real, fully wired countries alongside Singapore (62 sources, 57 active) — 152 active sources total across 3 countries. All 8 business domains (BER/EDU/GENERAL/RCC/HLS/MFG/CTE/PSS) are tagged and routable via `--domain`.
- **Presentation-prep session (2026-07-13)** — UI consolidated to 3 visible domain tabs (EDU/BER/GENERAL) per country, folding RCC/HLS/MFG/CTE/PSS content into GENERAL with per-item domain badges (source tagging and `--domain` routing for all 8 domains still fully intact underneath); leaked "No actionable signals" placeholder cards removed (render-time filter + prompt hardening); "Log in as Admin" shortcut added for viewer sessions; admin source-approval card layout fixed (was overflowing its container since Feature 005 added 5 more domain checkboxes without adjusting the layout); VN/MY report gaps filled via live pipeline runs (MY/BER and VN/GENERAL newly generated, VN/BER refreshed to fix stale pre-Feature-005 domain tags); both Vietnam's and Malaysia's source-submission PDFs cross-referenced line-by-line against `config/sources.json` — confirmed 60/60 VN and 55/55 MY sources present and correctly tagged.
- **GitLab clone-readiness audit + fixes** — `sentence-transformers` added to `requirements.txt` (was silently missing, broke `main.py`/`feedback.py`/`weekly.py` with `ModuleNotFoundError` on a fresh install); `requirements.txt` pinned to exact versions from a clean install under Python 3.12.3 (matching prod, not this dev machine's 3.13.5); `.python-version` added; `.env.example` added listing all 6 real env vars; README rewritten twice — first for accuracy (login wall, `scrapling install` step, current multi-country architecture), then reordered so Build & Run comes before the project description, per a team request that a new person get to a running app before reading about RAG/ChromaDB/scoring. Both README passes were verified against genuine fresh `git clone` tests, not just written from memory.
- **Two-remote GitLab split** — see "Repository Setup" above.
- **GitLab clone-readiness live review + shared-password fix (2026-07-17)** — a genuinely fresh `git clone` of the GitLab repo (separate scratch directory, not Alfonso's working copy) was walked through the README's Build & Run section end-to-end: dependency install, `.env` setup, app boot, login flow, admin-refusal check, and a zero-cost `--domain=EDU --country=SG` pipeline run — all confirmed working. Found and fixed a real bug in the process: `.env`'s `VIEWER_PASSWORD=` (present but blank) was being read by `python-dotenv` as an empty string, not an unset variable, so `os.environ.get("VIEWER_PASSWORD", "changeme")` never applied its default — a new teammate following the README's own instructions (log in with `changeme`) would hit "Incorrect password." Fixed by changing the viewer password to a hardcoded shared default (`Silversea`, in `app.py`) rather than an env-only fallback, since `VIEWER_PASSWORD` is meant to be known company-wide by design — every clone now gets working dashboard access with zero `.env` setup. `ADMIN_PASSWORD` deliberately kept `.env`-only with no default, since baking an admin credential into a git-committed file would give every clone admin rights. Both fixes verified live (not just logic-checked) against a second fresh clone after publishing. README also had a dead link to `.context/DECISIONS.md`/`STATE.md` removed (those files don't exist in the GitLab tree) and gained a short note on `.env` being local-only/per-machine. **The GitLab repo was then announced to the team as ready for testing.**

## What's In Progress

Team is now testing the GitLab clone for the first time. Nothing else actively in flight.

## What's Next (Ordered)

1. Watch for team feedback on the GitLab clone-and-run experience — first real external test of the README and onboarding flow.
2. **Alfonso has confirmed he wants tighter, per-person access control eventually** (not just a shared admin password) — likely real user accounts instead of the current two-shared-static-password model. Explicitly fine to defer while the team is just testing; revisit once testing feedback comes in. Not yet scoped as a feature.
3. Decide how to sequence the deferred-work list below — the `source_name` attribution breakage is the most severe open item.
4. `feature/002-local-llm-backend` needs real end-to-end verification against actual Ollama + a real model on GPU hardware — the code has been statically reviewed twice and looks correct, but has never produced a verified pass anywhere (see below).
5. Malaysia's thin signal density needs manual re-sourcing of better newsroom URLs (not a code fix) if BD wants deeper MY coverage.
6. Decide whether/when to bring `feature/002-local-llm-backend` into the GitLab-facing tree, once it's actually verified — right now it should stay GitHub-only/experimental.

## Current Blockers

None. All work described above is committed on `main` and (as of the last publish) live on `gitlab-main`/GitLab.

## Recent Decisions

- Domain UI consolidated back to 3 tabs (EDU/BER/GENERAL) per country, with the other 5 domains folded into GENERAL rather than removed — preserves the underlying 8-domain data model, just simplifies what's shown until there's real content in those domains.
- Ollama was installed on this dev machine for `feature/002` investigation, then explicitly **not** used to pull a model or run a real test, per Alfonso's direction mid-session — that branch's real verification is deferred to actual target GPU hardware, not this machine.
- Two-remote setup (`origin`=GitHub, `gitlab`=company) chosen over two separate repos, to keep one shared commit history — `gitlab-main` untracks the Claude-tooling files rather than a second repo maintained by hand. Full rationale in `.context/DECISIONS.md`.
- `VIEWER_PASSWORD` given a hardcoded shared default (`Silversea`) instead of relying on an `.env`-blank fallback that turned out to be broken; `ADMIN_PASSWORD` deliberately kept env-only, no default, distributed out-of-band only to admin-role people. Alfonso confirmed he'll want real per-user access control later, but the shared-password model is fine while the team is just testing. Full rationale in `.context/DECISIONS.md`.

## Notes for Next Session

- If asked to publish to GitLab: use the workflow above, don't improvise a different merge/push sequence.
- `feature/002-local-llm-backend` is real, unmerged, and genuinely untested against a live model — don't claim it works, don't merge it into `main` or `gitlab-main` without Alfonso explicitly confirming it's been verified on real hardware.
- Known bugs below are mostly still open — nothing in this session touched `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT` (the `source_name` fix) or the fabricated-product-name issue.
- The team is now actually using the GitLab clone — expect real feedback/bug reports from people other than Alfonso for the first time. Don't assume issues they report are code-review-confirmed already; treat as fresh reports.
- If asked to build tighter access control: this means moving off the two-shared-static-password model toward real per-user accounts — a genuinely new architectural decision (reversing the OVERVIEW.md "explicitly out of scope" call on per-user auth), not a tweak. Treat as its own `/feature-discuss`, not a quick fix.

## Known Bugs / Open Items

**Most severe, still open:**
- **`source_name` attribution broken** — most VN signals/opportunities (and some MY) carry the literal placeholder `"Extracted signals"` instead of a real source name. Root cause: `pipeline/analyst.py`'s `_synthesize_sector()` user-message has no enforced per-source delimiter around extraction text, so the model grabs the wrapper label itself. Predates Features 003-006; needs prompt-engineering judgment on `SECTOR_EXTRACT_PROMPT`/`SECTOR_SYNTHESIS_PROMPT`, not a mechanical patch.

**Confirmed root-caused, deliberately deferred (not bugs to "fix" quickly, need real design work):**
- **"For Silversea Media" implication text is repetitive within a sector** — `_generate_implications()` is a deliberate zero-LLM-cost keyword-matching function (~14 phrases + 6 generic per-sector fallbacks), not per-signal LLM generation. Alfonso wants this genuinely unique per signal eventually (likely needs LLM involvement, probably paired with a local-backend cost story) and also wants "two signals would get an identical implication" used as a signal to consider *consolidating* those signals.
- **Malaysia's BER/GENERAL signal density is much lower than Vietnam's** — confirmed as a source-quality issue (most MY source URLs are generic homepages, not newsroom pages; MY's list is dominated by small local vendors vs. VN's global-tech-vendor-heavy competitor list), not a scraping/filter/LLM bug. Fix requires manual re-sourcing, same effort as the original SG sourcing pass.
- **Fabricated Silversea product names in some opportunities' `product_fit` fields** (e.g. "Building Automation", "Smart Building" — not real catalog products).
- **`filter.py`'s per-country relevance gate vs. `SUMMARY_PROMPT`'s hardcoded-global opportunities gate diverge** — widest for VN, where dual BER+EDU-tagged sources create an EDU→BER leak path.
- **`_build_rag_context()` is confirmed dead code** (never called); `REPORT_HISTORY` writes are country-scoped but domain-blind — a dormant cross-domain contamination trap if RAG context is ever restored.
- **`analyse()` receives no explicit `domain` parameter** — every `product_fit` judgment reasons across all 7 sector catalogs regardless of which domain the report is actually for.
- **One confirmed cross-source content contamination instance** — a VN Becamex IDC signal contains text copy-pasted near-verbatim from a different cited source in the same report. Not systemically checked beyond this one instance.

**`feature/002-local-llm-backend` (unmerged, GitHub-only):**
- Code statically reviewed twice (original feature review + this session's GitLab-readiness audit) — dispatch logic, JSON schema enforcement, and the `LLM_BACKEND=local` guard against requiring `GROQ_API_KEY` all check out correct on inspection.
- **Never verified against a real model on any machine.** Its own smoke test has never produced a pass — always skips cleanly (no Ollama server present) rather than actually exercising a live call. Ollama is now installed on this dev machine but deliberately untested (no model pulled) per Alfonso's explicit direction.
- Branched from an older `main` (pre-Vietnam/Malaysia) — bringing it into current `main` will need a real merge/rebase, not just a checkout.
- **Do not present this as working or bring it into the GitLab-facing tree until it's actually been run against a real model on real hardware.**

**Explicitly deferred future work (Alfonso confirmed intent, not yet scoped):**
- **Real per-user access control**, replacing the two-shared-static-password model — Alfonso confirmed (2026-07-17) he wants this once the team moves past just testing. Current model has no audit trail (can't tell which admin approved a source or rotated a password, only that *someone* with the shared secret did) and no way to revoke one person's access without changing the password for every admin. This reverses `.context/OVERVIEW.md`'s "explicitly out of scope" call on per-user auth — treat as a real scope change needing its own discussion, not a quick patch.

**Smaller, longstanding, lower priority:**
- SG has no real sources tagged for the 5 newer verticals (RCC/HLS/MFG/CTE/PSS) — will show empty under those domains until sources are added.
- No LLM rate limiter despite an old decision recording one.
- Email digest likely renders blank (`main.py`'s MIME part ordering).
- `run_metadata.json` writes are skipped entirely when a domain run finds zero relevant sources (early-return happens before the metadata write).
- Dead file: `scripts/feedback_server.py`, superseded by `app.py` long ago.
- `?demo=feedback` toggle non-functional — `data/presentation/` doesn't exist.
- `config/sources.json`'s `_domain_tagging_status` draft flag still unreviewed.
- VN keyword filter is English-only, no Vietnamese-language matching — not empirically checked against a live run.
- Indonesia country expansion — fully unbuilt; VN/MY establish a reusable pattern but nothing extends to it yet.
- Real-browser visual QA of PDF print-preview and login/admin page styling — still open, pixels-need-eyes items.
