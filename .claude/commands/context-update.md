---
name: context-update
description: "Update all context files at the end of a session: STATE.md (progress snapshot), CONTEXT.md (architectural decisions), PLAN.md (task status), ROADMAP.md (phase status). Run at the end of every session."
---

# Context Update — End of Session

Update all four context files in this order. Each file has a specific purpose — do not blur them.

---

## 1. Update STATE.md

Rewrite STATE.md as a current snapshot. It must reflect right now, not history.

Include:
- **Status line** — one emoji + phrase (🟡 In Progress, 🟢 Done, 🔴 Blocked)
- **Last updated** — today's date
- **Last worked on** — what was actually touched this session (be specific: file names, what changed)
- **What's Done** — full checkbox list of completed work across all sessions
- **What's In Progress** — only things actively being worked on right now
- **What's Next (Ordered)** — next 4-6 steps in priority order
- **Current Blockers** — anything stopping progress; "None" if clear
- **Recent Decisions** — decisions from the last 1-2 sessions (minor ones; architectural decisions go in CONTEXT.md)
- **Notes for Next Session** — 2-3 lines of specific handoff context

Keep it concise. Status snapshot only, not a log.

---

## 2. Update CONTEXT.md (only if needed)

Append to the Decision Log if a major architectural decision was made this session.

Format:
```
### [YYYY-MM] Short title
**Decision:** What was decided
**Reason:** Why — the constraint, tradeoff, or requirement that drove it
```

Only append genuinely architectural decisions: new technology chosen, module added, significant design tradeoff resolved. Do not append minor implementation choices.

---

## 3. Update PLAN.md

Update task checkboxes to reflect what was completed this session.

- Mark completed tasks `[x]`
- If a task was partially completed, add a short note below it
- If a new task was discovered mid-session, add it in the right position
- If the phase is fully complete, add a `## Phase Complete` section at the bottom with date and one-line summary

Do not rewrite the plan — only update status. Rewrites happen via `/phase` at the start of a new phase.

---

## 4. Update ROADMAP.md (only if phase status changes)

Only update ROADMAP.md if:
- A phase task was completed (tick the checkbox under that phase)
- A phase status changed (e.g., `[IN PROGRESS]` → `[DONE]`, or `[PENDING]` → `[IN PROGRESS]`)
- A new open question was resolved or added

Do not rewrite phase descriptions. Only update status markers and open questions.

---

## 5. Confirm

Tell Alfonso:
"Context updated. STATE.md: [one sentence on what changed]. PLAN.md: [tasks completed]. ROADMAP.md: [updated / not changed]. CONTEXT.md: [decision added / not changed]."
