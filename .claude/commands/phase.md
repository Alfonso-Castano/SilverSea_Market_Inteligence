---
name: phase
description: "Phase workflow: guides through Discuss → Plan → Execute → Review for a build phase. Run at the start of a new context when beginning or resuming a phase."
---

# Phase Workflow

This command guides through the four stages of a build phase.
Run it at the start of any context where you are beginning or resuming a phase.

---

## Step 1: Orient

Read the following files before doing anything else:
- `ROADMAP.md` — identify which phase is IN PROGRESS and what its goal is
- `PLAN.md` — check current task status
- `STATE.md` — check what was last worked on and any blockers
- `CONTEXT.md` — remind yourself of architectural decisions already made

Based on what you read, determine which stage this session starts at:

| Situation | Start at |
|---|---|
| No PLAN.md tasks exist for this phase yet | **Discuss** |
| PLAN.md exists but Alfonso wants to revisit scope | **Discuss** |
| PLAN.md exists and tasks are ready to start | **Execute** |
| PLAN.md exists and tasks are partially done | **Execute** (continue) |
| All PLAN.md tasks are checked off | **Review** |

Tell Alfonso which stage you're starting at and why, in one sentence.

---

## Stage 1 — Discuss

**Purpose:** Align on what the phase will build before writing a plan.

1. Summarise your understanding of the phase goal from ROADMAP.md in 3-5 bullet points
2. List any open questions or ambiguities — things that would block planning if unanswered
3. Ask Alfonso to confirm or correct your understanding
4. Do not start planning until Alfonso confirms alignment

When Alfonso confirms: move to Stage 2.

---

## Stage 2 — Plan

**Purpose:** Turn the agreed scope into an executable task list.

Rewrite `PLAN.md` with:
- Phase name and goal (from ROADMAP.md)
- **Done when** — one concrete, testable statement of phase completion
- **Tasks** — ordered list, each with:
  - Clear description of what to build/change
  - Which file(s) are touched
  - How to verify it works
- **Order of execution** — note which tasks are independent vs dependent
- **Verify Phase Complete** — checklist of end-to-end tests to run before calling the phase done

Show Alfonso the plan before executing. Wait for approval.

When Alfonso approves: move to Stage 3.

---

## Stage 3 — Execute

**Purpose:** Build what the plan says. Nothing more, nothing less.

Rules during execution:
- Work through PLAN.md tasks in order
- Mark each task `[x]` in PLAN.md as soon as it's complete — do not batch
- If a task reveals something unexpected, STOP and flag it to Alfonso before continuing
- Do not add scope — if something new comes up, add it to ROADMAP.md open questions
- Run verification step after each task, not just at the end
- When all tasks are done, run the full **Verify Phase Complete** checklist

When all tasks are checked and the checklist passes: move to Stage 4.

---

## Stage 4 — Review

**Purpose:** Confirm the phase delivered its goal, then update all context files.

1. Run the **Verify Phase Complete** checklist from PLAN.md — confirm every item passes
2. Write a one-paragraph phase summary:
   - What was built
   - What the quality/test result was
   - Any scope that was deferred and why
3. Update all context files via `/context-update`
4. In ROADMAP.md: mark this phase `[DONE]`, mark next phase `[IN PROGRESS]`
5. Tell Alfonso: "Phase [N] complete. [One sentence on what was built and the verification result.] Ready for Phase [N+1] — run /phase to begin."
