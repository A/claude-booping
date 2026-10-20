---
type: story
title: Run state machines
summary: "A run's state lives in per-playbook states: machines that only the booping CLI advances."
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want run state held in declared `states:` machines that only
the CLI advances, so that a run's status is never re-derived or hand-edited by the model.

## Scenarios

1. A playbook author declares a `states:` machine in `playbook.yaml`: the artefact, the
   initial status, the statuses and their transitions with `when`, `gates` and `hooks`.
2. A run reaches a step outcome; the driver matches it against a transition's `when`,
   judges its gates, and moves the artefact with the CLI.
3. The CLI writes the new status and runs the transition's hooks — frontmatter stamps
   and `script` hooks — and prints a mutation report the driver takes as authoritative.
4. Later, the driver asks the CLI for the run's state and gets every artefact's status
   and the per-instance frontier, from which an interrupted run resumes.

## Edge cases

- A machine declares no `artifact:`: the artefact is addressed with `--target`.
- The user cancels a run in any non-terminal status: it moves to `cancelled` and that edge's own exit hooks run.
- A script hook's name exists both in the playbook's `_scripts/` and in a shared `_scripts/` root: the playbook's own wins, then the most specific discovery root.
- `--append` on a list key that is absent creates it, and adds a value already present only once.

## Criteria

- `booping playbook-transition` is the sole writer of run state, guarded by `when`
  conditions and gates declared in `playbook.yaml`.
- `frontmatter-update` hooks stamp any workdir-relative file with `{instance}`
  interpolation, and `--append` adds to a list key, creating and de-duplicating it.
- `script` hooks resolve playbook-dir first, then by discovery-root specificity over
  the shared `_scripts/` roots, passing argv through.
- `cancelled` is a terminal outcome reachable from any non-terminal status, with its
  own exit hooks; `--target` addresses a run artefact when the machine declares no
  `artifact:`.
- `booping playbook-state` reports every run artefact's status and a per-instance
  frontier, so per-milestone statuses resume a run.
