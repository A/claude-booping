# Write the plan

Your task is to build a plan for the user request, from the framing and the research findings this
conversation already carries — the blast-radius map and the external ground the work rests on.

- **Draft design with the user**: architecture, pattern choices, data / API / config surface
  changes, open trade-offs. Iterate until aligned before writing.
- **Write the plan**: pick a plan template from [Available plan templates](#available-plan-templates)
  whose name + description matches the work, then produce the plan against its `# Plan Body` — see
  [Plan Structure](#plan-structure).
- **Write `summary`**: set the `summary:` frontmatter to a single line of plain plan intent — ≤ ~120
  chars / ~20 words, no prose, no trailing period needed. It feeds search and the `sprints.md`
  snapshot.

## Hard rules

- The orchestrator never edits files outside `{project}/plans/`.
- Each milestone executable in a fresh session with only the plan as context.
- Sprint total past **{{ config.core.sprint.default_threshold_sp }} SP** — offer the user a split at a dependency seam (the first slice
  shippable on its own, each later one useless without it), keep only the first slice that fits the
  threshold in this plan, and park the rest as sibling stubs to be groomed in their own runs. They
  may decline and keep one plan.
- User approval is **explicit** — "looks good" is enough; silence is not.

{% include "_partials/plan_structure.md" %}

{% include "_partials/plan_templates.md" %}

{% include "_partials/sprint_planning.md" %}