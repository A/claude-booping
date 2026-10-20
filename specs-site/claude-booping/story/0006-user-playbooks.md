---
type: story
title: User playbooks
summary: Playbooks the user authors at the global level or in the Project Vault are discovered and run beside the core ones.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to write my own playbooks with the same mechanics as
the core ones, so that my own procedures run under `/playbook` like the shipped loop.

## Scenarios

1. The user creates a playbook in the Project Vault's `_playbooks/` (or at the global
   level) — `playbook.md`, an optional `playbook.yaml`, one directory per step with its
   `prompt.md` — by hand or through the `playbook-authoring` playbook.
2. `/playbook` lists it beside the core playbooks and drives it with the same
   mechanics: the step graph, parallel waves, subgraphs and, when declared, its
   `states:` machine.
3. The user opts its bodies into Jinja with `jinja: true` and reads its own config
   namespace from them.
4. The user adds an eval suite beside a step and runs it to guard the step's contract.

## Edge cases

- The user's playbook takes a name already used at another level: names must be unique across levels, so the clash blocks the run.
- A step directory holds no `prompt.md`: it is no step, and is skipped with a warning.
- Steps in one parallel wave must all be detached.

## Criteria

- A playbook at the global level or in the Project Vault's `_playbooks/` —
  `playbook.md`, optional `playbook.yaml`, one directory per step with `prompt.md` — is
  discovered, names unique across levels.
- It declares a step graph with parallel waves and subgraphs, opt-in `states:`
  machines, and its own config namespace by the core placement rule.
- Bodies can be Jinja templates over the full context (`jinja: true`), resolved
  most-specific-first, and a step can hold per-model prompt variants.
- A step can carry its own eval suite (`tests.yaml`, `promptfooconfig.yaml`,
  fixtures).
- The `playbook-authoring` playbook creates a new playbook: brief, decomposition,
  manifest, then per step spec, fixtures, prompt and eval suite driven to green.
