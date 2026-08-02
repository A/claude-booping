---
status: test-planning
reviewed_at: 20260802 08:55
---

[← index](../../index.md)

# cross-review

## Contract

- **Delegation** — detached: `detached: "{{ config.cross_review.agent }}"` resolves at render
  time (the playbook is `jinja: true`), so the agent the project's `cross_review` config names
  fetches and performs the step body itself; the runner never reads the instructions. With no
  `cross_review` agent configured the field renders empty, the step is **skipped** — nothing
  reviewer-flavoured enters the plan, no findings list, no severity vocabulary, no risk
  register — and the drafting-side gate is vacuously satisfied.
- **Needs** —
  - the written plan — the full document the reviewer reads end to end (frontmatter, context,
    decisions, architecture, milestones with task tables, DoDs and Verifies, out-of-scope), and
    the path it lives at: `plans/{slug}/index.md`, named in the agent's run-time context
  - the lessons in force — injected into the step body by the renderer; the Rules review
    dimension checks the plan against them by name
- **Value** — a second model's independent read of the finished draft, before the user's first
  read: execution gaps an AI executor would trip on, architectural blind spots specific to this
  plan, rule violations against the lessons, and plan-mechanics defects (a milestone not
  executable in a fresh session, a DoD or Verify naming nothing observable, a `Files` path that
  neither exists nor is created). Every finding references a specific part of the plan — no
  generic engineering advice. The runner disposes of the findings before advancing, so the
  criticals are folded in before present shows the plan to the user.
- **Output files** —
  - none — the step writes **nothing**. The findings block returned to the runner is the
    artifact; disposal edits to `index.md` belong to the runner, not this step: every
    `CRITICAL` folded into the plan or recorded as a deferral in `## Risk register`, `RISK`
    folded in unless it reopens a call the user already settled, `NOTE` at the runner's
    discretion. A finding that reopens a settled design call is folded in nowhere — it sends
    the run back to `drafting`.
- **Step report** — findings only, one per line, most severe first:
  `- CRITICAL|RISK|NOTE: {finding} — {plan section}`; when the plan is clean, the whole reply
  is the literal `no findings`. Nothing else — no preamble, no verdict line, no summary, no
  praise, no fixes applied. The contract is fixed here and never renegotiated mid-run.
  Severity meanings: `CRITICAL` — the plan's executor will fail, guess wrong, or write the
  wrong thing; `RISK` — it will likely hold, but a stated condition can break it; `NOTE` —
  worth folding in, blocks nothing.
- **Review gate** —
  - none on the step itself (`review_gate: null`) — the user never sees the findings raw;
    disposal is the runner's, and present reports the outcome
  - the `cross-reviewing → presenting` edge gates on every `CRITICAL` finding folded in or
    recorded as a deferral — vacuously satisfied when no `cross_review` agent is configured
    and the step was skipped

## Example artifact

The step's return for `plans/20260731-14-05_rate-limit-public-api/index.md` — the findings block is
the artifact; no file is written:

```markdown
- CRITICAL: task 2.1 catches `redis.TimeoutError` but no DoD item or test asserts the request
  is admitted and logged on that path — the executor can ship fail-closed unnoticed — M2 task
  table
- RISK: internal service-to-service calls bypass `AuthMiddleware`, so `request.client` is
  unset and the limiter is silently skipped for them — ## Architecture
- NOTE: `RATE_LIMIT_BURST` (20) appears in task 1.2 but not in the CLAUDE.md impact table —
  ## CLAUDE.md impact
```

A clean plan returns exactly:

```markdown
no findings
```

## Return Format

```markdown
- CRITICAL|RISK|NOTE: {finding} — {plan section}
```

One line per finding, most severe first, or the single literal line `no findings`. No other
sections, no prose around the block.
