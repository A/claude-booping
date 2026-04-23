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

The skill owns all reads and writes against the project vault (`~/Claude/{project}/`). The agent's job is to edit code in the attached repo and report back. The skill flips DoD checkboxes in the plan file after the agent reports done and Verify passes.

Lesson context reaches agents through two baked-in channels, not per-briefing routing:

- **Plan** — `/groom` folded applicable lessons into DoD items and Verify commands at grooming time. The skill pastes those fields into the briefing verbatim.
- **Agent extension** — the shared `agent_booping-developer.md` extension in the project vault (owned by `/learn`) is read by the agent itself during Preflight at `~/Claude/{project}/_booping/agent_booping-developer.md`. The agent also self-loads `partial_agents_developer_rules.md` and `partial_agents_developer_workflow.md` from its own Preflight. The skill does not prepend a contract block or inject an extra-instructions path.

The skill does not filter or inline lessons per-briefing. If a lesson isn't already in the plan or the agent extension file, it won't reach the agent.

### Briefing template

Developer agents self-load their full operating contract (rules, workflow, extra instructions) via their own Preflight. The skill only passes the task envelope.

Every briefing sent via `Agent()` uses this body:

```
Task / goal: <what to change and why>
Decisions that apply: <plan decisions relevant here>
Related files: <files relevant; read only the ones you'll touch. If something outside this list needs to change, stop and report.>
DoD: <checklist from the plan, verbatim>
Verify: <exact test/lint commands the agent must run before reporting done>
```

Both `booping-developer-middle` and `booping-developer-senior` receive identical briefings.
