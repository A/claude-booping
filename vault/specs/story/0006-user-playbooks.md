---
type: story
title: User playbooks
summary: Playbooks the user authors at the global level or in the Project Vault are discovered and run beside the core ones.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **an advanced user**, I want to write my own playbooks with the same mechanics as
the core ones, so that my own procedures run under `/playbook` like the shipped loop.

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
- The `playbook-authoring` playbook scaffolds a new playbook: brief, decomposition,
  manifest, then per step spec, fixtures, prompt and eval suite driven to green.
