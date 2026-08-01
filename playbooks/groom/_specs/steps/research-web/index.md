---
status: done
reviewed_at: 20260731 19:14
fixtures_reviewed_at: 20260731 19:27
suite_reviewed_at: 20260731 19:47
---

[← index](../../index.md)

# research-web

## Contract

- **Needs** —
  - the confirmed framing — the restated problem, the task type, and the scope boundaries the
    user confirmed
  - the uncertainty signals that framing carries — unfamiliar surfaces, new or upgraded
    dependencies, approaches with no obvious precedent
- **Value** — settles what current external practice says before the architecture is called, so
  design argues from dated sources rather than model memory. The step always runs and always
  writes its file: with no conditional edges in the framework, a well-trodden request is
  answered with a skip note instead of an absent artifact, so `design` never has to work out
  whether research happened.
- **Output files** —
  - `[CREATED] _runs/groom/{slug}/research-web.md` — `## Verdict` first (`Researched` or
    `Skipped`, one line of rationale), then on the researched path the candidate approaches
    with their trade-offs and fit, the pitfalls that constrain the design, and a source table
    carrying a URL and a retrieval date per claim; on the skip path the verdict alone. The file
    is written on both paths — never omitted, never empty.
- **Harness return** — `## Changed:` list, the entry annotated with the verdict and its counts,
  plus `## Notes:` carrying the recommendation and the pitfall count (or the skip rationale).
- **Review gate** —
  - none — the step never pauses the run; its findings reach the user through `design`, where
    the user confirms the architecture they shaped

## Example artifact

```markdown
# research-web — 20260731-14-20_rate-limit-public-api

## Verdict

Researched — the request adds a dependency and a request-admission approach the codebase has no
prior art for.

## Approaches

### Token bucket in gateway middleware

Per-key bucket refilled at a fixed rate, checked before the handler runs.

- Fits: limits are per API key, which the gateway already resolves.
- Costs: bucket state must be shared across processes — needs the cache tier, which the
  deployment already runs.
- Retire cost: low — the middleware is one layer, removable without touching handlers.

### Sliding-window counter in the datastore

Counts requests per key per window directly in the primary datastore.

- Fits: no new infrastructure.
- Costs: a write per request on the hot path; the window boundary allows a 2x burst.

### Managed limiter at the CDN edge

- Fits: zero application code.
- Costs: limits cannot key on anything the application knows (plan tier, per-endpoint budgets),
  and local development loses the behaviour entirely.

## Pitfalls

- Returning `429` without `Retry-After` makes well-behaved clients retry immediately; the header
  is expected, not optional.
- Counting on the cache tier without a failure policy turns a cache outage into a total outage —
  fail-open vs fail-closed is a design call, not an implementation detail.
- Per-process in-memory buckets silently multiply the effective limit by the process count.

## Sources

| Source                                                | Backs                            | Checked  |
| ----------------------------------------------------- | -------------------------------- | -------- |
| https://www.rfc-editor.org/rfc/rfc6585                | `429` + `Retry-After` semantics  | 20260731 |
| https://redis.io/docs/latest/develop/use-cases/rate-limiting/ | token bucket on a shared cache | 20260731 |
| https://developer.fastly.com/reference/vcl/functions/rate-limit/ | edge limiter constraints   | 20260731 |
```

On the skip path the file carries the verdict alone:

```markdown
# research-web — 20260731-16-05_fix-stale-session-cookie

## Verdict

Skipped — well-trodden: a cookie-expiry bug on the framework's own session middleware, no new
dependency, no new surface, prior art for the fix in the repository.
```

## Return Format

```markdown
## Changed:

- [CREATED] _runs/groom/{slug}/research-web.md — researched: 3 approaches, 3 sources

## Notes:

- recommended: token bucket in gateway middleware — lowest retire cost, keys on what the
  gateway already resolves
- 3 pitfall(s) the design must answer, one of them a fail-open vs fail-closed call
```

On the skip path the annotation and the note carry the rationale instead:

```markdown
## Changed:

- [CREATED] _runs/groom/{slug}/research-web.md — skipped: well-trodden

## Notes:

- skipped: framework-native session bug, no new dependency or surface, prior art in the repository
```
