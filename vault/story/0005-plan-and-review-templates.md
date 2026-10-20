---
type: story
title: Plan and review templates
summary: Groom and code-review offer plan and review templates the user authored in the Project Vault or at the global level.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P2
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to author plan and review templates, so that groom and
code-review shape their artefacts the way my project needs.

## Scenarios

1. The user drops a plan template, with its `name` and `description` frontmatter, into
   the Project Vault's `plan_templates/`.
2. At drafting, groom offers it beside the templates the plugin ships, and drafts the
   plan against the one chosen.
3. The user drops a review template into the Project Vault's `review_templates/`, or
   into the global level's to use it in every project on the machine.
4. A code-review run offers it and reviews against the one chosen.

## Edge cases

- A project template carries the same name as a shipped one: it overrides the shipped one.
- A review template exists at both the global and the project level under one name: the project's wins.

## Criteria

- Plan templates in the Project Vault's `plan_templates/` are offered by groom at
  drafting.
- Review templates in the Project Vault's `review_templates/` or at the global level
  are offered by code-review runs.
