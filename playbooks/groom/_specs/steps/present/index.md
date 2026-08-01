---
status: done
reviewed_at: 20260731 19:52
fixtures_reviewed_at: 20260731 20:07
suite_reviewed_at: 20260731 20:34
---

[← index](../../index.md)

# present

## Contract

- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.
- **Needs** —
  - the drafted plan — its approach, milestones, per-milestone and sprint SP totals, and the
    path it lives at
  - the `## Refinement` section of `index.md` — the split threshold, and the split candidate
    the refinement pass flagged with its sibling shape and rough sizes, or the note that
    nothing was flagged
  - the cross-review findings with the deferrals recorded against them, or the note that no
    cross-review agent is configured
  - the `## References` section of `index.md` — what was checked, what was corrected, what
    stayed unresolved
  - whether the vault lives inside the repository being planned
  - when this presentation follows a change request: what the user asked for and what changed
    in the plan since the last summary
- **Value** — the run's **single review gate**, and the user's first read of the plan. One
  screen the user can approve from, opened **human-first**: what the plan does and why, in
  prose a stakeholder reads, before any mechanics — then the milestones and their SP totals,
  the plan's path, and the outcome of every check the run performed, so approval is a decision
  on evidence rather than on trust. It is also the run's only exit — the plan reaches
  `/develop` through this gate and no other — and the last point at which an oversized sprint
  is called out before development starts.
- **Output files** —
  - `[UPDATED] plans/{slug}/index.md` — the `## Approval` section: `### Summary` (the
    human-targeted prose intro), `### Milestones` (a row per milestone with its SP and what it
    delivers), `### Totals` (sprint SP against the split threshold), `### Plan` (path and
    current lifecycle status), `### Checks` (refinement verdict, cross-review outcome with
    deferrals, reference verification), `### Split recommendation` (only when the total passes
    the threshold), `### Branch` (only on a repo-local vault) and `### Next` (what approval
    hands to `/develop`). The approval edge stamps `reviewed_at` on `index.md`. On a loopback
    return the section is rewritten in place, never appended to, and the subsections that
    changed since the last round are marked as changed.
  - nothing else — the plan is complete before present runs; present summarises it and never
    edits it, and the sibling stubs of a recommended split are the user's to park
- **Step report** — `## Changed:` list; `## Notes:` carrying the sprint SP total against the
  threshold, the check outcomes in one line each, and — on a repo-local vault where the user
  takes the branch — the proposed `git switch -c` command for the driver to run; `## Questions:`
  carrying the approval question ("ready for development, or want changes?") and, on a
  repo-local vault, the branch offer. The questions come back empty only once the user has
  approved.
- **Review gate** —
  - explicit user approval — "looks good" counts, silence never does; the run moves to
    `ready-for-dev` on that word alone. This is the run's only review gate: the summary and the
    full plan are approved together.
  - a change request loops the run back to the status that owns what it touches: milestones,
    tasks or estimates reopen the refinement pass; architecture or scope reopens the design.
    Present never absorbs a change itself
  - a recommended split is acknowledged, not required: the user may approve the plan whole and
    park no siblings

Two calls this step makes conservatively, recorded here so a later run does not re-litigate
them: the branch offer is an offer only — the step proposes the command and never runs git
itself — and on a repo-local vault the plan's earlier commits already landed on the current
branch (the lifecycle-mirror hooks commit from wave 1), so a branch taken here carries them
forward rather than removing them from where they are.

## Example artifact

`plans/20260731-rate-limit-public-api/index.md`, the `## Approval` section:

```markdown
## Approval

### Summary

Public API callers get a per-key request quota, so one client's retry loop can no longer
saturate the service for everyone else. A token-bucket limiter lands in the existing API
middleware chain, buckets held in the Redis instance the cache already uses, keyed on the
authenticated client id. It fails open on a Redis outage — an outage never takes the API down —
and anonymous callers get a per-IP quota at a quarter of the authenticated one.

### Milestones

| # | Milestone              | SP | Delivers                                                     |
| - | ---------------------- | -- | ------------------------------------------------------------ |
| 1 | Bucket + settings      | 8  | token-bucket primitive, the two config keys, unit coverage    |
| 2 | Middleware integration | 12 | the limiter in the chain, headers on every `/api/` response   |
| 3 | Anonymous quota        | 9  | per-IP buckets, the fail-open path and its error logging      |
| 4 | Rollout                | 15 | staged enablement, dashboards, the operator runbook           |

### Totals

44 SP — over the 35 SP split threshold; see the split recommendation below.

### Plan

`plans/20260731-rate-limit-public-api/plan.md` — currently `awaiting-plan-review`.

### Checks

- **Refinement** — two tasks were at 5 SP and were re-decomposed; every task now sits at 4 SP
  or under and the totals above are re-summed.
- **Cross-review** — 3 findings, 1 CRITICAL (missing `Retry-After` on the 429 path) folded into
  milestone 2; 2 NOTEs deferred and recorded in the plan's risk register.
- **References** — 6 external references checked; the `redis-py` floor was corrected from 4.6 to
  5.0 (the timeout argument the design relies on landed in 5.0). Nothing unresolved.

### Split recommendation

44 SP passes the threshold. Recommended shape — two siblings, each parked as a backlog stub with
`split_from:` pointing at this plan and groomed in its own run:

- **Authenticated rate limiting** (~29 SP) — milestones 1–3, the limiter and its quotas.
- **Rate-limit rollout** (~15 SP) — milestone 4, staged enablement and operations.

Approving the plan whole is also fine; the siblings are a recommendation, not a requirement.

### Branch

The vault lives inside the repository, so plan commits land on the current branch. Proposed:
`git switch -c feat/rate-limit-public-api` — the same name `/develop` would pick, so it reuses
the branch. Declining keeps the current branch.

### Next

On approval the run moves to `ready-for-dev` and `/develop` claims the plan from there. Change
requests loop back: milestones or estimates to the refinement pass, architecture or scope to the
design.
```

## Return Format

```markdown
## Changed:

- [UPDATED] plans/20260731-rate-limit-public-api/index.md — approval summary

## Notes:

- 44 SP across 4 milestones — over the 35 SP threshold, split into 2 siblings recommended
- cross-review: 1 CRITICAL folded in, 2 NOTEs deferred to the risk register
- references: 6 checked, 1 corrected (`redis-py` floor 4.6 → 5.0), none unresolved
- proposed on branch accept: `git switch -c feat/rate-limit-public-api`

## Questions:

1. Ready for development, or want changes? Approval moves the plan to `ready-for-dev`.
2. Create `feat/rate-limit-public-api` for this plan, or stay on the current branch?
```

Once the user has approved, the re-run records the approval and closes its questions:

```markdown
## Changed:

- [UPDATED] plans/20260731-rate-limit-public-api/index.md — approval recorded

## Notes:

- decision: plan approved whole; the two siblings will be parked by the user, not this run
- decision: branch declined — the plan stays on the current branch

## Questions:
```
