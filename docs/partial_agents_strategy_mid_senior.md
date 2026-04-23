Delegation strategy where only two developer tiers are active: `booping-developer-middle` (Sonnet) and `booping-developer-senior` (Opus, reasoning high). Every task is delegated — the orchestrator never edits application code itself.

## Active roster

| Agent | Model | Handles |
|-------|-------|---------|
| `booping-developer-middle` | sonnet | 1–2 SP tasks; may be batched |
| `booping-developer-senior` | opus (reasoning high) | 3–4 SP tasks; one per briefing |

A **5 SP** task is a refuse — kick back to `/groom` for re-decomposition before any worker takes it.

## SP → agent + batching rules

- **1–2 SP → middle.** Prefer batching: scan the milestone for 1–2 SP tasks and combine related or sequential ones into a single briefing, up to **~10 SP combined**. Keep independent tasks that touch unrelated files in separate briefings so they can run in parallel.
- **3–4 SP → senior.** Always one task per briefing. Do not batch senior tasks; their design judgment is per-task.
- **5 SP → refuse.** Stop and route the user to `/groom` for re-decomposition. This rule's canonical home is `docs/partial_sprint_planning.md`.

## Delegation invariant

Every task runs inside an `Agent()` call — even a 1-line change. Batching consolidates small tasks into one briefing; it does NOT permit the orchestrator to edit application code itself. The rule is "delegate every write", not "delegate every call".

## How to invoke agents

The skill owns all reads and writes against the project vault (`~/Claude/{project}/`). The agent's job is to edit code in the attached repo and report back. The skill flips DoD checkboxes in the plan file after the agent reports done and Verify passes, and appends to `metrics/lesson-hits.md` at the end of the sprint.

Lesson context reaches agents through two baked-in channels, not per-briefing routing:

- **Plan** — `/groom` folded applicable lessons into DoD items and Verify commands at grooming time. The skill pastes those fields into the briefing verbatim.
- **Contract** — `/develop` reads `partial_agents_developer_rules.md`, `partial_agents_developer_workflow.md`, and `partial_extra_instructions.md` at runtime, concatenates their bodies under a `Contract:` heading, and prepends that block to every `Agent()` call. Agents do not scan the plugin tree.

The skill does not filter or inline lessons per-briefing. If a lesson isn't already in the plan or the contract block, it won't reach the agent.

### Briefing template

The skill reads the three partials at runtime (`partial_agents_developer_rules.md`, `partial_agents_developer_workflow.md`, `partial_extra_instructions.md`) and concatenates their bodies under the `Contract:` heading. Agents do not scan the plugin tree.

Every briefing sent via `Agent()` starts with this header:

```
Contract:
  <literal concatenation of:
    docs/partial_agents_developer_rules.md body
    docs/partial_agents_developer_workflow.md body
    docs/partial_extra_instructions.md body>

Extra instructions file: ~/Claude/{project}/_booping/agent_booping-developer.md

Task / goal: <what to change and why>
Decisions that apply: <plan decisions relevant here>
Related files: <files relevant; read only the ones you'll touch. If something outside this list needs to change, stop and report.>
DoD: <checklist from the plan, verbatim>
Verify: <exact test/lint commands the agent must run before reporting done>
```

Both `booping-developer-middle` and `booping-developer-senior` receive the same `Contract:` block. The `Extra instructions file:` path is verbatim; the agent reads it or skips silently if absent.
