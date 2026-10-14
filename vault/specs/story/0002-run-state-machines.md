---
type: story
title: Run state machines
summary: "A run's state lives in per-playbook states: machines that only the booping CLI advances."
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want run state held in declared `states:` machines that only
the CLI advances, so that a run's status is never re-derived or hand-edited by the model.

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
