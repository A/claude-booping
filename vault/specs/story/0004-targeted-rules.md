---
type: story
title: Targeted rules
summary: "An accepted rule's brief is injected into exactly the playbooks, steps, agents or skills its targets: list names."
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to write a rule that reaches only the surfaces it
names, so that a project's rule shapes exactly the step it is about and nothing else.

## Criteria

- Rules are `status: accepted` rule records in the core, global and project specs
  tiers, each carrying a `targets:` list and a `brief:`.
- A target names a playbook, a step, an agent or a skill (`{playbook}`,
  `{playbook}/{step}`, `agent:{id}`, `skill:{name}`).
- Matched rules are injected as brief plus link into a playbook render's `## Rules`
  section, each step's body and internal agent and skill bodies; an untargeted rule
  injects nowhere.
