# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — request split — answered

**Asked:** 2026-10-15 — intake

**Question:** The request holds four parts. One plan, or split?

**Options:**

- One plan for all four parts
- The playbook with its docs and evals now; the autonomous extras parked

**Answer:**

Split. This plan carries part (1) — the playbook and the two CLI gaps it needs — plus its docs and smoke evals, part (4). Part (2) — the budget/usage gate before each milestone with pause and resume, the time window, size batching — is a parked sibling stub: it needs a usage probe in code (backlog-run reads Claude Code's undocumented, version-pinned `rate_limit_event` stream line) and a per-milestone hook in develop, its own design. Grooming both together would pass the 35 SP split threshold, and the extras are useless without the manager they gate.

## C2 — setup linking a repo-pointed specs tier — answered

**Asked:** 2026-10-15 — research-codebase

**Question:** Part (3) asks setup to link a repo-directory specs tier into the vault. What is missing?

**Answer:**

Nothing. `booping-python/src/booping/specs/init.py` `plan()` plans a `{vault}/specs` symlink when the project tier resolves outside the vault, `playbooks/setup/setup-project/` runs `booping specs init --tier project`, and two e2e cases hold it (`init-project-tier-outside-vault-creates-repo-specs-and-links-it`, `init-a-repo-tier-beside-an-in-repo-vault-is-linked`). Part (3) is dropped from this plan as already shipped.

## C3 — where a question on an item lives — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0028 puts questions on the item as a sidecar. Which file, which format, which writer?

**Options:**

- `open-items/OI-NNNN.questions.md` beside the item
- `open-items/questions/OI-NNNN.md`

**Answer:**

`open-items/questions/OI-NNNN.md` — a sibling file beside the item would match the store's `open-items/*.md` item glob. Format: `docs/clarifications.md` (the `C{n}` H2s with `open`/`answered`, the answered test) — one question format across plans and items. Writers: `booping items ask` appends an open question, `booping items answer` writes the answer and flips the marker. The answered test runs as code (value/0015).

## C4 — how an item waiting on the owner shows — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A new item status (`waiting`) or computed from the sidecar?

**Answer:**

Computed. `booping status`'s items line gains a `{n} waiting on you` segment and its detail a table of those items; the item's status machine is untouched by questions. adr/0028 — status is computed, never stored.

## C5 — closing an item without a plan — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The `open_item` machine closes only `planned` items as `done`. How does a tiny fix, an answered question or a recorded decision close?

**Answer:**

A new `open → done` edge, taken by `booping items close` on an open item, with the same `closed_at` hook as `planned → done`.

## C6 — launching the independent review — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** How does the manager run the review after develop?

**Answer:**

`booping run code-review PLAN [--autonomous]` — the run registry gains the code-review playbook, one plan target like develop. adr/0028: every launched run is registered.

## C7 — playbook shape — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A state machine of its own, a per-item subgraph, or a few inline steps?

**Answer:**

Three inline steps — `on-start` → `intake` → `work` — and no `states:`. The manager is session-long and event-driven (messages arrive, runs finish); the wave model fits only its opening. Items, plans and runs already carry every state the manager reads. `intake` and `work` repeat for every later message per the preamble.

## C8 — what each mode runs where — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A headless supervised groom cannot ask its scope questions or wait at plan approval. How does supervised mode groom?

**Answer:**

Supervised drives `/playbook groom` inline in the manager session, so the user answers intake and approves the plan there; develop and code-review go through `booping run … --autonomous` (value/0007: an approved plan runs to the end). Autonomous launches all three through `booping run … --autonomous`. Supervised stops again before merge.

## C9 — merge — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What does "merge" mean in the core, where pushing, PRs and deploys are host- and project-specific?

**Answer:**

Local only: the plan's sprint branch merged `--no-ff` into the branch it was cut from; a plan developed on the current branch has nothing to merge. Never pushed. Push, PR, deploy and release happen only when a project rule or runbook targeting `project-manager` says so (value/0005).

## C10 — concurrency — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** How many runs at once?

**Answer:**

At most one develop or code-review run per checkout at a time — both write the working tree; more items queue. Groom runs touch only the vault and may overlap.

## C11 — report content — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What does the manager's report say per item?

**Answer:**

One line per item: `{id} {title} — {outcome} — {pointer}`; outcome one of `done`, `planned`, `running`, `waiting on you`, `dropped`; pointer the plan path, the run record, the questions sidecar or the closing commit. Locked in the plan's I/O contract.

## C12 — plan approval — answered

**Asked:** 2026-10-15 — present

**Question:** The plan is ready for development — approve, or say what to change?

**Answer:**

Approved by the autonomous run (the owner was unavailable; the session directive auto-confirms review gates). Cross-review (codex) returned one RISK and six NOTEs: the RISK (how the one-run-per-checkout queue is checked) and four NOTEs (branch merge target, groom batching, which items a blocker lands on, where review findings live) were folded into M05; two NOTEs (message splitting and item titles are judgement) were not — that judgement is the model's job by value/0015.
