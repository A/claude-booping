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
- **5 SP → refuse.** Stop and route the user to `/groom` for re-decomposition. Canonical threshold: `src/config.yaml` → `sprint.redecompose_threshold`.

## Delegation invariant

Every task runs inside an `Agent()` call — even a 1-line change. Batching consolidates small tasks into one briefing; it does NOT permit the orchestrator to edit application code itself. The rule is "delegate every write", not "delegate every call".

## How to invoke agents

The skill owns all reads and writes against the project vault (`~/Claude/{project}/`). The agent's job is to edit code in the attached repo and report back. The skill flips DoD checkboxes in the plan file after the agent reports done and Verify passes.

Lesson context reaches agents through two baked-in channels, not per-briefing routing:

- **Plan** — `/groom` folded applicable lessons into DoD items and Verify commands at grooming time. The skill pastes those fields into the briefing verbatim.
- **Agent extension** — the shared `agent_booping-developer.md` extension in the project vault (owned by `/learn`) is injected at agent load time via `!`bin/booping-extra-instructions agent_booping-developer.md`` at the bottom of the agent body. The skill does not prepend a contract block or inject an extra-instructions path. Rules, workflow, and report format are inlined in the agent body itself.

The skill does not filter or inline lessons per-briefing. If a lesson isn't already in the plan or the agent extension file, it won't reach the agent.

### Briefing template

Developer agents carry their full operating contract (rules, workflow, report format) inline in the agent body, plus the project-local extension injected via `!`bin/booping-extra-instructions agent_booping-developer.md``. The skill only passes the task envelope.

Every briefing sent via `Agent()` uses this body:

```
Task / goal: <what to change and why>
Decisions that apply: <plan decisions relevant here>
Related files: <files relevant; read only the ones you'll touch. If something outside this list needs to change, stop and report.>
DoD: <checklist from the plan, verbatim>
Verify: <exact test/lint commands the orchestrator will run after the agent reports done — informational for the agent>
```

Both `booping-developer-middle` and `booping-developer-senior` receive identical briefings.
