---
type: adr
title: The driver owns the vault; workers receive briefings
summary: The playbook driver does every vault read and write; worker agents touch only repo code and know nothing of lessons, plan statuses or the vault layout.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
rules: [rule/0019]
values: [values/0001#minimal-effective-context, values/0001#single-source, values/0001#stack-agnostic-core]
sources: [CLAUDE.md, vault/retrospectives/20260423-skill-refactors-chat-develop-retro.md, vault/retrospectives/20260422-plans-as-data-refactor.md, vault/retrospectives/20260610-plannotator-code-review-surface.md, vault/retrospectives/20260610-cli-logging-and-agent-namespacing.md, vault/retrospectives/20260722-seven-plan-retro.md]
---

## Context

The 2026-04-23 refactor found three kinds of rot in agent bodies: context rot
(phrases left from old corrections), leakage (orchestrator concepts such as lessons,
`/learn` and plan statuses inside agents that do not need them) and duplicated
rules across agents. The 2026-04-22 retro found the orchestrator bypassing the
CLI-only write path for plan files during the very sprint that established it.
Agents returning extra prose rotted the orchestrator's context until briefings
bounded the return to what the harness needs.

## Decision

The driver — the runner of a playbook — owns all vault reads and writes: plan
status, lessons, milestone tables, sidecars, vault commits. Worker agents touch only
repo code. A worker receives a briefing (its milestone file's path and the context
the runner chooses) and returns a bounded report; it does not name skills or
playbooks, read lessons or know plan statuses. A worker's code work may reach outside
the attached repo (a deliverable under `~/.claude/`, another repo) only after the
user explicitly confirms it for that plan; the vault stays the driver's either way. A lesson reaches a worker only
through the runner's briefing; project-local shaping of an agent is a targeted
lesson (`agent:{id}`), not an extension file.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Driver owns the vault](#driver-owns-the-vault) | accepted | low | medium | One writer for run state; lean agents |
| [Workers read and write the vault](#workers-read-and-write-the-vault) | rejected | low | medium | Leakage into agent bodies |

### Driver owns the vault

Vault knowledge stays with the runner; agents get a briefing.

- **Pros:** one writer of vault state; agent bodies stay generic and short; a
  worker on a foreign harness needs no vault access.
- **Cons:** a lesson that matters to a worker reaches it only if the runner puts it
  in the briefing — the 2026-07-22 retro found an audience lesson missing from a
  delegated docs task for that reason.
- **Complexity:** low.
- **Reversibility:** medium.

### Workers read and write the vault

Agents load lessons, read the plan and update its status themselves.

- **Pros:** less briefing work for the runner.
- **Cons:** orchestrator concepts leak into every agent body; several writers of
  plan state.
- **Complexity:** low.
- **Reversibility:** medium.

## Consequences

- Develop's runner flips milestone checkboxes, takes transitions and commits the
  vault; the worker reports what it did and leaves the work uncommitted.
- Work outside the repo with the user's explicit confirmation was settled by the
  owner on 2026-10-14, after the 2026-06-10 Plannotator retro called "developer
  agents operate only inside the attached repo" an artificial limitation for a
  deliverable under `~/.claude/`. The code and `CLAUDE.md` still say "only repo
  code" — a backlog task brings them in line.
