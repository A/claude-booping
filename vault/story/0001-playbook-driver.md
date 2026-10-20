---
type: story
title: Playbook driver
summary: The /playbook skill discovers a procedure across the core, global and project levels and drives it to completion.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want one `/playbook` skill to find a procedure and drive its steps in
graph order, so that any procedure runs to completion without me sequencing it.

## Scenarios

1. The user invokes `/playbook` and sees the playbooks visible from the core, global
   and project levels.
2. The user names a playbook, or describes the work and the skill selects the playbook
   whose trigger matches.
3. The skill renders the playbook's procedure and drives its steps in graph order: a
   runner-performed step's body is fetched with `booping render-playbook --step` when
   the step runs, a detached step goes to its sub-agent, which fetches its own body.
4. After each batch of steps the run pauses at their review gates, presents the
   output, and continues on the user's explicit confirmation, until the procedure is
   complete.

Resuming: the user invokes the same playbook on a run that was interrupted; the skill
reads the state frontier and continues from the first unfinished step.

## Edge cases

- Two levels hold a playbook of the same name: the clash is flagged and the run is blocked.
- The user stays silent at a review gate: the run waits, it never passes the gate on silence.
- An assisted step loops back: the follow-up goes to the same research agent by id, not to a fresh one.
- A graph or render problem: the run surfaces it as a STOP or Note notice to tell the user, not as a crash.

## Criteria

- Lists the playbooks visible from the core, global and project levels and selects
  one by its trigger or by name; a name clash across levels is flagged and blocks the
  run.
- Drives steps in graph order, each parallel wave as detached sub-agents, with
  one-level subgraphs.
- Delegates each step inline, assisted or detached per its `detached:` field; an
  assisted step hands heavy reads to the config-named research agent, resumed by id
  across a loopback.
- Loads step bodies lazily with `booping render-playbook --step`.
- Pauses at review gates for an explicit verdict, never running past one on silence,
  and resumes an interrupted run from the state frontier.
