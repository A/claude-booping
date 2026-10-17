---
id: "09"
title: "Smoke evals for specs/guide"
sp: 4
status: done
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M09: Smoke evals for specs/guide

`just smoke specs/guide` runs three deterministic cases against the guide step.

**Scope**: `playbooks/specs/guide/promptfooconfig.yaml` + `tests.yaml` + `_fixtures/`, shaped like the playbook-authoring fixtures suite (provider `playbooks/_lib/claude_provider.py`, shared asserts from `playbooks/_lib/asserts/`), every case `metadata.tier: smoke`:

1. **init offer** — fixture vault with no project tier, user message "set up specs for this project": the reply offers init and the alignment guide (return assert); no file under a `specs/` dir written (files assert).
2. **record a decision** — fixture vault with a project tier holding one value, user message stating a decision with its rejected alternative and a confirmation line: `specs/adr/0001-*.md` exists and passes `mdcheck` against the shipped ADR schema; `open-items/OI-0001.md` exists; the reply contains no "which action" question (return assert on its absence).
3. **what is open** — fixture vault with two open items: the reply carries both ids; no file written.

Tests: this milestone is the test — the smoke tier.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | Suite config and the three fixture vaults. | `playbooks/specs/guide/promptfooconfig.yaml`, `playbooks/specs/guide/_fixtures/` | 2 | done |
| 9.2 | The three cases and their asserts. | `playbooks/specs/guide/tests.yaml` | 2 | done |

## Definition of Done

### Task 9.1

- [x] `just suites` lists `specs/guide`.

### Task 9.2

- [x] Three cases, all `tier: smoke`, only shared asserts from `playbooks/_lib/asserts/`.
- [x] `just smoke specs/guide` is green (run with `EVAL_PR=0`).

Return: the list of changed files and the smoke pass count, nothing else.

## References

- `playbooks/playbook-authoring/fixtures/tests.yaml`, `playbooks/playbook-authoring/fixtures/promptfooconfig.yaml` — the smallest suite to copy.
- `playbooks/_lib/asserts/files.js`, `playbooks/_lib/asserts/mdcheck.js`, `playbooks/_lib/asserts/return.js` — the asserts.

## Verify

`EVAL_PR=0 just smoke specs/guide`
