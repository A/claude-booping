---
id: "06"
title: "The vault scaffold drops _lessons"
sp: 2
status: pending
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M06: The vault scaffold drops _lessons

A vault created by `setup` (`booping scaffold core.setup_playbook.scaffold`) has no `_lessons/` directory.

**Scope**: `src/config.yaml` — delete `core.setup_playbook.scaffold._lessons`. `playbooks/setup/setup-project/opus-5.md` — the vault-tree list drops `_lessons/`. The scaffold e2e cases (`booping-python/e2e/cases/scaffold/core-vault-tree-*.txtar`) drop `_lessons/` from their expected trees. `documentation/project_config.md`'s scaffold sample and its prose list move in M08, not here.

Tests: the scaffold txtar cases are the integration check; expected trees edited by hand.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Drop the scaffold key and the setup-project mention. | `src/config.yaml`, `playbooks/setup/setup-project/opus-5.md` | 1 | pending |
| 6.2 | Scaffold cases without `_lessons/`. | `booping-python/e2e/cases/scaffold/core-vault-tree-*.txtar` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] `rg -n '_lessons' src/config.yaml playbooks/setup` prints nothing.
- [ ] `just snapshots` drift is limited to `playbooks/setup/_reports/output.md`, the one-word list change.

### Task 6.2

- [ ] `rg -l '_lessons' booping-python/e2e/cases/scaffold` prints nothing.

Return: the list of changed files, nothing else.

## References

- `src/config.yaml` `core.setup_playbook.scaffold` — the tree being trimmed.

## Verify

`just e2e -k scaffold`
