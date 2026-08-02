---
reviewed_at: 20260802 09:00
---

# develop — Brief

## Goal

Convert booping's core `/develop` skill into a playbook: the same execution procedure — intake a groomed plan and validate its entry status and commit-drift validity, propose milestone groupings for agent briefings and confirm them, create the sprint branch after confirming its name with the user, then run the sequential milestone-group loop where every task is delegated to a worker agent (the orchestrator never edits application code), flipping DoD checkboxes and milestone statuses and committing per milestone, and finally run Final Verification plus the project's own lint/typecheck/test commands and take the exit transition — expressed as discrete playbook steps with review gates instead of one monolithic skill body. The port stays **close to the original prose**: step bodies carry the skill's existing wording, not rewritten expanded prose, and every doc the skill leans on (plan templates, review templates, plan-frontmatter shape, git guide, task-type guidance, available-agents and transitions surfaces) is wired into the playbook rather than dropped.

## Success result

A run ends with a plan whose milestones are all `done`, DoD checkboxes all `[x]`, work committed on the sprint branch in the attached repo, Final Verification and project quality commands green, and the plan moved through its exit transition (`awaiting-retro`, or the failure branch after two failed fix attempts on the same issue). The playbook's step prompts are no longer than the skill prose they replace, and every reference doc the original skill lazy-loads is reachable from the playbook. The canonical `/develop` skill is untouched and remains the default entry point; the playbook ships alongside it and runs in parallel until beta-testing concludes.

## Artifact home

The groomed plan's own directory inside the resolved project vault — `{vault}/plans/{slug}/`, where `{vault}` is detected deterministically at run time by the playbook driver, never a hardcoded path. That directory doubles as the run workdir, so develop picks up exactly where groom left off.

## Wishes

- Stay close to the original `/develop` prose. Do not convert short, simple prompts into large prose — it adds no value and eats tokens.
- Do not repeat the groom port's omission: connect the proper docs the skill references (plan templates, review templates, plan-frontmatter doc, git guide, task classification, agent/transition surfaces) instead of leaving them unlinked.
- Leave the core `/develop` skill unchanged; the playbook ships alongside it and stays parallel until beta-testing is finished.
- Confirm the sprint git branch with the user before creating it — a branch-name confirmation gate, same spirit as the milestone-grouping confirmation.
- Give the playbook its own state machine — a subset of the shared plan lifecycle joined to groom's at the edges: groom ends at `ready-for-dev`, develop picks up from there and from `awaiting-plan-review`.
