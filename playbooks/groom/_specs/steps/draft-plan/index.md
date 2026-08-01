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
  context; the cross-review agent, when configured, is spawned by the runner from this step's
  instructions.
- **Needs** —
  - the settled design — the `## Design` section of `index.md`: the chosen architecture and why
    it won, the surface changes, the alternatives rejected, the trade-off calls the user made,
    and the risks with their mitigations
  - the confirmed framing — the restated problem, the task type, the scope boundaries and the
    user's answers to the scope-challenge questions
  - the blast radius — the `## Blast radius` section of `index.md`, with the prior art and
    conventions already in play
  - the plan-template catalogue — each template's name, description and the location to read its
    `# Plan Body` and `# Quality Checklist` from
  - the plan frontmatter shape — every key, its type and its default
  - the sizing scale — what each story-point value means — and how many consecutive milestones a
    development run bundles into one agent briefing, which bounds how large a milestone may be
  - whether the project configures a cross-review agent, and which agent it names
- **Value** — the design becomes an executable plan in the vault: milestones and tasks each
  carrying file paths, a testable DoD and a Verify, story points at every level, and a `summary:`
  line — written against a template chosen for the dominant surface and verified against that
  template's own checklist, so the plan passes or fails on published rules rather than on taste.
  The cross-review pass happens here, on the fresh draft, so the user's first read lands on a plan
  whose critical findings are already folded in.
- **Output files** —
  - `[UPDATED] plans/{slug}/plan.md` — the plan file intake created; this step writes its body
    and completes its frontmatter. Always `[UPDATED]`, never `[CREATED]` — the file exists from
    wave 1 and is never renamed or re-created.
    - pick the plan template whose name and description match the dominant surface of the work,
      read it, and write the body against its `# Plan Body` — section for section, in its order.
      When no template fits, a new one is authored in the project's own `plan_templates/` before
      drafting rather than improvising a shape.
    - every milestone carries a one-sentence goal, a `Verify` command or observable outcome, a
      task table with exact file paths and per-task story points, and a checkbox DoD per task;
      each milestone is executable in a fresh session with only the plan file as context
    - story points are set per task, summed per milestone and summed into the sprint total. The
      estimate is the honest one for the work as it stands — enforcing the re-decompose threshold
      and flagging a split are the sizing pass's job, and this step never inflates or splits a
      task to dodge them.
    - frontmatter keys this step owns: `sp` (the sprint total) and `summary` (one line of plain
      plan intent, ≤ ~120 chars, phrased as the visible outcome, not the engineering output).
      `title` and `type` are intake's and are only corrected if the design changed them; the H1
      matches `title`. `status` is never written here — the machine's edge hooks own it, as do the
      remaining date and outcome keys.
    - verify the finished draft against the template's `# Quality Checklist` before returning; an
      unsatisfied item is fixed, not reported as satisfied
    - cross-review, when the project's config carries a `cross_review` key: the finished draft is
      handed to the agent it names, exactly once per invocation, after the Quality-Checklist pass
      and before returning. This replaces the external-validator path booping's cross-validation
      doc describes — a playbook run never calls it. The reviewer's return contract is fixed here
      and is never renegotiated mid-run: findings only, one per line, each
      `- CRITICAL|RISK|NOTE: {finding} — {plan section}`, or the literal `no findings`, and
      nothing else — no preamble, no verdict line, no summary. With the key absent nothing is
      spawned, the plan is returned as drafted, and the drafting gate is vacuously satisfied.
    - every `CRITICAL` finding is folded into the plan, or recorded as a deferral; `RISK` is
      folded in when it does not reopen a call the user already settled, otherwise recorded;
      `NOTE` is folded in at the step's discretion and never blocks. A finding that reopens a
      settled design call is acted on nowhere in the plan — it travels as a note line so the
      runner can route it back to design.
    - deferred findings are recorded in a `## Risk register` section (added after
      `## Out of scope` when the chosen template defines none), one line per finding: the finding,
      its severity, and the reason it was deferred
  - no other file — the cross-review outcome travels in the step report, not in a file of its
    own
- **Step report** — `## Changed:` with the single plan entry annotated by the template chosen
  and the sprint total, and `## Notes:` carrying the milestone/SP breakdown, the
  Quality-Checklist verdict, and the cross-review outcome — findings by severity, what was folded
  in, what was deferred, or the line that no cross-review agent is configured.
- **Review gate** —
  - none — the user never reads the draft at this point; the sizing pass refines it first
  - the edge out of drafting is gated on the cross-review being run and every `CRITICAL` folded in
    or recorded as a deferral, which this step's return evidences

## Example artifact

`plans/20260731-rate-limit-public-api/plan.md`, at the end of draft-plan:

```markdown
---
title: Rate limit the public API
type: feature
status: in-spec
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

## Risk register

- **RISK, deferred** — the quota is not enforced for internal service-to-service calls, which
  bypass `AuthMiddleware`. Deferred: internal callers are trusted today and gating them changes
  the auth surface, which is out of this plan's scope.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Configuration` | document the two rate-limit settings and the fail-open policy | M2.2 |
```

## Return Format

```markdown
## Changed:

- [UPDATED] plans/20260731-rate-limit-public-api/plan.md — template `backend`, 12 SP

## Notes:

- milestones: M1 bucket primitive 5 SP, M2 middleware wiring 7 SP; sprint total 12 SP
- quality checklist (`backend`): all items pass
- cross-review (`codex`): 3 findings — 1 CRITICAL folded in (fail-open path was untested, now
  task 2.1 DoD), 1 RISK deferred to the risk register (internal callers bypass the limiter),
  1 NOTE folded in
```

With no cross-review agent configured, the last note is one line instead:

```markdown
## Notes:

- milestones: M1 bucket primitive 5 SP, M2 middleware wiring 7 SP; sprint total 12 SP
- quality checklist (`backend`): all items pass
- cross-review: no `cross_review` agent configured — not run
```
