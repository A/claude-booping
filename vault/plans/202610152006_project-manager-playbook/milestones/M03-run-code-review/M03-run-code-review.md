---
id: "03"
title: "booping run code-review registers the independent review"
sp: 2
status: pending
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M03: booping run code-review registers the independent review

`booping run code-review PLAN [--autonomous]` launches and records the independent review the way `booping run develop` does.

**Scope**: in `booping-python/src/booping/commands/run.py` add the `code-review` sub-verb beside `develop`, sharing its target validation (exactly one plan — `error: code-review takes exactly one plan`), item resolution (`planned_for`), prompt filling (`{playbook}` = `code-review`) and launch; the record's `playbook:` is `code-review`. If `booping-python/src/booping/runs.py` holds a playbook allow-list, add `code-review` there. No config change: `core.run.prompt` already takes `{playbook}`.

Tests (integration tier, e2e corpus `booping-python/e2e/cases/run/`, the same `sh -c` fake command as the existing cases, hand-derived): code-review over a plan directory → `finished` record with `playbook: code-review` and the prompt naming `code-review` and the absolute plan path; code-review with two targets → exit 1 with the contract's message and no record.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `code-review` sub-verb on `booping run`. | `booping-python/src/booping/commands/run.py`, `booping-python/src/booping/runs.py` | 1 | pending |
| 3.2 | Two e2e cases above. | `booping-python/e2e/cases/run/code-review-*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] `bin/booping run --help` lists `groom`, `develop`, `code-review`, `ack`; `bin/booping run code-review --help` shows `PLAN` and `--autonomous`.
- [ ] `develop` and `code-review` share one validation path — no copied block.

### Task 3.2

- [ ] Both cases exist and pass; every existing `run` case passes unchanged.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/run/develop-over-a-plan-directory-records-a-finished-run.txtar`, `booping-python/e2e/cases/run/develop-with-two-targets-is-rejected.txtar` — the cases to mirror.

## Verify

`cd booping-python && uv run pytest e2e/cases/run -q`
