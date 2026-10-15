---
id: "01"
title: "Migrate survey summary always asks about uncommitted work"
sp: 1
status: pending
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M01: Migrate survey summary always asks about uncommitted work

The migrate survey's rendered summary says the uncommitted-work ask names the current branch and is always asked, matching the body `opus-5.md` already carries ([adr/0027](../../../../specs/adr/0027-autonomy-modes.md)).

**Scope**: `playbooks/migrate/survey/prompt.md`, its frontmatter `summary:` only — the body (`{% include "opus-5.md" %}`) and `review_gate:` stay. The new summary, exact text:

> Open the run: confirm a project is attached and the recorded migration id is readable; when work is uncommitted, name the current branch and the work and ask to commit repo and vault — always asked, whatever `core.auto_migrate` and `core.autonomy` say — committing on confirmation; present the pending set the rendered body carries and what each migration will do; report "already current" and end the run when the set is empty.

The one expected snapshot drift is the `survey` row of `playbooks/migrate/_reports/output.md`; the runner accepts it (index.md, Decisions — Snapshots).

Tests: none new — the committed migrate report holds the rendered summary, and `just snapshots` shows the one-row drift.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Replace the frontmatter `summary:` with the text above. | `playbooks/migrate/survey/prompt.md` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `summary:` renders character for character as the text above.
- [ ] `bin/booping render-playbook migrate` prints no STOP notice.
- [ ] No other file changes.

Return: the list of changed files, nothing else.

## References

- `playbooks/migrate/survey/opus-5.md` — `## Work in flight`, the wording the summary follows.

## Verify

`bin/booping render-playbook migrate | grep -F 'always asked, whatever'`
