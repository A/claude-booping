---
status: smoke-greening
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:28
suite_reviewed_at: 20260731 19:47
---

# design

[← index](../../index.md)

## Contract

- **Needs** —
  - the confirmed framing — the restated problem, the task type, the scope boundaries, and the
    user's answers to the scope-challenge questions
  - the blast radius — the files, modules, integrations and external surfaces the work touches,
    with the prior art and the conventions already in play
  - the current external practice for this work — approaches, trade-offs and pitfalls with their
    sources — or the note that the work is well-trodden and none was gathered
  - when the run has looped back into design: the user's objection or change request, and the
    design call it targets
- **Value** — the architecture settled with the user in one reviewable document, so the plan is
  written against decided calls instead of re-deciding them mid-draft; every trade-off that is
  the user's to call is surfaced here, not buried in a plan they have not read yet.
- **Output files** —
  - `[CREATED|UPDATED] _runs/groom/{slug}/design.md` — H1 `# design — {slug}`, then:
    - `## Approach` — the chosen architecture and pattern choice with the rationale that made it
      win, named against the modules and files the blast radius identified
    - `## Surface changes` — every data, API, config and CLI change the approach implies, each
      concrete enough to implement from: field and key names, endpoint shapes, defaults
    - `## Alternatives` — each approach considered and not taken, with the one reason it lost
    - `## Trade-offs` — the calls that are the user's, each with its options, the consequence of
      each, and a recommendation
    - `## Risks` — what can go wrong on this approach, each with its mitigation
    - frontmatter is harness-owned: the step writes none and preserves whatever it finds — the
      confirm edge stamps `reviewed_at` on this file
    - on a loopback re-entry the file is revised in place, never appended to: settled sections
      stay as they are and only the reopened call is rewritten
  - no other file — `plans/{slug}.md` already exists carrying its identity frontmatter, and stays
    untouched until the plan is drafted
- **Harness return** — `## Changed:` list; `## Questions:` — one numbered line per open
  trade-off call, empty when the design leaves none.
- **Review gate** —
  - the user iterates on the design — rejecting a call, asking for another alternative — and
    confirms it in-file before any plan body is written
  - every call in `## Trade-offs` is settled, or the recommendation is explicitly taken; an
    unanswered call blocks the gate
  - an objection that needs blast radius or external practice the research pass missed sends the
    run back to research rather than into another design pass

## Example artifact

```markdown
# design — 20260731-14-02_rate-limit-public-api

## Approach

A token-bucket limiter added to the existing middleware chain in `api/middleware.py`, buckets
held in the Redis instance the cache already uses. Chosen because the chain is the only place
every public route passes through, and per-key accounting needs the authenticated client id the
middleware already resolves.

## Surface changes

- **Config** — `RATE_LIMIT_PER_MINUTE` (int, default 120) and `RATE_LIMIT_BURST` (int, default
  20), both read in `settings/base.py` alongside the existing cache keys.
- **API** — every `/api/` response gains `X-RateLimit-Remaining` and `X-RateLimit-Reset`; over
  quota returns 429 with the standard error body and a `Retry-After` header.
- **Data** — no schema change. Redis keys `rl:{client}:{window}`, TTL twice the window.

## Alternatives

- **Per-process in-memory counters** — rejected: the four gunicorn workers each keep their own
  bucket, so the effective limit is four times the configured one.
- **Nginx `limit_req`** — rejected: it sees only the IP, never the authenticated client id, and
  the quota is per API key.

## Trade-offs

- **Redis unavailable: fail open or fail closed** — fail open keeps the API serving during a
  cache outage but drops the limit entirely; fail closed holds the limit but turns a cache
  outage into an API outage. Recommended: fail open, logged at error level.
- **Anonymous callers: per-IP or one shared quota** — per-IP is fairer but is defeated by a
  rotating client; a shared quota bounds total anonymous load. Recommended: per-IP at a quarter
  of the authenticated quota.

## Risks

- Redis becomes a hard dependency of the request path — mitigated by the fail-open call above
  and a 50 ms timeout on the bucket read.
- Clients behind one NAT share an anonymous quota and see spurious 429s — mitigated by
  documenting the authenticated path as the supported one for shared egress.
```

## Return Format

```markdown
## Changed:
- [CREATED] _runs/groom/20260731-14-02_rate-limit-public-api/design.md

## Questions:
1. Fail open or fail closed when Redis is unavailable? Recommended: fail open — the plan's error
   path cannot be written until this is called.
2. Per-IP quota or one shared quota for anonymous callers? Recommended: per-IP at a quarter of
   the authenticated quota.
```
