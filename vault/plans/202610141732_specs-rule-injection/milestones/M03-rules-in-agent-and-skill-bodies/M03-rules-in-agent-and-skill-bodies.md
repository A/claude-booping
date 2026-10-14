---
id: "03"
title: "Rules section in agent and skill bodies"
sp: 4
status: done
plan: "vault/plans/202610141732_specs-rule-injection/index.md"
---

# M03: Rules section in agent and skill bodies

The internal agent bodies (`booping-developer`, `booping-researcher`) and the `/playbook` skill body render a `## Rules` section, before their `## Lessons` section, for every targeted rule naming `agent:{id}` or `skill:{name}`.

**Scope**: `booping render src/templates/…` on the agent and skill templates. Files: new partial `src/templates/_partials/_targeted_rules.j2`; call sites `src/templates/_partials/_developer_body.j2`, `src/templates/agents/booping-researcher.md.j2`, `src/templates/skills/playbook.md.j2`; tests under `booping-python/tests/templates/`. Reuses M02's `src/templates/_partials/_rules.j2` for the section itself.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `_targeted_rules.j2` (args `kind` = `agent`\|`skill`, `id`): selects `context.targeted_rules` whose `parsed_targets` name that agent or skill and renders `_rules.j2` with `surface` = `kind`; called directly before the lessons partial at each of the three call sites | `src/templates/_partials/_targeted_rules.j2`, `src/templates/_partials/_developer_body.j2`, `src/templates/agents/booping-researcher.md.j2`, `src/templates/skills/playbook.md.j2` | 2 | done |
| 3.2 | Template tests for agent and skill surfaces | `booping-python/tests/templates/test_agent_rules.py`, `booping-python/tests/templates/test_skill_rules.py` | 2 | done |

Section content is M02's, with `{agent|skill}` as the surface noun and no `; conflict → stop and flag` ([clarifications.md](../../clarifications.md) C1). Agent and skill surfaces print no notices (C6).

## Definition of Done

### Task 3.1

- [x] A rule targeting `agent:booping-researcher` renders in the researcher body only; `agent:booping-developer` in the developer body only; `skill:playbook` in the `/playbook` skill body only.
- [x] Rules section sits directly before the lessons section; no matching rule → nothing rendered, no stray blank lines.
- [x] The three call sites hold one line each; selection logic lives once, in `_targeted_rules.j2`.

### Task 3.2

- [x] Tests render the partial against a context carrying real `TargetedRule` objects, mirroring `test_agent_lessons.py`.
- [x] Parametrized over: matching agent, other agent, matching skill, other skill, no rules; exact section text asserted as a literal.

## References

- `src/templates/_partials/_agent_lessons.j2`, `src/templates/_partials/_skill_lessons.j2` — selection shape to mirror.
- `booping-python/tests/templates/test_agent_lessons.py`, `booping-python/tests/templates/test_skill_lessons.py` — test shape.

## Verify

`uv run --project booping-python pytest booping-python/tests/templates -q` — all pass.

Return: only the list of changed files, then the last line of the Verify output.
