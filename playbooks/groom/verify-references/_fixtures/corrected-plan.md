# Input — corrected-plan

The plan below was refined by `decompose-work`; the user has not read it yet — the run's only
review gate is `present`, after this step. Check every external reference the plan names against
current upstream documentation, correct what is wrong, and write the `## References` section of
the run's `index.md`.

## Run-time context

- project: `orders-api` — a Django/DRF service managed with `uv`, deployed as four identical
  application workers behind a load balancer, with a cache tier declared in the repository's
  `compose.yaml`
- run slug: `20260731-rate-limit-public-api`
- run workdir: the plan directory `plans/20260731-rate-limit-public-api/`, relative to the
  current working directory
- plan file: `plans/20260731-rate-limit-public-api/plan.md`, on disk beside the run's `index.md`

## Inputs

- the refined plan — the file at the path above; its external references sit in
  task bodies, in DoD lines and in a milestone `Verify` command
- the run's `index.md`, on disk: `## Framing`, `## Blast radius`, `## Design` and the
  `## Refinement` verdict the sizing pass wrote
- current upstream documentation for every external reference the plan names — the vendor's own
  docs, release notes, changelogs and package registries, read now rather than recalled

## Context files

<file path="plans/20260731-rate-limit-public-api/index.md">
---
status: verifying-references
---
# Rate limit the public API

## Framing

### Request

> Public API callers get a per-key request quota with standard rate-limit headers

### Restated problem

**Current state** — every `/api/` route is served without admission control; one client's retry
loop saturates all four application workers.

**Motivation** — two incidents this quarter traced to a single caller; support has no lever short
of revoking the key.

**Scope** — per-key quotas on `/api/` routes with the standard rate-limit response headers. Not:
per-endpoint budgets, plan tiers, or any quota-management UI.

### Task type

`feature` — classified at intake and unchanged since.

### Scope boundaries

**In scope**

- M1: Cache backing for the limiter
- M2: Middleware wiring

**Out of scope**

- Per-endpoint budgets and plan-tier quotas.
- Any admin surface for inspecting or resetting a caller's bucket.
- Internal service-to-service calls, which do not pass through the authentication middleware.

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
| base.py | `settings/base.py` | cache configuration, middleware order, and the two quota settings | medium — the plan changes what it does |
| compose.yaml | `compose.yaml` | the local `cache` service the tests run against | medium — the plan changes what it does |

### Prior art

- `api/middleware.py` — the closest existing shape this work follows

### Conventions in play

- the project's own lint / typecheck / test gate runs on every change under these
  surfaces, and the plan's Final Verification restates it

### Unknowns for design

- none left open: the design below settles every call the map raised

## Design

### Approach

The limiter never holds a client of its own: `CACHES["default"]` is pointed at the framework's
Redis cache backend, and `RateLimitMiddleware` consumes the bucket through the cache API. The
bucket key is `rl:{api_key}:{window}`; the window length and the per-window allowance come from
two settings, so staging can run a tighter quota than production. A cache exception inside the
middleware admits the request and logs.

### Surface changes

- `api/middleware.py` — the chain every public route passes through; the limiter lands here
- `settings/base.py` — cache configuration, middleware order, and the two quota settings
- `compose.yaml` — the local `cache` service the tests run against

### Alternatives

- none survived the blast radius: the approach above is the only one the mapped
  surfaces support

### Trade-offs

- **Bucket store**: one cache tier shared by every worker — per-process counters multiply the
  effective limit by the worker count.
- **Placement**: the token bucket lives in the middleware chain (`api/middleware.py`), the only
  layer every public route passes through and the one that has already resolved the API key.
- **Failure policy**: fail open on a cache error, logged at error level — a cache outage must not
  become an API outage.

### Risks

- the change lands across several call sites at once — mitigated by the plan's own
  Final Verification pass

## Refinement

Skipped — no task sits at or over the 5 SP re-decompose threshold (the largest is 4 SP), and the
sprint totals 12 SP, well under the 35 SP split threshold. The plan file was not touched.
</file>

<file path="plans/20260731-rate-limit-public-api/plan.md">
---
title: Rate limit the public API
type: feature
status: awaiting-plan-review
sp: 12
split_from: null
created: 2026-07-31
planned: 20260731 14:38
started: null
completed: null
retro: null
goal: null
summary: "Public API callers get a per-key request quota with standard rate-limit headers"
commit: 4c1f9ab7d2e5b8103f6a0c9d7e2b4a15c8039fde
---

# Rate limit the public API

## Context

**Current state** — every `/api/` route is served without admission control; one client's retry
loop saturates all four application workers.

**Motivation** — two incidents this quarter traced to a single caller; support has no lever short
of revoking the key.

**Scope** — per-key quotas on `/api/` routes with the standard rate-limit response headers. Not:
per-endpoint budgets, plan tiers, or any quota-management UI.

## Decisions

- **Bucket store**: one cache tier shared by every worker — per-process counters multiply the
  effective limit by the worker count.
- **Placement**: the token bucket lives in the middleware chain (`api/middleware.py`), the only
  layer every public route passes through and the one that has already resolved the API key.
- **Failure policy**: fail open on a cache error, logged at error level — a cache outage must not
  become an API outage.

## Architecture

The limiter never holds a client of its own: `CACHES["default"]` is pointed at the framework's
Redis cache backend, and `RateLimitMiddleware` consumes the bucket through the cache API. The
bucket key is `rl:{api_key}:{window}`; the window length and the per-window allowance come from
two settings, so staging can run a tighter quota than production. A cache exception inside the
middleware admits the request and logs.

## Milestones

### M1: Cache backing for the limiter — 5 SP | pending

**Goal**: the service has a Redis-backed Django cache that every worker shares.

**Verify**: `uv add --group dev redis==5.0.1 && just test tests/api/test_cache.py`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add the cache dependency `redis==5.0.1` and declare the compose service `cache` on the image `redis:7.2-alpine3.18` | `pyproject.toml`, `compose.yaml` | 2 | pending |
| 1.2 | Point `CACHES["default"]["BACKEND"]` at `django.core.cache.backends.redis.RedisCache` against the compose service, with `RATE_LIMIT_PER_MINUTE` (120) and `RATE_LIMIT_WINDOW_SECONDS` (60) beside it | `settings/base.py` | 3 | pending |

#### Task 1.1 DoD

- [ ] The pinned cache client is importable inside the app image.
- [ ] `just services up` starts the `cache` service and `just test tests/api/test_cache.py` passes
      against it.

#### Task 1.2 DoD

- [ ] The cache backend is the framework's own built-in one — no third-party cache package is
      added to the project.
- [ ] `cache.set` / `cache.get` round-trip against the running `cache` service in
      `just test tests/api/test_cache.py`.
- [ ] Both new settings carry the defaults above and are read from the environment when set.

### M2: Middleware wiring — 7 SP | pending

**Goal**: every `/api/` response carries the quota headers, and over-quota callers get a 429.

**Verify**: `just test tests/api/test_ratelimit_middleware.py && just lint`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `RateLimitMiddleware` — consume the bucket, fail open on a cache error, and return 429 over quota with a `Retry-After` header | `api/middleware.py` | 4 | pending |
| 2.2 | Set `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset` on every `/api/` response, and register the middleware after the authentication middleware | `api/middleware.py`, `settings/base.py` | 3 | pending |

#### Task 2.1 DoD

- [ ] A caller over quota receives 429 together with `Retry-After` carrying the seconds until the
      window resets; the next window admits it again.
- [ ] A cache exception raised inside the middleware admits the request and logs at error level —
      asserted by test.

#### Task 2.2 DoD

- [ ] `X-RateLimit-Reset` carries the epoch seconds at which the caller's window resets.
- [ ] `X-RateLimit-Remaining` is present on every `/api/` response and never drops below zero.
- [ ] The limiter runs after authentication, so the bucket key is the resolved API key rather than
      the client address.

## Key Files Reference

| File | Role |
|------|------|
| `api/middleware.py` | the chain every public route passes through; the limiter lands here |
| `settings/base.py` | cache configuration, middleware order, and the two quota settings |
| `compose.yaml` | the local `cache` service the tests run against |

## Final Verification

- [ ] A key over quota receives 429 with `Retry-After`; the next window admits it again.
- [ ] `just test` — all tests pass.
- [ ] `just lint && just typecheck` — clean.

## Out of scope

- Per-endpoint budgets and plan-tier quotas.
- Any admin surface for inspecting or resetting a caller's bucket.
- Internal service-to-service calls, which do not pass through the authentication middleware.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Configuration` | document the two quota settings and the fail-open policy | M2.2 |
</file>

