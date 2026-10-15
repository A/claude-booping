# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — part (2), linking a repo-pointed specs tier — answered

**Asked:** 2026-10-15 — intake

**Question:** setup should link a repo-directory specs tier into the vault (adr/0001). What is missing?

**Answer:**

Nothing in code or docs. `booping-python/src/booping/specs/init.py` `plan()` plans the `{vault}/specs` symlink whenever the project tier resolves outside the vault, `playbooks/setup/setup-project/` runs `booping specs init --tier project` (step 7), `src/specs/README.md`'s tier table and `documentation/specs.md` document it, and e2e cases `init-project-tier-outside-vault-creates-repo-specs-and-links-it` and `init-a-repo-tier-beside-an-in-repo-vault-is-linked` hold it. The parent plan reached the same finding (its C2). Part (2) needs no milestone.

## C2 — one plan or a split — answered

**Asked:** 2026-10-15 — intake

**Question:** Part (1) plus docs in one plan, or split?

**Answer:**

One plan — part (2) carries no work (C1) and part (3) is the docs of part (1). A split is reconsidered at draft-plan if the total passes 35 SP.

## C3 — where the usage reading comes from — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The gate needs the subscription's usage. Which source, computed by what?

**Answer:**

Code, never the model (value/0015). `booping budget read` takes the last `rate_limit_event` line of the newest `{vault}/runs/*.log` whose mtime is younger than `core.budget.max_age_s` — `booping run` already logs the child's `stream-json`, so every registered run refreshes it for free. No fresh log → it runs `core.budget.probe` (an argv; default a one-turn haiku `claude -p … --output-format stream-json --verbose`) and parses its stdout. The fields are `rate_limit_info.unifiedWindows.{five_hour,seven_day}.{utilization,resetsAt}`, checked live on Claude Code 2.1.280; the event is not in Claude Code's official docs, so a stream without it is "no reading", never "room to spend". The probe is a config argv, so a project on another harness points it at its own script printing the same line (value/0006).

## C4 — thresholds and verdicts — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Which thresholds, which verdicts?

**Options:**

- backlog-run's three verdicts (allow / pause / stop) with a nightly baseline and per-size estimates
- two verdicts (allow / pause), ceilings plus an optional per-run allowance

**Answer:**

Two verdicts. `core.budget`: `ceiling_5h_pct` (90), `ceiling_7d_pct` (85), `run_pct` (null = off; the 7-day points one registered run may spend, measured from a baseline the run record stores at launch), `max_age_s` (600), `window` (null), `probe`. A ceiling, a spent allowance, a closed window and a missing reading all mean the same thing to a run — end now, resume later — so one `pause` verdict carries a reason and a `resume_after`; backlog-run's `stop` only differed in what its night loop did next, which core has no equivalent of. Per-size cost estimates are dropped: they were hand-tuned guesses, and the gate runs before every milestone group anyway.

## C5 — when the gate applies — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A supervised user developing interactively should not be gated. Who decides, and how?

**Answer:**

Code. `booping budget gate` applies when it runs inside a registered run (`BOOPING_RUN_ID` in the environment, set by `booping run` on its child) or when `core.autonomy` is `autonomous`; otherwise it prints `allow — not gated: supervised session` and exits 0. Step prompts call it unconditionally.

## C6 — where the pause and the next milestone are recorded — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The request says "the next milestone recorded on the item". Item frontmatter, plan, or run record?

**Answer:**

The run record. A new run status `paused`, and on the record `paused_reason`, `resume_after` and `next_milestone` — the last computed by `booping budget gate` itself — inside a registered run a `pause` verdict stamps the run's record — from the plan's milestone files (the first one not `done`), never passed in by the model. The record already names the run's items and plan, so `booping status` shows the item, its plan and the next milestone together. Writing it on the item too would store the same fact twice (value/0003); the plan's milestone statuses stay the live truth and the record keeps where the run stopped as history (value/0004). Departure from the request's wording, flagged in the plan.

## C7 — how a run resumes — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What resumes a paused run, and does develop need a pause state?

**Answer:**

`booping run develop {plan} --autonomous` again — a new run record; develop's own resume reads the milestone frontier, and the paused group never left `pending` because the gate runs before the group's transitions. No new develop status. A paused record whose plan has a later run record counts as resumed and leaves `booping status`'s paused list (computed, no stamp). `booping status runs --detail` prints the resume command beside each paused run. `booping run … --autonomous` passes the gate before it allocates a record: a `pause` verdict prints it, writes nothing and exits 3.

## C8 — time window — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Window shape, timezone, and does a run get killed at the window's end?

**Answer:**

`core.budget.window: {start: "HH:MM", end: "HH:MM"}`, local time, an end before the start wrapping midnight; null = always open. Checked by the same gate (outside → `pause`, `resume_after` the next start), so at launch and before each milestone group. No kill at a grace deadline: a run overruns the window by at most one milestone group (≤ `core.sprint.max_sp`), and killing a worker mid-edit leaves a dirty tree for the next run to inherit — worse than the overrun.

## C9 — sizing and batching small items — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Who sizes, who batches, which sizes skip grooming?

**Answer:**

The manager sizes (judgement) and records it with `booping items size {id} {XS|S|M|L}` into a new item `size:` field; code batches. `core.project_manager_playbook.batch`: `sizes` (XS 1, S 2, M 5, L 13 SP), `direct` ([XS, S] — the sizes that skip grooming), `max_sp` (8). `booping items batch` packs the open items whose size is in `direct` and that wait on no question, in id order, greedily under `max_sp`, and prints one line per batch. One batch → one worker briefing, one commit per item, each item closed. An unsized item, or one of size M or L, takes the plan route as today. Batching plan-sized items into one groom (backlog-run's merged plan) stays out — the manager already grooms several items as one plan when the user framed them as one change.

## C10 — what the manager does with a pause — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** How does the project-manager react to a paused run or a closed gate?

**Answer:**

The report gains outcome `paused` (pointer: the run record); on a later turn a paused run whose `resume_after` has passed is relaunched with the command `booping status` prints; a direct batch passes `booping budget gate` before its briefing and on `pause` stops the turn. The report-line contract of the parent plan (C11 there) gains exactly that one outcome row.

## C11 — the timer — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** adr/0028 says a timer can start the autonomous manager. In scope?

**Answer:**

No. A timer is the machine's scheduler (systemd, cron, launchd) — not core (value/0005). `booping run … --autonomous` passing the gate at launch is what a timer calls; the docs show it with a generic cron line.

## C12 — no new eval suite — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The work step and develop-loop change; add evals?

**Answer:**

No new suite. The changed behaviour is code-computed and held by e2e cases; the prompt changes are one call each, held by the committed snapshot reports. The work step has no suite today and adding one is its own task.
