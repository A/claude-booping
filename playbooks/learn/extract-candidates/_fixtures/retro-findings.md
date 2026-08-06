# Input — retro-findings

Extract self-learning candidates from the retrospective below. The project is `taskflow`, a Django + React task manager. Run date: **2026-08-06**.

## Lesson Target Space

Every lesson targets exactly one entry from the target space, written into its `targets:` frontmatter list. Entry forms — exact names only, no globs, no wildcards, no negation:

- `{playbook}` — the whole playbook
- `{playbook}/{step}` — one step of it
- `agent:{id}` — one agent

The target space, already fetched for every playbook this project runs:

### groom

Shape a feature, bug, or refactor into a specified, estimated, user-approved plan. Grooming owns the plan's content: scope, design, milestones, Definition of Done, and the verification steps a sprint must clear before it closes.

- Steps: `intake`, `research-codebase`, `research-web`, `draft-plan`, `cross-review`, `present`

### develop

Execute a groomed plan by delegating every task to a worker agent, one milestone group at a time, then hand off a verified sprint to retro. Owns git mechanics: the `provision` step selects and creates the working branch per the configured branch conventions, and the loop commits each milestone group.

- Steps: `intake`, `provision`, `develop-loop`, `verify`, `wrap-up`

### retro

Generate a project- and plan-specific sprint retrospective — mine session logs, gather the user's raw feedback, triage issues, then save it and hand off to learn. The `research-issues` step audits what happened during the sprint against what the plan and lessons prescribed.

- Steps: `intake`, `prepare`, `gather-feedback`, `research-issues`, `synthesize`, `save`

### learn

Turn retrospective findings into durable behavior changes routed to exactly one target each — extract atomic candidates, sweep for duplicates, confirm a review table with the user, write the accepted items, close the plans out.

- Steps: `intake`, `extract-candidates`, `dedup-sweep`, `review-table`, `write`, `transition`

Addressable agents: `agent:booping-developer` (the worker that implements milestone groups), `agent:booping-researcher` (heavy reads, returns summaries).

## Retrospective — sprint 20260801-notification-center

### What went wrong

1. The sprint shipped the notification center, but the user found two UX dead-ends within ten minutes of clicking through it. Nothing in the plan ever asked a human to try the feature before the sprint was declared done. The user's ask: from now on, plans should include a user-testing step that must pass before the develop run is allowed to close.

2. The sprint ran on a feature branch `feat/notification-center`, and merging it back at the end cost an hour of conflict resolution against two hotfixes that had landed on master meanwhile. The user decided: in this project, always commit straight to master; never create separate branches.

3. Lessons 0002 (atomic-migrations) and 0003 (fixture-factories) were both directly relevant to this sprint's work, yet the sprint's sessions never consulted either, and the retrospective only caught this by accident. The retrospective procedure should explicitly check which existing lessons were applicable to the sprint and flag the ones that went unused.

4. Two worker sessions stalled rediscovering project basics: that the API service starts with `just api`, and that the end-to-end tests only run against the compose stack via `just e2e`. Neither command is written down anywhere an agent reads.

5. The developer worker's mid-sprint reports were walls of prose — restated plan context, speculation about next steps — and the orchestrator had to scroll for the one thing it needed, the list of changed files. The developer agent must return only the changed-file list and a one-line outcome, nothing else.

6. The schema change in milestone 3 was applied straight to the shared dev database and broke two teammates' environments for an afternoon. Two things must change: every plan that touches the schema must carry a rollback note for each migration, and the developer worker must rehearse migrations against a database copy before applying them anywhere shared.
