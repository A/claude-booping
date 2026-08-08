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
    path it lives at (`plans/{slug}/index.md`)
  - the split threshold, and the split offer draft-plan made with the user's answer, when the
    total passed it
  - the cross-review outcome — the findings with the deferrals recorded against them, or the
    note that no `core.cross_review_agent` is configured and the pass was skipped
  - whether the vault lives inside the repository being planned
  - when this presentation follows a change request: what the user asked for and what changed
    in the plan since the last summary
- **Value** — the run's **single review gate**, and the user's first read of the plan. One
  screen the user can approve from: the request and plan paths, the plan's status and sprint
  SP total, the milestones with what each delivers, and the outcome of every check the run
  performed, so approval is a decision on evidence rather than on trust. It is also the run's
  only exit — the plan reaches the `develop` playbook through this gate and no other — and the last point
  at which an oversized sprint is called out before development starts.
- **Output files** —
  - none — the approval screen is posted in chat: the request path, the plan path, the plan's
    status and SP total, a milestone table (id, summary, SP), a split recommendation
    (only when the total passes the threshold), a branch offer (only on a repo-local vault),
    the open questions, and the next step — approve, or jump straight in via
    `/playbook develop {plan path}`. The plan is complete before present runs;
    present summarises it and never edits it, and the sibling stubs of a recommended split are
    the user's to park. On approval the edge's hooks — not this step — stamp `reviewed_at` on
    `index.md` and run the `ready-for-dev` lifecycle script. On a loopback return the screen
    is re-posted whole, with what changed since the last round marked as changed.
- **Step report** — the approval screen itself. The approval ask is **prose in the message**,
  not a `## Questions:` entry and never an `AskUserQuestion` call — the driver's gate rule
  defers to a gate that calls for a prose ask. `## Questions:` carries only the other open
  questions and, on a repo-local vault, the branch offer.
- **Review gate** —
  - explicit user approval, asked for in prose — "looks good" counts, silence never does; the
    run moves to `ready-for-dev` on that word alone. This is the run's only review gate: the
    summary and the full plan are approved together.
  - a change request that touches the plan itself — architecture, scope, milestones, tasks or
    estimates — sends the run back to `drafting`. Present never absorbs a change itself
  - a recommended split is acknowledged, not required: the user may approve the plan whole and
    park no siblings

Two calls this step makes conservatively, recorded here so a later run does not re-litigate
them: the branch offer is an offer only — the step proposes the command and never runs git
itself — and on a repo-local vault the plan's earlier commits already landed on the current
branch (the lifecycle scripts commit from wave 1), so a branch taken here carries them
forward rather than removing them from where they are.

## Example screen

Posted in chat for `plans/20260731-10-05_rate-limit-public-api/`:

```markdown
Request: plans/20260731-10-05_rate-limit-public-api/request.md
Plan: plans/20260731-10-05_rate-limit-public-api/index.md
Status: awaiting-plan-review
SPs: 44

| # | Summary                                                                    | SP |
| - | -------------------------------------------------------------------------- | -- |
| 1 | token-bucket primitive, the two config keys, unit coverage                  | 8  |
| 2 | the limiter in the middleware chain, headers on every `/api/` response      | 12 |
| 3 | per-IP anonymous buckets, the fail-open path and its error logging          | 9  |
| 4 | staged rollout, dashboards, the operator runbook                            | 15 |

Checks: cross-review (`codex`) — 3 findings, 1 CRITICAL (missing `Retry-After` on the 429
path) folded into milestone 2; 2 NOTEs deferred and recorded in the risk register.

Split recommendation: 44 SP passes the 35 SP threshold. Recommended shape — two siblings,
each parked as a backlog stub with `split_from:` pointing at this plan and groomed in its
own run:

- **Authenticated rate limiting** (~29 SP) — milestones 1–3, the limiter and its quotas.
- **Rate-limit rollout** (~15 SP) — milestone 4, staged enablement and operations.

Approving the plan whole is also fine; the siblings are a recommendation, not a requirement.

Branch: the vault lives inside the repository, so plan commits land on the current branch.
Proposed: `git switch -c feat/rate-limit-public-api` — the same name the `develop` playbook
would pick, so it reuses the branch. Declining keeps the current branch.

## Questions:

1. Create `feat/rate-limit-public-api` for this plan, or stay on the current branch?

## Next Steps

Approve plan or jump into develop via:

/playbook develop plans/20260731-10-05_rate-limit-public-api/index.md
```

The approval ask follows the screen as prose, in the same message:

> The plan is ready for development — approve it, or tell me what to change. Approval moves
> the run to `ready-for-dev`.

Once the user has approved, the re-run records the approval and closes its questions:

```markdown
## Notes:

- decision: plan approved whole; the two siblings will be parked by the user, not this run
- decision: branch declined — the plan stays on the current branch

## Questions:
```
