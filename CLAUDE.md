# CLAUDE.md — Market Intelligence Pipeline

Silversea Media | Alfonso's Internship Project

@.context/OVERVIEW.md @.context/STATE.md @.context/DECISIONS.md @.context/ROADMAP.md

Full context lives in `.context/` and is auto-loaded above. Read it before doing anything else — this file is the protocol layer, `.context/OVERVIEW.md` is the actual project description.

---

## Session Protocol

**Starting a session**
- OVERVIEW.md, STATE.md, and DECISIONS.md (and ROADMAP.md, if present) are auto-loaded via the `@imports` above — read them before touching anything.
- Native Auto Memory loads automatically alongside them; no action needed.
- If STATE.md looks stale relative to recent git activity, run `/update-context` before proceeding.
- Confirm your understanding of the current task before touching any code.

**Mid-session**
- Run `/update-context` anytime it'd help — a natural pause, a decision just got made, or before you'd lose your own thread. It's safe to run mid-task.
- Run `/compact` when context feels heavy — don't wait until it's bloated.
- If something goes sideways, STOP and re-plan immediately. Don't keep pushing on a plan that's already wrong.

**Ending a session**
- Run `/update-context` before you stop. This is manual and deliberate — there is no automatic hook doing it for you, by design.

---

## Building a Feature

For any new feature or non-trivial fix, start with `/feature` and describe what you want built. It classifies the request and tells you what runs next:

| Path | When | Commands |
|---|---|---|
| Fast path | Small, single-file, well-understood | `/feature-quick` |
| Full loop | Everything else, or any real uncertainty | `/feature-discuss` → `/feature-plan` (add `--thorough` for unfamiliar territory) → `/feature-execute` → `/feature-verify` |

Each stage writes to `.context/features/NNN-slug/` and tells you the next command — don't skip ahead. Every command here is explicit-invocation only; none fire on their own. Both paths end with a hard evidence gate before anything is called done (see **Verification Before Done** below) — this isn't optional ceremony, it's built into `/feature-quick` and `/feature-verify` directly.

On PASS, `/feature-verify` refreshes `.context/` itself as an announced final step — no separate `/update-context` needed for that event. Run `/update-context` manually for every other occasion.

---

## Subagent Strategy

Whenever scope is ambiguous, invoke the **`orchestrator`** skill and stop at the lowest rung of its ladder that works (single session → subagents → agent teams) — this applies to any task, not just `/feature-*` work.

Generate every dispatch prompt via **`prompt-engineer`** (task-file mode when a task file exists, from-scratch mode otherwise) — it owns the tier↔model mapping. Every dispatch states an explicit model tier; never let a subagent silently inherit the most expensive model available.

---

## Working Style

- **Plan before building.** Anything with real architectural weight or 3+ steps: use `/feature-discuss` and `/feature-plan`, don't just start editing. Genuinely simple, obvious tasks: skip the ceremony and execute directly.
- **Fix bugs autonomously.** Given a bug report, diagnose from the actual logs/errors/failing tests and fix it — don't ask for hand-holding. One reasonable attempt informed by the real error; if it fails again, stop and reconsider the root cause rather than re-patching the symptom a third time.
- **Demand elegance, in balance.** For non-trivial changes, pause and ask "is there a more elegant way?" If a fix feels hacky, ask "knowing everything I know now, what's the clean solution?" Skip this for simple, obvious fixes — don't over-engineer what doesn't need it.
- **Minimal impact.** Touch only what the current task needs. Don't refactor things that aren't broken. One change at a time — keep problems easy to isolate.

---

## Verification Before Done

Never mark anything complete without fresh evidence from this turn: name the exact command that proves the claim, run it now, read the output and exit code — "should work" means you skipped a step.

For this project specifically: verifying the pipeline (`main.py`) end-to-end means a live LLM call against Groq's free-tier daily quota (100k TPD) — don't burn it on speculative runs. Prefer stage-by-stage verification (scraper → filter → analyst → report, checked independently) over a full `py main.py` run unless a full-pipeline claim is actually being made. Flask-side changes (`app.py`, templates) can be verified by booting the app and curling the affected route — no LLM call needed.

This is a hard, mechanized gate inside `/feature-quick` and `/feature-verify` — see those skills for exactly how it's enforced.

---

## Token Efficiency

*Alfonso is on a personal Claude Code plan — token use matters.*

- Read specific files, not whole directories, unless a full scan is genuinely needed.
- Don't dump full file contents back into responses — summarize findings.
- Ask targeted questions, not broad exploratory ones.
- For simple tasks, skip planning ceremony entirely and go straight to `/feature-quick`.
- `STATE.md` is a snapshot, overwritten in place by `/update-context` — never let it grow into a log.
- `.context/research/` is read once at init and never re-read automatically — treat it as reference, not a recurring cost.
- Native Auto Memory already handles small recurring operational notes (build quirks, debugging fixes, inferred preferences) for free in the background — don't duplicate that inside `.context/` files, and don't ask about it explicitly.
- Every subagent dispatch carries an explicit model tier — see **Subagent Strategy** above.

---

## Honesty and Pushback

- If an idea has a gap, a redundancy, or a clearly better alternative exists, say so plainly before proceeding. Agreement for its own sake is not helpful here.
- No guessing — if something is genuinely unclear, ask rather than assume, and say explicitly when you're stating an assumption versus reporting a fact.
- Never round up a completion claim — see **Verification Before Done**.
- Auto Memory handles day-to-day self-correction automatically now; there's no manual lessons/mistakes log to maintain on top of it.

---

## Core Principles

- **Simplicity first** — make every change as simple as possible.
- **No laziness** — find root causes; no temporary fixes; senior-developer standards.
- **Minimal impact** — changes touch only what's necessary.

---

## Architecture Quick Reference

```
main.py (--domain=BER|EDU|GENERAL, --country=SG, --no-email)
    → pipeline/scraper.py       # tiered fetch: requests (default) / Scrapling stealth / Scrapling dynamic (JS)
    → pipeline/filter.py        # keyword-weighted relevance filter (priority vs. general keywords)
    → pipeline/analyst.py       # multi-pass Groq (llama-4-scout-17b): per-sector extract → per-sector
    |                           #   synthesize → single summary call. RAG context via vectorstore.
    → pipeline/vectorstore.py   # ChromaDB — RAG context, feedback digests, weekly/report-history summaries
    → pipeline/report.py        # structured JSON output, domain- and country-scoped filenames
    → app.py                    # Flask: /, /internals, /admin, /login, POST /feedback
        templates/               # base, report, internals, admin, login (Jinja2 + Tailwind CDN)

config/sources.json            # sector- (gov_agencies/associations/customers/partners/competitors/
                                #   general_news) and domain-tagged (BER/EDU/GENERAL) source list,
                                #   nested per country; config/sources.py is a thin loader + save_sources()
data/company_context.md        # RAG seed doc — Silversea's 7-sector product catalog, prospects, priorities
pipeline/feedback.py           # feedback aggregation → LLM digest → vector store
pipeline/weekly.py             # weekly compression of daily reports → vector store
pipeline/source_suggestions.py # admin-approval queue for sources suggested via the feedback form
```

Sectors describe each source's *relationship* to Silversea (who it comes from); `domain` describes the *industry* it covers (BER/EDU/GENERAL). These are orthogonal and both live per-source in `config/sources.json`.

Full decision history and rationale: `.context/DECISIONS.md`. Current state and open items: `.context/STATE.md`.
