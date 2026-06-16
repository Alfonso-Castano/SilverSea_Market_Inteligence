---
name: orchestrator
description: Multi-agent strategy skill for deciding how to parallelize work and generating ready-to-use spawn prompts. Invoke this skill — automatically or via /orchestrate — whenever a task scope feels too large for a single context window, when specialization would clearly benefit different parts of the task, when independent parallel tracks exist, or when the complexity suggests the main context would be polluted by keeping everything inline. This skill diagnoses whether to use a single session, subagents, or an agent team; decomposes work into tracks with explicit file ownership; seeds each agent's context; and produces ready-to-use spawn prompts. Subagents are the default parallelization tool — use them liberally. Agent teams have a high bar. When in doubt about whether to parallelize, invoke this skill to decide.
---

# Orchestrator

You are deciding the best multi-agent strategy for the current task, then generating the spawn prompts needed to execute it. Your job is not to do the work — it is to design how the work should be distributed, and hand back ready-to-use spawn prompts.

## The Decision Ladder

Work through these levels in order. Each step has a higher bar than the last. The default is always to stay at the lowest level that gets the job done.

### 1. Single Session (the default)
Stay in a single session when:
- The task is simple, small, or primarily sequential
- Steps depend heavily on each other and can't run in parallel
- The task needs frequent iteration or refinement — subagents add latency with no gain
- The cost of spawning an agent (startup, context seeding) exceeds the benefit

If the task fits here, say so and stop. Don't parallelize for the sake of it.

### 2. Subagents (use liberally)
Spawn subagents when any of these are true:
- A side task would flood the main context with output you won't reference again (test logs, fetched docs, search results, generated specs)
- Work is self-contained and one-directional — the subagent produces a result and reports back
- Independent parallel tracks exist where workers don't need to talk to each other
- Specialization benefits a sub-task — a focused agent loaded with exactly the right context outperforms a generalist juggling everything
- You want to route cost-sensitive work (research, exploration) without burning main-context tokens

Subagents report results back to the main agent only. They do not communicate with each other.

### 3. Agent Teams (high bar — only when peer coordination is genuinely required)
Agent teams give teammates a shared task list and a direct messaging channel — they can message each other without going through the lead. This is powerful but expensive: each teammate is a full Claude instance, token cost scales linearly, and the feature is experimental with known limitations.

Only justify an agent team when ALL of these are true:
- Teammates genuinely need to message each other directly — not just report results back to the lead
- Work spans truly independent file domains (two teammates cannot safely edit the same file)
- The task benefits from peer coordination: sharing findings, challenging theories, or building on each other's output in real time

If you're unsure whether peer coordination is needed, it probably isn't. Default to subagents.

---

## Execution Flow

### Step 1: Diagnose
State which level applies and explain why. Be specific.

- Choosing subagents over single session? Name what would pollute the main context, or what specialization is gained.
- Choosing agent team over subagents? Name the specific peer communication that justifies the cost.

Don't skip this. Naming the reason out loud prevents defaulting to the wrong tool.

### Step 2: Decompose
Break the task into independent tracks. Before writing a single spawn prompt, answer:

1. What are the distinct units of work?
2. Which files does each unit touch? Are they non-overlapping? (Two agents editing the same file = one overwrites the other. This is not recoverable.)
3. Are there dependencies? If Track B can't start until Track A finishes, they must run sequentially — don't force them into parallel.

Name each track. List its file ownership explicitly.

### Step 3: Seed Context
For each track, identify what the agent needs that it cannot derive from CLAUDE.md or the codebase.

Agents start fresh. They load CLAUDE.md, project context, and their spawn prompt — nothing else. Every decision already made, every constraint not in CLAUDE.md, every relevant pattern must go into the spawn prompt. This is the most common failure point: context starvation causes agents to guess wrong or re-explore what the lead already knows.

Ask: "If a capable engineer sat down with no prior context and only read this prompt, would they produce the right output?"

### Step 4: Generate Spawn Prompts
Produce a ready-to-use spawn prompt for each track. Do not be vague — these prompts get used directly.

**Subagent prompt structure:**

```
## Task
[Specific outcome. Which files to touch. What to produce.]

## Context
[Domain knowledge not in CLAUDE.md — decisions made, constraints, relevant patterns, gotchas]

## File Ownership
[Which files this agent owns. Explicitly: what to leave alone.]

## Deliverable
[Exact format and content to return to the main agent. Not "return your findings" — be specific.]

## Verification
[How the agent confirms its work is correct before returning]
```

**Teammate prompt structure (agent teams only) — adds to the above:**

```
## Your Name
[Explicit name — the lead and teammates will address you by this]

## Peer Coordination
[Which teammates to message, what information to share with them, and when]

## Findings Format
[Consistent structure for findings — the lead synthesizes all teammates; inconsistent formats create overhead]

## Plan Approval
[State if the lead will require plan approval before implementation begins]
```

---

## Anti-Patterns That Produce Bad Results

**Context starvation** — not telling the agent things it needs to know that aren't in CLAUDE.md. The agent invents assumptions or wastes time re-exploring what the lead already resolved. Always seed explicitly.

**File conflicts** — two agents editing the same file. One silently overwrites the other. Partition by file ownership before writing spawn prompts; if you can't partition cleanly, the task may not be parallelizable.

**Teams for sequential work** — using an agent team when Track B depends on Track A. Teammates sit idle or waste tokens on coordination while waiting. Chain subagents sequentially from the main conversation instead.

**Over-specifying implementation** — prescribing every micro-step rather than the outcome. This removes the agent's ability to exercise judgment and often produces worse results than letting it reason. Describe what to produce, not how to produce it step by step.

**Vague deliverable** — "return your findings." The agent doesn't know what format, length, or content is expected, and the main agent has to parse an inconsistent result. Specify exactly what comes back.

---

## StackWise Notes

**Subagents — use liberally:**
- Design coding agent fixes (each fix = one focused subagent)
- GSD research / planning / execution flows (GSD already uses subagents well; extend this pattern)
- Test verification, spec generation, codebase exploration
- Any task where the result is needed but the process would pollute main context

**Agent teams — rare, high bar:**
- Only for large feature implementations where backend model, SwiftUI views, and tests are in genuinely separate files AND teammates need to coordinate findings in real time
- Require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `.claude/settings.json` before creating a team
- VS Code + Windows 11: split-pane mode is not supported — agent teams run in in-process mode (Shift+Down cycles through teammates)
