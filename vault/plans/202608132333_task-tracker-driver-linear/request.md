---
plan: plans/202608132333_task-tracker-driver-linear/index.md
---

# Request

> let's groom next feature: we currently have everything built to work from claude cli. I want to change it a bit, so i can integrate it to linear. The idea is next: in linear we'll have hermes agent that handles all interaction with linear as agent, so it can be assigned to tasks and handle them. I want it to be based on statuses (not 1-1 as in playbooks, linear statuses will be presentational and triggers). Let's review plan workflow: so when there is a task(let say it 'request' type) to plan it appears in in-spec status, human will fill it with inputs, then when it's filled, it goes to ready-to-plan and agent gets this task, gets input and call `claude -p` with it. Claude should have linear mcp configured, or at least linear api with a token, so it can comment, create tasks, move statuses and so on. If claude has questions, it rises them as comments in initial request, and reassign task to user and moves to awaiting-clarification. Then when claude finally builds a new task "plan"-type (it can be a project or splitted different way), plan goes into body, milestones to be sub-tasks, and claude moves the plan task it into ready for review. User can comment, or move into ready-for-development (not autopicked) or selected-for-development (autopicked). Then flow continues to develop and then can go to retro (separate task type) or cr (on github). request and plan (i think it's epic or more like regular task) are cross-linked.
>
> So, now how i see it:
>
> 1. I want to make a "driver" - specific component, that isolates integration with a task-tracker surface (now linear only, but might be a jira later)
>     - driver is same way an integration on hooks level (idk, if it's possible) and some prompt injections (conditional step changes, etc). I want it to be encapsulated. Mb we can do 2 drivers now: cli and linear?
>     - probably driver goes into config core, as well as default env vars (key names, or we can do bash string interpolation there like ${LINEAR_API_KEY})
> 2. I want to review statuses in plan, so they can work for linear through hooks or just be representative to return after stopped (claude -p is oneshot, so it leaves plan into some state)
> 3. There is no on-demand questions surface, so need to think how to extract this part, mb make awaiting-clarification status for questions and track prev-status to return to after clarification? Also need to review prompts/steps how they're aligned to do so
>
> For test, we'll start locally, i can provide you linear api, and I can trigger claude -p for testing (hermes will do it later).
>
> For github I have a separate account to use, but now current is ok

## Task type

`feature` — a new user-facing capability: booping gains a second operating surface (a task tracker) alongside the interactive CLI, with new config, new run-state semantics and a new clarification surface.

Ruled out by test:

- `bug` — nothing diverges from expected behaviour today; there is no defect to reproduce. The named gaps ("no on-demand questions surface", "no tracker integration") are absent capabilities, not broken ones.
- `refactoring` — the driver abstraction is internal structure, but the run is not behaviour-preserving: it adds a Linear-driven plan track, a clarification state and non-interactive one-shot operation. A refactor DoD ("no user-visible behaviour change") would be false on this plan.

## Problem

Today booping runs only as an interactive Claude Code session. `/playbook` drives a playbook in one long conversation: the driver (the model) reads and writes vault artifacts, asks the user questions in chat as prose or `AskUserQuestion`, waits for review gates in-conversation, and persists run state only through `booping playbook-transition` on the vault artifact. Every questioning and gating mechanism assumes a live human on the other side of the same conversation.

What must change: the same playbooks must also run from a task tracker, one-shot. A tracker agent (`hermes`) assigned to a Linear issue invokes `claude -p` with that issue as input; the resulting Claude run must be able to read the issue, write back to it (comments, sub-issues, status moves, assignment), and terminate cleanly at a state the tracker can present and later resume from. That demands three things booping does not have:

1. **A tracker driver** — an encapsulated component that isolates the tracker surface (Linear now, possibly Jira later) from the playbooks. Two drivers to start: `cli` (today's interactive behaviour) and `linear`. Its integration points are hooks plus conditional prompt injection into steps; its configuration and credential env-var names live in `core` config.
2. **Status semantics that survive a one-shot run** — playbook run statuses reviewed so each is either mapped to a presentational Linear status through hooks, or at minimum a faithful resume point for the next invocation. Linear statuses are presentational and act as triggers; they are explicitly not 1:1 with playbook statuses.
3. **A questions surface** — questions raised on demand are today only chat prose. They must become a first-class, addressable surface: an `awaiting-clarification` status (or equivalent) that records the questions, the state to return to, and the answers when they arrive — plus a review of the existing step prompts so they raise questions through that surface rather than assuming a conversation.

Target plan-track flow in Linear (as described): a `request`-type issue sits in `in-spec` while a human fills its inputs, moves to `ready-to-plan`, the agent picks it up and runs groom via `claude -p`; open questions become comments on the request, the issue is reassigned to the user and moved to `awaiting-clarification`; on completion Claude creates a `plan`-type issue (project or issue, split TBD) with the plan body and milestones as sub-issues, cross-linked to the request, and moves it to `ready-for-review`; the user then moves it to `ready-for-development` (not auto-picked) or `selected-for-development` (auto-picked), from where develop runs, and downstream retro (separate task type) or code review (GitHub) follows.

## Clarifications and Decisions

- Scope of this plan: the **plan track only** (request issue to reviewed plan issue), shipped as a pilot; the full intent covers develop, retro, code review and eventually user playbooks, parked as sibling plans.
- Artifact truth: the **vault stays canonical** — plan directory, `index.md`, milestone files and run state; the Linear driver mirrors body, sub-issues and status outward and reads human input back.
- Tracker access: **prefer the API**, and likely wrapped as booping CLI subcommands — auth lives longer with an API token, and a CLI wrapper is the level at which the driver can be swapped. Research the API-vs-MCP tradeoff before locking it.
- Driver shape: **one config-selected driver** (`cli` and `linear`) contributing hook scripts on transitions plus conditional partials injected into step bodies at render; playbooks stay single-source. Hooks are wrapped as booping CLI calls and are **no-ops when the driver is `cli`**.
