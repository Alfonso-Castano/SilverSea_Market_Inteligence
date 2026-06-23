# Visual Design Discussion — Handoff Prompt

Copy-paste this into a fresh chat to start the discussion session.

---

## Prompt

You are starting a **discussion session** (not an execution session) for Silversea Media's AI
market intelligence system at `C:\Users\alfon\SilverSea\SilverSea_Market_Inteligence`.

### Context files — read these first
1. `CLAUDE.md` — project instructions + auto-imports STATE.md, CONTEXT.md, ROADMAP.md, PLAN.md
2. `templates/report.html`, `templates/base.html`, `static/style.css` — the current report page
3. `templates/internals.html` — the current internals page (lower priority for this discussion)

### Where things stand
Phase 3 (Web Dashboard) is complete and verified end-to-end. The pipeline produces structured
JSON (`data/latest_report.json`), and a Flask app (`app.py`) serves it through two Jinja2
templates: a CEO/BD-facing report page (`/`) and a developer-facing internals page (`/internals`).
Current stack: Flask + Jinja2, Tailwind CSS via CDN (no build step), Chart.js via CDN, vanilla JS
for interactivity (tab switching, feedback form fetch). No npm, no React, no SPA framework.

The current report page works and looks clean, but Alfonso wants it to be **visually impressive**
— this is the surface the BD/sales team and possibly the CEO will look at daily, and right now it
reads as competent-but-plain. The internals page is lower priority — it's a developer tool, not
client/exec-facing.

### What Alfonso wants from this discussion
1. **Make the report page (`/`) visually impressive**: animations, color gradients, "cool"
   features — something that feels designed, not templated.
2. **Constraint: don't over-engineer.** This is an internal tool, not a public product. Avoid
   adding complexity (build tooling, frameworks, dependencies) that isn't earning its keep.
3. **Constraint: minimize architecture/infrastructure changes.** The Flask + Jinja2 + server-side
   rendering model should ideally stay — changing it should be a deliberate, justified decision,
   not a side effect of chasing a visual effect.

### What this discussion needs to produce
A plan (not code) that a future **execution session** will implement. Before proposing anything,
scope the problem:

1. **What's possible with zero architecture change** — i.e., purely within Tailwind CDN + vanilla
   JS + Chart.js + CSS, on top of the current Jinja2 templates. CSS animations, gradients,
   transitions, scroll-triggered reveals, micro-interactions on cards/badges, etc. all likely fit
   here.
2. **What would require a small, bounded addition** — e.g. a lightweight animation library via
   CDN (no build step), without abandoning Flask/Jinja2.
3. **What would require a real architecture change** — e.g. moving to a JS framework, adding a
   build step, going client-rendered. Identify what becomes *possible* at each tier so Alfonso can
   judge whether it's worth the tradeoff — don't just say "more is possible," name the specific
   capability gained (e.g. "true SPA transitions between report dates" or "component reuse across
   pages").

### Tooling to evaluate
Alfonso has two specific tools he wants evaluated, plus an open invitation for you to find more.
Specifically evaluate:
- The `frontend-design` Claude Code plugin:
  `https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design`
- The `ui-ux-pro-max-skill`:
  `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`
  (Note: a prior planning session looked at a similarly-named repo and dismissed it as "a
  recommendation engine, not a component library" — re-verify that assessment against this
  specific repo yourself rather than trusting that note; it may be a different project or the
  earlier read may have been shallow.)
- For both: actually read what they do (README, skill/plugin definition files, via WebFetch)
  before judging relevance — don't assume from the name. Determine whether each is a
  design-system/component-generation aid, a code-review tool, a static reference doc, or
  something else, and whether it fits a Tailwind-CDN + Jinja2, no-build-step stack.
- Beyond these two: **take the lead on finding more options.** Alfonso explicitly wants you
  driving this research — you know your own tool/skill/plugin ecosystem and capabilities better
  than he does. Don't wait for him to paste more links; go look for other Claude Code
  skills/plugins/agents (or lightweight CDN-based libraries) that would meaningfully improve
  front-end output quality, and bring back concrete candidates with a recommendation, not just
  an open-ended list.

### How to run this conversation
Alfonso wants you to lead. His framing: "Claude knows best what it can and cannot do" — he wants
you proposing the scope, the tool choices, and the plan, while he steers and gives taste/judgment
calls rather than originating the technical options himself. Concretely:
- Don't just list tradeoffs and ask him to pick — form a recommendation and lead with it, then
  let him redirect.
- Still ask the clarifying questions below (his taste/constraints genuinely can't be inferred),
  but don't make the whole conversation a question queue — drive toward a concrete plan.
- By the end of this session, two things must exist: (1) the finalized plan, and (2) a
  ready-to-paste handoff prompt for the next (execution) session, written the same way this
  handoff was written for you. Do not end the session without producing that handoff prompt.

### Questions to ask Alfonso before finalizing a plan
Don't assume — ask directly, early in the conversation:
1. Do you have specific reference sites/dashboards whose look you want to emulate? (Helps anchor
   "impressive" to something concrete instead of guessing.)
2. Is the internals page (`/internals`) in scope for this visual pass at all, or strictly the
   report page (`/`) for now?
3. Any hard constraint on page load time or on keeping this servable with zero build step (i.e.,
   is "no npm/webpack" non-negotiable, or open for discussion if the payoff is big enough)?
4. Should country-tab switching (SG active, MY/VN/ID greyed out) factor into the animation/visual
   design, or is that future-phase concern?

### Output of this session
1. A written plan (in the style of the existing `.claude/execution/phase3-dashboard.md`) scoping
   exactly what will be implemented, which tier of architecture change it requires, and which
   tool(s)/skill(s)/plugin(s) will be used and why.
2. A handoff prompt for the next execution session (fresh chat), self-contained the way this one
   is, so Alfonso can copy-paste it directly to start implementation.
Do not write implementation code in this session — this is a scoping and decision-making
conversation that ends in a plan + handoff prompt, not in edited files.
