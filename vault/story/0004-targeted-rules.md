---
type: story
title: Targeted rules
summary: "An accepted rule's brief is injected into exactly the playbooks, steps, agents or skills its targets: list names."
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to write a rule that reaches only the surfaces it
names, so that a project's rule shapes exactly the step it is about and nothing else.

## Scenarios

1. The user writes a rule record in the project specs tier with `status: accepted`, a
   `targets:` list naming, for example, one step of a playbook, and a `brief:`.
2. The user runs that playbook; its render carries a `## Rules` section with the
   rule's brief and a link to the record.
3. The targeted step's body carries the rule too; steps, agents and skills the rule
   does not name never see it.

## Edge cases

- A rule with no `targets:` injects nowhere.
- A rule that is not `status: accepted` is not injected.
- A rule meant for an external agent cannot target it with `agent:`; it targets the step that delegates to that agent.

## Criteria

- Rules are `status: accepted` rule records in the core, global and project specs
  tiers, each carrying a `targets:` list and a `brief:`.
- A target names a playbook, a step, an agent or a skill (`{playbook}`,
  `{playbook}/{step}`, `agent:{id}`, `skill:{name}`).
- Matched rules are injected as brief plus link into a playbook render's `## Rules`
  section, each step's body and internal agent and skill bodies; an untargeted rule
  injects nowhere.
