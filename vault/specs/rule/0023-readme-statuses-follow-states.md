---
type: rule
title: The README Statuses section follows the states blocks
summary: The README's Statuses section is a hand-kept narrative over each playbook's states block; a change to a states block revisits it in the same change.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [CLAUDE.md]
---

## Rule

Each playbook's `states:` block is the authority on its statuses. The README's
Statuses section is a hand-maintained narrative over them, not rendered from them,
so a change to a `states:` block revisits that section.

[clarify] The source says "revisit"; whether it must land in the same commit is not
named in the source.

## Follows from

- [Single source](../values/0001-booping.md#single-source) — the narrative is a known copy, kept honest by
  hand until it is rendered.
