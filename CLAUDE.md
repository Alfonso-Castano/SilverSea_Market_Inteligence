# CLAUDE.md — Market Intelligence Pipeline
## Silversea Media | Alfonso's Internship Project

@CONTEXT.md
@STATE.md
@ROADMAP.md
@PLAN.md

---

## What This Project Is

An automated weekly market intelligence pipeline for Silversea Media's BD/sales team.
It scrapes Singapore's built environment / construction / smart FM space, synthesizes
findings via Claude API, and delivers a weekly HTML report + email digest.

Read `PROJECT_REQUIREMENTS.md` for full context before doing anything else.

---

## Session Protocol

### Starting a Session
1. `CONTEXT.md` and `STATE.md` are auto-loaded via @imports above — read them before touching code
2. If either file appears outdated or contradicts the codebase, flag it to Alfonso before proceeding
3. Confirm your understanding of the current task before touching any code

### Ending a Session
1. Update `STATE.md` with: what was completed, any decisions made, blockers, next steps
2. If a major architectural decision was made, append it to `CONTEXT.md`
3. Keep `STATE.md` concise — it's a status snapshot, not a log

### Mid-Session
- Run `/compact` when context feels heavy — don't wait until it's bloated
- If something goes sideways, STOP and re-plan — don't keep pushing through

---

## Workflow

### 1. Plan Before Building
- For any task with 3+ steps or architectural implications: write the plan first, confirm with Alfonso
- Keep plans concise — bullet points, not essays
- For simple obvious tasks: just execute

### 2. Verify Before Done
- Never mark a task complete without proving it works
- Run the code. Check the output. Don't assume.
- Ask: "Would this actually work end-to-end right now?"

### 3. Minimal Impact
- Only touch files relevant to the current task
- Don't refactor things that aren't broken
- One change at a time — make it easy to isolate bugs

### 4. Fix Bugs Autonomously
- Given a bug: diagnose, fix, verify — don't ask for hand-holding
- Check logs and error output before asking questions
- If a fix feels hacky, find the clean solution instead

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- Skip this for simple obvious fixes — don't over-engineer
- Simple > clever, always

---

## Token Efficiency
*Alfonso is on a personal Claude Code plan — token use matters.*

- Read specific files, not whole directories, unless a full scan is genuinely needed
- Don't dump full file contents back in responses — summarize findings
- Ask targeted questions, not broad exploratory ones
- For simple tasks: skip planning ceremony and just execute
- Avoid re-reading files already in context

---

## Core Principles

- **Simplicity First** — make every change as simple as possible
- **No Laziness** — find root causes, no temporary fixes, senior developer standards
- **Minimal Impact** — changes should only touch what's necessary
- **No Guessing** — if something is unclear, ask Alfonso rather than assuming

---

## Architecture Quick Reference

```
GitHub Actions (weekly cron)
    → scraper.py       # fetches raw content from target URLs
    → filter.py        # keyword filtering, drops irrelevant content
    → analyst.py       # Claude API: summarize, score, find opportunities
    → report.py        # generates HTML report
    → emailer.py       # sends digest
    → Vercel           # serves updated HTML at live URL
```

Full architecture and rationale in `PROJECT_REQUIREMENTS.md`.
Key decisions and their reasons in `CONTEXT.md`.
