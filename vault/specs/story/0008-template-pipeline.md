---
type: story
title: Template pipeline
summary: Skill and agent bodies render in one runtime stage from src/templates/ with full project context, reproducibly when pinned.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want every skill and agent body rendered live at load time from
one template source, so that an edit takes effect without a build step and a render can
be reproduced anywhere.

## Criteria

- Skill and agent bodies render in one runtime stage from `src/templates/` with full
  project context; the committed `skills/` and `agents/` shells are hand-authored.
- `booping render` and `booping render-playbook` render any template or playbook by
  hand.
- `--set dotted.key=value` overrides one config value per render and timestamped
  values can be pinned, for byte-identical renders.
- `--project` pins a render to an explicit Project Vault, narrowing discovery and the
  config merge to the core and project levels.
- `booping debug-context` dumps the assembled render context as YAML.
