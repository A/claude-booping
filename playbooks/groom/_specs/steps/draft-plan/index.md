---
status: done
reviewed_at: 20260731 19:52
fixtures_reviewed_at: 20260731 20:07
suite_reviewed_at: 20260731 20:34
---

[← index](../../index.md)

# draft-plan

## Contract

- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.
- **Needs** —
  - the confirmed framing brief — the restated problem, the task type, and the decisions the
    user settled at intake
  - the research findings this conversation already carries — the blast-radius map with its
    prior art and conventions, and the web findings with their sources
  - the plan-template catalogue — each template's name, description and the location to read its
    `# Plan Body` and `# Quality Checklist` from
  - the plan frontmatter shape — every key, its type and its default
  - the sizing scale — what each story-point value means — and the split threshold the sprint
    total is judged against
- **Value** — the design is settled with the user and becomes an executable plan, both in this
  one step: architecture, pattern choices, data / API / config surface changes and open
  trade-offs are iterated in conversation until aligned, then written as milestones and tasks
  each carrying file paths, a testable DoD and a Verify, story points at every level, and a
  `summary:` line — against a template chosen for the dominant surface and verified against
  that template's own checklist, so the plan passes or fails on published rules rather than on
  taste.
- **Output files** —
  - `[UPDATED] plans/{slug}/index.md` — the plan document intake created; this step writes its
    body and completes its frontmatter. Always `[UPDATED]`, never `[CREATED]` — the file exists
    from wave 1 and is never renamed or re-created.
    - the design is settled with the user first — architecture, surface changes, alternatives
      and trade-offs, iterated in conversation until aligned. Nothing is written before that
      alignment, and a design that needs blast radius or external practice the research pass
      missed sends the run back to `researching` instead of guessing.
    - pick the plan template whose name and description match the dominant surface of the work,
      read it, and write the body against its `# Plan Body` — section for section, in its order.
      When no template fits, a new one is authored in the project's own `plan_templates/` before
      drafting rather than improvising a shape.
    - every milestone carries a one-sentence goal, a `Verify` command or observable outcome, a
      task table with exact file paths and per-task story points, and a checkbox DoD per task;
      each milestone is executable in a fresh session with only the plan as context
    - story points are set per task, summed per milestone and summed into the sprint total. A
      total past the split threshold is offered as a split at a dependency seam — the first
      slice shippable on its own, each later one useless without it — keeping only the first
      slice that fits the threshold in this plan and parking the rest as sibling stubs to be
      groomed in their own runs; the user may decline and keep one plan. The estimate is the
      honest one for the work as it stands — a task is never inflated or split to dodge the
      threshold.
    - frontmatter keys this step owns: `sp` (the sprint total) and `summary` (one line of plain
      plan intent, ≤ ~120 chars, phrased as the visible outcome, not the engineering output).
      `title` and `type` are intake's and are only corrected if the design changed them; the H1
      matches `title`. `status` is never written here — the run machine owns it, and the
      lifecycle mirror `plan_status:` belongs to the edge scripts, as do the remaining date and
      outcome keys.
    - verify the finished draft against the template's `# Quality Checklist` before returning; an
      unsatisfied item is fixed, not reported as satisfied
  - no other file — the runner never edits files outside `plans/`, and the cross-review of the
    draft is the next step's job, not this one's
- **Step report** — `## Changed:` with the single plan entry annotated by the template chosen
  and the sprint total, and `## Notes:` carrying the milestone/SP breakdown, the
  Quality-Checklist verdict, and the split offer with the user's answer when the total passed
  the threshold.
- **Review gate** —
  - the in-conversation design alignment is the confirmation — no separate approval of the
    written draft is asked for; the user's first full read lands at `present`
  - the edge out of `drafting` moves to `cross-reviewing` once the body is written against the
    template's Plan Body, the Quality Checklist passed, and every call that is the user's is
    answered; a design that needs ground the research pass missed loops back to `researching`

## Example artifact

`plans/20260731-10-05_rate-limit-public-api/index.md`, at the end of draft-plan:

```markdown
---
status: drafting
plan_status: in-spec
title: Rate limit the public API
type: feature
sp: 12
split_from: null
created: 2026-07-31
planned: null
started: null
completed: null
retro: null
goal: null
summary: "Public API callers get a per-key request quota with standard rate-limit headers"
commit: null
---

# Rate limit the public API

## Context

**Current state** — every `/api/` route is served without admission control; one client's retry
loop saturates all four gunicorn workers.

**Motivation** — two incidents this quarter traced to a single caller; support has no lever short
of revoking the key.

**Scope** — per-key quotas on `/api/` routes with standard headers. Not: per-endpoint budgets,
plan tiers, or any quota-management UI.

## Decisions

- **Placement**: token bucket in the middleware chain (`api/middleware.py`) — the only layer every
  public route passes through, and it already resolves the authenticated client id.
- **Bucket store**: the Redis instance the cache already uses — buckets must be shared across
  workers; per-process counters multiply the effective limit by the worker count.
- **Failure policy**: fail open on a Redis error, logged at error level — a cache outage must not
  become an API outage.

## Architecture

`RateLimitMiddleware` is inserted after `AuthMiddleware` in `settings/base.py`, so `request.client`
is resolved before the bucket key is built. Consume and refill run as one Lua script against
`rl:{client}:{window}` so the check is atomic; a `redis.TimeoutError` is caught in the middleware
and the request is admitted.

## Milestones

### M1: Bucket primitive — 5 SP | pending

**Goal**: a tested token-bucket helper that consumes and refills a bucket in Redis atomically.

**Verify**: `just test tests/api/test_ratelimit.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Lua consume+refill script and its Python wrapper returning remaining/reset | `api/ratelimit/bucket.py`, `api/ratelimit/consume.lua` | 3 | pending |
| 1.2 | `RATE_LIMIT_PER_MINUTE` (120) and `RATE_LIMIT_BURST` (20) settings with defaults | `settings/base.py` | 2 | pending |

#### Task 1.1 DoD

- [ ] `Bucket.consume(client, cost=1)` returns `(allowed, remaining, reset_epoch)`.
- [ ] Refill is time-based, not request-based: a bucket idle for the full window is full again.
- [ ] Concurrent consumes from two connections never over-admit — covered by a test driving two
      clients against one key.
- [ ] `just test tests/api/test_ratelimit.py` passes.

### M2: Middleware wiring — 7 SP | pending

**Goal**: every `/api/` response carries the quota headers, and over-quota callers get a 429.

**Verify**: `just test tests/api/test_ratelimit_middleware.py && just lint`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `RateLimitMiddleware` — bucket check, fail-open on Redis error, 429 body + `Retry-After` | `api/middleware.py` | 4 | pending |
| 2.2 | Register after `AuthMiddleware`; anonymous callers keyed per IP at a quarter quota | `settings/base.py`, `api/middleware.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] `X-RateLimit-Remaining` and `X-RateLimit-Reset` are present on every `/api/` response.
- [ ] Over quota returns 429 with the standard error body and a `Retry-After` header.
- [ ] A raised `redis.TimeoutError` admits the request and logs at error level — asserted by test.

## Key Files Reference

| File | Role |
|------|------|
| `api/middleware.py` | the chain every public route passes through; new limiter lands here |
| `settings/base.py` | middleware order and the two new quota settings |

## Final Verification

- [ ] A key over quota receives 429 with `Retry-After`; the next window admits it again.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Per-endpoint budgets and plan-tier quotas.
- Any admin surface for inspecting or resetting a caller's bucket.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Configuration` | document the two rate-limit settings and the fail-open policy | M2.2 |
```

## Return Format

```markdown
## Changed:

- [UPDATED] plans/20260731-10-05_rate-limit-public-api/index.md — template `backend`, 12 SP

## Notes:

- milestones: M1 bucket primitive 5 SP, M2 middleware wiring 7 SP; sprint total 12 SP
- quality checklist (`backend`): all items pass
- sprint total under the split threshold — no split offered
```
