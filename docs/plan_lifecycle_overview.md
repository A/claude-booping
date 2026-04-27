Lifecycle reference for plan statuses and transitions across skills. Lazy-loaded by `/chat` when the user asks about valid moves or wants a manual status flip. Operational gates (cross-validation, redecomposition checks) and `on_exit` ceremony are intentionally omitted — those belong to the owning skill's contract in `src/templates/_partials/_plan_transitions.j2`.


### `backlog`

Parked plan — not actively being worked on. Sibling stubs from split sprints and user-filed ideas not yet in grooming live here.


| To | When | Owner |
|----|------|-------|
| `in-spec` | User asks /groom to shape a parked plan, or /groom is invoked on a fresh request | /groom |
| `cancelled` | User shelves the request before grooming | /groom |


### `in-spec`

/groom is actively specifying — researching, designing, drafting the plan.


| To | When | Owner |
|----|------|-------|
| `awaiting-plan-review` | Draft is complete and ready to present to the user | /groom |
| `backlog` | User parks the work mid-grooming to revisit later | /groom |
| `cancelled` | User shelves the work mid-grooming | /groom |


### `awaiting-plan-review`

Plan drafted; /groom is presenting to the user and awaiting explicit approval, change request, or cancellation.


| To | When | Owner |
|----|------|-------|
| `ready-for-dev` | User explicitly approves the plan ('looks good', 'ship it'). Silence does not count. | /groom |
| `in-spec` | User requests changes that require re-research or re-design | /groom |
| `cancelled` | User shelves the plan instead of approving | /groom |


### `ready-for-dev`

Approved by user. Queued for /develop to claim.


| To | When | Owner |
|----|------|-------|
| `in-progress` | /develop claims the plan at the start of its execute phase | /develop |


### `in-progress`

/develop has claimed the plan and is executing milestones.


| To | When | Owner |
|----|------|-------|
| `awaiting-retro` | All milestones done | /develop |
| `fail` | Unrecoverable blocker on the same milestone | /develop |


### `awaiting-retro`

All milestones done; waiting for /retro to write the retrospective.


| To | When | Owner |
|----|------|-------|
| `awaiting-learning` | Retrospective written and saved | /retro |
| `done` | User opts to skip retro for a stale plan and mark it done without retrospective or learning | /retro |


### `awaiting-learning`

Retro written; waiting for /learn to absorb lessons.


| To | When | Owner |
|----|------|-------|
| `done` | All accepted learnings written | /learn |


### `done`

Terminal success. /learn has absorbed all lessons.

_Terminal — no outgoing transitions._


### `fail`

Terminal technical failure. /develop hit an unrecoverable blocker.

_Terminal — no outgoing transitions._


### `cancelled`

Terminal product decision. User shelved the plan.

_Terminal — no outgoing transitions._

