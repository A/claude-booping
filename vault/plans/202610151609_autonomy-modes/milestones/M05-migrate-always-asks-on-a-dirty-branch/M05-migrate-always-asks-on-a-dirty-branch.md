---
id: "05"
title: "Migrate always asks about uncommitted work on the branch"
sp: 3
status: done
plan: "plans/202610151609_autonomy-modes/index.md"
---

# M05: Migrate always asks about uncommitted work on the branch

migrate's survey shows the current branch with the uncommitted work and waits for the answer in either mode, and the auto-migrate notice no longer licenses skipping that question.

**Scope**: `playbooks/migrate/survey/opus-5.md` `## Work in flight`: name the current branch alongside the counts and notable paths; replace "It is not the review gate and it never blocks — a user who declines still proceeds." with the survey text of `index.md` `## Output contract` → `### Migrate`. `booping-python/src/booping/migrations.py` `_AUTO` becomes the amended notice of the contract; update every case and test asserting the old text — `booping-python/e2e/cases/render-playbook/a-behind-vault-gates-the-playbook-render.txtar`, `a-behind-vault-gates-the-render-command.txtar`, `the-project-flag-pins-the-marker-to-that-root.txtar`, `booping-python/tests/migrations_test.py`. Then run `just snapshots` and report its drift; accepting it is the runner's, per the run's snapshot policy, never the worker's: the migrate report drifts in the survey section only.

Tests: the three existing txtar cases and the unit test, updated to the new notice; no new case — the survey text is a prompt, not code.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Survey text: branch named, the answer always awaited. | `playbooks/migrate/survey/opus-5.md` | 1 | done |
| 5.2 | Amended `_AUTO` notice and every assertion of the old text. | `booping-python/src/booping/migrations.py`, the three cases, `booping-python/tests/migrations_test.py` | 2 | done |

## Definition of Done

### Task 5.1

- [x] The survey names the branch, asks, waits, and still proceeds on a decline; nothing else in the body changes.
- [x] `just snapshots` drift is limited to `playbooks/migrate/_reports/output.md`, in `## Work in flight`.

### Task 5.2

- [x] `_AUTO` equals the contract text; `grep -rn "without asking the user" booping-python` finds nothing.

Return: the list of changed files, nothing else.

## References

- `playbooks/migrate/survey/opus-5.md` — the body edited.
- `booping-python/e2e/cases/render-playbook/a-behind-vault-gates-the-playbook-render.txtar` — the notice assertion.

## Verify

`just e2e -k behind-vault`
