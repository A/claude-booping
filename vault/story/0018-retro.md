---
type: story
title: Retro
summary: Retro mines a finished sprint's session logs, diff and the user's feedback into a standalone retrospective.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a finished sprint mined into a retrospective, so that what went
wrong is found by root cause and can be learnt from.

## Scenarios

1. The user runs `/playbook retro`; `intake` validates the plan is in the retro queue
   and offers the other queued plans to include, postpone or skip.
2. `prepare` reads the open corrections, marks each handled, and mines the session logs
   and the sprint diff, keeping the mined list back.
3. `gather-feedback` asks the user's raw take first, one question at a time, then walks
   the mined items for accept, dismiss or the user's own wording.
4. `research-issues` root-causes each accepted issue; `synthesize` drafts the
   retrospective and shows a summary.
5. `save` writes `retrospectives/{slug}.md` and stamps `retro:` on every covered plan;
   the retrospective waits for learn.

## Edge cases

- A plan not worth a retrospective: the user picks skip and the plan gets `retro: skipped`, out of the queue for good, its status still `done`.
- Several queued plans: one retrospective covers them all, each plan pointing back through its own `retro:` key.

## Criteria

- Queues every `done` plan not yet covered (`retro: null`).
- Mines session logs and the sprint diff for what actually happened.
- Reads the open corrections (`corrections/`, [adr/0026](../adr/0026-corrections-log.md)) first and marks what it handled.
- Gathers the user's raw feedback and triages issues by root cause.
- Saves `retrospectives/{slug}.md` and stamps each covered plan's `retro:` key, the
  plan staying at `done`.
