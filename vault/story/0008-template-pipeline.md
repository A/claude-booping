---
type: story
title: Template pipeline
summary: Skill and agent bodies render in one runtime stage from src/templates/ with full project context, reproducibly when pinned.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want every skill and agent body rendered live at load time from
one template source, so that an edit takes effect without a build step and a render can
be reproduced anywhere.

## Scenarios

1. A contributor edits a template under `src/templates/`.
2. The next time Claude Code loads the skill or agent, its hand-authored thin shell
   runs `booping render` on that template, and the body renders with the full project
   context — config merge, vault, rules, playbooks — so the edit takes effect with no
   build step.
3. To inspect a body without loading it, the contributor renders it by hand with
   `booping render` or `booping render-playbook`, and dumps the assembled context with
   `booping debug-context` when the output is unexpected.
4. For a reproducible render, the contributor pins config values with `--set`, the
   timestamped macros with stubs, and the Project Vault with `--project`, and gets a
   byte-identical result.

## Edge cases

- A macro exits non-zero: the render is an error.
- The `session` macro runs outside a Claude Code session: it prints an empty string, so the render still succeeds.
- A render pinned with `--project`: discovery and the config merge see only the core and project levels, never the global one.

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
