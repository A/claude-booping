# groom — Brief

## Goal

Convert booping's core `/groom` skill into a playbook: the same grooming procedure — deep-research a feature, bug, or refactor across any domain and task type, challenge scope, map the blast radius in the codebase, research the web when the work is novel, verify every external reference, draft the design with the user, then write a specified, estimated plan with a Definition of Done that an agentic tool can execute from the plan file alone — expressed as discrete playbook steps with review gates instead of one monolithic skill body. The playbook takes the name `groom`, which requires retiring the stale core `playbooks/groom/` that currently occupies it; the new playbook is not to be framed by that stale one.

## Success result

A run ends with a plan file in the project vault that the user has explicitly approved and that has moved through the plan lifecycle to `awaiting-plan-review` — scope challenged, codebase and (where warranted) web research done, external references verified, design agreed with the user, milestones and story points set, `summary:` frontmatter written, and each milestone executable in a fresh session with only the plan as context. The canonical `/groom` skill is untouched and remains the default entry point: the playbook runs in parallel with it through beta-testing, and only after beta-testing concludes is any decision made about which one is canonical.

## Artifact home

`~/Claude/{project}/plans/`

## Wishes

- Retire the stale core `playbooks/groom/` so the new playbook can take the name `groom`.
- Do not frame the new playbook by the stale `playbooks/groom/` — design the decomposition fresh from the `/groom` skill.
- Leave the core `/groom` skill unchanged; the playbook ships alongside it and stays parallel until beta-testing is finished.
- Render `sprints.md` from the playbook, not from booping: localize the rendering as a playbook-local script under the groom playbook's `_scripts/` dir, fired through the playbook hook vocabulary (`script <name>`), instead of relying on booping's built-in `render-sprints` hook. This serves the long-term direction — playbook-specific behavior migrates into playbooks, booping core stays a pure framework for playbooks, and `render-sprints` is eventually removed from booping.
- Give the playbook its own state machine instead of reusing the single shared plan lifecycle that `/groom` and `/develop` both sit on today. Groom's machine and develop's machine should be two different subsets of that one lifecycle, joined at their edges: groom ends by putting the plan into `ready-for-dev`, and develop picks up from there and from `awaiting-plan-review`.
