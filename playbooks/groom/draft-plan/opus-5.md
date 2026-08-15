# Write the plan

Your task is to build a plan for the user request, from the framing and the research findings this
conversation already carries — the blast-radius map and the external ground the work rests on.

- **Draft design with the user**: architecture, pattern choices, data / API / config surface
  changes, open trade-offs. Iterate until aligned before writing.
{%- if config.core.tracker.driver == 'linear' %}
  There is no conversation to iterate in: a design call this step cannot settle from the framing
  and the research goes to `{plan-dir}/clarifications.md` — with the candidate answers as
  `**Options:**` — and parks the run, per the preamble's `Tracker driver` rules. A call settled that
  way is written into the plan on the resumed invocation, never guessed here.
{%- endif %}
- **Write the plan**: pick a plan template from [Available plan templates](#available-plan-templates) whose name + description matches the work, then produce the plan against its `# Plan Body` — `index.md` from the template's top-level sections, plus one file per milestone.
- **Write `summary`**: set the `summary:` frontmatter to a single line of plain plan intent — ≤ ~120
  chars / ~20 words, no prose, no trailing period needed. It feeds search and the `sprints.md`
  snapshot.

## Hard rules

- The orchestrator never edits files outside `{project}/plans/`.
- Each milestone file executable in a fresh session with only it and `index.md` as context.
- Sprint total past **{{ config.core.sprint.default_threshold_sp }} SP** — offer the user a split at a dependency seam (the first slice
  shippable on its own, each later one useless without it), keep only the first slice that fits the
  threshold in this plan, and park the rest as sibling stubs to be groomed in their own runs. They
  may decline and keep one plan.
- User approval is **explicit** — "looks good" is enough; silence is not.

{% include "_partials/plan_templates.md" %}

## Write the milestone files

Yours to write, here, one milestone at a time — no sub-step, no worker agent, no batched pass. `{plan-dir}` is the preamble's `Plan dir:` line. In execution order, per milestone:

1. Seed the milestone's directory and the file inside it:

   ```
   booping scaffold core.groom_playbook.milestone_scaffold {plan-dir}/milestones --set id={nn} --set slug={kebab} --set title="{title}" --set sp={sp} --set plan={plan-dir}/index.md
   ```

   `{nn}` is the milestone's position in execution order, zero-padded to two digits; `{kebab}` is its title kebab-cased — the two name the directory `M{nn}-{kebab}` and the file `M{nn}-{kebab}.md` inside it, identically. The seed owns everything it writes; never retype it into the body.

2. Write that milestone's body into the seeded file with a normal file edit, against the chosen template's milestone-file section. Then move to the next milestone.

`index.md`'s `## Milestones` table is generated from the files on disk, never hand-kept — paste the output of:

```
booping query --glob {plan-dir}/{{ config.core.plans.milestones.glob }} --columns {{ config.core.plans.milestones.table_columns | join(',') }}
```

A milestone that changes after that is edited in its own file, and the query re-run.

{% include "_partials/milestone_contract.md" %}

{% include "_partials/sprint_planning.md" %}