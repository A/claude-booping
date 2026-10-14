---
id: "02"
title: "Agent, skill and step bodies inject rules only"
sp: 3
status: done
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M02: Agent, skill and step bodies inject rules only

Internal agent bodies, the `/playbook` skill body, the driving protocol and learn's target space carry no lessons: each renders its `## Rules` section and nothing in their place.

**Scope**: delete `src/templates/_partials/_agent_lessons.j2`, `src/templates/_partials/_skill_lessons.j2` and the unused `src/templates/_partials/_lesson_template.j2`, with their unit tests `booping-python/tests/templates/test_agent_lessons.py` and `test_skill_lessons.py`; drop each partial's call line from `src/templates/_partials/_developer_body.j2`, `src/templates/skills/playbook.md.j2`, `src/templates/agents/booping-researcher.md.j2`, and the "placed directly before the lessons partial" note in `src/templates/_partials/_targeted_rules.j2`'s header. `src/templates/_partials/_playbook_driving.j2`: the `## Lessons` bullet goes; the `## Rules` wording stands alone (rules bind the run; step-scoped rules reach a step through its own `--step` fetch; never copied into a bootstrap prompt). `playbooks/_partials/target_space.md`: delete the `**Lessons:**` block. `playbooks/develop/develop-loop/base.md` line "the worker gets its lesson context from its own extension file" → the worker gets its project shaping from the `agent:{id}` rules injected into its own body. Not in scope: `_lessons.j2`, `_plan_lesson_check.j2`, `_session_log_extraction.j2` and their callers — the legacy cross-check set, parked (`clarifications.md` C3).

Tests: the surviving `tests/templates/test_agent_rules.py` / `test_skill_rules.py` stay green; a rendered agent and skill body with a targeted rule and a `_lessons/` file present shows the rule and no `## Lessons` — asserted by extending one of those two files, not by a new one.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Delete the three partials and two test files; drop the call lines; trim `_targeted_rules.j2`'s header; one added test asserting a `_lessons/` file no longer reaches an agent body. | `src/templates/_partials/_agent_lessons.j2`, `src/templates/_partials/_skill_lessons.j2`, `src/templates/_partials/_lesson_template.j2`, `src/templates/_partials/_developer_body.j2`, `src/templates/skills/playbook.md.j2`, `src/templates/agents/booping-researcher.md.j2`, `src/templates/_partials/_targeted_rules.j2`, `booping-python/tests/templates/test_agent_lessons.py`, `booping-python/tests/templates/test_skill_lessons.py`, `booping-python/tests/templates/test_agent_rules.py` | 2 | done |
| 2.2 | Reword `_playbook_driving.j2`, `target_space.md` and develop-loop `base.md` as Scope states. | `src/templates/_partials/_playbook_driving.j2`, `playbooks/_partials/target_space.md`, `playbooks/develop/develop-loop/base.md` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `rg -n '_agent_lessons|_skill_lessons|_lesson_template' src playbooks booping-python` prints nothing.
- [x] `bin/booping render src/templates/agents/booping-researcher.md.j2` and `bin/booping render src/templates/skills/playbook.md.j2` render without error and contain no `## Lessons`.

### Task 2.2

- [x] `rg -n -i 'lesson' src/templates/_partials/_playbook_driving.j2 playbooks/_partials/target_space.md playbooks/develop/develop-loop/base.md` prints nothing.
- [x] `just snapshots` drift is limited to `playbooks/develop/_reports/output.md` and `playbooks/learn/_reports/output.md`, each hunk one of this milestone's rewordings.

Return: the list of changed files, nothing else.

## References

- `src/templates/_partials/_targeted_rules.j2` — the rules partial every caller keeps.
- `booping-python/tests/templates/test_agent_rules.py` — the test file to extend.

## Verify

`cd booping-python && uv run pytest tests/templates -q`
