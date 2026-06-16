---
name: prompt-engineer
description: Generate self-contained, agent-ready prompts for delegating work to fresh Claude sessions or sub-agents. Use whenever you need to hand off a task (fix, feature, debug, refactor) to another agent that has no prior context. Also use when crafting sub-agent prompts within workflows, or when any skill/workflow needs a high-quality delegation prompt. Trigger on: "generate a prompt for", "write a prompt to", "hand this off to another agent", "create a fix prompt", or any context where work must be delegated to a fresh agent with zero shared context.
---

# Prompt Engineer

Generate prompts that let a fresh agent act without back-and-forth. Every prompt you produce must be self-contained — the receiving agent has zero context from this conversation.

## Core Principle

A good delegation prompt answers five questions for the receiving agent:
1. **What** — the specific outcome expected
2. **Where** — exact file paths, line numbers, or components involved
3. **Why** — enough context to make judgment calls (not just follow instructions)
4. **Constraints** — what must NOT change, what to avoid, boundaries
5. **Verification** — how the agent confirms it worked

If any of these are missing, the receiving agent will either ask questions (wasting time) or guess wrong (creating bugs).

## Prompt Structure

Use this structure for all delegation prompts. Adapt section depth to task complexity — a one-line label fix needs less than a navigation flow rewrite.

```
## Context
[1-3 sentences: what the project is, what area of code this touches, why this matters]

## The Problem
[What's wrong or what's needed. Be specific and observable — "the category label is missing below supplement icons in StackView" not "labels are broken"]

## Files Involved
[Exact paths. If you know line numbers, include them. If uncertain, say which file to search in and what to search for]

## What to Do
[Step-by-step if multi-step, or a clear single instruction. Include the expected end state]

## Constraints
[What NOT to change. Adjacent features to leave alone. Patterns to follow. Design system tokens to use. Architecture to respect]

## Verification
[How to confirm the fix works — build command, what to check in simulator, expected behavior]

## Attachments
[Note any screenshots, error logs, or reference files being provided alongside this prompt]
```

## Calibration by Task Size

### Trivial Fix (missing label, wrong color, typo)
- Context: 1 sentence
- Problem: 1 sentence with exact location
- Files: 1-2 paths
- What to Do: single clear instruction
- Constraints: 1 line ("don't change layout")
- Verification: "build and confirm X appears"
- Total: ~8-12 lines

### Medium Fix (add tap navigation, wire up data binding, fix a flow)
- Context: 2-3 sentences covering the feature area
- Problem: describe current vs expected behavior
- Files: 2-5 paths with relationships explained
- What to Do: numbered steps
- Constraints: adjacent features, architectural patterns
- Verification: specific user flow to test
- Total: ~20-40 lines

### Large Task (new feature, significant refactor)
- Context: full paragraph on the system and motivation
- Problem: detailed gap analysis
- Files: file tree of relevant area + key patterns to follow
- What to Do: phased approach with intermediate checkpoints
- Constraints: comprehensive (design system, architecture, existing tests)
- Verification: multiple scenarios including edge cases
- Total: ~50-80 lines

## iOS/SwiftUI-Specific Anchoring

When generating prompts for iOS work in this project, always include:

- **Design system reference**: "Use tokens from `StackWise/DesignSystem.swift` — no hardcoded colors or magic numbers"
- **File placement convention**: Components → `Views/Components/`, Screens → `Views/[TabName]/`, ViewModels → `ViewModels/`
- **SwiftUI patterns**: Reference existing similar views as examples ("follow the same pattern as `StackView.swift`")
- **Build verification**: "Build in Xcode (Cmd+B) to confirm no compiler errors. Run in simulator to verify visually."

## Sub-Agent Prompts

When crafting prompts for sub-agents spawned within a workflow (not fresh sessions):

- Sub-agents inherit some context from parent but not conversation history
- Be explicit about what the sub-agent should return (format, length, structure)
- Include the specific question or task — don't rely on ambient context
- Specify whether the sub-agent should write code or just research/analyze

## Anti-Patterns

Avoid these — they produce prompts that fail:

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| "Fix the bug" | No specifics — agent has to explore blindly | Name the exact symptom and location |
| Assuming shared context | Fresh agent knows nothing about prior work | State everything explicitly |
| Vague verification | "Make sure it works" — how? | Specific observable outcome |
| Over-specifying implementation | Leaves no room for judgment on approach | Describe the outcome, not every keystep |
| Missing constraints | Agent "fixes" one thing and breaks another | Name what must not change |
| No file paths | Agent wastes time finding the right files | Anchor with exact paths |

## When Invoked by Other Skills

When called from `/stackwise-design` Stage 6 or any other workflow:

1. Receive the issue description from the calling skill
2. Ask one clarifying question if the issue is ambiguous (otherwise proceed)
3. Determine task size (trivial/medium/large)
4. Generate the prompt using the structure above, calibrated to size
5. Output as a single copy-pasteable block
6. Note if a screenshot should be attached alongside the prompt
