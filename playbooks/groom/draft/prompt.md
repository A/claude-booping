---
name: draft
title: Draft
summary: "Owns the write-the-plan and write-summary craft rules, sprint planning + estimation flow, plan-template selection, the local-vault branch offer, and the move out of in-spec."
agent: null
review_gate: null
---
{% import "_partials/_sprint_planning.j2" as sprint_planning with context %}
{{ sprint_planning.render() }}

{% include "_partials/_plan_template.j2" %}

## Draft

Write the agreed design into a plan file at `{{ context.project.directory if context.project else "~/Claude/{project}" }}/plans/{YYYYMMDD}-{kebab-title}.md`.

1. **Pick a plan template** from [Plan Structure](#plan-structure) whose name + description matches the dominant surface of the work. Read it, and write the plan against its `# Plan Body`.
2. **Write the plan**: decompose into milestones, and milestones into tasks. Each milestone must be executable in a fresh session with only the plan as context — the design decisions, file paths, and DoD it needs live in the plan, not in this conversation.
3. **Write `summary`**: set the `summary:` frontmatter to a single line of plain plan intent — ≤ ~120 chars / ~20 words, no prose, no trailing period needed. It feeds search and the `sprints.md` snapshot.
4. **Estimate** per the Estimation flow above: per task, summed per milestone, summed per sprint. Re-decompose any task at or above the re-decomposition threshold. If the sprint total exceeds the split threshold, flag it and propose splitting into sibling plans (each sibling stub carries `split_from:` pointing at the primary plan).
5. **Verify** the finished draft against the selected template's `# Quality Checklist`, plus every gate the Plan Transitions table lists on the move out of `in-spec`.
{%- if context.project and context.project.is_local_vault %}
6. **Offer a branch** (local vault): the vault lives inside the repo, so the next `booping transition` (`in-spec → awaiting-plan-review`) commits the plan onto the current branch. Before that move, offer to create/switch to a dedicated branch so the plan never lands on the default branch unintentionally. Derive the default name from the plan's `type`:

   | Plan type | Branch prefix |
   |-----------|---------------|
{% for entry in config.git.branches %}   | {{ entry.when | join(", ") }} | `{{ entry.branch }}` |
{% endfor %}
   Default name = matched prefix + the kebab plan slug (e.g. `feat/local-vault-directories`) — must match what `/develop` would pick so it reuses the branch. Ask the user; they may decline and keep the current branch. On accept: `git switch -c <name>` for a new branch, or `git switch <name>` if it already exists.

7. **Move the plan** out of `in-spec` per the Plan Transitions table once every gate holds, passing any sibling stubs with `--also`.
{%- else %}
6. **Move the plan** out of `in-spec` per the Plan Transitions table once every gate holds, passing any sibling stubs with `--also`.
{%- endif %}

## Output

Plan file path, milestone list with per-milestone SP, sprint SP total, and the status the plan now sits in.
