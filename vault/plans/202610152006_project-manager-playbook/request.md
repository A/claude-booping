# Request

**Request**

> Request — the core `project-manager` playbook itself (adr/0028; read it and adr/0024-0027, value/0015, core rules). Everything it stands on already exists in this branch: `booping items` (request/backlog/spec-gap items, verbatim text, source), `booping specs open-items`, `booping status` (computed report), `booping run groom|develop` (run registry, ack, lost runs), `booping correction add`, `booping defaults add`, `core.autonomy` (supervised | autonomous). Sources to fold in (read; carry the generic parts only): /home/anton/Dev/@A/notes/projects/hermes-pet/_playbooks/orchestrate/ and /home/anton/Dev/@A/notes/projects/_playbooks/backlog-run/ (+ backlog-manage).
> Build: (1) the playbook: on start it prints `booping status` (short) and acts from there; every user message is split into items (`booping items add`, verbatim) before work; the loop item → classify (tiny fix / plan / question / decision) → groom → develop via `booping run` → independent review → fixes → merge → report, with questions to the user filed on the item (sidecar), chat only pointing to the item; supervised mode stops at the plan review and before merge/deploy, autonomous mode auto-confirms and records defaults. (2) Autonomous extras from backlog-run, generic only: a budget/usage gate before each milestone (configurable thresholds; pause with the next milestone recorded, resume later), an optional time window, batching small items by size so tiny fixes skip grooming. (3) setup: when a project points its specs tier at a repo directory, link it into the vault (adr/0001). (4) Docs and evals per the repo's playbook conventions (smoke tier). Not core and out of scope: intake from messengers/ntfy, duplicate merging, tracker providers (a later plan), retiring the user-level orchestrate/backlog-run (owner decides).

(Run directives — autonomous, worktree, snapshot policy — are in the session prompt and not repeated here.)

**Task type** — `feature`: a new user-facing capability — a playbook the user talks to, plus the CLI it needs (questions on an item, a launched code-review run). Not `bug`: nothing observed diverges from documented behaviour — no manager exists to be wrong. Not `refactoring`: a new playbook, new subcommands and a new vault sidecar appear; the no-behaviour-change test fails.

**Problem** — Today the manager role is two user-level playbooks (`orchestrate`, `backlog-run` + `backlog-manage`) with their own task store, state machine and scattered state; requests asked only in chat are lost, finished runs go unnoticed, and every project copies the manager (adr/0028). Every primitive the core manager needs now exists — items, computed status, the run registry, corrections, defaults, autonomy — except two: an item cannot carry a question, and a review cannot be launched as a registered run. After this plan `/playbook project-manager` opens with `booping status`, files every request as an item verbatim, takes each item through classify → groom → develop → independent review → fixes → merge → report in the project's autonomy mode, and files the questions it cannot settle on the item.

**Clarifications and Decisions** (autonomous run — every one is a default, logged in `clarifications.md`)

- C1 — split: this plan is part (1) plus its docs and smoke evals (4); part (2), the autonomous extras, is parked as a sibling stub; part (3) already shipped.
- C2 — part (3): `booping specs init --tier project` already symlinks `{vault}/specs` to a repo-pointed tier and `setup` already runs it; covered by two e2e cases — no work.
- C3 — questions on an item: sidecar `open-items/questions/OI-NNNN.md` in the `docs/clarifications.md` format, written only by `booping items ask` / `booping items answer`; the answered test runs as code.
- C4 — an item with an open question shows as "waiting on you" in `booping status` (computed from the sidecar, no new item status).
- C5 — item lifecycle: a new `open → done` edge so a tiny fix, an answered question or a recorded decision closes without a plan.
- C6 — `booping run code-review PLAN [--autonomous]` registers the independent review like groom and develop.
- C7 — playbook shape: `on-start` → `intake` → `work`, inline steps, no `states:` of its own — items, plans and runs carry the state.
- C8 — mode routing: supervised grooms inline in the manager session (the user answers intake and approves the plan there) and develops/reviews through `booping run … --autonomous`; autonomous does every stage through `booping run … --autonomous`.
- C9 — merge: local, the sprint branch into the branch it was cut from, `--no-ff`, never pushed; push, deploy and release only through a project rule or runbook targeting `project-manager`. Supervised stops before it.
- C10 — one develop or code-review run per checkout at a time; groom runs may overlap.
- C11 — report line content locked in the plan (rule/0010).
