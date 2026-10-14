---
type: story
title: Targeted lessons
summary: "A lesson is a markdown note injected into exactly the playbooks, steps, agents or skills its targets: list names."
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **an advanced user**, I want to write a lesson that reaches only the surfaces it
names, so that a project's lesson shapes exactly the step it is about and nothing else.

## Criteria

- Lessons live in two flat `_lessons/` roots, the global level and the Project Vault,
  each carrying a `targets:` list.
- A target names a playbook, a step, an agent or a skill (`{playbook}`,
  `{playbook}/{step}`, `agent:{id}`, `skill:{name}`).
- Matched lessons are injected into a playbook render's `## Lessons` section, each
  step's body and internal agent and skill bodies; an untargeted lesson injects
  nowhere.
