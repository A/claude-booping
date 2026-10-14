---
type: story
title: External agents
summary: Agents the plugin does not ship are wired into playbook agent slots through config and shaped per project by targeted rules.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **an advanced user**, I want to plug my own agents into booping's agent slots, so
that runs use the agents I already have instead of only the shipped ones.

## Criteria

- A playbook's agent slot points at an external `~/.claude/agents/` agent via config.
- Any agent or skill is shaped per project by a targeted rule, not an extension
  file; `agent:` targets reach booping's own agents only, so an external agent is
  shaped by a rule on the step that delegates to it.
