---
type: story
title: External agents
summary: Agents the plugin does not ship are wired into playbook agent slots through config and shaped per project by targeted lessons.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **an advanced user**, I want to plug my own agents into booping's agent slots, so
that runs use the agents I already have instead of only the shipped ones.

## Criteria

- A playbook's agent slot points at an external `~/.claude/agents/` agent via config.
- Any agent or skill is shaped per project by a targeted lesson, not an extension
  file.
