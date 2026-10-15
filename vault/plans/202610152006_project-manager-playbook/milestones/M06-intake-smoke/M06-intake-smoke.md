---
id: "06"
title: "Smoke suite for project-manager intake"
sp: 3
status: done
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M06: Smoke suite for project-manager intake

A deterministic smoke suite holds `intake`'s contract: one item per request, the user's words verbatim, nothing else written.

**Scope**: create the suite beside the step — `playbooks/project-manager/intake/promptfooconfig.yaml`, `tests.yaml`, `_fixtures/` — copying `playbooks/specs/guide/`'s shape: `mode: step`, `output_mode: files`, the cwd the vault root, the run has no shell, so each fixture states the `booping` outputs a live run would read and stands in for the item files `booping items add` would write (frontmatter `id`, `title`, `status: open`, `source: request`, body the verbatim text — copy the shape `booping items add` writes, from `booping-python/e2e/cases/items/add-request-with-a-title-and-argv-text.txtar`). Cases, all `tier: smoke`:

1. `two-requests-and-an-aside` — a message with two requests and an aside → exactly `open-items/OI-0001.md` … `OI-0003.md`, each body containing its request's sentence verbatim (a distinctive phrase per request asserted with `contains`), `noOthers: true`.
2. `answer-only` — a message that only answers `C1` on an existing item whose sidecar the fixture holds → no new item file; the sidecar's `C1` heading ends `answered` and its answer contains the user's words.
3. `filed-ids-posted` — the return lists each filed id with its title (`return.js`, one entry per item).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Suite config and the three fixtures. | `playbooks/project-manager/intake/promptfooconfig.yaml`, `playbooks/project-manager/intake/_fixtures/*.md` | 2 | done |
| 6.2 | `tests.yaml` with the asserts above. | `playbooks/project-manager/intake/tests.yaml` | 1 | done |

## Definition of Done

### Task 6.1

- [x] `just suites` lists `project-manager/intake`.

### Task 6.2

- [x] Every case carries `metadata: {playbook: project-manager, step: intake, fixture, tier: smoke}` and only the shared asserts under `playbooks/_lib/asserts/`.
- [x] The suite passes.

Return: the list of changed and created files and the suite's pass count, nothing else.

## References

- `playbooks/specs/guide/promptfooconfig.yaml`, `playbooks/specs/guide/tests.yaml`, `playbooks/specs/guide/_fixtures/record-decision.md` — suite, case and fixture shapes.
- `playbooks/_lib/asserts/files.js`, `playbooks/_lib/asserts/return.js` — assert configs.

## Verify

`EVAL_PR=0 just smoke project-manager/intake`
