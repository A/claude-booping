---
id: "03"
title: "The driving protocol renders gates and questions per mode"
sp: 3
status: pending
plan: "plans/202610151609_autonomy-modes/index.md"
---

# M03: The driving protocol renders gates and questions per mode

The `/playbook` skill's driving protocol renders its gate rule and its questions rule from `core.autonomy`: supervised byte-identical to today, autonomous auto-confirming gates and settling questions, every one logged through `booping defaults add`.

**Scope**: `src/templates/_partials/_playbook_driving.j2` only. Under `{% if config.core.autonomy == 'autonomous' %}` the batch step 5 and the `## Questions:` paragraph render as the autonomous text of `index.md` `## Output contract` → `### Driving protocol, autonomous`; the `{% else %}` branch is today's text unchanged. The partial needs no validation of its own: M01 stops any render whose final value is neither mode, `--set` included. No playbook's `review_gate`, `playbook.yaml` or step body changes.

Tests: integration tier, two txtar cases under `booping-python/e2e/cases/render/` rendering `src/templates/skills/playbook.md.j2` — default config shows the supervised step 5 (`stop, and wait for the user's chat reply`); `--set core.autonomy=autonomous` shows the autonomous step 5 and the `booping defaults add` line, and not the supervised one. Assert the relevant lines with the corpus's wildcard matching, not the whole render.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | The conditional and the autonomous text. | `src/templates/_partials/_playbook_driving.j2` | 2 | pending |
| 3.2 | The two txtar cases. | `booping-python/e2e/cases/render/driving-protocol-*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] With `core.autonomy` unset, `bin/booping render src/templates/skills/playbook.md.j2` is byte-identical to its output before this milestone except the M01 project-context line.
- [ ] With `--set core.autonomy=autonomous`, the rendered step 5 and questions paragraph equal the contract text.
- [ ] No other line of the partial changes.

### Task 3.2

- [ ] Each case asserts the presence of its branch's text and the absence of the other branch's distinguishing line.

Return: the list of changed files, nothing else.

## References

- `playbooks/migrate/survey/opus-5.md` — the `config.core.auto_migrate` branch shape in a template body.
- `booping-python/e2e/cases/render/a-set-override-wins-over-the-core-config-value.txtar` — `--set` in a render case.

## Verify

`just e2e -k driving-protocol`
