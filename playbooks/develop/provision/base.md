{%- import "_partials/_git_guide.j2" as git_guide with context -%}
# Provision the sprint

Set the sprint up in one step: a confirmed branch to commit on, and the milestone groups every
briefing in `develop-loop` will cover.

You get the plan — its type, title and slug — the repo's current branch, and the drift findings
intake raised. The milestones come off disk, one file each.

## Branch

If branch wasn't explicitly defined by user, decide which branch the sprint goes on per the table above — the plan's `type` picks the prefix — and propose a kebab-case name. Ask through `AskUserQuestion`. A name the user rewrites is used verbatim, and nothing touches git until the answer arrives. Switch from the current branch to the target one after user confirmation.

In multi-repo projects, reuse the same branch name across repos unless the user asks otherwise. When a branch for this sprint already exists, switch onto it and reuse it instead of creating one.

{{ git_guide.render() }}

## Milestone groups

Enumerate the milestones in execution order — never from `index.md`'s table, which is derived:

```
booping query --glob {plan-dir}/{{ config.core.plans.milestones.glob }} --columns {{ config.core.plans.milestones.table_columns | join(',') }} --sort id
```

{% if config.core.sprint.max_milestones_per_agent -%}
Group consecutive milestones into agent briefings: each briefing covers **up to {{ config.core.sprint.max_milestones_per_agent }} milestone(s)**.
Group only when the milestones share enough context that one agent handling them in sequence is
cheaper than spinning a fresh agent per milestone. Otherwise keep them one-per-briefing.
{%- else -%}
Group consecutive milestones into agent briefings only when they share enough context that one
agent handling them in sequence is cheaper than spinning a fresh agent per milestone. Otherwise
keep them one-per-briefing.
{%- endif %}

The groups are yours to settle — reported in the return, never put to the user for confirmation.
Settle them as a table you keep for the return, milestones named by file so `develop-loop` briefs
paths:

| Group | Milestone files | SP | Grouped because |
| --- | --- | --- | --- |

Carry intake's outstanding drift alongside them, so `develop-loop` briefs against it.

## Closing the step

With the branch created and the groups settled, advance the run per the `## State` section. Unresolved non-trivial drift halts back to grooming instead of advancing.

## Return format

```markdown
## Changed:

- [UPDATED] plans/{slug}/index.md — {status before} → {status after}

## Notes:

- branch: `{name}` created off the current branch `{base}`, name confirmed by the user
- transition: {the transition report verbatim}
- groups: {n} briefings over {m} milestones (ceiling {c}) — G1 `01-{kebab}`+`02-{kebab}`, G2 `03-{kebab}`
- drift: {what intake raised and whether anything is outstanding}

```

When a branch for this sprint already existed, the branch note says so instead:

```markdown
- branch: `{name}` already existed and was reused — switched onto it, 2 commits ahead of `{base}`
```
