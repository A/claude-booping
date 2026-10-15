---
id: "03"
title: "Learn stops reading and staging _lessons"
sp: 3
status: done
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M03: Learn stops reading and staging _lessons

`learn` neither reads nor stages `_lessons/`: its dedup sweep looks only at the three specs tiers and `CLAUDE.md`, its review table has no `_lessons/{file}` target, and its closing hook stages `specs` alone.

**Scope**: `playbooks/learn/dedup-sweep/base.md` and `prompt.md` — drop `{vault}/_lessons/` and `{home_dir}/_lessons/` from the lookup set and the `update existing at _lessons/{file}` verdict (plan 202610142150 C6's lesson-duplicate branch retires: no lesson is left to convert). `docs/learn_review_table.md` — drop the `_lessons/{file}` Target form. `playbooks/learn/playbook.yaml` — `close-working-set --stage _lessons specs` → `--stage specs`. `playbooks/learn/_partials/_learn_targets.j2` — "rules and lessons already targeting them" → "rules already targeting them". Any learn eval fixture or assert (`playbooks/learn/*/tests.yaml`, `_fixtures/`) naming a lesson file as a destination or lookup source moves to rules; smoke tier only, `EVAL_PR=0`; `regress` left to the owner. "Lesson" as plain English for what a retro teaches stays.

Tests: the learn render (snapshot) carries the change; `just smoke learn/dedup-sweep` and `just smoke learn/extract-candidates` pass where their fixtures changed.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Dedup sweep and review-table doc without lessons; `_learn_targets.j2` wording. | `playbooks/learn/dedup-sweep/base.md`, `playbooks/learn/dedup-sweep/prompt.md`, `docs/learn_review_table.md`, `playbooks/learn/_partials/_learn_targets.j2` | 2 | done |
| 3.2 | Closing hook stages `specs` only; learn eval fixtures/asserts that name `_lessons` move to rules, smoke tier run. | `playbooks/learn/playbook.yaml`, `playbooks/learn/*/tests.yaml`, `playbooks/learn/*/_fixtures/*` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `rg -n '_lessons' playbooks/learn docs/learn_review_table.md` prints nothing.
- [x] The sweep's verdict vocabulary matches the review table's Type column in `docs/learn_review_table.md` (`rule` | `claude-md` | `covered`).

### Task 3.2

- [x] `bin/booping render-playbook learn` shows the closing edge staging `specs` only.
- [x] Every smoke suite whose files changed passes.
- [x] `just snapshots` drift is limited to `playbooks/learn/_reports/output.md`, each hunk one of this milestone's changes.

Return: the list of changed files, nothing else.

## References

- `vault/plans/202610142150_lessons-become-rules/milestones/M03-learn-dedup-and-review-table/M03-learn-dedup-and-review-table.md` — the milestone that put rules into the sweep; this one takes lessons out.
- `vault/specs/runbook/0002-run-eval-suites.md` — how to run a smoke suite.

## Verify

`! bin/booping render-playbook learn | rg -n '_lessons'`
