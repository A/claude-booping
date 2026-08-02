---
status: done
agents:
  step-prompt: a53ba5fadff536c08
  step-spec: a9c376b2d7be4a869
  llm-tests: ad9e034ac1b4492d1
reviewed_at: 20260802 09:48
fixtures_reviewed_at: 20260802 09:52
suite_reviewed_at: 20260802 09:58
---

[← index](../../index.md)

# develop-loop

## Contract

- **Needs** —
  - the confirmed milestone groups and the order they run in
  - each milestone's tasks with their related files, DoD checkboxes and the milestone's
    `Verify` command
  - the project conventions the worker must follow
  - the plan's scope boundary
  - the worker's report and the diff it left behind
  - the commit-message convention
  - the fix attempts already spent on a failing issue
- **Value** — the sprint's code is actually written, group by group, without the runner
  touching application code: one briefing per group, one worker at a time on the sprint
  branch, and every group closed against its own milestones' plan-authored `Verify` — the
  project's own guardrails all wait for `verify` at sprint end. Each closed group leaves the
  truth on disk — DoD checkboxes, task rows and milestone statuses flipped in the plan, one
  commit per milestone in the repo — so a resume reads the frontier off the plan and the
  branch rather than off conversation.
- **Output files** —
  - code changes in the attached repo on the sprint branch, one commit per milestone per the
    commit-message convention — written by the worker, never by the runner
    - provision fires the `ready-for-dev → in-progress` edge at its end, so the run is
      already at `in-progress` on entry; the step keeps only an idempotent guard — on a resume
      that still finds the plan at `ready-for-dev`, take the edge before the first delegation,
      otherwise never touch it
    - per group: open one tracking task, compose **one** briefing covering every milestone in
      it — per-milestone request, related files, DoD and Verify, plus the project conventions
      and the plan's scope boundary — and delegate it to the worker agent the preamble's
      available-agents block names. Always delegate, even for a one-line change. Never two
      workers on one sprint branch: the next group starts only after the current one closed.
    - briefings carry no lesson paths — the worker gets its lesson context through its own
      extension file, not through the briefing
    - on the worker's report, per milestone: verify the output against the milestone's DoD and
      the resulting diff, run the milestone's plan-authored `Verify` command, then commit
    - a failing `Verify` or a wrong diff goes back to the worker as a fix briefing; the attempt
      is recorded under the milestone in the plan. After two recorded attempts on the same
      issue the blocker is unrecoverable: ask the user to approve the abort and take the
      `in-progress → fail` edge. No scope additions and no runner-authored fix at any point.
  - `[UPDATED] plans/{slug}/index.md` — bookkeeping only, as each milestone closes: task DoD
    `- [ ]` → `- [x]`, each task row `pending` → `done`, the milestone status → `done`, plus
    the short blocked-attempt note when a fix was needed. Nothing else in the plan is edited
    here — no new milestones, no rewritten tasks, and never `status:`, which the run machine
    owns.
  - the plan committed to the vault once per closed group with
    `booping vault-commit in-progress <plan-path>`; the playbook ships no `_scripts/`, so the
    vault commit is the step's to call. `sprints.md` is not re-rendered by this playbook.
  - a per-group summary posted in chat — what shipped, anything deferred — before the next
    group starts
- **Harness return** — `## Changed:` with the plan entry annotated by groups closed and
  milestones flipped, and one line per milestone commit; `## Notes:`
  carrying the per-group shipped/deferred summary, the `Verify` verdict per milestone, and any
  fix attempts spent.
- **Review gate** —
  - none — the per-group report is informational and never stops the run; the sprint's exit is
    decided by `verify`'s guardrails
  - the abort is not a gate but the failure exit: user-approved, after two attempts on the
    same issue are documented in the plan
- **Delegation** — assisted: the runner renders the step, owns the loop, the verification and
  all plan bookkeeping; the coding work is what leaves the conversation — one worker agent per
  group, spawned from inside the step, exactly as the skill does today.

## Example artifact

`plans/20260731-10-05_rate-limit-public-api/index.md` after group 1 (M1) closed — the milestone
slice as the step leaves it:

```markdown
### M1: Bucket primitive — 5 SP | done

**Goal**: a tested token-bucket helper that consumes and refills a bucket in Redis atomically.

**Verify**: `just test tests/api/test_ratelimit.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Lua consume+refill script and its Python wrapper returning remaining/reset | `api/ratelimit/bucket.py`, `api/ratelimit/consume.lua` | 3 | done |
| 1.2 | `RATE_LIMIT_PER_MINUTE` (120) and `RATE_LIMIT_BURST` (20) settings with defaults | `settings/base.py` | 2 | done |

#### Task 1.1 DoD

- [x] `Bucket.consume(client, cost=1)` returns `(allowed, remaining, reset_epoch)`.
- [x] Refill is time-based, not request-based: a bucket idle for the full window is full again.
- [x] Concurrent consumes from two connections never over-admit — covered by a test driving two
      clients against one key.
- [x] `just test tests/api/test_ratelimit.py` passes.
```

And the chat report closing that group:

```markdown
**Group 1 — M1 Bucket primitive (5 SP): done.** The Lua consume+refill script and its Python
wrapper landed with the two quota settings; `just test tests/api/test_ratelimit.py` is green and
the milestone is committed as `feat(api): add redis token bucket primitive`. Nothing deferred.
Starting group 2 (M2 Middleware wiring).
```

A milestone that needed a fix carries the attempt note the abort gate reads:

```markdown
**Blocked (1/2)**: `just test tests/api/test_ratelimit.py` failed on concurrent over-admission;
re-briefed the worker to move the check into the Lua script.
```

## Return Format

```markdown
## Changed:

- [UPDATED] plans/20260731-10-05_rate-limit-public-api/index.md — 2 groups closed, M1–M2 done
- repo commits: `feat(api): add redis token bucket primitive`, `feat(api): wire rate limit middleware`

## Notes:

- group 1 (M1, 5 SP): bucket primitive shipped; `just test tests/api/test_ratelimit.py` green
- group 2 (M2, 7 SP): middleware + registration shipped; `just test tests/api/test_ratelimit_middleware.py && just lint` green; 1 fix attempt spent on the fail-open path
- nothing deferred; project-wide guardrails not run here — they belong to verify
```
