# Request

**Request**

> Request — the remaining parts of the project-manager (adr/0028, adr/0027; the playbook itself is done in plan 202610152006_project-manager-playbook — read it and its develop-defaults.md): (1) autonomous-mode extras taken from backlog-run, generic only: a budget/usage gate before each milestone with configurable thresholds (pause with the next milestone recorded on the item, resume later via `booping run`), an optional time window, and batching of small items by size so tiny fixes skip grooming; read /home/anton/Dev/@A/notes/projects/_playbooks/backlog-run/ for the mechanics, keep code-computed what can be (value/0015). (2) setup: a project that points its specs tier at a repo directory gets it linked into the vault (adr/0001). (3) docs. Not in scope: tracker providers, intake channels, retiring user-level playbooks.

(Run directives — autonomous, worktree, snapshot policy — are in the session prompt and not repeated here.)

**Task type** — `feature`: a new capability of an autonomous project-manager run — it stops itself at a usage ceiling or outside a time window and resumes later, and it groups small items into one run. Not `bug`: nothing documented diverges; the manager simply has no ceiling yet (the parent plan's recorded departure from adr/0028). Not `refactoring`: new config keys, a new CLI surface and new run behaviour appear; the no-behaviour-change test fails.

**Problem** — The core project-manager (plan 202610152006) launches groom, develop and code-review through `booping run … --autonomous` with no usage ceiling, no time window and one run per item: an autonomous session can spend the whole subscription window, run at any hour, and pays a full groom for every one-line fix. backlog-run solved all three for its own task store; adr/0028 says the manager carries them over. After this plan an autonomous develop run checks a code-computed budget and window before each milestone group, pauses itself with the next milestone recorded where `booping status` and a later `booping run` find it, and the manager sizes items so the small ones share one run without grooming. Part (2) — linking a repo-pointed specs tier into the vault — already ships (`booping specs init --tier project`, run by `setup`, held by two e2e cases).

**Clarifications and Decisions** (autonomous run — each one a default, logged in `clarifications.md`)

- C1 — part (2) already shipped; no work beyond confirming the docs say so.
- C2 — scope: part (1) plus its docs, one plan.
