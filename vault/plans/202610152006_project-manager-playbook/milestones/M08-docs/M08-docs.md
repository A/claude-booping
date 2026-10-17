---
id: "08"
title: "Documentation, README and CLAUDE.md on the project-manager"
sp: 3
status: done
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M08: Documentation, README and CLAUDE.md on the project-manager

The public docs, the README and CLAUDE.md describe the project-manager, the item questions and `booping run code-review` — what a user touches, no internal churn (rule/0008).

**Scope**: create `documentation/project_manager.md` — what the manager does in a session, the two modes and where each stops, the item questions (`booping items ask|answer`, the sidecar, how status shows a waiting item), the runs it launches, merge staying local, and how a project adds push/deploy through a rule or runbook targeting `project-manager`; copy `documentation/specs_playbook.md`'s depth and tone. Add it to `mkdocs.yml`'s `Workflow:` nav. Add `project-manager` to `documentation/playbook.md`'s shipped-playbooks list. In `documentation/specs.md` (or wherever `booping items` verbs are documented — find it with grep) add `ask`, `answer` and `close` on an open item. In `README.md` add the playbook where playbooks are listed and, in the Statuses section, the `open → done` edge of the open-item narrative (rule/0023). In `CLAUDE.md`: the opening paragraph's playbook list, `## Commands` (`items` gains `ask`, `answer`; `run` gains `code-review`), `## Lifecycle` open-items track (the `open-items/questions/{id}.md` sidecar, written only by `booping items ask|answer`; `open → done`), `## Config` (`core.project_manager_playbook`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | `documentation/project_manager.md` and the nav entry. | `documentation/project_manager.md`, `mkdocs.yml` | 1 | done |
| 8.2 | Shipped list, items verbs, README list and Statuses. | `documentation/playbook.md`, `documentation/specs.md`, `README.md` | 1 | done |
| 8.3 | CLAUDE.md lines above. | `CLAUDE.md` | 1 | done |

## Definition of Done

### Task 8.1

- [x] The page covers the user-facing surface above and nothing about how it is implemented.

### Task 8.2

- [x] Every page that lists the shipped playbooks names `project-manager`; the README Statuses open-item narrative has `open → done`.

### Task 8.3

- [x] CLAUDE.md names `project-manager`, `items ask|answer`, `run code-review`, the questions sidecar and `core.project_manager_playbook`, one line each where its section lists its peers.

Return: the list of changed files, nothing else.

## References

- `documentation/specs_playbook.md` — page depth and tone.
- `mkdocs.yml` — the `Workflow:` nav.

## Verify

`just docs`
