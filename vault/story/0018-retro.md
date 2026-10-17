---
type: story
title: Retro
summary: Retro mines a finished sprint's session logs, diff and the user's feedback into a standalone retrospective.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: done
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a finished sprint mined into a retrospective, so that what went
wrong is found by root cause and can be learnt from.

## Criteria

- Queues every `done` plan not yet covered (`retro: null`).
- Mines session logs and the sprint diff for what actually happened.
- Reads the open corrections (`corrections/`, [adr/0026](../adr/0026-corrections-log.md)) first and marks what it handled.
- Gathers the user's raw feedback and triages issues by root cause.
- Saves `retrospectives/{slug}.md` and stamps each covered plan's `retro:` key, the
  plan staying at `done`.
