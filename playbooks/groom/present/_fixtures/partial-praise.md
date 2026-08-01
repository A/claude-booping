# Input — partial-praise

Round one has been presented and the user has replied. Handle the reply and put the run's state
to the harness.

## Run-time context

- project: `northwind-api` — a Django REST API served by gunicorn, with a Redis instance already
  in use as the cache backend
- run slug: `20260731-rate-limit-public-api`
- run workdir: the plan directory `plans/20260731-rate-limit-public-api/`, relative to the
  current working directory
- the current working directory **is the project vault**, and the vault lives **inside the
  repository being planned**: the repo's `.booping` marker carries `vault_path: booping`, so the
  vault is the repo's `booping/` directory and every commit the run has made so far landed on
  the branch the repository is currently on
- the project's branch convention for a `feature` plan is the `feat/` prefix; the name `/develop`
  would pick for this plan is `feat/rate-limit-public-api`
- sizing thresholds in force this run: split threshold **35 SP**, re-decompose threshold **5 SP**
- run start: **2026-07-31 14:02 UTC**; round one was presented at **18:04 UTC**; this pass runs
  at **18:22 UTC**

## Inputs

- the drafted plan — `plans/20260731-rate-limit-public-api/plan.md`, on disk; unchanged since
  round one
- the run's `index.md` — `plans/20260731-rate-limit-public-api/index.md`, on disk: `## Framing`,
  `## Blast radius`, the confirmed `## Design`, the `## Refinement` verdict with the split
  candidate the sizing pass flagged, and the `## References` results
- the cross-review findings and their deferrals, as `draft-plan` returned them:

  > - cross-review (`codex`): 3 findings — 1 CRITICAL folded into milestone 2 (the 429 path
  >   returned no `Retry-After`, so callers could not back off deterministically; now task 2.1's
  >   DoD), 2 NOTEs deferred and recorded in the plan's risk register (no machine-readable quota
  >   window in the 429 body; bucket keys not namespaced by API version)

- round one's summary — the `## Approval` section of that same `index.md`, written at
  18:04and the summary the user is replying to
- the user's reply to round one, in full — they said nothing else, and nothing about the plan as
  a whole, the split or the branch:

  > yeah, Redis is the right call for the buckets

## Context files

<file path="plans/20260731-rate-limit-public-api/index.md">
---
status: awaiting-approval
---
# Rate limit the public API

## Framing

### Request

> Public API callers get a per-key request quota with standard rate-limit headers

### Restated problem

**Current state** — every `/api/` route is served without admission control; one client's retry
loop saturates all four gunicorn workers and the rest of the callers queue behind it.

**Motivation** — two incidents this quarter traced to a single caller. Support's only lever today
is revoking the client's key outright.

**Scope** — per-client quotas on `/api/` routes with standard rate-limit headers, a per-IP quota
for anonymous callers, and a staged rollout with the operational surface to run it. Not:
per-endpoint budgets, plan tiers, or any quota-management UI.

### Task type

`feature` — classified at intake and unchanged since.

### Scope boundaries

**In scope**

- M1: Bucket + settings
- M2: Middleware integration
- M3: Anonymous quota
- M4: Rollout

**Out of scope**

- Per-endpoint budgets and plan-tier quotas.
- Any admin surface for inspecting or resetting a caller's bucket.

### Web research

Not requested — the request asks for no deep web research, and the user asked for none
when the scope questions came back.

### Scope challenge

- [x] Anything the request pulls in that it does not state? — answered at intake;
      the boundaries above are what the answers settled.

## Blast radius

### Touched surfaces

| Surface | Where | Why it moves | Risk |
| --- | --- | --- | --- |
| middleware.py | `api/middleware.py` | the chain every public route passes through; the limiter lands here | medium — the plan changes what it does |
| base.py | `settings/base.py` | middleware order and the quota settings | medium — the plan changes what it does |
|  | `api/ratelimit/` | the bucket primitive, its Lua script, key derivation and metrics | medium — the plan changes what it does |
|  | `ops/grafana/dashboards/` | provisioned dashboards | medium — the plan changes what it does |

### Prior art

- `api/middleware.py` — the closest existing shape this work follows

### Conventions in play

- the project's own lint / typecheck / test gate runs on every change under these
  surfaces, and the plan's Final Verification restates it

### Unknowns for design

- none left open: the design below settles every call the map raised


## Design

### Approach

A token-bucket limiter in the existing API middleware chain, with the buckets held in the Redis
instance the cache already uses and keyed on the authenticated client id the middleware resolves.
Consume and refill run as one Lua script so the check is atomic across gunicorn workers. The
limiter fails open on a Redis outage, logged at error level; anonymous callers get a per-IP quota
at a quarter of the authenticated one.

### Surface changes

- **Middleware** — `RateLimitMiddleware` after `AuthMiddleware`, so the client id is resolved
  before the bucket key is built.
- **Config** — `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_BURST`, `RATE_LIMIT_ANON_DIVISOR` and the
  staged `RATE_LIMIT_ENFORCE` flag.
- **HTTP** — `X-RateLimit-Remaining` and `X-RateLimit-Reset` on every `/api/` response; 429 with
  `Retry-After` over quota.
- **Dependencies** — the `redis` client, reusing the cache's connection pool rather than opening
  a second one.
- **Operations** — throttle/admit counters on the existing metrics scrape, a provisioned
  dashboard, and a runbook.

### Alternatives

- **Per-worker in-process counters** — rejected: four workers multiply the effective limit by
  four, and the count resets on every deploy.
- **A limiter at the reverse proxy** — rejected: the proxy cannot resolve the authenticated
  client id, so quotas could only be per IP, which is the wrong unit for API keys behind NAT.
- **A fixed-window counter instead of a token bucket** — rejected: the window boundary admits a
  double burst, which is the exact failure the incidents showed.

### Trade-offs

- **Failure policy: fail open or fail closed** — failing closed turns a cache outage into an API
  outage; failing open lets a caller exceed quota for the duration of the outage. — **Settled:**
  fail open, logged at error level, with the outage rate on the dashboard.
- **Anonymous quota unit: per IP or none at all** — per IP penalises callers behind a shared
  NAT; leaving anonymous traffic unlimited leaves the incident path open. — **Settled:** per IP
  at a quarter quota, read from the trusted proxy header.
- **Rollout: enforce immediately or observe first** — observing first delays the protection but
  shows the real distribution before anyone is rejected. — **Settled:** staged, observe first per
  environment.

### Risks

- A forged forwarded header would let an anonymous caller widen its own quota — mitigated by
  reading the IP only from the trusted proxy hop.
- The Lua script runs on every public request and is on the latency path — mitigated by keeping
  it to one round trip and by the fail-open timeout.
- Staged rollout leaves observe-mode traffic uncapped for as long as the stage lasts — mitigated
  by the per-environment flag and the dashboard that shows what enforcement would have rejected.

## Refinement

Refined — 2 tasks sat at or over the 5 SP re-decompose threshold; the sprint totals 44 SP, past
the 35 SP split threshold, so a split candidate is flagged.

### Re-decomposed

| Was | SP | Became | SP |
| --- | --- | --- | --- |
| M2 · Middleware with fail-open handling | 6 | M2 · `RateLimitMiddleware` — bucket check, 429 body and `Retry-After` | 4 |
| | | M2 · Fail-open path on `redis.TimeoutError` with error-level logging | 3 |
| M4 · Dashboards and runbook | 5 | M4 · Grafana dashboard provisioned from the repo | 4 |
| | | M4 · Operator runbook — what to watch, how to widen, how to disable | 3 |

Each half stands alone — its own DoD, its own Verify. The fail-open path ships with its own test
rather than riding on the middleware task's.

### Totals

| Milestone | Before | After |
| --- | --- | --- |
| M1 · Bucket + settings | 8 | 8 |
| M2 · Middleware integration | 11 | 12 |
| M3 · Anonymous quota | 9 | 9 |
| M4 · Rollout | 14 | 15 |
| **Sprint** | **42** | **44** |

Both splits landed on a pair costing one point more than the task they replaced — the separated
halves each carry their own verification. The largest surviving task is 4 SP.

### Split candidate

The seam sits between M3 and M4: M1–M3 make the limiter work and enforce quotas for both caller
kinds; M4 is the staged rollout and the operational surface around it. The first half is
shippable behind the observe flag without the second; the second is meaningless without the
first.

- **Primary** — Authenticated rate limiting — M1–M3, 29 SP.
- **Sibling** — Rate-limit rollout — M4, 15 SP; parked as a `backlog` stub with `split_from:`
  pointing at the primary, groomed in its own run once the primary merges.

## References

Corrected — 6 references checked, 1 corrected, 0 unverifiable.

### Checked

| Reference | Named in | Plan claims | Upstream | Verdict | Source (checked 20260731) |
| --------- | -------- | ----------- | -------- | ------- | ------------------------- |
| `redis` (PyPI) floor | M1.2 · "pin the client" | `redis>=4.6` | the `timeout=` argument the design's fail-open path passes landed in 5.0 | corrected | https://pypi.org/project/redis/ |
| `Retry-After` with 429 | M2.1 · 429 response | required alongside 429 | RFC 6585 §4 defines exactly this pairing | ok | https://www.rfc-editor.org/rfc/rfc6585 |
| cache backend path | M1.2 · limiter connection | `django.core.cache.backends.redis.RedisCache` | built in since Django 4.0 | ok | https://docs.djangoproject.com/en/stable/topics/cache/ |
| `X-RateLimit-*` header names | M2.2 · response headers | `X-RateLimit-Remaining`, `X-RateLimit-Reset` | the conventional pair, matching the names the API gateway already emits on its own throttles | ok | https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-ratelimit-headers |
| Redis Lua atomicity | Architecture · consume+refill | one `EVAL` runs to completion without interleaving | scripts are atomic for their whole execution | ok | https://redis.io/docs/latest/commands/eval/ |
| Grafana dashboard provisioning path | M4.3 · `ops/grafana/dashboards/` | provisioned from a repo directory | the provisioning directory layout is as the plan names it | ok | https://grafana.com/docs/grafana/latest/administration/provisioning/ |

### Corrections

- **`redis` floor** — M1, task 1.2: `redis>=4.6` → `redis>=5.0`. The fail-open path passes a
  connection `timeout=`, which the 4.6 line does not accept; it landed in 5.0.
  https://pypi.org/project/redis/ (checked 20260731)

## Approval

### Summary

A token-bucket limiter in the existing API middleware chain, buckets held in the Redis instance
the cache already uses, keyed on the authenticated client id the middleware resolves. Fails open
on a Redis outage, logged at error level; anonymous callers get a per-IP quota at a quarter of
the authenticated one.

### Milestones

| # | Milestone              | SP | Delivers                                                    |
| - | ---------------------- | -- | ----------------------------------------------------------- |
| 1 | Bucket + settings      | 8  | token-bucket primitive, the two config keys, unit coverage   |
| 2 | Middleware integration | 12 | the limiter in the chain, headers on every `/api/` response  |
| 3 | Anonymous quota        | 9  | per-IP buckets, the fail-open path and its error logging     |
| 4 | Rollout                | 15 | staged enablement, dashboards, the operator runbook          |

### Totals

44 SP — over the 35 SP split threshold; see the split recommendation below.

### Plan

`plans/20260731-rate-limit-public-api/plan.md` — currently `awaiting-plan-review`.

### Checks

- **Refinement** — two tasks were at 5 SP or over and were re-decomposed; every task now sits
  at 4 SP or under and the totals above are re-summed.
- **Cross-review** — 3 findings, 1 CRITICAL (missing `Retry-After` on the 429 path) folded into
  milestone 2; 2 NOTEs deferred and recorded in the plan's risk register.
- **References** — 6 external references checked; the `redis` floor was corrected from 4.6 to 5.0
  (the timeout argument the design relies on landed in 5.0). Nothing unresolved.

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
requests loop back: milestones, tasks or estimates to the refinement pass, architecture or
scope to the design.
</file>

<file path="plans/20260731-rate-limit-public-api/plan.md">
---
title: Rate limit the public API
type: feature
status: awaiting-plan-review
sp: 44
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
loop saturates all four gunicorn workers and the rest of the callers queue behind it.

**Motivation** — two incidents this quarter traced to a single caller. Support's only lever today
is revoking the client's key outright.

**Scope** — per-client quotas on `/api/` routes with standard rate-limit headers, a per-IP quota
for anonymous callers, and a staged rollout with the operational surface to run it. Not:
per-endpoint budgets, plan tiers, or any quota-management UI.

## Decisions

- **Placement**: a token bucket in the middleware chain (`api/middleware.py`) — the only layer
  every public route passes through, and it already resolves the authenticated client id.
- **Bucket store**: the Redis instance the cache already uses — buckets must be shared across
  workers; per-process counters multiply the effective limit by the worker count.
- **Failure policy**: fail open on a Redis error, logged at error level — a cache outage must not
  become an API outage.
- **Anonymous callers**: keyed per IP at a quarter of the authenticated quota.

## Architecture

`RateLimitMiddleware` is inserted after `AuthMiddleware` in `settings/base.py`, so
`request.client` is resolved before the bucket key is built. Consume and refill run as one Lua
script against `rl:{client}:{window}` so the check is atomic; a `redis.TimeoutError` is caught in
the middleware and the request is admitted.

## Milestones

### M1: Bucket + settings — 8 SP | pending

**Goal**: a tested token-bucket primitive that consumes and refills a bucket in Redis atomically,
with the two quota settings behind it.

**Verify**: `just test tests/api/test_ratelimit.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Lua consume+refill script and its Python wrapper returning remaining/reset | `api/ratelimit/bucket.py`, `api/ratelimit/consume.lua` | 3 | pending |
| 1.2 | Pin `redis>=5.0` and point the limiter at the existing cache connection | `pyproject.toml`, `api/ratelimit/client.py` | 2 | pending |
| 1.3 | `RATE_LIMIT_PER_MINUTE` (120) and `RATE_LIMIT_BURST` (20) settings with defaults | `settings/base.py` | 3 | pending |

#### Task 1.1 DoD

- [ ] `Bucket.consume(client, cost=1)` returns `(allowed, remaining, reset_epoch)`.
- [ ] Refill is time-based: a bucket idle for the full window is full again.
- [ ] Two concurrent consumers on one key never over-admit — covered by test.

#### Task 1.2 DoD

- [ ] `redis>=5.0` is pinned and `uv sync` resolves it.
- [ ] The limiter reuses the cache's connection pool rather than opening its own.

#### Task 1.3 DoD

- [ ] Both settings read from the environment with the documented defaults.
- [ ] An invalid value fails at startup rather than at first request.

### M2: Middleware integration — 12 SP | pending

**Goal**: every `/api/` response carries the quota headers, over-quota callers get a 429 they can
back off from, and a Redis outage admits traffic instead of dropping it.

**Verify**: `just test tests/api/test_ratelimit_middleware.py && just lint`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `RateLimitMiddleware` — bucket check, 429 body and `Retry-After` | `api/middleware.py` | 4 | pending |
| 2.2 | Register after `AuthMiddleware`; emit `X-RateLimit-*` on every `/api/` response | `settings/base.py`, `api/middleware.py` | 3 | pending |
| 2.3 | Fail-open path on `redis.TimeoutError` with error-level logging | `api/middleware.py` | 3 | pending |
| 2.4 | Integration tests across the admitted, throttled and outage paths | `tests/api/test_ratelimit_middleware.py` | 2 | pending |

#### Task 2.1 DoD

- [ ] Over quota returns 429 with the standard error body.
- [ ] Every 429 carries a `Retry-After` header whose value matches the bucket's reset — asserted
      by test.

#### Task 2.2 DoD

- [ ] `X-RateLimit-Remaining` and `X-RateLimit-Reset` are present on every `/api/` response.
- [ ] The middleware runs after `AuthMiddleware`, asserted against the settings order.

#### Task 2.3 DoD

- [ ] A raised `redis.TimeoutError` admits the request and logs at error level.
- [ ] The fail-open path adds no more than one Redis round trip to the request.

#### Task 2.4 DoD

- [ ] The three paths are covered end to end through the test client.

### M3: Anonymous quota — 9 SP | pending

**Goal**: unauthenticated callers get their own per-IP quota at a quarter of the authenticated
one, on the same primitive.

**Verify**: `just test tests/api/test_ratelimit_anonymous.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Per-IP bucket key derivation behind the proxy's forwarded header | `api/ratelimit/keys.py` | 3 | pending |
| 3.2 | `RATE_LIMIT_ANON_DIVISOR` (4) and quota resolution per caller kind | `settings/base.py`, `api/middleware.py` | 3 | pending |
| 3.3 | Tests for the anonymous path, including the spoofed-header case | `tests/api/test_ratelimit_anonymous.py` | 3 | pending |

#### Task 3.1 DoD

- [ ] The client IP is read from the trusted proxy header, not from the socket peer.
- [ ] An untrusted hop cannot widen its own quota by forging the header.

#### Task 3.2 DoD

- [ ] An anonymous caller's quota is the authenticated quota divided by the divisor.

#### Task 3.3 DoD

- [ ] Both the honest and the spoofed-header cases are asserted.

### M4: Rollout — 15 SP | pending

**Goal**: the limiter is enabled stage by stage with the dashboards and the runbook an operator
needs to watch it and turn it off.

**Verify**: `just test && just lint && just typecheck`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `RATE_LIMIT_ENFORCE` staged flag — observe, then enforce, per environment | `settings/base.py`, `api/middleware.py` | 4 | pending |
| 4.2 | Throttle and admit counters exported for the metrics scrape | `api/ratelimit/metrics.py` | 4 | pending |
| 4.3 | Grafana dashboard provisioned from the repo | `ops/grafana/dashboards/ratelimit.json` | 4 | pending |
| 4.4 | Operator runbook — what to watch, how to widen a quota, how to disable | `docs/runbooks/rate-limit.md` | 3 | pending |

#### Task 4.1 DoD

- [ ] In observe mode the bucket is consumed and the decision logged, but nothing is rejected.
- [ ] The flag is per environment and defaults to observe.

#### Task 4.2 DoD

- [ ] Admitted and throttled requests are counted separately, labelled by caller kind.

#### Task 4.3 DoD

- [ ] The dashboard provisions from the repo and renders both counters plus the outage rate.

#### Task 4.4 DoD

- [ ] The runbook names the flag, the two settings and the rollback step.

## Key Files Reference

| File | Role |
|------|------|
| `api/middleware.py` | the chain every public route passes through; the limiter lands here |
| `settings/base.py` | middleware order and the quota settings |
| `api/ratelimit/` | the bucket primitive, its Lua script, key derivation and metrics |
| `ops/grafana/dashboards/` | provisioned dashboards |

## Final Verification

- [ ] A client over quota receives 429 with `Retry-After`; the next window admits it again.
- [ ] A Redis outage admits traffic and logs at error level.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Per-endpoint budgets and plan-tier quotas.
- Any admin surface for inspecting or resetting a caller's bucket.

## Risk register

- **NOTE, deferred** — the 429 body carries no machine-readable quota window; clients must read
  the reset from the header set. Deferred: the header set already carries it and changing the
  error body is a public-contract change.
- **NOTE, deferred** — bucket keys are not namespaced by API version, so a future `/api/v2/`
  route would share `/api/v1/`'s bucket. Deferred: only one version is served today.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Configuration` | document the quota settings and the fail-open policy | M2.3 |
| `## Operations` | link the rate-limit runbook | M4.4 |
</file>

