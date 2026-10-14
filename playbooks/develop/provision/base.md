{%- import "_partials/_git_guide.j2" as git_guide with context -%}
# Provision the sprint

Set the sprint up in one step: a confirmed branch to commit on, and the milestone groups every
briefing in `develop-loop` will cover.

You get the plan — its type, title and slug — the repo's current branch, and the drift findings
intake raised. The milestones come off disk, one directory each.

## Branch

If branch wasn't explicitly defined by user, decide which branch the sprint goes on per the table above — the plan's `type` picks the prefix — and propose a kebab-case name. Ask through `AskUserQuestion`. A name the user rewrites is used verbatim, and nothing touches git until the answer arrives. Switch from the current branch to the target one after user confirmation.

In multi-repo projects, reuse the same branch name across repos unless the user asks otherwise. When a branch for this sprint already exists, switch onto it and reuse it instead of creating one.

{{ git_guide.render() }}

## Milestone groups

Enumerate the milestones in execution order — never from `index.md`'s table, which is derived:

```
booping query --glob {plan-dir}/{{ config.core.plans.milestones.glob }} --columns {{ config.core.plans.milestones.table_columns | join(',') }} --sort id
```

{% if config.core.sprint.max_sp -%}
Pack milestones into agent briefings greedily, in that order: a group takes the next milestone
while the group's summed `sp` stays at or under **{{ config.core.sprint.max_sp }} SP**, and closes otherwise.
A group is a contiguous run of milestones in `id` order. A single milestone is always a valid group
and is never split, even when its `sp` alone exceeds the cap.
{% else -%}
One milestone per briefing: each milestone is its own group.
{% endif %}
The groups are yours to settle — reported in the return, never put to the user for confirmation.
Settle them as a table you keep for the return, milestones named by their directory so
`develop-loop` briefs paths:

| Group | Milestone dirs | SP | Grouped because |
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
- groups: {n} briefings over {m} milestones (cap {c} SP) — G1 `M01-{kebab}`+`M02-{kebab}`, G2 `M03-{kebab}`
- drift: {what intake raised and whether anything is outstanding}

```

When a branch for this sprint already existed, the branch note says so instead:

```markdown
- branch: `{name}` already existed and was reused — switched onto it, 2 commits ahead of `{base}`
```
