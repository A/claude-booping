---
status: smoke-greening
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:28
suite_reviewed_at: 20260731 19:47
---

# design

[← index](../../index.md)

## Contract

- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.
- **Needs** —
  - the confirmed framing — the restated problem, the task type, the scope boundaries, and the
    user's answers to the scope-challenge questions
  - the blast radius — the `## Blast radius` section of `index.md`, with the prior art and the
    conventions already in play
  - the current external practice for this work — `research.md` when the user requested it — or
    the note that no research was requested
  - when the run has looped back into design: the user's objection or change request, and the
    design call it targets
- **Value** — the architecture settled with the user **in conversation** during the step: every
  trade-off that is the user's to call is asked and answered here, so the plan is written
  against decided calls instead of re-deciding them mid-draft. The settled outcome is recorded
  in one place; there is no separate confirm status — alignment is the conversation itself.
- **Output files** —
  - `[UPDATED] plans/{slug}/index.md` — the `## Design` section:
    - `### Approach` — the chosen architecture and pattern choice with the rationale that made it
      win, named against the modules and files the blast radius identified
    - `### Surface changes` — every data, API, config and CLI change the approach implies, each
      concrete enough to implement from: field and key names, endpoint shapes, defaults
    - `### Alternatives` — each approach considered and not taken, with the one reason it lost
    - `### Trade-offs` — the calls that were the user's, each recorded with the option taken and
      why; an open call is asked in the conversation, never parked here unanswered
    - `### Risks` — what can go wrong on this approach, each with its mitigation
    - on a loopback re-entry the section is revised in place, never appended to: settled
      subsections stay as they are and only the reopened call is rewritten
  - no other file — `plan.md` already exists carrying its identity frontmatter, and stays
    untouched until the plan is drafted
- **Step report** — `## Changed:` list; `## Questions:` — one numbered line per trade-off call
  still open in the conversation, empty once the design is settled.
- **Review gate** —
  - none as a status — the user iterates in conversation during the step, rejecting a call or
    asking for another alternative; the step does not end while a call that is the user's is
    unanswered
  - an objection that needs blast radius or external practice the research pass missed — or a
    mid-design request for web research — sends the run back to research rather than into
    another design pass

## Example artifact

`plans/20260731-rate-limit-public-api/index.md`, the `## Design` section:

```markdown
## Design

### Approach

A token-bucket limiter added to the existing middleware chain in `api/middleware.py`, buckets
held in the Redis instance the cache already uses. Chosen because the chain is the only place
every public route passes through, and per-key accounting needs the authenticated client id the
middleware already resolves.

### Surface changes

- **Config** — `RATE_LIMIT_PER_MINUTE` (int, default 120) and `RATE_LIMIT_BURST` (int, default
  20), both read in `settings/base.py` alongside the existing cache keys.
- **API** — every `/api/` response gains `X-RateLimit-Remaining` and `X-RateLimit-Reset`; over
  quota returns 429 with the standard error body and a `Retry-After` header.
- **Data** — no schema change. Redis keys `rl:{client}:{window}`, TTL twice the window.

### Alternatives

- **Per-process in-memory counters** — rejected: the four gunicorn workers each keep their own
  bucket, so the effective limit is four times the configured one.
- **Nginx `limit_req`** — rejected: it sees only the IP, never the authenticated client id, and
  the quota is per API key.

### Trade-offs

- **Redis unavailable: fail open** — taken in conversation: fail open keeps the API serving
  during a cache outage; the dropped limit is logged at error level.
- **Anonymous callers: per-IP at a quarter of the authenticated quota** — taken in
  conversation: per-IP is fairer, and the shared-egress case is documented rather than solved.

### Risks

- Redis becomes a hard dependency of the request path — mitigated by the fail-open call above
  and a 50 ms timeout on the bucket read.
- Clients behind one NAT share an anonymous quota and see spurious 429s — mitigated by
  documenting the authenticated path as the supported one for shared egress.
```

## Return Format

Mid-conversation, with calls still open:

```markdown
## Changed:
- [UPDATED] plans/20260731-rate-limit-public-api/index.md — design

## Questions:
1. Fail open or fail closed when Redis is unavailable? Recommended: fail open — the plan's error
   path cannot be written until this is called.
2. Per-IP quota or one shared quota for anonymous callers? Recommended: per-IP at a quarter of
   the authenticated quota.
```

Once the calls are answered the questions come back empty and the run moves to drafting.
