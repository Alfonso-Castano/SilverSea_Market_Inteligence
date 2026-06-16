---
name: quality-review
description: "Run the two-pass quality review on the latest Silversea market intelligence report. Uses the orchestrator skill to design the subagent strategy, prompt-engineer to craft the review brief, then spawns the review agent with web search to fact-check and score the report."
---

# Quality Review — Silversea Market Intelligence

## Step 1: Read current state
Before anything else, read:
- `output/index.html` — the report to review
- `quality/rubric.md` — the scoring rubric and fact-check definitions
- The most recent file in `quality/reviews/` — for comparison with prior scores

## Step 2: Apply the Orchestrator skill
Read `.claude/orchestrator/SKILL.md` and work through the decision ladder for this task.

The task is: fact-check and quality-score the latest report using web search.

This should resolve to: **subagent** (web search results would flood main context; the research is self-contained and one-directional; specialization is gained by giving the agent exactly the rubric and nothing else).

## Step 3: Apply the Prompt Engineer skill
Read `.claude/prompt-engineer/SKILL.md` and craft the subagent brief.

The brief must include:
- Full report text (extracted from output/index.html — strip HTML tags, keep the content)
- The complete rubric from quality/rubric.md (both passes, all definitions)
- File ownership: agent writes nothing to disk — it returns its review as text
- Deliverable format: markdown with three sections — FACT-CHECK TABLE, QUALITY SCORES TABLE, VERDICT + TOP 3 IMPROVEMENTS
- Verification: agent must search the web for each specific named claim before tagging it

This is a **medium** task by prompt-engineer calibration: 2-3 context sentences, specific deliverable, explicit constraints on what not to do (no guessing without searching).

## Step 4: Spawn the review agent
Spawn an Agent with the crafted prompt. The agent needs WebSearch capability — confirm this is in its available tools.

## Step 5: Save the review
Once the agent returns its review, save it to:
`quality/reviews/YYYY-MM-DD.md` (use today's date)

Then summarise the verdict and top 3 improvements for Alfonso in 4-5 lines.
